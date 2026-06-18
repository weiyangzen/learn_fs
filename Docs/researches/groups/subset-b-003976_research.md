# subset-b-003976 research

Grouped research for Linux input serio, sparse-keymap, tablet, test, touch-overlay, and touchscreen files under `sources/distributed-fs/ceph-client`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/serio.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/serio.c

## Purpose
`serio.c` is the core bus implementation for Linux serial I/O input ports. It provides the `serio_bus`, registration and unregistration of `struct serio` ports and `struct serio_driver` drivers, asynchronous event handling through `system_long_wq`, sysfs bind controls, modalias/uevent support, PM reconnect behavior, and exported helpers used by PS/2, RS232, and virtual serio providers.

## Important APIs, types, and functions
The central state is the global `serio_list`, protected by `serio_mutex`, plus each port's `drv_mutex` and `lock`. `struct serio_event` tracks queued operations such as `SERIO_REGISTER_PORT`, rescans, reconnects, subtree reconnects, and driver attach requests. Exported entry points include `__serio_register_port()`, `serio_unregister_port()`, `serio_unregister_child_port()`, `serio_rescan()`, `serio_reconnect()`, `__serio_register_driver()`, `serio_unregister_driver()`, `serio_open()`, `serio_close()`, and `serio_interrupt()`. Bus callbacks are `serio_bus_match()`, `serio_uevent()`, `serio_driver_probe()`, `serio_driver_remove()`, and shutdown/PM callbacks.

## Control flow
Port registration initializes the device, assigns a `serioN` name, installs attribute groups, and queues a register event. The worker holds `serio_mutex`, drains ordered events, and calls add, rescan, reconnect, or attach helpers while suppressing back-to-back duplicates. `serio_add_port()` links child ports under parents with RX paused, starts low-level hardware, and calls `device_add()`, after which the driver core attempts binding. Matching uses the serio ID table unless either the port or driver is in manual-bind mode. Disconnect walks children depth-first, releases attached drivers, and destroys dynamically-created child ports.

## State and persistence
All persistent kernel state is in memory: global port and event lists, per-port parent/child trees, `serio->drv`, sysfs `manual_bind`, and pending module references held by queued events. The core does not persist device settings across reboot. PM suspend calls driver cleanup; resume first tries `fast_reconnect()` under the per-port driver mutex, then queues a slower reconnect if needed.

## Dependencies and integration points
This file integrates with the Linux driver core, sysfs device and driver attributes, module lifetime accounting, workqueues, kobject uevents, PM ops, and the `linux/serio.h` exported API. It is the hub for downstream serio providers such as i8042, serial line disciplines, platform PS/2 controllers, `serio_raw`, and serial tablet/touchscreen protocol drivers.

## Risks
Ordering and lifetime are the main hazards. Events carry raw object pointers guarded by module references, so pending event removal and duplicate suppression must stay correct. Tree teardown must account for children queued for registration but not yet device-added. `serio_interrupt()` can trigger automatic rescans on unhandled data, so lock ordering between IRQ context, RX pause guards, and workqueue reconnects is important. Manual sysfs binding accepts driver names directly and must avoid racing unregister.

## Test signals
Build with `CONFIG_SERIO` and representative serio providers. Useful runtime tests include async port registration/removal, child-port teardown during parent disconnect, sysfs `drvctl` operations (`none`, `reconnect`, `rescan`, explicit driver name), manual-vs-auto bind behavior, module unload with queued events, PM fast reconnect fallback, and uevent modalias generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/serio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/serio_raw.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/serio_raw.c

## Purpose
`serio_raw.c` exposes selected serio ports as raw misc character devices, emulating the historical `/dev/psaux` byte stream. It is manually bound to 8042-compatible ports so userspace can read incoming bytes, write outgoing bytes, poll for data, and receive async notifications.

## Important APIs, types, and functions
`struct serio_raw` holds a 64-byte circular receive queue, kref lifetime, underlying `struct serio`, miscdevice, waitqueue, client list, and dead flag. `struct serio_raw_client` stores per-open fasync state. File operations are `serio_raw_open()`, `release()`, `read()`, `write()`, `poll()`, and `fasync()`. Serio callbacks are `serio_raw_connect()`, `serio_raw_interrupt()`, `serio_raw_reconnect()`, and `serio_raw_disconnect()`.

## Control flow
Connect allocates the raw object, opens the serio port, links it into `serio_raw_list`, and registers a misc device, first trying `PSMOUSE_MINOR` and falling back to a dynamic minor. Incoming bytes are queued from the serio interrupt path while holding the serio lock; readers drain bytes under `serio_pause_rx()`, blocking on the waitqueue unless nonblocking. Writes are serialized by `serio_raw_mutex` and send at most 32 bytes through `serio_write()`. Disconnect deregisters the misc device, marks the object dead, wakes readers, sends fasync hangup, closes serio, and drops the kref.

## State and persistence
Runtime state is in the in-memory queue, open-client list, kref, and `dead` flag. The raw device has no persistent configuration. Open file descriptors keep the object alive after disconnect until release, but operations then fail or hang up based on `dead`.

## Dependencies and integration points
The driver integrates with the serio driver model, miscdevice subsystem, waitqueues, poll/fasync, usercopy helpers, and `PSMOUSE_MINOR`. Its ID table covers `SERIO_8042` and `SERIO_8042_XL`, and `manual_bind = true` keeps it from automatically taking over normal keyboard/mouse ports.

## Risks
The receive queue silently drops a byte when the ring would become full because the head update is skipped on overflow. Read-side checks of head/tail are partly lockless before the locked fetch, so correctness depends on retry behavior and simple byte queue semantics. The fixed-minor fallback must not confuse userspace expecting psaux-compatible numbering. Disconnect must wake all blocking and async users so stale file descriptors do not hang indefinitely.

## Test signals
Exercise manual binding/unbinding to an 8042 port, blocking and nonblocking reads, partial writes and write error propagation, poll masks before and after disconnect, fasync `SIGIO` delivery, queue overflow behavior, reconnect preserving the same raw device, and misc minor fallback when `PSMOUSE_MINOR` is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/serio_raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/serport.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/serport.c

