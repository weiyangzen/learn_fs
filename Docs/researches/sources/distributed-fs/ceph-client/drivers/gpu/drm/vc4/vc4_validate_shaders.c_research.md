<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_validate_shaders.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_validate_shaders.c

## Purpose
`vc4_validate_shaders.c` validates VC4 QPU shader BO contents before they can execute on hardware without an IOMMU. It rejects unsafe register writes, invalid branches, unsupported signals, unbounded uniform reads, direct TMU reads without clamp proof, and threaded shaders that touch the upper register halves; it also records texture sample relocation metadata and uniform stream layout for command-list validation.

## Important APIs, Types, and Functions
The main exported API is `vc4_validate_shader(struct drm_gem_dma_object *shader_obj)`, returning `struct vc4_validated_shader_info` or `NULL`. `struct vc4_shader_validation_state` tracks instruction pointer, TMU setup slots, live clamp/immediate state, branch targets, uniform-address update requirements, loop reset needs, and threaded register usage. Important helpers include `waddr_to_live_reg_index()`, `raddr_add_a_to_live_reg_index()`, `check_tmu_write()`, `validate_uniform_address_write()`, `check_reg_write()`, `track_live_clamps()`, `check_instruction_reads()`, `vc4_validate_branches()`, and `vc4_handle_branch_target()`.

## Control Flow
Validation initializes live register state, allocates a branch-target bitmap, allocates the validated-info result, and first scans all instructions for legal branch form and in-range branch targets. It then walks instructions linearly until the program-end delay slots complete. Each instruction is classified by QPU signal: normal math-like signals validate writes and uniform reads, `LOAD_IMM` validates writes and immediate tracking, and `BRANCH` validates no side-effect writes and delay-slot placement. Branch target entries reset tracked live state and force a uniform address reset before later uniform reads. Texture setup counts TMU parameters and records a sample when `TMU*_S` submits the lookup.

## State and Persistence Behavior
All validation state is transient except the returned `vc4_validated_shader_info`, which persists with the immutable shader BO and records `uniforms_size`, `uniforms_src_size`, texture sample offsets, direct-sample markers, uniform-address reset offsets, and threaded status. The code assumes shader BOs are immutable after creation, so successful validation is a one-time capability check. Hardware state is not touched; only kernel memory is allocated and freed.

## Dependencies and Integration Points
The file depends on DRM logging/allocation helpers, VC4 driver types, `vc4_qpu_defines.h` bitfield macros, GEM DMA BO mapping, and later VC4 validation/relocation code that consumes texture sample and uniform offset metadata. It is an authorization boundary between userspace shader blobs and QPU execution.

## Risks
The validator is security-critical because missed unsafe QPU behavior can permit arbitrary memory access. Direct TMU read safety depends on recognizing a specific `MAX(x,0)` then `MIN(..., uniform)` clamp pattern and invalidating that proof at all control-flow joins. Uniform address reset validation is intentionally conservative and may reject shaders that are semantically safe but not in the supported form. Branch delay-slot, program-end, and thread-switch timing are subtle. Allocation failure paths must free partially allocated metadata.

## Test Signals
Useful tests include shader fuzzing, branch target and delay-slot edge cases, direct TMU access with and without clamp proof, uniform reads across branch targets and backward loops, threaded shaders using lower versus upper registers, unsupported write addresses such as VPM DMA trigger, texture setup overflow, program-end termination checks, and memory-leak checks on validation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_validate_shaders.c -->
