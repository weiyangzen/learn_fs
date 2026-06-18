# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_6_0_sh_mask.h lines 1-4330

## Scope

This chunk is the opening section of the generated AMD GCA/GFX 6.0 shift/mask header. It begins with the AMD permissive license and `GFX_6_0_SH_MASK_H` include guard, then defines bit-field masks and shifts for the first third of the ASIC register database through the beginning of `GDS_DEBUG_REG0`.

The range is preprocessor metadata only. It contains no C functions, structs, enums, global variables, allocations, locks, callbacks, or executable branches. Its API surface is the generated `#define` namespace used by Southern Islands/GFX6 AMDGPU code to pack and unpack hardware register fields.

## Purpose

The file exposes the bit-level contract for GFX 6.0 hardware registers. Each field normally appears as a pair:

- `<REGISTER>__<FIELD>_MASK`, the bit mask for the field inside a 32-bit register value.
- `<REGISTER>__<FIELD>__SHIFT`, the low bit position for composing or decoding the field.

The companion offset header, `gca/gfx_6_0_d.h`, supplies the matching `mm*` register identifiers. Driver code combines these masks and shifts with MMIO helpers such as `RREG32`/`WREG32`, and with local field-building macros or generic register helpers, to program the GFX pipeline, command processor, compute dispatch state, color/depth buffers, tiling mode tables, and global data share registers.

Although this repository path is under `sources/distributed-fs/ceph-client`, this chunk is AMD GPU register metadata and has no Ceph filesystem behavior.

## Important APIs, Types, And Macro Families

The important "APIs" are macro families rather than callable routines:

- Header boundary: the AMD license and `GFX_6_0_SH_MASK_H` guard protect the generated definitions from duplicate inclusion.
- `CB_*`: color-buffer and render-backend fields. The range includes `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL`, constant blend color channels, `CB_CGTT_SCLK_CTRL`, complete `CB_COLOR0_*` through `CB_COLOR7_*` render-target layouts, `CB_COLOR_CONTROL`, debug buses, hardware-control/chicken-bit registers, CB performance counters, `CB_SHADER_MASK`, and `CB_TARGET_MASK`.
- `CC_*`, `GC_USER_*`: shader-array and render-backend configuration masks, including inactive CU bitmaps, double-precision rate, SQC balance disable, RB backend disable, RB daisy chain/redundancy, and SQC bank disable fields.
- `CGTS_*` and `CGTT_*`: clock-gating and clock tree controls for BCI, CP, GDS, IA, PA, PC, RLC, SC, SPI, SQ, SQG, SX0..4, TCI, TCP, and VGT. These fields encode on-delay, off-hysteresis, soft overrides, group overrides, and status/readback multiplexing.
- `CLIPPER_DEBUG_REG00` through `CLIPPER_DEBUG_REG19`: packed live-debug views for clipper state machines, FIFOs, primitive metadata, clip codes, vertex-store indices, event/null-primitive flags, clip-to-output counters, priority sequencer state, and per-state-machine valid/current-state counts.
- `COHER_DEST_BASE_*`: coherency destination base fields.
- `COMPUTE_*`: compute dispatch and shader-program state. This includes dispatch dimensions and starts, dispatch initiator controls, full/partial thread counts, program base address high/low, `COMPUTE_PGM_RSRC1/2` resource descriptors, wave/thread-group limits, static CU enables for shader engines, trap table/MA addresses, temporary ring sizing, 16 user-data dwords, and compute VMID.
- `CP_*`: command-processor, constant-engine, DMA, ring, interrupt, fence, performance, counter, and status fields. This family is the largest in the chunk and covers append/fence addresses, busy/stall status, CE/PFP/ME microcode and IB state, coherency control, CP DMA commands, ECC first-occurrence metadata, EOP done data, GDS atomic preops, GRBM free counts, IB1/IB2 descriptors, interrupt enable/status for rings 0..2, ME halt/step/icache controls, ring-buffer bases/control/read/write pointers for rings 0..2, ring VMIDs/priorities, semaphore/wait addresses, stream-out and pipe-stat addresses, CP/VGT/PA counters, VMID preempt/reset, and wait timeout configuration.
- `CS_COPY_STATE`: a small compute-state copy selector.
- `DB_*`: depth-buffer and stencil state. The range includes alpha-to-mask, DB clock gating, count controls, credit limits, debug/override controls, depth bounds/clear/control/info/size/slice/view fields, EQAA, FIFO/free-cacheline controls, HTILE base/surface, DB performance counters, preload and debug readback registers, render control/override, shader control, stencil compare/control/refmask/read/write base, subtile/watermark, Z info, Z pass counter, and Z read/write bases.
- `DEBUG_DATA` and `DEBUG_INDEX`: generic debug register data/index fields.
- `GB_*`: graphics backend address and tiling configuration, including `GB_ADDR_CONFIG`, backend map, EDC mode, GPU ID, and `GB_TILE_MODE0` through `GB_TILE_MODE31`. Each tile mode entry uses the same field layout for array mode, pipe config, tile split, micro tile mode, and sample split.
- `GDS_*`: global data share atomic and status fields. The visible portion covers atom base/control/complete/source/destination/read/size/offset/op fields, control/status conflict and busy flags, per-shader GPR phase selection, debug index/data, and the beginning of `GDS_DEBUG_REG0`.

