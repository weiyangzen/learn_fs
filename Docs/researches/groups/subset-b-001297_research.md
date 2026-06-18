# Research Group subset-b-001297

This grouped report covers the assigned GPIB common support and adapter drivers under `sources/distributed-fs/ceph-client/drivers/gpib`. Each file section is source-path aligned for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/cec/cec_gpib.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/cec/cec_gpib.c

Purpose: implements the `cec_pci` GPIB board type for CEC PCI/PCMCIA boards. It is mostly a board-specific wrapper around the shared NEC7210 core, adding PCI discovery for vendor `0x12fc`, device `0x5cec`, subsystem `0x9050`, PLX9050 interrupt enablement, and resource ownership.

Important APIs and functions: `cec_pci_interface` registers `attach`, `detach`, read/write/command/control/address/poll/EOS/status callbacks with `gpib_register_driver`. `cec_interrupt()` serializes through `board->spinlock` and delegates to `nec7210_interrupt`. `cec_generic_attach()` allocates `struct cec_priv`, initializes `nec7210_priv`, and selects IO-port access via `nec7210_ioport_read_byte` and `nec7210_ioport_write_byte`. `cec_pci_attach()` finds the PCI device, enables it, requests BAR regions, stores PLX and NEC IO bases, requests the hardware IRQ and a pseudo IRQ, initializes the chip, then enables PLX local and PCI interrupts.

Control flow and state: online setup is `gpib_common` `IBONL` -> `cec_pci_attach()` -> NEC reset/clock/online -> PLX interrupt enable. Runtime I/O calls are thin pass-throughs to NEC7210 helpers using `board->private_data`. Detach frees pseudo IRQ, disables PLX interrupts, frees IRQ, resets the NEC7210, releases PCI regions, drops the PCI reference, and frees private memory.

Dependencies and integration: depends on `cec.h`, `gpibP.h`, `nec7210` helpers, Linux PCI/IRQ/IO-port APIs, and the common GPIB driver registry. `cec_pci_probe()` is intentionally a no-op because user-space configuration selects a board through the GPIB ioctl path.

Risks: several attach failure paths return before unwinding earlier allocations, such as after `pci_enable_device`, `pci_request_regions`, IRQ allocation, or pseudo IRQ allocation. A `gpib_register_driver` failure after successful `pci_register_driver` does not unregister the PCI driver. `line_status` and local parallel poll mode are unimplemented, reducing status fidelity and command acceptor checks.

Test signals: build with `CONFIG_GPIB_CEC`; verify module registration/unregistration; exercise `CFCBOARDTYPE=cec_pci`, `IBONL`, read/write/command paths, IRQ delivery, pseudo IRQ polling, and detach after partial attach failures. Hardware tests should confirm PLX interrupt masking, NEC7210 reset/clock programming, and selected PCI bus/slot/device-path filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/cec/cec_gpib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/common/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/common/Makefile

Purpose: declares the common GPIB kernel module build target. `obj-$(CONFIG_GPIB_COMMON) += gpib_common.o` makes the subsystem core conditional on `CONFIG_GPIB_COMMON`, and `gpib_common-objs := gpib_os.o iblib.o` links the OS/device-file layer with the exported bus operation library.

Important build APIs: the file uses standard kbuild composite object syntax. `gpib_os.o` contributes character-device registration, ioctl dispatch, board lifecycle, driver registration, PCI selection helpers, timers, event queues, and status queues. `iblib.o` contributes the reusable IEEE-488 operations used by the ioctl layer and hardware adapters.

Control flow and integration: all adapter Makefiles in sibling folders build separate board modules that call symbols exported by this common module. The common module must be available before board modules can resolve `gpib_register_driver`, `gpib_request_pseudo_irq`, `push_gpib_event`, and PCI helper exports.

State and persistence behavior: no runtime state is present in the Makefile itself. Its main effect is link composition: `gpib_os.c` and `iblib.c` share one module namespace, one `MODULE_ALIAS_CHARDEV_MAJOR(GPIB_CODE)`, and one exported symbol provider.

Dependencies: depends on Kconfig selecting `CONFIG_GPIB_COMMON` and on kbuild compiling both C files in the same directory with access to the GPIB include tree.

Risks: if new common source files are added but not included in `gpib_common-objs`, adapters may compile but fail to link or miss exported behavior. If `CONFIG_GPIB_COMMON` is disabled while board drivers are enabled, board modules will have unresolved common symbols unless Kconfig prevents that combination.

