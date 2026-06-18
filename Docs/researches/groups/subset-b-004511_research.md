# Research: subset-b-004511

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs.c

### Purpose

`mcs.c` is the PCI-facing hardware driver for the Marvell/Cavium CN10K MCS block, the MACsec engine used by the OcteonTX2 RVU Admin Function stack. It discovers MCS PCI functions, maps the BAR, selects CN10KB or CNF10KB operation callbacks, initializes MACsec parser/port/global state, manages RX/TX MACsec resources, programs TCAM/SecY/SC/SA/PN tables, reads and clears hardware counters, handles MCS interrupts, and exposes helper APIs consumed by `mcs_rvu_if.c`.

The file is not a network datapath by itself. It is the low-level state and register layer that PF/VF mailbox handlers use to configure MACsec offload for logical functions.

### Important APIs, Types, And Functions

The global device list is `mcs_list`; `mcs_get_blkcnt()`, `mcs_get_pdata()`, and `is_mcs_bypass()` are lookup helpers used by RVU code. `mcs_probe()` and `mcs_remove()` are the PCI driver lifecycle hooks in exported `struct pci_driver mcs_driver`.

Statistics APIs include `mcs_get_tx_secy_stats()`, `mcs_get_rx_secy_stats()`, `mcs_get_flowid_stats()`, `mcs_get_port_stats()`, `mcs_get_sa_stats()`, `mcs_get_sc_stats()`, `mcs_clear_stats()`, and `mcs_clear_all_stats()`. They read CSE counter registers through `mcs_reg_read()` and are serialized by callers with `mcs->stats_lock`.

Policy and table programming APIs include `mcs_pn_table_write()`, `mcs_sa_plcy_write()`, `mcs_rx_sc_cam_write()`, `mcs_secy_plcy_write()`, `mcs_flowid_entry_write()`, `mcs_ena_dis_flowid_entry()`, `mcs_ena_dis_sc_cam_entry()`, `mcs_pn_threshold_set()`, and `mcs_clear_secy_plcy()`. Variant-specific callbacks are `cn10kb_mcs_tx_sa_mem_map_write()`, `cn10kb_mcs_rx_sa_mem_map_write()`, `cn10kb_mcs_flowid_secy_map()`, and the CNF10KB implementations in `mcs_cnf10kb.c`.

Resource APIs include `mcs_alloc_rsrc()`, `mcs_free_rsrc()`, `mcs_alloc_all_rsrc()`, `mcs_free_all_rsrc()`, `mcs_alloc_ctrlpktrule()`, `mcs_free_ctrlpktrule()`, and `mcs_ctrlpktrule_write()`. They wrap RVU bitmap helpers and maintain per-resource `pcifunc` owner maps.

Interrupt APIs include `mcs_ip_intr_handler()`, RX/TX PN threshold and wrapped-PN helpers, BBE/PAB handlers, and `mcs_register_interrupts()`. Interrupt notification is completed through `mcs_add_intr_wq_entry()` in `mcs_rvu_if.c`.

### Control Flow

Probe flow allocates `struct mcs` and `struct hwinfo`, enables the PCI device, requests regions, maps BAR0, picks CN10KB ops when `pdev->subsystem_device == PCI_SUBSYS_DEVID_CN10K_B` and CNF10KB ops otherwise, fills capabilities, applies global configuration, performs X2P calibration, derives `mcs_id` from BAR address bits, allocates RX and TX resource maps, initializes each LMAC, configures parser tags, registers MSI-X interrupt handling, appends the device to `mcs_list`, and initializes the stats mutex. Failure after global setup puts the block into external bypass before releasing PCI resources.

Initialization programs the block out of bypass, clears RX/TX stats memories, sets IEEE 802.1AE mode on single-block CN10KB hardware, and programs CNF10KB BBE calendar fields on multi-block hardware. Each LMAC starts in 25G-style port mode with CNF10KB FIFO skid defaults. `mcs_set_lmac_channels()` assigns 16-channel windows per LMAC using the LINK LMAC config registers.

