# subset-b-003645 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gmu.c

## Purpose

`a6xx_gmu.c` implements the GMU side of the Adreno A6xx/A7xx/A8xx GPU driver: firmware loading, HFI startup, RPMh vote construction, runtime power transitions, OOB handshakes, GMU memory allocation, IRQ handling, and GMU device binding. The GMU owns most GPU power-management decisions on full-GMU targets; wrapper/RGMU targets use a reduced path where Linux still maps GMU registers and power domains but skips firmware/HFI allocation.

## Important APIs, Types, And Functions

- `a6xx_gmu_resume()` and `a6xx_gmu_stop()` are the runtime PM entry points used by `a6xx_gpu.c`.
- `a6xx_gmu_set_freq()` translates GPU OPPs into GMU performance and bandwidth indices, sends either HFI frequency messages or legacy DCVS OOB requests, and updates `gmu->freq` plus `current_perf_index`.
- `a6xx_gmu_set_oob()` and `a6xx_gmu_clear_oob()` perform the CPU-to-GMU out-of-band handshake for boot/slumber, GPU critical sections, DCVS, and perfcounter/sysprof blocking.
- `a6xx_gmu_fw_start()` is the boot sequence coordinator. It starts RPMh, loads firmware on cold boot, programs HFI queue base, AHB fence ranges, chip id/log buffer registers, CX GBIF settings, idle policy, CM3 startup, legacy GX rail, SPTPRAC, and HFI queue control.
- `a6xx_gmu_init()` and `a6xx_gmu_wrapper_init()` bind the GMU platform device, configure DMA, map registers, attach power domains, allocate GMU buffers, install IRQs, probe OPP/RPMh votes, and initialize HFI queues.
- `a6xx_gmu_memory_alloc()` creates WC GEM BOs in the GMU VM, optionally at fixed IOVAs for firmware cache/dummy/debug regions.
- `a6xx_gmu_rpmh_votes_init()`, `a6xx_gmu_rpmh_arc_votes_init()`, `a6xx_gmu_rpmh_bw_votes_init()`, and `a6xx_gmu_pwrlevels_probe()` derive GMU/GX/CX ARC votes and DDR BCM votes from OPP tables and command-db data.
- `a6xx_gmu_fault()`, `a6xx_gmu_irq()`, and `a6xx_hfi_irq()` convert GMU watchdog, firmware fault, AHB bus, and fence errors into normal GPU recovery work.

## Control Flow

Initialization starts from `a6xx_gmu_init()`. The function finds the GMU platform device from the DT phandle, enables runtime PM, probes GMU clocks, creates a GMU-only `drm_gpuvm`, allocates fixed and dynamic BOs for dummy pages, debug memory, icache/dcache, log, and HFI queues, maps GMU MMIO and RSCC, requests disabled-by-default IRQs, attaches CX/GX power domains, obtains optional QMP/AOSS, builds OPP and RPMh vote tables, probes ACD, initializes HFI queue descriptors, initializes PDC/RSCC sleep sequences, and marks the GMU initialized. `a6xx_gmu_wrapper_init()` takes a shorter path for GMU wrapper/RGMU devices: map registers, attach domains, fetch clocks, mark legacy for manual SPTPRAC, and skip HFI/firmware memory.

Resume is serialized by `gmu->lock` in `a6xx_gpu.c`. `a6xx_gmu_resume()` powers the GMU device and GX domain, sets conservative GMU/hub clock rates, enables clocks, performs secure-world initialization for newer parts, reads A8xx slice info, applies initial bandwidth, unmasks/enables GMU IRQ, decides warm versus cold boot from retention state, calls `a6xx_gmu_fw_start()`, starts HFI, enables firmware fault IRQ, and finally applies the current GPU frequency. If any boot stage fails, it disables IRQs/clocks and releases runtime PM refs.

Suspend goes through `a6xx_gmu_stop()`. If the GMU is responsive, `a6xx_gmu_shutdown()` performs any missing dummy GPU OOB handshake, releases perfcounter OOB, waits for the target idle level, halts the bus as needed, tells firmware to slumber, waits for GMU not busy, stops HFI, disables IRQs, and asks RPMh/RSCC to power off. If hung or timed out, `a6xx_gmu_force_off()` disables keepalive, flushes HFI, masks IRQs, disables SPTPRAC, asserts GEMNoC workaround, waits for outstanding RPMh TCS votes, opens the AHB fence, halts CM3, halts buses, asserts GPU SW reset, and runs the RPMh stop path.

