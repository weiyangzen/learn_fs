# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 21916-24636

## Scope

This chunk is part of the generated AMD GC 9.4.3 shift/mask register header. It contains preprocessor constants only: hardware register fields are represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for composing and decoding 32-bit MMIO register values.

The range starts in the middle of the `CB_COLOR3_DCC_CONTROL` family, covers most of the color-buffer target slots 4 through 7, then spans these generated address blocks:

- `xcd0_gc_gfxudec`: command processor, graphics pipeline, shader trace/cache, depth/color query, GDS, and SPI control fields.
- `xcd0_gc_gccanedec`: GC CANE correctable/uncorrectable error status fields.
- `xcd0_gc_perfddec`: performance counter data registers for CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, and RMI.
- `xcd0_gc_utcl2_atcl2pfcntrdec`, `xcd0_gc_utcl2_vml2prdec`, and `xcd0_gc_utcl2_l2tlbprdec`: UTCL2/VM L2/L2TLB performance counter data fields.
- `xcd0_gc_perfsdec`: the beginning of performance counter selector/control fields for CPG, CPC, CPF, CP perfmon, CP draw-window filtering, and the first portion of `GRBM_PERFCOUNTER0_SELECT`.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_9_4_3_sh_mask.h` is the bit-level ABI between GC 9.4.3 driver code and AMD graphics hardware registers. The sibling `gc_9_4_3_offset.h` header supplies register offsets such as `regCB_COLOR4_INFO`, `regCP_COHER_CNTL`, `regSQ_THREAD_TRACE_CTRL`, `regGDS_ATOM_CNTL`, `regCP_PERFMON_CNTL`, and `regGRBM_PERFCOUNTER0_SELECT`; this header supplies the field positions and masks used with those offsets.

Driver code consumes these definitions through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `SOC15_REG_OFFSET`, command-stream packets, and register dump/debug tooling. The macros also allow common code to share field names across ASIC-specific generated headers while still using the correct GC 9.4.3 layout.

## Important Macro Families

### Color Buffer Targets

The opening section completes the tail of `CB_COLOR3_DCC_CONTROL` and the remaining `CB_COLOR3_*` metadata registers, then defines `CB_COLOR4_*` through `CB_COLOR7_*`. These families describe render-target state:

- `*_BASE` and `*_BASE_EXT` carry the low and high portions of 256-byte-aligned color surface base addresses.
- `*_ATTRIB2`, `*_VIEW`, `*_INFO`, and `*_ATTRIB` encode mip dimensions, slice ranges, mip level, format, numeric type, component swap, fast clear, compression, DCC enable, CMASK address type, sample/fragment count, color/FMASK swizzle mode, resource type, and RB/pipe alignment.
- `*_DCC_CONTROL` contains DCC policy fields such as overwrite combiner disable, key-clear enable, compressed and uncompressed block sizes, color transform, independent 64-byte blocks, lossy precision, and constant encode controls.
- `*_CMASK`, `*_FMASK`, `*_CLEAR_WORD*`, and `*_DCC_BASE` provide metadata-surface base addresses and clear words.

These definitions are context/render-target state, not general software data structures. Incorrect masks can make render-target programming write the wrong surface address, format, compression mode, or metadata layout.

### Command Processor And Coherency Windows

The `xcd0_gc_gfxudec` block starts with CP end-of-pipe, stream-out, primitive counter, pipe-stat, scratch, append/fence, semaphore, atomic pre-operation, memory read/write, and DMA fields. Most low/high address or counter registers are full-width `0xFFFFFFFFL` fields, while control registers expose narrower command bits.

Important CP control families include:

- `CP_PIPE_STATS_CONTROL`, `CP_STREAM_OUT_CONTROL`, and `CP_STRMOUT_CNTL`, which gate pipeline statistics and stream-out accounting.
- `SCRATCH_REG0..7`, `SCRATCH_UMSK`, and `SCRATCH_ADDR`, which define CP scratch data, user mask, and scratch address selection.
- `CP_SIG_SEM_ADDR_*`, `CP_WAIT_SEM_ADDR_*`, `CP_SEM_WAIT_TIMER`, and `CP_WAIT_REG_MEM_TIMEOUT`, which support semaphore and wait-reg-mem sequencing.
- `CP_DMA_ME_*`, `CP_DMA_PFP_*`, and `CP_DMA_CNTL`, which describe CP DMA source/destination addresses, commands, byte counts, SA/DA increment behavior, raw-wait, disable-write-confirm, and read-tag state.
- `CP_COHER_*` and `CP_ME_COHER_*`, which define coherency operation base, size, control, status, engine/VMID bits, cache action bits, GL2 probe behavior, and destination base state.
- `CP_PFP_IB_CONTROL`, `CP_PFP_LOAD_CONTROL`, command-buffer offsets/sizes, CE/IB base registers, EOP done event/data controls, metadata base registers, indirect draw/dispatch addresses, index base/type, GDS backup base, and sample status fields.

The command processor fields connect directly to ring execution, indirect buffer setup, event/fence completion, cache flush/invalidate sequencing, and low-level synchronization. The header has no sequencing logic; the owning CP/GFX code must still order writes, waits, and polling correctly.

### Graphics Pipeline, Shader Trace, SQC, DB, And GDS

The same block includes front-end and shader/debug controls:

- `RLC_GPM_PERF_COUNT_0/1` expose GPM performance counter and read-valid/counter-valid status fields.
- `GRBM_GFX_INDEX` selects SE/SA/instance targeting and broadcast modes for indexed graphics register access.
- `VGT_*`, `IA_MULTI_VGT_PARAM`, and `WD_*` fields cover primitive type, index type, stream-out buffer filled sizes, vertex-index bounds, primitive reset enable, draw instance/index counts, tessellation ring and offchip parameters, and work distributor buffer bases.
- `PA_SC_*`, `PA_SU_LINE_STIPPLE_VALUE`, and stereo/trap screen fields describe line stipple, screen extents, and raster/trap-screen debug counters.
- `SQ_THREAD_TRACE_*` fields define shader thread-trace base/size, token and performance masks, control/status, mode, write pointer, hi-water mark, counter, and userdata registers.
- `SQC_CACHES` and `SQC_WRITEBACK` expose shader instruction/cache invalidation, volatile behavior, client selection, force bits, writeback, and completion status.
- `DB_OCCLUSION_COUNT*` and `DB_ZPASS_COUNT*` provide query counter low/high fields.
- `GDS_RD_*`, `GDS_WR_*`, `GDS_WRITE_COMPLETE`, `GDS_ATOM_*`, and `GDS_GWS_*` fields describe GDS direct read/write, burst access, atomic operation setup/completion/readback, global-wave-sync resource selection, ownership/mask/counter state, and ordered-append ring control/address/incdec/ring size.
- `SPI_CONFIG_CNTL`, `SPI_CONFIG_CNTL_1`, `SPI_CONFIG_CNTL_2`, and `SPI_WAVE_LIMIT_CNTL` define shader processor interface policy such as GPR write priority, export priority order, SQG event enables, resource-management reset, thread-trace stall, allocation/export arbitration, pixel shader packer priority, PC-limit behavior, CRC/LBPW checks, CSG/CSC power-save disables, context-save wait overheads, and wave-slot limits.

These fields are a mix of persistent configuration, hardware-updated status, and command-like bits. Trace, cache, GDS atomic, and ordered-append registers are especially side-effect-prone because they represent active hardware engines rather than passive metadata.

### GC CANE Error Status

The `xcd0_gc_gccanedec` block defines `GC_CANE_ERR_STATUS`, `GC_CANE_UE_ERR_STATUS_LO/HI`, and `GC_CANE_CE_ERR_STATUS_LO/HI`. These fields expose GC CANE correctable and uncorrectable error bits across shader and graphics blocks, including CPF/CPC/CPG, TCP, SQ, SPI, TA, TD, WD, IA, VGT, PA_SC, PA_SU, DB, CB, SX, and GDS-style sources.

These masks are diagnostic and RAS-facing integration points. They can be used to decode hardware error status words, but this header does not define clear semantics, interrupt routing, recovery policy, or whether individual bits are sticky.

### Performance Counter Data

The `xcd0_gc_perfddec` and UTCL2-related blocks are dominated by low/high performance counter data registers. Families include:

- CP front-end counters: `CPG`, `CPC`, `CPF`, plus latency-stat data.
- Global and per-SE GRBM counters.
- Pipeline counters for `WD`, `IA`, `VGT`, `PA_SU`, `PA_SC`, `SPI`, `SQ`, `SX`, `GDS`, `TA`, `TD`, `TCP`, `TCC`, `TCA`, `CB`, `DB`, `RLC`, and `RMI`.
- UTCL2, VM L2, and L2 TLB counters: `ATC_L2_PERFCOUNTER_*`, `MC_VM_L2_PERFCOUNTER_*`, and `L2TLB_PERFCOUNTER_*`.

Most low registers expose a full-width `PERFCOUNTER` or `COUNTER_LO` field. High registers often split the low 16 bits of counter high data from a high-half `COMPARE_VALUE` field. Consumers need a coherent read strategy outside this header when sampling split 64-bit counters that may update while being read.

### Performance Counter Selection And Draw Filtering

The `xcd0_gc_perfsdec` portion begins performance-counter selector state:

- `CPG_PERFCOUNTER*`, `CPC_PERFCOUNTER*`, and `CPF_PERFCOUNTER*` selector registers pack `CNTR_SEL*`, `SPM_MODE`, and `CNTR_MODE*` fields.
- `CP_PERFMON_CNTL` controls CP perfmon state, SPM perfmon state, enable mode, and sample-enable behavior.
- `CPF_TC_PERF_COUNTER_WINDOW_SELECT` and `CPG_TC_PERF_COUNTER_WINDOW_SELECT` choose TC performance counter windows with `INDEX`, `ALWAYS`, and `ENABLE` bits.
- `CPF_LATENCY_STATS_SELECT`, `CPG_LATENCY_STATS_SELECT`, and `CPC_LATENCY_STATS_SELECT` choose latency-stat slots and expose `CLEAR` and `ENABLE` bits.
- `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_MASK_HI`, `CP_DRAW_WINDOW_HI`, `CP_DRAW_WINDOW_LO`, and `CP_DRAW_WINDOW_CNTL` provide draw-object and draw-window filtering controls for performance/debug measurement.
- The chunk ends in the first half of `GRBM_PERFCOUNTER0_SELECT`, after the busy-mask shift fields through `EA_BUSY_USER_DEFINED_MASK__SHIFT`; the corresponding `RMI` shift and all masks are in the following lines/chunk.

These selector fields configure what the data counters in the preceding block measure. They are persistent profiling/debug configuration until reset or reprogrammed.

## Control Flow

There is no runtime control flow in this chunk. It contains no C functions, structs, variables, allocations, locks, callbacks, loops, or branches. Its behavior is compile-time macro substitution.

The implied runtime flow is:

1. GC 9.4.3 driver code includes `gc_9_4_3_offset.h` and `gc_9_4_3_sh_mask.h`.
2. A call site chooses the relevant `reg*` offset for the active register.
3. The call site uses these `__SHIFT` and `_MASK` macros through helper macros or manual bit operations to compose, update, or decode a 32-bit register value.
4. The value is read or written through SOC15 MMIO helpers, RLC-safe accessors, packetized command streams, debug/register-dump code, KFD queue-management code, or profiling tooling.

Any real ordering, polling, W1C/W1S behavior, latching, privilege checks, XCC instance selection, or timeout policy lives in the surrounding AMDGPU/KFD code and hardware specification, not in this generated header.

## State And Persistence Behavior

The macros themselves hold no software state and persist nothing. They describe hardware-visible state:

- Color-buffer base, view, format, compression, DCC, CMASK, FMASK, and clear-word registers persist as render-target context state until changed by command streams, context restore, reset, or clear-state setup.
- CP scratch, append/fence, semaphore, atomic, DMA, IB, coherency, metadata, indirect draw/dispatch, index, GDS backup, and EOP registers represent command processor execution and synchronization state. Some are software-programmed, some are hardware-updated completion/status words.
- Shader trace, SQC cache, SPI control, GDS atomic/GWS/OA, DB query counters, and PA/SC trap-screen fields are active debug, cache, synchronization, and query surfaces with side effects.
- CANE error registers represent hardware error status and may contain sticky or latched bits depending on the underlying register semantics.
- Performance counter selector and control registers persist as measurement configuration. Counter data registers are hardware-updated while active, and low/high halves can race unless sampled using the correct hardware sequence.

Reserved fields and non-covered bits should be preserved in read-modify-write sequences unless the driver is deliberately writing a known full-register value from an authoritative table.

## Dependencies And Integration Points

The primary dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_offset.h`, which supplies the matching register offsets and base indices. `gc_9_4_3_default.h` and generation-adjacent enum headers provide reset/default values or selector enumerations where available.

