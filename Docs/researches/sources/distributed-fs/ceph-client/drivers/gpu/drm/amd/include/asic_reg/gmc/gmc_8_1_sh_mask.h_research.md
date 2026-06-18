# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002738`: lines 1-5155, `Docs/researches/chunks/subset-b-002738_research.md`
- `subset-b-002739`: lines 5156-9959, `Docs/researches/chunks/subset-b-002739_research.md`
- `subset-b-002740`: lines 9960-14959, `Docs/researches/chunks/subset-b-002740_research.md`
- `subset-b-002741`: lines 14960-15682, `Docs/researches/chunks/subset-b-002741_research.md`

## Chunk Research

### subset-b-002738: lines 1-5155

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_sh_mask.h lines 1-5155

## Purpose

This chunk is the opening portion of the generated GMC 8.1 register field mask header for the AMDGPU DRM driver. It contains only preprocessor constants: each hardware register field is represented as a `<REGISTER>__<FIELD>_MASK` value and a matching `<REGISTER>__<FIELD>__SHIFT` value. The companion address/header files provide register offsets; this file supplies the bit layout used by register read-modify-write helpers, initialization tables, debug dumps, and ASIC-specific memory-controller programming paths.

The range covers the license/header guard and the first 5,129 lines of field definitions. The definitions are source-of-truth-like hardware contract data for the GMC 8.1 memory controller, not executable logic.

## Major Register Families Covered

- `MC_CONFIG`, `MC_CONFIG_MCD`, `MC_CG_CONFIG`, and `MC_CG_CONFIG_MCD`: select/index memory-controller dies or channels, enable MCD write paths, configure MC read access, and support indexed access modes.
- `MC_ARB_*`: memory-controller arbitration controls. This includes atomic/snoop grouping, aging, return credits, GECC/ECC status and injection fields, bank/rank/row/column mapping, DRAM timing, write timing/watermarks, refresh, power management, replay behavior, latency monitoring, real-time/urgent GRUB arbitration, client grouping, and busy/idle status fields.
- `MC_CITF_*`: client interface controls and credits. These fields map graphics/display/system clients to local or hub arbitration paths, configure read/write credits, return ordering, DAGB behavior, WTM decrementing, per-client throttling, clock gating, and performance-monitor status.
- `MC_RD_*`, `MC_WR_*`, `MC_RD_GRP_*`, and `MC_WR_GRP_*`: per-client read/write knobs and group assignments for CB, DB, TC, HUB, GFX, SYS, OTH, and EXT clients. The repeated field pattern is `ENABLE`, `PRESCALE`, `BLACKOUT_EXEMPT`, `STALL_MODE`, `STALL_OVERRIDE`, `MAX_BURST` or `MAXBURST`, `LAZY_TIMER`, and WTM override bits.
- `MC_HUB_MISC_*`, `MC_HUB_RDREQ_*`, `MC_HUB_WDP_*`, and `MC_HUB_WRRET_*`: hub-side read request, write datapath, write return, status, idle, blackout, deadlock-warning, credit, and client-specific flow-control fields. This chunk includes many repeated client blocks for MCDW/MCDX/MCDY/MCDZ/MCDS/MCDT/MCDU/MCDV plus SIP, SDMA, RLC, HDP, SMU, VCE, UVD, MCIF, VMC, IH, SH, SEM, VP8, ISP, XDMA/XDMAM, ACPG/ACPO, and related clients.
- `MC_RPB_*`: request packet buffer configuration, BIF ordering/credits, read/write switching, write combining, client-ID queue assignment, performance counters, and TCI policy/VMID/credit controls.
- `MC_SHARED_*`: shared channel map/remap fields, virtualization enable/reset/active-function identifiers, and blackout controls.
- `MC_VM_*`: frame-buffer and AGP apertures, system aperture default address fields, display-controller write hit regions, L1 TLB control/debug/status, and virtualization-related VM fields. These fields integrate with GPUVM setup and TLB invalidation/debug flows.
- `MC_XPB_*`: crossbar/peer/P2P bridge fields. The range includes P2P BAR configuration, peer system BARs, XDMA peer BARs, clock gating, interface credits/status, pipe status, sub-block reset/stall controls, sticky bits, misc config, and CLG configuration entries through the start of `MC_XPB_CLG_CFG29`.

## Important APIs, Types, and Functions

This header declares no C functions, structs, enums, or variables. Its API surface is the macro namespace itself:

- `*_MASK` constants isolate a field inside a 32-bit register value.
- `*__SHIFT` constants state how far to shift a caller-supplied value before combining it with the mask, or how far to shift a masked register value after reading it.
- The expected calling pattern in AMDGPU code is a register helper such as `WREG32`, `RREG32`, `WREG32_FIELD`, or local equivalents that combine register offsets from adjacent GMC 8.1 headers with these mask/shift definitions.

