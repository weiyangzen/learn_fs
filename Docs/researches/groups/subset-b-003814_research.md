# subset-b-003814 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/wacom_wac.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/wacom_wac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/wacom_wac.h -->
# sources/distributed-fs/ceph-client/drivers/hid/wacom_wac.h

## Purpose
`wacom_wac.h` defines the shared constants, packet/report IDs, Wacom vendor HID usage values, device type taxonomy, quirk flags, feature records, and runtime state structures used by the Wacom HID driver. It is the contract between the Wacom-specific decoder in `wacom_wac.c` and the broader driver in `wacom.h` / other Wacom implementation files.

## Important APIs, Types, and Fields
- Packet length defines such as `WACOM_PKGLEN_BBFUN`, `WACOM_PKGLEN_BBTOUCH3`, `WACOM_PKGLEN_WIRELESS`, and `WACOM_BYTES_PER_MT_PACKET` are used by raw IRQ routing.
- Device/report IDs include stylus/touch/cursor/eraser/pad IDs and report numbers like `WACOM_REPORT_PENABLED`, `WACOM_REPORT_INTUOSPAD`, `WACOM_REPORT_REMOTE`, `WACOM_REPORT_DEVICE_LIST`, and `WACOM_REPORT_USB`.
- Command report IDs include LED, icon transfer, pairing, and wireless Intuos commands.
- Quirk flags include low-resolution Bamboo touch, `SENSE`, AES pen, battery, tool serial, and inferred third pen button behavior.
- Vendor HID usage constants cover Wacom digitizer, touch, G9/G11 pages, serial high bits, tool type, distance, touch strips/rings, mute/touch switches, battery, accelerometer, offsets, mode changes, and ExpressKeys.
- Field-class macros `WACOM_BATTERY_USAGE()`, `WACOM_PAD_FIELD()`, `WACOM_PEN_FIELD()`, `WACOM_FINGER_FIELD()`, and `WACOM_DIRECT_DEVICE()` categorize HID fields for mapping/event dispatch.
- The enum assigns integer device families from `PENPARTNER` through `HID_GENERIC`, `BOOTLOADER`, and `MAX_TYPE`.
- `struct wacom_features` stores static/probed capabilities: name, axis maxima/resolution/fuzz, pressure/distance, type, button count, offsets, device type bitmask, physical units, quirks, touch max, paired product IDs, packet length, and HID-type filters.
- `struct wacom_shared` stores cross-interface pen/touch/wireless state.
- `struct hid_data` stores per-report and persistent HID-generic decode state.
- `struct wacom_wac` is the central per-interface runtime object containing names, data buffer, tool IDs, serials, feature state, input devices, FIFOs, Bluetooth flags, ring counters, mode state, and `hid_data`.

## Control Flow Role
The header does not execute control flow itself, but it shapes all Wacom dispatch. Raw packet handlers branch on enum `features.type` and packet length constants. HID-generic mapping and event paths rely on the usage classification macros and Wacom usage constants. Probe/setup code uses `struct wacom_features` to decide which input devices to allocate and which capabilities to expose; report handlers update `struct wacom_wac` and `struct wacom_shared` fields across callbacks.

## State and Persistence
All structures defined here are volatile kernel runtime state. `struct wacom_features` begins from static table data but is modified during probe by HID descriptors and quirks. `struct hid_data` is intentionally mutable across report callbacks. `struct wacom_shared` enables multiple HSI/HID interfaces or paired pen/touch devices to share arbitration and device references. No disk persistence is defined.

## Dependencies and Integration Points
The header depends on `linux/types.h`, `linux/hid.h`, and `linux/kfifo.h`. Its constants map directly to HID usages, Linux input event codes, HSI-independent Wacom command reports, and local Wacom driver work. It is included by `wacom_wac.c` and other Wacom driver files that need feature and state definitions.

