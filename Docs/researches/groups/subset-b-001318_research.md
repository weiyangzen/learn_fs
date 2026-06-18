# Research: subset-b-001318 AMDGPU IP, IRQ, KMS, MES, Media, RAS, and Display Headers

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ip.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ip.c

Purpose: implements common AMDGPU IP block registry, discovery helpers, lifecycle wrappers, and logical-to-physical hardware instance mapping. It is the thin coordination layer used by device setup, power management, KMS queries, and block-specific code that needs to find or control an IP by `enum amd_ip_block_type`.

Important APIs/functions: `amdgpu_ip_map_init()` builds `adev->ip_map` for GC, SDMA, and VCN/JPEG aliases using masks discovered elsewhere; `amdgpu_device_ip_block_add()` appends `struct amdgpu_ip_block_version` entries into `adev->ip_blocks`; `amdgpu_ip_block_suspend()` and `amdgpu_ip_block_resume()` delegate to block `suspend`/`resume` callbacks and update `status.hw`; query helpers include `amdgpu_device_ip_get_ip_block()`, `amdgpu_device_ip_block_version_cmp()`, `amdgpu_device_ip_is_hw()`, and `amdgpu_device_ip_is_valid()`. Clock/power gating wrappers iterate valid blocks and call optional per-IP callbacks.

Control flow: device setup calls `amdgpu_device_ip_block_add()` for ASIC-supported blocks. The add path rejects null versions and silently skips harvested VCN/JPEG blocks based on `adev->harvest_ip_mask`, then logs the version tuple and stores the block. Power and clock gating requests walk the active block array, skip invalid or type-mismatched entries, call optional function pointers, and return the last error. Idle waiting resolves one block by type and invokes `wait_for_idle` if present. Logical instance conversion only translates GC, SDMA0, and VCN/JPEG through `adev->ip_map.dev_inst`; other IPs assume logical equals physical.

State and persistence: all state is in-memory on `struct amdgpu_device`: `ip_blocks[]`, `num_ip_blocks`, `ip_map.dev_inst`, and per-block `status`. There is no durable storage. Suspension/resume mutates `status.hw`, while validity is managed by surrounding device code.

Dependencies/integration: depends on `amdgpu.h`, `amdgpu_ip.h`, `amd_shared.h`, block `amd_ip_funcs`, harvesting flags, and IP discovery masks. KMS uses the query helpers for hardware IP info/counts; JPEG idle power management calls `amdgpu_device_ip_set_powergating_state()`.

Risks: `amdgpu_device_ip_block_add()` does not bounds-check `adev->num_ip_blocks` against `AMDGPU_MAX_IP_NUM`, so callers must enforce list capacity. `amdgpu_logical_to_dev_mask()` assumes mapped instances are nonnegative and small enough for `1 << dev_inst`; malformed masks or uninitialized maps could produce invalid shifts. Clock/power gating returns only the last callback error, potentially hiding earlier failures.

Test signals: boot logs should show expected IP block detection strings and absence of harvested VCN/JPEG. Suspend/resume tests should see `status.hw` transitions and no callback errors. KMS `AMDGPU_INFO_HW_IP_*` queries and JPEG power-gating behavior indirectly validate the registry and type lookup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ip.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ip.h

Purpose: declares AMDGPU's hardware IP taxonomy, version encoding helpers, logical instance map, and IP block lifecycle/query API. It is the shared contract between ASIC setup code, IP block implementations, and cross-cutting callers such as KMS, power management, and recovery.

Important APIs/types: `enum amd_hw_ip_block_type` names hardware-discovery IPs and aliases `VCN_HWIP`/`JPEG_HWIP` to `UVD_HWIP` for discovery compatibility. `IP_VERSION_FULL()`, `IP_VERSION()`, and extractor macros encode major/minor/revision/variant/subrevision into a packed 32-bit value. `struct amdgpu_ip_map_info` stores logical-to-device instance mappings and function pointers. `struct amdgpu_ip_block_status`, `struct amdgpu_ip_block_version`, and `struct amdgpu_ip_block` describe an IP's runtime state, static version, callback table, and owning device.

Control flow contract: device code fills IP blocks with `amdgpu_device_ip_block_add()`, then calls block lifecycle functions through the function table referenced by `amdgpu_ip_block_version.funcs`. Consumers should use `amdgpu_device_ip_get_ip_block()` and validity/hardware helpers rather than walking `adev->ip_blocks` directly where possible. Clock/power gating and idle wrappers provide type-based broadcast or lookup.

State and persistence: the header defines only in-memory device state. `status.valid`, `status.sw`, `status.hw`, `status.late_initialized`, and `status.hang` are status bits used by initialization, runtime PM, reset, and diagnostics; the header does not prescribe persistence across driver unload.

Dependencies/integration: includes `amd_shared.h` for shared IP block and callback definitions and forward-declares `struct amdgpu_device`. The IP version macros are widely used by version-specific code such as ISP and MES firmware naming.

Risks: the enum includes fixed maximums (`HWIP_MAX_INSTANCE`, `HW_ID_MAX`) that must stay aligned with discovery data. Aliasing JPEG to VCN/UVD is intentional but easy to misread when writing code that needs a separate JPEG IP block versus an IP-discovery hardware ID. Callers of logical mapping functions must handle unmapped entries defensively.

Test signals: compile-time coverage should catch mismatched prototypes. Runtime validation comes from IP discovery, ASIC version selection, KMS hardware info queries, and successful load/unload across ASICs with harvested or multi-instance IPs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.c

Purpose: implements the generic AMDGPU interrupt subsystem: PCI IRQ/MSI setup, interrupt handler entry, IH ring dispatch, source registration, enable refcounting, reset-time state replay, and IRQ-domain forwarding for child components.

Important APIs/functions: `amdgpu_irq_init()` allocates one PCI IRQ vector, registers `amdgpu_irq_handler()`, initializes work handlers for IH1/IH2/soft IH, and marks IRQ state installed. `amdgpu_irq_add_id()` installs a `struct amdgpu_irq_src` under client/source IDs and allocates per-type atomic enable counters. `amdgpu_irq_get()`/`amdgpu_irq_put()` refcount interrupt enables and call `amdgpu_irq_update()` on 0-to-1 or 1-to-0 transitions. `amdgpu_irq_dispatch()` decodes IV entries, routes to registered source processors, IRQ domains, or AMDKFD fallback. `amdgpu_irq_gpu_reset_resume_helper()` restores MSI-X for VF/passthrough and reapplies every source state.

