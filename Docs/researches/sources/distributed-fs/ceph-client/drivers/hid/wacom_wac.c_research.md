# sources/distributed-fs/ceph-client/drivers/hid/wacom_wac.c

## Purpose
`wacom_wac.c` is the Wacom-specific event decoder, capability setup, quirk layer, and HID ID table for the kernel HID Wacom driver. It translates Wacom raw USB/Bluetooth/I2C/PCI reports and HID-generic field events into Linux input devices for pen, touch, pad, wireless monitor, and remote controls. It also maintains user-visible compatibility details such as `ABS_MISC` tool IDs, `MSC_SERIAL`, ExpressKey numbering, touch mute switches, and LED selection behavior expected by legacy userspace such as xf86-input-wacom, udev, and libwacom.

## Important APIs, Types, and Functions
- Module parameter: `touch_arbitration` controls whether touch reports are suppressed while a stylus is in proximity and whether pen reports are delayed while touch is down.
- Proximity and battery helpers: `wacom_force_proxout()`, `wacom_idleprox_timeout()`, `__wacom_notify_battery()`, and `wacom_notify_battery()` clear stuck pen state and push battery state into `struct wacom_battery` / power_supply.
- Raw report decoders: `wacom_penpartner_irq()`, `wacom_pl_irq()`, `wacom_ptu_irq()`, `wacom_dtu_irq()`, `wacom_dtus_irq()`, `wacom_graphire_irq()`, `wacom_intuos_irq()`, `wacom_tpc_irq()`, `wacom_bpt_irq()`, `wacom_bamboo_pad_irq()`, `wacom_wireless_irq()`, `wacom_status_irq()`, and `wacom_remote_irq()` cover fixed-packet families.
- Intuos helpers: `wacom_intuos_pad()`, `wacom_intuos_inout()`, `wacom_intuos_general()`, `wacom_exit_report()`, `wacom_intuos_get_tool_type()`, `wacom_intuos_id_mangle()`, and Bluetooth-specific handlers decode tool IDs, serials, pen packets, pad rings/buttons, battery status, and batched pen/touch frames.
- HID-generic bridge: `wacom_equivalent_usage()`, `wacom_wac_usage_mapping()`, `wacom_wac_event()`, and `wacom_wac_report()` normalize vendor usages, map HID fields into input capabilities, process values, and perform report-end synthesis.
- HID-generic category handlers: battery, pad, pen, and finger functions such as `wacom_wac_pad_usage_mapping()`, `wacom_wac_pad_event()`, `wacom_wac_pen_event()`, `wacom_wac_pen_report()`, `wacom_wac_finger_event()`, and `wacom_wac_finger_report()` hold per-report state in `wacom_wac->hid_data`.
- Capability setup APIs exported to the companion driver include `wacom_setup_device_quirks()`, `wacom_setup_pen_input_capabilities()`, `wacom_setup_touch_input_capabilities()`, and `wacom_setup_pad_input_capabilities()`.
- Device identification is encoded by many `static const struct wacom_features wacom_features_<product>` records and the final `wacom_ids[]` HID device table.

## Control Flow
For legacy/raw devices, the outer entry point is `wacom_wac_irq(wacom_wac, len)`. It switches on `features.type`, calls the matching packet decoder, and if the decoder returns `sync = true`, synchronizes all present input devices. Each decoder validates report ID or packet length, updates `wacom->tool[]`, `wacom->id[]`, `wacom->serial[]`, proximity flags, and reports input events with `input_report_*`.

For Intuos-class devices, `wacom_intuos_irq()` first routes pad packets through `wacom_intuos_pad()`, then proximity/tool enter and exit through `wacom_intuos_inout()`, then positional/button data through `wacom_intuos_general()`. Enter packets populate serial and tool ID; general packets are ignored until an ID is known; exit packets call `wacom_exit_report()` to clear axes/buttons and report the serial for userspace correlation.

For HID-generic devices, the HID core calls `wacom_wac_usage_mapping()` during input mapping and `wacom_wac_event()` for individual values. `wacom_wac_report()` wraps complete report processing: it detects whether pad/pen/finger fields are present, runs pre-report reset code, walks collections so related fields are processed together, and then runs post-report synthesis such as pad prox, pen tool reports, battery notification, and touch frame sync.

Touch handling is guarded by `touch_is_muted()`, `report_touch_events()`, and `delay_pen_events()`. Single-touch, multi-touch, 24HDT, Bamboo, and HID-generic finger paths all update `shared->touch_down`; pen paths update `shared->stylus_in_proximity`, giving the arbitration code cross-interface visibility.

## State and Persistence
State is in memory only. Key persistent-across-report fields are `tool[]`, `id[]`, `serial[]`, `reporting_data`, `num_contacts_left`, ring counters, Bluetooth timing, and the nested `hid_data` report accumulator. Cross-interface state lives in `struct wacom_shared`, especially `stylus_in_proximity`, `touch_down`, `touch_input`, `has_mute_touch_switch`, and `is_touch_on`. Battery values are cached in the parent `struct wacom` battery objects and remotes. Remote status events are queued with `kfifo_in()` and scheduled work, not stored on disk. The product table is static data used at probe time.

## Dependencies and Integration Points
This file depends on the Linux HID, input, multitouch, LED, power_supply, timer, kfifo, and workqueue infrastructure, plus local `wacom.h` / `wacom_wac.h`. It integrates with the companion Wacom driver through `struct wacom`, `wacom_schedule_work()`, LED helpers (`wacom_led_find()`, `wacom_led_next()`, `wacom_leds_brightness_get()`), battery registration workers, wireless/remote workers, and mode-change workers. User-visible integration is through `/dev/input` event nodes, evdev capabilities, power_supply battery updates, LED triggers, module parameters, and HID device matching via `MODULE_DEVICE_TABLE(hid, wacom_ids)`.

## Risks and Edge Cases
- Packet decoders are highly device-specific and rely on fixed offsets and endian conversions; adding a product with the wrong `type`, packet length, or `touch_max` can misreport axes or buttons.
- Pen/touch arbitration can drop or delay events if `shared` state is stale, especially around touch mute, forced prox-out, and partial multi-packet touch frames.
- HID-generic handling is stateful across individual usage callbacks; missing `pre_report` or `report` processing can leak eraser, tip, serial, or contact counters between reports.
- Several paths manipulate shared remote/battery/LED state under locks or in callbacks; lock ordering and destructor paths matter during disconnect or `hsi`/HID flushes.
- Compatibility behavior is deliberate: clearing `ABS_MISC`, reporting `BTN_TOOL_*` before serial/misc, fake pad axes, and numbered button mapping should not be changed casually.
- Some code paths schedule work or timers from interrupt/report context; error handling must avoid sleeping in atomic context.

## Test Signals
- Build coverage: compile the Wacom HID driver with `CONFIG_HID_WACOM` across USB, Bluetooth, I2C, and PCI HID support.
- Runtime input tests: verify pen proximity enter/exit, tip pressure, eraser, stylus buttons, serial/tool ID, touch slots, pad buttons/rings/strips, LED mode changes, battery reporting, and touch mute on representative devices.
- Regression signals include no stuck `BTN_TOOL_*` after idleprox timeout, no partial multitouch sync while `num_contacts_left` is nonzero, no dropped Bluetooth frames without warning, and correct `SW_MUTE_DEVICE` state after pad touch-toggle events.
- HID-generic devices need descriptor-driven tests for vendor usage normalization, logical min/max bounds, rotation offsets, third barrel button quirk, and packet sequence warnings.
