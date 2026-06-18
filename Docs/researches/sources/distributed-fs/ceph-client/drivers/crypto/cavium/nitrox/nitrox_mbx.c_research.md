# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_mbx.c

## Purpose

`nitrox_mbx.c` implements the PF-to-VF mailbox handling used when Nitrox SR-IOV is enabled. The physical function receives VF mailbox interrupts, decodes per-ring VF requests from NPS mailbox CSRs, and replies asynchronously from a workqueue with VF mode, VF up/down state, chip/VF IDs, and microcode information.

## Important APIs, Types, And Functions

- `enum mbx_msg_type` defines NOP, request, ACK, and NACK message types.
- `enum mbx_msg_opcode` defines supported VF requests: `MSG_OP_VF_MODE`, `MSG_OP_VF_UP`, `MSG_OP_VF_DOWN`, `MSG_OP_CHIPID_VFID`, and `MSG_OP_MCODE_INFO`.
- `struct pf2vf_work` packages a VF device, PF device, and `work_struct` for deferred response handling.
- `pf2vf_read_mbox()` reads `NPS_PKT_MBOX_VF_PF_PFDATAX(ring)`.
- `pf2vf_write_mbox()` writes `NPS_PKT_MBOX_PF_VF_PFDATAX(ring)`.
- `pf2vf_send_response()` transforms a VF request into an ACK response and updates `nitrox_vfdev` state.
- `pf2vf_resp_handler()` runs workqueue processing for one mailbox request.
- `nitrox_pf2vf_mbox_handler()` is called from the PF SR-IOV interrupt path and fans out work for set interrupt bits in low/high mailbox interrupt registers.
- `nitrox_mbox_init()` allocates per-VF state, initializes VF numbers, creates the `nitrox_pf2vf` workqueue, and enables mailbox interrupts.
- `nitrox_mbox_cleanup()` disables interrupts, destroys the workqueue, and frees VF state.

## Control Flow

SR-IOV setup calls `nitrox_mbox_init()` after PF SR-IOV interrupt registration. When mailbox interrupts arrive, `nitrox_pf2vf_mbox_handler()` reads `NPS_PKT_MBOX_INT_LO` for rings 0-63 and `NPS_PKT_MBOX_INT_HI` for rings 64-127. For each set bit it computes the VF number using `ring / ndev->iov.max_vf_queues`, stores the ring and request message into the corresponding `nitrox_vfdev`, allocates `pf2vf_work` with `GFP_ATOMIC`, queues the work item, and clears the interrupt bit by writing `BIT_ULL(i)`.

The worker handles only request-type messages. `MSG_OP_VF_MODE` returns `ndev->mode`; `MSG_OP_VF_UP` records VF queue count from message data and marks the VF ready; `MSG_OP_CHIPID_VFID` returns PF device index and VF number; `MSG_OP_VF_DOWN` clears VF queue count and marks it not ready; `MSG_OP_MCODE_INFO` reports two microcode types. Non-supported opcodes become NOP and do not produce a response.

## State And Persistence Behavior

Per-VF mutable state is stored in `ndev->iov.vfdev[]`: VF number, current ring, last message, queue count, readiness, and mailbox response counter. The PF workqueue is stored at `ndev->iov.pf2vf_wq`. Hardware state is the pair of VF-to-PF and PF-to-VF mailbox CSRs and interrupt bits. State persists while SR-IOV remains enabled; cleanup zeros the workqueue and VF array pointers.

## Dependencies And Integration Points

This code depends on Nitrox CSR definitions, mailbox message layout in `union mbox_msg`, VF state in `struct nitrox_vfdev`, HAL interrupt toggles `enable_pf2vf_mbox_interrupts()`/`disable_pf2vf_mbox_interrupts()`, and the SR-IOV lifecycle in `nitrox_sriov.c`. It integrates with interrupt dispatch from the Nitrox ISR code, which calls `nitrox_pf2vf_mbox_handler()`.

## Risks And Edge Cases

- If `kzalloc_obj(..., GFP_ATOMIC)` fails in the interrupt handler, the request is skipped but the interrupt bit is still cleared, so the VF may need retry logic.
- Ring-to-VF mapping assumes `max_vf_queues` is nonzero and matches hardware mode.
- `vfdev->msg` and `vfdev->ring` are written in interrupt context and read in workqueue context without an explicit per-VF lock; repeated requests for the same VF can overwrite state before prior work runs.
- Cleanup destroys the workqueue after disabling interrupts, which drains queued work, but caller ordering must prevent new mailbox handler invocations.

## Test Signals

Signals include successful VF queries for mode, chip/VF ID, and microcode info; VF up/down state changes; mailbox response counters increasing; no lost interrupt bits under low/high register coverage; SR-IOV teardown without queued work use-after-free; and VF retry behavior when PF allocation pressure drops a response.
