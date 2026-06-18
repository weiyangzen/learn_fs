# subset-b-005521 Research

Grouped source research for USB misc, usbmon, and MediaTek MTU3 sources under `sources/distributed-fs/ceph-client/drivers/usb`. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/uss720.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/uss720.c

## Purpose

`uss720.c` is a USB parallel-port bridge driver for Lucent USS720 based cables. It binds known USB VID/PID adapters, exposes them as Linux parport instances, and translates parport register, EPP, ECP, and compatibility operations into USS720 USB control and bulk transfers.

## Important APIs, Types, and Functions

Important state is `struct parport_uss720_private`, which holds the USB device, registered `struct parport`, cached USS720 registers, async URB list, spinlock, and kref. `struct uss720_async_request` wraps a control URB, setup packet, completion, register snapshot, list node, and private reference. `submit_async_request()`, `async_complete()`, `get_1284_register()`, and `set_1284_register()` implement the register access layer. `change_mode()`, `clear_epp_timeout()`, and the `parport_uss720_*` callbacks implement the parport operations table. `uss720_probe()` and `uss720_disconnect()` own USB binding and teardown.

## Control Flow

Probe requires three alternate settings, switches to alternate setting 2, registers a parport, initializes USS720 registers to manual PS/2-like mode, verifies register access, announces the port, and stores the parport in USB interface data. Runtime parport calls issue control URBs for 1284 register reads and writes, with reads waiting up to one second and writes submitted asynchronously. Bulk endpoint 1 is used for EPP/ECP/compat writes, and endpoint 2 is used for ECP reads. Disconnect clears interface data, removes the parport, kills pending async URBs, and drops the private kref.

## State and Persistence Behavior

The only persistent runtime state is in memory: cached register bytes, pending async requests, parport state snapshots, and krefs. Hardware mode and FIFO allocation live in the adapter and are reprogrammed on probe or mode changes. There is no file-backed persistence. `priv->reg` is intentionally a soft cache for control and ECR bits, updated after register reads and selected writes.

## Dependencies and Integration Points

The driver integrates Linux USB core, URBs, `usb_bulk_msg()`, and the parport core. It shares IEEE 1284 helpers for nibble and byte reads and relies on USS720 vendor-specific control requests 3 and 4. It competes conceptually with `usblp`, and module init prints that this driver is for nonstandard parallel protocols rather than normal USB printing.

## Risks and Test Signals

Risks include stale cached control bits, timeout-driven unlink of all async requests, interrupt-like parport callbacks from async completions, limited validation of endpoint layout beyond endpoint count, and partial error unwinding if parport registration succeeds but later USB register access fails. Test signals include successful probe on each supported cable ID, parport mode transitions through SPP/PS2/EPP/ECP, EPP timeout clearing, disconnect while async reads are pending, and bulk transfer failures returning partial byte counts without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/uss720.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/yurex.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/yurex.c

## Purpose

`yurex.c` is a character-device USB driver for the Meywa-Denki/KAYAC YUREX gadget. It exposes the device counter value through `/dev/yurexN`, accepts command writes for LED, animation, read, version, and set-count operations, and reports asynchronous counter updates through SIGIO.

## Important APIs, Types, and Functions

`struct usb_yurex` stores the USB device/interface, interrupt-in URB and coherent buffer, HID class control URB and coherent buffer, kref, I/O mutex, disconnect flag, fasync queue, wait queue, spinlock, and signed 64-bit BBU counter. `yurex_probe()` allocates URBs and buffers, configures a HID SET_REPORT control request, submits the interrupt URB, and registers a USB minor. `yurex_interrupt()` decodes `CMD_COUNT`, `CMD_READ`, and `CMD_ACK`. File operations `yurex_open()`, `yurex_read()`, `yurex_write()`, `yurex_release()`, and `yurex_fasync()` implement userspace access.

## Control Flow

Probe finds an interrupt-in endpoint, starts a continuously resubmitted interrupt URB, then registers the class device. Incoming interrupt packets either update `dev->bbu` from five payload bytes and send SIGIO, or wake command writers after an ACK. Writes build an 8-byte HID output report padded with `0xff`, submit the control URB, wait up to two seconds for ACK or callback wakeup, kill the URB to ensure it is idle, and optionally update the cached counter for successful SET commands. Disconnect deregisters the minor, poisons both URBs, marks the device disconnected under mutex, wakes readers/writers, signals fasync listeners, and drops the kref.

## State and Persistence Behavior

Runtime state is the cached BBU counter and in-flight URBs. `bbu` starts at `-1`, is updated by interrupt reports or successful SET writes, and is guarded by a spinlock. Open file references hold krefs; disconnect prevents new I/O with `disconnected`. No state is persisted across unplug or module reload.

## Dependencies and Integration Points

The driver depends on USB core, USB class minors, HID report constants, coherent DMA buffers, `simple_read_from_buffer()`, wait queues, fasync, and user-copy helpers. It presents a simple character device rather than using the HID input stack, but sends commands as HID class output reports.

## Risks and Test Signals

Risks include trusting short command buffers for commands that read `buffer[1]`, control URB serialization around a single shared buffer, ACK timeout ambiguity, and ensuring poisoned URBs cannot wake freed objects. Test signals include read format after interrupt count packets, write commands `A`, `L`, `R`, `V`, `S123`, numeric-only SET, disconnect during blocking write, fasync SIGIO on counter update, and probe failure cleanup after each allocation stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/yurex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/mon/Kconfig

## Purpose

`drivers/usb/mon/Kconfig` defines `CONFIG_USB_MON`, the build option for the USB Monitor facility that captures USB traffic between peripheral drivers and host-controller drivers.

## Important APIs, Types, and Functions

This file contributes one tristate symbol, `USB_MON`, with user-visible prompt "USB Monitor". It does not define C APIs, but its symbol controls whether `usbmon.o` and its text, binary, stat, and main components are built.

## Control Flow

There is no runtime control flow. During configuration, users can choose built-in, module, or disabled. The help text points readers to `Documentation/usb/usbmon.rst` and recommends enabling it when allowed.

