# Research Report: subset-b-005018

This grouped report covers the requested PCMCIA/CardBus socket, resource-management, SoC glue, vendor bridge tuning, and PECI controller files. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pd6729.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/pd6729.c

Purpose: Implements the Cirrus PD6729 PCI-to-PCMCIA bridge driver. It exposes two 16-bit PC Card sockets to the PCMCIA core, using indirect ExCA/I82365-style register access over the controller I/O BAR.

Important APIs and functions: The module registers `pd6729_pci_driver`. `pd6729_pci_probe()` allocates two `pd6729_socket` objects, enables the PCI function, requests the I/O region, chooses PCI or ISA/polling interrupt mode, fills `struct pcmcia_socket`, and registers each socket. `pd6729_pci_remove()` unregisters sockets and tears down IRQ/timer and PCI resources. The `pccard_operations` implementation is `pd6729_init()`, `pd6729_get_status()`, `pd6729_set_socket()`, `pd6729_set_io_map()`, and `pd6729_set_mem_map()`.

Control flow: Register access goes through `indirect_read*()` and `indirect_write*()` protected by the global `port_lock`, adding `socket->number * 0x40` to select socket-local ExCA registers. Interrupts enter `pd6729_interrupt()`, which loops over both sockets, reads and clears `I365_CSC`, translates detect/ready/battery/status-change bits, and calls `pcmcia_parse_events()`. Without PCI IRQs, `pd6729_interrupt_wrapper()` polls once per second.

State and persistence: Runtime state is the per-socket number, `card_irq`, I/O base, PCMCIA socket object, and optional poll timer. Socket power, Vcc/Vpp, reset, interrupt masks, and I/O/memory windows persist in bridge registers until reprogrammed or removed.

Dependencies and integration points: Depends on Linux PCI/module/IRQ APIs, PCMCIA socket services, `pccard_nonstatic_ops`, `i82365.h`, `cirrus.h`, and `pd6729.h`. It integrates through `pcmcia_register_socket()` and PCMCIA core map/socket callbacks.

Risks: Indirect register access is shared between sockets, so locking is critical. PCI IRQ mode uses hard-coded PD67 interrupt routing values; ISA mode depends on probing a legacy IRQ mask and otherwise falls back to polling for status changes. Voltage programming uses PD67 3.3V selection plus I365 power bits, so wrong `state->Vcc` handling can damage cards or leave sockets unpowered. Memory map programming must fit 24-bit/page constraints and only rejects speeds above 1000 ns.

Test signals: Build with PD6729 support, PCI match on Cirrus 6729, two socket registrations, card insertion/removal events, status polling when `irq_mode=0`, Vcc/Vpp transitions, I/O and memory window setup for 16-bit cards, and clean remove without timer/IRQ use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pd6729.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pd6729.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/pd6729.h

Purpose: Provides the private Cirrus PD6729 socket state and register constants used by `pd6729.c`.

Important APIs and types: Defines PD6729/Cirrus-specific bits `I365_DF_VS1`, `I365_DF_VS2`, `PD67_EXD_VS1(s)`, `PD67_EXD_VS2(s)`, and the default ISA IRQ mask `PD67_MASK`. `struct pd6729_socket` stores the socket index, selected card IRQ, controller I/O base, embedded `struct pcmcia_socket`, and polling timer.

Control flow: No executable logic exists. The macros are used by `pd6729_get_status()` for voltage-sense decoding and by `pd6729_isa_scan()` for legacy IRQ probing.

State and persistence: The struct is the driver's per-socket runtime state. The embedded PCMCIA socket persists for the socket lifetime and carries PCMCIA core-visible state; the timer exists only in ISA/polling mode.

Dependencies and integration points: Requires PCMCIA socket definitions before use. It is private to the PD6729 driver and mirrors the controller's two-socket register layout.

Risks: The `PD67_EXD_VS*` macros assume socket numbering compatible with the external-data register layout. Any mismatch would misreport voltage capability. The IRQ mask selects legacy lines 3,4,5,7,9,10,11 and is intentionally conservative but platform-sensitive.

Test signals: Compile coverage of `pd6729.c`, voltage status bits reported correctly for 3.3V cards, and successful ISA IRQ scan/poll fallback validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pd6729.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pxa2xx_base.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/pxa2xx_base.c

Purpose: Implements the common PXA2xx PCMCIA socket controller platform driver. It translates PCMCIA timing requests into PXA static-memory-controller timing values and registers sockets through the shared SoC PCMCIA layer.

Important APIs and functions: Exports `pxa2xx_configure_sockets()`, `pxa2xx_drv_pcmcia_add_one()`, and `pxa2xx_drv_pcmcia_ops()`. Internal timing helpers compute setup, assertion, and hold fields (`pxa2xx_mcxx_setup()`, `pxa2xx_mcxx_asst()`, `pxa2xx_mcxx_hold()`) and write them through `pxa_smemc_set_pcmcia_timing()`. `pxa2xx_drv_pcmcia_probe()` and remove/resume callbacks implement the platform driver.

Control flow: Probe reads platform `struct pcmcia_low_level`, rejects unsupported multi-slot PXA320 setups, obtains the memory-controller clock, installs PXA timing callbacks into low-level ops, allocates a flexible `skt_dev_info`, initializes each `soc_pcmcia_socket`, and calls `pxa2xx_drv_pcmcia_add_one()`. After socket registration it invokes `pxa2xx_configure_sockets()`. CPU-frequency transitions pre-update timing when frequency rises and post-update timing when it falls.

State and persistence: Per-socket resources are physical PXA PCMCIA partitions for I/O, memory, and attribute space. Timing values persist in SMEMC registers until frequency changes, resume, or later map operations.

Dependencies and integration points: Uses PXA SoC helpers (`cpu_is_pxa320()`, `pxa_smemc_set_pcmcia_socket()`, `pxa_smemc_set_pcmcia_timing()`), common SoC PCMCIA (`soc_common.h`), Linux platform/clock/cpufreq APIs, and board-specific low-level ops passed through platform data.

Risks: Timing math is integer-rounded and depends on clock rate in 10 kHz units; low clock or extreme access values can underflow helper return values. Platform data is mandatory. Resource ranges are hard-coded PXA physical layout, so this driver is tightly architecture-specific.

Test signals: Platform device probe, socket registration, card insertion on each supported slot, I/O/attribute/common-memory access, CPU-frequency transitions with stable card traffic, PXA320 one-slot rejection, and resume reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pxa2xx_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pxa2xx_base.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/pxa2xx_base.h

Purpose: Declares the public PXA2xx PCMCIA glue functions shared between board-specific socket code and the PXA2xx base driver.

