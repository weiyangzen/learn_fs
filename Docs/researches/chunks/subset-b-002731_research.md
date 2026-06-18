# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_0_sh_mask.h lines 1-5143

## Scope and Purpose

This chunk covers lines 1-5143 of `gmc_7_0_sh_mask.h`, an AMD-generated register field mask/shift header for the GMC 7.0 memory-controller block used by CIK-era GPUs. It contains preprocessor constants only: each hardware register field is represented as a `REGISTER__FIELD_MASK` value and a matching `REGISTER__FIELD__SHIFT` value. The paired constants are the ABI used by driver code to extract, compose, clear, or test fields in 32-bit MMIO registers.

The covered range starts with the file license and include guard, then defines field metadata for memory-controller configuration, arbitration, client interface routing, hub request/write-return paths, VM apertures and TLB controls, XPB peer/BAR routing, crossbar credits, performance counters, ATC/ATS translation, PASID mappings, and the first part of GMCON reset/stutter control. The requested range ends at line 5143, in the middle of `GMCON_MISC`; later `GMCON_MISC` fields and subsequent registers are outside this chunk.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or exported symbols in this chunk. The important API surface is the macro naming contract:

- `REGISTER__FIELD_MASK` identifies the bit mask for a field inside a 32-bit hardware register.
- `REGISTER__FIELD__SHIFT` identifies the right shift needed after masking, or the left shift needed before composing a value.
- Register addresses are not defined here; they come from the paired `gmc_7_0_d.h` address header and are used with accessors such as `RREG32()` and `WREG32()`.

Major covered register families:

- `MC_CONFIG`, `MC_CG_CONFIG`, `MC_CONFIG_MCD`, and `MC_CG_CONFIG_MCD` define memory-controller read/write enable and index-mode fields for MCD/MCDW-MCDZ instances.
- `MC_ARB_*` defines the memory arbiter programming surface: aging, ECC/GECC2 status and injection, address swizzling and hashing, bank maps, RAM geometry, refresh/power management, DRAM timing, lazy/streak/write-turnaround controls, return credits, replay controls, busy status, and arbitration performance counters.
- `MC_CITF_*` defines the client-interface layer: client read/write enable controls, credits, DAGB delay, return mode, WTM decrement controls, local/remote grouping, busy/perf status, and clock-gating fields.
- `MC_HUB_*` defines hub-side read request, write data path, write-return, status, blackout, credit, stall, priority, and client-specific throttle controls for clients including graphics, display, SDMA, UVD, VCE, RLC, SMU, HDP, CP, ACP, XDMA, CPC, CPF, and SAM.
- `MC_RPB_*` defines the request packet buffer interface, queue selection, read/write switch controls, write combining, BIF credits, and RPB performance counter control/status.
- `MC_SHARED_*`, `MC_RD_GRP_*`, and `MC_WR_GRP_*` define channel mapping/remapping and assignment of GPU clients into read/write arbitration groups.
- `MC_VM_*` defines framebuffer/AGP/system aperture fields, display-controller write hit regions, L1 TLB enable/debug/status fields for MB/MD clients, L2 arbiter credits, steering, and blackout control.
- `MC_XPB_*` defines cross-peer bridge source apertures, destination maps, cache-line gathering configuration entries, P2P BAR setup/debug/delta registers, peer system BARs, interface credits/status, pipeline status, sticky status, clock gating, and sub-block reset/stall controls.
- `MC_XBAR_*` defines memory crossbar address decoding, remote enable, per-output credits for read/write requests and returns, channel remap, two-channel mode, arbitration, maximum bursts, and xbar performance monitor fields.
- `MC_*_PERFCOUNTER*`, `ATC_PERFCOUNTER*`, and `CHUB_ATC_PERFCOUNTER*` provide common low/high counter halves, compare values, selection ranges, enable/clear bits, and result control fields for CITF, hub, RPB, MCBVM, MCDVM, VM L2, MC arbiter, ATC, and CHUB ATC counters.
- `ATC_*` defines address translation cache aperture ranges, ATS/PRI/PASID enable controls, ATS fault logging/status/default page handling, ATC L1/L2 cache/TLB debug, invalidation, deadlock status, and VMID-to-PASID mapping status/entries.
- `GMCON_RENG_*` and the covered portion of `GMCON_MISC` define reset-engine RAM access, reset-engine execution pointers/modes, SRBM credits, and stutter/self-refresh control bits.

## Control Flow and Data Flow

This header has no executable control flow. Runtime flow appears in consumers that include `gmc_7_0_d.h` for register addresses and this file for field layout. A typical use is:

1. Read a register with `RREG32(mmREGISTER)`.
2. Extract a field with `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`.
3. Compose or clear fields with mask/shift constants.
4. Write the new register image with `WREG32(mmREGISTER, value)`.

Concrete integration examples found in the tree:

