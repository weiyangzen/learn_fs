# subset-b-003973 research

This grouped report covers Linux input mouse, mousedev, and Synaptics RMI4 support files under `sources/distributed-fs/ceph-client`. Each section preserves the original source path so the reconciliation step can split it into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics.c

## Purpose
`synaptics.c` is the PS/2 Synaptics TouchPad protocol driver. It detects Synaptics devices through PS/2 sliced commands, queries firmware capabilities, chooses a PS/2 absolute/relative mode or SMBus InterTouch path, decodes touchpad packets, reports Linux input events, and handles many historical hardware quirks.

## Important APIs, Types, and Functions
The public entry points are `synaptics_module_init()`, `synaptics_detect()`, `synaptics_init_absolute()`, `synaptics_init_relative()`, `synaptics_init_smbus()`, `synaptics_init()`, and `synaptics_reset()`. Internally, `synaptics_query_hardware()` chains identify, model, firmware, mode, capability, and resolution queries into `struct synaptics_device_info`. `struct synaptics_data` stores the queried info, current mode byte, absolute/relative choice, pass-through serio state, advanced gesture state, and ForcePad click state. Packet handling centers on `synaptics_process_byte()`, `synaptics_parse_hw_state()`, `synaptics_process_packet()`, `synaptics_report_mt_data()`, and `synaptics_report_buttons()`.

## Control Flow
Detection sends four `SETRES` commands followed by `GETINFO` and expects the Synaptics signature byte. Initialization resets the psmouse, queries hardware, optionally tries SMBus InterTouch for devices advertising `SYN_CAP_INTERTOUCH`, and otherwise configures the PS/2 native path through `synaptics_init_ps2()`. In absolute PS/2 mode, six-byte packets are validated byte-by-byte, classified as pass-through or touchpad packets, decoded into `struct synaptics_hw_state`, and translated to `BTN_TOUCH`, button, absolute axis, pressure, tool-width, and multitouch slot events. Relative mode falls back to the generic PS/2 packet handler but keeps Synaptics mode and gesture controls.

## State and Persistence
Runtime state is per `psmouse` in `psmouse->private`. It is not persistent across module unload or reconnect, but sysfs writes to `disable_gesture` change the active device mode until disconnect/reconnect. DMI-derived flags (`impaired_toshiba_kbc`, `broken_olpc_ec`, `cr48_profile_sensor`) are initialized once at module init. Hardware-derived quirks and capability flags are re-queried during reconnect and compared against the original identity to avoid silently binding to a different device.

## Dependencies and Integration Points
The driver integrates with the serio/libps2 `psmouse` core, Linux input multitouch helpers, DMI matching, RMI/SMBus support through `psmouse_smbus_init()`, and optional pass-through serio ports for guest devices such as TrackPoints. It relies on capability macros and data definitions from `synaptics.h`. It also routes some extended stick buttons through the pass-through port using out-of-band serio data.

## Risks and Edge Cases
Protocol parsing is dense and firmware-specific; relaxed packet validation exists because some newabs devices do not satisfy strict masks. Coordinate wraparound handling treats large 13-bit values as negative or edge sentinels. ForcePad click emulation depends on timing and continuing reports while stationary. SMBus setup intentionally leaves breadcrumbs on some failures, which `synaptics_disconnect()` and fallback paths must clean. Reconnect can fail if hardware reports different identity/capability data, and several DMI/PNP quirks alter coordinate ranges or protocol choice.

## Test Signals
Useful signals include successful `psmouse` protocol selection, kernel logs for queried coordinates and capability IDs, `evtest` output for absolute axes, pressure, tool buttons, multitouch slots, clickpad/ForcePad buttons, pass-through TrackPoint behavior, and suspend/resume reconnect. SMBus-capable systems should be tested both with InterTouch enabled and with fallback to PS/2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics.h

## Purpose
`synaptics.h` defines the protocol constants, capability-bit helpers, packet types, and private data structures shared by the Synaptics PS/2 implementation and the psmouse core.

## Important APIs, Types, and Functions
The header exports query command IDs such as `SYN_QUE_IDENTIFY`, mode bits such as `SYN_BIT_ABSOLUTE_MODE`, model/capability extraction macros, and special command IDs used by PS/2 sliced commands. `enum synaptics_pkt_type` identifies oldabs/newabs validation modes. `struct synaptics_hw_state` is the decoded packet representation, `struct synaptics_device_info` is the queried hardware descriptor, and `struct synaptics_data` is the per-device runtime state. Function prototypes expose detection, initialization, SMBus initialization, module init, and reset.

## Control Flow
The header itself has no execution path, but it encodes the contract used by `synaptics.c`: queries populate `struct synaptics_device_info`, device mode is built from `SYN_BIT_*` flags, packets are decoded to `struct synaptics_hw_state`, and initialization returns one of the psmouse protocol selections.

## State and Persistence
The structs describe volatile kernel runtime state only. `struct synaptics_data` persists while the `psmouse` binding is active and holds pass-through state, advanced gesture last-contact state, and ForcePad timing state.

## Dependencies and Integration Points
The declarations assume Linux kernel bit macros such as `BIT()` and `GENMASK()`, psmouse types, and serio pointers. The header is included by the PS/2 Synaptics implementation and referenced by the psmouse protocol dispatch layer.

## Risks and Edge Cases
The macros encode hardware ABI details; incorrect bit interpretation changes user-visible capabilities and packet decoding. Some comments document ambiguous firmware meanings, especially extended query 0x0c/0x10 fields, so downstream code must treat those fields conservatively.

## Test Signals
Compile coverage is the primary signal for this header. Runtime validation comes from matching reported device properties, capability flags, and input event capabilities against known Synaptics hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics_i2c.c

## Purpose
`synaptics_i2c.c` is an older direct I2C Synaptics touchpad driver. It reads RMI-style registers over SMBus page selection, configures a relative-motion reporting mode, and registers a simple Linux input mouse with left button and relative X/Y axes.

