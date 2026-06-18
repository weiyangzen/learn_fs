# subset-b-003970 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/Makefile -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/Makefile

## Purpose

This Kbuild file selects and composes Linux input mouse and touchpad drivers under `drivers/input/mouse`. In this subset it is the build integration point for legacy platform mouse drivers (`amimouse.o`, `atarimouse.o`), USB Apple touchpad drivers (`appletouch.o`, `bcm5974.o`), the Cypress APA I2C trackpad aggregate module (`cyapatp.o`), and PS/2 psmouse protocol extensions including ALPS and BYD.

## Important APIs, Types, and Functions

The important interface is Kbuild object composition rather than C APIs. `obj-$(CONFIG_MOUSE_...) += ...` binds each Kconfig option to an object or module. `cyapatp-objs := cyapa.o cyapa_gen3.o cyapa_gen5.o cyapa_gen6.o` composes one module from a bus/core file plus generation-specific protocol files. `psmouse-objs := psmouse-base.o synaptics.o focaltech.o` defines the base PS/2 module, then `psmouse-$(CONFIG_MOUSE_PS2_ALPS) += alps.o` and similar lines add protocol drivers into that same module when enabled.

## Control Flow

Kbuild evaluates the configuration symbols and builds either standalone objects or composite modules. Standalone USB/I2C/platform drivers register through their own module macros. ALPS, BYD, Elantech, TrackPoint, and other PS/2 protocols are linked into `psmouse.o`, so their `*_detect` and `*_init` entry points are called by psmouse core rather than by module init functions in those files.

## State and Persistence Behavior

The file has no runtime state. Its persistent effect is the build-time shape of kernel modules and symbol availability. Changing composite membership changes which protocol handlers are present in `psmouse.o` and therefore changes runtime detection order and exported device support.

## Dependencies and Integration Points

It depends on Kconfig symbols such as `CONFIG_MOUSE_CYAPA`, `CONFIG_MOUSE_PS2_ALPS`, and transport sub-options such as `CONFIG_MOUSE_ELAN_I2C_I2C` and `CONFIG_MOUSE_ELAN_I2C_SMBUS`. It integrates with Linux Kbuild conventions for composite objects and with source files in this directory that assume they are either standalone bus drivers or psmouse protocol plugins.

## Risks and Edge Cases

Composite object ordering matters for duplicate symbols and protocol registration availability. Adding a psmouse protocol as a standalone `obj-*` instead of `psmouse-*` would break its integration model. `cyapatp` requires all generation files to remain listed together because `cyapa.c` dispatches through `cyapa_gen3_ops`, `cyapa_gen5_ops`, and `cyapa_gen6_ops`.

## Test Signals

Useful checks are `make drivers/input/mouse/` with combinations of the relevant `CONFIG_MOUSE_*` options, verifying that `cyapatp` links all generation ops and that `psmouse.o` includes selected protocol objects. Runtime smoke tests should confirm that standalone USB/I2C/platform drivers bind independently while ALPS/BYD bind through psmouse detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/alps.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/alps.c

## Purpose

`alps.c` is the PS/2 protocol implementation for ALPS GlidePoint and DualPoint touchpads. It detects many ALPS generations, switches devices into absolute or multitouch reporting modes, decodes protocol-specific packets, reports Linux input events for the touchpad and optional pointing stick, and manages difficult PS/2 pass-through/interleaving behavior.

## Important APIs, Types, and Functions

The exported psmouse entry points are `alps_detect()` and `alps_init()`. Detection is driven by `alps_identify()`, `alps_rpt_cmd()`, the `alps_model_data[]` E7 signature table, firmware EC report heuristics, and `alps_set_protocol()`. Runtime byte handling uses `alps_process_byte()` as `psmouse->protocol_handler`, with protocol-specific callbacks stored in `struct alps_data`: `hw_init`, `process_packet`, `decode_fields`, and `set_abs_params`.

Packet/reporting code includes `alps_process_packet_v1_v2()`, `alps_process_touchpad_packet_v3_v5()`, `alps_process_packet_v4()`, `alps_process_packet_v6()`, `alps_process_packet_v7()`, and `alps_process_packet_ss4_v2()`. The important decoders are `alps_decode_pinnacle()`, `alps_decode_rushmore()`, `alps_decode_dolphin()`, `alps_decode_packet_v7()`, and `alps_decode_ss4_v2()`. Hardware setup is split across `alps_hw_init_v1_v2()`, `alps_hw_init_v3()`, `alps_hw_init_rushmore_v3()`, `alps_hw_init_v4()`, `alps_hw_init_dolphin_v1()`, `alps_hw_init_v6()`, `alps_hw_init_v7()`, and `alps_hw_init_ss4_v2()`.

