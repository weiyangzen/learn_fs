# subset-b-005363 Research

Grouped research for the listed Linux kernel source files. Each wrapped section preserves the source path and is intended to be split into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/wd719x.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/wd719x.c

Purpose: PCI SCSI host driver for Western Digital WD7193/7197/7296 "Spider" adapters. It bridges the SCSI midlayer to card firmware by building Spider Control Blocks, DMA mapping them, issuing direct adapter commands, and completing commands from interrupts.

Important APIs and functions: `wd719x_pci_probe/remove` own PCI enablement, BAR mapping, host allocation, and scan/remove. `wd719x_board_found` allocates coherent firmware, EEPROM parameter, and hash buffers, requests IRQ, reads EEPROM, and initializes firmware. `wd719x_chip_init` loads `wd719x-wcs.bin` and `wd719x-risc.bin`, bootstraps the RISC with DMA, resets the SCSI bus, sets host parameters, and starts SCAM. `wd719x_queuecommand` maps the SCB, sense buffer, and scatterlist, queues it on `active_scbs`, and writes the SCB pointer and process opcode. Error handlers call `wd719x_abort`, `wd719x_reset`, and `wd719x_host_reset`. `wd719x_interrupt` maps completion status to SCSI host bytes through `wd719x_interrupt_SCB`.

Control flow: probe prepares PCI and SCSI host state, initializes firmware, adds the host, then scans. Normal I/O flows from `queuecommand` to adapter DMA to interrupt completion and `scsi_done`. Direct commands serialize under the host lock for reset/abort paths. Removal removes the SCSI host before putting the RISC to sleep and freeing DMA state.

