# Research: subset-b-004996

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/wax.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/wax.c

## Purpose
`wax.c` is the PA-RISC WAX bus-adapter driver. It discovers the WAX GSC ASIC, disables and initializes its interrupt block, claims the fixed GSC interrupt line, registers common GSC resources, and assigns child-device interrupt lines for WAX-attached i8042, serial, and EISA functions.

## Important APIs, Types, and Functions
The file is built around the PA-RISC driver model: `struct parisc_driver wax_driver`, `struct parisc_device_id wax_tbl`, and `arch_initcall(wax_init)`. `wax_init_chip()` allocates and fills `struct gsc_asic`, claims IRQ routing with `gsc_claim_irq()`, installs `gsc_asic_intr` with `request_irq()`, calls `gsc_common_setup()`, and finally performs interrupt fixups. `wax_choose_irq()` maps known `dev->id.sversion` values to primary and optional auxiliary ASIC IRQ inputs through `gsc_asic_assign_irq()`. `wax_init_irq()` masks the ASIC, clears pending interrupt state, and leaves firmware-managed resets commented out.

## Control Flow
At architecture init, `register_parisc_driver()` binds WAX devices matching HPHW_BA sversion `0x0008e`. Probe allocates a zeroed ASIC structure, records `dev->hpa.start`, masks/clears interrupts, claims hardcoded `WAX_GSC_IRQ` 7, derives the EIM value from the claimed transaction address/data, requests the actual CPU IRQ, writes the EIM to the WAX IAR, and enters common GSC setup. IRQ fixup runs over WAX children and, on 715-class layouts where WAX EISA is a sibling rather than child, over the parent as well.

## State and Persistence
Runtime state is in the allocated `struct gsc_asic`: name, HPA, version, GSC IRQ metadata, and EIM. Hardware state is the interrupt mask/request/address registers under the WAX HPA. There is no persistent storage and no module exit path because this is early platform init.

## Dependencies and Integration Points
The driver depends on PA-RISC platform headers, `gsc.h`, the PARISC bus, and GSC interrupt helpers. It integrates with child drivers by filling `dev->irq` and `dev->aux_irq`, not by directly driving child hardware.

## Risks
The fixed IRQ mapping is sversion-specific; unknown devices silently keep existing IRQ state. Failure after `request_irq()` but before or inside `gsc_common_setup()` frees the ASIC object but does not explicitly free the requested IRQ in the error branch, so cleanup correctness depends on setup failure expectations. The parent dereference assumes `parisc_parent(dev)` is non-null.

## Test Signals
Boot on WAX-equipped PA-RISC hardware should log `wax at 0x... found`, successfully route interrupts for i8042/serial/EISA, and avoid spurious WAX interrupts after masking and IRR clearing. Regression signals are missing keyboard/serial/EISA IRQs or `cannot get GSC irq`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/wax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/parport/Kconfig

## Purpose
This Kconfig file defines the Linux parallel-port feature hierarchy. It exposes core parport support, PC-style and platform-specific low-level drivers, optional PCMCIA and serial-card integration, and optional IEEE 1284 advanced transfer support.

## Important APIs, Types, and Functions
The central symbol is `PARPORT`, a tristate gated by `HAS_IOMEM`. Driver symbols include `PARPORT_PC`, `PARPORT_SERIAL`, `PARPORT_PC_FIFO`, `PARPORT_PC_SUPERIO`, `PARPORT_PC_PCMCIA`, `PARPORT_IP32`, `PARPORT_AMIGA`, `PARPORT_MFC3`, `PARPORT_ATARI`, `PARPORT_GSC`, and `PARPORT_SUNBPP`. `PARPORT_1284` controls advanced IEEE 1284 negotiation, daisy-chain discovery, probing, and enhanced transfer modes. `PARPORT_NOT_PC` is a helper selected by non-PC implementations.

## Control Flow
Configuration starts with an architecture opt-in helper `ARCH_MIGHT_HAVE_PC_PARPORT`, then presents `menuconfig PARPORT`. All subordinate symbols live inside `if PARPORT`, so no low-level driver builds without the core. Dependencies narrow each driver to relevant buses or architectures: for example `PARPORT_IP32` depends on `SGI_IP32`, Amiga drivers depend on `AMIGA` or `ZORRO`, and `PARPORT_GSC` defaults to `GSC`.