- `amdgpu/gfx_v7_0.c` directly includes `gmc/gmc_7_0_d.h` and `gmc/gmc_7_0_sh_mask.h`, making these constants available to the GFX7 driver path.
- `amdgpu/cik.c` saves `GMCON_RENG_EXECUTE`, `GMCON_MISC`, and `GMCON_MISC3` around reset, then clears `GMCON_RENG_EXECUTE__RENG_EXECUTE_ON_PWR_UP_MASK`, `GMCON_MISC__RENG_EXECUTE_ON_REG_UPDATE_MASK`, and `GMCON_MISC__STCTRL_STUTTER_EN_MASK` before reset-sensitive operations.
- `pm/legacy-dpm/si_dpm.c` reads `mmMC_ARB_RAMCFG` and extracts `MC_ARB_RAMCFG__NOOFROWS`, `NOOFCOLS`, and `NOOFBANK` to derive DRAM row/column/bank geometry and refresh-rate behavior.

Because these macros describe hardware bit layout, data flow is from hardware register values into driver state decisions, and from driver-selected policy values back into hardware registers.

## State and Persistence Behavior

The header itself persists no state. Its constants describe hardware state that persists in GPU registers until reset, power-state transitions, firmware/hardware updates, or driver writes change it.

Important state classes represented in this chunk:

- Configuration state: memory channel/MCD enablement, arbitration policy, grouping, credit limits, blackout behavior, stutter/self-refresh controls, P2P BAR routing, ATS/PASID enablement, and aperture boundaries.
- Status state: busy/outstanding bits, deadlock warnings, credit availability, performance counter values, fault status, sticky XPB bits, and VMID remapping completion.
- Clear/update semantics: several fields imply write-one-clear, clear, invalidate, update, or trigger behavior, such as `*_CLEAR`, `*_W1C`, `INVALIDATE_*`, `CLEAR_ALL`, `UPDATE`, and `RENG_EXECUTE_NOW`. Consumers must preserve unrelated fields when manipulating these registers.

## Dependencies and Integration Points

This file depends only on the C preprocessor. Its practical dependencies are the generated register address headers and the AMDGPU register accessor layer:

- Paired address definitions in `gmc/gmc_7_0_d.h`.
- ASIC-specific consumers that include both address and mask headers, especially CIK/GFX7 code paths.
- MMIO access helpers such as `RREG32`, `WREG32`, and read/modify/write helpers in AMDGPU.
- Power-management, reset, VM, memory-controller, and performance-monitor code that needs stable field encodings.

The macro names are not namespaced by C types, so collisions are controlled by ASIC-specific include discipline. Many equivalent field names exist in other generated ASIC headers (`gmc_7_1_sh_mask.h`, `gmc_8_*_sh_mask.h`, `athub_*_sh_mask.h`, newer `gc_*_sh_mask.h`), and a compilation unit must include the header matching the register block it programs.

## Risks and Edge Cases

- Bit-layout drift is high impact: an incorrect mask or shift can silently program the wrong hardware field, causing memory corruption, hangs, display underruns, failed resets, broken power management, or invalid address translation.
- The chunk boundary cuts through `GMCON_MISC`: line 5143 defines `GMCON_MISC__STCTRL_DISABLE_GMC_OFFLINE_MASK`, while its matching shift appears at line 5144 outside this work item. Any merged research for the full file must reconcile that split.
- Generated headers are easy to misuse across ASIC generations. Similar-looking fields may have different masks, shifts, suffixes, or semantics in `gmc_7_1`, `gmc_8_*`, `gc_*`, or `athub_*` headers.
- Reserved/debug/ECO fields are present throughout. Driver writes should avoid changing unknown reserved bits unless the hardware programming guide or known workaround requires it.
- Status and clear fields require care: write-one-clear, invalidate, update, and trigger bits should not be treated like passive configuration fields.
- Address and aperture fields use encoded page-number or base/top units, not raw byte addresses. Callers must apply the correct page/shift conventions from the relevant programming code.
- Performance counter fields are split across low/high/compare/config/result-control registers. Incorrect ordering of clear/enable/read operations can produce stale or partial counts.

## Test and Validation Signals

Useful validation for changes touching this header or its consumers:

- Build coverage for AMDGPU configurations that compile CIK/GFX7 paths, verifying no macro name collisions or missing mask/shift pairs.
- Runtime boot/resume/reset tests on GMC 7.0 hardware, with attention to hangs during reset, stutter/self-refresh transitions, and memory-controller initialization.
- Power-management tests that exercise DRAM geometry and refresh calculations derived from `MC_ARB_RAMCFG`.
- VM and fault tests that exercise aperture programming, L1/L2 TLB invalidation, ATS/PASID mapping, and fault-status reporting.
- Peer-to-peer/XDMA tests for `MC_XPB_*` BAR and routing fields where supported.
- Perf counter smoke tests for MC arbiter, hub, RPB, VM, and ATC counters: clear, enable, run traffic, read low/high results, and verify nonzero or saturating behavior as expected.
- Static checks that every generated `*_MASK` has the intended matching `*__SHIFT`, especially around chunk boundaries and repeated numbered register families.
