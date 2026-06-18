# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_6_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002727`: lines 1-4469, `Docs/researches/chunks/subset-b-002727_research.md`
- `subset-b-002728`: lines 4470-9119, `Docs/researches/chunks/subset-b-002728_research.md`
- `subset-b-002729`: lines 9120-11899, `Docs/researches/chunks/subset-b-002729_research.md`

## Chunk Research

### subset-b-002727: lines 1-4469

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_6_0_sh_mask.h lines 1-4469

## Purpose

This chunk begins the generated GMC 6.0 shift/mask header for the AMDGPU Southern Islands era memory controller. It defines C preprocessor constants for bit masks and bit shifts used to read, write, and update fields in GMC/ATC/MC registers. The paired offset header is `gmc_6_0_d.h`; this file supplies the field layout for those register offsets.

The first 4469 lines cover:

- The include guard and AMD/MIT-style license.
- Address Translation Cache and ATS control, debug, fault, status, VM aperture, and VMID-to-PASID mapping fields.
- GMC control/debug/power-gating sequencer fields (`GMCON_*`).
- Memory-controller arbitration, DRAM timing, refresh, retry/training, GECC, queue, page/bank mapping, and power-management fields (`MC_ARB_*`).
- Memory BIST control, command, compare, data, readback, start/end address, and mismatch-address fields.
- Clock-gating, CITF, hub, read request, write data path, write return, and memory-controller hub client throttle/credit/status fields.
- Memory IO impedance calibration, CDR controls, and the start of many PHY debug/tuning register fields for ACMD, ADDRH, ADDRL, CK, CMD, DBI, DQ, DQB0, DQB1, and DQB2 lanes. The chunk ends mid-register-family at `MC_IO_DEBUG_DQB2L_OFSCAL_D0`.

The constants are not behavior by themselves. They are hardware ABI metadata that lets driver code manipulate exactly the documented bit fields in volatile GPU MMIO registers.

## Important APIs, Types, And Data

This chunk defines no functions, structs, enums, or storage. Its API surface is the macro naming contract:

- `REG__FIELD_MASK` gives the already-positioned bit mask.
- `REG__FIELD__SHIFT` gives the right-shift amount for the field.
- Register names such as `MC_ARB_RAMCFG` match offsets from `gmc_6_0_d.h`, for example `mmMC_ARB_RAMCFG`.
- Indexed IO debug register names such as `MC_IO_DEBUG_DQB2L_OFSCAL_D0` match `ix*` offsets in `gmc_6_0_d.h`.

Important field groups in this chunk:

- `ATC_ATS_*`, `ATC_L1*`, `ATC_L2*`: ATS enable/disable, PRI/PASID behavior, debug invalidation, default page routing, fault reporting, busy/crashed/deadlock status, TLB debug, and translation request throttling.
- `ATC_VM_APERTURE*` and `ATC_VMID*_PASID_MAPPING`: per-aperture virtual-page ranges, VMID selection masks, PASID values, and valid bits for up to 16 VMIDs.
- `MC_ARB_RAMCFG`: memory geometry fields consumed by driver code, including `NOOFBANK`, `NOOFRANKS`, `NOOFROWS`, `NOOFCOLS`, `CHANSIZE`, and `NOOFGROUPS`.
- `MC_ARB_DRAM_TIMING*`, `MC_ARB_RFSH_*`, `MC_ARB_BANKMAP`, `MC_ARB_GDEC_*`: low-level DRAM scheduling, refresh, bank/rank/page decode, and request grouping fields.
- `MC_ARB_GECC2*` and `MC_ARB_FED_CNTL`: ECC/error injection, status clear/status bits, read/write error mode, and fatal-error handling fields.
- `MC_BIST_*`: memory BIST reset/run/done, address/data mode, loop counts, command issue, compare mask, data/EDC storage, mismatch count/address, and readback data words.
- `MC_CITF_*`: client-interface credits, return mode, clock gating, DAGB delay, performance monitor, and weighted throttling fields.
- `MC_HUB_MISC_*`, `MC_HUB_RDREQ_*`, `MC_HUB_WDP_*`, `MC_HUB_WRRET_*`: hub status, idle/busy/deadlock indicators, read request client enables and throttles, write data path credits and throttles, multi-GPU fields, and write-return status.
- `MC_IMP_*` and `MC_IO_*`: memory IO impedance calibration, PHY strength, clock-data-recovery controls, phase selection, drive strength pull-up/pull-down, self-calibration, RX equalization, and VREF calibration fields.

## Control Flow

There is no executable control flow in this chunk. The only compile-time flow is header inclusion guarded by `GMC_6_0_SH_MASK_H`.

Runtime control flow happens in consumers:

- Callers read a register offset from `gmc_6_0_d.h`, apply a mask from this file, shift by the matching `__SHIFT`, and interpret the result.
- For writes, callers either build a register value by shifting field values into place and masking, or use helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `CGS_REG_SET_FIELD`, and `CGS_REG_GET_FIELD`, which depend on the `REG__FIELD_MASK` and `REG__FIELD__SHIFT` naming convention.
- SI/GMC6-era files include this header with `gmc_6_0_d.h`, notably `amdgpu/gmc_v6_0.c`, `amdgpu/gfx_v6_0.c`, `amdgpu/si.c`, `amdgpu/dce_v6_0.c`, `pm/legacy-dpm/si_dpm.c`, and display resource code for DCE 6.0.

