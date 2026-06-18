# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 45148-47858

## Purpose

This chunk is generated AMD GC 10.3.0 register bitfield metadata. It contains no executable C; it publishes C preprocessor `__SHIFT` and `_MASK` constants for composing and decoding 32-bit graphics-core MMIO and indirect-register values. The matching register offsets and indirect indices are provided by the sibling GC 10.3.0 offset header.

The selected range covers four related hardware metadata areas:

- GC CAC accumulator readback and override fields for graphics, shader, memory, cache, SDMA, geometry, and MMU-facing blocks.
- CAC power-state pattern tables and fixed-pattern counters used around release, stall, and power-break transitions.
- SE CAC control and override fields, plus SPM global/per-SE sample-delay fields.
- RTAVFS indexed fields for closed-loop adaptive voltage/frequency sensing, CPO ripple counters, voltage-code selection, temperature ring oscillator controls, and AVFS FSM timing counters.

Although this tree is rooted under `sources/distributed-fs/ceph-client`, the file is AMDGPU hardware-description data, not Ceph or filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation sites, callbacks, locks, or direct hardware accesses in this chunk. The API surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- Consumers pair these constants with `mm*` register-offset macros or `ix*` indirect-index macros from `gc_10_3_0_offset.h`, then use AMDGPU MMIO and indirect-register helpers.

Major macro groups in this chunk:

- `GC_CAC_ACC_*` accumulator registers. Most blocks expose a single full-width `ACCUMULATOR_31_0` field, for example `GC_CAC_ACC_CB*`, `DB*`, `CP*`, `GDS*`, `PA*`, `SPI*`, `TCP*`, `TD*`, `RMI*`, `EA*`, `UTCL2_*`, `GE*`, `GL2C*`, `SDMA*`, `GL1C*`, `SQC*`, and `RLC0`. Shader-centric `SQ*_LOWER` and `SP*_LOWER` registers expose the lower 32 bits, while `SQ*_UPPER` and `SP*_UPPER` expose `ACCUMULATOR_39_32` plus reserved/unused upper bits. These fields are readback windows for CAC activity accumulation.
- `GC_CAC_OVRD_*` override registers. Each block has `OVRRD_SELECT` and `OVRRD_VALUE` fields. Field widths vary by hardware block: small one-bit or few-bit overrides for blocks such as `RLC`, wider packed override selectors/values for blocks such as `CB`, `DB`, `TCP`, `TD`, `GE`, `SDMA`, and a high-half `GC_CAC_OVRD_GE_HI`. These are configuration/forcing controls, not counters.
- CAC power-transition LUTs. `RELEASE_TO_STALL_LUT_*`, `STALL_TO_RELEASE_LUT_*`, `STALL_TO_PWRBRK_LUT_*`, `PWRBRK_STALL_TO_RELEASE_LUT_*`, and `PWRBRK_RELEASE_TO_STALL_LUT_*` pack several `FIRST_PATTERN_*` entries into one register. Release-to-stall and power-break release-to-stall use compact 3-bit entries at 4-bit spacing; stall-to-release uses 5-bit entries at 8-bit spacing; stall-to-power-break uses 3-bit entries at 8-bit spacing.
- `FIXED_PATTERN_PERF_COUNTER_1` through `FIXED_PATTERN_PERF_COUNTER_10` define a 17-bit `PERF_COUNTER` field used to observe fixed CAC pattern counters.
- `HW_LUT_UPDATE_STATUS` exposes per-table `DONE`, `ERROR`, and `ERROR_STEP` fields for five hardware LUT update tables. It is a status register for table update completion and fault diagnosis.
- `addressBlock: secacind` contains `SE_CAC_ID`, `SE_CAC_CNTL`, `SE_CAC_OVR_SEL`, and `SE_CAC_OVR_VAL`. `SE_CAC_ID` separates CAC block and signal IDs, `SE_CAC_CNTL` exposes `CAC_FORCE_DISABLE` and a 16-bit threshold field, and the override selection/value registers are full-width data windows.
- `addressBlock: spmglbind` contains global SPM sample-delay fields. Every `GLB_*_SAMPLEDELAY` register in this block has the same layout: a 6-bit `SAMPLEDELAY` field at bits 0-5 and reserved bits 6-31. Covered blocks include CPG, CPC, CPF, GDS, GCR, PH, GE, GUS, CHA/CHC/CHCG, ATCL2, VML2, SDMA0-3, GL2A0-3, GL2C0-15, EA0-15, and GE2SE0-3.
- `addressBlock: spmind` contains per-shader-engine/per-shader-array sample-delay fields. The same 6-bit `SAMPLEDELAY` plus reserved-bit pattern appears for `SE_SPI`, `SE_SQG`, `SE_CBR`, `SE_DBR`, `SE_PA`, SA0 and SA1 blocks, GL1 blocks, CB/DB/SC/RMI, and WGP-local TA/TD/TCP blocks for WGP00 through WGP04.
- `addressBlock: grtavfsind` starts the RTAVFS indexed register set. `RTAVFS_REG0` through `RTAVFS_REG127` are repeated CPO measurement registers: even registers define 16-bit `RTAVFSCPO<N>_STARTCNT` and `RTAVFSCPO<N>_STOPCNT` fields, while odd registers define a 16-bit `RTAVFSCPO<N>_RIPPLECNT` field plus reserved high bits. This gives CPO entries 0 through 63.
- `RTAVFS_REG128` through `RTAVFS_REG148` define AVFS control/readback fields: raw AVFS voltage in `RTAVFS_REG130`, clock-divider and loop controls in `RTAVFS_REG131` and `RTAVFS_REG138`, ripple-counter/CPO final result selection and min/max accumulation in `RTAVFS_REG132` through `RTAVFS_REG139`, PSM controls/readbacks for VDD and VREG in `RTAVFS_REG140` through `RTAVFS_REG143`, and temperature ring oscillator controls/readbacks/calibration coefficients in `RTAVFS_REG144` through `RTAVFS_REG148`.
- `RTAVFS_REG149` through `RTAVFS_REG159` define 16-bit FSM timing/count fields, including startup, idle, CPO/ripple-counter reset/start/done, CPO final-result ready, voltage-code ready, target-voltage ready, stop-CPO, and wait-for-ack counts. The chunk ends at the first line of `RTAVFS_REG160`, so the complete definition for that register is in the following chunk.