## Purpose
`serport.c` implements the `N_MOUSE` TTY line discipline named `input`, converting a serial TTY byte stream into a `SERIO_RS232` port. It lets serial input devices such as tablets and touchscreens bind to normal serio protocol drivers via tools like `inputattach`.

## Important APIs, types, and functions
`struct serport` stores the tty, waitqueue, active serio port, serio ID, spinlock, and flags `SERPORT_BUSY`, `SERPORT_ACTIVE`, and `SERPORT_DEAD`. The line discipline callbacks are open, close, read, ioctl, compat ioctl, receive buffer, hangup, and write wakeup. Serio callbacks implement write, open, and close.

## Control flow
Opening the line discipline requires `CAP_SYS_ADMIN`, allocates state, sets `receive_room`, and enables write wakeups. The read method is the long-lived activation path: it creates a serio port, fills name/phys/protocol/write/open/close fields, registers it, then sleeps until hangup marks the port dead. Incoming TTY bytes are ignored until the serio driver opens the port; then receive-buffer callbacks translate TTY parity/frame flags into `SERIO_PARITY` or `SERIO_FRAME` and call `serio_interrupt()`. `SPIOCSTYPE` sets protocol/id/extra before registration.

## State and persistence
State exists only while the line discipline is installed. The protocol selection in `serport->id` persists for that ldisc instance until close. `SERPORT_ACTIVE` follows serio open/close, `SERPORT_BUSY` prevents multiple concurrent readers from creating multiple ports, and hangup wakes the read path for orderly unregister.

## Dependencies and integration points
This file integrates the TTY layer, serio core, `SPIOCSTYPE` ioctl ABI, compat ioctl translation, TTY write wakeups, and serial input protocol drivers. It depends on userspace selecting the line discipline and setting the protocol expected by the target serio driver.

## Risks
`serport_ldisc_read()` sets `SERPORT_BUSY` before allocating the serio object and returns `-ENOMEM` without clearing it if allocation fails, leaving the ldisc instance busy until close. Protocol must be set before the read-side registration; changing it later does not affect an already registered port. Lifetime correctness depends on hangup/read/close ordering and on the TTY layer not freeing `disc_data` while read is sleeping.

## Test signals
Test privileged and unprivileged ldisc open, `SPIOCSTYPE` and compat ioctl packing, one-reader-only behavior, byte and flag forwarding, write wakeups to `serio_drv_write_wakeup()`, hangup unblocking read and unregistering serio, and serial protocol driver binding through `inputattach`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/serport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/sun4i-ps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/sun4i-ps2.c

## Purpose
`sun4i-ps2.c` is a platform serio provider for the Allwinner A10/Sun4i PS/2 host controller. It maps the controller registers, manages its clock and interrupt, exposes a `SERIO_8042` port, and translates hardware FIFO/line status into serio bytes and flags.

## Important APIs, types, and functions
`struct sun4i_ps2data` carries the serio port, device, MMIO base, clock, IRQ, and spinlock. `sun4i_ps2_probe()` allocates and registers the port. `sun4i_ps2_open()` programs line-control, FIFO reset/interrupt bits, clock dividers, and global enable. `sun4i_ps2_interrupt()` drains the RX FIFO and reports bytes. `sun4i_ps2_write()` polls `PS2_FSTS_TXRDY` before writing one byte. `sun4i_ps2_close()` disables interrupts and synchronizes the IRQ.

## Control flow
Probe maps the first memory resource, gets/enables the clock, initializes `struct serio`, disables controller interrupts, obtains the platform IRQ, requests it, then registers the serio port. Opening the port enables error interrupts, FIFO interrupts, the sample clock divider, master mode, bus enable, reset, and interrupt enable. IRQ handling reads line and FIFO status, clears errors, computes serio flags, drains the RX count encoded in FIFO status bits, and finally acknowledges status registers. Removal unregisters the port, frees IRQ, disables/puts the clock, unmaps MMIO, and frees private data.

## State and persistence
The controller configuration is programmed on each serio open and disabled on close. Runtime state is the MMIO register set plus private pointers. There is no persistent software configuration. Clock state persists while the platform device is bound; FIFO and interrupt state is reset during open.

## Dependencies and integration points
The driver depends on platform resources, OF compatible `allwinner,sun4i-a10-ps2`, `clk_get()/clk_prepare_enable()`, `ioremap()`, `request_irq()`, and the serio core. It feeds standard PS/2 protocol drivers through a `SERIO_8042` port.

## Risks
The transmit path busy-waits for up to 10 seconds with no sleep, which can stall callers if hardware never becomes ready. Error flag mapping sets `SERIO_TIMEOUT` from parity error rather than timeout-specific bits, which may misclassify faults. Clock divider calculations assume sane source clock rates and do not check for zero or underflow. Probe uses manual resource management rather than devm helpers, so cleanup ordering is important.

## Test signals
Build with the Sun4i platform option, boot on matching DT hardware, verify clock rates and divider programming, open/close IRQ enable behavior, RX FIFO draining under normal and error status, TX timeout behavior with no device attached, and removal while the serio port is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/sun4i-ps2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/userio.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/userio.c

## Purpose
`userio.c` creates `/dev/userio`, a misc character device that lets userspace instantiate a virtual serio port, configure its port type, inject incoming bytes with `serio_interrupt()`, and receive bytes written by the kernel-side serio driver.

## Important APIs, types, and functions
`struct userio_device` stores one open file's `struct serio`, mutex, running flag, 16-byte circular output buffer, spinlock, and waitqueue. File operations are `userio_char_open()`, `release()`, `read()`, `write()`, and `poll()`. `userio_execute_cmd()` handles `USERIO_CMD_REGISTER`, `USERIO_CMD_SET_PORT_TYPE`, and `USERIO_CMD_SEND_INTERRUPT`. `userio_device_write()` is the serio `.write` callback that queues kernel-to-userspace bytes.

## Control flow
Each open allocates an independent device and serio object. Userspace first writes a `USERIO_CMD_SET_PORT_TYPE`, then `USERIO_CMD_REGISTER` to asynchronously register the serio port, and can later inject bytes using `USERIO_CMD_SEND_INTERRUPT`. When a serio protocol driver writes back, `userio_device_write()` appends the byte to the circular buffer and wakes readers. Release unregisters the serio port if it was registered; otherwise it frees the unused serio directly.

