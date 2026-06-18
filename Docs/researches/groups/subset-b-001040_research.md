# subset-b-001040 research

Grouped research for ceph-client Linux ATA PATA controller and pata_parport protocol sources. Each source section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_octeon_cf.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_octeon_cf.c

## Purpose
Provides the Cavium OCTEON bootbus CompactFlash libata driver. It supports 8-bit PIO, 16-bit PIO, and 16-bit True IDE with optional bootbus DMA, all described by Open Firmware properties.

## Important APIs, Types, And Functions
`struct octeon_cf_port` keeps the hrtimer, ATA port pointer, DMA state, chip selects, True IDE flag, and DMA register base. Timing helpers include `ns_to_tim_reg()`, `octeon_cf_set_boot_reg_cfg()`, `octeon_cf_set_piomode()`, and `octeon_cf_set_dmamode()`. Data/taskfile hooks include `octeon_cf_data_xfer8()`, `octeon_cf_data_xfer16()`, `octeon_cf_tf_read16()`, `octeon_cf_tf_load16()`, `octeon_cf_softreset16()`, and `octeon_cf_exec_command16()`. DMA control is split across `octeon_cf_dma_setup()`, `octeon_cf_dma_start()`, `octeon_cf_interrupt()`, `octeon_cf_delayed_finish()`, and `octeon_cf_dma_finished()`.

## Control Flow
Probe reads `cavium,true-ide`, `cavium,bus-width`, bootbus chip-select registers, and an optional DMA-engine phandle, maps the command/control regions, selects the appropriate SFF overrides, and activates a one-port host. PIO commands fall through `ata_sff_qc_issue()`. DMA commands load the taskfile, submit one scatterlist segment to the bootbus DMA engine, advance to the next segment on DMA-done interrupts, then either finish immediately or poll with an hrtimer until the CF card clears BUSY/DRQ.

## State And Persistence
Driver state is device-managed except for hardware state in OCTEON bootbus CS timing registers and DMA CSRs. `ap->private_data` and `pdev->dev.platform_data` point at `struct octeon_cf_port`; `dma_finished` and `qc->cursg` track active DMA progress under `host->lock`.

## Dependencies And Integration Points
Integrates libata SFF/BMDMA-like hooks, OF address/property parsing, OCTEON `cvmx_*` CSR accessors, DMA mask setup, hrtimers, IRQ delivery from the companion DMA platform device, and libata tracepoints.

## Risks And Edge Cases
`octeon_cf_ops` is a static operations object that probe mutates based on board mode, so multiple differently wired devices would share changed callbacks. DMA is opt-in by module parameter and only valid in True IDE mode. DMA size is limited to the 20-bit bootbus counter, and shutdown must quiesce DMA and pulse reset. Busy-after-DMA timing is card dependent, making the interrupt/hrtimer handoff critical.

## Test Signals
Boot DT variants for 8-bit, 16-bit non-True-IDE, and True IDE DMA; PIO0-6 timing programming; odd-byte 16-bit transfers; LBA48 HOB taskfile reads; multi-segment DMA; DMA timeout/error injection; unload or shutdown during no-DMA and DMA cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_octeon_cf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_of_platform.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_of_platform.c

## Purpose
Adapts Open Firmware `ata-generic` nodes to the generic `__pata_platform_probe()` helper, letting device-tree systems instantiate simple PIO-only ATA interfaces.

## Important APIs, Types, And Functions
`pata_of_platform_probe()` is the only substantive function. It resolves two address resources with `of_address_to_resource()`, obtains an optional IRQ with `platform_get_irq_optional()`, parses `reg-shift`, `pio-mode`, and `ata-generic,use16bit`, builds a cumulative PIO mask, and calls `__pata_platform_probe()`.

## Control Flow
Probe fails if IO or CTL resources are missing, accepts no IRQ as polling mode, defaults absent `pio-mode` to PIO0, rejects modes above PIO6, and delegates all host allocation, register mapping, and activation to `pata_platform.c`.

## State And Persistence
No private persistent state is allocated here. The resulting ATA host state is owned by the generic platform helper and removed by `ata_platform_remove_one`.

## Dependencies And Integration Points
Depends on OF address translation, `ata_platform.h`, libata SFF support, and the `ata-generic` compatible string.

## Risks And Edge Cases
Incorrect DT resource ordering or bad `reg-shift` gives wrong taskfile register addresses. IRQ values less than zero except `-ENXIO` are propagated, while no IRQ intentionally becomes polling. The 16-bit flag changes the data transfer callback selected by the helper.

## Test Signals
DT nodes with and without IRQ, several `pio-mode` values, invalid PIO mode rejection, nonzero `reg-shift`, 16-bit transfer property, and removal via the platform driver's generic remove path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_of_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_oldpiix.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_oldpiix.c

## Purpose
Implements libata support for early Intel PIIX controllers that lack separate slave timing registers. Because timing is effectively per channel, the driver reloads timing when issuing commands to a different device.

## Important APIs, Types, And Functions
`oldpiix_pre_reset()` verifies PCI enable bits before SFF reset. `oldpiix_set_piomode()` and `oldpiix_set_dmamode()` program IDE timing registers at `0x40/0x42`. `oldpiix_qc_issue()` is the key wrapper that detects drive changes and reloads PIO/DMA timing before delegating to `ata_bmdma_qc_issue()`.

## Control Flow
PCI probe registers a BMDMA host for device ID `0x1230`. During mode setup, libata calls timing functions and the driver records the currently programmed `ata_device` in `ap->private_data`. Every command issue compares that pointer with `qc->dev`; if it differs, the driver reprograms shared timing and then starts the normal BMDMA/SFF command path.

## State And Persistence
Persistent state is minimal: PCI config timing registers and `ap->private_data` as a cache of which drive's timing is loaded. No driver-private allocation is needed.

## Dependencies And Integration Points
Uses libata BMDMA port operations, SFF prereset, PCI config access, Intel timing encodings, and standard libata PCI suspend/resume helpers.

## Risks And Edge Cases
The entire correctness model depends on `qc_issue()` seeing all drive switches. Clearing the other drive's TIME bits is a defensive fallback but may reduce performance. Shared timing makes mixed master/slave devices a regression-prone path, especially for MWDMA modes that require derived PIO timing.

## Test Signals
Master-only, slave-only, and master/slave configurations; alternating command streams; MWDMA mode selection; disabled PCI port bits returning `-ENOENT`; suspend/resume preserving libata behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_oldpiix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_opti.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_opti.c

## Purpose
Supports early OPTi 621/621X PCI PATA controllers using indexed controller registers and PIO-only libata operation.

## Important APIs, Types, And Functions
`opti_pre_reset()` checks controller enable bits before generic SFF reset. `opti_write_reg()` performs the OPTi indexed-register access sequence. `opti_set_piomode()` computes PIO timing from `ata_timing_compute()` and writes read/write/control timing fields. `opti_init_one()` registers a single PIO port via `ata_pci_sff_init_one()` style libata infrastructure.