Field names are descriptive but not sufficient to infer access rules. `RESERVED` and `UNUSED_0` fields mark bits that consumers should preserve unless the ASIC programming guide or generated defaults explicitly say otherwise.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU and related driver code:

1. GC 10.3.0 users include `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h`.
2. Driver code selects a direct MMIO register, an indexed GC CAC register, an indexed SE CAC register, an SPM sample-delay indirect address, or a GRTAVFS indirect register.
3. The code composes a 32-bit value with this chunk's masks and shifts, preserving unrelated fields as required.
4. Register access helpers perform the actual read/write over MMIO or an indirect index/data pair.

The indirect CAC path is lock-protected in `soc15.c`: GC CAC accesses write `mmGC_CAC_IND_INDEX` and read/write `mmGC_CAC_IND_DATA`, while SE CAC accesses write `mmSE_CAC_IND_INDEX` and read/write `mmSE_CAC_IND_DATA`. This matters because many macros in this chunk describe indexed registers rather than independently addressable direct MMIO registers.

For SPM sample-delay programming, `gfx_v10_0.c` golden settings write `mmRLC_SPM_GLB_SAMPLEDELAY_IND_ADDR` followed by `mmRLC_SPM_GLB_SAMPLEDELAY_IND_DATA`. The `*_SAMPLEDELAY` masks in this chunk describe the data payload once the correct indirect address is selected.

For CAC power-transition LUT and pattern-control programming, driver code writes GC CAC indirect indices such as `ixPWRBRK_STALL_PATTERN_CTRL` through `mmGC_CAC_IND_INDEX` and data through `mmGC_CAC_IND_DATA`. The LUT, fixed-pattern counter, and update-status masks in this chunk describe the packed fields used by that hardware state machine.

The RTAVFS definitions describe hardware fields used by firmware or power-management paths, but this chunk does not encode polling loops, wait times, reset sequencing, thermal conversion formulas, voltage-code policy, or ownership between SMU firmware, RLC, and host driver code.

## State And Persistence Behavior

This file stores no software state and persists nothing on disk. It describes hardware state exposed by GC 10.3.0 registers.

Represented hardware state includes CAC activity accumulators, forced override selectors/values, CAC power-transition lookup tables, fixed-pattern performance counters, LUT update status, SE CAC IDs/control/overrides, SPM sample-delay configuration for global and per-SE blocks, CPO start/stop/ripple counters, AVFS voltage and target-voltage selections, PSM min/max/average measurements, temperature ring oscillator configuration and readback, and RTAVFS FSM timing counters.

Persistence is hardware-defined. Some fields are configuration bits that remain until reset or reprogramming. Others are live counters, latched measurement results, status bits, or action-control fields that may change while the GPU is running. GPU reset, suspend/resume, clock-gating, power-gating, runtime power management, SMU intervention, and RLC firmware activity can clear, overwrite, or make stale the state described by these fields.

The macros do not describe access class. A register field may be read-only, write-only, read/write, write-one-to-clear, self-clearing, sticky, firmware-owned, or invalid on a subset of SKUs. Consumers need read-modify-write discipline for mixed control/reserved registers and explicit sequencing for status/counter reads.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h`, which supplies corresponding register offsets and indirect indices. The broader generated register set also includes enum/default headers for related GC 10.3.0 values.

Known include users of the GC 10.3.0 shift/mask header in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`