## State and persistence
State is per file descriptor. `running` freezes the port type after registration and controls release cleanup. The circular buffer stores pending bytes for userspace reads; overflow logs a warning but still advances `head`, making old data indistinguishable from overwritten data. No state persists after closing the device.

## Dependencies and integration points
The module uses miscdevice minor `USERIO_MINOR`, UAPI command definitions from `uapi/linux/userio.h`, usercopy, poll/waitqueues, and the serio core. It is useful for userspace-emulated input devices and protocol testing.

## Risks
The 16-byte buffer is tiny and overflow only warns; a slow userspace client can lose driver writes. Reads wait only for buffer non-empty and do not check a dead/disconnected state beyond file lifetime. Command ABI requires exact `sizeof(struct userio_cmd)`, so UAPI layout compatibility matters. Register is asynchronous via serio core, so immediate post-register commands may race actual driver binding.

## Test signals
Test command size validation, missing port type rejection, type changes before and after registration, duplicate register returning `-EBUSY`, interrupt injection before registration returning `-ENODEV`, blocking/nonblocking reads, poll readiness, buffer overflow warning, and release cleanup in both registered and unregistered states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/userio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/xilinx_ps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/xilinx_ps2.c

## Purpose
`xilinx_ps2.c` is a platform serio provider for the Xilinx XPS PS/2 controller. It binds through device tree, maps the big-endian MMIO register block, resets the controller, exposes a `SERIO_8042` port, and reports RX/TX error conditions as serio flags.

## Important APIs, types, and functions
`struct xps2data` holds IRQ, spinlock, MMIO base, accumulated serio flags, serio pointer, and device. `xps2_of_probe()` handles DT resource discovery and port registration. `sxps2_open()` requests IRQ and enables RX interrupts. `xps2_interrupt()` acknowledges interrupt status, records parity/timeout flags, receives a byte with `xps2_recv()`, and calls `serio_interrupt()`. `sxps2_write()` writes one byte if TX is not full. `sxps2_close()` disables interrupts and frees IRQ.

## Control flow
Probe resolves the memory resource and IRQ from OF, allocates state, requests the memory region, maps registers, disables interrupts, resets the controller, initializes the serio port, and registers it. The IRQ is requested only when the serio port is opened by a protocol driver. Interrupt status is cleared by writing the read value back to IPISR; RX_FULL triggers a receive and dispatch, while RX_ERR, TX_NOACK, and watchdog timeout set flags that are consumed with the next received byte.

## State and persistence
Hardware state is reset at probe and interrupt-enable state follows open/close. `drvdata->flags` accumulates error state until a byte is reported, then is cleared. There is no saved configuration beyond in-memory platform driver data.

## Dependencies and integration points
The driver uses OF address and IRQ APIs, manual memory-region reservation, big-endian MMIO accessors, platform driver registration, and the serio core. It matches `xlnx,xps-ps2-1.00.a` and feeds normal PS/2 keyboard/mouse drivers.

## Risks
TX writes fail with `-EAGAIN` if the transmitter is full and do not wait or retry. IRQ mapping via `irq_of_parse_and_map()` is not explicitly disposed in remove. Probe and remove use manual MMIO resource handling, so failure paths must preserve ordering. Error flags can be set by interrupts without RX_FULL and then apply to a later byte, which may or may not match hardware intent.

## Test signals
Build with OF/platform support, bind to a Xilinx DT node, validate memory-region conflicts, reset behavior, IRQ open/close lifetime, RX_FULL delivery, RX overflow/error logging, TX full returns, and module unload with the input device open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/xilinx_ps2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/sparse-keymap.c -->
# sources/distributed-fs/ceph-client/drivers/input/sparse-keymap.c

## Purpose
`sparse-keymap.c` provides shared helpers for drivers whose firmware scan codes are sparse rather than dense arrays. It copies a `struct key_entry` table into the input device, sets event capabilities, implements input-core get/set keycode callbacks, and reports key or switch events by scancode.

## Important APIs, types, and functions
Exported APIs are `sparse_keymap_setup()`, `sparse_keymap_entry_from_scancode()`, `sparse_keymap_entry_from_keycode()`, `sparse_keymap_report_entry()`, and `sparse_keymap_report_event()`. Internal helpers locate entries by input keymap index or scancode and compute the user-visible key index among `KE_KEY` entries.

## Control flow
Setup counts entries through `KE_END`, devm-duplicates the map, optionally invokes a caller setup callback for each entry, and sets `EV_KEY`, `EV_SW`, `EV_MSC`, `MSC_SCAN`, key bits, or switch bits according to entry type. Keycode get/set use `INPUT_KEYMAP_BY_INDEX` or scalar scancode lookup. Reporting emits MSC scan and key state for keys, optional autorelease, or switch state for `KE_SW` and `KE_VSW`; unknown scan codes are reported as `KEY_UNKNOWN` for diagnostics.

## State and persistence
The copied keymap is stored in `input_dev->keycode` and freed with the device via devm. Runtime remapping mutates the copied `key_entry.keycode` and updates `dev->keybit`; it does not change the original static map or persist across driver rebind.

## Dependencies and integration points
The helper is part of the input core support library and depends on `linux/input/sparse-keymap.h`, input keymap callbacks, devres allocation, and input event reporting. Platform hotkey and special-button drivers commonly call it during probe.

## Risks
`map_size` includes the `KE_END` entry and is assigned to `keycodemax`, so users of index-based APIs must remember that only `KE_KEY` entries are indexable. Setkeycode clears the old key bit only when no other entry uses it, but it does not validate whether the new keycode is in a desired driver-specific range. Unknown scancodes intentionally emit `KEY_UNKNOWN`, which can surprise tests expecting no event.

## Test signals
Unit-style tests should cover setup with key, switch, virtual-switch, and custom setup callbacks; get/set by index and scancode; duplicate keycodes; unknown scancode reporting; autorelease behavior; and preservation of switch semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/sparse-keymap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/input/tablet/Kconfig

## Purpose
This Kconfig file defines the tablet-driver menu and build-time configuration symbols for USB Acecad, Aiptek, Hanwang, KB Gear, Pegasus, and serial Wacom protocol 4 tablets.

