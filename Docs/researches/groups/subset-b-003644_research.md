# Research Report: subset-b-003644

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_gpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_gpu.c

## Purpose
`a2xx_gpu.c` implements the MSM DRM Adreno A2xx backend. It wires the common `msm_gpu`/`adreno_gpu` framework to A200/A220/A225 hardware by programming the legacy GPUMMU, loading PM4/PFP firmware, submitting indirect buffers, handling interrupts, exposing register ranges for dumps, and creating the A2xx-specific VM.

## Important APIs, Types, And Functions
The public integration point is `a2xx_gpu_funcs`, whose `.base` methods provide `hw_init`, `submit`, `irq`, `recover`, `destroy`, `gpu_state_get`, `create_vm`, and `get_rptr`, while `.init` points at `a2xx_gpu_init`. Important private helpers are `a2xx_submit`, `a2xx_me_init`, `a2xx_hw_init`, `a2xx_recover`, `a2xx_idle`, `a2xx_irq`, `a2xx_gpu_state_get`, `a2xx_create_vm`, and `a2xx_get_rptr`. The file also owns the `a200_registers`, `a220_registers`, and `a225_registers` debug register range tables.

## Control Flow
Initialization starts in `a2xx_gpu_init`: allocate `struct a2xx_gpu`, initialize the common Adreno object with one ring, choose the register table by chip revision, and return the embedded `msm_gpu`. Hardware bring-up in `a2xx_hw_init` obtains GPUMMU physical addresses from `a2xx_gpummu_params`, halts the ME, resets RBBM, configures MMU client behavior and virtual address range, writes arbiter/cache/interrupt/GMEM registers, calls `adreno_hw_init`, programs ringbuffer base/control, uploads PM4 and PFP firmware, sets CP queue thresholds, clears ME halt, and runs `a2xx_me_init`. `a2xx_me_init` emits `CP_ME_INIT` into the ring, including protected-mode setup unless legacy firmware forced protection off.

Submit flow walks `submit->cmd[]`, skips IB target buffers, conditionally skips context restore buffers when the ring context sequence is unchanged, emits `CP_INDIRECT_BUFFER_PFD` for real buffers, writes the submit seqno to scratch reg 2, waits for idle, writes `CACHE_FLUSH_TS` to the ring fence address, triggers a CP interrupt, and flushes the ring write pointer. IRQ flow reads `MASTER_INT_SIGNAL`, decodes MH, CP, and RBBM substatus, logs unexpected faults, acknowledges each source, then calls `msm_gpu_retire`.

## State And Persistence
Persistent state is held in `struct a2xx_gpu` (`pm_enabled`, `protection_disabled`) and in the shared `adreno_gpu` and `msm_gpu` fields initialized by the common layer. Firmware version detection can set `protection_disabled`, which changes later ME initialization. The file programs hardware registers rather than maintaining large software caches; fences persist through ring memptrs and scratch register writes. The debug state snapshot adds `REG_A2XX_RBBM_STATUS` to the common Adreno state.

## Dependencies And Integration Points
The file depends on `a2xx_gpu.h`, `a2xx.xml.h`, `msm_gem`, `msm_mmu`, Adreno firmware helpers, ring packet macros, GPUMMU helpers in `a2xx_gpummu.c`, and common DRM/MSM recovery, retire, suspend/resume, state, and VM plumbing. `a2xx_create_vm` is the key integration point with the old GPU-side MMU path, using a 16 MiB base and `0xfff * 64 KiB` range.

## Risks
Bring-up is register-order sensitive; ME halt/reset, firmware upload, MMU invalidation, and protected-mode setup must remain in the required order. Legacy firmware disables protection support and changes error coverage. `a2xx_submit` uses 32-bit IB addresses and A2xx packet forms, so it depends on the VM aperture and ring setup matching those constraints. IRQ handling mostly logs non-RB CP errors, so fault diagnosis depends on preserving status before acknowledgements.

## Test Signals
Useful signals are successful probe for A200/A220/A225, PM4/PFP firmware load messages with expected versions, `a2xx_me_init` reaching idle, command submission completing via `CACHE_FLUSH_TS` fence updates, MH/RBBM faults logging and clearing, `create_vm` producing a GPUMMU-backed GPU VM, recovery reinitializing after soft reset, and debug dumps showing A2xx register tables without invalid access faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_gpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_gpu.h

## Purpose
`a2xx_gpu.h` declares the A2xx-specific GPU wrapper, generation register definitions, and the GPUMMU interface used by `a2xx_gpu.c`.

## Important APIs, Types, And Functions
The central type is `struct a2xx_gpu`, embedding `struct adreno_gpu base` and adding `pm_enabled` plus `protection_disabled`. `to_a2xx_gpu()` converts from `adreno_gpu` to the generation wrapper. The header exports `a2xx_gpu_funcs`, `a2xx_gpummu_new`, and `a2xx_gpummu_params`.

## Control Flow
The header has no runtime control flow. It defines the declarations that allow catalog/platform code to select `a2xx_gpu_funcs`, allow the runtime file to cast into `struct a2xx_gpu`, and allow VM creation to instantiate/configure the A2xx GPUMMU.