## Control Flow
On probe, the PCI ID table selects OPTi 82C621-class hardware. Reset first checks port enablement. Mode setup derives address/setup/recovery/active timing from the ATA timing table and writes the controller's read, write, strap, control, and miscellaneous timing registers through the indexed configuration window.

## State And Persistence
State persists in PCI/controller timing registers only. The driver does not allocate private state and has no runtime cache beyond libata's device mode fields.

## Dependencies And Integration Points
Depends on PCI config access, libata SFF PIO operations, `ata_timing_compute()`, and generic PCI driver registration.

## Risks And Edge Cases
The hardware programming sequence is register-index sensitive and old-chip documentation is sparse. Unsupported variants may have incompatible strap/control behavior. Since the driver is PIO-only, DMA-capable later OPTi chips belong in `pata_optidma.c`.

## Test Signals
Probe/reset on both ports, PIO0-4 mode programming, IORDY-needed devices, disabled-port detection, and comparison with legacy IDE timing behavior on real OPTi hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_opti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_optidma.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_optidma.c

## Purpose
Handles OPTi FireStar and FireStar Plus DMA-capable PCI PATA controllers, including both base DMA timing and FireStar Plus UDMA-specific paths.

## Important APIs, Types, And Functions
`optidma_pre_reset()` checks enable bits. `optidma_lock()` and `optidma_unlock()` guard the controller's timing-programming window. `optidma_mode_setup()` handles base PIO/MWDMA timing, while `optiplus_mode_setup()` handles Plus timing and UDMA. `optidma_set_mode()` coordinates libata mode selection and controller-specific bit programming. `optiplus_with_udma()` identifies UDMA-capable Plus variants.

## Control Flow
Probe chooses either `optidma_port_ops` or `optiplus_port_ops` based on PCI ID and hardware probing, then registers BMDMA ATA ports. Mode setup computes or selects timing values, enters the controller's indexed programming mode, writes timing/control registers, and exits the mode. Plus chips use a different setup routine and can expose UDMA masks.

## State And Persistence
The module-level `pci_clock` captures clock assumptions, while actual transfer state persists in PCI config and controller timing registers. Runtime ATA state is owned by libata.

## Dependencies And Integration Points
Uses libata BMDMA operations, PCI config IO, controller-specific locking sequences, generic PCI power-management helpers, and ATA mode/timing helpers.

## Risks And Edge Cases
The indexed timing register lock/unlock sequence is fragile; failures can corrupt unrelated controller settings. Clock assumptions affect timing correctness. UDMA detection for Plus variants is hardware-specific, and mixed devices require careful mode bit composition.

## Test Signals
PIO, MWDMA, and UDMA mode transitions; Plus versus non-Plus hardware; lock/unlock error paths; disabled port reset; suspend/resume; and data integrity under sustained DMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_optidma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/Kconfig

## Purpose
Defines Kconfig entries for optional parallel-port IDE protocol modules used by the `pata_parport` core.

## Important APIs, Types, And Functions
The file declares tristate options for ATEN, MicroSolutions BACKPACK Series 5 and 6, DataStor, Fidelity, Shuttle, Freecom, KingByte, KT, and OnSpec protocols. `PATA_PARPORT_EPATC8` is a bool child option of `PATA_PARPORT_EPAT` that enables Shuttle EP1284/c7/c8 support.

## Control Flow
There is no runtime control flow. Build-time dependency resolution requires `PATA_PARPORT`, then allows each protocol module to be compiled built-in, modular, or omitted.

## State And Persistence
Configuration state persists in the kernel `.config`; it determines which protocol drivers are compiled and therefore which `pi_protocol` registrations are available at runtime.

## Dependencies And Integration Points
Integrates with `drivers/ata/pata_parport/Makefile`, the central `PATA_PARPORT` option, and individual protocol modules that call `pata_parport_register_driver()`.

## Risks And Edge Cases
Selecting the wrong BACKPACK series or omitting EPATC8 support can make real hardware invisible. Built-in protocol choices affect probing order and may keep some Freecom powered devices enabled for the life of the kernel.

## Test Signals
Kconfig dependency checks, module build matrix for every option, EPAT with and without c8 support, and boot/module-load probing with multiple protocol options enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/Makefile

## Purpose
Maps `PATA_PARPORT*` Kconfig symbols to the core `pata_parport.o` object and each parallel-port IDE protocol object.

## Important APIs, Types, And Functions
The Makefile uses standard `obj-$(CONFIG_...) += file.o` entries for the core and all protocol modules: `aten`, `bpck`, `bpck6`, `comm`, `dstr`, `epat`, `epia`, `fit2`, `fit3`, `friq`, `frpw`, `kbic`, `ktti`, `on20`, and `on26`.

## Control Flow
Build control flow is declarative: enabled symbols add objects to the kernel or module build.

## State And Persistence
No runtime state. Build artifacts and module availability persist according to the kernel configuration.

## Dependencies And Integration Points
Directly consumes symbols from the adjacent Kconfig and emits modules that depend on the exported `pata_parport` protocol registration API.

## Risks And Edge Cases
Object names must stay aligned with Kconfig symbols and source files. Missing core selection would leave protocol modules without exported registration symbols.

## Test Signals
`make M=drivers/ata/pata_parport` with all options enabled, modular-only builds, built-in builds, and modpost symbol dependency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/aten.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/aten.c

## Purpose
Implements the ATEN EH-100 parallel-port IDE protocol for the `pata_parport` core, supporting 4-bit and 8-bit transfer modes.

## Important APIs, Types, And Functions
`aten_write_regr()` and `aten_read_regr()` translate ATA register accesses through ATEN command/control strobes. `aten_read_block()` and `aten_write_block()` transfer PIO data in the selected mode. `aten_connect()`, `aten_disconnect()`, and `aten_log_adapter()` save/restore parallel-port state and report mode details. The `aten` `pi_protocol` advertises `max_mode = 2` and one unit.

## Control Flow
The core probes modes through the protocol table, calls connect before register tests, and then uses the protocol callbacks for libata taskfile and data operations. Mode 0 reconstructs bytes from nibbles with `j44()`, while mode 1 uses direct 8-bit reads.

## State And Persistence
`pi->saved_r0` and `pi->saved_r2` preserve port register state across connect/disconnect. No protocol-private allocation exists.

## Dependencies And Integration Points
Depends on `pata_parport.h` port IO macros and `module_pata_parport_driver()` registration.

## Risks And Edge Cases
The EH-132 EPP variant is explicitly unsupported. Byte-pair loops assume even transfer counts from libata PIO block operations. Incorrect restore of parallel-port state can affect other devices after detach.

