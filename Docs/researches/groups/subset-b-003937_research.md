# subset-b-003937 research

This grouped report covers the requested Intel IRDMA HMC, hardware initialization, generation adapter, PBLE, and common header files. Each section preserves the source path in its title and is wrapped for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/hmc.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/hmc.c

## Purpose
`hmc.c` implements Host Memory Cache backing-store management for IRDMA resources. It calculates segment descriptor (SD) and page descriptor (PD) ranges for HMC object types, allocates DMA-coherent backing pages, publishes SD entries through the CQP path, invalidates hardware PD caches, and tears objects down with use-count checks.

## Important APIs, types, and functions
The exported control points are `irdma_sc_create_hmc_obj`, `irdma_sc_del_hmc_obj`, `irdma_hmc_sd_one`, `irdma_add_sd_table_entry`, `irdma_add_pd_table_entry`, `irdma_remove_pd_bp`, `irdma_prep_remove_sd_bp`, and `irdma_prep_remove_pd_page`. Internal helpers `irdma_find_sd_index_limit` and `irdma_find_pd_index_limit` translate an object range into SD/PD limits using object `base`, `size`, and count. `irdma_set_sd_entry` and `irdma_clr_sd_entry` encode the hardware SD update payload.

## Control flow, state, and persistence
Creation validates object bounds, skips Gen3+ local-memory objects, derives SD and PD ranges, allocates any missing SD table entries, optionally allocates PD backing pages, records SD indexes to program, marks SDs valid, and commits the additions with `process_cqp_sds`. Deletion first removes valid paged backing pages, then prepares SD invalidation for direct or paged SDs, optionally frees PBLE PD metadata for VF/PBLE HMC info, sends SD clear commands when privileged and not resetting, and finally frees DMA memory. Runtime state persists only in kernel memory: `hmc_info->sd_table`, `sd_entry->valid`, PD table use counts, and DMA addresses. Hardware persistence is the programmed SD/PD view until cleared or reset.

## Dependencies and integration points
The file depends on HMC types from `hmc.h`, register bit definitions from `irdma.h`/`defs.h`, CQP methods through `struct irdma_sc_dev`, coherent DMA allocation, and privileged PF register writes for PD invalidation. PBLE setup in `pble.c` reuses `irdma_add_sd_table_entry`, `irdma_add_pd_table_entry`, and `irdma_hmc_sd_one`.

## Risks and test signals
Key risks are off-by-one range math, SD index overflow, stale valid bits after partial allocation failure, unbalanced `use_cnt`, and invalidation index mistakes. Useful tests are fault injection in DMA/kzalloc paths, create/delete of ranges spanning SD boundaries, paged versus direct SD cases, PBLE-specific HMC info deletion, Gen3 local-memory skip behavior, and reset teardown where CQP SD clear is intentionally bypassed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/hmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/hmc.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/hmc.h

## Purpose
`hmc.h` defines the HMC object model used by the IRDMA control plane. It gives names, constants, SD/PD table structures, create/delete request structures, and function prototypes for programming host memory backing for queues, MRs, PBLEs, timers, and other hardware objects.

## Important APIs, types, and functions
Important constants include SD/PD geometry such as `IRDMA_HMC_MAX_BP_COUNT`, `IRDMA_HMC_PD_CNT_IN_SD`, `IRDMA_HMC_DIRECT_BP_SIZE`, `IRDMA_HMC_PAGED_BP_SIZE`, and `IRDMA_HMC_MAX_SD_COUNT`. `enum irdma_hmc_rsrc_type` enumerates object classes, with `IRDMA_HMC_IW_MAX` as the table size. `struct irdma_hmc_info` owns the object table and SD table; `struct irdma_hmc_sd_entry`, `struct irdma_hmc_pd_table`, and `struct irdma_hmc_pd_entry` describe the host-side mirror of hardware descriptors.

## Control flow, state, and persistence
The header itself has no control flow but defines the state persisted across control initialization and runtime allocations: object counts/bases/sizes, function id, SD entries, PD tables, and cached SD indexes used to batch CQP programming. Create/delete info structures carry one operation's range, object type, selected SD entry type, and counts of SDs to add or delete.

