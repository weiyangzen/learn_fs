# subset-b-000945 Research

Grouped research report for the requested DRM accelerator source subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_pci.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_pci.c

Purpose: implements the AIE2-family AMD XDNA PCI hardware operations exposed through `struct amdxdna_dev_ops`. It owns firmware loading/startup, PSP/SMU/mailbox bring-up, runtime configuration, PM handoff, hardware suspend/resume, and user-visible query/state ioctls for AIE metadata, telemetry, power, preemption, resources, and context status.

Important APIs, types, and functions: `aie2_ops` wires this file into the generic driver. `aie2_init()` maps PCI BARs, loads `npu.sbin` or `npu_7.sbin`, allocates MSI-X vectors, creates PSP state, starts hardware, initializes the XRS solver, and starts runtime PM. `aie2_hw_start()` creates the mailbox, starts SMU and PSP, reads management-channel SRAM descriptors, starts the management channel, initializes firmware/runtime PM, queries firmware/AIE metadata, and allocates async error handling. `aie2_get_info()`, `aie2_get_array()`, and `aie2_set_state()` dispatch DRM query/set requests under runtime PM. XRS callbacks `aie2_xrs_load()` and `aie2_xrs_unload()` create and destroy firmware contexts for allocated columns.

Control flow: probe calls `aie2_init()` under `dev_lock`; open clients later use ops callbacks for context creation and command submission. Resume restarts hardware then resumes every client hardware context; suspend walks clients to suspend contexts before stopping firmware and hardware. Most user queries enter `drm_dev_enter()`, resume runtime PM, copy data to/from user buffers, and suspend runtime PM.

State and persistence: persistent runtime state is in `struct amdxdna_dev_hdl`: mapped BAR bases, management mailbox resources, firmware protocol/version/features, AIE metadata, power levels, current TOPS, preemption flags, context count, and last async error. Nothing is stored on disk; firmware choice is from kernel firmware files.

Dependencies and integration points: depends on PCI, firmware loader, PSP and SMU helpers, `aie2_message.c` firmware mailbox commands, `amdxdna_mailbox`, `amdxdna_pm`, `aie2_solver`, and UAPI structs from `drm/amdxdna_accel.h`.

Risks: startup and unwind ordering is critical; failure paths must stop PSP/SMU/mailbox in reverse order. User-buffer size checks gate telemetry/status copies. Protocol feature-mask checks drive preemption and command-mode behavior. Hypervisor rejection, firmware absence, or bad SRAM management-channel descriptors block probe.

Test signals: bind supported PCI IDs, firmware load success/failure, suspend/resume with active contexts, runtime PM autosuspend, every `GET_INFO`/`GET_ARRAY`/`SET_STATE` parameter, bad user buffers, unsupported firmware protocol, and XRS allocation/release under concurrent contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_pci.h -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_pci.h

Purpose: declares the shared AIE2 hardware interface, firmware-facing metadata, register-index enums, runtime configuration categories, firmware feature bits, per-device private configuration, and prototypes for the AIE2 PSP/SMU/PM/message/context helpers.

Important APIs and types: `struct amdxdna_dev_hdl` is the live device-handle backing AIE2 ops, containing BAR bases, PSP handle, management mailbox resources, protocol version, AIE metadata, feature mask, execution-message ops, power/DPM state, mailbox pointers, async events, device status, and context count. `struct amdxdna_dev_priv` describes per-NPU constants: firmware path, runtime config table, DPM clocks, firmware feature table, column alignment, BAR-relative SRAM/PSP/SMU offsets, mailbox geometry, context limit, and `aie2_hw_ops`. `struct amdxdna_hwctx_priv` is the AIE2-private scheduler/mailbox state for a hardware context. Enums define SMU, SRAM, PSP register slots, runtime config categories, and firmware feature bits.

Control flow: implementation files include this header to translate generic AMD XDNA driver calls into AIE2-specific register, mailbox, PSP, SMU, and firmware-message operations. Macros such as `SMU_REG()`, `SRAM_GET_ADDR()`, `AIE2_SRAM_OFF()`, and `MBOX_SIZE()` normalize per-device BAR layouts.

State and persistence: this header defines state shape only. Runtime state lives in allocated `amdxdna_dev_hdl` and `amdxdna_hwctx_priv` instances; tables in register files persist as const data.

Dependencies and integration points: includes the private AIE2 message ABI, mailbox API, AMD PMF metric hooks, DRM UAPI, PCI conversion, and exported `aie2_ops`. It bridges register-table files, `aie2_pci.c`, `aie2_pm.c`, `aie2_psp.c`, `aie2_smu.c`, context code, and message code.

Risks: register-offset macros assume device-private tables are correct. Firmware feature gating uses bit operations on an `unsigned long` feature mask, so feature-table definitions must stay synchronized with firmware protocol. `HWCTX_MAX_CMDS` must remain a power of two for sequence indexing.

Test signals: compile all NPU register variants, probe every supported revision, validate PMF-disabled builds, and run firmware protocols with and without optional NPU command, preemption, temporal-only, and app-health features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_pm.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_pm.c

Purpose: implements AIE2-specific power-mode policy on top of generic AMD XDNA runtime PM. It sets DPM levels through device-private SMU operations, toggles firmware runtime clock-gating configuration, initializes default power state, and handles user-requested power modes.

Important APIs/functions: `aie2_pm_init()` discovers the highest DPM level from the device clock table, sets the initial DPM, enables clock gating, and records default mode. On resume it restores previous `dpm_level` and `clk_gating`. `aie2_pm_set_dpm()` resumes the device with `amdxdna_pm_resume_get_locked()`, calls `ndev->priv->hw_ops.set_dpm()`, updates `ndev->dpm_level`, and drops runtime PM. `aie2_pm_set_mode()` validates and applies `POWER_MODE_TURBO`, `POWER_MODE_HIGH`, or `POWER_MODE_DEFAULT`, including a no-active-context guard for turbo mode.

Control flow: user `DRM_AMDXDNA_SET_POWER_MODE` reaches this file through `aie2_set_state()`. XRS can also adjust the default DPM level when resource requirements change. DPM changes call SMU helper implementations selected by device-generation register files.

State and persistence: updates `pw_mode`, `dpm_level`, `dft_dpm_level`, `max_dpm_level`, and `clk_gating` in `amdxdna_dev_hdl`. State persists only while the driver/device handle is alive and is restored on resume.

Dependencies: relies on `aie2_runtime_cfg()` for firmware clock-gating controls, `amdxdna_pm` runtime PM helpers, and `aie2_smu.c` through `hw_ops.set_dpm`.

Risks: `aie2_pm_set_mode()` assumes caller holds `dev_lock`; failing to hold it risks racing context creation and turbo-mode checks. Runtime PM lock dropping in `amdxdna_pm_resume_get_locked()` must not be used from contexts that cannot release `dev_lock`.

Test signals: power-mode ioctl coverage, turbo rejection with active contexts, resume restore of DPM/clock gating, SMU command failure injection, and concurrent context creation while changing modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_psp.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_psp.c

Purpose: handles AMD Platform Security Processor interaction for validating, starting, wait-mode polling, and stopping NPU firmware. It prepares an aligned firmware buffer and drives PSP command registers.

Important APIs/functions: `aie2m_psp_create()` allocates a managed `psp_device`, copies PSP register mappings from `psp_config`, allocates an aligned firmware buffer, computes a physical address acceptable to PSP, and copies firmware bytes. `aie2_psp_start()` sends `PSP_VALIDATE` with firmware address/size, then `PSP_START` with copy-fw mode. `aie2_psp_stop()` sends `PSP_RELEASE_TMR`. `aie2_psp_waitmode_poll()` waits for firmware wait mode via the PWAITMODE register. Internal `psp_exec()` writes command/argument registers, toggles interrupt, polls ready, and checks response.

Control flow: `aie2_init()` creates the PSP handle after BAR mapping and firmware loading; `aie2_hw_start()` starts PSP before mailbox firmware handshake; `aie2_hw_stop()` stops PSP after firmware suspend/mailbox teardown.