Visible direct consumers include:

- `gmc_v6_0.c`, which reads `mmMC_ARB_RAMCFG` and uses `MC_ARB_RAMCFG__CHANSIZE_MASK` while setting up VRAM geometry.
- `gfx_v6_0.c`, which caches `MC_ARB_RAMCFG` and extracts `NOOFCOLS`.
- `si_dpm.c`, which extracts `NOOFROWS`, `NOOFCOLS`, `NOOFBANK`, and `CHANSIZE` from `MC_ARB_RAMCFG`.
- `si.c`, `cik.c`, and `vi.c`, which list or handle `mmMC_ARB_RAMCFG` in register tables; later generations use analogous masks from their own generated headers.

## State And Persistence Behavior

The macros are stateless compile-time constants. They do not allocate memory, mutate software state, persist files, or cache values.

The state they describe is volatile GPU hardware state:

- ATS, ATC, and VMID/PASID fields affect address translation behavior and fault/status reporting until reset or reprogramming.
- `MC_ARB_*` fields describe and control memory-controller arbitration, timing, refresh, queueing, error handling, and power behavior. Some are read as hardware configuration, while others can be programmed by initialization or power-management paths.
- `MC_BIST_*` fields drive built-in memory tests and expose test status and mismatch information.
- `MC_HUB_*` fields control per-client request throttles, credits, blackout exemptions, stall modes, and status bits for display, HDP, RLC, SMU, UVD, VCE, VMC, XDMA, and memory-channel paths.
- `MC_IO_*` fields tune or observe memory PHY analog/digital behavior. Misprogramming these fields can affect signal integrity or memory stability.

Any durable policy comes from BIOS tables, driver tables, firmware decisions, or kernel code that writes registers later. This header only provides the bit-level schema those paths use.

## Dependencies

This chunk depends on the generated AMD ASIC register include contract:

- `gmc_6_0_d.h` provides the matching `mm*` and `ix*` register offsets.
- Register helper macros in AMDGPU/CGS code assume exact `REG__FIELD_MASK` and `REG__FIELD__SHIFT` names.
- Callers need the appropriate register-access functions or macros, such as `RREG32`, `WREG32`, `REG_GET_FIELD`, `REG_SET_FIELD`, and CGS equivalents.
- The masks must match the GMC 6.0 hardware specification. Adjacent generated headers for GMC 7.x and 8.x contain similar names but not always identical fields, clients, or reserved bits.

The source path places this under `drivers/gpu/drm/amd/include/asic_reg/gmc/`, so it is shared by multiple AMDGPU submodules rather than owned by one runtime component.

## Integration Points

This header integrates with:

- GMC6 memory-management initialization in `amdgpu/gmc_v6_0.c`.
- SI display and graphics setup paths in `dce_v6_0.c`, `gfx_v6_0.c`, and display DCE 6.0 resource code.
- Legacy SI dynamic power management in `pm/legacy-dpm/si_dpm.c`.
- ASIC register table handling in SI/CIK/VI-era code that needs memory-controller register metadata.
- AtomBIOS-derived memory geometry and timing interpretation, because BIOS structures refer to `MC_ARB_RAMCFG` fields such as rows, columns, banks, ranks, and channel size.
- Hardware debug, bring-up, and board characterization workflows that may access `MC_IO_DEBUG_*`, BIST, GECC, hub status, or performance monitor registers.

The chunk also has a strong merge-time dependency on later chunks of the same file: line 4469 stops in the middle of the `MC_IO_DEBUG_DQB2L_OFSCAL_D0` field pair, so whole-file research must merge this with subsequent `MC_IO_DEBUG_*` definitions before describing the complete PHY debug register surface.

## Risks

- A wrong mask or shift can silently corrupt unrelated bits in an MMIO register. That is especially risky for hardware control fields that share registers with reset, enable, clear, force, or debug bits.
- Cross-generation reuse is unsafe. GMC 6.0, 7.x, and 8.x headers use overlapping names but can add fields, change reserved bits, or expose different clients.
- `MC_ARB_RAMCFG` fields feed memory geometry calculations. Incorrect field definitions can cause wrong VRAM row/column/bank/channel interpretation, which can cascade into tiling, address decoding, or performance assumptions.
- ATS/PASID/VMID mapping fields affect address translation and fault attribution. Bad masks can break isolation, fault logging, or invalidation behavior.
- BIST and GECC fields include reset, run, status clear, fault injection, and mismatch reporting. Blind read-modify-write operations can clear diagnostics or start intrusive tests.
- Hub read/write throttling and credits affect display, media, DMA, VM, and command clients. Misprogramming can cause stalls, underruns, deadlock warnings, or misleading status polling.
- PHY tuning/debug fields are analog-sensitive and often board/ASIC dependent. Writes should be limited to documented bring-up or firmware-guided paths.
- Because this is generated metadata, manual edits are high risk. A compile test catches missing names but usually cannot prove a mask matches silicon.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for SI/GMC6 AMDGPU code that includes both `gmc_6_0_d.h` and `gmc_6_0_sh_mask.h`.
- Static checks that every `REG__FIELD_MASK` in lines 1-4469 has a matching `REG__FIELD__SHIFT` unless intentionally a one-off guard macro.
- Static checks that every register prefix in this chunk has a matching `mm*` or `ix*` offset in `gmc_6_0_d.h`.
- Compile-time coverage of `REG_GET_FIELD` and `REG_SET_FIELD` users, especially `MC_ARB_RAMCFG` consumers in `gmc_v6_0.c`, `gfx_v6_0.c`, and `si_dpm.c`.
- Runtime smoke tests on matching SI hardware that read `MC_ARB_RAMCFG` and confirm decoded geometry is plausible against BIOS-reported memory configuration.
- Power-management and display stress tests that exercise hub read/write throttling and watch for deadlock warnings, display underruns, or media/DMA stalls.
- Hardware diagnostic tests that run memory BIST and GECC status paths only in safe test environments, verifying status/mismatch fields without disturbing normal operation.
- Register metadata diffing against AMD's generated source or known-good kernel headers for GMC 6.0.