## State And Persistence
The only declared persistent state is the per-device A2xx wrapper. `protection_disabled` is especially important because firmware probing can set it and subsequent ME initialization will skip protected mode.

## Dependencies And Integration Points
It includes `adreno_gpu.h`, undefines `ROP_COPY` and `ROP_XOR` before including generated `a2xx.xml.h`, and forward-declares the MMU helper API consumed by `a2xx_gpu.c`.

## Risks
The header couples A2xx runtime code to the generated XML register namespace and the old GPUMMU implementation. Any change to `struct a2xx_gpu` must preserve `base` as the first field for `container_of`. Prototype drift would break VM setup or firmware/protection handling.

## Test Signals
Compile coverage is the primary signal. Runtime signals include successful casts through `to_a2xx_gpu`, successful A2xx VM creation through `a2xx_gpummu_new`, and protected-mode behavior following `protection_disabled`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_gpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_gpummu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_gpummu.c

## Purpose
`a2xx_gpummu.c` implements the legacy A2xx GPU MMU backend used when creating an A2xx `drm_gpuvm`. It allocates a contiguous page table, maps DRM GEM scatterlists into the GPU's 4 KiB page table format, invalidates the A2xx MMU after changes, and reports page table and translation-error addresses to hardware init.

## Important APIs, Types, And Functions
The private type is `struct a2xx_gpummu`, embedding `struct msm_mmu` and storing `gpu`, `pt_base`, and the CPU pointer to the table. Public functions are `a2xx_gpummu_new` and `a2xx_gpummu_params`. The `msm_mmu_funcs` implementation supplies `a2xx_gpummu_map`, `a2xx_gpummu_unmap`, `a2xx_gpummu_detach`, and `a2xx_gpummu_destroy`.

## Control Flow
`a2xx_gpummu_new` allocates the wrapper, then allocates `TABLE_SIZE + 32` bytes of force-contiguous DMA memory for the page table plus translation-error area, initializes `msm_mmu` with type `MSM_MMU_GPUMMU`, and returns the base object. Map computes the table index from `(iova - GPUMMU_VA_START) / 4 KiB`, derives read/write protection bits from IOMMU flags, iterates DMA pages in the scatter-gather table, writes one table entry per 4 KiB page, then invalidates all MMU and texture-cache translations. Unmap clears entries over the supplied length and performs the same invalidation. Destroy frees the contiguous DMA allocation and wrapper.

## State And Persistence
Persistent MMU state is the DMA-coherent page table and its bus address. `GPUMMU_VA_START` is 16 MiB and the range is `0xfff * 64 KiB`, matching `a2xx_create_vm`. The translation-error pointer returned by `a2xx_gpummu_params` is immediately after the table and is expected to be 32-byte aligned.

## Dependencies And Integration Points
This file depends on Linux DMA mapping, MSM MMU abstractions, `msm_drv`, `adreno_gpu`, `a2xx_gpu`, and A2xx MMU invalidation register definitions. `a2xx_gpu.c` calls `a2xx_gpummu_params` during hardware initialization and uses `a2xx_gpummu_new` when creating the GPU VM.

## Risks
Map/unmap assume page-aligned 4 KiB iteration and warn, but do not recover, if `off != 0`. Bounds are trusted from the upper VM layer, so an invalid IOVA could index outside the allocated table. The table uses simple read/write bits with no richer caching attributes. Every map/unmap flushes immediately, which is safe but can be costly under many small mappings.

## Test Signals
Signals include successful DMA allocation on probe, valid `MH_MMU_PT_BASE`/`TRAN_ERROR` programming, command buffers executing from mapped IOVAs, MMU page faults for unmapped addresses, no out-of-range table warnings from VM tests, and clean DMA free on GPU teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_gpummu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a3xx_catalog.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a3xx_catalog.c

## Purpose
`a3xx_catalog.c` is the static device catalog for Adreno 3xx GPUs. It describes supported chip IDs, firmware filenames, GMEM size, inactive period, revision numbers where needed, and the function table used by the common Adreno discovery path.

## Important APIs, Types, And Functions
The file defines `static const struct adreno_info a3xx_gpus[]` and publishes it through `DECLARE_ADRENO_GPULIST(a3xx)`. Each entry uses `ADRENO_CHIP_IDS`, firmware slots `ADRENO_FW_PM4`/`ADRENO_FW_PFP`, `ADRENO_3XX`, GMEM sizes, optional `.revn`, and `.funcs = &a3xx_gpu_funcs`.

## Control Flow
There is no executable flow beyond static registration. At probe/catalog lookup time, the shared Adreno code matches a detected chip ID against this array and passes the selected `adreno_info` into platform/runtime initialization.

## State And Persistence
The table is immutable. Its values persist as `adreno_gpu->info` and drive firmware loading, GMEM range setup, revision checks, and runtime workarounds in `a3xx_gpu.c`.

## Dependencies And Integration Points
It includes `adreno_gpu.h` and `a3xx_gpu.h`. Runtime code consumes the resulting `adreno_info` through helpers such as `adreno_is_a305`, `adreno_is_a320`, and `adreno_is_a330`, and uses `.gmem` for GMEM register programming.

