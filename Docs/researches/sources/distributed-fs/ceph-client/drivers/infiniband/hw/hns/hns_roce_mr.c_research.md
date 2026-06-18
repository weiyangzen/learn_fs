# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_mr.c

## Purpose
`hns_roce_mr.c` implements HNS memory registration and the reusable memory-translation-region layer used by MRs and queue buffers. It allocates MR keys, builds MPT hardware contexts, pins or allocates backing buffers, chooses page size and hop depth, builds base-address/MTT tables, maps SG lists for fast registration, and exposes MTT lookup helpers.

## Important APIs, Types, And Functions
Important types include `struct hns_roce_mr`, `struct hns_roce_mtr`, `struct hns_roce_buf_attr`, `struct hns_roce_hem_cfg`, and `struct hns_roce_buf_region`. Verbs entry points are `hns_roce_get_dma_mr()`, `hns_roce_reg_user_mr()`, `hns_roce_rereg_user_mr()`, `hns_roce_dereg_mr()`, `hns_roce_alloc_mr()`, and `hns_roce_map_mr_sg()`. MTR helpers include `hns_roce_mtr_create()`, `hns_roce_mtr_destroy()`, `hns_roce_mtr_map()`, and `hns_roce_mtr_find()`. Key internal helpers are `alloc_mr_key()`, `alloc_mr_pbl()`, `hns_roce_mr_enable()`, `mtr_alloc_bufs()`, `get_best_page_shift()`, `get_best_hop_num()`, `mtr_init_buf_cfg()`, and `mtr_alloc_mtt()`.

## Control Flow
Normal user MR registration allocates a software MR, obtains an MTPT ID/key, creates a PBL MTR over user memory, writes the MTPT through hardware callbacks, creates the MPT hardware context, and returns the key as both lkey and rkey. DMA MRs allocate only a key and enable an MPT without a PBL. Reregistration queries the current MPT, destroys it, updates IOVA/size/PD/access, optionally rebuilds the PBL, writes a replacement MTPT, and recreates the hardware context. Fast MRs allocate an MTT-only PBL at creation, then `hns_roce_map_mr_sg()` converts scatterlists into page addresses and maps them into the MTR. MTR creation optionally pins user memory or allocates kernel buffers, adapts page shift and hop count, initializes HEM config, allocates MTT tables, and maps DMA addresses unless the caller will map later.

## State And Persistence
MR state is runtime only: key, PD, access flags, IOVA, length, PBL hop count, page count, enable state, optional page list, and embedded MTR. MTR state records user or kernel backing memory, direct-vs-multihop layout, root base address, base-address page size, buffer page size, regions, and HEM list state. IDA state in `mr_table.mtpt_ida` owns key indexes. No persistent storage is used; hardware MPT and MTT contents are reconstructed from software state during creation/reregistration.

## Dependencies And Integration Points
The file depends on RDMA core MR and umem APIs, scatterlist page conversion, HNS command mailboxes, hardware MTPT writer callbacks, HEM table/list APIs, buffer allocation helpers, page-size capabilities from `hr_dev->caps`, and tracepoints from `hns_roce_trace.h`. The MTR abstraction is shared by QP and SRQ code for WQE, index, and queue buffers.

## Risks
`alloc_mr_key()` maps any negative ID allocation failure to `-ENOMEM`, which can hide `-ENOSPC`-style exhaustion details. Reregistration destroys the hardware MPT before all replacement work is guaranteed to succeed; if later steps fail the MR remains disabled and partially updated. `hns_roce_mtr_map()` assumes `pages[0]` is valid for direct mode, so callers must never pass zero pages. Adaptive page-size and hop calculations are sensitive to device page capability masks and umem alignment. The fast-MR page list is transient, so error paths must always free it. Direct-mode multi-region splitting requires physically contiguous small pages and can fail for otherwise valid allocations.

## Test Signals
Test DMA MR, user MR, FRMR allocation, invalid `dmah`, MTPT exhaustion, MPT create/destroy failure, reregistration by PD/access/translation combinations, failed reregistration recovery expectations, SG mapping alignment and page-size bounds, SG overrun returning zero, direct and multihop MTR creation, MTT-only MTRs, `hns_roce_mtr_find()` for direct and multihop offsets, adaptive page-size selection, hop-count overflow, and cleanup after every injected allocation failure.