### subset-b-002728: lines 4470-9119

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_6_0_sh_mask.h lines 4470-9119

## Purpose

This chunk is the middle generated register-field mask slice for AMD GMC 6.0. It exports C preprocessor constants for memory-controller, memory-IO, power-management, request-buffer, sequencer, and training registers. Each field is represented as a `REGISTER__FIELD_MASK` and, normally, a matching `REGISTER__FIELD__SHIFT` value for composing or decoding 32-bit MMIO register values.

The range starts inside the `MC_IO_DEBUG_DQB2L_OFSCAL_D0` field list, continues through the remaining DQB2L entries, complete DQB3, EDC, WCDR, WCK, and `MC_IO_DEBUG_UP_0..159` debug value tables, then covers pad/PHY control, memory clock power management, PMG mode-register controls, read arbitration groups, RPB request-buffer controls, and a large block of memory-sequencer control/timing/status/training masks. It ends in the first part of `MC_SEQ_TRAIN_WAKEUP_MASK`; the remaining fields are in the next chunk.

This file is declarative hardware binding data. It has no executable code, but the constants are part of the Southern Islands / GMC 6.0 register ABI used by AMDGPU display, graphics, power-management, and memory-controller bring-up paths.

## Major Register Areas Covered

The first section defines memory-IO debug lane masks. The `MC_IO_DEBUG_DQB2L_*`, `MC_IO_DEBUG_DQB3_*`, `MC_IO_DEBUG_DQB3H_*`, `MC_IO_DEBUG_DQB3L_*`, `MC_IO_DEBUG_EDC_*`, `MC_IO_DEBUG_WCDR_*`, and `MC_IO_DEBUG_WCK_*` families expose four byte-wide `VALUE0..VALUE3` fields at shifts 0, 8, 16, and 24. These cover clock select, miscellaneous, offset calibration, RX equalization, RX phase, RX VREF calibration, TX boost pull-down/pull-up, TX phase, TX self settings, CDR phase-size, dynamic RX power management, and EDC/WCDR equalization power-management fields for D0/D1 channels.

`MC_IO_DEBUG_UP_0..159` is a dense debug table with the same four 8-bit `VALUE*` fields per register. It appears to map a generated register-index space used by the memory-controller IO debug loader rather than hand-authored driver logic. In the GMC 6.0 firmware load path, `gmc_v6_0.c` writes firmware-provided index/data pairs to `MC_SEQ_IO_DEBUG_INDEX` and `MC_SEQ_IO_DEBUG_DATA`; these `MC_IO_DEBUG_*` masks document the bit layout of those indexed payload registers.

The pad and PHY control section covers `MC_IO_DPHY_STR_CNTL_D0/D1`, `MC_IO_PAD_CNTL`, `MC_IO_PAD_CNTL_D0/D1`, RX control for DPHY0/1 and D0/D1, TX control for APHY and DPHY, `MCLK_PWRMGT_CNTL`, `MC_MEM_POWER_LS`, `MC_NPL_STATUS`, and `MC_PHY_TIMING*`. These masks describe low-level electrical and timing controls: data/command/address delay sync, fall-out behavior, read strobe forcing/delay, VREF enable/select, clock delay selection, power-off controls, GDDR power-on, drive strengths, RX comparator/equalization and CDR controls, TX pull-up/pull-down strengths, TX slew, dynamic power management, DLL/pad timing, and memory clock gating or switching state.

The PMG and mode-register section covers `MC_PMG_AUTO_CFG`, `MC_PMG_AUTO_CMD`, `MC_PMG_CFG`, `MC_PMG_CMD_MRS*`, and `MC_PMG_CMD_EMRS`. These fields describe memory power-management automation, self-refresh and DPM wake behavior, mode-register reset/command construction, MRS wait counters, YCLK and ACPI acknowledgement behavior, RX power state, and ZQ calibration send controls.

The read arbitration and request-buffer section covers `MC_RD_CB`, `MC_RD_DB`, `MC_RD_HUB`, `MC_RD_TC0/TC1`, `MC_RD_GRP_EXT/GFX/LCL/OTH/SYS`, and `MC_RPB_*`. The masks provide per-client or per-traffic-class read-request controls, grouping, weights, queue IDs, BIF/XPB ordering controls, read/write combine and switch controls, performance counter selection, debug fields, and effective-control/status bits for the request path between clients and the memory controller.