## Risks
Catalog errors cause wrong firmware, wrong GMEM size, or wrong generation dispatch. Several chip IDs collapse to shared firmware, while some entries use artificial `.revn` values for helper compatibility; changing them can break runtime branch selection.

## Test Signals
Probe logs should identify the intended A3xx variant, request the expected `a300_*` or `a330_*` firmware files, program the expected GMEM size, and route initialization through `a3xx_gpu_funcs`. Device-tree/platform matrices should confirm every listed chip ID matches exactly one entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a3xx_catalog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a3xx_gpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a3xx_gpu.c

## Purpose
`a3xx_gpu.c` implements the Adreno 3xx runtime backend for MSM DRM. It initializes A305/A306/A320/A330-class hardware, submits command buffers, loads PM4/PFP firmware, handles IRQ retirement, exposes performance counters and debug state, and manages optional OCMEM-backed GMEM.

## Important APIs, Types, And Functions
The exported function table is `a3xx_gpu_funcs`. Key helpers are `a3xx_submit`, `a3xx_me_init`, `a3xx_hw_init`, `a3xx_recover`, `a3xx_destroy`, `a3xx_idle`, `a3xx_irq`, `a3xx_gpu_state_get`, `a3xx_gpu_busy`, `a3xx_get_rptr`, and `a3xx_gpu_init`. `A3XX_INT0_MASK`, `a3xx_registers`, and `perfcntrs` define interrupt, dump, and devfreq/perf counter behavior.

## Control Flow
`a3xx_gpu_init` allocates `struct a3xx_gpu`, sets perf counters and register table, runs common Adreno initialization with one ring, optionally allocates OCMEM for A330/A305B, obtains `gfx-mem` and optional `ocmem` interconnect paths, and currently raises both to a maximum bandwidth derived from `gpu->fast_rate`.

`a3xx_hw_init` writes variant-specific VBIF tuning for A305, A305B, A306/A306A, A320, A330v2, and A330, then programs busy masks, hysteresis, AHB reporting, power counters, hang detection, UCHE cacheline mode, clock gating, OCMEM GMEM base, perf counter selectors, interrupt mask, ringbuffer base/control, CP protected-register ranges, PM4/PFP firmware, CP queue thresholds, ME enable, and finally `CP_ME_INIT`.

Submit flow emits `CP_INDIRECT_BUFFER_PFD` packets for context restore and command buffers, writes the seqno to scratch register 2, sends `HLSQ_FLUSH`, waits for idle, emits `CACHE_FLUSH_TS | IRQ` to the fence address, and flushes the ring. IRQ handling reads and clears `RBBM_INT_0_STATUS` and calls `msm_gpu_retire`.

## State And Persistence
`struct a3xx_gpu` stores optional OCMEM state. The common Adreno state stores firmware, ring, register ranges, and `adreno_info`. Runtime state includes selected perf counters, ring fences, CP scratch seqnos, and OCMEM base. GPU state capture adds `RBBM_STATUS`.

## Dependencies And Integration Points
The file depends on generated A3xx registers, ring packet macros, common Adreno helpers, OCMEM helpers, interconnect APIs, DRM state/debug APIs, and MSM retire/recovery/PM helpers. `a3xx_catalog.c` supplies `.gmem`, firmware names, and revision information that decide most branches.

## Risks
The most fragile area is variant-specific VBIF and clock-gating programming. Incorrect revision helpers or catalog data can select an invalid register sequence. OCMEM allocation and interconnect setup errors abort probe for variants that require them. IRQ decoding is minimal, so unexpected faults may only be visible through raw status and hang recovery.

## Test Signals
Signals include successful probe for each A3xx catalog entry, correct firmware load, no `BUG()` branch in init, OCMEM GMEM base setup on A330/A305B, command fences completing, RBBM busy counter changing with workload, interconnect bandwidth requests succeeding, recovery after soft reset, and no repeated hang-detect or AHB status during GLES workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a3xx_gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a3xx_gpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a3xx_gpu.h

## Purpose
`a3xx_gpu.h` declares the A3xx GPU wrapper and function table used by the Adreno catalog and runtime implementation.

## Important APIs, Types, And Functions
`struct a3xx_gpu` embeds `struct adreno_gpu base` and contains an `adreno_ocmem` member for variants using OCMEM as GMEM. `to_a3xx_gpu()` performs the container cast. `a3xx_gpu_funcs` is the exported generation function table.

## Control Flow
The header has no executable flow. It defines the type relationship that lets common Adreno code operate on `msm_gpu` while A3xx runtime code can recover generation-local OCMEM state.

## State And Persistence
The declared persistent state is the common Adreno base plus optional OCMEM allocation metadata. Firmware, rings, and register tables live in the embedded base.

## Dependencies And Integration Points
It includes `adreno_gpu.h`, undefines framebuffer ROP macros before including generated `a3xx.xml.h`, and is consumed by `a3xx_gpu.c` and `a3xx_catalog.c`.

## Risks
`base` must remain first for `to_a3xx_gpu`. Generated XML naming conflicts are managed by the ROP undef workaround; removing it can create compile breakage depending on include order.

## Test Signals
Compile coverage and successful A3xx probe are the primary signals. Runtime signals include correct OCMEM cleanup through `to_a3xx_gpu` during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a3xx_gpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a4xx_catalog.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a4xx_catalog.c