## State And Persistence Behavior

Persistent GMU state lives in `struct a6xx_gmu`: MMIO/RSCC mappings, IRQ numbers, power domains, GMU VM, BOs for HFI/debug/icache/dcache/dummy/log, clock handles, OPP-derived frequency/bandwidth tables, ARC and BCM vote arrays, HFI queue descriptors, ACD table, QMP handle, current frequency/perf index, `idle_level`, and status bits. `GMU_STATUS_FW_START` and `GMU_STATUS_PDC_SLEEP` coordinate RSCC/PDC sleep transitions; `GMU_STATUS_OOB_PERF_SET` tracks sysprof's perfcounter OOB vote; `GMU_STATUS_SECURE_INIT` prevents repeated secure init.

Firmware persistence is split by target generation. Legacy GMUs load a flat image into ITCM and use OOB for boot/slumber and DCVS. Newer GMUs parse block headers from firmware and place blocks into ITCM, DTCM, icache, dcache, or dummy BOs. Warm boot only applies where retention state is known safe; newer A6xx forces cold boot because external cache regions must be restored.

## Dependencies And Integration Points

This file depends on DRM GEM and msm GEM/VM helpers, Adreno firmware arrays, HFI helpers from `a6xx_hfi.*`, register XML headers, Linux OPP/devfreq, runtime PM, generic power domains, Qualcomm SCM, QMP/AOSS, command-db, TCS/RPMh, clocks, IRQs, and platform resources named `gmu_pdc`, `gmu_pdc_seq`, `rscc`, and GMU core memory. It is consumed by `a6xx_gpu.c` through PM callbacks, frequency callbacks, hardware init OOB sections, sysprof setup, fault recovery, crash-state GMU snapshots, and `gx_is_on` tests.

## Risks And Edge Cases

- OOB requests require `gmu->lock`; callers that violate the lock contract risk racing firmware state or losing ack/clear ordering.
- Firmware block parsing trusts the firmware's block walk enough to iterate until image end; bad block sizes or addresses only log unmatched blocks, so malformed firmware can produce partial state.
- Runtime PM reference handling spans GMU device, GX domain, CX domain links, clocks, and OPPs. Error paths must remain balanced, especially around `pm_runtime_put(gmu->gxpd)` where `gxpd` may be optional on some paths.
- Forced-off recovery writes registers while the hardware may be partially collapsed; barriers, fence allow mode, bus halt, and reset ordering are critical.
- RPMh/command-db data and OPP `level`/bandwidth properties must match DT. Missing levels fail probe or leave GMU unable to vote the intended corners.
- Sysprof uses `GMU_OOB_PERFCOUNTER_SET` to block IFPC while performance counter select registers are meaningful. Missed clear leaves extra power residency; missed set loses counters through IFPC.
- Generation conditionals are dense. A6xx legacy, A650/A660, A7xx, A8xx, wrapper, and RGMU paths use different registers and firmware assumptions.

## Test Signals

Useful validation signals include successful probe with GMU BO allocation names visible, boot logs showing GMU firmware version, runtime suspend/resume cycles without GMU watchdog or HFI fault IRQs, devfreq transitions changing `gmu->freq`, OPP/command-db failures absent, sysprof toggling perfcounter OOB without timeout, GPU hang recovery completing with CX collapse, and devcoredumps containing GMU log/HFI/debug buffers. Kernel logs to watch are "GMU firmware initialization timed out", "Unable to start the HFI queues", "Timeout waiting for GMU OOB set", "Unable to power off the GPU RSC", "GMU watchdog expired", and ACD/QMP errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gmu.h

## Purpose

`a6xx_gmu.h` defines the public GMU data model and low-level MMIO helpers used by the A6xx/A7xx/A8xx Adreno driver. It describes GMU BOs, bandwidth-manager metadata, boot and idle-state constants, the `struct a6xx_gmu` state container, register access wrappers, OOB request IDs, and function prototypes shared with GPU, HFI, preemption, and crash-state code.

## Important APIs, Types, And Functions