The sequencer section starts with bit/byte remap (`MC_SEQ_BIT_REMAP_B0..B3_D0/D1`, `MC_SEQ_BYTE_REMAP_D0/D1`) and then covers DRAM timing and command state. `MC_SEQ_CAS_TIMING*`, `MC_SEQ_RAS_TIMING*`, `MC_SEQ_MISC_TIMING*`, `MC_SEQ_PMG_TIMING*`, `MC_SEQ_CNTL*`, `MC_SEQ_DRAM*`, `MC_SEQ_CMD`, `MC_SEQ_FIFO_CTL`, `MC_SEQ_MPLL_OVERRIDE`, and `MC_SEQ_CG` fields encode memory-type/timing controls, low-power variants, queue and FIFO controls, command issue state, PLL override, clock gating, DRAM configuration, and error insertion hooks.

The sequencer microcontroller and status portion includes `MC_SEQ_IO_DEBUG_INDEX/DATA`, `MC_SEQ_IO_RDBI/REDC/RWORD*`, `MC_SEQ_MISC*`, performance counters, PMG command registers for low-power modes, page-gating hardware/software controls, read-control framing for D0/D1, reserved sequencer state, RX framing for bytes/DBI/EDC, `MC_SEQ_STATUS_M/S`, and `MC_SEQ_SUP_*` supervisor program/status registers. These masks support memory-controller firmware loading, sequencer state inspection, and low-level training/debug flows.

The final part covers training and wakeup controls. `MC_SEQ_TCG_CNTL` defines a training command generator with reset/start/load FIFO, MOP, burst/data count, auto-refresh, DBI, valid-pointer masking, done, and channel-enable fields. `MC_SEQ_TIMER_RD/WR` define full-width counters. `MC_SEQ_TRAIN_CAPTURE`, `MC_SEQ_TRAIN_WAKEUP_CLEAR`, `MC_SEQ_TRAIN_WAKEUP_CNTL`, `MC_SEQ_TRAIN_WAKEUP_EDGE`, and the beginning of `MC_SEQ_TRAIN_WAKEUP_MASK` describe wakeup/capture events for auto-refresh, command/data FIFO readiness, read/write EDC, memory-clock frequency changes, software wakeup, timers, training state-machine completion, DPM, allow-stop signals, idle, and PHY power gating. `MC_SEQ_TRAIN_EDC_THRESHOLD*` and `MC_SEQ_TRAIN_TIMING` provide EDC retrain status/threshold and train timing fields.

## Important APIs, Types, and Functions

There are no functions, types, structs, or enums in this chunk. The exported API is the generated macro namespace:

- `REGISTER__FIELD_MASK` gives the bit mask to preserve, clear, test, or encode a field.
- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- Full-register fields such as sequencer timers, status words, program words, and debug data use `0xffffffffL` masks with shift 0.
- Repeated debug-register families use four byte fields: `VALUE0`, `VALUE1`, `VALUE2`, and `VALUE3`.

