# Research Report: subset-b-003972

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/elantech.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/elantech.c

## Purpose
`elantech.c` implements the Elantech PS/2 touchpad protocol family and, when supported, routes newer devices to the `elan_i2c` SMBus companion path. It detects Elantech hardware via a PS/2 "magic knock", queries firmware/capability registers, selects hardware-version-specific packet decoders, configures absolute mode, exposes low-level debug/register sysfs attributes, and reports absolute, semi-multitouch, full multitouch, buttonpad, rocker, and optional TrackPoint events through the input subsystem.

## Important APIs, Types, And Functions
The file centers on `struct elantech_data` and `struct elantech_device_info` from `elantech.h`. Register and query helpers include `synaptics_send_cmd()`, `elantech_send_cmd()`, `elantech_ps2_command()`, `elantech_read_reg()`, `elantech_write_reg()`, and v4-specific `elantech_get_resolution_v4()`. Runtime packet processing is routed through `elantech_process_byte()`, which dispatches to `elantech_report_absolute_v1()`, `_v2()`, `_v3()`, `_v4()`, or `elantech_report_trackpoint()`. Initialization entry points are `elantech_detect()`, `elantech_init()`, `elantech_init_ps2()`, and `elantech_init_smbus()`.

## Control Flow
Detection resets/disables the mouse, sends the Elantech knock, validates the returned signature, and confirms the firmware version does not look like a false-positive Logitech response. Initialization resets the device, calls `elantech_query_info()`, derives hardware version and quirks in `elantech_set_properties()`, then either creates an SMBus companion or configures PS/2 absolute mode. PS/2 setup allocates private state, builds a parity table, writes version-specific absolute-mode registers, sets input capabilities/ranges, creates sysfs attributes, optionally registers a second TrackPoint `input_dev`, and installs `elantech_process_byte()` as the psmouse protocol handler. Each complete packet is validated for parity, debounce, CRC-dependent signatures, or packet type before input events are emitted.

## State And Persistence
State is per-device in `psmouse->private`: cached registers, parity table, multitouch coordinates, Y max/trace width, TrackPoint input device, and queried hardware info. Sysfs can read/write selected registers and toggle debug/parity/CRC fields for the current device only. There is no persistent storage beyond module parameters and DMI-based quirks. Reconnect re-detects, may apply a DMI disable/enable cycle, and re-enters absolute mode.

## Dependencies And Integration Points
The driver integrates with `psmouse-base.c` as a `PSMOUSE_ELANTECH` or `PSMOUSE_ELANTECH_SMBUS` protocol. It uses libps2 command helpers, Linux input and input-mt APIs, DMI tables for model quirks, I2C/software-node APIs for SMBus handoff, and `psmouse_smbus_init()/cleanup()` for companion lifecycle. It also depends on `elan_i2c` properties for host-notify devices.

## Risks
Hardware behavior is highly revision-specific: incorrect signatures, CRC flags, DMI quirks, or register writes can cause false detection, lost sync, cursor jumps, or unusable absolute mode. The SMBus path intentionally leaves "breadcrumbs" when the adapter is not ready, so cleanup and rescan behavior are sensitive. Sysfs register writes can alter live hardware state. TrackPoint packet filtering discards out-of-range motion to avoid jumps, so regressions may appear as lost pointing-stick movement.

## Test Signals
Useful signals include `psmouse_info()` hardware-version/capability/sample logs, successful creation/removal of Elantech sysfs attributes, correct `ABS_X/Y`, `ABS_MT_*`, `BTN_TOOL_*`, clickpad, and optional TrackPoint events under `evtest`, stable suspend/resume reconnect, correct fallback to bare PS/2 when query/setup fails, and successful SMBus companion creation with PS/2-side input suppressed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/elantech.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/elantech.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/elantech.h

## Purpose
`elantech.h` defines the constants, packet identifiers, state structures, and public entry points used by the Elantech PS/2 and SMBus bridge implementation. It is the protocol contract between `elantech.c`, `psmouse-base.c`, and conditional SMBus support.

## Important APIs, Types, And Functions
Key definitions include query codes such as `ETP_FW_VERSION_QUERY`, register opcodes, retry/delay values, register bit masks, v1/v2 coordinate ranges, packet type constants, `ETP_MAX_FINGERS`, bus-provider constants, and the `ETP_NEW_IC_SMBUS_HOST_NOTIFY()` macro. `struct finger_pos` stores per-finger coordinates. `struct elantech_device_info` captures firmware version, hardware version, geometry, resolution, bus, feature booleans, quirks, and the selected command helper. `struct elantech_data` is live driver state: cached registers, parity table, multitouch coordinates, optional TrackPoint device, and a saved original rate setter. Exported functions are `elantech_detect()`, `elantech_init_ps2()`, `elantech_init()`, and `elantech_init_smbus()`.