## Test Signals
Mode 0 and mode 1 probe, register echo tests, read/write sectors, disconnect state restoration, and failure to select unsupported EPP modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/aten.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/bpck.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/bpck.c

## Purpose
Implements MicroSolutions BACKPACK Series 5 parallel-port IDE protocol support, including chained-unit probing, register access, block transfers, EEPROM reads, and port/mode validation.

## Important APIs, Types, And Functions
`bpck_read_regr()` and `bpck_write_regr()` access ATA and internal BACKPACK registers. `bpck_read_block()` and `bpck_write_block()` implement 4-bit, 8-bit, EPP-8, EPP-16, and EPP-32 modes. `bpck_probe_unit()`, `bpck_test_proto()`, `bpck_test_port()`, `bpck_read_eeprom()`, and `bpck_log_adapter()` provide detection and diagnostics. The protocol uses `pi->private` as a shadow of control register 2 through custom `r2/w2/t2` macros.

## Control Flow
Probe selects a chained unit, tests supported port modes, runs register and block scratch tests, and logs EEPROM-derived adapter information. Runtime register and data callbacks select different strobe sequences based on `pi->mode`, with EPP modes using port offset 4 for bulk data.

## State And Persistence
Port state is saved in `pi->saved_r0`; `pi->private` mirrors the current control byte and avoids stale toggles. Hardware mode and selected unit persist until disconnect.

## Dependencies And Integration Points
Integrates with the core `pi_protocol` interface, low-level x86 port IO, and BACKPACK internal register conventions.

## Risks And Edge Cases
Series 5 and Series 6 hardware require different drivers. Chained unit selection and EEPROM probing are timing-sensitive. The protocol uses raw casts for 16/32-bit EPP transfers and assumes aligned counts from the ATA layer.

## Test Signals
Unit 0-7 probing, all five transfer modes, EEPROM identification, register echo tests, sector transfers, and rejection of Series 6 devices when only this protocol is loaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/bpck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/bpck6.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/bpck6.c

## Purpose
Supports MicroSolutions BACKPACK Series 6 parallel-port IDE adapters using the newer PPC command/register protocol.

## Important APIs, Types, And Functions
Command helpers include `bpck6_send_cmd()`, byte data helpers, `bpck6_read_regr()`, `bpck6_write_regr()`, and `bpck6_wait_for_fifo()`. Bulk transfer callbacks implement software and EPP modes. `bpck6_open()`, `bpck6_deselect()`, `bpck6_connect()`, `bpck6_disconnect()`, `bpck6_test_port()`, `bpck6_probe_unit()`, and `bpck6_log_adapter()` handle adapter activation and detection. `mode_map[]` maps core modes to PPC modes.

## Control Flow
Probe validates the port, opens the PPC interface, selects a unit, chooses a supported transfer mode, and then leaves normal ATA register and block accesses to protocol callbacks. FIFO waits guard bulk transfers, and command prefixes alter read/write/register versus port access.

## State And Persistence
The selected PPC mode, unit, saved parallel-port state, and any protocol-private values live in `pi_adapter`. Hardware selection persists while the core keeps the parport claimed.

## Dependencies And Integration Points
Uses `pata_parport.h`, raw port IO, module registration, and the core's probe loop for modes and units.

## Risks And Edge Cases
FIFO wait timeout behavior is key to avoiding hangs. Series 6 command prefixes differ from Series 5, so false-positive probing would cause bad strobes. EPP word/dword paths depend on port alignment enforced by the core.

## Test Signals
Series 6 probe, mode mapping across UNI/BI/EPP modes, FIFO timeout injection, register echo, block reads/writes, unit deselect, and clean disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/bpck6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/comm.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/comm.c

## Purpose
Implements the DataStor Commuter parallel-port IDE adapter protocol for `pata_parport`.

## Important APIs, Types, And Functions
`comm_read_regr()` and `comm_write_regr()` encode ATA register access using Commuter control maps and strobe macros. `comm_read_block()` and `comm_write_block()` implement nibble and byte transfer modes. `comm_connect()`, `comm_disconnect()`, and `comm_log_adapter()` manage port state and diagnostics. The `comm` `pi_protocol` exposes two non-EPP modes.

## Control Flow
During probe the core connects, performs default register echo testing, and records the best working mode. At runtime, ATA taskfile accesses go through the register callbacks; data phases call the block callbacks that reconstruct or emit bytes using the Commuter handshake.

## State And Persistence
The protocol stores only saved parallel-port registers in `pi->saved_r0/saved_r2` and uses `pi->mode` for transfer selection.

## Dependencies And Integration Points
Depends on `pata_parport` core registration and SPP-style parallel port IO macros.

## Risks And Edge Cases
Low-speed nibble mode is timing-sensitive and susceptible to wrong delay settings. The protocol has no custom test hook, so default register tests must distinguish it from similar adapters.

## Test Signals
Default protocol testing, both modes, ATA identify/read/write paths, delay override through `new_device`, and disconnect restoring saved registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/comm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/dstr.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/dstr.c

## Purpose
Implements the DataStor EP2000 parallel-to-IDE protocol with nibble, 8-bit, and EPP block transfer modes.

## Important APIs, Types, And Functions
`dstr_read_regr()` and `dstr_write_regr()` access command/control register spaces through DataStor strobe sequences. `dstr_read_block()` and `dstr_write_block()` implement modes 0-4, including EPP-16 and EPP-32 paths. `dstr_connect()` and `dstr_disconnect()` use the `CCP()` command preamble to enter and leave adapter mode. The `dstr` protocol advertises `epp_first = 2`.

## Control Flow
The core tests available modes, then normal ATA operations dispatch into register or block callbacks. Connect saves the parallel-port state and sends the EP2000 enable sequence; disconnect sends the disable sequence and restores the port.

## State And Persistence
Only saved port register values and the selected mode are persistent in `pi_adapter`. Adapter hardware state remains enabled while connected.

## Dependencies And Integration Points
Uses `pata_parport.h` IO helpers and the core `pi_protocol` registration path.

## Risks And Edge Cases
EPP paths assume an EPP-capable base address and count alignment. The custom enable/disable sequence is easy to break with delay changes. Like other protocols, it monopolizes the parport while the ATA host is active.

## Test Signals
Probe in modes 0-4, EPP base alignment rejection in the core, sector read/write in EPP-16/32, connect/disconnect state restore, and default register echo validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/dstr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/epat.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/epat.c

## Purpose
Provides Shuttle EPAT/EPEZ parallel-port IDE protocol support, including optional EP1284 c7/c8 chip initialization for newer LS-120-class devices.

