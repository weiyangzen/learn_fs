# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h lines 13902-19048

## Scope

This chunk is part of the generated AMD GFX 8.1 ASIC register field mask header. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>_MASK` value and a matching `<REGISTER>__<FIELD>__SHIFT` value. There are no functions, structs, enums, storage definitions, or executable control-flow blocks in this range.

The covered line range starts in shader/SQC control masks, moves through SQ performance, thread trace, wave debug, shader resource descriptor, instruction-encoding, SX export/blend, TCC/TCA/TA/TD/TCP cache/texture, GDS, VGT/IA/WD primitive pipeline, and ends in WD debug register masks.

## Purpose

The purpose of this header chunk is to give AMDGPU driver code stable symbolic names for GFX 8.1 register bitfields. Callers combine these masks and shifts with register addresses from companion ASIC register headers to read, write, pack, unpack, and validate values for Southern Islands/GCN-style graphics hardware blocks.

The constants let driver code avoid hard-coded bit positions when it:

- Builds values for MMIO register writes.
- Extracts status and counter fields from MMIO register reads.
- Programs shader resources, image resources, samplers, and scratch descriptors.
- Configures performance counters and thread trace collection.
- Decodes wave state, instruction words, interrupts, and debug buses.
- Tunes or diagnoses cache, clock-gating, GDS, VGT, IA, and WD hardware blocks.

## Macro Interface

Every definition follows the same ABI-like macro pattern:

- `<REG>__<FIELD>_MASK` is the bit mask for a field in a 32-bit register word.
- `<REG>__<FIELD>__SHIFT` is the right-shift count needed to align the masked field to bit 0.

Typical use by consumers is expected to look like:

```c
field = (reg_value & REG__FIELD_MASK) >> REG__FIELD__SHIFT;
reg_value = (reg_value & ~REG__FIELD_MASK) |
            ((field_value << REG__FIELD__SHIFT) & REG__FIELD_MASK);
```

This chunk does not provide helper macros to perform those operations; it only exports the constants. Correctness therefore depends on callers pairing the right mask with the right shift and constraining field values before shifting.

## Register Families Covered

### SQ and SQC Shader Core

The opening section covers shader queue and shader instruction/data cache controls:

- `SQC_DSM_CNTL` controls DSM/irritator data selection and single-write enables for SQC instruction and data cache banks.
- `SQ_DSM_CNTL` exposes wavefront stall, SPI backpressure, SGPR/LDS/SP DSM irritator data selection, and single-write enables.
- `SQ_RANDOM_WAVE_PRI`, `SQ_REG_CREDITS`, and `SQ_FIFO_SIZES` describe scheduling priority, command/register credit accounting, overflow status, and FIFO sizing.
- `CC_GC_SHADER_RATE_CONFIG` and `GC_USER_SHADER_RATE_CONFIG` carry shader rate knobs such as DPFP rate, SQC balance disable, and half-LDS configuration.
- `CC_SQC_BANK_DISABLE` and `USER_SQC_BANK_DISABLE` mask SQC bank-disable fields per SQC instance.

These masks are integration points for shader initialization, clock/power tuning, debug/stress modes, and low-level fault diagnostics.

### SQ Performance Counters and Clock/Power Controls

The chunk defines 16 SQ performance counter low/high data registers and 16 `SQ_PERFCOUNTER*_SELECT` registers. Select fields include event select, SQC bank/client masks, SPM mode, SIMD mask, and performance mode. `SQ_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_MASK`, and `SQ_PERFCOUNTER_CTRL2` gate counters by shader stage, sampling rate, force-enable, and shader array masks.

Clock and power fields include:

- `CGTT_SQ_CLK_CTRL`, `CGTT_SQG_CLK_CTRL` with on-delay, off-hysteresis, and override bits.
- `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, `SQ_LDS_CLK_CTRL` for forcing CUs on per shader half.
- `SQ_POWER_THROTTLE` and `SQ_POWER_THROTTLE2` for min/max power, power delta, interval, ratio, and reference-clock selection.
- `SQ_TIME_HI` and `SQ_TIME_LO` timestamp fields.

These definitions are consumed by performance monitoring, power management, and debug code that must preserve unrelated fields during read-modify-write sequences.

### SQ Thread Trace

Thread trace register masks include:

- Trace buffer base/size registers: `SQ_THREAD_TRACE_BASE`, `SQ_THREAD_TRACE_BASE2`, and `SQ_THREAD_TRACE_SIZE`.
- Selection and gating: `SQ_THREAD_TRACE_MASK`, `SQ_THREAD_TRACE_MODE`, `SQ_THREAD_TRACE_TOKEN_MASK`, `SQ_THREAD_TRACE_TOKEN_MASK2`, and `SQ_THREAD_TRACE_PERF_MASK`.
- Runtime state: `SQ_THREAD_TRACE_WPTR`, `SQ_THREAD_TRACE_STATUS`, `SQ_THREAD_TRACE_CNTR`, and `SQ_THREAD_TRACE_HIWATER`.
- User data payload registers `SQ_THREAD_TRACE_USERDATA_0` through `_3`.