## Risks and Edge Cases
- The device enum order is semantically significant because source code uses range comparisons such as `type >= INTUOS5S && type <= INTUOSPL`; inserting new values in the wrong place can break family checks.
- Usage-classification macros are broad and order-sensitive; `wacom_wac_usage_mapping()` checks battery, pad, pen, then finger.
- Struct fields such as `offset_*`, `oVid/oPid`, `pktlen`, and `check_for_hid_type` drive probe-time pairing and filtering; incorrect defaults can expose the wrong input device.
- `WACOM_MAX_REMOTES`, packet lengths, and `touch_max` values need to align with buffer sizes and multitouch slot allocation in the C implementation.

## Test Signals
- Compile tests should catch missing constants and struct layout users.
- Runtime descriptor tests should verify field classifiers put vendor usages in the expected battery/pad/pen/finger paths.
- Device table additions should be checked for enum range assumptions, `touch_max`, paired product IDs, and packet length compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/wacom_wac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hsi/Kconfig

## Purpose
This Kconfig file defines the top-level High Speed Synchronous Serial Interface subsystem switch. `menuconfig HSI` enables HSI support and, when selected, includes controller and client configuration menus.

## Important Symbols
- `HSI`: tristate, user-visible "HSI support". The help text describes HSI as a synchronous serial interface mainly for application engines and cellular modems.
- `HSI_BOARDINFO`: internal bool defaulting to `y` under `if HSI`; used to include board-info support in the HSI core build.
- Included files: `drivers/hsi/controllers/Kconfig` and `drivers/hsi/clients/Kconfig`.

## Control Flow and Build Flow
When `CONFIG_HSI` is disabled, controller/client options and `HSI_BOARDINFO` are not visible. When enabled as built-in or module, the nested Kconfig files declare concrete controller and client drivers. `HSI_BOARDINFO` defaults to enabled without prompting.

## State and Persistence
There is no runtime state. The only persistence is kernel configuration state in `.config`, controlling which HSI objects are compiled.

## Dependencies and Integration Points
This file integrates the HSI subtree into the kernel configuration hierarchy. It feeds `drivers/hsi/Makefile`, where `CONFIG_HSI` builds `hsi.o` and `CONFIG_HSI_BOARDINFO` adds `hsi_boardinfo.o`.

## Risks and Edge Cases
- Because `HSI_BOARDINFO` defaults to `y` whenever HSI is enabled, disabling legacy board-info support would require changing this file or adding a prompt/dependency.
- Controller/client options are hidden behind `if HSI`; symbols that already depend on `HSI` in child files are protected twice.

## Test Signals
- `make menuconfig` or `scripts/kconfig/conf` should show HSI support and child menus only when expected.
- Build matrix should cover `CONFIG_HSI=y`, `m`, and unset to confirm core and child Makefiles resolve correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hsi/Makefile

## Purpose
This Makefile builds the HSI subsystem core and descends into HSI controller and client subdirectories.

## Important Build Rules
- `obj-$(CONFIG_HSI) += hsi.o` builds the aggregate HSI core object when HSI is enabled.
- `hsi-objs := hsi_core.o` makes `hsi_core.o` the base object in `hsi.o`.
- `hsi-$(CONFIG_HSI_BOARDINFO) += hsi_boardinfo.o` conditionally adds board-info support.
- `obj-y += controllers/` and `obj-y += clients/` always descend into child directories; their contents are gated by their own config symbols.

## Control Flow and Build Flow
Kbuild creates `hsi.o` from the listed component objects and links it built-in or as a module depending on `CONFIG_HSI`. Subdirectory traversal is unconditional, but object generation inside controller/client Makefiles depends on individual symbols.

## State and Persistence
No runtime state exists. The file only expresses Kbuild dependency state.

## Dependencies and Integration Points
It depends on Kconfig symbols from `drivers/hsi/Kconfig` and child Kconfig files. It integrates `hsi_core.c`, optional `hsi_boardinfo.c`, and all controller/client Makefiles into the kernel build.

## Risks and Edge Cases
- `obj-y` traversal means syntax errors in child Makefiles can affect builds even when HSI is off, although object compilation remains symbol-gated.
- Adding new HSI core objects must use the `hsi-*` aggregate pattern or they will not be linked into `hsi.o`.