## Control Flow
This header does not execute control flow directly, but it drives `elantech.c` branching. Hardware version and packet constants decide decoder selection; bus constants and host-notify macro decide whether `elantech_init()` should prefer SMBus; conditional compilation makes `elantech_init()` return `-ENOSYS` when PS/2 Elantech support is disabled.

## State And Persistence
The structures are per-device runtime state. Cached register fields mirror live hardware and can be exposed through sysfs. No fields are persisted across driver unload or reboot.

## Dependencies And Integration Points
The declarations depend on `struct psmouse` and input device types included by users of the header. `CONFIG_MOUSE_PS2_ELANTECH` controls whether PS/2 initialization is compiled. SMBus initialization is declared unconditionally for callers but defined when the relevant implementation is enabled.

## Risks
The constants encode fragile hardware knowledge. Incorrect coordinate bounds or bit masks can misreport touch geometry. The host-notify macro is a policy gate for routing devices away from PS/2, so mistakes affect driver binding and user-visible input devices.

## Test Signals
Compile coverage under different Kconfig combinations is important. Runtime validation should confirm `struct elantech_device_info` fields match log output, input abs ranges match actual hardware, and SMBus-capable firmware follows the intended initialization path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/elantech.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/focaltech.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/focaltech.c

## Purpose
`focaltech.c` implements support for FocalTech PS/2 touchpads identified by PNP IDs. It intentionally detects devices even when full support is unavailable so the generic psmouse probe sequence can avoid confusing the touchpad and can fall back to basic PS/2 behavior.

## Important APIs, Types, And Functions
The detector is `focaltech_detect()`, using `psmouse_matches_pnp_id()` against `FLT0101`, `FLT0102`, and `FLT0103`. With `CONFIG_MOUSE_PS2_FOCALTECH`, it defines packet type constants `FOC_TOUCH`, `FOC_ABS`, and `FOC_REL`, per-finger state in `struct focaltech_finger_state`, aggregate hardware state in `struct focaltech_hw_state`, and private geometry/state in `struct focaltech_data`. Runtime handlers are `focaltech_process_byte()`, `focaltech_process_packet()`, and per-packet processors for touch bitmap, absolute position, and relative updates. Setup helpers include `focaltech_read_register()`, `focaltech_read_size()`, `focaltech_switch_protocol()`, and `focaltech_set_input_params()`.

## Control Flow
Initialization allocates private state, resets the device, reads touchpad size, switches protocol through repeated PS/2 command sequences, configures input as a buttonpad multitouch device, and installs a 6-byte packet handler. A touch packet updates active finger bits and clears validity on release. Absolute packets seed a finger coordinate and width. Relative packets increment one or two tracked fingers. After each packet, `focaltech_report_state()` reports all valid active slots and clickpad button state.

## State And Persistence
The driver stores current per-finger active/valid flags, coordinates, last width, pressed state, and max X/Y in `psmouse->private`. Unsupported set-rate, set-resolution, and set-scale callbacks are replaced with no-ops because generic PS/2 tuning can confuse devices. No state persists beyond the device instance.

## Dependencies And Integration Points
It integrates with `psmouse-base.c` as `PSMOUSE_FOCALTECH`, uses libps2 command helpers, input-mt slot APIs, and PNP firmware IDs exposed on the serio device. The psmouse core always probes FocalTech early as a safe PNP-only check.

## Risks
The protocol is only partially known: packet validation is minimal and size calculation is explicitly uncertain. Relative packets can reference invalid finger IDs, handled by logging but otherwise tolerated. Generic PS/2 command sequences are disabled because they can upset hardware, so regressions may show up as complete device lockups rather than minor misconfiguration.

## Test Signals
Check detection only on matching PNP IDs, successful size read and protocol switch, `INPUT_PROP_BUTTONPAD`, five MT slots, clamped coordinates, Y inversion, button press reporting, disabled resync, and reconnect recovery after reset. Negative tests should ensure non-FocalTech devices are not disturbed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/focaltech.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/focaltech.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/focaltech.h

## Purpose
`focaltech.h` exposes the FocalTech detector and, when enabled, the full initializer to the psmouse core.

## Important APIs, Types, And Functions
The exported API is `focaltech_detect(struct psmouse *, bool)` and conditionally `focaltech_init(struct psmouse *)`. If `CONFIG_MOUSE_PS2_FOCALTECH` is disabled, the inline initializer returns `-ENOSYS` while detection remains available from `focaltech.c`.

## Control Flow
The header lets `psmouse-base.c` probe FocalTech devices early regardless of whether full protocol support is compiled. When support is disabled, the core can detect the device and then restrict probing/fall back without calling an unavailable initializer.

## State And Persistence
No state is defined here. All state lives in `focaltech.c` private allocations.