## Important APIs, Types, and Functions
`struct synaptics_i2c` owns the I2C client, input device, delayed work, scan-rate state, and cached module parameters. Register helpers `synaptics_i2c_reg_get()`, `synaptics_i2c_reg_set()`, and `synaptics_i2c_word_get()` write `PAGE_SEL_REG` before accessing the low-byte address. Probe/open/close/PM paths are `synaptics_i2c_probe()`, `synaptics_i2c_open()`, `synaptics_i2c_close()`, `synaptics_i2c_suspend()`, and `synaptics_i2c_resume()`. The work path uses `synaptics_i2c_work_handler()` and `synaptics_i2c_get_input()`.

## Control Flow
Probe allocates private state, resets and configures the device, decides between IRQ and polling mode, registers an input device, and stores client data. Opening resets/configures again and schedules polling if needed. In IRQ mode, the interrupt handler schedules immediate delayed work; the worker checks changed module parameters, handles spontaneous error/reset status, reads gesture plus relative X/Y registers, reports `BTN_LEFT`, `REL_X`, and inverted `REL_Y`, then reschedules itself either for periodic health polling or adaptive polling.

## State and Persistence
Driver state is devm-managed except the delayed work lifecycle, which is explicitly canceled on close and suspend. Module parameters (`no_decel`, `reduce_report`, `no_filter`, `polling_req`, `scan_rate`) are global; several are mutable and checked in the worker so configuration can change at runtime. The device is put into deep sleep on close/suspend.

## Dependencies and Integration Points
The driver depends on I2C/SMBus byte and word transfers, Linux workqueues, input core, IRQ registration, OF matching, and simple device PM ops. It advertises `synaptics_i2c` I2C IDs and an OF compatible string `synaptics,synaptics_i2c`.

## Risks and Edge Cases
The file notes that no locking is used because the initial design assumes no I2C bus races; extending the driver with additional asynchronous users would need serialization. `polling_req` is a global module parameter that can be forced true by one IRQ-less or failed-IRQ device, affecting all instances. `SENS_MAX_POS_LSB_REG` references `SENS_MAX_POS_UPPER_REG`, which is not otherwise defined, but the macro is unused here. Error handling resets the device when status bits are unexpected, so noisy hardware may repeatedly reconfigure.

## Test Signals
Test with both IRQ and polling paths, module parameter changes while the device is active, suspend/resume, open/close power transitions, and `evtest` relative movement/button output. I2C fault injection should verify reset-on-error handling and delayed-work cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics_usb.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics_usb.c

## Purpose
`synaptics_usb.c` supports USB Synaptics touchpads, sticks, touchscreens, cPads, and composite devices. It selects an interrupt endpoint, parses eight-byte reports, and maps them into Linux input absolute, relative, button, and pressure events.

## Important APIs, Types, and Functions
`struct synusb` holds USB device/interface pointers, an interrupt URB, coherent DMA buffer, PM mutex, open state, input device, names, and device flags. Reporting functions are `synusb_report_buttons()`, `synusb_report_stick()`, and `synusb_report_touchpad()`. Lifecycle entry points are `synusb_probe()`, `synusb_disconnect()`, `synusb_open()`, `synusb_close()`, suspend/resume/reset hooks, and the URB completion handler `synusb_irq()`.

## Control Flow
Probe switches to alternate setting 1, finds an interrupt-in endpoint, allocates an input device and URB, fills the URB with the coherent report buffer, builds a name/phys path, assigns capabilities based on device flags, optionally starts I/O for always-on devices, and registers input. Open uses USB autosuspend PM, submits the URB, and enables remote wakeup. Each successful URB completion reports either stick relative motion or touchpad absolute position/tool data, then resubmits the URB. Suspend, close, and pre-reset kill the URB; resume/post-reset resubmit when open or always-on.

## State and Persistence
State is per USB interface and lasts until disconnect. `is_open` and `needs_remote_wakeup` are protected by `pm_mutex` around open/suspend/reset races. There is no persistent configuration; input capabilities are derived from the USB ID table and interface number for composite devices.

## Dependencies and Integration Points
The driver integrates with USB core, USB autosuspend, input core, USB input ID helpers, and module USB driver registration. The ID table maps Synaptics product IDs to flags such as `SYNUSB_TOUCHPAD`, `SYNUSB_STICK`, `SYNUSB_TOUCHSCREEN`, `SYNUSB_AUXDISPLAY`, `SYNUSB_COMBO`, and `SYNUSB_IO_ALWAYS`.

## Risks and Edge Cases
Alternate setting selection uses `min(intf->num_altsetting, 1U)`, which means devices with only setting 0 remain on 0 while devices with more settings use 1. The touchpad path uses pressure hysteresis for `BTN_TOUCH` and maps pen width as a finger. Wheel events for VMware-like behavior are not relevant, but this driver reports cPad auxiliary middle button from a fourth button bit. Reset and suspend paths must avoid URB resubmission after disconnect.

## Test Signals
USB enumeration should show the correct input capabilities for touchpad, stick, touchscreen, and composite interfaces. Validate URB resubmission after runtime PM resume and USB reset, pressure hysteresis, button mapping, cPad always-on I/O, and no use-after-free on unplug during open reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/touchkit_ps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/touchkit_ps2.c

## Purpose
`touchkit_ps2.c` detects and drives eGalax TouchKit PS/2 touchscreens. It configures the psmouse instance as a five-byte absolute touchscreen protocol and reports X/Y plus touch state.

## Important APIs, Types, and Functions
The exported function is `touchkit_ps2_detect()`. Packet parsing happens in `touchkit_ps2_process_byte()`. Macros define maximum coordinates, command framing, active-controller query values, and packet field extraction for touch, X, and Y.