State and persistence: no disk persistence; runtime state is `struct wd719x`, coherent firmware/parameter/hash buffers, EEPROM-derived host parameters, and `active_scbs`. Dependencies include PCI, firmware loader, DMA API, SCSI midlayer, EEPROM 93cx6 helpers, and MMIO. Risks are legacy hardware timing, direct-command timeouts, active SCB pointer validation, reset/abort races, firmware availability, and a possible list traversal bug if no active SCB matches the returned pointer. Test signals are successful firmware version log, SCSI scan, command completion, reset/abort recovery, DMA mapping failure paths, and module unload without non-empty `active_scbs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/wd719x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/wd719x.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/wd719x.h

Purpose: private hardware contract for the WD719x SCSI driver. It defines the DMA-visible Spider Control Block layout, driver-private host state, register offsets, command opcodes, interrupt and error codes, EEPROM layout, and host parameter block.

Important types and constants: `struct wd719x_scb` is packed and contains the firmware-owned SCB fields followed by driver-only DMA address, command pointer, list node, and a 255-entry SG list. `struct wd719x` stores the SCSI host, PCI device, MMIO base, card type, coherent firmware/parameter/hash buffers, and active SCB list. `union wd719x_regs` decodes the adapter status longword into opcode, SCSI status, Spider unique error, and interrupt status. `struct wd719x_host_param` mirrors EEPROM/programmable adapter parameters. Register constants cover advanced-mode AMR registers, PCI/GPIO firmware bootstrap registers, EEPROM pins, and SCB option flags.

Control flow support: the C file uses command constants for direct commands, status constants for interrupt dispatch, and register offsets for all MMIO access. The packed SCB layout is the core DMA ABI between host memory and firmware.

State and dependencies: this header depends on kernel endian and SCSI/Pci types through the including source. No independent persistence exists, but EEPROM-derived fields are staged in `wd719x_host_param` and sent to firmware. Risks are ABI sensitivity: packing, alignment, endian conversions, SG count, and register bit definitions must match hardware documentation. Test signals are successful compile on supported architectures, correct firmware initialization, DMA-safe SCB completion, and no structure layout regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/wd719x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/xen-scsifront.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/xen-scsifront.c

Purpose: Xen virtual SCSI frontend driver. It exposes a SCSI host in the guest, translates SCSI commands into Xen vscsi ring requests, grants backend access to data pages, and handles Xenbus lifecycle and LUN hotplug.

Important APIs and functions: `scsifront_probe/remove/resume/suspend` manage SCSI host, shared ring, event channel, and pause state. `scsifront_queuecommand` maps command data into grant references and posts a ring request via `scsifront_do_request`. `map_data_for_request` builds inline or granted SG segment tables. `scsifront_irq_fn`, `scsifront_ring_drain`, and `scsifront_do_response` consume backend responses. Error handlers use `scsifront_action_handler` to send synchronous abort/reset requests. `scsifront_backend_changed` reacts to Xenbus state transitions, and `scsifront_do_lun_hotplug` adds/removes SCSI devices from backend `vscsi-devs` entries.

Control flow: Xenbus probe allocates a ring and IRQ, adds the SCSI host, then switches to Initialised. Backend Connected triggers feature negotiation and LUN discovery. I/O requests claim a request id, grant data pages, push a ring entry, and notify the backend. IRQ processing completes commands, frees grant access, updates result/status/sense/residual fields, and calls `scsi_done`.

State and persistence: runtime state is `vscsifrnt_info`, shadow request slots, grant refs, ring indices, wait queues, pause/caller counters, and Xenstore device-state paths. Dependencies include Xenbus, grant table, event channels, SCSI midlayer, runtime scheduler, and Xen vscsi protocol headers. Risks include backend misbehavior, illegal rqids, grant still in use, suspend/resume races, ring-full backpressure, and hotplug state synchronization. Test signals include Xen guest attach/detach, LUN add/remove in Xenstore, successful read/write with large SG lists, abort/reset completion, suspend/resume drain, and error-state refusal of new I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/xen-scsifront.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/zalon.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/zalon.c

Purpose: PA-RISC GSC bus front-end for Bluefish/Zalon 720 NCR53c7xx SCSI hardware. It initializes Zalon-specific registers and hands the controller to the shared `ncr53c8xx` SCSI core.

Important APIs and functions: `zalon_probe` maps the HPA window, resets the module, enables interrupt/pre-fetch/packing bits, allocates a GSC IRQ, seeds a `struct ncr_device`, calls `ncr_attach`, requests the shared interrupt, adds and scans the SCSI host. `zalon_remove` removes the host, releases the NCR core, and frees IRQ. `zalon7xx_init/exit` pair `ncr53c8xx_init/exit` with PA-RISC driver registration.

Control flow: module init initializes the common NCR core then registers a PA-RISC driver for matching firmware IDs. Probe performs platform register setup before the common core takes over normal SCSI command processing and interrupt handling.

State and dependencies: state is mostly in the shared NCR core and SCSI host; local state is MMIO mapping, device IRQ, and static unit number. Dependencies include PA-RISC GSC/PDC hardware interfaces, raw MMIO, `ncr53c8xx`, and SCSI midlayer. Risks include missing `iounmap` on probe failure/removal in this legacy code path, interrupt setup ordering, old hardware revision quirks, and assumptions about differential mode and host ID. Test signals are boot-time Zalon version logs, IRQ allocation, `scsi_scan_host` discovering targets, interrupt-driven I/O, and clean module removal on PA-RISC hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/zalon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/zorro7xx.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/zorro7xx.c

Purpose: Amiga Zorro bus front-end for NCR53C710-based SCSI controllers such as WarpEngine, A4091, PowerUP, and GForce boards. It configures board offsets and delegates command handling to the `53c700` core.

Important APIs and functions: the Zorro ID table maps products to `zorro_driver_data`. `zorro7xx_init_one` reserves the Zorro device, allocates `NCR_700_Host_Parameters`, maps the controller address using either `ioremap` or `ZTWO_VADDR`, configures clock/chip flags and CTEST settings, calls `NCR_700_detect`, requests the Amiga ports IRQ, stores drvdata, and scans the host. `zorro7xx_remove_one` reverses these allocations and releases the common core.

Control flow: Zorro probe selects absolute or board-relative IO address, initializes host parameters, then SCSI processing moves to `NCR_700_intr` and the 53c700 host template. Removal stops the SCSI host before freeing shared IRQ and board reservation.

State and dependencies: state lives in `Scsi_Host`, NCR hostdata, and Zorro drvdata. Dependencies include Amiga Zorro resources, Amiga interrupt constants, SCSI SPI transport, and `53c700`. Risks are product-specific offsets, mixed Zorro II/absolute address handling, shared IRQ behavior, and cleanup ordering. Test signals are board detection by Zorro ID, successful region reservation, target scan, interrupt-driven transfers, and unload without stale IRQ or mapping references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/zorro7xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/zorro_esp.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/zorro_esp.c

Purpose: Amiga Zorro ESP/NCR5C9x SCSI front-end for several accelerator boards. It supplies board-specific register access, IRQ-pending checks, DMA programming, and probe/remove glue for the shared `esp_scsi` core.

Important APIs and functions: board register structs describe Blizzard, CyberStorm, and Fastlane DMA layouts. `zorro_esp_write8/read8`, IRQ helpers, DMA length limiters, and board-specific `zorro_esp_send_*_dma_cmd` implementations populate `struct esp_driver_ops`. `zorro_esp_probe` identifies Zorro II/III addressing, fixes the shared Blizzard/Fastlane ID case, maps ESP and DMA registers, allocates the ESP command block, requests `IRQ_AMIGA_PORTS`, validates optional SCSI presence, and registers via `scsi_esp_register`. `zorro_esp_remove` unregisters ESP and frees mappings, IRQ, DMA buffer, and private data.

Control flow: probe selects `zorro_driver_data`, maps device resources, attaches ops to `struct esp`, then the common ESP core drives SCSI command sequencing. DMA send functions handle protocol message phases via PIO fallback, cache synchronization, register address staging, transfer-count setup, and ESP command issue.

State and dependencies: state includes `zorro_esp_priv` with board base, Zorro III flag, and Fastlane control shadow; `struct esp`; coherent command block; and Zorro drvdata. Dependencies include Zorro resources, Amiga cache/DMA helpers, `esp_scsi`, SCSI midlayer, and DMA mapping. Risks are hardware-specific address bit semantics, cache coherency on m68k, unsupported Oktagon PDMA, shared product IDs, and cleanup after partial probe. Test signals include board-specific probe logs, successful SCSI option register echo, target scan, DMA/PIO fallback transfers, and Fastlane Z3 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/zorro_esp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/sh/Kconfig

Purpose: top-level Kconfig menu for SuperH and SH-Mobile specific drivers. It creates the "SuperH / SH-Mobile Driver Options" menu and includes the interrupt-controller Kconfig.

Important symbols: it sources `drivers/sh/intc/Kconfig`; no local config symbols are defined here. Control flow is Kconfig inclusion only: architecture Kconfig files include this menu, and this file delegates feature selection to subdirectories.

State and dependencies: no runtime state or persistence. Dependency is the Kconfig parser and the referenced `drivers/sh/intc/Kconfig` path. Integration point is the kernel configuration UI/build system, which exposes SH interrupt-controller options. Risks are mainly menu placement and stale source paths if the directory layout changes. Test signals are `make menuconfig` visibility and successful configuration parsing with SH/COMPILE_TEST combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/Makefile -->
# sources/distributed-fs/ceph-client/drivers/sh/Makefile

Purpose: build orchestration for SuperH specific driver subtrees and common runtime PM support.

Important build rules: `CONFIG_SH_INTC` adds `intc/`; legacy `clk/` is built for `CONFIG_HAVE_CLK` only when `CONFIG_COMMON_CLK` is not enabled; `CONFIG_MAPLE` adds `maple/`; `pm_runtime.o` is always included for this directory.

Control flow: Kbuild evaluates config symbols and descends into selected subdirectories. Runtime behavior is in the compiled objects, not this file.

State and dependencies: no runtime state. Dependencies include Kbuild, SH architecture configuration, clock framework selection, and Maple/INTC config symbols. Risks are duplicate clock framework builds if `COMMON_CLK` gating is wrong, always-built `pm_runtime.o` on unsupported configurations, and missing subdir objects when symbols move. Test signals are allmodconfig/allyesconfig builds across SuperH and COMPILE_TEST, plus object inclusion checks for legacy clk versus common clk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/clk/Makefile -->
# sources/distributed-fs/ceph-client/drivers/sh/clk/Makefile

Purpose: Kbuild file for the legacy SuperH clock framework.

Important build rules: `core.o` is always built when the directory is selected, and `cpg.o` is added by `CONFIG_SH_CLK_CPG`.

Control flow and integration: the parent Makefile selects this directory for legacy `CONFIG_HAVE_CLK` systems without `CONFIG_COMMON_CLK`. Platform clock definitions then link against `core.o` APIs and optionally CPG helpers.

State and dependencies: no runtime state in this file. Dependencies are Kbuild and the `CONFIG_SH_CLK_CPG` symbol. Risks are mismatched platform expectations if CPG users build without `cpg.o`, or accidental coexistence with common-clk code. Test signals are successful SH legacy-clock builds and exported symbol resolution for `clk_register`, `sh_clk_mstp_register`, and div helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/clk/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/clk/core.c -->
# sources/distributed-fs/ceph-client/drivers/sh/clk/core.c

Purpose: legacy SuperH clock framework core. It registers `struct clk` instances, manages parent/child topology, enable reference counts, rate calculation/rounding helpers, MMIO register mappings, and resume/late-disable behavior.

Important APIs and functions: exported APIs include `clk_register/unregister`, `clk_enable/disable`, `clk_get_rate`, `clk_set_rate`, `clk_set_parent`, `clk_get_parent`, `clk_round_rate`, `clk_rate_table_build`, rate-table/range rounders, `followparent_recalc`, `clk_reparent`, `propagate_rate`, `recalculate_root_clocks`, and `clk_enable_init_clocks`. Mapping helpers establish shared `clk_mapping` ioremaps with kref lifetime. PM hooks reapply parent/rate settings on resume, and `clk_late_init` disables unused clocks after boot.

Control flow: platforms register clock objects; registration maps registers, links parent/child lists, and optionally calls legacy init ops. Enable walks parents before enabling a leaf, while disable decrements and may disable parent after child usecount hits zero. Rate changes call ops, recalc, then propagate recursively to children.

State and dependencies: global `clock_list`, `root_clks`, spinlock, mutex, `allow_disable`, per-clock usecount/mapping/rate/children. Dependencies include legacy `linux/sh_clk.h`, cpufreq tables, MMIO, syscore PM, and kernel clk consumers. Risks are global locking correctness, usecount imbalance, recursive parent propagation, mapping lifetime, late-init disabling hardware too aggressively, and legacy API divergence from common-clk. Test signals include platform boot clock tree, cpufreq rate tables, suspend/resume rate restoration, warnings on disable with zero usecount, and register access under lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/clk/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/clk/cpg.c -->
# sources/distributed-fs/ceph-client/drivers/sh/clk/cpg.c

Purpose: helper library for SuperH Clock Pulse Generator clocks in the legacy framework. It implements module-stop, div4/div6, reparenting, and FSI divisor clock operations.

Important APIs and functions: `sh_clk_mstp_register` creates clocks with module-stop enable/disable ops. Div helpers include `sh_clk_div6_register`, `sh_clk_div6_reparent_register`, `sh_clk_div4_register`, `sh_clk_div4_enable_register`, and `sh_clk_div4_reparent_register`. `sh_clk_read/write/read_status` abstract 8/16/32-bit registers. `sh_clk_div_recalc/set_rate/round_rate/enable/disable` build frequency tables and manipulate divisor fields. FSI-DIV support uses `sh_clk_fsidiv_register` with dedicated recalc/round/set/enable/disable ops.

Control flow: platform clock arrays are passed to registration helpers; helpers assign ops, allocate frequency tables, initialize parent from hardware fields when needed, and call `clk_register`. Enable/disable and set-rate callbacks later write CPG registers through the mapped register pointer supplied by the core.

State and dependencies: per-clock state is in `struct clk` fields such as `enable_reg`, `status_reg`, divisor masks, parent tables, arch flags, and private div tables. Dependencies include `linux/sh_clk.h`, MMIO, cpufreq frequency tables, and parent clocks. Risks include invalid divisor tables, wrong register width flags, status polling timeout, div6 CKSTP quirks, parent-table mismatch, and leaked frequency-table allocation if later registration fails. Test signals are platform CPG registration, clock enable status-bit clearing, rate round/set correctness, parent switching, and FSI register behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/clk/cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/sh/intc/Kconfig

Purpose: configuration for the SuperH interrupt controller framework and optional features.

Important symbols: `SH_INTC` is a bool that selects `IRQ_DOMAIN`. Under it, `INTC_USERIMASK` enables userspace interrupt masking for SH-4A or COMPILE_TEST, `INTC_BALANCING` enables hardware IRQ auto-distribution for SH-X3 SMP, and `INTC_MAPPING_DEBUG` exposes irq-to-controller enum mappings through debugfs.

Control flow: Kconfig gates compilation of optional `userimask.o`, `balancing.o`, and `virq-debugfs.o` through the Makefile. The base INTC framework is built when the architecture selects `SH_INTC`.

State and dependencies: no runtime state here. Dependencies include architecture CPU symbols, SMP, DEBUG_FS, and IRQ_DOMAIN. Risks are allowing options on hardware that lacks support or excluding useful COMPILE_TEST coverage. Test signals are Kconfig dependency resolution, allmodconfig coverage, and expected object selection for each symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/sh/intc/Makefile

Purpose: Kbuild object list for the SuperH INTC framework.

Important build rules: base objects are `access.o`, `chip.o`, `core.o`, `handle.o`, `irqdomain.o`, and `virq.o`. Optional objects are `balancing.o` for `CONFIG_INTC_BALANCING`, `userimask.o` for `CONFIG_INTC_USERIMASK`, and `virq-debugfs.o` for `CONFIG_INTC_MAPPING_DEBUG`.

Control flow: the base objects collectively implement register access, handle encoding, irq-chip operations, controller registration, irqdomain setup, and virtual subgroup IRQs. Optional objects extend hooks compiled into the base through stubs in `internals.h`.

State and dependencies: no runtime state in the Makefile. Dependencies are the Kconfig symbols and internal symbol references between objects. Risks include missing an optional object when stubs are not sufficient and link failures if feature guards diverge. Test signals are link success for every symbol combination and boot tests for base INTC with optional features enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/access.c -->
# sources/distributed-fs/ceph-client/drivers/sh/intc/access.c

Purpose: low-level register accessor and mode-dispatch helpers for the SH INTC framework.

Important APIs and functions: `intc_phys_to_virt` translates physical register addresses through descriptor windows. `intc_get_reg` indexes the descriptor register table. `intc_set_field_from_handle` and `intc_get_field_from_handle` manipulate encoded bitfields. `test_8/16/32`, `write_8/16/32`, and `modify_8/16/32` implement width-specific raw access. Dispatch tables `intc_reg_fns`, `intc_enable_fns`, `intc_disable_fns`, and `intc_enable_noprio_fns` map encoded handle function/mode fields to runtime operations.

Control flow: higher-level handle code encodes register index, mode, width, and shift into a handle. IRQ chip operations later decode the handle and call these dispatch tables to enable, disable, acknowledge, test, or set priority fields.

State and dependencies: state is descriptor register/window arrays; accessor functions themselves are stateless. Dependencies include raw MMIO and `internals.h` handle macros. Risks include `BUG()` on missing register mapping, local IRQ masking around read-modify-write only on the local CPU, write-posting flush assumptions, and invalid width-to-dispatch encoding. Test signals include enable/disable bit changes on real INTC registers, priority field updates, ack writes, and boot without `BUG()` from descriptor table mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/balancing.c -->
# sources/distributed-fs/ceph-client/drivers/sh/intc/balancing.c

Purpose: optional support for SH-X3 hardware-managed interrupt auto-distribution.

Important APIs and functions: `intc_set_dist_handle` records a per-IRQ distribution register handle derived by `intc_dist_data`. `intc_balancing_enable` and `intc_balancing_disable` write the distribution bit when IRQ balancing is not globally disabled for that IRQ.

Control flow: during controller registration, the core calls `intc_set_dist_handle` after normal mask/ack setup. Later, `intc_enable` enables distribution after unmasking, and `intc_disable` disables distribution before masking.

State and dependencies: global `dist_handle[INTC_NR_IRQS]` stores encoded handles. Dependencies include mask register descriptors with `dist_reg`, the INTC register dispatch tables, `irq_balancing_disabled`, SMP-capable SH-X3 hardware, and `intc_big_lock` during setup. Risks are silently absent distribution handles, hardware-specific semantics, interaction with CPU affinity, and wrong register width/field index. Test signals are SMP boot with `CONFIG_INTC_BALANCING`, expected distribution register writes on IRQ enable/disable, and no balancing writes for IRQs lacking `dist_reg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/balancing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/chip.c -->
# sources/distributed-fs/ceph-client/drivers/sh/intc/chip.c