Important APIs and types: Declares `pxa2xx_drv_pcmcia_add_one()`, `pxa2xx_drv_pcmcia_ops()`, and `pxa2xx_configure_sockets()`.

Control flow: No direct logic. Board/platform glue calls these functions to install PXA timing callbacks, configure the PXA socket controller, and register one `soc_pcmcia_socket`.

State and persistence: No state is stored here. The prototypes operate on `struct soc_pcmcia_socket`, `struct pcmcia_low_level`, and `struct device`, with state maintained by `soc_common.c` and `pxa2xx_base.c`.

Dependencies and integration points: This header is coupled to `soc_common.h` definitions and the PXA platform driver. It is consumed by `pxa2xx_base.c` and board files such as `pxa2xx_sharpsl.c`.

Risks: Signature changes must be synchronized with all board-specific users. Since platform data low-level ops are mutated by `pxa2xx_drv_pcmcia_ops()`, callers must provide mutable ops storage.

Test signals: Compile/link coverage for PXA2xx PCMCIA and successful board driver probe using these exported functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pxa2xx_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pxa2xx_sharpsl.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/pxa2xx_sharpsl.c

Purpose: Provides Sharp SL-C7xx/Zaurus board-specific PCMCIA/CF control using SCOOP companion-chip registers. It supplies low-level socket operations for the generic PXA2xx PCMCIA driver, with an alternate Collie path using SA11xx base glue.

Important APIs and functions: Key callbacks are `sharpsl_pcmcia_hw_init()`, `sharpsl_pcmcia_socket_state()`, `sharpsl_pcmcia_configure_socket()`, `sharpsl_pcmcia_socket_init()`, and `sharpsl_pcmcia_socket_suspend()`. `sharpsl_pcmcia_init()` creates a `pxa2xx-pcmcia` platform device carrying `sharpsl_pcmcia_ops`; under `CONFIG_SA1100_COLLIE`, `pcmcia_collie_init()` calls `sa11xx_drv_pcmcia_probe()`.

Control flow: Init verifies `platform_scoop_config`, sets the socket count from its SCOOP device array, allocates a platform device, attaches low-level ops as platform data, sets the parent device, and adds it. Socket state reads SCOOP CPR/CSR, manages CDR and saved voltage-sense bits, then fills PCMCIA state flags. Configure validates Vcc/Vpp, computes new SCOOP MCR/CPR/CCR/IMR values, applies machine-specific power-bit differences for Spitz/Borzoi/Akita, and writes changed registers under local IRQ disable.

State and persistence: Persistent board state lives in SCOOP registers and per-SCOOP `keep_vs`/`keep_rd` fields used to preserve voltage-sense/reset behavior across power/card-detect transitions. The platform device persists until module exit.

Dependencies and integration points: Depends on Sharp SCOOP platform data, `machine_is_*()` board checks, `pxa2xx_base` or `sa11xx_base`, and common SoC PCMCIA callbacks.

Risks: Power controls are shared and board-specific, so incorrect socket index handling can affect the wrong slot. The code accepts 3.3V/5V Vcc but rejects independent Vpp; CF cards needing other Vpp modes are unsupported. IRQ masking is derived from current `skt->status`, so stale status could change event enables.

Test signals: Probe on supported Zaurus boards, correct socket count, card detect/eject, 3.3V and 5V power paths, reset sequencing, suspend powerdown, and Collie-specific SA11xx registration when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pxa2xx_sharpsl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/ricoh.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/ricoh.h

Purpose: Defines Ricoh RF5C/RL5C CardBus bridge registers and Yenta override helpers for Ricoh-specific initialization, suspend/resume save/restore, CLKRUN handling, and Zoom Video enablement.

Important APIs and functions: Under `__YENTA_H`, it provides `ricoh_zoom_video()`, `ricoh_set_zv()`, `ricoh_set_clkrun()`, `ricoh_save_state()`, `ricoh_restore_state()`, and `ricoh_override()`. It also defines register offsets and bit masks for mode, power, bridge config, misc control, 16-bit timing, ZV, and CLKRUN.

Control flow: `ricoh_override()` reads and updates 16-bit timing/config registers, enabling prefetch on newer bridges or level timing on older ones, installs the ZV callback for RL5C478, and optionally disables CLKRUN. Save/restore copy five vendor registers into `yenta_socket.private[]`; restore rewrites them and reapplies CLKRUN.

State and persistence: Register snapshots persist in the Yenta socket's private array across suspend. Hardware state persists in PCI config space and ExCA-compatible vendor registers.

Dependencies and integration points: Included directly by `yenta_socket.c` when `CONFIG_YENTA_RICOH` is enabled. It relies on Yenta helper functions `config_read*()` and `config_write*()`, the global `disable_clkrun` module parameter, and PCI vendor/device ids.

Risks: This header contains executable static functions compiled into Yenta, so it is not a passive definition file. CLKRUN disabling is limited to selected revisions and may be necessary for broken cards but can alter power behavior. ZV enablement is narrow and register-specific. Save-state slot allocation must not conflict with other vendor helpers.

Test signals: Ricoh CardBus probe with Yenta, register restore after suspend/resume, CLKRUN messages and stable card operation with `disable_clkrun`, ZV callback behavior on RL5C478, and no regressions on older RL5C46x chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/ricoh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/rsrc_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/rsrc_mgr.c

Purpose: Supplies small resource-management helpers and the static resource-ops implementation for sockets with fixed address mappings.

Important APIs and functions: Exports `pcmcia_make_resource()` and `pccard_static_ops`. `static_init()` marks resource setup done for `SS_CAP_STATIC_MAP` sockets. `static_find_io()` maps a requested base through `s->io_offset`. The ops table leaves memory validation and memory finding NULL because fixed-map socket drivers provide static ranges directly.

Control flow: Static sockets call `static_init()` through the PCMCIA core. For I/O allocation, `static_find_io()` rejects sockets without an `io_offset`, preserves the low 12 bits of the requested base, applies the static offset, returns no parent resource, and reports success.

State and persistence: It only sets `s->resource_setup_done`. `pcmcia_make_resource()` allocates transient `struct resource` objects used by nonstatic and bridge code.

Dependencies and integration points: Depends on PCMCIA socket services and `cs_internal.h`. Used by SoC/static-map drivers such as `soc_common.c` and `xxs1500_ss.c`; `pcmcia_make_resource()` is also used by `rsrc_nonstatic.c`.

Risks: `pcmcia_make_resource(start, end, ...)` treats the second argument as a size, not an absolute end despite the parameter name. Callers must pass a length. Static I/O mapping assumes a 4 KiB window layout.