Control flow: hardware IRQs enter `amdgpu_irq_handler()`, which processes the primary IH ring and marks runtime PM activity when handled, then invokes fatal RAS interrupt handling. Secondary IH rings are processed from workqueue callbacks. Dispatch decodes the IV, validates client/source IDs, forwards legacy/ISP virqs through `generic_handle_domain_irq()` when mapped, otherwise calls `src->funcs->process()`. If no driver source claims the IV, AMDKFD receives it.

State and persistence: persistent runtime state lives in `adev->irq`: installed IRQ number, MSI status, client source arrays, atomic enable counters, IH rings, work items, IRQ domain, virq mappings, and reset-related fields. No disk persistence exists. The enable counters are the source of truth for whether `src->funcs->set()` should enable or disable hardware.

Dependencies/integration: depends on PCI IRQ APIs, Linux IRQ domains, DRM vblank, PM runtime, IH decode/process helpers, RAS fatal handling, AMDKFD interrupt delivery, and optional DC IRQ code. KMS vblank enable/disable uses `amdgpu_irq_get/put()` on `adev->crtc_irq`; NBIO/JPEG RAS late init enables IRQ sources through this subsystem.

Risks: incorrect source registration or `num_types` sizing can produce invalid refcount access. `amdgpu_irq_put()` guards RMA state specially and warns on underflow, but callers still need balanced get/put. Dispatch deliberately forwards unhandled IVs to KFD, so source processors should return nonzero only when fully handled. IRQ domain mask/unmask callbacks are stubs, making mapped child IRQ behavior dependent on simple handling.

Test signals: probe should allocate/free vectors cleanly with MSI enabled or disabled by module parameter. Interrupt tests should verify vblank, hotplug, RAS, IH1/IH2/soft delegation, reset resume state replay, and KFD interrupt delivery. Fault injection should exercise invalid client/source IDs without crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.h

Purpose: defines the AMDGPU interrupt ABI inside the driver: IV decode result shape, IRQ source callback contract, per-client source registry, IRQ domain state, and exported control functions.

Important APIs/types: `AMDGPU_MAX_IRQ_SRC_ID`, `AMDGPU_IRQ_CLIENTID_MAX`, and `AMDGPU_IRQ_SRC_DATA_MAX_SIZE_DW` bound source tables and IV payload. `struct amdgpu_iv_entry` carries decoded IH data such as client/source IDs, ring, VMID/PASID, timestamp, node ID, source data, and raw IV pointer. `struct amdgpu_irq_src` combines `num_types`, `enabled_types`, and `amdgpu_irq_src_funcs`. `struct amdgpu_irq` stores installed IRQ state, source clients, IH rings, work items, IRQ domain, virqs, and reset fields. `node_id_to_phys_map` maps AID/XCD node IDs to physical indices.

Control flow contract: IP blocks allocate and populate `amdgpu_irq_src` objects, call `amdgpu_irq_add_id()`, then use `amdgpu_irq_get()`/`amdgpu_irq_put()` as consumers appear or disappear. Each source must provide `set()` to program hardware interrupt enable state and `process()` to handle decoded IVs. External drivers can request IRQ-domain mappings via `amdgpu_irq_create_mapping()`.

State and persistence: state is per-device and in-memory. `enabled_types` atomic counters are allocated during registration and freed in software teardown. IH rings and virq mappings are owned by `struct amdgpu_irq`.

Dependencies/integration: includes Linux IRQ domain headers, SOC IH client ID headers, and `amdgpu_ih.h`. It is used by display, KMS, RAS blocks, media engines, IH implementation, and KFD.

Risks: the maximum client macro is tied to SOC15 client ID maximum even though the file also carries legacy constants; new hardware client IDs must keep those bounds correct. Source processors must tolerate IV fields that differ across ASIC generations. Missing or wrong `set` callbacks make get/put fail with `-EINVAL`.

Test signals: compilation across DC/non-DC and ASIC variants verifies the shared declarations. Runtime tests should cover IRQ source registration, enable refcounting, IV dispatch, domain mapping for delegated clients, and reset resume replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_isp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_isp.c

Purpose: integrates AMD ISP hardware as an AMDGPU IP block and exports buffer allocation helpers to an external V4L2/MFD ISP device. It selects version-specific ISP callbacks, loads ISP firmware for PSP, bridges runtime suspend/resume, and gives ISP clients GTT-backed GPU buffers.

Important APIs/functions: `isp_early_init()` selects `isp_v4_1_0_set_isp_funcs()` or `isp_v4_1_1_set_isp_funcs()` based on `amdgpu_ip_version()`, stores parent/device pointers, and calls `isp_load_fw_by_psp()`. `isp_hw_init()`, `isp_hw_fini()`, `isp_suspend()`, and `isp_resume()` delegate to `struct isp_funcs`. Exported symbols `isp_user_buffer_alloc/free()` import DMABUF-backed user buffers through `amdgpu_bo_create_isp_user()` and `amdgpu_bo_free_isp_user()`. Exported `isp_kernel_buffer_alloc/free()` allocate/free aligned GTT kernel BOs through AMDGPU BO helpers.

Control flow: early init decodes the firmware prefix, requests optional `amdgpu/<prefix>.bin`, registers it in `adev->firmware.ucode[AMDGPU_UCODE_ID_ISP]`, and increments PSP firmware size. Buffer allocation APIs convert the supplied device to a platform device, retrieve the first MFD cell's platform data, recover `adev`, validate that the ISP device parent is the AMDGPU device, then allocate and return BO handle plus GPU/CPU addresses.

State and persistence: runtime state is in `adev->isp`: callback table, firmware pointer, MFD resources, parent, harvest config, and generic PM domain. Buffer BOs are kernel objects whose lifetime is explicitly returned to the external ISP device via free calls; no disk persistence exists.

Dependencies/integration: depends on firmware loading, PSP firmware table, MFD platform data, Linux firmware APIs, BO/GART allocation helpers, and version-specific `isp_v4_1_0`/`isp_v4_1_1` implementations. It exports symbols for a V4L2 ISP driver outside the DRM device.