## Control Flow

`alps_detect()` first does a trial identify, rejects ALPS CS19 trackpoint-only devices so `trackpoint.c` can own them, resets the PS/2 device, allocates `struct alps_data`, identifies again, and optionally sets psmouse vendor/name/model. `alps_init()` runs the selected hardware initializer, converts the primary input device from relative to absolute/multitouch reporting, creates an optional second input device for DualPoint stick data, initializes delayed registration for bare pass-through PS/2 mice, and installs psmouse callbacks.

At runtime `alps_process_byte()` validates packet sync bytes, handles bare PS/2 packets and interleaved PS/2 packets, applies protocol-specific partial-packet validation for V7/V8, and calls the selected `process_packet()` on complete packets. Early generations report single-touch absolute data plus buttons. V3/V5 combine position and bitmap packets into semi-MT bounding boxes through `alps_process_bitmap()`. V7 and SS4/V8 decode direct multitouch coordinates and use MT slot assignment. Trackstick packets are routed to `dev2` with relative movement and pressure when supported.

## State and Persistence Behavior

Persistent driver state is `struct alps_data`, stored in `psmouse->private`. It holds protocol identity, device and firmware IDs, flags, input devices, coordinate limits/resolution, nibble-command tables, packet assembly state (`multi_packet`, `multi_data`, `second_touch`, `prev_fin`), quirks, a flush timer, and delayed work for registering a bare PS/2 mouse. No on-disk state is used. Hardware state is changed by command/monitor-mode register writes to enable absolute mode, trackstick extended format, passthrough, raw mode, and stream reporting.

## Dependencies and Integration Points

The file integrates with psmouse core (`struct psmouse`, packet callbacks, polling, reconnect/disconnect), `libps2` commands, the Linux input subsystem including MT helpers, DMI quirks, serio pause helpers, workqueues, timers, and TrackPoint ID reads. `alps.h` supplies protocol constants and state structures. Documentation for wire formats is referenced in `Documentation/input/devices/alps.rst`.

## Risks and Edge Cases

ALPS hardware uses fragile magic command sequences; failures can leave devices in command mode, so error paths repeatedly call `alps_exit_command_mode()`. Packet validation is heuristic, especially for interleaved PS/2 and Rushmore last-byte corruption. Multi-packet bitmap flows can lose sync or reject palm-like packets. Some devices dynamically reveal trackstick-button quirks only after a button press. `alps_disconnect()` disables delayed work and unregisters optional devices, but race-sensitive paths involve timers, serio RX pause, and delayed `dev3` registration. Coordinate/resolution derivation from OTP/register data can fail, preventing protocol setup.

## Test Signals

Tests should cover detection through known E6/E7/EC signatures and fallback heuristics, CS19 rejection, every protocol initializer, command-mode failure unwinds, packet validation/resync for V1 through V8, semi-MT bitmap corner selection, V7/SS4 MT slot reporting, DualPoint trackstick setup and button routing, interleaved bare PS/2 packet handling, reconnect after reset, and disconnect while the flush timer or `dev3_register_work` is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/alps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/alps.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/alps.h

## Purpose

`alps.h` is the private protocol contract for the ALPS PS/2 touchpad driver. It defines protocol version IDs, packet bitfield extraction macros, multitouch packet identifiers, decode result structures, private driver state, quirks, and the psmouse-facing `alps_detect()` / `alps_init()` declarations.

## Important APIs, Types, and Functions

Important protocol constants include `ALPS_PROTO_V1` through `ALPS_PROTO_V9`, `MAX_TOUCHES`, Dolphin and SS4 sensor geometry constants, and `ALPS_QUIRK_TRACKSTICK_BUTTONS`. `enum SS4_PACKET_ID` and `enum V7_PACKET_ID` classify packet kinds. The SS4 macros such as `SS4_1F_X_V2`, `SS4_STD_MF_X_V2`, `SS4_TS_X_V2`, and `SS4_BTN_V2` centralize byte-to-coordinate extraction.

Core structures are `struct alps_protocol_info`, `struct alps_model_info`, `struct alps_nibble_commands`, `struct alps_bitmap_point`, `struct alps_fields`, and `struct alps_data`. `struct alps_data` is the long-lived state object used by `alps.c`; it stores input devices, command tables, device IDs, geometry, callback pointers, packet assembly fields, decoded fields, quirks, and the timer.

## Control Flow

