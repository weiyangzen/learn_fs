# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs_cnf10kb.c

## Purpose

`mcs_cnf10kb.c` supplies the CNF10KB-specific MCS operation table for the common driver in `mcs.c`. CNF10KB uses multiple MCS blocks with smaller per-block tables and a different register packing for parser tags, flow-to-SecY mapping, TX SA selection, auto rekey state, and BBE/PAB interrupt reporting.

## Important APIs, Types, And Functions

`cnf10kb_mcs_ops` is the family ops table returned by `cnf10kb_get_mac_ops()`. It points to `cnf10kb_mcs_set_hw_capabilities()`, `cnf10kb_mcs_parser_cfg()`, `cnf10kb_mcs_tx_sa_mem_map_write()`, `cnf10kb_mcs_rx_sa_mem_map_write()`, `cnf10kb_mcs_flowid_secy_map()`, `cnf10kb_mcs_bbe_intr_handler()`, and `cnf10kb_mcs_pab_intr_handler()`.

`cnf10kb_mcs_set_hw_capabilities()` reports 64 TCAM, 64 SecY, 64 SC, and 128 SA entries, four LMACs per MCS block, one X2P interface, seven MCS blocks, and interrupt vector `MCS_CNF10KB_INT_VEC_IP`.

`cnf10kb_mcs_parser_cfg()` programs custom CTag/STag parser entries for RX and TX and enables custom tags 0/1 plus SecTAG ethertype parsing. `cnf10kb_mcs_flowid_secy_map()` writes RX or TX SecY mapping; TX additionally writes SCI and SC fields across CNF10KB-specific map registers.

`cnf10kb_mcs_tx_sa_mem_map_write()` programs two TX SA indices, auto-rekey enable state, SA-valid bits, and the active SA bit using split CNF10KB registers. `cnf10kb_mcs_rx_sa_mem_map_write()` maps RX SC/an pairs to SA indices. `mcs_set_force_clk_en()` is defined here for CNF10KB stats reads.

Interrupt helpers `cnf10kb_mcs_tx_pn_thresh_reached_handler()` and `cnf10kb_mcs_tx_pn_wrapped_handler()` identify expired TX SAs from auto-rekey status and `tx_sa_active`; BBE/PAB handlers translate per-LMAC fatal bits into `mcs_intr_event` notifications.

## Control Flow

Common probe selects these ops for non-CN10KB subsystem devices, calls the capability callback, and later calls the parser callback. Mailbox flow-entry and SA-map handlers call through the ops table so the common RVU path can stay format-neutral.

During CNF10KB stats reads, RVU handlers call `mcs_set_force_clk_en(true)` before reading counters and `mcs_set_force_clk_en(false)` afterward. The helper sets `MCSX_MIL_GLOBAL` bit 4 and polls `MCSX_MIL_IP_GBL_STATUS` bit 0 with a 2 ms timeout.

TX PN threshold interrupt handling reads `MCSX_CPM_TX_SLAVE_AUTO_REKEY_ENABLE_0`, walks allocated TX SCs, skips SCs without auto rekey, reads the active-SA status register, compares it with cached `mcs->tx_sa_active[sc]`, derives the expired SA index from `MCSX_CPM_TX_SLAVE_SA_MAP_MEM_0X(sc)`, maps that SA to a `pcifunc`, and queues a PF/VF event.

## State And Persistence Behavior

The file programs CNF10KB hardware state only through MMIO registers. It mutates parser custom tag registers, SecY map registers, SA map and valid registers, auto-rekey enable bits, active-SA registers, and force-clock state. It reads software resource ownership from the common `mcs->tx` and `mcs->rx` maps and relies on `mcs->tx_sa_active[]` being maintained by mailbox writes.

The force-clock helper intentionally toggles a transient hardware bit around stats reads. Auto-rekey and active-SA registers persist until rewritten or reset, and are interpreted with software cache state during interrupts.

## Dependencies And Integration Points

This file depends on `mcs.h` for state, ops, constants, and interrupt event types, and on `mcs_reg.h` for CNF10KB-aware register offsets. It integrates with the common interrupt path through the ops table and with the RVU workqueue notification path through `mcs_add_intr_wq_entry()`.

## Risks

`mcs_set_force_clk_en()` logs a timeout but still returns 0, so callers cannot distinguish accurate from possibly stale stats. TX PN threshold detection depends on `mcs->tx_sa_active[]` being current; missed mailbox writes or concurrent rekey updates could misidentify the expired SA. The BBE handler checks `if (intr & 0xFULL)` inside a per-bit loop, which classifies all reported bits as data FIFO overflow if any lower-nibble bit is set; mixed lower/upper-nibble events may lose specificity.

CNF10KB field widths are narrower than CN10KB: 6-bit flow/SecY/SC and 7-bit SA values. Any shared code that assumes CN10KB limits can write truncated IDs through these helpers.

## Test Signals

Useful tests are capability reporting for seven blocks, parser recognition of CTag/STag/SecTAG traffic, RX and TX flow-to-SecY map programming with SCI on TX, TX auto-rekey with PN threshold notifications for both SA slots, XPN wrap notification, stats reads under force-clock enable, BBE/PAB overflow event routing to the configured PF/VF, and no timeout logs from `mcs_set_force_clk_en()`.
