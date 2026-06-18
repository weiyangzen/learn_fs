# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 22066-24623

## Purpose

This chunk is generated-style bitfield metadata for the AMD GC 9.4.2 graphics core, used by the AMDGPU driver and KFD bridge for Aldebaran-class GFX9.4.2 hardware. It defines `__SHIFT` and `_MASK` macros for fields in RLC, RMI, shader/SPI, compute-dispatch, and early `gc_shsdec` status/control registers. The definitions are compile-time constants only; consumers combine them with AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, and packet builders instead of hard-coding bit positions.

The range starts in the tail of `RLC_SERDES_WR_CTRL`, covers a large RLC block, crosses into `gc_rmi_rmidec`, then into `gc_shdec` shader and compute registers, and ends partway through `gc_shsdec` at `SPI_WF_LIFETIME_LIMIT_9`.

## Important APIs, Types, And Data

There are no C functions, structs, enums, storage objects, or runtime APIs in this range. The exposed interface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the low bit of a register field.
- `REGISTER__FIELD_MASK` gives the unshifted 32-bit mask for the field.
- `REGISTER__DATA__SHIFT` and `REGISTER__DATA_MASK` indicate full-word payload registers.
- Address-block comments such as `gc_rmi_rmidec`, `gc_shdec`, and `gc_shsdec` identify hardware decode domains, not C namespaces.

Important register groups in this chunk include:

- RLC SERDES and GPM/SPM/SRM registers: `RLC_SERDES_WR_CTRL`, `RLC_SERDES_WR_DATA`, `RLC_SERDES_CU_MASTER_BUSY`, `RLC_SERDES_NONCU_MASTER_BUSY`, `RLC_GPM_GENERAL_0..15`, `RLC_GPM_SCRATCH_*`, `RLC_SPM_MC_CNTL`, `RLC_SPM_INT_*`, `RLC_GPM_LOG_*`, `RLC_GPM_INT_*`, `RLC_SRM_*`, and `RLC_SRM_INDEX_CNTL_*`.
- RLC microcontroller, save/restore, and utility controls: `RLC_CSIB_*`, `RLC_CP_SCHEDULERS`, `RLC_GPM_UTCL1_CNTL_0..2`, `RLC_SPM_UTCL1_CNTL`, `RLC_UTCL1_STATUS*`, `RLC_PREWALKER_UTCL1_*`, `RLC_UTCL2_CNTL`, `RLC_DS_CNTL`, `RLC_SEMAPHORE_*`, clock-capture registers, spare interrupts, and RLCV spare interrupt registers.
- RLC diagnostic/error-counting controls: `RLC_EDC_CNT`, `RLC_EDC_CNT2`, `RLC_DSM_CNTL`, `RLC_DSM_CNTLA`, `RLC_DSM_CNTL2`, and `RLC_DSM_CNTL2A` describe SEC/DED counters plus design-for-test RAM irritator and error-injection fields.
- RMI/RB memory interface controls in `gc_rmi_rmidec`: `RMI_GENERAL_CNTL*`, `RMI_GENERAL_STATUS`, `RMI_SUBBLOCK_STATUS0..3`, `RMI_XBAR_CONFIG`, `RMI_PROBE_POP_LOGIC_CNTL`, `RMI_UTC_XNACK_N_MISC_CNTL`, `RMI_DEMUX_CNTL`, `RMI_UTCL1_CNTL1/2`, `RMI_TCIW_FORMATTER0/1_CNTL`, `RMI_SCOREBOARD_CNTL`, `RMI_SCOREBOARD_STATUS0..2`, `RMI_XBAR_ARBITER_CONFIG*`, `RMI_CLOCK_CNTRL`, `RMI_UTCL1_STATUS`, and `RMI_SPARE*`.
- Pixel/graphics shader programming registers in `gc_shdec`: `SPI_SHADER_PGM_RSRC3_PS`, `SPI_SHADER_PGM_LO/HI_PS`, `SPI_SHADER_PGM_RSRC1/2_PS`, the 32-entry `SPI_SHADER_USER_DATA_PS_*` array, and equivalent resource/user-data groups for VS, GS/ES, HS/LS, and `SPI_SHADER_USER_DATA_COMMON_0..31`.
- Compute shader dispatch and resource registers: `COMPUTE_DISPATCH_INITIATOR`, `COMPUTE_DIM_*`, `COMPUTE_START_*`, `COMPUTE_NUM_THREAD_*`, `COMPUTE_PGM_LO/HI`, dispatch packet and scratch base addresses, `COMPUTE_PGM_RSRC1/2/3`, `COMPUTE_VMID`, `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_STATIC_THREAD_MGMT_SE0..7`, `COMPUTE_TMPRING_SIZE`, restart/relaunch/wave-restore registers, checksum, and `COMPUTE_USER_DATA_0..15`.
- Early `gc_shsdec` controls: `SX_DEBUG_1`, `SPI_PS_MAX_WAVE_ID`, `SPI_START_PHASE`, `SPI_GFX_CNTL`, `SPI_DSM_CNTL`, `SPI_DSM_CNTL2`, `SPI_EDC_CNT`, `SPI_CONFIG_PS_CU_EN`, `SPI_WF_LIFETIME_CNTL`, and `SPI_WF_LIFETIME_LIMIT_0..9`.

