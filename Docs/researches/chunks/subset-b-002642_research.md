# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 24775-27132

## Purpose

This chunk is generated register-field metadata for AMD GC 9.1 graphics-core registers. It contains only preprocessor `#define` constants for bit shifts and masks; it does not define executable code. The slice begins in the `gc_grbmdec` address block, covering RunList Controller (RLC) save/restore, UTCL1, load-balancer, interrupt, and DSM/R2I fields, then crosses into the `gc_pwrdec` address block for shader/compute-unit clock-gating and clock-test controls.

The major purpose is to let AMDGPU code name hardware register fields symbolically when using the driver register helpers. For example, callers can set `RLC_CP_SCHEDULERS.scheduler1` via `REG_SET_FIELD()` instead of hard-coding an 8-bit field at shift 8, and can preserve reserved bits by masking only named fields.

The assigned range contains 175 register comment blocks and 2181 `#define` lines. It starts at `RLC_SRM_INDEX_CNTL_ADDR_1`; the matching `_ADDR_0` block is immediately before this chunk, so merge/reconciliation should treat the `_ADDR_0..7` family as split across chunk boundaries.

## Important APIs, Types, And Data

There are no C functions, structs, classes, or enums. The API surface is the macro naming contract used by the AMD register access layer:

- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift amount for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit mask for that field.
- Register comments such as `//RLC_SRM_STAT` or `//CGTS_CU4_SP0_CTRL_REG` delimit generated groups.

Important register families in this chunk:

- `RLC_SRM_INDEX_CNTL_ADDR_1..7` and `RLC_SRM_INDEX_CNTL_DATA_0..7`: save/restore-memory indexed address and data windows. Address fields are 16-bit plus reserved upper bits; data windows expose full 32-bit payload fields.
- `RLC_SRM_STAT`, `RLC_SRM_GPM_ABORT`, `RLC_SRM_*_COMMAND_STATUS`: busy, delay, abort, FIFO-empty, and FIFO-full fields used around RLC save/restore commands.
- `RLC_CSIB_ADDR_LO`, `RLC_CSIB_ADDR_HI`, `RLC_CSIB_LENGTH`: command-stream indirect-buffer address/length fields, with the high address field limited to 16 bits.
- `RLC_SMU_COMMAND`, `RLC_SMU_ARGUMENT_1`, `RLC_SMU_ARGUMENT_2`: full-width command and argument fields for RLC-to-SMU command exchange.
- `RLC_CP_SCHEDULERS`: four 8-bit scheduler fields named `scheduler0` through `scheduler3`.
- `RLC_GPM_GENERAL_8..12`: full-width general-purpose RLC GPM data registers.
- `RLC_GPM_UTCL1_CNTL_0..2`, `RLC_SPM_UTCL1_CNTL`, `RLC_PREWALKER_UTCL1_CNTL`: UTCL1 control fields for XNACK redo timer count, drop mode, bypass, invalidate, fragment-limit mode, force-snoop, and VMID-dirty behavior.
- `RLC_UTCL1_STATUS` and `RLC_UTCL1_STATUS_2`: busy and stall-on-transaction status bits for GPM threads, SPM, and prewalker UTCL1 paths.
- `RLC_*_UTCL1_*_ERROR_*`: UTCL1 fault fields, including client ID, faulting VMID, permissions, queue ID, CID, and GCRD client ID.
- `RLC_LB_THR_CONFIG_1..4`, `RLC_R2I_CNTL_0..3`, `RLC_DS_CNTL`, `RLC_DSM_TRIG`, `RLC_LBPW_CU_STAT`: RLC load balancing, response-to-interrupt, depth/stencil, DSM trigger, and load-balance prewalker/CU status fields.
- `RLC_CGCG_CGLS_CTRL_3D` and `RLC_CGCG_RAMP_CTRL_3D`: coarse-grain clock-gating and light-sleep controls for the 3D block, including enable, delay, divider, ramp, wakeup, and override-style fields.
- `RLC_SEMAPHORE_0`, `RLC_SEMAPHORE_1`, `RLC_CP_EOF_INT`, `RLC_CP_EOF_INT_CNT`, `RLC_SPARE_INT`, `RLC_RLCV_SPARE_INT`: synchronization and interrupt flags/counters.
- `CGTS_SM_CTRL_REG`, `CGTS_RD_CTRL_REG`, `CGTS_RD_REG`, `CGTS_TCC_DISABLE`, `CGTS_USER_TCC_DISABLE`: global clock-test/control and TCC-disable fields in the `gc_pwrdec` block.
- `CGTS_CU0..15_*_CTRL_REG`: six repeated compute-unit control register types per CU: `SP0`, `LDS_SQ`, `TA_SQC`, `SP1`, `TD_TCP`, and `TCPI`. These expose 7-bit clock-test values plus override, busy-override, light-sleep-override, and SIMD-busy-override fields for shader processor, LDS, SQ, texture address, SQC, texture data, TCP/TCPF, and TCPI subblocks.
- `CGTT_SPI_CLK_CTRL`, `CGTT_PC_CLK_CTRL`, `CGTT_BCI_CLK_CTRL`, `CGTT_VGT_CLK_CTRL`: clock-gating turn-on delay, turn-off hysteresis, performance-enable, soft-stall override, core override, and register override fields for SPI, primitive/culling, BCI, and VGT blocks.