Configuration flow from mailbox handlers typically allocates resources, writes flow TCAM data/masks, maps flow IDs to SecY/SC state, writes SecY policy, writes RX SC CAM entries or TX/RX SA maps, writes SA policy blocks, writes PN tables, and finally enables flow entries. The default bypass entry reserves the last flow ID and SecY entry in both directions, installs all-ones TCAM masks, writes permissive SecY policies, maps the reserved flow to the reserved SecY, and enables it.

Interrupt flow disables the top IP interrupt, reads `MCSX_TOP_SLAVE_INT_SUM`, dispatches CPM RX, CPM TX, BBE RX/TX, and PAB RX/TX sources, clears each child interrupt, then clears and re-enables the top interrupt. CPM RX PN threshold walks the RX SA threshold registers. TX PN threshold and XPN wrap handling differ between CN10KB packed SA-map format and CNF10KB split status registers. BBE/PAB handling is also variant-specific through `mcs_ops`.

### State And Persistence Behavior

Persistent hardware state is all MMIO-programmed state in the MCS block: flow TCAM entries, masks, enable bits, SecY maps and policies, SC CAM entries, SA maps and policies, PN tables, PN thresholds, parser tag configuration, port configuration, channel mapping, interrupt masks, and bypass mode. This state persists in the device until reset, FLR cleanup, driver removal, or explicit mailbox reconfiguration; it is not written to disk.

Software state mirrors ownership and runtime behavior. `struct mcs_rsrc_map` holds bitmaps and owner maps for flow IDs, SecY entries, SC entries, SA entries, and control packet rules. `flowid2secy_map` is used to disable affected flows when a SecY policy is cleared. `tx_sa_active[]` caches the last active TX SA bit per SC so TX rekey/expiration interrupts can identify which SA changed. `mcs->pf` and `mcs->vf` interrupt masks are allocated later by RVU init, not by PCI probe.

The driver uses devm allocation for most per-device memory, RVU bitmap allocation for resource bitmaps, MSI-X vectors for interrupt delivery, and a process-context workqueue in the RVU layer for PF/VF notification.

### Dependencies And Integration Points

`mcs.c` depends on Linux PCI, IRQ, delay, bitfield, bitmap, and device APIs; RVU helpers such as `rvu_alloc_rsrc()`, `rvu_free_rsrc()`, and `rvu_alloc_bitmap()`; mailbox request/response types from RVU headers; and register macros from `mcs_reg.h`.

It integrates upward with `mcs_rvu_if.c`, which validates mailbox requests and calls these helpers, and sideways with `mcs_cnf10kb.c`, which supplies CNF10KB-specific ops. Hardware-family selection depends on PCI subsystem IDs and on `hw->mcs_blks`: single-block CN10KB has 128 flow/SecY/SC entries and 256 SAs; CNF10KB has multiple smaller blocks with 64 flow/SecY/SC entries and 128 SAs.

### Risks

Resource allocation is not transactional. `mcs_alloc_all_rsrc()` returns on the first failure after allocating earlier resources, but it does not roll back those earlier allocations. Several mailbox allocation paths also return success with partial response counts, so callers must inspect response fields and logs.

Banked enable-register helpers switch to `_ENA_1` for IDs above 63 but still use `BIT_ULL(flow_id)` or `BIT_ULL(sc_id)` rather than a normalized bit index. Current CNF10KB limits often keep IDs below 64, but CN10KB has 128 entries, making this a sensitive area for high-index resources.

Ownership checks are uneven. Freeing resources validates `pcifunc`, but many direct write/enable mailbox paths rely on the caller passing IDs it owns. The source even leaves a `TODO validate the flowid` in the flow-entry write path.

Interrupt routing for misc/fatal events uses `mcs->pf_map[0]`, which is set by interrupt configuration rather than by probe. If no PF has configured interrupts, fatal events may be dropped or mapped to an unintended owner. `mcs_remove()` sets bypass and frees PCI resources but does not remove the node from `mcs_list`, so stale lookups would be risky if PCI remove/reprobe occurs in the same kernel lifetime.

### Test Signals