Purpose: Linux `irq_chip` implementation for SH INTC interrupts. It translates generic IRQ mask/unmask/type/affinity calls into encoded INTC register operations.

Important APIs and functions: `_intc_enable` iterates per-CPU enable registers and applies `intc_enable_fns`, then enables balancing. `intc_disable` disables balancing and writes disable handles. `intc_mask_ack` masks then clears an ack bit for controllers with ack registers. `intc_set_priority` updates per-IRQ priority and optional secondary priority handles. `intc_set_type` writes sense register fields using `intc_irq_sense_table`. `intc_irq_chip` exports mask, unmask, enable, disable, mask_ack, set_type, and optional set_affinity.

Control flow: controller registration installs `intc_irq_chip` on each IRQ with a primary handle in chip data. Generic IRQ core later invokes these callbacks for interrupt lifecycle operations. Secondary handles are enabled during registration for combined mask/priority controllers.

State and dependencies: uses descriptor lookup through chip container, per-IRQ priority array in core, prio/sense handle lists, affinity masks, and optional balancing. Risks include invalid sense type for narrow fields, priority range validation, cpumask interactions with SMP register banks, raw ack mask inversion width, and `BUG()` on unexpected handle function. Test signals are IRQ delivery after unmask, masking and ack clearing, trigger-type programming, priority syscalls/platform code, and SMP affinity behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/chip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/core.c -->
# sources/distributed-fs/ceph-client/drivers/sh/intc/core.c