## Test Signals
- Build with HSI built-in and as module; inspect generated objects to ensure `hsi_boardinfo.o` follows `CONFIG_HSI_BOARDINFO`.
- Confirm controller/client modules still build when only their symbols are selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/clients/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hsi/clients/Kconfig

## Purpose
This Kconfig file declares HSI client driver options for Nokia modem support, CMT speech, SSI protocol, and a generic HSI/SSI character interface.

## Important Symbols
- `NOKIA_MODEM`: tristate, depends on `HSI && SSI_PROTOCOL && CMT_SPEECH`; supports the modem on Nokia N900/RX-51 hardware.
- `CMT_SPEECH`: tristate, depends on `HSI && SSI_PROTOCOL`; provides Nokia CMT speech protocol support and can build as `cmt_speech`.
- `SSI_PROTOCOL`: tristate, depends on `HSI && PHONET && OMAP_SSI`; enables the SSI protocol, also described as McSAAB.
- `HSI_CHAR`: tristate, depends on `HSI`; provides a generic character device interface for modem serial communication over HSI/SSI.

## Control Flow and Build Flow
Selections in this file drive `drivers/hsi/clients/Makefile`. The dependency chain requires the OMAP SSI controller and Phonet for `SSI_PROTOCOL`, then speech depends on SSI protocol, and Nokia modem depends on both protocol and speech. `HSI_CHAR` is independent of that Nokia stack beyond needing HSI.

## State and Persistence
No runtime state exists. User choices persist in kernel configuration and decide which modules are compiled.

## Dependencies and Integration Points
This file ties protocol/client layering together: the Nokia modem composition driver is not available unless both `ssi_protocol` and `cmt_speech` are buildable. It also exposes `hsi_char` as a simpler diagnostic or general HSI client interface.

## Risks and Edge Cases
- The `NOKIA_MODEM` dependency on `CMT_SPEECH` means probe-time child creation is matched by build-time availability; changing that relationship could cause `device_attach()` deferrals or missing child drivers.
- `SSI_PROTOCOL` is tied to `OMAP_SSI`, so non-OMAP HSI deployments will only get `HSI_CHAR` unless they add compatible protocol support.

## Test Signals
- Kconfig dependency tests should verify `NOKIA_MODEM` is hidden until `SSI_PROTOCOL` and `CMT_SPEECH` are enabled.
- Module builds should produce `nokia-modem.ko`, `cmt_speech.ko`, `ssi_protocol.ko`, and `hsi_char.ko` according to selected tristates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/clients/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/clients/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hsi/clients/Makefile

## Purpose
This Makefile maps HSI client Kconfig symbols to the corresponding object files.

## Important Build Rules
- `obj-$(CONFIG_NOKIA_MODEM) += nokia-modem.o`
- `obj-$(CONFIG_SSI_PROTOCOL) += ssi_protocol.o`
- `obj-$(CONFIG_CMT_SPEECH) += cmt_speech.o`
- `obj-$(CONFIG_HSI_CHAR) += hsi_char.o`

## Control Flow and Build Flow
Kbuild compiles each client object as built-in or module based on its tristate symbol. There are no aggregate objects or subdirectories in this file.

## State and Persistence
No runtime state exists. Build output follows `.config`.

## Dependencies and Integration Points
The rules consume symbols defined in `drivers/hsi/clients/Kconfig`. The resulting modules register `hsi_client_driver` instances that bind to HSI child devices by name/alias.

## Risks and Edge Cases
- Kconfig expresses dependencies, not the Makefile; forcing object builds outside Kconfig could break due to missing protocol/controller dependencies.
- Object names must match module aliases and child device names used by `nokia-modem.c` (`ssi-protocol`, `cmt-speech`) and by HSI board/device declarations.

## Test Signals
- Build each client as `y` and `m` to confirm module naming and link dependencies.
- Confirm `modinfo` aliases for generated modules align with HSI client names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/clients/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/clients/cmt_speech.c -->
# sources/distributed-fs/ceph-client/drivers/hsi/clients/cmt_speech.c