## State and Persistence
The file contributes build-time state only. Selected symbols determine which objects compile and which runtime features are available. No runtime persistence exists here.

## Dependencies and Integration Points
It integrates with kbuild through the symbols consumed by `drivers/parport/Makefile`. It also connects to architecture Kconfig through `ARCH_MIGHT_HAVE_PC_PARPORT` and to subsystem configs such as `PCI`, `PCMCIA`, `SERIAL_8250_PCI`, `HAS_IOPORT`, `SBUS`, and platform architecture symbols.

## Risks
Feature availability depends on accurate architecture selection. Enabling generic PC-style support on platforms with incompatible I/O mappings can produce unusable drivers, while disabling `PARPORT_1284` removes daisy-chain probing and advanced readback behavior. `PARPORT_GSC` has no prompt and follows `GSC`, so PA-RISC coverage depends on that platform symbol.

## Test Signals
Useful checks are generated `.config` combinations and object inclusion: `CONFIG_PARPORT=m/y` should build core `parport`, non-PC drivers should select `PARPORT_NOT_PC`, and `CONFIG_PARPORT_1284=y` should cause daisy/probe support to be compiled into the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/Makefile -->
# sources/distributed-fs/ceph-client/drivers/parport/Makefile

## Purpose
The Makefile maps parport Kconfig symbols to kernel objects and defines which compilation units form the core `parport` module.

## Important APIs, Types, and Functions
`parport-objs` always contains `share.o`, `ieee1284.o`, `ieee1284_ops.o`, and `procfs.o`. If `CONFIG_PARPORT_1284=y`, it adds `daisy.o` and `probe.o`. `obj-$(CONFIG_...)` lines bind config symbols to low-level driver objects such as `parport_pc.o`, `parport_cs.o`, `parport_amiga.o`, `parport_gsc.o`, and `parport_ip32.o`.

## Control Flow
kbuild evaluates the core object list, conditionally extends it for IEEE 1284 discovery/probe support, then includes low-level modules based on selected config symbols. The core can be built-in or modular via `CONFIG_PARPORT`.

## State and Persistence
This is build metadata only. Its main stateful effect is the composition of the `parport` module, especially whether daisy-chain and probe code is linked.

## Dependencies and Integration Points
It consumes symbols declared in `Kconfig` and integrates all C files in this subset with the kernel build. It also implies that `ieee1284.c` and `ieee1284_ops.c` are always part of core parport, while `daisy.c` is only present when `PARPORT_1284` is built into the core.

## Risks
Because `daisy.o` and `probe.o` are included only when `CONFIG_PARPORT_1284` equals `y`, a modular or disabled advanced-mode configuration must be checked against intended behavior. Missing an `obj-*` mapping would silently omit a platform driver even if Kconfig offers it.

## Test Signals
Build logs or `make V=1` should show the expected object list for each config. `modinfo` or built-in symbol inspection should show platform drivers only when their configs are selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/daisy.c -->
# sources/distributed-fs/ceph-client/drivers/parport/daisy.c

## Purpose
`daisy.c` implements IEEE 1284.3 daisy-chain and multiplexor discovery for parport. It builds a canonical device-number topology, creates cloned `struct parport` aliases for mux ports, selects daisy devices for negotiated transfer modes, and provides `parport_open()`/`parport_close()` by canonical device number.

## Important APIs, Types, and Functions
The key state type is `struct daisydev`, linked in the global `topology` list protected by `topology_lock`. `parport_daisy_init()` discovers muxes and daisy devices, `parport_daisy_fini()` removes topology entries for a physical port, `parport_open()` registers a parport device by discovered canonical number, and `parport_daisy_select()` sends the correct chain-select command for EPP, ECP, or compatibility modes. Low-level command helpers are `cpp_daisy()` and `cpp_mux()`.