## Control Flow
Detection sends a vendor command using `ps2_command()` and verifies the returned command byte, length/status byte, and active command echo. If `set_properties` is true, the function rewrites input capabilities to key/absolute only, sets `BTN_TOUCH`, configures `ABS_X` and `ABS_Y` to 0..0x07ff, sets psmouse vendor/name, assigns the protocol handler, and sets packet size to five. The handler waits until `pktcnt == 5`, reports decoded X/Y/touch, syncs, and returns `PSMOUSE_FULL_PACKET`.

## State and Persistence
No private allocation is used. State is stored in the shared `psmouse` fields and the packet buffer while the protocol is active.

## Dependencies and Integration Points
The driver uses the psmouse/libps2 serio framework and Linux input absolute/key reporting. It is included by the PS/2 mouse protocol selection machinery rather than registering a standalone module driver.

## Risks and Edge Cases
The protocol assumes fixed five-byte packets and does not perform additional packet validation beyond psmouse framing. Detection depends on a specific active command response; incompatible firmware may be rejected. The capability rewrite clears mouse key state and should only run after a positive detection.

## Test Signals
Detection should reject ordinary PS/2 mice and accept TouchKit hardware. `evtest` should show `ABS_X`, `ABS_Y`, and `BTN_TOUCH` only, with correct coordinate range and one sync per five-byte packet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/touchkit_ps2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/touchkit_ps2.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/touchkit_ps2.h

## Purpose
`touchkit_ps2.h` is the minimal interface header for the eGalax TouchKit PS/2 touchscreen protocol.

## Important APIs, Types, and Functions
It declares `touchkit_ps2_detect(struct psmouse *psmouse, bool set_properties)`, which is implemented in `touchkit_ps2.c` and called by psmouse protocol probing.

## Control Flow
The header has no runtime control flow; it allows the psmouse core to invoke detection and optional property setup.

## State and Persistence
No state is declared here.

## Dependencies and Integration Points
The prototype depends on `struct psmouse` and the boolean type being visible to including files. Its integration point is the PS/2 mouse protocol dispatcher.

## Risks and Edge Cases
The header is intentionally narrow. Any additional TouchKit protocol state would need a corresponding psmouse-private structure and lifecycle handling in the implementation.