Test signals: run kernel build coverage with `CONFIG_GPIB_COMMON=m` and at least one adapter enabled; inspect `modinfo gpib_common`; verify `gpib_common.ko` contains both ioctl and library symbols via `nm`/`modpost`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/common/gpib_os.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/common/gpib_os.c

Purpose: provides the kernel-facing GPIB core: `/dev/gpib*` character-device operations, ioctl dispatch, board state initialization, provider registration, timers, pseudo IRQs, serial-poll queues, event queues, PCI selection helpers, and online/offline lifecycle.

Important APIs and functions: exported functions include `gpib_register_driver`, `gpib_unregister_driver`, `gpib_request_pseudo_irq`, `gpib_free_pseudo_irq`, `push_gpib_event`, `gpib_match_device_path`, `gpib_pci_get_device`, and `gpib_pci_get_subsys`. `ibopen`, `ibclose`, and `ibioctl` implement the file operations. Ioctl helpers cover board type selection, online/offline, read/write/command, open/close device handles, serial/parallel poll, wait, addresses, EOS, request service, mutex ownership, timeouts, board info, PCI/device-path selection, events, system control, and T1 delay.

Control flow: module init initializes `board_array`, registers major `GPIB_CODE`, creates a class, and creates `gpibN` devices. Opening a minor allocates `gpib_file_private`, creates descriptor 0 as the board descriptor, and tries to hold the selected provider module. `ibioctl` first handles board selection and online/offline, then validates provider/online state, enforces the user mutex for most bus-mutating operations, unlocks the big mutex around long I/O, and dispatches to `iblib.c` operations or adapter callbacks.

State and persistence: global state is in `board_array` and `registered_drivers`. Per-board state includes provider module, config, online flag, status bits, waitqueue, spinlocks, user and big GPIB mutexes, timeout timer, pseudo IRQ timer, event queue, open device list, autospoll count/thread, address, timeout, parallel-poll config, master flag, and private adapter data. Per-file state tracks descriptors, module ownership, and whether the file holds the user mutex. State is in-memory only and reset at module unload.

Dependencies and integration: depends on `ibsys.h`, `gpibP.h`, Linux fs/device/timer/list/pci/uaccess/kthread APIs, and adapter-supplied `struct gpib_interface`. Adapter drivers register interfaces by name; user space selects them with `CFCBOARDTYPE` and configures resources through ioctls.

Risks: locking is complex and depends on `big_gpib_mutex` before `user_mutex` except `IBMUTEX`, which deliberately drops the big mutex. Several ioctl paths update descriptors or device open counts with partial rollback risk. Queue overflow uses dropped markers and returns `-EPIPE` on next pop. Online init-data allocation is freed after attach but failure paths require care. Autospoll can mark `stuck_srq` if polling finds no requester. Module use counts and board `use_count` must remain balanced during board type changes and close.

Test signals: exercise open/close, board type changes, online/offline with failing adapters, long read/write interruption, `IBWAIT` with timeout and status masks, descriptor close while I/O is busy, autospoll on SRQ, status/event queue overflow, PCI bus/slot/device-path selection, and module unload while providers are registered or in use. Lockdep and fault-injection around `copy_from_user`, `vmalloc`, IRQ/timer teardown, and adapter attach failures are high value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/common/gpib_os.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/common/iblib.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/common/iblib.c

Purpose: implements the reusable IEEE-488/GPIB operation layer used by the ioctl core. It translates high-level operations such as command, read, write, wait, serial poll, interface clear, remote enable, address changes, EOS, and status queries into adapter `gpib_interface` callbacks.

Important APIs and functions: `ibcac`, `ibcmd`, `ibgts`, `ibonline`, `iboffline`, `iblines`, `ibrd`, `ibrpp`, `ibppc`, `ibrsv2`, `ibsic`, `ibrsc`, `ibsre`, `ibpad`, `ibsad`, `ibeos`, `ibstatus`, `general_ibstatus`, `ibwait`, and `ibwrt`. Internal helpers include `check_for_command_acceptors`, the autospoll kthread, wait timer helpers, and status wait predicates.

Control flow: command operations require controller-in-charge, start the board timeout, take control, optionally check for NRFD/NDAC command acceptors via `line_status`, then call the adapter command callback. Reads and writes place the controller in standby when master, start timeouts, and loop through adapter read/write callbacks until length, END, or error. Online allocates the board buffer, calls adapter attach, starts autospoll, and marks the board online; offline stops autospoll, detaches, and deallocates buffers/events.