## Control Flow
Discovery registers a private `daisy_driver` once, checks whether a mux is present, clones extra logical ports for 2-way or 4-way muxes, recursively initializes clones, selects mux ports, deselects daisy devices, assigns daisy addresses, and adds a final legacy device entry. If nothing responds, it resets the attached devices through control lines and retries once. Address assignment uses the 1284.3 command preamble, strobes daisy addresses 0-3, records devices, and probes their device IDs.

## State and Persistence
State is in the in-memory topology list, `numdevs`, `daisy_init_done`, `port->muxport`, `real->slaves[]`, and `dev->daisy`. No persistent storage exists. Topology is rebuilt and removed as ports are announced or removed.

## Dependencies and Integration Points
The code depends on core parport registration, `parport_device_id()`, IEEE 1284 constants, parport control/status operations, scheduler/signal handling, and the daisy driver registration path. It integrates with high-level drivers through canonical device numbers and `parport_register_dev_model()`.

## Risks
Topology numbering can develop gaps; the comment notes enumeration is imperfect. `clone_parport()` creates aliases sharing the same physical registers, so mux selection must be correct before transfers. Discovery performs timing-sensitive control/data strobes and can mis-detect non-compliant peripherals. `add_dev()` silently drops entries on allocation failure.

## Test Signals
Expected logs include mux port announcements and daisy device counts. Tests should verify device-ID readback, `parport_open()` failure for absent devices, cleanup by `parport_daisy_fini()`, and correct select commands for EPP/ECP/compat modes on hardware or instrumented parport mocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/daisy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/ieee1284.c -->
# sources/distributed-fs/ceph-client/drivers/parport/ieee1284.c

## Purpose
`ieee1284.c` provides the core IEEE 1284 protocol orchestration for parport: waiting for peripheral status transitions, negotiating transfer modes, terminating negotiated modes, dispatching read/write calls to the selected low-level operation, and handling parport IEEE 1284 interrupts.

## Important APIs, Types, and Functions
Exported APIs are `parport_wait_event()`, `parport_poll_peripheral()`, `parport_wait_peripheral()`, `parport_negotiate()`, `parport_write()`, `parport_read()`, `parport_set_timeout()`, and `parport_ieee1284_interrupt()`. Internal helpers include `parport_ieee1284_wakeup()`, `timeout_waiting_on_port()`, `parport_ieee1284_terminate()`, and `parport_ieee1284_ack_data_avail()`.

## Control Flow
Wait helpers combine fast polling, interrupt-backed sleeps through `port->physport->ieee1284.irq`, and signal checks. Negotiation first terminates any incompatible current mode, drives IEEE 1284 event sequences over control/data lines, validates status transitions, handles extensibility-link requests, and sets `port->ieee1284.mode` and `phase`. `parport_write()` and `parport_read()` mask address/device-ID bits and choose hardware or software implementations from `port->ops`, negotiating byte/nibble reverse mode from compatibility when needed.

## State and Persistence
Protocol state is `port->physport->ieee1284.mode`, `phase`, the IRQ semaphore, and per-device timeout (`pardevice.timeout`). `parport_set_timeout()` mutates the active device timeout and wakes waiters when the current active device changes. All state is volatile kernel runtime state.

## Dependencies and Integration Points
This file sits between high-level parport clients and low-level drivers. It depends on the operation table for control/status/data primitives and mode-specific block transfer functions. It exports symbols for modules, and conditionally compiles full negotiation behavior under `CONFIG_PARPORT_1284`.

## Risks
Handshake correctness depends on exact status polarity and timing from hardware drivers. Zero timeouts force busy-wait paths and can be problematic if used for long operations. Unsupported modes return `-ENOSYS`, rejected modes return `1`, and non-compliant peripherals return `-1`, so callers must distinguish these outcomes. Interrupt wakeups are advisory; code rechecks status after wake.

## Test Signals
Protocol tests should cover successful compatibility, nibble, byte, EPP, and ECP negotiation; timeout paths at documented events; mode termination back to compatibility; interrupt-driven wakeups; read/write dispatch to the expected `port->ops` function; and behavior when `CONFIG_PARPORT_1284` is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/ieee1284.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/ieee1284_ops.c -->
# sources/distributed-fs/ceph-client/drivers/parport/ieee1284_ops.c

