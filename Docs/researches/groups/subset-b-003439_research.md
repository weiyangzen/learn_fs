# Research: subset-b-003439

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_10_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_10_0_offset.h

## Purpose

`umc_8_10_0_offset.h` is a generated AMDGPU register-offset header for the UMC 8.10.0 memory-controller block. It exports symbolic offsets and base-index selectors for a small set of GPU memory error reporting registers. It contains no executable code, types, or storage; its public surface is the `reg*` macro namespace.

## Important APIs, Types, And Macros

The header defines `regUMCCH0_0_GeccErrCntSel`, `regUMCCH0_0_GeccErrCnt`, `regMCA_UMC_UMC0_MCUMC_STATUST0`, `regMCA_UMC_UMC0_MCUMC_ADDRT0`, and `regUMCCH0_0_GeccCtrl`, with matching `_BASE_IDX` macros. The offsets identify the GECC error counter selector, GECC error counter, MCA-style UMC status/address registers, and a GECC control register. All base indexes are `2`, unlike older UMC 8.7.0 and newer UMC 8.14.0 headers in this work item, so consumers must not assume the same register aperture across generations.

## Control Flow And Data Flow

There is no local control flow. Driver logic includes this file, combines one of these offsets with a register access helper, and uses matching masks from `umc_8_10_0_sh_mask.h` to select counters, read corrected/uncorrected error counts, decode MCA status, read the fault address, or enable fatal handling for uncorrectable errors.

## State And Persistence Behavior

The macros store no software state. They name persistent hardware registers whose values are maintained by the UMC/MCA hardware until read, cleared, reprogrammed, or reset. The represented state includes ECC/poison counter configuration, accumulated error counts, MCA status validity/overflow bits, error-address state, and fatal-error enablement.

## Dependencies And Integration Points

The file depends only on the C preprocessor. It is intended to be paired with `umc_8_10_0_sh_mask.h` and with AMDGPU RAS, UMC, memory-controller, and GPU reset paths that poll or clear memory error state.

## Risks And Test Signals

Risks are ABI-style: using these offsets with another UMC generation can read the wrong aperture, corrupt GECC control, or misreport RAS errors. The key tests are compile coverage for ASIC code that includes UMC 8.10.0 headers, RAS injection or fault-reporting tests that verify corrected/uncorrected counts and MCA address decoding, and reset/suspend-resume tests that confirm error registers are not decoded through the wrong base index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_10_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_10_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_10_0_sh_mask.h

## Purpose

`umc_8_10_0_sh_mask.h` is the generated field-layout companion for UMC 8.10.0 offsets. It defines bit masks and shifts used to encode or decode GECC counter control, GECC counter values, MCA UMC status, MCA error address, and GECC fatal-error control. It has no functions, structs, or runtime data.

## Important APIs, Types, And Macros

For `UMCCH0_0_GeccErrCntSel`, the header exposes interrupt selection, GECC counter enable, and poison counter enable fields. `UMCCH0_0_GeccErrCnt` splits the register into 16-bit corrected and uncorrectable GECC counts. `MCA_UMC_UMC0_MCUMC_STATUST0` is a 64-bit status map with error code, extended code, address LSB, error core ID, scrub/poison/deferred flags, UECC/CECC classification, syndrome-valid, TCC, PCC, address/misc valid, enabled, uncorrected, overflow, and valid bits. `MCA_UMC_UMC0_MCUMC_ADDRT0` exposes a 56-bit error address. `UMCCH0_0_GeccCtrl__UCFatalEn` controls fatal treatment for uncorrectable errors.

## Control Flow And Data Flow

Consumers typically write `GeccErrCntSel` fields to select and enable an error counter, read `GeccErrCnt`, then read `STATUST0` and `ADDRT0` when a memory error is reported. Data flows from hardware MCA latches into driver RAS decoding. Status bits gate interpretation: the driver should treat address and misc fields as meaningful only when validity fields are set and should handle overflow as evidence of lost events.

## State And Persistence Behavior

The header itself is stateless. The described hardware state is persistent until cleared or reset: counters accumulate, MCA status latches error classification, address registers retain the reported physical address, and `UCFatalEn` changes future fault handling. Incorrect writes can persist until driver recovery or GPU reset.

## Dependencies And Integration Points