## Dependencies and integration points
It includes `defs.h` and refers to `struct irdma_hw`, `struct irdma_sc_dev`, DMA memory wrappers from `osdep.h`, and CQP-facing update structures. It is consumed by `hmc.c`, `hw.c`, `pble.c`, and lower-level control code that configures FPM values.

## Risks and test signals
The main risk is contract drift: constants and enum order must match firmware/hardware FPM layouts and CQP encodings. Tests should verify table sizes, SD/PD geometry assumptions, object enum count handling, and that all code using `sd_indexes` respects `IRDMA_HMC_MAX_SD_COUNT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/hmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/hw.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/hw.c

## Purpose
`hw.c` is the main IRDMA control/runtime hardware orchestration file. It creates and destroys CQP, CCQ, CEQs, AEQ, HMC objects, PBLE resources, VSI runtime state, iWARP PUDA queues, resource bitmaps, local MAC/ARP/APBVT entries, qhash entries, and QP flush/AE control operations.

## Important APIs, types, and functions
Public entry points include `irdma_ctrl_init_hw`, `irdma_ctrl_deinit_hw`, `irdma_rt_init_hw`, `irdma_rt_deinit_hw`, `irdma_initialize_hw_rsrc`, `irdma_cqp_ce_handler`, `cqp_compl_worker`, `irdma_next_iw_state`, `irdma_manage_arp_cache`, `irdma_manage_qhash`, `irdma_hw_flush_wqes`, `irdma_gen_ae`, and `irdma_flush_wqes`. Important internal paths include AEQ/CEQ processing, CQP/CCQ/CEQ/AEQ creation and destruction, HMC setup, PBLE initialization, and APBVT/local MAC management.

## Control flow, state, and persistence
Control initialization proceeds through `irdma_ctrl_init_hw`: setup init memory, create CQP, query features, configure HMC/FPM and HMC objects, initialize resource bitmaps, create CCQ, create CEQ0 and extra CEQs, initialize PBLE chunks, and create/configure AEQ. Each completed phase updates `rf->init_state`, allowing `irdma_ctrl_deinit_hw` to fall through in reverse order after failures or unload. Runtime initialization initializes VSI state, CM core, stats, iWARP ILQ/IEQ if needed, MAC/IP state, cleanup workqueue, and used-resource counters. Interrupt flow moves from IRQ handler to tasklet to CEQ/AEQ polling, CQP completion worker, QP event dispatch, and user callbacks. State persists in `struct irdma_pci_f`, `struct irdma_device`, HMC/PBLE tables, resource bitmaps, CM hashes, and workqueues until teardown.

## Dependencies and integration points
`hw.c` depends on generation-specific data installed in `rf->gen_ops`, `dev->irq_ops`, register maps, HMC functions, PBLE functions, CQP/CCQ/CEQ/AEQ low-level routines, RDMA core ibdev event callbacks, netdev state, workqueues, tasklets, spinlocks, and auxiliary driver setup. Gen1, Gen2, and Gen3 interface files all converge on `irdma_ctrl_init_hw` and Gen1/Gen2/vport paths call `irdma_rt_init_hw`.

## Risks and test signals
Highest-risk areas are partial initialization cleanup, asynchronous AEQ/CEQ races with CQ/QP deletion, CQP request lifetime and deferred completion, flush retry edge cases, shared versus dedicated MSI-X vector indexing, and reset paths that bypass hardware commands. Test signals include staged failure injection at every `init_state`, interrupt storm and stale CEQE scenarios, qhash/APBVT add-delete races, QP flush with new SQ work posted during flush, RoCE versus iWARP mode coverage, and Gen1/Gen2/Gen3 hardware capability differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/i40iw_hw.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/i40iw_hw.c

## Purpose
`i40iw_hw.c` provides the Gen1/i40e hardware register map, interrupt operations, statistics layout, masks/shifts, and capability defaults for the common IRDMA core.

## Important APIs, types, and functions
The exported API is `i40iw_init_hw`. Local helpers `i40iw_config_ceq`, `i40iw_ena_irq`, and `i40iw_disable_irq` implement Gen1 interrupt programming. Static tables map `IRDMA_MAX_REGS`, hardware statistics offsets, CQP masks, and shifts to i40e register definitions.

## Control flow, state, and persistence
`i40iw_init_hw` fills `dev->hw_regs` from `i40iw_regs`, treating the doorbell offset as a special non-MMIO base, installs stat offsets and hardware masks/shifts, assigns doorbell pointers, installs `i40iw_irq_ops`, and sets Gen1 capability limits. Hardware state changes happen through interrupt configuration writes, while software state persists in `struct irdma_sc_dev` attribute and register pointer fields.

## Dependencies and integration points
This file depends on `i40iw_hw.h` register definitions and common register enum ordering from `irdma.h`. It integrates with `irdma_sc_dev_init`, generic queue setup in `hw.c`, and Gen1 auxiliary setup in `i40iw_if.c`.

## Risks and test signals
Risks are incorrect register offsets, vector index off-by-one behavior, mismatched CQP field masks, and stale Gen1 capability limits. Tests should verify CEQ interrupt enable/disable register writes, stat collection offsets, CQP create/destroy status bit handling, and that Gen1 uses the expected lower capability limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/i40iw_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/i40iw_hw.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/i40iw_hw.h

## Purpose
`i40iw_hw.h` contains Gen1 i40e PF/VF register offsets, bit masks, shift definitions, doorbell offsets, interrupt constants, and hardware capability constants.

## Important APIs, types, and functions
The header exports `i40iw_init_hw`. Key definitions include PF/VF PE queue registers, `I40E_PFINT_*` interrupt registers, `I40E_GLPES_*` statistics registers, CQP status masks, CQ/CEQ field masks, and `enum i40iw_device_caps_const`.

## Control flow, state, and persistence
There is no runtime control flow. The file is a compile-time hardware contract consumed by `i40iw_hw.c`; its values become persistent runtime register pointers and attribute limits after `i40iw_init_hw`.

## Dependencies and integration points
It relies on Linux bit macros and common IRDMA constants from included users. It is tightly coupled to `i40iw_hw.c` table ordering and the common `enum irdma_registers`, `enum irdma_masks`, and `enum irdma_shifts`.

## Risks and test signals
The main risk is register or mask drift versus i40e hardware specifications. Test signals include read/write smoke tests on interrupt and CQP registers, capability exposure checks through RDMA core, and compile-time/table-size validation when common enum entries change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/i40iw_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/i40iw_if.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/i40iw_if.c

## Purpose
`i40iw_if.c` connects the IRDMA driver to the i40e auxiliary/client interface for Gen1 iWARP devices. It handles client probe/remove, open/close, L2 parameter changes, reset requests, device-info population, control/runtime hardware bring-up, and IB device registration.

## Important APIs, types, and functions
Important local functions are `i40iw_l2param_change`, `i40iw_close`, `i40iw_request_reset`, `i40iw_fill_device_info`, `i40iw_open`, `i40iw_probe`, and `i40iw_remove`. The file exports `struct auxiliary_driver i40iw_auxiliary_drv` for module registration.

## Control flow, state, and persistence
Probe registers an i40e RDMA client. The i40e client `open` callback allocates `irdma_device` and `irdma_pci_f`, fills Gen1 PF-only iWARP state, runs `irdma_ctrl_init_hw`, builds L2 parameters from i40e QoS data, runs `irdma_rt_init_hw`, and registers the IB device. Close marks reset if requested, clears status, emits an IB port event, and unregisters the IB device. Runtime state is held in `iwdev`, `rf`, i40e client data, and the registered ibdev lifetime.

## Dependencies and integration points
The file depends on `<linux/net/intel/i40e_client.h>`, Gen1 hardware constants, common `main.h` APIs, and RDMA core device lookup by netdev. It integrates with i40e-provided MSI-X vectors, netdev, QoS parameters, and reset operations.

## Risks and test signals
Risks include missing ibdev during close/L2 callbacks, error unwind leaks between control/runtime init, incorrect DCB VLAN mode detection, and reset ordering with i40e. Tests should cover open failure at each stage, close with and without reset, MTU change propagation, QoS mapping, and module probe/remove cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/i40iw_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/icrdma_hw.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/icrdma_hw.c

## Purpose
`icrdma_hw.c` provides the Gen2/E810-style hardware register map, interrupt operations, statistics layout, masks/shifts, and capability flags for the shared IRDMA core.

## Important APIs, types, and functions
The exported API is `icrdma_init_hw`. Local helpers `icrdma_ena_irq`, `icrdma_disable_irq`, and `icrdma_cfg_ceq` implement interrupt programming. Static arrays map common register, mask, shift, and stat indexes to Gen2 definitions.

## Control flow, state, and persistence
`icrdma_init_hw` populates MMIO pointers, masks, shifts, doorbell addresses, IRQ ops, page-size capabilities, statistics metadata, RDMA read/write limits, push-page limits, minimum WQ size, SQ chunking, and feature flags such as RTS AE and CQ resize. IRQ enable uses CEQ interrupt moderation when configured and handles Gen1-style indexing only as a compatibility branch.

## Dependencies and integration points
The file depends on `icrdma_hw.h`, common register enums in `irdma.h`, CQP/CEQ code in `hw.c`, and Gen2 auxiliary setup in `icrdma_if.c`. It provides hardware attributes later consumed by verbs, queue setup, and HMC sizing.

## Risks and test signals
Risks include incorrect field masks, interrupt moderation interval units, vector indexing, and stat map offsets with mixed 24/32/48/56-bit counters. Tests should validate interrupt enable/disable writes, CEQ mapping, stats reads, feature flag exposure, and behavior with configured `ceq_itr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/icrdma_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/icrdma_hw.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/icrdma_hw.h

