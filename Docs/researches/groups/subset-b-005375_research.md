# Group Research: subset-b-005375

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/k3-ringacc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/k3-ringacc.c

## Purpose
This file implements the TI K3 NAVSS Ring Accelerator driver. It provides a shared ring abstraction for K3 DMA, message, and proxy ring users, plus a separate initializer for UDMA-style DMA rings embedded in DMA controllers. The driver owns ring allocation, hardware/TI-SCI programming, coherent ring memory, proxy thread allocation, MSI IRQ mapping for ring events, and push/pop operations over memory, FIFO MMIO, or proxy datapaths.

## Important APIs, Types, And Functions
Core types are `struct k3_ringacc`, `struct k3_ring`, `struct k3_ring_state`, register layout structs, `struct k3_ring_ops`, and SoC match data. Exported APIs include `k3_ringacc_request_ring`, `k3_ringacc_request_rings_pair`, `k3_ringacc_ring_cfg`, `k3_ringacc_ring_free`, `k3_ringacc_ring_reset`, `k3_ringacc_ring_reset_dma`, `k3_ringacc_ring_push`, `k3_ringacc_ring_push_head`, `k3_ringacc_ring_pop`, `k3_ringacc_ring_pop_tail`, `k3_ringacc_get_ring_id`, `k3_ringacc_get_tisci_dev_id`, `k3_ringacc_get_ring_irq_num`, `of_k3_ringacc_get_by_phandle`, and `k3_ringacc_dmarings_init`. Internal operation tables select memory-ring, message-FIFO, proxy, forward-DMA, and reverse-DMA behavior.

## Control Flow
`k3_ringacc_probe` allocates the accelerator, runs SoC init, then publishes it on `k3_ringacc_list` for phandle lookup. `k3_ringacc_init` resolves MSI domain, TI-SCI handle/resource ranges, MMIO resources, proxy counts, ring arrays, and per-ring register windows. Clients request a ring, configure size/mode/element size, and then call push/pop helpers. Configuration allocates coherent memory and sends `ti_sci_rm_ringacc_ops->set_cfg`. Runtime access dispatches through `ring->ops`; pop paths refresh hardware occupancy when local state is empty. Freeing tears down TI-SCI configuration, coherent memory, proxy allocation, flags, and module refs.

## State And Persistence
Runtime state is in memory only: global accelerator list, bitmaps for ring/proxy usage, per-ring use counts, flags, cached occupancy/free counts, ring memory pointers, and indices. Hardware-visible state persists in ring accelerator registers, doorbells, and TI-SCI-managed ring configuration until reset/free. DMA ring reset includes an AM65x SR1.0 quirk that doorbells through the 21-bit occupancy wrap condition before reset.

## Dependencies And Integration Points
The driver depends on device tree properties `ti,num-rings`, `ti,sci`, `ti,sci-dev-id`, and TI-SCI GP ring resources, plus named resources `rt`, `fifos`, `proxy_gcfg`, and `proxy_target`. It integrates with TI-SCI INTA MSI domains, `soc_device_match` revision data, coherent DMA APIs, CPPI5 teardown markers, and K3 UDMA/BCDMA/PKTDMA clients.

## Risks And Test Signals
Key risks are occupancy-cache drift, proxy mode errors, missing MSI domain causing probe deferral, TI-SCI resource mismatches, DMA coherent allocation failures, shared ring misuse, and reset quirks that can hang if doorbell semantics change. Test signals include probe logs with ring/proxy counts, successful TI-SCI set_cfg calls, IRQ lookup via `msi_get_virq`, push/pop behavior for each access mode, DMA teardown marker handling, and stress tests for request/free/shared/proxy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/k3-ringacc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/k3-socinfo.c -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/k3-socinfo.c

## Purpose
This file registers TI K3 SoC identity information on the Linux SoC bus. It reads the CTRLMMR WKUP JTAG ID register, validates the TI manufacturer field, maps the part number to a family name, maps the variant to an SR revision string, and registers a `soc_device_attribute`.

## Important APIs, Types, And Functions
Important data includes the `k3_soc_ids` part-number table and revision maps for J721E and AM62LX. `k3_chipinfo_partno_to_names` resolves `family`, while `k3_chipinfo_variant_to_sr` allocates a revision string. `k3_chipinfo_probe` performs MMIO regmap setup, field extraction, root-node `model` lookup, and `soc_device_register`. The driver is registered at `subsys_initcall` for compatible `ti,am654-chipid`.

## Control Flow
Probe maps resource 0, wraps it with a regmap, reads offset 0, checks `MFG == 0x17`, extracts `variant` and `partno`, allocates attributes, populates family/revision/machine, and registers the SoC device. Errors free allocated strings/attributes before returning.

## State And Persistence
The driver has no mutable global runtime state. Its persistent kernel-visible result is the SoC bus device and strings allocated for `soc_device_attribute`. Hardware state is read-only chip identification.

## Dependencies And Integration Points
It depends on an MMIO chipid node, regmap MMIO, OF root `model`, and Linux `sys_soc`. Other drivers can match revisions using `soc_device_match`; for example, the K3 ring accelerator uses SoC family/revision to enable a DMA reset quirk.

## Risks And Test Signals
Risks include unknown part numbers, variant table gaps, invalid manufacturer fields, and memory leaks if registration fails. Test signals are boot logs like `Family:<name> rev:<SR> JTAGID[...] Detected`, populated `/sys/devices/soc*` fields, and correct `soc_device_match` behavior for AM65X/J721E/AM62-class boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/k3-socinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/knav_dma.c -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/knav_dma.c