The header does not execute code directly, but it shapes `alps.c` dispatch. Detection fills an `alps_protocol_info`, `alps_set_protocol()` copies it into `alps_data`, and packet handlers write normalized decoded values into `struct alps_fields` before reporting through input core. Packet macros are used by SS4/V8 decode paths to select one-finger, multi-finger, idle, and stick packets.

## State and Persistence Behavior

`struct alps_data` persists for the lifetime of the psmouse protocol binding. `multi_packet` and `multi_data` preserve partial packet streams, `prev_fin` preserves tap/drag transition state, `second_touch` stabilizes semi-MT bounding-box corner choice, and `quirks` records runtime-detected model behavior. All persistence is in kernel memory.

## Dependencies and Integration Points

The header depends on `linux/input/mt.h` for `struct input_mt_pos` and input MT slot semantics. Its public declarations are consumed by psmouse core and `alps.c`. The byte extraction macros must remain aligned with the protocol packet documentation and the report sizes set in `alps.c`.

## Risks and Edge Cases

Many macros assume a six-byte packet and valid indices; callers must validate packet length and type first. `BIT(priv->x_bits) - 1` style consumers rely on geometry values staying within integer widths. Callback pointers in `struct alps_data` must be fully initialized for each protocol version, or runtime packet processing can dereference NULL. The misspelled comment on `ALPS_QUIRK_TRACKSTICK_BUTTONS` is harmless but the quirk itself affects which device receives button events.

## Test Signals

Build tests should ensure the header remains synchronized with `alps.c` callbacks and structure fields. Runtime tests should indirectly validate each packet macro through V7 and SS4 packet decode fixtures, and should verify state fields are initialized/reset correctly across detection, init, reconnect, and disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/alps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/amimouse.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/amimouse.c

## Purpose

`amimouse.c` is a Linux/m68k platform input driver for the Amiga mouse. It reads Amiga custom chip joystick/mouse counters and button registers on the vertical blank interrupt, converts wraparound deltas into relative movement, and reports a three-button relative mouse through the input subsystem.

## Important APIs, Types, and Functions

`amimouse_interrupt()` is the IRQ handler. `amimouse_open()` snapshots the initial `joy0dat` counters and requests `IRQ_AMIGA_VERTB`; `amimouse_close()` frees it. `amimouse_probe()` allocates/registers the `input_dev`, sets `EV_REL` and `EV_KEY` capabilities, and stores it in platform driver data. `amimouse_remove()` unregisters the input device. `module_platform_driver_probe()` registers a non-hot-unbind platform driver named `amiga-mouse`.

## Control Flow

When the platform device probes, the driver creates an input device with BUS_AMIGA IDs and open/close callbacks. On first userspace open, it records the current low/high bytes of `amiga_custom.joy0dat` as the last X/Y counters and requests the vertical blank IRQ. Each interrupt reads the next 8-bit counters, computes signed deltas with 256-count wrap correction, reads `ciaa.pra` and `amiga_custom.potgor` for button state, reports `REL_X`, `REL_Y`, `BTN_LEFT`, `BTN_MIDDLE`, and `BTN_RIGHT`, then syncs the input frame.

## State and Persistence Behavior

The only driver state is `amimouse_lastx` and `amimouse_lasty`, static globals preserving the prior hardware counter values between interrupts. The input device pointer is owned by platform driver data after registration. There is no persistent configuration or storage.

## Dependencies and Integration Points

The file depends on Amiga architecture headers and hardware globals (`amiga_custom`, `ciaa`, `IRQ_AMIGA_VERTB`), platform driver infrastructure, and input core. Its remove function is in exit text and is used only for module unload, matching `module_platform_driver_probe()` constraints.

## Risks and Edge Cases

Button bits are reported directly from hardware bit masks; if the electrical polarity is active-low, consumers rely on the historical convention used here. Delta wrap correction assumes interrupt frequency keeps movement between samples within +/-127 counts. Missed vertical blanks can produce wrong direction after large movement. The driver is Amiga-specific and will not probe without the matching platform device.

## Test Signals

Useful tests are m68k build coverage, probe/open/close with IRQ request/free, synthetic counter wrap cases, button bit reporting for all three buttons, and module unload ensuring the input device is unregistered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/amimouse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/appletouch.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/appletouch.c

## Purpose

`appletouch.c` is a USB input driver for pre-BCM5974 Apple PowerBook/MacBook touchpads. It switches supported Geyser devices into raw sensor mode, reads USB interrupt reports containing sensor banks, reconstructs touch position and pressure from sensor deltas, detects approximate finger count, and reports an absolute single-touch style input device with tool-count keys.