Observed integration points in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c`, which includes this header with `gc_9_4_3_offset.h` for GC 9.4.3 initialization, register lists, queue setup, RLC/GFX handling, XCC-aware access, and diagnostics.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.c`, which includes `gc/gc_9_4_3_sh_mask.h` for GCVM/gfxhub register field programming and decoding on this ASIC family.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v9.c`, which include the same generated header for KFD/compute queue and GC 9.4.3 integration.
- Common AMDGPU helpers and command definitions in SOC15-era code, including register read/write helpers and packet definitions for copying perf counters or GDS atomic return data.
- Clear-state and context-state paths for render targets, which rely on matching CB register offsets/masks when restoring graphics context state.
- Profiling, debugfs, register-dump, RAS, GPU reset, suspend/resume, and bring-up code paths that read or program CP, SQ trace, SQC cache, SPI, GDS, CANE, and performance-monitoring registers.

Cross-generation similarity is high but not exact. Nearby GC 9.0, GC 10.x, GC 11.x, and GC 12.x headers expose many similarly named fields, but masks, offsets, address-block names, and complete register coverage can differ. Consumers must include the GC 9.4.3 header set that matches the active ASIC.

## Risks And Edge Cases

- Generated bitfield drift is the central risk. A wrong mask or shift compiles cleanly but can program unrelated hardware bits, leading to rendering corruption, hangs, bad synchronization, invalid profiling data, or broken recovery paths.
- This chunk starts mid-register at `CB_COLOR3_DCC_CONTROL` and ends mid-register at `GRBM_PERFCOUNTER0_SELECT`. The final merged report must join adjacent chunks before describing those two register families as complete.
- Color-buffer target slots 4 through 7 are highly repetitive. Mechanical generation or copy errors can affect only one MRT slot and show up as format, DCC, CMASK/FMASK, clear, or base-address bugs under multi-render-target workloads.
- Address high/low registers commonly encode aligned addresses rather than byte addresses. Callers must respect hardware granularity such as 256-byte base fields and not treat every field as a raw byte pointer.
- CP coherency, DMA, semaphore, wait, EOP, and indirect-buffer registers have strict sequencing requirements. The masks do not encode cache flush ordering, wait conditions, timeout handling, or engine ownership.
- GDS atomic, ordered append, GWS resource, and write-complete fields can be active command surfaces. Treating command/status bits as inert configuration can corrupt synchronization or return data.
- SQ thread trace and SQC cache control fields are debug/cache-management surfaces. Bad masks can stall shader execution, miss trace data, or leave stale instruction/data cache state.
- CANE error-status fields are RAS-sensitive. Mis-decoding correctable versus uncorrectable error status can hide real hardware faults or trigger unnecessary recovery.
- Performance counter data and select fields are dense and repeated. Wrong selector, mode, SPM, window, latency-stat, or draw-window masks can silently collect plausible but incorrect measurements.
- Low/high counter pairs can race with hardware updates. This header provides bit positions only, not a latching or retry algorithm.
- `GRBM_GFX_INDEX` and per-SE/SA targeting fields affect which graphics instance is addressed. Incorrect broadcast or instance selection can write only part of a multi-XCC/multi-SE device or unintentionally broadcast to all instances.

## Test And Validation Signals

Useful validation is a mix of generated-data checks, build coverage, and hardware-oriented runtime behavior:

- Build AMDGPU and KFD code paths that include `gc/gc_9_4_3_sh_mask.h`, including `gfx_v9_4_3.c`, `gfxhub_v1_2.c`, `amdgpu_amdkfd_gc_9_4_3.c`, and `kfd_device_queue_manager_v9.c`. Missing or renamed macros should fail at compile time.
- Mechanically compare this chunk against AMD's authoritative GC 9.4.3 register database. Each complete register in the range should have paired `__SHIFT` and `_MASK` entries, aligned masks, and matching offsets in `gc_9_4_3_offset.h`.
- Run static sanity checks for repeated CB slots 4-7, CP counter pairs, GDS fields, and performance counter families to catch one-slot or one-counter layout drift.
- Exercise graphics render-target workloads with multiple color attachments, DCC/FMASK/CMASK paths, fast clears, MSAA, mip/slice views, and context save/restore. Expected signals are correct rendering and no metadata corruption.
- Exercise CP DMA, wait-reg-mem, semaphore, fence/EOP, coherency, indirect draw/dispatch, stream-out, and query paths. Watch for hangs, timeouts, stale cache contents, missing fences, or wrong primitive/query counts.
- Exercise SQ thread trace and SQC cache invalidation/writeback flows where supported. Expected signals are valid trace buffers, correct write pointers/status, and no shader execution stalls outside intended trace control.
- Exercise GDS atomic/GWS/ordered-append behavior through compute and graphics workloads that use append/consume, atomics, and GDS backup/restore. Expected signals are correct synchronization and returned atomic data.
- Run RAS/error-injection or register-decode tests for GC CANE correctable and uncorrectable status where hardware or simulation support exists.
- Run profiling validation that programs CPG/CPC/CPF selectors, CP perfmon state, latency stats, draw-window filters, and the covered data counters. Counter movement should match controlled graphics, compute, memory, and shader workloads.
- On multi-XCC or partitioned GC 9.4.3 systems, validate instance-targeted register access through `GRBM_GFX_INDEX` and XCC-aware AMDGPU helpers so that reads/writes reach the intended hardware instance.

## Cross-Chunk Notes

The previous chunk owns the beginning of `CB_COLOR3_DCC_CONTROL`; this range begins with its later shift/mask fields and then continues into `CB_COLOR3_CMASK`. The next chunk owns the remainder of `GRBM_PERFCOUNTER0_SELECT`, starting after `EA_BUSY_USER_DEFINED_MASK__SHIFT`, including the `RMI` shift and all masks. The merge/reconciliation lane should stitch these artificial boundaries before producing the final per-file research document.