## Dependencies And Integration Points
It depends on `struct psmouse` from `psmouse.h` users and Kconfig selection. The split between detect and init is an important integration point because detection has side-effect-avoidance semantics in `psmouse_extensions()`.

## Risks
If callers assume detection implies initialization support, disabled Kconfig builds can return `-ENOSYS`. The header's policy makes detection broader than implementation availability by design.

## Test Signals
Build both with and without `CONFIG_MOUSE_PS2_FOCALTECH`, verify symbol availability, and confirm fallback behavior remains clean when `focaltech_init()` is the inline `-ENOSYS` stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/focaltech.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/gpio_mouse.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/gpio_mouse.c

## Purpose
`gpio_mouse.c` implements a platform driver that simulates a relative mouse from GPIO lines. Four required GPIOs represent directional movement and up to three optional GPIOs represent buttons.

## Important APIs, Types, And Functions
`struct gpio_mouse` stores scan interval and GPIO descriptors for `up`, `down`, `left`, `right`, `button-left`, `button-middle`, and `button-right`. `gpio_mouse_probe()` reads device properties, acquires GPIOs with devm helpers, allocates an input device, configures relative axes/buttons, installs polling with `input_setup_polling()`, and registers the device. `gpio_mouse_scan()` reads GPIO values and reports `REL_X`, `REL_Y`, and present buttons.

## Control Flow
On platform probe, the driver reads `scan-interval-ms`, defaults invalid values to 50 ms, requires all four direction GPIOs, allows absent button GPIOs, and registers a polled input device. While the input device is open, the input polling core calls `gpio_mouse_scan()` at the configured interval. X movement is `right - left`; Y movement is `down - up`.

## State And Persistence
State is simple and devm-managed: GPIO descriptors and scan period live for the platform device lifetime. No counters or persisted calibration are stored. Input state is reported each poll from current GPIO values.

## Dependencies And Integration Points
The driver binds through platform/OF compatible `"gpio-mouse"` and module alias `platform:gpio_mouse`. It uses the GPIO descriptor consumer API, device properties, and Linux input polling.

## Risks
Movement is one unit per poll, so scan interval directly controls pointer speed. Simultaneously active opposite directions cancel out. GPIO polarity comes from firmware descriptors; wrong active-low configuration in board data will invert behavior. Optional button debug text appears to list missing buttons, so logs should be interpreted carefully.

## Test Signals
Validate DT/property binding, default scan warning, failure when required GPIOs are missing, correct capabilities for only present buttons, stable polling open/close behavior, and `evtest` relative deltas for each direction and button state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/gpio_mouse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/lifebook.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/lifebook.c

## Purpose
`lifebook.c` supports Fujitsu Lifebook/Panasonic touchscreen-like PS/2 devices that provide absolute coordinates and, on some systems, a separate relative touchpad stream. It relies on DMI identification rather than active probing because detection should not disturb normal PS/2 devices.

## Important APIs, Types, And Functions
`struct lifebook_data` stores an optional second relative `input_dev`. `lifebook_module_init()` runs DMI matching and sets global feature flags such as `lifebook_present`, `desired_serio_phys`, and `lifebook_use_6byte_proto`. `lifebook_detect()` gates protocol selection. `lifebook_init()` enters absolute mode, configures the main absolute device, optionally creates the relative device via `lifebook_create_relative_device()`, and installs `lifebook_process_byte()`. Mode helpers are `lifebook_absolute_mode()`, `lifebook_relative_mode()`, and `lifebook_set_resolution()`.

## Control Flow
At module init, DMI table callbacks can restrict matching to `isa0060/serio3` or select a 6-byte protocol. During psmouse probing, detection succeeds only on matching DMI and desired serio path. Initialization sends the magic `SETRES` value for absolute output, clears default relative capabilities on the primary input device, configures absolute axes, creates a secondary relative device unless restricted to one serio port, and then handles packets. The packet handler distinguishes relative packets via bit 3 of byte 0; 6-byte absolute packets are validated byte-by-byte before reporting 12-bit coordinates, while 3-byte mode reports 10-bit coordinates.

## State And Persistence
Global DMI-derived booleans persist for the module lifetime. Per-device state only stores the optional secondary input device. Reconnect re-runs absolute-mode setup. Disconnect resets the PS/2 device, unregisters the relative device, and frees private data.

## Dependencies And Integration Points
The file integrates as `PSMOUSE_LIFEBOOK`, called early in psmouse extension probing because its detection is DMI-only. It uses libps2, DMI, input abs/rel APIs, and psmouse standard motion/button helpers for the relative device.

## Risks
DMI matching is broad and platform-specific; false positives could hijack a regular PS/2 mouse. The 6-byte protocol uses validation while psmouse `pktsize` remains 3 because `POLL` returns 3 bytes, which can surprise resync logic. Absolute-mode `SETRES` is expected to fail but still has required side effects.