Purpose: central registration and lifecycle code for SH INTC controllers. It converts platform `struct intc_desc` hardware descriptors into Linux IRQ domains, irq chips, register tables, virtual subgroup mappings, syscore PM hooks, and an `intc` bus device.

Important APIs and functions: exported priority helpers manage default/per-IRQ levels. `register_intc_controller` allocates `intc_desc_int`, maps memory windows, builds register index arrays, allocates priority/sense lists, initializes irqdomain, registers each vector, handles duplicate vectors through chained redirects, initializes subgroups, and records the controller. `intc_suspend/resume` preserve wakeup/enable state around syscore PM. `register_intc_devs` registers syscore ops and exposes controller devices with a `name` attribute.

Control flow: architecture code calls `register_intc_controller` during init. The core maps descriptors, selects mask/priority handles via `handle.c`, installs chip handlers, disables IRQs initially, and then finalizes subgroup data. During suspend/resume it walks active IRQs belonging to each INTC chip.

State and dependencies: global `intc_list`, `intc_big_lock`, controller count, per-IRQ priorities, radix trees, mapped windows, register arrays, domain, and device objects. Dependencies include IRQ core, irqdomain, radix tree, syscore, device model, and descriptor data from platform code. Risks include allocation failure cleanup, `BUG_ON(k > 256)` register encoding limit, descriptor inconsistencies, duplicate vector redirection, no unregister path, and suspend state mismatch. Test signals are controller registration logs, correct IRQ domain associations, interrupt delivery, subgroup finalization, sysfs `intc/name`, and suspend/resume wake IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/handle.c -->
# sources/distributed-fs/ceph-client/drivers/sh/intc/handle.c