State and persistence: updates `board->status`, `board->master`, `board->pad`, `board->sad`, `board->parallel_poll_configuration`, `board->t1_nano_sec`, descriptor `io_in_progress`, and autospoll fields. Timers drive `TIMO`; events and status queues are maintained in `gpib_os.c`. No state persists after module unload.

Dependencies and integration: tightly coupled to `struct gpib_interface` callbacks, `gpib_board` fields from `gpib_types.h`, GPIB command constants, `gpib_os.c` timers/status queues, and adapter status-line implementations. It is linked into `gpib_common.o`.

Risks: `ibrpp()` returns early on `ibcac()` failure without removing the timeout timer. Read/write timeout semantics can be extended by repeated chunking in ioctl loops, as noted by an in-code comment. `serial_poll_single()` returns the original retval when cleanup fails, losing cleanup errors if the poll itself succeeded. Autospoll treats nonpositive poll results as stuck SRQ. `check_for_command_acceptors` depends on accurate line-status support and may be skipped by adapters.

Test signals: validate controller state transitions, sync/async take-control fallback, no-listener command detection, read/write timeout and END/EOS behavior, `IBWAIT` clear/set masks, autospoll thread behavior on SRQ and stuck SRQ, online/offline attach failure unwinding, address limits, T1 delay propagation, and unsupported adapter callbacks returning expected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/common/iblib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/common/ibsys.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/common/ibsys.h

Purpose: private common header for the GPIB core implementation. It pulls in subsystem, kernel, I/O, IRQ, DMA, and uaccess dependencies needed by `gpib_os.c` and `iblib.c`, and declares shared helper functions for board allocation and serial-poll/status-queue management.

Important APIs and types: declares `gpib_allocate_board`, `gpib_deallocate_board`, `num_status_bytes`, `push_status_byte`, `pop_status_byte`, `get_gpib_status_queue`, `get_serial_poll_byte`, and `autopoll_all_devices`. It also defines the common address bounds `MAX_GPIB_PRIMARY_ADDRESS` and `MAX_GPIB_SECONDARY_ADDRESS`.

Control flow and integration: `gpib_os.c` provides allocation, status-queue, and autospoll implementations; `iblib.c` calls them while performing online/offline, serial poll, and high-level bus operations. Including `gpibP.h` makes the common implementation see GPIB core structures, ioctl definitions, command constants, and provider registration prototypes.

State and persistence: the header itself has no state. Its declarations expose operations that mutate `gpib_board` buffers, event queues, device status queues, and autospoll behavior.

Dependencies: Linux kernel headers for scheduling, errno, major numbers, modules, memory allocation, timers, I/O, uaccess, IRQ, and DMA. It is intentionally not a public user-space ABI header; user ABI lives under Linux GPIB headers.

Risks: broad includes can mask missing direct includes in source files and increase rebuild scope. The address-limit macros are private constants; mismatches with public ioctl validation or adapter assumptions would create inconsistent behavior. Because this header declares non-exported helpers shared only inside `gpib_common.o`, moving files between modules would require export changes.

Test signals: compile `gpib_common.o` with sparse/modpost; ensure prototypes match definitions; exercise address-bound validation through `IBPAD`, `IBSAD`, and serial-poll ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/common/ibsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/eastwood/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/eastwood/Makefile

Purpose: builds the Fluke/Eastwood GPIB adapter module when `CONFIG_GPIB_FLUKE` is enabled. The single kbuild line maps the configuration symbol to `fluke_gpib.o`.

Important build API: uses standard `obj-$(CONFIG_GPIB_FLUKE) += fluke_gpib.o` syntax. The resulting module contains the platform driver for compatible `flk,fgpib-4.0` devices and the three registered GPIB board interfaces (`fluke_unaccel`, `fluke_hybrid`, and `fluke`).

Control flow and integration: this module depends on `gpib_common` exports and NEC7210 helper symbols. It must be selected only in configurations that provide platform-device and DMAengine support needed by `fluke_gpib.c`.

State and persistence: no runtime state is encoded in the Makefile. The build choice determines whether user space can select Fluke board types through `CFCBOARDTYPE`.

Dependencies: Kconfig should enforce dependencies on the GPIB common core, NEC7210 support, platform bus, MMIO, and DMAengine facilities.

Risks: if `CONFIG_GPIB_FLUKE` can be enabled without the common GPIB module or DMAengine symbols, link or load failures will occur. Since all three Fluke board interfaces live in the same object, there is no build-time way to include only unaccelerated support.