It is paired with `umc_8_10_0_offset.h`; offsets without these masks cannot be decoded safely. Integration points include AMDGPU RAS interrupt/report paths, sysfs/debugfs error count reporting, memory poison handling, GPU reset decision logic, and ASIC-specific UMC helpers.

## Risks And Test Signals

The main risks are 64-bit field truncation, using 32-bit helpers for MCA status, treating reserved fields as writable, and assuming address validity without checking `AddrV`. Test signals include ECC injection, poison event handling, CE/UE classification checks, validation that 16-bit counter fields do not bleed into each other, and register-generation diffs against AMD's canonical UMC 8.10.0 data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_10_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_14_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_14_0_offset.h

## Purpose

`umc_8_14_0_offset.h` is a compact generated UMC 8.14.0 register-offset header. It exposes only the GECC error-counter selector and GECC error-counter registers for channel 0, using the `regUMCCH0_*` naming style and base index `0`.

## Important APIs, Types, And Macros

The exported macros are `regUMCCH0_GeccErrCntSel`, `regUMCCH0_GeccErrCnt`, and their `_BASE_IDX` values. The offsets match the familiar `0x0328` and `0x0329` GECC selector/counter locations, but the symbol names no longer include the `CH0_0` instance spelling used by UMC 8.10.0 and 8.7.0. There are no MCA status/address offsets in this generation-specific file.

## Control Flow And Data Flow

No control flow is implemented here. Consumers use the selector offset to choose GECC or poison counting behavior and read the counter offset to retrieve corrected and uncorrected counts. Decoding requires the matching `umc_8_14_0_sh_mask.h` masks.

## State And Persistence Behavior

The header has no mutable state. It names persistent hardware counter configuration and count registers. The state is hardware-owned and may be affected by RAS configuration, error events, resets, or power transitions.

## Dependencies And Integration Points

This file depends only on preprocessing and integrates with ASIC-specific AMDGPU UMC/RAS code. It should be used with `umc_8_14_0_sh_mask.h`, not with older UMC masks whose symbol names include `UMCCH0_0` or whose base indexes differ.

## Risks And Test Signals

The narrowed surface is itself a risk: code ported from UMC 8.10.0 or 8.7.0 must not expect MCA `STATUST0` or `ADDRT0` macros from this header. Tests should build the UMC 8.14.0 path, verify GECC count reads on matching hardware, and compare generated names/offsets against the AMD register database.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_14_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_14_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_14_0_sh_mask.h

## Purpose

`umc_8_14_0_sh_mask.h` defines field masks and shifts for the two UMC 8.14.0 GECC counter registers exported by the offset header. It is generated hardware ABI data, not executable driver logic.

## Important APIs, Types, And Macros

`UMCCH0_GeccErrCntSel` exposes `GeccErrInt`, `GeccErrCntEn`, and `PoisonCntEn` fields. `UMCCH0_GeccErrCnt` exposes a low 16-bit `GeccErrCnt` field and high 16-bit `GeccUnCorrErrCnt` field. There are no MCA status, MCA address, or GECC fatal-control fields in this file.

## Control Flow And Data Flow

Driver code writes selector fields to enable and choose GECC/poison counting, then reads the count register and masks/shifts the two 16-bit counters. The absence of MCA fields means detailed error classification and address decoding must come from another block, another header, firmware, or generation-specific code outside this file.

## State And Persistence Behavior

The macros are stateless. The hardware fields describe persistent counter-enable state and counter values. Counter state may accumulate across ordinary driver activity and should be reset, sampled, or latched according to UMC/RAS sequencing outside this header.

## Dependencies And Integration Points

It pairs with `umc_8_14_0_offset.h`. Consumers include AMDGPU RAS and UMC helpers that need GECC counter reporting on UMC 8.14.0 ASICs. The symbols intentionally differ from the `UMCCH0_0_*` names used by earlier versions.

## Risks And Test Signals

Risks include stale consumer code referencing older macro names, accidental use of UMC 8.10.0 masks against UMC 8.14.0 offsets, and misinterpreting the two adjacent 16-bit fields. Test signals are build coverage for UMC 8.14.0, GECC counter readback, poison-count enable checks where supported, and generated-header diffing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_14_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_7_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_7_0_offset.h

## Purpose

`umc_8_7_0_offset.h` is the generated UMC 8.7.0 register-offset header for GECC counters and MCA UMC error-reporting registers. It uses the `mm*` address macro style rather than the `reg*` style used by the later UMC 8.10.0 and 8.14.0 headers in this work item.

