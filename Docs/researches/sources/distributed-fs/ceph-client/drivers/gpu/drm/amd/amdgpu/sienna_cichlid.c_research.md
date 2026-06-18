# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sienna_cichlid.c

Purpose: reset-control implementation for Sienna Cichlid mode2 resets. It registers a reset handler that suspends graphics/SDMA state, asks DPM/SMU to perform a mode2 reset, restores GFXHUB and selected IP blocks, resumes RAS/IRQ state, and reruns IB tests.

Important APIs, types, and functions: exported `sienna_cichlid_reset_init()` and `sienna_cichlid_reset_fini()` allocate/free `adev->reset_cntl`. Static handler functions implement reset-handler callbacks: default selection, handler lookup, prepare hardware context, perform reset, restore hardware context, async reset work, and direct `do_reset`.

Control flow: handler lookup honors an explicit reset method, otherwise selects mode2 only when `amdgpu_reset_method` requests it. Preparation ungates PG/CG and suspends GFX and SDMA blocks in reverse order for non-SRIOV. Reset clears PCI bus mastering and calls `amdgpu_dpm_mode2_reset()`. Restore starts PSP RLC autoload, restores and reenables GFXHUB GART, resumes IH, then GFX/SDMA, runs late init, regates PG/CG, registers the GPU instance, resumes RAS/IRQ reset helpers, and runs IB ring tests.

State and persistence: state is in `adev->reset_cntl`, reset work item, active reset method, IP block status flags, GFXHUB saved registers, and hardware reset side effects. No persistent storage exists.

Dependencies and integration points: depends on amdgpu reset framework, DPM mode2 reset, PSP RLC autoload, GFXHUB callbacks, IP block suspend/resume, RAS, IRQ reset helpers, PCI bus-mastering control, and IB ring tests.

Risks and test signals: mode2 support is gated by a disabled firmware-version block and currently by module reset method, so default behavior is conservative. Restore ordering is critical: GFXHUB and IH must come back before GFX/SDMA work. Test signals are successful mode2 reset recovery, no GART faults after restore, RAS resume, IRQ reenablement, and passing IB ring tests.
