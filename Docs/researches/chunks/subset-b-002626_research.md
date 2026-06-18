# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 27123-29720

## Scope

This chunk covers a generated AMD GC 9.0 shift/mask header segment. It contains preprocessor constants only: bit `__SHIFT` values and `_MASK` values used by AMDGPU, AMDKFD, and power-management code to compose and decode 32-bit graphics-core register values.

The requested range contains 2,145 `#define` entries: 1,074 shift macros and 1,071 mask macros. The count is intentionally unbalanced because the chunk starts at the mask for `CP_ME_RAM_WADDR__ME_RAM_WADDR` while its shift is on the previous line, and it ends inside `DIDT_TCP_EDC_STALL_DELAY_4`, before the corresponding masks for TCP12-TCP15.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU DRM graphics metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_9_0_sh_mask.h` supplies bitfield layouts for GC 9.0 graphics-core registers. This chunk covers several independent hardware namespaces:

- CP and RLC microcode access fields for ME, CE, MEC1, MEC2, and RLC GPM RAM/register windows.
- GRBM graphics-index, graphics-control, and CAM remapping selectors used to target shader engines, shader arrays, instances, pipes, MEs, VMIDs, and queues.
- RLC GPU IOV, RLCV timer, hypervisor semaphore, clock-control, scratch, firmware, function, interrupt, doorbell, virtual reset, SDMA status, and busy-status fields used by SR-IOV/PF-VF scheduling and virtualization flows.
- `gccacind` and `secacind` indirect CAC registers for graphics-core and shader-engine power/activity counters, weights, override selection/value fields, and accumulator readback across BCI, CB, CBR, CP, DB, DBR, GDS, IA, LDS, PA, PC, SC, SPI, SQ, SX, SXRB, TA, TCC, TCP, TD, VGT, WD, CU, EA, RMI, UTCL2/ATCL2, UTCL2 router, VML2, and walker blocks.
- `sqind` indirect shader queue debug and wave-state fields for wave mode/status/trap status, hardware IDs, GPR/LDS allocation, instruction buffer status/debug, program counter, instruction words, temporary trap registers, execution masks, and SQ interrupt-word encodings.
- `didtind` dynamic inductive/droop throttling fields for SQ, DB, TD, and TCP blocks, including control, thresholds, power windows, stall delays, stall patterns, weights, EDC control, EDC thresholds, EDC status, EDC stall patterns, and EDC per-lane delay registers.

Driver code pairs these macros with register offsets from `gc_9_0_offset.h` and uses helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, SOC15 MMIO helpers, indirect-register helpers, CGS power-management accessors, and KFD MQD setup code to program or inspect hardware without hard-coding bit positions.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for isolating or preserving that field.
- Register comments such as `//RLC_GPU_IOV_CFG_REG1` and address-block comments such as `// addressBlock: didtind` preserve grouping from the hardware register database.
- Consumers normally pair these field definitions with `reg*`, `mm*`, or `ix*` offsets from the matching generated offset header.

Important field families in this chunk include:

- Microcode windows: `CP_HYP_ME_UCODE_DATA`, `CP_ME_RAM_DATA`, `CP_CE_UCODE_ADDR/DATA`, `CP_HYP_CE_UCODE_ADDR/DATA`, `CP_HYP_MEC1/2_UCODE_*`, `CP_MEC_ME1/2_UCODE_*`, `RLC_GPM_UCODE_ADDR`, and `RLC_GPM_UCODE_DATA`.
- GRBM selector fields: `GRBM_GFX_INDEX_SR_DATA` fields for instance/SH/SE indices and broadcast writes; `GRBM_GFX_CNTL_SR_DATA` fields for pipe, ME, VMID, and queue; and `GRBM_CAM_DATA`/`GRBM_HYP_CAM_DATA` address/remap fields.
- RLC IOV fields: VF enable/count, context size/location/offset, VM busy status, doorbell status/set/clear/mask, scheduler block identity/version/size, command type/execute/interrupt/function ID/next function ID, command status, active functions, active PF/VF identity, RLC IOV microcode and scratch access, F32 enable/reset, SDMA0/SDMA1 preempted/saved/restored status, SMU/RLC responses, virtual reset request bits, interrupt disable/force, and SDMA VM busy masks.
- CAC fields: global and SE `CAC_ENABLE`, thresholds, block/signal IDs, override select/value registers, per-block 16-bit signal weights, 32-bit accumulators, and override selectors/values with block-dependent widths.
- SQ wave debug fields: mode bits for FP rounding/denorms, DX10 clamp, IEEE, debug and exception enable, perf disable, GPR index, VSKIP, CSP; status bits for SCC, priorities, privilege, traps, export readiness, EXECZ/VCCZ, barriers, halt, valid, ECC, replay, and fatal halt; trap status, hardware attribution, allocation sizes, instruction buffer counters/debug states, PC and instruction words, TTMP0-TTMP15, M0, EXEC masks, and interrupt word encodings.
- DIDT/EDC fields: `DIDT_*_CTRL0/1/2/3`, stall/tuning/auto-release controls, stall pattern registers, weight registers, `DIDT_*_EDC_CTRL`, EDC thresholds, EDC stall patterns, EDC status, EDC delay registers, overflow counters, and rolling power delta fields for SQ, DB, TD, and TCP. The DB family has only `DIDT_DB_EDC_STALL_DELAY_1` in this chunk, while SQ, TD, and TCP expose delay groups for up to 16 lanes or instances.

## Control Flow

This header has no local runtime control flow. Its direct behavior is compile-time macro substitution.

The implied driver flow is:

1. GC 9.0 AMDGPU, AMDKFD, or power-management code includes `gc_9_0_offset.h` and `gc_9_0_sh_mask.h`.
2. Code selects a register offset, sometimes through direct SOC15 MMIO and sometimes through indirect index/data windows such as GC CAC, SE CAC, SQ, or DIDT.
3. Code composes or decodes field values using these shift/mask constants through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_DIDT`, `WREG32_DIDT`, `cgs_read_ind_register`, and `cgs_write_ind_register`.
4. Runtime paths use the resulting values to load firmware, select GRBM targets, manage SR-IOV and RLC virtualization state, inspect wave/debug state, configure power/throttling tables, collect counters, or handle reset and preemption state.

Concrete include users in this tree include `amdgpu/gfx_v9_0.c`, `amdgpu/soc15.c`, `amdgpu/mxgpu_ai.c`, `amdgpu/gfxhub_v1_0.c`, `amdgpu/gmc_v9_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v9.c`, `amdgpu/amdgpu_amdkfd_arcturus.c`, `amdkfd/kfd_mqd_manager_v9.c`, and `pm/powerplay/hwmgr/vega10_inc.h`. Power-management files such as `vega10_powertune.c`, `smu7_powertune.c`, and `kv_dpm.c` use the DIDT and CAC field macros to build tuning tables and toggle droop/throttling controls.

The generated header does not encode ordering requirements, side-effect semantics, access permissions, polling timeouts, firmware ownership, read-only/write-only status, clear-on-read behavior, write-one-to-clear behavior, or reset sequencing. Those rules come from hardware documentation and the consuming AMDGPU/AMDKFD/PM code.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state in GC 9.0 registers:

- CP and RLC microcode address/data windows affect firmware upload or firmware-visible RAM/register windows. Values are transient during load and debug flows, but wrong field packing can corrupt the loaded microcode stream or address window.
- GRBM selectors route later indexed or broadcast operations to specific shader engines, shader arrays, instances, pipes, MEs, VMIDs, and queues. Their values are control state that can affect subsequent register accesses until changed.
- RLC GPU IOV fields describe persistent virtualization scheduler state, active PF/VF identity, context allocation, VF doorbell masks/status, interrupt routing, virtual function reset requests, and SDMA save/restore/preempt progress. These values matter across SR-IOV scheduling, reset, and preemption windows.
- CAC weight, override, and accumulator fields represent power/activity modeling state. Weight and override values are programmed policy; accumulators are live counters or sampled state that power-management code may read, clear, or use for telemetry.
- SQ wave debug fields expose live shader execution context: current wave mode/status, trap state, attribution, register allocation, instruction buffer state, PC/instruction data, TTMP registers, EXEC masks, and interrupt payload fields. They are diagnostic hardware state, not driver-owned persistent storage.
- DIDT control and EDC fields configure throttling and power response for SQ, DB, TD, and TCP blocks. Thresholds, intervals, stall patterns, weights, forced-stall controls, EDC enables/resets, and per-unit stall delays are persistent hardware policy until reset or reprogramming.
- Overflow, rolling power delta, EDC status, busy status, response, and interrupt status fields are live telemetry or latched hardware state. This header cannot identify which fields require special access sequences to clear or sample correctly.

Because this is a generated shift/mask file, it cannot show whether a register is privileged, shadowed, per-instance, per-SE, PF-only, VF-visible, saved by firmware, restored by reset code, or safe for read-modify-write. Consumers must preserve reserved fields unless the programming guide or local driver code says otherwise.

## Dependencies And Integration Points

This chunk depends on synchronization with AMD's GC 9.0 register database and companion generated files:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` for matching MMIO and indirect register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_default.h` for generated defaults where applicable.
- AMDGPU register helper infrastructure, including SOC15 accessors, indirect CAC/SQ/DIDT accessors, `REG_SET_FIELD`, `REG_GET_FIELD`, and CGS power-management register wrappers.

Primary integration points are:

- `amdgpu/gfx_v9_0.c`, which programs GC 9.0 graphics, CP/RLC, GRBM, wave debug, reset, and firmware-facing state.
- `amdgpu/mxgpu_ai.c` and other SR-IOV paths, which rely on RLC GPU IOV masks for PF/VF scheduling, virtual reset, doorbells, and function attribution.
- `amdkfd/kfd_mqd_manager_v9.c` and `amdgpu/amdgpu_amdkfd_gfx_v9.c`, which include the GC 9.0 register namespace for KFD queue integration.
- `amdgpu/gfxhub_v1_0.c`, `amdgpu/gmc_v9_0.c`, and `amdgpu/soc15.c`, which include GC 9.0 field definitions for memory hub, SOC initialization, reset, and register access support.
- `pm/powerplay/hwmgr/vega10_powertune.c`, `pm/powerplay/hwmgr/smu7_powertune.c`, and `pm/legacy-dpm/kv_dpm.c`, which consume DIDT and CAC fields to build power-tuning tables, enable/disable DIDT blocks, and configure EDC behavior.
- Hardware diagnostics, profiling, debugfs, RAS, SR-IOV, and reset paths that decode SQ debug, wave, interrupt, CAC, DIDT, RLC, and GRBM state.

## Risks And Edge Cases

- Generated-data drift is the main risk. A wrong shift or mask can compile cleanly while writing the wrong hardware bits.
- The chunk starts and ends inside register definitions. `CP_ME_RAM_WADDR` is missing its shift in this chunk, and `DIDT_TCP_EDC_STALL_DELAY_4` is missing all four masks. Adjacent chunks are required before making whole-register completeness claims.
- The RLC GPU IOV fields are virtualization-sensitive. Incorrect VF enable, VF number, PF/VF identity, doorbell mask/status, active-function, command, interrupt, or virtual-reset masks can misroute work, break isolation, or make PF/VF reset handling unreliable.
- GRBM index and broadcast fields are high-risk because they route later writes. An incorrect index or broadcast bit can program the wrong shader engine, shader array, instance, pipe, ME, VMID, or queue.
- CP/RLC/MEC microcode address/data fields are firmware-critical. Address mask errors can truncate firmware upload addresses or write data to an unintended window.
- CAC and DIDT tables are repetitive and policy-sensitive. Copy/paste or generator errors can affect only a specific block such as TCP, TD, DB, SQ, UTCL2 router, or CU, which may appear as workload-dependent throttling, power, or telemetry anomalies rather than immediate boot failures.
- SQ debug and wave-state fields expose live execution context. Mis-decoding these fields can mislead hang analysis, wave dumps, shader debugging, trace decoding, or exception attribution.
- Some status, accumulator, interrupt, overflow, and response fields may be latched or have side effects on access. This header cannot distinguish ordinary status bits from clear-on-read, write-one-to-clear, or sample-triggered registers.
- Reserved and unused masks are explicit throughout the chunk. Read-modify-write code must preserve them unless the hardware programming guide specifies a safe value.
- Field names include generated spelling and casing quirks such as `Sch_Block_ID`, `Time_Quanta_Def`, `OVRRD_SELECT`, and compact SQ interrupt masks. Consumers must match the generated identifiers exactly.

## Test Signals

Useful validation should combine static generated-data checks, build coverage, and hardware/runtime testing:

- Build AMDGPU, AMDKFD, and power-management code with GC 9.0 support. Missing or renamed macros should surface in `gfx_v9_0.c`, KFD MQD/queue code, SR-IOV code, and powertune tables.
- Mechanically diff this range against AMD's authoritative GC 9.0 register database and verify both shift values and masks.
- Verify shift/mask pairing for complete registers in the chunk, allowing the known boundary exceptions for `CP_ME_RAM_WADDR` and `DIDT_TCP_EDC_STALL_DELAY_4`.
- Cross-check repeated CAC weight/accumulator/override groups and DIDT SQ/DB/TD/TCP families for consistent field widths, unused ranges, and expected per-block differences.
- Exercise GC 9.0 firmware load and reset paths. Relevant signals include successful CP/RLC/MEC initialization, no firmware load failures, and clean ring bring-up after reset.
- Run SR-IOV/PF-VF tests where hardware and firmware support are available. Watch VF enable/count, active function ID, doorbell status/masks, virtual reset requests, SDMA preempt/save/restore status, and busy-status attribution.
- Run graphics and compute workloads while exercising GRBM-targeted register paths. Failures may present as wrong per-SE/per-SH state, hangs, or inconsistent debug dumps.
- Run power-management tests around Vega10/GC9 DIDT and EDC enable/disable, including suspend/resume, clock changes, and throttling events. Expected signals are stable clocks, plausible power telemetry, no forced-stall leakage, and no performance collapse under normal loads.
- Validate CAC accumulators and weights with power-tuning table programming. Check for plausible activity counter movement across SQ, TCP, TD, TCC, CU, UTCL2, and related blocks.
- Exercise shader debugging, wave dumps, trap/exception handling, and thread trace. Check SQ wave status, trap status, hardware ID attribution, PC/instruction values, TTMP data, EXEC masks, and SQ interrupt word decoding.
- Run GPU reset, hang recovery, and preemption scenarios. RLC, GRBM, SQ, and DIDT state should return to expected defaults or driver-programmed values after recovery.

## Cross-Chunk Notes

The previous chunk owns the beginning of the CP/RLC microcode field area, including `CP_ME_RAM_WADDR__ME_RAM_WADDR__SHIFT`. This chunk continues CP/RLC/GRBM definitions, fully covers the RLC GPU IOV block and the GC/SE CAC and SQ debug blocks in this range, then covers DIDT SQ, DB, TD, and most of TCP EDC delay definitions. The next chunk must complete `DIDT_TCP_EDC_STALL_DELAY_4` masks and continue with subsequent DIDT DBR fields.

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002626_research.md`; whole-file research for `gc_9_0_sh_mask.h` should be produced later by merging all chunk documents for the source file.