## Important APIs, Types, And Macros

The header exports `mmUMCCH0_0_GeccErrCntSel`, `mmUMCCH0_0_GeccErrCnt`, `mmMCA_UMC_UMC0_MCUMC_STATUST0`, and `mmMCA_UMC_UMC0_MCUMC_ADDRT0`, with `_BASE_IDX` values of `0`. There is no `GeccCtrl` offset in this version-specific file.

## Control Flow And Data Flow

No code executes here. Consumers use these addresses with `umc_8_7_0_sh_mask.h` to select GECC counter sources, sample corrected/uncorrected counts, decode MCA status, and read the MCA error address when RAS or machine-check reporting indicates a UMC error.

## State And Persistence Behavior

The macros do not store software state. They name hardware latches and counters that persist until cleared, reset, or overwritten by new hardware events. The base-index value is part of the access path and is therefore important state-routing metadata for register helpers.

## Dependencies And Integration Points

This file integrates with AMDGPU UMC 8.7.0 RAS handling, memory error interrupt/reporting code, and MMIO helpers that understand `mm*` offsets and base indexes. It should be paired with `umc_8_7_0_sh_mask.h`.

## Risks And Test Signals

Risks include confusing `mm*` and `reg*` naming families, using the wrong base index, and assuming the later `GeccCtrl` fatal-enable field exists. Tests should include build coverage for UMC 8.7.0, ECC injection/readout, MCA address decode validation, and generated-offset comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_7_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_7_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_7_0_sh_mask.h

## Purpose

`umc_8_7_0_sh_mask.h` is the generated UMC 8.7.0 bitfield header. It defines masks and shifts for GECC counter selection, GECC count values, MCA UMC status, and MCA UMC address reporting. It is hardware description data with no functions or mutable variables.

## Important APIs, Types, And Macros

The `UMCCH0_0_GeccErrCntSel` field set includes `GeccErrCntCsSel`, `GeccErrInt`, `GeccErrCntEn`, and `PoisonCntEn`; the chip-select selector is a notable difference from UMC 8.10.0. `UMCCH0_0_GeccErrCnt` again provides corrected and uncorrectable 16-bit counters. `MCA_UMC_UMC0_MCUMC_STATUST0` defines the 64-bit MCA status layout, including error code, address LSB, core ID, scrub, poison, deferred, UECC/CECC, syndrome-valid, TCC, PCC, address/misc valid, enable, uncorrected, overflow, and valid fields. `MCA_UMC_UMC0_MCUMC_ADDRT0` exposes a 56-bit error address plus a six-bit `LSB` field and two reserved high bits.

## Control Flow And Data Flow

Consumer control flow is external: configure the counter selector, read counts, then decode MCA status/address when an event is latched. Address reconstruction may require combining `ErrorAddr`, `LSB`, and status `AddrLsb`, depending on the consuming RAS path and hardware documentation.

## State And Persistence Behavior

The header is stateless, but the hardware fields represent persistent counters, status latches, validity flags, and address state. Overflow and valid bits are especially important because they determine whether the current report is complete or whether events were lost.

## Dependencies And Integration Points

It pairs with `umc_8_7_0_offset.h` and integrates with AMDGPU RAS, MCA decoding, UMC error count reporting, memory poison handling, and reset/recovery paths. Consumers need 64-bit-safe access for the MCA status/address masks.

## Risks And Test Signals

Risks include dropping the `GeccErrCntCsSel` dimension, ignoring the `LSB` address field, reading 64-bit MCA registers through 32-bit-only helpers, or writing reserved bits. Test signals include CE/UE injection on multiple chip-selects, address reconstruction checks, overflow handling, and register-generation diffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_7_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_3_1_d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_3_1_d.h

## Purpose

`uvd_3_1_d.h` is a generated register-address header for the AMD UVD 3.1 video decode engine. It defines `mm*` MMIO offsets and `ix*` indexed-register offsets for firmware communication, semaphores, memory-interface setup, clock/power control, ring-buffer command submission, VCPU control, and status reporting.

## Important APIs, Types, And Macros