- `struct a6xx_gmu_bo` stores a GMU-visible GEM object, CPU virtual mapping, size, and IOVA.
- `struct a6xx_bcm` describes a Bus Clock Manager used to construct RPMh DDR interconnect votes.
- `struct a6xx_gmu` is the central persistent object embedded in `struct a6xx_gpu`.
- `GMU_WARM_BOOT` and `GMU_COLD_BOOT` identify firmware boot mode.
- `GMU_IDLE_STATE_ACTIVE`, `GMU_IDLE_STATE_SPTP`, and `GMU_IDLE_STATE_IFPC` define how much low-power control firmware owns.
- `gmu_read()`, `gmu_write()`, `gmu_write_bulk()`, `gmu_rmw()`, `gmu_read64()`, `gmu_poll_timeout()`, and RSCC variants abstract register offsets based on the GPU register base.
- `enum a6xx_gmu_oob_state` names direct CPU-to-GMU requests: boot/slumber, GPU critical-section, DCVS, and perfcounter.
- Exported prototypes cover HFI init/start/stop/frequency, GX/SPTP status, SPTPRAC control, GMU resume/stop/init/remove, OOB operations, sysprof setup, and GMU wait-idle.

## Control Flow

The header is not executable control flow, but it encodes the contracts the C files follow. GMU users obtain a pointer from `to_a6xx_gpu(adreno_gpu)->gmu`, serialize state-changing firmware communication with `gmu->lock`, access registers through helpers that subtract `mmio_offset`, and select OOB request/ack/clear bits in `a6xx_gmu.c` from `enum a6xx_gmu_oob_state`. The HFI code owns queue contents but stores queue descriptors inside `gmu->queues`. Crash-state code reads `gmu->initialized`, `gmu->log`, `gmu->hfi`, `gmu->debug`, and register helpers to snapshot state safely.

## State And Persistence Behavior

`struct a6xx_gmu` persists across runtime PM cycles and stores:

- Device and locking state: `dev`, `lock`, `initialized`, `hung`, `legacy`, `status`.
- Addressing: `vm`, `mmio`, `mmio_offset`, `rscc`.
- IRQs and power domains: `hfi_irq`, `gmu_irq`, `gxpd`, `cxpd`, `pd_nb`, `pd_gate`.
- Firmware and diagnostic memory: `hfi`, `debug`, `icache`, `dcache`, `dummy`, `log`.
- Clocks and performance: clock bulk, core/hub clocks, current perf index, GPU/GMU frequency tables, bandwidth table, ARC/BCM vote arrays, ACD table, current `freq`.
- HFI and AOSS: HFI queues, QMP handle, optional HFI bandwidth table.

The header's `status` bit definitions are persistent software bookkeeping, not hardware registers. They coordinate PDC sleep, firmware startup, sysprof OOB, and one-time secure initialization.

## Dependencies And Integration Points

The header includes Linux completion, polling, interrupt, notifier, and QMP types, plus msm DRM, Adreno GPU, and A6xx HFI headers. It exposes GMU helpers to `a6xx_gmu.c`, `a6xx_gpu.c`, `a6xx_gpu_state.c`, and A8xx-related code. Register constants come from XML-generated headers included by implementation files, so helper callers pass dword register offsets rather than byte offsets.

## Risks And Edge Cases

- `GMU_BYTE_OFFSET()` assumes the caller passes GPU-base dword offsets and that `mmio_offset` was derived correctly from platform resources. Incorrect resource layout causes silent wrong MMIO access.
- `gmu_write_bulk()` receives `size` in bytes but writes to an IO pointer computed from dword register offset; callers must pass firmware block sizes correctly and maintain alignment.
- `gmu_poll_timeout*` macros directly evaluate conditions on MMIO reads; callers must choose atomic versus sleepable variants based on IRQ/runtime context.
- `struct a6xx_gmu` combines wrapper, legacy, full GMU, A7xx, and A8xx state. Code must check `initialized`, `legacy`, `adreno_has_gmu_wrapper()`, and `adreno_has_rgmu()` before assuming HFI/firmware buffers exist.
- OOB enum values are ABI-like inside the driver. Reordering without updating the bit table in `a6xx_gmu.c` would break firmware handshakes.

## Test Signals

Header-level issues surface as build failures, sparse/type warnings, bad MMIO offsets, OOB timeout logs, crash-state NULL dereferences, or runtime PM imbalance. Useful checks include building with `CONFIG_DRM_MSM_GPU_STATE`, booting wrapper and full-GMU targets, reading GMU state after suspend/resume, and exercising sysprof/perfcounter paths that require the `GMU_STATUS_OOB_PERF_SET` bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu.c

