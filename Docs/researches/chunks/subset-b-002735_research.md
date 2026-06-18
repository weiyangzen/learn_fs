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
