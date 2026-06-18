## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_jpeg.c

Purpose: implements shared JPEG engine software lifecycle, idle power-gating coordination, ring and IB tests, RAS poison handling, PSP SRAM update, debugfs/sysfs controls, IP state dump, and JPEG command-stream validation.

Important APIs/functions: `amdgpu_jpeg_sw_init/fini()` initialize delayed idle work, power-gating lock, submission count, DPG SRAM BOs, rings, and register dump storage. `amdgpu_jpeg_ring_begin_use/end_use()` ungate/gate the JPEG IP around submissions through `amdgpu_device_ip_set_powergating_state()`. `amdgpu_jpeg_dec_ring_test_ring()` and `amdgpu_jpeg_dec_ring_test_ib()` verify register writes through ring packets or direct IB jobs. RAS paths are `amdgpu_jpeg_process_poison_irq()`, `amdgpu_jpeg_ras_sw_init()`, and `amdgpu_jpeg_ras_late_init()`. `amdgpu_jpeg_dec_parse_cs()` validates PACKETJ command streams.

Control flow: init allocates per-instance DPG SRAM BOs only when PSP firmware loading and JPEG DPG are enabled, skipping harvested instances. Submission begin increments an atomic count, cancels idle work, ungates under mutex; end decrements and schedules idle work. The idle worker counts outstanding ring fences and submission count, gates the IP when idle, otherwise reschedules itself. Ring tests write known values to JPEG pitch registers and poll with `adev->usec_timeout`. IB tests allocate a direct job, write PACKETJ commands, wait on the fence, and then verify the register value outside SRIOV. CS parsing walks two dwords at a time, rejects reserved bits, invalid types, invalid conditions, and writes outside the allowed JPEG register range or inside atomic registers.

State and persistence: runtime state is under `adev->jpeg`: instance/ring arrays, harvest mask, delayed work, lock, atomic submission count, RAS interface, DPG SRAM BOs, debug caps/reset mask, and IP dump buffers. Debugfs can mutate `ring->sched.ready`; sysfs exposes supported reset masks. No disk persistence exists.

Dependencies/integration: depends on AMDGPU rings/jobs/fences, PSP firmware load, RAS dispatch, debugfs/sysfs, SOC15 register macros, power-gating via common IP code, and KMS hardware info that reports JPEG rings.

Risks: idle gating races are mitigated by atomic submission count plus mutex, but callers must pair begin/end. Debugfs scheduler mask can disable all but rejects a zero effective mask; it directly toggles scheduler readiness. CS parser assumes even-length packet layout by stepping two dwords; malformed lengths need upstream validation. DPG SRAM size and pointer advancement must match version-specific programming.

Test signals: JPEG ring/IB tests, command submission parser negative tests, suspend canceling idle work, debugfs sched mask get/set, sysfs reset mask, RAS poison IRQ dispatch, harvested-instance boot, SRIOV ring tests skipping MMIO verification, and coredump IP state printing.