## Important APIs, types, and functions
The key symbols are `INPUT_TABLET`, `TABLET_USB_ACECAD`, `TABLET_USB_AIPTEK`, `TABLET_USB_HANWANG`, `TABLET_USB_KBTAB`, `TABLET_USB_PEGASUS`, and `TABLET_SERIAL_WACOM4`. USB drivers depend on `USB_ARCH_HAS_HCD` and select `USB`; the Wacom serial driver selects `SERIO`.

## Control flow
`menuconfig INPUT_TABLET` gates the submenu but does not by itself build code. When enabled, users can select individual tristate drivers, each with help text documenting supported hardware and module names.

## State and persistence
Configuration state is persisted in the kernel `.config`. The file has no runtime state, but its symbol values control which objects are compiled into vmlinux or modules.

## Dependencies and integration points
These options feed the tablet Makefile through `obj-$(CONFIG_...)` entries. They also surface dependency expectations: USB host support for USB tablets, input event userspace interfaces for practical use, and serio for serial Wacom devices.

## Risks
The USB options select `USB` but depend only on `USB_ARCH_HAS_HCD`, so build coverage should ensure this remains valid across architectures. Help text can become stale if device ID coverage changes. `INPUT_TABLET` being a bool menu gate may hide individual symbols if disabled.

## Test signals
Kconfig tests should verify all symbols are visible with their dependencies met, module names match Makefile targets, Wacom pulls in `SERIO`, USB drivers pull in `USB`, and all combinations compile as built-in and modules where allowed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/Makefile -->
# sources/distributed-fs/ceph-client/drivers/input/tablet/Makefile

## Purpose
This Makefile maps tablet Kconfig symbols to the driver object files that implement each supported tablet family.

## Important APIs, types, and functions
The file has six `obj-$(CONFIG_...)` assignments: `acecad.o`, `aiptek.o`, `hanwang.o`, `kbtab.o`, `pegasus_notetaker.o`, and `wacom_serial4.o`.

## Control flow
Kbuild evaluates each assignment according to the corresponding Kconfig tristate. Built-in selections compile into the kernel image, module selections produce loadable modules, and unset symbols omit the object.

## State and persistence
There is no runtime state. Build state is derived from `.config` and Kbuild's generated objects.

## Dependencies and integration points
The Makefile integrates the tablet directory with the kernel build system and must remain aligned with `drivers/input/tablet/Kconfig` symbol names and with source filenames.

## Risks
Misspelled symbols or object names silently break driver builds for a configuration. Adding a driver requires updating both Kconfig and this Makefile.

## Test signals
Build each tablet symbol as `m` and `y`, check generated module names, and run `make drivers/input/tablet/` or allmodconfig-style builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/acecad.c -->
# sources/distributed-fs/ceph-client/drivers/input/tablet/acecad.c

## Purpose
`acecad.c` is a USB input driver for Acecad Flair and Acecad 302 tablets. It decodes fixed 8-byte interrupt reports into pen proximity, coordinates, pressure, touch, and stylus button events.

## Important APIs, types, and functions
`struct usb_acecad` stores device strings, USB interface, input device, interrupt URB, coherent DMA buffer, and DMA address. Core functions are `usb_acecad_probe()`, `usb_acecad_irq()`, `usb_acecad_open()`, `usb_acecad_close()`, and `usb_acecad_disconnect()`. The USB ID table distinguishes Flair and 302 by `.driver_info`.

## Control flow
Probe requires exactly one interrupt-in endpoint, allocates driver/input objects, an 8-byte coherent buffer, and a URB. It builds the input device name/phys path, sets key and absolute capabilities, applies model-specific X/Y/pressure ranges, fills the interrupt URB, and registers the input device. Opening submits the URB; each successful interrupt decodes report bits, emits input events, syncs, and resubmits. Close kills the URB; disconnect unregisters input and frees USB resources.

## State and persistence
The driver stores only per-device runtime pointers and the DMA report buffer. Input state is maintained by the input core. No tablet settings are persisted or programmed by the driver.

## Dependencies and integration points
It depends on the USB input helper APIs, interrupt endpoints, coherent DMA buffers, input absolute/key events, and USB module matching for vendor `0x0460` device IDs `0x0004` and `0x0008`.

## Risks
Probe uses `usb_maxpacket()` but always allocates 8 bytes; the URB transfer length is clamped to 8, so endpoint descriptors with smaller packets are tolerated but malformed packets may result in stale fields. Name construction can be empty until the model fallback path. Disconnect relies on input unregister closing the device and killing the URB through `close()` when open.

## Test signals
Test both USB IDs, endpoint rejection paths, input capability ranges per model, packet decoding for proximity out and in-range events, URB resubmission after transient errors, open/close behavior, and disconnect while the input node is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/acecad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/aiptek.c -->
# sources/distributed-fs/ceph-client/drivers/input/tablet/aiptek.c

## Purpose
`aiptek.c` supports Aiptek HyperPen USB tablets and related Genius/KYE devices. It decodes six proprietary report formats, programs tablet mode and resolution through HID class control reports, exposes extensive sysfs tuning attributes, and reports stylus, mouse, macro-key, tilt, wheel, pressure, and diagnostic events.

## Important APIs, types, and functions
`struct aiptek` holds the input device, USB interface/URB/DMA buffer, discovered feature codes, current and staged settings, packet/jitter state, macro tracking, and USB path. `struct aiptek_settings` contains pointer mode, coordinate mode, tool mode, tilt, wheel, button mappings, and command delays. Important functions include `aiptek_irq()`, `aiptek_open()`, `aiptek_close()`, `aiptek_set_report()`, `aiptek_get_report()`, `aiptek_command()`, `aiptek_query()`, `aiptek_program_tablet()`, the sysfs show/store functions, `aiptek_probe()`, and `aiptek_disconnect()`.