## Purpose
This file implements the TI Keystone Navigator packet DMA helper driver. It discovers packet DMA instances from device tree, exposes channel open/close APIs to client drivers, and programs TX channels, RX flows, priorities, queue-manager base addresses, and teardown behavior.

## Important APIs, Types, And Functions
Main structs are `knav_dma_pool_device`, `knav_dma_device`, and `knav_dma_chan`, with register structs for global, channel, TX scheduler, and RX flow blocks. Exported APIs are `knav_dma_device_ready`, `knav_dma_open_channel`, and `knav_dma_close_channel`. Internal helpers include `chan_start`, `chan_stop`, `chan_teardown`, `knav_dma_hw_init`, `knav_dma_hw_destroy`, `of_channel_match_helper`, `pktdma_get_regs`, and `dma_init`.

## Control Flow
`knav_dma_probe` creates a singleton pool device, enables runtime PM, and initializes each child DMA node. `dma_init` maps global/TX/RX/scheduler/flow register windows, reads navigator cloud queue-manager addresses, optional loopback/enable-all settings, timeout, and creates TX channel plus RX flow objects. Clients call `knav_dma_open_channel`, which resolves phandle/name arguments from `ti,navigator-dmas`, finds the DMA instance and channel/flow, checks compatible reuse configuration, initializes DMA hardware on first user, and programs registers. Close decrements channel and device refcounts, stopping the channel and hardware on last user.

## State And Persistence
State is singleton global `kdev`, `device_ready`, per-DMA refcounts, per-channel refcounts and cached config, lists of DMA instances/channels, spinlocks, and debugfs visibility. Hardware state persists in packet DMA registers until stop/destroy or device reset.

## Dependencies And Integration Points
The driver depends on OF properties `ti,navigator-cloud-address`, `ti,navigator-dmas`, `ti,navigator-dma-names`, optional `ti,enable-all`, `ti,loop-back`, and `ti,rx-retry-timeout`. It integrates with Keystone QMSS queue numbering, runtime PM, debugfs, and public `linux/soc/ti/knav_dma.h` clients.

## Risks And Test Signals
Risks include singleton limitations, race potential around global lists without broad locking, refcount underflow on bad close calls, teardown timeout, invalid phandle names, and shared channel config mismatches. Test signals include debugfs `knav_dma`, successful channel open/close cycles, expected register programming for TX/RX directions, teardown timeout absence, and packet traffic through QMSS-backed queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/knav_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/knav_qmss.h -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/knav_qmss.h

## Purpose
This internal header defines the shared data model, register layouts, constants, range operation hooks, and helper macros used by the Keystone Navigator QMSS queue and accumulator drivers.

## Important APIs, Types, And Functions
It defines accumulator command/status constants, descriptor pointer masks, queue/pool/region constants, PDSP control bits, and `RANGE_*` flags. Major structs include `knav_reg_config`, `knav_reg_region`, `knav_reg_pdsp_regs`, `knav_reg_acc_command`, `knav_link_ram_block`, `knav_acc_info`, `knav_acc_channel`, `knav_pdsp_info`, `knav_qmgr_info`, `knav_queue_stats`, `knav_reg_queue`, `knav_region`, `knav_pool`, `knav_queue_inst`, `knav_queue`, `knav_device`, `knav_range_ops`, `knav_irq_info`, and `knav_range_info`. It declares `knav_init_acc_range` and `knav_queue_notify`.

## Control Flow
The header itself has no runtime control flow, but its operation table drives queue-range behavior: generic queue ranges and accumulator-backed ranges supply init/open/close/notify/free callbacks used by `knav_qmss_queue.c`.

## State And Persistence
The structs model persistent driver state for descriptor regions, queues, pools, accumulator lists, PDSP firmware state, queue manager MMIO windows, and per-handle stats. Hardware state is represented by mapped register structs and queue descriptors.

## Dependencies And Integration Points
It includes percpu support and depends on external public Keystone types from `linux/soc/ti/knav_qmss.h` through the C files. It binds the queue and accumulator source files together and should remain private to the driver implementation.

## Risks And Test Signals
Risks are ABI drift between this private model and public client headers, descriptor mask assumptions, fixed accumulator channel/list limits, and packed hardware field assumptions. Test signals are successful builds of both QMSS source files, correct struct field use under sparse/build checks, and runtime queue/accumulator behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/knav_qmss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/knav_qmss_acc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/knav_qmss_acc.c

## Purpose
This file implements accumulator-backed notification support for Keystone QMSS queue ranges. Accumulator firmware running on a PDSP writes descriptor lists into DMA memory and signals interrupts; this driver converts those lists into per-queue software descriptor rings and invokes queue notifiers.

## Important APIs, Types, And Functions
The exported entry point is `knav_init_acc_range`. Range operations are `knav_acc_set_notify`, `knav_acc_init_queue`, `knav_acc_open_queue`, `knav_acc_close_queue`, `knav_acc_init_range`, and `knav_acc_free_range`. Core helpers are `knav_acc_int_handler`, `knav_range_setup_acc_irq`, `knav_acc_write`, `knav_acc_setup_cmd`, `knav_acc_start`, and `knav_acc_stop`.

## Control Flow
`knav_init_acc_range` parses the `accumulator` property, finds a started PDSP, validates channel/pacing/multi-queue constraints, allocates one or more double-buffered accumulator lists, maps them for DMA, and installs accumulator range ops. Queue initialization allocates a 1024-entry software descriptor array. Opening the first queue requests the IRQ. The ISR handles retriggers first, then syncs the active list for CPU access, decodes entries, updates per-queue descriptor arrays and `desc_count`, notifies clients, clears the list, syncs back to device, flips buffers, resets the interrupt count, and writes EOI.