This section also defines masks for decoded thread trace packet words: common, instruction, PC, userdata, timestamp, wave, misc, wave-start, register, compute-shader register, event, issue, and perf packet formats. These packet masks are useful for trace parsing tools and driver debug code that interpret trace memory after capture.

Risk is high when these fields drift from the hardware packet format: trace output may still be collected but parsed incorrectly, causing misleading profiling or debug data.

### Error Detection and Wave Debug

Error and wave-state fields include:

- `SQC_EDC_CNT`, `SQ_EDC_SEC_CNT`, `SQ_EDC_DED_CNT`, and `SQ_EDC_INFO` for single/double error counters and wave/SIMD/source/VMID attribution.
- Wave register masks for instruction words, program counter, execution mask, status, mode, trap status, hardware ID, GPR/LDS allocation, wait counters, M0, trap base/metadata addresses, and temporary trap registers.
- `SQ_IND_INDEX`, `SQ_IND_DATA`, and `SQ_CMD` for indexed wave/register access and SQ commands.
- `SQ_DEBUG_STS_GLOBAL`, `SQ_DEBUG_STS_GLOBAL2`, `SQ_DEBUG_STS_GLOBAL3`, `SQ_DEBUG_STS_LOCAL`, and `SQ_DEBUG_CTRL_LOCAL` for global/local SQ debug status.

These masks are used by wave dump, trap/debug, hang diagnosis, and EDC reporting paths. State represented here is hardware state, not persistent software state.

### Shader Resource, Image Resource, Sampler, and Scratch Descriptors

The chunk includes descriptor word layouts:

- `SQ_BUF_RSRC_WORD0` through `WORD3`: base address, high address, stride, record count, destination swizzles, numeric/data format, element size, index stride, TID addition, ATC, hash, heap, memory type, and resource type.
- `SQ_IMG_RSRC_WORD0` through `WORD7`: base address, min LOD, data/number format, width/height/depth/pitch, perf modifier, interlace, swizzle selectors, mip levels, tiling index, ATC, type, array bounds, metadata address, compression, alpha/color transform, and lost-bit fields.
- `SQ_IMG_SAMP_WORD0` through `WORD3`: clamp modes, anisotropy, depth compare, unnormalized coordinates, coordinate truncation, degamma, filter modes, LOD bounds/bias, border color pointer/type, and precision fixes.
- `SQ_FLAT_SCRATCH_WORD0/1`, `SQ_M0_GPR_IDX_WORD`, and `SH_MEM_*` masks for scratch and shader memory configuration.

These fields are central to command submission and shader setup. Incorrect packing can corrupt GPU memory access, sampling behavior, cacheability, or VM/ATC behavior.

### Instruction Encoding Masks

The chunk defines bit layouts for several GCN instruction formats:

- Scalar formats: `SQ_SOP1`, `SQ_SOP2`, `SQ_SOPC`, `SQ_SOPK`, `SQ_SOPP`, and `SQ_SMEM_0/1`.
- Vector formats: `SQ_VOP1`, `SQ_VOP2`, `SQ_VOP3_0`, `SQ_VOP3_0_SDST_ENC`, `SQ_VOP3_1`, `SQ_VOPC`, `SQ_VOP_SDWA`, and `SQ_VOP_DPP`.
- Memory/export/interp formats: `SQ_MUBUF_0/1`, `SQ_MTBUF_0/1`, `SQ_MIMG_0/1`, `SQ_FLAT_0/1`, `SQ_DS_0/1`, `SQ_EXP_0/1`, and `SQ_VINTRP`.
- `SQ_INST` exposes the full 32-bit instruction encoding word.

These masks are integration points for disassembly, debug decode, trace decode, trap handling, and any tooling that inspects wave instruction state. They are not instruction implementations.

### SX Export/Blend Block

The SX section includes:

- `CGTT_SX_CLK_CTRL0` through `CGTT_SX_CLK_CTRL4` clock-gating controls.
- `SX_DEBUG_BUSY` through `SX_DEBUG_BUSY_4` detailed busy/valid state across position, column, DBIF, buffer, and command paths.
- `SX_DEBUG_1` blend/quad/pixel optimization debug controls.
- Four SX performance counters with select, mode, low, and high masks.
- `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, and per-MRT `SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT`.

Consumers are expected in color export, render backend interaction, perf monitoring, and hang debug paths. Debug fields are numerous and hardware-specific, making stale documentation or wrong masks a diagnostic risk.

### TCC, TCA, TA, TD, TCP, and TCI Cache/Texture Paths

Cache and texture-related masks include:

- `TCC_CTRL`, `TCC_EDC_CNT`, redundancy/execute-disable/DSM controls, TCC/TCA clock-gating, and TCC/TCA performance counters.
- `TD_CNTL`, `TD_STATUS`, TD debug, DSM, counters, scratch, and clock-gating.
- `TA_CNTL`, `TA_CNTL_AUX`, TA base address, status, debug, performance counters, scratch, and clock-gating.
- `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, channel steering, address configuration, credits, counters, buffer address hashing, EDC counters, watchpoint address/control, GATCL1 control, DSM control, and clock disable controls.
- `TC_CFG_L1_LOAD_POLICY0/1`, `TC_CFG_L1_STORE_POLICY`, `TC_CFG_L2_LOAD_POLICY0/1`, `TC_CFG_L2_STORE_POLICY0/1`, `TC_CFG_L2_ATOMIC_POLICY`, and L1/L2 volatile controls.
- `TCI_STATUS`, `TCI_CNTL_1`, and `TCI_CNTL_2`.

These definitions support cache invalidation, address hashing, VMID-aware watchpoints, cache policy selection, EDC reporting, and performance counter setup. Integration is sensitive to hardware generation because cache policy encodings and channel/bank layouts are ASIC-specific.

### GDS, GWS, OA, and Context Switch State

The GDS section is large and covers:

- Global control/status: `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ENHANCE`, `GDS_ENHANCE2`, and clock-gating.
- Fault and EDC status: `GDS_PROTECTION_FAULT`, `GDS_VM_PROTECTION_FAULT`, `GDS_EDC_CNT`, `GDS_EDC_GRBM_CNT`, `GDS_EDC_OA_DED`.
- Direct read/write and burst access registers.
- Atomic controls, operands, results, base/size, offsets, destination, and completion status.
- GWS resource control/status, resource counts, global reset masks for 64 resources, and targeted resource reset.
- Ordered append controls: counters, address, inc/dec, ring size, VMID masks, reset, reset masks, and CGPG restore identity fields.
- Debug registers `GDS_DEBUG_REG0` through `GDS_DEBUG_REG6` and GDS performance counters.
- Per-VMID base/size masks for GDS, GWS per-VMID base/size, and OA VMID masks.
- Context-switch status and counters for compute, graphics, vertex shader, and pixel shader slots.

These fields expose state that is directly tied to GPU queues, VMIDs, ordered append, global wave synchronization, and context switching. Misprogramming risks include VM isolation mistakes, lost or stuck GWS resources, incorrect context-save/restore accounting, and hard-to-debug hangs.

### VGT, IA, and WD Primitive Pipeline

The VGT/IA/WD section defines masks for graphics primitive setup and draw control:

- Draw/event initiators and event address fields.
- DMA base, index type, number of instances, size, max size, primitive type, and DMA control.
- Immediate data, index type, index counts, primitive ID enable/reset, vertex count, reuse controls, min/max index, index offset, and multi-primitive reset.
- Tessellation and geometry shader controls: output path, HOS controls, group primitive/vector controls, vector format controls, GS mode/on-chip control/output primitive type, cache invalidation, reset debug, FIFO depths, GS/ES/VS ratios, shader stage enables, LS/HS config, tessellation factor parameters, tessellation distribution, TF ring/memory, offchip buffering, GS instance count, ESGS/GSVS ring sizes/offsets/itemsizes, and max wave IDs.
- Streamout configuration, buffer sizes/offsets/strides/filled sizes, opaque draw offsets, and streamout buffer config.
- IA and VGT busy status, debug select/data registers, and clock-gating controls.
- WD status, QoS, debug select/data registers, and detailed `WD_DEBUG_REG0` through `WD_DEBUG_REG7` pipeline/FIFO/handshake state.
- Shader/primitive array masks: `CC_GC_SHADER_ARRAY_CONFIG`, `GC_USER_SHADER_ARRAY_CONFIG`, `CC_GC_PRIM_CONFIG`, and `GC_USER_PRIM_CONFIG`.

These constants are used by graphics pipeline setup, draw packet handling, tessellation/GS programming, streamout, multi-VGT/dual-IA configuration, and hang/debug diagnostics. They are especially stateful because many fields represent live hardware FIFOs, busy bits, or resource counts.

## Dependencies

This chunk has no include directives in the line range and no direct C dependencies. Its practical dependencies are:

- Companion register offset/address headers for GFX 8.1, typically in the same `asic_reg/gca` generated header set.
- AMDGPU register access helpers and macros that perform read-modify-write, masking, and field packing.
- Hardware documentation or generated register database used to produce `gfx_8_1_sh_mask.h`.
- Consumers in DRM/AMDGPU code that use these masks for SI/CI/VI-era GCN register programming and diagnostics.

Because the constants are generated hardware ABI data, the main dependency contract is semantic rather than link-time: each mask/shift pair must match the actual GFX 8.1 register layout.

## Control Flow

There is no runtime control flow in this chunk. Control flow appears only in downstream code that uses these constants. Conceptually, downstream access follows these patterns:

- Read a register and test status bits such as busy, full, valid, fault, overflow, or EDC counters.
- Build a control value from multiple fields, then write the register.
- Configure counters by programming select/mode fields, then read low/high counter values.
- Program descriptors by packing resource/sampler/image fields before GPU consumption.
- Decode trace, interrupt, wave, instruction, or debug words by applying mask and shift pairs.

The absence of helper code means there is no central runtime guard against invalid field values or mismatched mask/shift use.

## State and Persistence Behavior

The file itself is static compile-time data. It persists only as source code and preprocessor output.

The registers described by the masks represent volatile GPU hardware state. Some fields are configuration state that persists until reset or reprogramming, such as cache policy, clock-gating overrides, shader stage enables, descriptor words, and VMID GDS bounds. Other fields are transient status/counter/debug state, such as busy bits, FIFO levels, EDC counters, wave status, trace write pointers, performance counters, and protection-fault latches.

Driver suspend/resume, GPU reset, context switch, and queue teardown code must not assume this header stores state. It only names fields that other code may save, restore, or inspect.

## Integration Points

Important integration surfaces include:

- AMDGPU register read/write helpers for GFX 8.1 hardware blocks.
- Graphics pipeline setup code for VGT, IA, WD, tessellation, GS, and streamout.
- Shader setup and descriptor construction paths for buffer, image, sampler, scratch, and static memory configuration.
- Debugfs, GPU hang collection, wave dump, trap, thread trace, and performance counter code.
- Cache and memory-system setup paths for SQC, TCP, TCC, TCA, TCI, GATCL1, ATC, and TC policy controls.
- GDS/GWS/OA allocation, VMID protection, context switch, and reset handling.
- Hardware generation gating that selects GFX 8.1-specific headers and avoids applying these masks to incompatible ASICs.

## Risks

- Mask/shift drift from hardware documentation can silently corrupt register programming.
- Pairing a mask from one register with a shift from another register can compile cleanly and fail only at runtime.
- Unmasked shifted values can bleed into adjacent fields if callers do not apply the mask after shifting.
- Writing debug, DSM, force-miss, force-hit, clock override, or reset fields in production paths can cause severe performance loss or hangs.
- Reserved and unused fields appear throughout the chunk; callers should preserve them unless hardware documentation explicitly says otherwise.
- Many fields are status or counter latches. Treating them as ordinary writable configuration bits can break diagnostics or clear important evidence.
- Descriptor field mistakes can cause GPU virtual memory faults, wrong cacheability/ATC behavior, incorrect image sampling, or data corruption.
- VMID-specific GDS/GWS/OA masks are isolation-sensitive; incorrect base, size, or mask values can expose or corrupt another VMID's resources.
- Instruction and trace decode masks must match the exact ISA/hardware generation; reusing them for another GFX version can produce plausible but wrong debug output.

## Test Signals

Useful validation signals for changes to this chunk or its generator include:

- Build coverage for AMDGPU paths that include `gfx_8_1_sh_mask.h`.
- Static checks that every `*_MASK` has a corresponding `*__SHIFT` in the same register/field family.
- Register pack/unpack unit tests where available: `(value << shift) & mask` round-trips expected field values and does not affect neighboring fields.
- GPU boot and mode-setting on affected GFX 8.1 hardware.
- Shader/resource descriptor tests using buffer, image, sampler, scratch, ATC, compression, and format fields.
- Perf counter tests for SQ, SX, TCC/TCA, TA/TD/TCP, and GDS counter select/read paths.
- Thread trace capture and parser validation against known packet streams.
- GPU reset and hang-dump tests that verify busy/status/debug fields decode correctly.
- GDS/GWS/OA allocation, reset, VMID isolation, and context-switch tests.
- Graphics pipeline tests covering indexed draws, tessellation, geometry shader, streamout, primitive restart/reset, and multi-VGT/dual-IA cases.

## Chunk Notes for Merge

This is a partial chunk report for one oversized source file. It should be merged with neighboring chunk reports before producing the final source-tree-aligned per-file research document for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h`.

No final per-file report is produced here. The merge lane should retain that this chunk covers macro definitions only and that the source path is a generated GFX 8.1 register mask header, not an implementation file.