## Purpose

`a6xx_gpu.c` is the main Adreno A6xx-family GPU implementation. It binds the GPU object, loads SQE/AQE firmware, initializes registers and CP state, emits command streams for A6xx and A7xx/A8xx submissions, manages runtime PM through the GMU, handles IRQs/faults/recovery, configures LLCC/system cache, performs bus halt/reset operations, exposes devfreq hooks, and registers the `adreno_gpu_funcs` tables for A6xx, wrapper, A7xx, and A8xx variants.

## Important APIs, Types, And Functions

- `a6xx_gpu_init()` allocates `struct a6xx_gpu`, detects GMU wrapper mode, initializes LLCC and supported OPP hardware, initializes the generic Adreno core, binds GMU, installs MMU fault handling, computes UBWC config, and initializes preemption.
- `a6xx_hw_init()` wraps `hw_init()` with `gmu->lock`. `hw_init()` programs GBIF/VBIF, security, address modes, HWCG, QoS, UCHE/GMEM, CP mempool, performance counters, UBWC, fault detection, CP protection, APRIV, interrupts, SQE/RB registers, preemption, CP init, and secure-mode exit.
- `a6xx_submit()` emits A6xx ring commands for pagetable switch, stats capture, IB execution, scratch fence, cache flush timestamp, trace, and flush.
- `a7xx_submit()` emits the generation 7 path with BR/BV thread control, IFPC markers, optional pseudo-reg/preemption state, BV fence synchronization, command-completion yield, and preempt trigger.
- `a6xx_set_pagetable()` emits SMMU table update packets and UCHE/perfcounter synchronization when a submit's context changes.
- `a6xx_flush()` updates shadow read pointers, updates ring `cur`, and fenced-writes `CP_RB_WPTR` if the ring is active and not currently preempting.
- `a6xx_irq()` decodes RBBM interrupts, keeps GMU alive while reading/clearing status, handles faults, CP errors, SW fuse violations, retirements, and preemption IRQs.
- `a6xx_recover()` coordinates crash recovery with runtime PM and CX power collapse.
- `a6xx_gmu_pm_resume()/suspend()` and `a6xx_pm_resume()/suspend()` implement full GMU and wrapper PM paths.
- `a6xx_gpu_busy()`, `a6xx_gpu_set_freq()`, `a6xx_get_rptr()`, and `a6xx_progress()` implement devfreq and scheduler integration.

## Control Flow

Probe calls `a6xx_gpu_init()` through the selected `adreno_gpu_funcs`. It allocates the object, initializes locks, reads the `qcom,gmu` phandle, initializes LLCC slices before OPP filtering, enables up to four rings if preemption is allowed, runs generic Adreno init, records speedbin, initializes the GMU full or wrapper path, installs the MMU fault handler, calculates UBWC settings, and sets up preemption records.

Runtime resume begins in the function table PM callback. Full GMU targets call `a6xx_gmu_resume()` under `gmu->lock`, resume devfreq, and activate LLCC slices. Wrapper targets set OPP/clock/domain state directly. The first submit or explicit core path later calls `a6xx_hw_init()`, which holds `GMU_OOB_GPU_SET` on full GMU targets so firmware does not power-collapse registers while Linux programs the GPU. The sequence ends by yielding preemption state, clearing OOB votes, and optionally setting perfcounter OOB for sysprof.

Submissions are ringbuffer packet construction. Both submit paths switch pagetables only when context sequence changes, write performance counters to memstore, emit user IBs while periodically updating shadow RPTR visibility, write a seqno fence, emit cache-clean/flush timestamp events, trace, and flush the ring. A7xx/A8xx adds BR/BV threading and separate BV fence wait so BR does not signal completion before BV finishes.

IRQs use `a6xx_gpu_keepalive_vote()` and `irq_poll_fence()` before reading `RBBM_INT_0_STATUS`. Hang-detect interrupts queue recovery after disabling GPU interrupts and deleting hangcheck. Cache flush timestamp retires completed submits and may trigger preemption. CP software interrupts service preemption completion. Severe CP and fuse errors log details and can queue recovery.

Recovery dumps Adreno info, halts SQE if GX is on, optionally dumps registers, marks the GPU hung, disables autosuspend, temporarily zeros active submit count, forces wrapper/RGMU bus halt and reset, asks genpd to power off CX, drops runtime PM refs to collapse hardware, waits for `pd_gate`, restores active submit count, resumes runtime PM, reinitializes hardware, and clears `hung`.