## State And Persistence
State is held in `range->acc`, `knav_acc_channel` list buffers, `list_index`, `open_mask`, `retrigger_count`, per-queue `descs/head/tail/count`, and PDSP command registers. Firmware configuration persists until channel stop/free.

## Dependencies And Integration Points
It depends on PDSP firmware having been loaded and started by the queue driver, IRQ mappings from the queue range, DMA mapping APIs, and `knav_queue_notify`. It is selected per queue range by the presence of the `accumulator` device-tree property and optional `multi-queue`.

## Risks And Test Signals
Risks include unbounded polling in `knav_acc_write`, dropped descriptors when the software ring reaches `ACC_DESCS_MAX`, malformed multi-queue entries, DMA sync mistakes, and IRQ affinity setup failure paths. Test signals include working accumulator IRQ delivery, correct descriptor count changes, notifier callbacks on pending descriptors, firmware command result `success`, and clean IRQ free/unmap during range teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/knav_qmss_acc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/knav_qmss_queue.c -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/knav_qmss_queue.c

## Purpose
This file implements the TI Keystone Queue Manager Subsystem. It creates hardware queues, descriptor regions, descriptor pools, PDSP firmware support, queue range discovery, queue notification, and exported queue/pool APIs used by networking and DMA clients.

## Important APIs, Types, And Functions
Exported APIs include `knav_qmss_device_ready`, `knav_queue_notify`, `knav_queue_open`, `knav_queue_close`, `knav_queue_device_control`, `knav_queue_push`, `knav_queue_pop`, `knav_pool_create`, `knav_pool_destroy`, descriptor virt/DMA conversion, descriptor map/unmap, `knav_pool_desc_get`, `knav_pool_desc_put`, and `knav_pool_count`. Probe helpers cover qmgr mapping, PDSP init/load/start/stop, link RAM, descriptor regions, queue ranges, queue instances, and debugfs.

## Control Flow
Probe allocates singleton `kdev`, enables runtime PM, reads global queue range, initializes queue managers, optionally loads PDSP accumulator firmware, parses queue pools/ranges, configures link RAM, allocates descriptor regions, initializes queue instances, creates debugfs, and marks ready. Queue open selects by type or explicit ID, enforces reserved/shared/exclusive rules under `knav_dev_lock`, creates a handle, sets register windows, and opens range-specific IRQ/accumulator resources for first user. Push writes a packed descriptor pointer/size to the push register. Pop either drains the accumulator software ring or reads the hardware pop register. Pools allocate slices from descriptor regions and back them with a general-purpose queue.

## State And Persistence
Global state includes singleton `kdev`, `device_ready`, queue/region/pool/PDSP/qmgr lists, per-instance handle lists, notifier counts, per-handle percpu stats, descriptor region memory, link RAM, PDSP loaded/started flags, and debugfs output. Hardware state includes queue threshold/pop/push registers, link RAM registers, descriptor region registers, and PDSP IRAM/command/intd state.

## Dependencies And Integration Points
It depends on device-tree children `qmgrs`, `pdsps`, `queue-pools`, `descriptor-regions`, `linkram0`, optional `linkram1`, IRQ specs, and firmware `ks2_qmss_pdsp_acc48.bin`. It integrates with `knav_qmss_acc.c`, runtime PM, debugfs, DMA APIs, and public Keystone QMSS clients.

## Risks And Test Signals
Risks include singleton design, TODO-level remove cleanup, firmware absence disabling accumulator ranges, descriptor-pool fragmentation, IRQ affinity failure leaks, busy queue sharing mistakes, link RAM misconfiguration, and DMA address truncation to 32 bits. Test signals include successful probe logs for qmgrs/regions/PDSPs, debugfs `qmss`, descriptor pool create/destroy, queue push/pop count consistency, accumulator and QPEND notifications, and runtime PM enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/knav_qmss_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/pm33xx.c -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/pm33xx.c

## Purpose
This file implements AM33xx/AM43xx platform power management glue. It copies suspend code and data into SRAM, coordinates EMIF and RTC-only suspend support, communicates with the WKUP M3 firmware, installs platform suspend operations, and invokes SoC-specific PM platform callbacks.

## Important APIs, Types, And Functions
Important functions include `am33xx_push_sram_idle`, `am33xx_do_sram_idle`, `am33xx_pm_suspend`, `am33xx_pm_begin`, `am33xx_pm_end`, `am33xx_pm_set_ipc_ops`, `am33xx_pm_alloc_sram`, `am33xx_pm_rtc_setup`, `am33xx_pm_probe`, and `am33xx_pm_remove`. State comes through `struct am33xx_pm_platform_data`, `struct am33xx_pm_sram_addr`, `struct wkup_m3_ipc`, genalloc SRAM pools, RTC/nvmem scratch registers, and optional GIC distributor mapping for IRQ retriggering.

## Control Flow
Probe verifies machine compatibility, obtains platform PM ops, maps GIC, gets SRAM function addresses, acquires WKUP M3 IPC, allocates code/data SRAM pools, sets up RTC scratch state, copies WFI/EMIF/data tables to SRAM, programs M3 memory type and resume address, registers suspend ops, enables runtime PM, and calls SoC PM init with the SRAM idle callback. Suspend begin prepares M3 for deep sleep or standby. Enter either performs RTC-only/off-mode sequencing or normal SRAM WFI. End finishes low power, clears RTC magic, optionally retriggers RTC IRQ, and calls platform finish hooks.