The public API is a flat macro list. Key groups are `mmUVD_SEMA_*` semaphore registers; `mmUVD_GPCOM_VCPU_*` firmware command/data registers; `mmUVD_ENGINE_CNTL`; UDEC/MIF address-configuration registers; context index/data; CGC gate/status/control; LMI control/status/swap/address-extension registers; master interrupt enable; firmware start/status; MPC mux/ALU controls; VCPU cache offset/size and `mmUVD_VCPU_CNTL`; `mmUVD_SOFT_RESET`; RBC IB/RB base, size, pointers, write-pointer control, read-pointer writeback, and status; semaphore timeout registers; and PGFSM/power-status registers.

## Control Flow And Data Flow

Driver initialization programs memory tiling and LMI settings, configures VCPU firmware cache windows, starts firmware through engine/VCPU controls, enables interrupts and semaphores, and submits decode work through the RBC ring and indirect buffers. Runtime paths update write pointers, read status, handle semaphore timeouts, and use GPCOM data registers for firmware commands.

## State And Persistence Behavior

The header stores no state, but the addressed registers control persistent hardware state: firmware boot state, ring pointers, memory address mappings, cache/swap settings, clock-gating state, power state, soft-reset bits, context ID, and semaphore timeout latches.

## Dependencies And Integration Points

It pairs with `uvd_3_1_sh_mask.h` and integrates with AMDGPU UVD initialization, firmware loading, ring submission, interrupt handling, power management, and reset paths. Indexed `ix*` registers require the correct indexed-register access method, not ordinary MMIO.

## Risks And Test Signals

Risks include address/mask generation mismatch, using an `ix*` offset with an MMIO helper, misprogramming ring pointer alignment, or writing reset/power registers out of sequence. Tests should cover video decode firmware boot, ring submission, interrupt delivery, semaphore timeout handling, suspend/resume, and reset recovery on UVD 3.1 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_3_1_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_3_1_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_3_1_sh_mask.h

## Purpose

`uvd_3_1_sh_mask.h` is the generated UVD 3.1 field-layout header. It supplies masks and shifts for the register addresses in `uvd_3_1_d.h`; it implements no executable logic.

## Important APIs, Types, And Macros

The exported fields cover semaphore address/command/VMID control; GPCOM VCPU command and data payloads; engine start bits; UDEC and MIF tiling geometry; semaphore enable and timeout counters; LMI extended addressing, coherency, urgent, clean/idle status, swap controls, and cache flush/enable bits; context index/data; CGC gate/status/control for SYS, UDEC, MPEG2, RE/CM/IT/DB/MP, RBC, LMI, MPC, WCB, VCPU, and SCPU domains; master interrupt enables and overrun status; MPC mux/ALU/debug controls; VCPU cache windows and `UVD_VCPU_CNTL`; soft-reset bits for many UVD subblocks; RBC ring/IB base, size, read/write pointer, and control fields; PGFSM power-control/readback fields; power status; and firmware status masks such as busy, active, done, pass, fail, and invalid firmware metadata.

## Control Flow And Data Flow

Consumer code encodes startup, clock-gating, firmware, ring, and semaphore values with these masks. Decode submission data flows from software-managed ring buffers through RBC fields to the UVD VCPU. Status data flows back through `UVD_STATUS`, LMI clean/idle bits, interrupt enables/overruns, semaphore timeout latches, and firmware status bits.

## State And Persistence Behavior

The macros are stateless. The underlying fields control persistent engine state: clocks, power, reset, firmware validation, memory coherency, ring fetch behavior, timeout counters, and address-extension settings. Many fields must be preserved or updated in a defined sequence.

## Dependencies And Integration Points

This file must match `uvd_3_1_d.h`. It integrates with AMDGPU UVD firmware loading, ring tests, IB submission, interrupt handling, LMI cache maintenance, clock/power gating, and reset logic.

## Risks And Test Signals

Risks include unmasked writes to reserved/RFU bits, 64-bit address truncation through split address fields, incorrect ring alignment, enabling clocks or ring fetch before firmware/memory windows are valid, and treating timeout/status bits as ordinary writable state. Test signals include firmware-auth status checks, UVD ring tests, decode conformance, interrupt overrun tests, LMI clean/idle polling, and suspend/resume power-gating validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_3_1_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_0_d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_0_d.h

## Purpose

`uvd_4_0_d.h` is the generated register-address header for UVD 4.0. It exports MMIO and indexed offsets for the video decode engine's firmware communication, memory-interface configuration, clock/power management, ring-buffer command processor, semaphore handling, and status/control registers.

