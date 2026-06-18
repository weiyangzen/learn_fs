# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 2579-5025

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains C preprocessor constants only: each register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for composing or decoding 32-bit hardware register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this line range.

The selected lines start at the body of `SDMA0_F32_CNTL`, then cover SDMA0 performance counter control/result registers, SDMA0 clock/power override bits, GRBM global graphics status/reset/error/trap/scratch registers, CP command-processor debug/status/FIFO/register-queue counters, PA/VGT/GE front-end controls, SQ/SQC/LDS/shader debug and watchpoint controls, SPI shader-processor counters/trap-screen/debug controls, TD/TA texture block controls, GDS status/protection/EDC registers, and the beginning of `DB_DEBUG`. The range ends after only the first several `DB_DEBUG` masks; the remaining masks continue after line 5025 in the adjacent chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 11.5.0 graphics IP and is not Ceph filesystem logic.

## Purpose

`gc_11_5_0_sh_mask.h` supplies field layouts for GC 11.5.0 registers. Driver code pairs these macros with register addresses from the matching `gc_11_5_0_offset.h` header, then usually uses helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` so register programming and diagnostics do not embed magic bit positions.

This chunk focuses on control, observability, fault reporting, and low-level debug for major graphics blocks:

- SDMA0 firmware/F32 and performance counter state: `SDMA0_F32_CNTL` controls F32 halt, checksum clear, thread reset/enable, and thread priorities. `SDMA0_PERFCNT_*` and `SDMA0_PERFCOUNTER*` define event selection, modes, enable/clear controls, result selection, and low/high counter result fields.
- SDMA0 clock override: `GFX_ICG_SDMA0_CTRL` exposes soft overrides for F32, performance-counter, copy-engine, dynamic, and register clocks.
- GRBM register-bus manager state: `GRBM_STATUS*`, `GRBM_SOFT_RESET`, clock/idle controls, read/write error attribution, trap address/data/mask registers, IH credits, UTCL2 invalidation ranges, invalid-pipe logging, fence ranges, scratch registers, and asynchronous VF violation state.
- CP command processor state: CPC/CPF/CP debug, busy, stalled, status, GRBM free-count, header dump, scratch indexed access, ring-buffer read/write pointer, queue threshold/availability, ROQ/STQ/MEQ stats, command index/data, and queue doorbell status macros.
- PA/VGT/GE front-end state: DMA FIFO depths, draw-init FIFO depth, memory-controller latency/timestamp controls, wave-dispatch/primitive configuration, UTCL1 controls/status, unit-disable and rate controls, geometry engine safe/status controls, shader-array configuration, and PA clipping/setup/scissor FIFO status.
- SQ/SPI shader state: SQ/SQC/LDS configuration, wave priority, FIFO sizes, arbitration, trap/watchpoint status, GL1H/SQG status, shader-rate config, interrupt masking, watchpoint address/control windows, indirect index/data, commands, SPI wave lifetime counters/status, load-balancer counters, WGP masks, export/scoreboard buffer sizes, active-wave counters, trap-screen base/mask/GPR windows, and crawler configs.
- TP and GDS state: TD/TA texture controls, power/status/scratch registers, GDS global status/enhancement, protection and VM-protection fault attribution, and EDC counters for GDS memory/input queue/GRBM/OA paths.
- RB depth-buffer debug state: the first part of `DB_DEBUG`, covering compression/read/HiZ/HiS/fast-Z/stencil/noop-cull/z-plane/sync disable and force fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the mask for that field in the register value.
- Register-address symbols live in the companion `gc_11_5_0_offset.h` header, commonly with `reg...` or `mm...` names matching the register.
- AMDGPU consumers use these constants through register helpers, direct MMIO helpers, ring packet writers, debug dump code, reset paths, perf counter paths, VM/fault handlers, and KFD/compute queueing code.

The chunk contains 2,172 `#define` entries across 244 register names: 1,093 shift macros and 1,079 mask macros. The address-block inventory is:

- `gc_sdma0_sdma0perfsdec`: SDMA0 performance-counter selector/configuration registers.
- `gc_sdma0_sdma0perfddec`: SDMA0 performance-counter low/high result windows.
- `gc_sdma0_sdma0pwrdec`: SDMA0 internal clock-gating override control.
- `gc_grbmdec`: GRBM status, reset, clock, trap, error, scratch, fence, invalidation, and violation registers.
- `gc_cpdec`: CP/CPC/CPF busy/stall/status/debug, queue, ring, threshold, and command registers.
- `gc_padec`: VGT, WD, GE, IA, PA, and shader-array front-end controls/status.
- `gc_sqdec`: SQ/SQC/LDS/SP/SQG controls, debug, interrupts, watchpoints, and indexed command/data registers.
- `gc_shsdec`: SX/SPI controls, EDC, wave lifetime, load-balancer, active-wave, trap-screen, and crawler registers.
- `gc_tpdec`: TD/TA texture block controls/status/scratch.
- `gc_gdsdec`: GDS configuration, status, protection fault, VM fault, and EDC registers.
- `gc_rbdec`: the opening `DB_DEBUG` bitfield definitions.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU is:

1. Select the GC 11.5.0 register headers for an ASIC with `IP_VERSION(11, 5, 0)`.
2. Choose the matching address macro from `gc_11_5_0_offset.h`.
3. Read a current register value, construct a register write, or prepare a command packet/debug dump/perf access.
4. Use the `__SHIFT` and `__MASK` pairs, normally through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract a single field.
5. Feed the resulting value into VM setup, GFX/SDMA bring-up, idle waits, reset, performance monitoring, KFD queue handling, trap/fault reporting, hang diagnostics, or power/debug configuration.

For SDMA and performance counters, consumers select events/modes, clear and enable counters, then read low/high result registers. For GRBM and CP status, consumers poll or snapshot busy/stalled/clean bits during idle waits, reset decisions, hang dumps, and debugfs-style diagnostics. For SQ/SPI/GDS/DB fields, consumers generally program debug controls, watchpoints, trap screens, counters, or decode fault/EDC status. Required ordering, delays, clear-on-read behavior, latching, and side-effect sequencing are not expressed in this header; those rules live in engine code and the hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware-owned state that is live, latched, sticky, or side-effectful depending on the register.

SDMA0 F32 and clock override fields affect active engine behavior while programmed. Halting or resetting F32 threads, clearing checksums, changing priorities, or overriding internal clocks can alter queue execution, firmware servicing, power behavior, or diagnostics until the fields are restored or the engine is reset.

Performance counter configuration fields persist selected events, modes, enable/clear state, and result-selection state while counters accumulate. Counter result registers expose hardware values that may require documented read ordering or latching to avoid torn high/low snapshots. This chunk can identify bit widths but cannot guarantee atomicity or saturation behavior.

GRBM and CP status fields are mostly volatile snapshots of busy, stalled, request-pending, free-count, FIFO, pointer, and active/clean state. Error, trap, invalid-pipe, write/read fault, violation, protection, and interrupt-status fields may be sticky until cleared through a documented sequence. `GRBM_SOFT_RESET`, `GRBM_PWR_CNTL2`, clock-gating controls, and CP queue controls have direct side effects and should not be handled as passive status.

Scratch, fence-range, trap-screen, watchpoint, indexed data, and GDS configuration registers can persist driver or firmware state across ordinary operation until overwritten, context-switched, power-gated, or reset. In virtualized/SR-IOV contexts, VF/VFID/VMID/SSRCID/TMZ/security-write fields must be decoded exactly because they attribute faults, resets, and illegal accesses to specific functions or address spaces.