Because the definitions are macros, consumers get no type checking. Correctness depends on using the exact register-family macro for the matching ASIC generation and register offset.

## Control Flow

There is no runtime control flow in this file. At compile time, including the header exposes constants under the `GMC_8_1_SH_MASK_H` include guard. Runtime behavior emerges only in downstream code that reads, modifies, and writes hardware registers using these constants.

The logical flow enabled by this chunk is:

1. Select a register address from the GMC 8.1 register offset definitions.
2. Read the current 32-bit register value if only one field is being changed.
3. Clear the relevant `*_MASK` bits.
4. Shift a field value by the matching `*__SHIFT`.
5. Mask and OR the field back into the register value.
6. Write the final value to the hardware register.

Status fields invert that pattern: read the register, mask the field, shift it down, then interpret the resulting integer or bit.

## State and Persistence Behavior

The header itself has no mutable state and persists no data. The constants describe persistent hardware state held in GPU registers while the device is powered and initialized. Many fields control long-lived memory-controller behavior: arbitration weights, credit counts, channel maps, TLB enables, aperture bounds, peer BAR windows, clock gating, and blackout modes. Other fields expose transient hardware state such as busy bits, outstanding request counts, deadlock warnings, buffer fullness, interrupt/status flags, and performance counter values.

Several definitions represent clear or reset semantics in hardware, for example GECC clear bits, TLB invalidation bits, sticky/W1C XPB status, and XPB sub-block resets. Callers must follow the hardware programming sequence; this header does not encode whether a bit is write-one-to-clear, write-one-to-set, self-clearing, or read-only.

## Dependencies and Integration Points

- Depends only on the C preprocessor and include guard discipline.
- Integrates with adjacent generated AMD ASIC register headers under `drivers/gpu/drm/amd/include/asic_reg/gmc/`, especially files that define GMC 8.1 register offsets and default values.
- Used by AMDGPU GMC, VM, hub, memory-controller, power-management, interrupt, and debug/performance paths that program GMC 8.1 hardware.
- Register client names tie this file to other GPU blocks: graphics/color/depth (`CB`, `DB`, `TC`, `SH`), DMA (`SDMA`, `XDMA`), display/media (`DMIF`, `MCIF`, `UVD`, `VCE`, `VP8`, `ISP`), host/system paths (`HDP`, `IH`, `SMU`, `RLC`, `VMC`), and virtualization/peer paths.
- The file is generated-style data. Any hand edit must stay synchronized with AMD hardware documentation and the matching register-offset header; otherwise helper macros can silently program the wrong bits.

## Risks and Edge Cases

- Mask/shift mismatch is high impact: a one-bit error can corrupt memory-controller arbitration, VM apertures, peer BAR routing, or TLB behavior.
- Register family reuse is easy to confuse. Many blocks have near-identical field layouts for read vs write, hub vs CITF, and MCDW through MCDV variants, but not all masks are identical.
- Some masks cover reserved/debug fields. Writing non-reset values to reserved bits can cause undefined hardware behavior.
- Status and control fields are mixed in the same namespace. Callers must know which fields are read-only, write-only, write-one-to-clear, or self-clearing from hardware docs or driver sequencing.
- Address fields such as VM aperture, frame-buffer, AGP, P2P BAR, and peer BAR masks are truncated/encoded hardware values, not raw byte addresses. Incorrect units or shifts can misroute GPU memory traffic.
- The chunk boundary ends mid-family at `MC_XPB_CLG_CFG29`; downstream research chunks must cover the rest of the CLG table and later GMC 8.1 fields before producing a final per-file report.

## Test Signals

- Build coverage: any consumer include or macro spelling break should surface as kernel/driver compile errors.
- Register programming review: changes should be checked against AMD GMC 8.1 register documentation or generated header provenance, especially for repeated MCD, hub, VM, and XPB families.
- Hardware smoke signals: GPU bring-up, display scanout, SDMA transfers, VM fault handling, suspend/resume, and multi-GPU/P2P paths exercise these fields indirectly.
- Debug signals: readback of `MC_HUB_MISC_STATUS`, `MC_HUB_*_STATUS`, `MC_ARB_BUSY_STATUS`, GECC status, RPB performance counters, XPB pipe/interface/sticky status, and VM TLB status can validate that configured masks align with hardware behavior.
- Negative signals: hangs during memory-controller init, VM faults after aperture/TLB programming, deadlock-warning bits, stuck outstanding-request bits, incorrect channel-map behavior, or failed peer/XDMA traffic suggest a field definition or caller usage mismatch.

