# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h lines 7462-9915

## Scope

This chunk is a generated AMDGPU GC 11.0.0 register-offset header segment. It contains C preprocessor constants only: each hardware register receives a `reg...` offset macro and an adjacent `reg..._BASE_IDX` macro. The range starts in the middle of the `gc_cprs64dec` command-processor RS64 address block at `regCP_MES_INTERRUPT`, continues through cache/interconnect and performance-monitor address blocks, covers RTAVFS register windows, contains the CP hypervisor/program-memory window, and ends in the first part of `gc_rlcdec` at `regRLC_AUTO_PG_CTRL`.

The segment defines 1,205 register-offset macros and 1,205 matching base-index macros. By address block, the non-`_BASE_IDX` register coverage is:

- `gc_cprs64dec` continued: 424 CP RS64/MES/GFX/MEC registers from `regCP_MES_INTERRUPT` through `regCP_GFX_RS64_INTERRUPT1`.
- `gc_gl1dec`, `gc_chdec`, `gc_gl2dec`, and `gc_gl1hdec`: 49 GL1/channel/GL2/GL1H cache and arbitration registers.
- `gc_perfddec`: 288 performance counter data/result registers.
- `gc_perfsdec`: 307 performance counter selector/control registers.
- `gc_grtavfs_grtavfs_dec`, `gc_grtavfs_se_grtavfs_dec`, and `gc_grtavfsdec`: 24 RTAVFS/global and shader-engine voltage/frequency-control window registers.
- `gc_cphypdec`: 55 CP hypervisor, CP microcode RAM, instruction-cache/data-cache base, and bound registers.
- `gc_rlcdec`: 58 RLC control, timer, doorbell, clock-count, clock-gating, and power-gating registers.

## Purpose

The purpose of this header slice is to give GC 11 AMDGPU code stable symbolic offsets for low-level graphics command processor, MES, cache fabric, performance-monitoring, RTAVFS, and RLC registers. Driver code combines these offsets with SOC15 register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and `REG_GET_FIELD`/`REG_SET_FIELD` definitions from the matching `gc_11_0_0_sh_mask.h`.

This is not policy code. It is generated hardware metadata used by policy code in `gfx_v11_0.c`, `mes_v11_0.c`, KFD GC 11 queue/MQD code, display code that needs GC register definitions, SDMA v6 support, and graphics hub initialization. The most active consumers for this chunk are MES and RLC paths: `mes_v11_0.c` programs `regCP_MES_*` instruction/data base and bound registers, scratch registers, program counters, and cache-operation controls; `gfx_v11_0.c` programs RLC control, clear-state, power-gating, clock-gating, firmware load, and status registers, and reads CP MES timer registers for clock-counter queries.

## Register Families Covered

The continued `gc_cprs64dec` portion covers MES and RS64 command-processor state. The MES group includes interrupt and scratch registers, instruction pointer, machine-mode status/cause/bad-address/IP registers, cycle/time/instret counters, ISA/vendor/architecture identifiers, timer compare registers, pipe quantum and priority controls, doorbell controls 1-6, debug interrupt pointers, GP0-GP9 scratch pairs, local data/instruction/scratch aperture registers, perfcount and pending interrupt state, interrupt data payload registers, debug and unknown interrupt status, queue current pointers, arbitration controls, busy status, command-engine switch controls, memory-mapped register access windows, and `CP_MES_MDBOUND`/`MIBOUND`-style memory range controls. The same address block then covers GFX RS64 and MEC RS64 program counter, status, interrupt, local aperture, event, debug, aperture base/mask/control, and machine-state registers. These definitions support firmware bring-up, MES scheduling, command submission, queue preemption, and post-hang debugging.

The GL1/CH/GL2/GL1H blocks provide cache and interconnect control/status offsets. They include GL1 DRAM burst masks and arbitration status, GL1C UTCL0 control/status/retry registers, CH arbitration and burst controls, channel-client credit/free-delay registers, CHC/CHCG control and status, GL2C miss-tag, ECC/XCC, invalidation, arbitration, and status registers, GL2A address-match and response-throttle registers, and GL1H arbitration controls. These are the low-level addresses for cache hierarchy tuning, invalidation status, retry/error diagnosis, and fabric arbitration.

The `gc_perfddec` and `gc_perfsdec` blocks are the largest middle section. The data block maps low/high result registers for performance counters across CP front-end subblocks (`CPG`, `CPC`, `CPF`), GRBM, graphics frontend and shader blocks (`PA`, `SPI`, `SQ`, `SQG`, `SX`), texture/cache blocks (`TA`, `TD`, `TCP`, `GL1A`, `GL1C`, `GL1H`, `GL2A`, `GL2C`, `UTCL1`), render and data-share blocks (`CB`, `DB`, `GDS`, `RMI`), and GUS/GCEA. The selector/control block maps the corresponding select, mode, counter-control, result-control, binning/sample-finish, latency-stat, and draw-window registers. Together these offsets are the address side of GPU performance monitoring: the field masks in the sibling sh-mask header define how to select events and modes, while these macros tell the driver where to read or program them.