## Important APIs, Types, and Functions

`struct atp_info` describes per-generation sensor counts, coordinate scale factors, USB report length, callback, and fuzz. `struct atp` stores USB/input state, raw and accumulated sensor arrays, smoothing buffers, old coordinates, finger count, idle counter, and reinit work. The USB ID table is built with `ATP_DEVICE()`.

Important functions include `atp_geyser_init()` for USB class control mode switching, `atp_calculate_abs()` for finger/centroid/pressure calculation, `atp_complete_geyser_1_2()` and `atp_complete_geyser_3_4()` for interrupt report decoding, `atp_status_check()` for URB validation, `atp_detect_size()` for 17-inch sensor range detection, and `atp_probe()` / `atp_disconnect()` / PM callbacks for lifecycle.

## Control Flow

Probe locates the first interrupt-in endpoint, allocates `struct atp`, an input device, an URB, and coherent transfer buffer, fills the interrupt URB with the model-specific callback, switches non-Fountain devices into raw mode, sets ABS_X/Y/PRESSURE and button/tool keys, and registers the input device. `atp_open()` submits the URB; `atp_close()` kills it and cancels reinit work.

On each interrupt, the generation-specific callback checks status and exact report length, reorders packed sensor bytes into `xy_cur`, updates baseline/old values, derives positive sensor deltas into `xy_acc`, calculates X and Y centroids with smoothing, reports touch/position/pressure if coordinates and finger count are stable, reports release on empty data, reports the physical button, and resubmits the URB. Geyser 3/4 devices are reinitialized after repeated idle packets to stop high-rate empty reports.

## State and Persistence Behavior

State persists in memory while the USB interface is bound: raw sample arrays, previous baseline, accumulated deltas, smoothing buffers, last reported coordinate, previous finger count, overflow warning flag, and size-detection flag. `atp_reinit()` work resets device mode after idle streaming. No settings are persisted outside the device; module parameters `threshold` and `debug` affect runtime behavior.

## Dependencies and Integration Points

The driver integrates with USB core, USB input ID conversion, coherent DMA buffers, input core, workqueues, and system suspend/resume/reset_resume. It claims Apple HID mouse-protocol interfaces for specific product IDs and competes with generic HID behavior by switching raw sensor mode.

## Risks and Edge Cases

Exact report lengths are required; short or overflowed URBs are dropped. Geyser mode switching can fail or be lost across reset/resume. Sensor baseline handling differs between Geyser 1/2 and 3/4; wrong model data yields bad coordinates. Finger count changes intentionally reset smoothing, which can drop movement around transitions. `atp_disconnect()` does not explicitly cancel `work`; open/close cancels it, but disconnect racing with scheduled idle reinit deserves attention. The 17-inch size detection only expands X range after seeing nonzero high-index sensors.

## Test Signals

Tests should cover probe for each product ID/model info, mode-switch read/write failures, URB status paths including overflow and short packets, sensor reordering for Geyser 1/2/3/4, centroid/finger count fixtures, release/accumulator reset, idle-triggered reinit, open/close URB lifetime, suspend/resume/reset_resume, and disconnect while URBs or reinit work are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/appletouch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/atarimouse.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/atarimouse.c

## Purpose

`atarimouse.c` is the Linux/m68k Atari mouse input driver. Low-level ACIA keyboard/mouse handling lives in Atari architecture code; this driver registers an input device and installs a callback hook that converts IKBD relative mouse packets into standard Linux relative motion and button events.

## Important APIs, Types, and Functions

`mouse_threshold` is a module parameter array passed to the Atari keyboard controller. `atamouse_interrupt()` is the hook called with three-byte relative mouse data. `atamouse_open()` programs IKBD mouse mode and assigns `atari_input_mouse_interrupt_hook`; `atamouse_close()` disables IKBD mouse reporting and clears the hook. `atamouse_init()` checks Atari hardware, initializes keyboard support, allocates/registers the input device, and `atamouse_exit()` unregisters it.

## Control Flow

Module init exits unless running on Atari hardware with ST MFP present. It then initializes the Atari keyboard layer and registers a BUS_HOST relative mouse input device. On open, the driver sets top-origin Y mode, applies movement thresholds, selects relative-position packets, and installs its interrupt hook. Each hook call decodes button bits from `buf[0]`, takes signed `dx`/`dy` from bytes 1 and 2, reports `REL_X`, `REL_Y`, left/middle/right buttons, and syncs. Close disables mouse reporting and removes the hook.