Risks: exported buffer APIs trust `mfd_cell[0].platform_data` after minimal checks; stale or malformed MFD data can crash before normal AMDGPU validation. `isp_kernel_buffer_alloc()` checks `!cpu_addr` instead of `!*cpu_addr`, so a null mapping would only be caught by `ret`. Firmware load failure makes early init fail with `-ENOENT`; optional firmware policy still releases on request failure.

Test signals: ISP-supported ASIC probe should select the correct callback table, load firmware, and complete IP lifecycle. External ISP tests should allocate/free user and kernel buffers, validate GPU address alignment (`ISP_MC_ADDR_ALIGN` for kernel buffers), and reject devices not parented by the AMDGPU device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_isp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_isp.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_isp.h

Purpose: declares the ISP IP block interface and per-device ISP state used by `amdgpu_isp.c` and version-specific ISP implementations.

Important APIs/types: `ISP_REGS_OFFSET_END` bounds ISP register resources. `struct isp_funcs` provides `hw_init`, `hw_fini`, `hw_suspend`, and `hw_resume` callbacks. `struct amdgpu_isp` stores parent `struct device`, owning `amdgpu_device`, callback table, MFD cell and resources for ISP/I2C/GPIO, platform data, harvest config, firmware pointer, and a generic PM domain. It declares `isp_v4_1_0_ip_block` and `isp_v4_1_1_ip_block` as IP block versions.

Control flow contract: ASIC code installs one of the exported IP block versions; early init then fills `amdgpu_isp.funcs` with version-specific operations. The external ISP stack is expected to receive platform data and resources derived from this state.

State and persistence: all state is runtime in-memory. Firmware lifetime is associated with the device's firmware table and `adev->isp.fw`. MFD resources are references to kernel resource descriptors, not durable data.

Dependencies/integration: includes `drm/amd/isp.h` for external ISP platform data and Linux PM-domain support. It integrates AMDGPU DRM with an MFD/V4L2-style ISP child device.

Risks: callback pointers are optional at the type level but `amdgpu_isp.c` returns `-ENODEV` when missing; version-specific setup must populate them before lifecycle use. Resource pointers must remain valid for the lifetime of child devices.

Test signals: compile coverage for both ISP versions, platform-device creation, runtime suspend/resume, and buffer allocation from the external ISP driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_isp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_job.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_job.c

Purpose: implements AMDGPU job allocation, scheduler backend callbacks, direct IB submission, timeout recovery, resource cleanup, and forced job poisoning. It connects DRM GPU scheduler jobs to AMDGPU rings, VMID assignment, fences, resets, and coredumps.

Important APIs/functions: `amdgpu_job_alloc()` and `amdgpu_job_alloc_with_ib()` allocate flexible `struct amdgpu_job` objects with HW and VM fences. `amdgpu_job_submit()` arms a DRM scheduler job and pushes it; `amdgpu_job_submit_direct()` bypasses entity scheduling and calls `amdgpu_ib_schedule()`. Backend ops are `amdgpu_job_prepare_job()`, `amdgpu_job_run()`, `amdgpu_job_timedout()`, and `amdgpu_job_free_cb()`. `amdgpu_job_stop_all_jobs_on_sched()` drains queued and pending jobs with `-EHWPOISON`.

Control flow: scheduled jobs first run `prepare_job`, which checks entity errors, handles gang switching, enforces isolation, and grabs a VMID if needed. `run_job` validates VM generation and gang resubmit policy, schedules IBs to the target ring, increments `job_run_counter`, and frees IB resources against the proper fence. Timeout handling first records IP state and coredumps non-SRIOV devices, attempts soft recovery when supported, then tries per-queue reset, otherwise marks the finished fence with `-ETIME` and calls full GPU recovery if allowed. When recovery is disabled or unsuitable, the scheduler is suspended and SRIOV TDR debug is marked.

State and persistence: jobs hold VM pointer, explicit sync, fences, IBs, PASID/VMID, preamble/preemption flags, user fence address/sequence, shadow/CSA/GDS virtual addresses, generation, and isolation flags. State is transient but error status is propagated through DMA fences and coredump infrastructure.

Dependencies/integration: depends on DRM scheduler, DMA fences, AMDGPU IB/ring/fence, VM generation/VMID, reset domain, XGMI hive handling, coredump, KFD/PASID task info, and GPU recovery policy.

Risks: timeout paths are concurrency-heavy and touch scheduler state, reset state, coredumps, XGMI hive locks, and fences; ordering bugs can deadlock or double signal. `amdgpu_job_stop_all_jobs_on_sched()` is explicitly documented as duplicated and racy, retained only temporarily. Direct submission transfers ownership by freeing the job after successful IB scheduling, so callers must not reuse it after success.

Test signals: scheduler unit/integration tests should cover normal submit, direct ring tests, VMID wait fences, gang submit, isolation fences, timeout soft recovery, per-queue reset, full GPU recovery, SRIOV no-coredump behavior, and job cleanup under error allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_job.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_job.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_job.h

Purpose: declares the AMDGPU scheduler job structure, internal kernel job identifiers, preamble/preemption flags, and job lifecycle API.

Important APIs/types: `struct amdgpu_job` embeds `struct drm_sched_job` and carries VM, explicit sync, HW fences, gang fence, VMID/PASID, GDS/GWS/OA allocation ranges, VM generation, user fence metadata, shadow/CSA/GDS virtual addresses, isolation flags, run counter, and a flexible array of IBs. `AMDGPU_KERNEL_JOB_ID_*` reserves descending `u64` IDs for internal jobs such as VM updates, TTM moves, TLB flush, KFD GART map, ring tests, and cleaner shader. `amdgpu_job_ring()` maps a job to its scheduler ring.

Control flow contract: callers allocate with `amdgpu_job_alloc()` or `_with_ib()`, fill IBs/resources, optionally set gang leader, submit through scheduler or direct ring path, and release with `amdgpu_job_free()` on unsubmitted/error paths. Scheduler callbacks in `amdgpu_job.c` own cleanup after normal scheduled submission.

State and persistence: job state is transient per submission. Fence state persists only as kernel synchronization objects until all references drop. The generation field records VM generation at allocation and is used to cancel jobs after VRAM loss.

Dependencies/integration: includes DRM GPU scheduler, AMDGPU sync, and ring definitions. Used broadly by command submission, ring tests, VM updates, media tests, and reset/recovery.