## State and Persistence Behavior

The selected Kconfig value persists in the kernel build configuration. At runtime, state is owned by the compiled usbmon module, not this file.

## Dependencies and Integration Points

The symbol has no explicit dependency in this file, but it lives under the USB driver tree and is consumed by the local Makefile through `obj-$(CONFIG_USB_MON) += usbmon.o`.

## Risks and Test Signals

Risks are mostly configuration exposure: enabling usbmon creates privileged capture interfaces that can reveal device data. Test signals are `.config` values for built-in and module builds, successful creation of `usbmon.o`, and visibility of debugfs and character-device monitor endpoints when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/mon/Makefile

## Purpose

`drivers/usb/mon/Makefile` builds the USB Monitor composite object when `CONFIG_USB_MON` is enabled.

## Important APIs, Types, and Functions

The key build variable is `usbmon-y`, which combines `mon_main.o`, `mon_stat.o`, `mon_text.o`, and `mon_bin.o`. `obj-$(CONFIG_USB_MON)` links that composite as `usbmon.o`.

## Control Flow

There is no runtime control flow. Kbuild evaluates `CONFIG_USB_MON`; if enabled, the four implementation objects are compiled and linked into one module or built-in object according to the tristate selection.

## State and Persistence Behavior

The file has no runtime state. It preserves the module composition contract: `mon_main` supplies lifecycle and bus fanout, while `mon_text`, `mon_bin`, and `mon_stat` supply user interfaces.

## Dependencies and Integration Points

It integrates with Linux Kbuild and depends on the object-level symbols declared in `usb_mon.h`, especially `mon_text_init/exit`, `mon_bin_init/exit`, and `mon_fops_stat`.

## Risks and Test Signals

Risks include missing an object if a new usbmon interface is added, or link failures if interface functions are renamed. Test signals include `make M=drivers/usb/mon`, module load/unload, and checking that both text debugfs and binary character-device paths are present in the built object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/mon_bin.c -->
# sources/distributed-fs/ceph-client/drivers/usb/mon/mon_bin.c

## Purpose

`mon_bin.c` implements usbmon's binary userspace API. It provides `/dev/usbmonN` character devices with per-open ring buffers, event records for URB submit/error/complete callbacks, ioctl-based fetch and statistics, poll support, and read-only mmap access for capture tools.

## Important APIs, Types, and Functions

Public ABI structures include `struct mon_bin_hdr`, `mon_bin_get`, `mon_bin_mfetch`, and `mon_bin_stats`, plus compat 32-bit variants. `struct mon_reader_bin` is the per-open reader containing buffer offsets, page map, wait queue, locks, mmap count, reader callbacks, and drop counter. Core functions are `mon_bin_event()`, `mon_bin_open()`, `mon_bin_read()`, `mon_bin_ioctl()`, `mon_bin_fetch()`, `mon_bin_flush()`, `mon_bin_mmap()`, `mon_bin_add()`, and `mon_bin_init()`.

## Control Flow

Open resolves the bus minor, allocates a default 300 KiB page-backed ring, registers reader callbacks with `mon_reader_add()`, and stores the reader on the file. URB callbacks allocate aligned packet areas under `b_lock`, fill a 64-byte API header, optionally copy setup, isochronous descriptors, and data into the ring, shrink if scatterlist copying stops early, then wake readers. Userspace can read packet streams, fetch mmap offsets, flush events, resize the ring when not mmaped, query queue length, or retrieve events with either API header size. Release unregisters the reader and frees all pages.

## State and Persistence Behavior

All capture state is per open file and volatile: ring pages, in/out/read offsets, bytes used, mmap-active count, and drop counter. No events persist after release. `cnt_lost` is reset when userspace reads `MON_IOCG_STATS`; global bus state is managed by `mon_main.c`.

## Dependencies and Integration Points

The file depends on usbmon core reader callbacks, USB URB and endpoint helpers, cdev/class registration, wait queues, poll, compat ioctls, page allocation, mmap fault handling, scatterlist helpers, and user-copy APIs. It creates one `usbmon` class with up to 128 minors and associates each minor with a `mon_bus`.

## Risks and Test Signals

Risks include ring wrap correctness, mmap requiring contiguous packet placement with filler records, large buffer allocation pressure up to 64 MiB, dropped captures under high traffic, highmem or DMA-coalesced scatterlists marked uncapturable, and ABI compatibility between 48-byte and 64-byte headers. Test signals include read and ioctl capture on bus 0 and real bus minors, resize rejection during mmap, nonblocking reads returning `-EWOULDBLOCK`, compat ioctl fetches, isochronous descriptor capture, dropped counter behavior, and module unload after open readers are closed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/mon_bin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/mon_main.c -->
# sources/distributed-fs/ceph-client/drivers/usb/mon/mon_main.c

## Purpose

`mon_main.c` is the usbmon core. It registers hooks with the USB core, tracks all USB buses plus pseudo bus 0, fans URB submit/error/complete events out to active text and binary readers, and coordinates bus add/remove with usbmon interface creation.

## Important APIs, Types, and Functions

Global state includes `mon_lock`, `mon_bus0`, and the `mon_buses` list. Exported helpers are `mon_reader_add()`, `mon_reader_del()`, and `mon_bus_lookup()`. Internal callbacks `mon_submit()`, `mon_submit_error()`, and `mon_complete()` are registered through `struct usb_mon_operations`. Lifecycle functions `mon_init()` and `mon_exit()` initialize text and binary subsystems, register USB bus notifications, create per-bus `struct mon_bus` records, and tear them down.

## Control Flow

Module init initializes text and binary interfaces, creates bus 0, registers usbmon operations, walks existing USB buses under `usb_bus_idr_lock`, and installs a notifier for later bus add/remove. Reader open paths call `mon_reader_add()` under `mon_lock`; the first reader sets `usb_bus->monitored` for the chosen bus or all buses for bus 0. USB core events call into the registered operations, which dispatch to the specific bus and always to bus 0. Bus removal removes debugfs and char-device endpoints, dissolves the USB bus association, and drops the `mon_bus` reference.

