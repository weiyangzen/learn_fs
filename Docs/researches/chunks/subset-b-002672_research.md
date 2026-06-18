# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 12227-14836

## Purpose

This chunk is generated AMD GPU register metadata for the GC 9.4.2 graphics core, used by the Linux AMDGPU driver path carried in this source tree. It defines symbolic bit positions and masks for hardware registers; it does not implement executable logic. The macros let GC 9.4.2 consumers build or decode 32-bit register values through `REG_GET_FIELD`, `REG_SET_FIELD`, SOC15 MMIO helpers, and packet-emission code without open-coded hex bit layouts.

The range starts at the tail of color-buffer target 5 state, completes color-buffer targets 6 and 7, then crosses several hardware decode blocks:

- `gc_gfxudec`: command processor EOP/fence/writeback, streamout and pipeline-stat counters, scratch registers, append/atomic preop registers, CP DMA, coherency, CE/IB/ST buffers, indirect draw/dispatch/index pointers, GDS backup, sample status, RLC GPM perf counters, GRBM indexing, VGT draw state, PA screen/trap state, SQ thread trace, SQC cache controls, DB counters, GDS direct/atomic/resource/OA registers, and SPI configuration.
- `gc_grbmdec`: GRBM status, reset, clock/power, read/write error, interrupt, trap, fence, scratch, and async VF violation fields.
- `gc_hypdec`: CP/RLC microcode RAM access, GRBM saved-register/CAM access, RLC GPU IOV virtualization, doorbell, timer, semaphore, scheduler, interrupt, SDMA save/restore status, and SDMA VM busy fields.
- `gc_padec`: the beginning of PA/VGT frontend decode, including DMA FIFO depths, cache invalidation, streamout delay, FIFO depths, IA status, and VGT status.

## Important APIs, Types, And Data

There are no C functions, structs, enums, variables, locks, or allocation APIs in this range. The public surface is the macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit.
- `REGISTER__FIELD_MASK` gives the field's 32-bit mask before shifting.
- Address-block comments such as `gc_gfxudec`, `gc_grbmdec`, `gc_hypdec`, and `gc_padec` identify hardware decode domains, not C namespaces.
- Full-width fields such as `SCRATCH_REG*__SCRATCH_REG*_MASK`, `CP_*_DATA_*`, `GDS_*_DATA`, `SQ_THREAD_TRACE_CNTR__CNTR_MASK`, and `GRBM_NOWHERE__DATA_MASK` expose whole register words.

Important register families in this chunk include:

- Color buffer target state for slots 5-7: `CB_COLOR{5,6,7}_INFO`, `ATTRIB`, `ATTRIB2`, `VIEW`, base/base-ext, CMASK, FMASK, clear words, DCC base, and `DCC_CONTROL`. These encode render target base addresses, mip dimensions, array slice/mip views, format/number type/component swap, fast clear/compression/DCC controls, sample/fragment counts, swizzle modes, resource type, and alignment flags.
- CP writeback and pipeline statistics: `CP_EOP_DONE_*`, `CP_EOP_LAST_FENCE_*`, `CP_STREAM_OUT_ADDR_*`, `CP_NUM_PRIM_*`, `CP_VGT_*COUNT*`, `CP_PA_*COUNT*`, `CP_SC_PSINVOC_COUNT*`, `CP_PIPE_STATS_*`, and `CP_STREAM_OUT_CONTROL`. These describe address, data, cache-policy, and counter layouts for EOP events, fences, streamout, and graphics pipeline accounting.
- CP scratch, append, atomic, semaphore, DMA, and coherency controls: `SCRATCH_REG0..7`, obsolete `SCRATCH_UMSK/ADDR`, `CP_APPEND_*`, `CP_*ATOMIC*PREOP*`, `CP_SIG_SEM_*`, `CP_WAIT_SEM_*`, `CP_WAIT_REG_MEM_TIMEOUT`, `CP_DMA_{PFP,ME}_*`, `CP_DMA_CNTL`, `CP_DMA_READ_TAGS`, `CP_COHER_*`, and `CP_ME_COHER_*`.
- Command-buffer and indirect-execution state: `CP_PFP_IB_CONTROL`, `CP_PFP_LOAD_CONTROL`, `CP_SCRATCH_INDEX/DATA`, `CP_RB_OFFSET`, CE/IB2/ST base/offset/buffer-size registers, `CP_EOP_DONE_EVENT_CNTL`, `CP_EOP_DONE_DATA_CNTL`, completion status, predication visibility, metadata base addresses, indirect draw/dispatch pointers, index base/type, GDS backup, and `CP_SAMPLE_STATUS`.
- Frontend VGT/PA/WD state: `GRBM_GFX_INDEX`, `VGT_GSVS_RING_SIZE`, `VGT_PRIMITIVE_TYPE`, `VGT_INDEX_TYPE`, streamout filled sizes, index range/offset/count/instance controls, tessellation factor memory/ring sizing, WD buffer bases, `IA_MULTI_VGT_PARAM`, line stipple/screen extent/trap screen registers, and the later `gc_padec` FIFO/status/cache invalidation registers.
- SQ/SQC trace and cache controls: `SQ_THREAD_TRACE_BASE/SIZE/MASK/TOKEN_MASK/PERF_MASK/CTRL/MODE/BASE2/TOKEN_MASK2/WPTR/STATUS/HIWATER/CNTR/USERDATA_*`, plus `SQC_CACHES` and `SQC_WRITEBACK`.
- DB/GDS/SPI support: DB occlusion and z-pass counters, direct GDS read/write/burst registers, GDS atomic operand/result/register windows, GWS resource controls, ordered-append controls, `SPI_CONFIG_CNTL`, `SPI_CONFIG_CNTL_1`, `SPI_CONFIG_CNTL_2`, and `SPI_WAVE_LIMIT_CNTL`.
- GRBM status and controls: `GRBM_STATUS`, `GRBM_STATUS2`, per-SE `GRBM_STATUS_SE0..SE3`, `GRBM_SOFT_RESET`, `GRBM_GFX_CLKEN_CNTL`, wait-idle clocks, read/write error decoders, interrupt enable, trap programming, power controls, UTCL2 invalidation ranges, fence ranges, scratch registers, and async VF violation reporting.
- Hypervisor and RLC IOV state: CP PFP/ME/CE/MEC and RLC GPM microcode address/data registers, saved-register select/data registers, GRBM CAM remap registers, VF enable/mask/doorbell status set/clear, RLC timers, hypervisor semaphores, RLC clock controls, IOV scheduler/config/status registers, active function ID, IOV interrupt state, scratch and ucode windows, F32 control/reset, virtual reset requests, RLC responses, and SDMA0-7 preempt/save/restore plus VM busy status.

## Control Flow

This header chunk has no runtime branches or call graph. Its only direct execution effect is C preprocessing: consumers include the header and compile the constants into register read-modify-write operations, packet payloads, or debug/status decoders.

Typical runtime use follows this pattern:

1. A GC 9.4.2-specific source such as `gfx_v9_4_2.c` or `amdgpu_amdkfd_aldebaran.c` includes both `gc_9_4_2_offset.h` and this `gc_9_4_2_sh_mask.h`.
2. Driver code selects an offset macro from the matching offset header and reads or writes the hardware register via SOC15 helpers such as `RREG32_SOC15`/`WREG32_SOC15`, or emits a PM4 packet that carries the same field layout.
3. Field helpers use the `__SHIFT`/`_MASK` pair to pack a field value into a 32-bit register word or extract a status field from a readback.

Representative downstream flows in the tree include GFX idle checks that read `GRBM_STATUS2` and test `RLC_BUSY`, cache flush/invalidate packet paths that emit `CP_COHER_CNTL` action bits, golden-setting paths that program `VGT_CACHE_INVALIDATION`, and RLC IOV firmware paths in later GFX files that write `RLC_GPU_IOV_UCODE_ADDR`, `RLC_GPU_IOV_UCODE_DATA`, and `RLC_GPU_IOV_F32_CNTL`. The GC 9.4.2 macro names here are the generation-specific definitions such consumers rely on.