### subset-b-002739: lines 5156-9959

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

### subset-b-002740: lines 9960-14959

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_sh_mask.h lines 9960-14959

## Scope And Purpose

This chunk is the third line range of the generated-style GMC 8.1 register mask header. It contains preprocessor constants only: each hardware register field is represented as a `<REGISTER>__<FIELD>_MASK` and matching `<REGISTER>__<FIELD>__SHIFT` definition. There are no functions, structs, storage objects, or executable control-flow paths in this range.

The chunk describes bit layouts for memory-controller sequencer, PHY, memory PLL, power-management, training/debug, and indirect IO debug registers used by AMDGPU/PowerPlay code for CI/Tonga/Iceland-era ASICs. It spans about 600 register macro bases in these broad groups:

- low-power memory sequencer command/timing fields, including `MC_SEQ_PMG_CMD_{EMRS,MRS,MRS1,MRS2}_LP`, `MC_SEQ_PMG_TIMING_LP`, `MC_SEQ_PMG_DVS_{CTL,CMD}` and `_LP`, `MC_SEQ_G5PDX_*`, and `MC_SEQ_DLL_STBY`;
- training and diagnostic sequencer fields, including `MC_SEQ_TCG_CNTL`, `MC_SEQ_TSM_*`, `MC_TSM_DEBUG_*`, `MC_SEQ_IO_RWORD*`, `MC_SEQ_IO_RDBI`, `MC_SEQ_IO_REDC`, timers, and DRAM error insertion;
- PHY and clock controls, including `MC_PHY_TIMING_D0`, `MC_PHY_TIMING_D1`, `MC_PHY_TIMING_2`, `MC_SEQ_MPLL_OVERRIDE`, `MCLK_PWRMGT_CNTL`, `DLL_CNTL`, and the `MPLL_*` control/status families;
- PHY lane power-gating and broadcast controls, including `MC_SEQ_PMG_PG_HWCNTL`, `MC_SEQ_PMG_PG_SWCNTL_0`, `MC_SEQ_PMG_PG_SWCNTL_1`, and `MC_SEQ_PHYREG_BCAST`;
- the large indirect `MC_IO_DEBUG_*` namespace, including `MC_SEQ_IO_DEBUG_INDEX/DATA`, `MC_IO_DEBUG_UP_0` through `MC_IO_DEBUG_UP_159`, and per-lane/clock/command debug registers for DQB, DBI, EDC, WCK, CK, ADDR, ACMD, CMD, and WCDR paths.

The header's purpose is to let driver code form and decode 32-bit register values symbolically instead of open-coding bit literals beside MMIO or indirect-register accesses.

## Important APIs, Types, And Constants

There are no C APIs or types exported here. The usable interface is the macro namespace:

- `MC_SEQ_PMG_CMD_*_LP__ADR/MOP/BNK_MSB/END/CSB/ADR_MSB*`: low-power mode register command encodings. The matching `MC_SEQ_PMG_TIMING_LP` fields define self-refresh and CKE timing windows such as `TCKSRE`, `TCKSRX`, `TCKE_PULSE`, `SEQ_IDLE`, and `SEQ_IDLE_SS`.
- `MC_SEQ_IO_RWORD[0-7]`, `MC_SEQ_IO_RDBI`, and `MC_SEQ_IO_REDC`: full-width readback words, DBI mask, and EDC data from memory IO training/debug paths.
- `MC_SEQ_TCG_CNTL`: test command generator control bits for reset, channel enable, start/done, FIFO loading, command opcodes, data counts, burst count, auto-refresh injection, DBI control, frame training, and runtime read-data overrides.
- `MC_SEQ_TSM_CTRL` plus `MC_SEQ_TSM_{GCNT,OCNT,NCNT,BCNT,FLAG,UPDATE,EDC,DBI,WCDR,MISC}`: training state machine controls and comparison/update fields. These macros define start/capture/done/error/step behavior, channel selection, pointer fields, true/false actions, test masks, compare ranges, nibble skip/masks, capture/update tests, and WCDR offsets.
- `MC_SEQ_TIMER_{WR,RD}` and `MC_SEQ_DRAM_ERROR_INSERTION`: full-width timer counters plus TX/RX error-insertion masks for DRAM test paths.
- `MC_PHY_TIMING_D0`, `MC_PHY_TIMING_D1`, and `MC_PHY_TIMING_2`: RX/TX clock delay/extension fields per channel, inversion/force bits, clock-enable controls, write delay, and RX power-on force bits.
- `MC_SEQ_MPLL_OVERRIDE`, `MCLK_PWRMGT_CNTL`, `DLL_CNTL`, `MPLL_SEQ_UCODE_{1,2}`, `MPLL_CNTL_MODE`, `MPLL_FUNC_CNTL*`, `MPLL_AD/DQ_FUNC_CNTL`, `MPLL_TIME`, `MPLL_SS*`, `MPLL_CONTROL`, and `MPLL_*_STATUS`: memory PLL programming, reset, bypass, spread-spectrum, power-on, lock-time, divider, status, and sticky-unlock field layouts.
- `MC_SEQ_PMG_PG_HWCNTL` and `MC_SEQ_PMG_PG_SWCNTL_{0,1}`: memory PHY power-gating controls for hardware-managed gating and per-PMD/PMA software gating of DQ, DBI, EDC, WCLK, and AC TX/RX lanes.
- `MC_SEQ_IO_DEBUG_INDEX/DATA` and `MC_IO_DEBUG_*`: indirect IO debug index/data fields and decoded 4-byte `VALUE0`-`VALUE3` overlays for hundreds of internal debug registers. The named groups cover generic `UP_*` registers and lane/control families such as `DQB[0-3][LH]`, `DBI`, `EDC`, `WCK`, `CK`, `ADDRL`, `ADDRH`, `ACMD`, `CMD`, and `WCDR`.
- `MC_SEQ_CNTL_3`, `MC_SEQ_G5PDX_*`, `MC_SEQ_SREG_*`, `MC_SEQ_PHYREG_BCAST`, and `MC_SEQ_PMG_DVS_*`: late-chunk sequencer controls for pipe delay, repeat-clock gating, CDC programming, CAC/IDSC enable, GDDR5 power-down exit command/timing mirrors, sequencer register read/status, PHY broadcast masks, and dynamic-voltage-scaling command setup.