## Test Signals
Verify DMI match and serio restriction, absolute coordinate ranges of 1024 or 4096, optional secondary relative device registration, packet validation failure paths, relative packet handling, reconnect re-entering absolute mode, and fallback to relative mode if second device creation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/lifebook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/lifebook.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/lifebook.h

## Purpose
`lifebook.h` provides the psmouse-facing declarations for the Lifebook PS/2 touchscreen driver and hides module initialization when the feature is disabled.

## Important APIs, Types, And Functions
It declares `lifebook_detect()`, `lifebook_init()`, and conditionally `lifebook_module_init()`. Without `CONFIG_MOUSE_PS2_LIFEBOOK`, `lifebook_module_init()` is an empty inline, allowing `psmouse_init()` to call it unconditionally.

## Control Flow
The header participates in startup by allowing psmouse core to initialize Lifebook DMI state before registering the serio driver. Protocol detection and initialization are invoked later from the psmouse protocol table when configured.

## State And Persistence
No state is declared here; DMI and per-device state are private to `lifebook.c`.

## Dependencies And Integration Points
It depends on `struct psmouse` consumers and Kconfig. The unconditional declaration of detect/init pairs with conditional table entries in `psmouse-base.c`.

## Risks
The no-op module init under disabled Kconfig must remain semantically harmless. Any mismatch between header stubs and psmouse table guards would become a build or link failure.

## Test Signals
Build with Lifebook support enabled and disabled. Confirm `psmouse_init()` compiles in both cases and DMI matching only occurs when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/lifebook.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/logips2pp.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/logips2pp.c

## Purpose
`logips2pp.c` implements Logitech PS/2++ and PS2T++ extensions for legacy Logitech mice and touchpads. It detects model IDs, enables extended packets when supported, maps model features to input capabilities, decodes extra wheel/button packets, and exposes SmartScroll control.

## Important APIs, Types, And Functions
`struct ps2pp_info` maps model number to kind and feature bits. `ps2pp_detect()` performs model detection and optional protocol setup. `get_model_info()` provides the model table. `ps2pp_cmd()` sends sliced PS2++ commands. Runtime packet decoding is in `ps2pp_process_byte()`. Setup and policy helpers include `ps2pp_set_model_properties()`, `ps2pp_setup_protocol()`, `ps2pp_set_resolution()`, `ps2pp_set_smartscroll()`, and sysfs show/store handlers for `smartscroll`.

## Control Flow
Detection sends a Logitech query sequence, derives model and button count, looks up model metadata, and attempts PS2++ activation. TouchPad 3 uses a dedicated RAM-unprotect/feature-enable sequence; other models use PS2++ magic commands and response validation. If extended mode is active, the driver installs a 3-byte handler and optional SmartScroll sysfs file. The packet handler distinguishes Logitech extended packets from standard PS/2 packets and reports wheel, horizontal wheel, side/extra/task/back/forward buttons, or normal relative movement.

## State And Persistence
State mostly lives in core `struct psmouse`: model number, name/vendor, `smartscroll`, protocol handler, packet size, and resolution callback. The sysfs `smartscroll` attribute persists only for the device lifetime and is removed on disconnect.

## Dependencies And Integration Points
The driver integrates as `PSMOUSE_PS2PP` in the psmouse protocol table. It uses psmouse standard button/motion helpers, libps2 sliced commands, and the generic psmouse sysfs attribute mechanism.

## Risks
Detection can identify a Logitech mouse but fail to enable PS2++, returning `-ENXIO` so the core can continue probing. Unknown models log a warning and may be treated as non-PS2++. SmartScroll and 800 dpi setup use command sequences that may be device-specific. Extended packet decoding relies on bit signatures and may ignore unknown packet subtypes.

## Test Signals
Check model-specific capability bits, successful creation/removal of `smartscroll`, correct decoding of vertical/horizontal wheel and extra buttons, fallback behavior when extended mode is unavailable, 800 dpi resolution behavior, and no regression for standard PS/2 packet reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/logips2pp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/logips2pp.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/logips2pp.h

## Purpose
`logips2pp.h` declares the Logitech PS/2++ detector for the psmouse core.

## Important APIs, Types, And Functions
The only exported function is `ps2pp_detect(struct psmouse *psmouse, bool set_properties)`.

## Control Flow
`psmouse-base.c` references this declaration in the protocol table when `CONFIG_MOUSE_PS2_LOGIPS2PP` is enabled. The detector both identifies Logitech models and may initialize extended mode when `set_properties` is true.

## State And Persistence
No state is declared in this header. Runtime state is kept in `psmouse` fields and device sysfs created by `logips2pp.c`.

## Dependencies And Integration Points
It depends on callers having `struct psmouse` available. The header is intentionally minimal because Logitech support is table-driven inside the implementation file.

## Risks
Any signature change to `ps2pp_detect()` must be kept synchronized with the psmouse protocol table. There are no compile-time stubs here, so Kconfig guards must prevent unresolved references.