The CU clock-test pattern is highly regular: every CU index from 0 through 15 appears with the same six register types. Dual-subblock registers generally place the first subblock at bits 0-11 and the second at bits 16-27, leaving upper or intermediate reserved bits outside the named masks.

## Control Flow

The header chunk has no runtime control flow. Its practical control flow is compile-time expansion through AMDGPU macros:

1. A GC-generation-specific implementation includes the appropriate generated offset/mask headers.
2. Runtime code reads a 32-bit hardware register with `RREG32*()` or derives an address through `SOC15_REG_OFFSET()`.
3. Code updates fields with `REG_SET_FIELD()`, `WREG32_FIELD15*()`, or explicit mask operations using the macros in this file.
4. Code writes the result back with `WREG32*()`.

Examples elsewhere in the tree show the same fields being used in that pattern. `gfx_v9_0.c` reads `mmRLC_SRM_CNTL`, sets `RLC_SRM_CNTL__AUTO_INCR_ADDR_MASK`, and later uses `WREG32_FIELD15(..., RLC_SRM_CNTL, SRM_ENABLE, 1)` during RLC setup. MES and KFD code read `regRLC_CP_SCHEDULERS`, update scheduler fields, and write the value back. GC 10 code programs `mmCGTT_VGT_CLK_CTRL` in golden-register tables and direct writes, illustrating how CGTT masks map to clock-gating programming even when a newer generation owns the active implementation.

## State And Persistence Behavior

The macros are stateless compile-time constants. The state they describe is GPU hardware register state:

- RLC save/restore registers hold volatile command, address, data, FIFO, abort, busy, and status state. That state is meaningful during firmware-driven graphics setup, suspend/resume, reset, and power-management transitions.
- RLC UTCL1 status/error fields report live memory-translation/fault status. They should be treated as volatile hardware state, not cached software state.
- RLC interrupt and semaphore fields describe transient signaling between command processor, RLC firmware, and driver paths.
- CGTS/CGTT fields program persistent-until-reset clock-test and clock-gating behavior. They are not persisted by this header; persistence comes from driver init/golden-setting code reprogramming registers after GPU reset or power transitions.

Reserved masks are part of the persistence story: callers must preserve reserved bits on read-modify-write paths because these registers can carry hardware-owned state outside the named fields.

## Dependencies

This chunk depends on the generated GC 9.1 register database remaining synchronized with the hardware specification. It is coupled to:

- `gc_9_1_offset.h`, which provides the register offsets corresponding to these field masks.
- AMDGPU register helpers such as `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `WREG32_FIELD15`.
- ASIC-specific GFX, MES, KFD, PM, and reset code that manipulates RLC, CP scheduler, CGTS, and CGTT registers.
- RLC firmware/SMU protocols for save/restore memory, scheduler setup, and power-gating state.

The only GC 9.1-specific generated files in this directory are `gc_9_1_offset.h` and `gc_9_1_sh_mask.h`; unlike some generations, there is no separate `gc_9_1_d.h` in this tree. The mask names therefore need to line up with offset naming and with the include path selected by the target ASIC code.

## Integration Points

Primary integration points are low-level AMDGPU hardware bring-up and power-management paths:

- RLC initialization and firmware setup use `RLC_SRM_*`, `RLC_SMU_*`, and `RLC_CP_SCHEDULERS` fields to prepare save/restore memory, communicate with the SMU, and assign scheduler positions.
- MES/KFD queue-management code uses `RLC_CP_SCHEDULERS__scheduler*` fields to place or clear scheduler ownership for compute and kernel queues.
- GPU reset, suspend/resume, and power-gating paths depend on the RLC status, UTCL1 status/error, interrupt, and semaphore fields to sequence hardware state safely.
- Golden-register and clock-gating programming use the `CGTS_*` and `CGTT_*` fields to override clocks, force clocks on for diagnostics or safe programming, and tune on/off delays and hysteresis.
- Diagnostics and debug tooling can decode register dumps using these masks to show named field values instead of raw 32-bit words.

Because the chunk crosses from `gc_grbmdec` into `gc_pwrdec`, it sits at an integration boundary between RLC control/status and power/clock-control metadata.

## Risks

- Incorrect mask or shift values can silently program the wrong hardware bit, causing hangs, missed interrupts, bad queue scheduling, broken RLC save/restore, or unstable clock-gating behavior.
- The range starts mid-family at `RLC_SRM_INDEX_CNTL_ADDR_1`; generated-file consumers are fine, but research merging must avoid assuming `_ADDR_1` is the first address register.
- Many CGTS CU blocks are repetitive. Copy/paste or generation errors can be hard to spot because all 16 CUs should have consistent field layouts.
- Clock-gating override fields can affect power, performance, and hardware liveness. Writing broad constants to `CGTT_*` or `CGTS_*` registers without preserving reserved bits is risky.
- UTCL1 control fields such as bypass, invalidate, force snoop, and VMID dirty behavior can affect GPU virtual memory correctness and fault recovery.
- Full-width data/command fields such as `RLC_SMU_COMMAND`, `RLC_SMU_ARGUMENT_*`, and `RLC_GPM_GENERAL_*` provide no field-level guardrails; correctness depends on the higher-level firmware protocol.
- Cross-generation reuse is unsafe. Nearby GC versions often share names but can differ in offsets, extra fields, or reserved-bit layout.

## Test Signals

Useful validation signals for this chunk are mostly build-time, static, and hardware-runtime oriented:

- Build AMDGPU configurations that include GC 9.x generated register masks and exercise `REG_SET_FIELD()`/`WREG32_FIELD15*()` call sites for `RLC_SRM_CNTL` and `RLC_CP_SCHEDULERS`.
- Static comparison against `gc_9_1_offset.h` should confirm every register family in this chunk has a corresponding offset definition and that split families are reconciled with neighboring chunks.
- Static lint can verify that each field mask matches its shift and width, that masks within a register do not overlap unexpectedly, and that reserved masks cover the unnamed bits.
- Hardware smoke tests on GC 9.1 ASICs should cover RLC firmware load, RLC save/restore memory enable, CP scheduler programming, queue creation/destruction, suspend/resume, GPU reset, and memory-fault handling.
- Power-management tests should check that CGCG/CGLS and CGTT/CGTS programming does not regress idle power, wake latency, clock-gating counters, or GPU hang rates.
- Register-dump decoders should decode representative `RLC_UTCL1_STATUS*`, `RLC_*_ERROR_*`, `CGTS_CU*_CTRL_REG`, and `CGTT_*_CLK_CTRL` values consistently with these masks.