## Test Signals
Compile-time coverage of the psmouse protocol table is the main signal; runtime behavior is validated through `touchkit_ps2.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/touchkit_ps2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/trackpoint.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/trackpoint.c

## Purpose
`trackpoint.c` detects IBM-compatible PS/2 TrackPoint devices, configures their programmable parameters, exposes sysfs knobs, and enables model-specific features such as middle-button support and double-tap on capable Lenovo devices.

## Important APIs, Types, and Functions
The public entry point is `trackpoint_detect()`. Low-level I/O helpers are `trackpoint_read()`, `trackpoint_write()`, `trackpoint_toggle_bit()`, `trackpoint_update_bit()`, and `trackpoint_power_on_reset()`. Sysfs attributes are generated through `TRACKPOINT_INT_ATTR` and `TRACKPOINT_BIT_ATTR` for sensitivity, speed, inertia, thresholds, press-to-select, skipback, and external-device toggling. `trackpoint_sync()`, `trackpoint_defaults()`, `trackpoint_reconnect()`, and `trackpoint_disconnect()` manage lifecycle.

## Control Flow
Detection starts with `TP_READ_ID` and accepts known variant IDs. On property setup, it allocates `struct trackpoint_data`, stores variant/firmware IDs, sets psmouse vendor/name callbacks, queries extended button info for IBM devices, adds input capabilities, optionally power-on-resets, synchronizes non-default or unknown-state parameters, creates the sysfs attribute group, logs firmware/buttons, and enables double-tap when the serio firmware ID passes the Lenovo PNP allow/deny logic. Reconnect re-runs protocol start, attempts power-on reset for IBM devices, then syncs current settings back into hardware.

## State and Persistence
Per-device state lives in `psmouse->private` and mirrors hardware tunables. Sysfs writes update both the private field and the device RAM/register bit immediately. Values persist only while the driver instance is active; reconnect writes the remembered settings back after reset.

## Dependencies and Integration Points
The driver integrates with psmouse/libps2 commands, serio device sysfs, Linux input capability reporting, and psmouse attribute helper macros. It relies on constants and `struct trackpoint_data` from `trackpoint.h`.

## Risks and Edge Cases
Only IBM variants expose the full sysfs set; non-IBM variants expose a limited subset. Bit toggles are guarded to command locations 0x20..0x2e because toggling outside that range is unsafe. Some firmware reports zero or unreadable extended button data, so the driver assumes three buttons. Double-tap enablement is gated by PNP ID because several Lenovo devices are known incapable.

## Test Signals
Validate sysfs attribute visibility by variant, writes that change hardware behavior, reconnect after suspend with settings preserved, middle-button capability reporting, and double-tap enablement only on allowed PNP IDs. Fault-inject failed `ps2_command()` calls to ensure detection and reconnect abort cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/trackpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/trackpoint.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/trackpoint.h

## Purpose
`trackpoint.h` defines the IBM TrackPoint PS/2 command set, variant IDs, RAM/register addresses, toggle masks, default parameter values, and the per-device data structure used by `trackpoint.c`.

## Important APIs, Types, and Functions
The header provides `TP_COMMAND`, `TP_READ_ID`, variant IDs, reset/power commands, memory access commands, sensitivity/speed/threshold addresses, toggle masks, double-tap values, default settings, and `MAKE_PS2_CMD()`. `struct trackpoint_data` stores variant, firmware, integer tunables, and boolean toggles. It declares `trackpoint_detect()`.

## Control Flow
No executable flow lives here, but the constants directly drive `ps2_command()` packet construction and sysfs attribute generation in `trackpoint.c`.

## State and Persistence
`struct trackpoint_data` is the volatile software mirror of programmable TrackPoint settings. The defaults represent hardware power-on values used to skip unnecessary writes after a successful reset.

## Dependencies and Integration Points
The header is consumed by the TrackPoint PS/2 driver and assumes psmouse integration. The command values map to IBM TrackPoint engineering documentation and compatible vendor variants.

## Risks and Edge Cases
Incorrect command or mask constants can make the pointing stick unusable until hardware reset. The same RAM location is used for `TP_DRAGHYS` and `TP_DOUBLETAP` semantics, so callers must use the right value for the intended feature.

## Test Signals
Compile-time coverage and runtime `trackpoint_detect()` behavior are the main signals. Sysfs default values should match the constants and write operations should produce expected hardware changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/trackpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/vmmouse.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/vmmouse.c

## Purpose
`vmmouse.c` implements the VMware/QEMU virtual PS/2 mouse protocol. It detects the hypervisor channel, enables absolute pointer mode, creates a second input device for absolute coordinates, and multiplexes button state between relative and absolute devices.

## Important APIs, Types, and Functions
Public entry points are `vmmouse_detect()` and `vmmouse_init()`. `struct vmmouse_data` stores the absolute input device and names. Hypervisor interaction is done with `vmware_hypercall*()` commands in `vmmouse_enable()`, `vmmouse_disable()`, and `vmmouse_report_events()`. PS/2 data integration uses `vmmouse_process_byte()`, while lifecycle callbacks are `vmmouse_reset()`, `vmmouse_disconnect()`, and `vmmouse_reconnect()`.

## Control Flow
Detection first checks `x86_hyper_type` against VMware/KVM and verifies the VMware hypervisor magic/version. Initialization resets psmouse, enables the absolute pointer channel, allocates and registers an absolute input device, adds wheel capability to the existing relative psmouse device, and installs the vmmouse packet handler. The handler accepts the PS/2 notification bytes and then drains hypervisor queue entries. Each entry is classified as relative or absolute, reports motion to the preferred device, reports wheel on the relative device for userspace compatibility, reports buttons on whichever device already holds the button if pressed, and syncs both devices.

## State and Persistence
State is per psmouse binding in `psmouse->private` and is freed on disconnect. Hypervisor mode is disabled on cleanup, disconnect, reset, and before reconnect. No state persists beyond the active virtual device session.

## Dependencies and Integration Points
The driver depends on x86 hypervisor detection, VMware backdoor hypercalls, psmouse/libps2, serio, and Linux input. `vmmouse.h` declares the public psmouse hooks and `VMMOUSE_PSNAME`.

## Risks and Edge Cases
Queue length must be a multiple of four or the driver forces bad data to trigger psmouse recovery. The event loop caps processing at 255 packets to avoid indefinite drain. `vmmouse_disable()` warning logic is suspicious because it warns when status does not equal the error sentinel after disable. Button ownership across two input devices is subtle and needed to keep release events on the device that reported the press.

## Test Signals
Run under supported VMware/KVM environments, verify detection fails on unsupported hypervisors, absolute and relative motion both report correctly, wheel events reach the relative device, reconnect after suspend re-enables the channel, and malformed queue/status values trigger recovery without crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/vmmouse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/vmmouse.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/vmmouse.h

## Purpose
`vmmouse.h` exposes the VMware virtual PS/2 mouse protocol hooks to the psmouse core.

## Important APIs, Types, and Functions
It defines `VMMOUSE_PSNAME` and declares `vmmouse_detect()` and `vmmouse_init()`.

## Control Flow
No runtime flow is implemented here; the psmouse probe path uses the declarations to detect and initialize the vmmouse protocol.

## State and Persistence
The header declares no state.

## Dependencies and Integration Points
The prototypes depend on `struct psmouse` and are implemented by `vmmouse.c`. The header belongs to the psmouse protocol integration layer.

## Risks and Edge Cases
The interface is intentionally narrow. Any future vmmouse feature requiring shared state should remain in `vmmouse.c` unless the psmouse core needs to see it.

## Test Signals
Compile coverage of psmouse protocol selection and successful vmmouse detection/initialization provide validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/vmmouse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/vsxxxaa.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/vsxxxaa.c

## Purpose
`vsxxxaa.c` is a serio RS232 driver for DEC VSXXX-AA/GA mice and VSXXX-AB tablets. It buffers serial bytes, resynchronizes packet streams, decodes relative mouse, absolute tablet, and power-on-reset packets, and reports Linux input events.

## Important APIs, Types, and Functions
`struct vsxxxaa` stores the input device, serio port, 15-byte buffer, detected version/country/type, and name/phys strings. Buffer helpers are `vsxxxaa_queue_byte()`, `vsxxxaa_drop_bytes()`, and `vsxxxaa_check_packet()`. Packet handlers are `vsxxxaa_handle_REL_packet()`, `vsxxxaa_handle_ABS_packet()`, and `vsxxxaa_handle_POR_packet()`. Driver lifecycle uses `vsxxxaa_connect()`, `vsxxxaa_interrupt()`, `vsxxxaa_disconnect()`, and `module_serio_driver()`.

## Control Flow
Connect allocates state and input device, advertises key/relative/absolute capabilities, opens the serio port, sends `T` to request self-test, and registers input. Every incoming byte is queued and `vsxxxaa_parse_buffer()` repeatedly drops non-header bytes, checks whether a known packet type and length are available, validates that continuation bytes are not headers, handles complete packets, and drops stray bytes when a broken packet is detected. POR packets identify the device and then force standard format, incremental streaming, and a 72 samples/sec rate by writing `S`, `R`, and `L`.

## State and Persistence
The byte buffer preserves partial packets across interrupts. Device identity fields are updated after POR/self-test. There is no persistent configuration outside the live serio session; mode/rate commands are reissued after POR.

## Dependencies and Integration Points
The driver integrates with serio RS232 device matching (`SERIO_VSXXXAA`), Linux input, and module serio registration. It exposes both relative mouse and absolute tablet capabilities on one input device.

## Risks and Edge Cases
Serial streams can lose sync, so the parser aggressively drops bytes and logs errors. `vsxxxaa_drop_bytes()` uses `BUFLEN - num` in `memmove`, which copies more than the remaining valid byte count but stays inside the fixed buffer; correctness depends on `count` being adjusted afterward. Hardware mode forcing uses `mdelay()` in packet handling after POR, which can stall processing. The adapter/power requirements described in comments are unusual and hardware failures may look like protocol noise.

## Test Signals
Test relative packets, absolute tablet packets, POR/self-test identification, hot-plug recovery, broken-packet resynchronization, and disconnect during active serial traffic. `evtest` should show three buttons, `BTN_TOUCH`, `REL_X/Y`, and `ABS_X/Y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/vsxxxaa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mousedev.c -->
# sources/distributed-fs/ceph-client/drivers/input/mousedev.c