## Test Signals
Build with Logitech PS2++ support enabled and disabled, and verify the protocol table only references the function in enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/logips2pp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/maplemouse.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/maplemouse.c

## Purpose
`maplemouse.c` is the Sega Dreamcast Maple bus mouse driver. It binds Maple mouse devices, periodically requests condition data while the input device is open, and reports relative X/Y, wheel, and three buttons.

## Important APIs, Types, And Functions
`struct dc_mouse` stores the input device and Maple device. `probe_maple_mouse()` allocates/registers input state and attaches driver data. `dc_mouse_open()` and `dc_mouse_close()` start and stop `maple_getcond_callback()` polling. `dc_mouse_callback()` decodes the Maple response buffer. `remove_maple_mouse()` unregisters input and clears Maple driver data. Module lifecycle uses `maple_driver_register()` and `maple_driver_unregister()`.

## Control Flow
Probe allocates `dc_mouse` and `input_dev`, sets key/relative capability bitmaps, wires open/close callbacks, registers input, and stores driver data. Opening the input device schedules condition callbacks at `HZ/50`; closing sets interval 0. Each callback reads buttons from `res[8]` and relative axes from 16-bit fields at offsets 12, 14, and 16, subtracting 512 from each axis before reporting events.

## State And Persistence
Per-device state is only the `dc_mouse` object and driver data on the Maple device. Polling is active only while opened. No calibration or persistent state exists.

## Dependencies And Integration Points
The driver depends on Linux Maple bus APIs and the input subsystem. It binds devices advertising `MAPLE_FUNC_MOUSE`.

## Risks
The callback casts unaligned response bytes to `unsigned short *`, which is architecture-sensitive but historically tied to Dreamcast. Button bit mapping is compact and unusual (`BTN_MIDDLE` uses `buttons & 9`), so behavior should be checked against actual Maple reports. Buffer layout assumptions depend on Maple core guarantees.

## Test Signals
Verify Maple probe/remove, open starts callbacks and close stops them, relative deltas center at 512, wheel events report from the Z field, button mapping matches hardware, and unplug/removal clears callbacks before freeing state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/maplemouse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/psmouse-base.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/psmouse-base.c

## Purpose
`psmouse-base.c` is the central PS/2 mouse serio driver. It owns generic PS/2 packet handling, protocol probing, device lifecycle, sysfs controls, reconnect/resync behavior, module parameters, and integration with specialized protocol modules such as Elantech, Synaptics, FocalTech, Lifebook, Logitech PS2++, and Sentelic.

## Important APIs, Types, And Functions
Public helpers include `psmouse_from_serio()`, `psmouse_reset()`, `psmouse_set_state()`, `psmouse_set_resolution()`, `psmouse_activate()`, `psmouse_deactivate()`, `psmouse_matches_pnp_id()`, and standard reporting helpers. The protocol table `psmouse_protocols[]` maps `enum psmouse_type` to detect/init callbacks and policy flags. Core receive flow uses `psmouse_pre_receive_byte()`, `psmouse_receive_byte()`, `psmouse_handle_byte()`, and default `psmouse_process_byte()`. Lifecycle functions are `psmouse_connect()`, `psmouse_disconnect()`, `psmouse_cleanup()`, `__psmouse_reconnect()`, and `psmouse_switch_protocol()`. Sysfs handlers expose protocol, rate, resolution, reset-after, and resync-time controls.

## Control Flow
On serio connect, the driver deactivates a pass-through parent if needed, allocates `psmouse` and `input_dev`, opens serio, probes for a mouse ID, applies module defaults, and calls `psmouse_switch_protocol()`. Automatic extension probing follows a carefully ordered sequence to avoid devices upsetting each other: safe PNP/DMI checks first, then virtual/touchpad/vendor protocols, then standard IntelliMouse variants, then bare PS/2 fallback. If the selected protocol is not an SMBus companion, the input device is registered and stream mode is enabled. Incoming bytes pass through error/OOB filtering, packet accumulation, protocol handler dispatch, bad-data resync accounting, and optional workqueue resync.

## State And Persistence
`struct psmouse` stores protocol, device names, packet buffer, state machine, timing counters, module-default-derived rate/resolution/reset/resync settings, callbacks, pass-through hooks, and protocol private data. Module parameters persist for the module lifetime and seed new devices. Sysfs changes mutate live device state and may switch protocol by allocating a replacement input device.

## Dependencies And Integration Points
The driver sits between serio/libps2 and input. It includes all protocol headers and conditionally compiles protocol table entries based on Kconfig. It also initializes Lifebook/Synaptics module state and the psmouse SMBus notifier bridge.

