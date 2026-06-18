# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_0.c

## Purpose

`vcn_v2_0.c` implements VCN 2.0 for AMDGPU. It carries forward the decode/encode ring model while adding doorbell-based write pointers, internal register-offset aliases for KMD commands, firmware shared multi-queue state, SR-IOV MMSCH v2.0 startup, reset support, register dump/sysfs reset-mask integration, and DPG/indirect-SRAM boot support.

## Important APIs, Types, And Functions

The main export is `vcn_v2_0_ip_block`. Lifecycle hooks in `vcn_v2_0_ip_funcs` call `vcn_v2_0_early_init()`, `sw_init()`, `hw_init()`, suspend/resume, idle checks, and clock/power state handlers. `vcn_v2_0_start()` handles the normal direct boot path, while `vcn_v2_0_start_dpg_mode()` handles DPG and optional PSP SRAM update. `vcn_v2_0_start_sriov()` builds an MMSCH v2.0 table for VF operation and `vcn_v2_0_start_mmsch()` submits it.

Several ring helpers are exported through `vcn_v2_0.h` for reuse by later generations: decode start/end/NOP, decode fence/IB/reg-wait/VM-flush/wreg, encode fence/IB/reg-wait/VM-flush/wreg/end, and `vcn_v2_0_dec_ring_test_ring()`. Ring function tables install these helpers plus `amdgpu_vcn_ring_begin_use()`, `amdgpu_vcn_ring_end_use()`, and `amdgpu_vcn_ring_reset()`.

## Control Flow

Early init chooses one encoder ring for SR-IOV VFs and two otherwise. Software init registers decode and encode interrupts, initializes common VCN firmware, enables doorbells, sets per-ring VM hubs, fills internal/external register offsets, assigns reset callbacks, allocates the virtualization MM table, sets `AMDGPU_VCN_MULTI_QUEUE_FLAG` in firmware shared memory, initializes fwlog/register dump/reset-mask sysfs, and marks supported reset types.

Hardware init enables the VCN doorbell range, starts the SR-IOV MMSCH path for VFs, tests decode, disables VF decode scheduling, and tests encoder rings. Normal start powers up VCN through DPM, configures clock/power gating, programs firmware/stack/context/non-cache windows, boots VCPU, resets decode and encode queue state through `fw_shared->multi_queue`, and initializes ring registers. DPG start writes similar state through DPG-mode accessors and can push an indirect SRAM image through PSP.

## State And Persistence

Persistent runtime state includes `adev->vcn.inst[0]` firmware, `fw_shared`, rings, internal/external register aliases, reset callbacks, DPG SRAM pointer, pause state, supported reset mask, virtualization MM table, and sysfs reset-mask state. Doorbell writeback memory persists ring write pointers. `fw_shared->multi_queue.*_queue_mode` is used to coordinate queue resets with firmware.

## Dependencies And Integration Points

Dependencies include common VCN helpers, PSP SRAM update, MMSCH v2.0 definitions, SOC15/VCN 2.0 registers, IRQ source IDs, DPM, NBIO doorbell ranges, VM/GMC TLB flushing, ring scheduling, register dump helpers, and sysfs reset-mask support. It integrates with later VCN generations by exporting reusable ring emitters.

## Risks And Test Signals

Risks include doorbell index mistakes, SR-IOV decode scheduling assumptions, stale multi-queue reset flags, indirect SRAM load failures, DPG pause restoring rings with wrong write pointers, MMSCH table corruption, and generation-specific internal register offsets diverging from firmware expectations. Test signals are decode/encode ring tests, doorbell writeback checks, SR-IOV VF startup with encode-only scheduling, DPG direct and indirect modes, reset-mask sysfs behavior, per-queue reset, interrupt routing for decode/general/low-latency encode, and firmware shared queue-state validation.