## Purpose
`icrdma_hw.h` defines Gen2 IRDMA register offsets, doorbell offsets, CQP field masks/shifts, and capability constants used by `icrdma_hw.c`.

## Important APIs, types, and functions
The header exports `icrdma_init_hw`. Important definitions include PF/VF queue registers, `GLINT_DYN_CTL`, `GLINT_CEQCTL`, `VSIQF_PE_CTL1`, HMC invalidation registers, `GLINT_RATE`, CQP status and field masks, and `enum icrdma_device_caps_const`.

## Control flow, state, and persistence
There is no runtime control flow; it provides compile-time constants that become the runtime `hw_regs`, `hw_masks`, `hw_shifts`, and capability attributes after initialization.

## Dependencies and integration points
It includes `irdma.h`, so its masks are tied to the common register/mask/shift enum ordering. It is used by the Gen2 hardware adapter and indirectly by common control initialization.

## Risks and test signals
Risks are duplicated or stale definitions, wrong CQP bit positions, and mismatched register offsets. Test signals include CQP command encode/decode validation, interrupt register smoke tests, and capability checks for ORD/IRD and push-page limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/icrdma_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/icrdma_if.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/icrdma_if.c

## Purpose
`icrdma_if.c` connects Gen2 IRDMA to the ice IIDC RDMA auxiliary interface. It handles QoS and MTU events, critical error reset requests, LAN qset registration, MSI-X vector allocation, device-info population, control/runtime initialization, IB registration, and remove cleanup.