Purpose: builds encoded INTC handles from platform hardware descriptor tables. Handles compactly encode register access function, mode, enable/disable register indexes, field width, and field shift.

Important APIs and functions: `intc_get_mask_handle`, `intc_get_prio_handle`, and `intc_get_sense_handle` find fields for an enum id, optionally falling back to group ids. `intc_set_ack_handle` stores per-IRQ ack handles and `intc_get_ack_handle` retrieves them. `intc_enable_disable_enum` applies force-enable/force-disable operations across all matching mask and priority entries before or after IRQ registration.

Control flow: the core calls these helpers during controller registration to select primary/secondary handles, populate priority/sense lists, and configure forced descriptor bits. At runtime chip code consumes the encoded handles through access dispatch tables.

State and dependencies: static `ack_handle[INTC_NR_IRQS]`; descriptor arrays for groups, mask regs, priority regs, sense regs, ack regs; register index table in `intc_desc_int`. Dependencies include handle macros and `intc_get_reg`. Risks are descriptor search state using register/field cursors, group fallback only one level deep, `BUG()` for invalid priority descriptors, and per-IRQ ack array bounds. Test signals are successful mapping of every platform enum id, warning-free registration, force-enable/disable register effects, and ack handling for controllers with pending-clear registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/internals.h -->
# sources/distributed-fs/ceph-client/drivers/sh/intc/internals.h

Purpose: private ABI for the SH INTC implementation. It defines encoded-handle macros, internal descriptor structures, SMP register-bank helpers, and cross-object prototypes.

Important types and macros: `_INTC_MK` packs function, mode, register indexes, field width, and shift into one word; `_INTC_*` macros decode it. `INTC_REG` and `SMP_NR` resolve per-CPU register addresses when SMP metadata is present. `struct intc_desc_int` holds controller runtime state including device, radix tree, raw lock, register arrays, priority/sense lists, windows, irqdomain, irq chip, and suspend flag. `struct intc_map_entry` and `struct intc_subgroup_entry` back enum-to-IRQ and subgroup mappings.

Control flow support: all INTC `.c` files include this header to share helper prototypes and optional feature stubs. `get_intc_desc` recovers controller state from the installed `irq_chip`.

State and dependencies: no standalone runtime state, but it shapes all internal state. Dependencies include IRQ core, irqdomain, radix tree, device model, and `linux/sh_intc.h`. Risks are bitfield width limits, 8-bit register index limits, container lookup assuming chip object embedding, and ABI fragility across all INTC objects. Test signals are compile/link across SMP and non-SMP, optional feature builds, and successful handle decoding under all register widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/internals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/irqdomain.c -->
# sources/distributed-fs/ceph-client/drivers/sh/intc/irqdomain.c

Purpose: IRQ domain support for SH INTC vectored interrupts.

Important APIs and functions: `intc_evt_xlate` translates a firmware/device-tree interrupt specifier into a Linux hardware IRQ using `evt2irq` and sets type to `IRQ_TYPE_NONE`. `intc_irq_domain_init` chooses a linear domain when vector-derived IRQs start at zero and are contiguous; otherwise it creates a tree domain.

Control flow: controller registration calls `intc_irq_domain_init` before associating each IRQ with its domain. Device tree or other domain users can then translate vector specifiers through the domain ops.

State and dependencies: state is the `irq_domain` pointer stored in `intc_desc_int`. Dependencies include IRQ domain APIs, `evt2irq`, and hardware vector ordering in `intc_hw_desc`. Risks are `BUG_ON` if domain allocation fails, wrong linear-domain selection when vectors are sparse, and type information not propagated beyond `IRQ_TYPE_NONE`. Test signals are successful domain creation, association for every vector, xlate of event-vector cells, and boot on sparse/non-zero IRQ bases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/irqdomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/userimask.c -->
# sources/distributed-fs/ceph-client/drivers/sh/intc/userimask.c

Purpose: optional hardware-assisted userspace interrupt masking support for supported SH interrupt blocks.

Important APIs and functions: `register_intc_userimask` maps a 4 KiB user-mask register page and records it globally. Sysfs attribute `userimask` under the `intc` bus root uses `show_intc_userimask` and `store_intc_userimask` to read/write the mask level, writing the required key byte and level field. `userimask_sysdev_init` creates the sysfs file late after the INTC bus exists.

Control flow: platform code registers the hardware address. Late init exposes sysfs. Userspace writes a level lower than the default INTC priority; the register then masks lower-priority hard IRQs for userspace driver scenarios.

State and dependencies: global `uimask` mapping and the `intc_subsys` bus root. Dependencies include MMIO, sysfs/device model, default priority from INTC core, and CPU support. Risks include only one global mapping, no unmap path, strict priority validation, direct raw register writes, and exposing a privileged tuning knob. Test signals are successful registration log, sysfs file creation, readback of written levels, rejection of invalid high levels, and hardware interrupt masking behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/userimask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/virq-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/sh/intc/virq-debugfs.c

Purpose: optional debugfs view of the SH INTC enum-id to Linux IRQ mapping.

Important APIs and functions: `intc_irq_xlate_show` iterates all IRQ numbers, calls `intc_irq_xlate_get`, skips unmapped entries, and prints IRQ, enum id, and chip name. `DEFINE_SHOW_ATTRIBUTE` provides file operations. `intc_irq_xlate_init` creates `debugfs` file `intc_irq_xlate`.