The immediate companion dependency is `gmc_6_0_d.h`, which supplies register offsets such as `mmMC_SEQ_TRAIN_WAKEUP_CNTL`, `mmMC_SEQ_SUP_CNTL`, `mmMC_SEQ_IO_DEBUG_INDEX`, and `mmMC_SEQ_IO_DEBUG_DATA`. Including C files combine these offsets with the mask constants through raw `RREG32`/`WREG32` operations or through generic AMDGPU field helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` where applicable.

## Control Flow

This header has no runtime control flow. Its effective flow is compile-time macro expansion:

1. A GMC 6.0 consumer includes the generated register offset and mask headers.
2. Driver code selects a register by offset and a field by `REGISTER__FIELD_*` macro.
3. The driver reads, tests, clears, or writes a 32-bit MMIO value using `RREG32`, `WREG32`, or a register-field helper.
4. Hardware interprets the selected bit fields as memory-controller, PHY, PMG, request-buffer, sequencer, or training state.

The most visible runtime flow from this chunk appears in `amdgpu/gmc_v6_0.c`. During memory-controller firmware loading, the driver checks `MC_SEQ_SUP_CNTL__RUN_MASK`, writes supervisor control values to reset and make the sequencer writable, streams firmware IO debug index/data pairs through `MC_SEQ_IO_DEBUG_INDEX` and `MC_SEQ_IO_DEBUG_DATA`, writes sequencer program words through `MC_SEQ_SUP_PGM`, returns the engine to active state, then polls `MC_SEQ_TRAIN_WAKEUP_CNTL__TRAIN_DONE_D0_MASK` and `MC_SEQ_TRAIN_WAKEUP_CNTL__TRAIN_DONE_D1_MASK` until both memory channels report training completion or the device timeout expires.

Other flows are implied by the register groups: memory timing setup writes DRAM, CAS/RAS, miscellaneous timing, and PHY fields; display and graphics clients rely on read-group/request-buffer fields for memory request priority and ordering; power-management paths can program PMG, memory clock, and sequencer page-gating controls; diagnostics can read status, wakeup capture, EDC retrain, performance counter, and debug fields.

## State and Persistence Behavior

The header stores no state. It names fields in GPU hardware registers, and those hardware registers retain or lose state according to the ASIC's reset, suspend, resume, dynamic power management, and memory-training sequences.

Persistent or semi-persistent state represented by this range includes memory PHY electrical tuning, pad enable and power-off bits, drive strengths, RX/TX phase/equalization/VREF controls, memory clock power-management state, mode-register command data, DRAM timing values, sequencer microcode program/control state, request-buffer ordering and queue controls, and page-gating or clock-gating settings. Firmware-provided IO debug arrays written during initialization can materially affect memory training and signal integrity.

Transient and status state includes `MC_NPL_STATUS`, RPB performance counter status, sequencer status master/slave fields, supervisor program/status fields, training wakeup captures, training wakeup clear bits, EDC retrain status/in-progress bits, training timers, and TCG done bits. The macro names alone do not identify read-clear, write-one-to-clear, sticky, or side-effect semantics. Callers must rely on the register programming sequence, hardware documentation, and existing AMDGPU initialization flows.

## Dependencies and Integration Points

This generated header depends only on the C preprocessor, but it must stay synchronized with the GMC 6.0 register-offset header and with AMD's source register database. It is included directly by `amdgpu/gmc_v6_0.c`, `amdgpu/gfx_v6_0.c`, `amdgpu/si.c`, `amdgpu/dce_v6_0.c`, `pm/legacy-dpm/si_dpm.c`, and `display/dc/resource/dce60/dce60_resource.c`.

Important integration points for this chunk are:

- GMC 6.0 memory-controller initialization in `amdgpu/gmc_v6_0.c`, especially sequencer firmware loading, IO debug index/data programming, and polling `MC_SEQ_TRAIN_WAKEUP_CNTL` training-done bits.
- Southern Islands graphics and display code that shares the same generated register namespace and may combine GMC masks with graphics, display, and memory arbitration setup.
- Legacy DPM code that can interact with memory-clock power management, PMG, self-refresh, memory clock switching, and low-power timing fields.
- Firmware and VBIOS data paths that provide IO debug tables and memory-timing values consumed by the driver and interpreted through these register layouts.
- Hardware diagnostics, bring-up, and RAS-style tooling that need to decode sequencer status, request-buffer counters, EDC retraining state, and wakeup captures.

## Risks and Edge Cases

The main risk is silent hardware misprogramming if any generated mask or shift drifts from the actual GMC 6.0 register specification. A wrong bit in this chunk can alter memory PHY training, DRAM timing, page/clock gating, request ordering, or sequencer firmware control without necessarily causing a compile error.

The chunk is heavily repetitive. Debug families repeat the same four `VALUE*` byte fields across DQB, EDC, WCDR, WCK, and 160 `MC_IO_DEBUG_UP_*` registers. Sequencer byte/bit remap, RX framing, D0/D1, and low-power/non-low-power variants also repeat with small name changes. Reviewers should treat generation drift, skipped entries, duplicated entries, or off-by-one register-family ranges as realistic hazards.

Several constants use `0xffffffffL` or high-bit masks such as `0x80000000L`. Callers must use unsigned 32-bit register semantics and avoid sign-extension assumptions from the `L` suffix on platforms where `long` width differs.

Many fields are not ordinary configuration bits. Wakeup clear, training command-generator start/reset, DRAM error insertion, supervisor program/control, mode-register commands, page-gating controls, memory-clock controls, and PHY power-off fields can have immediate hardware side effects. The header does not encode valid sequencing, required delays, timeout policy, or whether a status bit is sticky.

This chunk starts mid-register and ends mid-family. `MC_IO_DEBUG_DQB2L_OFSCAL_D0` begins before line 4470, and `MC_SEQ_TRAIN_WAKEUP_MASK` continues after line 9119. Any final per-file report should merge chunks 1 and 3 before making complete-header claims.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Kernel builds with Southern Islands AMDGPU, display, and legacy DPM enabled should compile without missing `gmc_6_0_sh_mask.h` macro names.
- Static comparison against AMD's generated GMC 6.0 register database should verify every `MASK`/`SHIFT` pair, especially repeated `MC_IO_DEBUG_UP_0..159`, D0/D1, low-power, and wakeup-clear/capture/mask families.
- Field round-trip checks can validate representative masks: `MC_SEQ_TRAIN_WAKEUP_CNTL__TRAIN_DONE_D0/D1`, `MC_SEQ_SUP_CNTL__RUN`, `MC_IO_PAD_CNTL_D1__TXPWROFF_CLK`, `MC_PMG_CFG__ZQCL_SEND`, `MC_RPB_CONF__RPB_*_PCIE_ORDER`, and `MC_SEQ_TCG_CNTL__DONE`.
- Hardware boot tests on GMC 6.0 devices should verify successful memory-controller firmware load, IO debug table programming, memory training completion on both D0 and D1, VRAM sizing, and stable display scanout.
- Suspend/resume and DPM tests should exercise memory clock switching, self-refresh, page/clock gating, PMG wake paths, and restoration of sequencer/PHY state.
- Stress tests should include VRAM bandwidth, display under memory pressure, graphics workloads, and fault/retrain diagnostics where available, watching for training timeouts, EDC retrain status changes, request-buffer stalls, or sequencer status errors.

### subset-b-002729: lines 9120-11899

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_6_0_sh_mask.h lines 9120-11899

## Scope

This chunk is the tail section of AMD's generated GMC 6.0 shift/mask header. It covers lines 9120-11899, with 2,778 preprocessor definitions: 1,389 `_MASK` constants and 1,389 matching `__SHIFT` constants, followed by the file-closing `#endif`. The range contains no functions, structs, enums, storage objects, branches, allocation, locking, or direct MMIO access. Its public interface is a set of compile-time bitfield constants for Southern Islands / GMC v6 memory-controller, crossbar, XPB, memory PLL, GPUVM, and PRT registers.