Test signals: build with `CONFIG_GPIB_FLUKE=m`, verify `modpost` dependencies, load the module on a kernel with and without matching platform devices, and confirm `gpib_register_driver` exposes all three interface names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/eastwood/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/eastwood/fluke_gpib.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/eastwood/fluke_gpib.c

Purpose: implements Fluke CDA/Eastwood GPIB board support for a custom CB7210/NEC7210-compatible core connected to a PL330 DMA channel. It provides unaccelerated, hybrid, and fully accelerated GPIB interfaces.

Important APIs and functions: `fluke_unaccel_interface` uses NEC7210 PIO read/write; `fluke_hybrid_interface` accelerates writes only; `fluke_interface` accelerates both reads and writes. Wrappers delegate standard GPIB operations to NEC7210 helpers. DMA paths include `fluke_config_dma`, `fluke_dma_write`, `fluke_accel_write`, `fluke_dma_read`, and `fluke_accel_read`. Interrupt flow is `fluke_gpib_interrupt` -> `fluke_gpib_internal_interrupt`, which reads CB7210/NEC7210 status, handles IFC events, delegates NEC7210 interrupt handling, updates read-ready state, and wakes waiters.

Control flow: attach requires a probed platform device, allocates private state and a DMA buffer, maps three MMIO resources, requests IRQ, optionally acquires DMA channel 0, resets and configures the CB7210 clock/handshake mode, requests a pseudo IRQ, and enables IFC interrupts. Accelerated writes DMA all but a final EOI byte when needed, waits for source handshake readiness before `AUX_SEOI`, and records transferred bytes from a hardware counter. Accelerated reads release RFD holdoff, start DMA, handle END races, terminate/pause DMA, copy from the bounce buffer, and set `end`.

State and persistence: private state tracks NEC7210 state, MMIO resources, IRQ, DMA channel, DMA bounce buffer, and write-transfer counter mapping. NEC7210 state bits coordinate DMA in progress, read/write readiness, bus errors, END, and device clear. State is only live while the board is online.

Dependencies and integration: depends on `fluke_gpib.h`, `gpibP.h`, NEC7210 helpers, Linux platform bus, OF match `flk,fgpib-4.0`, DMAengine, MMIO, IRQ, waitqueues, and pseudo IRQ support from `gpib_common`.

Risks: many attach failure exits do not unwind already requested regions, mappings, IRQs, or private allocations. `fluke_dma_write()` unmaps `address` even if mapping setup was not valid after an earlier failure, and DMA mapping errors are not checked. The code documents possible DMA-read corruption and offers the hybrid interface as mitigation. Wait logic relies on precise hardware state bits and may return partial transfers after timeout, device clear, or bus error.

Test signals: build/load with matching OF device; test all three interface names; inject missing resources, IRQ failure, and DMA unavailable; run read/write with and without EOI, timeout, IFC/device clear, and bus error; verify pseudo IRQ polling, IFC event delivery, DMA residue/counter correctness, and detach resource release under repeated online/offline cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/eastwood/fluke_gpib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/eastwood/fluke_gpib.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/eastwood/fluke_gpib.h

Purpose: defines Fluke CB7210 board-private state, register layout, bit fields, and inline MMIO helpers used by `fluke_gpib.c`.

Important types and APIs: `struct fluke_priv` embeds `struct nec7210_priv` and stores MMIO resources for GPIB registers, DMA port, write-transfer counter, IRQ, DMA channel, bounce buffer, buffer size, and transfer-counter mapping. Inline helpers include `cb7210_page_in_bits`, `fluke_read_byte_nolock`, `fluke_write_byte_nolock`, `fluke_paged_read_byte`, and `fluke_paged_write_byte`. Enums define CB7210 paged registers, ISR/IMR bits, source-handshake states, bus-status bits, and Fluke auxiliary commands.

Control flow and state: paged register access writes a page-select auxiliary command, delays, then reads or writes the selected register while holding `nec_priv->register_page_lock`. Bus status bits are active-low and translated by the C file into `BUS_*` line-status flags. `write_transfer_counter_mask` limits accelerated write chunks to 0x7ff bytes.

Dependencies and integration: includes `nec7210.h`, DMAengine, I/O, delay, and interrupt headers. The C file installs these helpers as NEC7210 `read_byte`/`write_byte` callbacks and uses the register constants in interrupt, DMA, line-status, and T1-delay paths.