Control flow: `fs_initcall` registers the debugfs file after core infrastructure is available. Reads are generated on demand from the live translation table maintained by `virq.c` and `core.c`.

State and dependencies: no owned state beyond the debugfs dentry. Dependencies include debugfs, seq_file, IRQ core, and INTC translation state. Risks are assuming `entry->desc` is valid for every mapped entry, no explicit dentry cleanup, and debug-only exposure of internal IDs. Test signals are file creation with `CONFIG_INTC_MAPPING_DEBUG`, readable rows after controller registration, and no crashes when sparse IRQ ranges contain unmapped entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/virq-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/virq.c -->
# sources/distributed-fs/ceph-client/drivers/sh/intc/virq.c

Purpose: virtual IRQ subgroup support for SH INTC. It lets one physical parent IRQ fan out to multiple virtual IRQs based on subgroup status bits.

Important APIs and functions: `intc_irq_xlate_set/get` maintain global IRQ-to-enum translation. `intc_irq_lookup` finds an IRQ by chip name and enum id, deferring subgroup VIRQs until allocated. `intc_subgroup_init` inserts pending subgroup entries into the controller radix tree. `intc_finalize` allocates IRQ descriptors for tagged subgroup entries through `intc_subgroup_map`. `intc_virq_handler` masks/acks the parent, tests each virtual bit, dispatches matching virtual IRQs, then unmasks the parent.

Control flow: controller registration inserts normal mappings and subgroup placeholders. Finalization allocates virtual IRQs, configures them with simple handlers and parent chip data, chains the parent handler, and replaces radix entries with real translation entries. Runtime parent interrupts dispatch to active subgroup virtual descriptors.

State and dependencies: global `intc_irq_xlate[INTC_NR_IRQS]`, per-parent linked lists of virtual IRQs in handler data, controller radix tree tags, and subgroup entries. Dependencies include IRQ allocation, radix trees, raw locks, and access dispatch. Risks include memory allocation under init locks, no duplicate virtual entry leak cleanup, parent handler data ownership, non-threadable VIRQs, and failure when no IRQ descriptors remain. Test signals are subgroup setup logs, successful `intc_irq_lookup` before and after finalize, parent-to-virtual interrupt dispatch, and debugfs mapping rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/intc/virq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/maple/Makefile -->
# sources/distributed-fs/ceph-client/drivers/sh/maple/Makefile

Purpose: Kbuild file for the Dreamcast Maple bus core.

Important build rule: `obj-$(CONFIG_MAPLE) := maple.o`, so the Maple bus implementation is built only when `CONFIG_MAPLE` is enabled.

Control flow and integration: the parent SH Makefile descends into this directory for `CONFIG_MAPLE`, and this Makefile contributes the bus core object. Runtime behavior is in `maple.c`.