## Important APIs, types, and functions
Important functions are `icrdma_prep_tc_change`, `icrdma_fill_qos_info`, `icrdma_iidc_event_handler`, `icrdma_lan_register_qset`, `icrdma_lan_unregister_qset`, `icrdma_request_reset`, `icrdma_init_interrupts`, `icrdma_deinit_interrupts`, `icrdma_fill_device_info`, `icrdma_probe`, and `icrdma_remove`. The exported object is `icrdma_core_auxiliary_drv`.

## Control flow, state, and persistence
Probe allocates `irdma_device` and `irdma_pci_f`, fills Gen2 PF state, allocates RDMA qvectors from ice, runs control initialization, derives L2 parameters from IIDC QoS, runs runtime initialization, registers the IB device, enables the VSI filter, and stores drvdata. Event handling updates MTU, suspends QPs before TC changes, rebuilds QoS after TC changes, and requests reset on critical PE/HMC/push errors. Remove disables the VSI filter, unregisters the IB device, frees qvectors, destroys AH locking, and frees `rf`.

## Dependencies and integration points
The file depends on `<linux/net/intel/iidc_rdma_ice.h>`, ice RDMA qvector/qset APIs, common `main.h`, work scheduler handling, and RDMA core registration. It bridges LAN traffic-class scheduling with IRDMA work scheduler nodes.