Risks: flexible array sizing requires accurate `num_ibs`. The inline ring accessor assumes `base.entity` and scheduler queue are initialized, so it is not valid for all direct-submit jobs. Internal job ID space must avoid collision with userspace client IDs.

Test signals: compile coverage for command submission and ring-test paths, leak tests for allocation failure, scheduler tests for fence signaling and job free callback, and VM generation tests after recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_job.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_jpeg.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_jpeg.c

Purpose: implements shared JPEG engine software lifecycle, idle power-gating coordination, ring and IB tests, RAS poison handling, PSP SRAM update, debugfs/sysfs controls, IP state dump, and JPEG command-stream validation.

Important APIs/functions: `amdgpu_jpeg_sw_init/fini()` initialize delayed idle work, power-gating lock, submission count, DPG SRAM BOs, rings, and register dump storage. `amdgpu_jpeg_ring_begin_use/end_use()` ungate/gate the JPEG IP around submissions through `amdgpu_device_ip_set_powergating_state()`. `amdgpu_jpeg_dec_ring_test_ring()` and `amdgpu_jpeg_dec_ring_test_ib()` verify register writes through ring packets or direct IB jobs. RAS paths are `amdgpu_jpeg_process_poison_irq()`, `amdgpu_jpeg_ras_sw_init()`, and `amdgpu_jpeg_ras_late_init()`. `amdgpu_jpeg_dec_parse_cs()` validates PACKETJ command streams.

Control flow: init allocates per-instance DPG SRAM BOs only when PSP firmware loading and JPEG DPG are enabled, skipping harvested instances. Submission begin increments an atomic count, cancels idle work, ungates under mutex; end decrements and schedules idle work. The idle worker counts outstanding ring fences and submission count, gates the IP when idle, otherwise reschedules itself. Ring tests write known values to JPEG pitch registers and poll with `adev->usec_timeout`. IB tests allocate a direct job, write PACKETJ commands, wait on the fence, and then verify the register value outside SRIOV. CS parsing walks two dwords at a time, rejects reserved bits, invalid types, invalid conditions, and writes outside the allowed JPEG register range or inside atomic registers.

State and persistence: runtime state is under `adev->jpeg`: instance/ring arrays, harvest mask, delayed work, lock, atomic submission count, RAS interface, DPG SRAM BOs, debug caps/reset mask, and IP dump buffers. Debugfs can mutate `ring->sched.ready`; sysfs exposes supported reset masks. No disk persistence exists.

Dependencies/integration: depends on AMDGPU rings/jobs/fences, PSP firmware load, RAS dispatch, debugfs/sysfs, SOC15 register macros, power-gating via common IP code, and KMS hardware info that reports JPEG rings.

Risks: idle gating races are mitigated by atomic submission count plus mutex, but callers must pair begin/end. Debugfs scheduler mask can disable all but rejects a zero effective mask; it directly toggles scheduler readiness. CS parser assumes even-length packet layout by stepping two dwords; malformed lengths need upstream validation. DPG SRAM size and pointer advancement must match version-specific programming.

Test signals: JPEG ring/IB tests, command submission parser negative tests, suspend canceling idle work, debugfs sched mask get/set, sysfs reset mask, RAS poison IRQ dispatch, harvested-instance boot, SRIOV ring tests skipping MMIO verification, and coredump IP state printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_jpeg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_jpeg.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_jpeg.h

Purpose: declares shared JPEG engine data structures, DPG register access macros, capabilities, RAS state, lifecycle APIs, diagnostics, and CS parser entry point.

Important APIs/types: constants bound JPEG instances/rings and legal register ranges. DPG macros (`WREG32_SOC15_JPEG_DPG_MODE`, `RREG32_SOC15_JPEG_DPG_MODE`, SOC24 variants, and SRAM append macro) abstract direct versus indirect SRAM programming. `struct amdgpu_jpeg_inst` holds decoder rings, IRQ sources, DPG SRAM BO/address/pointer, pause state, and AID ID. `struct amdgpu_jpeg` stores instance count, internal/external register maps, harvest config, delayed idle work, power-gating lock, submission count, RAS state, DPG mode, reset/cap flags, and register dump metadata.

Control flow contract: version-specific JPEG implementations populate instances, rings, register maps, IRQ funcs, and call shared lifecycle helpers. Submit paths should call begin/end use around work to keep power gating correct. CS paths call `amdgpu_jpeg_dec_parse_cs()` before scheduling user packets.

State and persistence: all state is per-device runtime state. DPG SRAM BOs persist for driver lifetime and are freed in shared fini. Register dump memory persists only for diagnostics.

Dependencies/integration: includes RAS and CS parser headers, expects `amdgpu_device`, `amdgpu_ring`, `amdgpu_ip_block`, `drm_printer`, and firmware ID definitions from broader AMDGPU headers.

Risks: register access macros reference `adev` implicitly, so they must be used in scopes where that name exists. The SOC15 indirect macro can append to `dpg_sram_curr_addr` without explicit bound checks in the macro. JPEG register range constants are security-relevant for parser validation and must track hardware packet permissions.

Test signals: build coverage for SOC15/SOC24 users, parser fuzz/negative tests, DPG SRAM programming tests, multi-instance/multi-ring scheduling, and IP dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_jpeg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_kms.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_kms.c

Purpose: implements core KMS driver load/unload, per-open file private setup/teardown, userspace `AMDGPU_INFO` query ioctl, vblank helpers, GPU instance accounting, and firmware debugfs output.

Important APIs/functions: `amdgpu_driver_load_kms()` calls `amdgpu_device_init()`, runtime PM mode detection, ACPI init, and SmartShift load notification. `amdgpu_driver_unload_kms()` unregisters the GPU instance, tears down ACPI, and finalizes hardware. `amdgpu_info_ioctl()` is the large userspace query dispatcher for hardware IP info/counts, firmware versions, memory usage, MMR reads, device info, VBIOS, sensors, RAS, video caps, GPUVM fault, max IBs, and user-queue metadata. `amdgpu_driver_open_kms()` allocates file-private VM/PASID/context/userq state. `amdgpu_driver_postclose_kms()` tears those down. Vblank helpers use display scanout and IRQ refcounts.