## Control Flow And State Behavior

This chunk has no local control flow. At compile time, including C files receive symbolic bit masks and shifts. Runtime behavior appears only in consumers that pair these masks with register address macros from `gmc_8_1_d.h`/related address headers.

The relevant runtime state lives in GPU hardware registers:

- Power-management and SMU code reads and writes `MCLK_PWRMGT_CNTL`, `DLL_CNTL`, and `MPLL_*` fields while programming memory clock transitions, DLL reset/power state, and BACO or low-power entry/exit flows.
- SMU manager code mirrors normal registers into low-power versions such as `MC_SEQ_G5PDX_CMD0_LP`, `MC_SEQ_G5PDX_CMD1_LP`, `MC_SEQ_G5PDX_CTRL_LP`, `MC_SEQ_PMG_DVS_CMD_LP`, and `MC_SEQ_PMG_DVS_CTL_LP`.
- Training/debug code can use `MC_SEQ_TCG_CNTL`, `MC_SEQ_TSM_*`, `MC_SEQ_IO_DEBUG_INDEX/DATA`, and `MC_TSM_DEBUG_*` as state-machine controls and indirect readback windows. The header does not provide locking, sequencing, polling, or timeout behavior for those operations.
- Full-width readback and status macros such as `MC_SEQ_IO_RWORD*`, `MC_SEQ_TIMER_RD`, `MC_SEQ_SREG_READ`, `MPLL_*_STATUS`, and `MC_IO_DEBUG_*__VALUE*` describe hardware-observed state. They do not cache or persist anything in system memory.

Persistence is therefore hardware-defined. Values can survive until GPU reset, power-gating, clock reprogramming, or firmware/SMU intervention, depending on the register block. The header itself has no restore path or ownership policy.

## Dependencies And Integration Points

This header is included as part of the AMDGPU GMC 8.1 ASIC register vocabulary. It depends on matching address headers for the `mm*` and `ix*` register offsets; the mask header alone cannot perform an MMIO access.

Important integration points visible from repository cross-references:

- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c`, `tonga_baco.c`, and `polaris_baco.c` use `MPLL_CNTL_MODE__MPLL_SW_DIR_CONTROL_MASK`, `MPLL_CNTL_MODE__MPLL_MCLK_SEL_MASK`, `MPLL_CNTL_MODE__GLOBAL_MPLL_RESET_MASK`, and `MCLK_PWRMGT_CNTL__MRDCK*_PDNB_MASK` in command tables for BACO/low-power transitions.
- `drivers/gpu/drm/amd/pm/powerplay/smumgr/{ci,tonga,iceland}_smumgr.c` uses `MCLK_PWRMGT_CNTL` fields through register-field helper macros while programming DLL speed, MRDCK power/reset state, and memory-clock setup. The same SMU managers translate normal G5PDX/DVS registers to `_LP` register addresses and copy normal values into the low-power mirrors.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.c` writes `mmMC_SEQ_IO_DEBUG_INDEX` and reads/writes `MCLK_PWRMGT_CNTL` as part of SMU7 hardware-manager setup and clock-register snapshots.
- `drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.c` also touches `MC_SEQ_IO_DEBUG_INDEX` and snapshots `MCLK_PWRMGT_CNTL` into SMC state-table structures, showing that these generated masks support both legacy DPM and PowerPlay paths.
- The indirect `MC_IO_DEBUG_*` and `MC_TSM_DEBUG_*` families are paired with `MC_SEQ_IO_DEBUG_INDEX/DATA` and `MC_SEQ_TSM_DEBUG_INDEX/DATA`; consumers must select an index/register address before reading or writing the data aperture.