## State And Persistence
Global state tracks mapped RTC/GIC bases, clocks, SRAM pool addresses, copied SRAM entry point, suspend flags, RTC-only flags, wake source data, and M3 IPC handle. RTC scratch nvmem persists across low-power transitions for bootloader/ROM resume coordination.

## Dependencies And Integration Points
It depends on OMAP/AMx3 platform data, SRAM genalloc nodes, `ti-emif-sram`, `wkup_m3_ipc`, RTC/OMAP RTC helpers, clocks, nvmem, runtime PM, ARM suspend APIs, and SoC compatibility strings `ti,am33xx`/`ti,am43`.

## Risks And Test Signals
Risks include fragile SRAM symbol offset copying, missing M3/EMIF/RTC dependencies causing probe deferral, RTC-only scratch incompatibility, GIC hard-coded AM43xx base, and suspend/resume data corruption. Test signals are successful probe, suspend/resume through standby and mem, M3 PM status 0, correct wake-source logging, RTC-only resume when supported, and no SRAM allocation/free leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/pm33xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/pruss.c -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/pruss.c

## Purpose
This file implements the PRU-ICSS/ICSSG subsystem platform driver. It exposes PRUSS handles and memory-region management to PRU remoteproc clients, maps PRUSS memories and CFG registers, registers clock mux providers, and populates PRU child devices.

## Important APIs, Types, And Functions
Exported APIs are `pruss_get`, `pruss_put`, `pruss_request_mem_region`, `pruss_release_mem_region`, `pruss_cfg_get_gpmux`, `pruss_cfg_set_gpmux`, `pruss_cfg_gpimode`, `pruss_cfg_miirt_enable`, and `pruss_cfg_xfr_enable`. Internal setup functions include `pruss_of_setup_memories`, `pruss_cfg_of_init`, `pruss_clk_init`, and `pruss_clk_mux_setup`. Match data controls absent shared RAM and core clock mux availability.

## Control Flow
Probe sets a 32-bit coherent DMA mask, allocates `struct pruss`, maps DRAM0/DRAM1/shared RAM from the `memories` child, enables runtime PM, maps `cfg`, creates a regmap, registers IEP and optional core clock mux providers from `cfg/clocks`, and populates child devices. `pruss_get` starts from a PRU `rproc`, verifies the parent is a PRU remoteproc, gets the PRUSS platform device data, and increments the PRUSS device refcount. Memory request/release serializes ownership with `pruss->lock`.

## State And Persistence
State is held per PRUSS platform device: memory region metadata, in-use pointers, CFG regmap/base, device pointer, lock, and optional clock muxes managed by devm actions. Hardware CFG changes persist in PRUSS registers until changed or reset.

## Dependencies And Integration Points
It depends on OF child layout `memories`, `cfg`, and `cfg/clocks`, regmap MMIO, runtime PM, remoteproc PRU devices, `linux/pruss_driver.h`, and `pruss.h`. It supports AM335x, AM437x, AM57xx, K2G, AM65x/J721E/AM64x/AM62x compatible strings.

## Risks And Test Signals
Risks include strict DT layout failures, memory ownership leaks if clients fail to release, clock provider cleanup ordering, and invalid mux/mode arguments. Test signals include child PRU devices populated, `pruss_get` from PRU rproc succeeding, memory request returning correct physical/virtual ranges, CFG bit updates visible in registers, and runtime PM transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/pruss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/pruss.h -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/pruss.h

## Purpose
This private header defines PRUSS CFG register offsets, bit masks, and inline regmap helpers used by `pruss.c`.

## Important APIs, Types, And Functions
It defines `PRUSS_CFG_*` offsets, GPCFG GPI/mux masks, MII RT event enable, SPP XFR-shift bits, and inline helpers `pruss_cfg_read` and `pruss_cfg_update`. The helpers validate the PRUSS pointer and call `regmap_read` or `regmap_update_bits`.

## Control Flow
There is no independent runtime flow. Callers in `pruss.c` use these definitions to implement exported PRUSS configuration APIs.

## State And Persistence
State is not stored here, but the helpers operate on `pruss->cfg_regmap`; writes persist in the hardware CFG register block.

## Dependencies And Integration Points
The header depends on `struct pruss` being defined by included public PRUSS driver headers before use, and on Linux regmap. It is an internal bridge between exported PRUSS APIs and CFG register programming.

## Risks And Test Signals
Risks include offset or mask drift against new PRUSS variants and use with an invalid/uninitialized regmap. Test signals are successful compilation, correct GPMUX/GPI/MII/XFR register changes, and no invalid pointer warnings from helper users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/pruss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/smartreflex.c -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/smartreflex.c

## Purpose
This file implements OMAP SmartReflex voltage-control hardware support. It registers SmartReflex instances, exposes configuration APIs to a class driver, handles interrupts, controls automatic voltage compensation, and provides debugfs controls/telemetry.

## Important APIs, Types, And Functions
Exported APIs include `sr_configure_errgen`, `sr_disable_errgen`, `sr_configure_minmax`, `sr_enable`, `sr_disable`, `sr_register_class`, `omap_sr_enable`, `omap_sr_disable`, and `omap_sr_disable_reset_volt`. Important helpers include `_sr_lookup`, `sr_interrupt`, `sr_set_clk_length`, `sr_late_init`, `sr_v1_disable`, `sr_v2_disable`, `sr_retrieve_nvalue_row`, and debugfs autocomp handlers.