## Purpose
`ieee1284_ops.c` contains generic software IEEE 1284 transfer implementations used by low-level parport drivers when hardware-specific acceleration is absent. It covers compatibility writes, nibble/byte reverse reads, ECP forward/reverse data and address transfers, and software-emulated EPP data/address transfers.

## Important APIs, Types, and Functions
Exported functions include `parport_ieee1284_write_compat()`, `parport_ieee1284_read_nibble()`, `parport_ieee1284_read_byte()`, `parport_ieee1284_ecp_write_data()`, `parport_ieee1284_ecp_read_data()`, `parport_ieee1284_ecp_write_addr()`, `parport_ieee1284_epp_write_data()`, `parport_ieee1284_epp_read_data()`, `parport_ieee1284_epp_write_addr()`, and `parport_ieee1284_epp_read_addr()`. Direction helpers `ecp_forward_to_reverse()` and `ecp_reverse_to_forward()` manage ECP phase changes.

## Control Flow
Compatibility writes wait for `BUSY`/`ERROR` readiness, optionally yield the claimed port, write a byte, pulse strobe, and count accepted bytes. Nibble and byte reads perform IEEE event handshakes using `AUTOFD`, `ACK`, `STROBE`, and data/status lines. ECP writes drive HostAck/Strobe handshakes with transfer recovery attempts; ECP reads can accept RLE command bytes and expand them. EPP routines emulate address/data strobes with short polling windows and restore forward direction after reverse reads.

## State and Persistence
The functions update `port->physport->ieee1284.phase` and depend on `port->physport->cad->timeout`. ECP reads maintain local RLE counters only during a call. There is no persistent storage beyond parport state.

## Dependencies and Integration Points
Low-level drivers place these functions into `struct parport_operations` as fallbacks. The code depends only on generic parport primitives, `parport_wait_peripheral()`, `parport_wait_event()`, scheduler/signal APIs, and memory helpers such as `memset()`.

## Risks
The generic operations assume compliant control/status polarity from drivers. ECP RLE and channel-command handling can stop short or accept illegal RLE from devices not negotiated for RLE. Compatibility writes may release and reclaim the port during waits, so callers must tolerate interleaving through parport arbitration. Fast EPP timing is implemented in software and may fail on slow or unusual devices.

## Test Signals
Good tests include loopback or peripheral-based transfer count validation, signal interruption, timeout behavior, phase transitions, RLE decompression, port yield/reclaim behavior during long compatibility writes, and fallback use by simple platform drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/ieee1284_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/multiface.h -->
# sources/distributed-fs/ceph-client/drivers/parport/multiface.h

## Purpose
`multiface.h` provides address constants for Amiga SerialMaster and Multiface II/III expansion-card register blocks. In this subset it is used by `parport_mfc3.c` to locate the PIA parallel-port block relative to a Zorro card base.

## Important APIs, Types, and Functions
The header defines `PIA_REG_PADWIDTH`, `DUARTBASE`, `PITBASE`, `ROMBASE`, and `PIABASE`. It has only include guards and no functions or types.

## Control Flow
There is no runtime control flow. Consumers include the header and add offsets such as `PIABASE` to bus resources.

## State and Persistence
The constants encode hardware layout. No mutable or persistent state exists.

## Dependencies and Integration Points
`parport_mfc3.c` uses `PIABASE` to request and map the MC6821 PIA registers for the Multiface III parallel port. Other card functions may use the remaining offsets.

## Risks
Incorrect offsets would make low-level drivers touch the wrong card registers. `PIA_REG_PADWIDTH` is a hardware access-spacing constant and must stay aligned with MC6821/Zorro register layout expectations.

## Test Signals
Compile-time inclusion should succeed, and MFC3 probing should request memory at `zorro_resource.start + PIABASE`. Hardware tests should confirm PIA register access at that offset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/multiface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_amiga.c -->
# sources/distributed-fs/ceph-client/drivers/parport/parport_amiga.c

