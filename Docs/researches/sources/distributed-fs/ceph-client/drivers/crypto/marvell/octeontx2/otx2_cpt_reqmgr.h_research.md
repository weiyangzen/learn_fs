# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_reqmgr.h

## Purpose
This header defines the CPT request-manager data model and inline DMA/scatter-gather setup helpers used by the VF crypto data path. It translates Crypto API request buffers into CPT instruction inputs, output scatter lists, completion memory, and per-request lifetime records.

## Important APIs and types
Core types are `struct otx2_cpt_req_info`, `struct otx2_cpt_inst_info`, `struct otx2_cpt_pending_entry`, `struct otx2_cpt_pending_queue`, `struct otx2_cpt_buf_ptr`, `struct otx2_cpt_iq_command`, and SG component formats `struct otx2_cpt_sglist_component` and `struct cn10kb_cpt_sglist_component`. Important helpers are `otx2_cpt_info_destroy()`, `setup_sgio_components()`, `sgv2io_components_setup()`, `cn10k_sgv2_info_create()`, and `otx2_sg_info_create()`. External functions declared here are `otx2_cpt_do_request()`, `otx2_cpt_post_process()`, and `otx2_cpt_get_eng_grp_num()`.

## Control flow
Algorithm code fills `otx2_cpt_req_info` with input/output buffers, context pointer, opcode, callback, and engine group. The selected hardware op calls either `otx2_sg_info_create()` or `cn10k_sgv2_info_create()` to allocate one aligned memory block containing `otx2_cpt_inst_info`, gather/scatter lists, and completion result space. Each SG setup maps caller buffers with `dma_map_single()`, writes hardware SG descriptors, maps descriptor memory, and records DMA addresses used by `otx2_cptvf_reqmgr.c` when building the CPT instruction.

## State and persistence
Per-request state persists until completion callback cleanup. `otx2_cpt_inst_info` owns DMA mappings for SG descriptors and points back to the original request. Individual `otx2_cpt_buf_ptr.dma_addr` fields are set during mapping and cleared only on partial setup failures; normal completion unmaps them in `otx2_cpt_info_destroy()`. No disk persistence exists.

## Dependencies and integration points
The header depends on `otx2_cpt_common.h`, hardware result layout from `otx2_cpt_hw_types.h`, and Linux DMA APIs. VF algorithms create requests, VF request manager submits and completes them, and LF hardware ops choose CN9K or CN10K SG formats.

## Risks and edge cases
Alignment math is security- and correctness-critical: DPTR/RPTR need 8-byte alignment and completion results need 32-byte alignment. SG v1 supports up to 50 input and 50 output buffers; v2 does not enforce the same explicit count in the helper, so callers must remain bounded by request arrays. DMA mapping failures must unwind all prior mappings. Zero or NULL virtual pointers are skipped, but descriptor counts still come from `buf_count`, so malformed sparse lists can create descriptors with zero addresses.

## Test signals
Signals include successful encryption/decryption over fragmented scatterlists, DMA API debug runs with no unbalanced mappings, CN10K SGv2 capability path coverage, allocation-failure injection through both SG builders, and completion cleanup that frees mappings under normal, hardware-error, and timeout paths.