Useful signals include successful PCI probe on CN10KB and CNF10KB devices, `mcs_get_hw_info` returning expected resource counts, default bypass passing traffic before MACsec configuration, allocation/free cycles for every resource type and both directions, high-index resource enable/disable tests on CN10KB, FLR cleanup clearing all resources owned by a PF/VF, RX/TX SecY/SC/SA/flow counter reads and clears, PN threshold and XPN wrap notifications, BBE/PAB overflow notification, port mode and channel mapping validation, and `dmesg` absence of X2P calibration failures, IRQ registration failures, and unexpected policy/data FIFO overflow warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs.h

### Purpose

`mcs.h` is the private interface and data-model header for the OcteonTX2 AF MCS MACsec driver. It defines hardware limits, interrupt bits, per-device state, resource ownership maps, variant operation callbacks, register access inlines, and the exported helper prototypes used by `mcs.c`, `mcs_cnf10kb.c`, and `mcs_rvu_if.c`.

### Important APIs, Types, And Constants

Hardware identity and limits include `PCI_DEVID_CN10K_MCS`, `MCS_ID_MASK`, `MCS_MAX_PFS`, port masks, custom tag limits, control packet rule counts and offsets, reserved resource count, interrupt vector IDs, BBE/PAB interrupt masks, and CPM RX/TX interrupt bits.

`struct mcs_pfvf` stores the enabled interrupt mask for one PF or VF. `struct mcs_intr_event` and `struct mcs_intrq_entry` define queued async notifications to PF/VF drivers. `struct secy_mem_map` is the normalized flow-to-SecY/SC/SCI mapping passed to family-specific map writers.

`struct mcs_rsrc_map` owns all per-direction software resource state: owner arrays for flow IDs, SecY entries, SC entries, SA entries, and control packet rules, plus the `rsrc_bmap` allocation bitmaps. `struct hwinfo` describes per-family capacities and topology. `struct mcs` is the main device state: BAR base, PCI/device pointers, hardware info, RX/TX maps, PF map, MCS ID, ops table, list node, stats mutex, PF/VF interrupt masks, RVU back pointer, TX active-SA cache, and bypass state.

`struct mcs_ops` abstracts the family-specific operations for capabilities, parser configuration, TX/RX SA map programming, flow-to-SecY mapping, and BBE/PAB interrupt handling. `mcs_reg_write()` and `mcs_reg_read()` are the MMIO accessors used throughout the driver.

### Control Flow

The header does not execute logic itself, but it establishes the control boundaries. PCI probe creates `struct mcs`, selects an `mcs_ops` table, calls capability and parser callbacks, and then common code calls the exported APIs. RVU mailbox handlers call the prototypes declared here after validating MCS IDs and holding resource/stat locks where needed.

The interrupt path also follows types from this header: hardware-specific handlers fill `struct mcs_intr_event`, `mcs_add_intr_wq_entry()` masks it against the target PF/VF `intr_mask`, and workqueue code sends an upward mailbox notification.

### State And Persistence Behavior

The header defines transient kernel state used to track persistent device programming. Resource bitmaps and owner maps are the authoritative software view of which PF/VF owns each hardware table entry. `hwinfo` determines how much hardware state exists and which register layout is active. `bypass` mirrors external bypass configuration. None of this state is persisted across driver reloads; the hardware state is rebuilt at probe/RVU init and cleaned on FLR/remove.

### Dependencies And Integration Points

`mcs.h` includes `<linux/bits.h>` and `rvu.h`, so it depends on RVU mailbox types, `struct rsrc_bmap`, `enum mcs_direction`, and all MCS mailbox request/response structures. It is included by the common driver, the CNF10KB variant file, and the RVU mailbox bridge. It also declares `extern struct pci_driver mcs_driver` for driver registration elsewhere in the AF module.

### Risks

Because `mcs.h` is shared across the common, variant, and RVU layers, layout or semantic changes have broad impact. Any change to resource limits or bit masks must match both hardware register layout and mailbox ABI expectations. `struct mcs_ops` additions require all variants to be updated together. The inline MMIO helpers assume `reg_base` is valid and offsets are already family-correct, putting correctness pressure on `mcs_reg.h`.