## Purpose
`cmt_speech.c` implements the Nokia CMT speech HSI client. It exposes a single misc character device, `/dev/cmt_speech`, that lets userspace exchange control commands and shared-memory audio/data buffers with a modem over two HSI channels named `speech-control` and `speech-data`. It is layered on top of the SSI protocol slave helpers and uses an mmap page as the userspace/kernel control block plus RX/TX ring buffer area.

## Important APIs, Types, and Functions
- `struct cs_char` is the global character device state: open flag, HSI client pointer, active `cs_hsi_iface`, notification queues, mmap page, async queue, wait queue, and command/data HSI channel IDs.
- `struct cs_hsi_iface` is the active HSI session: HSI client/master pointers, interface/control/data states, mmap config pointer, buffer sizes and offsets, current RX/TX slots, preallocated command/data messages, data wait queue, PM QoS request, and lock.
- Queue helpers `cs_notify()`, `cs_notify_control()`, `cs_notify_data()`, and `cs_pop_entry()` deliver u32 notifications to blocking reads, poll, and fasync.
- Command message helpers `cs_alloc_cmds()`, `cs_claim_cmd()`, `cs_release_cmd()`, `cs_free_cmds()`, and `cs_cmd_destructor()` maintain a pool of four control messages.
- HSI control path: `cs_hsi_read_on_control()`, `cs_hsi_peek_on_control_complete()`, `cs_hsi_read_on_control_complete()`, `cs_hsi_write_on_control()`, and `cs_hsi_write_on_control_complete()`.
- HSI data path: `cs_hsi_read_on_data()`, `cs_hsi_peek_on_data_complete()`, `cs_hsi_read_on_data_complete()`, `cs_hsi_write_on_data()`, and `cs_hsi_write_on_data_complete()`.
- Buffer/session management: `cs_hsi_buf_config()`, `check_buf_params()`, `set_buffer_sizes()`, `cs_hsi_data_enable()`, `cs_hsi_data_disable()`, `cs_hsi_data_sync()`, `cs_hsi_start()`, and `cs_hsi_stop()`.
- Character device operations: `cs_char_open()`, `cs_char_release()`, `cs_char_read()`, `cs_char_write()`, `cs_char_poll()`, `cs_char_ioctl()`, `cs_char_mmap()`, and `cs_char_fasync()`.
- Driver entry points: `cs_hsi_client_probe()`, `cs_hsi_client_remove()`, `cs_char_init()`, and `cs_char_exit()`.

## Control Flow
Probe initializes global `cs_char_data`, resolves HSI channel IDs by name, and registers the misc device. `open()` is exclusive: it allocates one zeroed page, starts the HSI session, claims the HSI port, gets the SSI master client, verifies it is running, and starts a pending control read. Userspace then `mmap()`s the one-page shared area, configures buffers with `CS_CONFIG_BUFS`, uses `write()` to send u32 commands, and reads u32 notifications.

Control reads use a zero-length "peek" async read first, then a real one-word read. Completion releases the command message back to the pool, optionally timestamps RX control messages, enqueues a notification, and immediately re-arms the control read. Control writes are serialized by `SSI_CHANNEL_STATE_WRITING`; the command target bits decide whether a userspace write goes to remote control or local TX-data handling.

Data reads also use a peek read followed by a read into the current RX slot inside the mmap page. On completion, the driver increments `rx_slot`, updates `mmap_cfg->rx_ptr`, wakes data waiters, enqueues `CS_RX_DATA_RECEIVED | slot`, and re-arms reads. Data writes use a TX slot selected by the low command parameter and write `buf_size` bytes from the mmap page.

`CS_CONFIG_BUFS` temporarily moves a configured interface back to opened state, waits for active transfers to finish or time out, validates buffer counts and total mmap size, lays out cache-aligned RX/TX slots after the config block, and starts/stops data reads and CPU latency QoS depending on configured state.

