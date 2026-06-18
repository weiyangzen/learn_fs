# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_reqmgr.c Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_reqmgr.c

### Purpose
`otx_cptvf_reqmgr.c` turns algorithm-layer CPT requests into DMA gather/scatter lists, hardware instructions, command queue entries, and pending completion records. It also scans completion status and invokes crypto callbacks.

### Important APIs, Types, And Functions
Public APIs are `otx_cpt_dump_sg_list()`, `otx_cpt_do_request()`, and `otx_cpt_post_process()`. Important internals include pending entry management, `setup_sgio_components()`, `setup_sgio_list()`, `cpt_fill_inst()`, `cpt_send_cmd()`, `process_request()`, `cpt_process_ccode()`, and `process_pending_queue()`.

### Control Flow, State, And Persistence
Submission validates VF readiness and SE/AE request compatibility, allocates a combined info/list/result/completion buffer, maps input and output buffers bidirectionally, writes SG component lists and header counts, maps the SG list buffer, initializes completion code, reserves a pending queue entry under lock, fills callback/request pointers, creates a CPT instruction with opcode/params/dlen and DPTR/RPTR/CPTR group, copies the instruction into the current command queue slot, advances circular chunk pointers, issues a write barrier, and rings the VF doorbell. Completion processing walks pending entries in FIFO order, checks hardware completion code and microcode error code, handles not-done timeout extension, treats truncated-HMAC scatter/gather write-length errors as success, wakes senders when the resume margin is reached, frees pending entries, and calls callbacks outside the queue lock.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on VF queue state, hardware instruction/result layouts, DMA mapping APIs, jiffies timeouts, algorithm callbacks, and cleanup helpers in the request-manager header. Risks include a cleanup typo in failed SG mapping that unmaps `list[i]` instead of `list[j]`, leaking mapped buffers after partial `setup_sgio_list()` failures, FIFO completion assumptions while hardware can complete out of order, busy-waiting for pending entries, bidirectional mappings for all buffers, and callback resume ordering. Test signals include DMA mapping failure injection, SG counts over 50, queue-full `-EBUSY`/resume behavior, CPT fault/SWERR/HWERR completion codes, not-done timeout warnings, truncated HMAC decrypt, and request cleanup after callback.