The GRT/RTAVFS portions cover register-address, write-data, read-data, control/status, target frequency, target voltage, soft reset, PSM control, and clock-control windows for both global and shader-engine RTAVFS instances. The shorter `gc_grtavfsdec` block exposes the legacy/simple `regRTAVFS_RTAVFS_REG_ADDR` and `regRTAVFS_RTAVFS_WR_DATA` aliases. These are integration surfaces for adaptive voltage/frequency and clock-control firmware or PM paths, even though this header itself does not sequence voltage or frequency changes.

The `gc_cphypdec` block maps CP hypervisor and CP microcode RAM surfaces. It includes `regCP_HYP_PFP_UCODE_ADDR/DATA`, ME/MEC hypervisor microcode address/data aliases, PFP/ME/CPC/MES instruction-cache base/control/operation registers, MES instruction/data base and bound aliases (`MIBASE`, `MDBASE`, `MIBOUND`, `MDBOUND`), GFX RS64 data-cache and instruction-bound registers, and MEC data/instruction base/bound registers. Several macro names intentionally alias the same offset, such as `regCP_HYP_PFP_UCODE_ADDR` and `regCP_PFP_UCODE_ADDR`, or `regCP_MES_IC_BASE_LO` and `regCP_MES_MIBASE_LO`. These aliases let different driver subsystems use names matching their programming model while targeting the same register.

The `gc_rlcdec` block begins the RLC register map. This chunk includes RLC enable/status, F32 microcode version, reference/GPU/clock counters, GPM timer interrupt/control/status, interrupt status/clear registers, MGCG and CGCG/CGLS controls, jump-table restore, power-gating delays, ucode control, GPM thread reset/priority/enable/invalidate-cache controls, CP DMA completion status, RLCG doorbell control/status/range and four doorbell data pairs, GPU clock 32-bit selector/value, dynamic power-gating status/request, WGP status, always-on WGP mask, maximum power-gated WGP, and auto power-gating control. Later RLC registers are outside this chunk.

## Important APIs, Types, And Macros

This chunk declares no functions, structs, enums, or runtime storage. Its API is the generated macro naming convention:

- `reg<REGISTER>` gives the register offset used by SOC15 register accessors.
- `reg<REGISTER>_BASE_IDX` gives the register base-index selector. Every macro in this chunk uses base index `1`.
- Address-block comments, such as `// addressBlock: gc_perfsdec`, document the hardware decode block associated with the following offsets.
- Matching field macros live in `gc_11_0_0_sh_mask.h`; matching reset/default values live in `gc_11_0_0_default.h` where generated.

The driver-level API contract is compile-time name composition. A call such as `WREG32_SOC15(GC, 0, regRLC_CNTL, value)` depends on `regRLC_CNTL` from this file, while `REG_SET_FIELD(value, RLC_CNTL, RLC_ENABLE_F32, 1)` depends on the sibling sh-mask header. Golden register tables, debug register lists, register dump helpers, and KFD/MES setup code all rely on the spelling and numeric offsets staying in sync with the generated hardware database.

## Control Flow

There is no executable control flow in this header. The implied runtime flows are in consumers:

1. GC 11 initialization includes this header and selects registers through `reg...` symbols.
2. MES boot/setup code writes MES program-counter, instruction-cache, data-cache, scratch, bound, control, and cache-operation registers before starting MES firmware and later reads GP/status/time registers for scheduler state and diagnostics.
3. RLC initialization and power-management code writes clear-state buffer pointers, loads RLC/GPM/LX6/PACE/GPU IOV firmware through RLC ucode address/data registers, enables RLC F32, adjusts GPM thread enables, and toggles RLC power/clock-gating controls.
4. Performance monitoring code programs select/mode/control registers from `gc_perfsdec`, starts or gates counters, then reads result registers from `gc_perfddec`.
5. Debug, reset, and hang-dump paths read MES, GL/cache, RLC, and perf registers to report current hardware state.

The header is therefore upstream of many runtime branches, but the branch decisions and polling loops live in C source files such as `gfx_v11_0.c`, `mes_v11_0.c`, and KFD GC 11 queue management.

## State And Persistence

The macros themselves are immutable compile-time constants and hold no software state. The represented hardware state is volatile MMIO or indirect-register state owned by the GPU and firmware.

