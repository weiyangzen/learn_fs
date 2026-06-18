# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-vpu.c

## Purpose
This file implements MDP3 communication with the MediaTek SCP/VPU firmware. It registers IPI handlers, allocates shared DMA working buffers, sends init/deinit/frame messages, and waits for firmware acknowledgements.

## Important APIs, Types, And Functions
`mdp_vpu_register()` and `mdp_vpu_unregister()` bind SCP IPI handlers for init, deinit, and frame messages. `mdp_vpu_dev_init()` performs a two-stage init: first asks firmware for work size, then allocates aligned parameter/work/config buffers and sends the work address back. `mdp_vpu_dev_deinit()` sends deinit. `mdp_vpu_process()` copies an `img_ipi_frameparam` into shared memory and sends a frame request. `mdp_vpu_shared_mem_free()` releases the DMA buffers. Internal ack handlers update `vpu->status` and complete `ipi_acked`.

## Control Flow
The core driver boots the remote processor and calls init on first stream use. For each job, M2M code fills a frame parameter and calls `mdp_vpu_process()`. The function locks shared memory, allocates if needed, clears buffers, writes virtual/physical self/config pointers into the parameter, copies it to shared memory, unlocks, sends an SCP IPI, and waits up to 500 ms for completion.

## State, Persistence, And Dependencies
State lives in `struct mdp_vpu_dev`: SCP handle, shared DMA virtual/physical addresses, sizes, completion, lock, and firmware status. No persistent storage is used. Dependencies include SCP IPI APIs, remoteproc, DMA write-combine allocation, and image IPI structs.

## Integration Points
`mtk-mdp3-core.c` manages VPU lifetime and IPI registration. `mtk-mdp3-m2m.c` calls `mdp_vpu_process()` before CMDQ submission and consumes `vpu.config`.

## Risks
The completion object is reused for multiple messages, so serialization through `vpu->lock` and higher-level VPU references is important. Shared-memory allocation failure unwinds partially allocated buffers. DMA addresses are stored in 32-bit message fields, relying on device addressing constraints. Timeout or nonzero firmware status maps to generic errors.

## Test Signals
SCP boot/init/deinit cycles, firmware timeout injection, shared-memory allocation failure, repeated stream open/close, and valid CMDQ config returned for real image transforms.