Test signals: Static-map socket probe, successful I/O port allocation with correct offset, and no resource database setup needed for fixed-map sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/rsrc_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/rsrc_nonstatic.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/rsrc_nonstatic.c

Purpose: Implements dynamic PCMCIA resource management for sockets without static mappings. It maintains available I/O and memory interval databases, probes/validates regions, allocates resources, and exposes the resource database through sysfs.

Important APIs and functions: Exports `pccard_nonstatic_ops` with `pcmcia_nonstatic_validate_mem()`, `nonstatic_find_io()`, `nonstatic_find_mem_region()`, `nonstatic_init()`, and `nonstatic_release_resource_db()`. Internal core helpers include `add_interval()`, `sub_interval()`, `claim_region()`, `do_io_probe()`, `readable()`, `checksum()`, `do_validate_mem()`, `do_mem_probe()`, `validate_mem()`, `adjust_io()`, `adjust_memory()`, and `nonstatic_autoadd_resources()`.

Control flow: Init allocates a `socket_data` with circular interval-list sentinels and optionally imports parent PCI bridge windows. Memory validation probes candidate ranges, claims halves, maps CIS memory, calls socket validation callbacks, falls back to checksums, and moves validated intervals into `mem_db_valid`. I/O allocation uses `allocate_resource()` or `pci_bus_alloc_resource()` with custom alignment against `io_db`, then grows existing windows when possible. Sysfs `available_resources_io` and `available_resources_mem` show and adjust intervals using `+`, `-`, or implicit add syntax.

State and persistence: Per-socket resource state lives in `s->resource_data` as `mem_db`, `mem_db_valid`, and `io_db` linked lists. Kernel resource claims persist until released. Sysfs writes mutate the live resource database and can trigger probing.

Dependencies and integration points: Depends on global `ioport_resource`/`iomem_resource`, PCI bridge resources, PCMCIA core callbacks, socket `ops_mutex`, `pccard_nonstatic_ops`, and optional `CONFIG_PCMCIA_PROBE`.

Risks: Region probing can touch legacy I/O or memory ranges and is guarded but inherently platform-sensitive. Interval arithmetic must avoid overflow and ordering mistakes. Sysfs allows privileged users to modify resource windows at runtime. Memory validation unlocks `ops_mutex` around callback validation, so callers rely on PCMCIA core serialization assumptions.

Test signals: Yenta/PD6729 resource setup, sysfs add/remove/show behavior, allocation of aligned I/O windows, memory validation with real CIS and fake CIS cards, PCI bridge autoadd on non-root buses, probe disabled builds, and cleanup freeing all interval nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/rsrc_nonstatic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1100_generic.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/sa1100_generic.c

Purpose: Registers SA-11x0 PCMCIA platform support for both legacy machine-specific sockets and newer GPIO/regulator-described CF sockets.

Important APIs and functions: `sa11x0_cf_hw_init()` obtains reset, optional bus-enable, optional Vcc regulator, and status GPIOs. `sa11x0_cf_configure_socket()` applies Vcc through `soc_pcmcia_regulator_set()`. `sa11x0_drv_pcmcia_probe()` chooses legacy init for platform id `-1` or creates one socket using `sa11xx_drv_pcmcia_add_one()`. Remove paths call `soc_pcmcia_remove_one()`.

Control flow: Modern probe allocates a `soc_pcmcia_socket`, gets the clock, installs SA11xx timing callbacks into `sa11x0_cf_ops`, initializes the common socket, and registers it. Legacy probe iterates machine-specific init functions built by config, stopping at the first successful match.

State and persistence: Modern socket state includes GPIO descriptors, regulator state, clock, and common SoC socket state. Legacy state is stored in the `skt_dev_info` set by machine-specific init. Hardware power/reset state persists through GPIO and regulator outputs.

Dependencies and integration points: Depends on `soc_common.c`, `sa11xx_base.c`, Linux platform/GPIO/regulator APIs, and optional machine-specific functions such as H3600 and Collie.

Risks: Optional regulator handling returns `PTR_ERR()` for all `IS_ERR()` values; behavior depends on how optional regulator absence is represented by the kernel version. Legacy mode assumes `platform_get_drvdata()` returns `skt_dev_info`. GPIO polarity and named descriptors must match board data.

Test signals: Platform probe for id-specific and legacy devices, GPIO acquisition, Vcc regulator enable/disable, reset and bus-enable toggling during socket state changes, card detect/ready GPIO events, and legacy H3600/Collie registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1100_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1100_generic.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/sa1100_generic.h

Purpose: Declares machine-specific SA-1100 PCMCIA initialization entry points used by the generic SA-11x0 platform driver.

Important APIs and types: Includes common SoC and SA11xx base definitions, then declares `pcmcia_*_init(struct device *)` functions for many legacy SA-1100 boards, including H3600 and Collie-relevant names.

Control flow: No logic executes here. `sa1100_generic.c` conditionally references a subset of these declarations based on Kconfig symbols.

State and persistence: No state is stored. The declared functions create or register common SoC socket state in their implementations.

Dependencies and integration points: Ties legacy board files to the generic SA11x0 PCMCIA platform driver and `sa11xx_drv_pcmcia_probe()`.

Risks: Declarations include many legacy boards not necessarily built in this tree; Kconfig must ensure only available implementations are referenced. Signature mismatch would break compile-time integration.

Test signals: Compile coverage for enabled SA1100 machine configs and successful dispatch from legacy probe into the matching board init routine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1100_generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1100_h3600.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/sa1100_h3600.c

Purpose: Supplies HP iPAQ H3600-specific low-level PCMCIA operations for the SA11xx common socket driver.

Important APIs and functions: Defines `h3600_pcmcia_ops` and exports `pcmcia_h3600_init()`. Important callbacks are `h3600_pcmcia_hw_init()`, `h3600_pcmcia_hw_shutdown()`, `h3600_pcmcia_socket_state()`, `h3600_pcmcia_configure_socket()`, `h3600_pcmcia_socket_init()`, and `h3600_pcmcia_socket_suspend()`.

Control flow: Machine init checks `machine_is_h3600()` and probes two sockets through `sa11xx_drv_pcmcia_probe()`. Socket 0 hardware init requests several EGPIOs for option/NVRAM/reset/card reset; socket 1 has no extra GPIO setup. Configure validates Vcc, drives card reset from `SS_RESET`, and ignores Vpp/output/speaker. Socket init enables the CF bus and waits 10 ms; suspend powers down shared option rails when called for socket 1.

State and persistence: State persists in H3xxx EGPIO outputs and common SoC socket structures. The code relies on shared-bus ordering during suspend.

Dependencies and integration points: Depends on H3xxx machine definitions, legacy GPIO API, `machine_is_h3600()`, and `sa1100_generic.h`.