Control flow: the ioctl first validates nonzero return size and pointer, then switches on query type and uses bounded `copy_to_user()` with `min(size, sizeof(result))`. Hardware IP info derives available rings from live `sched.ready` and `no_user_submission`, handles JPEG as its own block when present, and computes user queue slots from MES masks. HW IP counts honor XCP partition masks when active. Device info aggregates PCI IDs, clocks, VM address limits, CU/cache topology, flags, PCIe capability masks, shadow/CSA sizes, and user queue IP mask. Open flushes delayed IB tests, rejects RAS-disabled devices, takes runtime PM, allocates fpriv, PASID, XCP assignment, VM/root PD, PRT VA, optional CSA, seq64 mapping, BO-list IDR, userq manager, EVF manager, and context manager. Error paths free PASID/VM/fpriv and drop runtime PM.

State and persistence: global multi-GPU counts live in `mgpu_info` under a mutex. Per-open state lives in `struct amdgpu_fpriv`: VM, PASID, XCP ID, BO list handles, userq/EVF/context managers, CSA and seq64 mappings. Query results reflect current device state and counters; no durable persistence exists.

Dependencies/integration: integrates DRM core, PM runtime, ACPI/SmartShift, AMDGPU device init/fini, RAS, reset domain, DPM sensors, TTM memory managers, VBIOS Atom context, KFD/PASID, XCP partitioning, user queues, display/vblank, UVD/VCE handles, debugfs, and firmware metadata.

Risks: this file is userspace ABI-sensitive; every query must validate sizes, indexes, and offsets before exposing data or reading registers. MMR reads lock the reset domain and disable gfx off, but invalid register allowlists return `-EFAULT`. Open error paths are complex and must avoid leaks of PASID, VM BOs, CSA, seq64, and runtime PM refs. Firmware debugfs assumes an Atom context when printing VBIOS part number.

Test signals: libdrm/mesa `AMDGPU_INFO` query tests, `modetest`/vblank tests, open/close leak tests, runtime PM balance checks, partitioned XCP query tests, sensor and VBIOS queries, firmware debugfs reads, RAS-disabled open rejection, and MMR register allowlist negative tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_lsdma.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_lsdma.c

Purpose: provides common wrapper helpers for LSDMA register polling, memory copy, and memory fill operations while chunking large transfers into hardware-supported maximum sizes.

Important APIs/functions: `amdgpu_lsdma_wait_for()` polls an MMIO register until `(value & mask) == reg_val` or `adev->usec_timeout` expires. `amdgpu_lsdma_copy_mem()` splits a copy into chunks of at most `AMDGPU_LSDMA_MAX_SIZE` and delegates to `adev->lsdma.funcs->copy_mem()`. `amdgpu_lsdma_fill_mem()` similarly chunks fills and calls `fill_mem()`.

Control flow: copy/fill reject zero-length requests with `-EINVAL`, then loop while bytes remain, choose `min(mem_size, 0x2000000)`, call the ASIC-specific function, propagate any error immediately, and advance addresses/remaining size. The wait helper uses microsecond polling with `udelay(1)`.

State and persistence: no state is owned here. Functions operate on device registers and pass-through transfer parameters to version-specific callbacks.

Dependencies/integration: depends on `adev->lsdma.funcs`, MMIO `RREG32`, `adev->usec_timeout`, and hardware-specific LSDMA implementations that program transfer engines.

Risks: wrappers do not null-check `adev->lsdma.funcs` or callback pointers, so callers/ASIC init must ensure LSDMA support before calling. Polling is busy-waiting and can consume CPU for long timeouts. Chunking advances byte addresses, so callback semantics must use byte sizes/addresses consistently.

Test signals: large copy/fill tests crossing 32 MiB boundaries, zero-size negative tests, callback error propagation, register wait timeout tests, and memory compare verification after LSDMA transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_lsdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_lsdma.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_lsdma.h

Purpose: declares the LSDMA function table and shared wrapper APIs for memory copy/fill and register polling.

Important APIs/types: `struct amdgpu_lsdma_funcs` contains ASIC callbacks for `copy_mem`, `fill_mem`, and `update_memory_power_gating`. `struct amdgpu_lsdma` stores the selected callback table. Exports are `amdgpu_lsdma_copy_mem()`, `amdgpu_lsdma_fill_mem()`, and `amdgpu_lsdma_wait_for()`.

Control flow contract: ASIC-specific code installs callback pointers in `adev->lsdma.funcs`; generic callers use the wrappers so transfer sizes are chunked and polling is standardized.

State and persistence: only a runtime callback pointer is defined here; no durable state.

Dependencies/integration: relies on `struct amdgpu_device` from broader AMDGPU headers. Used by code paths that need lightweight DMA transfers or memory power-gating changes.

Risks: the header does not encode capability checks; callers need to avoid invoking wrappers on devices without LSDMA callbacks.

Test signals: compile coverage for ASIC callback providers and runtime copy/fill tests on LSDMA-capable hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_lsdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mca.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mca.c

Purpose: implements Machine Check Architecture/RAS helpers for querying, caching, dumping, and accounting MCA error banks through SMU callbacks. It registers MCA RAS blocks, parses CE/UE/DE counts, prevents duplicate UE counting during recovery, and exposes debugfs dump/debug mode controls.

Important APIs/functions: simple UMC status helpers query/reset CE/UE counts from PCIe MCA status registers. `amdgpu_mca_mp0/mp1/mpio_ras_sw_init()` register RAS block objects. `amdgpu_mca_init/fini/reset()` initialize and free MCA bank caches. `amdgpu_mca_smu_init_funcs()` installs SMU callback table; `amdgpu_mca_smu_set_debug_mode()` delegates debug mode. `amdgpu_mca_smu_log_ras_error()` collects MCA banks, dispatches parsed counts into `ras_err_data`, caches unconsumed banks, and re-dispatches cached data. Debugfs adds `mca_debug_mode`, `mca_ue_dump`, and `mca_ce_dump`.

Control flow: SMU-backed collection asks for valid count by error type, reads each MCA entry within max count bounds, adds it to a temporary bank set, and logs selected register dumps. UE updates are suppressed after the first recovery-stage update using `ue_update_flag`; CE entries are dumped only when deferred-error logic says so. Dispatch parses a count per bank for the requested RAS block; nonzero counts are accumulated per socket/die as UE, CE, or deferred. Entries that could not be attributed remain cached for later attempts.

