# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/struct.h

## Purpose
Defines CN20K-specific hardware context layouts for NIX SQ/CQ/RQ and NPA aura/pool contexts, plus CN20K RVU mailbox interrupt vector enumerations.

## Important APIs, Types, and Functions
Important declarations are `NIX_MAX_CTX_SIZE`, `enum rvu_mbox_pf_int_vec_e`, `enum rvu_af_cn20k_int_vec_e`, `struct nix_cn20k_sq_ctx_s`, `struct nix_cn20k_cq_ctx_s`, `struct nix_cn20k_rq_ctx_s`, `struct npa_cn20k_aura_s`, and `struct npa_cn20k_pool_s`. Fields cover queue enablement, CQ/RQ/SQ indices, scheduler mappings, aura/pool IDs, interrupts, buffering, caching, stashing, flow control, LSO, stats, drops, and reserved hardware words. `static_assert` checks enforce 128-byte context size.

## Control Flow
There is no executable flow. AQ mailbox handlers select CN20K request/response variants and use these structures and masks when reading or writing hardware contexts.

## State and Persistence Behavior
Every context struct is a hardware-persistent record. SQ/RQ/CQ fields determine queue behavior and counters. NPA aura/pool fields determine buffer pool ownership, limits, flow control, thresholds, and error interrupt behavior.

## Dependencies and Integration Points
Included by `mbox.h`, which embeds these structs in CN20K NIX and NPA AQ request/response messages. It complements generic `rvu_struct.h` and CN10K context variants.

## Risks
ABI drift is the main risk. Reordering bitfields, changing widths, or altering reserved fields can corrupt hardware contexts. One `static_assert` after the CQ struct checks `sizeof(struct nix_cn20k_sq_ctx_s)` again rather than the CQ type, reducing layout coverage for CQ.

## Test Signals
Build-time size checks, CN20K NIX/NPA LF allocation, AQ read/write/init of RQ/SQ/CQ/aura/pool contexts, queue traffic, LSO, flow control, interrupt routing, stats counters, and hardware context dump comparisons.