## State and Persistence Behavior

State is in-memory only: bus list, reader lists, reader counts, refs, event counters, and lost text counters. `mon_bus` objects are kref-managed and may outlive USB bus removal while readers exist; `mon_dissolve()` nulls `ubus->mon_bus` and `mbus->u_bus` to prevent stale hardware access.

## Dependencies and Integration Points

The file depends on USB core monitor registration, USB bus notifiers and IDR, text/binary/stat usbmon submodules, and the shared `usb_mon.h` types. It is the coordination point that lets multiple frontend formats observe the same URB stream.

## Risks and Test Signals

Risks include locking between `mon_lock` and per-bus spinlocks, handling bus removal with open readers, ensuring bus 0 monitoring toggles all current buses, and not dereferencing dissolved `u_bus`. Test signals include module load after USB buses already exist, hot-add and hot-remove host controllers, simultaneous bus-specific and bus-0 readers, event counters increasing on submit/complete/error paths, and unload refusal or leak diagnostics with outstanding opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/mon_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/mon_stat.c -->
# sources/distributed-fs/ceph-client/drivers/usb/mon/mon_stat.c

## Purpose

`mon_stat.c` implements usbmon's lightweight debugfs statistics reader, the `Ns` files under `/sys/kernel/debug/usbmon`, for inspecting usbmon reader and event counters.

## Important APIs, Types, and Functions

`struct snap` stores one formatted snapshot string. `mon_stat_open()` allocates the snapshot and formats `nreaders`, `cnt_events`, and `cnt_text_lost` from the `mon_bus` in `inode->i_private`. `mon_stat_read()` uses `simple_read_from_buffer()`, and `mon_stat_release()` frees the snapshot. `mon_fops_stat` is exported to `mon_text.c` for debugfs file creation.

## Control Flow

Opening the stat file captures one point-in-time line. Reads return that fixed line according to the file offset. Closing releases the allocated snapshot. The code intentionally does not update while the file is held open.

## State and Persistence Behavior

The stat file maintains only the per-open snapshot buffer. Source counters live in `struct mon_bus`; this file does not mutate them. The source comment notes that it reads through locks, so access is intended for protected debugfs use.

## Dependencies and Integration Points

It depends on debugfs files created by `mon_text_add()`, `mon_bus` fields from `usb_mon.h`, and standard file/user-copy helpers. It is part of the text/debugfs usbmon interface rather than the binary char device.

## Risks and Test Signals

Risks are stale snapshots and unlocked counter reads racing with event updates, acceptable for diagnostics. Test signals include `cat /sys/kernel/debug/usbmon/0s`, reader counts changing after opening text or binary captures, event counts increasing after USB traffic, and `text_lost` increasing when text readers overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/mon_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/mon_text.c -->
# sources/distributed-fs/ceph-client/drivers/usb/mon/mon_text.c

## Purpose

`mon_text.c` implements usbmon's debugfs text readers. It creates `Nt`, `Nu`, and `Ns` files under `/sys/kernel/debug/usbmon`, captures URB events into per-open queues, and formats them as the legacy and extended text usbmon lines.

## Important APIs, Types, and Functions

`struct mon_event_text` stores one captured event including URB id, type, timestamp, bus/device/endpoint, transfer metadata, setup bytes, small data sample, and limited isochronous descriptors. `struct mon_reader_text` owns the event slab, event queue, wait queue, printf buffer, and embedded `mon_reader`. `mon_text_event()`, `mon_text_submit()`, `mon_text_complete()`, and `mon_text_error()` capture events. `mon_text_open()`, `mon_text_read_t()`, `mon_text_read_u()`, and `mon_text_release()` implement file behavior. `mon_text_add()` and `mon_text_init()` create debugfs entries.

## Control Flow

Opening a text file allocates a reader, event slab, print buffer, installs usbmon callbacks, and enables monitoring through `mon_reader_add()`. USB callbacks run under the bus spinlock and allocate a bounded event object with `GFP_ATOMIC`, copying setup data for control submits and up to 32 bytes of data when direction and event type allow. Reads block unless nonblocking, fetch one event from the queue, format it in either `t` or `u` syntax, copy to userspace possibly over multiple reads, then free the event. Release removes the reader and drains queued events before destroying the slab.

## State and Persistence Behavior

State is per open reader: a bounded event queue limited by `EVENT_MAX`, `nevents`, a temporary formatted output buffer, and a unique slab cache. Events are dropped when allocation or queue limits fail; drops increment `mbus->cnt_text_lost`. No capture survives close.

## Dependencies and Integration Points

The file depends on debugfs, usbmon core reader callbacks, USB endpoint and URB helpers, scatterlist access, wait queues, slab caches, and `mon_fops_stat` for stat files. It integrates with `usb_debug_root` and with bus records created by `mon_main.c`.

## Risks and Test Signals

Risks include local DoS if debugfs permissions are weakened, lost events under high traffic, partial capture of only the first scatterlist segment, highmem data being represented by flags instead of copied bytes, and careful release after bus removal. Test signals include reading both `0u` and per-bus `Nt` formats, nonblocking read behavior, isochronous formatting with descriptor caps, `cnt_text_lost` increments under overflow, and close while traffic is arriving.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/mon_text.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/usb_mon.h -->
# sources/distributed-fs/ceph-client/drivers/usb/mon/usb_mon.h

## Purpose

`usb_mon.h` is the shared internal header for usbmon. It defines bus and reader structures, common globals, and the contracts between the main, text, binary, and stat implementations.

## Important APIs, Types, and Functions

`struct mon_bus` represents one USB bus or pseudo bus 0, with bus linkage, lock, USB bus pointer, interface init flags, debugfs/device handles, reader list, kref, and counters. `struct mon_reader` is the embedded callback object for each open capture file and carries submit/error/complete function pointers. Prototypes expose reader add/delete, bus lookup, text and binary add/delete, subsystem init/exit, `mon_lock`, `mon_fops_stat`, and `mon_bus0`.