State and persistence: `adev->mca` holds RAS block interfaces, SMU funcs, per-error-type caches (`mca_caches`), mutexes, and the UE update atomic. MCA bank sets are in-memory linked lists. Debugfs reads can also populate caches. No persistent storage exists.

Dependencies/integration: depends on AMDGPU RAS framework, SMUIO MCM config, UMC status field macros, SMU MCA callbacks, debugfs, and RAS event logging. It feeds global RAS error accounting and recovery flows.

Risks: cache merging ignores allocation failures from `amdgpu_mca_bank_set_add_entry()` in some loops, so memory pressure may silently drop MCA entries. MCA bank list operations require correct lock usage around caches. UE duplicate suppression relies on `amdgpu_ras_intr_triggered()` state. Debugfs dump paths both inspect and cache MCA banks, so diagnostic reads can affect later accounting.

Test signals: RAS injection/fault tests for CE/UE/DE, recovery-stage duplicate UE suppression, SMU callback `-EOPNOTSUPP` behavior, debugfs dump and debug-mode controls, cache carryover across unmatched banks, and per-socket/die error statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mca.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mca.h

Purpose: declares MCA register field helpers, MCA IP/error enums, bank data structures, RAS wrapper structures, SMU callback interface, and exported MCA/RAS functions.

Important APIs/types: `MCA_REG_FIELD()` and `MCA_REG__*` macros decode status, misc, and syndrome fields. `enum amdgpu_mca_ip` identifies PSP, SDMA, GC, SMU, MP5, UMC, and XGMI PCS sources. `enum amdgpu_mca_error_type` separates UE, CE, and deferred errors. `struct mca_bank_entry` stores bank index, type, IP, topology info, and up to 16 registers. `struct amdgpu_mca_smu_funcs` defines SMU hooks for debug mode, valid counts, bank reads, and count parsing.

Control flow contract: ASIC/SMU code installs `amdgpu_mca_smu_funcs`; RAS query paths call `amdgpu_mca_smu_log_ras_error()` or lower-level query helpers. RAS block init functions attach MP0/MP1/MPIO blocks to the RAS framework.

State and persistence: `struct amdgpu_mca` holds block interfaces, SMU funcs, caches for UE/CE classes, and `ue_update_flag`. The cache is volatile runtime state used to bridge asynchronous parsing/accounting.

Dependencies/integration: includes `amdgpu_ras.h`; expects `ras_err_data`, `ras_query_context`, `dentry`, and device definitions from broader AMDGPU/RAS code.

Risks: field macros depend on stable MCA register layouts. `AMDGPU_MCA_ERROR_TYPE_DE` is used as an array bound for caches, so enum ordering matters. SMU callback max counts must match firmware-provided bank arrays.

Test signals: compile coverage for SMU providers, field decode unit checks, RAS block registration, and MCA error accounting tests across CE/UE/deferred types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mes.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mes.c

Purpose: implements the common Micro Engine Scheduler layer for AMDGPU. It initializes MES resources, doorbells, firmware metadata, scheduler context writeback slots, event logs, hung queue buffers, legacy queue map/unmap/reset operations, register operations via firmware, shader debugger commands, isolation policy updates, and debugfs event log output.

Important APIs/functions: `amdgpu_mes_init/fini()` allocate/free writeback slots, doorbell bitmap, event log BO, and hung-queue DB arrays while deriving VMID and HQD masks. Queue helpers `amdgpu_mes_map_legacy_queue()`, `amdgpu_mes_unmap_legacy_queue()`, and `amdgpu_mes_reset_legacy_queue()` translate ring state into firmware input structures under `amdgpu_mes_lock()`. `amdgpu_mes_detect_and_reset_hung_queues()` asks firmware to identify/reset hung queues and copies doorbell offsets. `amdgpu_mes_rreg/wreg/reg_write_reg_wait()` perform register operations through `misc_op`. `amdgpu_mes_init_microcode()` selects and requests MES firmware, extracts start addresses/version, and registers PSP firmware IDs. `amdgpu_mes_update_enforce_isolation()` pushes cleaner-shader isolation policy to MES.

Control flow: init sets masks based on GFX/compute/SDMA topology, reserves kernel HQDs, allocates per-pipe writeback slots, initializes doorbell allocation with aggregated priority doorbells, optionally allocates event logging, and optionally allocates hung queue arrays. Suspend/resume use firmware all-gang commands only when version support says yes. Register and debugger operations populate `mes_misc_op_input` and serialize with the MES lock. Firmware naming prefers unified MES, otherwise uses generation-specific `_mes`, `_mes1`, `_mes_2` variants with fallback for GFX11 scheduler pipe.

State and persistence: `adev->mes` holds firmware pointers, versions, BOs and GPU addresses, rings, locks, doorbell bitmap/IDA, VMID/HQD masks, writeback addresses, event log memory, hung queue buffers, and cooperative dispatch fields. State is volatile and reinitialized on driver load/reset; firmware pointers persist for driver lifetime.

Dependencies/integration: depends on firmware loading, PSP firmware table, writeback allocator, BO allocator, GFX topology, SDMA topology, NBIO HDP flush offsets, GFX HDP flush mask, MES function table, KMS/user queue slot reporting, KFD queue management, shader debugger, reset handling, and debugfs.

Risks: `amdgpu_mes_rreg()` frees the writeback slot only when `addr_offset` is nonzero, which relies on allocator not returning a valid offset 0 or accepting leak semantics. Many operations require `adev->mes.funcs->misc_op`; unsupported firmware returns `-EINVAL`. The lock intentionally enters no-reclaim context to avoid MMU notifier deadlocks, so callbacks must not take unrelated locks that reintroduce cycles. Hung queue copy loops assume firmware writes within `hung_queue_hqd_info_offset`.

Test signals: firmware load tests across unified and legacy naming, MES queue map/unmap/reset, all-gang suspend/resume version gates, hung queue detection/reset, HDP flush through MES, shader debugger set/flush, debugfs event log, isolation policy toggles, and user queue slot reporting through KMS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mes.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mes.h

Purpose: declares the MES core data model, firmware command input structures, function table, priority/pipe constants, doorbell/version macros, lock helpers, and exported MES operations.