## State And Persistence Behavior

`struct a6xx_gpu` stores SQE/AQE BOs and IOVAs, current/next ring pointers, per-ring preemption records and SMMU info, last seqnos, preemption state/timer/locks, postamble BO, embedded `struct a6xx_gmu`, shadow RPTR BO, A7xx power-up reglist BO, LLCC state, hang flags, aperture state, and A8xx slice mask. BOs live across runtime suspend and are released in `a6xx_destroy()`. Runtime suspend clears shadow RPTR memory so ring state is re-established on next init.

Hardware state is mostly volatile and rebuilt by `hw_init()` after GMU resume or recovery. `pwrup_reglist_emitted` prevents regenerating A7xx power-up register lists after the initial capture. `cur_ring`, ring `cur_ctx_seqno`, `last_cp_state`, and `last_seqno` track scheduler/preemption progress.

## Dependencies And Integration Points

This file integrates with the DRM msm GPU scheduler, GEM/VM helpers, Adreno common code, generated register/enumeration/perfcounter headers, GMU/HFI code, preemption helpers, A8xx helpers, Linux OPP/devfreq, runtime PM, power domains, LLCC, IOMMU page-table code, UBWC common config, zap shader secure firmware, SCM-secure initialization through GMU code, and crash-state callbacks under `CONFIG_DRM_MSM_GPU_STATE`.

## Risks And Edge Cases

- Fenced register writes must work when GMU/IFPC can power-collapse GX. Timeouts around `GMU_AHB_FENCE_STATUS` can leave RB write pointers stale.
- `hw_init()` is a long generation-specific register script. Small ordering mistakes can break secure mode, CP init, IFPC, UBWC, or preemption.
- A7xx BR/BV synchronization is subtle; missing thread control or BV fence wait can signal completion before all work is done.
- Recovery manipulates runtime PM and `active_submits` intentionally. Imbalance can deadlock suspend, skip CX collapse, or lose active-submit refs.
- `a6xx_progress()` lies when IFPC is enabled because GX registers cannot be read safely. Hang detection hardware must be trusted in that mode.
- Firmware version gating rejects old SQE images on A630/A650. Unknown firmware names currently fail with `-EPERM`.
- Wrapper/full GMU function tables differ in PM and timestamp behavior; selecting the wrong table breaks clocks, OPP voting, or GMU firmware expectations.

## Test Signals

Important signals are successful SQE/AQE BO creation, CP init returning idle, zap shader success or expected `-ENODEV` fallback, working suspend/resume, ring fences retiring, preemption on multi-ring workloads, no fenced-write timeout logs, no CP protected mode/opcode errors, GPU busy counters changing under load, devfreq frequency changes, MMU faults reporting useful block names, recovery completing and resuming submissions, and devcoredump support calling `a6xx_gpu_state_get()` without wedging the GPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu.h

## Purpose

`a6xx_gpu.h` defines the private A6xx-family GPU object, generation-specific static data descriptors, preemption structures, CP protection macros, helper accessors, and function prototypes shared by GMU, GPU, preemption, A8xx, and crash-state code.

## Important APIs, Types, And Functions

- `struct cpu_gpu_lock` is the shared A7xx power-up/preemption register-list lock and list descriptor consumed by CP firmware.
- `struct a6xx_info` carries per-GPU tables from the Adreno device database: HWCG, CP protect ranges, power-up reglists, dynamic reglists, IFPC reglists, GBIF CX setup, non-context reglists, slice limits, GMU chip id/cgc mode, primitive FIFO threshold, and BCM vote metadata.
- `struct a6xx_gpu` extends `struct adreno_gpu` with firmware BOs, ring/preemption state, embedded GMU, shadow RPTR storage, A7xx power-up reglist storage, LLCC state, hang flags, aperture state, and slice mask.
- `enum a6xx_preempt_state` defines the lockless preemption state machine.
- `struct a6xx_preempt_record` and `struct a7xx_cp_smmu_info` define GPU-visible records used by CP save/restore and A7xx SMMU context programming.
- `A6XX_PROTECT_NORDWR()` and `A6XX_PROTECT_RDONLY()` encode CP_PROTECT register spans.
- `to_a6xx_gpu()`, `a6xx_has_gbif()`, LLCC read/write helpers, `shadowptr()`, and `a6xx_in_preempt()` are inline helpers used in hot paths.
- Function prototypes expose GMU lifecycle, preemption, frequency, state capture/show, bus halt, reset, fenced writes, flush, zap shader, A8xx hooks, and function tables.