## Purpose
`mousedev.c` implements the legacy `/dev/input/mouseX`, `/dev/input/mice`, and optional `/dev/psaux` compatibility interface. It consumes generic input events from mouse-like, tablet-like, touchpad, and wheel devices and emits PS/2, IntelliMouse, or ExplorerPS/2 byte streams to character-device clients.

## Important APIs, Types, and Functions
`struct mousedev` represents a per-input-device node or the global mixer, including input handle, client list, locks, cdev/device, packet accumulator, touchpad conversion history, and open/close hooks. `struct mousedev_client` is per open file and stores queued motion packets, PS/2 response buffer, emulation mode, and async state. Event handling uses `mousedev_event()`, `mousedev_abs_event()`, `mousedev_touchpad_event()`, `mousedev_rel_event()`, `mousedev_key_event()`, and `mousedev_notify_readers()`. File operations are `mousedev_open()`, `mousedev_release()`, `mousedev_read()`, `mousedev_write()`, `mousedev_poll()`, and `mousedev_fasync()`.

## Control Flow
Module init creates the global `mice` mix device, registers an input handler, and optionally registers `/dev/psaux`. When a matching input device appears, `mousedev_connect()` creates a cdev-backed device and adds it to the mixer. Incoming input events accumulate into `mousedev->packet` until `SYN_REPORT`, then notify per-device clients and mixer clients. Each client has a 16-entry circular queue; reads convert queued motion into PS/2-compatible packets, clamping large deltas and leaving residue for subsequent reads. Writes emulate mouse commands, including sample-rate sequences that switch the client into IMPS or ExplorerPS/2 mode.

## State and Persistence
State is in kernel memory only. Per-device open counts drive `input_open_device()`/`input_close_device()`. Mixer open state can open all currently known devices and later opens new devices added to the mix. Per-client position starts at screen center and persists for the life of the file descriptor. Module parameters `xres`, `yres`, and `tap_time` globally control absolute scaling and touchpad tap emulation.

## Dependencies and Integration Points
The file integrates with the input handler API, input minor allocator, cdev/device model, wait queues, fasync, poll, optional misc `/dev/psaux`, RCU list traversal for clients, and input device ID matching. It is the compatibility consumer for many drivers in this subset, including Synaptics and VSXXX absolute reports.

## Risks and Edge Cases
Legacy emulation requires careful state sequencing: button changes can force a new queue entry, large deltas are split across reads, and writes can interleave PS/2 responses with motion data. Touchpad absolute-to-relative conversion relies on duplicate event handling and four-sample history. The global `mousedev_mix->packet.buttons` is updated from all devices, so button state races across devices must be considered. Disconnect marks devices dead and wakes clients, but already queued clients must handle `-ENODEV`.

## Test Signals
Validate per-device and `/dev/input/mice` reads, blocking and nonblocking reads, poll/fasync wakeups, IMPS/Explorer command negotiation, absolute tablet scaling, touchpad tap-to-click timing, disconnect wakeups, and module parameter effects. Regression tests should include multiple clients and multiple devices opened through the mixer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mousedev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/Kconfig

## Purpose
`drivers/input/rmi4/Kconfig` defines build-time configuration for the Synaptics RMI4 bus, transports, and function drivers.

## Important APIs, Types, and Functions
Key symbols include `RMI4_CORE`, `RMI4_I2C`, `RMI4_SPI`, `RMI4_SMB`, `RMI4_F03`, `RMI4_F03_SERIO`, `RMI4_2D_SENSOR`, `RMI4_F11`, `RMI4_F12`, `RMI4_F1A`, `RMI4_F21`, `RMI4_F30`, `RMI4_F34`, `RMI4_F3A`, `RMI4_F54`, and `RMI4_F55`. `RMI4_CORE` selects `IRQ_DOMAIN`, `RMI4_F34` selects `FW_LOADER`, and `RMI4_F54` selects `VIDEOBUF2_VMALLOC` and `RMI4_F55`.

## Control Flow
The file is declarative. Enabling `RMI4_CORE` gates all other RMI options. Transport symbols select bus-specific modules, while function symbols include optional handlers into `rmi_core` through the Makefile.

## State and Persistence
Kconfig state persists in the kernel build configuration. It determines which code paths and symbols exist at compile time.

## Dependencies and Integration Points
The options map directly to `rmi4/Makefile`. `RMI4_SMB` is relevant to Synaptics PS/2 InterTouch fallback in `synaptics.c`; F11/F12 select the common 2D sensor helper; F03 plus F03_SERIO enables PS/2 guest/TrackPoint support.

## Risks and Edge Cases
Feature combinations can affect runtime capability: Synaptics InterTouch needs both `MOUSE_PS2_SYNAPTICS_SMBUS` and `RMI4_SMB`, while ForcePad support needs function coverage beyond a basic PS/2 path. `RMI4_F54` has a specific built-in/module dependency with `VIDEO_DEV`, so invalid configurations are blocked.

## Test Signals
Build matrix tests should cover core-only, each transport, F11/F12 2D sensor inclusion, SMBus InterTouch, F34 firmware sysfs, and module versus built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/Makefile -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/Makefile