The source path is under `sources/distributed-fs/ceph-client`, but this file is AMD GPU register metadata and has no Ceph filesystem behavior.

## Purpose

`gmc_6_0_sh_mask.h` supplies bit positions and masks for registers whose addresses are defined in the companion `gmc_6_0_d.h` header. Driver code combines these constants with register helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`, or with direct shifts and masks, to compose and decode 32-bit hardware register values.

The naming convention is consistent:

- `<REGISTER>__<FIELD>_MASK` is the raw field mask in the 32-bit register.
- `<REGISTER>__<FIELD>__SHIFT` is the field's least significant bit.

This chunk describes the later GMC v6 register families: memory sequencer training/status fields, GDDR transmit framing, write timing and low-power write timing mirrors, shared memory-channel layout, memory-controller training error counters, VM aperture and GART/page-table controls, MC client write grouping, MC crossbar arbitration and credit controls, XPB peer/routing/BAR controls, memory PLL controls, VM context fault and invalidation fields, L2 VM cache controls, and partially resident texture aperture controls.

## Important APIs, Types, And Macro Families

There are no C APIs or local types. The macros are the API, and their effective type is an integer constant used as part of a `u32` register value.

Important macro groups in this chunk are:

- `MC_SEQ_TRAIN_WAKEUP_MASK` at lines 9120-9159. These fields mask wakeup events for D0/D1 ARF, REDC, WEDC, command/data FIFO readiness, idle, DPM, low-power training, software wakeup, timer, TSM, TCG, SCLK/SRBM readiness, MCLK frequency changes, and PHY power-gating events.
- `MC_SEQ_TSM_*` at lines 9160-9253 plus `MC_TSM_DEBUG_*` at lines 9722-9827. These define the training state machine control, counters, flags, DBI/EDC/WCDR payload fields, capture/debug index/data fields, breakpoint fields, and debug readbacks for multiple byte counters.
- `MC_SEQ_TXFRAMING_*` at lines 9254-9445. These describe DQ, DBI, EDC, WCDR, and FCK nibble mappings for bytes 0-3 and memory channels D0/D1.
- `MC_SEQ_VENDOR_ID_*`, `MC_SEQ_WCDR_CTRL`, `MC_SEQ_WR_CTL_2`, `MC_SEQ_WR_CTL_D0/D1`, and their `_LP` variants at lines 9446-9603. These cover vendor ID readbacks, write clock/data recovery controls, write data delay, ODT delay, DQS timing, DAT_DLY, WCK timing, DQ/DQM timing, and low-power mirror registers used by the Southern Islands DPM path.
- `MC_SHARED_BLACKOUT_CNTL`, `MC_SHARED_CHMAP`, and `MC_SHARED_CHREMAP` at lines 9604-9629. These fields control memory-controller blackout and report or remap channel layout.
- `MC_TRAIN_EDCCDR_*`, `MC_TRAIN_EDC_STATUS_*`, and `MC_TRAIN_PRBSERR_*` at lines 9630-9721. These expose EDC/CDR training values and PRBS error counters/status fields by channel.
- `MC_VM_*` and `VM_*` at lines 9828-9975 and 11514-11897. These are the most directly used macros in `gmc_v6_0.c`: AGP base/bottom/top, display-controller write hit-region controls, framebuffer location and offset, per-client L1 TLB debug/status, MX L1 TLB control, system aperture low/high/default registers, VM context controls, page-table base/start/end addresses, protection fault defaults/status, context disable bits, invalidate request/response bits, L2 cache controls/status, PRT apertures, and PRT fault policy.
- `MC_WR_*` at lines 9976-10105. These field groups classify write clients such as CB, DB, EXT, GFX, LCL, OTH, SYS, HUB, TC0, and TC1 with watermark, group, and enable style controls.
- `MC_XBAR_*` at lines 10106-10257. These define memory crossbar address decode, arbitration, max burst, channel tri-remap, performance monitor select/result, read/write request and return credits, priority credits, remote controls, spare registers, and two-channel control.
- `MC_XPB_*` at lines 10258-11269. These describe XPB client latency-generator config slots 0-36, clock gating, interface config/status, local BAR address, map-invert flush controls, P2P BARs and setup/debug/delta fields, peer system BARs, performance knobs, pipe status, route destination maps, route source apertures, sticky and write-one-clear sticky status, sub-control flags, uncorrectable thresholds, write-combine buffer status/config, and XDMA peer/routing variants.
- `MPLL_*` at lines 11270-11513. These expose memory PLL analog/digital controls and status: AD function/status, mode control, main control, DQ lane status/function control, function control words, sequencer microcode words, spread-spectrum controls, and PLL timing.

## Control Flow

This header has no runtime control flow. Runtime control is in the including driver code:

1. Southern Islands code includes `gmc/gmc_6_0_d.h` and `gmc/gmc_6_0_sh_mask.h`.
2. The caller selects a register address such as `mmVM_CONTEXT1_CNTL`, `mmVM_L2_CNTL`, `mmMC_SHARED_CHMAP`, or `mmMC_SEQ_WR_CTL_D0_LP`.
3. The caller composes or decodes a 32-bit value using the macros directly or through `REG_SET_FIELD()` / `REG_GET_FIELD()`.
4. MMIO helpers such as `RREG32()`, `WREG32()`, or ring packets perform the hardware read/write.

Concrete consumers include `gmc_v6_0.c`, which programs memory apertures, GART contexts, L1/L2 TLBs, VM context fault policy, PRT apertures, and TLB invalidations; `gfx_v6_0.c`, which emits command-stream VM flushes through `mmVM_INVALIDATE_REQUEST`; and `si_dpm.c`, which maps active MC timing registers to `_LP` low-power mirror registers such as `MC_SEQ_WR_CTL_D0_LP`, `MC_SEQ_WR_CTL_D1_LP`, and `MC_SEQ_WR_CTL_2_LP`.

## State And Persistence Behavior

The macros themselves store no state and have no persistence. The hardware registers they describe are stateful:

- Memory sequencer training, TSM, WCDR, EDC/CDR, PRBS, and MPLL fields reflect or control memory bring-up, clocking, lane framing, and training state. Some bits are live status, some are control bits, and some are debug snapshots.
- `_LP` memory timing registers persist low-power timing/programming alternatives used by DPM transitions. `si_dpm.c` copies active timing registers into low-power mirrors and builds a VBIOS-derived MC register table around these addresses.
- `MC_SHARED_BLACKOUT_CNTL` changes CPU/MC access behavior during MC stop/resume in `gmc_v6_0.c`. Incorrect persistence across suspend/resume or reset can block framebuffer access.
- `MC_SHARED_CHMAP` is read to derive memory channel count and VRAM bus width in `gmc_v6_0_mc_init()`.
- `MC_VM_SYSTEM_APERTURE_*`, `MC_VM_AGP_*`, `MC_VM_FB_LOCATION`, and page-table address fields persist the GPU address map until reprogrammed or reset.
- `VM_CONTEXT0_CNTL` and `VM_CONTEXT1_CNTL` enable context translation and fault behavior. Context 0 is programmed for the PCIE GART; contexts 1-15 are configured for application VMIDs.
- `VM_INVALIDATE_REQUEST` and `VM_INVALIDATE_RESPONSE` are live synchronization registers for GPU TLB/cache invalidation domains.
- `VM_L2_CNTL*` and `MC_VM_MX_L1_TLB_CNTL` determine GPUVM cache/TLB behavior and are rewritten during GART enable/disable.
- `VM_CONTEXT*_PROTECTION_FAULT_*` fields hold fault default addresses, faulting logical page address, VMID, client ID, read/write direction, and protection class. They are diagnostic state updated by hardware.
- `VM_PRT_CNTL` and `VM_PRT_APERTURE*` persist partially resident texture aperture policy and are changed when PRT support is enabled or disabled.
- XPB and XBAR fields describe routing, credits, P2P BARs, sticky faults, and performance counters. Their values can be live status, configuration, or sticky write-one-clear state depending on the register.

The header does not encode reset values, access permissions, write-one-clear semantics, reserved-bit policy, read side effects, timing constraints, or required ordering. Those semantics come from hardware documentation and the surrounding driver sequences.

## Dependencies

This chunk depends on:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_6_0_d.h` for matching `mm*` register addresses. The macros in this chunk are meaningful only when paired with that generation's address header.
- AMDGPU register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `RREG32()`, `WREG32()`, and `amdgpu_ring_emit_wreg()`.
- Southern Islands GMC/GFX code in `amdgpu/gmc_v6_0.c` and `amdgpu/gfx_v6_0.c`.
- Southern Islands power-management code in `pm/legacy-dpm/si_dpm.c`, which includes both `gmc_6_0_d.h` and this shift/mask header and uses the MC timing mirror register names from this chunk.
- Firmware and VBIOS-derived memory-controller tables used by `gmc_v6_0_mc_load_microcode()` and `si_initialize_mc_reg_table()`. The header provides bit metadata around the register set; firmware/VBIOS tables provide many actual values.