## State and Persistence
State is global and single-open. The misc device only permits one active session via `cs_char_data.opened`. Runtime state includes list-backed control and data notification queues, `dataind_pending`, HSI state bitmasks, mmap config contents visible to userspace, precomputed RX/TX offsets, current slots, wake line state, and PM QoS request. Nothing persists after close; `release()` stops HSI, frees the page, clears queues, and resets `opened`.

## Dependencies and Integration Points
The driver depends on HSI core APIs (`hsi_claim_port`, `hsi_async_read/write`, `hsi_release_port`, `hsi_get_channel_id_by_name`), SSI protocol slave APIs (`ssip_slave_get_master`, `ssip_slave_running`, `ssip_slave_start_tx`, `ssip_slave_stop_tx`, `ssip_slave_put_master`), CMT speech UAPI definitions from `linux/hsi/cs-protocol.h`, miscdevice, mmap VM operations, wait queues, fasync, spinlocks, and CPU latency QoS. It binds as an HSI client named `cmt-speech` with module alias `hsi:cmt-speech`.

## Risks and Edge Cases
- `cs_char_data` is a single global, so multiple CMT speech HSI clients would collide.
- The mmap area is only one page; buffer validation must remain correct or userspace-selected sizes can overlap the config block or exceed the page.
- HSI callbacks and file operations share state under spinlocks and bottom-half disabling; destructor/error paths must release message ownership exactly once.
- `cs_hsi_write_on_control()` returns 0 even after an immediate async write submission error path has called the error handler, which may hide errors from userspace.
- Data reconfiguration depends on `cs_hsi_data_sync()` timing out after 500 ms; slow or stuck controllers can force `-EIO`.
- Notification queue overrun handling drops oldest data indications beyond RX buffer count, so userspace must keep up with reads.

## Test Signals
- Module load should register `/dev/cmt_speech` after the HSI child named `cmt-speech` probes and finds both named channels.
- ABI tests should cover exclusive open, one-page mmap, `CS_GET_STATE`, `CS_GET_IF_VERSION`, `CS_SET_WAKELINE`, `CS_CONFIG_BUFS`, blocking/nonblocking read, poll, fasync, and write command routing.
- HSI tests should verify control read re-arming, remote command writes, data RX slot advancement, TX slot writes, PM QoS activation only while configured, and clean close after pending transfers.
- Fault tests should cover missing channel names, missing SSI master, async read/write errors, signal interruption, buffer overrun, and remove while open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/clients/cmt_speech.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/clients/hsi_char.c -->
# sources/distributed-fs/ceph-client/drivers/hsi/clients/hsi_char.c

## Purpose
`hsi_char.c` implements a generic HSI/SSI character driver. For each bound HSI client, it registers 16 character-device minors, one per HSI channel, and lets userspace perform aligned blocking reads/writes, configure RX/TX HSI parameters, send/receive break frames, and control the wake line.

## Important APIs, Types, and Functions
- Constants: `HSC_DEVS` is 16 channels; `HSC_MSGS` preallocates four messages per opened channel; `max_data_size` module parameter bounds transfer size and must be a power of two from 4 to 65536.
- Minor layout: `HSC_BASEMINOR(id, port_id)` packs HSI controller and port IDs into the base minor; low 4 bits select channel.
- `struct hsc_channel` stores per-channel flags, free/RX/TX message queues, spinlock, HSI client pointer, parent client data, and read/write wait queues.
- `struct hsc_client_data` stores the cdev, open/close mutex, port flags, port use count, HSI client pointer, and all 16 channels.
- Message lifecycle helpers: `hsc_msg_alloc()`, `hsc_msgs_alloc()`, `hsc_msg_free()`, `hsc_free_list()`, `hsc_reset_list()`, `hsc_add_tail()`, and `hsc_get_first_msg()`.
- Completion/destructor callbacks: `hsc_rx_completed()`, `hsc_rx_msg_destructor()`, `hsc_tx_completed()`, `hsc_tx_msg_destructor()`, `hsc_break_received()`, and `hsc_break_req_destructor()`.
- HSI configuration helpers: `hsc_rx_set()`, `hsc_rx_get()`, `hsc_tx_set()`, `hsc_tx_get()`, `hsc_break_request()`, and `hsc_break_send()`.
- File operations: `hsc_open()`, `hsc_release()`, `hsc_read()`, `hsc_write()`, and `hsc_ioctl()`.
- Driver entry points: `hsc_probe()`, `hsc_remove()`, `hsc_init()`, and `hsc_exit()`.

