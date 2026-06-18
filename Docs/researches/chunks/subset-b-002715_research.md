# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_sh_mask.h lines 9310-13970

## Scope

This chunk is a generated AMD GFX 8.0 register shift/mask header segment. It contains only C preprocessor constants: each hardware register field is represented by `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` macros. There are no functions, structs, enums, variables, includes, allocations, locks, branches, or executable control flow in this range.

The selected range starts in the tail of the RLC SPM sample-delay family, covers RLC GPU IOV/SR-IOV control/status fields, a large SPI programming block, SPI and SQ performance counters, CGTS/CGTT clock-gating controls, shader program resource/user-data registers for PS/VS/GS/ES/HS/LS, SQC/SQ configuration fields, and ends in the SQ thread-trace mask family. Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for GFX8-era AMD GPUs, not Ceph filesystem code.

## Purpose

`gfx_8_0_sh_mask.h` supplies the bit layouts for GFX8 hardware registers. GFX8 driver code combines these masks with register-address macros from `gfx_8_0_d.h`, value enums from `gfx_8_0_enum.h`, and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD`, MMIO accessors, and PM4 packet builders. The header lets the driver pack or decode register fields without open-coded bit positions.

This chunk primarily supports:

- RLC streaming performance monitor setup, including per-block sample delays and global mux/ring controls.
- RLC GPU IOV virtualization control, firmware/scratch interfaces, function scheduling, VF/PF reset signaling, SDMA save/restore status, SMU/RLC responses, and interrupt force/disable masks.
- Pixel shader input interpolation and barycentric setup through `SPI_PS_INPUT_CNTL_0..31`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, and `SPI_BARYC_CNTL`.
- Shader export, ring, arbitration, debug, wave lifetime, and context-save state through SPI configuration registers.
- Shader program base, trap base, trap memory, resource, user-data, late-allocation, and resource-limit fields for PS, VS, GS, ES, HS, and LS stages.
- Per-CU SPI resource reservation and enable masks for 16 CUs.
- CGTS/CGTT clock-gating and light-sleep controls for SPI, PC, BCI, SQ, SQG, and per-CU shader sub-blocks.
- SPI and SQ performance-counter select/readout registers, including counter modes, bin thresholds, SQC client/bank/SIMD masks, SPM modes, and 64-bit low/high counter pairs.
- SQC/SQ configuration, DSM, cache, writeback, random priority, credits, interrupt message, power throttle, timestamp, and thread-trace buffer/mask fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. Its exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>_MASK` identifies the bits occupied by a field in a 32-bit register.
- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- Full-register data, counter, address-low, and response fields use `0xffffffff` masks.
- High address fields for shader trap/program bases often use an 8-bit mask, reflecting the high portion accepted by GFX8 register encoding.
- Repeated indexed families, such as `SPI_PS_INPUT_CNTL_0..31`, `SPI_RESOURCE_RESERVE_CU_0..15`, `SPI_SHADER_USER_DATA_*_0..15`, `SPI_WF_LIFETIME_*`, and `SQ_PERFCOUNTER0..15`, are part of the ABI-like hardware metadata surface and must remain index-aligned with the offset header.

Major macro families in this chunk include:

- `RLC_SPM_*_PERFMON_SAMPLE_DELAY`, `RLC_SPM_GLOBAL_MUXSEL_*`, `RLC_SPM_RING_RDPTR`, and `RLC_SPM_SEGMENT_THRESHOLD`: streaming performance monitor sample delay, mux selection, ring read pointer, and segment threshold fields.
- `RLC_GPU_IOV_*` and `RLC_GPM_VMID_THREAD2`: SR-IOV/PF/VF control, command/status, time quantum, active function ID, microcode and scratch access, F32 control/reset, SDMA context status, virtual FLR request, interrupt, busy, scheduler, and VMID/thread fields.
- `SPI_PS_INPUT_CNTL_0..31`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, and `SPI_BARYC_CNTL`: pixel shader input offsets, defaults, flat shade, cylindrical wrap, point-sprite attributes, FP16 interpolation, valid flags, interpolation enable/address masks, point-sprite override, interpolation count, and barycentric position controls.
- `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT`: position, depth, and color export format fields.
- `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0`, and `SPI_ARB_CYCLES_1`: SPI time-slice order and duration controls. GFX8 init code programs `SPI_ARB_PRIORITY` through `REG_SET_FIELD`.
- `SPI_CDBG_SYS_*`, `SPI_GDBG_*`, `SPI_RESET_DEBUG`, `SPI_DEBUG_*`, and `SPI_SLAVE_DEBUG_BUSY`: shader-stage debug enablement, trap base/memory, trap mask/config, debug reads, busy bits, and reset-debug disable fields.
- `SPI_RESOURCE_RESERVE_CU_*` and `SPI_RESOURCE_RESERVE_EN_CU_*`: per-CU reserved VGPR, SGPR, LDS, wave, and barrier resources plus enable/type/queue masks.
- `SPI_PERFCOUNTER*`, `SPI_PERFCOUNTER*_SELECT*`, and `SPI_PERFCOUNTER_BINS`: SPI performance counter readout, event selection, counter mode, and bin threshold fields.
- `CGTS_*` and `CGTT_*`: coarse-grain tree shader and clock-gating controls, including per-CU SP/LDS/SQ/TA/SQC/TD/TCP control/override/busy-override fields and SPI/PC/BCI/SQ/SQG clock on-delay/off-hysteresis/override bits.
- `SPI_WF_LIFETIME_*`, `SPI_CSQ_WF_ACTIVE_*`, `SPI_GDS_CREDITS`, `SPI_SX_*`, and trap-screen registers: wave lifetime limits/status, active wavefront counts, GDS credits, export/scoreboard buffer sizes, and pre-shader trap-screen address/mask/minimum register fields.
- `SPI_SHADER_TBA_*`, `SPI_SHADER_TMA_*`, `SPI_SHADER_PGM_*`, `SPI_SHADER_PGM_RSRC*_*`, `SPI_SHADER_USER_DATA_*`, and `SPI_SHADER_LATE_ALLOC_VS`: shader trap/program addresses, shader resource fields, user SGPR payloads, scratch/trap/wave-count/exception controls, streamout controls, CU enable/wave limits, and late VS allocation.
- `SQ_CONFIG`, `SQ_FIFO_SIZES`, `SQ_RANDOM_WAVE_PRI`, `SQ_DSM_CNTL`, `SQC_DSM_CNTL`, `SQC_CONFIG`, `SQC_CACHES`, `SQC_WRITEBACK`, `SQ_REG_CREDITS`, and `SQ_INTERRUPT_*`: shader queue and shader cache configuration/status/diagnostic/cache-control fields.
- `SQ_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_MASK`, `SQ_PERFCOUNTER_CTRL2`, `SQ_PERFCOUNTER*_LO/HI`, and `SQ_PERFCOUNTER*_SELECT`: SQ counter enable/rate/flush controls, shader-array masks, force enable, 64-bit counter readouts, event selection, SQC bank/client masks, SPM mode, SIMD mask, and perf mode.
- `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, `SQ_LDS_CLK_CTRL`, `SQ_POWER_THROTTLE*`, `SQ_TIME_*`, and `SQ_THREAD_TRACE_*`: CU force-on masks, power throttle thresholds/intervals, SQ timestamp, thread-trace base/size, and selected CU/SH/SIMD/VM/stall capture masks.

## Control Flow

This header has no runtime control flow; all behavior is compile-time macro substitution.

The implied driver flow is:

1. GFX8-specific code includes `gca/gfx_8_0_d.h`, `gca/gfx_8_0_enum.h`, and this shift/mask header.
2. A caller selects a register address from `gfx_8_0_d.h`.
3. The caller reads, writes, builds a context-state PM4 packet, creates an MQD, snapshots debug/perf state, or polls a status register.
4. The caller packs or extracts fields with the generated mask/shift pair, usually through helper macros.
5. The resulting value programs GPU hardware state or decodes volatile hardware status.

Concrete consumers in this tree include `gfx_v8_0.c`, which uses `REG_SET_FIELD` to program `SPI_ARB_PRIORITY`, update `RLC_SPM_VMID`, decode and set RLC/CGTS clock-gating state, issue SQ commands, and handle SQ interrupt fields. KFD VI MQD code includes this header and uses matching GFX8 shift/mask definitions when initializing compute queue descriptors, trap settings, memory type fields, doorbells, and context-save controls. Clear-state headers carry reset/context values for many SPI registers in this chunk.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe fields in live GPU registers and context images whose values may be global engine state, per-context graphics state, per-queue compute state, firmware-managed state, performance-monitor state, volatile status, or side-effect triggers.

RLC SPM and SQ/SPI performance counter state persists until the driver or firmware reprograms the relevant registers. Counter low/high readouts are volatile and require a coherent sampling sequence outside this header. SPM sample delays, mux selection, ring read pointers, and segment thresholds shape profiler output and can affect attribution or sampling quality.

RLC GPU IOV fields are virtualization-sensitive. `VF_ENABLE`, `VF_NUM`, `ACTIVE_FCN_ID`, function switching fields, time quanta, virtual reset request bits, SDMA preempt/save/restore status, busy masks, interrupt force/disable controls, and scheduler data reflect PF/VF scheduling and reset state. Incorrect field packing can disrupt SR-IOV isolation, leave a VF stuck, misreport SDMA context save/restore, or confuse firmware handshakes.

SPI shader input, interpolation, export format, barycentric, and shader program resource fields are context programming state. Values are usually submitted through command streams or clear-state/context programming paths and persist as GPU context state until changed. Misprogramming can surface as rendering corruption, broken interpolation, invalid shader exports, bad scratch or user SGPR setup, or shader trap failures.

Shader TBA/TMA/PGM low/high fields and trap-screen base/mask fields are split address encodings. The header gives only bit widths; alignment, address shifting, and valid virtual/physical address rules come from the surrounding driver sequence and hardware spec. KFD VI MQD setup, for example, shifts trap base and memory addresses before storing them in descriptor fields.

CGTS/CGTT registers control clock gating and light sleep. `gfx_v8_0.c` reads `CGTS_SM_CTRL_REG` to report CG support and writes `SM_MODE`, `SM_MODE_ENABLE`, `OVERRIDE`, `LS_OVERRIDE`, and monitor address fields when toggling medium-grain clock gating. Per-CU CGTS override/busy-override fields can force or block sub-block gating for SP, LDS, SQ, TA/SQC, TD, and TCP. These settings persist globally and can affect power, latency, and hang behavior.

SQ cache, DSM, writeback, credits, random priority, interrupt, throttle, timestamp, and thread-trace registers are a mix of persistent configuration and volatile readback. Thread-trace base/size/mask fields describe capture buffers and selection filters; bad values can capture the wrong CU/SH/SIMD/VM, overflow buffers, or miss stalls. SQ power throttle controls can intentionally constrain shader execution.

Reserved, unused, and full-register data fields are present because the header is generated. Their presence does not make arbitrary writes safe. Register programming code should preserve undocumented bits unless the hardware sequence requires a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GFX8 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_d.h` supplies matching register address macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_enum.h` supplies many field value enums used with these masks.
- AMDGPU helper macros and MMIO/PM4 accessors in the driver provide packing, extraction, register read/write, and command-stream emission.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c` is the main GFX8 graphics/RLC/clock-gating consumer.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v8.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_vi.c` integrate these definitions with KFD compute queue management, MQDs, trap setup, context save/restore, CU masks, and memory type/ATC controls.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_vi.c` is an SR-IOV/MxGPU-adjacent consumer that includes the same GFX8 register headers.
- Power-management SMU8/VI paths include the header for GFX8 register fields related to clock, power, and firmware-managed controls.
- Clear-state headers such as `clearstate_vi.h` list reset/context values for many SPI state registers whose fields are described here.

