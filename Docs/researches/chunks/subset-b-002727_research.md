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