Risks: the nolock helpers require callers to hold the page lock; misuse can corrupt paged register selection. `readl`/`writel` are used for byte-wide values, which assumes the hardware tolerates 32-bit accesses. The custom `DATA_IN_STATUS` bit and undocumented `AUX_RTL2` behavior are hardware-specific and need matching HDL/firmware.

Test signals: static build coverage, lockdep review around paged access, hardware tests for paged ISR/BUS_STATUS/STATE1 reads, line-status polarity, high-speed/low-speed AUX commands, transfer-counter masking, and RTL behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/eastwood/fluke_gpib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/fmh_gpib/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/fmh_gpib/Makefile

Purpose: builds the `fmh_gpib.o` module when `CONFIG_GPIB_FMH` is enabled. This module supports Frank Mori Hess's `fmh_gpib_core` platform device and a prototype PCI variant.

Important build API: `obj-$(CONFIG_GPIB_FMH) += fmh_gpib.o` maps the Kconfig symbol to the single adapter implementation. That object registers multiple board interface names: unaccelerated and accelerated platform variants, plus unaccelerated and FIFO-accelerated PCI variants.

Control flow and integration: the module links against common GPIB and NEC7210 helper symbols. Runtime availability is controlled by platform OF match `fmhess,fmh_gpib_core` or prototype PCI IDs in the C file, not by separate build outputs.

State and persistence: no runtime state in the Makefile. It controls whether the board types are available to `CFCBOARDTYPE`.

Dependencies: Kconfig should require GPIB common support, NEC7210 support, platform/OF support, PCI support if the PCI path is built unconditionally, MMIO, IRQ, and DMAengine APIs.

Risks: the C file contains both platform and PCI paths, so missing dependencies can surface as compile/link issues if Kconfig is incomplete. Prototype PCI IDs are bogus constants by design, so successful build does not imply discoverable PCI hardware.

Test signals: build as module and built-in, inspect modpost for GPIB/DMA/PCI dependencies, load/unload, and confirm all interface registrations occur or unwind on simulated registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/fmh_gpib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/fmh_gpib/fmh_gpib.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/fmh_gpib/fmh_gpib.c

Purpose: implements the adapter driver for `fmh_gpib_core`, a custom CB7210/NEC7210-compatible GPIB core with platform MMIO/DMA support and a prototype PCI FIFO variant.

Important APIs and functions: registers `fmh_gpib_unaccel`, `fmh_gpib`, `fmh_gpib_pci_unaccel`, and `fmh_gpib_pci`. Standard GPIB callbacks wrap NEC7210 operations. FMH-specific callbacks implement local parallel-poll mode, serial-poll response mode 2 (`fmh_gpib_serial_poll_response2`), line status, T1 delay, and return-to-local. Accelerated paths include DMA write/read for platform devices and FIFO write/read for PCI devices. `fmh_gpib_internal_interrupt` handles IFC/ATN-related status, delegates NEC7210 interrupts, mirrors extended status into NEC7210 state bits, handles FIFO half-full/half-empty interrupts, and wakes waiters.

Control flow: platform attach finds an unattached matching device by OF path, marks it with `dev_set_drvdata`, allocates private data, maps named resources `gpib_control_status` and `dma_fifos`, requests shared IRQ, optionally acquires DMA channel `"rxtx"`, reads FIFO burst length, initializes hardware, and sets RFD holdoff. PCI attach finds prototype vendor/device IDs, enables PCI, maps BAR resources, requests IRQ, reads FIFO capability, and initializes. Accelerated reads release holdoff, run DMA/FIFO transfers, drain residual FIFO bytes, set END from status/EOI flags, then reassert holdoff when appropriate.

State and persistence: `struct fmh_priv` tracks NEC7210 state, resources, IRQ, DMA channel, DMA buffer, FIFO base, burst length, and FIFO interrupt support. `board->dev` is used to prevent duplicate platform attachment. NEC7210 state bits track data readiness, command readiness, END, bus error, device clear, DMA progress, and RFD holdoff.

Dependencies and integration: depends on `fmh_gpib.h`, `gpibP.h`, NEC7210 helpers, platform/OF APIs, PCI APIs, DMAengine, MMIO, IRQ, waitqueues, and common GPIB registration. User space selects the specific accelerated/unaccelerated board type by name.