## Control Flow
`omap_sr_probe` allocates an `omap_sr`, maps registers, gets optional IRQ and fck clock, copies platform data such as voltage domain, n-value table, sensor mods, limits, and IP type, adds the instance to `sr_list`, performs late init if a class is registered, and creates debugfs files. `sr_register_class` records class callbacks and late-initializes all existing instances. Class code calls configure/enable/disable APIs to program SRCONFIG, ERRCONFIG/IRQ registers, AVGWEIGHT, and NVALUERECIPROCAL. Global OMAP enable/disable APIs look up by voltage domain and delegate to class callbacks when autocomp is active.

## State And Persistence
Global state includes `sr_list`, singleton `sr_class`, and debugfs root. Per-instance state stores register base, clock, IRQ, voltage-domain pointer, n-value data, limits, sensor bits, `enabled`, and `autocomp_active`. Hardware state persists in SmartReflex registers and voltage processor interactions.

## Dependencies And Integration Points
It depends on platform data from OMAP voltage code, `linux/power/smartreflex.h`, voltage-domain APIs, clocks, runtime PM, debugfs, and optional IRQ lines. It integrates with SmartReflex class drivers that supply configure/enable/disable/notify callbacks.

## Risks And Test Signals
Risks include class-driver singleton ordering, platform-data absence, IP-version-specific status bit clearing mistakes, timeout on disable acknowledge, invalid fck rates, and debugfs-modifiable voltage n-values. Test signals include probe logs, debugfs `smartreflex/*/autocomp`, IRQ notification callbacks, successful enable/disable across OPP voltages, and timeout-free v1/v2 disable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/smartreflex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/ti_sci_inta_msi.c -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/ti_sci_inta_msi.c

## Purpose
This file provides MSI-domain helper support for TI SCI Interrupt Aggregator based MSI users. It creates an MSI IRQ domain with TI-SCI INTA bus token semantics and allocates MSI descriptors from TI-SCI resource ranges.

## Important APIs, Types, And Functions
Exported APIs are `ti_sci_inta_msi_create_irq_domain` and `ti_sci_inta_msi_domain_alloc_irqs`. Internal helpers are no-op MSI message callbacks, `ti_sci_inta_msi_update_chip_ops`, and `ti_sci_inta_msi_alloc_descs`.

## Control Flow
Domain creation patches the provided IRQ chip operations to delegate resource, type, mask, unmask, and ack operations to the parent domain, installs no-op compose/write MSI message hooks, enables `MSI_FLAG_FREE_MSI_DESCS`, creates the MSI domain, and marks its bus token as `DOMAIN_BUS_TI_SCI_INTA_MSI`. IRQ allocation requires a nonnegative platform device ID, sets up MSI device data, inserts descriptors for all primary and secondary TI-SCI resource ranges, then allocates all IRQs while holding the MSI descriptors lock.

## State And Persistence
The file stores no global state. State is held in MSI descriptors attached to the device and the created IRQ domain. Firmware resource ranges define the persistent MSI index space.

## Dependencies And Integration Points
It depends on Linux MSI/IRQ-domain core, TI-SCI resource descriptions, platform device IDs, and parent interrupt domains. K3 Ring Accelerator uses it to allocate ring IRQs from `ti,sci-rm-range-gp-rings`.

## Risks And Test Signals
Risks include platform IDs not being set before allocation, descriptor insertion failure requiring cleanup, resource range gaps, and no-op MSI message hooks being inappropriate for non-INTA users. Test signals include domain bus-token lookup success, allocated virqs for each resource index, and downstream `msi_get_virq` returning valid ring interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/ti_sci_inta_msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/wkup_m3_ipc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/wkup_m3_ipc.c

## Purpose
This file implements IPC between the ARM MPU and AM33xx/AM43xx Wakeup M3 remote processor. It exposes PM operations used by `pm33xx.c`, boots the M3 remoteproc asynchronously, exchanges low-power commands through control IPC registers plus mailbox kicks, handles M3 TX events, and reports wake/status information.

## Important APIs, Types, And Functions
Exported APIs are `wkup_m3_ipc_get` and `wkup_m3_ipc_put`. The exposed operation table contains `set_mem_type`, `set_resume_address`, `prepare_low_power`, `finish_low_power`, `request_pm_status`, `request_wake_src`, and `set_rtc_only`. Important helpers include `wkup_m3_copy_aux_data`, `wkup_m3_scale_data_fw_cb`, `wkup_m3_txev_handler`, `wkup_m3_ping`, `wkup_m3_ping_noirq`, IPC register read/write helpers, and probe/remove/PM callbacks.

## Control Flow
Probe maps IPC registers, requests the TXEV IRQ, obtains a mailbox channel, resolves a remoteproc phandle, initializes IPC state and optional VTT/io-isolation/scale-data firmware settings, then starts a kernel thread that boots the remoteproc. The TXEV handler acknowledges the event, transitions state from reset or message states, records firmware version, initializes optional scale data, completes synchronous waits, and reenables TXEV. Low-power preparation writes resume address, command, memory/VTT/isolation/halt flags, optional scale offsets, sets state, and pings the M3. Finish sends reset and waits for completion.

## State And Persistence
Global singleton `m3_ipc_state` provides the shared handle. Per-device state stores mapped IPC memory, mailbox, remoteproc, completion, state enum, firmware options, wake flags, VTT/isolation/halt bits, resume address, memory type, and debugfs path. IPC registers and M3 DMEM hold command and auxiliary data across low-power handshakes.