## Important APIs, Types, And Macros

The macro set largely mirrors UVD 3.x but is ordered differently and includes `mmUVD_GP_SCRATCH4`. Important groups include `ixUVD_CGC_*`, `ixUVD_LMI_*`, and `ixUVD_MIF_*` indexed registers; `mmUVD_CGC_*`; context index/data; `mmUVD_ENGINE_CNTL`; GPCOM command/data; LMI control/status/swap/address-extension; master interrupt enable; MPC setup; PGFSM and power status; RBC IB/RB base, pointer, writeback, control, and size-update registers; semaphore address/command/control and timeout registers; soft reset; UDEC address configuration; VCPU cache windows; and `mmUVD_VCPU_CNTL`.

## Control Flow And Data Flow

The driver programs UVD memory format and cache controls, loads and starts firmware, configures clock/power gating, initializes the RBC ring, and submits decode commands through write-pointer updates. Status and completion flow through interrupts, firmware/VCPU status fields, semaphore status, and ring read pointers.

## State And Persistence Behavior

The header is stateless. The hardware registers it names hold persistent engine configuration: ring locations, cache windows, command state, clock-gating masks, low-power memory controls, semaphore state, and reset status.

## Dependencies And Integration Points

It should be paired with `uvd_4_0_sh_mask.h`. It integrates with AMDGPU UVD 4.0 ASIC support, firmware boot, ring testing, decode scheduling, interrupt handling, and power/reset code.

## Risks And Test Signals

Risks include confusing UVD 4.0 VCPU cache offsets with the UVD 3.1/4.2 layout, mixing indexed and MMIO access, and accidentally reusing UVD 4.2 masks for fields that differ. Tests should boot firmware, run decode and ring tests, verify clock-gating transitions, handle semaphore faults, and compare generated offsets against the hardware register source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_0_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_0_sh_mask.h

## Purpose

`uvd_4_0_sh_mask.h` defines the UVD 4.0 register field masks and shifts used with `uvd_4_0_d.h`. The file is generated C preprocessor data and has no functions, structs, or runtime control flow.

## Important APIs, Types, And Macros

Field groups include CGC dynamic clock/ramp controls, clock gates, clock status, UDEC subblock status, and low-power memory controls; context and GPCOM command/data fields; LMI address extension, cache control, coherency, urgent, clean/idle, and byte-swap controls; semaphore address/command/enable and timeout fields; master interrupt enable/overrun fields; UDEC/MIF tiling geometry fields; MPC mux/ALU and debug fields; PGFSM power-control/readback and power-status fields; RBC ring and IB base/size/pointer/control fields; UVD soft-reset bits; UVD status; and VCPU control fields.

## Control Flow And Data Flow

Consumers encode register writes for firmware startup, ring initialization, clock/power configuration, LMI cache and coherency setup, and semaphore timeout control. Runtime status is decoded from clock-status bits, LMI clean/idle fields, `UVD_STATUS`, semaphore timeout status, and ring read pointers.

## State And Persistence Behavior

The macros are stateless, but the fields describe persistent hardware state. Clock-gate and memory-light-sleep fields influence power behavior across idle intervals; LMI fields control cache/coherency behavior; ring fields determine command fetch; reset fields alter subblock state; timeout fields latch error conditions.

## Dependencies And Integration Points

It pairs with `uvd_4_0_d.h` and is consumed by AMDGPU UVD 4.0 firmware, ring, interrupt, LMI, power-management, and reset code. The `L` suffix on many masks makes the constants suitable for the generated C macro style, but consumers still need correct register width handling.

## Risks And Test Signals

Risks include reserved-bit writes, generation drift from UVD 4.2, wrong VCPU cache-field assumptions, and sequencing errors around ring fetch, clock gating, or reset. Tests should include UVD ring tests, decode playback, interrupt and semaphore timeout paths, LMI cache flush/coherency checks, suspend/resume, and generated mask/shift diffing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_2_d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_2_d.h

## Purpose

`uvd_4_2_d.h` is the generated UVD 4.2 register-address header. It exposes the MMIO and indexed offsets needed by AMDGPU to initialize, command, monitor, power-manage, and reset the UVD video decode engine.

## Important APIs, Types, And Macros