## Important APIs, Types, And Functions
`epat_read_regr()`, `epat_write_regr()`, `epat_read_block()`, and `epat_write_block()` implement six transfer modes. `epat_connect()` issues CPP command sequences and optionally programs c8 registers when `epatc8` is enabled. `epat_test_proto()` performs register and block scratch tests. `epat_log_adapter()` reads and reports the chip version. `epat_init()` defaults `epatc8` from `CONFIG_PATA_PARPORT_EPATC8`.

## Control Flow
Module init registers the `epat` protocol. Probe iterates modes, connect initializes the chip and requests EPP for modes 3-5, tests taskfile and block paths, and then runtime ATA operations use the selected mode callbacks.

## State And Persistence
`epatc8` is module/config state. `pi->saved_r0/saved_r2` preserve host port state; EPAT internal registers persist while connected.

## Dependencies And Integration Points
Depends on `pata_parport` core, module parameter handling, config option `PATA_PARPORT_EPATC8`, and EPP-capable parport IO for high modes.

## Risks And Edge Cases
The comment notes CPP handling is not fixed for multiple EPATs on a chain. c8 setup changes internal registers and must match hardware. Tail handling in EPP-16/32 block reads has special byte reads for the final bytes.

## Test Signals
EPAT and EP1284/c8 devices, all six modes, version logging, scratch block test failures, EPP alignment constraints, and module parameter/config combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/epat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/epia.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/epia.c

## Purpose
Implements the older Shuttle EPIA parallel-to-IDE adapter protocol, now superseded by EPAT but still supported for legacy devices.

## Important APIs, Types, And Functions
`epia_read_regr()` and `epia_write_regr()` encode command/control accesses with EPIA-specific cont maps. `epia_read_block()` and `epia_write_block()` provide nibble, 5/3, 8-bit, and EPP-style transfer modes. `epia_connect()`, `epia_disconnect()`, `epia_test_proto()`, and `epia_log_adapter()` initialize, validate, and report the adapter.

## Control Flow
The core probes supported modes using the protocol's test hook. Connect enters the adapter command state, test writes and reads taskfile registers and may validate block transfer behavior, then libata operations run through the selected callbacks.

## State And Persistence
Saved port registers and selected mode live in `pi_adapter`; EPIA adapter state persists only during connect.

## Dependencies And Integration Points
Uses the common `pata_parport` protocol ABI, direct port IO macros, and module-driver registration.

## Risks And Edge Cases
Obsolete hardware and overlapping Shuttle protocol families make false-positive tests a concern. EPP modes require correct base alignment and byte-count assumptions. Connect/disconnect must restore the parallel port for system stability.

## Test Signals
Legacy EPIA adapter probe, each mode's register echo path, block transfer tests, EPP mode constraints, and clean detach after ATA host removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/epia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/fit2.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/fit2.c

## Purpose
Supports the Fidelity International Technology TD-2000 simple parallel-port IDE adapter.

## Important APIs, Types, And Functions
`fit2_read_regr()` and `fit2_write_regr()` implement ATA taskfile access using a small strobe sequence. `fit2_read_block()` and `fit2_write_block()` transfer data in nibble-style form. `fit2_connect()`, `fit2_disconnect()`, and `fit2_log_adapter()` save/restore port state and describe the adapter. The `fit2` protocol exposes a low mode count and no EPP modes.

## Control Flow
Core probing uses the default register echo test. Runtime control flow is direct: taskfile operations call register callbacks, and PIO data phases call the block callbacks.

## State And Persistence
Only saved parallel-port register values and selected mode are stored in `pi_adapter`.

## Dependencies And Integration Points
Uses `pata_parport` core registration and low-level SPP port IO helpers.

## Risks And Edge Cases
This is intentionally low-speed and timing-sensitive. Lack of a custom probe hook means it relies on generic echo testing to avoid matching the wrong adapter.

## Test Signals
TD-2000 probe, mode selection, register echo, single-sector reads/writes, delay tuning, and detach state restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/fit2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/fit3.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/fit3.c

## Purpose
Implements the Fidelity International Technology TD-3000 protocol, a newer FIT parallel-port IDE adapter with more transfer modes than FIT2.

## Important APIs, Types, And Functions
`fit3_read_regr()` and `fit3_write_regr()` use data and extended port offset 7 helpers. `fit3_read_block()` and `fit3_write_block()` handle multiple modes, including faster paths. `fit3_connect()`, `fit3_disconnect()`, and `fit3_log_adapter()` handle port state and diagnostics. The `fit3` `pi_protocol` advertises its supported mode range.

## Control Flow
Probe chooses a mode with generic tests. Data and register paths branch on `pi->mode`, using nibble reconstruction for low modes and wider accesses for higher modes.

## State And Persistence
State is limited to saved port registers and the selected mode in `pi_adapter`; no private allocation is used.

## Dependencies And Integration Points
Depends on `pata_parport.h` direct IO macros and core module registration.

## Risks And Edge Cases
The protocol uses nonstandard port offset 7, so resource range assumptions must match the core's EPP/wide-mode validation. Mixed portable disk/CD devices can expose different timing tolerances.

## Test Signals
Mode probing across all supported modes, register echo, block read/write in low and high modes, invalid port-range rejection, and disconnect restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/fit3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/friq.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/friq.c

## Purpose
Supports Freecom IQ ASIC-2 parallel-port IDE adapters, including power-management commands for battery-powered external drives.

## Important APIs, Types, And Functions
`friq_read_regr()` and `friq_write_regr()` send encoded `CMD()` sequences for taskfile access. `friq_read_block_int()`, `friq_read_block()`, and `friq_write_block()` implement modes 0-4. `friq_test_proto()` powers the drive on and validates registers plus scratch data. `friq_log_adapter()` disables the sleep timer and marks power state in `pi->private`; `friq_release_proto()` powers the drive off.

## Control Flow
Probe turns power on, waits, tests register and block paths, and selects a working mode. Runtime connect/disconnect save/restore port state; release-time cleanup sends power-off commands if this protocol enabled power.

## State And Persistence
`pi->private` tracks whether the protocol powered the device and should power it down. Saved port state persists across connect/disconnect.

## Dependencies And Integration Points
Integrates with `pata_parport` release hooks and raw parport IO; the core calls `release_proto()` from device teardown.

## Risks And Edge Cases
Built-in use may keep devices powered indefinitely, as noted in the file header. Power sequencing delays are hardware-sensitive. Final-byte handling differs by mode and must avoid over-reading.

## Test Signals
Power-on probe, sleep-timer disable, release power-off, register echo, block scratch test, all modes, and module built-in versus module unload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/friq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/frpw.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/frpw.c

## Purpose
Implements the Freecom Power parallel-port IDE protocol, including detection of Xilinx versus ASIC adapter implementations.

## Important APIs, Types, And Functions
`frpw_read_regr()` and `frpw_write_regr()` use the `cec4` strobe sequence. `frpw_read_block_int()`, `frpw_read_block()`, and `frpw_write_block()` implement modes 0-5. `frpw_test_pnp()` detects chip type; `frpw_test_proto()` filters unsupported mode/chip combinations and runs scratch tests. `frpw_log_adapter()` reports chip type and mode.