## State and Persistence Behavior

`atamouse_dev` is a single global input device pointer. Optional `FIXED_ATARI_JOYSTICK` code shares `atari_mouse_buttons` with architecture joystick handling. Thresholds persist as module parameter values for the module lifetime. There is no dynamic per-open allocation or durable state.

## Dependencies and Integration Points

The file depends on Atari-specific architecture APIs and globals (`MACH_IS_ATARI`, `ATARIHW_PRESENT`, `atari_keyb_init`, `ikbd_mouse_*`, and `atari_input_mouse_interrupt_hook`), plus input core and module infrastructure. It relies on the architecture keyboard/ACIA code to receive and classify mouse packets.

## Risks and Edge Cases

The global hook supports only one device instance. Open/close ordering must not race with architecture interrupt delivery after the hook is cleared. Button bit mapping is hardware-specific and includes optional joystick-derived middle button behavior under `FIXED_ATARI_JOYSTICK`. Invalid `mouse_threshold` values are not range-clamped in this file.

## Test Signals

Build and boot tests on Atari/m68k configurations should verify hardware gating, keyboard init failure handling, input registration, threshold programming, relative packet decoding including signed movement, all button combinations, close hook removal, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/atarimouse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/bcm5974.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/bcm5974.c

## Purpose

`bcm5974.c` is the USB multitouch input driver for Apple Broadcom BCM5974/Wellspring trackpads used in MacBook Air and MacBook Pro generations. It identifies Apple HID mouse interfaces, switches the trackpad into Wellspring raw mode, decodes per-finger records, reports multitouch protocol B slots plus compatibility ABS pressure/width fields, handles integrated or separate buttons, and coordinates USB autosuspend.

## Important APIs, Types, and Functions

`bcm5974_table[]` lists supported Apple product IDs. `struct bcm5974_config` captures per-generation endpoint numbers, report layouts, button offsets, mode-switch control-message fields, coordinate/pressure/width/orientation ranges, and capabilities such as `HAS_INTEGRATED_BUTTON`. `struct bcm5974` owns URBs, coherent buffers, input device, slot arrays, mode-reset work, PM mutex, and open state.

Important functions include `bcm5974_get_config()`, `setup_events_to_report()`, `report_bt_state()`, `report_tp_state()`, `report_finger_data()`, `report_synaptics_data()`, `bcm5974_wellspring_mode()`, `bcm5974_irq_button()`, `bcm5974_irq_trackpad()`, `bcm5974_start_traffic()`, `bcm5974_pause_traffic()`, and lifecycle/PM callbacks.

## Control Flow

Probe selects a config from USB product ID, allocates state/input/URBs/coherent buffers, creates a button URB for TYPE1 devices, always creates a trackpad URB, fills interrupt URBs, initializes input capabilities and MT slots, then registers the input device. Opening the input device takes USB runtime PM, locks `pm_mutex`, switches to Wellspring mode, submits button and trackpad URBs, and marks the device opened. Closing kills URBs, switches back to normal mode, clears opened, and releases runtime PM.

Trackpad IRQ completion ignores two-byte control responses, validates the report layout, decodes all finger records whose `touch_major` is nonzero, transforms Y coordinates, assigns MT slots, reports touch/tool/touch-width/orientation/position fields for each slot, emits compatibility pressure/width from the first finger, reports integrated button state when applicable, syncs, and resubmits. Bad eight-byte HID reports suggest the device fell out of Wellspring mode, so delayed work toggles normal mode, waits about 1 ms, and switches raw mode back on.

## State and Persistence Behavior

Runtime state includes `opened`, `pm_mutex`, URB buffers, copied config, last mode-reset timestamp, MT position/index arrays, and scheduled mode-reset work. Device mode is an external hardware state toggled by USB control messages on open, close, resume, and reset recovery. No persistent storage is used. Autosuspend state is coordinated through USB runtime PM.

## Dependencies and Integration Points

The driver depends on USB core, HID interface descriptors, coherent DMA for interrupt buffers, Linux input MT helpers, runtime PM/autosuspend, workqueues, and Apple USB product IDs. It coexists with the keyboard/HID portion of the same USB device, which is why mode switching is performed when traffic starts rather than only at probe.

## Risks and Edge Cases

Mode switches can be ignored if issued too close to a control response; the reset work mitigates this but is asynchronous. TYPE3 skips mode switching, so config accuracy is critical. `bcm5974_disconnect()` disables mode-reset work before clearing intfdata, but URBs and input unregistering must still be ordered against open/close. Report size validation prevents malformed parsing, but a wrong `tp_header/tp_fsize/tp_delta` config would misinterpret raw data. `bcm5974_start_traffic()` calls `usb_kill_urb(dev->bt_urb)` on the error path even when `bt_urb` may be NULL; kernel helpers tolerate NULL in many contexts, but this is a point to verify for target kernel semantics.