State and persistence: `struct psp_device` keeps DRM device, aligned firmware backing memory, physical firmware address, firmware size, and PSP register pointers. Firmware state persists in hardware until stop/reset, not on disk.

Dependencies: depends on BAR offset tables from register files, PSP indices from `aie2_pci.h`, Linux polling helpers, DRM managed allocation, and the firmware loader path in `aie2_pci.c`.

Risks: PSP requires physical address alignment; using `virt_to_phys()` on the managed allocation assumes suitable memory. Command timeouts or nonzero firmware responses become probe/start failures. Register tables must map PSP command, argument, status, interrupt, response, and wait-mode slots accurately per device.

Test signals: valid and corrupt firmware images, timeout/error response simulation, alignment checks, start/stop cycles across runtime/system suspend, and per-generation PSP register table validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_psp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_smu.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_smu.c

Purpose: implements AIE2 SMU power sequencing and DPM clock programming for NPU1 and NPU4-derived devices.

Important APIs/functions: internal `aie2_smu_exec()` writes SMU argument and command registers, toggles interrupt, polls response, optionally reads output, and returns errors on timeout or non-OK response. `aie2_smu_init()` powers the device off then on. `aie2_smu_fini()` sets DPM level 0 and powers off. `npu1_set_dpm()` programs MP-NPU and H clocks separately and computes TOPS using returned frequency. `npu4_set_dpm()` sets hard and soft DPM levels and computes max/current TOPS from total columns and H clock.

Control flow: `aie2_hw_start()` initializes SMU before PSP firmware startup. `aie2_pm` calls generation-specific `set_dpm()` callbacks during init, power-mode changes, XRS default-DPM changes, and shutdown.

State and persistence: updates `npuclk_freq`, `hclk_freq`, `max_tops`, and `curr_tops` in `amdxdna_dev_hdl`; SMU hardware holds the actual power/clock state until changed or reset.

Dependencies: relies on per-generation SMU register offsets, DPM tables, `total_col` from firmware metadata, and `readx_poll_timeout()`.

Risks: DPM index bounds are assumed to have been validated by PM initialization. A failed power-off in init is treated as unrecoverable. TOPS formulas differ by generation and need hardware documentation alignment.

Test signals: SMU timeout/error paths, all DPM levels for NPU1 and NPU4 tables, power-cycle sequences during probe/remove and runtime PM, and resource-query values for current/max TOPS after DPM changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_smu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_solver.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_solver.c

Purpose: provides a small column/resource solver used by AMD XDNA to allocate AIE partitions to hardware contexts and select a default DPM level that satisfies QoS requirements.

Important APIs/functions: `xrsm_init()` creates a solver state with one resource group and action callbacks. `xrs_allocate_resource()` sanity-checks a request, rejects duplicate request IDs, creates a solver node, finds or shares a partition, calls the load callback, sets a DPM level, and stores callback state. `xrs_release_resource()` finds a node by request ID, unloads the associated context, and frees or decrements the partition. Helpers calculate GOPS from QoS, validate feasible throughput, choose DPM level from the configured clock list, scan bitmaps for free columns, and share compatible non-exclusive partitions.

Control flow: AIE2 hardware-context initialization calls allocation with CDO partition possibilities and QoS. Load/unload callbacks in `aie2_pci.c` create/destroy firmware contexts and assign columns. The solver itself is single-threaded by contract; callers must provide locking.

State and persistence: `solver_state` owns a bitmap of occupied columns, a list of allocated solver nodes, and a list of partition nodes with share counts. State lives for the DRM device lifetime through managed allocation.

Dependencies: uses Linux bitmaps/lists, DRM logging, `init_config` clock/action callbacks, and AIE QoS structs from `aie2_solver.h`.

Risks: no internal locking; misuse can corrupt lists or bitmap. Sharing logic currently marks all partitions non-exclusive, so isolation depends on higher-level request semantics. `sanity_check()` only checks max-clock feasibility, not all layout constraints.

Test signals: duplicate RID rejection, full-column exhaustion, partition sharing, release of shared partitions, invalid QoS/CDO inputs, DPM selection under multiple active nodes, and caller-side locking under parallel context creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_solver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_solver.h -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_solver.h

Purpose: defines the public contract for the AIE2 resource solver: partition descriptions, QoS capability/requirements, CDO relocation choices, allocation requests, load actions, power-level constants, clock lists, action callbacks, and solver init/allocate/release APIs.

Important APIs/types: `struct aie_part` names a start column and number of columns. `struct cdo_parts` carries legal start columns, column count, and QoS capacity for a relocatable CDO. `struct aie_qos` captures requested GOPS, FPS, DMA bandwidth, latency, execution time, and priority. `struct alloc_requests` binds a request ID to CDO and QoS. `struct xrs_action_ops` lets the solver ask the device layer to load/unload a partition and set default DPM level. `xrsm_init()`, `xrs_allocate_resource()`, and `xrs_release_resource()` are the exported solver lifecycle calls.

Control flow: device code initializes one solver per AIE array, then callers submit allocation requests when creating hardware contexts and release the request ID when tearing them down.

State and persistence: this header owns no state; it documents the in-memory state managed by `aie2_solver.c`. The comments explicitly state that the caller must provide locking.

Dependencies: depends on DRM device types and Linux fixed-width integer types through included translation units.

Risks: `XRS_MAX_COL` bounds bitmap-backed allocation; devices with more columns require changes. Caller-provided start-column arrays and QoS fields must be validated before or during allocation.

Test signals: ABI compile coverage for all solver clients, resource allocation with each power level, and negative tests for invalid CDO dimensions and missing callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_solver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ctx.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ctx.c

Purpose: implements generic AMD XDNA DRM hardware-context and command-submission ioctl plumbing, leaving device-specific hardware scheduling to `amdxdna_dev_ops`.

Important APIs/functions: context ioctls `amdxdna_drm_create_hwctx_ioctl()`, `amdxdna_drm_destroy_hwctx_ioctl()`, and `amdxdna_drm_config_hwctx_ioctl()` allocate, publish, configure, and destroy `struct amdxdna_hwctx` objects in a per-client xarray. `amdxdna_cmd_submit()` builds `amdxdna_sched_job`, pins/holds command and argument BOs, resumes runtime PM, protects the context lookup with SRCU, creates an output fence, and calls the device `cmd_submit` callback. Command helpers parse ERT headers, payloads, CU masks, and error state. `amdxdna_hwctx_walk()` provides SRCU-safe enumeration for query code.

Control flow: users create a context with QoS, create BOs, then submit an execbuf with one command BO and argument BO handles. Destroy removes the xarray entry first, synchronizes SRCU, and then calls device finalization so new submissions cannot race destroyed state.

State and persistence: per-client `hwctx_xa`, `next_hwctxid`, hardware-context fields, scheduler job references, BO references, fences, and atomic submit/free counters are in-memory only. `amdxdna_hwctx_remove_all()` cleans remaining contexts on file close/remove.

Dependencies: DRM GEM, DRM scheduler/fences, xarray, SRCU, tracepoints, runtime PM, AMD XDNA GEM and PCI driver ops.

Risks: error unwinds must drop PM, BO, fence, and job refs exactly once. `cmd_bo` may be absent for driver commands, so cleanup paths must tolerate NULL where expected. Config buffer handling caps CU config to one page; new config types need explicit validation.

Test signals: create/destroy/config ioctls, invalid handles, context ID wrap, concurrent submit/destroy, BO pin failures, PM resume failures, ERT payload bounds, and close/remove cleanup with live jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ctx.h -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ctx.h

Purpose: declares AMD XDNA command formats, context/job structures, ERT command opcodes/states, inline command-state helpers, and ioctl entry points for context and command submission.

Important APIs/types: `struct amdxdna_cmd` models the shared ERT-style command header and payload; bit masks encode state, extra CU masks, payload count, and opcode. Payload structs describe NPU start, command chains, and preempt data. `struct amdxdna_hwctx` stores client association, firmware context ID, allocated columns, QoS/CU config, syncobj handle, and counters. `struct amdxdna_sched_job` extends DRM scheduler job with context, mm, fences, command BO, argument BO array, driver command, sequence, and optional AIE health report. Inline helpers get/set opcode/state through mapped GEM memory.