Risks: The shared-bus suspend FIXME is explicit: it depends on PCMCIA core shutting down socket 0 then socket 1. GPIO cleanup paths must match requested pins. Socket state hard-codes battery/voltage signals low rather than reading hardware.

Test signals: H3600 boot probe, socket 0 GPIO requests, CF bus enable timing, reset assertion/deassertion, suspend powerdown after both sockets, and remove freeing all EGPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1100_h3600.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_generic.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_generic.c

Purpose: Implements generic SA1111 companion-chip PCMCIA support. It handles status decoding, PCCR register configuration, SA1111 IRQ mapping, device enable/disable, and dispatch to board-specific power control.

Important APIs and functions: Exports `sa1111_pcmcia_socket_state()`, `sa1111_pcmcia_configure_socket()`, and `sa1111_pcmcia_add()`. The SA1111 driver entry points are `pcmcia_probe()` and `pcmcia_remove()`, registered via `sa1111_driver_register()`.

Control flow: Probe enables the SA1111 device, claims its register window, initializes sleep/float state, and calls `pcmcia_jornada720_init()` or `pcmcia_neponset_init()` depending on machine type. `sa1111_pcmcia_add()` fetches six SA1111 IRQs, installs the generic status callback into low-level ops, allocates one wrapper per socket, maps ready/card-detect/BVD IRQs for socket 0 or 1, and calls the supplied add function. Configure computes socket-specific masks but socket-independent set bits, then updates PCCR under local IRQ disable.

State and persistence: Each socket wrapper stores a common `soc_pcmcia_socket`, `struct sa1111_dev *`, and linked-list pointer in device driver data. SA1111 PCCR/PCSSR state persists in mapped hardware registers.

Dependencies and integration points: Depends on SA1111 bus APIs, common SoC PCMCIA, SA11xx timing/resource glue, and board files `sa1111_jornada720.c` and `sa1111_neponset.c`.

Risks: `sa1111_pcmcia_configure_socket()` sets PWAIT/PSE/RST/FLT bits for both sockets then masks to the target, so future bit additions must preserve this pattern. Probe only supports Jornada720 and Assabet/Neponset machine paths. IRQ index mapping is fixed and must match SA1111 hardware.

Test signals: SA1111 device probe, two-socket registration on supported boards, PCSR status changes, PCCR reset/power/float transitions, card-detect/BVD IRQ delivery, and clean linked-list removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_generic.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_generic.h

Purpose: Defines the SA1111 PCMCIA wrapper type and declares generic and board-specific SA1111 socket functions.

Important APIs and types: `struct sa1111_pcmcia_socket` embeds `struct soc_pcmcia_socket`, the owning `struct sa1111_dev`, and a linked-list pointer. `to_skt()` converts from common socket to wrapper. Declarations cover `sa1111_pcmcia_add()`, `sa1111_pcmcia_socket_state()`, `sa1111_pcmcia_configure_socket()`, and board init functions.

Control flow: No executable control flow except the inline container conversion. The type is used by `sa1111_generic.c` to manage multiple sockets under one SA1111 device.

State and persistence: The wrapper is per-socket runtime state allocated during `sa1111_pcmcia_add()` and stored in the SA1111 device driver-data list.

Dependencies and integration points: Includes `soc_common.h` and `sa11xx_base.h`; depends on SA1111 device definitions visible to including files.

Risks: The linked-list ownership is manual and must be removed in tandem with `soc_pcmcia_remove_one()`. Board init declarations must match enabled implementations.

Test signals: Compile coverage for SA1111 PCMCIA configs and successful `to_skt()` use in status/configure callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_jornada720.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_jornada720.c

Purpose: Provides HP Jornada 720 board-specific SA1111 PCMCIA power GPIO control.

Important APIs and functions: `jornada720_pcmcia_hw_init()` allocates per-socket GPIO descriptor storage and gets `s0-power`/`s1-power` plus `s0-3v`/`s1-3v`. `jornada720_pcmcia_configure_socket()` maps requested Vcc/Vpp to GPIO values and calls `sa1111_pcmcia_configure_socket()`. `pcmcia_jornada720_init()` installs SA11xx timing callbacks and calls `sa1111_pcmcia_add()`.

Control flow: Init adjusts SA11x0 GPIO edge register `GRER`, then adds two sockets. Configure handles socket 0 with separate 3.3V vs 5V GPIO state; socket 1 treats 3.3V and 5V the same. Unsupported independent Vpp returns `-EPERM`. On success, SA1111 register state is updated before GPIO outputs are written as an array.

State and persistence: Per-socket `jornada720_data` is stored in `skt->driver_data`. GPIO power and voltage-select outputs persist until reconfigured or device removal.

Dependencies and integration points: Depends on SA1111 generic functions, SA11xx timing glue, board GPIO descriptors, and `machine_is_jornada720()` dispatch in `sa1111_generic.c`.

Risks: Socket 1 voltage behavior is uncertain per source comments. Power sequencing order may matter because SA1111 state is applied before board GPIOs. The direct `GRER` manipulation is legacy board-specific global state.

Test signals: Jornada720 probe, GPIO descriptor lookup for both sockets, Vcc 0/33/50 transitions, Vpp rejection path, card operation on both slots, and correct status/IRQ behavior via SA1111 common code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_jornada720.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_neponset.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_neponset.c

Purpose: Provides Assabet Neponset board-specific PCMCIA power control using a Maxim MAX1600 power switch while delegating socket status and SA1111 register control to generic code.

Important APIs and functions: `neponset_pcmcia_hw_init()` initializes a MAX1600 channel for each socket and stores it in `skt->driver_data`. `neponset_pcmcia_configure_socket()` calls `sa1111_pcmcia_configure_socket()` and then `max1600_configure()`. `pcmcia_neponset_init()` installs SA11xx timing callbacks and adds two sockets.

Control flow: The generic SA1111 probe dispatches here for Assabet. Per-socket init chooses MAX1600 channel A for socket 0 and channel B for socket 1, both in low-code mode. Configure applies SA1111 reset/float/wait state first, then power-switch Vcc/Vpp.

State and persistence: MAX1600 channel object persists in `driver_data`; voltage output state persists in the power switch and SA1111 PCCR registers.

Dependencies and integration points: Depends on `max1600.h`, SA1111 generic helpers, SA11xx resource/timing glue, and Assabet machine dispatch.

Risks: The comments describe asymmetric VPP wiring: socket B is CF and VPP lines are grounded. The code relies on `max1600_configure()` to reject or translate unsupported combinations. Ordering between SA1111 and power switch writes should be preserved.