## Control Flow

The header has no runtime control flow. It establishes that frontend readers register callback triplets with `mon_main.c`, and that `mon_main.c` owns bus lifetime and monitoring toggles while frontend files own per-open buffering.

## State and Persistence Behavior

The structures are runtime-only and protected by `mon_lock` plus per-bus spinlocks as described in comments and use sites. The kref lets dissolved bus objects remain valid while readers are open.

## Dependencies and Integration Points

It depends on kernel list, slab, and kref declarations, while using USB types by pointer to keep includes light. It is the integration boundary for all four usbmon object files.

## Risks and Test Signals

Risks are local ABI coupling: field or callback changes must be reflected across `mon_main.c`, `mon_text.c`, `mon_bin.c`, and `mon_stat.c`. Test signals are compile coverage of every usbmon object, successful text and binary reader registration, and correct kref behavior when bus removal races with open files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mon/usb_mon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/mtu3/Kconfig

## Purpose

`drivers/usb/mtu3/Kconfig` defines configuration symbols for the MediaTek USB3 Dual Role controller driver and its host, gadget, dual-role, and debug build variants.

## Important APIs, Types, and Functions

The main symbol is `USB_MTU3`, a tristate depending on USB or USB_GADGET, MediaTek architecture or compile testing, and extcon availability. The mode choice defines `USB_MTU3_HOST`, `USB_MTU3_GADGET`, and `USB_MTU3_DUAL_ROLE`; dual-role selects `USB_ROLE_SWITCH`. `USB_MTU3_DEBUG` enables debug messages.

## Control Flow

Configuration chooses exactly one operating mode when `USB_MTU3` is enabled. Defaults prefer dual-role when both host and gadget stacks are available, host when only USB host is available, and gadget when only gadget is available.

## State and Persistence Behavior

The selected symbols persist in the kernel build config and control which source files are compiled. Runtime role and hardware state live in the MTU3 driver, not this Kconfig file.

## Dependencies and Integration Points

The symbols drive the MTU3 Makefile and the stub/full declarations in `mtu3_dr.h`. They integrate with xHCI MTK host support, USB gadget core, extcon, and USB role switch infrastructure.

## Risks and Test Signals

