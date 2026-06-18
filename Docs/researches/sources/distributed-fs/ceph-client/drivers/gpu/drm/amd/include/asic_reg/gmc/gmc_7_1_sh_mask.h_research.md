# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002734`: lines 1-5205, `Docs/researches/chunks/subset-b-002734_research.md`
- `subset-b-002735`: lines 5206-10157, `Docs/researches/chunks/subset-b-002735_research.md`
- `subset-b-002736`: lines 10158-14416, `Docs/researches/chunks/subset-b-002736_research.md`

## Chunk Research

### subset-b-002734: lines 1-5205

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_1_sh_mask.h lines 1-5205

## Scope

This chunk is the first 5,205 lines of the generated AMD GMC 7.1 shift/mask register header. It contains preprocessor constants only: hardware register fields are exposed as `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` macros so C code can pack, update, and decode 32-bit MMIO values.

The requested range covers the license and include guard plus 5,180 `#define` lines across roughly 458 register groups. Within this chunk there are 2,590 mask constants and 2,589 shift constants; the mismatch is intentional at the artificial chunk boundary, because line 5205 ends on `MC_MCBVM_PERFCOUNTER3_CFG__PERF_SEL_END_MASK` and its matching shift is in a later line outside this work item.

Although the repository path is under `distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata for the CIK/GMC 7.x memory-controller generation. It does not implement Ceph or filesystem behavior.

## Purpose

`gmc_7_1_sh_mask.h` describes the bit layout of GMC 7.1 memory-controller, graphics memory hub, virtual-memory, crossbar, peer-to-peer, and performance-counter registers. Driver code pairs these constants with register offsets from the companion GMC offset headers and then uses AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, and `WREG32`.

This chunk covers these major hardware surfaces:

- MC arbiter configuration, aging, refresh, DRAM timing, list management, write/read arbitration, return credits, error correction, replay, address swizzle/hash, power management, and busy/status reporting.
- CITF client-interface controls for graphics/local/hub clients, credits, DAGB delay, group routing, watermark decrements, local read/write client knobs, performance monitor state, and CITF clock-gating controls.
- MC hub read-request, write-data-path, write-return, credit, bypass, shared delay, idle/status, blackout, and clock-gating controls for GPU clients including GFX, RLC, SDMA, display/DMIF, UVD, VCE, ACP, CP, XDMA, ISP, HDP, SMU, VMC, IA, CPG/CPF/CPC, and memory-channel blocks.
- MC RPB, shared channel mapping/remapping, read/write group maps, memory aperture registers, L1 TLB debug/status registers, and MCD/MCD clock-gating configuration.
- MC XPB routing, destination mapping, cross-link gateway configuration, loopback/address matching, unclean thresholding, write-combine buffer status/configuration, P2P BAR and peer system BAR registers, XPB interface/status/sub-control, sticky bits, and XPB clock gating.
- MC XBAR address-decode, remote, credit, channel remap, two-channel, arbitration, burst, and performance-monitor registers.
- Low/high performance counter value registers and the beginning of per-block performance-counter configuration registers for CITF, HUB, RPB, ARB, MCBVM, and related blocks.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, locks, allocations, callbacks, or direct MMIO operations in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>_MASK` gives the raw bit mask for a field.
- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit.
- Consumer code normally writes `REG_SET_FIELD(value, REGISTER, FIELD, new_value)` or `REG_GET_FIELD(value, REGISTER, FIELD)`, which depends on these exact macro names.
- Matching register address names are in GMC offset headers such as `gmc_7_1_d.h`/related generated register files included by the same CIK-era sources.

Important register groups in this chunk include:

- `MC_CONFIG`, `MC_CONFIG_MCD`, `MC_CG_CONFIG`, and `MC_CG_CONFIG_MCD`: enable reads/writes for memory-controller channels/MCDs and indexed access modes.
- `MC_ARB_*`: arbiter aging, ECC/GECC2 status and injection/debug, address swizzle/hash, DRAM timing, refresh, power-management override, group decode, list management, replay, return credits, max-latency capture, busy status, and clock gating.
- `MC_CITF_*`, `MC_RD_*`, and `MC_WR_*`: client-interface credit allocation, read/write grouping, local/hub/TC/CB/DB client throttling, watermark decrement, performance monitor, and CITF clock-gating fields.
- `MC_HUB_MISC_*`, `MC_HUB_RDREQ_*`, `MC_HUB_WDP_*`, and `MC_HUB_WRRET_*`: hub idle/status bits, read-request and write-data path queue controls, per-client enable/prescale/blackout/stall/burst/lazy-timer knobs, MCD channel credit counts, bypass controls, and per-client availability/status reporting.
- `MC_RPB_*`: request path buffer configuration, ordering, switch counts, write-combine behavior, CID queue programming, TCI controls, and RPB performance counter control/status.
- `MC_VM_*`: frame-buffer and AGP apertures, system aperture bounds/default address, display-controller write hit regions, L1 TLB controls/debug/status, VM steering, and memory-channel/MCD VM-related debug.
- `MC_XPB_*`: cross-partition/bus routing apertures, destination maps, CLG configuration, P2P BAR setup, peer system BARs, interface credits/status, subblock stall/reset controls, sticky bits, and clock gating.
- `MC_XBAR_*`: memory crossbar address decode, remote routing, per-output credits, channel remapping, arbitration, max burst, and XBAR performance monitoring.
- `*_PERFCOUNTER_LO`, `*_PERFCOUNTER_HI`, and `*_PERFCOUNTER*_CFG`: split counter values, compare values, select ranges, mode, enable, and clear bits for CITF, HUB, RPB, MCBVM, MCDVM, VM L2, ARB, and ATC performance fabrics.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is:

1. A CIK/GMC7 driver source includes `gmc/gmc_7_1_sh_mask.h` and the corresponding register address header.
2. The driver reads a hardware register through `RREG32`, `RREG32_PCIE`, or a CGS/powerplay wrapper, or starts from a zero/full-register value.
3. It uses `REG_SET_FIELD`, `REG_GET_FIELD`, raw mask tests, or mask arrays to update or decode a specific field.
4. It writes the resulting value with `WREG32`/wrapper helpers, or uses the decoded field for topology, memory size, VM, display, power, or debug decisions.

Concrete integration patterns in this tree include:

- `amdgpu/gmc_v7_0.c` reads `mmMC_VM_FB_LOCATION` to derive VRAM placement, programs system/AGP apertures, uses `MC_SHARED_CHMAP__NOOFCHAN` to infer memory channels, configures `MC_VM_MX_L1_TLB_CNTL`, and toggles clock/memory light-sleep bits in `MC_HUB_MISC_*`, `MC_XPB_CLK_GAT`, and `MC_CITF_MISC_*`.
- `amdgpu/gmc_v7_0.c` uses `MC_SHARED_BLACKOUT_CNTL__BLACKOUT_MODE` around blackout/FBI enable sequencing, showing that some fields in this header participate in ordered reset/display/memory-controller transitions.
- `display/dc/resource/dce80/dce80_resource.c` maps `mmMC_HUB_RDREQ_DMIF_LIMIT` plus `MC_HUB_RDREQ_DMIF_LIMIT__ENABLE_{MASK,SHIFT}` into display resource register tables.
- `pm/powerplay/hwmgr/smu7_hwmgr.c` reads and writes `mmMC_CG_CONFIG`, connecting this mask family to power-management clock-gating policy.

The header itself does not encode required waits, polling loops, write-one-to-clear behavior, ordering around reset, whether a field is read-only, or whether a write triggers hardware action. Those semantics are in consuming code and the hardware specification.

## State And Persistence Behavior

The macros hold no software state. They describe hardware state that lives in GMC 7.1 registers.

Hardware state represented by this chunk includes:

- Persistent configuration until reset or reprogramming: channel enables, memory-channel routing/remapping, DRAM timing, arbiter policy, credit depths, queue burst/lazy timers, blackout behavior, VM apertures, L1 TLB controls, P2P BARs, crossbar routing, and clock-gating/light-sleep enables.
- Live status: arbiter and hub busy bits, outstanding client read/write bits, MCD availability, RPB/XPB pipe and buffer status, write deadlock/read deadlock warnings, TLB busy bits, sticky XPB status, and performance counter values.
- Fault and reliability state: GECC/ECC corrected/uncorrected/FED status and clear fields, replay and poison controls, debug injection fields, VM-related protection/fault support registers, and write-one-to-clear-style sticky status surfaces such as `MC_XPB_STICKY_W1C`.
- Profiling state: selected performance events, counter mode, enable/clear bits, compare values, and low/high counter values across MC subblocks.

Persistence is hardware-defined. Some registers are initialized during ASIC bring-up, resume, BACO/power transitions, or display setup and then left programmed. Others are transient status/counters or write-trigger controls. The generated macros do not distinguish safe observation from side-effecting writes.

## Dependencies And Integration Points

This chunk depends on the AMDGPU generated register ecosystem:

- Companion GMC 7.1 address/offset headers provide `mm*` register addresses such as `mmMC_VM_FB_LOCATION`, `mmMC_SHARED_CHMAP`, `mmMC_HUB_RDREQ_DMIF_LIMIT`, `mmMC_CG_CONFIG`, and `mmMC_XPB_CLK_GAT`.
- AMDGPU field helpers require the exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` names emitted here.
- CIK-era consumers include `amdgpu/gmc_v7_0.c`, `amdgpu/cik.c`, `amdgpu/cik_sdma.c`, `amdgpu/amdgpu_amdkfd_gfx_v7.c`, `amdgpu/sdma_v2_4.c`, `amdgpu/dce_v8_0.c`, `pm/powerplay/hwmgr/ci_baco.c`, `pm/powerplay/smumgr/ci_smumgr.c`, and `display/dc/resource/dce80/dce80_resource.c`.
- Closely related generated headers such as `gmc_7_0_sh_mask.h` and `gmc_8_2_sh_mask.h` share many names but not all bit layouts. Consumers must include the header matching the active ASIC generation.

Functionally, this header is integrated into memory-controller setup, VRAM aperture discovery, GPUVM/TLB programming, display read-request limiting, power/clock gating, memory-channel topology detection, reset/blackout sequencing, peer-to-peer routing, and diagnostics/performance monitoring.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong mask or shift compiles cleanly but causes the driver to program or decode the wrong hardware bits.
- The chunk boundary is artificial and ends mid-register group. `MC_MCBVM_PERFCOUNTER3_CFG__PERF_SEL_END_MASK` is present, while its matching `__SHIFT` and the rest of `MC_MCBVM_PERFCOUNTER3_CFG` are outside this chunk. The final merged file research must reconcile that continuation.
- Many register families are highly repetitive across channels, groups, clients, MCDW/MCDX/MCDY/MCDZ/MCDS/MCDT/MCDU/MCDV, and counter indices. Copy or generation errors can affect only one client/channel and be difficult to diagnose.
- Cross-generation similarity is dangerous. GMC 7.0 and 7.1 definitions are close, but line searches show differences such as additional MCDS/MCDT/MCDU/MCDV fields and shifted `MC_HUB_RDREQ_CNTL` bit positions in GMC 7.1.
- VM aperture and TLB fields are isolation-critical. Bad masks for `MC_VM_FB_LOCATION`, system aperture, AGP aperture, L1 TLB controls, or VM steering can corrupt address translation, mis-size VRAM, or route accesses outside intended memory ranges.
- Clock-gating and light-sleep fields under `MC_HUB_MISC_*`, `MC_CITF_MISC_*`, `MC_XPB_CLK_GAT`, and `MC_CG_CONFIG*` can create hangs, wakeup failures, or power regressions if toggled with incorrect masks or without required sequencing.
- Blackout, reset, stall, and self-init controls can disturb live display, hub, XPB, RPB, and memory-controller traffic. These should be changed only in the ordered paths that own those transitions.
- ECC/GECC/replay/debug-injection fields may be sticky, W1C, diagnostic-only, or fault-injection surfaces. Treating them as ordinary configuration can clear evidence or inject hardware errors.
- Low/high performance counters can race hardware updates. This header gives masks, but not a coherent sampling method.
- Reserved/debug fields such as `DEBUG_RSV`, `RSVD*`, `TBD_FIELD`, and generic `FIELDNAME*` should generally be preserved during read-modify-write unless authoritative init tables specify full register values.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU CIK/GMC7 paths that include this header, especially `gmc_v7_0.c`, `cik.c`, `cik_sdma.c`, `amdgpu_amdkfd_gfx_v7.c`, `sdma_v2_4.c`, `dce_v8_0.c`, `ci_baco.c`, `ci_smumgr.c`, and `dce80_resource.c`.
- Mechanically compare this range against AMD's authoritative GMC 7.1 register database. Every complete field in the range should have aligned mask/shift pairs, and the known line-5205 boundary should be completed by the next chunk.
- Cross-check against companion offset/address headers so every register group used with `REG_SET_FIELD`/`REG_GET_FIELD` has matching `mm*` addresses for GMC 7.1.
- Run static mask sanity checks: masks should align with shifts, repeated client/channel groups should have expected structural symmetry, full-width fields should use full masks, and reserved fields should not overlap named fields.
- Boot and initialize CIK/GMC7 hardware, verifying VRAM size/aperture discovery, memory-channel count detection, MC blackout transitions, VM/TLB enablement, and display initialization complete without register access warnings.
- Exercise suspend/resume, BACO/power transitions, clock-gating toggles, and display on/off paths. Relevant regressions include hangs on wake, memory-controller busy bits stuck, display underflow, or incorrect `MC_HUB_MISC_IDLE_STATUS`.
- Run GPUVM and GART tests that program system/AGP/framebuffer apertures, enable L1/L2 translation, invalidate TLBs, and validate fault reporting.
- Run SDMA, graphics, display, UVD/VCE, and KFD workloads concurrently to stress hub/CITF credits, read/write groups, MCD availability, and arbitration fairness.
- Validate performance counters by programming covered `*_PERFCOUNTER*_CFG` registers, reading low/high counter pairs, and checking that controlled memory/display/SDMA/GFX traffic moves the expected counters.
- Run ECC/RAS/debug tests only where supported by hardware and platform policy, confirming GECC status/clear/replay/debug masks decode observed faults correctly.

## Cross-Chunk Notes

This chunk starts at the top of `gmc_7_1_sh_mask.h` and covers the first part of the generated GMC 7.1 mask namespace through the beginning of `MC_MCBVM_PERFCOUNTER3_CFG`. Later chunks are required for the remainder of that performance-counter group and the rest of the 14,416-line header. The final per-file research should merge this chunk with later chunks before making file-wide claims about the complete GMC 7.1 register field set.

### subset-b-002735: lines 5206-10157

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_1_sh_mask.h lines 5206-10157

## Scope And Purpose

This chunk is a generated-style AMD GMC 7.1 register mask header slice. It contains only C preprocessor constants of the form `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT`; it defines no functions, structs, enums, global storage, locks, or executable branches. The source path is under a `ceph-client` mirror, but the content is AMDGPU DRM hardware metadata for the Graphics Memory Controller, not Ceph filesystem logic.

The range starts in the tail of `MC_MCBVM_PERFCOUNTER3_CFG` at line 5206 and ends inside `MC_IO_DEBUG_UP_37` at line 10157. Whole-file research should merge this with neighboring chunks before treating those edge register groups as complete.

The chunk provides bit layouts for these main GMC 7.1 hardware domains:

- Lines 5206-5447: memory-controller, VM, ATC, CHUB ATC, and MC arbiter performance-counter configuration/result controls.
- Lines 5449-5739: ATC apertures, ATS/PASID fault/status/debug controls, ATC L1/L2 TLB controls, and VMID-to-PASID mapping fields.
- Lines 5743-5909: GMCON register-engine, stutter/save-restore, power-gating FSM, performance monitor, mask, low-power target, and debug fields.
- Lines 5909-6307: VM L2, VM contexts, page-table base/start/end addresses, invalidation request/response bits, PRT apertures, context disable bits, protection fault reporting, and identity-aperture fields.
- Lines 6309-8385: memory sequencer, DRAM timing, power-management commands, impedance, wakeup/training, IO TX/RX/CDR/drive controls, framing, FIFO, pad controls, and NPL status fields.
- Lines 8385-8569: memory BIST command/control/address/compare/data/mismatch/readback masks.
- Lines 8569-9393: MC sequencer performance/status, vendor/reserve/supplemental registers, remap tables, low-power timing variants, TCG/TSM controls, timers, PHY timing, MCLK power, and DLL controls.
- Lines 9403-9653: MPLL microcode, control mode, function control, spread-spectrum, timing, control, and status fields.
- Lines 9653-9743: MC sequencer PMG power-gating hardware/software controls.
- Lines 9743-10157: TSM debug and IO debug index/data/readout fields.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The usable interface is the macro namespace consumed by AMDGPU register programming code together with the companion address header `gmc_7_1_d.h`.

Important macro families include:

- Performance counters: `MC_MCDVM_PERFCOUNTER[0-3]_CFG`, `ATC_PERFCOUNTER[0-3]_CFG`, `MC_VM_L2_PERFCOUNTER[0-1]_CFG`, `CHUB_ATC_PERFCOUNTER[0-1]_CFG`, and result controls such as `MC_CITF_PERFCOUNTER_RSLT_CNTL`, `MC_HUB_PERFCOUNTER_RSLT_CNTL`, `MC_RPB_PERFCOUNTER_RSLT_CNTL`, `MC_MCBVM_PERFCOUNTER_RSLT_CNTL`, `MC_MCDVM_PERFCOUNTER_RSLT_CNTL`, `MC_VM_L2_PERFCOUNTER_RSLT_CNTL`, `MC_ARB_PERFCOUNTER_RSLT_CNTL`, `ATC_PERFCOUNTER_RSLT_CNTL`, and `CHUB_ATC_PERFCOUNTER_RSLT_CNTL`.
- Address translation and ATS: `ATC_VM_APERTURE[0-1]_{LOW_ADDR,HIGH_ADDR,CNTL,CNTL2}`, `ATC_ATS_CNTL`, `ATC_ATS_DEBUG`, `ATC_ATS_FAULT_DEBUG`, `ATC_ATS_STATUS`, `ATC_ATS_FAULT_CNTL`, `ATC_ATS_FAULT_STATUS_INFO`, `ATC_ATS_FAULT_STATUS_ADDR`, default-page controls, `ATC_L1*`, `ATC_L2*`, `ATC_VMID_PASID_MAPPING_UPDATE_STATUS`, and `ATC_VMID[0-15]_PASID_MAPPING`.
- VM state: `VM_L2_CNTL*`, `VM_CONTEXT[0-1]_CNTL*`, `VM_CONTEXT[0-15]_PAGE_TABLE_BASE_ADDR`, `VM_INVALIDATE_REQUEST`, `VM_INVALIDATE_RESPONSE`, `VM_PRT_*`, `VM_CONTEXTS_DISABLE`, `VM_CONTEXT[0-1]_PROTECTION_FAULT_*`, `VM_FAULT_CLIENT_ID`, and identity aperture registers.
- GMCON and power state: `GMCON_RENG_*`, `GMCON_MISC*`, `GMCON_STCTRL_REGISTER_SAVE_*`, `GMCON_PERF_MON_*`, `GMCON_PGFSM_*`, `GMCON_MASK`, `GMCON_LPT_TARGET`, and `GMCON_DEBUG`.
- DRAM/memory sequencer and IO: `MC_SEQ_CNTL*`, `MC_SEQ_DRAM*`, timing registers, PMG command/config registers, impedance registers, training/wakeup capture/mask/clear registers, `MC_IO_TXCNTL_*`, `MC_IO_RXCNTL*`, `MC_IO_CDRCNTL*`, framing registers, `MC_IO_PAD_CNTL*`, and `MC_NPL_STATUS`.
- BIST and diagnostics: `MC_BIST_*`, `MC_SEQ_PERF_*`, `MC_SEQ_STATUS_*`, `MC_SEQ_SUP_*`, byte/bit remap registers, TCG/TSM controls, MPLL controls/status, PMG power-gating switches, `MC_TSM_DEBUG_*`, and `MC_IO_DEBUG_UP_*`.

Common field patterns are full-width data fields (`*_MASK 0xffffffff` with shift 0), packed per-VMID/per-channel bitmaps, repeated counter `PERF_SEL/PERF_MODE/ENABLE/CLEAR` fields, paired low/high address fields, and D0/D1 channel variants for DRAM/PHY/IO controls.

## Control Flow

This header has no local runtime control flow. The implied consumer flow is:

1. Include `gmc_7_1_d.h` for a register address and `gmc_7_1_sh_mask.h` for the bitfield contract.
2. Read or compose a 32-bit register value using the relevant mask and shift macros.
3. Write MMIO or indirect registers through AMDGPU helpers, or decode hardware readback/fault/status values.
4. Rely on the surrounding driver for sequencing, polling, locking, reset ordering, power-state transitions, and error handling.

The control-sensitive behavior described by these fields lives in hardware and in consumers such as GMC v7 initialization, VM setup/invalidation, CIK platform code, SDMA v2 paths, DCE v8 display code, KFD GFX v7 integration, and CI-era power-management code that include this header.

## State And Persistence Behavior

The file itself is stateless, but the constants describe persistent or volatile GPU register state once used by driver code.

VM and ATC fields are persistent translation configuration until reset or reprogramming. Page-table base/start/end fields, VM context control bits, VMID/PASID mappings, PRT apertures, identity apertures, invalidation request/response bits, and fault enable/default/report fields directly affect GPU virtual-memory access, PASID attribution, protection fault reporting, and TLB invalidation behavior.

GMCON and MC sequencer fields govern memory-controller low-power behavior, register save/restore ranges, stutter/self-refresh gating, power-gating FSM programming, DRAM timing, IO training, and PLL controls. These settings are hardware state and can remain active across normal operation until power management, reset, resume, or ASIC-specific initialization changes them.

Performance-counter selector and result-control fields persist as hardware counter mux/configuration state, while the counter values and status bits are volatile observations. BIST, training, TSM, and IO debug fields are mostly diagnostic or test state: some are commands or enables, while others capture read-only status from memory test, PHY training, or debug buses.

## Dependencies And Integration Points

This header is paired with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_1_d.h`, which supplies the corresponding `mm*` register addresses. It is directly included by AMDGPU/AMDKFD and display/power-management sources, including `amdgpu/cik.c`, `amdgpu/gmc_v7_0.c`, `amdgpu/cik_sdma.c`, `amdgpu/sdma_v2_4.c`, `amdgpu/amdgpu_amdkfd_gfx_v7.c`, `amdgpu/dce_v8_0.c`, `pm/powerplay/hwmgr/ci_baco.c`, `pm/powerplay/smumgr/ci_smumgr.c`, and `display/dc/resource/dce80/dce80_resource.c`.

