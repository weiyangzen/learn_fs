# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs.c

## Purpose

`mcs.c` is the PCI-facing hardware driver for the Marvell/Cavium CN10K MCS block, the MACsec engine used by the OcteonTX2 RVU Admin Function stack. It discovers MCS PCI functions, maps the BAR, selects CN10KB or CNF10KB operation callbacks, initializes MACsec parser/port/global state, manages RX/TX MACsec resources, programs TCAM/SecY/SC/SA/PN tables, reads and clears hardware counters, handles MCS interrupts, and exposes helper APIs consumed by `mcs_rvu_if.c`.

The file is not a network datapath by itself. It is the low-level state and register layer that PF/VF mailbox handlers use to configure MACsec offload for logical functions.

## Important APIs, Types, And Functions

The global device list is `mcs_list`; `mcs_get_blkcnt()`, `mcs_get_pdata()`, and `is_mcs_bypass()` are lookup helpers used by RVU code. `mcs_probe()` and `mcs_remove()` are the PCI driver lifecycle hooks in exported `struct pci_driver mcs_driver`.

Statistics APIs include `mcs_get_tx_secy_stats()`, `mcs_get_rx_secy_stats()`, `mcs_get_flowid_stats()`, `mcs_get_port_stats()`, `mcs_get_sa_stats()`, `mcs_get_sc_stats()`, `mcs_clear_stats()`, and `mcs_clear_all_stats()`. They read CSE counter registers through `mcs_reg_read()` and are serialized by callers with `mcs->stats_lock`.

Policy and table programming APIs include `mcs_pn_table_write()`, `mcs_sa_plcy_write()`, `mcs_rx_sc_cam_write()`, `mcs_secy_plcy_write()`, `mcs_flowid_entry_write()`, `mcs_ena_dis_flowid_entry()`, `mcs_ena_dis_sc_cam_entry()`, `mcs_pn_threshold_set()`, and `mcs_clear_secy_plcy()`. Variant-specific callbacks are `cn10kb_mcs_tx_sa_mem_map_write()`, `cn10kb_mcs_rx_sa_mem_map_write()`, `cn10kb_mcs_flowid_secy_map()`, and the CNF10KB implementations in `mcs_cnf10kb.c`.

Resource APIs include `mcs_alloc_rsrc()`, `mcs_free_rsrc()`, `mcs_alloc_all_rsrc()`, `mcs_free_all_rsrc()`, `mcs_alloc_ctrlpktrule()`, `mcs_free_ctrlpktrule()`, and `mcs_ctrlpktrule_write()`. They wrap RVU bitmap helpers and maintain per-resource `pcifunc` owner maps.

Interrupt APIs include `mcs_ip_intr_handler()`, RX/TX PN threshold and wrapped-PN helpers, BBE/PAB handlers, and `mcs_register_interrupts()`. Interrupt notification is completed through `mcs_add_intr_wq_entry()` in `mcs_rvu_if.c`.

## Control Flow

Probe flow allocates `struct mcs` and `struct hwinfo`, enables the PCI device, requests regions, maps BAR0, picks CN10KB ops when `pdev->subsystem_device == PCI_SUBSYS_DEVID_CN10K_B` and CNF10KB ops otherwise, fills capabilities, applies global configuration, performs X2P calibration, derives `mcs_id` from BAR address bits, allocates RX and TX resource maps, initializes each LMAC, configures parser tags, registers MSI-X interrupt handling, appends the device to `mcs_list`, and initializes the stats mutex. Failure after global setup puts the block into external bypass before releasing PCI resources.

Initialization programs the block out of bypass, clears RX/TX stats memories, sets IEEE 802.1AE mode on single-block CN10KB hardware, and programs CNF10KB BBE calendar fields on multi-block hardware. Each LMAC starts in 25G-style port mode with CNF10KB FIFO skid defaults. `mcs_set_lmac_channels()` assigns 16-channel windows per LMAC using the LINK LMAC config registers.

Configuration flow from mailbox handlers typically allocates resources, writes flow TCAM data/masks, maps flow IDs to SecY/SC state, writes SecY policy, writes RX SC CAM entries or TX/RX SA maps, writes SA policy blocks, writes PN tables, and finally enables flow entries. The default bypass entry reserves the last flow ID and SecY entry in both directions, installs all-ones TCAM masks, writes permissive SecY policies, maps the reserved flow to the reserved SecY, and enables it.