Reserved and `UNUSED` fields appear throughout the generated map. Callers should preserve such bits during read-modify-write unless the hardware documentation requires a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` provides the matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c` directly includes both `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h` for GC 11.5.0 VM/GART/fault setup and demonstrates the intended `REG_SET_FIELD`/`REG_GET_FIELD` usage.
- `gfx_v11_0.c`, `gmc_v11_0.c`, `mes_v11_0.c`, `amdgpu_discovery.c`, KFD device selection, PSP/ucode loading, PM/SMU code, and display family selection all contain `IP_VERSION(11, 5, 0)` integration points that select GC 11.5.0 behavior, firmware, or family-specific paths.
- Common AMDGPU helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD` perform the actual MMIO access and field packing/extraction.

Runtime integration points include SDMA0 performance monitoring and firmware debug, graphics idle waits, GPU reset/hang recovery, GRBM read/write error logging, CP queue and command processor diagnostics, CP interrupt and ring-pointer handling, KFD queue/debug operations, shader watchpoint/trap support, GDS aperture/fault handling, GDS EDC reporting, texture/front-end status dumps, VM protection fault reporting, and depth-buffer debug/golden-register programming.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can write the wrong bit, corrupt hardware state, or decode misleading diagnostics.
- This chunk has partial-boundary coverage. It starts immediately after the `//SDMA0_F32_CNTL` comment and ends before all `DB_DEBUG` masks are present, so file-level research must merge this with adjacent chunks.
- Side-effect registers are intermixed with passive status registers. Misusing `SDMA0_F32_CNTL`, `GFX_ICG_SDMA0_CTRL`, `GRBM_SOFT_RESET`, `GRBM_PWR_CNTL2`, CP queue controls, SQ commands, SPI trap/crawler controls, or `DB_DEBUG` can hang active work, change timing, lose debug state, or perturb rendering.
- Busy/stalled/free-count/status bits are volatile. Polling code must handle transitions, clock-gated blocks, in-flight command streams, and blocks that legitimately remain busy during firmware activity.
- High/low result and pointer registers can be race-prone if read without the documented latch/order sequence. This applies to performance counters, instruction pointers, ring read pointers, and trap/status snapshots.
- Address and identity fields are often encoded, aligned, or split. Treating shifted fields as raw byte addresses can produce plausible but wrong trap, fence, context, or fault addresses.
- Virtualization/security attribution fields are high impact. VF/VFID/VMID/SSRCID/TMZ/security-write bits in GRBM, GDS, and CP paths must remain exact for SR-IOV isolation and fault reporting.
- Reserved and `UNUSED` masks cover large portions of several registers. Full-register writes that do not preserve undocumented bits may introduce ASIC-specific regressions.
- Symmetric-looking status families across CP pipes, ME/MEC engines, SPI wave counters, and GDS OA paths are prone to copy/generator mistakes; one wrong field width can make only one pipe or WGP class misreport.
- `DB_DEBUG` fields can disable compression, fast-Z/stencil, z-plane optimization, or surface sync. Debug settings may mask real rendering bugs or create performance regressions if left programmed outside diagnostic/golden-register paths.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include or indirectly depend on `gc_11_5_0_sh_mask.h`, especially GC 11.5.0 VM, GFX, MES/SDMA, reset, KFD, PM, debug, and perf paths.
- Mechanical comparison against AMD's authoritative GC 11.5.0 register database to confirm every `__SHIFT` and `__MASK` value in lines 2579-5025.
- Cross-checks that all 244 register names in this chunk have matching address definitions in `gc_11_5_0_offset.h`.
- Static mask/shift sanity checks: masks should align with shifts, fields for one register should not overlap unless documented, full-width data fields should use `0xFFFFFFFFL`, and repeated low/high/result/status families should have consistent widths.
- SDMA0 tests that program performance counters, clear/enable/disable them, run controlled DMA workloads, read low/high results, and check for monotonic or expected activity.
- GFX idle and reset tests that poll `GRBM_STATUS*`, exercise `GRBM_SOFT_RESET` paths, and verify post-reset engine recovery without impossible busy/clean combinations.
- Hang/debug dump tests that decode GRBM read/write errors, invalid-pipe logs, CP busy/stalled/status registers, CP ring/read pointers, queue thresholds/availability, SQ/SPI active-wave counters, and GDS fault/EDC registers.
- SR-IOV or virtualized-device tests that trigger faults or reset requests and verify VF/VFID/VMID/SSRCID/TMZ attribution in GRBM/GDS/CP-related logs.
- Shader debug tests for SQ watchpoints, trap-screen base/mask/GPR windows, SPI lifetime counters, load-balancer counters, and crawler controls.
- Rendering and conformance tests after any `DB_DEBUG` or depth-buffer debug programming changes, with attention to compression, HiZ/HiS, fast-Z/stencil, z-plane optimization, and depth/HTILE synchronization behavior.
- Runtime warning signals include SDMA0 perf counter nonsense, failed idle waits, GPU reset loops, wrong fault attribution, CP queue stalls, impossible GRBM/CP status dumps, unexpected GDS protection faults, EDC counter spikes, shader trap misrouting, or depth-buffer rendering/performance regressions.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002550`. It covers lines 2579-5025 of `gc_11_5_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to include the immediately preceding SDMA0 decode fields and the remaining `DB_DEBUG` masks after line 5025.
