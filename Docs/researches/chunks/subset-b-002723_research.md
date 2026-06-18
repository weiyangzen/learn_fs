# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h lines 9228-13901

## Purpose

This chunk is a generated AMD GCA/GFX 8.1 shader-mask header slice. It defines preprocessor constants for register bitfields: each field is represented as `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT`. Driver code uses these constants with the matching GFX 8.1 offset header and AMDGPU bitfield helpers to compose or decode 32-bit MMIO register values.

The repository path is under `distributed-fs/ceph-client`, but this source is AMD GPU driver hardware metadata, not Ceph or filesystem logic. The chunk contains no executable C code, no structs, no functions, no callbacks, and no software-owned storage.

This specific range starts in the middle of `RLC_ROM_CNTL`, covers a large run of RLC, CGTT/CGTS, and SPI field layouts, then enters SQ/SQC fields near the end. The major hardware areas are:

- RLC ROM, clock-count, GPM, power-gating, SMU handshake, SERDES, scratch, save/restore, interrupt, SPM, CP table, and global-control fields.
- Clock-gating and clock-tree controls for RLC, BCI, SPI, and repeated per-CU shader/texture blocks.
- SPI pixel input, shader program, resource, user-data, trap, debug, performance-counter, wave-lifetime, GDS/export/scoreboard, and load-balance fields.
- SQ and SQC control/cache/DSM fields at the tail of the chunk.

## Important APIs, Types, And Macros

There are no C APIs in the ordinary function/type sense. The public interface is the generated macro namespace consumed by AMDGPU and KFD code:

- `<REGISTER>__<FIELD>__SHIFT` names the bit offset of a field.
- `<REGISTER>__<FIELD>_MASK` names the raw register mask.
- Full-width `0xffffffff` fields identify data, counter, scratch, address, or bitmap-style registers, but do not imply that arbitrary writes are safe.

Important register families in this chunk include:

- `RLC_*`: register-list-controller fields for ROM control, GPU clock counters, microcode flags, GPM status, power gating, clock gating, load balancing, GPM threads/VMIDs, SERDES read/write control, scratch/general registers, GPM performance counters, SRM index/data windows, interrupt controls, SPM mux/ring controls, SMU messages/arguments, CP table programming, and global RLC state.
- `RLC_GPM_STAT`: a dense status word for RLC busy state, graphics power/clock/light-sleep status, context/GFX/compute processing, register save/restore, static/dynamic CU power transitions, aborted power-down sequence, and power-gating error status.
- `RLC_PG_CNTL`: GFX power-gating enable/source, dynamic/static per-CU power gating, pipeline power gating, override/disable bits, CHUB/SMU handshake controls, and SMU clock-slowdown controls.
- `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_MGCG_CTRL`, and `CGTT_*`: coarse/fine clock-gating controls, sleep-mode behavior, hysteresis/delay fields, soft override/stall fields, and clock-ramp timing.
- `CGTS_CU*_SP0_CTRL_REG`, `CGTS_CU*_SP1_CTRL_REG`, `CGTS_CU*_LDS_SQ_CTRL_REG`, `CGTS_CU*_TA_CTRL_REG`, `CGTS_CU*_TA_SQC_CTRL_REG`, and `CGTS_CU*_TD_TCP_CTRL_REG`: repeated per-CU clock/tree-status controls. Each group exposes block masks plus override, busy-override, light-sleep override, and SIMD-busy override fields for shader processors, LDS/SQ, texture address/SQC, and texture data/TCP blocks.
- `CGTS_SM_CTRL_REG` and `CGTS_SM_CTRL_REG_2`: shader-module level clock/tree controls, including CP/RLC/SX/TA/TD/TCP/SQC/SQ/LDS fields, override bits, sleep/busy override bits, and multipipe controls.
- `SPI_*`: shader processor interpolator and shader-stage programming metadata. This includes `SPI_CONFIG_CNTL`, `SPI_GFX_CNTL`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_PS_INPUT_CNTL_0..31`, shader position/color/Z format controls, LDS/GDS ring controls, debug and trap controls, performance counters, and wave-lifetime/load-balance counters.
- `SPI_SHADER_*`: shader program address, trap base/memory address, resource, user SGPR/user-data, and stage resource fields for PS, VS, GS, ES, HS, and LS. Resource registers define VGPR/SGPR counts, priority, float mode, privileged/debug/IEEE/DX10 behavior, scratch/trap/LDS/exception enables, CU masks, wave limits, lock thresholds, and group FIFO depth.
- `SQ_CONFIG` and `SQC_CONFIG`: shader queue and scalar instruction/data cache control fields, including debug behavior, soft-clause disables, export-ready priority behavior, replay sleep count, cache sizing, FIFO depths, hash behavior, per-VMID invalidate behavior, LRU policy, bank forcing, and clock-disable fields.
- `SQC_CACHES`, `SQC_WRITEBACK`, and the beginning of `SQC_DSM_CNTL`: cache invalidate/writeback targets, completion status, dirty/writeback status, and diagnostic/scan-mux controls.

## Control Flow

This header chunk has no runtime control flow. Its effect is entirely through C preprocessing.

Typical consumer flow is:

1. A GFX 8.1-era driver source includes `gfx_8_1_offset.h` and `gfx_8_1_sh_mask.h`.
2. The caller selects a register offset macro from the offset header and one or more field macros from this mask header.
3. Driver code uses helper patterns such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, `RREG32_SOC15`, or generation-specific wrappers to update or decode a 32-bit register value.
4. The hardware-visible MMIO read/write, indexed access, polling, firmware table programming, or debug dump happens in the consumer source, not in this header.

Examples visible in this tree show the same field families used by older and newer AMDGPU paths:

- `gfx_v6_0.c`, `gfx_v7_0.c`, and later SOC15-era `gfx_v10_0.c`, `gfx_v11_0.c`, `gfx_v12_0.c`, and `gfx_v12_1.c` manipulate `RLC_PG_CNTL` fields around GFX power gating, static/dynamic per-CU power gating, SMU slowdown, and SMU handshake behavior.
- `mxgpu_vi.c` programs VI golden settings for `CGTT_*` and `CGTS_CU*` registers, showing these generated field layouts are used for virtualization and bring-up register tables.
- Clear-state headers such as `clearstate_si.h` and `clearstate_gfx11.h` carry repeated `SPI_PS_INPUT_CNTL_0..31` entries, matching the repeated pixel-input-control field family defined here.

The header does not define valid programming order. It also does not state whether a field is read-only, write-one-to-clear, sticky, firmware-owned, indexed by GRBM, safe during active waves, or reset/power-gating sensitive.

## State And Persistence Behavior

The macros persist no software state. They describe hardware state in GFX 8.1 graphics blocks.

The represented hardware state includes:

- Persistent-until-reprogrammed configuration: RLC power/clock gating, CGTT/CGTS clock tree controls, SPI shader-stage programming, pixel input interpolation controls, shader resource controls, GDS/export/scoreboard buffer sizing, and SQ/SQC cache configuration.
- Live status: RLC busy and power-transition status, CU work-pending bitmaps, SERDES busy/read data, GPM performance counters, SPI debug busy/status fields, wave-lifetime counters, CSQ active counters, SQC cache completion/dirty state, and power-gating status bitmaps.
- Trigger/control windows: GPU clock capture, SERDES read/write commands, GPM scratch index/data windows, SRM index/data windows, SMU command/argument registers, SPM sample/mux/ring controls, cache invalidate/writeback controls, trap/debug controls, and performance counter control fields.
- Shader ABI state: shader program base addresses, trap base/memory addresses, user SGPR/user-data registers, scratch/trap/exception enables, VGPR/SGPR counts, LDS sizes, and per-stage resource limits. These fields are part of how graphics and compute work is launched on the GPU.

Persistence is hardware-defined. Configuration values are usually reestablished during ASIC initialization, suspend/resume, reset recovery, virtualization transitions, or golden-setting programming. Status, counter, interrupt, and command fields may be volatile, latched, clear-on-read/write, or meaningful only while a specific block is selected or idle.

## Dependencies

This chunk depends on the generated AMD GFX 8.1 register family remaining synchronized:

- `gfx_8_1_sh_mask.h` supplies the field masks and shifts documented here.
- The companion GFX 8.1 offset header supplies the matching register addresses, usually with `mm*` register names for pre-SOC15/VI-era code.
- AMDGPU bitfield helpers rely on exact macro spelling, especially the `__SHIFT` and `_MASK` suffix conventions.
- RLC/CP firmware initialization, clock-gating tables, power-management code, KFD/queue setup, graphics pipeline programming, and debug/RAS-like dump paths depend on these layouts matching the actual ASIC register specification.
- Cross-generation code often has nearly identical register names. Similar fields in SI/CIK/VI, GFX9, GFX10, GFX11, or GFX12 headers may differ in width, ownership, or semantics.

## Integration Points

Primary integration points are:

- GFX power management and RLC control: `RLC_PG_CNTL`, `RLC_GPM_STAT`, `RLC_CGCG_CGLS_CTRL`, `RLC_MGCG_CTRL`, `RLC_AUTO_PG_CTRL`, and SMU message/argument fields are consumed by bring-up, power-gating, clock-gating, and reset/recovery paths.
- Golden-setting tables: CGTT/CGTS/RLC/SPI fields are commonly programmed from generation-specific register tables. In this tree, `mxgpu_vi.c` shows VI golden settings for `CGTT_*`, `CGTS_CU*`, `RLC_CGCG_CGLS_CTRL`, and related fields.
- Shader pipeline setup: `SPI_SHADER_PGM_*`, `SPI_SHADER_PGM_RSRC*`, `SPI_SHADER_USER_DATA_*`, `SPI_PS_INPUT_*`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_COL_FORMAT`, and `SPI_SHADER_Z_FORMAT` define the bit layout for graphics shader stages and per-stage user data.
- Trap/debug/diagnostic flows: `SPI_GDBG_*`, `SPI_CDBG_*`, `SPI_DEBUG_*`, `SPI_SLAVE_DEBUG_BUSY`, `SPI_P*_TRAP_SCREEN_*`, SQ debug fields, SQC DSM fields, and RLC scratch/index windows support debugging, hang analysis, trap handling, and register dumps.
- Performance and telemetry: RLC GPM counters, RLC SPM mux/ring controls, SPI performance counters, SPI wave lifetime counters, CSQ active counts, and SQC cache status fields support performance monitoring and low-level diagnostics.
- Cache coherency and invalidation: `SQC_CACHES` and `SQC_WRITEBACK` fields describe scalar cache invalidate/writeback operations and completion/dirty reporting. Consumers must supply the correct sequencing and polling.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after `RLC_ROM_CNTL__SLP_MODE_EN_MASK` from the previous chunk and ends after `SQC_DSM_CNTL__EN_SINGLE_WR_ICACHE_BANKC_MASK`, before the remaining `SQC_DSM_CNTL` fields in the next chunk.
- Header/offset mismatch is the main risk. A GFX 8.1 mask macro can compile with the wrong generation's offset or register name but program the wrong bit on hardware.
- Repeated register families are easy to copy incorrectly. `SPI_PS_INPUT_CNTL_0..31`, `SPI_SHADER_USER_DATA_*_0..15`, shader-stage resource registers, and `CGTS_CU*` controls are regular but not universally identical across stages or CU groups.
- Reserved masks are explicit throughout the header. Read-modify-write users should preserve reserved bits unless the hardware programming sequence requires a full-register write.
- RLC power-gating and clock-gating fields can affect active queues, firmware handshakes, CU availability, and reset behavior. Incorrect writes can cause hangs, failed power transitions, or missed SMU/RLC handshakes.
- CGTS per-CU override and busy/light-sleep fields can force shader, LDS, SQ, TA, SQC, TD, or TCP blocks into unexpected clock/power behavior. This is particularly risky under virtualization or golden-setting programming.
- Shader program/user-data/resource fields are ABI-sensitive. Wrong masks or shifts can misprogram program addresses, trap addresses, SGPR/VGPR counts, LDS size, exception enables, scratch state, user SGPR mapping, CU masks, or wave limits.
- SQC invalidate/writeback fields are action-oriented. Treating them as passive configuration can trigger cache operations or make polling observe stale/incomplete state.
- Many data/status fields are full-width. Full-width masks hide field-level semantics; consumers must know whether the underlying register is data, address, command, status, scratch, or write-triggered.