Interrupt flow disables the top IP interrupt, reads `MCSX_TOP_SLAVE_INT_SUM`, dispatches CPM RX, CPM TX, BBE RX/TX, and PAB RX/TX sources, clears each child interrupt, then clears and re-enables the top interrupt. CPM RX PN threshold walks the RX SA threshold registers. TX PN threshold and XPN wrap handling differ between CN10KB packed SA-map format and CNF10KB split status registers. BBE/PAB handling is also variant-specific through `mcs_ops`.

## State And Persistence Behavior

Persistent hardware state is all MMIO-programmed state in the MCS block: flow TCAM entries, masks, enable bits, SecY maps and policies, SC CAM entries, SA maps and policies, PN tables, PN thresholds, parser tag configuration, port configuration, channel mapping, interrupt masks, and bypass mode. This state persists in the device until reset, FLR cleanup, driver removal, or explicit mailbox reconfiguration; it is not written to disk.

Software state mirrors ownership and runtime behavior. `struct mcs_rsrc_map` holds bitmaps and owner maps for flow IDs, SecY entries, SC entries, SA entries, and control packet rules. `flowid2secy_map` is used to disable affected flows when a SecY policy is cleared. `tx_sa_active[]` caches the last active TX SA bit per SC so TX rekey/expiration interrupts can identify which SA changed. `mcs->pf` and `mcs->vf` interrupt masks are allocated later by RVU init, not by PCI probe.

## Dependencies And Integration Points

`mcs.c` depends on Linux PCI, IRQ, delay, bitfield, bitmap, and device APIs; RVU helpers such as `rvu_alloc_rsrc()`, `rvu_free_rsrc()`, and `rvu_alloc_bitmap()`; mailbox request/response types from RVU headers; and register macros from `mcs_reg.h`.

It integrates upward with `mcs_rvu_if.c`, which validates mailbox requests and calls these helpers, and sideways with `mcs_cnf10kb.c`, which supplies CNF10KB-specific ops. Hardware-family selection depends on PCI subsystem IDs and on `hw->mcs_blks`: single-block CN10KB has 128 flow/SecY/SC entries and 256 SAs; CNF10KB has multiple smaller blocks with 64 flow/SecY/SC entries and 128 SAs.

## Risks

Resource allocation is not transactional. `mcs_alloc_all_rsrc()` returns on the first failure after allocating earlier resources, but it does not roll back those earlier allocations. Several mailbox allocation paths also return success with partial response counts, so callers must inspect response fields and logs.

Banked enable-register helpers switch to `_ENA_1` for IDs above 63 but still use `BIT_ULL(flow_id)` or `BIT_ULL(sc_id)` rather than a normalized bit index. Current CNF10KB limits often keep IDs below 64, but CN10KB has 128 entries, making this a sensitive area for high-index resources.

Ownership checks are uneven. Freeing resources validates `pcifunc`, but many direct write/enable mailbox paths rely on the caller passing IDs it owns. The source even leaves a `TODO validate the flowid` in the flow-entry write path.

Interrupt routing for misc/fatal events uses `mcs->pf_map[0]`, which is set by interrupt configuration rather than by probe. If no PF has configured interrupts, fatal events may be dropped or mapped to an unintended owner. `mcs_remove()` sets bypass and frees PCI resources but does not remove the node from `mcs_list`, so stale lookups would be risky if PCI remove/reprobe occurs in the same kernel lifetime.

## Test Signals

Useful signals include successful PCI probe on CN10KB and CNF10KB devices, `mcs_get_hw_info` returning expected resource counts, default bypass passing traffic before MACsec configuration, allocation/free cycles for every resource type and both directions, high-index resource enable/disable tests on CN10KB, FLR cleanup clearing all resources owned by a PF/VF, RX/TX SecY/SC/SA/flow counter reads and clears, PN threshold and XPN wrap notifications, BBE/PAB overflow notification, port mode and channel mapping validation, and `dmesg` absence of X2P calibration failures, IRQ registration failures, and unexpected policy/data FIFO overflow warnings.
