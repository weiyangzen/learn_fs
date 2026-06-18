# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_cn10k.c

## Purpose
`rvu_cn10k.c` contains CN10K-specific RVU AF helpers for APR LMTST map-table management, programmable channel numbering, NIX/RPM/LBK channel programming, and CN10K NIX/APR block initialization. It supplements the generic RVU core with features absent or different on older OcteonTX2 silicon.

## Important APIs, Types, and Functions
- `lmtst_map_table_ops()` temporarily maps the APR LMT map table, reads or writes an entry, programs entry word1 defaults on writes, and flushes the APR interceptor cache.
- `rvu_get_lmtst_tbl_index()` maps a `pcifunc` to its two-word LMT map table entry offset.
- `rvu_get_lmtaddr()` asks RVUM/SMMU translation registers to translate a PF/VF IOVA to a physical LMTLINE address.
- `rvu_update_lmtaddr()` stores the original LMT base in `pfvf->lmt_base_addr` and writes a replacement.
- `rvu_mbox_handler_lmtst_tbl_setup()` handles local LMT memory, shared-primary LMT region setup, scheduled LMTST enable, line-prefetch disable, and ordered early-completion disable.
- `rvu_reset_lmt_map_tbl()` restores saved LMT base and word1 values during FLR.
- `rvu_set_channels_base()` computes channel bases and marks `hw->cap.programmable_chans`.
- `rvu_program_channels()` applies programmable channel configuration to NIX, LBK, and RPM blocks.
- `rvu_nix_block_cn10k_init()` sets NIX vWQE timer and RX/global clock bits.
- `rvu_apr_block_cn10k_init()` raises APR LMTST throttling.

## Control Flow
Generic RVU setup calls `rvu_apr_block_cn10k_init()` before resource discovery on non-OcteonTX2 devices. Later, `rvu_set_channels_base()` reads NIX constants, fills CGX/LBK/SDP/CPT link counts and default channel bases, and, when programmable channels are supported, computes compact contiguous channel windows ordered LBK, SDP, CGX, CPT. After NIX/SDP setup, `rvu_program_channels()` writes the computed windows into each NIX link config, each LBK P2X/X2P config, and each RPM LMAC link config.

At runtime, PF/VF drivers can send `lmtst_tbl_setup`. The handler optionally translates a local LMT IOVA into a physical address, updates the caller's LMT map entry, mirrors a base pcifunc's LMT address for shared mode, and updates word1 flags for scheduled LMTST behaviors. Original values are saved only once in `struct rvu_pfvf` so `rvu_reset_lmt_map_tbl()` can restore them on FLR. LMT table writes flush APR LMT cache immediately.

## State and Persistence Behavior
The file updates `struct rvu_hwinfo` channel fields (`cgx`, `lmac_per_cgx`, link counts, channel bases, programmable channel capability) and per-function LMT defaults (`lmt_base_addr`, `lmt_map_ent_w1`). Hardware state persists in APR LMT map table memory, APR LMT configuration/control CSRs, RVUM SMMU translation registers, NIX link channel registers, LBK link channel registers, RPM LMAC channel registers, and NIX AF config/timer registers. Saved LMT defaults are runtime-only and are cleared after FLR restoration.

## Dependencies and Integration Points
The file depends on RVU core MMIO helpers, CGX/RPM LMAC read/write helpers, APR/RVU/NIX/LBK/RPM register definitions, Linux PCI device iteration for LBK programming, and `rvu->rsrc_lock` for SMMU translation serialization. It integrates with `rvu.c` setup, mailbox dispatch through `rvu_mbox_handler_lmtst_tbl_setup()`, FLR cleanup via `rvu_reset_lmt_map_tbl()`, and NIX initialization through `rvu_nix_block_cn10k_init()`.

## Risks and Edge Cases
- `lmtst_map_table_ops()` maps and unmaps the entire LMT table on every operation; failures or high-frequency calls can be expensive.
- `rvu_get_lmtaddr()` serializes translation with `rsrc_lock`, but callers must ensure the IOVA remains valid during translation and subsequent use.
- Saved LMT defaults use zero as "not saved"; if a legitimate original value is zero, restoration of that field is skipped.
- Channel base computation must fit CPT into channels 2048-4095; otherwise initialization fails.
- `rvu_lbk_set_channels()` iterates PCI LBK devices and has a late `pci_dev_put()` only on the error path; PCI reference handling deserves scrutiny.
- RPM channel programming assumes 16 channels per LMAC because no read-only constant exists.
- LMT map word1 writes OR new bits into existing values, so clearing previously enabled options requires FLR/reset rather than a second setup call.

## Test Signals
- CN10K probe tests with programmable channels disabled and enabled, including NIX1, multiple LBK devices, RPM/RPM2 LMAC counts, and CPT channel windows.
- LMTST mailbox tests for local region translation, shared base pcifunc, scheduled LMTST flags, word1 updates, invalid/null IOVA, and translation errors.
- FLR tests confirming LMT base and word1 restoration and clearing of saved defaults.
- MMIO mock tests verifying APR cache flush sequence after LMT writes.
- Channel programming tests validating NIX/LBK/RPM base/range fields and no overlap between LBK, SDP, CGX, and CPT windows.
- Regression coverage for `rvu_nix_block_cn10k_init()` and `rvu_apr_block_cn10k_init()` register bits.