## Risks
Probe ordering is fragile because some command sequences confuse other devices. Resync/reconnect races require the global `psmouse_mutex`, serio receive pausing, and work cancellation. Protocol switching must destroy child pass-through ports, preserve fallback behavior, and avoid registering input devices for SMBus companions. Bad packet thresholds can cause reconnect storms or leave devices disabled if enable retries fail.

## Test Signals
Exercise module parameters, protocol auto-detection and forced sysfs switching, standard PS/2/IMPS/IMEX packet decoding, OOB extra buttons, pass-through parent deactivation/reactivation, suspend cleanup, reconnect and fast reconnect, resync after delayed packets, SMBus-companion suppression, and Kconfig combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/psmouse-base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/psmouse-smbus.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/psmouse-smbus.c

## Purpose
`psmouse-smbus.c` is a bridge for PS/2 devices that expose a higher-bandwidth SMBus/I2C companion interface. It creates I2C client devices, tracks their lifecycle, suppresses PS/2 event reporting, and triggers serio rescans when host-notify-capable adapters or companion clients appear/disappear.

## Important APIs, Types, And Functions
`struct psmouse_smbus_dev` records board info, owning `psmouse`, created `i2c_client`, list node, dead flag, and whether PS/2 deactivation is needed. Public functions are `psmouse_smbus_init()`, `psmouse_smbus_cleanup()`, `psmouse_smbus_module_init()`, and `psmouse_smbus_module_exit()`. Internal lifecycle functions include `psmouse_smbus_check_adapter()`, `psmouse_smbus_detach_i2c_client()`, notifier callback, `psmouse_smbus_create_companion()`, `psmouse_smbus_disconnect()`, and asynchronous removal work.

## Control Flow
Module init creates an unbound workqueue and registers an I2C bus notifier. Protocol drivers call `psmouse_smbus_init()` with board information; the bridge stores a list entry, optionally deactivates PS/2, installs dummy packet/reconnect/disconnect callbacks, disables resync, and scans existing I2C adapters for SMBus Host Notify support. If a client is created, a stateless device link connects it to the serio device. If no adapter is ready and breadcrumbs are allowed, the list entry remains so future adapter notifications trigger serio rescan. Client removal marks the companion dead, removes links, and rescans PS/2; PS/2 disconnect schedules asynchronous I2C unregister to avoid mutex deadlocks.

## State And Persistence
Global state is the `psmouse_smbus_list`, mutex, notifier, and workqueue. Per-companion state persists only while either the PS/2 owner or I2C client is alive. Platform data is duplicated and freed if no client is created.

## Dependencies And Integration Points
It integrates with protocol drivers such as Elantech and Synaptics via `psmouse_smbus_init()`, with I2C core through bus notifiers and `i2c_new_scanned_device()`, with serio through rescans, and with psmouse lifecycle callbacks.

## Risks
Adapter scanning cannot prove the target device is present before PS/2 reset, so it may try host-notify adapters opportunistically. Removal races with I2C adapter teardown are explicitly unresolved. Device-link creation failure only logs a warning. Breadcrumb cleanup must be called on failed protocol setup to avoid stale list entries.

## Test Signals
Verify module init/exit cleanup, delayed adapter arrival triggering rescan, successful I2C client creation and device link, `-EAGAIN` breadcrumb behavior, PS/2 input suppression, asynchronous unregister on disconnect, client-removal rescan, and cleanup after failed protocol init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/psmouse-smbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/psmouse.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/psmouse.h

## Purpose
`psmouse.h` defines the shared PS/2 mouse core contract: command constants, return values, state/type enums, protocol descriptor, live device structure, sysfs attribute helpers, logging macros, and optional SMBus bridge APIs.

## Important APIs, Types, And Functions
It defines PS/2 command encodings such as `PSMOUSE_CMD_GETID`, `PSMOUSE_CMD_SETRATE`, and `PSMOUSE_CMD_RESET_BAT`, response constants, `enum psmouse_state`, `psmouse_ret_t`, `enum psmouse_scale`, and `enum psmouse_type`. `struct psmouse_protocol` describes detection/init behavior and policy flags. `struct psmouse` is the core per-device object containing private protocol state, input device, ps2dev, packet buffer, callbacks, state, tunables, pass-through hooks, and reconnect hooks. `struct psmouse_attribute` and `PSMOUSE_DEFINE_*` macros standardize per-protocol sysfs files.

## Control Flow
The header enables protocol modules to plug into psmouse by setting callbacks and returning `PSMOUSE_GOOD_DATA`, `PSMOUSE_FULL_PACKET`, or `PSMOUSE_BAD_DATA` from packet handlers. Attribute macros route sysfs show/store through psmouse helper functions, which can protect operations by deactivating devices.

## State And Persistence
`struct psmouse` fields persist for the lifetime of a serio-bound device. Module parameters in `psmouse-base.c` seed some fields, while protocol modules fill `private` and callbacks. The header itself stores no data.

