# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c

## Purpose

`mxgpu_ai.c` implements SR-IOV virtualization mailbox operations for AMDGPU AI-era hardware. It lets a VF communicate with the PF for full-GPU access, reset coordination, init-data exchange, RAS poison/bad-page handling, and mailbox interrupt setup. It exports `xgpu_ai_virt_ops` and several IRQ setup helpers used by SOC15 virtualization code.

## Important APIs, Types, And Functions

Externally visible functions are `xgpu_ai_mailbox_set_irq_funcs`, `xgpu_ai_mailbox_add_irq_id`, `xgpu_ai_mailbox_get_irq`, `xgpu_ai_mailbox_put_irq`, and `const struct amdgpu_virt_ops xgpu_ai_virt_ops`. Internal helpers include mailbox valid/ack primitives, `xgpu_ai_mailbox_trans_msg`, polling functions for ACK/messages/reset completion, access request/release wrappers, workqueue handlers for FLR and RAS bad pages, IRQ set/process callbacks, `xgpu_ai_ras_poison_handler`, and `xgpu_ai_rcvd_ras_intr`.

## Control Flow

Message transmission clears TRN valid until ACK deasserts, writes request/data dwords, sets valid, polls PF ACK, and clears valid. Full-GPU init/fini/reset requests then poll for `IDH_READY_TO_ACCESS_GPU`; init/reset also capture a checksum key from receive DW2. Reset requests retry up to `AI_MAILBOX_POLL_MSG_REP_MAX`. IRQ setup registers BIF client interrupt IDs 135 for receive and 138 for ACK, enables their interrupt bits, and initializes work items. Receive IRQ dispatches mailbox events: bad-page ready/notification schedules data-exchange work, unrecoverable error marks RAS RMA and schedules FLR recovery, FLR notification schedules reset-domain work, and query-alive is acknowledged.

## State And Persistence Behavior

State is held in hardware mailbox registers, `adev->virt` work items/IRQ sources, `adev->virt.fw_reserve.checksum_key`, `adev->virt.req_init_data_ver`, reset-domain scheduling state, and RAS context `is_rma`. Polling uses fixed millisecond timeouts. Work handlers call `amdgpu_virt_fini_data_exchange`, `amdgpu_virt_init_data_exchange`, `amdgpu_virt_request_bad_pages`, and `amdgpu_device_gpu_recover` under reset-domain constraints.

## Dependencies And Integration Points

The file depends on NBIO, GC, MP, SOC15, Vega10 IH, AMDGPU reset, RAS, IRQ, SR-IOV runtime, and reset-domain infrastructure. `soc15.c` includes the header and wires these ops into virtualized AI devices. It uses `RREG/WREG*_NO_KIQ` because mailbox access may occur in contexts where KIQ is unsuitable.

## Risks

Mailbox handshakes are timing-sensitive. `xgpu_ai_mailbox_peek_msg` is documented as IRQ-only but is also used by reset wait and RAS interrupt checks, so callers must understand validity assumptions. Busy wait/poll loops can delay recovery. Receive IRQ accesses `ras->is_rma` without a visible null check after `amdgpu_ras_get_context`. Work scheduling is best-effort via reset-domain queues and can fail with warnings. The typo `AI_MAIBOX` is baked into macro names but harmless if used consistently.

## Test Signals

Test PF/VF mailbox access negotiation, init-data request, reset request/release, FLR notification and completion waits, IRQ enable/disable, ACK/receive interrupts, RAS poison and bad-page flows, unrecoverable error handling, and timeout logging. SR-IOV runtime tests should validate no KIQ dependency and correct reset-domain work scheduling.