## Risks and test signals
Risks include timeout while waiting for QP suspend, qvector partial allocation cleanup, TC-change races, reset requests on recoverable critical events, and qset TEID lifetime. Tests should simulate MTU/TC/critical events, verify qset register/unregister calls, inject qvector allocation failures, and exercise iWARP versus RoCE protocol selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/icrdma_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ig3rdma_hw.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ig3rdma_hw.c

## Purpose
`ig3rdma_hw.c` provides Gen3 hardware capability defaults, statistics layout, interrupt enable/disable operations, and register-offset-to-MMIO-region resolution for IDPF-backed devices.

## Important APIs, types, and functions
The exported APIs are `ig3rdma_init_hw` and `ig3rdma_get_reg_addr`. Local helpers `ig3rdma_ena_irq`, `ig3rdma_disable_irq`, and `__ig3rdma_get_reg_addr` implement interrupt register selection and MMIO lookup.

## Control flow, state, and persistence
`ig3rdma_init_hw` installs Gen3 IRQ ops and stats map, sets WQE/SGE limits, enables 64-byte CQE, CQE timestamping, SRQ, RTS AE, and CQ resize features, configures page-size and push-page limits, and records Gen3 stat index bounds. Register lookup first checks the RDMA MMIO window, then extra IO regions exposed by the core device.

## Dependencies and integration points
It depends on Gen3 constants in `ig3rdma_hw.h`, common `irdma_hw` region fields configured by `ig3rdma_if.c`, and generic register-access helpers that can call `ig3rdma_get_reg_addr`.

## Risks and test signals
Risks include PF/VF interrupt stride mistakes, missing MMIO region coverage, WARNs on valid offsets after firmware layout changes, and feature flags advertised before all dependent paths are ready. Tests should cover PF and VF vector writes, register lookup across primary and auxiliary regions, stats reads through the Gen3 map, and capability exposure for SRQ and timestamped CQEs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ig3rdma_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ig3rdma_hw.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ig3rdma_hw.h

## Purpose
`ig3rdma_hw.h` defines Gen3 RDMA MMIO window geometry, PF/VF count constants, hardware capability constants, and prototypes for Gen3 register lookup and virtual-channel send.

## Important APIs, types, and functions
Important definitions include `IG3_PF_RDMA_REGION_OFFSET`, `IG3_PF_RDMA_REGION_LEN`, `IG3_VF_RDMA_REGION_OFFSET`, `IG3_VF_RDMA_REGION_LEN`, `enum ig3rdma_device_caps_const`, `ig3rdma_get_reg_addr`, and `ig3rdma_vchnl_send_sync`.

## Control flow, state, and persistence
No runtime control flow exists in the header. Its constants are applied during Gen3 core probe when MMIO regions are mapped and during hardware initialization when limits are copied into `dev->hw_attrs`.

## Dependencies and integration points
The header is consumed by Gen3 hardware and interface files. `ig3rdma_vchnl_send_sync` is implemented in `ig3rdma_if.c` and used by common virtual-channel code through the generation setup.

## Risks and test signals
Risks are stale region offsets/lengths, PF/VF capability mismatch, and push-page limit exposure errors. Tests should verify PF and VF region mapping, virtual-channel timeout handling, and max inline/IRD/ORD/resource attributes reported to verbs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ig3rdma_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ig3rdma_if.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ig3rdma_if.c

## Purpose
`ig3rdma_if.c` manages the Gen3 IDPF core auxiliary device. It initializes virtual-channel support, maps RDMA MMIO regions, configures the shared `irdma_pci_f`, starts the common control hardware path, and enables or disables vport device creation through IDPF.

## Important APIs, types, and functions
Important functions are `ig3rdma_idc_core_event_handler`, `ig3rdma_vchnl_send_sync`, `ig3rdma_vchnl_init`, `ig3rdma_request_reset`, `ig3rdma_cfg_regions`, `ig3rdma_decfg_rf`, `ig3rdma_cfg_rf`, `ig3rdma_core_probe`, and `ig3rdma_core_remove`. The exported driver object is `ig3rdma_core_auxiliary_drv`.

## Control flow, state, and persistence
Core probe allocates `irdma_pci_f`, initializes virtual-channel state and workqueue, maps the PF or VF RDMA window plus additional memory regions, sets protocol and reset operations, runs `irdma_ctrl_init_hw`, saves drvdata, and asks IDPF to enable vport devices. Remove disables vport devices, deinitializes control hardware, unmaps/free regions and locks, destroys workqueues, and frees `rf`. Reset warning events mark `rf->reset` and clear virtual-channel availability.

