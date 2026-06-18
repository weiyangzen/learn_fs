# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_reqmgr.c

## Purpose
This file implements VF request submission and completion processing for CPT crypto operations. It allocates pending entries, builds CPT instructions from request-manager metadata, submits commands to LF hardware, polls completion results in order, maps hardware/microcode completion codes to Crypto API statuses, and invokes callbacks.

## Important APIs and functions
Public APIs are `otx2_cpt_do_request()`, `otx2_cpt_post_process()`, and `otx2_cpt_get_eng_grp_num()`. Internal helpers include `process_request()`, `process_pending_queue()`, `cpt_process_ccode()`, `get_free_pending_entry()`, `free_pentry()`, `modulo_inc()`, and debug dumping through `otx2_cpt_dump_sg_list()`.

## Control flow
Algorithm code calls `otx2_cpt_do_request()` with a prepared `otx2_cpt_req_info` and CPU/LF number. `process_request()` checks LF started state, creates SG/DMA info through hardware ops, initializes the completion code, reserves a pending queue entry under lock with bounded retry, records callback/request metadata, builds big-endian IQ command words, fills `otx2_cpt_inst_s`, sends the command, and returns `-EINPROGRESS` or `-EBUSY` to throttle senders. Done interrupt tasklets call `otx2_cpt_post_process()`, which drains pending entries from the front until it finds an incomplete request.

## State and persistence
Pending queue state tracks ring front/rear, pending count, busy entries, callbacks, completion addresses, and resume-sender flags. Each `otx2_cpt_inst_info` owns DMA mappings and timing fields until callback cleanup. Completion state is DMA-written by hardware. No persistent storage is used.

## Dependencies and integration points
This file depends on VF device state from PCI drvdata, LF hardware ops, request-manager SG builders, hardware completion-code definitions, and algorithm callbacks. It is triggered by LF done interrupts scheduled in `otx2_cptlf.c` and tasklets created in VF main.

## Risks and edge cases
Completion processing is strictly in order; a stuck earlier entry blocks later completed entries. `CPT_COMP_E_NOTDONE` extends timeout a few times before repeatedly warning and returning for later polling. Queue throttling uses `resume_sender` entries and callback `-EINPROGRESS` to restart senders. Debug dumps can expose plaintext/key-adjacent data if dynamic debug is enabled. Error cases must still call callbacks and free DMA state.

## Test signals
Signals include async Crypto API completion, queue-full `-EBUSY` and resume behavior, timeout warnings on dropped completions, correct status mapping for fault/hwerr/insterr/software microcode errors, truncated-HMAC success handling for SG write length, DMA cleanup under every completion code, and CPU-to-LF queue selection under load.