## Control Flow
Probe first determines chip type and caches it in `pi->private`, then rejects EPP modes unsupported by the detected implementation. Successful modes are validated with ATA register echo and scratch block reads before normal libata traffic uses the callbacks.

## State And Persistence
`pi->private` stores `port * 2 + chip_type` so chip detection is not repeated unnecessarily. Saved port registers are restored on disconnect.

## Dependencies And Integration Points
Uses the `pata_parport` test hook, module registration, and direct parallel-port IO macros. Optional `FRPW_HARD_RESET` is compile-time-only and not normally enabled.

## Risks And Edge Cases
Hard reset can disturb devices on other ports if enabled. Chip-type caching depends on the port number. Xilinx and ASIC mode restrictions are easy to regress because they share most callbacks.

## Test Signals
Xilinx and ASIC adapters, rejected unsupported modes, PNP detection, register and scratch block tests, delay override, and disconnect restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/frpw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/kbic.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/kbic.c

## Purpose
Supports KingByte KBIC-951A and KBIC-971A parallel-to-IDE adapter chips, registering separate protocols because the 971A wakeup sequence can break 951A behavior.

## Important APIs, Types, And Functions
Shared helpers `kbic_read_regr()`, `kbic_write_regr()`, `kbic_read_block()`, and `kbic_write_block()` implement register and data transfers across multiple modes. Protocol-specific connect/test/log routines distinguish 951A and 971A behavior, including the 971A wakeup handling. Two `pi_protocol` instances expose the related adapters.

## Control Flow
Each protocol registers separately. The core probes both as configured, runs protocol tests, and selects a working transfer mode. Runtime callbacks branch on `pi->mode` and use SPP/EPP port sequences as needed.

## State And Persistence
Saved port state lives in `pi_adapter`; protocol-specific detection or wake state may use `pi->private`. Hardware remains selected only while connected.

## Dependencies And Integration Points
Depends on `pata_parport` registration/exported callbacks and raw IO helpers, including word reads from `pi->port + 1` for 5/3 style mode.

## Risks And Edge Cases
Registering related protocols increases false-positive risk. The 971A wakeup code must not run against 951A hardware. Wider transfer modes depend on port resource alignment.

## Test Signals
Separate 951A and 971A detection, wakeup path, all transfer modes, register echo, sector reads/writes, and loading both protocols together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/kbic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/ktti.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/ktti.c

## Purpose
Implements the KT Technology PHd simple parallel-port IDE protocol.

## Important APIs, Types, And Functions
`ktti_read_regr()` and `ktti_write_regr()` implement taskfile access; `ktti_read_block()` and `ktti_write_block()` handle data transfer; `ktti_connect()`, `ktti_disconnect()`, and `ktti_log_adapter()` provide core lifecycle hooks. The `ktti` `pi_protocol` is small, low-speed, and single-unit.

## Control Flow
The `pata_parport` core probes with generic tests, records a mode, keeps the parport claimed, and calls the protocol callbacks for all ATA register and data operations.

## State And Persistence
Only saved parallel-port data/control register values and the selected mode are stored in `pi_adapter`; no additional allocation or persistent media state exists.

## Dependencies And Integration Points
Uses the core `pi_protocol` ABI, direct port IO macros, and `module_pata_parport_driver()`.

## Risks And Edge Cases
As a simple low-speed adapter, it is sensitive to delay settings and generic false-positive probing. It lacks custom unit or protocol tests.

## Test Signals
PHd adapter probe, mode selection, register echo, read/write sectors, user-specified delay through `new_device`, and removal via `delete_device`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/ktti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/on20.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/on20.c

## Purpose
Supports the obsolete OnSpec 90c20 parallel-port IDE protocol.

## Important APIs, Types, And Functions
Macros encode OnSpec operation and value strobes. `on20_read_regr()` and `on20_write_regr()` provide ATA register access, while `on20_read_block()` and `on20_write_block()` provide data transfer. `on20_connect()`, `on20_disconnect()`, and `on20_log_adapter()` implement lifecycle and diagnostics.

## Control Flow
Core probing uses the protocol's callback table and selected mode. Runtime ATA taskfile commands are encoded through OnSpec strobes; PIO data paths reconstruct bytes with nibble-combine logic.

## State And Persistence
Saved port registers and selected transfer mode are the only software state. Adapter selection persists while connected by the core.

## Dependencies And Integration Points
Depends on `pata_parport` core and direct SPP port IO.

## Risks And Edge Cases
The hardware is obsolete and likely timing-sensitive. Low-level macros make command ordering hard to audit. Generic probing must distinguish it from similar low-speed adapters.

## Test Signals
90c20 adapter detection, register echo, block reads/writes, delay tuning, disconnect restore, and failure behavior when no device is attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/on20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/on26.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/on26.c

## Purpose
Implements the OnSpec 90c26 parallel-port IDE protocol, a later OnSpec adapter with more modes and internal register handling.

## Important APIs, Types, And Functions
`on26_read_regr()` and `on26_write_regr()` perform taskfile access. `on26_read_block()` and `on26_write_block()` implement block transfers across low and EPP-style modes. `on26_test_port()`, `on26_probe_unit()`, `on26_test_proto()`, `on26_connect()`, `on26_disconnect()`, and `on26_log_adapter()` support detection and diagnostics.

## Control Flow
Probe may test port capabilities and unit presence before mode selection. After a successful protocol test, the core uses register and block callbacks for libata SFF command execution.

## State And Persistence
Selected unit/mode and saved port values live in `pi_adapter`. Any internal OnSpec register state persists only for the connected session.

## Dependencies And Integration Points
Uses `pata_parport` protocol hooks and direct parallel-port IO, including wider EPP-style accesses for high modes.

## Risks And Edge Cases
Unit probing and mode testing are hardware-specific; false positives can corrupt connected devices. EPP modes require aligned base ports and correct resource range.

## Test Signals
90c26 unit probe, all supported modes, custom protocol test failure paths, register echo, block transfer integrity, and detach cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/on26.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/pata_parport.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/pata_parport.c

## Purpose
Provides the core libata bridge for parallel-port ATA adapters. It owns the `pata_parport` bus, parport discovery, protocol registration, sysfs manual device creation/removal, and ATA SFF operations backed by protocol callbacks.

## Important APIs, Types, And Functions
ATA operations include `pata_parport_dev_select()`, `pata_parport_set_devctl()`, `pata_parport_softreset()`, `pata_parport_tf_load()`, `pata_parport_tf_read()`, `pata_parport_exec_command()`, `pata_parport_data_xfer()`, and `pata_parport_drain_fifo()`. Discovery and lifecycle are handled by `pi_init_one()`, `pi_probe_unit()`, `pi_probe_mode()`, `pi_test_proto()`, `pata_parport_register_driver()`, `pata_parport_unregister_driver()`, `pata_parport_attach()`, `pata_parport_detach()`, `new_device_store()`, and `delete_device_store()`.