Risks include invalid dependency combinations, built-in versus module constraints for host/gadget dependencies, and accidentally excluding needed source objects for a chosen role. Test signals include all three mode builds, compile-test builds on non-MediaTek architectures, and debug builds adding `-DDEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/mtu3/Makefile

## Purpose

`drivers/usb/mtu3/Makefile` assembles the MTU3 composite driver object according to Kconfig-selected role, tracing, debugfs, and debug-message options.

## Important APIs, Types, and Functions

`obj-$(CONFIG_USB_MTU3) += mtu3.o` creates the composite object. `mtu3-y` always includes `mtu3_plat.o`; optional additions include `mtu3_trace.o`, `mtu3_host.o`, gadget objects `mtu3_core.o`, `mtu3_gadget_ep0.o`, `mtu3_gadget.o`, `mtu3_qmu.o`, dual-role `mtu3_dr.o`, and debugfs `mtu3_debugfs.o`. `ccflags-$(CONFIG_USB_MTU3_DEBUG)` adds `-DDEBUG`.

## Control Flow

There is no runtime control flow. Kbuild conditionals select source objects based on `CONFIG_TRACING`, `CONFIG_USB_MTU3_HOST`, `CONFIG_USB_MTU3_GADGET`, `CONFIG_USB_MTU3_DUAL_ROLE`, and `CONFIG_DEBUG_FS`.

## State and Persistence Behavior

The file has no runtime state. It preserves the build-time contract that platform probe is always present, with host/gadget/DRD functionality linked only when configured.

## Dependencies and Integration Points

It integrates with Kbuild, trace header include paths, and the local role abstraction in `mtu3_dr.h`, where missing role objects are replaced by inline stubs.

## Risks and Test Signals

Risks include missing objects for dual-role combinations, stale trace include path behavior, or linking debugfs callers without debugfs implementation. Test signals include building host-only, gadget-only, dual-role, tracing-enabled, debugfs-disabled, and debug-message-enabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3.h -->
# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3.h

## Purpose

`mtu3.h` is the central internal header for the MediaTek MTU3 USB3 dual-role controller. It defines register access helpers, endpoint/request/controller state, QMU descriptor layout, FIFO management, OTG switch state, and prototypes shared by platform, host, gadget, EP0, QMU, debug, and DRD code.

## Important APIs, Types, and Functions

Key types are `struct ssusb_mtk` for the whole SSUSB controller, `struct mtu3` for the gadget/device controller, `struct mtu3_ep` for endpoint state, `struct mtu3_request` for wrapped gadget requests, `struct qmu_gpd` and `struct mtu3_gpd_ring` for Queue Management Unit descriptors, `struct mtu3_fifo_info` for FIFO bitmap allocation, and `struct otg_switch_mtk` for role switching. Inline helpers map from gadget or endpoint objects and wrap MMIO read/write/set/clear. Prototypes cover gadget setup, endpoint configuration, QMU-facing request completion, start/stop, and EP0 ISR handling.

## Control Flow

The header itself has no execution path, but its structures define the runtime flow: platform probe creates `ssusb_mtk`, gadget init creates `mtu3`, endpoints queue `mtu3_request` objects into QMU rings, interrupts dispatch through core and EP0 code, and dual-role code switches host/device state through `otg_switch_mtk`.

## State and Persistence Behavior

All state is runtime memory and MMIO-backed hardware state. Persistent-like flags include role, speed, endpoint flags, softconnect, wakeup ability, U1/U2 enable state, delayed status, hardware version, and FIFO bitmaps, but none survive device removal.

## Dependencies and Integration Points

The header depends on Linux clocks, devices, DMA pools, extcon, PHY, regulator, USB gadget, USB role switch, and local `mtu3_hw_regs.h` and `mtu3_qmu.h`. It is the main compile-time integration point for all MTU3 implementation files.

## Risks and Test Signals

Risks include structure field coupling across many files, register helper misuse without locking, mismatched QMU descriptor bit layout for Gen2-compatible hardware, and endpoint array indexing assumptions. Test signals are full compile coverage of host/gadget/dual-role configs, endpoint enable/disable on every endpoint number, QMU transfer completion, EP0 standard request handling, and suspend/resume using the same shared state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_core.c

## Purpose

`mtu3_core.c` is the hardware access and gadget-device initialization layer for MTU3. It powers and resets the device IP, initializes FIFOs, endpoints, QMU, interrupts, speed/link behavior, and exposes `ssusb_gadget_init/exit/suspend/resume()` to platform and dual-role code.

## Important APIs, Types, and Functions

Important functions include FIFO alloc/free (`ep_fifo_alloc()`, `ep_fifo_free()`), device power and port control (`mtu3_device_enable()`, `mtu3_device_disable()`, `mtu3_dev_power_on()`, `mtu3_dev_power_down()`), interrupt control (`mtu3_intr_enable()`, `mtu3_intr_disable()`), endpoint setup (`mtu3_config_ep()`, `mtu3_deconfig_ep()`, `mtu3_ep_stall_set()`), device lifecycle (`mtu3_start()`, `mtu3_stop()`), memory setup (`mtu3_mem_alloc()`), ISR dispatch (`mtu3_irq()`), and public gadget glue (`ssusb_gadget_init()`, `ssusb_gadget_suspend()`, `ssusb_gadget_resume()`).

## Control Flow

Gadget init allocates `struct mtu3`, obtains the device IRQ and MAC MMIO, links it to `ssusb_mtk`, initializes hardware, sets the DMA mask, registers a threaded IRQ, stops the device for power saving, registers the UDC, and initializes debugfs. Hardware init reads IP version and capabilities, clamps max speed, resets and enables device mode, allocates endpoint arrays and QMU resources, and initializes registers. Runtime interrupts read level-1 status under `mtu->lock` and dispatch link speed changes, U2 common events, U3 LTSSM events, EP0, and QMU interrupts. Start powers on, configures CSR/speed, enables interrupts, and applies pending softconnect; stop reverses this.

## State and Persistence Behavior

State is held in `struct mtu3`: endpoint arrays, FIFO bitmaps, QMU pool, speed, active flags, connection status, hardware version, Gen2 compatibility, and wake/suspend flags. Hardware register state is reinitialized after reset and start. There is no nonvolatile persistence.

## Dependencies and Integration Points

The file depends on platform resources, DMA mask APIs, runtime PM, IRQ registration, QMU helpers, gadget core setup/cleanup, debugfs helpers, tracepoints, and IPPC/MAC register definitions. It is called from `mtu3_plat.c` and cooperates with `mtu3_gadget.c`, `mtu3_gadget_ep0.c`, `mtu3_qmu.c`, and `mtu3_dr.c`.

## Risks and Test Signals

Risks include FIFO bitmap exhaustion, hardware clock polling failures, incorrect max-speed downgrade when U3 port0 is disabled, IRQ handling while stopped, runtime PM imbalance on connect/disconnect speed changes, and error unwinding after IRQ or UDC registration failures. Test signals include probe on U2-only and U3-capable IP, speed-change interrupts for FS/HS/SS/SSP, endpoint config for bulk/int/isoc, QMU error interrupt handling, gadget suspend rejection while connected, and clean remove after partial init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_debug.h -->
# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_debug.h

## Purpose

`mtu3_debug.h` declares optional MTU3 debugfs and trace-debug helpers while providing no-op stubs when debugfs or tracing is disabled.

## Important APIs, Types, and Functions

`struct mtu3_regset` wraps a named `debugfs_regset32`, and `struct mtu3_file_map` maps debugfs file names to `seq_file` show functions. When `CONFIG_DEBUG_FS` is enabled, prototypes expose `ssusb_dev_debugfs_init()`, `ssusb_dr_debugfs_init()`, `ssusb_debugfs_create_root()`, and `ssusb_debugfs_remove_root()`. When tracing is enabled, `mtu3_dbg_trace()` is available; otherwise it is an inline no-op.

## Control Flow

The header has no runtime control flow. Compile-time conditionals decide whether callers link to `mtu3_debugfs.c` and `mtu3_trace.c` or compile to empty operations.

## State and Persistence Behavior

The header defines only helper structures for runtime debugfs state; no persistence exists. Debugfs dentries are owned by `ssusb_mtk` and removed recursively by the implementation.

## Dependencies and Integration Points

It depends on debugfs declarations and forward-declares `struct ssusb_mtk`. It is included by platform, core, and dual-role code to avoid scattering `#ifdef CONFIG_DEBUG_FS` at call sites.

## Risks and Test Signals

Risks include callers assuming debugfs side effects in builds where calls are stubbed, and trace debug calls silently disappearing without `CONFIG_TRACING`. Test signals include compiling with debugfs and tracing both enabled and disabled, and verifying probe/remove succeeds without unresolved symbols in all combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_debugfs.c

## Purpose

`mtu3_debugfs.c` creates MTU3 debugfs controls and diagnostics for register dumps, endpoint state, FIFO allocation, QMU rings/GPDs, probe registers, manual dual-role mode switching, and VBUS control.

## Important APIs, Types, and Functions

Register arrays `mtu3_ippc_regs`, `mtu3_dev_regs`, `mtu3_csr_regs`, and `mtu3_prb_regs` define debugfs regsets. Show functions include `mtu3_link_state_show()`, `mtu3_ep_used_show()`, `mtu3_ep_info_show()`, `mtu3_fifo_show()`, `mtu3_qmu_ring_show()`, and `mtu3_qmu_gpd_show()`. Public helpers are `ssusb_dev_debugfs_init()`, `ssusb_dr_debugfs_init()`, `ssusb_debugfs_create_root()`, and `ssusb_debugfs_remove_root()`.