Key integration surfaces are:

- GMC v7 VM bring-up, page-table programming, VM fault handling, PRT aperture setup, L2 cache control, and invalidate request/response handling.
- KFD GFX v7 queue/device integration where PASID, VMID, retry, and fault behavior must line up with the hardware VM contract.
- SDMA and display blocks that need consistent GMC aperture, VM, clock-gating, and memory-system register definitions for CIK-era ASICs.
- CI/Bonaire-era power management and BACO/SMU paths that coordinate memory controller low-power states, stutter, register save/restore, power-gating, and PLL/clock controls.
- Debug, diagnostic, and performance tooling that configures MC/ATC/VM counters, reads fault/status fields, runs memory BIST, or captures PHY/TSM/IO debug signals.

## Risks And Edge Cases

- Hardware contract drift is the dominant risk. These masks and shifts compile even if wrong, but a wrong bit position can silently program the wrong VM, ATC, DRAM, power, or PLL field.
- The range begins and ends mid-context. `MC_MCBVM_PERFCOUNTER3_CFG` lacks its first fields in this chunk, and `MC_IO_DEBUG_UP_37` continues after line 10157. Merge logic must combine adjacent chunks for complete register-family descriptions.
- Several fields control TLB invalidation, VM context enablement, page-table depth/range, protection-fault defaults, PASID mappings, and retry behavior. Mistakes can appear as GPU hangs, incorrect process attribution, missing or spurious VM faults, data corruption, or broken recovery.
- GMCON stutter, save/restore, power-gating FSM, and PLL fields are timing and power sensitive. Misprogramming them can break suspend/resume, BACO, memory self-refresh, clock changes, or register restore after low-power transitions.
- DRAM timing, PHY training, IO drive, CDR, and framing fields are channel/lane specific. Copying D0 values to D1 or mixing DPHY/APHY fields can produce board- or memory-type-specific failures that may only reproduce under load, resume, or high clocks.
- BIST command and data masks can alter memory test behavior or diagnostic interpretation. Running BIST or clearing/masking mismatch fields at the wrong time can hide real memory/EDC issues.
- Many status/debug fields are full-width or packed byte/nibble readouts. Consumers must preserve unsigned 32-bit behavior and avoid assuming every macro is writable just because it has a mask.
- Repeated register patterns are similar across GMC 6/7/8 generations, but not guaranteed identical. Cross-generation table reuse should be checked against the matching `gmc_7_1_*` headers.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation signals are build, static consistency, and hardware-level behavior:

- Compile coverage for CIK/GMC v7, SDMA v2, DCE v8, KFD GFX v7, and CI power-management files that include `gmc_7_1_sh_mask.h`.
- Mechanical comparison against AMD's authoritative GMC 7.1 register database for every mask and shift in lines 5206-10157.
- Static checks that masks are contiguous where fields are numeric, single-bit masks match their shift, full-width fields use shift zero, repeated D0/D1 and VMID[0-15] families are internally consistent, and adjacent chunks complete partial edge registers.
- VM runtime tests covering page-table setup, VM context disable/enable, invalidation request/response, PRT apertures, identity aperture behavior, PASID mapping, and expected VM/protection fault reporting.
- Power-management and resume tests on supported CIK-era hardware covering stutter/self-refresh, BACO, register save/restore, memory clock changes, PLL programming, and power-gating transitions.
- Memory-controller stress tests covering DRAM timing, memory training, IO lane/channel setup, BIST mismatch reporting, and EDC/status diagnostics.
- Performance-counter smoke tests that select representative MC, ATC, VM L2, CHUB ATC, and arbiter events and verify plausible nonzero/monotonic counters under targeted memory/VM workloads.
- Debug dump validation for ATC status, VM faults, TSM/IO debug buses, sequencer status, and BIST readback fields.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002735`. The final per-file document should merge it with the rest of `gmc_7_1_sh_mask.h`, especially neighboring chunks that contain the start of `MC_MCBVM_PERFCOUNTER3_CFG` and the remainder of `MC_IO_DEBUG_UP_37` plus later debug definitions.

### subset-b-002736: lines 10158-14416

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_1_sh_mask.h lines 10158-14416

## Scope And Purpose

This chunk is the tail of the GMC 7.1 register mask header. It contains generated-style C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>_MASK` macro and a matching `<REGISTER>__<FIELD>__SHIFT` macro. There are no functions, structs, globals, or executable branches in this range.