Important APIs/types: `struct amdgpu_mes` stores scheduler/firmware versions, rings, firmware BOs, MQD backups, IRQs, VMID/HQD masks, writeback slots, doorbells, event log, resource BOs, hung queue buffers, cooperative dispatch buffers, and callback table. `struct amdgpu_mes_gang`, `struct amdgpu_mes_queue`, and property structs model process/gang/queue scheduling entities. `mes_*_input` structs are firmware command payloads for queue add/remove/map/unmap/suspend/resume/reset, TLB invalidation, and misc operations. `struct amdgpu_mes_funcs` is the firmware/backend command vtable.

Control flow contract: version-specific MES implementations set `adev->mes.funcs`, KIQ callbacks, ring data, firmware versions, and resource sizes. Generic callers use exported wrappers that serialize with `amdgpu_mes_lock()` where needed. `amdgpu_mes_lock()` wraps `mutex_lock()` with `memalloc_noreclaim_save()` because MES locks can be taken from MMU notifier/reclaim contexts.

State and persistence: the header defines extensive runtime state but no durable persistence. Fence queue IDs use `AMDGPU_FENCE_MES_QUEUE_FLAG` and mask constants to distinguish MES queues in fence IDs.

Dependencies/integration: includes AMDGPU IRQ, KFD interface, GFX, doorbell, and Linux scheduler/MM headers. It connects DRM scheduler, KFD, user queues, firmware, and memory-notifier paths.

Risks: command structs mirror firmware ABI and must remain layout-compatible with MES firmware. Lock helper comments explicitly warn against taking reservation locks or triggering reclaim under MES lock. Pipe/instance macros assume `AMDGPU_MAX_MES_PIPES` times GC instance layout. Duplicated fence flag definitions in `amdgpu_mes_ctx.h` must stay consistent.

Test signals: ABI tests against firmware command versions, queue lifecycle stress, MMU notifier eviction under memory pressure, user queue creation/destruction, MES reset paths, and no-reclaim lockdep validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mes_ctx.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mes_ctx.h

Purpose: defines MES context metadata layout used for GFX, compute, and SDMA queues, including ring memory, save/restore metadata, writeback slots, IB-test buffers, and per-file MES context data.

Important APIs/types: offset enums define writeback slot roles (`RPTR`, `WPTR`, `FENCE`, `COND_EXE`, `TRAIL_FENCE`) and memory offsets for ring/IB/padding. Constants bound MES context ring counts for one GFX, four compute, and two SDMA rings. `struct amdgpu_mes_ctx_meta_data` is page-aligned and contains per-ring ring buffers, GFX v10 metadata, GDS backup, MEC HPD, SDMA CSA, writeback slots, and aligned IB test buffers. `struct amdgpu_mes_ctx_data` stores the metadata BO, GPU/MC addresses, VA mapping, CPU pointer, and gang IDs by hardware IP.

Control flow contract: MES/user queue setup allocates and maps a metadata BO matching this layout, then firmware and ring tests use the fixed offsets. The fence queue flag/mask constants identify MES queue IDs in fence values.

State and persistence: metadata lives in GPU BOs mapped for the process/context lifetime. It is runtime state, not durable. Gang IDs track per-IP scheduling gang association.

Dependencies/integration: includes `v10_structs.h` for GFX metadata. Used by MES context and user-mode queue setup, ring tests, and firmware state save/restore.

Risks: this is a firmware-visible memory layout; alignment and size changes are ABI-sensitive. The header defines `AMDGPU_FENCE_MES_QUEUE_FLAG` and mask twice, which is harmless to the compiler only because values match but is a maintenance risk. Array sizing by `AMDGPU_HW_IP_DMA+1` assumes enum ordering.

Test signals: user queue/MES context allocation tests, firmware queue bring-up, IB ring tests using metadata IB buffers, and structure size/alignment assertions where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mes_ctx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mmhub.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mmhub.c

Purpose: provides shared MMHUB RAS software initialization.

Important APIs/functions: `amdgpu_mmhub_ras_sw_init()` registers `adev->mmhub.ras->ras_block` with the RAS framework, names it `"mmhub"`, marks the block as `AMDGPU_RAS_BLOCK__MMHUB`, sets type `AMDGPU_RAS_ERROR__MULTI_UNCORRECTABLE`, and stores `adev->mmhub.ras_if`.

Control flow: the function is a no-op if no MMHUB RAS object is installed. On registration failure it logs and returns the error. Late init is intentionally left to the default RAS block late-init behavior.

State and persistence: updates `adev->mmhub.ras_if` and the embedded RAS common descriptor in-memory. No persistence exists.

Dependencies/integration: depends on AMDGPU RAS registration and `struct amdgpu_mmhub` state configured by ASIC-specific MMHUB code.

Risks: assumes `adev->mmhub.ras` points to valid storage and that `ras_block.ras_comm.name` has enough space for `"mmhub"`. Missing RAS object silently disables MMHUB RAS registration.

Test signals: RAS-enabled boot should show MMHUB registered; RAS query/injection paths should find MMHUB as multi-uncorrectable, and late-init should follow default RAS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mmhub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mmhub.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mmhub.h

Purpose: declares MMHUB RAS memory IDs, function table, client name mapping, device state, and RAS software initialization.

Important APIs/types: `enum amdgpu_mmhub_ras_memory_id` names MMHUB memory blocks used for RAS reporting. `struct amdgpu_mmhub_funcs` provides callbacks for framebuffer location, MC FB offset, init, GART enable/disable, fault defaults, clock/power gating, VM page table registers, and XGMI info. `struct amdgpu_mmhub_client_ids` and inline helpers map client IDs to read/write names. `struct amdgpu_mmhub` stores RAS interface, function table, RAS object, and client ID names.

Control flow contract: ASIC-specific MMHUB code installs function table and optional client ID map. Generic memory-management code calls the callbacks for GART and VM setup; RAS setup calls `amdgpu_mmhub_ras_sw_init()`.

State and persistence: runtime state only: callback pointers, RAS pointer/interface, and client name table.

Dependencies/integration: used by GMC/VM setup, page fault reporting, RAS, XGMI, and power management.

Risks: client name lookup returns `NULL` for out-of-range IDs, so fault-reporting callers must handle missing names. GART and VM callbacks are required for functional memory management on supported ASICs but are optional at the type level.