## Dependencies and integration points
The file depends on `<linux/net/intel/iidc_rdma_idpf.h>`, IDPF virtual-channel and reset APIs, common IRDMA control initialization, Gen3 hardware region definitions, and `main.c` vport probe for runtime device creation.

## Risks and test signals
Risks include virtual-channel timeout leaving control paths blocked, MMIO leaks on partial setup failure, core/vport lifetime ordering, and function type misclassification. Tests should cover PF/VF region setup, virtual-channel timeout and recovery, core probe failure injection, vport enable/disable sequencing, and reset-warning event handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ig3rdma_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/irdma.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/irdma.h

## Purpose
`irdma.h` is the common hardware register and capability contract shared across IRDMA generations. It defines generic register enum slots, common bit masks, shift/mask table indexes, multicast context structures, hardware generation enum values, and hardware attribute structures.

## Important APIs, types, and functions
Important definitions include `enum irdma_registers`, `enum irdma_shifts`, `enum irdma_masks`, `enum irdma_vers`, `struct irdma_uk_attrs`, `struct irdma_hw_attrs`, and multicast group context structures. It declares `i40iw_init_hw`, `icrdma_init_hw`, `ig3rdma_init_hw`, and `ig3rdma_get_reg_addr`.

## Control flow, state, and persistence
There is no executable flow. The enum order is persistent ABI within the driver because generation-specific files fill arrays indexed by these enums and common code reads register pointers and masks through the same indexes.

## Dependencies and integration points
This header is included by generation hardware headers and common type/control code. It bridges hardware-specific register maps with common CQP, interrupt, HMC, statistics, and verbs capability logic.

## Risks and test signals
Risks are enum/table ordering drift, bit mask width mistakes, and capability fields being interpreted differently by user/kernel paths. Tests should include table-size validation, generation init smoke tests, and verbs capability checks across Gen1, Gen2, and Gen3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/irdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/main.c

## Purpose
`main.c` is the module entry/exit and Gen3 vport integration file. It registers network notifiers, exposes module metadata, handles Gen3 vport auxiliary probe/remove and MTU events, and registers/unregisters all generation auxiliary drivers.

## Important APIs, types, and functions
Important functions include `irdma_register_notifiers`, `irdma_unregister_notifiers`, `irdma_log_invalid_mtu`, `ig3rdma_idc_vport_event_handler`, `ig3rdma_vport_probe`, `ig3rdma_vport_remove`, `irdma_init_module`, and `irdma_exit_module`. It registers Gen1 `i40iw_auxiliary_drv`, Gen2 `icrdma_core_auxiliary_drv`, Gen3 core, and Gen3 vport drivers.

## Control flow, state, and persistence
Module init registers auxiliary drivers in order and unwinds earlier registrations if a later registration fails, then registers IP/netdevice notifiers. Gen3 vport probe retrieves the already-initialized core `rf`, allocates an `irdma_device`, fills vport/netdev/RoCE defaults, runs runtime initialization, registers the IB device, and stores drvdata. Vport remove unregisters the IB device. Module exit unregisters notifiers and all auxiliary drivers.

## Dependencies and integration points
The file depends on Linux auxiliary bus, IDPF vport IIDC APIs, network notifier callbacks implemented elsewhere, and common runtime init/IB registration paths. It links Gen3 core setup from `ig3rdma_if.c` to per-vport runtime devices.

## Risks and test signals
Risks include registration/unregistration ordering, missing cleanup when `ib_alloc_device` fails, core drvdata absence during vport probe, notifier callbacks after device removal, and MTU warning correctness. Tests should cover module init failure unwinds, vport probe/remove, MTU events, notifier registration lifecycle, and Gen3 core-before-vport ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/main.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/main.h

## Purpose
`main.h` is the central private header for the IRDMA Linux driver. It gathers Linux/RDMA includes, shared constants, initialization state enums, control queue structures, interrupt/event queue wrappers, resource tracking, generation callbacks, primary device structures, inline conversion helpers, resource bitmap helpers, and cross-file prototypes.