Test signals: Assabet/Neponset probe, MAX1600 channel initialization for both sockets, Vcc/Vpp transitions including CF socket limitations, and card detect/status via SA1111 common code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_neponset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa11xx_base.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/sa11xx_base.c

Purpose: Provides SA-1100/SA-1110 PCMCIA base support: MECR timing calculation, static resource assignment, common SoC socket registration, and CPU-frequency timing updates.

Important APIs and functions: Exports `sa11xx_drv_pcmcia_add_one()`, `sa11xx_drv_pcmcia_ops()`, and `sa11xx_drv_pcmcia_probe()`. Internal helpers include `sa1100_pcmcia_default_mecr_timing()`, `sa1100_pcmcia_set_mecr()`, `sa1100_pcmcia_set_timing()`, and `sa1100_pcmcia_show_timing()`.

Control flow: `sa11xx_drv_pcmcia_ops()` supplies default `get_timing` when absent and installs SA11xx `set_timing`, `show_timing`, and optional cpufreq callbacks. Probe gets a clock, allocates `skt_dev_info`, initializes each common socket with the requested first/nr range, then calls `sa11xx_drv_pcmcia_add_one()`. Timing updates compute max requested I/O/memory/attribute speeds, convert them through board-specific or default BS calculations, update socket fields in MECR under local IRQ disable, and expose requested/effective timing through the SoC status sysfs file.

State and persistence: Socket resources are fixed SA11xx PCMCIA physical regions; MECR holds persistent timing state. Per-socket requested speeds live in `soc_pcmcia_socket` arrays managed by `soc_common.c`.

Dependencies and integration points: Depends on `mach/hardware.h` MECR accessors/macros from `sa11xx_base.h`, common SoC PCMCIA, Linux clocks, and optional cpufreq.

Risks: Direct MECR register updates are architecture-specific and interrupt-protected but not otherwise serialized. Timing math depends on clock units and board-provided overrides. Resource windows assume two classic SA11xx sockets.

Test signals: Socket probe on SA1100/SA1110 boards, timing visible in sysfs status, card operation across I/O/attribute/common memory, CPU-frequency changes, and resource cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa11xx_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa11xx_base.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/sa11xx_base.h

Purpose: Defines SA11xx MECR bit layout, timing calculation helpers, and public SA11xx PCMCIA base functions.

Important APIs and types: Provides `MECR_*_SET()` and `MECR_*_GET()` macros for BSIO, BSA, BSM, and FAST fields per socket. Inline helpers `sa1100_pcmcia_mecr_bs()` and `sa1100_pcmcia_cmd_time()` convert between command width and MECR wait-state encoding. Declares `sa11xx_drv_pcmcia_add_one()`, `sa11xx_drv_pcmcia_ops()`, and `sa11xx_drv_pcmcia_probe()`.

Control flow: No runtime flow except inline arithmetic/macros used by `sa11xx_base.c`.

State and persistence: Macros operate on MECR values; actual state persists in the hardware MECR register managed by the base driver.

Dependencies and integration points: Consumed by SA1100 and SA1111 board glue plus `sa11xx_base.c`. Requires common `soc_pcmcia_socket` definitions.

Risks: Macro arguments are evaluated in assignment expressions and should be simple lvalues/values. Timing helper arithmetic can underflow for invalidly small cycle requests. Socket selection assumes two MECR halves.

Test signals: Compile coverage and sysfs timing output matching MECR register fields after socket map changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/sa11xx_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/soc_common.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/soc_common.c

Purpose: Implements common PCMCIA socket services for integrated SoC controllers. It bridges low-level board/SoC operations to the PCMCIA core, handling resource windows, GPIO/regulator controls, status polling/IRQs, map timing, cpufreq integration, and debug/status sysfs.

Important APIs and functions: Exports `soc_pcmcia_regulator_set()`, `soc_common_pcmcia_get_timing()`, `soc_pcmcia_request_gpiods()`, `soc_common_cf_socket_state()`, `soc_pcmcia_init_one()`, `soc_pcmcia_add_one()`, and `soc_pcmcia_remove_one()`. Core PCMCIA ops are `soc_common_pcmcia_sock_init()`, `soc_common_pcmcia_suspend()`, `soc_common_pcmcia_get_status()`, `soc_common_pcmcia_set_socket()`, `soc_common_pcmcia_set_io_map()`, and `soc_common_pcmcia_set_mem_map()`.

Control flow: `soc_pcmcia_add_one()` claims fixed resources, remaps I/O space, installs default timing, initializes low-level hardware and IRQ/GPIO state, sets static-map PCMCIA capabilities, registers cpufreq notifier, registers the socket, and creates a status file. Status events are detected by IRQs and a periodic timer; `soc_common_check_status()` compares current status against prior status and `csc_mask`, then calls `pcmcia_parse_events()`. Socket/map setters update board hardware, optional reset/bus-enable GPIOs, IRQ type, timing arrays, and map translations.

State and persistence: Per-socket state includes requested card-services state, last status, resource objects, speed arrays, status GPIOs/IRQs, reset/bus-enable GPIOs, regulators, clock, poll timer, and cpufreq notifier. Hardware state persists in board-specific registers, GPIOs, regulators, and SoC memory-controller timing registers.

Dependencies and integration points: Depends on `struct pcmcia_low_level` from PCMCIA SoC headers, `pccard_static_ops`, Linux resource, GPIO descriptor, regulator, clock, IRQ, timer, and cpufreq APIs. Used by PXA2xx, SA11xx, and SA1111 drivers.

Risks: This is the central state machine for many board drivers. It mixes IRQ and polling paths, uses `status_lock` for status updates, and toggles IRQ type for card IRQs based on `state->io_irq`. Resource cleanup must mirror add error paths. Low-level `configure_socket()` failure attempts rollback to prior state, which can itself fail. GPIO active-low handling is special for card-detect.

Test signals: Socket registration/removal on all SoC users, IRQ and polling event delivery, sysfs status readability, map translation for I/O/memory/attribute windows, regulator Vcc changes, reset/bus-enable GPIO changes, suspend/resume, and cpufreq timing recalculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/soc_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/soc_common.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/soc_common.h

Purpose: Defines the private common interface used by SoC PCMCIA socket drivers.

Important APIs and types: Defines `struct skt_dev_info` as a flexible array of `soc_pcmcia_socket`, `struct soc_pcmcia_timing` with I/O/memory/attribute access times, public common helper prototypes, debug macro plumbing, default access timing constants, polling period, and aliases `iostschg`/`iospkr` for I/O-card signal semantics.

Control flow: No executable logic except debug macro expansion. The prototypes form the boundary between low-level board drivers and `soc_common.c`.