## Purpose
`parport_amiga.c` is the low-level driver for the Amiga built-in parallel port. It adapts Amiga CIA registers to the generic parport operation table despite hardware limitations such as automatic strobe on data access and mostly non-programmable control lines.

## Important APIs, Types, and Functions
The driver defines `pp_amiga_ops`, implementing data, status, IRQ, direction, and state callbacks. `amiga_parallel_probe()` registers one port using `ciaa.prb` and `IRQ_AMIGA_CIAA_FLG`, requests the IRQ with `parport_irq_handler`, announces the port, and stores it in platform device data. `amiga_parallel_remove()` removes the port, frees IRQ, and drops the parport reference.

## Control Flow
Platform probe initializes data lines as outputs and status lines as inputs, calls `parport_register_port()`, requests the CIAA flag interrupt, logs the port, announces it, and returns. Data reads/writes access `ciaa.prb`; status reads translate low CIA bits from `ciab.pra`; direction callbacks switch `ciaa.ddrb`. Control write is intentionally a no-op because the hardware cannot directly drive those PC-style lines.

## State and Persistence
State is held in CIA data/direction registers and saved/restored through `struct parport_state` fields under `u.amiga`. The platform device stores the `struct parport *`. No persistent state exists.

## Dependencies and Integration Points
The driver depends on Amiga platform headers, CIA register globals, platform-driver probing, parport core, and generic IEEE 1284 software operations. It exposes a `platform:amiga-parallel` alias.

## Risks
PC-style control semantics are partly faked, so some IEEE 1284 protocols may be unreliable despite generic ops being present. Reading data also triggers strobe according to the hardware comment. State restore uses direct CIA bit manipulation and must preserve unrelated bits. Interrupt behavior depends on `/ACK` through CIAA flag IRQ.

## Test Signals
Probe should announce an Amiga built-in port with IRQ. Tests should validate data direction changes, status bit translation for BUSY/PAPEROUT/SELECT, interrupt delivery through `parport_irq_handler`, and graceful removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_amiga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_atari.c -->
# sources/distributed-fs/ceph-client/drivers/parport/parport_atari.c

## Purpose
`parport_atari.c` adapts the Atari built-in parallel port to parport. The hardware has output data, strobe control, and BUSY interrupt/status only, so the driver provides a minimal PC-style parport surface.

## Important APIs, Types, and Functions
`parport_atari_ops` implements data access through YM sound-chip registers, strobe control, BUSY status, IRQ enable/disable, forward direction setup, and generic IEEE 1284 fallback functions. `parport_atari_init()` checks `MACH_IS_ATARI`, configures sound-chip and MFP registers, registers the port, requests `IRQ_MFP_BUSY`, and announces it. `parport_atari_exit()` removes and releases it.

## Control Flow
Data reads/writes select YM register 15 under `local_irq_save()`. Control accesses select YM register 14 and manipulate bit 5 for STROBE. Init configures sound-chip ports as outputs, sets strobe high, configures MFP port I0 as input and high-to-low edge interrupt, registers the parport, requests IRQ, and announces. Reverse direction and state callbacks are empty because the hardware does not support meaningful reverse data state here.

## State and Persistence
Global `this_port` holds the registered port. Hardware state lives in YM and MFP registers. No persistent state exists; state callbacks are no-ops.

## Dependencies and Integration Points
The driver depends on Atari platform globals (`sound_ym`, `st_mfp`), Atari IRQ definitions, parport core, and generic IEEE 1284 operations. It integrates with parport IRQ handling via `parport_irq_handler`.

## Risks
The operation table advertises generic reverse/advanced functions even though `data_reverse()` is empty and status lines are sparse, so advanced IEEE 1284 modes may not work beyond simple compatibility use. Register access needs interrupt masking because YM register select/data writes are shared hardware state.

## Test Signals
On Atari hardware, init should announce one port with `IRQ_MFP_BUSY`. Functional checks should verify YM data writes, strobe toggling, BUSY status polarity, interrupt delivery on MFP I0, and clean unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_atari.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_cs.c -->
# sources/distributed-fs/ceph-client/drivers/parport/parport_cs.c

