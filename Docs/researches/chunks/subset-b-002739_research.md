# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_sh_mask.h lines 5156-9959

## Scope And Purpose

This chunk is a large middle slice of the generated-style AMD GMC 8.1 register shift/mask header. It contains only C preprocessor definitions. Each exported symbol names a hardware register bitfield as `<REGISTER>__<FIELD>_MASK` plus the matching `<REGISTER>__<FIELD>__SHIFT`. There are no functions, structs, enums, storage objects, or executable paths in this line range.

The purpose of the chunk is to provide the software-visible bit layout for major memory-controller, address-translation, virtual-memory, power-management, memory-training, BIST, and IO PHY registers used by VI/SMU7-era AMDGPU code. Consumers pair these masks with register-address macros from `gmc_8_1_d.h` and register accessors such as `RREG32`, `WREG32`, and `cgs_read_register`/`cgs_write_register`.

The range starts in the tail of the `MC_XPB_CLG_CFG29` field set and ends in the first two fields of `MC_SEQ_WR_CTL_2_LP`. The continuation after line 9959 belongs to the same low-power write-control register and should be merged with adjacent chunk research for whole-file analysis.

## Important APIs, Types, And Constants

This chunk exports macro constants rather than callable APIs. Important register families in the slice are:

- `MC_XPB_*` and `MC_XBAR_*`: crossbar and PCIe/XPB client routing fields. These include client group configuration entries `MC_XPB_CLG_CFG29` through `MC_XPB_CLG_CFG36`, XPB read comparison fields, XBAR address decode toggles, remote request enables, read/write request and return credits, channel remap fields, arbitration priority/burst controls, FIFO monitor controls/results, and spare registers.
- `*_PERFCOUNTER*` for `MC_CITF`, `MC_HUB`, `MC_RPB`, `MC_MCBVM`, `MC_MCDVM`, `MC_VM_L2`, `MC_ARB`, `ATC`, and `CHUB_ATC`: low/high counter fields, compare values, per-counter event selectors, modes, enable bits, clear bits, and result-control fields (`PERF_COUNTER_SELECT`, start/stop triggers, clear-all, enable-any, stop-on-saturate).
- `ATC_*`: Address Translation Cache controls and diagnostics. The range covers ATC VM aperture controls, L1/L2 controls and status/debug/cache data fields, ATS control/status/debug/fault fields, per-VMID PASID mappings for VMID 0-15, and mapping-update status bits.
- `GMCON_*`: graphics memory-controller power/control support. Fields cover low-power target registers, clock/power-gating FSM configuration/read/write/data paths, register-engine execution and RAM index/data registers, STCTRL save/restore ranges and exclusions, performance-monitor controls/results, mask/debug/misc registers, and PGFSM control status.
- `VM_*` and `MC_VM_*`: VM context, L2, PRT, invalidation, MARC, NB, and per-VF framebuffer aperture definitions. `VM_CONTEXT0_CNTL` and `VM_CONTEXT1_CNTL` define enable, page-table depth/block size, and fault behavior; context address/fault registers expose full-width address/client/status fields; `VM_L2_CNTL*` defines cache/TLB behavior, fragment size, outstanding requests, and protection-fault handling; `VM_INVALIDATE_REQUEST/RESPONSE` define per-VMID invalidation handshake bits; `MC_VM_*` adds NB, MARC, TLS L1 aperture/protection, and SR-IOV VF framebuffer size/offset fields.
- `MC_PMG_*`, `MC_SEQ_*`, and `MC_IO_*`: memory power-management and sequencer/PHY configuration fields. The chunk includes PMG auto command/config and MRS/EMRS command layouts, many sequencer timing/control/status/training fields, byte/bit remap fields, TX/RX framing fields, WCDR control, read/write control for D0/D1, and low-power timing/control variants.
- `MC_BIST_*` and `MC_TRAIN_*`: built-in self-test and memory-training controls, address ranges, compare controls, mismatch reporting, data masks/patterns/readback words, EDC status, PRBS error registers, and EDC CDR training controls.
- `MC_IMP_*` and `MC_IO_*`: impedance calibration, DQ status, pad controls, APHY/DPHY strobe strength controls, CDR controls, RX controls, and TX controls for D0/D1 and APHY/DPHY lanes.

Representative field layouts show the expected generated pattern: full-register data/status fields use `0xffffffff` with shift `0`, packed 8-bit credit/counter selector lanes use masks such as `0xff`, `0xff00`, `0xff0000`, and `0xff000000`, and control/status bits use single-bit masks at their hardware bit positions.

## Control Flow And State Behavior

There is no local control flow in this header. Runtime behavior occurs only in consumers that include it:

- AMDGPU GMC 8 initialization includes `gmc/gmc_8_1_d.h` and this mask header in `amdgpu/gmc_v8_0.c`. Golden-register programming tables combine `mm*` register addresses with masks from this header and pass them to `amdgpu_device_program_register_sequence`.
- SMU7 power-management code copies and augments memory-controller register tables. For example, `iceland_smumgr.c` maps normal memory sequencer registers to low-power forms such as `mmMC_SEQ_RAS_TIMING_LP`, `mmMC_SEQ_CAS_TIMING_LP`, `mmMC_SEQ_RD_CTL_D0_LP`, `mmMC_SEQ_WR_CTL_D0_LP`, `mmMC_SEQ_PMG_CMD_MRS_LP`, `mmMC_SEQ_PMG_TIMING_LP`, and `mmMC_SEQ_WR_CTL_2_LP`; it also writes LP registers from their active-register counterparts during MC table initialization. The masks in this chunk define the bit layout of those programmed values even where that code copies whole registers.
- VM and ATC state is hardware state. Driver code writes context controls, page-table bounds, L2 controls, invalidate requests, PASID mappings, and aperture registers, then observes status/fault/invalidate-response bits through the fields defined here.
- Performance-counter state is also in hardware. Config registers select events and modes, result-control registers start/stop/clear counters, and low/high result registers expose counts and compare values.
- BIST, training, GMCON, and IO PHY fields represent state machines and calibration/programming state inside the memory controller. Some fields are commands (`RUN`, `RESET`, `READ`, `WRITE`, `POWER_DOWN`, `POWER_UP`), some are latched status (`DONE`, busy/full/empty flags, fault status, update status), and some are persistent configuration until reset or power-management reprogramming.