State and persistence: The header defines container shapes for per-device socket allocation and timing values; persistent hardware state is managed by users.

Dependencies and integration points: Includes Linux clock/cpufreq and PCMCIA SoC/CIS headers, and is included by PXA2xx, SA11xx, SA1111, and board-specific files.

Risks: Timing constants encode PC Card spec assumptions and drive SoC memory-controller programming. `struct skt_dev_info` flexible allocation requires correct size calculation. Debug macro availability depends on `CONFIG_PCMCIA_DEBUG`.

Test signals: Compile coverage of all SoC socket drivers and runtime timing defaults when no explicit map speed is supplied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/soc_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/socket_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/socket_sysfs.c

Purpose: Provides generic sysfs attributes for PCMCIA socket devices.

Important APIs and functions: Exports `pccard_sysfs_add_socket()` and `pccard_sysfs_remove_socket()`. Attributes include `card_type`, `card_voltage`, `card_vpp`, `card_vcc`, `card_insert`, `card_pm_state`, `card_eject`, `card_irq_mask`, and `available_resources_setup_done`.

Control flow: Show methods read `struct pcmcia_socket` state and format status through `sysfs_emit()`. Store methods validate non-empty input and dispatch synthetic PCMCIA uevents for insert, eject, suspend, resume, or requery. `card_irq_mask` parses a hex mask and intersects it with the socket IRQ mask under `ops_mutex`. `available_resources_setup_done` marks resource setup complete and triggers requery.

State and persistence: Writes mutate the live socket state indirectly through PCMCIA event parsing, `s->irq_mask`, and `s->resource_setup_done`. The sysfs group persists while the socket device is registered.

Dependencies and integration points: Depends on PCMCIA core internals (`cs_internal.h`) and `pcmcia_parse_uevents()`. Called by socket registration paths outside this file.

Risks: User-triggered insert/eject/power events can change runtime card state. `card_irq_mask` only narrows the existing mask, not replaces it, which is intentional but easy to misread. Several show files return `-ENODEV` when no card is present.

Test signals: Attribute group creation/removal, correct output with present and absent cards, insert/eject/requery event effects, suspend/resume via `card_pm_state`, and IRQ mask narrowing under concurrent socket operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/socket_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/ti113x.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/ti113x.h

Purpose: Defines Texas Instruments and ENE CardBus bridge registers plus Yenta override logic for interrupt routing, Zoom Video, suspend/resume state, CLKRUN/burst behavior, power IRQ masking, and ENE tuning.

Important APIs and functions: Under Yenta inclusion it provides `ti_save_state()`, `ti_restore_state()`, `ti_zoom_video()`, `ti1250_zoom_video()`, `ti_init()`, `ti_override()`, `ti113x_override()`, `ti12xx_override()`, `ti1250_override()`, `ti12xx_power_hook()`, and `ene_override()` or alias. The header also defines many TI/ENE PCI config registers and bit masks.

Control flow: Override paths first adjust interrupt routing. TI113x enables PCI CSC/IREQ when possible or probes ISA IRQ fallback. TI12xx probes PCI interrupt delivery, adjusts MFUNC and device-control routing for serial/parallel PCI modes, aligns/ties dual-slot IRQs when needed, enables memory-read burst, and installs a power hook that temporarily disables interrupt pins around power-on for storm-prone bridges. TI1250 updates diagnostic routing before TI12xx setup. ENE optionally scans CardBus children and adjusts test register C9.

State and persistence: Vendor config-space snapshots persist in `yenta_socket.private[]` for suspend/resume. Runtime routing choices mutate PCI config registers, Yenta `cb_irq`, optional power hook, `zoom_video`, and `tune_bridge` callbacks.

Dependencies and integration points: Included by `yenta_socket.c` when `CONFIG_YENTA_TI` is enabled; relies on Yenta register helpers, module parameters `disable_clkrun`, `isa_probe`, `pwr_irqs_off`, and PCI id definitions.

Risks: This is executable code in a header with many chipset-specific branches. IRQ probing intentionally forces events and may fail on broken firmware. Dual-slot routing can affect sibling functions. The source contains legacy rough edges such as duplicated braces and informal warning messages, so behavior should be validated on real hardware.

Test signals: TI/ENE bridge probe across supported IDs, PCI and ISA interrupt routing logs, card insert/remove events on both slots, suspend/resume preserving vendor registers, Zoom Video toggles, power-on without interrupt storms, and ENE tuning with matching child devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/ti113x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/topic.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/topic.h

Purpose: Defines Toshiba ToPIC95/97/100 CardBus bridge registers and Yenta override helpers.

Important APIs and functions: Provides `topic97_zoom_video()`, `topic97_override()`, and `topic95_override()`, plus register/bit definitions for socket, slot, card-control, card-detect, register-control, misc, Zoom Video, audio/video switch, ExCA interface control, and PCI write-buffer config.

Control flow: `topic97_override()` installs a Zoom Video callback. `topic97_zoom_video()` toggles ZV control and audio/video switch bits. `topic95_override()` enables 3.3V support in ExCA interface control, marks Yenta to use ExCA/DF power for 16-bit cards, and disables ToPIC95 CardBus write buffers on older revisions when firmware left them enabled.

State and persistence: Hardware state persists in PCI config and ExCA registers. The Yenta socket flags and `zoom_video` callback persist for the socket lifetime.

Dependencies and integration points: Included by `yenta_socket.c` when `CONFIG_YENTA_TOSHIBA` is set and uses Yenta helper functions and flags.

Risks: ToPIC95 power handling changes Yenta's generic power path for 16-bit cards. Write-buffer disabling is a hardware erratum workaround and revision-gated. ZV register effects are chipset-specific.

Test signals: Probe of Toshiba ToPIC95/97/100 bridges, stable 16-bit 3.3V card power, absence of CardBus lockups under load on affected ToPIC95 systems, and ZV callback toggling on ToPIC97/100.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/topic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/vg468.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/vg468.h

Purpose: Provides Vadem VG468/VG469 PCMCIA controller register definitions for i82365-compatible code.

Important APIs and types: Defines the Vadem identity bit, power-control VPP2 masks, unique register offsets (`VG469_VSENSE`, `VG469_VSELECT`, `VG468_CTL`, `VG468_TIMER`, `VG468_MISC`, GPIO/select/ATA registers), and bit masks for voltage sense/selection, control, timers, misc, and extended mode.

Control flow: No functions are implemented. Consumers use these constants when detecting and programming Vadem-compatible controllers.

State and persistence: Constants describe controller register state; no state is stored in this header.

Dependencies and integration points: Intended for legacy PCMCIA controller code that also uses `i82365.h` semantics. It is not directly used by the files in this work item except as part of the same driver family.