### Test Signals

Compile-time signals are missing prototypes, incomplete `mcs_ops` initializers, and mailbox type mismatches. Runtime signals include correct hardware-info responses, expected resource counts per family, interrupt masks honored per PF/VF, and no invalid BAR access during probe, RVU init, interrupt handling, or remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs_cnf10kb.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs_cnf10kb.c

### Purpose

`mcs_cnf10kb.c` supplies the CNF10KB-specific MCS operation table for the common driver in `mcs.c`. CNF10KB uses multiple MCS blocks with smaller per-block tables and a different register packing for parser tags, flow-to-SecY mapping, TX SA selection, auto rekey state, and BBE/PAB interrupt reporting.

### Important APIs, Types, And Functions

`cnf10kb_mcs_ops` is the family ops table returned by `cnf10kb_get_mac_ops()`. It points to `cnf10kb_mcs_set_hw_capabilities()`, `cnf10kb_mcs_parser_cfg()`, `cnf10kb_mcs_tx_sa_mem_map_write()`, `cnf10kb_mcs_rx_sa_mem_map_write()`, `cnf10kb_mcs_flowid_secy_map()`, `cnf10kb_mcs_bbe_intr_handler()`, and `cnf10kb_mcs_pab_intr_handler()`.

`cnf10kb_mcs_set_hw_capabilities()` reports 64 TCAM, 64 SecY, 64 SC, and 128 SA entries, four LMACs per MCS block, one X2P interface, seven MCS blocks, and interrupt vector `MCS_CNF10KB_INT_VEC_IP`.

`cnf10kb_mcs_parser_cfg()` programs custom CTag/STag parser entries for RX and TX and enables custom tags 0/1 plus SecTAG ethertype parsing. `cnf10kb_mcs_flowid_secy_map()` writes RX or TX SecY mapping; TX additionally writes SCI and SC fields across CNF10KB-specific map registers.

`cnf10kb_mcs_tx_sa_mem_map_write()` programs two TX SA indices, auto-rekey enable state, SA-valid bits, and the active SA bit using split CNF10KB registers. `cnf10kb_mcs_rx_sa_mem_map_write()` maps RX SC/an pairs to SA indices. `mcs_set_force_clk_en()` is defined here for CNF10KB stats reads.

Interrupt helpers `cnf10kb_mcs_tx_pn_thresh_reached_handler()` and `cnf10kb_mcs_tx_pn_wrapped_handler()` identify expired TX SAs from auto-rekey status and `tx_sa_active`; BBE/PAB handlers translate per-LMAC fatal bits into `mcs_intr_event` notifications.

### Control Flow

Common probe selects these ops for non-CN10KB subsystem devices, calls the capability callback, and later calls the parser callback. Mailbox flow-entry and SA-map handlers call through the ops table so the common RVU path can stay format-neutral.

During CNF10KB stats reads, RVU handlers call `mcs_set_force_clk_en(true)` before reading counters and `mcs_set_force_clk_en(false)` afterward. The helper sets `MCSX_MIL_GLOBAL` bit 4 and polls `MCSX_MIL_IP_GBL_STATUS` bit 0 with a 2 ms timeout.

TX PN threshold interrupt handling reads `MCSX_CPM_TX_SLAVE_AUTO_REKEY_ENABLE_0`, walks allocated TX SCs, skips SCs without auto rekey, reads the active-SA status register, compares it with cached `mcs->tx_sa_active[sc]`, derives the expired SA index from `MCSX_CPM_TX_SLAVE_SA_MAP_MEM_0X(sc)`, maps that SA to a `pcifunc`, and queues a PF/VF event.

### State And Persistence Behavior

The file programs CNF10KB hardware state only through MMIO registers. It mutates parser custom tag registers, SecY map registers, SA map and valid registers, auto-rekey enable bits, active-SA registers, and force-clock state. It reads software resource ownership from the common `mcs->tx` and `mcs->rx` maps and relies on `mcs->tx_sa_active[]` being maintained by mailbox writes.