Control flow: ioctl and AIE2 context code include this header to create contexts, inspect command BOs, push jobs, wait on sequences, and synchronize debug BOs.

State and persistence: structures define in-memory state tied to a DRM file, context, or submitted job. Command state is stored in user-visible GEM command buffers and can be observed by userspace.

Dependencies: depends on AMD XDNA GEM, DRM scheduler, dma-fence, syncobj, and UAPI QoS/CU config types.

Risks: command header bitfields must match userspace ABI. Inline helpers silently return invalid state/opcode if vmap fails, so callers must handle invalid commands. Flexible arrays require correct allocation sizing.

Test signals: command parsing for all opcodes, malformed count/mask fields, chained command error reporting, debug BO sync, scheduler job cleanup, and UAPI struct compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ctx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_error.h -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_error.h

Purpose: defines compact AMD XDNA AIE error encoding values used to report critical AIE hardware errors and extra row/column location metadata.

Important APIs/types: `enum amdxdna_error_num` enumerates AIE saturation, floating-point, stream, access, bus, instruction, ECC, lock, DMA, memory parity, and unknown errors. `enum amdxdna_error_module` enumerates AIE core, memory, shim, NOC, PL, and unknown modules. `AMDXDNA_ERROR_ENCODE()` packs error number, driver ID, severity, module, and class into a 64-bit value using fixed masks. `AMDXDNA_EXTRA_ERR_ENCODE()` packs row/column location into auxiliary error data.

Control flow: async error and query paths include this header to translate firmware or hardware error details into UAPI-facing encoded values.

State and persistence: no state; it is a pure encoding contract. Encoded values can persist in in-memory async error records until queried.

Dependencies: Linux bitfield and bit mask helpers.

Risks: masks are part of a UAPI-visible interpretation; changing field positions breaks consumers. Constants assume AIE driver/class/severity assignments remain stable.

Test signals: compile-time coverage, unit-style checks for mask packing/unpacking, async-error query validation, and userspace decoder compatibility for known row/column/module/number combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_gem.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_gem.c

Purpose: implements AMD XDNA GEM buffer objects, including shmem BOs, command/share BOs, device heap/device BOs, imported dma-bufs, user-buffer imports, mmap/HMM notification, explicit cache sync, IOMMU mapping hooks, and BO usage accounting.

Important APIs/functions: `amdxdna_drm_create_bo_ioctl()` dispatches BO creation by type. Share/command BOs use DRM shmem or imported user buffers; device heap BOs create a per-client DRM-MM allocator over device memory; device BOs allocate from that heap. `amdxdna_gem_prime_import()` attaches and maps external dma-bufs. `amdxdna_gem_vmap()`, `amdxdna_gem_uva()`, and `amdxdna_gem_dev_addr()` expose CPU/user/device addresses. mmap paths register HMM interval notifiers and insert pages or delegate imported dma-buf mmap. `amdxdna_drm_sync_bo_ioctl()` flushes CPU caches and optionally syncs debug BOs from device. `amdxdna_drm_get_bo_usage()` aggregates per-client memory accounting.

Control flow: open/close GEM funcs attach BOs to clients and maintain usage; free funcs unregister HMM, unmap IOMMU, unpin, vunmap, and free/import-release storage. Command submission pins argument BOs through this API.

State and persistence: BO state includes type, pinned flag, client, mem addresses, mmap notifier list, DRM-MM nodes, dma-buf attachment, assigned context, and accounting counters. It is all kernel runtime state.

Dependencies: DRM shmem/GEM/dma-buf helpers, HMM/mmu interval notifier, IOMMU helpers, user-buffer helper, cache flush helpers, and AMD XDNA UAPI.

Risks: HMM invalidation and unregister workqueue ordering are subtle; stale user virtual addresses can affect PASID mode. Imported BO mmap drops a GEM reference acquired by DRM mmap. Explicit cache sync bounds are not deeply validated against object size in this file. Device heap lifetime is tied to the client and must outlive device BOs.

Test signals: BO create/get-info/mmap/sync for every type, imported dma-buf paths, PASID vs IOVA addressing, HMM invalidation/unmap, close with live heaps/device BOs, memory accounting queries, and cache-sync offset/size edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_gem.h -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_gem.h

Purpose: declares AMD XDNA GEM object layout, memory tracking structures, user mmap notifier state, address helpers, pin/get APIs, BO ioctl entry points, and prime-import integration.

Important APIs/types: `struct amdxdna_gem_obj` extends DRM shmem with client ownership, BO type, pin state, lock, `amdxdna_mem`, DRM-MM heap/node data, assigned hardware context, dma-buf attachment, and internal flag. `struct amdxdna_mem` tracks CPU mapping, DMA address, size, HMM mapping list, invalidation flag, and cached first user VA. `struct amdxdna_umap` ties a VMA to an mmu interval notifier and HMM range. Helpers convert to GEM objects, detect imported BOs, compute device heap offsets, choose DMA/user addresses under PASID, and manage references.

Control flow: GEM implementation, context submission, AIE2 command code, and IOMMU paths include this header to look up, pin, map, and address BOs.

State and persistence: declared fields are in-memory per BO or mapping; the only user-visible persistence is through GEM handles and mmap offsets while a DRM file is open.

Dependencies: DRM shmem helper, Linux HMM/IOMMU, AMD XDNA PCI driver definitions, and UAPI BO type constants.

Risks: `amdxdna_obj_dma_addr()` switches address source based on PASID, so callers must know whether firmware expects VA or DMA/IOVA. Lock comments identify protected fields; new users must respect them.

Test signals: compile users across PASID/IOVA modes, object reference lifecycle, address helper outputs for heap/device/share/imported BOs, and notifier invalidation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_iommu.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_iommu.c

Purpose: provides optional forced-IOVA mapping for AMD XDNA BOs and driver allocations when SVA/PASID is not used or when the `force_iova` module parameter is enabled.

Important APIs/functions: `amdxdna_iommu_init()` obtains the IOMMU group, and if `force_iova` is set, allocates a paging domain with PASID-capable flags, initializes the IOVA domain, and attaches the group. `amdxdna_iommu_map_bo()` maps shmem/dev-heap BO sg-tables into an allocated IOVA and records `mem.dma_addr`. `amdxdna_iommu_unmap_bo()` unmaps and frees the IOVA. `amdxdna_iommu_alloc()` and `amdxdna_iommu_free()` allocate page-backed coherent-ish driver memory and map/unmap it into the IOMMU domain.

Control flow: probe calls init before hardware startup; GEM open/free map and unmap BOs when IOVA mode is active; message-buffer allocation can use the alloc/free helpers.

State and persistence: `amdxdna_dev` stores `group`, `domain`, and `iovad`; each mapped BO stores its DMA/IOVA address. State is runtime only and released at remove.

Dependencies: Linux IOMMU, IOVA allocator, DRM shmem sg-tables, and AMD XDNA GEM types.

Risks: map failure after partial `iommu_map_sgtable()` must free the allocated IOVA. Only BO types `AMDXDNA_BO_DEV_HEAP` and `AMDXDNA_BO_SHMEM` are mapped here; type mismatches can leave unexpected physical addressing. `__get_free_pages()` allocation order can fail for large sizes.

Test signals: `force_iova=0/1`, domain allocation failure, sg-table absence, map partial failure, BO open/free mapping lifecycle, and message-buffer allocation/free under IOVA mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox.c

Purpose: implements the low-level AMD XDNA mailbox transport over firmware-provided ring buffers and mailbox registers. It sends host-to-firmware messages, receives firmware responses through IRQ/workqueue, matches responses by message ID, and handles ring wrap with tombstones.