## State And Persistence Behavior

The macros are stateless compile-time constants. All state described here is hardware state in the GPU or packet-visible command processor state.

The range describes several persistence classes:

- Context/render state that persists until reprogrammed by command streams, clear state, context restore, reset, or power transitions: color-buffer target state, VGT draw parameters, PA screen/trap controls, SPI limits, and tessellation/WD buffer bases.
- Command processor and synchronization state: EOP done addresses/data, last fence registers, append/fence registers, semaphore address/control fields, wait timeouts, CP DMA source/destination/command state, scratch registers, CE/IB/ST buffer windows, completion status, and predication/sample-status bits.
- Cache and coherency state: `CP_COHER_*`, `CP_ME_COHER_*`, `SQC_CACHES`, `SQC_WRITEBACK`, and `VGT_CACHE_INVALIDATION` define fields that trigger or observe cache writeback/invalidation and ordering operations.
- Status and diagnostic state: GRBM global/per-SE busy bits, read/write error fields, interrupt/trap registers, DB counters, GDS counters, SQ thread trace status/write pointer/counters, IA/VGT busy status, and SDMA save/restore/preempt state.
- Virtualization and firmware state: hypervisor CP/RLC ucode windows, saved-register and CAM remap data, RLC GPU IOV VF enable/mask/scheduler/doorbell/interrupt/reset status, active function IDs, semaphores, and VM busy masks.

Some fields are likely sticky, write-one-to-clear, clear-on-read, or command-triggering according to the hardware spec. This header does not encode those semantics. Consumers must know whether a register is safe to read, must be polled, or must be written only during quiescent/reset/firmware-load windows.

## Dependencies

This chunk depends on the generated AMD ASIC register ecosystem:

- `gc_9_4_2_offset.h` supplies matching register offsets. These masks are incomplete and unsafe without the corresponding offsets.
- Other GC 9.4.2 generated headers provide defaults and adjacent register ranges not covered by this line chunk.
- AMDGPU's SOC15 register helpers, PM4 packet emission helpers, and field helpers provide the operators that combine these constants with MMIO reads/writes or command packets.
- `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c` include this header directly for Aldebaran/GC 9.4.2 behavior.
- Shared AMDGPU definitions such as `soc15d.h` expose packet-level equivalents for some `CP_COHER_CNTL` bits; the register-mask values here must remain consistent with those command packet definitions where hardware reuses the same bit layout.

The data is a hardware ABI. It must stay synchronized with AMD's GC 9.4.2 register specification and with sibling generated files. Similar macro names exist in GC 9.1, 9.4.3, 10.x, 11.x, and 12.x headers, but fields can move or change width across generations.

## Integration Points

Primary integration points are:

- AMDGPU GFX 9.4.2 initialization, reset, idle, golden-setting, and command submission paths that include the GC 9.4.2 offset/mask pair.
- KFD/Aldebaran compute integration, where GC 9.4.2 register fields may be used for queue, VMID, debug, and performance/debug state.
- Render backend setup and context restore for color-buffer slots 5-7, including DCC, CMASK, FMASK, fast clear, sample count, resource type, swizzle mode, and base address programming.
- PM4 packet generation for EOP writebacks, fences, acquire-mem/coherency operations, CP DMA copies, semaphore waits/signals, streamout/stat counters, and indirect draw/dispatch/index state.
- Idle and hang diagnostics that decode `GRBM_STATUS`, `GRBM_STATUS2`, `GRBM_STATUS_SE*`, `IA_CNTL_STATUS`, `VGT_CNTL_STATUS`, `CP_*_COMPLETION_STATUS`, `CP_SAMPLE_STATUS`, and read/write error fields.
- SQ thread trace and profiling tooling that programs trace buffers, masks CUs/SHs/SIMDs/VMIDs/shader stages, checks full/busy/new-buffer/error status, and reads trace counters/userdata.
- SR-IOV and GPU virtualization flows that manipulate RLC GPU IOV VF enable/mask/status, doorbell set/clear, scheduler slots, active function IDs, per-SDMA save/restore state, and virtual reset requests.
- GDS/GWS/OA users that access GDS memory windows, atomics, resource counters, ordered append rings, and backup state.