## Dependencies And Integration Points
It depends on remoteproc, mailbox, firmware loading, debugfs, suspend PM, and OF compatibles `ti,am3352-wkup-m3-ipc` and `ti,am4372-wkup-m3-ipc`. It is consumed directly by AM33xx PM code.

## Risks And Test Signals
Risks include singleton lifetime assumptions, 500 ms sync timeout, missing mailbox/rproc deferral, auxiliary data size not explicitly bounded against firmware size, state-machine desynchronization, and remove paths assuming `m3_ipc_state`. Test signals include CM3 firmware version logs, PM status 0, wake source strings, successful standby/deepsleep/idle pings, debugfs halt control, and RTC-only reboot of remoteproc on resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/wkup_m3_ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ux500/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/ux500/Kconfig

## Purpose
This Kconfig file defines `UX500_SOC_ID`, enabling the ST-Ericsson ux500 SoC bus identity driver.

## Important APIs, Types, And Functions
It is a build configuration stanza, not C code. The symbol is a `bool`, depends on `ARCH_U8500 || COMPILE_TEST`, defaults to `ARCH_U8500`, and describes sysfs SoC information for the ASIC variant.

## Control Flow
When selected, it allows the ux500 Makefile to build `ux500-soc-id.o`. There is no runtime flow in the Kconfig file itself.

## State And Persistence
The symbol persists in kernel configuration and determines whether the driver is compiled in.

## Dependencies And Integration Points
It integrates with the ux500 Makefile and the SoC bus identity code. The help text mentions RealView, which appears to be a stale copy/paste wording for a ux500 option.

## Risks And Test Signals
Risks are incorrect help text and missing `select SOC_BUS` despite the driver using `soc_device_register`. Test signals include `CONFIG_UX500_SOC_ID=y` under U8500 or COMPILE_TEST and successful object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ux500/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ux500/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/ux500/Makefile

## Purpose
This Makefile connects the ux500 SoC identity driver object to its Kconfig symbol.

## Important APIs, Types, And Functions
The key build rule is `obj-$(CONFIG_UX500_SOC_ID) += ux500-soc-id.o`.

## Control Flow
Kbuild includes `ux500-soc-id.o` only when `CONFIG_UX500_SOC_ID` is enabled.

## State And Persistence
There is no runtime state. The persistent effect is the compiled object list.

## Dependencies And Integration Points
It depends on the local Kconfig symbol and the `ux500-soc-id.c` source file.

## Risks And Test Signals
Risks are limited to symbol/file name drift. Test signals are kernel build inclusion/exclusion matching `CONFIG_UX500_SOC_ID`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ux500/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ux500/ux500-soc-id.c -->
# sources/distributed-fs/ceph-client/drivers/soc/ux500/ux500-soc-id.c

## Purpose
This file identifies ST-Ericsson DBx500/ux500 SoCs, prints the ASIC variant, reads a unique SoC ID from backup RAM, contributes that ID to entropy, and registers a SoC bus device with custom `process` sysfs attribute.

## Important APIs, Types, And Functions
Key data is `struct dbx500_asic_id dbx500_id`. Important functions are `ux500_read_asicid`, `ux500_setup_id`, `ux500_print_soc_info`, `ux500_get_machine`, `ux500_get_family`, `ux500_get_revision`, `process_show`, `db8500_read_soc_id`, `soc_info_populate`, and `ux500_soc_device_init`.

## Control Flow
`subsys_initcall` looks for `ste,dbx500-backupram`. If present, `ux500_setup_id` selects an ASIC ID address based on ARM MIDR, reads the register, decodes process/part/revision, and prints it. It then allocates SoC attributes, reads backup RAM UID at offset `0x1fc0`, registers it as `soc_id`, sets family/machine/revision, attaches the process attribute group, and calls `soc_device_register`.

## State And Persistence
Global `dbx500_id` stores decoded identity for sysfs show functions. The registered SoC device and allocated strings persist after init. Hardware identity comes from fixed physical ASIC ID registers and backup RAM UID.

## Dependencies And Integration Points
It depends on ARM CPU ID helpers, ioremap, OF backup RAM, SoC bus, entropy APIs, and early init ordering. It is compiled through `UX500_SOC_ID`.

## Risks And Test Signals
Risks include `BUG()` on unrecognized/zero ASIC ID, hard-coded physical addresses, possible string allocation leaks on some failure paths, and stale platform assumptions. Test signals include boot log `DBxxxx`, populated SoC bus fields, `process` sysfs output, and UID entropy injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ux500/ux500-soc-id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/versatile/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/versatile/Kconfig

## Purpose
This Kconfig file defines build symbols for ARM Integrator core module and ARM RealView SoC bus identity drivers.

## Important APIs, Types, And Functions
It defines `SOC_INTEGRATOR_CM` and `SOC_REALVIEW`, both bool options depending on their respective architectures or `COMPILE_TEST`, and both selecting `SOC_BUS`.

## Control Flow
Selection of each symbol controls whether the corresponding Makefile object is built. There is no runtime control flow here.

## State And Persistence
Configuration state persists in `.config` and determines built-in driver availability.

## Dependencies And Integration Points
The symbols integrate with `soc-integrator.c`, `soc-realview.c`, and Linux SoC bus support.

## Risks And Test Signals
Risks are limited to build dependency drift. Test signals are successful COMPILE_TEST builds and correct object inclusion when each symbol is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/versatile/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/versatile/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/versatile/Makefile

## Purpose
This Makefile maps Versatile-family SoC bus Kconfig symbols to their object files.