Important APIs/functions: `xdnam_mailbox_create()` records mailbox/ring resource bases. `xdna_mailbox_alloc_channel()` creates a channel and RX workqueue. `xdna_mailbox_start_channel()` validates power-of-two rings, records X2I/I2X resources, initializes xarray message tracking, reads initial pointers, requests IRQ, and clears interrupt state. `xdna_mailbox_send_msg()` validates size/alignment/tombstone, builds a protocol header, allocates a magic-tagged message ID, copies payload, and writes the package to the ring. RX flow uses `mailbox_irq_handler()`, `mailbox_rx_worker()`, `mailbox_get_msg()`, and `mailbox_get_resp()` to consume responses and call callbacks.

Control flow: AIE2 startup creates the mailbox and management channel. Message helper calls send and waits on a completion. Stop frees IRQ, drains RX work, completes pending messages with NULL data, and destroys the xarray.

State and persistence: `mailbox_channel` stores ring resources, IRQ, interrupt register, message ID xarray, cached tail/head, workqueue, RX work, and bad-state flag. Pending requests persist until response, timeout cleanup, or channel stop.

Dependencies: DRM managed allocation, Linux xarray with IRQ locking, request_irq, workqueues, IO memcpy, bitfields, tracepoints, and `amdxdna_mailbox.h`.

Risks: ring pointer validation is safety-critical; invalid firmware tail/head marks channel bad and disables further RX. Send-side timeout parameter is currently not used by `mailbox_send_msg()` beyond helper wait. Large-message splitting is explicitly not supported despite header fields.

Test signals: ring wrap/tombstone, full-ring polling, invalid alignment/size/data, bad message ID, IRQ storms, response callback errors, stop with pending messages, and firmware malformed tail/size values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox.h -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox.h

Purpose: declares the public AMD XDNA mailbox transport interface and resource descriptors used by AIE2 firmware message code.

Important APIs/types: opaque `struct mailbox` and `struct mailbox_channel` hide implementation details. `struct xdna_mailbox_msg` carries opcode, callback handle, response callback, send data, and send size. `struct xdna_mailbox_res` describes global ring-buffer and mailbox register mappings. `struct xdna_mailbox_chann_res` describes one channel direction's ring start/size and head/tail mailbox register offsets. Public functions create the mailbox, allocate/start/stop/free channels, and send messages.

Control flow: device bring-up obtains management channel descriptors from firmware SRAM, fills channel resources, starts the channel, then higher-level message helpers submit `xdna_mailbox_msg` requests and wait for callbacks.

State and persistence: the header defines handles and descriptors; runtime state lives in `amdxdna_mailbox.c`. Mailbox resources are MMIO/SRAM mappings supplied by the device.

Dependencies: DRM device for mailbox creation and Linux `void __iomem` conventions through users.

Risks: comments say oversized data may be split transparently, but implementation rejects packages larger than the ring and does not split, so API users must keep messages within ring size. `send_data` must be 4-byte aligned in size and first word cannot equal tombstone.

Test signals: compile coverage for all users, channel resource translation from firmware descriptors, send callback behavior for success, timeout, and stop paths, and validation of message-size assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox_helper.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox_helper.c

Purpose: provides synchronous helper glue around the asynchronous mailbox API: copy a firmware response into caller storage, complete a wait, and send a message while waiting for completion.

Important APIs/functions: `xdna_msg_cb()` is a standard mailbox callback that accepts an `xdna_notify` handle, treats NULL data as cancellation, validates response size, copies response data from MMIO with `memcpy_fromio()`, completes the stack completion, and returns stored error. `xdna_send_msg_wait()` calls `xdna_mailbox_send_msg()`, waits up to `RX_TIMEOUT`, and returns either send error, timeout, or callback error.

Control flow: firmware command helpers declare request/response/notify/message objects using the macro in the header, populate request fields, then call `xdna_send_msg_wait()` on the management channel.

State and persistence: no long-lived state; `xdna_notify` is usually stack-scoped and completed by the mailbox RX worker. Response data is copied into caller-provided response storage.

Dependencies: mailbox API, Linux completions, MMIO copy, DRM logging through AMD XDNA device.

Risks: callback size mismatch returns `-EINVAL` and still completes. Send timeout does not cancel the pending mailbox message; later channel stop or firmware response will release it. Callers must initialize completion and response status correctly.

Test signals: normal response, timeout, NULL-data cancellation on stop, size mismatch, callback error propagation, and repeated synchronous firmware commands under concurrent mailbox RX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox_helper.h -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox_helper.h

Purpose: declares synchronous mailbox helper constants, callback state, a request/response/message declaration macro, and helper prototypes used by AIE2 firmware command wrappers.

Important APIs/types: `TX_TIMEOUT` and `RX_TIMEOUT` define nominal send and receive waits. `struct xdna_notify` carries a completion, response data pointer, expected response size, error, and status pointer. `DECLARE_XDNA_MSG_COMMON(name, op, s)` creates zeroed request, initialized response status, notify handle, and `xdna_mailbox_msg` wired to `xdna_msg_cb`.

Control flow: AIE2 message functions use the macro to reduce boilerplate, then fill request fields and call `xdna_send_msg_wait()`. The mailbox RX worker invokes `xdna_msg_cb()` to complete the wait.

State and persistence: notify objects are caller-owned and generally stack-local; no global state.

Dependencies: Linux completions and mailbox message definitions.

Risks: the macro assumes request and response types follow `<name>_req` and `<name>_resp` naming and that response has a `status` member. It initializes completion on stack, so the notify handle must not outlive the sending function.

Test signals: build all message wrappers using the macro, response-status initialization, timeout behavior, and static analysis for stack lifetime escapes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pci_drv.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pci_drv.c

Purpose: implements the AMD XDNA PCI DRM accel driver: PCI ID matching, DRM driver registration, per-file client lifecycle, ioctls, GEM integration, IOMMU/notifier setup, sysfs setup, runtime/system PM hooks, and probe/remove.

Important APIs/functions: `amdxdna_drm_drv` defines DRM features, file operations, ioctls, open/close, GEM create, and prime import. `amdxdna_probe()` allocates the DRM device, selects `amdxdna_dev_info` by device/revision, initializes locks/lists/IOMMU/notifier workqueue, calls hardware ops init, creates sysfs, and registers DRM. `amdxdna_remove()` unplug/unregisters, cleans clients, finalizes hardware, and tears down IOMMU. `amdxdna_drm_open()` allocates `amdxdna_client`, binds SVA/PASID unless forced IOVA, initializes SRCU/xarray/mm lock, and links into client list. `amdxdna_client_cleanup()` removes contexts, heap, SVA, mm refs, and client memory.

Control flow: `/dev/accel` open enters `accel_open()` then DRM open callback. Ioctls dispatch to context, BO, exec, get-info/get-array, and privileged set-state handlers. PM callbacks call generic AMD XDNA PM functions.

State and persistence: `amdxdna_dev` stores DRM device, selected hardware info, handle, XRS solver, locks, clients, firmware version, notifier state, and IOMMU state. Each file has an `amdxdna_client`. Runtime only.

Dependencies: PCI, DRM accel core, DRM GEM/scheduler/ioctl, IOMMU SVA, AMD XDNA hardware ops, sysfs, PM.

Risks: close path returns early if `drm_dev_enter()` fails, which can leave cleanup to remove path. Client cleanup occurs under `dev_lock`; operations that drop/reacquire the lock must preserve ordering. Set-state is `DRM_ROOT_ONLY`.

Test signals: probe/remove all supported IDs/revisions, open failure paths for SVA/PASID, ioctl validation, runtime/system suspend, forced IOVA mode, remove with open clients, and sysfs/DRM node registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pci_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pci_drv.h -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pci_drv.h

Purpose: declares the shared AMD XDNA PCI driver structures, logging helpers, hardware operation callbacks, static device information, client state, IOMMU helpers, and device-info exports.

Important APIs/types: `struct amdxdna_dev_ops` is the hardware abstraction used by generic ioctls and PM: init/fini, suspend/resume, hwctx lifecycle/config/debug sync, HMM invalidate, command submit, AIE info/state, and array queries. `struct amdxdna_dev_info` records BAR indices, device memory geometry, vbnv string, device type, private per-generation data, and ops. `struct amdxdna_dev` embeds `drm_device` and stores device handle, solver, locks, client list, firmware version, notifier workqueue, and IOMMU state. `struct amdxdna_client` stores per-file PID, hwctx xarray/SRCU, file pointer, heap, SVA/PASID/mm, and memory usage counters.