There are no local type definitions. The effective data type is a 32-bit hardware register word interpreted through generation-specific masks and shifts.

## Control Flow

This header has no runtime control flow. The runtime pattern is supplied by consumers:

1. A GFX6-specific source file includes `gca/gfx_6_0_d.h` for register offsets and this mask header for field layouts.
2. Driver initialization, ring management, power management, command submission, or debug code selects an `mm*` register.
3. The caller composes a 32-bit value with a shift macro, an explicit mask, or a helper such as `REG_SET_FIELD`, then writes it through an MMIO accessor.
4. For read paths, the caller reads a register and isolates fields with the mask/shift pair.

Concrete integration visible in this tree includes `amdgpu/gfx_v6_0.c`, which includes this header, defines tile-mode builders from `GB_TILE_MODE0__*__SHIFT`, and programs `mmCP_RB0_CNTL` with `CP_RB0_CNTL__RB_RPTR_WR_ENA_MASK` during ring initialization. Other Southern Islands paths such as `amdgpu/si.c`, `pm/legacy-dpm/si_dpm.c`, `pm/legacy-dpm/si_smc.c`, and `amdgpu/dce_v6_0.c` also include this GFX6 mask header alongside related SMU, GMC, DCE, BIF, and OSS register headers.

## State And Persistence Behavior

The macros are compile-time constants and persist no software state. The hardware registers described by the macros are stateful:

- CB and DB render-target/depth/stencil fields hold current graphics pipeline state until command-stream updates, context switches, reset, or power transitions reprogram them.
- CP ring-buffer base/control/read/write pointer fields describe persistent queue state shared between CPU-visible memory, firmware/CP engines, and MMIO registers. Read-pointer writeback addresses and ring VMIDs must stay coherent with driver-owned ring memory.
- Compute program, dispatch, user-data, temporary-ring, and resource-limit fields describe active compute dispatch state. Their values are context-sensitive and can be replaced by command processor context management.
- Clock-gating fields persist as power-management configuration and can materially affect whether GFX blocks are gated, forced on, or placed in low-power timing modes.
- Debug, busy, stall, counter, clipper, GDS, CB, CP, and DB performance/status fields are hardware-updated telemetry. Values can change while the GPU is executing.
- Address and base fields are hardware addresses or address fragments. Many are in 256-byte or aligned-low-bit units, so the mask/shift constants encode only field placement, not full address validation.

The header does not encode access permissions, reset values, ordering requirements, or side effects. A full-width `0xffffffffL` data mask can represent a writable payload, a read-only counter, a debug snapshot, or an address fragment depending on the register.

## Dependencies

This chunk depends on generated-register consistency across:

- `gca/gfx_6_0_sh_mask.h`, which provides the field masks and shifts researched here.
- `gca/gfx_6_0_d.h`, which provides the matching GFX6 register offsets such as `mmCP_RB0_CNTL`.
- AMDGPU MMIO helpers and register-field helpers used by GFX6/SI driver code.
- Southern Islands GFX setup code in `amdgpu/gfx_v6_0.c`, plus SI platform and legacy DPM/SMC code that include the same header.
- Adjacent generated AMD register headers for SMU, GMC, DCE, BIF, and OSS blocks, because initialization code often programs several ASIC blocks in one sequence.
- Hardware and firmware expectations for CP/CE/PFP/ME rings, microcode, indirect buffers, DMA, wait/semaphore operations, EOP fences, and GDS atomics.

The generated macro names are part of the contract. Renaming, deleting, or moving fields can break compile-time references even when the numeric value is unchanged.

## Integration Points

Primary integration points in this source tree are:

- GFX6 ring initialization and command processor setup, including CP ring control, read/write pointer writeback, IB descriptors, queue thresholds, ME/PFP/CE microcode addressing, and CP DMA command fields.
- Southern Islands tiling setup. `gfx_v6_0.c` builds tile-mode values from `GB_TILE_MODE0__ARRAY_MODE__SHIFT`, `GB_TILE_MODE0__PIPE_CONFIG__SHIFT`, `GB_TILE_MODE0__TILE_SPLIT__SHIFT`, and `GB_TILE_MODE0__SAMPLE_SPLIT__SHIFT`.
- Render backend setup for color targets, blend controls, target/shader masks, CB caches, CMASK/FMASK, fast clear, compression, and backend-disable configuration.
- Depth/stencil setup for DB render state, HTILE/Z/stencil surfaces, depth bounds, EQAA, alpha-to-mask, count controls, and Z pass accounting.
- Compute dispatch setup for program resource descriptors, dispatch dimensions, user SGPR/user-data registers, scratch/temp-ring sizing, VMID, and static CU enablement.
- Power-management and clock-gating sequences for CGTS/CGTT and DB/CB clock controls, including soft overrides and on/off timing.
- Debug and hang-analysis paths that decode CP busy/stall status, clipper debug registers, CB/DB read-debug registers, performance counters, GDS debug state, and interrupt/status bits.

## Risks And Edge Cases

- Header/offset mismatch is the main correctness risk. GFX6 masks must be paired with GFX6 offsets; nearby generations reuse many names with changed fields.
- Repeated register banks can invite copy/paste mistakes. `CB_COLOR0_*` through `CB_COLOR7_*`, `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL`, `GB_TILE_MODE0` through `GB_TILE_MODE31`, and CP ring 0..2 registers are similar but not always semantically interchangeable.
- Some registers have aliases or family variants, such as generic `CP_RB_*` plus ring-specific `CP_RB0_*`, `CP_RB1_*`, and `CP_RB2_*`. Consumers must use the register intended by the hardware programming sequence.
- Full-width masks do not imply safe full-register writes. Counter, status, debug, address, microcode-data, and payload registers may be read-only, write-one-to-clear, alignment constrained, or side-effectful.
- Address fields frequently omit low alignment bits or store high address fragments. Incorrect shifts or truncation can silently point CP, CB, DB, GDS, or coherency logic at the wrong memory.
- Ring-buffer fields affect CPU/GPU synchronization. Incorrect `RB_BUFSZ`, `RB_BLKSZ`, read-pointer writeback enable/address, VMID, or endian swap settings can hang command submission or corrupt memory.
- Clock-gating override fields can hide timing bugs or create power/stability problems if programmed outside the intended PM sequence.
- Debug and status registers are volatile. CP stall/busy, clipper, CB, DB, and GDS readbacks can change while being decoded, so diagnostics must tolerate races and non-atomic multi-register snapshots.
- Reserved and `UNUSED` fields appear in several GDS and clock-control registers. Read-modify-write sequences should preserve unrelated bits unless the ASIC programming guide requires a full write.
- This chunk ends mid-register family at `GDS_DEBUG_REG0`; the later GDS debug fields are outside this chunk and must be reconciled with subsequent chunk reports.

## Test And Validation Signals

Useful validation is mostly build, static, and hardware based:

- Build AMDGPU/SI configurations that include `gfx_6_0_sh_mask.h`, especially `gfx_v6_0.c`, `si.c`, `si_dpm.c`, `si_smc.c`, and `dce_v6_0.c`.
- Static generated-header checks that every field has a matching mask/shift pair, masks align with shifts, field names match the companion GFX6 offset header, and fields in each register do not unintentionally overlap.
- Ring bring-up tests on GFX6 hardware: initialize CP rings, submit no-op and DMA packets, verify read/write pointer movement, EOP fence writes, interrupts, and reset recovery.
- Graphics render tests that exercise multiple color targets, blend modes, shader/target masks, fast clear, CMASK/FMASK, depth/stencil, HTILE, alpha-to-mask, EQAA, and Z pass counters.
- Compute tests that launch kernels with varying dimensions, user data, scratch/temp-ring use, CU masks, VMIDs, and resource descriptors.
- Power-management tests across idle, load, suspend/resume, and GPU reset to catch incorrect CGTS/CGTT/DB/CB clock-gating programming.
- Tiling tests that validate `GB_ADDR_CONFIG` and all programmed `GB_TILE_MODE*` entries through scanout, render, texture, and buffer operations.
- Diagnostic tests that read CP busy/stall/status, CB/DB performance counters, clipper debug registers, GDS status/debug, and interrupt status without malformed field decoding.