## Important APIs, types, and functions
Important types are `enum init_completion_state`, `struct irdma_cqp_request`, `struct irdma_cqp`, `struct irdma_ccq`, `struct irdma_ceq`, `struct irdma_aeq`, `struct irdma_pci_f`, `struct irdma_device`, and `struct irdma_gen_ops`. Inline helpers include `to_iwdev`, `to_iwqp`, `dev_to_rf`, `irdma_alloc_rsrc`, and `irdma_free_rsrc`. It prototypes major control/runtime APIs, CQP operations, CM helpers, qhash/APBVT/ARP operations, and notifier callbacks.

## Control flow, state, and persistence
The header defines the state machine used by `hw.c` for staged initialization and teardown. `struct irdma_pci_f` persists control-plane hardware state, resource bitmaps, HMC/PBLE data, queue objects, MSI-X tables, workqueues, generation ops, and locks. `struct irdma_device` persists the IB-facing runtime object, netdev, VSI, CM core, RoCE/iWARP mode flags, and runtime init state.

## Dependencies and integration points
It includes kernel networking, PCI, DMA, workqueue, auxiliary bus, RDMA core, ABI, and local IRDMA headers. Almost every file in this subset depends on it for shared contracts, especially `hw.c`, generation interface files, verbs, CM, PBLE, and HMC code.

## Risks and test signals
Risks are global coupling, stale prototypes, lock-order assumptions, resource bitmap off-by-one behavior, and init-state mismatch. Tests should cover resource allocation wraparound, init/deinit state transitions, compile coverage across feature configs, and lifetime checks for `rf` versus `iwdev` in Gen3 core/vport mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/osdep.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/osdep.h

## Purpose
`osdep.h` provides Linux OS abstraction declarations and simple memory wrapper structures used by the IRDMA shared-control code.

## Important APIs, types, and functions
Important types are `struct irdma_dma_mem`, `struct irdma_virt_mem`, and `struct irdma_dma_info`. It forward-declares many core structs and prototypes OS-facing hooks for ibdev lookup, IEQ handling, virtual-channel state, device refcounting, CQP SDS/HMC commands, FPM buffers, termination timers, hardware stats timers, register access, and vmalloc page mapping.

## Control flow, state, and persistence
There is no executable flow. The memory wrapper structs carry virtual address, DMA physical address, and size through HMC, PBLE, CQP, queue, and context allocation paths.

## Dependencies and integration points
It includes Linux PCI, bitfield, RDMA verbs, and DSCP headers. It is included by most low-level files before hardware/control types are fully defined, allowing shared code to call OS-specific helpers implemented elsewhere.

## Risks and test signals
Risks include packed DMA memory wrappers causing unexpected alignment assumptions, stale prototypes, and divergent OS helper behavior. Tests should cover DMA mapping/unmapping, register access on 32-bit and 64-bit builds, virtual-channel timeout handling, and stats/termination timer lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/osdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/pble.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/pble.c

## Purpose
`pble.c` manages PBLE backing memory carved from the HMC PBLE object space. It creates PBLE chunks using direct or paged SDs, tracks free PBLE ranges with bitmaps, allocates level-1 or level-2 PBLE lists, and returns PBLEs during MR/AEQ teardown.

## Important APIs, types, and functions
Exported functions include `irdma_hmc_init_pble`, `irdma_destroy_pble_prm`, `irdma_get_pble`, and `irdma_free_pble`. Internal helpers include `get_sd_pd_idx`, `add_sd_direct`, `add_bp_pages`, `irdma_get_type`, `add_pble_prm`, `get_lvl1_pble`, `get_lvl2_pble`, `free_lvl2`, and `get_lvl1_lvl2_pble`.

## Control flow, state, and persistence
Initialization aligns the PBLE FPM base to 4 KiB, records unallocated PBLE count and next FPM address, initializes mutex/spinlock/list state, and adds the first PBLE PRM chunk. `add_pble_prm` chooses direct SD when a full SD-aligned 2 MiB region is available, otherwise paged SD, registers the chunk with the PRM bitmap, advances `next_fpm_addr`, decrements `unallocated_pble`, programs the SD when required, and links the chunk. Allocation first tries existing free PBLEs, then adds SD chunks as needed, creating level-1 lists or level-2 root/leaf lists. State persists in `irdma_hmc_pble_rsrc` counters, chunk list, PRM bitmaps, and HMC SD/PD entries.