## Control flow
Probe allocates input and USB resources, initializes default settings and capabilities, finds an interrupt-in endpoint, fills the URB, then tries several programming delays until tablet queries return sane X limits. `aiptek_program_tablet()` sends resolution, model, ODM, firmware, X/Y size, pressure, coordinate-mode, macro-key, and autogain commands. Runtime interrupts decode report 1 relative motion, report 2 stylus absolute data, report 3 mouse absolute data, reports 4/5 macro keys from stylus or mouse, and report 6 official macro reports. Sysfs stores update `newSetting`; writing `execute` copies staged settings to `curSetting` and reprograms hardware.

## State and persistence
Settings are per-device in memory. `curSetting` is active, while `newSetting` is staged until `execute`. Hardware is reprogrammed with those settings but the driver does not persist them across unplug or reboot. Runtime state includes event count, diagnostic code, jitter delay window, previous tool, and last macro key pressed.

## Dependencies and integration points
The driver uses USB input APIs, HID `SET_REPORT`/`GET_REPORT` control messages, unaligned little-endian helpers, input ABS/REL/KEY/MSC events, sysfs device groups attached to the USB driver, and module parameters `programmableDelay` and `jitterDelay`.

## Risks
This is a large legacy parser with many mode-dependent paths. Sysfs settings are not protected by a dedicated lock against interrupt handling, so staged/active changes around `execute` can race with event reporting. `store_tabletWheel()` accepts any integer despite defined wheel range constants. `map_str_to_val()` uses prefix matching by write length, so short strings can match unexpectedly. Macro index checks compare signed values with `ARRAY_SIZE()` and report 6 releases neighboring keys in a non-obvious way. Control programming failures during probe are partly inferred from axis size rather than direct error checks.

## Test signals
Use USB ID coverage for Aiptek and KYE IDs, endpoint discovery failure tests, report decoding fixtures for all six report IDs, pointer-mode rejection diagnostics, relative/absolute mismatch diagnostics, jitter delay transitions, macro press/release behavior, sysfs parse/execute semantics, programming-delay fallback, and disconnect/open URB lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/aiptek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/hanwang.c -->
# sources/distributed-fs/ceph-client/drivers/input/tablet/hanwang.c

## Purpose
`hanwang.c` is a USB input driver for Hanwang Art Master II/III/HD tablets. It maps product IDs to feature tables, decodes pen/cursor/eraser/pad packets, and reports coordinates, pressure, tilt, wheel, pad buttons, and tool identity.

## Important APIs, types, and functions
`struct hanwang_features` describes product ID, model name, tablet type, packet length, coordinate ranges, tilt ranges, and pressure range. `struct hanwang` stores the USB/input state, current tool/id, feature pointer, names, and URB buffer. Main functions are `get_features()`, `hanwang_probe()`, `hanwang_parse_packet()`, `hanwang_irq()`, `hanwang_open()`, `hanwang_close()`, and `hanwang_disconnect()`.

## Control flow
Probe accepts a vendor/interface-class match, validates at least one endpoint, finds product features from the USB descriptor, allocates a coherent packet buffer and URB, configures input capabilities from static event arrays and feature ranges, submits the interrupt URB on open, and registers the input device. Packet parsing handles `0x02` tool data/proximity packets and `0x0c` pad packets, with type-specific pressure and pad decoding.

## State and persistence
Current tool and current ID are kept in memory to report proximity and `ABS_MISC`. Feature tables are static and selected at probe. There is no persistent configuration or hardware programming.

## Dependencies and integration points
The driver integrates with USB interrupt input, input ABS/KEY/MSC events, endian helpers for big-endian coordinate fields, and module matching based on vendor plus HID-like interface class/subclass/protocol.

## Risks
The USB ID table matches broad vendor/interface information and relies on `get_features()` to reject unknown product IDs. Probe does not verify that endpoint 0 is interrupt-in before filling the URB. Art Master II has special proximity handling and ignores pad packets; changes to shared parsing can regress that path. Packet parsing assumes `features->pkg_len` bytes are valid for all field accesses.

## Test signals
Test every product in `features_array`, unknown product rejection, endpoint validation, pressure formulas for Art Master III vs HD/II, proximity in/out for stylus and eraser, pad packet decoding for III and HD, Art Master II special cases, and disconnect while an URB is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/hanwang.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/kbtab.c -->
# sources/distributed-fs/ceph-client/drivers/input/tablet/kbtab.c

## Purpose
`kbtab.c` is a compact USB driver for the KB Gear JamStudio tablet. It converts 8-byte interrupt reports into pen coordinates, right-button state, and either left-click-by-pressure or raw pressure events.

## Important APIs, types, and functions
`struct kbtab` stores the DMA buffer, input device, USB interface, URB, and physical path. `kbtab_irq()` decodes reports. `kbtab_probe()` validates an interrupt-in endpoint, allocates resources, sets input capabilities, and registers the device. `kbtab_open()` submits the URB and `kbtab_close()` kills it. Module parameter `kb_pressure_click` controls pressure threshold or raw pressure reporting when set to `-1`.

## Control flow
Probe matches vendor `0x084e` product `0x1001`, configures `EV_KEY` and `EV_ABS`, sets X/Y/pressure ranges, and fills an 8-byte interrupt URB. Each interrupt reports `BTN_TOOL_PEN`, X/Y from little-endian fields, `BTN_RIGHT`, and either `BTN_LEFT` based on pressure threshold or `ABS_PRESSURE`; then it syncs and resubmits the URB.

## State and persistence
Per-device state is minimal and nonpersistent. The pressure threshold is a module parameter set at load time. The driver always reports the pen tool as present during packets and does not track proximity release state.

## Dependencies and integration points
It uses USB input helpers, coherent DMA, unaligned little-endian access, input event reporting, and module parameter infrastructure.

## Risks
No proximity-out handling means userspace may rely on absence of packets or higher-level heuristics. Threshold mode suppresses pressure events even though ABS_PRESSURE is configured. Only endpoint 0 is considered. The default pressure-to-left-click policy is driver-specific and may not match modern tablet expectations.

## Test signals
Test USB ID binding, invalid endpoint rejection, coordinate decoding, pressure threshold boundaries including `-1`, URB resubmission after transient errors, open/close behavior, and input capability consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/kbtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/pegasus_notetaker.c -->
# sources/distributed-fs/ceph-client/drivers/input/tablet/pegasus_notetaker.c