Test signals: GART enable/disable, VM PT register setup, MMHUB page fault decoding with client names, clock/power-gating tests, and RAS registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mmhub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mode.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mode.h

Purpose: defines AMDGPU display/KMS private types and constants for CRTCs, connectors, encoders, framebuffers, I2C/DDC, HPD, audio, color properties, pageflip/vblank state, and display function callbacks.

Important APIs/types: container macros convert DRM objects to AMDGPU private structs. Enums define scaling, underscan, HPD pins, CRTC/vline IRQ IDs, pageflip IRQ IDs, and flip status. `struct amdgpu_i2c_bus_rec` captures Atom GPIO/I2C bus register metadata; `struct amdgpu_pll` stores clock limits/flags; `struct amdgpu_display_funcs` is the display backend vtable. `struct amdgpu_mode_info` is the central display state holder with Atom context, CRTC/plane/audio arrays, properties, color-management properties, backlight, firmware flags, and display function table. `struct amdgpu_crtc`, `amdgpu_encoder`, `amdgpu_connector`, and `amdgpu_mst_connector` extend DRM objects with AMD-specific state.

Control flow contract: display initialization populates `amdgpu_mode_info`, creates properties, links encoders/connectors, installs display funcs, and uses the declared helpers for DDC probing, scanout position, page flip, CRTC config, connector lookup, and mode fixups. KMS vblank code in `amdgpu_kms.c` relies on CRTC arrays and scanout flags from this header.

State and persistence: all structures are runtime DRM/KMS state. Some fields cache BIOS-derived data, EDID, backlight level, audio pin status, color properties, pageflip work, and writeback state. No durable persistence is defined here.

Dependencies/integration: includes DRM CRTC/encoder/framebuffer/probe helpers, DisplayPort/MST helpers, Linux I2C/hrtimer, AMD freesync modules, DM IRQ params, and idle state manager. It bridges legacy Atom display and DC/DM display paths.

Risks: many fields are shared between IRQ handlers, modeset paths, and atomic/display code, so locking and lifetime rules are external and critical. Fixed maximum arrays for CRTCs/planes/HPD/AFMT must match hardware limits. Color-management property semantics must stay ABI-compatible with DRM userspace.

Test signals: modeset and pageflip tests, HPD connect/disconnect, MST topology, DDC/AUX probing, vblank counter accuracy, backlight/audio properties, writeback, color-management property tests, and compile coverage for DC/non-DC configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_nbio.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_nbio.c

Purpose: implements shared NBIO/PCIe-BIF RAS registration, PCIe replay counter access, replay-counter support checks, and NBIO RAS late init interrupt enabling.

Important APIs/functions: `amdgpu_nbio_ras_sw_init()` registers the NBIO RAS block, names it `"pcie_bif"`, sets block `AMDGPU_RAS_BLOCK__PCIE_BIF`, type `AMDGPU_RAS_ERROR__MULTI_UNCORRECTABLE`, and stores `adev->nbio.ras_if`. `amdgpu_nbio_get_pcie_replay_count()` delegates to `adev->nbio.funcs->get_pcie_replay_count()` when available. `amdgpu_nbio_is_replay_cnt_supported()` rejects SRIOV VF and missing ASIC/NBIO callbacks. `amdgpu_nbio_ras_late_init()` calls generic RAS late init, then enables NBIO RAS controller and ATHUB error event IRQs when supported.

Control flow: software init is a no-op without an installed RAS object. Late init first initializes RAS block state; if RAS is supported for the block, it calls `amdgpu_irq_get()` for two NBIO IRQ sources. Any failure jumps to RAS late fini and returns the error.

State and persistence: updates `adev->nbio.ras_if` and uses IRQ enable counters in `adev->nbio.ras_controller_irq` and `ras_err_event_athub_irq`. Replay counts are read live from hardware via callbacks. No persistence exists.

Dependencies/integration: depends on RAS framework, AMDGPU IRQ subsystem, NBIO function table, ASIC function table, and SRIOV mode checks.

Risks: if the first IRQ get succeeds and the second fails, this function calls RAS late fini but does not explicitly put the first IRQ; correctness depends on late fini or caller cleanup. Replay support requires both ASIC and NBIO callbacks even though the getter itself only calls NBIO funcs. RAS object absence silently disables registration.

Test signals: RAS-enabled boot, NBIO/PCIe error injection, IRQ enable failure cleanup, PCIe replay count queries on PF versus VF, and RAS late init/fini balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_nbio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_nbio.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_nbio.h

Purpose: declares NBIO hardware callback interfaces, HDP flush register masks, NBIO RAS state, and helper APIs for RAS and PCIe replay counters.

Important APIs/types: `struct nbio_hdp_flush_reg` stores per-engine HDP flush reference/mask values. `struct amdgpu_nbio_ras` wraps a RAS block plus optional no-BIF-ring interrupt handlers and init hooks. `struct amdgpu_nbio_funcs` is the large NBIO vtable for HDP offsets, PCIe index/data offsets, revision/memsize, doorbell ranges for SDMA/VPE/VCN/GC/IH, doorbell aperture/interrupt control, clock gating/light sleep, IH control, register init/remap, ASPM/link workarounds, ROM offset, compute/memory partition mode, NPS switch request, replay count, and register remap. `struct amdgpu_nbio` stores HDP regs, RAS IRQ sources, RAS interface, funcs, and RAS object.

Control flow contract: ASIC-specific NBIO code installs function table and RAS object. Common MES HDP flush and other subsystems call offset functions; doorbell users call range callbacks; RAS code uses `amdgpu_nbio_ras_sw_init()` and `amdgpu_nbio_ras_late_init()`.

State and persistence: runtime callback pointers, RAS IRQ sources, and RAS interface live in `adev->nbio`. Hardware counters and partition modes are queried live.

Dependencies/integration: NBIO connects PCIe, doorbells, IH, HDP flush, partitioning, ASPM, RAS, and MES/KMS/user queue subsystems.

Risks: the vtable is broad and many callbacks are mandatory for a given ASIC even though the type allows nulls. Doorbell range programming must stay consistent with MES/user queue doorbell allocation. Replay count support checks must match actual firmware/hardware capability.

Test signals: doorbell aperture/range programming, IH doorbells, ASPM/link workarounds, HDP flush via MES, partition mode queries, RAS IRQ setup, and PCIe replay count reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_nbio.h -->