## Dependencies And Integration Points
The contract spans serio, libps2, input, workqueue, protocol modules, and the optional SMBus bridge. When `CONFIG_MOUSE_PS2_SMBUS` is disabled, inline no-op stubs keep callers buildable while preventing companion creation.

## Risks
Callback contracts are tight: wrong `pktsize`, handler return values, or state transitions can break resync and reconnect. The attribute macros assume matching show/set declarations. Protocol type ordering matters because `PSMOUSE_AUTO` must remain last for max-protocol logic.

## Test Signals
Build all relevant Kconfig combinations, validate protocol table type values in input IDs, exercise sysfs attributes with protected deactivation, verify logging includes serio device context, and confirm SMBus stubs behave as no-ops when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/psmouse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/rpcmouse.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/rpcmouse.c

## Purpose
`rpcmouse.c` implements the Acorn RiscPC host mouse driver. It reads hardware cursor counters and button state on each VSYNC interrupt and reports relative movement through the input subsystem.

## Important APIs, Types, And Functions
Global state consists of last X/Y counter values and the single `input_dev`. `rpcmouse_irq()` reads `IOMD_MOUSEX`, `IOMD_MOUSEY`, and the button register, computes deltas, and reports `REL_X`, inverted `REL_Y`, and left/middle/right buttons. `rpcmouse_init()` allocates/registers the input device and requests `IRQ_VSYNCPULSE`; `rpcmouse_exit()` frees the IRQ and unregisters input.

## Control Flow
Module init allocates the device, fills identity and capability bitmaps, captures initial counter values, requests a shared VSYNC IRQ, and registers input. Each interrupt computes movement since the last interrupt and updates the stored counters. Exit reverses IRQ and input registration.

## State And Persistence
The only runtime state is the previous hardware counter values and input device pointer. There is no per-open behavior, calibration, or persistent storage.

## Dependencies And Integration Points
The driver is architecture-specific, depending on ARM RiscPC headers, IOMD hardware registers, `IRQ_VSYNCPULSE`, raw MMIO reads, and the input subsystem.

## Risks
Counter wraparound and interrupt cadence determine delta correctness. The driver assumes fixed hardware addresses and button bit polarity. Requesting a shared VSYNC IRQ means handler behavior must remain quick and unconditional.

## Test Signals
On supported hardware, verify IRQ registration, stable deltas for movement, Y direction, button mapping, no events after module unload, and clean failure if IRQ allocation or input registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/rpcmouse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/sentelic.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/sentelic.c

## Purpose
`sentelic.c` implements the Sentelic Finger Sensing Pad PS/2 protocol. It detects FSP hardware, accesses proprietary registers, configures relative or absolute/multitouch reporting depending on hardware revision, decodes 4-byte packets, and exposes sysfs controls for low-level register access, scroll zones, on-pad click behavior, page selection, flags, and driver version.

## Important APIs, Types, And Functions
Register helpers include `fsp_reg_read()`, `fsp_reg_write()`, `fsp_reg_write_enable()`, `fsp_page_reg_read()`, and `fsp_page_reg_write()`, with command-value sanitizers `fsp_test_swap_cmd()` and `fsp_test_invert_cmd()`. Device queries include `fsp_get_version()`, `fsp_get_revision()`, `fsp_get_sn()`, and `fsp_get_buttons()`. Configuration helpers are `fsp_opc_tag_enable()`, `fsp_onpad_vscr()`, `fsp_onpad_hscr()`, and `fsp_activate_protocol()`. Packet handling is in `fsp_process_byte()`. Entry points are `fsp_detect()` and `fsp_init()`.

## Control Flow
Detection reads `FSP_REG_DEVICE_ID` and requires value `0x01`. Initialization reads version/revision/serial, allocates `struct fsp_data`, installs psmouse callbacks, activates protocol, configures input bits, and creates a sysfs attribute group. Activation first enters IntelliMouse Explorer 4-byte packet mode. Older hardware is configured for relative packets, button/scroll output, OPC tags, and scroll zones. C0-or-newer hardware enables absolute one-finger/two-finger continuous reporting. The packet handler decodes absolute, normal, and normal-OPC packet classes; absolute mode reports semi-MT slots and button/touch tool state, while normal packets translate wheel/horizontal scroll/back/forward and then reuse standard PS/2 reporting.

## State And Persistence
Per-device state in `struct fsp_data` records version, revision, button mode, flags, scroll enable booleans, last register read, and last multitouch finger. Sysfs writes mutate live registers and private flags but are not persisted. Disconnect removes sysfs, disables OPC/scroll features, and frees private state.

## Dependencies And Integration Points
The driver integrates as `PSMOUSE_FSP`, uses psmouse activation/deactivation around register reads, libps2 low-level byte commands, Linux input/input-mt APIs, and constants from `sentelic.h`.