## Control Flow
Module init registers a bus, root device, sysfs attributes, and a parport driver. Parport attach records ports in an IDR and optionally probes every registered protocol. Protocol registration records the protocol and optionally probes every known parport. Successful `pi_init_one()` registers a child device, gets a protocol module ref, registers a parport device, probes unit/mode, allocates one ATA host, claims the parport, connects the protocol, and activates a polling SFF ATA host.

## State And Persistence
Global state uses `parport_list`, `protocols`, `pata_parport_bus_dev_ids`, `pata_parport_bus`, and `pi_mutex`. Each `pi_adapter` stores device identity, protocol pointer, port/mode/delay/unit, saved port registers, private protocol data, and `pardev`. The parport is intentionally claimed for the entire ATA host lifetime.

## Dependencies And Integration Points
Integrates libata SFF PIO polling, Linux parport, driver core buses/devices, sysfs bus attributes, IDR/IDA allocation, module refcounting, and protocol modules via exported GPL symbols.

## Risks And Edge Cases
Holding the parport prevents chained devices and printers from sharing it. Device/protocol enumeration is serialized by `pi_mutex`, but removal paths must balance ATA detach, disconnect, parport unregister, module refs, and device refs. Manual `new_device` parsing can scan many combinations. Softreset handles ghosty master/slave behavior where adapters return bogus values.

## Test Signals
Automatic probe on protocol load and parport attach, `probe=0`, sysfs `new_device` and `delete_device`, duplicate protocol/port rejection, master/slave reset, DRQ drain, module unload with active devices, and parport detach while devices exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/pata_parport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/pata_parport.h -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/pata_parport.h

## Purpose
Defines the private ABI between the `pata_parport` core and individual parallel-port IDE protocol modules.

## Important APIs, Types, And Functions
`struct pi_adapter` stores per-adapter device state, selected protocol, I/O base, mode, delay, unit, saved register values, protocol-private storage, and parport device pointer. `struct pi_protocol` defines callbacks for register access, block transfer, connect/disconnect, tests, logging, optional init/release, module owner, driver object, and SCSI template. Macros `w0/r0` through `w4l/r4l` wrap port IO with optional delay. `module_pata_parport_driver()` registers a protocol with the core.

## Control Flow
The header has no runtime control flow but dictates callback order used by the core: optional init, probe/test, connect, read/write register and block operations, disconnect, optional release, and unregister.

## State And Persistence
The state contract is explicit in `pi_adapter`; protocol modules may use `private` for small cached values but the core owns allocation and release.

## Dependencies And Integration Points
Includes libata and exports prototypes for `pata_parport_register_driver()` and `pata_parport_unregister_driver()`.

## Risks And Edge Cases
Callbacks are synchronous and called while the parport may be claimed. Protocols must preserve saved registers and respect delay. Raw port macros assume valid I/O ranges and architecture support for in/out instructions.

## Test Signals
Build all protocol modules, modpost exported symbol resolution, protocol registration/unregistration, delay behavior, and static checking of callback table completeness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_parport/pata_parport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_pcmcia.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_pcmcia.c

## Purpose
Provides a libata driver for PCMCIA ATA/ATAPI cards and adapters, including many legacy product IDs and an 8-bit emulated transfer quirk.

## Important APIs, Types, And Functions
`pcmcia_set_mode()` detects ghost slave devices by comparing IDENTIFY strings. `pcmcia_set_mode_8bit()`, `ata_data_xfer_8bit()`, and `pcmcia_8bit_drain_fifo()` support TI-style 8-bit emulation. `pcmcia_check_one_config()` validates/request IO windows. `pcmcia_init_one()` enables the card, maps IO/control windows, creates one or two ATA ports, and activates the host. `pcmcia_remove_one()` detaches and disables the card.

## Control Flow
PCMCIA probe configures resource flags, applies KME quirks, loops possible CIS configurations, enables the device, maps IO ports, optionally chooses 8-bit ops, allocates an ATA host for one or two ports, fills standard SFF addresses, and activates shared-IRQ PIO operation. Remove detaches the host and disables the PCMCIA device.

## State And Persistence
`pdev->priv` stores the ATA host. PCMCIA resource settings and enabled-device state persist until removal. No separate driver-private allocation is used.

## Dependencies And Integration Points
Uses PCMCIA CIS/config APIs, libata SFF PIO, product/manufacturer ID tables, devm IO port mapping, and standard SCSI host templates.

## Risks And Edge Cases
Ghost master/slave detection may disable a real identical device if serial data is misleading. Some cards need fallback without VCC checking. Two-port support is inferred from IO window size. 8-bit data transfer and FIFO drain paths differ from normal SFF behavior.

## Test Signals
Known PCMCIA IDs, config fallback, KME control quirk, TI 8-bit card path, ghost slave suppression, one-port and two-port windows, card removal while mounted, and shared IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_pcmcia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_pdc2027x.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_pdc2027x.c

## Purpose
Supports Promise PDC20268 through PDC20277 PATA controllers, including PATA100/PATA133 variants, MMIO taskfile windows, PLL detection/adjustment, and 133 MHz timing table overrides.

## Important APIs, Types, And Functions
Helpers `port_mmio()` and `dev_mmio()` compute register windows. `pdc2027x_cable_detect()`, `pdc2027x_prereset()`, `pdc2027x_mode_filter()`, `pdc2027x_set_piomode()`, `pdc2027x_set_dmamode()`, `pdc2027x_set_mode()`, and `pdc2027x_check_atapi_dma()` implement libata policy. `pdc_read_counter()`, `pdc_detect_pll_input_clock()`, `pdc_adjust_pll()`, and `pdc_hardware_init()` calibrate hardware. `pdc_ata_setup_port()` maps MMIO ATA registers.

## Control Flow
PCI probe allocates a two-port host, enables the device, maps BAR5, sets DMA mask, assigns MMIO command/BMDMA addresses, initializes PLL hardware, enables bus mastering, and activates BMDMA interrupts. For PATA133 variants, libata mode setting is followed by explicit timing table writes because hardware SET FEATURES timing may be wrong at 133 MHz.

## State And Persistence
Controller state persists in MMIO timing/control/PLL registers. No private host data is allocated; `host->iomap` is the key runtime mapping.

## Dependencies And Integration Points
Uses PCI managed resources, libata BMDMA, SCSI command opcodes for ATAPI DMA whitelisting, ktime for PLL measurement, and PM resume reinitialization.