## Purpose
`parport_cs.c` is a PCMCIA wrapper for PC-style parallel-port cards, originally targeting Quatech SPP-100 EPP-class adapters. It allocates PCMCIA resources and delegates actual port probing/unregistration to `parport_pc`.

## Important APIs, Types, and Functions
The local state type is `parport_info_t`, holding the `pcmcia_device`, number of registered ports, and `struct parport *`. `parport_probe()` allocates state and starts configuration. `parport_config_check()` requests 8-bit I/O windows. `parport_config()` loops CIS configs, enables the card, calls `parport_pc_probe_port()`, and marks EPP capabilities if requested. `parport_cs_release()` unregisters and disables the card. `parport_cs_driver` binds PCMCIA IDs.

## Control Flow
Probe allocates `link->priv`, sets `CONF_ENABLE_IRQ | CONF_AUTO_SET_IO`, then configures. Configuration optionally sets `FORCE_EPP_MODE`, requests I/O, requires an IRQ, enables the PCMCIA device, probes a PC-style parport at resource windows 0 and 1, and records success. Remove calls release and frees private state.

## State and Persistence
State is per-card heap memory referenced by `link->priv`; runtime hardware/resource state is managed through PCMCIA core and `parport_pc`. The module parameter `epp_mode` controls EPP forcing and advertised modes.

## Dependencies and Integration Points
The driver depends on PCMCIA core APIs, CIS IDs, `parport_pc_probe_port()`, and `parport_pc_unregister_port()`. It integrates PCMCIA hotplug with the parport PC low-level implementation.

## Risks
The failure path in `parport_config()` calls `parport_cs_release(link)` and frees `link->priv`; `parport_detach()` also frees `link->priv`, so probe-time failure handling must be reviewed against PCMCIA core expectations to avoid double-free or stale private data. The driver assumes two I/O windows and an IRQ. `epp_mode` may advertise EPP/TRISTATE on cards that do not behave like the original target.

## Test Signals
Hotplug tests should cover resource allocation, no-IRQ rejection, successful `parport_pc_probe_port()`, EPP-mode flagging, card removal, and probe failure paths under allocation or I/O request failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_gsc.c -->
# sources/distributed-fs/ceph-client/drivers/parport/parport_gsc.c

## Purpose
`parport_gsc.c` is the HP PA-RISC GSC/LASI low-level parallel-port driver for PC-style hardware. It probes SPP and bidirectional capability, registers a parport instance, handles IRQ setup, and binds to PA-RISC FIO devices.

## Important APIs, Types, and Functions
`parport_gsc_ops` is the operation table, with basic accessors from `parport_gsc.h` and generic IEEE 1284 fallbacks. `clear_epp_timeout()`, `parport_SPP_supported()`, and `parport_PS2_supported()` probe hardware behavior. `parport_gsc_probe_port()` allocates private data and copied ops, performs detection, registers the port, requests IRQ if available, initializes data direction, and announces the port. `parport_init_chip()` is the PA-RISC probe entry.

## Control Flow
The PA-RISC driver matches HPHW_FIO sversion `0x74`. Probe checks a platform IRQ, computes port base as HPA plus `PARPORT_GSC_OFFSET`, optionally initializes enhanced mode on newer CPUs with valid PDC address, then probes the port. Port probing first tests a stack `struct parport` for hardware existence, then registers a real parport and transfers detected modes. Removal unregisters, frees IRQ, frees private data and copied ops, and drops the parport reference.

## State and Persistence
`struct parport_gsc_private` stores cached control register value, writable control mask, PWord metadata placeholders, and unused DMA-related fields. Driver-global `parport_count` counts successful probes. Hardware state is in GSC memory-mapped data/status/control registers.

## Dependencies and Integration Points
The driver depends on PA-RISC device registration, PDC address validation, SuperIO/GSC I/O helpers, parport core, and generic IEEE 1284 software operations. `parport_gsc.h` supplies inline register access and control-bit handling.