Risks: Vadem chips have unique voltage and compatibility modes. Misusing `VG469_VSEL_*` or `VG469_MODE_*` can select wrong voltage, routing, or compatibility behavior. Since this is all macros, compiler checks are minimal.

Test signals: Compile coverage in Vadem-enabled builds, correct Vadem detection, voltage sense reporting, Vcc/Vpp programming, and legacy socket operation on VG468/VG469 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/vg468.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/xxs1500_ss.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/xxs1500_ss.c

Purpose: Implements PCMCIA socket services for the MyCable XXS1500 MIPS/Au1x00 platform using fixed physical windows and board GPIOs.

Important APIs and functions: The platform driver registers `xxs1500_pcmcia_probe()` and `xxs1500_pcmcia_remove()`. PCMCIA ops are `xxs1500_pcmcia_sock_init()`, `xxs1500_pcmcia_sock_suspend()`, `xxs1500_pcmcia_get_status()`, `xxs1500_pcmcia_configure()`, `au1x00_pcmcia_set_io_map()`, and `au1x00_pcmcia_set_mem_map()`. `cdirq()` handles card-detect IRQs.

Control flow: Probe allocates one socket, reads named platform resources for attribute, memory, and I/O physical areas, remaps I/O and adjusts for `mips_io_port_base`, fills a static-map `pcmcia_socket`, requests a GPIO card-detect IRQ, and registers the socket. Configure supports only Vcc 0 or 3.3V, toggles low-active power, asserts/deasserts reset and buffer-enable on reset changes, and waits 500 ms after deassert. Status reads GPIOs for card detect, voltage key, power, reset/ready, and battery signals.

State and persistence: `struct xxs1500_pcmcia_sock` stores physical windows, adjusted virtual I/O base, embedded socket, and previous flags. Hardware state persists in GPIO outputs and static physical maps.

Dependencies and integration points: Depends on MIPS Au1x00 headers, legacy GPIO API, platform resources, PCMCIA static resource ops, and fixed board wiring.

Risks: The I/O remap arithmetic subtracts `mips_io_port_base` and must be reversed exactly for `iounmap()`. Only 3.3V cards are supported; 5V cards are reported as unsupported. Fixed GPIO numbers make the driver non-portable. Card detect uses only one of two detect GPIOs for IRQ.

Test signals: Platform probe with all three named resources, I/O remap success, card-detect IRQ on GPIO_CDA, status values for present/absent/voltage-key states, 3.3V power/reset sequencing, and clean remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/xxs1500_ss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/yenta_socket.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/yenta_socket.c

Purpose: Implements the generic Yenta-compatible PCI CardBus bridge driver. It supports CardBus and 16-bit PC Card sockets, resource-window allocation, socket power/status/map operations, interrupt/polling event delivery, chipset-specific overrides, sysfs register dumps, and suspend/resume.

Important APIs and functions: The module registers `yenta_cardbus_driver`. Core PCMCIA ops are `yenta_sock_init()`, `yenta_sock_suspend()`, `yenta_get_status()`, `yenta_set_socket()`, `yenta_set_io_map()`, and `yenta_set_mem_map()`. Probe/remove are `yenta_probe()` and `yenta_close()`. Resource helpers include `yenta_allocate_resources()`, `yenta_allocate_res()`, and `yenta_search_res()`. IRQ helpers include `yenta_interrupt()`, polling wrapper, ISA/PCI probe helpers, and capability discovery.

Control flow: Probe validates a subordinate bus, allocates a `yenta_socket`, enables and requests PCI resources, maps the CardBus register BAR, initializes bridge config, disables events, allocates bridge I/O/memory windows, applies vendor override callbacks selected by PCI IDs, requests a PCI IRQ or starts polling, interrogates voltage/card type, probes ISA IRQ mask, fixes parent bridge bus numbers, registers the PCMCIA socket, and creates `yenta_registers`. Runtime interrupts clear CardBus event and ExCA CSC status, translate events, and call `pcmcia_parse_events()`.

State and persistence: `struct yenta_socket` stores PCI device, IRQ routing, mapped register base, timer, embedded socket, vendor type, flags, probe status, private vendor data, and saved PCI state. Hardware state persists in CardBus memory-mapped registers, ExCA registers, and PCI bridge config/resource windows.

Dependencies and integration points: Depends on PCI, PCMCIA socket services, `pccard_nonstatic_ops`, `i82365.h`, and optional TI/Ricoh/Toshiba/O2 headers. It integrates CardBus subordinate PCI buses with PCMCIA card services.

Risks: This driver programs power and resource windows directly and supports many legacy bridge quirks. Polling mode disables CardBus support when no PCI IRQ is available. Resource allocation may continue with missing windows. Power-on can trigger interrupt storms on some TI chips, mitigated by vendor hooks. Parent bridge bus-number fixups touch PCI topology.

Test signals: Probe on generic and vendor-specific CardBus bridges, CardBus and 16-bit card insertion/removal, PCI IRQ and polling modes, bridge resource assignment, I/O and memory map programming, socket power/reset/Vpp transitions, sysfs register dump, suspend/resume, and vendor override logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/yenta_socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/yenta_socket.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/yenta_socket.h

Purpose: Defines CardBus/Yenta register offsets, bit masks, vendor override contracts, and the `struct yenta_socket` state container.

Important APIs and types: Defines CardBus socket event/mask/state/force/control/power registers, bridge base/limit/control fields, ExCA page register, Yenta 16-bit power flags, `struct cardbus_type`, and `struct yenta_socket`.

Control flow: No executable logic. `cardbus_type` function pointers let vendor headers provide override, save/restore, and socket-init hooks used by `yenta_socket.c`.

State and persistence: `struct yenta_socket` is the runtime state for one PCI CardBus bridge function, including mapped registers, timer, embedded PCMCIA socket, vendor-private words, and saved PCI state.

Dependencies and integration points: Includes `asm/io.h` and is included before vendor headers so they can access Yenta types and helper functions from `yenta_socket.c`.

Risks: Bit definitions directly control socket power, event masks, and bridge windows; mistakes can mispower cards or hide events. The private array is shared by vendor hooks and requires disciplined indexing. `cb_irq` uses zero as "no IRQ" even though zero can be a valid IRQ on some systems, matching legacy assumptions in the driver.

Test signals: Compile coverage, correct status decoding from `CB_SOCKET_STATE`, vendor override callbacks receiving valid `struct yenta_socket`, and suspend/resume preserving `saved_state`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/yenta_socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/peci/Kconfig

Purpose: Defines the top-level Kconfig menu for Linux PECI support and includes controller-driver options.