## Control Flow

This header chunk has no executable control flow. Its behavior is via preprocessing: C files include the header, then compile these constants into register read-modify-write expressions, CP packet construction, debug register setup, golden-setting tables, or field decoders.

Typical runtime flow in consumers is:

1. Include `gc/gc_9_4_2_offset.h` for register offsets and `gc/gc_9_4_2_sh_mask.h` for field masks.
2. Build a register value with `REG_SET_FIELD` or extract a field with `REG_GET_FIELD`.
3. Write the value with SOC15 register helpers or emit it into a `PACKET3_SET_SH_REG` command stream.
4. Hardware persists, samples, or reports the corresponding register state until later programming, reset, or status clearing.

The local `gfx_v9_4_2.c` path shows this pattern for compute work: it emits `PACKET3_SET_SH_REG` packets for `regCOMPUTE_PGM_LO`, `regCOMPUTE_PGM_HI`, and `regCOMPUTE_USER_DATA_0`, then builds the dispatch initiator word with `REG_SET_FIELD(0, COMPUTE_DISPATCH_INITIATOR, COMPUTE_SHADER_EN, 1)` before a direct dispatch. `amdgpu_amdkfd_aldebaran.c` includes the same GC 9.4.2 mask header for KFD debug/trap register construction. Older same-name consumers in nearby GFX versions show how `RLC_SERDES_WR_CTRL` fields are commonly assembled for BPM/SERDES power and command operations.

## State And Persistence Behavior

The macros themselves are stateless and have no storage, lifetime, locking, or persistence behavior. They describe state that resides in GPU hardware registers and command packets.

State categories represented by this chunk include:

- Persistent configuration until reset or reprogramming: shader program resource registers, user-data registers, compute resource limits, thread-management masks, RLC UTCL1 controls, RMI arbitration/crossbar controls, and SPI wave lifetime limits.
- Per-dispatch or command-stream state: compute dimensions, start coordinates, thread counts, dispatch packet addresses, scratch bases, shader program base addresses, dispatch IDs, relaunch payloads, and user SGPR payloads.
- Volatile hardware status: SERDES master busy registers, SRM command FIFO status, RLC/RMI UTCL1 fault/retry/PRT status, RMI busy/error/subblock status, scoreboard counters, semaphore/interrupt indicators, and wave lifetime/EDC counts.
- Diagnostic and error-injection state: RLC and SPI DSM controls, SEC/DED counters, RAM irritator selections, inject-enable bits, and inject-delay fields. These are validation-oriented and can alter hardware behavior if programmed accidentally.
- Save/restore and power-management-related state: RLC SRM/ARAM/DRAM accessors, RLCV command/status, RLC static power-gating status, `RLC_PG_DELAY_3`, clock capture registers, and wave-restore addresses participate in low-level graphics microcontroller, reset, or debug flows rather than normal application state.

Because many fields are sticky or hardware-owned, consumers must follow the GC 9.4.2 register spec for clear-on-write, reserved-bit preservation, and reset/suspend/resume reinitialization. The header does not encode those semantics.

## Dependencies

This chunk depends on the rest of the generated GC 9.4.2 register set:

- `gc_9_4_2_offset.h` provides matching register offsets such as `regCOMPUTE_PGM_LO`, `regCOMPUTE_USER_DATA_0`, and RLC/RMI/SPI register symbols.
- Other generated GC 9.4.2 headers provide adjacent mask/default definitions outside this line range.
- AMDGPU SOC15 helpers, CP packet helpers, and register field macros provide the code-level operations that use these masks and shifts.
- `gfx_v9_4_2.c` depends on the header for Aldebaran GFX initialization, golden settings, compute-based VGPR/LDS clearing, RAS/UTC support, and wave-assignment diagnostics.
- `amdgpu_amdkfd_aldebaran.c` depends on the same generated register family for KFD debug/trap integration on Aldebaran.

The definitions are hardware-contract data. They must remain synchronized with the GC 9.4.2 register specification and with sibling offset/default headers. Similar macro names exist in GC 9.0, GC 9.2.1, GFX8, and later generations, but field layouts can differ; cross-generation substitution is unsafe even when names compile.

## Integration Points

Primary integration points are:

- Aldebaran GFX initialization and golden settings in `gfx_v9_4_2.c`, which include this header and use the same register namespace for chip-specific setup.
- Compute dispatch construction, especially `COMPUTE_PGM_LO/HI`, `COMPUTE_USER_DATA_*`, `COMPUTE_DIM_*`, and `COMPUTE_DISPATCH_INITIATOR`. These fields directly affect shader start address, dispatch dimensions, user SGPR payloads, scratch behavior, VMID, and wave scheduling.
- KFD/HSA integration. The KFD flat-memory documentation in the tree describes aperture mode selection in terms of `COMPUTE_DISPATCH_INITIATOR` fields and `SH_MEM_CONFIG`; Aldebaran KFD code includes this GC 9.4.2 mask header for debug and trap programming.
- RLC microcontroller workflows: GPM/SPM/SRM registers, SERDES write controls, scheduler bits, semaphores, spare interrupts, clock capture, and save/restore command/status fields integrate with graphics firmware, reset, power, and RAS flows.
- RMI/RB memory interface handling: VMID bypass, XNACK/UTCL1 controls, xbar and demux arbitration, scoreboard invalidation/status, TCIW formatter controls, and clock-control masks tie into memory translation, cache invalidation, render-backend traffic, and hang/fault diagnosis.
- Shader-stage programming through SPI resource registers and user-data arrays for PS, VS, GS/ES, HS/LS, common user data, and compute. These macros are the field-level contract for CP register programming and shader ABI setup.
- Diagnostics and validation through DSM/EDC and wave lifetime registers, which can be read for error counters or programmed to enable controlled test behavior.

## Risks

- A wrong shift or mask silently targets the wrong hardware bits. In this range that can corrupt shader resource setup, dispatch initiator words, CU/SIMD masks, VMID invalidation behavior, RLC save/restore commands, or RMI arbitration.
- The chunk mixes production control fields with debug, DSM, and error-injection fields. Accidentally setting inject-enable, irritator, force-stall, or debug-disable fields can create hangs, spurious RAS errors, or severe performance regressions.
- Reserved fields are explicitly represented in many registers. Consumers must preserve reserved bits when doing read-modify-write operations unless the hardware spec says otherwise.
- Several status fields may be sticky, clear-on-read, or clear-on-write depending on the underlying register. This header exposes only bit positions and cannot prevent destructive reads or incorrect clears.
- Compute dispatch fields are command-stream visible. Incorrect `COMPUTE_PGM_*`, scratch, user-data, resource-limit, thread-count, or initiator values can run the wrong shader address, misconfigure SGPR/VGPR allocation, break memory aperture selection, or hang a ring.
- RMI fields affect VMID bypass, XNACK handling, UTCL1 behavior, xbar/demux arbitration, and scoreboard invalidation. Misprogramming them can surface as GPUVM faults, invalidation timeouts, render-backend stalls, or hard-to-localize memory ordering bugs.
- Cross-generation names are deceptively similar. Reusing GC 9.0 or GFX8 assumptions for GC 9.4.2, especially around compute initiator, shader resource, RLC DSM/EDC, or RMI fields, can compile but misprogram Aldebaran hardware.
- Manual edits to this file are high risk because it is generated register metadata. Changes should generally come from regenerated AMD ASIC register sources.

## Test Signals

Useful validation signals include:

- Build coverage for AMDGPU configurations that compile `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c` with `gc_9_4_2_offset.h` and `gc_9_4_2_sh_mask.h`.
- Static consistency checks that registers in this chunk have corresponding offset symbols in `gc_9_4_2_offset.h` and that generated masks/shifts do not overlap unexpectedly within a register.
- Aldebaran boot and GFX initialization tests that apply golden settings, initialize RLC/CP/GFX blocks, and complete ring bring-up without invalid register access or timeout warnings.
- Compute dispatch smoke tests on GC 9.4.2 hardware, especially paths that program `COMPUTE_PGM_LO/HI`, `COMPUTE_USER_DATA_*`, `COMPUTE_DIM_*`, and `COMPUTE_DISPATCH_INITIATOR`.
- KFD process/debug tests that exercise trap enable/disable, wave launch modes, flat-memory aperture behavior, and VMID-specific debug state.
- Suspend/resume and GPU reset tests that verify RLC save/restore, SRM/RLCV command status, clock capture, semaphore, and power-gating related fields recover correctly.
- RAS/EDC diagnostics that read SEC/DED counters and verify DSM/error-injection controls are disabled in normal operation and only enabled in controlled validation.
- GPUVM/XNACK/invalidation stress tests that monitor RMI/RLC UTCL1 status, scoreboard status, busy bits, and fault/retry/PRT flags under memory pressure and preemption.
- Graphics and compute workloads that stress shader-stage user-data programming, scratch/LDS usage, CU masking, wave lifetime limits, render-backend memory traffic, and CP dispatch packet formation.