Control flow: probe fills `amdxdna_dev`; open fills `amdxdna_client`; implementation files call through `dev_info->ops` to keep generic DRM code separate from AIE2 details.

State and persistence: structure definitions describe runtime state only. Device-info constants in register files are immutable tables.

Dependencies: DRM UAPI, DRM logging, Linux IOMMU/IOVA/workqueue/xarray.

Risks: `amdxdna_pm_resume_get_locked()` relies on `dev_lock` conventions declared here. `XDNA_MBZ_DBG()` validates must-be-zero ABI padding and should be used on new ioctls.

Test signals: compile all ops implementers, invalid padding tests, PASID/IOVA mode checks, and per-client memory accounting consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pci_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pm.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pm.c

Purpose: implements generic AMD XDNA runtime and system PM wrappers used by the PCI driver, delegating hardware-specific suspend/resume to `amdxdna_dev_ops`.

Important APIs/functions: `amdxdna_pm_suspend()` and `amdxdna_pm_resume()` lock `dev_lock`, call hardware `suspend`/`resume` if present, and log return status. `amdxdna_pm_resume_get()` wraps `pm_runtime_resume_and_get()` and marks the device suspended on failure. `amdxdna_pm_suspend_put()` drops an autosuspend reference. `amdxdna_pm_init()` marks runtime PM active, sets a 5s autosuspend delay, enables autosuspend, allows runtime PM, and drops the initial ref. `amdxdna_pm_fini()` gets a noresume ref and forbids runtime PM.

Control flow: hardware init calls `amdxdna_pm_init()` after successful AIE2 startup; cleanup calls fini before hardware stop. User ioctls and DPM changes resume the device around hardware access.

State and persistence: state is Linux PM core runtime state on the device plus hardware state restored by ops callbacks. No independent storage.

Dependencies: Linux PM runtime, DRM device lookup, AMD XDNA driver structs.

Risks: suspend/resume callbacks assume `dev_get_drvdata()` points at `amdxdna_dev`. Returning `-EOPNOTSUPP` if ops are absent may not be desirable for future hardware. Failure handling in `resume_get()` changes PM state.

Test signals: runtime autosuspend/resume around ioctl and submit paths, system suspend/resume, PM failure injection, remove while suspended, and lockdep for `dev_lock` interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pm.h -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pm.h

Purpose: declares generic AMD XDNA PM helper functions and provides `amdxdna_pm_resume_get_locked()`, a convenience helper for callers that already hold `dev_lock`.

Important APIs: suspend/resume device callbacks, runtime resume get, autosuspend put, PM init/fini, and the inline locked resume helper.

Control flow: ioctl and AIE2 PM code often need runtime-resumed hardware while generic device state is protected by `dev_lock`. The inline helper temporarily unlocks `dev_lock`, calls `amdxdna_pm_resume_get()`, then reacquires the mutex.

State and persistence: no state; manipulates PM core state via functions in `amdxdna_pm.c`.

Dependencies: AMD XDNA PCI driver definitions and Linux device/PM types.

Risks: callers must be certain dropping `dev_lock` during resume cannot invalidate local assumptions. It should not be used when intermediate state must remain atomic across resume.

Test signals: lockdep coverage, concurrent ioctl/resume operations, and failure paths where resume returns error after the lock is reacquired.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_sysfs.c

Purpose: creates simple read-only sysfs attributes for AMD XDNA accel devices.

Important APIs/functions: `vbnv_show()` returns the static device vbnv string, `device_type_show()` returns the UAPI device type, and `fw_version_show()` returns `major.minor.sub.build` firmware version queried during hardware startup. `amdxdna_sysfs_init()` creates the attribute group on the DRM device kobject; `amdxdna_sysfs_fini()` removes it.

Control flow: PCI probe initializes sysfs after hardware init and before DRM registration; error and remove paths call fini.

State and persistence: sysfs values are derived from `amdxdna_dev_info` and `xdna->fw_ver`. Files exist only while the device is registered.

Dependencies: Linux sysfs device attributes, DRM device, AMD XDNA device info and firmware version state.

Risks: `fw_version` is meaningful only after successful firmware query. `sprintf()` is used with fixed simple values; future longer attributes should prefer bounded helpers.

Test signals: sysfs file presence after probe, removal after unbind, expected values for each supported NPU revision, and behavior when firmware query/init fails before sysfs creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ubuf.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ubuf.c

Purpose: converts user virtual-address ranges into an exported dma-buf that AMD XDNA can import as a GEM BO, enabling long-term pinned user memory submission.

Important APIs/functions: `amdxdna_get_ubuf()` copies a user VA table, validates page alignment and length overflow, enforces `RLIMIT_MEMLOCK` unless privileged, pins pages with `pin_user_pages_fast(FOLL_WRITE | FOLL_LONGTERM)`, exports a dma-buf with custom ops, and returns it for GEM prime import. dma-buf ops map pages to scatterlists, unmap/free sg-tables, release pins and pinned_vm accounting, mmap pages through PFN faults, and vmap/vunmap the pinned pages.

Control flow: `amdxdna_gem_create_ubuf_object()` calls this helper when a create-BO request supplies a VA table. The resulting dma-buf is immediately imported through AMD XDNA GEM prime import.

State and persistence: `amdxdna_ubuf_priv` stores pinned page array, page count, and grabbed mm. Pins and pinned_vm accounting persist until dma-buf release.

Dependencies: dma-buf framework, GUP/pagemap, scatterlist DMA mapping, VM fault insertion, resource limits/capabilities, and AMD XDNA UAPI VA entries.

Risks: long-term writable page pins can affect migration/COW and must be tightly accounted. Partial pin failure unwinds pinned pages by `start`. mmap faults assume pgoff is within pinned page count. Exported dma-buf size is accumulated from user entries.

Test signals: aligned/unaligned VA entries, overflow sizes, memlock limit enforcement, partial GUP failures, dma-buf map/unmap/vmap/mmap/release, and multiple VA entries with correct page ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ubuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ubuf.h -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ubuf.h

Purpose: declares the AMD XDNA user-buffer dma-buf export helper.

Important API: `amdxdna_get_ubuf(struct drm_device *dev, u32 num_entries, void __user *va_entries)` takes a DRM device, a count of user VA entries, and a pointer to the entry array, returning a dma-buf or ERR_PTR.

Control flow: AMD XDNA GEM creation includes this header when handling create-BO requests backed by user virtual addresses. The helper returns a dma-buf that is imported through the normal prime-import path.

State and persistence: no header-owned state; implementation-owned pinned pages persist in the returned dma-buf until release.

Dependencies: DRM device and Linux dma-buf declarations.

Risks: callers must validate the surrounding UAPI table enough to pass the correct entry pointer and count. Returned dma-bufs hold long-term user page pins.

Test signals: compile integration with GEM, error pointer handling, and create-BO userptr coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ubuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu1_regs.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu1_regs.c

Purpose: provides NPU1-specific AMD XDNA register offsets, firmware path/features, runtime config defaults, DPM clock table, hardware op selection, and exported `dev_npu1_info`.

Important data: defines NPU1 BAR indices/bases for register, mailbox, PSP, SMU, and SRAM apertures; maps SRAM firmware-alive and mailbox offsets; maps PSP scratch/interrupt/wait-mode registers; maps SMU scratch/interrupt registers. `npu1_default_rt_cfg` enables PDI app load mode, debug BO, and clock gating. `npu1_dpm_clk_table` lists MP-NPU/H clock pairs. Firmware feature table gates NPU command support by protocol version. `npu1_dev_priv` selects `npu1_set_dpm()`, no natural column alignment, six hardware contexts, and firmware path `amdnpu/1502_00/`.

Control flow: PCI probe selects this table for device `0x1502` revision `0x0`; AIE2 init consumes the BAR and private tables for PSP/SMU/mailbox/runtime configuration.