Important APIs and types: `menuconfig PECI` controls the PECI core as a tristate. `config PECI_CPU` enables the PECI CPU auxiliary-device driver and selects `AUXILIARY_BUS`. The file sources `drivers/peci/controller/Kconfig` under `if PECI`.

Control flow: Kconfig selection enables compilation of PECI core, optional CPU device support, and hardware controller menus. No runtime code.

State and persistence: Build configuration state determines which modules or built-in objects exist: `peci`, `peci-cpu`, and controller drivers.

Dependencies and integration points: Integrates with the kernel build system, auxiliary bus, and controller Kconfig files. Intended for Intel platform BMC kernels.

Risks: Controller options are invisible unless `PECI` is enabled. `PECI_CPU` creates auxiliary devices consumed by other drivers, so enabling it without functional controller support may not yield useful runtime behavior.

Test signals: Kconfig visibility, successful `CONFIG_PECI=m/y` builds, `peci.ko` and `peci-cpu.ko` generation when modular, and controller submenu inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/peci/Makefile

Purpose: Builds the PECI core, optional PECI CPU driver, and controller subdirectory.

Important APIs and types: `peci-y` links `core.o`, `request.o`, `device.o`, and `sysfs.o` into `peci.o`. `obj-$(CONFIG_PECI)` includes the core. `peci-cpu-y` builds `cpu.o` into `peci-cpu.o`. `obj-y += controller/` descends into hardware controller builds.

Control flow: Build-system only; no runtime flow.

State and persistence: Object composition determines module boundaries and exported symbols available to controller drivers.

Dependencies and integration points: Driven by Kconfig symbols `CONFIG_PECI` and `CONFIG_PECI_CPU`; delegates controller selection to `drivers/peci/controller/Makefile`.

Risks: The controller directory is always visited, but its objects are gated internally. Core object list must stay in sync with PECI subsystem source files and exported namespace expectations.

Test signals: `make drivers/peci/` with PECI built-in and modular configurations, expected module names, and successful controller linkage against core symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/controller/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/peci/controller/Kconfig

Purpose: Defines Kconfig options for hardware PECI bus controller drivers.

Important APIs and types: `CONFIG_PECI_ASPEED` enables ASPEED AST2400/AST2500/AST2600 PECI support with dependencies on ASPEED or compile-test, device tree, I/O memory, and common clock. `CONFIG_PECI_NPCM` enables Nuvoton NPCM PECI support with OF and `REGMAP_MMIO`.

Control flow: Kconfig only. Selection controls which controller objects are built and available to register with the PECI core.

State and persistence: Build configuration determines platform-driver availability and module names `peci-aspeed` or `peci-npcm`.

Dependencies and integration points: Sourced by the top-level PECI Kconfig only when `PECI` is enabled. Controller drivers depend on platform-specific clocks, MMIO, and device-tree matching.

Risks: Missing OF/common-clock dependencies would break ASPEED probe; `COMPILE_TEST` permits non-ASPEED build coverage but not runtime support. NPCM selects regmap MMIO while ASPEED uses direct MMIO and clock-provider APIs.

Test signals: Menu visibility under `PECI`, compile-test builds, module generation for selected controllers, and device-tree compatible matching at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/controller/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/controller/Makefile -->
# sources/distributed-fs/ceph-client/drivers/peci/controller/Makefile

Purpose: Builds selected PECI hardware controller drivers.

Important APIs and types: Adds `peci-aspeed.o` when `CONFIG_PECI_ASPEED` is enabled and `peci-npcm.o` when `CONFIG_PECI_NPCM` is enabled.

Control flow: Build-system only.

State and persistence: Determines which platform-driver modules are linked for PECI controller support.

Dependencies and integration points: Consumed from the top-level PECI Makefile's `controller/` descent and tied to controller Kconfig symbols.

Risks: Object names must match source files and module aliases; adding a controller requires both Kconfig and Makefile updates.

Test signals: Selected objects appear in build output and can link against the PECI core when built as modules or built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/controller/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/controller/peci-aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/peci/controller/peci-aspeed.c

Purpose: Implements the ASPEED AST2400/AST2500/AST2600 PECI controller driver. It programs the controller MMIO block, manages a hardware-derived PECI clock divider, sends PECI requests through the core controller API, and handles command-completion interrupts.

Important APIs and functions: `aspeed_peci_probe()` maps MMIO, requests IRQ, gets/deasserts reset, reads sanitized properties, initializes registers, registers a clock divider, enables it, enables the controller, and calls `devm_peci_controller_add()`. Runtime transfer is `aspeed_peci_xfer()`. IRQ handling is `aspeed_peci_irq_handler()`. Clock operations are `clk_aspeed_peci_set_rate()`, `clk_aspeed_peci_determine_rate()`, and `clk_aspeed_peci_recalc_rate()`.

Control flow: A transfer validates 32-byte TX/RX limits, calls `aspeed_peci_check_idle()` which may reset/reinitialize hung hardware, programs target/write/read lengths and TX data registers, clears status, fires the command, waits for completion, checks interrupt status, then reads RX data registers in dwords. The IRQ handler reads and clears interrupt status, ORs masked status into `priv->status`, completes the transfer on command done, writes zero to the command register, and releases the spinlock.

State and persistence: `struct aspeed_peci` stores controller pointer, device, MMIO base, reset, IRQ, spinlock, completion, clock, configured frequency, status, and timeout. Device-tree properties `clock-frequency` and `cmd-timeout-ms` are sanitized and persist in driver state. Hardware timing, interrupt, control, and data registers persist until reset or reprogramming.

Dependencies and integration points: Depends on Linux PECI core (`struct peci_controller_ops`), platform device/of matching, reset controller, common clock framework, MMIO polling, completions, spinlocks, and unaligned access helpers. Matches `aspeed,ast2400-peci`, `aspeed,ast2500-peci`, and `aspeed,ast2600-peci`.

Risks: The transfer path in this source contains a duplicated `spin_lock_irq(&priv->lock)` before checking `priv->status`; as written, that is a deadlock-level bug because the same spinlock is acquired twice without an intervening unlock. TX/RX loops write/read in 4-byte chunks using unaligned helpers, so request buffer sizing must remain compatible with `PECI_REQUEST_MAX_BUF_SIZE`. Idle recovery resets hardware and must restore clock rate and controller enable correctly. Clock divider search approximates the requested frequency.

Test signals: Device-tree probe on AST24xx/25xx/26xx, reset and clock setup, sanitized property warnings for invalid values, PECI ping/transactions through the core, command-done IRQ completion, timeout path, idle-hang reset recovery, dynamic-debug TX/RX dumps, and lockdep or runtime testing catching the duplicate spinlock acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/controller/peci-aspeed.c -->