Risks: numerous attach failure paths leak prior private allocations, device references, regions, mappings, IRQs, or DMA channels. `fmh_gpib_pci_attach_holdoff_end()` returns `-EIO` after successful attach if FIFO interrupts are unsupported without detaching. DMA mapping errors are logged but not made fatal. FIFO interrupt clearing writes zero to the full control/status register, intentionally disabling other FIFO modes and relying on no concurrent FIFO mode use. Prototype PCI IDs must be patched for real hardware.

Test signals: build/load with platform and PCI configs; run repeated online/offline; fault-inject resource, IRQ, DMA, and registration failures; test PIO, DMA, and FIFO paths; verify RFD holdoff around END bytes, serial-poll request-service transitions, local parallel-poll mode, IFC event delivery, FIFO half interrupt behavior, and fallback to unaccelerated board types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/fmh_gpib/fmh_gpib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/fmh_gpib/fmh_gpib.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/fmh_gpib/fmh_gpib.h

Purpose: defines private state, register offsets, FIFO layout, bit masks, and MMIO helpers for the `fmh_gpib_core` adapter.

Important types and APIs: `struct fmh_priv` embeds `nec7210_priv`, records MMIO resources, IRQ, DMA channel, DMA buffer, burst length, FIFO base, and FIFO interrupt capability. Helpers `fmh_gpib_half_fifo_size`, `gpib_cs_read_byte`, `gpib_cs_write_byte`, `fifos_read`, and `fifos_write` abstract control/status and FIFO register access. Constants define platform and prototype PCI resource indexes, placeholder PCI IDs, extended status registers, ISR/IMR bits, FIFO registers, FIFO control/status flags, data masks, counter masks, and auxiliary commands.

Control flow and state: C code uses `gpib_cs_*` as NEC7210 byte callbacks and `fifos_*` for accelerated PCI/platform FIFO movement. Extended status bits drive `READ_READY_BN`, `WRITE_READY_BN`, `COMMAND_READY_BN`, `RFD_HOLDOFF_BN`, and `RECEIVED_END_BN`. FIFO transfer counters bound chunks to 0x0fff bytes and encode EOI in bit 8 of FIFO data.

Dependencies and integration: includes DMAengine, IO resource, PCI, MMIO, and `nec7210.h`. It is private to `fmh_gpib.c` and assumes hardware register spacing of one byte for control/status and two bytes for FIFO registers, except prototype PCI control/status offset is adjusted in the C file.

Risks: `fmh_gpib_half_fifo_size()` returns the hardware burst length directly; zero would break loops that divide or iterate by half FIFO size if accelerated FIFO paths are used. `fifos_read` returns zero when `fifo_base` is absent, so unsupported FIFO hardware can look like empty/unsupported status unless callers check capabilities. Placeholder PCI IDs must not ship as real IDs.

Test signals: compile-time coverage; unit-style review of bit masks against HDL; hardware tests for FIFO data EOI bit, transfer counter limits, burst length, extended status transitions, RFD holdoff commands, and MMIO spacing on platform versus PCI variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/fmh_gpib/fmh_gpib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/gpio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/gpio/Makefile

Purpose: builds the GPIO bit-banged GPIB adapter when `CONFIG_GPIB_GPIO` is enabled. The single target is `gpib_bitbang.o`.

Important build API: `obj-$(CONFIG_GPIB_GPIO) += gpib_bitbang.o` compiles the Raspberry-Pi-oriented software handshake driver and registers one board interface using `KBUILD_MODNAME` as its name.

Control flow and integration: this module depends on `gpib_common` exports, GPIO descriptor/lookup APIs, IRQ APIs, and GPIB state machine definitions. It has no hardware helper core such as NEC7210; the C file directly implements bus handshakes.

State and persistence: no runtime state in the Makefile. Enabling the config makes the bit-banged board type available to user space.

Dependencies: Kconfig should require GPIB common support, gpiolib, IRQ support for GPIO lines, and the target platform GPIO labels used by the lookup tables.

Risks: building the module is not enough for portability; the C file documents Raspberry Pi limitations and hard-coded pin maps. Missing Kconfig dependencies would produce compile or load-time failures.

Test signals: build with `CONFIG_GPIB_GPIO=m`, load on Raspberry Pi GPIO-capable kernels, validate module parameters `pin_map`, `sn7516x_used`, and `debug`, and verify registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/gpio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/gpio/gpib_bitbang.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/gpio/gpib_bitbang.c

Purpose: implements a GPIO-driven GPIB controller, mainly for Raspberry Pi hardware with optional SN75160/SN75161 transceivers. It bit-bangs IEEE-488 handshakes using GPIO lines and IRQs rather than a GPIB controller ASIC.