## Purpose
`a4xx_catalog.c` registers the supported Adreno 4xx devices with static firmware, GMEM, revision, and function-table metadata.

## Important APIs, Types, And Functions
The file defines `a4xx_gpus[]` and publishes it with `DECLARE_ADRENO_GPULIST(a4xx)`. Entries cover A405, A420, and A430, using `ADRENO_CHIP_IDS`, `ADRENO_4XX`, `.revn`, PM4/PFP firmware names, `.gmem`, `.inactive_period`, and `.funcs = &a4xx_gpu_funcs`.

## Control Flow
There is no runtime algorithm. The shared Adreno catalog lookup selects these immutable entries during probe and stores them in the runtime `adreno_gpu`.

## State And Persistence
The table values persist as `adreno_gpu->info` and influence firmware loading, GMEM range setup, register table selection, and helper predicates such as `adreno_is_a405`, `adreno_is_a420`, and `adreno_is_a430`.

## Dependencies And Integration Points
It includes `adreno_gpu.h` and `a4xx_gpu.h`. Runtime code in `a4xx_gpu.c` consumes the revision and GMEM values and depends on the common catalog macros to expose the list.

## Risks
Incorrect catalog metadata will select wrong firmware or runtime workarounds. A405 shares A420 firmware but has a distinct register table and no CCU path, so revision accuracy matters.

## Test Signals
Expected signals are exact chip ID matching, correct firmware request names, correct A405/A420/A430 branch selection in `a4xx_hw_init`, and GMEM sizes matching hardware capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a4xx_catalog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a4xx_gpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a4xx_gpu.c

## Purpose
`a4xx_gpu.c` implements the Adreno 4xx backend. It provides command submission, hardware initialization, hardware clock gating, OCMEM/interconnect setup, power suspend/resume behavior, IRQ handling, state capture, timestamp/busy counters, and function dispatch for A405/A420/A430 GPUs.

## Important APIs, Types, And Functions
The exported table is `a4xx_gpu_funcs`. Major helpers are `a4xx_submit`, `a4xx_enable_hwcg`, `a4xx_me_init`, `a4xx_hw_init`, `a4xx_recover`, `a4xx_destroy`, `a4xx_idle`, `a4xx_irq`, `a4xx_gpu_state_get`, `a4xx_pm_resume`, `a4xx_pm_suspend`, `a4xx_get_timestamp`, `a4xx_gpu_busy`, `a4xx_get_rptr`, and `a4xx_gpu_init`. Register range tables are `a4xx_registers` and `a405_registers`.

## Control Flow
Probe allocates `struct a4xx_gpu`, initializes common Adreno state with one ring, chooses the A405 or general A4xx register dump table, allocates OCMEM, sets a UCHE trap base, obtains `gfx-mem` and optional `ocmem` interconnect paths, and requests maximum bandwidth.

Hardware init writes VBIF tuning per variant, busy/perf/hang-detect registers, GMEM base from OCMEM, CP timestamp counter selection, UCHE trap base, CP debug flags, A430-specific SP register file sleep, hardware clock-gating registers, A420 timing workaround, CP protection ranges, interrupt mask, common Adreno hardware setup, ringbuffer base/control, PM4/PFP firmware uploads, ME enable, and `CP_ME_INIT`. Submit flow is close to A3xx but uses `CP_INDIRECT_BUFFER_PFE` and A4xx write-pointer register, then emits `HLSQ_FLUSH`, idle wait, `CACHE_FLUSH_TS | IRQ`, and ring flush.

## State And Persistence
`struct a4xx_gpu` stores OCMEM metadata. The runtime also persists selected register table, UCHE trap base, ring/fence state, perf counter state, and A430 power-collapse state through PM callbacks. GPU snapshots add `RBBM_STATUS`.

## Dependencies And Integration Points
The file depends on generated A4xx registers, Adreno core helpers, OCMEM helpers, interconnect APIs, ring packet macros, MSM PM/recovery/retire hooks, and catalog-provided `adreno_info`. It integrates with debug/devcoredump through `adreno_show` and state hooks.

## Risks
Clock-gating and power sequences contain hardware errata: A420 HLSQ timing, early A430 SP/TP power-collapse issues, and A405 lacking CCU. Incorrect branching can cause hangs that look like generic CP faults. OCMEM allocation is required here, so cleanup and probe failure paths must stay balanced.