## Control Flow

The header shapes cross-file control by embedding `struct a6xx_gmu` inside `struct a6xx_gpu`, making GMU and GPU lifecycle mutually aware. `a6xx_gpu.c` fills the fields during init, `a6xx_preempt.c` owns preemption setup and transitions, `a6xx_gmu.c` owns GMU subfields, and `a6xx_gpu_state.c` snapshots fields and BOs. The function tables declared here are selected by Adreno info entries and determine which PM, submit, IRQ, busy, timestamp, and fault-handler paths execute at runtime.

## State And Persistence Behavior

Most fields in `struct a6xx_gpu` persist for the lifetime of the DRM GPU object. Firmware BOs, preemption records, SMMU records, shadow RPTR BO, postamble, and pwrup reglist are GPU-addressable allocations that survive suspend. `cur_ring`, `next_ring`, `last_seqno`, `preempt_state`, and `hung` reflect volatile execution and recovery state. `cached_aperture` plus `aperture_lock` coordinate register aperture selection for code that needs host access to per-pipe/per-cluster registers. `slice_mask` stores A8xx slice information discovered by A8xx-specific helpers.

## Dependencies And Integration Points

The header includes Adreno core definitions, generated A6xx/A7xx enum/perfcounter/register headers, and `a6xx_gmu.h`. It is included by GMU, GPU, preemption, A8xx, and GPU-state implementations. It exports `a6xx_gpu_funcs`, `a6xx_gmuwrapper_funcs`, `a7xx_gpu_funcs`, and `a8xx_gpu_funcs`, which are the integration contract with common Adreno probe code.

## Risks And Edge Cases

- `a6xx_in_preempt()` relies on memory barriers around `atomic_read()` so flush paths do not race preemption transitions. Weakening this can cause RB writes to the wrong ring or missed restore.
- Preemption record sizes are firmware contracts. `PREEMPT_RECORD_SIZE()` must match device info or CP save/restore can overwrite adjacent memory.
- `struct cpu_gpu_lock` packs list lengths in alternate layouts; A7xx CP firmware expects those fields and the following `regs` array exactly.
- `a6xx_has_gbif()` special-cases A630. Incorrect generation detection changes bus halt, debug dump, and QoS register paths.
- Function prototypes include A8xx hooks implemented elsewhere. Build configs and function tables must stay consistent with available symbols.

## Test Signals

Build coverage is the first signal: this header participates in multiple C files and generated-register dependencies. Runtime signals include working preemption state transitions, correct ring shadow pointers, successful A7xx power-up reglist behavior after IFPC/preemption, valid LLCC programming on MMU500 and non-MMU500 systems, and crash-state output that can interpret A6xx/A7xx struct-backed tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu_state.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu_state.c

## Purpose

`a6xx_gpu_state.c` implements A6xx/A7xx GPU crash-state capture and printing. It gathers generic Adreno state, GMU registers and buffers, CP indexed registers, main GPU register ranges, shader/debug memories, clusters, DBGAHB ranges, debugbus blocks, HFI queue history, and then emits a YAML-like devcoredump through `a6xx_show()`.

## Important APIs, Types, And Functions

- `struct a6xx_gpu_state` extends `struct msm_gpu_state` with arrays of captured GMU registers, GPU registers, shader blocks, clusters, DBGAHB clusters, indexed registers, debugbus blocks, GMU BO snapshots, HFI history, allocation list, and `gpu_initialized`.
- `struct a6xx_gpu_state_obj` pairs a static table handle with captured dword data and optional runtime count.
- `a6xx_gpu_state_get()` is the capture entry point used by the GPU function table.
- `a6xx_gpu_state_put()` releases state through kref.
- `a6xx_show()` prints all captured data.
- `a6xx_crashdumper_init()` and `a6xx_crashdumper_run()` allocate a 1 MiB GPU scratch BO, write a CP crashdump script, run it, and copy results.
- `a6xx_get_registers()` and `a7xx_get_registers()` capture normal register ranges via AHB or crashdumper depending on SMMU/fault state.
- `a6xx_get_shaders()/a7xx_get_shaders()`, `a6xx_get_clusters()/a7xx_get_clusters()`, and DBGAHB helpers capture deeper block state through CP apertures.
- `a6xx_get_gmu_registers()`, `a6xx_snapshot_gmu_bo()`, and `a6xx_snapshot_gmu_hfi_history()` preserve GMU-side diagnostics.
- Debugbus helpers collect GX, CX, and VBIF/GBIF debugbus data when the global `snapshot_debugbus` option is active.