The header includes semaphore registers; GPCOM VCPU command/data; engine control; UDEC address configuration; context index/data; CGC gate/status/control and UDEC status; LMI control/status/swap/address-extension; master interrupt enable; MPC mux/ALU controls; VCPU cache offsets/sizes at the `0x3d82` style locations; VCPU control; soft reset; RBC IB/RB base, size, read/write pointers, writeback, and controls; status and semaphore timeout registers; `UVD_RBC_IB_SIZE_UPDATE`; indexed LMI/CGC/MIF registers; PGFSM power registers; and power status.

## Control Flow And Data Flow

Driver control flow follows the standard UVD path: configure memory tiling and LMI behavior, prepare firmware cache windows, start the VCPU/engine, initialize the RBC ring, submit decode work through ring write pointers or IBs, service interrupts, and poll status/idle/timeout registers during teardown or recovery.

## State And Persistence Behavior

The header does not store state. The addressed registers persist engine configuration and event state: firmware/VCPU state, ring pointers, cache-window addresses, context ID, interrupt enablement, semaphore latches, clock/power state, and reset state.

## Dependencies And Integration Points

It should be used with `uvd_4_2_sh_mask.h`. Integration points are AMDGPU UVD 4.2 ASIC support, firmware loading, video decode scheduling, ring tests, LMI cache/coherency handling, interrupts, power gating, and GPU reset.

## Risks And Test Signals

Risks include assuming UVD 4.0's VCPU cache offset layout, mixing `ix*` and `mm*` access paths, and using masks from a nearby generation that has extra fields. Tests should run firmware boot, ring submission, decode workloads, semaphore fault paths, power-gating transitions, and generation-register diffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_2_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_2_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_2_sh_mask.h

## Purpose

`uvd_4_2_sh_mask.h` is the generated field-layout header for UVD 4.2. It provides masks and shifts for semaphore, command, memory-interface, clock-gating, ring-buffer, reset, status, and power-management registers.

## Important APIs, Types, And Macros

The public macro families cover semaphore address/command/VMID and timeout controls; GPCOM VCPU command/data; engine start; UDEC/MIF address-configuration geometry; LMI extended addressing, coherency, urgent, clean/idle, swap, and cache controls; context index/data; CGC gate/status/control for the main UVD and UDEC subdomains; master interrupt enable/overrun; MPC mux/ALU/debug controls; VCPU cache window fields; VCPU control; soft resets for RBC, LBSI, LMI, VCPU, UDEC, CSM, CXW, TAP, MPC, FWV, IH, MPRD, IDCT, LMI_UMC, SPH, MIF, and LCM; RBC ring/IB fields; PGFSM and power status.

## Control Flow And Data Flow

Consumers use these fields to bring the engine out of reset, program memory layout, load firmware cache ranges, enable clocks and interrupts, submit ring work, and wait for idle or clean status. Data moves from software command buffers to RBC/IB registers and from hardware back through status, timeout, interrupt, and read-pointer fields.

## State And Persistence Behavior

The macros are stateless. Underlying fields affect persistent video-engine behavior, including power/clock state, cache coherency, firmware command state, ring fetch state, semaphore timeout latches, and reset state. Some fields are status or clear-style and require semantics from the hardware guide or driver code.

## Dependencies And Integration Points

It pairs with `uvd_4_2_d.h` and integrates with AMDGPU UVD 4.2 firmware, ring, interrupt, power, LMI, and reset paths. It is close to UVD 3.1 but should remain generation-specific.

## Risks And Test Signals

Risks include truncating split address fields, writing reserved/RFU fields, enabling ring fetch before ring base and firmware windows are valid, and missing generation deltas from UVD 4.0. Test signals include UVD ring tests, decode validation, LMI clean/idle polling, semaphore timeout injection, suspend/resume, and generated header diffing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_4_2_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_5_0_d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_5_0_d.h

## Purpose

`uvd_5_0_d.h` is the generated register-address header for UVD 5.0. It extends the familiar UVD address surface with VMID, 64-bit BAR, SUVD clock-gating, additional PGFSM read tiles, direct MIF address-config MMIO registers, scalar/JPEG-related address configuration, and internal LMI VMID indexed registers.

## Important APIs, Types, And Macros