## Test Signals

Tests should cover every config row, TYPE1 separate button versus integrated-button devices, Wellspring mode on/off failures, two-byte control-response filtering, bad HID fallback and throttled mode reset, MT slot assignment with multiple fingers, orientation/width/pressure scaling, runtime PM open/close, suspend/resume while opened and closed, autosuspend support, and disconnect with pending reset work or active URBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/bcm5974.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/byd.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/byd.c

## Purpose

`byd.c` is a PS/2 psmouse protocol driver for BYD touchpads. It detects the device with a PS/2 command sequence, configures the touchpad into four-byte absolute/relative packet mode with most firmware gestures disabled, converts mixed absolute and relative packets into an absolute pointer position, reports touch/buttons, and uses a timer to synthesize touch release when packets stop.

## Important APIs, Types, and Functions

The exported psmouse hooks are `byd_detect()` and `byd_init()`. `struct byd_data` stores the release timer, psmouse pointer, current absolute coordinates, last-touch time, button states, and touch state. `byd_process_byte()` is the packet handler. `byd_reset_touchpad()` sends the reverse-engineered initialization sequence. `byd_clear_touch()` is the timeout handler. `byd_reconnect()` and `byd_disconnect()` manage reset/retry and cleanup.

## Control Flow

Detection sends four `SETRES` commands with parameter `0x03`, then `GETINFO`, and accepts devices returning `param[1] == 0x03` and `param[2] == 0x64`. Init resets the psmouse, sends the BYD initialization sequence, allocates private state, installs psmouse callbacks, selects packet size 4, disables resync, and converts the input device from relative motion to absolute ABS_X/ABS_Y with button/touch capabilities.

At runtime the packet handler validates the PS/2 always-one bit, waits for four bytes, and switches on byte 3. Absolute packets initialize position at touch start using 8-bit X/Y scaled to the driver’s estimated pad dimensions. Relative packets sign-extend PS/2 dx/dy, integrate velocity over `BYD_DT`, and mark touch active. The handler reports BTN_TOUCH, BTN_TOOL_FINGER, ABS_X/Y, BTN_LEFT, and BTN_RIGHT, then arms a 64 ms release timer. The timer pauses serio RX, clears touch, reports release, and recenters the internal coordinate.

## State and Persistence Behavior

State is per psmouse binding in `struct byd_data`. `abs_x`/`abs_y` persist between packets and are integrated from relative deltas. `last_touch_time` and `touch` decide whether the next absolute packet starts a new movement. The release timer persists until disconnect and is deleted there. Hardware configuration persists in the device until reset/reconnect.

## Dependencies and Integration Points

The driver depends on psmouse core, `libps2` command transport, serio pause helpers for timer-side reporting, Linux input core, and jiffies/timers. `byd.h` declares its psmouse entry points. It is linked into `psmouse.o` by the Makefile when `CONFIG_MOUSE_PS2_BYD` is enabled.

## Risks and Edge Cases

Many BYD command constants are documented but only a subset is used; unsupported gesture packet types are treated as bad data and logged. Absolute coordinates are based on estimated resolution and are not clamped after integrated relative motion, so large deltas may leave nominal bounds before input core clamps or consumers handle them. Touch start uses `time_after(jiffies, last_touch_time + timeout)`, so initial zero state behavior depends on jiffies. `byd_disconnect()` uses `timer_delete()` instead of a synchronous shutdown, making timer concurrency worth reviewing for the target kernel. Reconnect retries detection up to three times with one-second sleeps after reset.

## Test Signals

Tests should cover successful and failed detection signatures, the full initialization command sequence, relative sign extension, absolute packet scaling, release timeout behavior, tap timing around `BYD_TOUCH_TIMEOUT`, button reporting, bad packet first-byte validation, unknown gesture packet rejection, reconnect retry behavior, and disconnect during an active timer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/byd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/byd.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/byd.h

## Purpose

`byd.h` is the small private header that exposes the BYD PS/2 touchpad protocol hooks to psmouse core and the directory build. It keeps BYD detection and initialization declarations separate from `byd.c`.

## Important APIs, Types, and Functions