## Control Flow
Module init validates `max_data_size` and registers the HSI client driver named `hsi_char`. Probe allocates `hsc_client_data`, allocates a char-device region for 16 minors based on HSI ID and port ID, initializes channels, and adds a cdev spanning all channels.

Opening a minor selects the channel from the low minor bits, serializes with the parent mutex, enforces exclusive open per channel, claims and sets up the HSI port on first open, increments a use count, and preallocates four scatterlist-backed HSI messages. Reads and writes each allow only one in-flight operation per channel using `HSC_CH_READ`/`HSC_CH_WRITE`. A read takes a free message, sets length and callbacks, submits `hsi_async_read()`, waits for completion queue, copies data to userspace, and returns the message to the free list. A write copies userspace data into a free message, submits `hsi_async_write()`, waits for TX completion, and recycles the message.

`HSC_SET_RX` and `HSC_SET_TX` ioctls validate mode/channel/flow/arbitration values, update the HSI client config, call `hsi_setup()`, and roll back on setup failure. RX frame mode arms break detection. `HSC_SEND_BREAK` sends a break frame. `HSC_SET_PM` starts or stops TX using `hsi_start_tx()` / `hsi_stop_tx()` and tracks wake-line state with `HSC_CH_WLINE`.

Release stops TX if enabled, decrements the port use count, flushes/releases the HSI port on last close, frees all pending/free messages, clears flags, and wakes wait queues.

## State and Persistence
State is per bound HSI client and per opened channel. The major number is global and allocated on first probe. Each channel tracks open/read/write/wake-line bits and list-backed free/RX/TX message pools. The parent use count keeps the HSI port claimed while any channel is open. No state persists after module unload or device removal.

## Dependencies and Integration Points
The driver depends on HSI core async I/O, HSI config structures, the `linux/hsi/hsi_char.h` ioctl ABI, cdev/chrdev registration, wait queues, spinlocks, mutexes, scatterlists, and uaccess. It binds to HSI clients named `hsi_char` through `MODULE_ALIAS("hsi:hsi_char")`.

## Risks and Edge Cases
- Probe/remove do not appear to prevent removal while channels are open; cdev deletion with live file references needs careful lifetime assumptions.
- Blocking reads/writes flush the whole HSI client on signal interruption, which may disrupt other open channels sharing the same port.
- `hsi_flush()` is per client/port rather than per channel, so reset and break handling can affect all channels.
- The global major allocation plus per-port minor packing supports only masked ID/port ranges; IDs beyond the masks collide.
- Reads/writes silently clamp length to `max_data_size`; userspace may need to infer short transfer limits.
- All transfers require 32-bit alignment; unaligned userspace sizes return `-EINVAL`.

## Test Signals
- Module parameter validation should reject non-power-of-two, too-small, and too-large `max_data_size`.
- Device-node tests should verify 16 minors per HSI client and correct channel selection from minor number.
- Functional tests should cover aligned read/write, simultaneous channel opens, exclusive same-channel open, signal interruption, break receive broadcast, `HSC_RESET`, PM wake-line toggling, and RX/TX config rollback on `hsi_setup()` failure.
- Stress tests should exercise message pool exhaustion, port use counting across multiple channels, and controller removal during blocked I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/clients/hsi_char.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/clients/nokia-modem.c -->
# sources/distributed-fs/ceph-client/drivers/hsi/clients/nokia-modem.c

## Purpose
`nokia-modem.c` is an HSI composition driver for Nokia modem hardware such as the N900/RX-51 family. It binds to a DT-described `nokia-modem` HSI client, exports modem control GPIOs for userland-based power management, handles modem reset indication interrupts, and instantiates the `ssi-protocol` and `cmt-speech` child HSI clients on the same port.