## Risks
Register access relies on carefully ordered byte sequences and on avoiding values that collide with sample-rate or PS/2 command bytes. Some sysfs handlers do not fail the store when scroll configuration helpers fail. Older/newer hardware modes differ substantially, so version detection mistakes can disable useful reporting. Firmware workarounds for MFMC finger bits and finger-up noise are necessary to avoid stuck slots or cursor jumps.

## Test Signals
Check ID/version/revision logs, successful sysfs group creation/removal, register read/write/page operations, scroll toggles, OPC flag filtering, correct 4-byte packet mode, relative wheel/back/forward events on older hardware, absolute/semi-MT slots on newer hardware, reconnect reactivation, and cleanup disabling device features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/sentelic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/sentelic.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/sentelic.h

## Purpose
`sentelic.h` defines Sentelic Finger Sensing Pad register addresses, bit masks, packet type encodings, hardware revision constants, private runtime state, and psmouse entry points.

## Important APIs, Types, And Functions
The header defines information/control registers such as `FSP_REG_DEVICE_ID`, `FSP_REG_VERSION`, `FSP_REG_SYSCTL1`, `FSP_REG_SYSCTL5`, `FSP_REG_ONPAD_CTL`, and `FSP_REG_SWC1`; bit masks for register clock, packet modes, OPC tags, scroll zones, absolute packet output, and button flags; packet type constants shifted by `FSP_PKT_TYPE_SHIFT`; revision identifiers from A4 through E0; and `struct fsp_data`. It declares `fsp_detect()` and `fsp_init()`.

## Control Flow
Constants from this header drive `sentelic.c` register programming, packet class dispatch, and version-specific mode selection. `struct fsp_data` fields are updated by sysfs and packet processing to guide later event filtering.

## State And Persistence
The declared private state is per psmouse device and stores version/revision, button mode, flags, scroll state, last register readback, and last multitouch finger. No persistent storage is defined.

## Dependencies And Integration Points
The declarations are guarded by `__KERNEL__` and integrate with psmouse only inside the kernel. The header assumes `BIT()` and `struct psmouse` are available from including context.

## Risks
Register bit definitions are hardware contracts; wrong values can enable incompatible packet formats or prevent register writes. The packed first-byte button/multitouch definitions alias middle button with second-finger indication in MFMC mode, so packet interpretation must use context.

## Test Signals
Build coverage, version-specific mode checks, packet type decoding, and sysfs-controlled field updates in `struct fsp_data` should be validated against real or emulated packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/sentelic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/sermouse.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/sermouse.c

## Purpose
`sermouse.c` implements a serio driver for RS-232 serial mouse protocols: Mouse Systems, Sun, Microsoft, Logitech M+, Microsoft wheel, Logitech wheel-plus, and Logitech MZ++ variants. It decodes byte streams into relative movement, wheel, horizontal wheel, and button events.

## Important APIs, Types, And Functions
`struct sermouse` stores the input device, byte buffer, byte count, protocol type, last byte time, and phys path. `sermouse_connect()` allocates and registers input for matching serio IDs. `sermouse_interrupt()` resets packet assembly after idle gaps and dispatches each byte to `sermouse_process_msc()` or `sermouse_process_ms()`. `sermouse_process_msc()` handles Mouse Systems/Sun 5-byte-style data with prediction. `sermouse_process_ms()` handles Microsoft/Logitech families, including middle/side/extra buttons and wheel packets. `sermouse_disconnect()` closes serio and unregisters input.

## Control Flow
The serio ID table binds RS232 mouse protocols. Connect chooses a human-readable name from protocol type, sets capabilities based on `serio->id.extra`, opens serio, and registers input. Interrupt processing treats bytes after 100 ms idle as a new packet. Microsoft-style packets restart when bit 6 is set; MSC/Sun packets require `0x80` signature in the first byte. The handlers emit partial predicted movement during packet assembly to improve update rate and call `input_sync()` after each processed byte.

## State And Persistence
Per-device state includes the assembly buffer, count, inferred protocol type, last timestamp, and input device. The Microsoft protocol can promote `SERIO_MS` to `SERIO_MP` when extended bytes appear. No state persists across disconnect.

## Dependencies And Integration Points
The driver integrates with the serio bus using `module_serio_driver()`, consumes `SERIO_RS232` protocol IDs, and reports via the input subsystem.

## Risks
Serial protocols are timing-sensitive and weakly framed; noise or idle gaps can reset assembly. Middle-button guessing for 3-button Microsoft mice is heuristic. Extended MZ++ subpacket decoding is partial and logs unknown packet types. Capability bits depend on `id.extra` being populated correctly by lower serio detection.

## Test Signals
Feed protocol-specific byte streams and verify decoded deltas/buttons/wheels, idle reset behavior, MS-to-MP promotion, capability bits from `extra`, unknown MZ++ warning, serio open/register failure cleanup, and disconnect resource release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/sermouse.c -->