State and persistence: all data is const except runtime state stored elsewhere. Firmware path drives module firmware lookup.

Dependencies: AIE2 shared header, mailbox, DRM UAPI device type, Linux sizes.

Risks: one wrong offset prevents PSP, SMU, or management mailbox startup. Context limit and column alignment must match hardware/firmware constraints.

Test signals: probe NPU1 hardware, firmware protocol 5.7/5.8+ feature behavior, DPM table programming, runtime config application, sysfs vbnv/device type, and management channel SRAM offset validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu1_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu4_regs.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu4_regs.c

Purpose: provides NPU4-specific AMD XDNA register map and static hardware information, plus shared NPU4-family runtime config, DPM table, and firmware feature table used by later devices.

Important data: defines NPU4 public, MP0, MP1, SRAM mailbox, and aperture addresses; BAR indices/bases; `npu4_default_rt_cfg` for PDI app load, debug buffer, optional preemption, multiple clock-gating controls, force preempt, and frame-boundary preempt; `npu4_dpm_clk_table`; and `npu4_fw_feature_table` enabling NPU command, preemption, temporal-only, app-health, and all features by firmware major/minor. `npu4_dev_priv` selects natural column alignment, 16 contexts, NPU4 firmware path, SMU/PSP/SRAM offsets, and `npu4_set_dpm()`.

Control flow: selected for PCI device `0x17f0` revision `0x10`. AIE2 startup uses these offsets to map registers, start PSP/SMU, find firmware management channel info, and apply runtime configs based on feature mask.

State and persistence: const tables only; live state is in `amdxdna_dev_hdl`.

Dependencies: shared AIE2 ops, NPU4 SMU implementation, runtime config categories and feature bits.

Risks: feature table controls preemption/app-health availability and must match firmware protocol. Shared tables are reused by NPU5/NPU6, so changes affect multiple revisions.

Test signals: NPU4 probe, firmware major 6 minor boundary cases and major 7 all-feature path, preemption set/get, DPM/TOPS values, and BAR offset smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu4_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu5_regs.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu5_regs.c

Purpose: provides NPU5 PCI-revision static device information by reusing NPU4-family runtime configuration, DPM clocks, firmware features, register layout pattern, and hardware ops with an NPU5 firmware path and exported `dev_npu5_info`.

Important data: defines NPU5 BAR indices/bases and public/MP0/MP1/SRAM register addresses mirroring NPU4-family layout. `npu5_dev_priv` uses `amdnpu/17f0_11/`, `npu4_default_rt_cfg`, `npu4_dpm_clk_table`, `npu4_fw_feature_table`, natural column alignment, 16 context limit, and `npu4_set_dpm()`. `dev_npu5_info` exposes vbnv `RyzenAI-npu5`, KMQ device type, 64 MiB device memory, and AIE2 ops.

Control flow: PCI probe selects this table for device `0x17f0` revision `0x11`. The common AIE2 path consumes it exactly like NPU4.

State and persistence: static const data only.

Dependencies: shared NPU4 tables exported from `npu4_regs.c`, AIE2 common code, and SMU/PSP offset enums.

Risks: because it reuses NPU4 tables, any NPU5-specific firmware/runtime difference must be represented here or in shared tables before enabling. Firmware path mismatch would fail firmware request.

Test signals: probe revision 0x11, firmware loading from `17f0_11`, management mailbox startup, DPM operations through NPU4 SMU commands, and sysfs vbnv/device type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu5_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu6_regs.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu6_regs.c

Purpose: provides NPU6 static hardware information for AMD XDNA, largely reusing the NPU4-family register layout, runtime configs, DPM table, firmware features, and SMU DPM implementation.

Important data: defines NPU6 BAR indices/bases, public/MP0/MP1/SRAM addresses, `npu6_dev_priv`, and exported `dev_npu6_info`. The private table uses firmware path `amdnpu/17f0_10/`, NPU4 default runtime configs, NPU4 clock and feature tables, natural column alignment, 16 contexts, and `npu4_set_dpm()`. Device info identifies vbnv `RyzenAI-npu6` and KMQ type.

Control flow: selected for PCI device `0x17f0` revision `0x20`; common AIE2 probe/start/PM/query paths use the offsets and tables.

State and persistence: immutable device tables only.

Dependencies: NPU4 shared tables, AIE2 common ops, Linux sizes, DRM UAPI.

Risks: firmware path reuse with `17f0_10` is intentional only if NPU6 firmware packaging matches; otherwise probe firmware request fails or loads incompatible firmware. Register table copy/paste errors would break PSP/SMU/mailbox.

Test signals: revision 0x20 hardware bind, firmware request path, BAR offset validation, DPM power changes, context limit enforcement, and query metadata consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu6_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/drm_accel.c -->
# sources/distributed-fs/ceph-client/drivers/accel/drm_accel.c

Purpose: implements the DRM accel core character-device support used by accelerator drivers under `/dev/accel/*`, including accel class setup, minor lookup/open, common debugfs registration, and stub file-ops replacement.

Important APIs/functions: `accel_core_init()` registers the `accel` sysfs class and major char device with stub fops; `accel_core_exit()` unregisters them and checks the accel minor xarray. `accel_set_device_instance_params()` assigns dev_t, class, and device type for accel minors. `accel_open()` is the real open helper drivers use; it acquires the DRM accel minor, increments open count, shares the DRM anon inode mapping, and calls `drm_open_helper()`. `accel_stub_open()` handles initial char-device opens by replacing fops with the target driver's fops. `accel_debugfs_register()` adds a common `name` debugfs file.

Control flow: core init runs with DRM subsystem initialization. Driver fops typically use `DEFINE_DRM_ACCEL_FOPS` or `accel_open()`, so user opens flow through minor lookup into DRM open callbacks.

State and persistence: global `accel_minors_xa` maps minor numbers to DRM minors. Sysfs class and char device persist while DRM core is loaded.

Dependencies: DRM minor/open/debugfs/auth infrastructure, Linux device classes, xarray, and `ACCEL_MAJOR`.

Risks: minor acquire/release pairing is critical. Stub fops must replace with a valid driver fops reference. Open-count increment is undone only on helper failure.

Test signals: module/core init failure unwind, multiple accel device registration, open invalid minor, debugfs name output, and driver open failure reference cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/drm_accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/accel/ethosu/Kconfig

Purpose: adds the build-time configuration option for the Arm Ethos-U DRM accel driver.

Important entries: `config DRM_ACCEL_ETHOSU` is a tristate option named `ARM Ethos-U NPU` depending on `DRM_ACCEL`, `OF`, and `HAS_IOMEM`, and selecting `DRM_SCHED`, `DMA_SHARED_BUFFER`, and `GENERIC_ALLOCATOR`.

Control flow: kernel configuration enables or disables compilation of the Ethos-U platform accel driver and its support for DRM scheduler, dma-buf sharing, and SRAM gen-pool allocation.

State and persistence: no runtime state; affects build configuration and module availability.

Dependencies: DRM accel core, device tree, MMIO, scheduler, dma-buf, and generic allocator support.

Risks: missing selected dependencies would break build/link. The OF dependency means non-device-tree platforms cannot select it directly.

Test signals: `allyesconfig`, module and built-in builds, dependency-disabled configs, and device-tree platform probe with `arm,ethos-u65`/`arm,ethos-u85` compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/accel/ethosu/Makefile

Purpose: defines the object composition for the Arm Ethos-U DRM accel driver.

Important entries: `ethosu-y` includes `ethosu_drv.o`, `ethosu_gem.o`, and `ethosu_job.o`; `obj-$(CONFIG_DRM_ACCEL_ETHOSU)` builds the combined `ethosu.o` module or built-in object.

Control flow: Kbuild compiles the driver only when `DRM_ACCEL_ETHOSU` is enabled.

State and persistence: no runtime state.

Dependencies: the object list mirrors the driver split: platform/DRM probe, GEM/cmdstream validation, and scheduler/job execution.

Risks: adding new source files requires updating this list; missing objects cause unresolved symbols for declared helpers.