## Dependencies and integration points
The file depends on HMC APIs from `hmc.c`, PBLE bitmap helpers declared in `pble.h` and implemented elsewhere, DMA/vmalloc page mapping for paged chunks, and CQP SD programming. `hw.c` initializes PBLE resources after CEQs and before AEQ creation; AEQ virtual mapping can allocate PBLEs from this pool.

## Risks and test signals
Risks include allocation underflow/overflow around FPM alignment, direct-versus-paged fallback mistakes, bitmap leaks after level-2 partial failure, locking imbalance between mutex and PRM spinlock helpers, and programming SDs before `valid` is coherent. Tests should cover exact 512-PBLE boundaries, unaligned PBLE base, level-1 and level-2 allocation/free, forced direct allocation failure fallback, Gen3 direct mode rules, and destroy with mixed chunk types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/pble.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/pble.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/pble.h

## Purpose
`pble.h` defines PBLE geometry, allocation levels, chunk metadata, PRM allocator state, HMC PBLE resource state, and prototypes for PBLE resource management.

## Important APIs, types, and functions
Important constants are `PBLE_SHIFT`, `PBLE_PER_PAGE`, `HMC_PAGED_BP_SHIFT`, `PBLE_512_SHIFT`, and `PBLE_INVALID_IDX`. Important types are `enum irdma_pble_level`, `enum irdma_alloc_type`, `struct irdma_pble_info`, `struct irdma_pble_level2`, `struct irdma_pble_alloc`, `struct irdma_chunk`, `struct irdma_pble_prm`, and `struct irdma_hmc_pble_rsrc`. Public prototypes cover initialization, destruction, allocation, free, PRM bitmap operations, locks, and paged memory helpers.

## Control flow, state, and persistence
The header itself has no flow, but its structures define the PBLE persistent state: chunk list and bitmaps, free/allocated PBLE counters, next FPM position, allocation statistics, level-1 and level-2 allocation descriptors, and direct/paged SD chunk type.

## Dependencies and integration points
It depends on HMC structures, DMA info, virtual memory wrappers, list heads, locks, and the control device. It is consumed by MR registration paths, AEQ virtual mapping, `hw.c`, and `pble.c`.

## Risks and test signals
Risks are geometry mismatch with HMC page size, level-2 root/leaf count mistakes, and stats/counter drift. Tests should validate allocation descriptors returned to MR code, free/reallocate behavior, PRM bitmap accounting, and chunk type cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/pble.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/protos.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/protos.h

## Purpose
`protos.h` declares lower-level shared-control prototypes used across IRDMA control, HMC, queue, stats, VSI, work scheduler, termination, and CQP code. It also defines thresholds for pause/PFC and CQP completion waits.

## Important APIs, types, and functions
Important constants include `PAUSE_TIMER_VAL`, `REFRESH_THRESHOLD`, traffic-control thresholds, `CQP_COMPL_WAIT_TIME_MS`, `CQP_TIMEOUT_THRESHOLD`, and `CQP_DEF_CMPL_TIMEOUT_THRESHOLD`. Prototypes cover device initialization, CQP WQE handling, fast MR registration, HMC/FPM setup, stats commands, CEQ/AEQ commands, VSI initialization and stats, L2 parameter changes, QP suspend/resume, termination, HMC page allocation notification, feature query, bottom-half processing, SDS commands, FPM buffer allocation, HMC function management, and device refcount helpers.

## Control flow, state, and persistence
The header has no flow, but it defines cross-module call edges. Many routines mutate persistent `irdma_sc_dev`, `irdma_sc_vsi`, CQP, HMC, stats, and QP state in implementation files outside this subset.

## Dependencies and integration points
It is included by HMC, PBLE, hardware, and control files to avoid circular declarations. It bridges `hw.c` orchestration with low-level `ctrl.c`, `utils.c`, work scheduler, stats, and termination implementations.

## Risks and test signals
Risks include stale prototypes, hidden cross-file dependencies, and timeout constants that affect CQP reliability. Test signals include compile coverage, CQP timeout/deferred completion tests, FPM query/commit validation, stats gather tests, and QP suspend/resume behavior during TC changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/protos.h -->