## Risks

- Incorrect shifts or masks silently produce valid C code that targets the wrong hardware bits. In this chunk that can corrupt render-target metadata, fence addresses, DMA commands, cache invalidation policy, VMID/queue selection, trace programming, or virtualization state.
- The chunk mixes ordinary context state with control, status, reset, interrupt, trap, firmware, and hypervisor registers. Treating all fields as normal read-modify-write state is unsafe.
- Several address fields are split low/high and use alignment shifts, for example CP EOP/streamout/append/pipe-stat addresses and CB/GDS/WD base registers. Packing unaligned or incorrectly shifted addresses can redirect GPU writes or DMA.
- Coherency fields have system-wide effects. Misprogrammed `CP_COHER_CNTL`, `CP_ME_COHER_CNTL`, `SQC_CACHES`, or `VGT_CACHE_INVALIDATION` bits can leave stale shader, texture, color/depth, or memory-controller state visible to later work.
- `GRBM_SOFT_RESET`, `RLC_GPU_IOV_F32_RESET`, `RLC_GPU_IOV_VIRT_RESET_REQ`, interrupt force/disable, doorbell set/clear, and hypervisor semaphore fields are destructive or control-plane oriented. They should be used only in the intended reset/IOV/firmware sequences.
- Status fields such as GRBM busy bits, read/write errors, CP completion state, SQ trace status, GDS completion/resource state, and SDMA save/restore bits can be transient or sticky; tests must account for polling and clear behavior from the hardware spec.
- Cross-generation reuse is risky. GC 9.4.2 shares many names with GC 9.1 and GC 9.4.3, but field positions and register availability are not guaranteed identical.
- Because this file is generated register metadata, manual edits are high risk and should normally be replaced by regenerating the AMD register headers from the authoritative source.

## Test Signals

Useful validation signals include:

- Compile coverage for GC 9.4.2 include users, especially `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c`, with `REG_GET_FIELD` and `REG_SET_FIELD` expressions resolving against this header and `gc_9_4_2_offset.h`.
- Static consistency checks that every register represented in this chunk has a matching offset in `gc_9_4_2_offset.h` and, where applicable, a matching default/generated entry elsewhere in the ASIC register set.
- Boot and GFX initialization on Aldebaran/GC 9.4.2 hardware or emulation, confirming golden settings, context state, color-buffer clear state, GRBM idle polling, and reset flows complete without invalid-register warnings.
- Ring tests that exercise EOP writebacks/fences, CP DMA, acquire-mem cache invalidation, wait/signal semaphore, indirect draw/dispatch, index buffer setup, and streamout/pipeline-stat writes.
- Render and compute workloads that stress color targets 5-7, DCC/CMASK/FMASK, multisampling, fast clear, tessellation, streamout, line stipple/screen extents, GDS atomics, GWS resources, and ordered append.
- SQ thread trace/profiling tests that allocate a trace buffer, program mask/token/perf/mode fields, validate wrap/interrupt/full/error status, and decode the resulting trace stream.
- Virtualization/SR-IOV tests that load RLC IOV firmware, toggle VF enable/masks, process doorbell status set/clear, issue VF/PF reset requests, and observe per-SDMA preempt/save/restore and VM busy status.
- Suspend/resume, GPU reset, and RAS/hang-diagnostic runs that verify GRBM status/error fields, soft reset bits, RLC clock controls, microcode windows, and scratch/fence registers are restored or cleared in the expected sequence.