Driver subsystems that depend indirectly on this metadata include graphics context programming, command submission, shader trap/debug support, KFD queue creation and preemption, SR-IOV virtualization, RLC firmware handshakes, GPU reset and safe-mode paths, clock-gating/power-management policy, debugfs/hang dumps, and performance monitoring.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask still compiles but programs or decodes the wrong hardware bits.
- This chunk starts mid-family at `RLC_SPM_GDS_PERFMON_SAMPLE_DELAY__RESERVED__SHIFT` and ends mid-family after `SQ_THREAD_TRACE_MASK__VM_ID_MASK__SHIFT`. File-level reconciliation must merge adjacent chunks to complete both boundaries.
- Repeated families are index-sensitive. `SPI_PS_INPUT_CNTL_0..31`, `SPI_RESOURCE_RESERVE_CU_0..15`, `SPI_SHADER_USER_DATA_*_0..15`, `SPI_WF_LIFETIME_STATUS_0..20`, and `SQ_PERFCOUNTER0..15` must keep identical layouts where expected and correct exceptions where the hardware differs.
- Some `SPI_PS_INPUT_CNTL` fields differ between indices: early entries include cylindrical wrap and point-sprite attribute fields, while later entries omit some of those fields. Consumers must not assume every index has every field.
- Address split fields such as shader TBA/TMA/PGM and trap-screen bases require correct high/low composition and alignment. Shifting by the wrong granularity can produce valid-looking but incorrect trap or program addresses.
- Full-register masks are easy to misuse in read-modify-write code. Response, data, scheduler, counter, and userdata registers are not semantically interchangeable even when they all expose `0xffffffff` data fields.
- RLC GPU IOV fields affect virtualization isolation and reset behavior. Incorrect VF/PF identifiers, time quanta, FLR masks, command execute/status bits, or SDMA busy/save/restore interpretation can destabilize SR-IOV scheduling.
- Clock-gating override bits are power and liveness sensitive. Clearing overrides too early or setting light-sleep controls without the required RLC/SerDes idle sequencing can cause hangs or misleading clock-gating capability reporting.
- Performance counters require coherent low/high sampling and correct event/mode selection. The header does not describe latch order, overflow behavior, mux programming, or block-specific valid event IDs.
- `SQC_CACHES` invalidate/complete and `SQC_WRITEBACK` are side-effect-like cache controls. Treating them as ordinary passive state risks stale instruction/scalar cache data or false completion.
- SQ interrupt, thread-trace, debug, and wave lifetime fields interact with diagnostics and error handling. Bad masks can hide trap/thread-trace interrupts, misreport SQ event sources, or flood interrupts.
- Resource reservation and CU mask fields can reduce visible compute capacity or starve selected queue classes if enable/type/queue masks are wrong.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for all GFX8/VI AMDGPU and KFD files that include `gfx_8_0_sh_mask.h`.
- Mechanical comparison of every `__SHIFT` and `_MASK` in lines 9310-13970 against AMD's authoritative GFX8 register database.
- Static checks that each register field in this chunk has a matching address macro in `gfx_8_0_d.h` where applicable and that mask/shift pairs align.
- Repeated-family checks for index continuity and field-layout consistency across `SPI_PS_INPUT_CNTL`, `SPI_RESOURCE_RESERVE_CU`, `SPI_SHADER_USER_DATA`, `SPI_WF_LIFETIME`, `SPI_PERFCOUNTER`, and `SQ_PERFCOUNTER` groups.
- GFX8 boot/init tests that exercise `SPI_ARB_PRIORITY`, shader memory/program setup, clear-state restore, and graphics context switching.
- KFD queue tests that validate VI MQD initialization, user SGPR fields, trap TBA/TMA setup, CU masks, CWSR context-save fields, queue priority, and doorbell behavior.
- SR-IOV/MxGPU tests that cover VF enablement, active function reporting, VF/PF time quanta, virtual FLR request/response, SDMA save/restore status, and RLC/SMU response paths.
- RLC SPM/perf tests that program sample delays, mux selection, ring pointers, SPI/SQ counter selects, and low/high counter readout while checking monotonicity and overflow handling.
- Clock-gating tests that toggle MGCG/CGTS/CGLS/MGLS paths, verify `CGTS_SM_CTRL_REG` override/light-sleep behavior, and watch for hangs during RLC SerDes sequencing.
- Shader-interpolation and export rendering tests that exercise flat shade, point sprites, FP16 interpolation, barycentric modes, position/Z/color export formats, and user-data payloads.
- Debug and trap tests that validate shader trap bases, trap-screen bounds, SQ interrupt decoding, thread-trace buffer base/size/mask capture, wave lifetime warnings, and SPI/SQ busy status dumps.
- Cache and SQ state tests that validate SQC invalidate/writeback completion, SQ credits/fifo settings, power throttle behavior, and SQ timestamp/thread-trace readback.

Runtime warning signals include GPU hangs during clock-gating transitions, VF reset failures, SDMA save/restore timeouts, invalid shader trap dispatch, corrupted interpolation/export output, KFD queue launch/preemption failures, stale shader cache behavior, impossible busy/status dumps, performance counters stuck at zero, or thread-trace buffers missing expected events.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002715`. It covers lines 9310-13970 of `gfx_8_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the RLC SPM sample-delay boundary at the start and the SQ thread-trace family after the end, then place these GFX8 RLC/SPI/SQ/CGTS register masks in the full generated header map.
