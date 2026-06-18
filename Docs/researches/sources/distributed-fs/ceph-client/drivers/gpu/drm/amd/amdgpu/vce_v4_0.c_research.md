# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v4_0.c

## Purpose

`vce_v4_0.c` implements the AMDGPU VCE 4.0 video encode IP block. It wires the VCE block into the AMDGPU IP lifecycle, programs firmware and VCPU memory windows, initializes up to three encode rings, supports the SR-IOV MMSCH initialization path, emits VCE ring packets for IBs, VM flushes, fences, register waits/writes, and services VCE fence interrupts.

## Important APIs, Types, And Functions

The exported integration object is `vce_v4_0_ip_block`, backed by `vce_v4_0_ip_funcs`. Lifecycle entry points are `vce_v4_0_early_init()`, `sw_init()`, `sw_fini()`, `hw_init()`, `hw_fini()`, `suspend()`, and `resume()`. `vce_v4_0_start()` is the normal hardware boot path: it writes ring bases/sizes for rings 0, 1, and 2, calls `vce_v4_0_mc_resume()`, releases the ECPU reset, waits in `vce_v4_0_firmware_loaded()`, and clears the busy flag. `vce_v4_0_sriov_start()` builds an MMSCH v1.0 command table and `vce_v4_0_mmsch_start()` submits it through the VF mailbox.

Ring operations are collected in `vce_v4_0_ring_vm_funcs`. Pointer accessors select register sets by `ring->me` and use doorbells when configured. Packet emitters include `vce_v4_0_ring_emit_ib()`, `vce_v4_0_ring_emit_fence()`, `vce_v4_0_emit_vm_flush()`, `vce_v4_0_emit_reg_wait()`, `vce_v4_0_emit_wreg()`, and `vce_v4_0_ring_insert_end()`.

## Control Flow

Early init delegates common VCE setup to `amdgpu_vce_early_init()`, chooses one ring for SR-IOV or three rings for bare metal, and installs ring/IRQ functions. Software init registers the VCE interrupt, allocates the VCE firmware BO through common VCE code, handles PSP firmware metadata and saved BO allocation when applicable, initializes all rings, and allocates the virtualization MM table. Hardware init chooses the direct or SR-IOV start path, then runs `amdgpu_ring_test_helper()` on each active ring.

Suspend saves the VCPU BO for PSP-loaded firmware, cancels idle work, gates clocks/power or disables DPM, stops the block, and calls common VCE suspend. Resume restores the saved BO or reloads firmware, then reruns hardware init. Powergating state changes simply stop or start the block; clockgating is a no-op stub kept for unload compatibility.

## State And Persistence

State is held under `adev->vce`: firmware, `vcpu_bo`, `saved_bo`, `gpu_addr`, mapped CPU address, ring array, idle work, IRQ source, and the SR-IOV MM table in `adev->virt.mm_table`. PSP firmware mode persists a saved VCPU BO image across suspend/resume. Doorbell write pointers persist in ring writeback memory and are reset before MMSCH initialization.

## Dependencies And Integration Points

The file depends on AMDGPU VCE common helpers, SOC15 register accessors, VCE 4.0 register offsets/masks, MMHUB register metadata, MMSCH v1.0 table formats, PSP firmware loading, DPM/powergating hooks, doorbell writes, ring scheduling, VM hub TLB flush helpers, and IRQ/fence processing. It integrates with the AMD IP block table as `AMD_IP_BLOCK_TYPE_VCE` major 4.0 and with common VCE CS parsing/tests via the ring function table.

## Risks And Test Signals

Risks include firmware-load timeouts, incorrect cache-window offsets between PSP and non-PSP firmware loading, SR-IOV MMSCH table size or offset corruption, doorbell/write-pointer desynchronization, powergating races with delayed idle work, and interrupt source data outside the three-ring range. Good test signals are successful firmware boot, ring tests for all active rings, suspend/resume with PSP and non-PSP firmware, SR-IOV VF MMSCH startup, VM flush/fence completion, interrupt fence processing for rings 0 to 2, and timeout handling when the VCE status bit never reports firmware loaded.