The header exports semaphore, GPCOM, engine, UDEC, context, CGC, LMI, interrupt, MPC, VCPU cache/control, soft-reset, RBC, status, and timeout registers. UVD 5.0-specific or notable additions include `mmUVD_LMI_RBC_RB_64BIT_BAR_*`, `mmUVD_LMI_RBC_IB_64BIT_BAR_*`, `mmUVD_LMI_VCPU_CACHE_64BIT_BAR_*`, `mmUVD_LMI_RBC_IB_VMID`, `mmUVD_LMI_RBC_RB_VMID`, `mmUVD_SUVD_CGC_*`, `ixUVD_LMI_VMID_INTERNAL*`, PGFSM tile3 through tile7, `mmUVD_MIF_*_ADDR_CONFIG`, `ixUVD_MIF_SCLR_ADDR_CONFIG`, and `mmUVD_JPEG_ADDR_CONFIG`.

## Control Flow And Data Flow

Driver code uses these offsets to configure 64-bit memory windows and VMID-aware ring/IB access, boot firmware, configure memory tiling, submit decode commands, manage SUVD and UVD clock/power state, and poll or clear status. The address flow is broader than earlier UVD versions because ring, IB, and VCPU cache locations have explicit 64-bit BAR and VMID controls.

## State And Persistence Behavior

The header is stateless. Named registers hold persistent engine configuration: 64-bit base addresses, VMIDs, ring pointers, firmware cache windows, clock/power state, reset bits, semaphore latches, and MIF/JPEG tiling state.

## Dependencies And Integration Points

It pairs with UVD 5.0 mask and enum headers, especially `uvd_5_0_enum.h` for field values. Integration points include AMDGPU UVD 5.0 firmware loading, VM-aware ring setup, decode scheduling, JPEG/shared decode support, power gating, interrupts, and reset.

## Risks And Test Signals

Risks include mishandling 64-bit BAR high/low ordering, failing to program VMIDs consistently for RB and IB, applying earlier UVD offset assumptions, or omitting SUVD power/clock programming. Tests should cover firmware boot, decode and JPEG paths where present, VMID isolation, high-address buffer placement, ring tests, suspend/resume, and register-generation diffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_5_0_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_5_0_enum.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_5_0_enum.h

## Purpose

`uvd_5_0_enum.h` provides typed integer enumerations for UVD 5.0 and adjacent AMDGPU hardware programming values. Unlike the offset and mask headers, this file exports C `typedef enum` types that give semantic names to command IDs, tiling modes, debug block IDs, formats, cache policies, performance counter modes, and memory power controls.

## Important APIs, Types, And Macros

Important enums include `UVDFirmwareCommand` for firmware command packet IDs such as fence, trap, decoded/bitstream/display addresses, pitch, tiling, and end-of-decode; endian and array/tiling geometry enums such as `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, group/row/bank/sample split, address-config pipe/interleave/shader-engine/GPU/lower-pipe enums; extensive debug block ID maps, including current, old, and BY2 naming schemes; color, surface, buffer, image data, and numeric format enums; tile type, micro/macro tiling, pipe/bank geometry enums; `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`; surface array/color/depth enums; SIMD count; and memory power force/disable/select enums.

## Control Flow And Data Flow

The file has no local control flow. Its values are consumed by command construction, register field encoding, debug/performance selection, memory tiling setup, format descriptors, and power-management programming. Values flow into packets or bitfields defined in companion register headers and firmware interfaces.

## State And Persistence Behavior

The enum constants are compile-time state only. When used in register writes or firmware packets, they select persistent hardware or firmware behavior such as surface interpretation, memory layout, cache policy, performance counter mode, debug block selection, and memory power mode.

## Dependencies And Integration Points

The file stands alone syntactically but is intended to be included by UVD 5.0 ASIC code and generated register consumers. It integrates with UVD firmware command submission, buffer/image metadata programming, tiling/address-library logic, debug/perf tooling, and power-management code.

## Risks And Test Signals

Risks include ABI drift in enum numeric values, duplicate/reserved names being treated as valid runtime choices, cross-generation reuse of debug block IDs, and mismatch between format enums and userspace/firmware expectations. Test signals include compile coverage, firmware command tests for each used `UVDFirmwareCommand`, decode/render format validation, tiling/address tests, perf/debug block selection smoke tests, and generated enum diffs. The duplicate `IMG_DATA_FORMAT_RESERVED_29` name/value in the source should be preserved as generated data unless the upstream register database changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_5_0_enum.h -->