## Purpose
`drivers/input/rmi4/Makefile` maps RMI4 Kconfig symbols to object files and composes the `rmi_core` module.

## Important APIs, Types, and Functions
The main build target is `rmi_core.o`, made from `rmi_bus.o`, `rmi_driver.o`, and `rmi_f01.o`. Conditional additions include `rmi_2d_sensor.o` and function handlers `rmi_f03.o`, `rmi_f11.o`, `rmi_f12.o`, `rmi_f1a.o`, `rmi_f21.o`, `rmi_f30.o`, `rmi_f34.o`, `rmi_f34v7.o`, `rmi_f3a.o`, `rmi_f54.o`, and `rmi_f55.o`. Transport modules are `rmi_i2c.o`, `rmi_spi.o`, and `rmi_smbus.o`.

## Control Flow
The file is build-system logic only. It ensures F01 and bus/physical-driver code are always included with `RMI4_CORE`, while optional function and transport objects follow configuration.

## State and Persistence
Build outputs and module composition are determined by Kconfig state. There is no runtime state.

## Dependencies and Integration Points
The Makefile is paired with `Kconfig` and the Linux kbuild system. Function handler declarations in `rmi_driver.h` assume objects are only linked when their Kconfig symbols are enabled.

## Risks and Edge Cases
Missing an object from `rmi_core-y` would cause unresolved handler references or missing runtime support despite Kconfig visibility. F34 includes both base and v7 code as a pair.

## Test Signals
Run kernel builds with representative RMI4 configurations, especially `RMI4_CORE=m`, transports as modules, F11/F12 selecting `RMI4_2D_SENSOR`, and F34/F54 optional features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_2d_sensor.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_2d_sensor.c

## Purpose
`rmi_2d_sensor.c` provides shared helpers for RMI4 2D pointing functions such as F11 and F12. It applies axis alignment, clipping, offsets, tracking, input capability setup, absolute multitouch reporting, relative reporting, and device-tree parsing.

## Important APIs, Types, and Functions
Exported helpers are `rmi_2d_sensor_abs_process()`, `rmi_2d_sensor_abs_report()`, `rmi_2d_sensor_rel_report()`, `rmi_2d_sensor_configure_input()`, and `rmi_2d_sensor_of_probe()`. The code operates on `struct rmi_2d_sensor` and `struct rmi_2d_sensor_abs_object` from `rmi_2d_sensor.h`.

## Control Flow
Function drivers parse raw object data, call `rmi_2d_sensor_abs_process()` to transform coordinates and update `tracking_pos`, then call `rmi_2d_sensor_abs_report()` to select an MT slot and report position, pressure, major/minor touch dimensions, orientation, and slot state. Relative deltas pass through `rmi_2d_sensor_rel_report()`, which clamps to signed 8-bit range and applies axis flips/swaps. `rmi_2d_sensor_configure_input()` attaches the shared RMI input device and sets MT/REL capabilities according to sensor flags. OF probing fills axis, sensor type, physical size, report mask, and rezero wait parameters from device properties.

## State and Persistence
The helper mutates per-function `struct rmi_2d_sensor` state: clipped min/max, tracking positions, tracking slots, input pointer, and optional `dmax`. It does not persist configuration beyond the active device binding; DT/platform data provides static configuration.

## Dependencies and Integration Points
The file depends on Linux input MT helpers, OF property helpers, RMI debug, and `rmi_driver_data->input`. F11/F12 function drivers use this shared code to avoid duplicating sensor setup and event reporting.

## Risks and Edge Cases
The clipping high path uses `min(sensor->max_x, obj->x)` and `min(sensor->max_y, obj->y)` after checking high clip fields, so the configured high clips only constrain `sensor->max_*` earlier in input setup. Kernel tracking and function-provided slot IDs must match allocated arrays. Resolution and `dmax` depend on physical dimensions being present. Released fingers retain prior coordinates by design.

## Test Signals
Validate axis flip, swap, offsets, clipping, touchpad versus touchscreen MT flags, kernel tracking, relative movement clamping, DT property parsing, and F11/F12 raw object conversion through `evtest` or input selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_2d_sensor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_2d_sensor.h -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_2d_sensor.h

## Purpose
`rmi_2d_sensor.h` defines the shared 2D sensor object model and helper API used by RMI4 pointing functions.

## Important APIs, Types, and Functions
`enum rmi_2d_sensor_object_type` classifies none, finger, stylus, palm, and unclassified objects. `struct rmi_2d_sensor_abs_object` stores transformed/reportable object fields. `struct rmi_2d_sensor` stores axis alignment, tracking arrays, packet buffers, dimensions, finger counts, input pointers, report flags, physical sizes, and register-state preferences. The header declares the exported helper functions from `rmi_2d_sensor.c`.

## Control Flow
The header has no executable path. Function drivers instantiate `struct rmi_2d_sensor`, fill it from query/platform data, configure input, then use the process/report helpers during attention interrupts.

## State and Persistence
The declared structs hold per-function runtime state and static platform-derived configuration while the function is bound.

## Dependencies and Integration Points
It depends on `linux/rmi.h`, Linux integer types, and `struct rmi_function`. It is consumed by RMI4 F11/F12 and any other 2D pointing functions.

## Risks and Edge Cases
The structure contains raw pointers (`tracking_pos`, `tracking_slots`, `objs`, `data_pkt`) whose allocation and lifetime are owned by function drivers. Mismatched `nbr_fingers`, packet sizes, and tracking arrays can cause reporting errors.

## Test Signals
Compile and runtime validation through F11/F12 handlers should confirm object type mapping, slot counts, and property-driven axis behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_2d_sensor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_bus.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_bus.c

## Purpose
`rmi_bus.c` implements the Linux `rmi4` bus, registration of physical RMI devices from transport drivers, registration of per-function child devices, binding of function handlers, nested IRQ setup for function attention callbacks, OF child matching, debug logging, and module init/exit.