## Risks
`parport_count` is incremented but not used for policy. EPP/ECP advanced detection is limited; modes printed exclude ECP/DMA. The copied ops table is freed on removal with a comment noting risk if someone cached it. Probe manually allocates before `parport_register_port()`, so all failure paths must keep private and ops lifetimes paired.

## Test Signals
Boot on LASI/GSC systems should log the PC-style base, IRQ, and modes. Hardware tests should verify SPP data read/write, PS/2 tristate detection, IRQ fallback to polled operation when busy, and clean driver unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_gsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_gsc.h -->
# sources/distributed-fs/ceph-client/drivers/parport/parport_gsc.h

## Purpose
`parport_gsc.h` defines register offsets, private driver state, and inline accessors for the HP PA-RISC GSC parport driver. It abstracts GSC byte I/O into the operation callbacks used by `parport_gsc.c`.

## Important APIs, Types, and Functions
Macros `DATA(p)`, `STATUS(p)`, `CONTROL(p)`, `EPPADDR(p)`, and `EPPDATA(p)` compute register addresses. `struct parport_gsc_private` caches control register state and writable bits. Inline callbacks implement data read/write, raw and masked control frobbing, direction changes, status reads, and IRQ enable/disable. Extern declarations expose resource/state helpers and use-count hooks.

## Control Flow
Each control operation updates the cached `ctr`, masks writes through `ctr_writable`, writes the hardware control register, and returns or exposes the cached PC-style bits. Direction control uses bit `0x20`; IRQ enable uses bit `0x10`. Debug builds can add trace logging and optional I/O delays.

## State and Persistence
The main state is `priv->ctr` and `priv->ctr_writable`, which represent soft control-register state and allowed hardware bits. This avoids relying on hardware readback for logical control values.

## Dependencies and Integration Points
The header depends on GSC I/O helpers from `asm/io.h`, `linux/delay.h`, and parport structures from including C files. It is tightly coupled to `parport_gsc.c` and the core parport callback contract.

## Risks
Because reads of control return a software copy, any external hardware modification would not be reflected. The legacy warning path accepts attempts to control direction through bit `0x20` in write/frob control but asks callers to use `data_reverse`/`data_forward`. Register offsets must match LASI/GSC PC-style layout.

## Test Signals
Unit-style instrumentation can validate control mask behavior, direction bit updates, and status/data register addressing. Hardware tests should confirm `ctr_writable` is reduced when PS/2 direction is unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_gsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_ip32.c -->
# sources/distributed-fs/ceph-client/drivers/parport/parport_ip32.c

## Purpose
`parport_ip32.c` is the SGI O2/IP32 built-in parallel-port driver for the memory-mapped TL16PIR552-compatible hardware behind MACE. It supports basic SPP/PS2, IRQ forwarding, hardware EPP, FIFO-backed compatibility/ECP writes, and optional DMA for FIFO writes.

## Important APIs, Types, and Functions
Key types are `struct parport_ip32_regs`, `struct parport_ip32_private`, and `struct parport_ip32_dma_data`. The operation table starts as `parport_ip32_ops` and is patched during probing to use hardware SPP/EPP/ECP paths when enabled. Major functional groups include DMA setup/interrupt/stop (`parport_ip32_dma_*`), interrupt forwarding/local completion (`parport_ip32_interrupt()`), DCR/ECR register helpers, EPP accessors, FIFO wait/write/drain/residue helpers, compatibility and ECP write accelerators, feature probing, and module init/exit.

## Control Flow
Initialization computes memory-mapped ISA-style register addresses with a register shift of 8, allocates ops/private data, registers a placeholder parport, verifies ECR presence, assumes base PCSPP/TRISTATE capability, probes FIFO depth and thresholds, requests the main parallel IRQ if enabled, registers DMA context IRQs if enabled, patches operation callbacks for selected hardware features, initializes PS2 forward mode, prints modes, and announces the port. Transfers then use the active parport mode: EPP functions switch to EPP mode, perform byte or string I/O, clear timeout on failure, and return to PS2; FIFO compatibility/ECP writes switch to PPF/ECP mode, wait for peripheral readiness, write through PIO or DMA, drain and account for residue, then reset back to PS2.