Test signals: module and built-in builds, incremental builds after each source change, and link checks for all `ethosu_*` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_device.h -->
# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_device.h

Purpose: central Ethos-U private device header defining MMIO registers, command opcodes, bit masks, SRAM region constants, device state, and device conversion helpers.

Important APIs/types: register defines cover ID/status/command/reset/queue/base-pointer/config/protection/AXI/memory attributes for U65 and U85. `enum ethosu_cmds` lists NPU operations and configuration commands parsed by command-stream validation. `struct ethosu_device` embeds DRM device, register and SRAM mappings, gen-pool, clocks, IRQ, NPU info UAPI struct, in-flight job pointer, locks, DRM scheduler, fence context, and sequence number. `ethosu_is_u65()` derives architecture generation from the ID register.

Control flow: driver probe fills `ethosu_device`; GEM validation uses opcode constants; job submission programs base-pointer and queue registers; reset/config code writes register constants.

State and persistence: all fields are runtime device state. NPU info is cached from registers and exposed via query ioctl.

Dependencies: DRM device/scheduler, `drm/ethosu_accel.h`, Linux bitfield/bits, gen_pool, clock declarations.

Risks: register/opcode definitions are hardware ABI. U65/U85 overlapping register offsets require generation checks before writes. Region 2 is reserved for SRAM when present.

Test signals: register ID/config decode, U65 vs U85 reset configuration, command-stream validation for all opcodes used by Vela, SRAM-present and absent platforms, and job register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_drv.c -->
# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_drv.c

Purpose: implements the Arm Ethos-U platform DRM accel driver: device-tree probe/remove, reset and runtime PM, SRAM setup, NPU info discovery, DRM ioctls, open/close, and DRM driver registration.

Important APIs/functions: ioctl handlers query NPU info, create/wait/mmap BOs, create validated command-stream BOs, and submit jobs. `ethosu_reset()` resets the NPU to non-secure mode, configures region and AXI/memory attributes for U65/U85, and clears SRAM. Runtime PM callbacks enable/disable clocks and reset on resume. `ethosu_init()` resumes hardware, enables autosuspend, reads ID/config, initializes SRAM, and logs capabilities. `ethosu_probe()` allocates DRM device, sets DMA mask, maps registers, gets clocks, initializes jobs, initializes hardware, registers DRM, and autosuspends.

Control flow: users open the accel node, receive per-file scheduler entity state, allocate BOs/command streams, and submit jobs. Remove unregisters DRM, finalizes scheduler, and frees SRAM allocation.

State and persistence: `ethosu_device` stores clocks, regs, SRAM pool/allocation, NPU info, scheduler/fence/job state. Runtime PM core tracks active/suspended state.

Dependencies: platform device/OF, DRM accel/GEM/ioctl, PM runtime, clocks, genalloc SRAM, Ethos-U GEM/job helpers, UAPI.

Risks: `devm_platform_ioremap_resource()` result is assigned without explicit `IS_ERR()` check here. Runtime PM init ordering must balance refs. Reset configuration differs by generation and can break memory routing.

Test signals: probe for U65/U85 compatibles, missing clocks/IRQ/SRAM, all ioctls with invalid pads/sizes, suspend/resume, NPU query ABI, and remove with open files/jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_drv.h -->
# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_drv.h

Purpose: declares the per-file private state for the Ethos-U DRM accel driver.

Important type: `struct ethosu_file_priv` stores the `ethosu_device` pointer and a DRM scheduler entity for jobs submitted by that file.

Control flow: `ethosu_open()` allocates this structure and calls `ethosu_job_open()` to initialize the scheduler entity; `ethosu_postclose()` destroys it through `ethosu_job_close()`.

State and persistence: per-open runtime state only. It persists until DRM postclose.

Dependencies: DRM GPU scheduler and forward declaration of `ethosu_device`.

Risks: job submission assumes `file->driver_priv` is a valid initialized `ethosu_file_priv`; open failure paths must not publish partial state.

Test signals: open/postclose lifecycle, scheduler entity cleanup with queued jobs, and invalid file-private handling in submit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_gem.c -->
# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_gem.c

Purpose: implements Ethos-U GEM BO allocation and command-stream BO validation. It uses DMA GEM objects for data buffers and stores parsed command-stream region-size/output metadata on command BOs.

Important APIs/functions: `ethosu_gem_create_object()` provides DRM object allocation; `ethosu_gem_create_with_handle()` allocates a DMA GEM BO, records flags, creates a handle, and returns actual size. `ethosu_gem_mmap()` rejects mmap for BOs with `DRM_ETHOSU_BO_NO_MMAP`. `ethosu_gem_cmdstream_create()` allocates a DMA BO, copies user command words, validates them, stores `ethosu_validated_cmdstream_info`, and publishes a handle. Validation tracks command state, decodes immediate/address commands, computes maximum region sizes for DMA, IFM/IFM2/OFM, weights, and scales, and marks output regions.

Control flow: command-stream create ioctl calls this file before submit. Submit later compares required region sizes against supplied BO sizes and uses output-region flags for reservation fences.

State and persistence: each `ethosu_gem_object` stores flags and optional command metadata until BO free. Command BO data is copied into DMA memory.

Dependencies: DRM DMA GEM helpers, Ethos-U register/opcode definitions, UAPI flags.

Risks: command validation is a software parser for hardware command streams; unsupported U85 resize currently only warns/TODO. Address/stride arithmetic and U65/U85 opcode overlaps are subtle. Missing validation can permit out-of-BO device access.

Test signals: validated Vela command streams, malformed missing setup, oversized region access, NO_MMAP enforcement, U65/U85 elementwise differences, DMA stride modes, and command BO used incorrectly as region BO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_gem.h -->
# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_gem.h

Purpose: declares Ethos-U GEM private object state, command-stream validation metadata, conversion helper, and BO/command-stream creation APIs.

Important APIs/types: `struct ethosu_validated_cmdstream_info` records copied command size, required size per base-pointer region, and whether each region is written. `struct ethosu_gem_object` embeds `drm_gem_dma_object`, stores optional validation info, and BO flags. `to_ethosu_bo()` converts a DRM GEM object to the private container. Public helpers create generic BOs, BO handles, and command-stream BOs.

Control flow: driver ioctls create BOs through these functions; job submit reads command metadata to validate region handles and set fence dependencies.

State and persistence: metadata persists with the GEM object and is freed by the object free callback.

Dependencies: DRM DMA GEM helper, Ethos-U device definitions, and UAPI flags.

Risks: any object with non-NULL `info` is treated as a command-stream BO and rejected as a region BO. Users of `to_ethosu_bo()` must pass Ethos-U objects only.

Test signals: command BO metadata lifetime, data BO without metadata, handle creation, mmap flag behavior, and region validation in job submit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_job.c -->
# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_job.c

Purpose: implements Ethos-U job submission, DRM scheduler integration, hardware register programming, IRQ completion, timeout/reset handling, per-file scheduler entities, and submit ioctl validation.

Important APIs/functions: `ethosu_ioctl_submit()` copies an array of jobs and submits each. `ethosu_ioctl_submit_job()` validates SRAM/region handles against command metadata, rejects command BOs as region BOs, checks region size <= BO size, allocates fences, initializes a DRM scheduler job, and pushes it. `ethosu_job_push()` locks reservations, adds implicit dependencies, resumes runtime PM, arms and queues the scheduler job, and attaches output fences. `ethosu_job_run()` initializes the hardware completion fence, sets `in_flight_job`, and calls `ethosu_job_hw_submit()` to program base pointers, SRAM pointer, queue base/size, and run command. IRQ handlers clear IRQ and signal the done fence. Timeout stops scheduler, force-suspends/resumes hardware, and restarts scheduler.

Control flow: per-file scheduler entity queues jobs into a single-credit scheduler. Hardware has one in-flight job tracked under `job_lock`.

State and persistence: `ethosu_job` holds references to command and region BOs, region numbers, SRAM size, scheduler and IRQ fences, and kref. Device stores scheduler, in-flight job, fence context, and sequence.

Dependencies: DRM scheduler/fences/reservations, DRM GEM DMA, PM runtime, MMIO registers, gen_pool SRAM, IRQ.

