# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mbox.c

## Purpose
Implements shared RVU mailbox helpers for AF/PF/VF communication. It initializes mailbox regions, selects direction-specific windows and doorbell registers, allocates request/response slots, sends down/up messages, waits for responses, validates replies, creates invalid-message responses, detects pending messages, and maps message IDs to names.

## Important APIs, Types, and Functions
Public functions include `__otx2_mbox_reset`, `otx2_mbox_reset`, `otx2_mbox_destroy`, `otx2_mbox_init`, `otx2_mbox_regions_init`, `otx2_mbox_msg_send`, `otx2_mbox_msg_send_up`, `otx2_mbox_wait_for_rsp`, `otx2_mbox_busy_poll_for_rsp`, `otx2_mbox_wait_for_zero`, `otx2_mbox_alloc_msg_rsp`, `otx2_mbox_get_rsp`, `otx2_mbox_check_rsp_msgs`, `otx2_reply_invalid_msg`, `otx2_mbox_nonempty`, and `otx2_mbox_id2name`. Setup is split between CN20K-specific `cn20k_mbox_setup` and generic `otx2_mbox_setup`.

## Control Flow
Setup chooses TX/RX offsets and trigger CSR based on mailbox direction and chip generation. Initialization assigns contiguous or per-peer mailbox bases, initializes locks, and resets headers. Allocation aligns sizes, checks TX/RX space, increments `num_msgs`, zeros message/header regions, initializes version, advances sizes, and stores `next_msgoff`. Sending optionally copies from a bounce buffer, writes headers, resets construction counters, issues `smp_wmb`, clears peer RX `num_msgs`, traces, and rings the doorbell. Response helpers poll or walk request/response chains, matching IDs and returning response errors.

## State and Persistence Behavior
Shared hardware memory holds mailbox headers and payloads. Host-only `struct otx2_mbox_dev` counters track staged size, expected response size, sent messages, and acknowledged messages. Doorbell CSR state is read-modify-written on send. Reset zeros both TX and RX headers and local counters.

## Dependencies and Integration Points
Depends on PCI, spinlocks, jiffies, MMIO, memory barriers, tracepoints, `rvu_reg.h`, `cn20k/reg.h`, `cn20k/api.h`, `mbox.h`, and `rvu.h`. It is used by AF/PF/VF control paths across CGX, NIX, NPA, NPC, CPT, MCS, SDP, and representor support.

## Risks
Ordering is critical: payload and header must be visible before the doorbell. If interrupt handlers do not update `msgs_acked`, waits time out. `otx2_mbox_msg_send_data` avoids rewriting a nonzero `tx_hdr->sig`, so stale signatures must be managed by reset and peer processing. Sparse region setup leaves unselected devices uninitialized.

## Test Signals
AF/PF, PF/AF, PF/VF, VF/PF, and up-message traffic on pre-CN20K and CN20K, multi-message batches, mailbox full failures, bounce-buffer path, timeout tracepoint, busy-poll path, invalid response ID, nonzero response `rc`, invalid-message replies, reset during FLR/probe/remove, sparse region init, and wait-for-zero behavior.