The header declares `int byd_detect(struct psmouse *psmouse, bool set_properties);` and `int byd_init(struct psmouse *psmouse);`. It also provides the `_BYD_H` include guard. `struct psmouse` is expected to be visible from the includer; `byd.c` includes `psmouse.h` before this header.

## Control Flow

There is no executable control flow. psmouse core calls `byd_detect()` during protocol probing, and if accepted calls `byd_init()` to install BYD-specific packet handling and input capabilities.

## State and Persistence Behavior

The header defines no state. Runtime state lives in `struct byd_data` in `byd.c` and is attached to `psmouse->private`.

## Dependencies and Integration Points

It integrates `byd.c` with the psmouse protocol selection code and the composite `psmouse.o` build. Any signature change here must match psmouse callers and `byd.c`.

## Risks and Edge Cases

Because the header does not forward-declare `struct psmouse` or include `<linux/types.h>` for `bool`, it relies on include ordering. That is fine for current local use but fragile if included from another context.

## Test Signals

Build coverage with `CONFIG_MOUSE_PS2_BYD=y/m` is the main signal. Compile errors would catch signature drift or missing include context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/byd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa.c

## Purpose

`cyapa.c` is the bus/core driver for Cypress APA I2C/SMBus trackpads. It handles adapter detection, regulator power, device state discovery across Gen3/Gen5/Gen6 protocols, input device creation, IRQ dispatch, runtime/system power management, sysfs controls, and firmware update orchestration while delegating generation-specific protocol operations to `cyapa_gen3_ops`, `cyapa_gen5_ops`, and `cyapa_gen6_ops`.

## Important APIs, Types, and Functions

Externally visible helpers include `cyapa_is_pip_bl_mode()`, `cyapa_is_pip_app_mode()`, `cyapa_poll_state()`, `cyapa_sleep_time_to_pwr_cmd()`, and `cyapa_pwr_cmd_to_sleep_time()`. Internal state flow centers on `cyapa_get_state()`, `cyapa_check_is_operational()`, `cyapa_detect()`, `cyapa_initialize()`, and `cyapa_reinitialize()`. Input lifecycle is handled by `cyapa_create_input_dev()`, `cyapa_open()`, and `cyapa_close()`. IRQ and command coordination uses `cyapa_irq()`, `cyapa_enable_irq_for_cmd()`, and `cyapa_disable_irq_for_cmd()`. Sysfs and firmware paths include `cyapa_firmware()`, `cyapa_update_fw_store()`, `cyapa_calibrate_store()`, `cyapa_show_baseline()`, and mode/version/product attributes.

## Control Flow

Probe verifies I2C or SMBus functionality, does a basic SMBus presence read, allocates `struct cyapa`, enables the `vcc` regulator with devm cleanup, initializes all generation command-state helpers, detects the trackpad, prepares wake/runtime sysfs controls, requests a threaded falling-edge IRQ, disables the IRQ until input open, and creates an input device immediately only if firmware is operational.

State detection reads three status bytes from register zero, retries with SMBus block command when needed, and asks Gen3, PIP, and old Gen5 parsers to classify the state. Operational check selects the generation ops table and runs `ops->operational_check()`. Opening the input device locks `state_sync_lock`, sets full-active power or reinitializes, enables IRQ, enables runtime PM, and schedules autosuspend. The threaded IRQ first lets command-response handling consume interrupts; if it is a data interrupt and the device is operational, it calls the generation `irq_handler()`, bumps runtime PM, and attempts reinitialize on errors.

Firmware update sysfs unregisters the input device, locks state, requests firmware, validates it through the active ops table, resumes/powers the device, enables IRQ for command completion, enters/activates/initiates bootloader, writes firmware, then reinitializes and recreates input state if possible.

## State and Persistence Behavior

`struct cyapa` persists as devm-managed client data. It stores current state/gen, bootloader status bytes, operational flag, regulator/client/input pointers, power-mode policy for suspend and runtime suspend, cached product/firmware/platform/capability data, geometry, Gen5/Gen6 electrode data, `state_sync_lock`, ops pointer, and union command states. Sysfs writes persist only in memory as suspend/runtime scanrate settings. Firmware update persists to the device flash through generation-specific ops.

## Dependencies and Integration Points

The file depends on I2C/SMBus APIs, Linux input MT, IRQ threading, regulators, firmware loader, sysfs attribute groups, runtime PM, ACPI/OF matching, and generation-specific cyapa protocol files. `cyapa.h` defines shared constants, state, ops, and command prototypes. Userspace integration appears through input events and sysfs attributes `firmware_version`, `product_id`, `update_fw`, `baseline`, `calibrate`, `mode`, and power scanrate controls.