## Control Flow

`a6xx_gpu_state_get()` allocates state, initializes the owned allocation list, and calls `adreno_gpu_state_get()` first. On full GMU targets it snapshots GMU CX/RSCC/GPUCC/GX registers, GMU log/HFI/debug BO contents, and HFI queue history before checking GX state. If GX is off, it returns a GMU-only plus generic snapshot.

If GX is on, it halts SQE with `CP_SQE_CNTL = 3`, captures indexed CP registers, detects SMMU stalled-on-fault state, and only initializes the crashdumper if the SMMU is not stalled and hardware is initialized. This distinction matters because the crashdumper needs GPU memory writes, which will fail while translation is stalled.

For A7xx, capture uses generated `adreno_gen7_*_snapshot.h` tables. It collects pre-crashdumper registers, optional crashdumper register lists, shader blocks, clusters, SPTP/DBGAHB clusters, releases the crashdump BO, and then reads post-crashdumper registers. For A6xx, it uses local tables from `a6xx_gpu_state.h`, reading AHB-safe registers directly and deeper ranges through crashdumper when available. If `snapshot_debugbus` is true, it configures debugbus muxes and reads GX/CX/VBIF/GBIF data. Finally it records whether the GPU was initialized.

Printing mirrors the captured object arrays. It emits generic Adreno state, GMU BOs with encoded data, HFI queue history, register lists, GMU registers, indexed-register ascii85 blocks, shader blocks, clusters, DBGAHB clusters, and debugbus blocks. A7xx printers include pipe, cluster, context, location, SPTP, and USPTP metadata from table handles.

## State And Persistence Behavior

Captured state is immutable after `a6xx_gpu_state_get()` returns. Small arrays are owned by `state_kcalloc()` allocations linked on `a6xx_state->objs`; GMU BO snapshots allocate separate `kvzalloc()` buffers and are freed explicitly in `a6xx_gpu_state_destroy()`. The crashdumper BO is temporary and returned with `msm_gem_kernel_put()` after capture. The capture process can temporarily alter hardware debug selectors, SQE state, CP mempool size, debugbus config, A7xx `SP_DBG_CNTL`, and chicken debug bits; functions generally restore modified values where necessary.

## Dependencies And Integration Points

This file depends on `a6xx_gpu.h`, `a6xx_gmu.h`, `a6xx_gpu_state.h`, generated A7xx snapshot headers, register XML, msm GEM helpers, ASCII85 encoding, DRM printers, Adreno core state capture/show, GMU initialization/status helpers, and global debug flags. It integrates with `a6xx_gpu.c` through `gpu_state_get`, `gpu_state_put`, and `show` function-table entries, and with the MMU fault path because SMMU stall state controls crashdumper use.

## Risks And Edge Cases

- Crashdumper cannot run if SPTPRAC is off, GX is off, hardware needs init, or SMMU is stalled. The code falls back to partial AHB capture, so missing sections can be expected in some fault classes.
- The crashdump script uses a fixed 8 KiB script area and data area under 1 MiB. Large table additions must respect `A6XX_CD_DATA_SIZE`.
- Capture halts SQE and toggles debug registers on already-faulted hardware. Bad ordering can worsen hangs or obscure original fault state.
- `state_kmemdup()` stores binary data that printers later interpret using static table handles. Table/data mismatch yields misleading dumps.
- Debugbus capture is optional and invasive; it remaps `cx_dbgc`, reprograms muxes, and can be unavailable on some DTs.
- A7xx family selection uses `BUG_ON()` for unexpected families in several helper paths. New generations must add tables before enabling state capture.

## Test Signals

Validation includes forced GPU hangs producing devcoredumps, SMMU faults producing partial but non-crashing dumps, GMU log/HFI/debug snapshots on full-GMU targets, A7xx dumps showing BR/BV/LPAC metadata, indexed CP mempool data with plausible sizes, debugbus output only when requested, no warnings about data size overflow, and successful `a6xx_gpu_state_put()` without leaks or double frees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu_state.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu_state.h

