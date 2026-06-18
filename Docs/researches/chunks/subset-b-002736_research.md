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
