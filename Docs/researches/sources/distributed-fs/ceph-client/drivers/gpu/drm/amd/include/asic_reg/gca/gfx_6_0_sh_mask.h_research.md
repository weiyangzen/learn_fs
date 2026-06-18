# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_6_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002699`: lines 1-4330, `Docs/researches/chunks/subset-b-002699_research.md`
- `subset-b-002700`: lines 4331-8715, `Docs/researches/chunks/subset-b-002700_research.md`
- `subset-b-002701`: lines 8716-12821, `Docs/researches/chunks/subset-b-002701_research.md`

## Chunk Research

### subset-b-002699: lines 1-4330

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

### subset-b-002700: lines 4331-8715

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_6_0_sh_mask.h lines 4331-8715

## Purpose

This chunk is the middle segment of the generated Southern Islands / GFX 6.0 ASIC register shift-mask header. It does not implement algorithms; it defines C preprocessor constants that describe bitfield masks and shifts for GPU graphics-core registers. The paired offset header, `gfx_6_0_d.h`, supplies the `mm*` or `ix*` register addresses, while this file supplies the field layout used to build, update, or decode the 32-bit register values.

The covered block starts in the GDS debug/status area and runs through the beginning of SQ buffer-resource descriptors. It spans these register families:

- `GDS_*` at lines 4331-4585: Global Data Share debug registers, GWS resource controls, SEC/DED counters, performance counters, and direct read/write data windows.
- `GFX_COPY_STATE` at lines 4586-4587: a small graphics copy-state selector.
- `GRBM_*` at lines 4588-5063: graphics register bus manager indexing, read-error reporting, soft-reset bits, busy/idle status, scratch registers, skew/clock controls, and performance counters.
- `IA_*` at lines 5064-5563: input-assembler debug/status, multi-VGT parameters, VMID override, and IA performance counters.
- `PA_CL_*`, `PA_SC_*`, and `PA_SU_*` at lines 5564-6989: primitive assembly clipper, scan converter, raster config, viewport/scissor/depth state, antialiasing samples, line/stipple state, setup/rasterizer state, and PA performance counters.
- `RAS_*` at lines 6990-7043: block-level signature fields used by the register access/signature infrastructure.
- `RLC_*` at lines 7044-7341: runlist controller power-gating, clock-gating, memory sleep, load-balancing, save/restore, scratch/serdes access, and perfmon fields.
- `SCRATCH_*` and `SETUP_DEBUG_*` at lines 7342-7437: generic scratch addressing/masking plus setup debug views.
- `SPI_*` at lines 7438-8703: shader processor input controls, pixel shader input mapping, shader program base/resource registers for LS/HS/ES/GS/VS/PS stages, trap memory bases, user-data SGPR slots, GDS credits, export formats, static CU masks, debug/busy state, and SPI performance counters.
- `SQ_*` at lines 8704-8715: shader queue CU clock forcing and the first two words of buffer resource descriptors.

## Important APIs, Types, And Data

The API surface is entirely macro data in the form:

- `<REGISTER>__<FIELD>_MASK`
- `<REGISTER>__<FIELD>__SHIFT`

Consumers combine these with helpers such as `REG_SET_FIELD(value, REG, FIELD, field_value)` and `REG_GET_FIELD(value, REG, FIELD)`, or with local masked writes that use the same mask/shift contract. The macros define no functions, structs, enums, storage, callbacks, or module-visible symbols beyond the preprocessor names.

Important field groups in this chunk include:

- GDS/GWS fields: FIFO and write-buffer debug state, `GDS_GWS_RESOURCE` queue/counter/flag fields, SEC/DED counters, full-width read/write data fields, and four GDS perf counters.
- GRBM fields: `GRBM_GFX_INDEX` selection fields (`INSTANCE_INDEX`, `SH_INDEX`, `SE_INDEX`) and broadcast bits, read-error address/status fields, `GRBM_STATUS*` and `GRBM_STATUS_SE*` busy flags, and `GRBM_SOFT_RESET` bits for front-end, shader, scan, DB/CB, TA/TCP, and related graphics blocks.
- IA fields: debug FIFO/parser state, primitive IDs/counts, `IA_MULTI_VGT_PARAM` fields for partial VS wave behavior, switch-on-EOP/EOS, primitive group sizing, WD/VGT pipe enable, and IA VMID override fields.
- PA fields: clipper controls, viewport transform offsets/scales for 16 viewports, clip/scissor rectangles, antialiasing sample locations and masks, raster backend mapping (`PA_SC_RASTER_CONFIG` and `_1`), screen/window/generic scissor bounds, line stipple, point size/radius, polygon offset, primitive filtering, and scan-converter status/perf counters.
- RLC fields: auto power-gating controls, CGCG/CGLS ramp timing, dynamic power-gating request/status, load-balance masks/counters, memory-sleep controls, runlist controller soft reset, save/restore base, SMU power-gating handshakes, SERDES index/data controls, and microcode control.
- SPI fields: arbitration cycles/priority, barycentric and interpolation control, pixel shader input enable/address/control tables, shader program low/high addresses, `SPI_SHADER_PGM_RSRC1_*` and `SPI_SHADER_PGM_RSRC2_*` resource fields, trap table/memory address fields, user-data registers for all graphics shader stages, export color/position/Z formats, GDS credits, static CU masks, and SPI debug/busy state.
- SQ fields: `SQ_ALU_CLK_CTRL` per-shader-array CU force-on masks and `SQ_BUF_RSRC_WORD0/1` buffer descriptor base-address/stride/cache-swizzle/swizzle-enable fields. The rest of the SQ buffer descriptor continues in the next chunk.

## Control Flow

There is no runtime control flow inside the header. The preprocessor resolves field names to literal masks and shifts at compile time. Runtime control flow appears in call sites that:

1. Select the correct register address from `gfx_6_0_d.h` or packet/register tables.
2. Build a field value using these macros, often through `REG_SET_FIELD`.
3. Write it with MMIO or command-stream helpers such as `WREG32`, `RREG32`, shadowed SOC15 helpers in later generations, or PM4 packet construction.
4. Read status registers and decode bits with masks or `REG_GET_FIELD`.

For GFX 6-era code, representative paths include `amdgpu/si.c` and `radeon/si.c`. They use `GRBM_GFX_INDEX` to select shader engines/shader arrays, save and restore broadcast selection, program per-SE raster backend routing through `PA_SC_RASTER_CONFIG`, and sample GRBM status registers in reset/debug flows. Clear-state tables for SI-era hardware also carry entries for SPI pixel shader inputs, GDS state, and `IA_MULTI_VGT_PARAM`; this header is the generated field contract corresponding to those register values.

## State And Persistence Behavior

The macros are stateless and have no persistence behavior by themselves. The state they describe lives in volatile GPU hardware registers.

Several state classes are represented:

- Configuration state: shader program resources, SPI input mappings, IA/VGT grouping, viewport/scissor/depth transforms, raster config, RLC power controls, and GDS resource setup are programmed during device init, context setup, clear-state emission, or power-management transitions.
- Selector state: `GRBM_GFX_INDEX` changes which shader engine/shader array/instance subsequent indexed MMIO accesses target. Drivers must protect and restore it around per-SE/per-SH reads and writes.
- Telemetry/status state: GRBM, IA, SPI, GDS, SETUP, and PA debug/status/perf counter fields expose live busy flags, FIFO state, counters, and read-error latches.
- Reset/control state: `GRBM_SOFT_RESET`, `RLC_SOFT_RESET_GPU`, RLC power-gating controls, and GDS resource reset fields cause direct hardware side effects when written.
- Shader dispatch/program state: `SPI_SHADER_PGM_*`, `SPI_SHADER_USER_DATA_*`, `SPI_SHADER_TBA/TMA_*`, and `SQ_BUF_RSRC_WORD*` fields define shader-visible memory addresses, SGPR mappings, trap state, scratch/resource enablement, and descriptor interpretation until overwritten by a new context or command stream.

No file-system state, driver-private cache, or durable software persistence is implemented here. Persistence across suspend/resume, reset, or context switches is handled elsewhere by register-init tables, RLC save/restore logic, firmware, and driver code that replays hardware state.

## Dependencies

This chunk depends on the generated AMD ASIC register ecosystem staying internally consistent:

- `gfx_6_0_d.h` provides the matching GFX 6.0 register offsets, including early `ixGDS_DEBUG_REG*`, `ixIA_DEBUG_REG*`, `ixPA_SC_DEBUG_REG*`, `ixSETUP_DEBUG_REG*`, and many `mmGDS_*`/`mmGRBM_*`/`mmPA_*`/`mmSPI_*` addresses.
- `gfx_6_0_enum.h` supplies enumerated values for some fields where a mask/shift is not enough to explain allowed semantic values.
- AMDGPU and Radeon register helpers provide the actual read/modify/write operations.
- Generated clear-state tables and SI-family initialization code assume these masks match the hardware layout for GFX 6.0.

The names are generation-specific. Similar fields appear in later `gfx_7_*`, `gfx_8_*`, and GC headers, but bit positions and block naming can diverge. Code must include the correct ASIC-family header rather than reusing masks across generations.

## Integration Points

Key integration points are:

- SI/GFX 6 initialization in AMDGPU and Radeon, especially shader-engine selection via `GRBM_GFX_INDEX`, raster backend mapping via `PA_SC_RASTER_CONFIG`, and status polling through `GRBM_STATUS*`.
- Command submission and clear-state programming paths that emit IA, PA, SPI, and GDS context/register state.
- Debug and hang-diagnosis paths reading GRBM/IA/SPI/GDS/SETUP debug registers, perf counters, read-error fields, and busy flags.
- RLC/SMU/power-management code that manipulates RLC clock-gating, power-gating, memory sleep, save/restore base, and GPU soft-reset controls.
- Shader compiler/packet setup boundaries where SPI shader resource fields, user-data SGPR counts, LDS/scratch enables, trap-present bits, export formats, and pixel input controls must match the ABI expected by firmware and user-mode drivers.
- KFD/trap-handling and shader debug code that must agree on SQ/SPI resource and trap-memory field layout, although this particular chunk only starts the SQ buffer descriptor block.

## Risks

- Incorrect masks or shifts can silently corrupt adjacent hardware fields because most callers perform read/modify/write operations against packed 32-bit registers.
- `GRBM_GFX_INDEX` is global selector state; failure to serialize or restore it can redirect later indexed register accesses to the wrong shader engine, shader array, or instance.
- Reset and power-gating fields have direct side effects. Bad writes to `GRBM_SOFT_RESET`, RLC power controls, or GDS reset/resource fields can hang the graphics pipeline or lose volatile hardware state.
- Shader program/resource fields encode addresses, SGPR counts, VGPR/SGPR allocation, LDS size, scratch enablement, trap state, streamout enables, and export formats. A layout mismatch can cause shader faults, memory corruption, incorrect rendering, or GPU hangs.
- PA raster, viewport, clip, and scissor fields directly affect rendering correctness. Incorrect `PA_SC_RASTER_CONFIG` values can route pixels to the wrong render backends or break multi-SE chips.
- Perf counters and status bits are live hardware observations; readers must account for wraparound, latching/clear behavior, and races with reset or power transitions.
- Hand-editing a generated header risks diverging from AMD's register database. Many errors compile cleanly because these are numeric constants.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for SI/GFX 6 AMDGPU and Radeon code that includes `gfx_6_0_sh_mask.h` with `gfx_6_0_d.h`.
- Static consistency checks that every `<REGISTER>__<FIELD>_MASK` has the matching `<REGISTER>__<FIELD>__SHIFT`, and that register names exist in the GFX 6.0 offset header or are intentional descriptor-only fields such as `SQ_BUF_RSRC_WORD*`.
- GPU initialization smoke tests on Southern Islands hardware that exercise `GRBM_GFX_INDEX` selection, backend/raster configuration, clear-state programming, and SPI shader setup.
- Rendering tests that cover viewport/scissor/clip state, MSAA sample positions, line stipple, point/polygon setup, and streamout/export formats.
- Hang/reset diagnostics that read `GRBM_STATUS*`, `GRBM_READ_ERROR*`, IA/SPI/GDS debug registers, and RLC status before and after reset paths.
- Power-management suspend/resume and clock/power-gating tests that verify RLC and GDS state is restored or reprogrammed correctly.
- Shader ABI tests that dispatch graphics shaders with varying SGPR/VGPR/LDS/scratch/user-data requirements and verify SPI resource fields produce correct execution rather than faults.