## Purpose

`a6xx_gpu_state.h` is the static capture schema for A6xx GPU state and the shared metadata schema for A7xx generated snapshot tables. It contains register ranges, shader-memory blocks, cluster descriptors, DBGAHB descriptors, GMU/GPUCC ranges, indexed CP register descriptors, debugbus block tables, and printable name arrays used by `a6xx_gpu_state.c`.

## Important APIs, Types, And Tables

- `A6XX_NUM_CONTEXTS` and `A6XX_NUM_SHADER_BANKS` define A6xx dump dimensionality.
- `struct a6xx_cluster`, `struct a6xx_dbgahb_cluster`, `struct a6xx_registers`, `struct a6xx_shader_block`, `struct a6xx_indexed_registers`, and `struct a6xx_debugbus_block` describe local A6xx capture ranges.
- `a6xx_clusters`, `a6xx_dbgahb_clusters`, `a6xx_hlsq_reglist`, `a6xx_shader_blocks`, `a6xx_reglist`, AHB/VBIF/GBIF reglists, GMU reglists, GPUCC reglists, indexed reglists, and debugbus block arrays feed the capture loops.
- `struct gen7_sel_reg`, `struct gen7_cluster_registers`, `struct gen7_sptp_cluster_registers`, `struct gen7_shader_block`, and `struct gen7_reg_list` define the shape expected from generated A7xx snapshot headers.
- `a7xx_debugbus_blocks`, `a7xx_statetype_names`, `a7xx_pipe_names`, and `a7xx_cluster_names` let A7xx dumps print stable names from enum values.
- Forward declarations for `a6xx_get_cp_roq_size()` and `a7xx_get_cp_roq_size()` support runtime-sized indexed register dumps.

## Control Flow

The header supplies data, not active code. `a6xx_gpu_state.c` walks each range array in register-pair form, where each pair is inclusive start/end dword offset. `RANGE()` in the C file computes counts from these pairs. For A6xx, local arrays fully describe which normal registers, HLSQ/SP/TP blocks, shader banks, clusters, CP indexed regions, GMU regions, and debugbus blocks are dumped. For A7xx, generated snapshot files provide family-specific lists in the `gen7_*` structures declared here, while this header provides common debugbus lookup and enum-name tables.

## State And Persistence Behavior

All tables are `static const` and persist in kernel text/data for the module lifetime. They do not store captured values. Their pointers are saved as `handle` fields in `struct a6xx_gpu_state_obj`, letting printer functions recover names, register ranges, dimensions, selectors, and output formatting after capture.

## Dependencies And Integration Points

The header includes `a6xx.xml.h` for A6xx register and statetype constants and depends on A7xx enum types included earlier by `a6xx_gpu.h`. Generated A7xx snapshot headers must produce arrays compatible with the `gen7_*` structs. `a6xx_gpu_state.c` relies on the order and sentinel conventions: A6xx arrays use explicit `count`, while many A7xx arrays end with `UINT_MAX` or NULL `regs`.

## Risks And Edge Cases

- Register ranges are raw dword offsets. Wrong ranges can read reserved registers, miss critical fault data, or overflow crashdumper data space.
- A6xx register arrays use inclusive pairs and `ARRAY_SIZE`; an odd number of entries corrupts range walking.
- A7xx arrays use sentinel conventions. Missing `UINT_MAX` or NULL terminators can make capture walk past the table.
- Debugbus block IDs are global for A7xx but selected per generated family list. Invalid IDs index `a7xx_debugbus_blocks` incorrectly.
- Printable name arrays are enum-indexed. If generated enum values change without updating the arrays, dumps show wrong names or access outside intended entries.
- New GPU families require careful table additions plus corresponding family selection in `a6xx_gpu_state.c`; current code has `BUG_ON()` for unsupported A7xx family values.

## Test Signals

Good signals are devcoredumps with populated register, indexed-register, shader, cluster, DBGAHB, GMU, and debugbus sections matching the target family; no `WARN_ON(datasize > A6XX_CD_DATA_SIZE)` during crashdump; no missing or nonsensical A7xx names; and stable dumps across A6xx, A650/A660, A7xx generation 1/2/3, and targets with VBIF versus GBIF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu_state.h -->