## Important APIs, Types, and Functions
- Module parameter `pm` controls whether GPIO-based userland power management is enabled; default is 1.
- `struct nokia_modem_gpio` stores one GPIO descriptor and exported name.
- `struct nokia_modem_device` stores the reset tasklet/IRQ, owning device, GPIO array/count, and child `hsi_client` pointers for SSI protocol and CMT speech.
- `nokia_modem_gpio_probe()` reads all unnamed-index GPIOs and `gpio-names` from DT, requests them as output-low, exports them to sysfs, and creates named links under the device kobject.
- `nokia_modem_gpio_unexport()` removes the sysfs links and unexports descriptors.
- `nokia_modem_rst_ind_isr()` schedules `do_nokia_modem_rst_ind_tasklet()`, which calls `ssip_reset_event()` on the SSI protocol child.
- `nokia_modem_probe()` validates DT, maps the reset IRQ, sets wakeup, optionally exports GPIOs, creates and attaches `ssi-protocol` and `cmt-speech` HSI child devices, and unwinds on error.
- `nokia_modem_remove()` removes children, unexports GPIOs, disables wake, and kills the tasklet.

## Control Flow
Probe requires an OF node. It allocates device state with devm, parses the first IRQ with `irq_of_parse_and_map()`, records trigger flags, initializes a tasklet, requests the IRQ, and enables IRQ wake. If `pm` is enabled, it probes and exports GPIOs. It then copies the parent HSI TX/RX config into `struct hsi_board_info` for `ssi-protocol`, creates the child with `hsi_new_client()`, and forces driver binding with `device_attach()`. The same sequence is repeated for `cmt-speech`. On missing child drivers, `device_attach()` returning 0 is converted to `-EPROBE_DEFER`.

The reset indication IRQ handler does minimal work and defers to the tasklet. The tasklet logs the line change and notifies the SSI protocol child so the protocol layer can reset its state.

Remove tears down children in reverse conceptual order, unexports GPIOs, clears drvdata, disables IRQ wake, and kills the tasklet.

## State and Persistence
Runtime state is per modem device and devm-managed except for child HSI clients, sysfs GPIO exports, IRQ wake state, and tasklet lifecycle. GPIO values may be controlled externally through sysfs while the driver is loaded. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on OF device matching, GPIO descriptor APIs, sysfs GPIO export, IRQ APIs, tasklets, HSI child-client creation/removal, and SSI protocol reset notification. Kconfig requires `HSI`, `SSI_PROTOCOL`, and `CMT_SPEECH`, matching the child drivers it instantiates. OF compatibles include `nokia,n900-modem`, `nokia,n950-modem`, and `nokia,n9-modem`.

## Risks and Edge Cases
- If `pm=0`, `remove()` still calls `nokia_modem_gpio_unexport()` unconditionally; with zero/default GPIO state this loop is harmless only if `gpio_amount` remains zero.
- GPIO export is legacy sysfs ABI; failures after partially exporting GPIOs rely on the probe error path calling full unexport.
- `enable_irq_wake()` return value is not checked, so wake capability failures are silent.
- `device_attach()` is forced immediately for children; missing modules produce probe deferral, and attach errors unwind both children.
- The reset tasklet can race with removal unless IRQ disable/devm cleanup and `tasklet_kill()` ordering remain sufficient.

## Test Signals
- DT tests should cover missing OF node, invalid IRQ, mismatched GPIO and `gpio-names` counts, GPIO request/export failures, and valid Nokia compatibles.
- Probe tests should verify creation and binding of `ssi-protocol` and `cmt-speech` children with inherited HSI configs.
- Runtime tests should toggle the reset indication IRQ and verify `ssip_reset_event()` is called without sleeping in IRQ context.
- Remove/error-path tests should confirm child clients are removed, GPIO sysfs links disappear, IRQ wake is disabled, and no tasklet runs after teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hsi/clients/nokia-modem.c -->
