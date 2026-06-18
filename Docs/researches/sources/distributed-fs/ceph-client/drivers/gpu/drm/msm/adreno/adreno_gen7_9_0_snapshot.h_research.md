# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gen7_9_0_snapshot.h

## Purpose

`adreno_gen7_9_0_snapshot.h` is the expanded devcoredump capture definition for Gen7 9.0 Adreno GPUs. It describes core, GMU, GMUGX, CX, DBGC, shader, cluster, SPTP, indexed CP, and external-core register captures, with generated comments documenting block grouping and register counts.

## Important APIs, Types, And Functions

Key symbols include `gen7_9_0_debugbus_blocks`, separate `gen7_9_0_gbif_debugbus_blocks` and `gen7_9_0_cx_debugbus_blocks`, `gen7_9_0_shader_blocks`, pre-crashdumper and core GPU/GMU/GMUGX/CX_MISC/DBGC/CX_DBGC arrays, non-context pipe arrays for BR/BV/LPAC, RB RAC/RBP arrays, GRAS/PC/VFD/VPC/RB/SP/TPL1 cluster arrays, selector structs, `gen7_9_0_clusters`, `gen7_9_0_sptp_clusters`, `gen7_9_0_cp_indexed_reg_list`, `gen7_9_0_reg_list`, and external CPR/DPM/DPM leakage/ACD/GPUCC/ISENSE/RSCC arrays.

## Control Flow

The file is entirely declarative. Snapshot consumers iterate sentinel-terminated register ranges and table arrays. Compared with earlier Gen7 snapshot headers, Gen7 9.0 splits debugbus capture into GPU, GBIF, and CX groups, adds HLSQ data-stripe and local-misc shader ranges, includes indexed CP registers through `struct a6xx_indexed_registers`, and carries many generated block comments with pair/register counts to support auditability.

## State And Persistence Behavior

The table data is immutable after compile. Register arrays use inclusive start/end pairs ending in `UINT_MAX, UINT_MAX`; alignment asserts protect the pair-walk ABI. Indexed register descriptors persist enough metadata for consumers to select indexed CP debug registers rather than plain address ranges.

## Dependencies And Integration Points

The header includes `a6xx_gpu_state.h`, depends on A7xx register/debugbus constants and snapshot table type definitions, and is selected by Gen7 9.0 catalog/state code for devcoredump capture. External core arrays require access to non-GPU register spaces such as CPR, DPM, GPUCC, ISENSE, and RSCC.

## Risks

The larger capture surface increases the chance of reading unavailable power domains or fused-off debug blocks. Indexed CP register capture has more sequencing risk than simple ranges. Generated table comments help audit pair counts, but stale generation input can still produce incomplete or unsafe ranges. Debugbus split groups must match the dumper's power/clock sequencing.

## Test Signals

Validation signals include successful compile-time alignment, devcoredump completion on Gen7 9.0 hardware, distinct GPU/GBIF/CX debugbus sections, usable indexed CP output, no external-core read faults, and enough SP/HLSQ/TPL1 state to diagnose shader hangs.