## Risks And Edge Cases

- Hardware contract drift is the main risk. These constants must match the exact GMC 8.1 register specification. A wrong mask or shift can write reserved bits, miss a power gate, choose the wrong PLL divider, corrupt memory-clock transitions, or misdecode training/debug state.
- This chunk begins in the middle of `MC_SEQ_WR_CTL_2_LP`; line 9960 starts with a `__SHIFT` definition whose matching earlier mask is in the previous chunk. The merge lane should join adjacent chunks before making whole-register claims.
- Some fields intentionally use names such as `*_MASK_MASK`, for example `MC_SEQ_TCG_CNTL__VPTR_MASK_MASK`, `MC_SEQ_TSM_FLAG__NBBL_MASK_MASK`, and `MC_SEQ_PHYREG_BCAST__DQ_MASK_MASK`. These are generated field names where the hardware field itself is called `MASK`; cleanup scripts must not collapse the double `MASK`.
- Many registers expose full-width `0xffffffff` fields and high-bit masks such as `0x80000000`. Consumers should keep values unsigned/32-bit and avoid signed shifts or host-width assumptions.
- Indirect debug windows are order-sensitive. Interleaving writes to `MC_SEQ_IO_DEBUG_INDEX` or `MC_SEQ_TSM_DEBUG_INDEX` with unrelated data-window reads/writes can observe or update the wrong internal register unless the caller serializes access.
- The `MC_IO_DEBUG_*` region is highly repetitive: most entries decode four packed 8-bit values at shifts `0`, `8`, `16`, and `24`. Mechanical regeneration errors are easy to miss because names differ only by lane, channel suffix (`D0`/`D1`), or function (`CLKSEL`, `MISC`, `RXPHASE`, `TXPHASE`, `TXSLF`, `TXBST_*`, `RX_EQ`, `RX_VREF_CAL`, `RX_EQ_PM`, `RX_DYN_PM`, `CDR_PHSIZE`).
- Low-power mirror registers must stay layout-compatible with their normal counterparts. The `_LP` variants for G5PDX and DVS command/control use the same field shapes as the non-LP versions; a mismatch would break SMU code that copies normal register values into low-power mirrors.
- Several fields control destructive or timing-sensitive hardware behavior, including PLL resets, DLL resets, power gating, DRAM error insertion, TCG start/reset, and TSM start/step/capture. Incorrect writes can cause memory training failures, display hangs, or GPU resets.

## Test And Validation Signals

There are no direct unit tests for this macro chunk. Useful validation signals are integration-level:

- Compile coverage of AMDGPU PowerPlay, legacy DPM, and SMU manager files that include `gmc_8_1_sh_mask.h` and use the affected macro names.
- Static mask/shift validation: single-bit masks should shift to their bit index; packed 8-bit `VALUE0`-`VALUE3` fields should use `0xff`, `0xff00`, `0xff0000`, and `0xff000000`; full-width fields should have shift zero.
- Register table or helper validation for BACO and SMU memory-clock setup: read-modify-write helpers should preserve unrelated bits when applying `MPLL_CNTL_MODE`, `MCLK_PWRMGT_CNTL`, and `DLL_CNTL` fields.
- Runtime power-management smoke tests on supported CI/Tonga/Iceland/SMU7 hardware: memory-clock changes, BACO entry/exit, suspend/resume, and low-power state transitions should complete without hangs or PLL/DLL lock failures.
- Debugfs/register-dump checks can compare `MC_SEQ_G5PDX_*` and `MC_SEQ_PMG_DVS_*` normal-vs-`_LP` values after the SMU mirror-copy path runs.
- Hardware memory stress or error-injection validation can exercise `MC_SEQ_TCG_CNTL`, `MC_SEQ_TSM_*`, and `MC_SEQ_DRAM_ERROR_INSERTION` paths where they are exposed by diagnostic tooling.

## Chunk Notes For Merge Lane