Important APIs and functions: `bb_interface` registers read, write, command, controller, address, EOS, status, line-status, and lifecycle callbacks. `bb_read` arms DAV interrupts and accepts bytes by toggling NRFD/NDAC. `bb_write` arms NRFD/NDAC interrupts and sends data by toggling DAV/EOI. Interrupt handlers `bb_DAV_interrupt`, `bb_NRFD_interrupt`, `bb_NDAC_interrupt`, and `bb_SRQ_interrupt` implement the handshake. `bb_command` updates software talker/listener state from command bytes. Attach/detach paths allocate private state, map pin profiles, acquire GPIO descriptors, request IRQs, and release resources.

Control flow: attach selects `elektronomikon`, `gpib4pi-1.1`, or `yoga` pin maps, configures optional transceiver control pins, sets idle line levels, and requests disabled IRQs. Reads switch data lines to input, assert NRFD readiness, and wait for the DAV ISR to collect bytes until length, EOI/EOS, timeout, or signal. Writes switch to output, reject no-listener conditions when NRFD/NDAC are both high, and wait for NRFD/NDAC ISR progression. Controller operations manipulate active-low ATN/IFC/REN and software state.

State and persistence: `struct bb_priv` tracks IRQs, interrupt modes, active transfer buffers/counters, EOS settings, direction, busy flags, debug counters, software talker/listener states, and handshake phase. Global GPIO descriptor arrays and mutable `gpios_vector` represent pin mappings. State is in-memory and reset on detach/module unload.

Dependencies and integration: depends on `gpibP.h`, `gpib_state_machines.h`, Linux GPIO descriptor and machine lookup APIs, IRQ type control, waitqueues, spinlocks, and common GPIB registration. It implements line status directly from active-low GPIO values.

Risks: file comments list major limitations: Raspberry Pi focus, no non-master device mode with SN7516x, no parallel poll, no return-to-local, and no device support. `check_for_eos` appears inverted relative to `REOS` naming: `bb_read` sets `eos_check = (eos_flags & REOS) == 0`, while `check_for_eos` returns early when `eos_check` is true. Global `gpios_vector` is mutated by attach and may not reset cleanly across pin-map changes. `sprintf` into a fixed buffer is safe for current names but unnecessary. IRQ sequencing relies on edge/level reconfiguration and may be fragile under missed GPIO interrupts.

Test signals: hardware tests with each pin map, with and without SN7516x, read/write/command transfers under timeout and signal interruption, EOI/EOS detection, SRQ wait behavior, no-listener detection, repeated attach/detach, line-status polarity, and debug counters for idle/out-of-order interrupts. Static tests should review GPIO descriptor cleanup on partial attach failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/gpio/gpib_bitbang.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/hp_82335/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/hp_82335/Makefile

Purpose: builds the HP 82335 GPIB adapter module when `CONFIG_GPIB_HP82335` is enabled. The module target is `hp82335.o`.

Important build API: `obj-$(CONFIG_GPIB_HP82335) += hp82335.o` is the kbuild binding. The resulting adapter registers the `hp82335` GPIB board interface.

Control flow and integration: `hp82335.o` depends on common GPIB exports and TMS9914 helper symbols. It is a legacy memory-mapped ISA-style adapter driver, so runtime configuration comes from user ioctls for base address and IRQ rather than PCI/platform discovery.

State and persistence: no runtime state in the Makefile. Its effect is build availability of the HP82335 board type.

Dependencies: Kconfig should require GPIB common, TMS9914 support, MMIO/legacy resource APIs, and IRQ support.

Risks: if TMS9914 helper code is not selected, module linking will fail. Build coverage alone does not validate required legacy base-address/IRQ configuration.

Test signals: build with `CONFIG_GPIB_HP82335=m`, inspect dependencies, load/unload, and select `hp82335` through the common board-type ioctl with configured base/IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/hp_82335/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/hp_82335/hp82335.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/hp_82335/hp82335.c

Purpose: implements the `hp82335` GPIB board interface for HP 82335 cards. It wraps the shared TMS9914 core with HP-specific memory mapping, register offsets, interrupt clearing, and legacy base-address validation.

