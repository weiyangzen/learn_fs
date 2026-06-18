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
