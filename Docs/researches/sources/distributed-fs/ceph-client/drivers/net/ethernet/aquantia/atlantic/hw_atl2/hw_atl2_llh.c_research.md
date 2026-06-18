# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_llh.c

## Purpose
This file is the ATL2 low-level hardware helper implementation. It wraps specific A2 register and bitfield writes/reads behind typed helper functions used by `hw_atl2.c`, `hw_atl2_utils.c`, and `hw_atl2_utils_fw.c`.

## Important APIs, types, and functions
The helpers cover RPF/RSS controls (`hw_atl2_rpf_redirection_table2_select_set`, `hw_atl2_rpf_rss_hash_type_set`, `hw_atl2_rpf_new_enable_set`, `hw_atl2_new_rpf_rss_redir_set`), L2/VLAN tag programming (`hw_atl2_rpfl2_uc_flr_tag_set`, `hw_atl2_rpfl2_bc_flr_tag_set`, `hw_atl2_rpf_vlan_flr_tag_set`), TX scheduler and interrupt moderation (`hw_atl2_tpb_tx_tc_q_rand_map_en_set`, `hw_atl2_tpb_tx_buf_clk_gate_en_set`, `hw_atl2_reg_tx_intr_moder_ctrl_set`, `hw_atl2_tps_tx_pkt_shed_*`), launch-time setup, action resolver records, and firmware shared-buffer/boot/interrupt registers.

## Control flow
Most functions perform a single `aq_hw_write_reg_bit`, `aq_hw_write_reg`, or `aq_hw_read_reg_bit`. `hw_atl2_init_launchtime` reads the hardware version and selects a clock ratio based on version thresholds. Shared-buffer helpers loop across dword offsets to transfer structures between host and firmware input/output buffers. Action resolver record setup writes tag, mask, and action words to adjacent resolver-memory registers.

## State and persistence
All state is hardware or firmware shared state. Writes persist in device registers, resolver table memory, shared input buffers, boot registers, or interrupt clear registers until hardware, firmware, or reset changes them.

## Dependencies and integration points
The file depends on `hw_atl2_llh_internal.h` register addresses and masks plus `aq_hw_utils.h` register accessors. Higher-level ATL2 code relies on this file to avoid embedding raw offsets in policy logic.

## Risks
These helpers do little validation. Bad queue, TC, index, filter, offset, or length values can address unintended registers or shared-buffer dwords. Shared-buffer `int` offsets and lengths assume caller already computed dword counts correctly. Launch-time version thresholds are hard-coded and must track hardware revisions.

## Test signals
Register write/read tracing, hardware filter behavior, successful firmware shared-buffer transactions, boot register transitions, and interrupt moderation behavior provide coverage. Static review should verify every helper uses the matching address, mask, and shift from the internal register header.