## Control Flow

Platform probe creates the root directory named after the device. Gadget init adds register regsets, per-endpoint directories, QMU/FIFO views, probe-register read/write files, and link/endpoint summaries. In manual DRD mode, dual-role init adds `mode` and `vbus` writable files. Writes to `mode` queue role switches through `ssusb_mode_switch()`, and writes to `vbus` call `ssusb_set_vbus()`.

## State and Persistence Behavior

Debugfs reflects live hardware and driver state. Endpoint and QMU state reads take `mtu->lock`; probe writes directly modify selected IPPC probe registers. No settings persist after remove, though manual writes affect live role/VBUS state until changed.

## Dependencies and Integration Points

The file depends on debugfs, seq_file, user-copy helpers, regulator state, MTU3 register definitions, endpoint/QMU structures, and dual-role helpers. It is optional through `CONFIG_DEBUG_FS` and called from `mtu3_plat.c`, `mtu3_core.c`, and `mtu3_dr.c`.

## Risks and Test Signals

Risks include privileged users writing probe registers that can disturb hardware, direct VBUS toggles outside normal role policy, buffer parsing without explicit NUL termination after short copy windows, and debugfs file creation failures being intentionally nonfatal. Test signals include reading all regsets, endpoint directories appearing after gadget init, manual `mode` switches host/device, VBUS on/off writes, QMU GPD dumps while endpoints are enabled, and recursive cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_dr.c -->
# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_dr.c

## Purpose

`mtu3_dr.c` implements MTU3 dual-role switching. It changes port0 between host and device ownership, controls VBUS, handles extcon or USB role-switch requests, supports manual debugfs switching, and programs forced IDDIG mode.

## Important APIs, Types, and Functions

Key public functions are `ssusb_otg_switch_init()`, `ssusb_otg_switch_exit()`, `ssusb_mode_switch()`, `ssusb_set_vbus()`, and `ssusb_set_force_mode()`. Internal helpers include `ssusb_port0_switch()`, `switch_port_to_host()`, `switch_port_to_device()`, `ssusb_mode_sw_work()`, extcon notifier `ssusb_id_notifier()`, and role-switch callbacks `ssusb_role_sw_set()` and `ssusb_role_sw_get()`.

## Control Flow

Initialization creates a work item and selects manual debugfs, USB role switch, or extcon notifier mode. Role changes store `desired_role` and queue `ssusb_mode_sw_work()` on the freezable workqueue. The work function normalizes `USB_ROLE_NONE` to the default role, skips no-op transitions, runtime-resumes the device, then for host mode forces host, stops gadget, switches U2/U3 port0 to host, enables VBUS, and marks `is_host`. For device mode it forces device, disables VBUS, switches port0 to device, starts gadget, and marks non-host.

## State and Persistence Behavior

Role state lives in `otg_switch_mtk` and `ssusb_mtk`: desired/default role, whether role switch or manual DRD is used, whether U3 port0 supports DRD, VBUS regulator handle, and `ssusb->is_host`. Hardware state is held in IPPC U2/U3 port mode bits and force-IDDIG bits. No state persists across remove.

## Dependencies and Integration Points

The file depends on regulators, extcon, USB role-switch framework, system workqueues, runtime PM, debugfs helper hooks, and host/gadget core functions from `mtu3_dr.h`. It is used only in dual-role builds.

## Risks and Test Signals

Risks include role-switch races with suspend/remove, ignoring `ssusb_check_clocks()` return values in port switch helpers, VBUS regulator failures leaving partially switched roles, and policy differences between extcon and role-switch defaults. Test signals include extcon host cable insertion/removal, userspace role-switch writes, manual debugfs mode writes, VBUS regulator on/off behavior, U3 DRD and U2-only DRD variants, and remove canceling pending work before unregistering role switch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_dr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_dr.h -->
# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_dr.h

## Purpose

`mtu3_dr.h` declares the role-dependent host, gadget, and dual-role interfaces used by MTU3 platform code, with inline no-op fallbacks when a role is not compiled.

## Important APIs, Types, and Functions

Host-side declarations include `ssusb_host_init()`, `ssusb_host_exit()`, `ssusb_wakeup_of_property_parse()`, `ssusb_host_resume()`, `ssusb_host_suspend()`, and `ssusb_wakeup_set()`. Gadget-side declarations include `ssusb_gadget_init()`, `ssusb_gadget_exit()`, `ssusb_gadget_suspend()`, `ssusb_gadget_resume()`, and `ssusb_gadget_ip_sleep_check()`. Dual-role declarations include `ssusb_otg_switch_init()`, `ssusb_otg_switch_exit()`, `ssusb_mode_switch()`, `ssusb_set_vbus()`, and `ssusb_set_force_mode()`.

## Control Flow

The header has no runtime control flow. Its `IS_ENABLED()` blocks select real prototypes or no-op inline functions, allowing `mtu3_plat.c` to call role helpers without local conditional compilation for every call site.

## State and Persistence Behavior

No state is stored in this header. The fallback functions return success or safe defaults, such as `ssusb_gadget_ip_sleep_check()` returning true when gadget support is absent.

## Dependencies and Integration Points

It depends on `struct ssusb_mtk`, `struct otg_switch_mtk`, `enum mtu3_dr_force_mode`, `struct device_node`, and `pm_message_t` definitions available through `mtu3.h` users. It connects platform lifecycle code to role-specific implementation files.

## Risks and Test Signals

Risks include no-op stubs hiding missing role behavior in unexpected configurations and mismatched `IS_ENABLED()` conditions relative to the Makefile. Test signals include compiling host-only, gadget-only, and dual-role modes and verifying platform probe calls resolve to the intended real or stub functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_dr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_gadget.c -->
# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_gadget.c

## Purpose

`mtu3_gadget.c` implements the Linux USB gadget controller operations for non-EP0 endpoints and UDC registration behavior. It maps gadget requests to MTU3 QMU descriptors, manages endpoint enable/disable, halt/wedge, pullup, wakeup, driver bind/unbind, and gadget suspend/resume/disconnect callbacks.

