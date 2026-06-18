# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gen7_0_0_snapshot.h

## Purpose

`adreno_gen7_0_0_snapshot.h` is a static devcoredump register-capture description for Gen7 0.0 Adreno GPUs. It provides debugbus block IDs, shader memory block descriptors, GPU/GMU/register-range arrays, cluster capture tables, SPTP capture tables, and external core register lists consumed by the A6xx/A7xx GPU state snapshot code.

## Important APIs, Types, And Functions

The header exports data, not functions. Key symbols are `gen7_0_0_debugbus_blocks`, `gen7_0_0_shader_blocks`, pre/post crashdumper register arrays, `gen7_0_0_gpu_registers`, `gen7_0_0_gmu_registers`, `gen7_0_0_gmugx_registers`, non-context BR/BV/LPAC arrays, RB RAC/RBP selector structs, `gen7_0_0_clusters`, `gen7_0_0_sptp_clusters`, RSCC/CPR/GPUCC/CX_MISC/DPM arrays, `gen7_0_0_reg_list`, and `gen7_0_0_external_core_regs`.

## Control Flow

There is no executable control flow. Snapshot code iterates null- or sentinel-terminated tables. Register arrays encode inclusive start/end pairs terminated by `UINT_MAX, UINT_MAX`. Cluster arrays map cluster, pipe, forced-context state, register list, and optional selector register. SPTP arrays additionally specify SP/TP selector IDs, context indexes, logical locations such as HLSQ_STATE/SP_TOP/USPTP, and base offsets.

## State And Persistence Behavior

All data is `static const` and read-only after compilation. Captured state is generated at devcoredump time by consumers; this file only defines what hardware state should be sampled. `static_assert(IS_ALIGNED(sizeof(...), 8))` verifies register-pair alignment for snapshot iteration.

## Dependencies And Integration Points

The file includes `a6xx_gpu_state.h` for `gen7_*` table types and enum values. It depends on generated A7xx register/debugbus constants. It is integrated by device catalog or GPU-state selection paths that choose the appropriate snapshot tables for Gen7 0.0 hardware.

## Risks

Wrong register ranges can hang capture, miss diagnostic state, or read invalid/fused-off blocks. Selector register mistakes can capture the wrong RB/SP sub-block. The header is large and mostly declarative, so review should emphasize generated-data provenance, sentinel placement, alignment, and consistency with hardware manuals rather than local logic.

## Test Signals

Compile-time alignment asserts, successful devcoredump generation on Gen7 0.0 hardware, parseable debugbus sections, valid shader dumps, and no capture-time register read faults are the main validation signals.