Important integration points:

- AMDGPU SOC15 register-access plumbing, especially indirect GC CAC and SE CAC helpers guarded by `adev->reg.gc_cac.lock` and `adev->reg.se_cac.lock`.
- GFX v10 golden register programming, which initializes many RLC SPM sample-delay indirect registers from tables.
- Power-management and SMU paths for Van Gogh/GC 10.3-era parts, where RTAVFS and voltage/temperature fields are relevant to AVFS and thermal behavior.
- Profiling, diagnostics, and hardware validation paths that read CAC accumulators, fixed-pattern counters, LUT status, and sample-delay settings.
- GPU reset, runtime PM, suspend/resume, and ASIC bring-up flows, because these hardware fields are tied to clocks, power states, RLC firmware, and SMU-owned policy.

This chunk is source-tree aligned to AMDGPU generated register metadata. It does not provide the semantic event IDs, legal LUT entries, voltage-code interpretation, temperature calibration units, or firmware contracts; those must come from adjacent generated headers, firmware interfaces, ASIC documentation, and consuming driver code.

## Risks And Edge Cases

- Header/offset mismatch is a primary risk. Pairing GC 10.3.0 masks with a different generation's offsets or indirect indices can compile while programming the wrong hardware field.
- The macros are untyped integer constants. A swapped register name, incorrect shift, or missing mask can silently alter unrelated fields.
- Full-width `0xFFFFFFFFL` accumulator and override windows are common. Full-width masks do not mean every value is safe to write; many are readback counters, packed override payloads, or firmware/hardware-owned data windows.
- `SQ` and `SP` accumulators are split into lower and upper registers with only 8 valid high bits. Consumers need correct low/high ordering and should not treat reserved upper bits as part of a 64-bit counter.
- Indirect registers require serialized index/data access. Missing the GC CAC or SE CAC lock, reusing the wrong index register, or interleaving reads and writes from another path can corrupt the transaction.
- LUT fields are densely packed. Release/stall/power-break tables use different entry widths and spacing, so table programming code cannot safely reuse one packing formula across all LUT types.
- `HW_LUT_UPDATE_STATUS` has separate done/error/error-step fields for five tables. Polling only the done bits can miss partial update failures.
- Sample-delay fields have only 6 valid bits. Values outside `0x3f` must be masked, and reserved high bits should be preserved. Incorrect sample delays may show up as profiling data skew rather than an immediate fault.
- Per-SE/per-SA/per-WGP sample-delay registers encode topology assumptions. A field can be present in the generated header but irrelevant or fused off on a particular SKU.
- RTAVFS registers cross firmware, power, voltage, and thermal domains. Host writes that race SMU/RLC ownership or ignore enable/reset sequencing can destabilize AVFS behavior, produce invalid voltage targets, or create hard-to-reproduce hangs.
- RTAVFS CPO registers are repetitive and easy to index incorrectly. Off-by-one errors between even start/stop registers and odd ripple-count registers can associate a measurement with the wrong CPO.
- The chunk boundary is artificial. It starts in the middle of the CAC accumulator block and ends at `RTAVFS_REG160`; adjacent chunks are needed for a complete per-file analysis.

## Test Signals

Useful validation is mostly build, static, and hardware/profiling coverage:

- Build coverage for GC 10.3.0 AMDGPU, AMDKFD, SDMA, GFXHUB, and SMU users that include `gc_10_3_0_sh_mask.h`.
- Generated-header consistency checks that each `__SHIFT` has a matching `_MASK`, masks align to their shifts, fields do not overlap except documented full-width aliases, and register names match `gc_10_3_0_offset.h`.
- Static checks that reserved/unused fields are not written as literal one-filled values by consumers.
- Indirect-access tests or review checks confirming GC CAC and SE CAC operations use the proper index/data registers and the existing locks.
- CAC accumulator smoke tests on real GC 10.3 hardware: reset/clear or sample counters, run known graphics/compute workloads, read block accumulators, and confirm plausible nonzero activity in expected blocks.
- Power-transition LUT tests that program release/stall/power-break patterns, poll `HW_LUT_UPDATE_STATUS`, and verify both done and error fields.
- SPM sample-delay validation through GFX golden settings and profiler runs, including checks for skewed, zero, or unstable SPM streams after reset and resume.
- RTAVFS validation under power-management test matrices: boot, runtime PM, suspend/resume, GPU reset, thermal load, voltage changes, and firmware handoff. Watch for invalid voltage-code readbacks, stuck `RUNLOOP`, bad CPO final results, temperature calibration failures, or FSM counters that stop advancing.
- Regression indicators include GPU hangs during CAC/SPM/AVFS programming, profiler data becoming all zero or saturated, table update error bits, sample-delay values outside the 6-bit field, temperature/voltage telemetry discontinuities, or failures isolated to GC 10.3 SKUs and firmware revisions.