## Test Signals
Signals include successful firmware upload and ME init, command completion via fence writes, A430 suspend/resume toggling `RBBM_POWER_CNTL_IP`, timestamp counter reads increasing, OCMEM GMEM base correctness, protected-register faults reporting address/access, and debug state capture showing `RBBM_STATUS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a4xx_gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a4xx_gpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a4xx_gpu.h

## Purpose
`a4xx_gpu.h` declares the A4xx generation wrapper and function table used by catalog registration and runtime code.

## Important APIs, Types, And Functions
`struct a4xx_gpu` embeds `struct adreno_gpu base` and includes `struct adreno_ocmem ocmem`. `to_a4xx_gpu()` recovers the wrapper from an Adreno base pointer. `a4xx_gpu_funcs` is exported for catalog entries.

## Control Flow
The header has no executable flow. It establishes the static type layout and imports generated A4xx register definitions.

## State And Persistence
The persistent state declared here is the common Adreno object plus optional OCMEM allocation state. Runtime PM, firmware, ring, and register state are in the embedded/common structures.

## Dependencies And Integration Points
It includes `adreno_gpu.h`, applies the ROP macro workaround before `a4xx.xml.h`, and is consumed by `a4xx_gpu.c` and `a4xx_catalog.c`.

## Risks
The `base` field must remain first. Include-order macro conflicts with framebuffer ROP definitions are handled locally and can reappear if generated XML inclusion is moved.

## Test Signals
Build coverage plus successful A4xx probe/teardown are the primary signals, especially OCMEM initialization and cleanup through `to_a4xx_gpu`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a4xx_gpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_catalog.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_catalog.c

## Purpose
`a5xx_catalog.c` defines the static catalog for Adreno 5xx GPUs. It maps chip IDs to firmware, GMEM size, inactive period, quirks, ZAP shader firmware, GPMU firmware where present, and `a5xx_gpu_funcs`.

## Important APIs, Types, And Functions
The file defines `static const struct adreno_info a5xx_gpus[]` and exports it with `DECLARE_ADRENO_GPULIST(a5xx)`. Entries cover A505, A506, A508, A509, A510, A512, A530, and A540. Important metadata fields are `.fw`, `.gmem`, `.inactive_period`, `.quirks`, `.zapfw`, `.revn`, and `.funcs`.

## Control Flow
There is no direct control flow. Shared Adreno discovery matches chip IDs against this array and later runtime code branches on the selected info.

## State And Persistence
Catalog values persist in `adreno_gpu->info`. Quirks drive A5xx runtime workarounds such as two-pass WFI, fault-detect masking, and LMLOADKILL disable. Firmware names control PM4/PFP/GPMU buffer creation and secure ZAP loading.

## Dependencies And Integration Points
It includes `adreno_gpu.h` and `a5xx_gpu.h`. `a5xx_gpu.c` and `a5xx_power.c` consume this metadata for hardware init, GPMU setup, preemption decisions, and secure-mode exit.

## Risks
Wrong quirks or firmware names can produce subtle hangs or secure-world failures. Inactive periods are tuned for power-domain behavior on several parts. A509 intentionally reuses A512 ZAP firmware, and A530/A540 uniquely require GPMU firmware.

## Test Signals
Probe should request expected PM4/PFP/GPMU/ZAP files, select correct GMEM and speed behavior, and apply quirk-dependent register writes. Negative validation should check unsupported chip IDs do not match unintended entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_catalog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_debugfs.c

## Purpose
`a5xx_debugfs.c` provides debugfs inspection and reset controls for A5xx GPUs. It exposes CP PFP, ME, MEQ, and ROQ internal state dumps and a privileged reset path that releases firmware/firmware BOs and forces recovery.

## Important APIs, Types, And Functions
The exported function is `a5xx_debugfs_init`. Debug dump helpers are `pfp_print`, `me_print`, `meq_print`, and `roq_print`, all routed through the generic `show` callback in `a5xx_debugfs_list`. The writable debugfs path is `reset_set`, exposed through `reset_fops`.

## Control Flow
`a5xx_debugfs_init` creates the read-only DRM info files and a writable `reset` file under the DRM minor debugfs root. Read paths use `drm_seq_file_printer`, recover `priv->gpu`, and call the function pointer stored in the info entry. Each print helper writes an indexed debug address register and reads the corresponding data register repeatedly. `reset_set` requires `CAP_SYS_ADMIN`, locks `gpu->lock`, releases PM4/PFP firmware references, unpins and drops PM4/PFP BOs, marks `gpu->needs_hw_init`, runtime-resumes the device, invokes `gpu->funcs->recover`, runtime-suspends, and unlocks.

## State And Persistence
Read paths do not retain state, but they change indexed debug address registers while dumping. Reset mutates firmware pointers, firmware BO pointers, `needs_hw_init`, and hardware state through recovery. The reset file is intentionally privileged but writable by debugfs permissions.

## Dependencies And Integration Points
The file depends on Linux debugfs, DRM debugfs helpers, `drm_printer`, MSM device private data, and A5xx register definitions from `a5xx_gpu.h`. It integrates with A5xx teardown conventions by using the same unpin/put patterns for PM4/PFP BOs.

## Risks
Debug reads touch live indexed hardware registers and can race with GPU activity if used during workload execution. `reset_set` explicitly allows resetting an active GPU for debugging, so users can lose active submissions. Firmware/BO release must remain aligned with `a5xx_destroy` and `a5xx_ucode_load` or reset can leak or double-release resources.

## Test Signals
Signals include debugfs files appearing only when debugfs is enabled, PFP/ME/MEQ/ROQ dumps returning stable formatted rows, non-admin reset writes failing, admin reset forcing firmware reload and recovery without leaks, and no crashes when debugfs is absent or `minor` is NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_gpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_gpu.c

## Purpose
`a5xx_gpu.c` is the main Adreno 5xx runtime backend. It handles ring submission and preemption integration, PM4/PFP firmware BO loading, secure ZAP shader handoff, hardware initialization, interrupts and fault diagnosis, suspend/resume, crashdump-backed state capture, speed-bin setup, MMU fault handling, and function dispatch.

## Important APIs, Types, And Functions
The exported table is `a5xx_gpu_funcs`, and the externally used helpers are `a5xx_flush`, `a5xx_idle`, and `a5xx_set_hwcg`. Major private functions include `a5xx_submit`, `a5xx_submit_in_rb`, `a5xx_me_init`, `a5xx_preempt_start`, `a5xx_ucode_load`, `a5xx_zap_shader_init/resume`, `a5xx_hw_init`, `a5xx_recover`, `a5xx_destroy`, `a5xx_fault_handler`, `a5xx_irq`, `a5xx_pm_resume/suspend`, `a5xx_gpu_state_get`, `a5xx_show`, `a5xx_active_ring`, `a5xx_gpu_busy`, `a5xx_get_rptr`, `check_speed_bin`, and `a5xx_gpu_init`.

## Control Flow
Probe allocates `struct a5xx_gpu`, sets register ranges and leakage defaults, reads speed-bin support, chooses four rings except A510, initializes the common Adreno object, installs the SMMU fault handler, initializes preemption records, copies common UBWC config, and sets the UCHE trap base. Firmware loading creates GPU-addressable PM4/PFP BOs, checks PFP patch level for `CP_WHERE_AM_I`, allocates rptr shadow memory when supported, and disables multi-ring preemption when not.

Hardware init programs VBIF, busy counters, hang masks, perf counters, UCHE trap/write-through/GMEM ranges, queue thresholds, ECO workarounds, HWCG, UBWC highest-bank-bit mode, CP protection ranges, secure-video trust range disable, 64-bit address mode, quirk workarounds, common Adreno init, optional GPMU firmware preparation, PM4/PFP instruction bases, ringbuffer base/control, rptr shadow, preemption hardware state, interrupt mask, ME startup, GPMU/power setup, optional A530 stat event, secure mode exit through ZAP shader or `SECVID_TRUST_CNTL`, and final ring yield.

Submit emits preemption setup packets, IB packets, periodic rptr shadow updates, render-mode reset, fence write via `CACHE_FLUSH_TS | IRQ`, context-switch yield, flush, and preemption trigger. IRQ flow clears safe interrupts first, filters errors if requested, dispatches RBBM/CP/hang/UCHE/GPMU handlers, retires cache-flush fences, and handles CP software preempt completion.

## State And Persistence
`struct a5xx_gpu` owns firmware BOs/IOVAs, GPMU BO/dword count, LM leakage, current/next rings, preemption records, last seqnos, preemption state, rptr shadow BO, and `has_whereami`. Hardware state spans protected mode, secure mode, power domains, HWCG, fault masks, and CP context-switch registers. State capture adds RBBM status and optional HLSQ aperture registers read through a crashdump script.

## Dependencies And Integration Points
The file depends on SCM/ZAP firmware, PM OPP/nvmem speed binning, UBWC config, MSM GEM/VM/MMU APIs, Adreno common helpers, A5xx power and preemption modules, debugfs/devcoredump support, worker recovery, timers, and generated A5xx register definitions. Catalog metadata supplies firmware names, quirks, GMEM, and ZAP/GPMU availability.

## Risks
This file is highly sequencing-sensitive. Firmware patch level controls whether rptr shadows and preemption are safe. Secure-mode exit depends on correct ZAP firmware/device-tree configuration. HWCG and power collapse interact with state capture and PM. `a5xx_submit_in_rb` copies user command buffers into the RB and manually idles/retire, so it is a distinct sudo path. IRQ clearing order must avoid RBBM AHB interrupt storms. Crashdump state capture must not run while stalled on an IOMMU fault.

## Test Signals
Signals include firmware BO creation and naming, `has_whereami` enabling shadow rptr/preemption, successful `a5xx_me_init`, ZAP shader load/resume or expected fallback warning, command fences retiring on cache flush, CP SW preempt interrupts switching rings, RBBM/CP fault logs containing useful addresses, SMMU faults including scratch data, suspend clearing shadows, devfreq busy counter increments, coredump HLSQ registers appearing, and clean teardown of all BOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_gpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_gpu.h

## Purpose
`a5xx_gpu.h` declares the A5xx generation state, preemption record ABI shared with microcode, power/preemption/debugfs entry points, and small helpers used across A5xx source files.

## Important APIs, Types, And Functions
`struct a5xx_gpu` embeds `adreno_gpu` and stores PM4/PFP/GPMU firmware BOs, LM leakage, current/next ring, per-ring preemption BOs/records/IOVAs/counters, last seqnos, atomic preempt state, preempt lock/timer, rptr shadow BO, and `has_whereami`. `enum preempt_state` defines the software state machine. `struct a5xx_preempt_record` is the microcode-visible record. Exports include `a5xx_gpu_funcs`, `a5xx_power_init`, `a5xx_gpmu_ucode_init`, `a5xx_idle`, `a5xx_set_hwcg`, `a5xx_preempt_*`, and `a5xx_flush`.

## Control Flow
The header has no executable control flow except inline helpers. `spin_usecs` polls a register for a masked value with microsecond delays, `shadowptr` computes per-ring rptr shadow IOVA, and `a5xx_in_preempt` reports whether the atomic state is outside normal/abort.

## State And Persistence
This header defines most persistent A5xx runtime state. Preemption records are 64 KiB each plus a separate counter block; the CPU fills fields such as `magic`, `cntl`, `wptr`, `rptr_addr`, `rbase`, and `counter`, while CP firmware saves/restores additional hidden record content.

## Dependencies And Integration Points
It includes `adreno_gpu.h` and generated `a5xx.xml.h`. It links `a5xx_gpu.c`, `a5xx_power.c`, `a5xx_preempt.c`, and optionally `a5xx_debugfs.c`. The record format is an ABI with A5xx PM4/PFP microcode.

## Risks
Changing `struct a5xx_preempt_record` layout, record size, or magic breaks CP preemption. Memory barriers around `preempt_state` are required because IRQ and submit paths inspect it concurrently. `shadowptr` assumes a compact per-ring u32 shadow array.

## Test Signals
Compile coverage plus multi-ring preemption tests are primary. Runtime signals include valid preempt record magic, successful `spin_usecs` waits in power paths, correct rptr shadow updates, and clean preempt resource free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_gpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_power.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_power.c

## Purpose
`a5xx_power.c` programs A5xx GPMU, limits management, thermal/power configuration, and GPMU firmware upload command buffers for A530/A540-class GPUs.

## Important APIs, Types, And Functions
Exported functions are `a5xx_power_init` and `a5xx_gpmu_ucode_init`. Private helpers include `_get_mvolts`, `a530_lm_setup`, `a540_lm_setup`, `a5xx_pc_init`, `a5xx_gpmu_init`, and `a5xx_lm_enable`. Static data includes the A530 sequence register table and AGC/GPMU message offsets.

## Control Flow
`a5xx_gpmu_ucode_init` validates GPMU firmware format, checks firmware ID 2, extracts the command stream region, creates a GPU-readonly BO, and writes a sequence of type4 packets that load instruction RAM in chunks bounded by `TYPE4_MAX_PAYLOAD`. `a5xx_power_init` exits on chips without GPMU, runs A530 or A540 limits-management setup, initializes SP/TP power collapse registers, calls `a5xx_gpmu_init`, then enables LM interrupts/throttling for A530.

`a5xx_gpmu_init` submits the prepared GPMU firmware BO as an indirect buffer with protected mode disabled, waits for idle, optionally programs A530 WFI config, releases CM3 reset, and polls `GPMU_GENERAL_0` for the `BABEFACE` handshake. A540 also checks `GPMU_GENERAL_1` for firmware failure.

## State And Persistence
Persistent state is stored in `a5xx_gpu->gpmu_bo`, `gpmu_iova`, `gpmu_dwords`, and `lm_leakage`. Hardware state includes AGC message RAM, power-collapse controls, voltage/frequency payloads derived from OPP data, thermal sensor configuration, GPMU interrupt masks, and throttle controls.

## Dependencies And Integration Points
The file depends on PM OPP APIs for voltage lookup, A5xx register definitions, ring packet macros through `a5xx_gpu.h`, common firmware data in `adreno_gpu->fw[ADRENO_FW_GPMU]`, and `a5xx_flush`/`a5xx_idle` from the runtime file.

## Risks
Firmware parsing is intentionally conservative; invalid firmware silently disables GPMU microcode preparation. Power setup is only implemented for A530/A540 and uses hardcoded thresholds. If the GPMU handshake times out, the code logs but does not always fail hard, so advanced power behavior may be absent while the GPU remains usable. The IB upload must run with protected mode disabled and then restored.

## Test Signals
Signals include `gpmufw` BO creation, nonzero `gpmu_dwords`, successful type4 command construction, `GPMU_GENERAL_0 == 0xBABEFACE`, no nonzero A540 failure code, voltage payload matching OPP data, A530 LM interrupts configured, and GPU workloads remaining stable across power collapse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_preempt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_preempt.c

## Purpose
`a5xx_preempt.c` implements A5xx multi-ring hardware preemption. It allocates per-ring preemption records, maintains a lockless atomic state machine, chooses the highest-priority runnable ring, triggers CP context switches, handles completion interrupts, and recovers from timeouts.

## Important APIs, Types, And Functions
Exported functions are `a5xx_preempt_init`, `a5xx_preempt_fini`, `a5xx_preempt_hw_init`, `a5xx_preempt_trigger`, and `a5xx_preempt_irq`. Private helpers include `try_preempt_state`, `set_preempt_state`, `update_wptr`, `get_next_ring`, `a5xx_preempt_timer`, and `preempt_init_ring`.

## Control Flow
Initialization exits for single-ring GPUs. For each ring it allocates a privileged preempt record BO plus an unprivileged counter BO, names them, fills the record magic, default RB control, and counter IOVA, then initializes the start lock and watchdog timer. Hardware init resets current ring to ring 0, initializes per-ring record fields with ring base and rptr shadow addresses, writes zero SMMU switch info, and sets state to `PREEMPT_NONE`.

Trigger flow serializes with `preempt_start_lock`, atomically moves `NONE` to `START`, finds the first non-empty ring, aborts back to `NONE` if no switch is needed while updating current WPTR, or records the incoming ring WPTR, writes restore record address, sets `next_ring`, arms a 10-second watchdog, sets `TRIGGERED`, and writes `CP_CONTEXT_SWITCH_CNTL`. IRQ flow moves `TRIGGERED` to `PENDING`, deletes the timer, verifies hardware cleared switch control, updates `cur_ring`, writes the new WPTR, returns to `NONE`, and retriggers to catch queued work.

## State And Persistence
Persistent state lives in `struct a5xx_gpu`: per-ring preempt/counter BOs, record pointers, IOVAs, current/next rings, atomic preempt state, start lock, and timer. Records persist across switches and are shared with CP microcode.

## Dependencies And Integration Points
The file depends on MSM GEM kernel BO helpers, ringbuffer locking and memptrs, `gpu->funcs->get_rptr`, A5xx context-switch registers, and the GPU worker recovery path. `a5xx_gpu.c` calls preempt init, hardware init, trigger on submit/retire, IRQ handler on CP_SW, and fini during destroy.

## Risks
Concurrency is the main risk. Submit and IRQ paths can race with preemption state, so barriers and the `PREEMPT_ABORT` intermediate state are important. A stuck hardware switch queues recovery through the watchdog. If `WHERE_AM_I` shadow support is absent, multi-ring preemption is disabled by the firmware load path. Resource allocation failure degrades to one ring.

## Test Signals
Signals include four-ring GPUs allocating records, ring priority switching under mixed workloads, CP_SW interrupts completing switches, watchdog recovery on forced timeout, no WPTR loss when submit races with abort, valid preempt counters, and clean fallback to one ring on allocation or firmware capability failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_preempt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_catalog.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_catalog.c

## Purpose
`a6xx_catalog.c` is the large static catalog for modern Adreno generations driven by the A6xx-family runtime stack. It describes A6xx, A7xx, and A8xx GPUs, including chip IDs, firmware, GMEM sizes, function tables, quirks, ZAP firmware, speed bins, hardware clock-gating lists, CP protection ranges, GBIF settings, GMU settings, power-up/IFPC register lists, BCM bus votes, pipe-scoped register lists, and preemption record sizes.

## Important APIs, Types, And Functions
The file defines multiple immutable data families: HWCg reglists such as `a612_hwcg`, `a615_hwcg`, `a620_hwcg`, `a630_hwcg`, `a640_hwcg`, `a650_hwcg`, `a660_hwcg`, `a690_hwcg`, `a702_hwcg`, `a730_hwcg`, and `a740_hwcg`; protection lists `a630_protect`, `a650_protect`, `a660_protect`, `a690_protect`, `a730_protect`, `x285_protect`, and `a840_protect`; GBIF lists `a640_gbif` and `a840_gbif`; reglist descriptors such as `a7xx_pwrup_reglist`, `a750_ifpc_reglist`, `a7xx_dyn_pwrup_reglist`, `a840_pwrup_reglist`, `a840_ifpc_reglist`, `x285_dyn_pwrup_reglist`, and `a840_dyn_pwrup_reglist`; non-context register lists for A8xx; and catalog arrays `a6xx_gpus`, `a7xx_gpus`, and `a8xx_gpus` exported with `DECLARE_ADRENO_GPULIST`.

## Control Flow
The file has no active runtime algorithm besides compile-time build assertions. At probe time the common catalog machinery matches chip IDs and machine constraints, then stores the selected `struct adreno_info`. A6xx/A7xx/A8xx runtime code consumes nested `struct a6xx_info` pointers to program HWCg, CP protection, GMU CGC mode/chipid, GBIF CX registers, prim FIFO thresholds, IFPC save/restore lists, dynamic pipe register lists, and bus bandwidth channels.

## State And Persistence
All tables are read-only. Their values persist indirectly through `adreno_gpu->info` and nested `a6xx_info`. Because many entries use compound literals for `struct a6xx_info` and BCM arrays, the catalog is the single source for per-SKU hardware policy.

## Dependencies And Integration Points
The file depends on `adreno_gpu.h`, `a6xx_gpu.h`, generated A6xx/A6xx GMU register headers, catalog macros for GPU lists/protection/reglists, and runtime function tables including `a6xx_gpu_funcs`, `a6xx_gmuwrapper_funcs`, `a7xx_gpu_funcs`, and `a8xx_gpu_funcs`. Firmware names cover SQE, GMU, and AQE slots.

## Risks
Catalog correctness is critical and easy to regress. Wrong HWCg/protect lists can cause hangs, security exposure, or inaccessible perf/debug registers. Several entries share chip IDs but distinguish machines or speed bins, so ordering and metadata matter. A7xx/A8xx pipe-scoped lists and IFPC lists must match runtime save/restore expectations. Build assertions only check protection list capacity, not semantic correctness.

## Test Signals
Signals include every listed chip ID probing to the intended function table, firmware requests matching the SKU, speed-bin mapping selecting supported OPPs, HWCg/protect/GBIF lists programming without CP protection faults, IFPC resume restoring listed registers, preemption record allocations matching catalog sizes, BCM votes appearing for SH0/MC0/ACV where declared, and `BUILD_BUG_ON` not firing for protection list counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_catalog.c -->