## Risks And Edge Cases
PLL input measurement reads a split decrementing counter and must retry around rollover. The mode filter contains a suspicious Maxtor-related UDMA6 workaround that affects slave devices. ATAPI DMA is whitelisted to avoid lost IRQs. Firmware-disabled ports return `-ENOENT`.

## Test Signals
PDC20268/69/70/71/75/76/77 IDs, 40/80-wire detection, PLL clock on nonstandard PCI clocks, PIO/MDMA/UDMA timing writes, ATAPI DMA whitelist, suspend/resume reinit, and disabled-port handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_pdc2027x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_pdc202xx_old.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_pdc202xx_old.c

## Purpose
Supports older Promise PDC20246 and PDC20262/263/265/267 controllers with PCI-config timing, BMDMA quirks, cable detection, and clock switching for high UDMA modes.

## Important APIs, Types, And Functions
`pdc2026x_cable_detect()` reads cable state from PCI config. `pdc202xx_exec_command()` adds a 400 ns command delay. `pdc202xx_irq_check()` reads Promise interrupt bits. `pdc202xx_set_piomode()` and `pdc202xx_set_dmamode()` program timing. `pdc2026x_bmdma_start()` and `pdc2026x_bmdma_stop()` handle clock switching and ATAPI/LBA48 length registers. `pdc2026x_dev_config()` limits sectors, and `pdc2026x_port_start()` enables burst mode.

## Control Flow
PCI probe selects one of three port-info profiles by device ID and avoids claiming PDC20265 behind Promise I2O RAID bridges. Normal command flow follows libata BMDMA, with PDC2026x start/stop wrapping DMA to adjust clocks and state-machine helper registers.

## State And Persistence
State lives in PCI config timing registers, BMDMA registers, clock selection bits, and ATAPI/LBA48 byte-count helper registers. No heap private data is used.

## Dependencies And Integration Points
Uses libata BMDMA/SFF, PCI config and I/O resources, Promise PCI IDs, and generic PCI PM helpers.

## Risks And Edge Cases
Timing registers are shared between PIO and DMA programming. ATAPI DMA is disabled on old Promise. LBA48/ATAPI DMA needs special byte-count setup or the state machine may not complete. Clock bits are shared across channels and rely on host-level locking.

## Test Signals
All supported PCI IDs, I2O RAID exclusion, UDMA2/4/5 profiles, clock switch on UDMA3+, ATAPI DMA rejection, LBA48 DMA, cable detection, burst-mode enable, and interrupt status bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_pdc202xx_old.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_piccolo.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_piccolo.c

## Purpose
Adds Toshiba Piccolo ATA controller support as a small PCI BMDMA libata driver with Toshiba-specific timing tables.

## Important APIs, Types, And Functions
`tosh_set_piomode()` programs PIO timing in PCI config word `0x50`. `tosh_set_dmamode()` programs MWDMA/UDMA timing in config dword `0x5C`. `ata_tosh_init_one()` registers a one-port host, using a dummy second port entry.

## Control Flow
The PCI driver matches Toshiba Piccolo device IDs, constructs a single active ATA port profile with PIO5/MWDMA2/UDMA2 masks, and lets generic PCI BMDMA setup handle resource mapping and activation. Mode changes write the appropriate timing table values.

## State And Persistence
Only PCI config timing state is persisted by the driver. There is no private data allocation.

## Dependencies And Integration Points
Uses libata BMDMA port operations, Toshiba PCI IDs, and generic PCI suspend/resume helpers.

## Risks And Edge Cases
The driver intentionally claims only one port. Timing data comes from external documentation and masks off preserved bits, so register layout mistakes would corrupt unrelated config bits. Cable type is unknown.

## Test Signals
Each Piccolo PCI ID, single-port enumeration, PIO0-5 timing writes, MWDMA and UDMA timing writes, suspend/resume, and dummy second-port non-enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_piccolo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_platform.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_platform.c

## Purpose
Implements the generic platform-device PATA helper and driver for simple PIO ATA interfaces described by platform resources.

## Important APIs, Types, And Functions
`pata_platform_set_mode()` forces enabled devices to PIO0 without hardware reprogramming. `pata_platform_setup_port()` expands taskfile addresses from a command base plus shift. `__pata_platform_probe()` is exported for platform and OF wrappers; it maps IO or MMIO resources, creates per-device port ops, configures PIO polling when no IRQ exists, and activates the host. `pata_platform_probe()` validates resources and calls the helper.

## Control Flow
Probe requires command and control resources plus optional IRQ, determines IO versus MMIO, allocates one ATA host, creates a devm `ata_port_operations` inheriting SFF ops, selects 16- or 32-bit data transfer behavior, maps resources, computes register addresses, and activates with either `ata_sff_interrupt` or polling.

## State And Persistence
Device-managed mappings and per-device operations persist for the platform device lifetime. The module parameter `pio_mask` controls supported PIO modes for non-OF platform devices.

## Dependencies And Integration Points
Exports `__pata_platform_probe()` for `pata_of_platform.c`, uses platform resources, libata SFF, `ata_platform_remove_one`, and `pata_platform_info` platform data.

## Risks And Edge Cases
The helper assumes both command and control resources are both IO or both MEM. It never programs hardware timing, so firmware/platform setup must be correct. No IRQ means polling. `use16bit=false` selects 32-bit data transfer, which must match wiring.

## Test Signals
IO and MMIO resources, two-resource and three-resource devices, no-IRQ polling, IRQ trigger flags, shifted registers, platform `pio_mask`, 16-bit wrapper use, and mapping failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_pxa.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_pxa.c

## Purpose
Provides a DMA-capable platform PATA driver for PXA systems using the DMAengine slave API.

## Important APIs, Types, And Functions
`struct pata_pxa_data` stores DMA channel, cookie, and completion. `pxa_qc_prep()` prepares slave SG descriptors and callback. `pxa_bmdma_setup()`, `pxa_bmdma_start()`, `pxa_bmdma_stop()`, and `pxa_bmdma_status()` adapt libata BMDMA hooks to DMAengine. `pxa_ata_probe()` maps resources, configures DMA, and activates the ATA host; `pxa_ata_remove()` releases DMA and detaches.

## Control Flow
Probe validates four resources, maps command/control/DMA windows, derives taskfile addresses from platform `reg_shift`, requests DMA channel `data`, configures 16-bit bus widths and burst size, then activates SFF interrupts. For DMA commands, libata maps SG, `qc_prep` submits descriptors, setup issues the ATA command, start kicks DMAengine, stop waits for completion or error and terminates the channel.

## State And Persistence
Per-port state is `struct pata_pxa_data` in `ap->private_data`. DMA cookies and completions track the active transfer. Mapped register windows and DMA channel persist until remove.

## Dependencies And Integration Points
Depends on platform data `ata-pxa.h`, DMAengine, libata BMDMA/SFF, platform IRQ flags, and devm mappings.

