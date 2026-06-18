# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ih.c

## Purpose
`amdgpu_ih.c` implements common Interrupt Handler ring allocation, teardown, software IV injection, checkpoint waiting, ring processing, IV decoding, timestamp decoding, and ring naming. It is the common logic used by hardware IH rings and the software/delegated IH ring.

## Important APIs, types, and functions
The public API includes `amdgpu_ih_ring_init()`, `amdgpu_ih_ring_fini()`, `amdgpu_ih_ring_write()`, `amdgpu_ih_wait_on_checkpoint_process_ts()`, `amdgpu_ih_process()`, `amdgpu_ih_decode_iv_helper()`, `amdgpu_ih_decode_iv_ts_helper()`, and `amdgpu_ih_ring_name()`.

## Control flow
Ring initialization rounds the requested byte size to a power-of-two dword ring, sets masks and pointers, then either allocates one coherent DMA buffer containing ring plus shadow wptr/rptr storage or allocates a GTT BO plus writeback slots. Processing reads the hardware/software wptr, orders ring data with `rmb()`, dispatches up to `AMDGPU_IH_MAX_NUM_IVS` vectors through `amdgpu_irq_dispatch()`, writes the rptr unless overflow is set, wakes checkpoint waiters, and loops if the wptr advanced while processing. Overflow during SR-IOV runtime schedules FLR recovery work. Software write copies IV dwords, wraps the byte wptr, and commits it only if it would not equal rptr.

## State and persistence behavior
`struct amdgpu_ih_ring` stores ring allocation handles, CPU/GPU addresses, shadow pointers, enabled flag, rptr, processed timestamp, waitqueue, and overflow state. Ring content and pointers are runtime-only and are freed at driver teardown.

## Dependencies and integration points
The file depends on DMA coherent allocation, AMDGPU BO/writeback helpers, IRQ dispatch, reset domain scheduling, SR-IOV runtime state, and `amdgpu_ih_funcs` hardware callbacks for wptr/rptr handling and decoding. GMC retry-fault filtering uses IH timestamps and software ring delegation.

## Risks and edge cases
Ring-size rounding changes the requested size. The non-coherent teardown computes writeback offsets from `wptr_addr - gpu_addr`, which assumes those addresses share the same base; this is inherited driver behavior and needs caution. Software ring writes drop/skip commit on overflow and only warn for retry CAM. Processing caps IVs per pass but loops on new wptr changes, so interrupt storms and overflow handling are important.

## Test signals
IH allocation in bus-address and GTT/writeback modes, IV decode correctness, software ring delegation, checkpoint waits, overflow behavior, SR-IOV FLR scheduling, interrupt storm processing, teardown leak checks, and timestamp wrap comparisons are important tests.
