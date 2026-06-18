# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_sh_mask.h lines 13971-19163

## Purpose

This chunk is generated-style bitfield metadata for the AMD GFX 8.0 graphics core register interface. It contains C preprocessor constants that map hardware register fields to their 32-bit masks and low-bit shifts. The definitions are not executable code; they are the symbolic contract used by AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, raw `RREG32`/`WREG32`, packet register programming, golden-setting tables, debug capture code, and shader/debug tooling to compose or decode register values without hard-coding bit positions.

The range starts in the middle of shader queue/thread-trace definitions, covers shader resource descriptors, wave and instruction encodings, SQ/SQC interrupt and cache controls, clock-gating controls for several graphics blocks, SX/TCC/TCA/TCP/TD/TA/GDS performance and debug registers, GDS VMID/resource partitioning, VGT draw/index/tessellation/GS/streamout controls, WD debug state, and IA/VGT debug status. It ends in the middle of `VGT_DEBUG_REG1`, so the following chunk owns the remaining fields for that register.

## Important APIs, Types, And Data

There are no C functions, structs, enums, runtime variables, locks, or allocation paths in this chunk. The public surface is a large set of macros following the generated AMD ASIC register naming pattern:

- `REGISTER__FIELD_MASK` gives the unshifted mask for a field inside a 32-bit register word.
- `REGISTER__FIELD__SHIFT` gives the field's low bit index.
- Full-word payload fields use masks such as `0xffffffff`, for example thread-trace userdata, counter values, descriptor addresses, instruction words, wave registers, GDS read/write data, index counts, primitive IDs, tessellation levels, and debug-data payloads.
- Repeated register families are flattened into individual macro names, for example `GDS_VMID0_BASE` through `GDS_VMID15_BASE`, `GDS_GWS_RESET0/1`, `TC_CFG_L1_LOAD_POLICY0/1`, and `WD_DEBUG_REG0` through `WD_DEBUG_REG10`.

Major register families in this range include:

- SQ thread trace setup and decode: `SQ_THREAD_TRACE_MASK`, `SQ_THREAD_TRACE_USERDATA_0..3`, `SQ_THREAD_TRACE_MODE`, `SQ_THREAD_TRACE_CTRL`, `SQ_THREAD_TRACE_TOKEN_MASK`, `SQ_THREAD_TRACE_TOKEN_MASK2`, `SQ_THREAD_TRACE_PERF_MASK`, `SQ_THREAD_TRACE_WPTR`, `SQ_THREAD_TRACE_STATUS`, `SQ_THREAD_TRACE_CNTR`, `SQ_THREAD_TRACE_HIWATER`, and decoded thread-trace packet formats such as `SQ_THREAD_TRACE_WORD_CMN`, `INST`, `INST_PC_*`, `INST_USERDATA_*`, `TIMESTAMP_*`, `WAVE`, `MISC`, `WAVE_START`, `REG_*`, `REG_CS_*`, `EVENT`, `ISSUE`, and `PERF_*`.
- SQ shader-visible descriptors and wave state: `SQ_BUF_RSRC_WORD0..3`, `SQ_IMG_RSRC_WORD0..7`, `SQ_IMG_SAMP_WORD0..3`, `SQ_FLAT_SCRATCH_WORD0/1`, `SQ_M0_GPR_IDX_WORD`, `SQ_IND_INDEX`, `SQ_CMD`, `SQ_IND_DATA`, `SQ_REG_TIMESTAMP`, `SQ_CMD_TIMESTAMP`, `SQ_HV_VMID_CTRL`, `SQ_WAVE_INST_DW0/1`, `SQ_WAVE_PC_LO/HI`, `SQ_WAVE_IB_DBG0/1`, `SQ_WAVE_EXEC_LO/HI`, `SQ_WAVE_STATUS`, `SQ_WAVE_MODE`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_HW_ID`, `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_IB_STS`, `SQ_WAVE_M0`, trap-base registers, trap-memory registers, and temporary trap registers `SQ_WAVE_TTMP0..11`.
- SQ/SQC cache, interrupt, and instruction formats: `SQC_EDC_CNT`, `SQC_GATCL1_CNTL`, `SQC_ATC_EDC_GATCL1_CNT`, `SQ_EDC_SEC_CNT`, `SQ_EDC_DED_CNT`, `SQ_EDC_INFO`, `SQ_INTERRUPT_WORD_CMN`, `SQ_INTERRUPT_WORD_AUTO`, `SQ_INTERRUPT_WORD_WAVE`, and instruction encodings for `SQ_SOP*`, `SQ_VOP*`, `SQ_MUBUF`, `SQ_MTBUF`, `SQ_MIMG`, `SQ_FLAT`, `SQ_DS`, `SQ_EXP`, `SQ_VINTRP`, `SQ_INST`, and `SQ_WREXEC_EXEC_*`.
- Clock-gating and block control: `CGTT_SX_CLK_CTRL0..4`, `CGTT_TCP_CLK_CTRL`, `CGTT_TCI_CLK_CTRL`, `CGTT_GDS_CLK_CTRL`, `CGTT_IA_CLK_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_WD_CLK_CTRL`, `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `TCC_CGTT_SCLK_CTRL`, and `TCA_CGTT_SCLK_CTRL`, each with `ON_DELAY`, `OFF_HYSTERESIS`, and soft override fields.
- Shader export/cache/memory blocks: `SX_DEBUG_BUSY*`, `SX_DEBUG_1`, `SX_PERFCOUNTER*`, `TCC_CTRL`, `TCC_EDC_CNT`, `TCC_REDUNDANCY`, `TCC_EXE_DISABLE`, `TCC_DSM_CNTL`, `TCC_PERFCOUNTER*`, `TCA_CTRL`, `TCA_PERFCOUNTER*`, `TD_CNTL`, `TD_STATUS`, `TD_DSM_CNTL`, `TD_PERFCOUNTER*`, `TA_CNTL`, `TA_CNTL_AUX`, `TA_STATUS`, `TA_DEBUG_*`, `TA_PERFCOUNTER*`, `SH_MEM_BASES`, `SH_MEM_APE1_BASE/LIMIT`, `SH_MEM_CONFIG`, `SH_STATIC_MEM_CONFIG`, and `SH_HIDDEN_PRIVATE_BASE_VMID`.
- Texture/cache policy and watchpoints: `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, `TCP_CNTL2`, `TCP_ADDR_CONFIG`, `TCP_CREDIT`, `TCP_CHAN_STEER_LO/HI`, `TCP_BUFFER_ADDR_HASH_CNTL`, `TCP_EDC_CNT`, `TCP_GATCL1_CNTL`, `TCP_ATC_EDC_GATCL1_CNT`, `TCP_GATCL1_DSM_CNTL`, `TCP_DSM_CNTL`, `TCP_WATCH0..3_ADDR_H/L`, `TCP_WATCH0..3_CNTL`, and `TC_CFG_L1/L2_*_POLICY*` plus volatile-policy registers.
- GDS and GWS/OA state: `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ATOM_*`, `GDS_RD_*`, `GDS_WR_*`, `GDS_WRITE_COMPLETE`, `GDS_PROTECTION_FAULT`, `GDS_VM_PROTECTION_FAULT`, `GDS_DEBUG_*`, `GDS_DSM_CNTL`, `GDS_EDC_*`, `GDS_ENHANCE*`, `GDS_PERFCOUNTER*`, VMID partition registers `GDS_VMID0..15_BASE/SIZE`, global-wave-sync windows `GDS_GWS_VMID0..15`, ordered-append masks `GDS_OA_VMID0..15`, `GDS_GWS_RESET0/1`, `GDS_GWS_RESOURCE*`, `GDS_OA_RESET*`, `GDS_OA_ADDRESS`, `GDS_OA_COUNTER`, `GDS_OA_CNTL`, `GDS_OA_INCDEC`, `GDS_OA_RING_SIZE`, and GDS context-switch counters/status registers.
- VGT, WD, and IA frontend pipeline state: `VGT_DRAW_INITIATOR`, `VGT_EVENT_INITIATOR`, `VGT_DMA_*`, `VGT_INDEX_TYPE`, draw count and instance registers, primitive ID/reset, vertex reuse, index bounds, output path, tessellation controls, GS ring/sizing/on-chip controls, cache invalidation, shader-stage enablement, streamout buffer/config registers, `VGT_MULTI_PRIM_IB_RESET_*`, `VGT_RESET_DEBUG`, `VGT_FIFO_DEPTHS`, `VGT_CNTL_STATUS`, `WD_CNTL_STATUS`, `WD_QOS`, `WD_DEBUG_REG0..10`, `IA_MULTI_VGT_PARAM`, `IA_CNTL_STATUS`, `IA_DEBUG_REG0..9`, and the start of `VGT_DEBUG_REG0/1`.

## Control Flow

This header chunk has no runtime control flow. Its effect is through preprocessing and compilation: consumers include `gfx_8_0_sh_mask.h` with the matching GFX 8 offset header, then use these masks and shifts to read, write, decode, or emit values for GFX8 hardware registers.

Typical consumer flow is:

1. Select the GFX8 register headers by compiling the GFX8/VI AMDGPU code path.
2. Read or synthesize a 32-bit register value using `RREG32`, `WREG32`, packet3 register writes, or a golden-setting table entry.
3. Use these `*_MASK` and `*__SHIFT` constants directly or via `REG_GET_FIELD`/`REG_SET_FIELD` to isolate or place fields.
4. Program the register, store decoded state in driver structures, or export captured values through debug/hang-info paths.

Visible integration in the tree follows that pattern. `gfx_v8_0.c` includes this header, defines GFX8 golden-setting arrays with registers covered by this chunk such as `mmTA_CNTL_AUX`, `mmTCC_CTRL`, `mmTCP_ADDR_CONFIG`, `mmCGTT_GDS_CLK_CTRL`, `mmCGTT_IA_CLK_CTRL`, `mmCGTT_WD_CLK_CTRL`, `mmCGTT_SX_CLK_CTRL0..4`, `mmCGTT_TCI_CLK_CTRL`, `mmCGTT_TCP_CLK_CTRL`, and `mmCGTT_VGT_CLK_CTRL`, and initializes `gds_reg_offset` with `mmGDS_VMID*_BASE`, `mmGDS_VMID*_SIZE`, `mmGDS_GWS_VMID*`, and `mmGDS_OA_VMID*`. The same driver path reads GDS sizing registers into `adev->gds`, writes `mmGDS_COMPUTE_MAX_WAVE_ID` in ring setup, and captures `ixSQ_WAVE_STATUS` through the wave debug path.

Because many of these registers are command-processor or per-shader-engine state, the real runtime ordering is imposed by GFX initialization and command submission rather than by this header. Golden settings run early during device setup. GDS VMID windows are reset or programmed when address spaces and queues are initialized. VGT draw/index/tessellation registers are normally driven by command packets. Wave debug and thread-trace state is read only after selecting a wave/SIMD or enabling a trace session. Clock-gating controls must be programmed in a context where the relevant graphics blocks can tolerate clock control changes.

## State And Persistence Behavior

The macros do not store state. The state they describe lives in hardware registers, command streams, memory descriptors, or driver fields populated from those registers.

State categories in this chunk include:

- Persistent hardware configuration until reset, suspend/resume, power transition, or explicit reprogramming: clock-gating controls, `TA_CNTL_AUX`, `TCC_CTRL`, `TCP_ADDR_CONFIG`, `TCP_BUFFER_ADDR_HASH_CNTL`, `SH_MEM_CONFIG`, `SH_STATIC_MEM_CONFIG`, cache policy registers, GDS VMID/GWS/OA partition registers, GDS enhance/OA controls, VGT topology/GS/tessellation controls, and FIFO depth registers.
- Per-dispatch, per-draw, or command-stream state: VGT draw initiators, DMA/index registers, primitive type, instance counts, vertex index bounds, streamout buffer size/offset/filled-size registers, shader-stage enablement, GS ring sizing, and primitive-ID/reset controls.
- Debug/observation state: SQ wave state, SQ thread-trace words and status, SQ/SQC/TCP/TCC/GDS EDC counters, SX/WD/IA/VGT debug registers, block busy bits, FIFO fullness/emptiness, context-switch status counters, protection fault fields, and performance counter low/high registers.
- Address and resource descriptor state: SQ buffer/image/sampler descriptor words, scratch base/size fields, trap base/memory addresses, TCP watchpoint address/control registers, and GDS atom/read/write addresses and payloads.
- Command or handshake state: trace reset/autoflush/interrupt/wrap controls, `SQ_CMD`, TCP invalidate, GDS atom controls and complete bits, GDS/GWS/OA reset registers, VGT cache invalidation, and draw/DMA initiator registers.

Some of this state is restored from driver tables after reset or resume, while other state is emitted in command streams for each workload. GDS partition state is particularly persistent from the driver's perspective: `gfx_v8_0.c` caches global GDS sizing and programs per-VMID base/size/GWS/OA windows so user queues see the expected resource partitioning. Debug and counter fields are transient snapshots and should not be treated as stable configuration.

## Dependencies

This chunk depends on the rest of the generated GFX8 register header set:

- `gfx_8_0_offset.h` supplies the matching `mm*` and `ix*` register identifiers used with these field masks, such as `mmGDS_VMID0_BASE`, `mmGDS_COMPUTE_MAX_WAVE_ID`, `mmTCP_ADDR_CONFIG`, `mmTA_CNTL_AUX`, `mmTCC_CTRL`, `mmCGTT_*`, and `ixSQ_WAVE_STATUS`.
- Adjacent sections of `gfx_8_0_sh_mask.h` define fields before line 13971 and after line 19163, including the beginning of `SQ_THREAD_TRACE_MASK` before this chunk and the remainder of `VGT_DEBUG_REG1` after this chunk.
- GFX8 AMDGPU consumers include `gfx_v8_0.c`, `vi.c`, SDMA/VCE/SMU8 paths that include the same mask header, and shared register helper macros from the DRM AMDGPU tree.
- Packet building and register access code supplies the actual IO mechanisms: direct MMIO helpers, indexed SQ debug accessors, packet3 `SET_*_REG` writes, and golden-setting application helpers.
- Hardware/firmware behavior is the ultimate dependency. These constants must match the GFX8 ASIC specification; they are not self-validating and cannot be inferred safely from similar GC/GFX generations.

Macro names are intentionally similar across GFX6, GFX7, GFX8, GFX9, and later GC headers, but field widths and semantics can differ. Consumers must pair the offset and mask headers for the active ASIC generation.

## Integration Points

Important integration points include:

- GFX8 golden settings: registers from this chunk are present in `gfx_v8_0.c` golden tables. Mask/value pairs for `TA_CNTL_AUX`, `TCC_CTRL`, `TCP_ADDR_CONFIG`, `CGTT_*`, and `SX_DEBUG_1` rely on the same hardware bit layout represented here.
- GDS resource management: the `gds_reg_offset` table and GDS initialization paths use VMID base/size, GWS, and OA registers covered by this chunk. Correct fields are required for per-VMID GDS memory, global wave sync resources, and ordered-append resource isolation.
- Command submission and ring setup: VGT DMA/index/draw fields, primitive controls, streamout controls, shader-stage controls, and `GDS_COMPUTE_MAX_WAVE_ID` are emitted through command packets, so these masks define the contract between kernel command construction and the graphics frontend.
- Debug and hang analysis: wave capture reads `ixSQ_WAVE_STATUS`, and adjacent SQ wave/debug fields describe the values needed to identify wave ID, SIMD, CU, shader engine, queue, VMID, trap state, execution masks, instruction buffer state, and exception status. WD/IA/VGT/SX debug fields provide lower-level pipeline busy and FIFO diagnostics.
- Thread trace and profiling: `SQ_THREAD_TRACE_*` setup/status fields and decoded packet-word fields integrate with performance tooling and low-level diagnostics. `*_PERFCOUNTER*_SELECT`, `*_LO`, and `*_HI` registers describe block-specific counter selection and readback.
- Cache, memory, and coherency policy: SQC/TCP/TCC cache control, invalidation, EDC, L1/L2 policy, volatile, watchpoint, and channel steering registers interact with VM, command processor synchronization, SDMA/graphics interop, and shader memory semantics.
- Power and clock management: CGTT controls for SX, TCP, TCI, GDS, IA, VGT, WD, TD, TA, TCC, and TCA integrate with VI/GFX8 clock-gating defaults and power-management flows.
- Shader/user-mode ABI surface: SQ resource descriptor words, image sampler words, wave status/mode/trap fields, and instruction encoding fields mirror hardware formats that userspace compilers and command streams must match, even when the kernel only observes or validates pieces of them.

## Risks

- A wrong mask or shift compiles cleanly but changes the wrong hardware bits. In this chunk, likely symptoms include GPU hangs, bad golden-setting programming, broken GDS partitioning, corrupted indexed draws, incorrect tessellation/GS/streamout behavior, cache incoherency, or unusable debug captures.
- Several families contain command/action bits rather than passive configuration. Misusing `SQ_CMD`, `TCP_INVALIDATE`, `GDS_ATOM_CNTL`, `GDS_GWS_RESET*`, `GDS_OA_RESET*`, `VGT_DRAW_INITIATOR`, `VGT_EVENT_INITIATOR`, or `VGT_CACHE_INVALIDATION` can trigger hardware actions at the wrong time.
- Debug/status fields are mixed with writable policy fields. Treating `SQ_THREAD_TRACE_STATUS`, `TA_STATUS`, `TCP_STATUS`, `GDS_CNTL_STATUS`, `WD_DEBUG_REG*`, `IA_DEBUG_REG*`, or `VGT_DEBUG_REG*` as ordinary configuration can produce meaningless writes or mask real hang diagnostics.
- GDS VMID/GWS/OA partition registers are isolation-sensitive. Incorrect base/size/mask fields can let one queue or VMID consume resources intended for another, or can make GDS unavailable to workloads that expect it.
- Cache and coherency fields have system-wide effects. Bad `SQC_GATCL1_CNTL`, `TCP_GATCL1_CNTL`, `TCP_CNTL`, `TCC_CTRL`, `TC_CFG_*`, or volatile-policy programming can show up as intermittent shader memory corruption, stale data, unexpected force-miss behavior, or large performance cliffs.
- Resource descriptor and instruction encoding fields are ABI-like. If `SQ_BUF_RSRC_*`, `SQ_IMG_RSRC_*`, `SQ_IMG_SAMP_*`, or `SQ_*` instruction masks do not match hardware, tools that decode descriptors/instructions or any kernel-side validation/debugging can misinterpret user workloads.
- Many registers contain reserved, spare, or unused fields. Raw full-register writes can disturb these bits; masked read/modify/write or golden-setting masks are safer when the hardware programming guide requires preservation.
- The chunk starts and ends mid-register-family. The previous chunk owns earlier `SQ_THREAD_TRACE_MASK` fields, and the next chunk owns the rest of `VGT_DEBUG_REG1`. Any final per-file analysis must merge adjacent chunks before making complete claims about those registers.
- Generated ASIC register headers should not be hand-edited casually. Updates should normally come from regenerated hardware register specifications so offset headers, masks, comments, and consumer code stay synchronized.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for GFX8/VI AMDGPU configurations that include `gca/gfx_8_0_sh_mask.h`, ensuring all referenced `mm*`, `ix*`, `*_MASK`, and `*__SHIFT` symbols resolve with the matching offset header.
- Golden-setting smoke tests on GFX8 hardware: boot, initialize graphics, apply `gfx_v8_0.c` golden tables, and verify no register access faults or early GPU hangs around `TA_CNTL_AUX`, `TCC_CTRL`, `TCP_ADDR_CONFIG`, CGTT, and SX debug programming.
- GDS tests that initialize per-VMID GDS, GWS, and OA resources, then run compute/graphics queues using GDS atomics and ordered append. Failures may appear as resource allocation errors, wrong GDS readback, protection faults, or hangs.
- Wave debug and hang-dump tests that read `ixSQ_WAVE_STATUS` and adjacent wave registers after synthetic shader traps or hangs, checking that decoded wave, SIMD, CU, SE, queue, VMID, trap, and execution status fields are plausible.
- Thread-trace/profiling validation that enables thread trace, checks `SQ_THREAD_TRACE_STATUS`/`WPTR`, captures tokens, and decodes instruction, wave, event, register, timestamp, and performance words using the packet masks in this chunk.
- Cache/coherency stress using shader buffer/image loads/stores, atomics, TCP/SQC invalidation paths, SDMA/graphics interop, and VMID changes. Stale reads, VM faults, EDC counter changes, or performance regressions point at bad cache-policy or invalidation field handling.
- Draw/index frontend tests covering direct draws, indexed draws, instancing, primitive restart, multi-primitive IB reset, tessellation, GS, streamout, and opaque draws. These exercise `VGT_*`, `WD_*`, and `IA_*` register families.
- Suspend/resume, GPU reset, and runtime clock-gating tests. These stress whether persistent CGTT, cache policy, GDS, and frontend registers are restored and whether busy/debug status remains meaningful after transitions.
- Performance counter tests for SQ/SX/TCC/TCA/TCP/TD/TA/GDS counters, ensuring counter select/mode fields and high/low readback fields produce stable, monotonic, or workload-correlated results as expected.