The header does not cache state, serialize access, validate values, or define reset ordering. All persistence and side effects are owned by the GPU registers and by the higher-level AMDGPU/SMU code that sequences MMIO accesses.

## Dependencies And Integration Points

This chunk depends on the surrounding generated register-address and mask ecosystem:

- It is paired with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_d.h`, where the `mm*` register offsets are defined.
- It is included directly by GMC 8 code such as `amdgpu/gmc_v8_0.c`, VI common code, display/compressor code, SDMA/KFD code, and SMU7/powerplay modules for Tonga/Fiji/Iceland/Polaris-era ASICs.
- Register access goes through AMDGPU MMIO helpers (`RREG32`, `WREG32`, indirect access helpers, or `cgs_*` accessors) and table-driven helpers such as `amdgpu_device_program_register_sequence`.
- Power-management integration is visible in SMU manager code. It consumes the LP memory-controller registers in this chunk when building SMC memory tables from VBIOS/ATOM timing data, setting valid flags, and uploading tables for memory clock state changes.
- VM integration ties to GPUVM/KFD fault handling and PASID/VMID setup. `VM_CONTEXT*`, `VM_L2*`, `ATC_VMID*_PASID_MAPPING`, `ATC_ATS_*`, and invalidate request/response fields are the low-level hardware contract for page-table walking, translation caching, ATS, and per-process address spaces.
- Diagnostics and validation integrate through perf counters, debug/status registers, BIST, training, and FIFO monitor fields. These are useful to debug memory-controller hangs, translation faults, memory-training failures, and performance anomalies.

## Risks And Edge Cases

- Hardware contract drift is the dominant risk. A wrong mask or shift can program the wrong bit, fail to clear a status bit, enable an unintended fault policy, corrupt a VM aperture, or select the wrong perf event.
- Many names are duplicated across ASIC generations with similar but not guaranteed identical layouts. Consumers must include the matching `gmc_8_1_*` headers for the active ASIC rather than reusing masks from GMC 6/7/8 variants interchangeably.
- The chunk contains high-impact VM and ATC controls. Incorrect `VM_CONTEXT*`, `VM_L2*`, invalidation, or PASID field handling can cause page faults, stale translations, process isolation issues, GPU hangs, or incorrect fault attribution.
- Some fields are write-one command/status controls or command bits for internal FSMs (`GMCON_PGFSM_CONFIG`, `MC_BIST_CNTL`, `MC_SEQ_SUP_CNTL`, invalidate requests). Generic read-modify-write code must know whether a bit is level, pulse, clear-on-write, or read-only; the mask header alone does not encode that semantic.
- Full-width fields such as data ports, counter lows, address lows/highs, and spare registers need unsigned 32-bit treatment. Signed arithmetic or host-width assumptions can mis-handle masks like `0xffffffff`.
- Low-power memory-controller registers are initialized by copying active-register values. If mask definitions for LP variants diverge from the active variant or the hardware generation changes, whole-register copies can silently preserve incompatible reserved bits.
- The assigned line range ends mid-register at `MC_SEQ_WR_CTL_2_LP__DQS_DLY_H_D0`. Any generated documentation or regeneration must not treat the partial register as complete for whole-file conclusions.

## Test And Validation Signals

There are no direct unit tests for these macros. Useful validation signals are integration-level:

- Build coverage of AMDGPU modules that include `gmc_8_1_sh_mask.h`, especially `amdgpu/gmc_v8_0.c`, VI initialization, KFD GFX8 integration, DCE compressor code, SDMA v3, and SMU7 powerplay/legacy DPM files.
- Static consistency checks on generated masks: single-bit masks should match their shift index, contiguous multi-bit masks should shift down to dense low-bit fields, and full-width fields should use shift zero.
- Golden-register programming smoke tests on supported VI/Polaris hardware should complete without invalid MMIO access warnings and should preserve only the intended masked bits.
- GPUVM/KFD runtime tests should validate VMID/PASID setup, page-table base/end/start programming, VM invalidation response bits, protection-fault reporting, and ATS fault/status paths.
- Memory clock and power-management transitions should exercise the LP MC register table path, including copies to `MC_SEQ_*_LP` registers and SMC memory table uploads, without memory-training regressions or display/GPU hangs.
- Perf-counter/debug validation can program event selectors and result controls, then confirm monotonically changing low/high counters and expected start/stop/clear behavior.
- BIST/training diagnostics, when available on target hardware, should confirm `MC_BIST_*`, `MC_TRAIN_*`, `MC_SEQ_TRAIN_*`, and IO PHY status fields decode as expected during memory test and calibration flows.

## Chunk Notes For Merge Lane

This is one chunk of a generated GMC 8.1 mask header, not a standalone component. Whole-file research should describe it as the middle register-field vocabulary covering XPB/XBAR, perf counters, ATC/VM, GMCON, MC PMG/sequencer, IO PHY, BIST, and training definitions. The next chunk should be checked for the continuation of `MC_SEQ_WR_CTL_2_LP` and following low-power PMG command/timing fields.