## Integration Points

Key integration points are:

- MC stop/resume in `gmc_v6_0.c`: `MC_SHARED_BLACKOUT_CNTL__BLACKOUT_MODE` is used to blackout and unblackout the memory controller around access changes.
- VRAM and aperture setup in `gmc_v6_0.c`: `MC_VM_SYSTEM_APERTURE_LOW_ADDR`, `MC_VM_SYSTEM_APERTURE_HIGH_ADDR`, `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR`, `MC_VM_AGP_BASE`, `MC_VM_AGP_TOP`, `MC_VM_AGP_BOT`, and `MC_VM_FB_LOCATION` define the visible GPU memory map.
- Channel-width discovery in `gmc_v6_0_mc_init()`: `MC_SHARED_CHMAP__NOOFCHAN_MASK` and `MC_SHARED_CHMAP__NOOFCHAN__SHIFT` decode memory channel count and combine with RAM configuration to set `adev->gmc.vram_width`.
- GART enable/disable in `gmc_v6_0.c`: `MC_VM_MX_L1_TLB_CNTL`, `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, `VM_CONTEXT0_*`, and `VM_CONTEXT1_*` fields configure page-table depth, block size, context enable, fault defaults, and TLB/cache behavior.
- TLB flush paths: `gmc_v6_0_flush_gpu_tlb()` and `gmc_v6_0_emit_flush_gpu_tlb()` write `VM_INVALIDATE_REQUEST` bits for VMIDs 0-15, and `gfx_v6_0_ring_emit_vm_flush()` waits for the invalidate sequence in the command stream.
- Fault handling: `gmc_v6_0_set_fault_enable_default()` changes default handling for range, dummy-page, PDE0, valid, read, and write faults; `gmc_v6_0_vm_decode_fault()` decodes `VM_CONTEXT1_PROTECTION_FAULT_STATUS` fields such as `VMID`, `PROTECTIONS`, memory client ID, and access direction.
- PRT support in `gmc_v6_0_set_prt()`: `VM_PRT_CNTL` toggles fault suppression and invalid-entry storage for CB/TC/L1/L2 behavior, while `VM_PRT_APERTURE{0..3}_{LOW,HIGH}_ADDR` defines reserved partially resident texture ranges.
- Southern Islands DPM memory tables: `si_dpm.c` maps active memory timing registers to low-power mirrors, including `MC_SEQ_WR_CTL_D0`, `MC_SEQ_WR_CTL_D1`, and `MC_SEQ_WR_CTL_2` families from this chunk.
- Debug and performance tooling: `MC_TSM_DEBUG_*`, `MC_XBAR_PERF_MON_*`, `MC_XPB_PIPE_STS`, sticky XPB fields, TLB debug/status, and fault status fields provide readback surfaces for diagnosing memory-controller, VM, crossbar, and peer-routing behavior.

## Risks And Edge Cases

- Header/address mismatch is the primary risk. Using GMC 6.0 masks with another generation's address header can compile when names overlap but program the wrong bit layout.
- The chunk begins in the middle of the overall generated header and ends at the final `#endif`; earlier fields for related registers are outside this range. Merge tooling must combine adjacent chunk notes before drawing whole-file conclusions.
- `VM_CONTEXT0_*` and `VM_CONTEXT1_*` have similar field names but different runtime roles. Context 0 is the kernel/GART context, while context 1 controls the template for contexts 1-15 in this driver.
- Page-table and address fields are page-number fields. `gmc_v6_0.c` writes values shifted by 12 or 22 bits; feeding byte addresses directly would corrupt aperture, AGP, GART, PRT, or fault default programming.
- `VM_INVALIDATE_REQUEST` uses one bit per VMID/domain. Incorrect shifts or stale VMID assumptions can leave old translations live or invalidate the wrong context.
- `VM_L2_CNTL*` and `MC_VM_MX_L1_TLB_CNTL` are cache/TLB policy registers. Bad values can cause VM faults, stale PTE/PDE use, or broad GPU memory corruption rather than a localized failure.
- Fault-control bits have default, interrupt, and save variants with similar names. Confusing them can suppress fault reporting, create interrupt storms, or lose fault diagnostics.
- PRT enable intentionally disables some VM faults for unmapped accesses. `gmc_v6_0_set_prt()` warns when doing this; tests must distinguish expected PRT behavior from accidental fault masking.
- `_LP` timing registers must match VBIOS/DPM expectations. Copying or remapping the wrong MC sequence register can break memory clock transitions or low-power state entry.
- Full-width masks in this chunk describe payload registers such as debug data, vendor IDs, AGP/page numbers, counters, or route apertures. A `0xffffffffL` mask is not evidence that arbitrary writes are safe.
- XPB sticky and sticky-W1C registers have similar names but different clearing semantics. Treating write-one-clear status as normal read/write state risks losing fault evidence.
- XBAR and XPB routing/BAR fields affect peer/system routing and credits. Incorrect values can cause hangs or unreachable apertures in P2P/XDMA or multi-client memory traffic.
- MPLL and memory training controls are sequencing-sensitive. Incorrect direct writes can destabilize memory clocks or training and are generally only safe in prescribed firmware/bring-up flows.

