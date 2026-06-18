# sources/distributed-fs/ceph-client/drivers/hid/wacom_sys.c

## Purpose

`wacom_sys.c` is the system-integration half of the Wacom HID driver. It handles HID report I/O, descriptor parsing and quirks, input device allocation/registration, device mode switching, shared state between pen/touch interfaces, LEDs and OLED images, sysfs attributes, power-supply batteries, wireless receiver reconfiguration, ExpressKey Remote devices, mode-change reparsing, probe/remove, and suspend/resume.

Protocol-specific packet decoding and input capability details are delegated to `wacom_wac.c` and helpers declared in `wacom.h`/`wacom_wac.h`.

## Important APIs, Types, And Data

- `wacom_get_report()` and `wacom_set_report()` wrap `hid_hw_raw_request()` with retry loops for transient timeout/EAGAIN failures.
- `wacom_raw_event()` is the HID raw-event callback. It filters bootloader devices, enforces pen serial ordering where needed, stores the raw data pointer in `wacom_wac`, and calls `wacom_wac_irq()`.
- Descriptor parsing is handled by `wacom_hid_usage_quirk()`, `wacom_feature_mapping()`, `wacom_usage_mapping()`, `wacom_parse_hid()`, and `wacom_post_parse_hid()`.
- Device mode switching uses `wacom_set_device_mode()`, `wacom_hid_set_device_mode()`, `_wacom_query_tablet_data()`, and `wacom_bt_query_tablet_data()`.
- `struct wacom_hdev_data`, `wacom_udev_list`, and `wacom_add_shared_data()` manage shared pen/touch state across sibling HID interfaces with krefs.
- LED support is centered on `wacom_led_control()`, `wacom_led_putimage()`, sysfs attribute groups, LED class devices, and `wacom_initialize_leds()`.
- Battery and remote support use power-supply registration, `wacom_initialize_remotes()`, per-remote input devices, sysfs groups, and remote work queues.
- Lifecycle is driven by `wacom_probe()`, `wacom_parse_and_register()`, `wacom_remove()`, `wacom_resume()`, and the `wacom_driver` `struct hid_driver`.

## Control Flow

Probe begins in `wacom_probe()`. It validates table data, adjusts HID quirks, allocates and stores `struct wacom`, copies feature data from the HID ID table, initializes mode defaults, records USB pointers for USB devices, initializes mutex/work/timer objects, parses the HID descriptor, handles bootloader devices as hidraw-only, then calls `wacom_parse_and_register()`. Bluetooth devices additionally get a writable `speed` sysfs attribute.

`wacom_parse_and_register()` computes maximum input packet length, opens a devres group, allocates a pen FIFO, allocates pen/touch/pad input devices, handles Bamboo Pad special cases, applies default physical dimensions, parses feature and input descriptors, applies device quirks, infers or rejects unknown device types, calculates resolution, updates input names, attaches shared data, sets up input capabilities, starts HID hardware, registers input devices, initializes LEDs/remotes for pad devices, schedules delayed mode query for wired devices, handles special Bamboo and wireless monitor cases, updates shared values, and closes the devres group. Failures release the devres group and stop hardware where appropriate.

Raw input enters `wacom_raw_event()`. The serial-enforcement path queues reports in `wacom_wac->pen_fifo` until tool serial/type information arrives or the tool leaves range, then flushes queued reports through `hid_report_raw_event()`. Otherwise the raw data pointer is assigned and protocol decoding runs via `wacom_wac_irq()`.

Descriptor parsing first scans feature reports to discover contact maximum, input mode, mode reports, sensor offsets, and generic LED capability. It then scans input reports to infer pen/touch device type, axis maxima/physical size/unit data, pressure maximum, and generic HID mappings. Post-parse initializes multitouch slots for HID_GENERIC touch devices.

LED control exposes both legacy Wacom sysfs attributes under `wacom_led` and LED class devices. Store paths parse input, take `wacom->lock`, update group selection or luminance state, and send feature reports. OLED button image writes validate exact image size, send a start command, send four chunks, and send a stop command.