## Risks And Edge Cases
`pxa_qc_prep()` logs descriptor-prep failure but returns `AC_ERR_OK`, which may let later stages see missing DMA setup. ATAPI DMA is unsupported. Probe assumes non-null platform data for `reg_shift` and `irq_flags`. Error after DMA config does not release the channel in all early return paths.

## Test Signals
PIO and MWDMA transfers, DMAengine callback completion, DMA error status, timeout path, ATAPI DMA rejection, missing resources, absent DMA channel, remove after active host, and platform-data validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_pxa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_radisys.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_radisys.c

## Purpose
Supports Radisys R82600 PATA controllers, a PIIX-like single-channel controller with shared PIO/MWDMA timing and limited UDMA switching.

## Important APIs, Types, And Functions
`radisys_set_piomode()` programs PCI config word `0x40` for PIO timing. `radisys_set_dmamode()` handles MWDMA-derived PIO timing and UDMA enable/mode bits. `radisys_qc_issue()` reloads shared timing when issuing to a different device. `radisys_init_one()` registers the BMDMA host.

## Control Flow
Probe creates a single-port BMDMA host. Mode setup writes timing registers and stores the currently programmed device in `ap->private_data`. Command issue reloads timing for PIO/MWDMA or non-DMA cases when switching devices, then delegates to `ata_bmdma_qc_issue()`.

## State And Persistence
State is PCI config timing/UDMA bits plus `ap->private_data` as the current timing owner. No heap private data is used.

## Dependencies And Integration Points
Uses libata BMDMA ops, PCI config access, Radisys PCI IDs, and standard PCI PM helpers.

## Risks And Edge Cases
Shared non-UDMA timing creates the same mixed-device risk as early PIIX. The code treats UDMA timing as not shared, so command issue skips reload for UDMA-capable paths. Cable type is unknown.

## Test Signals
PIO and MWDMA timing, UDMA2/4 selection, alternating master/slave command issue, ATA-only and ATAPI devices, suspend/resume, and R82600 PCI matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_radisys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_rb532_cf.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_rb532_cf.c

## Purpose
Implements CompactFlash PATA support for MikroTik RouterBOARD 532 boards using platform resources and a GPIO/IRQ handshake.

## Important APIs, Types, And Functions
`struct rb532_cf_info` stores IRQ, GPIO descriptor, and mapped base. `rb532_pata_irq_handler()` acknowledges board-specific CF IRQ state before returning libata interrupt status. `rb532_pata_setup_ports()` fills ATA SFF register addresses at fixed RB500 offsets. `rb532_pata_driver_probe()` maps resources, requests GPIO/IRQ data, allocates the ATA host, and activates it. `rb532_pata_driver_remove()` detaches the host.

## Control Flow
Probe obtains memory resources and IRQ, maps the CF window, configures one SFF PIO port, records private info, and activates with a custom IRQ handler. The handler filters/acknowledges the hardware interrupt and then lets libata process the ATA interrupt.

## State And Persistence
Per-device state lives in `struct rb532_cf_info` and the mapped CF register window. Hardware IRQ/GPIO state persists across commands and is reset/acknowledged by the handler.

## Dependencies And Integration Points
Depends on platform bus, GPIO consumer API, RB532 board definitions, libata SFF PIO, and SCSI host registration.

## Risks And Edge Cases
The driver is board-specific and uses fixed register offsets. IRQ acknowledgement must match the board latch or interrupts can be lost or storm. It supports one port and PIO-only behavior.

## Test Signals
RouterBOARD 532 probe, register mapping, GPIO presence, IRQ delivery/ack, PIO identify/read/write, remove cleanup, and interrupt storm/lost-interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_rb532_cf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_rdc.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_rdc.c

## Purpose
Supports later RDC PATA controllers conforming to ATA host adapter standards, with cable detection, port enable checks, timing programming, and IOCFG restoration.

## Important APIs, Types, And Functions
`struct rdc_host_priv` saves IOCFG. `rdc_pata_cable_detect()` decodes saved cable bits. `rdc_pata_prereset()` checks PCI enable bits. `rdc_set_piomode()` and `rdc_set_dmamode()` program PIO, MWDMA, and UDMA timing under `rdc_lock`. `rdc_init_one()` prepares a two-port BMDMA32 host; `rdc_remove_one()` restores saved IOCFG before generic removal.

## Control Flow
Probe enables the PCI device, saves config dword `0x54`, prepares two libata ports, enables INTx, marks parallel scan, and activates BMDMA interrupts. Mode setup uses a global spinlock because timing and UDMA registers contain fields for multiple ports/devices.

## State And Persistence
Saved IOCFG persists in `host->private_data` for cable detect and detach restore. Hardware state persists in PCI timing/UDMA registers. No per-command state is cached.

## Dependencies And Integration Points
Uses libata BMDMA32 operations, PCI managed setup, DMI headers, PCI config bit helpers, and generic PM hooks.

## Risks And Edge Cases
Multi-field PCI config updates require locking to avoid cross-port corruption. IOCFG must be restored on remove. Cable detection trusts firmware-saved bits. MWDMA uses PIO-derived timing and may force DMA-only behavior when device PIO capability is slower.

## Test Signals
Both RDC PCI IDs, 40/80-wire cable detect, disabled port prereset, PIO/MWDMA/UDMA mode programming, concurrent two-port mode changes, remove restoring IOCFG, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_rdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_rz1000.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_rz1000.c

## Purpose
Supports RZ1000/RZ1001 PCI ATA controllers while disabling their unsafe FIFO behavior and forcing PIO operation.

## Important APIs, Types, And Functions
`rz1000_set_mode()` configures enabled devices for PIO0 only. `rz1000_fifo_disable()` clears FIFO enable bits in PCI config and verifies the result. `rz1000_init_one()` disables FIFO before registering the host. `rz1000_reinit_one()` repeats FIFO disable on resume before resuming libata.

## Control Flow
PCI probe first calls `rz1000_fifo_disable()`; if FIFO cannot be disabled, probe fails. It then registers a PIO-only SFF host. Resume repeats device resume, FIFO disable, and `ata_host_resume()`.

## State And Persistence
State persists in PCI config register `0x40` FIFO bits and libata device mode flags. No driver-private allocation exists.

## Dependencies And Integration Points
Uses PCI config access, libata SFF PIO, generic PCI PM helpers, and RZ1000/RZ1001 PCI IDs.

## Risks And Edge Cases
The FIFO is the main data-corruption risk; failure to disable it must prevent use. The driver deliberately limits modes to PIO0, trading performance for safety. Resume must reapply FIFO disable because firmware or power state can restore defaults.

## Test Signals
Probe with FIFO disable success/failure, PIO-only mode assignment, RZ1000 and RZ1001 IDs, suspend/resume re-disable, and data integrity tests under repeated reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_rz1000.c -->
