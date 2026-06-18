# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_mbox_common.c

## Purpose
This file provides shared CPT mailbox helpers used by PF and VF paths to communicate with RVU AF/PF firmware. It wraps mailbox allocation, send/wait behavior, AF register read/write requests, LF resource attach/detach, MSI-X offset queries, LF reset, and CN10K LMTST table setup.

## Important APIs and functions
Exported helpers include `otx2_cpt_send_mbox_msg()`, `otx2_cpt_send_ready_msg()`, `otx2_cpt_send_af_reg_requests()`, `otx2_cpt_add_write_af_reg()`, `otx2_cpt_read_af_reg()`, `otx2_cpt_write_af_reg()`, `otx2_cpt_detach_rsrcs_msg()`, `otx2_cpt_msix_offset_msg()`, `otx2_cpt_sync_mbox_msg()`, `otx2_cpt_lf_reset_msg()`, and `otx2_cpt_lmtst_tbl_setup_msg()`. `otx2_cpt_add_read_af_reg()` is file-local and queues a read request for later send.

## Control flow
Each helper allocates a typed mailbox request with `otx2_mbox_alloc_msg_rsp()`, fills the message ID/signature/pcifunc fields, populates request-specific payload, and sends through `otx2_cpt_send_mbox_msg()`. Register reads and writes use `MBOX_MSG_CPT_RD_WR_REGISTER`; batched writes can be queued with `otx2_cpt_add_write_af_reg()` and flushed by `otx2_cpt_send_af_reg_requests()`. Attach/detach calls validate asynchronous response side effects by checking `lfs->are_lfs_attached`, which mailbox response handlers update.

## State and persistence
The helpers mutate mailbox buffers and fields in `struct otx2_cptlfs_info`, especially `are_lfs_attached`, LF MSI-X offsets, and LMT metadata. Register read results are written through response-owned `ret_val` pointers. No persistent storage is used; all state is device, mailbox, or DMA/MMIO state.

## Dependencies and integration points
This file depends on the common RVU mailbox API from `mbox.h`, CPT LF structures from `otx2_cptlf.h`, and response handlers in `otx2_cptpf_mbox.c` and `otx2_cptvf_mbox.c` to complete state updates. PF/VF probe and LF init paths call these helpers before enabling queues or registering interrupts.

## Risks and edge cases
Allocation failure consistently returns `-EFAULT`, while mailbox timeout returns `-EIO` and other errors collapse to `-EFAULT`. Attach/detach correctness depends on response handlers updating `are_lfs_attached`; if responses are dropped or processed by the wrong LF block, callers see `-EINVAL`. `otx2_cpt_detach_rsrcs_msg()` hard-codes `cptlfs = 1`, which is intentional for current cleanup but worth checking if multi-LF detach semantics change.

## Test signals
Probe logs should show ready-message success, valid MSI-X offsets for every LF, successful attach/detach transitions, AF register reads returning expected constants, and no timeout path from `otx2_mbox_wait_for_rsp()`. Fault injection on mailbox allocation and timeout paths should unwind PF/VF probe cleanly.