## Test Signals

Useful validation signals include:

- Build coverage for AMDGPU/KFD code that includes the GFX 8.1 offset and mask headers, especially VI-era GFX, power-management, virtualization, and golden-setting code.
- Static generated-header checks that every field has matching `__SHIFT` and `_MASK` macros, masks align with shifts, repeated groups are complete, and chunk boundaries reconcile with adjacent chunks.
- Cross-checks against the companion GFX 8.1 offset header so every register family named here has matching `mm*` offsets where expected.
- Hardware bring-up on GFX 8.1/VI devices, confirming RLC firmware load, clock-gating initialization, power-gating transitions, SMU handshakes, graphics queue startup, and suspend/resume work without register access warnings or ring timeouts.
- Golden-setting validation that `CGTT_*`, `CGTS_CU*`, `RLC_CGCG_CGLS_CTRL`, and related clock-gating values are written with expected masks and do not disturb reserved bits.
- Graphics and compute smoke tests that exercise shader stage setup, user-data SGPR programming, traps, scratch/LDS allocation, pixel input interpolation, export/GDS resources, and CU masks/wave limits.
- Cache and diagnostic tests that issue SQC invalidate/writeback operations, poll completion, and validate no stale instruction/data-cache behavior.
- Debug and hang-dump tests that read SPI/RLC/SQ/SQC status, counters, scratch/index windows, wave lifetime counts, and performance counters without causing new hangs or false status decoding.