## Important APIs, Types, and Functions
Exported APIs include `rmi_dbg()`, `rmi_register_transport_device()`, `rmi_unregister_transport_device()`, `rmi_is_physical_device()`, `rmi_is_function_device()`, `rmi_register_function()`, `rmi_unregister_function()`, `__rmi_register_function_handler()`, `rmi_unregister_function_handler()`, and `rmi_of_property_read_u32()`. Bus matching is done by `rmi_bus_match()`. Function probing uses `rmi_function_probe()`, `rmi_function_remove()`, and `rmi_create_function_irq()`.

## Control Flow
Module init registers the `rmi4` bus, registers all compiled-in function handlers, and registers the physical RMI driver. A transport driver calls `rmi_register_transport_device()`, which creates a physical `rmi_device`; the physical driver scans the PDT and calls `rmi_register_function()` for function child devices. Function child probe invokes the handler's `probe()` and maps each function interrupt bit into a Linux IRQ with a simple nested IRQ chip and threaded handler. Module exit unregisters the physical driver, function handlers, and bus.

## State and Persistence
Physical devices and function devices are kernel device-model objects with release callbacks that free allocated structures. Function IRQ mappings are disposed on unregister. The global `debug_flags` module parameter controls conditional debug output.

## Dependencies and Integration Points
The file integrates with Linux device/bus core, IRQ domains, OF child nodes named `rmi4-fXX`, PM infrastructure, RMI transport APIs from `linux/rmi.h`, and the physical-driver helpers in `rmi_driver.c`. The `fn_handlers[]` list is built from Kconfig-selected handler symbols.

## Risks and Edge Cases
Error unwind during bus init unregisters the bus but does not explicitly unregister function handlers if physical-driver registration fails after handler registration; this mirrors the local code path and should be checked carefully. Function IRQ creation assumes `rmi_driver_data` and `irqdomain` are ready before function probe side effects. Optional OF properties return zero and default values when absent, so callers must distinguish absent optional values from explicit zero where that matters.

## Test Signals
Validate transport registration/unregistration, function device creation/removal, handler binding by function number, nested IRQ delivery to attention callbacks, OF child binding, module unload, and debug flag output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_bus.h -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_bus.h

## Purpose
`rmi_bus.h` defines the internal RMI bus abstractions for physical devices, function devices, function handlers, transport read/write helpers, and debug flags.

## Important APIs, Types, and Functions
`struct rmi_function` represents one function descriptor discovered on a physical RMI device and includes IRQ metadata plus a flexible `irq_mask`. `struct rmi_function_handler` describes handler callbacks for probe, remove, config, reset, attention, suspend, and resume. Inline helpers `rmi_read()`, `rmi_read_block()`, `rmi_write()`, and `rmi_write_block()` dispatch through the transport operations. The header declares function/device registration APIs and `rmi_bus_type`.

## Control Flow
The header defines the callback contracts used by `rmi_bus.c` and `rmi_driver.c`: transports create physical devices, the physical driver creates function devices, and function handlers bind by function number and receive lifecycle/attention callbacks.

## State and Persistence
The structures describe runtime device-model state. `irq_mask` is sized dynamically based on total function IRQ bits when functions are allocated.

## Dependencies and Integration Points
It depends on public RMI platform/transport definitions from `linux/rmi.h`, Linux device-driver types, and the bus implementation. Function drivers include this header indirectly through `rmi_driver.h`.

## Risks and Edge Cases
The inline transport helpers assume `xport->ops->read_block` and `write_block` are valid and return kernel-style error codes. Handlers must tolerate callbacks being absent in other functions and must manage device data lifetime through devm or remove callbacks.

## Test Signals
Build coverage with multiple transports and functions, static analysis of callback signatures, and runtime RMI function probe/IRQ/config paths validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_driver.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_driver.c

## Purpose
`rmi_driver.c` is the physical-device driver for one RMI4 sensor. It resets the sensor, scans the Page Description Table, creates RMI function devices, allocates interrupt state, owns the shared input device, dispatches attention IRQs, handles suspend/resume, and processes sensor reset/configuration requests.

## Important APIs, Types, and Functions
Exported or cross-file functions include `rmi_free_function_list()`, `rmi_set_attn_data()`, `rmi_find_function()`, `rmi_enable_sensor()`, `rmi_scan_pdt()`, `rmi_read_register_desc()`, `rmi_get_register_desc_item()`, `rmi_register_desc_calc_size()`, `rmi_register_desc_calc_reg_offset()`, `rmi_register_desc_has_subpacket()`, `rmi_initial_reset()`, `rmi_enable_irq()`, `rmi_disable_irq()`, `rmi_driver_suspend()`, `rmi_driver_resume()`, `rmi_probe_interrupts()`, `rmi_init_functions()`, `rmi_register_physical_driver()`, and `rmi_unregister_physical_driver()`. Probe logic is in `rmi_driver_probe()`.

## Control Flow
Probe validates a physical RMI device, loads OF platform data, allocates `struct rmi_driver_data`, performs an initial F01 reset by scanning page 0, reads PDT properties, initializes IRQ locks, counts function IRQs and bootloader state, allocates IRQ masks/domain, allocates or reuses an input device, scans the PDT again to create function children, creates F34 sysfs, registers input if owned by the core, registers the physical IRQ, and enables the sensor once F01 is bound. On interrupt, `rmi_irq_fn()` optionally consumes transport-provided attention FIFO data, processes enabled IRQ bits, calls `handle_nested_irq()` for each function bit, and syncs the shared input device.

## State and Persistence
`struct rmi_driver_data` stores the function list, f01/f34 containers, IRQ domain, IRQ bitmaps, current/new masks, enabled state, attention FIFO, input device, bootloader mode, and PDT properties. It is devm-managed for the physical device. Function list teardown unregisters child devices in reverse order so F01 is removed last.