Important APIs and functions: `hp82335_interface` registers standard GPIB callbacks that delegate to TMS9914 helpers. `hp82335_attach` validates configured base memory, requests/maps the upper 0x2000 region, requests the configured IRQ, resets the TMS9914, clears pending HP interrupts, enables HP interrupts through `HPREG_CCR`, and calls `tms9914_online`. `hp82335_detach` disables interrupts, resets the chip, unmaps memory, releases the region, frees IRQ, and frees private state. `hp82335_interrupt` reads TMS9914 ISR registers, clears the HP interrupt latch, and delegates to `tms9914_interrupt_have_status`.

Control flow and state: user space configures `ibbase` and `ibirq`, then `IBONL` calls attach. TMS9914 register access is translated by `tms9914_to_hp82335_offset`, placing the eight TMS9914 registers at `0x1ff8 + register`. Private state holds `tms9914_priv`, IRQ, and raw mapped base.

Dependencies and integration: depends on `hp82335.h`, `tms9914.h`, `gpibP.h`, Linux memory-region, MMIO, IRQ, and module APIs. It integrates with `gpib_common` as a named provider and with the TMS9914 controller implementation for actual bus protocol behavior.

Risks: attach failure paths after private allocation, memory-region request, ioremap, or IRQ request do not consistently unwind previous resources. `ioremap` result is not checked before `request_irq` and register access. The valid base list is fixed to legacy ROM windows from `0xc4000` to `0xfc000`; invalid or conflicting platform mappings fail. The file comment notes missing ATN interrupt/status update and possible bus-error recovery work.

Test signals: build/load; configure every valid base boundary and invalid bases; fault-inject region, map, and IRQ failures; verify interrupt clear/control register behavior, TMS9914 reset/online, read/write/command delegation, line status, T1 delay, and repeated online/offline cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/hp_82335/hp82335.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/hp_82335/hp82335.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/hp_82335/hp82335.h

Purpose: private header for the HP82335 adapter, defining board-private state, HP memory-window sizes, HP-specific register offsets, and control/status bits.

Important types and constants: `struct hp82335_priv` embeds `struct tms9914_priv` and tracks IRQ and raw mapped base. `hp82335_rom_size` is 0x2000 and `hp82335_upper_iomem_size` is 0x2000, matching the attach calculation that maps `ibbase + hp82335_rom_size`. Register enums define `HPREG_CSR`, `HPREG_STATUS`, `HPREG_INTR_CLEAR`, and `HPREG_CCR`. Bit enums define DMA enable/channel select, interrupt enable, system-controller disable, switch bits, system-controller status, DMA status, interrupt enable status, and interrupt pending.

Control flow and state: `hp82335.c` uses `HPREG_CCR` to enable/disable interrupts, `HPREG_INTR_CLEAR` to acknowledge interrupts, and the size constants for resource request/unmap. TMS9914 state remains in the embedded `tms9914_priv`.

Dependencies and integration: includes `tms9914.h` and `gpibP.h`, making it private to kernel adapter code and not part of the user ABI.

Risks: constants assume HP82335 memory layout and may not cover clones or alternate switch configurations. `DMA_ENABLE` and DMA channel bits are defined but unused by the current C file, so DMA support is not implemented despite hardware bit definitions. Header-level `static const int` values are fine for this single C user but would duplicate storage if widely included.

Test signals: compile checks, validation against hardware documentation, interrupt enable/pending bit tests, and confirmation that `ibbase + 0x2000` maps the TMS9914 register window on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/hp_82335/hp82335.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/hp_82341/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/hp_82341/Makefile

Purpose: builds the HP 82341 adapter module when `CONFIG_GPIB_HP82341` is enabled. The declared object is `hp_82341.o`.

Important build API: `obj-$(CONFIG_GPIB_HP82341) += hp_82341.o` maps the Kconfig option to its adapter object. This file only covers build inclusion; the implementation is outside this work item.

Control flow and integration: the module is expected to integrate with the common GPIB registration layer like the other board drivers and likely depends on shared controller helpers, but this Makefile does not expose which callbacks or hardware core are used.

State and persistence: no runtime state. Its only effect is whether the HP82341 board driver is compiled.

Dependencies: Kconfig should ensure common GPIB support and any HP82341-specific bus/helper dependencies are selected.

Risks: the object name uses an underscore (`hp_82341.o`) while the directory name is `hp_82341`; any source rename mismatch would break the build. Since no composite object list is present, all implementation must be in a single matching C file.

Test signals: build with `CONFIG_GPIB_HP82341=m`; verify `hp_82341.o` exists, module links against required common symbols, and load/unload registration succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/hp_82341/Makefile -->
