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