## Dependencies and Integration Points
The file integrates with RMI transport devices, `rmi_bus.c` function registration, function handlers such as F01/F11/F12/F34, Linux irqdomain/nested IRQ, input core, OF properties, and PM wrappers exported to transports. `rmi_driver.h` exposes register descriptor parsing and PDT definitions to function drivers.

## Risks and Edge Cases
Initial reset failure is logged but not fatal so slow cold-boot sensors can still bind. The PDT scan stops after two empty pages or bootloader mode. IRQ memory allocation uses one devm block split into four bitmaps, so size calculations must remain consistent. Transport attention FIFO data is allocated with `GFP_ATOMIC` and drained recursively if multiple entries exist. `rmi_register_desc_calc_reg_offset()` increments offset by one per register instead of by each register size, which may be intentional for register index offsets or a risk for byte-offset consumers.

## Test Signals
Test cold/warm boot reset behavior, devices in bootloader mode, PDT scan over multiple pages, IRQ enable/disable mask writes, nested function IRQ dispatch, transport-provided attention data, suspend/resume with wake IRQ, function teardown order, and register descriptor parsing with known F12/F54 descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_driver.h -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_driver.h

## Purpose
`rmi_driver.h` is the internal header for the RMI4 physical driver and function handlers. It defines PDT constants, register descriptor structures, core helper prototypes, optional function helper stubs, and handler externs.

## Important APIs, Types, and Functions
Important definitions include `SYNAPTICS_INPUT_DEVICE_NAME`, `SYNAPTICS_VENDOR_ID`, `PDT_PROPERTIES_LOCATION`, `BSR_LOCATION`, `RMI_PDT_ENTRY_SIZE`, `PDT_START_SCAN_LOCATION`, `PDT_END_SCAN_LOCATION`, `struct pdt_entry`, `struct rmi_register_desc_item`, and `struct rmi_register_descriptor`. It declares PDT scanning, register descriptor parsing, IRQ probing, function initialization, sensor enabling, suspend/resume helper dependencies, F03 button helpers, F34 sysfs helpers, and all function handler externs.

## Control Flow
The header defines the shared contracts: `rmi_driver.c` scans PDT entries and creates function devices; function handlers use register descriptor helpers and optional F03/F34 helpers; `rmi_bus.c` registers the handler externs selected by Kconfig.

## State and Persistence
The register descriptor structures are allocated per function as needed and describe query/control/data packet layouts. PDT entries are transient scan results copied into function descriptors.

## Dependencies and Integration Points
It includes Linux input, timing, ctype, and `rmi_bus.h`. It is included by RMI core and function implementation files such as `rmi_f01.c` and `rmi_2d_sensor.c`.

## Risks and Edge Cases
Optional helper stubs return success when features are disabled, so callers must be clear whether a no-op is acceptable. Handler externs must match Makefile/Kconfig inclusion or builds will fail. Register descriptor spelling uses `presense`, which is harmless but easy to duplicate incorrectly.

## Test Signals
Build matrix coverage for all Kconfig combinations is important. Runtime coverage comes from function handlers using PDT addresses, register descriptors, F03/F34 helpers, and IRQ setup without mismatched struct assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f01.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f01.c

## Purpose
`rmi_f01.c` implements RMI4 Function 01, the mandatory device-control function. It reads product/manufacturing properties, configures global sensor control and power-management registers, creates informational sysfs attributes, handles reset attention events, and manages sleep/resume behavior.

## Important APIs, Types, and Functions
The file defines `struct f01_basic_properties`, `struct f01_device_control`, and `struct f01_data`. Property parsing is in `rmi_f01_read_properties()`, and the product string API is `rmi_f01_get_product_ID()`. Sysfs show functions expose manufacturer ID, date of manufacture, product ID, firmware ID, and package ID on the physical RMI device. Lifecycle callbacks are `rmi_f01_probe()`, `rmi_f01_remove()`, `rmi_f01_config()`, `rmi_f01_suspend()`, `rmi_f01_resume()`, and `rmi_f01_attention()`, collected in `rmi_f01_handler`.

## Control Flow
Probe optionally reads F01 OF power-management properties, allocates private data, reads control register 0, applies `nosleep` policy, clears unexpected sleep mode, sets the configured bit, writes control 0, clears pending IRQs by dummy reading interrupt status, reads query properties, logs product information, walks optional doze/wakeup/holdoff control registers after the IRQ mask registers, validates that the device did not reset during setup, stores drvdata, and creates the sysfs group. Config rewrites saved control/doze fields after a core reset. Attention reads device status, warns on bootloader mode, and invokes the physical driver's reset handler if the device is unconfigured.

## State and Persistence
`struct f01_data` persists for the F01 function device lifetime and caches properties, control register values, optional register addresses, old nosleep state, suspended flag, and IRQ-register count. Sysfs values are read-only and reflect cached query data. Power-management settings are restored after resume or reset using the cached values.

## Dependencies and Integration Points
The file depends on the RMI bus/driver helpers, `rmi_get_platform_data()`, OF property parsing, sysfs, unaligned little-endian helpers, and the physical driver's reset callback. F01 is always included in `rmi_core` and suppresses user unbinding because the core depends on it.

## Risks and Edge Cases
F01 query layouts are variable: sensor ID, query 42, DS4 query length, package ID, and build ID alter offsets. Miscomputing these offsets corrupts property parsing. `package_id` is declared `u32` but read from a little-endian 64-bit buffer, truncating higher bits. Suspend writes reserved sleep mode 3 for wake-capable devices by design; platform compatibility should be validated. A reset during probe returns `-EINVAL`, while a later unconfigured status triggers full reset/config callbacks.

## Test Signals
Validate sysfs attributes, F01 property parsing on devices with and without DS4 queries, configurable doze/wakeup/holdoff OF properties, reset attention recovery, suspend/resume sleep mode writes, bootloader warnings, and interaction with the shared input device name set from product ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f01.c -->