## State and Persistence
Per-port private state caches DCR, writable DCR bits, FIFO parameters, IRQ mode, and a completion used for local waits. DMA state is global because only one port is supported: mapped buffer address, remaining byte count, active context, IRQ-on flag, and spinlock. Module parameters `features` and `verbose_probing` control runtime feature enablement. No state persists beyond module lifetime.

## Dependencies and Integration Points
The driver depends on MIPS IP32 MACE registers/IRQs, DMA mapping APIs, parport core, generic IEEE 1284 operations, completions, spinlocks, and memory-mapped I/O helpers. It integrates hardware IRQs either by forwarding to `parport_irq_handler()` or satisfying local FIFO waits, and registers DMA context IRQs separately from the parport IRQ.

## Risks
The file documents unimplemented hardware ECP read and ECP address-write support. DMA supports only `DMA_TO_DEVICE` and uses `BUG_ON()` for other directions. FIFO status is noted as unreliable; residue accounting has a FIXME about a missing byte when the printer is offline. Feature probing mutates the global `features` mask, so one failed probe disables later feature paths. Correct behavior depends on IP32-only single-port assumptions and MACE context IRQ handling.

## Test Signals
Useful tests include boot/probe logs for ECR/FIFO/IRQ/DMA feature enablement, EPP timeout clearing, PIO and DMA FIFO write counts, IRQ-mode switching between forwarded and local completion behavior, module parameter combinations disabling each feature, cleanup of IRQ/DMA resources on unload, and real peripheral tests for SPP/EPP/ECP write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_ip32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_mfc3.c -->
# sources/distributed-fs/ceph-client/drivers/parport/parport_mfc3.c

## Purpose
`parport_mfc3.c` is the low-level parport driver for Amiga Multiface III Zorro expansion cards. It maps the card's MC6821 PIA registers to parport operations and supports up to five cards sharing the Amiga ports interrupt.

## Important APIs, Types, and Functions
The driver uses `MAX_MFC`, global `this_port[]`, shared `use_cnt`, and `pp_mfc3_ops`. Data/control/status functions translate between PC parport bits and MFC3 PIA pins. `mfc3_interrupt()` scans registered cards for PIA interrupt status and calls `parport_generic_irq()`. `parport_mfc3_init()` discovers Zorro devices, initializes PIA data/status directions, registers ports, requests shared IRQ on first user, and announces each port. Exit unregisters all ports and releases resources.

## Control Flow
Init first requires `MACH_IS_AMIGA`, then loops over `ZORRO_PROD_BSC_MULTIFACE_III` devices. For each card it requests the PIA memory region at `resource.start + PIABASE`, maps it with `ZTWO_VADDR`, programs PIA control/data direction, pulses printer reset, registers a parport, requests the shared IRQ once, stores the port, sets `p->dev` and private physical base, then announces. Removal reverses this per slot and frees the IRQ when the last user exits.

## State and Persistence
State is the global port array, shared IRQ use count, dummy volatile reads used to clear interrupt bits, and PIA register contents. Per-port `private_data` stores the physical PIA base for release. Parport state callbacks save and restore PIA data/direction/status fields in `u.amiga`.

## Dependencies and Integration Points
The driver depends on `multiface.h`, Amiga/Zorro APIs, MC6821 PIA definitions, Amiga IRQs, parport core, and generic IEEE 1284 operations. It integrates with Zorro device discovery rather than platform-device probing.

## Risks
The interrupt handler scans all registered ports and always returns `IRQ_HANDLED`, which can mask unexpected shared IRQ causes. State save/restore manipulates PIA DDR visibility and must restore control-register mode correctly. Probe failure after shared IRQ request or partial card setup relies on local labels and loop continuation; multi-card cleanup needs `use_cnt` consistency. Generic advanced IEEE 1284 ops may exceed what the card/peripheral timing supports.

## Test Signals
Tests should cover discovery of zero, one, and multiple cards; memory-region conflict handling; shared IRQ request/free only on first/last port; data and status bit translation; interrupt clearing via PIA reads; parport announce/remove; and save/restore of PIA direction registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parport/parport_mfc3.c -->