### subset-b-002701: lines 8716-12821

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_6_0_sh_mask.h lines 8716-12821

## Purpose

This chunk is generated-style bitfield metadata for AMD Southern Islands / GFX 6.0 graphics-core registers. It exposes `*_MASK` and `*__SHIFT` constants for shader-queue (`SQ`/`SQC`) descriptors, instruction encodings, wave/debug state, thread trace packets, texture/cache blocks (`TA`, `TD`, `TCP`, `TCA`, `TCC`, `TCI`), shader export (`SX`), geometry/tessellation (`VGT`), and the final `WD_DEBUG_DATA` field before the include guard closes.

The file contains no executable driver logic. Its value is the hardware contract: code that includes `gca/gfx_6_0_d.h` for offsets can include this header for field layout and then build or decode register words with `REG_SET_FIELD`, `REG_GET_FIELD`, direct masks, or command-stream packet data. The chunk is especially relevant to legacy SI AMDGPU power-management code, Radeon SI clear-state/blit tables, debug tooling, performance counters, and any generated register validation that must understand GFX6 bit positions.

## Important APIs, Types, And Data

There are no C functions, structs, enums, storage objects, callbacks, or runtime APIs in this range. The public interface is the macro naming convention:

- `REGISTER__FIELD_MASK` gives the field bit mask in the 32-bit register or packet word.
- `REGISTER__FIELD__SHIFT` gives the low-bit shift for the same field.
- Full-word payload registers use fields such as `DATA`, `SIZE`, `OFFSET`, `BASE`, `COUNTER`, or `ENCODING` with `0xffffffffL` masks.
- Register families are encoded in the macro names, not in C namespaces.

Important groups in this chunk include:

- Shader resource descriptors and instruction encodings: `SQ_BUF_RSRC_WORD1..3`, `SQ_IMG_RSRC_WORD0..7`, `SQ_IMG_SAMP_WORD0..3`, `SQ_DS_*`, `SQ_EXP_*`, `SQ_MIMG_*`, `SQ_MTBUF_*`, `SQ_MUBUF_*`, `SQ_SMRD`, `SQ_SOP*`, `SQ_VOP*`, `SQ_VINTRP`, and `SQ_INST`. These describe buffer/image/sampler descriptors and instruction packet fields such as encodings, opcodes, register operands, GLC/SLC, data masks, formats, swizzles, type, mtype, address, offsets, and destination selectors.
- Shader queue configuration and cache/debug state: `SQC_CACHES`, `SQC_CONFIG`, `SQ_CONFIG`, `SQ_FIFO_SIZES`, `SQ_DEBUG_STS_*`, `SQ_DEBUG_CTRL_LOCAL`, `SQ_SEC_CNT`, `SQ_DED_CNT`, `SQ_DED_INFO`, and `SQC_SECDED_CNT`.
- Wave and indirect debug accessors: `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_WAVE_STATUS`, `SQ_WAVE_HW_ID`, `SQ_WAVE_MODE`, `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_IB_DBG0`, `SQ_WAVE_IB_STS`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_EXEC_*`, `SQ_WAVE_PC_*`, `SQ_WAVE_TBA_*`, `SQ_WAVE_TMA_*`, `SQ_WAVE_TTMP0..11`, and wave instruction words. These define per-wave status, allocation, PC, trap, SIMD/CU/VMID, and temporary-register fields.
- Thread-trace and interrupt metadata: `SQ_THREAD_TRACE_BASE*`, `SQ_THREAD_TRACE_SIZE`, `SQ_THREAD_TRACE_CTRL`, `SQ_THREAD_TRACE_STATUS`, `SQ_THREAD_TRACE_MODE`, `SQ_THREAD_TRACE_MASK`, token/perf masks, write pointers, high-water marks, userdata words, and `SQ_THREAD_TRACE_WORD_*` packet decoders for timestamps, events, waves, instruction PC, issue, perf, reg, and userdata tokens. `SQ_INTERRUPT_WORD_AUTO`, `SQ_INTERRUPT_WORD_CMN`, and `SQ_INTERRUPT_WORD_WAVE` define SQ interrupt packet fields.
- Performance and profiling registers: `SQ_PERFCOUNTER0..15_{LO,HI,SELECT}`, `SQ_PERFCOUNTER_CTRL*`, `SQ_LB_CTR_CTRL`, load-balancer data counters, `SX_PERFCOUNTER0..3_*`, `TA_PERFCOUNTER0..1_*`, `TD_PERFCOUNTER0_*`, `TCP_PERFCOUNTER0..3_*`, `TCA_PERFCOUNTER0..3_*`, `TCC_PERFCOUNTER0..3_*`, and `VGT_PERFCOUNTER0..3_*`.
- Texture/cache and memory-facing controls: `TA_CNTL`, `TA_CNTL_AUX`, `TA_BC_BASE_ADDR*`, `TA_CS_BC_BASE_ADDR*`, `TA_STATUS`, `TA_CGTT_CTRL`, `TD_CNTL`, `TD_CGTT_CTRL`, `TCP_CNTL`, `TCP_CHAN_STEER_*`, `TCP_CGTT_SCLK_CTRL`, `TCP_STATUS`, `TCP_WATCH*`, `TCC_CTRL`, `TCC_CGTT_SCLK_CTRL`, `TCC_EDC_COUNTER`, `TCA_CTRL`, `TCA_CGTT_SCLK_CTRL`, and `TCI_CNTL_*`.
- Shader export and crossbar debug: `SX_DEBUG_1`, `SX_DEBUG_BUSY*`, `SXIFCCG_DEBUG_REG0..3`, and `SX_PERFCOUNTER*`.
- Geometry, tessellation, and streamout state: a large `VGT_*` block covers event/init command words, DMA/index controls, draw index/instance counts, primitive type/id, group-vector formatting, GS/ES/VS ring sizing and offsets, geometry shader mode/output/instance controls, hull/tessellation controls, LS-HS configuration, streamout config and buffer sizes/offsets/strides, TF parameters, vertex reuse, shader-stage enables, system config, and VGT performance counters.
- Debug-heavy VGT status registers: `VGT_DEBUG_REG0..35`, `VGT_CNTL_STATUS`, `VGT_CACHE_INVALIDATION`, `VGT_FIFO_DEPTHS`, `VGT_HS_OFFCHIP_PARAM`, and related state expose many low-level busy, counter, FIFO, request, and arbitration fields.

## Control Flow

This header chunk has no control flow of its own. All behavior occurs at preprocessing and compile time:

1. A GFX6 source includes `gca/gfx_6_0_d.h` for register offsets and this `gca/gfx_6_0_sh_mask.h` file for field definitions.
2. Driver code, generated state tables, or command packet builders combine masks and shifts into register values.
3. Runtime code writes those values through MMIO helpers, indirect register access, or PM4 packets, or reads hardware values and decodes fields.
4. The GPU hardware interprets, latches, increments, or reports the corresponding state.

Local AMDGPU legacy SI power-management files (`si_dpm.c` and `si_smc.c`) include this generated header alongside GFX6, DCE6, GMC6, BIF3, and SMU6 register headers. The Radeon SI clear-state and blit tables show adjacent runtime usage of many same registers, including `VGT_GS_MODE`, `VGT_SHADER_STAGES_EN`, `VGT_STRMOUT_CONFIG`, streamout buffer state, primitive-id state, and tessellation/geometry controls. Those tables encode register values directly rather than using these macros at every call site, but the macros document the field layout those values must obey.

## State And Persistence Behavior

The macros are stateless constants. The state they describe lives in GPU registers, command-stream state, shader descriptors, or hardware-generated trace/status packets.

State categories represented by this chunk include:

- Persistent or context-saved graphics state: `VGT_*` geometry/tessellation/streamout controls, shader-stage enables, primitive ID reset/enables, index/instance ranges, GS ring sizes, and transform-feedback controls remain in the graphics context until cleared, reset, or overwritten by command streams.
- Per-dispatch or per-draw descriptor state: `SQ_BUF_RSRC_*`, `SQ_IMG_RSRC_*`, and `SQ_IMG_SAMP_*` fields define buffer, image, and sampler descriptors consumed by shaders. Incorrect mtype, format, swizzle, dimension, address, or tiling fields affect shader memory accesses.
- Volatile status and debug state: `SQ_DEBUG_STS_*`, `SQ_WAVE_*`, `TA_STATUS`, `TCP_STATUS`, `VGT_CNTL_STATUS`, `SX_DEBUG_BUSY*`, and numerous `VGT_DEBUG_REG*` fields report live hardware activity, queues, arbitration, wave allocation, or block busy conditions.
- Performance counter state: `SQ`, `SX`, `TA`, `TD`, `TCP`, `TCA`, `TCC`, and `VGT` perf-counter select/control/data pairs configure event sources and expose counter values that persist until reset, rollover, stop, or reprogramming.
- Thread-trace state: base, size, mode, masks, write pointer, high-water mark, status, token masks, and packet-word definitions describe a trace buffer workflow where programming selects what to capture and hardware emits tokenized records.
- Cache, clock-gating, and power-related state: `SQC_CACHES`, `SQC_CONFIG`, `SQ_TEX_CLK_CTRL`, `TA_CGTT_CTRL`, `TD_CGTT_CTRL`, `TCP_CGTT_SCLK_CTRL`, `TCA_CGTT_SCLK_CTRL`, and `TCC_CGTT_SCLK_CTRL` affect invalidation, cache behavior, or block clock-gating.
- Error-counting state: `SQ_SEC_CNT`, `SQ_DED_CNT`, `SQ_DED_INFO`, `SQC_SECDED_CNT`, and `TCC_EDC_COUNTER` expose single/double-error counts and diagnostic IDs. The header does not state whether individual fields are sticky, clear-on-read, clear-on-write, or reset-only.

Because generated masks do not encode sequencing rules, consumers must still follow the GFX6 register specification for reserved-bit preservation, read-modify-write safety, status-clear semantics, clock/power gating ordering, and shader-context save/restore.

## Dependencies

This chunk depends on the rest of the GFX6 generated register set:

- `gca/gfx_6_0_d.h` provides matching GFX6 offset symbols such as the `mm*` register names for these masks.
- Earlier and later ranges of `gfx_6_0_sh_mask.h` define other fields in the same generated mask namespace.
- AMDGPU/Radeon register helpers provide runtime use: `RREG32`, `WREG32`, `WREG32_P`, `REG_SET_FIELD`, `REG_GET_FIELD`, PM4 packet builders, and context-state table emitters.
- Legacy SI AMDGPU power management includes this header in `si_dpm.c` and `si_smc.c`, tying it to Southern Islands DPM/SMC setup with GFX6 register definitions available for clock, power, and block-control programming.
- Radeon SI-era command tables and clear-state headers depend on equivalent register layouts for initial graphics context values, blit shader setup, streamout disables, primitive/geometry defaults, and thread-trace clear state.
- Hardware documentation or generated register databases are the authoritative source. Cross-generation siblings may reuse macro names but not necessarily identical shifts or masks.

## Integration Points

Primary integration points are:

- Southern Islands graphics initialization and power management. The AMDGPU legacy SI DPM/SMC sources include this header with the GFX6 register offset header, making these fields available when configuring SI ASIC power, clocks, SMC memory access, and graphics-block state.
- Graphics command-stream setup. The `VGT_*` masks describe context registers used in clear-state tables and PM4 packets for primitive type, index ranges, instance counts, shader-stage enables, tessellation, geometry shader rings, streamout buffers, and transform feedback.
- Shader ABI and descriptor programming. `SQ_BUF_RSRC_*`, `SQ_IMG_RSRC_*`, and `SQ_IMG_SAMP_*` are the field-level contract for user/kernel code that constructs descriptors consumed by GFX6 shaders.
- Debug and hang diagnosis. `SQ_WAVE_*`, `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_DEBUG_STS_*`, `TA_STATUS`, `TCP_STATUS`, `SX_DEBUG_BUSY*`, and `VGT_DEBUG_REG*` provide decoded views into wave state, block busy state, FIFOs, and internal counters.
- Thread tracing and profiling. `SQ_THREAD_TRACE_*` controls and token decoders, plus the per-block performance-counter selects, integrate with profiling paths that program capture buffers, enable trace modes, select event counters, and decode emitted records.
- Cache and memory-path control. `SQC_CACHES`, `SQC_CONFIG`, `TCP_CNTL`, `TCC_CTRL`, `TCI_CNTL_*`, `TA_CNTL`, and clock-gating controls sit on performance, invalidation, and memory-traffic paths.
- Error reporting and RAS-adjacent diagnostics. `SQ_*SEC*`, `SQ_*DED*`, `SQC_SECDED_CNT`, and `TCC_EDC_COUNTER` describe counters and IDs that can be read during reliability diagnostics, even though this GFX6-era header does not provide higher-level RAS policy.

## Risks

- Wrong masks or shifts silently program the wrong hardware bits. In this chunk, that can corrupt shader descriptors, instruction decoders, wave debug access, thread trace setup, cache invalidation, VGT draw state, streamout buffers, or performance counters.
- Similar register names recur across AMD GPU generations. Reusing GFX7/GFX8/GFX9 field assumptions for this GFX6 header can compile but produce invalid SI register values.
- Reserved and debug fields are exposed as plain macros. Callers must preserve reserved bits and avoid enabling low-level debug, force, stall, or clock-gating controls outside documented sequences.
- Full-word `0xffffffffL` masks do not imply arbitrary values are safe. Address, size, counter, index, and descriptor fields often still require alignment, range, tiling, VMID, or packet-format constraints.
- Thread-trace fields combine setup registers and hardware-emitted packet decoders. Confusing control fields with trace-record fields can break profiling or produce misleading decoders.
- Status and counter registers can have destructive read/clear semantics not represented in the header. Polling or clearing `SQ`, `TA`, `TCP`, `TCC`, `SX`, or `VGT` status incorrectly can mask real faults or perturb diagnostics.
- VGT streamout/geometry/tessellation state has broad draw-path impact. Misprogramming `VGT_GS_MODE`, `VGT_SHADER_STAGES_EN`, `VGT_LS_HS_CONFIG`, `VGT_TF_PARAM`, or streamout buffer fields can cause incorrect rendering, command processor hangs, or memory corruption.
- Manual edits are high risk because this is generated hardware metadata. Changes should come from regenerated AMD ASIC register sources and be validated against matching offset/default headers.

## Test Signals

Useful validation signals include:

- Build coverage for SI AMDGPU legacy DPM/SMC paths that include `gca/gfx_6_0_d.h` and `gca/gfx_6_0_sh_mask.h`.
- Static consistency checks that each register family in this chunk has matching offset symbols in `gfx_6_0_d.h` and that field masks within a register do not overlap unexpectedly except for documented aliases such as nested/mask fields.
- Southern Islands boot and display bring-up without invalid GFX register access, clock-gating warnings, SMC/DPM failures, or graphics ring timeouts.
- Radeon/AMDGPU clear-state and blit-path smoke tests that exercise `VGT_GS_MODE`, `VGT_SHADER_STAGES_EN`, streamout disables, primitive ID state, and draw-index/instance setup.
- Graphics workloads with tessellation, geometry shaders, streamout, instancing, primitive restart, and transform feedback to cover the dense `VGT_*` field set.
- Shader descriptor tests that stress buffer, image, sampler, typed buffer, and memory instruction paths using the `SQ_*RSRC*`, `SQ_MIMG`, `SQ_MTBUF`, and `SQ_MUBUF` fields.
- Profiling and debug tests that program SQ/SX/TA/TD/TCP/TCA/TCC/VGT performance counters and verify event selection, counter rollover, start/stop/reset, and high/low reads.
- Thread-trace capture tests that validate base/size/mode/mask setup, write-pointer progress, overflow/high-water status, and token decoding for event, wave, instruction, issue, perf, timestamp, userdata, and register packets.
- Hang/debug workflows that read `SQ_IND_*`, `SQ_WAVE_*`, `SQ_DEBUG_STS_*`, `TA_STATUS`, `TCP_STATUS`, `SX_DEBUG_BUSY*`, and `VGT_DEBUG_REG*` while preserving status semantics.
- Cache and memory stress tests that monitor invalidation behavior, TCC/TCP/TCI controls, EDC counters, and clock-gating transitions under rendering and compute-like shader memory traffic.