## Purpose
`pegasus_notetaker.c` drives the Pegasus Mobile Notetaker EN100 and compatible digital pen receivers. It sets the device into XY pen mode with a vendor control report, reads interrupt packets, reports pen position and buttons, and supports USB autosuspend/resume.

## Important APIs, types, and functions
`struct pegasus` stores the USB/input state, coherent buffer, URB, PM mutex, open flag, names, and deferred initialization work. Key functions are `pegasus_control_msg()`, `pegasus_set_mode()`, `pegasus_parse_packet()`, `pegasus_irq()`, `pegasus_init()`, open/close helpers, probe/disconnect, and suspend/resume/reset-resume callbacks.

## Control flow
Probe binds only interface 0, validates packet size, allocates coherent DMA and an interrupt URB, sets input ABS/KEY properties, and registers the input device. Open gets an autosuspend PM reference, submits the URB, then sends the XY mode command. A special command packet schedules work to resend initialization. XY packets report low battery warnings, touch, pen button, tool, X, and Y; pen-up packets with zero coordinates are ignored. Suspend kills the URB and cancels init work; resume resubmits if open; reset-resume reprograms mode then resubmits.

## State and persistence
`is_open` under `pm_mutex` controls whether resume restarts I/O. The mode command changes device state while open and after reset-resume but is not persisted by the driver. Scheduled work is transient and canceled on close/suspend paths.

## Dependencies and integration points
The driver uses USB interrupt and control transfers, HID request constants, input ABS/KEY properties, workqueues, mutexes, and USB runtime PM. It matches vendor `0x0e20` product `0x0101`.

## Risks
Disconnect unregisters the input device before explicitly canceling `init` work; correctness relies on close/suspend paths or absence of pending work, so work lifetime deserves attention. Pen-up packets do not emit release events, potentially leaving tool/touch state if no later packet clears it. The driver sets both `INPUT_PROP_DIRECT` and `INPUT_PROP_POINTER`, which may be semantically ambiguous for userspace.

## Test signals
Test control-message framing, open failure cleanup after URB submit or mode command failure, special-command reinitialization, low-battery warning once, suspend/resume/reset-resume while open and closed, autosuspend references, and disconnect with pending init work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/pegasus_notetaker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/wacom_serial4.c -->
# sources/distributed-fs/ceph-client/drivers/input/tablet/wacom_serial4.c

## Purpose
`wacom_serial4.c` is a serio protocol driver for Wacom protocol 4 serial tablets. It negotiates model, ROM version, resolution, and coordinate limits through ASCII commands, configures packet mode, and decodes seven-byte binary packets into pen/cursor/eraser input events.

## Important APIs, types, and functions
`struct wacom` stores the input device, command completion, expected response type, model flags, resolution and range data, current tool, packet index, data buffer, and phys path. Important functions include response handlers for model/configuration/coordinates, `wacom_handle_packet()`, `wacom_interrupt()`, `wacom_send()`, `wacom_send_and_wait()`, `wacom_setup()`, `wacom_connect()`, and `wacom_disconnect()`. The serio ID table matches `SERIO_RS232` protocol `SERIO_WACOM_IV`.

## Control flow
Connect allocates state, initializes default pressure bit handling, opens the serio port, queries model/version, optionally queries configuration and coordinate strings, sends a model-specific setup command sequence, configures input properties/ranges, and registers the input device. The interrupt handler distinguishes carriage-return-terminated ASCII responses from binary packets whose first byte has the sync bit. A response completes the pending command; a complete packet reports tool proximity, ABS_MISC device ID, X/Y, pressure, stylus buttons or cursor buttons/wheel, and syncs.

## State and persistence
Runtime state is per attached serio port. Model responses determine flags such as screen coverage, stylus2, scrollwheel, eraser mask, extra pressure bits, and ABS resolution. The current tool is tracked to release the previous tool when switching. No state is persisted outside the device session.

## Dependencies and integration points
The driver integrates with the serio bus, serial line discipline/inputattach path, input ABS/REL/KEY events, completions, and Wacom protocol command strings. It assumes serial speed and protocol reset were handled before binding.

## Risks
ASCII response parsing handles timeout by processing partial data, which is needed for some tablets but can accept malformed responses. Unsupported model handling depends on response bytes and may reject compatible devices. Packet parsing does not use the incoming serio error flags. Setup strings include untested model paths and no tilt support despite protocol documentation.

## Test signals
Test model response parsing for Cintiq, Cintiq II, Graphire, PenPartner, ArtPad/Digitizer II, unsupported model rejection, timeout response handling, packet sync recovery after garbage, pressure-bit variants, eraser and cursor transitions, scroll wheel reporting, and disconnect during command wait.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tablet/wacom_serial4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tests/Makefile -->
# sources/distributed-fs/ceph-client/drivers/input/tests/Makefile

## Purpose
This Makefile builds input-core KUnit tests.

## Important APIs, types, and functions
It contains one Kbuild assignment: `obj-$(CONFIG_INPUT_KUNIT_TEST) += input_test.o`.

## Control flow
When `CONFIG_INPUT_KUNIT_TEST` is enabled, Kbuild compiles `input_test.c` into the test object. Otherwise no input tests from this directory are built.

## State and persistence
There is no runtime state in this Makefile. Test inclusion is controlled by kernel configuration.

## Dependencies and integration points
The file connects the input test source to KUnit-enabled kernel builds. It must stay aligned with the Kconfig symbol that defines `CONFIG_INPUT_KUNIT_TEST`.

## Risks
Adding additional tests without updating this Makefile will leave them unbuilt. Renaming the Kconfig symbol or test source requires synchronized changes.

## Test signals
Enable `CONFIG_INPUT_KUNIT_TEST` and verify that the `input_core` KUnit suite is present and runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tests/input_test.c -->
# sources/distributed-fs/ceph-client/drivers/input/tests/input_test.c

## Purpose
`input_test.c` is a KUnit suite for selected input-core helpers. It creates a virtual input device for each test and verifies polling setup, timestamp access, device-ID matching, and grab exclusivity behavior.

## Important APIs, types, and functions
`input_test_init()` allocates and registers a virtual input device with left/right button capabilities; `input_test_exit()` unregisters it. Test cases are `input_test_polling()`, `input_test_timestamp()`, `input_test_match_device_id()`, and `input_test_grab()`. The suite is registered with `kunit_test_suite(input_test_suite)`.