The force-clock helper intentionally toggles a transient hardware bit around stats reads. Auto-rekey and active-SA registers persist until rewritten or reset, and are interpreted with software cache state during interrupts.

### Dependencies And Integration Points

This file depends on `mcs.h` for state, ops, constants, and interrupt event types, and on `mcs_reg.h` for CNF10KB-aware register offsets. It integrates with the common interrupt path through the ops table and with the RVU workqueue notification path through `mcs_add_intr_wq_entry()`.

### Risks

`mcs_set_force_clk_en()` logs a timeout but still returns 0, so callers cannot distinguish accurate from possibly stale stats. TX PN threshold detection depends on `mcs->tx_sa_active[]` being current; missed mailbox writes or concurrent rekey updates could misidentify the expired SA. The BBE handler checks `if (intr & 0xFULL)` inside a per-bit loop, which classifies all reported bits as data FIFO overflow if any lower-nibble bit is set; mixed lower/upper-nibble events may lose specificity.

CNF10KB field widths are narrower than CN10KB: 6-bit flow/SecY/SC and 7-bit SA values. Any shared code that assumes CN10KB limits can write truncated IDs through these helpers.

### Test Signals

Useful tests are capability reporting for seven blocks, parser recognition of CTag/STag/SecTAG traffic, RX and TX flow-to-SecY map programming with SCI on TX, TX auto-rekey with PN threshold notifications for both SA slots, XPN wrap notification, stats reads under force-clock enable, BBE/PAB overflow event routing to the configured PF/VF, and no timeout logs from `mcs_set_force_clk_en()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs_cnf10kb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs_reg.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs_reg.h

### Purpose

`mcs_reg.h` is the MCS register offset map. It defines the MMIO addresses used by the common and CNF10KB MCS drivers for top-level control, MIL/HIL/link setup, PAB/PEX parser configuration, BBE/PAB interrupts, CPM flow/SecY/SC/SA/PN tables, CSE statistics, and top-level interrupt routing.

### Important APIs, Types, And Constants

Top-level and link macros include `MCSX_IP_MODE`, `MCSX_MCS_TOP_SLAVE_PORT_RESET()`, `MCSX_MCS_TOP_SLAVE_CHANNEL_CFG()`, `MCSX_MIL_GLOBAL`, `MCSX_MIL_RX_LMACX_CFG()`, `MCSX_HIL_GLOBAL`, `MCSX_LINK_LMACX_CFG()`, `MCSX_MIL_RX_GBL_STATUS`, and `MCSX_MIL_IP_GBL_STATUS`.

PAB/PEX macros cover port modes, FIFO skid config, VLAN/custom tag config, parser ethertype enable, PTP/custom header skip config, and control packet rule registers: ethertype rules, DA rules, DA-range rules, combo rules, MAC rule, and rule enable.

BBE/PAB interrupt macros define status, enable, and interrupt rewrite registers for RX/TX BBE and PAB paths plus overflow detail registers. CPM macros define RX/TX flow TCAM data/mask/enable registers, RX SC CAM and enable registers, RX/TX SecY map and policy registers, SA map/policy/PN table registers, PN/XPN thresholds, TX active-SA and SA valid registers, and CNF10KB auto-rekey registers.

CSE macros define RX/TX counter locations for SecY, SC, SA, flow ID, and port statistics, plus stats clear/control registers. Top-level interrupt macros include `MCSX_IP_INT`, `MCSX_IP_INT_ENA_W1S`, `MCSX_IP_INT_ENA_W1C`, `MCSX_TOP_SLAVE_INT_SUM`, `MCSX_TOP_SLAVE_INT_SUM_ENB`, and CPM child interrupt registers.

### Control Flow

The header has no runtime functions, but many macros are GNU statement expressions that compute offsets dynamically from the lexical `mcs` pointer. Most macros choose one base address for single-block CN10KB (`mcs->hw->mcs_blks == 1`) and another for multi-block CNF10KB. Driver code then adds resource indices and register-bank indices to those bases before calling `mcs_reg_read()` or `mcs_reg_write()`.

Control packet rule programming in `mcs.c` depends on the rule-offset layout in this header. Stats routines map each mailbox stats type to the corresponding CSE counter macro. Interrupt handling reads top-level and child status registers from this header and clears them by writing the same status value back.

### State And Persistence Behavior

The header defines where hardware state lives, not the state itself. Register groups correspond to persistent device programming: parser tag config, flow TCAM contents and masks, resource enable bits, SecY/SC/SA/PN policy memory, thresholds, stats controls, and interrupt enables. Counter registers are read-only from the software perspective except for clear/control sequences.

### Dependencies And Integration Points

`mcs_reg.h` includes `<linux/bits.h>` and depends on a local variable named `mcs` being in scope for most statement-expression macros. It is tightly coupled to `struct mcs->hw->mcs_blks` from `mcs.h`. The common driver and CNF10KB variant both include it; incorrect offsets affect all mailbox operations.

### Risks

The lexical dependency on `mcs` makes the macros concise but fragile: using them in a helper without a variable named `mcs` will fail to compile, and using a different `mcs` than intended will silently compute the wrong family layout. Register definitions mix dynamic offsets with fixed CN10KB-only and CNF10KB-only addresses; shared code must know when fixed `_ENA_1`, active-SA, and custom-tag registers are valid.

Several enable-register users support resources above 63 but the register macros only select the second register; the caller must also normalize bit positions. If callers pass raw IDs to `BIT_ULL()`, high-index entries can be enabled or disabled incorrectly.

Because these constants directly encode hardware ABI, any drift from the data sheet can cause silent corruption of MACsec policy memory, wrong stats, missed interrupts, or traffic bypass/drop behavior.

### Test Signals

Good signals include successful probe on both register layouts, correct hardware-info-derived capacities, parser config visible in custom tag registers, successful flow/SecY/SC/SA programming and packet hits, accurate stats by type and direction, working PN threshold interrupts, correct BBE/PAB fatal reporting, and no MMIO faults or nonsensical counter values when exercising both CN10KB and CNF10KB paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs_rvu_if.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs_rvu_if.c

### Purpose

`mcs_rvu_if.c` is the RVU mailbox bridge for the MCS MACsec driver. It exposes MCS hardware operations to PF/VF clients through AF mailbox handlers, handles asynchronous MCS interrupt notification back to PF/VF drivers, configures PTP/custom-header parsing interactions with RPM/CGX ports, initializes MCS state during RVU bring-up, and releases MCS resources during FLR and RVU teardown.

### Important APIs, Types, And Functions

The `MBOX_UP_MCS_MESSAGES` macro expansion builds upward mailbox allocators such as `otx2_mbox_alloc_msg_mcs_intr_notify()`. `rvu_mcs_ptp_cfg()` toggles parser skip behavior when RPM adds an 8-byte PTP header.

Async notification is implemented by `mcs_add_intr_wq_entry()`, `mcs_notify_pfvf()`, and `mcs_intr_handler_task()`. Events are masked by each PF/VF `intr_mask`, queued under `rvu->mcs_intrq_lock`, and sent on `rvu->afpf_wq_info.mbox_up` under `rvu->mbox_lock`.

Mailbox handlers cover interrupt config, hardware info, LMAC mode, port reset, stats get/clear, active LMAC bitmap, port config get/set, custom tag config get, flow ID enable, PN table writes, PN threshold set, RX/TX SA map writes, SA policy writes, RX SC CAM writes, SecY policy writes, flow TCAM writes, resource allocation/free, control packet rule allocation/free/write, FLR cleanup, init, and exit.

### Control Flow

RVU initialization calls `rvu_mcs_init()`, which discovers MCS block count via `mcs_get_blkcnt()`. For single-block CN10KB it programs LMAC channel bases and derives the active LMAC bitmap from CGX/RPM validity. For every MCS block it installs the default bypass entry, sets every LMAC to operational mode, stores the RVU back pointer, allocates PF and VF interrupt-mask arrays, and creates the MCS interrupt workqueue.

Mailbox handlers follow a common pattern: validate `req->mcs_id < rvu->mcs_blk_cnt`, fetch the block with `mcs_get_pdata()`, optionally validate port/Lmac/resource ownership, lock `rvu->rsrc_lock` for resource allocation/free or `mcs->stats_lock` for stats reads/clears, then delegate to `mcs.c` or `mcs_ops` functions. CNF10KB stats handlers set force-clock before reads and clear it afterward.

Resource allocation can allocate one resource type repeatedly or a full bundle of flow, SecY, SC, and two SA resources. Freeing can release one resource or all resources owned by the requester's `pcifunc`. FLR cleanup iterates all MCS blocks on CNF10KB and both directions, freeing resources for the reset function.

Interrupt notification starts in the hardware IRQ handler in `mcs.c`, which calls `mcs_add_intr_wq_entry()`. This bridge identifies PF versus VF from `pcifunc`, masks the event, queues it, and the workqueue sends an upward mailbox message to the PF that owns the function.

### State And Persistence Behavior

This file mutates RVU-owned process state: `rvu->mcs_blk_cnt`, `rvu->mcs_intrq_head`, `rvu->mcs_intr_work`, `rvu->mcs_intr_wq`, and each MCS block's `rvu`, `pf`, and `vf` pointers. It also mutates per-PF/VF interrupt masks and active LMAC bitmaps.

Mailbox operations persist by programming MCS hardware state through `mcs.c`. FLR cleanup removes the software ownership state and disables associated hardware entries. `rvu_mcs_exit()` destroys the interrupt workqueue, but PCI remove is handled by the lower MCS driver.

### Dependencies And Integration Points

The file depends on RVU core structures and locks, AF/PF mailbox helpers, `rvu_get_pf()`, `rvu_get_hwvf()`, CGX/RPM LMAC discovery through `lmac_common.h`, MCS core helpers, and register macros for the PTP parser adjustments. It is the main integration point between PF/VF MACsec clients and the physical MCS blocks.

### Risks

Several write handlers validate only `mcs_id` and then program hardware resource IDs supplied by the caller. Ownership is enforced on free, but direct writes to flow ID, SecY, SC, SA, and PN state rely on higher-level request discipline. `rvu_mbox_handler_mcs_alloc_resources()` logs allocation failure but returns 0, so callers must inspect response counts/IDs rather than only the mailbox return code.

`rvu_mcs_set_lmac_bmap()` declares `lmac_bmap` without an explicit zero initializer before setting bits, which risks stale stack bits becoming active LMACs. `mcs_add_intr_wq_entry()` indexes PF/VF interrupt arrays based on `pcifunc`; invalid or stale mappings would corrupt notification routing. Workqueue destruction does not explicitly drain the queue in this file, so teardown ordering must ensure no MCS IRQs can enqueue after `rvu_mcs_exit()`.

### Test Signals

Useful signals include mailbox ABI tests for every handler, invalid MCS ID rejection, invalid/inactive port rejection, PF/VF-specific interrupt mask filtering, upward interrupt notification contents for SA ID and LMAC ID, allocation/free/allocation reuse under `rvu->rsrc_lock`, FLR releasing both RX and TX resources, stats reads on CNF10KB with force-clock toggling, PTP enable/disable changing the expected parser skip register, and no workqueue use-after-free during RVU shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs_rvu_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/npc.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/npc.h

### Purpose

`npc.h` defines the parser, key extraction, action, profile, and MCAM rule data structures for the OcteonTX2 NPC block. NPC is the packet parser and match/action engine used by RVU/NIX flows; this header provides layer/ltype enumerations, key-field identifiers, packed firmware/profile formats, action bitfield layouts, vtag action masks, reserved MCAM entry indexes, and the in-memory rule representation used by AF flow steering.

### Important APIs, Types, And Constants

`SET_KEX_LD()` and `SET_KEX_LDFLAGS()` are helper macros for programming NPC key extraction registers. `enum NPC_LID_E` defines parser layers LA through LH. The `npc_kpu_*_ltype` enums define recognized ltypes at each layer: Ethernet/custom/CPT at LA, VLAN/DSA/PPPoE at LB, IPv4/IPv6/ARP/MPLS at LC, TCP/UDP/SCTP/ICMP/AH/GRE at LD, tunnel protocols at LE/LF/LG/LH, and inner transport ltypes.

`enum key_fields` defines logical fields used in MCAM keys: DMAC, SMAC, ethertype, VLAN tags, IPv4/IPv6 addresses, protocol selectors, ports, IPsec SPI, MPLS fields, ICMP fields, TCP flags, channel, PF_FUNC, error fields, layer ltypes, exact match result, extracted tag views, and unknown fields.

Packed profile structures include `npc_kpu_profile_cam`, `npc_kpu_profile_action`, `npc_kpu_profile`, `npc_kpu_fwdata`, `npc_kpu_profile_fwdata`, `npc_coalesced_kpu_prfl`, and `npc_mcam_kex`. These encode firmware-loadable KPU CAM/action entries, default MKEX data, layer-type definitions, and custom profile metadata.

Hardware register bitfield structs include `npc_kpu_cam`, `npc_kpu_action0`, `npc_kpu_action1`, `npc_kpu_pkind_cpi_def`, `nix_rx_action`, and `nix_tx_action`. `rvu_npc_mcam_rule` is the software rule object with packet/mask keys, interface, RX/TX action union, vtag action, owner, entry, counter, channel, priority, and flags.

### Control Flow

The header does not implement functions, but it drives NPC initialization and flow programming elsewhere in the AF driver. KPU profile loaders consume the packed profile structures, write CAM/action registers using the bitfield layouts, install key extraction profiles through `npc_mcam_kex`, and derive field offsets from `key_fields` and ltype defaults.

Flow installation code builds `rvu_npc_mcam_rule`, fills packet and mask data, chooses RX or TX action layout, optionally attaches counters and vtag actions, and writes MCAM entries. Default unicast, broadcast, all-multicast, and promiscuous entries use the reserved NIXLF entry indexes declared here.

### State And Persistence Behavior

Profile structures describe persistent NPC hardware programming loaded into KPU and key extraction registers. `rvu_npc_mcam_rule` instances are software state for installed flows; the corresponding MCAM entries, counters, and actions persist in hardware until removed, disabled, or reset. The firmware profile data is packed and endian-sensitive, with signatures such as `NPC_SIGN` and `KPU_SIGN` guarding profile identity.

### Dependencies And Integration Points

`npc.h` depends on constants and types from surrounding RVU/NPC headers, including `NPC_MAX_INTF`, `NPC_MAX_LID`, `NPC_MAX_LT`, `NPC_MAX_LD`, `NPC_MAX_LFL`, `MKEX_NAME_LEN`, `struct flow_msg`, and NIX interface/action definitions. It is included by `rvu.h` and used by NPC initialization, profile loading, MCAM resource management, flow steering, exact match support, VLAN tag actions, and NIX RX/TX delivery setup.

MCS files in this work item do not include `npc.h` directly, but both MCS and NPC live under the RVU Admin Function and participate in hardware packet processing: NPC classifies and steers packets, while MCS applies MACsec policies at the MACsec block.

### Risks

Several enum comments warn that ltype values must not be modified because RSS flow-tag calculation, IPv4/IPv6 checksum/length handling, and protocol detection depend on stable encodings. Packed firmware structures are ABI-sensitive; changing field order, packing, or endian annotations can break external KPU/MKEX profiles. The bitfield structs are endian-conditional and must match hardware register definitions exactly.

`rvu_npc_mcam_rule` mixes hardware entry ownership, action data, counters, vtag state, and list linkage. Incorrect lifetime or owner handling can leak MCAM entries, expose another function's traffic, or leave counters/actions attached to stale rules.

### Test Signals

Useful signals include KPU/MKEX profile signature validation, successful parser initialization, correct key extraction for RX and TX interfaces, default NIXLF entries installed at reserved indexes, flow steering tests for each supported key field class, VLAN tag action tests, exact match result decoding, RSS stability after ltype changes, endian build coverage, and MCAM rule allocation/free tests that confirm owner, counter, and enable state remain consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/npc.h -->