## Important APIs, Types, And Functions
It builds `soc-integrator.o` for `CONFIG_SOC_INTEGRATOR_CM` and `soc-realview.o` for `CONFIG_SOC_REALVIEW`.

## Control Flow
Kbuild includes each object according to its config symbol.

## State And Persistence
There is no runtime state. The only persistent effect is build object selection.

## Dependencies And Integration Points
It depends on the local Kconfig file and source filenames.

## Risks And Test Signals
Risks are symbol/file drift. Test signals are expected object inclusion under each config in build logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/versatile/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/versatile/soc-integrator.c -->
# sources/distributed-fs/ceph-client/drivers/soc/versatile/soc-integrator.c

## Purpose
This built-in init file registers SoC bus information for ARM Integrator core modules. It reads the core module ID from a syscon regmap, decodes manufacturer, architecture, FPGA, build, and revision information, and exposes custom sysfs attributes.

## Important APIs, Types, And Functions
Important functions are `integrator_arch_str`, `integrator_fpga_str`, attribute show handlers, and `integrator_soc_init`. The global `integrator_coreid` backs sysfs attributes. The OF match is `arm,core-module-integrator`.

## Control Flow
At `device_initcall`, the driver finds the matching core-module node, converts it to a regmap, reads offset 0, allocates `soc_device_attribute`, fills `soc_id`, `machine`, `family`, and custom attribute group, registers the SoC device, then logs decoded fields.

## State And Persistence
`integrator_coreid` stores the decoded raw ID for attribute reads. The SoC device persists after init. The syscon register is read-only platform identity state.

## Dependencies And Integration Points
It depends on OF, syscon/regmap, SoC bus, and Integrator platform DT. It is built by `SOC_INTEGRATOR_CM`.

## Risks And Test Signals
Risks include failure to unregister on later errors, generic `-ENODEV` returns obscuring causes, and unknown architecture/FPGA values. Test signals include boot logs with decoded core module fields and sysfs attributes `manufacturer`, `arch`, `fpga`, and `build`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/versatile/soc-integrator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/versatile/soc-realview.c -->
# sources/distributed-fs/ceph-client/drivers/soc/versatile/soc-realview.c

## Purpose
This file implements a platform driver that registers SoC bus information for ARM RealView platforms and exposes decoded syscon core ID attributes.

## Important APIs, Types, And Functions
Important functions are `realview_arch_str`, sysfs show handlers, `realview_soc_socdev_release`, and `realview_soc_probe`. The driver matches RealView EB, PB1176, PB11MP, PBA8, and PBX compatibles.

## Control Flow
Probe gets a syscon regmap from the node's `regmap` phandle, allocates devm SoC attributes, reads the first compatible string as `soc_id`, sets machine/family/custom attributes, registers the SoC device, adds a devm unregister action, reads the core ID register, and logs the core ID and HBI board number.

## State And Persistence
Global `realview_coreid` stores the raw ID for sysfs attributes. The SoC device is unregistered automatically by devm action. Hardware identity comes from syscon offset 0.

## Dependencies And Integration Points
It depends on OF platform binding, syscon/regmap, SoC bus, and builtin platform-driver registration through `SOC_REALVIEW`.

## Risks And Test Signals
Risks include global coreid if multiple devices ever existed, registration before core ID read causing attributes to rely on later state, and `of_property_read_string("compatible")` using only the first compatible string. Test signals include successful probe, SoC bus fields, custom attributes `manufacturer`, `board`, `fpga`, and `build`, and boot log with HBI number.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/versatile/soc-realview.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/vt8500/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/vt8500/Kconfig

## Purpose
This Kconfig file defines the VIA/WonderMedia SoC information driver option.

## Important APIs, Types, And Functions
It gates a menu under `ARCH_VT8500 || COMPILE_TEST` and defines `WMT_SOCINFO`, defaulting to `ARCH_VT8500` and selecting `SOC_BUS`.

## Control Flow
When `WMT_SOCINFO` is enabled, the Makefile builds `wmt-socinfo.o`. There is no runtime flow in this file.

## State And Persistence
The selected symbol persists in kernel configuration and controls compile-time inclusion.

## Dependencies And Integration Points
It integrates the VT8500/WonderMedia SoC info C driver with SoC bus support.