This is a partial chunk of a much larger generated register mask header. Whole-file research should merge it with chunks 1, 2, and 4 for `gmc_8_1_sh_mask.h` before summarizing register coverage. This chunk is the dense middle/tail section for GMC memory sequencer training, memory PLL/power control, PHY timing, IO debug, low-power mirror, DVS, and PHY broadcast bitfield definitions.

### subset-b-002741: lines 14960-15682

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_sh_mask.h lines 14960-15682

## Scope And Purpose

This chunk is the final portion of the `gmc_8_1_sh_mask.h` generated-style ASIC register mask header. It contains preprocessor constants only: each hardware register field is exposed as a `<REGISTER>__<FIELD>_MASK` and matching `<REGISTER>__<FIELD>__SHIFT` definition. There are no functions, structs, enums, storage objects, or executable branches in this line range.

The span covers three related register-contract areas for GMC 8.1-era AMD GPUs:

- Memory-controller sequencer and data-loopback controls: `MC_SEQ_DLL_STBY`, `MC_SEQ_DLL_STBY_LP`, and the `MC_DLB_*` register family.
- Memory-controller arbitration policy fields: `MC_ARB_HARSH_*` and `MC_ARB_GRUB_PRIORITY*` read/write priority registers.
- MCIF writeback buffer-manager fields: `MCIF_WB_BUFMGR_*`, `MCIF_WB_BUF_*`, `MCIF_WB_ARBITRATION_CONTROL`, `MCIF_WB_URGENCY_WATERMARK`, test/debug, VCE control, and VMID control registers.

The purpose is to give AMDGPU and display/power-management code symbolic bit layouts for register programming. The companion address header, `gmc_8_1_d.h`, defines the `mm*` register offsets; this mask header defines how to pack or decode values at those offsets.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The public interface is the macro namespace.

`MC_SEQ_DLL_STBY` and `MC_SEQ_DLL_STBY_LP` define bitfields for DLL standby behavior. The normal and low-power variants share fields for enable, forced/explicit VCTRL ADC and master-standby values, entry/standby delays, CKE pulse/extension timing, and exit delay. Power-management code maps `mmMC_SEQ_DLL_STBY` to `mmMC_SEQ_DLL_STBY_LP` and copies normal register values into the LP register when building memory-clock tables.

`MC_DLB_*` defines the data-loopback/test block:

- `MC_DLB_MISCCTRL0`, `MISCCTRL1`, and `MISCCTRL2` select user-defined data, PRBS run length, PRBS error limits, PRBS modes, stop behavior, clock stop, sweep delay, gray-code mode, PHY/AC checker selection, and status selection.
- `MC_DLB_CONFIG0` and `CONFIG1` hold per-channel configuration enable bits, auto enable, mask/pointer selection, and full-width configuration data.
- `MC_DLB_SETUP`, `SETUPSWEEP`, `SETUPFIFO`, and `WRITE_MASK` control DLB enablement, FIFO/status/config/PRBS enablement, PRBS resets, QDR mode, checked data-bit selection, memory-bit selection, RX/TX low-power enablement, DLL sweep setup, FIFO reset/sync/strobe settings, and bit/channel write masks.
- `MC_DLB_STATUS` and `MC_DLB_STATUS_MISC0` through `MISC7` expose sticky errors, lock state, sweep completion, and full-width status data words.

`MC_ARB_HARSH_*` defines memory-arbiter "harsh" policy fields for read and write traffic. The register families are structured in parallel for RD and WR:

- `MC_ARB_HARSH_EN_{RD,WR}` has 8-bit enable groups for transaction-priority, bandwidth-priority, fixed-priority, and stall-priority handling.
- `MC_ARB_HARSH_TX_HI*` and `TX_LO*` define high and low transaction thresholds for groups 0-7.
- `MC_ARB_HARSH_BWPERIOD*`, `BWCNT*`, and `SAT*` define packed 8-bit group values for bandwidth accounting periods, bandwidth counters, and saturation thresholds.
- `MC_ARB_HARSH_CTL_{RD,WR}` provides global policy controls: `FORCE_HIGHEST`, round-robin harsh mode, bank-age-only mode, legacy harsh mode, bandwidth-counter catch-up, stall mode, force-stall bitfield, and performance-monitor selection.

`MC_ARB_GRUB_PRIORITY1_*` and `MC_ARB_GRUB_PRIORITY2_*` define packed 2-bit client priority fields for read and write arbitration. The read registers cover clients such as `CB0`, `CBCMASK0`, `CBFMASK0`, `DB0`, `DBHTILE0`, `DBSTEN0`, `TC0`, `ACPG`, `ACPO`, `DMIF`, `MCIF`, `RLC`, `SDMA1`, `SMU`, `VCE0`, `VCE1`, `XDMAM`, `SDMA0`, `HDP`, `UMC`, `UVD`, `SEM`, `SAMMSP`, `VP8`, `ISP`, and reserved slots. The write-side registers are similar but include write-specific clients and ordering such as `CBIMMED0`, `SH`, `XDMA`, `XDP`, `IH`, and `VIN0`.