State and dependencies: no runtime state. Dependencies include the `CONFIG_MAPLE` symbol and Kbuild. Risks are minimal; the main risk is missing this object when Dreamcast Maple drivers depend on exported bus APIs. Test signals are successful link of Maple client drivers and presence of `maple_driver_register` when `CONFIG_MAPLE=y/m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/maple/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/maple/maple.c -->
# sources/distributed-fs/ceph-client/drivers/sh/maple/maple.c

Purpose: Sega Dreamcast Maple bus core. It registers a Linux bus, discovers Maple devices and subdevices, queues Maple packets, drives Maple DMA on VBLANK, and exposes driver registration helpers for Maple client drivers.

Important APIs and functions: exported `maple_driver_register/unregister`, `maple_getcond_callback`, and `maple_add_packet` are the client-facing APIs. `maple_bus_init` registers the bus/root/unsupported driver, allocates DMA buffers and queue cache, requests Maple DMA and VBLANK IRQs, allocates base port devices, and starts initial DEVINFO scans. `maple_send` builds DMA command blocks from `maple_waitq`. `maple_vblank_handler` schedules periodic get-condition and plug-and-play scans. `maple_dma_handler` parses responses, invokes callbacks, registers/detaches devices, and continues scans.

Control flow: IRQ handlers only schedule work. VBLANK work queues commands and triggers DMA; DMA-complete work consumes sent packets, interprets response codes, updates busy flags, attaches/detaches devices, wakes waiters, and starts the next DMA. Device matching checks Maple function bits against driver function masks.

State and dependencies: global wait/sent queues, mutex, DMA buffer pointers, scanning flags, per-port checked/empty/subdevice maps, base unit devices, cache, and root bus. Dependencies include Dreamcast Maple registers, SH DMA/cache primitives, sysasic IRQs, Linux device model, and Maple protocol constants. Risks include global shared state, cache coherency, workqueue/IRQ ordering, PnP false negatives, `free_irq` dev_id mismatch in cleanup paths, and packet buffer ownership. Test signals are bus registration log, initial port scan, device attach/detach, periodic condition callbacks, DMA completion responses, and clean failure-path resource release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/maple/maple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/pm_runtime.c -->
# sources/distributed-fs/ceph-client/drivers/sh/pm_runtime.c

Purpose: SuperH runtime PM glue that attaches the PM clock domain helpers to platform bus devices.

Important APIs and data: `default_pm_domain` uses `USE_PM_CLK_RUNTIME_OPS` and `USE_PLATFORM_PM_SLEEP_OPS`. `platform_bus_notifier` points at that domain and requests the default clock connection id. `sh_pm_runtime_init` registers the notifier with `platform_bus_type` through `pm_clk_add_notifier`.

Control flow: `core_initcall` installs the notifier early. Platform devices can then acquire PM clock runtime operations through the generic PM clock framework.

State and dependencies: static PM domain and notifier block. Dependencies include runtime PM, PM clock helpers, platform device bus, legacy SH clock APIs, and generic PM domains. Risks include applying a default domain to devices with custom PM expectations, missing clocks, and init ordering relative to platform device creation. Test signals are platform device runtime suspend/resume calling clock helpers, no boot-time notifier registration failures, and correct sleep ops for SH platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sh/pm_runtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/siox/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/siox/Kconfig

Purpose: configuration menu for Eckelmann SIOX bus support and its GPIO master.

Important symbols: `SIOX` is a tristate menuconfig for the SIOX bus core. `SIOX_BUS_GPIO` is a tristate child option for bit-banging a SIOX bus over four GPIO lines.

Control flow: enabling `SIOX` builds the core, and enabling `SIOX_BUS_GPIO` builds the platform GPIO master driver. The help text documents that SIOX is a synchronous I/O extension bus used in industrial refrigeration systems.

State and dependencies: no runtime state. Dependencies are Kconfig and the matching Makefile. The GPIO driver implicitly depends on GPIOLIB through its source includes but no explicit Kconfig dependency is declared here. Risks include users selecting GPIO support without the needed GPIO provider in unusual builds. Test signals are Kconfig visibility, module selection for core and GPIO driver, and allmodconfig build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/siox/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/siox/Makefile -->
# sources/distributed-fs/ceph-client/drivers/siox/Makefile

Purpose: Kbuild object selection for SIOX.

Important build rules: `CONFIG_SIOX` builds `siox-core.o`; `CONFIG_SIOX_BUS_GPIO` builds `siox-bus-gpio.o`.

Control flow and integration: client SIOX drivers link against symbols exported by `siox-core.o`, while the GPIO master registers a `siox_master` when its platform device probes.

State and dependencies: no runtime state. Dependencies are Kbuild and Kconfig symbols. Risks are symbol availability if a bus master is built without core support, normally handled by Kconfig menu nesting. Test signals are successful modular and built-in combinations, exported SIOX symbols resolving, and module aliases for the GPIO platform driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/siox/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/siox/siox-bus-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/siox/siox-bus-gpio.c

Purpose: platform SIOX master that implements the synchronous SIOX push/pull cycle using GPIO descriptors for DIN, DOUT, DCLK, and DLD.

Important APIs and functions: `siox_gpio_probe` allocates a managed `siox_master`, obtains GPIOs with `devm_gpiod_get`, sets `smaster->pushpull`, assigns bus number 0, and registers the master. `siox_gpio_pushpull` toggles load and clock lines, shifts bytes out in inverted DOUT form, samples DIN, observes configurable nanosecond delays, and writes received bytes.

Control flow: platform probe binds via OF compatible `eckelmann,siox-gpio`. Once registered, the SIOX core poll thread calls `pushpull` with prepared output and input buffers for each bus cycle. The GPIO routine clocks the longer of set/get byte counts and handles leading/trailing load pulses.

State and dependencies: per-device GPIO descriptors in `siox_gpio_ddata`; module parameters are static delay globals but not exposed as module_param in this file. Dependencies include GPIO consumer API, platform driver core, SIOX core, and `ndelay`. Risks include sleep-capable GPIO calls inside polling context, fixed `busno = 0`, timing accuracy limits, inverted DOUT protocol assumptions, and no automatic delay discovery. Test signals are OF probe, visible `siox-0` master, oscilloscope-valid GPIO waveforms, successful device status synchronization, and error paths for missing GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/siox/siox-bus-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/siox/siox-core.c -->
# sources/distributed-fs/ceph-client/drivers/siox/siox-core.c

Purpose: SIOX bus framework. It registers SIOX masters and devices, maintains a polling thread that exchanges bus frames, interprets status/watchdog/type bits, exposes sysfs controls, and dispatches data to SIOX client drivers.

Important APIs and functions: exported APIs include `siox_device_synced`, `siox_device_connected`, `siox_master_alloc/put/register/unregister`, managed allocation/registration helpers, and `__siox_driver_register`. `siox_poll_thread` periodically calls `siox_poll` while active. `siox_poll` prepares per-device output bytes, runs `smaster->pushpull`, validates readback status, updates sysfs notifications/counters, and invokes driver `set_data/get_data`. Sysfs attributes on masters control `active`, `device_add`, `device_remove`, and `poll_interval_ns`; device attributes expose type, byte counts, status errors, connected, watchdog, and watchdog errors.

Control flow: `subsys_initcall` registers the `siox` bus. Master drivers allocate/register a master and provide `pushpull`. Userspace manually adds supported devices through sysfs. Starting the master wakes the poll thread; polling exchanges one concatenated frame covering all devices in reverse input order and forward output interpretation.

State and dependencies: each `siox_master` owns a lock, active flag, device list, buffer lengths, shared buffer, status counter, last poll, and kthread. Each `siox_device` tracks byte sizes, type, status history, counters, and kernfs nodes. Dependencies include Linux device model, kthreads, sysfs, tracepoints, and the master driver. Risks include manual device model, kthread lifetime leaks because unregister does not visibly stop `poll_thread`, sysfs node references, buffer reallocation while inactive/active, strict support for only `siox-12x8` in `device_add`, and watchdog behavior during unsync. Test signals are bus registration, master/device sysfs operations, active polling at configured interval, trace events, status/watchdog counter changes, driver callbacks, and clean unregister under lockdep/KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/siox/siox-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/siox/siox.h -->
# sources/distributed-fs/ceph-client/drivers/siox/siox.h

Purpose: private SIOX core/master header. It defines the internal `struct siox_master` and helper APIs used by SIOX bus masters and the core.

Important types and APIs: `struct siox_master` contains driver-initialized fields `busno`, `pushpull`, optional `poll_interval`, plus framework-private lock, active flag, owner, embedded device, device list, concatenated buffers, status byte, last poll, and poll thread. `to_siox_master` and `siox_master_get_devdata` map devices to master state and driver-private storage. Declarations cover allocation, managed allocation, register/unregister, and managed register helpers.

Control flow support: bus master drivers allocate a master with extra private data, fill `pushpull` and bus number, then register it. The core owns the embedded device lifetime and polling state after registration.

State and dependencies: this header shapes all master runtime state. Dependencies include kthreads, mutex/list/device fields from kernel headers, and public `linux/siox.h` for device/driver types. Risks are exposing framework-private fields to master drivers, lifetime around `put_device`, and ABI fragility if fields are used outside intended core paths. Test signals are successful compilation of core and GPIO master, correct driver-private data pointer, and register/unregister lifetime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/siox/siox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/slimbus/Kconfig

Purpose: configuration menu for the Linux SLIMbus framework and the Qualcomm NGD controller.

Important symbols: `SLIMBUS` is a tristate bus framework option. `SLIM_QCOM_NGD_CTRL` selects the Qualcomm Satellite Non-Generic Device controller and depends on IOMEM, DMA engine, NET, QCOM remoteproc/common support or COMPILE_TEST fallback, and ARCH_QCOM or COMPILE_TEST. It selects QMI and PDR helper libraries.

Control flow: enabling the framework builds the core/messaging/scheduling/stream objects. Enabling the Qualcomm controller adds its controller implementation, which plugs into the framework APIs.

State and dependencies: no runtime state. Dependencies include Kconfig, SoC support, DMA, QMI/PDR helpers, and remoteproc integration. Risks are complex dependency combinations for compile-test versus real Qualcomm platforms. Test signals are Kconfig resolution, allmodconfig builds, and expected object/module generation for framework-only and Qualcomm-controller configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/slimbus/Makefile

Purpose: Kbuild rules for the SLIMbus framework and controllers.

Important build rules: `CONFIG_SLIMBUS` builds aggregate module/object `slimbus.o` from `core.o`, `messaging.o`, `sched.o`, and `stream.o`. `CONFIG_SLIM_QCOM_NGD_CTRL` builds `slim-qcom-ngd-ctrl.o` from `qcom-ngd-ctrl.o`.

Control flow and integration: common framework objects provide bus registration, messaging, clock scheduling, and stream APIs. Controller objects call framework registration and transfer APIs.

State and dependencies: no runtime state. Dependencies are Kbuild and the selected Kconfig symbols. Risks include aggregate object composition mismatches if APIs move between framework files, and controller link failures when helper symbols are unavailable. Test signals are modular and built-in builds, symbol export resolution for SLIMbus client/controller drivers, and controller module loading on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/core.c -->
# sources/distributed-fs/ceph-client/drivers/slimbus/core.c

Purpose: SLIMbus core device/bus/controller management. It registers the `slimbus` bus, matches client drivers by OF or enumeration address, registers controllers, creates/removes devices, tracks logical addresses, and reports device status.

Important APIs and functions: `slimbus_bus` provides match/probe/remove/uevent callbacks. `__slim_driver_register` and `slim_driver_unregister` manage client drivers. `slim_register_controller` initializes controller IDs, logical-address IDA, transaction IDR, locks, scheduler fields, and registers OF child devices. `slim_unregister_controller` removes child devices. `slim_get_device`, `of_slim_get_device`, `slim_device_report_present`, `slim_get_logical_addr`, and `slim_report_absent` manage device discovery and logical-address validity. `slim_device_probe` runs client probe then obtains a logical address.

Control flow: framework init registers the bus. Controller registration initializes state and creates child devices from DT compatible strings of form `slim<manf>,<prod>` plus `reg` device/instance ids. Client probe defers until logical address assignment succeeds. Report-present either returns an existing logical address or allocates/programs one while runtime PM keeps the controller active.

State and dependencies: global controller IDA; per-controller IDA/IDR, locks, scheduler state, device children; per-device enumeration address, logical address validity, stream list, and status. Dependencies include OF, runtime PM, IDA/IDR, device model, and controller callbacks `get_laddr/set_laddr`. Risks include logical address leaks on some error paths, probe deferral loops, runtime-PM state assumptions, DT parsing strictness, and child removal concurrency. Test signals are bus registration, OF child devices, MODALIAS generation, client probe/status callbacks, report-present address allocation, absent status transitions, and controller unregister removing children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/messaging.c -->
# sources/distributed-fs/ceph-client/drivers/slimbus/messaging.c

Purpose: SLIMbus messaging transaction support. It allocates transaction IDs, sends controller messages, matches asynchronous responses, implements timeouts, and provides read/write helpers for SLIMbus value elements.

Important APIs and functions: `slim_msg_response` is called by controllers when a response arrives; it finds the transaction by TID, copies reply bytes, completes waiters, frees TID, and drops runtime-PM vote. `slim_alloc_txn_tid` and `slim_free_txn_tid` manage TIDs through controller IDR. `slim_do_transfer` handles runtime PM, clock-pause exceptions, optional TID allocation, controller `xfer_msg`, synchronous wait, timeout cleanup, and error logging. `slim_xfer_msg` validates `slim_val_inf`, builds element-code and reply-length fields, and sends value/info messages. Convenience APIs `slim_read`, `slim_readb`, `slim_write`, and `slim_writeb` wrap common value operations.

Control flow: client or framework builds a `slim_msg_txn`, `slim_do_transfer` ensures the controller is active unless in clock-pause reconfiguration, assigns TID when the message class requires a reply, transmits through controller ops, then waits or returns for asynchronous completion. Responses complete via `slim_msg_response`.

State and dependencies: per-controller `tid_idr`, transaction spinlock, runtime PM vote, scheduler clock state, completions, and value buffers. Dependencies include controller `xfer_msg`, `slim_tid_txn`, SLIMbus message constants, runtime PM, and IDR. Risks include TID leak/double free on unusual controller errors, response length unchecked against caller buffer, runtime-PM imbalance, timeout races with late responses, and strict value length/address limits. Test signals are successful read/write byte and multi-byte transfers, timeout handling, async completion path, TID reuse, clock-pause messages, and PM autosuspend balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/messaging.c -->