The covered hardware-contract areas are:

- `MC_IO_DEBUG_UP_37` through `MC_IO_DEBUG_UP_159`, packed as four 8-bit `VALUE0`-`VALUE3` lanes per indirect debug register. The range starts mid-register at `MC_IO_DEBUG_UP_37__VALUE2__SHIFT` because earlier lines belong to the prior chunk.
- Per-lane memory PHY debug register layouts for data byte lanes, DBI, EDC, WCK, CK, address, ACMD, CMD, and WCDR blocks on both D0 and D1 channels. These define fields for `MISC`, `CLKSEL`, offset calibration, RX/TX phase, RX VREF calibration, CDR phase size, TX self/boost pull-down/pull-up, RX equalization, RX EQ power-management, and RX dynamic power-management snapshots or controls.
- Memory sequencer control fields for `MC_SEQ_CNTL_3`, GDDR5 power-down exchange (`MC_SEQ_G5PDX_*` plus `_LP` mirrors), serial-register access/status, PHY register broadcast, PMG DVS control/command registers, and DLL standby registers.
- DLB, or data loopback, controls/status fields for PRBS generation/checking, configuration RAM, FIFO reset/strobe behavior, sweep controls, channel/bit write masks, lock/error/sweep-done status, and eight miscellaneous status data registers.
- MC arbiter HARSH read/write control fields for priority enables, high/low transaction groups, bandwidth periods and counters, saturation thresholds, and read/write control options.

The header's purpose is to give AMDGPU/PowerPlay code symbolic bit layouts for GMC 7.1-era memory-controller registers. Consumers combine these masks and shifts with register address macros from `gmc_7_1_d.h` and register access helpers such as `RREG32`, `WREG32`, or `cgs_*_register`.

## Important APIs, Types, And Constants

This chunk exports no callable API. Its interface is the macro namespace:

- `MC_IO_DEBUG_UP_[37-159]__VALUE[0-3]_{MASK,__SHIFT}`: four byte-wide fields in each indirect debug word. Companion addresses include `ixMC_IO_DEBUG_UP_159` at `0x9f` in `gmc_7_1_d.h`. Existing code reads similar entries through `mmMC_SEQ_IO_DEBUG_INDEX` and `mmMC_SEQ_IO_DEBUG_DATA` to inspect MC firmware or ASIC identity state.
- `MC_IO_DEBUG_{DQB*,DBI,EDC,WCK,CK,ADDR*,ACMD,CMD}_MISC_D[0-1]__*`: common per-slice debug controls including output selector fields, enable/status fields, and power/driver-related bitfields for D0 and D1 instances.
- `MC_IO_DEBUG_*_CLKSEL_D[0-1]__*`: clock selection fields for the same PHY slices, generally splitting packed `VALUE0`-style bytes into selector subfields.
- `MC_IO_DEBUG_*_OFSCAL_D[0-1]__*`, `*_RXPHASE_*`, `*_TXPHASE_*`, `*_RX_VREF_CAL_*`, `*_TXSLF_*`, `*_TXBST_PD_*`, `*_TXBST_PU_*`, and `*_RX_EQ_*`: calibration and signal-integrity field layouts for byte-lane, strobe, command, and write-clock receiver/transmitter tuning.
- `MC_IO_DEBUG_WCDR_*_D[0-1]__*`: write-clock data recovery debug/calibration fields matching the broader per-lane families but for WCDR-specific registers. In `gmc_7_1_d.h`, `ixMC_IO_DEBUG_WCDR_MISC_D0` starts at `0x1e0`.
- `MC_SEQ_CNTL_3__*`: sequencer control fields controlling memory-channel sequencing behavior, including low-power and training-related options.
- `MC_SEQ_G5PDX_CTRL{,_LP}__*`, `MC_SEQ_G5PDX_CMD0{,_LP}__DATA`, and `MC_SEQ_G5PDX_CMD1{,_LP}__DATA`: normal and low-power mirror fields for GDDR5 power-down exchange control and command payloads.
- `MC_SEQ_SREG_READ__*` and `MC_SEQ_SREG_STATUS__*`: serial register access request/data/status fields.
- `MC_SEQ_PHYREG_BCAST__*`: broadcast command/address/data masks for writing PHY register values across selected lanes or channels.
- `MC_SEQ_PMG_DVS_CTL{,_LP}__ENABLE/TDVS` and `MC_SEQ_PMG_DVS_CMD{,_LP}__ADR/MOP/BNK_MSB/END/CSB/ADR_MSB*`: dynamic voltage-scaling command encoding and its low-power mirror.
- `MC_SEQ_DLL_STBY{,_LP}__EN`, force/value bits, and timing fields such as `ENTR_DLY`, `STBY_DLY`, `TCKE_*`, and `EXIT_DLY`: DLL standby entry/exit programming for normal and low-power copies.
- `MC_DLB_*__*`: data-loopback and PRBS field layouts. Full-width fields include `MC_DLB_MISCCTRL1__PRBS_ERR_CNT_LIMIT`, `MC_DLB_CONFIG1__DATA`, and `MC_DLB_STATUS_MISC[0-7]__DATA`; narrower fields enable PRBS modes, resets, FIFO pointer shifts, sweep delays, channel masks, lock/error bits, and status selectors.
- `MC_ARB_HARSH_*__*`: read/write arbiter fields. `*_EN_*` macros split TX/BW/fixed/ST priority enable bits; `*_TX_*`, `*_BWPERIOD*`, `*_BWCNT*`, and `*_SAT*` macros pack four 8-bit group values per register; `MC_ARB_HARSH_CTL_{RD,WR}` adds `FORCE_HIGHEST`, round-robin/legacy/bank-age/catch-up mode bits, stall forcing, and performance monitor selection.

## Control Flow And State Behavior

There is no local control flow. The preprocessor exposes constants at compile time, and runtime behavior is entirely in consumers.

For indirect MC IO debug registers, consumers write an `ixMC_IO_DEBUG_*` index to `mmMC_SEQ_IO_DEBUG_INDEX`, then read or write `mmMC_SEQ_IO_DEBUG_DATA`. Examples outside this exact chunk include `smu7_hwmgr.c`, which reads `ixMC_IO_DEBUG_UP_13` to decide memory-latency and FFC behavior, and `gmc_v8_0.c`, which reads `ixMC_IO_DEBUG_UP_159` to select a Polaris12 MC firmware variant. This chunk provides the byte field masks needed to decode the same debug-data words when consumers care about subfields rather than full-word equality.

For direct MC sequencer, DLB, and HARSH registers, state resides in GPU MMIO registers. The `_LP` register variants are low-power shadow/mirror registers. PowerPlay SMU managers for CI, Tonga, and Iceland map normal registers such as `mmMC_SEQ_DLL_STBY`, `mmMC_SEQ_G5PDX_CMD0`, `mmMC_SEQ_G5PDX_CMD1`, `mmMC_SEQ_G5PDX_CTRL`, `mmMC_SEQ_PMG_DVS_CMD`, and `mmMC_SEQ_PMG_DVS_CTL` to their `_LP` counterparts and copy current values into the low-power versions during SMU setup. The mask macros in this chunk describe the bitfields those copies preserve.

DLB and HARSH fields can change hardware behavior if programmed: DLB controls memory PHY loopback/test generation and status collection, while HARSH fields tune memory arbiter priorities and throttling/stall behavior. The header does not serialize access, validate values, cache programmed state, or restore state after reset; those responsibilities belong to the driver paths that issue MMIO writes.

## Dependencies And Integration Points