Risks: timeout reset must clear `in_flight_job` and restart scheduler safely. Reservation/fence ordering must protect output BOs. Multiple jobs are submitted sequentially; failure stops later jobs without rolling back earlier queued jobs.

Test signals: submit valid/invalid jobs, missing/extra region handles, SRAM region conflict, implicit fence dependencies, IRQ completion, timeout progress/no-progress branches, reset recovery, and close with queued jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_job.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_job.h -->
# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_job.h

Purpose: declares Ethos-U job state and job-management entry points used by the driver and ioctl layer.

Important APIs/types: `struct ethosu_job` embeds a DRM scheduler job, device pointer, command BO, up to eight region BOs and their region numbers, region count, requested SRAM size, inference-done scheduler fence, hardware done fence, and kref. Public functions initialize/finalize device scheduler state, initialize/destroy per-file scheduler entity state, and handle the submit ioctl.

Control flow: open initializes per-file scheduler entity; submit allocates `ethosu_job` and pushes it; scheduler backend runs and frees jobs; IRQ/timeout paths signal or reset.

State and persistence: per-job runtime state persists from ioctl submission until scheduler cleanup and kref release. No disk state.

Dependencies: Linux kref, DRM scheduler, Ethos-U region constants from device header.

Risks: fixed region array size must match hardware `NPU_BASEP_REGION_MAX`. Fence ownership is split between scheduler and IRQ completion, so cleanup must drop both.

Test signals: scheduler init/fini, per-file open/close, job kref lifetime, region array bounds, and submit ioctl ABI validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_job.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/Kconfig

Purpose: defines configuration for the HabanaLabs DRM accel driver and optional NVMe peer-to-peer direct I/O support.

Important entries: `DRM_ACCEL_HABANALABS` is a tristate depending on `DRM_ACCEL`, x86_64, PCI, and MMIO, selecting allocator, hwmon, dma-buf, CRC32, and firmware loader support. Nested `HL_HLDIO` enables HabanaLabs NVMe Direct I/O when PCI P2PDMA and block support are available.

Control flow: Kconfig determines whether the large HabanaLabs accelerator stack and optional HLDIO object are built.

State and persistence: build-time only; no runtime state.

Dependencies: DRM accel core, PCI, x86_64, HAS_IOMEM, firmware loading, DMA shared buffers, hwmon, CRC32, and optional P2PDMA/block.

Risks: HLDIO help notes hardware/IOMMU topology constraints; enabling it on unsupported systems may still compile but runtime paths must validate.

Test signals: config matrix for built-in/module/disabled, HLDIO enabled/disabled, dependency-disabled builds, and Kconfig help consistency with UAPI location.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/Makefile

Purpose: assembles the HabanaLabs accelerator driver object from common and ASIC-specific object lists.

Important entries: builds `habanalabs.o` when `CONFIG_DRM_ACCEL_HABANALABS` is enabled. It includes common, gaudi2, gaudi, and goya makefile fragments and appends their object lists. Debugfs support adds `common/debugfs.o` when `CONFIG_DEBUG_FS` is enabled.

Control flow: Kbuild includes this top-level makefile, then imported fragments contribute source objects for shared and per-ASIC code.

State and persistence: no runtime state; controls build composition.

Dependencies: subdirectory Makefiles must define `HL_COMMON_FILES`, `HL_GAUDI2_FILES`, `HL_GAUDI_FILES`, and `HL_GOYA_FILES`.

Risks: include order matters because each fragment populates variables used immediately afterward. Missing debugfs conditional coverage can hide unresolved references.

Test signals: all ASIC families build, debugfs on/off, module and built-in configurations, and incremental build after adding/removing common or ASIC files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/Makefile -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/Makefile

Purpose: defines the common HabanaLabs object list and imports common MMU and PCI makefile fragments.

Important entries: includes `common/mmu/Makefile` and `common/pci/Makefile`, appends their object lists, and defines `HL_COMMON_FILES` with core common sources such as driver, device, context, ASID, ioctl, command buffer, queues, IRQ, sysfs, hwmon, memory, command submission, firmware interface, security, state dump, memory manager, and decoder. Adds `common/hldio.o` when `CONFIG_HL_HLDIO` is set.

Control flow: top-level HabanaLabs Makefile includes this fragment to populate `habanalabs-y`.

State and persistence: build metadata only.

Dependencies: common subfragments and all listed source files.

Risks: the `ifdef CONFIG_HL_HLDIO` conditional depends on Kbuild variable visibility; wrong conditional style can omit or include optional code unexpectedly.

Test signals: HLDIO enabled/disabled builds, common MMU/PCI fragment integration, and link checks for common symbols used by ASIC-specific files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/asid.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/asid.c

Purpose: manages HabanaLabs ASID allocation with a bitmap, reserving ASID 0 for kernel/device CPU use.

Important APIs/functions: `hl_asid_init()` allocates `hdev->asid_bitmap`, initializes the mutex, and sets bit 0. `hl_asid_alloc()` locks the bitmap, finds the first zero bit below `max_asid`, sets it, and returns it; if full it returns 0. `hl_asid_free()` rejects kernel ASID or out-of-range ASIDs with a critical log and otherwise clears the bit. `hl_asid_fini()` destroys the mutex and frees the bitmap.

Control flow: device initialization calls init; context creation allocates ASIDs; context/device teardown frees them; final cleanup calls fini.

State and persistence: `hdev->asid_bitmap` and `asid_mutex` are runtime device state. ASID assignments persist while contexts live.

Dependencies: HabanaLabs device structures, Linux bitmap/slab/mutex helpers.

Risks: returning 0 for allocation failure overlaps the reserved kernel ASID value, so callers must treat 0 as failure for user contexts. `hl_asid_free()` lacks locking around `clear_bit()`, which relies on caller-side serialization or atomic bitops being sufficient for the driver contract.

Test signals: bitmap allocation failure, exhaustion at `max_asid`, reserved ASID rejection, double-free behavior, concurrent allocate/free, and device fini after active contexts are gone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/asid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/command_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/command_buffer.c

Purpose: implements HabanaLabs command-buffer allocation, mapping, mmap exposure, ioctl handling, kernel CB pools, and per-context command-buffer VA pools.

Important APIs/functions: `hl_cb_create()` validates device/reset state and size, then allocates an `hl_mmap_mem_buf` using `cb_behavior`. Allocation may reuse a kernel CB pool entry, allocate internal pool memory, or allocate coherent DMA memory. Optional `cb_map_mem()` reserves device VA from `ctx->cb_va_pool`, maps the CB into the device MMU, and invalidates MMU cache. `hl_cb_destroy()` atomically marks a handle destroyed and drops the handle reference. `hl_cb_info()` reports usage count or mapped device VA. `hl_cb_ioctl()` dispatches create/destroy/info UAPI operations. Kernel helpers create/get/destroy CBs, initialize/finalize the kernel CB pool, and initialize/finalize per-context CB VA pools.

Control flow: user ioctl creates CB handles in a file memory manager; command submission gets CB refs and increments usage elsewhere; mmap uses ASIC-specific mmap callback; release unmaps, removes debugfs, drops context ref, and either returns CB to pool or frees it.

State and persistence: CBs store kernel address, bus address, size, mapped VA, context/device refs, pool/internal flags, handle-destroyed atomic, and mmap buffer linkage. VA pools reserve a 4 GiB host VA range per context when supported.

Dependencies: HabanaLabs memory manager, MMU, ASIC DMA/mmap callbacks, gen_pool, debugfs, UAPI, reset/device status, and context refs.

Risks: GFP_ATOMIC allocation path is latency-sensitive. Mapping is unsupported for kernel context. Destroy can occur while CB is in use, leaving release to final ref. MMU map/unmap/cache invalidation must stay under `mmu_lock`.

Test signals: create/destroy/info ioctl, max-size rejection, disabled/reset device rejection, pool reuse, internal CB allocation, mapped CB VA reporting, mmap, destroy while in use, VA pool init/fini, and MMU failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/command_buffer.c -->