`MCIF_WB_*` defines the writeback path into memory:

- `MCIF_WB_BUFMGR_SW_CONTROL` controls buffer-manager enablement, dual-size requests, software interrupt enable/ack/slice interrupt enable, software lock bits, and producer VMID.
- `MCIF_WB_BUFMGR_STATUS` reports VCE/software interrupt status, current/next buffer, dual-size status, buffer tag, and current left-line position. `MCIF_WB_BUFMGR_CUR_LINE_R` reports the right-line position.
- `MCIF_WB_BUF_PITCH` packs luma and chroma pitches.
- `MCIF_WB_BUF_[1-4]_STATUS` and `STATUS2` repeat the same field layout for four buffers: active, software-locked, VCE-locked, overflow, disable, mode, buffer tag, next buffer, field, current line left/right, long-line error, short-line error, frame-length error, new-content flag, and color-depth flag.
- `MCIF_WB_ARBITRATION_CONTROL` selects client arbitration slice and time-per-pixel scheduling.
- `MCIF_WB_URGENCY_WATERMARK` packs two client urgency watermarks.
- `MCIF_WB_TEST_DEBUG_INDEX` and `MCIF_WB_TEST_DEBUG_DATA` expose an indexed test/debug path with write enable and full-width debug data.
- `MCIF_WB_BUF_[1-4]_ADDR_{Y,C}` and matching `_OFFSET` registers define luma/chroma base addresses and 18-bit offsets for the four writeback buffers.
- `MCIF_WB_BUFMGR_VCE_CONTROL` controls VCE lock-ignore, VCE interrupts/acks/slice interrupts, VCE lock bits, and slice size.
- `MCIF_WB_HVVMID_CONTROL` defines default VMID and allowed-VMID mask fields. The macro name `MCIF_WB_HVVMID_CONTROL__MCIF_WB_ALLOWED_VMID_MASK_MASK` is mechanically generated and includes the duplicated `MASK` token in the field name; consumers must use the exact generated spelling.

## Control Flow And State Behavior

This header chunk has no local runtime control flow. Its effects are compile-time substitution of constants into consumers that read, modify, or write MMIO registers.

Runtime state lives in GPU hardware registers:

- The DLL standby fields configure memory sequencer timing and low-power behavior. Power-management code for Island/Tonga/CI-era paths uses the address pair `mmMC_SEQ_DLL_STBY` and `mmMC_SEQ_DLL_STBY_LP` when constructing low-power memory register tables, so values can be mirrored from normal to low-power register banks.
- The `MC_DLB_*` registers configure and observe memory data-loopback or PRBS diagnostics. Enable, reset, checker selection, run length, and stop-on-error fields drive hardware test state; status and misc status fields expose sticky errors, lock status, sweep completion, and diagnostic data.
- The arbiter registers configure memory-controller scheduling policy. The "harsh" fields set group thresholds and enable different priority algorithms; the GRUB priority fields assign packed client priorities for read and write traffic. These values affect arbitration behavior inside hardware rather than storing software-owned state.
- The MCIF writeback registers describe buffer manager configuration and observable buffer state. Active/locked/error/new-content bits are hardware status signals; address, offset, pitch, urgency, arbitration, interrupt, lock, and VMID fields are programmed configuration state.

Persistence is therefore hardware-dependent. Values survive until reset, power-gating, mode changes, firmware/driver reinitialization, or explicit register writes. The header does not cache values, serialize access, restore state, or enforce read-modify-write discipline.

## Dependencies And Integration Points

This file is part of the AMDGPU ASIC register vocabulary under `drivers/gpu/drm/amd/include/asic_reg/gmc/`. It depends on conventional inclusion by driver code that also includes register-address headers:

- `gmc_8_1_d.h` defines the matching offsets: `mmMC_SEQ_DLL_STBY` at `0xd8e`, `mmMC_SEQ_DLL_STBY_LP` at `0xd8f`, `mmMC_DLB_*` at `0xd90` through `0xda1`, `mmMC_ARB_HARSH_*` at `0xdc0` through `0xdd7`, `mmMC_ARB_GRUB_PRIORITY*` at `0xdd8` through `0xddb`, and `mmMCIF_WB_*` starting at `0x5e78`.
- `gmc_8_1_d.h` also defines instance-specific aliases for MCIF writeback, such as `mmMCIF_WB0_*`, `mmMCIF_WB1_*`, and `mmMCIF_WB2_*`, with the same field layout described by this mask chunk.
- Power-management SMU manager code for related GCN 1.2 ASICs maps `mmMC_SEQ_DLL_STBY` to `mmMC_SEQ_DLL_STBY_LP` and writes the LP register from the normal register value when preparing memory tables.
- Display writeback code in newer DC/DCN paths uses analogous `MCIF_WB_*` register lists and masks for MCIF writeback programming. This GMC 8.1 chunk supplies the pre-DCN/GCN-era field layout for the same conceptual block.
- The mask names are intended to be used with AMDGPU register helpers such as raw MMIO reads/writes or table-driven register programming, usually in the form `(value << FIELD__SHIFT) & FIELD_MASK` or `(reg & FIELD_MASK) >> FIELD__SHIFT`.

The header is not useful by itself: every meaningful use needs a register address, an MMIO accessor, and an ASIC path that actually exposes the corresponding register block.

## Risks And Edge Cases

- The constants are a hardware ABI. A wrong mask or shift can write reserved bits, leave a target field unchanged, select an unintended arbiter policy, corrupt writeback buffer addressing, or misdecode status/errors.
- Many fields are packed 8-bit or 2-bit repeated groups. Off-by-one shifts in group registers are especially risky because they silently configure the wrong client/group while preserving a plausible-looking value.
- Several fields use full-width `0xffffffff` masks. Call sites should keep values in unsigned 32-bit types and avoid signed promotion surprises when composing or printing register values.
- MCIF writeback address fields are full 32-bit lows plus 18-bit offsets in this chunk. Consumers must combine these with the correct address granularity and any high-address registers supplied elsewhere for the target ASIC; using the wrong generation's layout can point writeback at the wrong memory.
- Buffer-manager lock and interrupt-ack fields are stateful hardware controls. Read-modify-write operations must preserve unrelated bits, and interrupt ack fields should be written according to the hardware's write-one/write-zero semantics rather than treated as ordinary sticky software state.
- `MC_DLB_*` PRBS, FIFO reset, DLL sweep, and stop-clock fields are diagnostic/control-path registers. Accidentally touching them during normal memory operation could disrupt memory-controller behavior or hide memory-training failures.
- Arbiter policy registers can affect display, DMA, video, shader, and host clients at once. A regression may appear as performance jitter, underruns, GPU hangs, or starvation rather than an immediate register-access failure.
- The generated name `MCIF_WB_HVVMID_CONTROL__MCIF_WB_ALLOWED_VMID_MASK_MASK` looks like a typo but is the macro exported by this header. Renaming it for style would break consumers that expect the generated symbol.
- This chunk ends with `#endif /* GMC_8_1_SH_MASK_H */`. Any regeneration or merge must preserve the guard close or every includer of the header will fail to compile.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation is mostly compile-time and hardware/integration-oriented:

- Build coverage for AMDGPU configurations that include `gmc_8_1_sh_mask.h`, especially power-management paths that reference `MC_SEQ_DLL_STBY`/`MC_SEQ_DLL_STBY_LP` and display or writeback paths that reference `MCIF_WB_*`.
- Static mask/shift consistency checks: single-bit masks should match their shift, contiguous multi-bit masks should shift down to dense fields, full-width fields should have shift zero, and repeated groups should occupy non-overlapping ranges.
- Register-table smoke tests on supported GMC 8.1 hardware: low-power memory table construction should mirror `MC_SEQ_DLL_STBY` into `MC_SEQ_DLL_STBY_LP` without clobbering adjacent LP registers.
- MCIF writeback validation: enable writeback, program buffer addresses/pitches/VMID/watermarks, then check buffer status, new-content, current-line, overflow, long-line, short-line, and frame-length status fields during capture.
- Arbitration validation: compare register dumps before and after any performance or QoS tuning path and confirm only intended `MC_ARB_HARSH_*` and `MC_ARB_GRUB_PRIORITY*` fields changed.
- Diagnostic-only validation for DLB fields: PRBS loopback/sweep tests should report lock and sweep-done status, preserve status-misc readability, and respect stop-on-error/error-limit controls.
- Cross-generation diffing against adjacent `gmc_8_2_sh_mask.h` can catch accidental edits in shared MCIF writeback layouts while still allowing real ASIC-generation differences.

## Chunk Notes For Merge Lane

This is a terminal chunk of a larger generated GMC 8.1 register mask header. Whole-file research should treat it as the mask/shift definition section for memory-controller standby/test/arbitration and MCIF writeback buffer-manager registers, not as standalone logic. The paired address definitions in `gmc_8_1_d.h` and the AMDGPU MMIO helpers are required to explain runtime behavior.
