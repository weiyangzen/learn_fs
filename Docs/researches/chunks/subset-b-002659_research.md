# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 24748-27129

## Scope

This chunk covers a generated AMD GC 9.2.1 shader/register mask header range. It contains 2,176 `#define` macros under 204 register comment anchors. The slice starts at `RLC_GPR_REG1` and moves through RLC scratch, save/restore, SMU, UTCL1, interrupt/status, clock-gating, and low-power controls before entering the `gc_pwrdec` address block for CGTS power-decoder controls. It ends in the shift half of `CGTS_CU14_TCPI_CTRL_REG`, so the adjacent chunk is needed for the remaining masks and later CU power-control definitions.

The file is not executable code. Its public surface is a collection of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` preprocessor constants used with matching register-address definitions elsewhere in the AMDGPU generated register headers.

## Purpose

`gc_9_2_1_sh_mask.h` provides compile-time bitfield positions and masks for AMD GC 9.2.1 graphics-core registers. This chunk focuses on firmware/power-management-facing graphics microcontroller state:

- RLC GPR, GPM, SPM, SRM, RLCV, CSIB, SMU-command, semaphore, interrupt, and GPU-clock-count registers.
- RLC UTCL1/UTCL2 translation controls, status, error reporting, prewalker address/size/trigger controls, and DSM/R2I control words.
- RLC clock-gating and light-sleep controls for 3D, plus deep-sleep busy-mask control.
- `gc_pwrdec` CGTS controls for shader-array power gating, TCC disable masks, readback muxes, and per-CU block override/state controls.

The constants let AMDGPU code build, decode, and validate 32-bit register values without embedding raw bit numbers. For this range, correctness is especially relevant to power gating, firmware save/restore, GPU virtual-memory fault diagnostics, SMU/RLC handshakes, and compute-unit block power-state control.

## Important API Surface

- `RLC_GPR_REG1`, `RLC_GPR_REG2`, `RLC_GPM_GENERAL_8` through `RLC_GPM_GENERAL_15`, and `RLC_R2I_CNTL_0` through `RLC_R2I_CNTL_3` are full-width data registers. Consumers treat them as opaque 32-bit firmware or microcode scratch/control values.
- `RLC_SRM_CNTL`, `RLC_SRM_ARAM_ADDR/DATA`, `RLC_SRM_DRAM_ADDR/DATA`, `RLC_SRM_GPM_COMMAND`, `RLC_SRM_RLCV_COMMAND`, status registers, index-control address/data slots 0-7, and `RLC_SRM_GPM_ABORT` describe the RLC save/restore manager command interface. Key fields include enable, auto-increment, operation, size, start offset, destination memory, FIFO empty/full status, and abort.
- `RLC_CSIB_ADDR_LO/HI` and `RLC_CSIB_LENGTH` expose a command-stream instruction buffer pointer and length split across low/high address fields.
- `RLC_SMU_COMMAND`, `RLC_SMU_ARGUMENT_1` through `_4`, and `RLC_SMU_CLK_REQ` define RLC-to-SMU command and argument payload fields, including a clock-request bit.
- `RLC_CP_SCHEDULERS`, `RLC_CP_EOF_INT`, `RLC_CP_EOF_INT_CNT`, `RLC_SPARE_INT`, `RLC_SPARE_INT_1`, `RLC_RLCV_SPARE_INT`, and `RLC_RLCV_SPARE_INT_1` cover scheduler selection and interrupt status/force/count-like state.
- `RLC_GPM_UTCL1_CNTL_0` through `_2`, `RLC_SPM_UTCL1_CNTL`, and `RLC_PREWALKER_UTCL1_CNTL` share the same UTCL1 policy layout: `XNACK_REDO_TIMER_CNT`, `DROP_MODE`, `BYPASS`, `INVALIDATE`, `FRAG_LIMIT_MODE`, `FORCE_SNOOP`, and `FORCE_SD_VMID_DIRTY`.
- `RLC_UTCL1_STATUS` and `RLC_UTCL1_STATUS_2` provide fault, retry, partial-residency, busy, and stall-on-transaction bits, including UTCL1 IDs for fault/retry/PRT sources. `RLC_SPM_UTCL1_ERROR_*` and `RLC_GPM_UTCL1_TH{0,1,2}_ERROR_*` expose per-thread client-ID and address fields for UTCL1 errors.
- `RLC_PREWALKER_UTCL1_TRIG`, address LSB/MSB, and size LSB/MSB fields describe a prewalk operation with VMID, read/write/execute permissions, prime mode, ready, address, and size fields.
- `RLC_CGCG_CGLS_CTRL_3D`, `RLC_CGCG_RAMP_CTRL_3D`, `RLC_DS_CNTL`, `RLC_LBPW_CU_STAT`, and `RLC_UTCL2_CNTL` define graphics clock-gating/light-sleep behavior, ramp timing, deep-sleep busy masks, live CU status, and UTCL2 no-PTE memory-type handling.
- `CGTS_SM_CTRL_REG`, `CGTS_RD_CTRL_REG`, `CGTS_RD_REG`, `CGTS_TCC_DISABLE`, and `CGTS_USER_TCC_DISABLE` are `gc_pwrdec` shader/tile-cache control and diagnostic registers.
- `CGTS_CU0_*` through the partial `CGTS_CU14_TCPI_CTRL_REG` family provides repeated per-CU power/override control for SP0, LDS/SQ, TA/SQC, SP1, TD/TCPF, and TCPI blocks. Repeated fields include block state bits, `*_OVERRIDE`, `*_BUSY_OVERRIDE`, `*_LS_OVERRIDE`, and `*_SIMDBUSY_OVERRIDE`.

There are no structs, enums, functions, or inline helpers in this chunk. The API is entirely macro names and their numeric shift/mask values.

## Control Flow

There is no direct C control flow in the header. Runtime control flow happens in consumers:

1. Select a GC 9.2.1 register offset from the matching address header.
2. Compose a 32-bit value by shifting caller-selected field values with `REGISTER__FIELD__SHIFT`.
3. Apply `REGISTER__FIELD_MASK` when preserving, clearing, or extracting fields.
4. Write or read the register via SOC15/MMIO accessors, PM4 packets, RLC firmware programming paths, golden-register setup, or debug dumps.

The repeated families imply table-driven callers. SRM index-control address/data slots can be iterated over 0-7; GPM UTCL1 thread controls and errors are indexed over threads 0-2; CGTS per-CU controls are naturally iterated by CU number and sub-block type when power-gating or diagnostic code walks a shader array.

## State and Persistence

The macros are stateless build artifacts, but the hardware registers they describe are persistent GPU state until changed by firmware, driver register programming, power-management transitions, suspend/resume, reset, or context restore.

RLC SRM and RLCV command fields affect firmware-managed save/restore movement between internal memories and destination memory. Incorrect command size, start offset, destination memory, FIFO-status handling, or abort programming can leave RLC state partially saved or restored.

UTCL1/UTCL2 and prewalker controls affect GPU virtual-memory translation behavior for RLC/GPM/SPM/prewalker traffic. XNACK retry timing, bypass/drop/invalidate policy, forced snooping, VMID, access permissions, and address/size fields can persist across diagnostic or firmware operations and influence fault visibility or recovery.

Clock-gating, light-sleep, deep-sleep, and CGTS fields persist as power-management policy. Overrides can force blocks on or off, override busy/light-sleep/SIMD-busy signals, disable TCC slices, or alter sequencing delays. Incorrect persistence here can produce higher idle power, missed power savings, or unstable entry/exit from gated states.

Interrupt, semaphore, scheduler, SMU-command, and GPU-clock-count registers are synchronization state between RLC, CP, SMU, and driver code. Their values may be sampled by firmware or interrupt handlers rather than by ordinary draw/dispatch state emission.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.2.1 register database. The masks in this header must stay synchronized with companion address headers such as `gc_9_2_1_d.h` and neighboring generated `*_sh_mask.h` files under `drivers/gpu/drm/amd/include/asic_reg/gc/`.
- Integrated through AMDGPU SOC15 register access helpers, RLC initialization, power-management setup, SMU/RLC messaging, golden-register tables, debugfs/register dumps, and GPU reset/suspend/resume paths.
- Ties into VM/fault handling through UTCL1 status and error fields, including fault/retry/PRT detection, UTCL1 IDs, client IDs, and prewalker address/permission programming.
- Ties into firmware save/restore through SRM, RLCV, ARAM/DRAM, GPM, and index-control registers.
- Ties into power management through RLC CGCG/CGLS/ramp/deep-sleep controls and `gc_pwrdec` CGTS per-CU block controls.
- Uses plain C preprocessor constants only. Callers must perform all range validation, reserved-bit handling, register-address selection, indexing, sequencing, and read/modify/write locking themselves.

## Risks

- Generated bitfield drift is the main risk. If a mask or shift diverges from the GC 9.2.1 hardware specification or the companion address header, callers silently program the wrong bits.
- This chunk ends mid-register-family at `CGTS_CU14_TCPI_CTRL_REG`. Merge tooling must avoid treating the TCPI CU family or the file-level CGTS coverage as complete from this chunk alone.
- SRM/RLCV command fields have high state-corruption risk because operation, size, offset, destination memory, FIFO, and abort fields control firmware save/restore movement.
- UTCL1 and prewalker fields are sensitive. Bad VMID, permission, address, size, retry, invalidation, or bypass/drop settings can hide VM faults, produce false fault attribution, or destabilize RLC-side memory accesses.
- Power-control overrides can mask real busy/idle state. Incorrect `CGTS_CU*_..._OVERRIDE`, `*_BUSY_OVERRIDE`, `*_LS_OVERRIDE`, or `*_SIMDBUSY_OVERRIDE` usage can cause hangs during power transitions or block expected clock/power gating.
- Repeated per-CU/per-block macros create indexing and copy/paste hazards. A CU index, block name, or high/low half mismatch can affect a different shader block than intended.
- Reserved masks are present but not enforced. Callers that do read/modify/write without preserving reserved bits, or that write reserved bits from stale tables, can trigger hardware-specific behavior.

## Test Signals

- Build coverage: compiling AMDGPU with this generated header catches syntax errors, duplicate definitions, and missing include dependencies.
- Register-generation validation: compare lines 24748-27129 against the GC 9.2.1 register source/spec and matching address header to verify every `__SHIFT` has the expected `_MASK`, bit width, and register association.
- Power-management smoke tests: boot/resume/reset a GC 9.2.1 device and watch for golden-register warnings, RLC/SMU handshake failures, GPU hangs, or elevated idle power after CGCG/CGLS/CGTS programming.
- VM/fault diagnostics: exercise GPUVM fault, retry/XNACK, PRT, and prewalker paths while decoding `RLC_UTCL1_STATUS*` and `RLC_*_UTCL1_*ERROR*` fields with these masks.
- Firmware save/restore validation: stress suspend/resume, GPU reset, power-gating transitions, and RLC firmware reload paths that use SRM/RLCV command/status fields.
- Register-dump validation: decode known-good dumps for `RLC_SRM_*`, `RLC_GPM_UTCL1_CNTL_*`, `RLC_PREWALKER_UTCL1_*`, `RLC_CGCG_*`, `RLC_DS_CNTL`, `CGTS_SM_CTRL_REG`, and representative `CGTS_CU*_CTRL_REG` entries.