## Risks and Edge Cases

`cyapa_suspend()` and `cyapa_resume()` dereference `cyapa->input`; probe can leave `input` NULL when firmware is non-operational, so suspend/resume on a bootloader-only device needs scrutiny. State detection has several protocol fallbacks and retries; incorrect adapter capability or even/odd address handling can misclassify devices. Firmware update unregisters the input device before taking the state lock, so input users, PM, and sysfs sequencing are sensitive. IRQ handling must distinguish command responses from touch reports; losing this distinction can drop command completions or report stale data. Runtime scanrate update calls `pm_runtime_get_sync()` before taking the state lock and may return early on lock interruption without a matching put. Regulator disable is devm-managed, so all probe failure paths after enabling rely on action cleanup.

## Test Signals

Tests should cover I2C-only, SMBus-only, and combined adapters; Gen3/Gen5/Gen6 state parse paths; bootloader busy/idle/active and app modes; operational input registration; open/close IRQ and PM transitions; threaded IRQ command-response versus data events; firmware update success and each bootloader step failure; sysfs scanrate parsing including `buttononly`, `off`, and numeric values; baseline/calibrate when non-operational; suspend/resume with and without wakeup; runtime suspend/resume; and probe where the device is detected but not operational.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa.h

## Purpose

`cyapa.h` is the shared private interface for Cypress APA trackpad support. It defines Gen3 register commands, PIP/TrueTouch command and response constants, power mode encodings, command-state structures, the main `struct cyapa`, the generation ops vtable, and cross-file helper prototypes used by `cyapa.c` and the generation-specific protocol files.

## Important APIs, Types, and Functions

Important constants include generation IDs (`CYAPA_GEN3`, `CYAPA_GEN5`, `CYAPA_GEN6`), SMBus command encoding macros, Gen3 operational/bootloader register bits, power modes (`PWR_MODE_FULL_ACTIVE`, `PWR_MODE_IDLE`, `PWR_MODE_SLEEP`, `PWR_MODE_BTN_ONLY`, `PWR_MODE_OFF`), PIP report IDs and command lengths, deep-sleep constants, and `CYAPA_MAX_MT_SLOTS`.

`struct cyapa_dev_ops` is the central polymorphic API for firmware checking/updating, baseline/calibration sysfs handling, initialization, state parsing, operational checking, IRQ handling, empty-output sorting, power-mode setting, and proximity control. `struct cyapa_pip_cmd_states` tracks command locks, completions, issued command, response buffers, IRQ/poll mode, PM stage, and scratch buffers. `struct cyapa` stores device state, bus/input/regulator pointers, power policy, product/firmware/geometry data, generation-specific electrode data, synchronization lock, ops pointer, and command states.

## Control Flow

The header does not execute directly. `cyapa.c` initializes a `struct cyapa`, selects one `cyapa_dev_ops` implementation after state parsing, then invokes its callbacks for operational checks, IRQ reporting, firmware update, and power management. Gen5/Gen6 PIP command helpers use the PIP constants and `cyapa_pip_cmd_states` to match command responses and synchronize IRQ-mode commands.

## State and Persistence Behavior

The main persistent state is `struct cyapa`, owned by the I2C client. `state`, `status`, `operational`, power modes, firmware/product fields, geometry, and command-state locks/completions persist until device removal. Firmware image persistence is handled by ops implementations declared here but not defined in this header. Sysfs-configured scanrates are in-memory fields.

## Dependencies and Integration Points

The header includes `<linux/firmware.h>` and relies on Linux I2C/input/regulator types being visible in users. It declares low-level read helpers, PIP command helpers, firmware update helpers, and extern ops tables from `cyapa_gen3.c`, `cyapa_gen5.c`, and `cyapa_gen6.c`. It binds all files into the `cyapatp` composite module listed in the Makefile.

## Risks and Edge Cases

The ops table is broad; missing or incompatible generation callbacks can break probe, IRQ, firmware update, or PM paths. PIP response macros assume exact report offsets and lengths. Power-mode macros cache the last device state and must remain consistent with actual hardware transitions. `CYAPA_MAX_MT_SLOTS` is tied to touch IDs and must match generation report formats. Several prototypes expose raw buffers and lengths, so callers must validate sizes before parsing.

## Test Signals

Build tests should verify all declared extern ops and helpers are defined by the composite module. Runtime and unit-style fixtures should validate PIP header macros, power conversion helpers, command completion matching, max slot assumptions, generation state transitions, and all `cyapa_dev_ops` callback coverage for Gen3/Gen5/Gen6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa.h -->
