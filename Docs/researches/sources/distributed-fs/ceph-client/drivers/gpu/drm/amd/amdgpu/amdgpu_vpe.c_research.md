# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vpe.c

## Purpose

This file implements AMDGPU's Video Processing Engine IP block support for VPE 6.1 family hardware. It handles early IP function selection, firmware loading, a command ring, DPM configuration, power gating, idle work, ring packet emission, preemption, reset, self-tests, and a reset-mask sysfs attribute.

## Important APIs, types, and functions

Externally visible functions include `amdgpu_vpe_configure_dpm()`, `amdgpu_vpe_psp_update_sram()`, `amdgpu_vpe_init_microcode()`, `amdgpu_vpe_ring_init()`, `amdgpu_vpe_ring_fini()`, `amdgpu_vpe_sysfs_reset_mask_init()`, and `amdgpu_vpe_sysfs_reset_mask_fini()`. The IP block is `vpe_v6_1_ip_block`, using `vpe_ip_funcs`. The ring function table `vpe_ring_funcs` supplies packet operations for NOP, IB, fence, VM flush, register writes/waits, conditional execute, preempt, begin/end use, and reset.

## Control flow, state, and persistence behavior

Early init selects VPE 6.1 function hooks based on IP version, enables collaborate mode for IP 6.1.1, installs ring functions, and caches register offsets. Software init allocates a one-page GTT command buffer, initializes IRQ, ring, microcode, reset mask, and sysfs. Microcode init requests `amdgpu/<ip-version>.bin`, parses firmware version and feature version, and registers VPE context/control firmware chunks for PSP loading when PSP firmware loading is active. Hardware init ungates VPE, loads microcode through hardware-specific callbacks, and starts the ring. Hardware fini cancels idle work, stops the ring, and gates power.

The ring path writes VPE-specific packets for indirect buffers, fences/traps, pipeline sync, register writes, register waits, VM flushes through GMC helpers, and conditional execution. `begin_use()` cancels idle power-down, ungates VPE, and toggles a context indicator on first context use. `end_use()` schedules delayed idle work. The idle worker waits until no emitted fences remain and, for older PM firmware needing DPM0 at power-down, until the requested DPM level is zero before gating VPE.

## Dependencies and integration points

The file depends on firmware loading, AMDGPU ucode metadata, PSP, SMU/DPM clock tables, SOC15 flush helpers, VPE 6.1 register functions, ring/fence/IB infrastructure, workqueues, and AMDGPU reset helpers. It integrates with power management through `amdgpu_device_ip_set_powergating_state()` and `amdgpu_dpm_enable_vpe()`, and with sysfs through `vpe_reset_mask`.

## Risks and test signals

Risks include firmware header mismatch, DPM ratio calculation errors, power-gating races with in-flight fences, collaborate-mode doorbell assumptions, ring preemption timeout handling, CSA address assumptions, and reset path failures leaving the ring unusable. Test signals are successful VPE firmware load, ring and IB tests writing `0xdeadbeef`, VM flush packet operation on VPE jobs, idle power-gating/resume under repeated submissions, reset-mask sysfs presence, and timeout recovery through `vpe_ring_reset()`.