## Risks And Test Signals
Risks are mostly dependency drift. Test signals are menu visibility under VT8500 or COMPILE_TEST and successful object build with `CONFIG_WMT_SOCINFO=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/vt8500/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/vt8500/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/vt8500/Makefile

## Purpose
This Makefile links the WonderMedia SoC info object to its Kconfig symbol.

## Important APIs, Types, And Functions
The build rule is `obj-$(CONFIG_WMT_SOCINFO) += wmt-socinfo.o`.

## Control Flow
Kbuild includes `wmt-socinfo.o` when the symbol is enabled.

## State And Persistence
There is no runtime state; it only affects the build graph.

## Dependencies And Integration Points
It depends on `WMT_SOCINFO` and `wmt-socinfo.c`.

## Risks And Test Signals
Risks are limited to symbol/name drift. Test signals are expected inclusion/exclusion during builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/vt8500/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/vt8500/wmt-socinfo.c -->
# sources/distributed-fs/ceph-client/drivers/soc/vt8500/wmt-socinfo.c

## Purpose
This file registers SoC bus information for VIA/WonderMedia VT8500-family systems by reading the SCC ID register and decoding family, revision, and raw SoC ID.

## Important APIs, Types, And Functions
Important data is `chip_id_table`, mapping SCC high-half IDs to chip names. Key functions are `sccid_to_name`, `wmt_socinfo_probe`, and `wmt_socinfo_remove`. It matches `via,vt8500-scc-id`.

## Control Flow
Probe maps the SCC ID register with `devm_of_iomap`, reads `sccid`, allocates SoC attributes, decodes family from bits 31:16, formats revision as letter/digit from low bytes, formats raw `soc_id`, registers the SoC device, logs the result, and stores the `soc_device` for remove. Remove unregisters the SoC device.

## State And Persistence
State is per-platform-device and mostly devm-managed strings plus the registered SoC device. The SCC ID register is hardware identity state.

## Dependencies And Integration Points
It depends on OF, MMIO, platform driver core, and SoC bus. Kconfig selects `SOC_BUS`.

## Risks And Test Signals
Risks include revision decoding producing odd characters for zero or unexpected fields, unknown chip IDs reported generically, and no custom attributes beyond standard SoC bus fields. Test signals include boot log `VIA/WonderMedia <family> rev <rev>`, `/sys/devices/soc*` values, and successful unregister on driver remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/vt8500/wmt-socinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/xilinx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/xilinx/Kconfig

## Purpose
This Kconfig file defines Xilinx SoC driver options for ZynqMP power management and Xilinx event management.

## Important APIs, Types, And Functions
It defines `ZYNQMP_POWER`, depending on `PM && ZYNQMP_FIRMWARE`, selecting mailbox/IPI mailbox support, and `XLNX_EVENT_MANAGER`, depending on and defaulting to `ZYNQMP_FIRMWARE`.

## Control Flow
The symbols control object inclusion from the Makefile. Help text explains firmware-backed power/event callback support.

## State And Persistence
Configuration state persists in `.config` and determines compiled driver availability.

## Dependencies And Integration Points
It integrates Xilinx firmware, mailbox infrastructure, and the event manager driver. `ZYNQMP_POWER` corresponds to `zynqmp_power.o`; `XLNX_EVENT_MANAGER` corresponds to `xlnx_event_manager.o`.

## Risks And Test Signals
Risks include help text typo `ZyqnMP` and dependency mismatch if firmware APIs change. Test signals are successful builds for each symbol and expected object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/xilinx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/xilinx/Makefile

## Purpose
This Makefile maps Xilinx SoC Kconfig options to object files.

## Important APIs, Types, And Functions
It builds `zynqmp_power.o` for `CONFIG_ZYNQMP_POWER` and `xlnx_event_manager.o` for `CONFIG_XLNX_EVENT_MANAGER`.

## Control Flow
Kbuild includes each object based on its config symbol.

## State And Persistence
There is no runtime state; the Makefile affects build selection only.

## Dependencies And Integration Points
It depends on Xilinx Kconfig symbols and matching source files.

## Risks And Test Signals
Risks are object/symbol drift. Test signals are expected object build under enabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/xilinx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/xilinx/xlnx_event_manager.c -->
# sources/distributed-fs/ceph-client/drivers/soc/xilinx/xlnx_event_manager.c

## Purpose
This file implements the Xilinx firmware event management driver. It lets client drivers register callbacks for firmware notify events or suspend-init callbacks, receives firmware callbacks through an SGI, dispatches callbacks from an in-kernel hash table, and re-registers one-shot notifications with firmware.

## Important APIs, Types, And Functions
Exported APIs are `xlnx_register_event` and `xlnx_unregister_event`. Main internal types are `struct registered_event_data` and `struct agent_cb`. Important helpers include `xlnx_is_error_event`, add/remove callback helpers, `xlnx_call_notify_cb_handler`, `xlnx_call_suspend_cb_handler`, `xlnx_event_handler`, SGI init/cleanup helpers, CPU hotplug callbacks, and probe/remove.

## Control Flow
Probe checks `PM_REGISTER_NOTIFIER` firmware feature/version, maps SGI 15 or module-param `sgi_num` through the GIC IRQ domain, requests a percpu IRQ, registers CPU hotplug enable/disable callbacks, registers the SGI with firmware, and sets availability to 0. Registration validates callback type/function, adds callback data to `reg_driver_map`, splits error-event bitmasks into single-event keys for Versal/Versal Net error nodes, and calls `zynqmp_pm_register_notifier`. The IRQ handler fetches callback payload via `GET_CALLBACK_DATA`, dispatches notify or suspend callbacks, splits error masks if needed, and re-registers notify events for future delivery. Remove frees all hash/list entries, unregisters SGI, removes hotplug state, frees percpu IRQ, and marks unavailable.

## State And Persistence
Global state includes `virq_sgi`, `event_manager_availability`, `sgi_num`, `is_need_to_unregister`, and hash table `reg_driver_map`. Each event stores key, callback type, wake flag, and callback list. Firmware notifier registrations persist until unregistered or driver removal.

## Dependencies And Integration Points
It depends on ZynqMP/Versal firmware APIs, GIC IRQ domain SGI mapping, percpu IRQs, CPU hotplug, Linux hashtable/list helpers, and public `linux/firmware/xlnx-event-manager.h`. Kconfig requires `ZYNQMP_FIRMWARE`.

## Risks And Test Signals
Risks include limited locking around hash/list mutation versus IRQ dispatch, global `is_need_to_unregister` semantics across multi-bit unregisters, SGI mapping assumptions, one-shot firmware notifier re-registration failures, and availability returning `-EACCES` before probe. Test signals include probe logs for SGI registration, successful callback registration/unregistration, callbacks firing for normal and error events, CPU hotplug enable/disable coverage, and clean remove freeing notifier state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/xilinx/xlnx_event_manager.c -->