## Control flow
Each test starts with a registered `struct input_dev` in `test->priv`. Polling verifies `input_get_poll_interval()` fails before `input_setup_polling()` and succeeds after `input_set_poll_interval()`. Timestamp verifies a valid default monotonic timestamp and a set/get round trip. Device-ID matching toggles match flags and fields. Grab testing creates synthetic handles and confirms only one handle can hold an input grab until release.

## State and persistence
State is per KUnit test instance and cleaned up in `exit`. The grab test temporarily increments input device references through `input_get_device()` and balances with `input_put_device()`.

## Dependencies and integration points
The suite depends on KUnit, input core allocation/registration, input polling APIs, timestamp APIs, device ID matching, and grab/release semantics. It is built by the local tests Makefile under `CONFIG_INPUT_KUNIT_TEST`.

## Risks
The synthetic `struct input_handler`, `input_handle`, and `input_device_id` objects are stack/local and only partially initialized, so changes in input core expectations could require more complete setup. The grab test is sensitive to reference balancing and shared device state. The suite covers only a small part of input core behavior.

## Test signals
Run the `input_core` KUnit suite, especially after changes to polling, timestamp initialization, input ID matching flags, or grab locking. Add negative tests if future input core changes add validation to handlers or handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/tests/input_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touch-overlay.c -->
# sources/distributed-fs/ceph-client/drivers/input/touch-overlay.c

## Purpose
`touch-overlay.c` provides helper functions for touchscreen overlay regions described in firmware. It maps rectangular segments that either define a touchscreen sub-area or on-screen buttons, adjusts coordinates, reports overlay key presses, and filters contacts that should not be processed by the client touchscreen driver.

## Important APIs, types, and functions
`struct touch_overlay_segment` stores rectangle origin/size, optional key code, pressed state, and tracking slot. Exported APIs are `touch_overlay_map()`, `touch_overlay_get_touchscreen_abs()`, `touch_overlay_mapped_touchscreen()`, `touch_overlay_sync_frame()`, and `touch_overlay_process_contact()`. Internal helpers parse firmware properties and test whether a contact lies inside a segment.

## Control flow
`touch_overlay_map()` looks for a `touch-overlay` child node under the input device's parent, allocates one segment per available child, reads `x-origin`, `y-origin`, `x-size`, `y-size`, and optional `linux,code`, sets key capabilities for button segments, and appends to the caller's list. During event processing, button segments are checked first to prioritize overlapping buttons. A contact on a button reports key down and marks the MT slot as consumed for the frame. Contacts in a touchscreen segment are shifted to that segment's origin; contacts outside a defined touchscreen area are dropped. Sync releases pressed buttons whose tracked slot is no longer used.

## State and persistence
Segments are devm-allocated and live with the parent device. Each button segment tracks `pressed` and `slot` across frames. Coordinate shifts mutate the caller-provided `input_mt_pos`. There is no persistent state beyond firmware-defined geometry.

## Dependencies and integration points
The helper uses firmware node/property APIs, input multitouch slot state, input key reporting, list management, and `linux/input/touch-overlay.h`. Client touchscreen drivers own the segment list and call these helpers from their report paths.

## Risks
`touch_overlay_get_touchscreen_abs()` uses `x_size - 1` and `y_size - 1`; zero-sized firmware properties would underflow. Button `slot` defaults to zero, so sync logic must only release when `pressed` is true. The first touchscreen segment controls outside-area filtering; multiple touchscreen areas or ordering mistakes may not behave as expected. Clients must call `touch_overlay_sync_frame()` for slot release semantics to work.

## Test signals
Test firmware parsing with no overlay, touchscreen-only, button-only, overlapping button/touchscreen, missing and malformed properties, zero/edge sizes, coordinate shifting, MT slot consumption, slide-out button release, and sync-frame release when a slot disappears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touch-overlay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen.c

## Purpose
`touchscreen.c` implements generic helpers for touchscreen and 2D pointing-device drivers. It parses common firmware properties for axis limits, fuzz, pressure, inversion, and X/Y swapping, then applies those transforms when reporting positions.

## Important APIs, types, and functions
Exported APIs are `touchscreen_parse_properties()`, `touchscreen_set_mt_pos()`, and `touchscreen_report_pos()`. Internal helpers are `touchscreen_get_prop_u32()`, `touchscreen_set_params()`, and `touchscreen_apply_prop_to_x_y()`. The caller-visible state is `struct touchscreen_properties`.

## Control flow
Parsing allocates absinfo, chooses single-touch or MT axes, reads min/size/fuzz properties for X and Y and pressure properties, and updates existing axis parameters only when data is present. If a properties struct is provided, it records maximum X/Y, detects inversion and swapping booleans, normalizes inverted axes to start at zero, and swaps X/Y absinfo when requested. Reporting helpers apply inversion then swapping before filling `input_mt_pos` or reporting ABS_X/ABS_Y or ABS_MT_POSITION_X/Y.

## State and persistence
The helper mutates `input_dev->absinfo` during probe/setup and stores transform flags and pre-inversion maxima in the caller's `struct touchscreen_properties`. There is no global or persistent state.

## Dependencies and integration points
It depends on generic device properties, input absinfo allocation, input multitouch position structs, and exported symbols consumed by touchscreen drivers throughout `drivers/input/touchscreen`.

## Risks
Drivers must set up the relevant ABS axes before parsing; otherwise parameters are ignored with a warning. Size properties are converted to maximum by subtracting one, so zero sizes underflow. Transform order is fixed as invert X/Y before swap, and drivers must use the helper consistently for all reported coordinates.

## Test signals
Test no-property defaults, min/size/fuzz overrides, single-touch vs multitouch axis selection, pressure properties, missing ABS axes warning path, inverted axes normalization, swapped axes, combined invert+swap transforms, and both report APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/88pm860x-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/88pm860x-ts.c

## Purpose
`88pm860x-ts.c` is a resistive touchscreen driver for the Marvell 88PM860x PMIC/MFD family. It configures GPADC/TSI registers, enables measurement channels on open, reads touch samples on IRQ, computes pressure resistance, and reports ABS_X, ABS_Y, ABS_PRESSURE, and BTN_TOUCH.