## Important APIs, Types, and Functions

Core functions include `mtu3_req_complete()`, `nuke()`, `mtu3_ep_enable()`, `mtu3_ep_disable()`, `mtu3_gadget_queue()`, `mtu3_gadget_dequeue()`, `mtu3_gadget_ep_set_halt()`, `mtu3_gadget_pullup()`, `mtu3_gadget_start()`, `mtu3_gadget_stop()`, and `mtu3_gadget_setup()`. `mtu3_ep_ops` exposes endpoint operations, and `mtu3_gadget_ops` exposes UDC operations.

## Control Flow

UDC setup initializes endpoint objects and registers the gadget. When a function driver starts, the driver pointer is stored and peripheral-only mode starts hardware immediately. Endpoint enable validates descriptor number/direction, configures hardware FIFO/CSR, allocates a QMU ring, starts QMU, and marks the endpoint active. Queue maps the request for DMA, prepares the transfer, appends it to `req_list`, inserts a GPD, and resumes QMU. Completion unmaps non-EP0 requests and gives them back with the controller lock temporarily dropped. Stop and disconnect paths clear softconnect, nuke all endpoint queues, notify function drivers, and reset state.

## State and Persistence Behavior

State is in `struct mtu3`, `struct mtu3_ep`, and `struct mtu3_request`: endpoint descriptors, QMU rings, request lists, active endpoint count, softconnect, gadget driver pointer, speed, wake flags, and callback enablement. It is runtime-only and rebuilt after probe.

## Dependencies and Integration Points

The file depends on USB gadget core, QMU helper functions, endpoint hardware config from `mtu3_core.c`, tracepoints, runtime PM, and EP0 operations from `mtu3_gadget_ep0.c`. It is the bridge between composite/function drivers and MTU3 hardware queues.

## Risks and Test Signals

Risks include DMA mapping leaks on `mtu3_prepare_transfer()` failure, queueing while endpoints are disabled, request length limits differing for Gen2-compatible QMU, halting endpoints with active requests, and callbacks while holding or dropping `mtu->lock`. Test signals include gadget bind/unbind, endpoint enable for all transfer types and speeds, queue/dequeue/completion, halt and wedge semantics, pullup before and after `mtu3_start()`, remote wakeup at HS and SS, and disconnect while requests are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_gadget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_gadget_ep0.c -->
# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_gadget_ep0.c

## Purpose

`mtu3_gadget_ep0.c` implements control endpoint 0 handling for MTU3 gadget mode. It manages SETUP decoding, standard USB requests handled by the controller, forwarding class/vendor requests to the gadget driver, PIO FIFO transfers, delayed status, stalls, and EP0 interrupt state transitions.

## Important APIs, Types, and Functions

Key functions include `ep0_read_setup()`, `ep0_handle_setup()`, `handle_standard_request()`, `ep0_get_status()`, `ep0_handle_feature()`, `ep0_set_sel()`, `handle_test_mode()`, `ep0_rx_state()`, `ep0_tx_state()`, `ep0_stall_set()`, `ep0_queue()`, and public `mtu3_ep0_isr()`. `mtu3_ep0_ops` exposes the EP0-specific endpoint operations.

## Control Flow

The EP0 ISR reads EP interrupt status, clears W1C bits, handles SETUPEND and sent-stall cleanup, then dispatches by `mtu->ep0_state`. SETUP state reads exactly eight bytes, completes any leftover EP0 request, chooses TX or RX data stage based on direction, handles standard requests locally when required, or forwards to the gadget driver. TX state writes maxpacket-sized chunks to FIFO and transitions to TX_END when complete; RX state reads FIFO packets until short or full request completion. Delayed status is recorded until a later EP0 queue call triggers the status stage.

## State and Persistence Behavior

EP0 state is runtime-only: `ep0_state`, `address`, `may_wakeup`, U1/U2 flags, `delayed_status`, `test_mode`, `test_mode_nr`, and the reusable `ep0_req`/`setup_buf`. The device address and link-power bits are mirrored into hardware registers during standard request handling.

## Dependencies and Integration Points

The file depends on USB chapter 9 definitions, composite gadget setup callbacks, MTU3 MMIO registers, debug trace helpers, and request completion from `mtu3_gadget.c`. It is invoked from the core IRQ path under `mtu->lock`.

## Risks and Test Signals

Risks include malformed SETUP lengths, request queue busy behavior, pointer use for `setup_buf`, test mode entering hardware state that requires platform restart, function-suspend forwarding, and correct lock release around gadget driver setup callbacks. Test signals include enumeration through SET_ADDRESS and SET_CONFIGURATION, GET_STATUS for device and endpoints, SET/CLEAR_FEATURE for halt, remote wake, U1/U2, SET_SEL six-byte OUT stage, delayed status from composite drivers, EP0 stall clear on next setup, and USB2 electrical test modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_gadget_ep0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_host.c -->
# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_host.c

## Purpose

`mtu3_host.c` implements MTU3 host-mode glue. It powers and configures host ports, populates the xHCI child device, handles host suspend/resume port power, and configures SoC-specific wakeup-from-IP-sleep registers.

## Important APIs, Types, and Functions

Public functions are `ssusb_wakeup_of_property_parse()`, `ssusb_wakeup_set()`, `ssusb_host_resume()`, `ssusb_host_suspend()`, `ssusb_host_init()`, and `ssusb_host_exit()`. Internal helpers include `ssusb_wakeup_ip_sleep_set()`, `host_ports_num_get()`, `ssusb_host_enable()`, `ssusb_host_disable()`, `ssusb_host_setup()`, and `ssusb_host_cleanup()`. `enum ssusb_uwk_vers` maps several MediaTek wakeup register layouts.

## Control Flow

