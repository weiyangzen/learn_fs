# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_mbox.c

## Purpose
This file implements VF-side PF/VF mailbox handling. It creates a bounce buffer for safe message preparation, synchronizes hardware mailbox responses into that buffer, handles PF responses, and sends VF requests for engine group numbers, kernel VF limits, and hardware capabilities.

## Important APIs and functions
Public APIs are `otx2_cpt_mbox_bbuf_init()`, `otx2_cptvf_pfvf_mbox_intr()`, `otx2_cptvf_pfvf_mbox_handler()`, `otx2_cptvf_send_eng_grp_num_msg()`, `otx2_cptvf_send_kvf_limits_msg()`, and `otx2_cptvf_send_caps_msg()`. Local helpers include `otx2_cpt_sync_mbox_bbuf()` and `process_pfvf_mbox_mbox_msg()`.

## Control flow
Mailbox init allocates a device-managed bounce buffer and redirects `mdev->mbase` to it. On interrupt, the handler queues mailbox work and acknowledges the VF interrupt bit. The work handler uses `smp_rmb()`, copies response bytes from hardware mailbox memory into the bounce buffer, validates response headers/signatures, processes each message, increments `msgs_acked`, and resets the mailbox. Send helpers allocate request/response mailbox slots, fill IDs/signatures/pcifunc, and call the shared send/wait helper.

## State and persistence
Responses update `cptvf->vf_id`, LF attach state, LF MSI-X offsets, AF register readback storage, SE/AE engine group numbers, KVF LF limits, and engine capabilities. Bounce-buffer memory persists for the VF device lifetime. There is no disk persistence.

## Dependencies and integration points
This file depends on RVU mailbox internals, shared mailbox send helpers, VF device state, and LF state. VF probe and LF init call its send helpers synchronously and rely on response processing to populate fields.

## Risks and edge cases
`otx2_cpt_sync_mbox_bbuf()` bounds response copy size by mailbox receive size to avoid overflow, but still trusts mailbox header placement. Responses with wrong signatures or unknown IDs are logged and ignored. `pcifunc` construction for VF requests uses the current `vf_id`, so requests after ready message are safest; early messages must use accepted PF/VF conventions.

## Test signals
Signals include ready response setting `vf_id`, capability response filling all engine caps, LF attach/detach flags changing after resource messages, valid MSI-X offset propagation, bounced mailbox responses on CN10K and OTX2, and ignored malformed responses without corrupting state.