MES state persists while the MES firmware is running: scratch registers, instruction/data base and bounds, program counters, doorbell controls, pending interrupts, GP registers, queue pointers, and timer/cycle counters can be read back after setup or failure. Driver code also stores some values read from these registers into software structures, for example MES scheduler or KIQ version values read from `regCP_MES_GP3_LO` in later MES code paths.

RLC state controls persistent device behavior across the active GPU session. Enabling `RLC_CNTL`, setting power-gating controls, programming GPM thread enables, loading firmware through ucode address/data registers, and configuring clock-gating overrides remain active until changed, reset, or reinitialized after suspend/resume or GPU reset. Clock counters, interrupt latches, doorbell data, and perf counters are live diagnostic state and can change asynchronously.

Performance counter state is programmable and transient. Selector/control registers define what each counter observes; result registers accumulate until reset, stopped, or overwritten by hardware policy. RTAVFS registers represent hardware/firmware voltage-frequency control windows and should be treated as stateful control/status endpoints rather than ordinary scratch registers.

## Dependencies And Integration Points

This generated offset header depends on the surrounding GC 11 register-description set:

- `gc_11_0_0_sh_mask.h` supplies bit fields for the same register names.
- `gc_11_0_0_default.h` supplies default/reset values for generated registers where available.
- SOC15 register helpers convert `reg...` offsets plus block/instance/base-index data into MMIO addresses.
- `mes_v11_0.c` uses the MES and CP hypervisor aliases for firmware setup, scratch programming, instruction/data aperture setup, cache invalidation, and scheduler state reads.
- `gfx_v11_0.c` uses RLC offsets for firmware loading, clear-state buffer setup, RLC enable/disable, safe-mode/power-gating/clock-gating control, register access lists, and hang diagnostics.
- KFD GC 11 queue and MQD management includes this header with the sh-mask header for queue scheduling and compute integration.
- Performance-monitoring and profiling paths depend on the perf data/select offsets to match hardware event-selection field definitions.

The aliasing between `regCP_HYP_*`, `regCP_PFP_*`, `regCP_ME_*`, `regCP_MEC_*`, and `regCP_MES_*` names is an integration detail, not duplication to clean up casually. Different parts of the driver use the alias that matches the engine being programmed.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. These offsets are numeric constants; an incorrect value or wrong base index can compile cleanly and make the driver read or write a different register. That can cause MES boot failure, incorrect queue scheduling, firmware load corruption, invalid cache apertures, broken performance counters, bad clock/power-gating behavior, or misleading hang dumps.

High-risk groups in this chunk include MES instruction/data base and bound registers (`regCP_MES_IC_BASE_*`, `regCP_MES_MIBASE_*`, `regCP_MES_DC_BASE_*`, `regCP_MES_MDBASE_*`, `regCP_MES_MIBOUND_*`, `regCP_MES_MDBOUND_*`), because MES firmware execution depends on those ranges; `regCP_MES_DOORBELL_CONTROL*` and queue pointer/status registers, because doorbell and scheduling mistakes can strand queues; CP hypervisor and microcode RAM aliases, because firmware upload paths write through them; RLC control, ucode, GPM thread, and power-gating registers, because they affect global graphics management; and perf select/result pairs, because a mismatched data/select pair produces plausible but wrong profiling data.

Generated alias pairs are an edge case for review. Multiple macro names can intentionally map to the same offset, for example instruction-cache names and machine-instruction-base aliases. Removing or renaming one alias can break consumers even if another numeric macro still exists. The chunk also starts mid-address-block, so analyses must include the preceding `gc_cprs64dec` context to avoid treating `regCP_MES_INTERRUPT` as the first register in the block.

Because this is generated source, manual edits should be avoided. If the hardware database is regenerated, offsets, base indices, sh-mask fields, and default values must be updated as a set.

## Test Signals

Useful compile-time signals are AMDGPU and AMDKFD builds that include `gc_11_0_0_offset.h`. Missing or renamed macros used by `gfx_v11_0.c`, `mes_v11_0.c`, KFD queue/MQD code, display code, SDMA v6, or gfxhub v3 fail at compile time.

Runtime validation needs GC 11 hardware or equivalent register emulation. Strong signals include successful GPU probe, MES firmware boot, KIQ/scheduler version reads, queue creation and submission through KFD and graphics paths, successful RLC firmware loading, clean suspend/resume and GPU reset recovery, and no hangs during RLC power-gating or clock-gating transitions.

Performance and diagnostic signals include sane perf-counter programming/readback across CP, GRBM, PA/SPI/SQ/SX, texture/cache, CB/DB/GDS/RMI, GL1/GL2, and UTCL1 blocks; stable MES timer reads from `regCP_MES_MTIME_*`; useful hang dumps for MES/RLC registers; correct RTAVFS control/status behavior under PM tests; and no unexpected cache retry, invalidation, ECC/XCC, doorbell, or RLC interrupt status changes after initialization.