## Test And Validation Signals

Useful validation for this generated-header chunk is mostly build, static, and hardware smoke coverage:

- Build Southern Islands AMDGPU objects that include the header, especially `gmc_v6_0.c`, `gfx_v6_0.c`, and `pm/legacy-dpm/si_dpm.c`.
- Static generated-header checks that every `_MASK` has the matching `__SHIFT`, field masks align with shifts, field names match `gmc_6_0_d.h` register names, and fields do not unexpectedly overlap within a register.
- Boot and modeset tests on Tahiti, Pitcairn, Verde, Oland, and Hainan class hardware to cover MC firmware load, MC blackout/unblackout, channel-map decoding, aperture programming, and framebuffer visibility.
- GART and GPUVM tests that allocate GPU mappings, emit VM flushes, exercise VMIDs 0-15, and verify `VM_INVALIDATE_REQUEST` behavior through graphics-ring flush paths.
- VM fault tests covering invalid, read, write, range, PDE0, and dummy-page faults, with checks that `VM_CONTEXT1_PROTECTION_FAULT_STATUS` decodes the expected VMID, client, access direction, and protection bits.
- PRT tests that toggle `gmc_v6_0_set_prt()`, validate aperture programming for all four PRT ranges, and confirm expected unmapped-access behavior without hiding unrelated VM faults.
- Suspend/resume and DPM memory-clock transition tests that exercise `_LP` MC timing register population from `si_dpm.c`.
- Memory-controller training diagnostics that watch TSM, EDC/CDR, PRBS error, WCDR, and MPLL status fields across boot, resume, and memory clock changes.
- Crossbar and XPB stress tests, when hardware support exists, using P2P/XDMA/system BAR traffic, high read/write pressure, and performance/sticky status readbacks.