Wireless receiver work tears down existing resources for stylus/touch interfaces, uses the monitor-reported PID to find Wacom feature table data, reparses/registers the stylus and maybe touch interfaces as wireless variants, and updates the monitor name. Remote work drains one FIFO item, reschedules if more remains, creates/destroys per-remote input devices and sysfs groups based on serial slots, and attaches batteries once active/status data is available. Mode-change work releases and stops shared pen/touch interfaces, sets direct/indirect mode flags, then reparses and re-registers affected interfaces.

Remove stops HID hardware, cancels all delayed and normal work, deletes the idle-proximity timer, removes Bluetooth sysfs, disables LED triggers by clearing groups, and releases resources except for REMOTE devices where devres remote cleanup owns additional state. Resume re-queries tablet mode and reapplies LED control under `wacom->lock`.

## State And Persistence Behavior

Most state is per `struct wacom` and volatile. Runtime state includes input devices, Wacom feature data, shared pen/touch pointers, LED group arrays and brightness/select values, batteries, remote slots, FIFOs, work items, timers, and the `resources` flag identifying an open devres group.

`wacom_hdev_data` entries persist only while at least one sibling interface holds a kref. They are stored in a global `wacom_udev_list` protected by `wacom_udev_list_lock`. Several features intentionally reparse and recreate resources at runtime: wireless tablet PID changes and direct/indirect mode changes release input/resources and call `wacom_parse_and_register()` again. Battery devices are dynamically created/destroyed based on feature quirks and remote activity.

No user configuration is persisted by this file. Sysfs writes update device state and kernel memory only until disconnect/reprobe.

## Dependencies And Integration Points

- Depends heavily on HID core: `hid_parse()`, `hid_hw_start()`, `hid_hw_stop()`, `hid_hw_open()`, `hid_hw_close()`, raw requests, report traversal, raw event callbacks, and HID collections/usages.
- Integrates with input core through multiple `input_dev` instances for pen, touch, pad, and remotes.
- Integrates with multitouch, LED class/trigger APIs, sysfs, and power supply class.
- Uses USB metadata for physical paths, product strings, interface numbers, and wireless receiver sibling interfaces.
- Calls protocol-layer functions declared elsewhere: `wacom_wac_irq()`, `wacom_wac_report()`, `wacom_wac_usage_mapping()`, `wacom_wac_event()`, capability setup functions, `wacom_setup_device_quirks()`, `wacom_equivalent_usage()`, and `wacom_idleprox_timeout()`.

## Risks And Edge Cases

- `wacom_set_device_mode()` compares `rep_data[1]` to `mode_report` rather than `mode_value` in its retry condition, which is subtle and should be verified against device protocol expectations.
- Many paths dynamically release and recreate devres-managed resources. Incorrect ordering can leave stale input devices, LED class devices, sysfs groups, or shared pointers.
- Wireless work assumes receiver interface indexes 1 and 2 exist and contain HID devices.
- LED sysfs and LED class operations use `wacom->lock`, but remote slot state also uses `remote_lock`; cross-subsystem ordering must avoid races during disconnect and work cancellation.
- Pen serial enforcement queues raw reports and later reinjects them through `hid_report_raw_event()`. Incorrect queue sizing or malformed report lengths can drop events or reorder tool state.
- Battery status is synthesized from several mutable booleans; stale fields can report misleading power-supply state if protocol updates are missed.

## Test Signals

- Probe tests should cover HID_GENERIC, legacy USB, Bluetooth, bootloader, Bamboo Pad, wireless monitor, and REMOTE feature-table entries.
- Descriptor tests should verify contact maximum discovery, input mode setup, mode report detection, AES serial usage patching, Dell Canvas mode quirk, and Intuos Pro Y maximum correction.
- Input tests should verify pen/touch/pad device creation, absence of unused devices, multitouch slot mode, resolution calculation, and shared mute-touch-switch behavior.
- LED tests should cover sysfs group creation, LED class brightness get/set, group selection, luminance writes, OLED image chunk transfer, and cleanup on disconnect.
- Battery, wireless, remote, suspend/resume, and disconnect-concurrency tests should cover dynamic resource creation/destruction and work cancellation.