This chunk is coupled to `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_1_d.h`, which supplies the matching `ix*` and `mm*` register addresses. Relevant addresses in the companion header include `ixMC_IO_DEBUG_UP_159`, `ixMC_IO_DEBUG_DQB0L_MISC_D0`, `ixMC_IO_DEBUG_WCDR_MISC_D0`, `mmMC_SEQ_G5PDX_*`, `mmMC_SEQ_PMG_DVS_*`, `mmMC_SEQ_DLL_STBY*`, `mmMC_DLB_*`, and `mmMC_ARB_HARSH_*`.

Repository integration points visible from includes and cross-references:

- `drivers/gpu/drm/amd/amdgpu/gmc_v7_0.c` includes `gmc_7_1_d.h` and this mask header for Sea Islands/Kaveri-era GMC programming, firmware loading, VM setup, and MC register access.
- `drivers/gpu/drm/amd/amdgpu/sdma_v2_4.c`, `dce_v8_0.c`, `amdgpu_amdkfd_gfx_v7.c`, and `display/dc/resource/dce80/dce80_resource.c` include the same GMC 7.1 register vocabulary when building ASIC-specific blocks.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c` includes this header as part of BACO power-transition command table construction for CI-class hardware.
- `drivers/gpu/drm/amd/pm/powerplay/smumgr/{ci,tonga,iceland}_smumgr.c` use the sequencer register address families from this range to map normal registers to low-power equivalents and to save/copy those registers during SMU initialization.
- Register access is performed through AMDGPU MMIO macros (`RREG32`, `WREG32`) or PowerPlay CGS helpers (`cgs_read_register`, `cgs_write_register`). This header supplies only masks and shifts; users also need the address header and an ASIC where the GMC 7.1 register layout is valid.

## Risks And Edge Cases

- Hardware contract drift is the main risk. These generated constants must match the GMC 7.1 register specification exactly. A bad mask or shift can silently decode the wrong debug byte, write reserved PHY calibration bits, corrupt DLB test setup, or change memory arbitration policy.
- The line range begins in the middle of `MC_IO_DEBUG_UP_37`; merge/reconciliation should combine this with the previous chunk before presenting whole-register coverage.
- Several macro names include repeated words, such as `MC_DLB_SETUPFIFO__SYNC_RST_MASK_MASK`, because the hardware field itself is named `SYNC_RST_MASK`. Consumers must not "simplify" these names by hand.
- Many fields are byte lanes packed at shifts `0x0`, `0x8`, `0x10`, and `0x18`; code should keep arithmetic unsigned and 32-bit. Full-width masks such as `0xffffffff` cannot be shifted or sign-extended through signed temporaries without risking incorrect comparisons or writes.
- `_LP` registers mirror normal sequencer controls but are not interchangeable with normal registers in all runtime states. SMU manager code explicitly maps normal to low-power registers before low-power transitions; direct writes to the wrong copy could leave resume, BACO, or memory power-state behavior inconsistent.
- DLB fields expose destructive or intrusive test controls (`PRBS_*_RST`, `STOP_CLK`, FIFO resets, loopback enable). These should not be changed in ordinary runtime paths unless the driver is deliberately entering a memory PHY test/calibration mode.
- HARSH arbiter controls affect quality of service and stall behavior for read/write traffic groups. Incorrect values can cause performance regressions, starvation, or memory-controller hangs that may only appear under bandwidth pressure.
- The range ends with `#endif /* GMC_7_1_SH_MASK_H */`; any generated edit must preserve the guard close or every includer of the header will fail to compile.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation is integration and hardware-contract oriented:

- Build coverage for AMDGPU, AMDKFD, display DCE 8, and PowerPlay files that include `gmc/gmc_7_1_sh_mask.h`.
- Static macro checks after regeneration or edits: every `*_MASK` should have a matching `*__SHIFT`, contiguous masks should shift down to dense field values, single-bit masks should match their bit index, and full-width fields should have shift zero.
- Register address/mask pairing checks against `gmc_7_1_d.h`, especially for the sequencer/DLB/HARSH address block around `0xd81`-`0xdd7` and indirect IO debug indices around `0x25`-`0x1fc`.
- Runtime smoke tests on GMC 7.1 ASICs covering suspend/resume, BACO/power transitions, and SMU low-power table setup; sequencer `_LP` copies should not introduce memory training, resume, or firmware selection regressions.
- Diagnostic reads of `mmMC_SEQ_IO_DEBUG_INDEX`/`DATA` for known indices can validate that byte extraction with `VALUE0`-`VALUE3` masks produces expected values.
- Memory stress and bandwidth benchmarks are useful after any HARSH-related change, because arbitration mistakes are more likely to show as throughput, latency, or hang symptoms than as compile-time failures.

## Chunk Notes For Merge Lane

This is one chunk of a larger generated GMC 7.1 mask header. Whole-file research should present it as the final register-field section for MC IO debug/PHY tuning, memory sequencer low-power and DVS controls, DLB test/status registers, and HARSH arbiter fields. It should not be described as implementing runtime logic; it is a hardware bitfield vocabulary consumed by separate AMDGPU, display, PowerPlay, and AMDKFD code.