Host init reads xHCI port counts, powers on host IP, enables all non-disabled U2/U3 ports in host mode, forces host IDDIG, enables VBUS for DRD port0, then populates child platform devices from the device tree. Suspend powers down U3 and U2 ports and host IP; resume powers them back on, optionally skipping port0 when dual-role is currently device. Wakeup parsing reads `wakeup-source` and `mediatek,syscon-wakeup`, and wakeup enable writes version-specific regmap bits.

## State and Persistence Behavior

Host state lives in `ssusb_mtk`: port counts, disabled-port masks, `is_host`, wakeup enable flag, syscon regmap, wakeup register base/version, and VBUS regulator in the OTG switch. Hardware state is IPPC power/port bits and wakeup syscon bits. No software state persists after remove.

## Dependencies and Integration Points

The file depends on OF platform population, regmap/syscon, PHY/clock/power setup done by `mtu3_plat.c`, xHCI child binding, wake IRQ policy, and dual-role state. It is compiled for host-only and dual-role configurations.

## Risks and Test Signals

Risks include SoC wakeup version mismatches, disabled-port mask handling, failing to disable VBUS only when currently host, child xHCI population failures after host hardware is enabled, and suspend/resume interactions with dual-role port0 ownership. Test signals include host-only probe creating xHCI, multiple U2/U3 port capabilities, disabled port masks, wakeup-source syscon programming for each version, suspend/resume with and without port0 skipped, and remove depopulating xHCI before host cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_hw_regs.h -->
# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_hw_regs.h

## Purpose

`mtu3_hw_regs.h` defines MTU3 SSUSB device, endpoint, USB2, USB3, QMU, and IPPC register offsets and bit fields. It is the hardware contract used by the platform, core, gadget, EP0, host, dual-role, QMU, and debugfs code.

## Important APIs, Types, and Functions

The file provides base offsets such as `SSUSB_DEV_BASE`, `SSUSB_EPCTL_CSR_BASE`, `SSUSB_USB3_MAC_CSR_BASE`, `SSUSB_USB2_CSR_BASE`, and `SSUSB_SIFSLV_IPPC_BASE`; register offsets such as `U3D_EP0CSR`, `U3D_DEVICE_CONF`, `U3D_POWER_MANAGEMENT`, and `U3D_SSUSB_IP_PW_CTRL*`; and field macros for interrupts, endpoint CSR fields, QMU status, speed, link power, test modes, port power/mode, and clock/reset status.

## Control Flow

There is no executable control flow. Callers compose these macros with `mtu3_readl()`, `mtu3_writel()`, `mtu3_setbits()`, and `mtu3_clrbits()` to control hardware.

## State and Persistence Behavior

The header defines access constants only. State lives in hardware registers and driver structures. Some fields are write-one-to-clear, captured by masks such as `EP0_W1C_BITS`, `TX_W1C_BITS`, and `RX_W1C_BITS`.

## Dependencies and Integration Points

It depends on kernel bit macro definitions through users including common Linux headers. It is included by `mtu3.h`, making it transitively available to all MTU3 implementation files and debugfs regsets.

## Risks and Test Signals

Risks include incorrect bit definitions causing destructive MMIO writes, Gen2 versus original TX/RX max-packet field differences, W1C mask misuse, and port-mode bits being used inconsistently between host, gadget, and DRD paths. Test signals include register dump comparison with vendor documentation, endpoint CSR programming for IN/OUT endpoints, QMU interrupt enable/clear behavior, speed detection from `U3D_DEVICE_CONF`, and IP clock/reset polling against `U3D_SSUSB_IP_PW_STS*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_hw_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_plat.c -->
# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_plat.c

## Purpose

`mtu3_plat.c` is the MTU3 platform driver. It acquires device-tree resources, regulators, clocks, PHYs, MMIO, reset, wake IRQ, port masks, and role policy; initializes common resources; chooses host/gadget/dual-role startup; and implements system/runtime suspend and resume.

## Important APIs, Types, and Functions

Key functions include `ssusb_check_clocks()`, resource helpers `get_ssusb_rscs()`, `ssusb_rscs_init()`, `ssusb_rscs_exit()`, PHY helpers, `ssusb_ip_sw_reset()`, `ssusb_u3_drd_check()`, platform lifecycle `mtu3_probe()` and `mtu3_remove()`, and PM helpers `mtu3_suspend_common()`, `mtu3_resume_common()`, `mtu3_runtime_suspend()`, and `mtu3_runtime_resume()`.

## Control Flow

Probe allocates `ssusb_mtk`, sets a 32-bit DMA mask, reads regulators/clocks/PHYs/MMIO/IRQs/role properties, creates debugfs root, enables runtime PM, initializes common resources, registers wake IRQ, resets the controller, detects U3 DRD capability, applies compile-time role overrides, and starts peripheral, host, or both plus the OTG switch. On success it enables async suspend, autosuspends, then forbids runtime PM until later policy allows it. Remove resumes the device, tears down role-specific subsystems, releases common resources, removes debugfs, and disables PM.

## State and Persistence Behavior

Platform state is runtime `ssusb_mtk`: common resource handles, role mode, host flag, port masks, wakeup config, debugfs root, and child gadget/host state. Hardware power, clock, PHY, reset, wake, and port states are reprogrammed during probe and PM transitions. No state persists beyond driver lifetime.

## Dependencies and Integration Points

The file depends on platform devices, device tree properties, regulators `vusb33` and `vbus`, clock bulk APIs, PHY framework, reset control, runtime/system PM, wake IRQ helpers, host/gadget/DRD helpers from `mtu3_dr.h`, and debugfs helpers.

## Risks and Test Signals

Risks include error unwinding order, treating `vbus` as required for host-capable modes, runtime PM forbid semantics, wakeup sleep polling failures, role-specific suspend with connected gadget returning `-EBUSY`, and resource leaks after partial host/gadget initialization. Test signals include probe for peripheral/host/OTG device trees, missing optional clocks, multiple PHY init rollback, wake IRQ registration, reset failure paths, system suspend/resume in host and device roles, runtime suspend with wakeup disabled, and clean remove after successful OTG initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_plat.c -->
