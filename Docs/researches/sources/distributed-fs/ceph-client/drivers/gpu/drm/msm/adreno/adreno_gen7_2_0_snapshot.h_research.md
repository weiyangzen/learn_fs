# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gen7_2_0_snapshot.h

## Purpose

`adreno_gen7_2_0_snapshot.h` defines devcoredump capture tables for Gen7 2.0 GPUs. It extends the Gen7 0.0 layout for a wider configuration: more debugbus blocks, 6-USP shader block dimensions, updated GPU/GMU/GMUGX ranges, DBGC capture, DPM leakage capture, and selective reuse of Gen7 0.0 register lists where hardware blocks match.

## Important APIs, Types, And Functions

Important symbols include `gen7_2_0_debugbus_blocks`, `gen7_2_0_shader_blocks`, `gen7_2_0_gpu_registers`, `gen7_2_0_gmu_registers`, `gen7_2_0_gmugx_registers`, non-context BR/BV and RB arrays, GRAS/RB/SP arrays, LPAC-specific SP arrays, selector structs, `gen7_2_0_clusters`, `gen7_2_0_sptp_clusters`, `gen7_2_0_dbgc_registers`, RSCC/CPR/DPM leakage/GPUCC/CX_MISC/DPM arrays, `gen7_2_0_reg_list`, and `gen7_2_0_external_core_regs`.

## Control Flow

The file has table-driven flow only. Consumers iterate `gen7_2_0_reg_list` for core GPU/CX/DPM/DBGC ranges, `gen7_2_0_external_core_regs` for external blocks, cluster tables for context-sensitive register blocks, and SPTP tables for shader/texture processor regions. Several cluster entries intentionally reference `gen7_0_0_*` arrays to avoid duplication when blocks are unchanged.

## State And Persistence Behavior

All state is immutable compile-time data. Arrays are terminated with `UINT_MAX` pairs and guarded by alignment asserts. The generated capture definitions persist in the kernel image and determine what state is captured during a GPU devcoredump.

## Dependencies And Integration Points

The header depends on `a6xx_gpu_state.h` and on Gen7 0.0 symbols being visible when this header is included in the same snapshot compilation unit. It integrates with catalog-selected snapshot descriptors and the A6xx/A7xx GPU-state dumper.

## Risks

Cross-version reuse is efficient but creates dependency risk: changing or removing a Gen7 0.0 symbol can break Gen7 2.0 capture. Mis-sized shader blocks or wrong USP counts can truncate or overrun diagnostic reads. DBGC and leakage ranges may be fuse or power-domain sensitive, so capture sequencing must match hardware availability.

## Test Signals

Build coverage should catch missing reused symbols and alignment failures. Hardware validation should confirm devcoredumps on Gen7 2.0 include DBGC, DPM leakage, shader blocks, core registers, external core registers, and cluster/SPTP sections without register access faults.