## Important APIs, types, and functions
`struct pm860x_touch` stores the input device, I2C client, parent `pm860x_chip`, IRQ, and X-plate resistance. `pm860x_touch_dt_init()` parses DT child-node configuration and writes ADC timing registers. `pm860x_touch_probe()` handles platform data fallback, GPADC enable, devm allocation, IRQ registration, and input setup. `pm860x_touch_handler()` reads eight measurement registers and reports events. Open/close enable or disable measurement bits in `MEAS_EN3`.

## Control flow
Probe gets the platform IRQ, initializes hardware from DT `touch` node or legacy platform data, enables GPADC, allocates input state, requests a threaded IRQ, sets input capabilities and 12-bit ranges, and registers the input device. Open sets pen detect and X/Y/Z measurement enable bits. On IRQ, the handler bulk-reads X, Y, Z1, and Z2 registers, checks pen-down, computes touch resistance when possible, reports contact or release, and syncs. Close clears the measurement enable bits.

## State and persistence
Register programming persists in the PMIC while the driver is loaded and the device is open, but is not saved across reboot. `res_x` comes from firmware or platform data and controls pressure calculation. Runtime input state is held by the input core.

## Dependencies and integration points
The driver depends on the 88PM860x MFD core, I2C register helpers, platform device children, optional OF properties, threaded IRQs, and input core. It exposes module alias `platform:88pm860x-touch`.

## Risks
Pressure calculation uses integer `z2 / z1 - 1`, losing precision before scaling and risking poor pressure values. DT initialization treats missing child node as fatal unless platform data exists. The handler ignores bulk-read errors except by returning `IRQ_HANDLED`. Input ranges are hardcoded to 12-bit maxima rather than using parsed calibration bounds. Open/close register writes are not synchronized with IRQ handling beyond hardware semantics.

## Test signals
Test DT and platform-data initialization paths, invalid/missing IRQ, GPADC register write failures, measurement enable/disable on open/close, pen-down and pen-up sample decoding, pressure calculation with zero and nonzero `res_x`/`z1`, and threaded IRQ behavior under I2C read errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/88pm860x-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/Kconfig

## Purpose
This Kconfig file defines the touchscreen driver menu and configuration symbols for a broad set of serial, I2C, SPI, USB, MFD, IIO, AC97, platform, and SoC touchscreen controllers.

## Important APIs, types, and functions
The top-level `INPUT_TOUCHSCREEN` bool gates all child options. Child symbols include concrete drivers such as `TOUCHSCREEN_88PM860X`, `TOUCHSCREEN_ADS7846`, `TOUCHSCREEN_ATMEL_MXT`, `TOUCHSCREEN_GOODIX`, `TOUCHSCREEN_USB_COMPOSITE`, `TOUCHSCREEN_WM97XX`, and many others, plus helper/core symbols such as `TOUCHSCREEN_GOODIX_BERLIN_CORE`, `TOUCHSCREEN_TSC200X_CORE`, and feature booleans such as `TOUCHSCREEN_TSC2007_IIO`.

## Control flow
When the touchscreen menu is enabled, each config entry applies dependencies, selects helper libraries such as `REGMAP_I2C`, `REGMAP_SPI`, `FW_LOADER`, `CRC_*`, `VIDEOBUF2_*`, `SERIO`, or `USB`, and describes module names. Some entries are hidden core symbols selected by bus-specific options, and several USB composite protocol options default to `y` under `TOUCHSCREEN_USB_COMPOSITE`.

## State and persistence
All state is build configuration stored in `.config`. The symbols determine which source files are compiled and which helper subsystems are pulled in. There is no runtime state in this file.

## Dependencies and integration points
This file integrates touchscreen drivers with the broader kernel configuration graph: bus subsystems, MFD parents, architecture guards, GPIO, OF/ACPI, IIO, HWMON, media/V4L, thermal, AC97, and COMPILE_TEST. It must stay synchronized with `drivers/input/touchscreen/Makefile`.

## Risks
With many options, dependency drift is the main risk: missing selects can break builds, excessive selects can force unwanted subsystems, and architecture-only dependencies can reduce compile coverage. Core/helper split symbols must remain hidden or selected consistently. Module-name help text can become stale when Makefile objects change.

## Test signals
Use allmodconfig, allyesconfig, randconfig, and COMPILE_TEST builds to catch dependency issues. Specifically test bus split families such as AD7879, Goodix Berlin, Cypress TTSP, TSC200x, WM97xx, and USB composite protocol booleans, plus serial options that must select `SERIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/Makefile -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/Makefile

## Purpose
This Makefile maps touchscreen Kconfig symbols to their implementation object files and defines a few composite module object lists.

## Important APIs, types, and functions
The file defines composite objects such as `wm97xx-ts-y := wm97xx-core.o`, `goodix_ts-y := goodix.o goodix_fwupload.o`, `tsc2007-y := tsc2007_core.o`, and conditional additions for `tsc2007_iio.o` and WM97xx chip variants. It then maps dozens of `CONFIG_TOUCHSCREEN_*` symbols to `.o` files.

## Control flow
Kbuild evaluates `obj-$(CONFIG_...)` assignments to include built-in or module objects. Composite object variables collect multiple source files into one module target, such as Goodix firmware upload support or WM97xx chip-specific support.

## State and persistence
There is no runtime state. Build outputs depend entirely on `.config` and Kbuild rules.

## Dependencies and integration points
This file is the build counterpart to touchscreen Kconfig. It must align symbol names, source filenames, composite module names, and helper-core selections for all touchscreen drivers.

## Risks
The large list is prone to symbol/object mismatches. Composite module rules can accidentally omit optional pieces if their Kconfig symbol logic changes. Adding, renaming, or splitting a driver requires coordinated Makefile and Kconfig updates.

## Test signals
Run allmodconfig and targeted builds for representative simple, composite, bus-split, and optional-helper drivers: `goodix_ts`, `wm97xx-ts`, `tsc2007`, `ad7879-*`, `goodix_berlin_*`, serial serio touchscreens, and USB composite support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/Makefile -->
