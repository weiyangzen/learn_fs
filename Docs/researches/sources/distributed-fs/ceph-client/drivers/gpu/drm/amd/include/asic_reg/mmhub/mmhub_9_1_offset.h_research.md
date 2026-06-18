# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_offset.h

## Purpose

`mmhub_9_1_offset.h` is a generated-style AMDGPU register offset header for the MMHUB 9.1 hardware block used by SOC15/Vega-era ASIC support. It does not implement executable logic. Instead, it exports preprocessor constants that name MMHUB registers and their SOC15 base-index selectors so driver code can use symbolic register names with AMD's register access macros.

The file is protected by `_mmhub_9_1_OFFSET_HEADER`, carries AMD's MIT-style license text, and is paired with `mmhub_9_1_sh_mask.h`, which supplies bit-field masks and shifts for the same register names. This offset header answers "where is the register?" while the matching mask header answers "which bits inside the register mean what?"

## Register Map Shape

The source contains 1,907 `#define` entries, split into 954 register offset macros and 953 companion `_BASE_IDX` macros. Every normal register symbol is intended to be used with a companion base-index selector, and in this MMHUB 9.1 map all visible `_BASE_IDX` values are `0`.

The source is organized by hardware address blocks, each annotated with an addressBlock name and base address:

- `mmhub_dagbdec`, base `0x68000`: DAGB read/write clients, arbitration controls, virtual-channel controls, credits, pending-status registers, performance counters, and reserved slots.
- `mmhub_ea_mmeadec`, base `0x68400`: MMEA0/MMEA1 DRAM and IO arbitration maps, priority/urgency controls, address normalization, DRAM address decode/hash controls, SDP controls, EDC/DSM controls, clock-gating controls, and error status.
- `mmhub_pctldec`, base `0x68e00`: power/deep-sleep controls, power gating, register-engine RAM access, and state-save ranges for multiple PCTL instances.
- `mmhub_l1tlb_vml1dec`, `mmhub_l1tlb_vml1pldec`, and `mmhub_l1tlb_vml1prdec`, bases around `0x69600`: MMHUB L1 TLB status and L1 perf-counter configuration/result registers.
- `mmhub_l1tlb_vmtlspfdec`, base `0x69680`: VM L2 SAW control and context-0 page-table aperture registers.
- `mmhub_utcl2_atcl2dec`, base `0x69900`: ATC L2 control, cache data/status, clock-gating, and memory-power registers.
- `mmhub_utcl2_vml2pfdec`, base `0x69a00`: VM L2 controls, dummy/protection fault controls and fault address/status registers, identity-aperture registers, bank selection, cache parity, and clock-gating.
- `mmhub_utcl2_vml2vcdec`, base `0x69b00`: VM context control registers, invalidation semaphore/request/acknowledge registers for engines 0-17, invalidation address ranges, and per-context page table base/start/end register pairs for contexts 0-15.
- `mmhub_utcl2_vml2pldec` and `mmhub_utcl2_vml2prdec`, bases around `0x69e90`: VM L2 perf-counter config and result registers.
- `mmhub_utcl2_vmsharedhvdec`, base `0x69f30`: virtual-function framebuffer size/offset, IOMMU controls, MARC base/relocation/length ranges, PCIe ATS controls for PF/VF operation, and UTCL2 clock-gating.
- `mmhub_utcl2_vmsharedpfdec`, base `0x6a040`: northbridge MMIO limits, PCI controls, top-of-DRAM registers, framebuffer offset, system aperture defaults, steering, shared virtualization reset, memory power, cacheable DRAM range, APT, and local HBM range controls.
- `mmhub_utcl2_vmsharedvcdec`, base `0x6a0b0`: framebuffer location, AGP aperture, system aperture, and MX L1 TLB control registers.
- `mmhub_utcl2_atcl2pfcntrdec` and `mmhub_utcl2_atcl2pfcntldec`, bases around `0x6a100`: ATC L2 perf-counter result/config controls.

The numeric offsets are SOC15-style register indices, not byte offsets used directly by C pointer arithmetic. Register access helpers combine the hardware IP block, instance, register offset, and base index to address the final MMIO register.

## Important APIs, Types, and Macros

This header exposes macros only. There are no C functions, structs, enums, or local data objects.

Important exported macro families include:

- `mmDAGB0_RDCLI*`, `mmDAGB0_WRCLI*`, `mmDAGB0_RD_*`, and `mmDAGB0_WR_*`: DAGB client routing, timing, credit, virtual-channel, pending, and perf-counter offsets.
- `mmMMEA0_*` and `mmMMEA1_*`: two MMEA instance maps for DRAM/IO arbitration, priority, address normalization, DRAM decode/hash, SDP, EDC, DSM, error, and performance registers.
- `mmPCTL*`: MMHUB power/deep-sleep, power-gating, register-engine, and state-save control offsets.
- `mmMC_VM_MX_L1_*`: L1 TLB status and perf-counter offsets.
- `mmATC_L2_*`: ATC L2 control, cache/status, clock, power, and perf-counter offsets.
- `mmVM_L2_*`: VM L2 configuration, status, protection fault, identity aperture, bank selection, cache parity, and clock-gating offsets.
- `mmVM_CONTEXT*_CNTL`: VM context control offsets for contexts 0-15.
- `mmVM_INVALIDATE_ENG*_SEM`, `REQ`, `ACK`, and `ADDR_RANGE_*`: TLB invalidation engine handshake and range offsets for engines 0-17.
- `mmVM_CONTEXT*_PAGE_TABLE_{BASE,START,END}_ADDR_{LO32,HI32}`: page-table root and virtual address aperture bounds for VM contexts 0-15.
- `mmMC_VM_*`, `mmVM_IOMMU_*`, and `mmVM_PCIE_ATS_CNTL*`: shared VM aperture, IOMMU, SR-IOV/VF, framebuffer, AGP, DRAM, HBM, and PCIe ATS offsets.

For each register macro `mmNAME`, the companion `mmNAME_BASE_IDX` is part of the public contract expected by AMD register helper macros such as `SOC15_REG_ENTRY_STR`, `RREG32_SOC15`, `WREG32_SOC15`, and related offset/base-index forms used elsewhere in the AMDGPU driver.

## Control Flow

There is no runtime control flow in this file. Including the header makes its symbolic constants available to compilation units.

The effective control flow happens in consumers:

1. A driver source includes `mmhub/mmhub_9_1_offset.h` and usually `mmhub/mmhub_9_1_sh_mask.h`.
2. Driver code passes a macro such as `mmVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32` to SOC15 register helpers.
3. The helper combines the selected hardware IP block, instance index, register offset, and base-index metadata to perform an MMIO read/write or to build a register whitelist/debug table entry.
4. Bit fields are interpreted with masks/shifts from the corresponding `sh_mask` header.

Because the constants are compile-time values, the compiler substitutes them directly. No symbol is emitted by this header itself.

## State and Persistence Behavior

The header itself has no memory, persistence, initialization, teardown, locking, or side effects. Its constants identify hardware registers that do hold device state. Important state surfaces represented by the offsets include:

- VM context enablement and page-table base/start/end registers, which determine GPU virtual-address translation.
- TLB invalidation request/acknowledge/semaphore registers, which synchronize page-table changes with MMHUB translation caches.
- L2 and ATC control/status registers, which affect translation/cache behavior.
- Protection fault status and fault-address registers, which persist fault information until handled or overwritten according to hardware semantics.
- Power/deep-sleep, clock-gating, memory-power, and state-save registers, which participate in suspend/resume, power management, and reset flows.
- SR-IOV and virtualization registers for framebuffer offsets, VF ATS controls, and shared VM/IOMMU behavior.

Persistence is therefore hardware-managed. Driver writes through these offsets persist in the MMHUB register file until reset, power transition, firmware/hardware intervention, or another driver write changes them.

## Dependencies

Direct dependencies are minimal:

- C preprocessor support for include guards and macro definitions.
- The AMDGPU SOC15 register access convention, where register offset macros and `_BASE_IDX` macros are consumed together.
- The matching `mmhub_9_1_sh_mask.h` for bit fields.
- Hardware documentation or generated register database consistency for MMHUB 9.1.

This file does not include other headers and does not depend on Linux kernel types.

## Integration Points

Observed in-tree direct includes include:

- `drivers/gpu/drm/amd/amdgpu/vcn_v1_0.c`, which includes this MMHUB offset header alongside VCN 1.0 offsets, SOC15 helpers, and `mmhub_9_1_sh_mask.h`. In that compilation unit, these definitions support register naming/whitelisting and MMHUB-related register access needed by VCN-era hardware.
- `drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`, which includes this header alongside DCN 1.0, NBIO 7.0, Vega10 IP offset, and MMHUB mask headers. Display resource setup can use these MMHUB register names through the DC register helper infrastructure.

Related MMHUB versions, such as `mmhub_1_0_offset.h`, `mmhub_2_0_0_offset.h`, `mmhub_2_3_0_offset.h`, `mmhub_9_3_0_offset.h`, and `mmhub_9_4_1_offset.h`, provide similar maps for other ASIC generations. Version selection is significant: offsets and base indexes differ between generations, so consumers must include the header matching the target IP version.

## Risks and Maintenance Concerns

- Offset correctness is critical. A single wrong numeric offset can make the driver read or write the wrong MMIO register, causing hangs, page faults, display/VCN failures, power-management breakage, or data corruption.
- Register generation drift is easy to miss. This file has no type checking beyond macro existence, so mismatches between the offset header and `mmhub_9_1_sh_mask.h` may compile but manipulate incorrect bit fields.
- Cross-generation copy/paste is risky. Similar register names appear in other MMHUB versions with different offsets or base indexes. Porting code between versions must not assume this file's numbers apply elsewhere.
- Reserved registers are explicitly named in the DAGB region. Consumers should avoid treating reserved offsets as safe programmable surfaces unless hardware documentation says otherwise.
- The MMHUB VM context and invalidation registers are central to GPU virtual memory correctness. Reordering or misaddressing those accesses can leave stale translations active or configure page-table apertures incorrectly.
- All `_BASE_IDX` values are `0` in this map. That is a property of this version, not a general rule for other generated MMHUB headers.

## Test and Validation Signals

Useful signals for this file are mostly compile-time and hardware-integration oriented:

- Build coverage for the AMDGPU configurations that include VCN 1.0 and DCN 1.0 paths should fail quickly if a consumed macro is missing or renamed.
- Register-access tests or boot logs on MMHUB 9.1 hardware should show successful MMHUB initialization, VM context programming, TLB invalidation, display bring-up, and VCN operation.
- GPU virtual memory stress tests, page-table update tests, VM fault handling tests, and suspend/resume tests are high-signal because they exercise the most safety-critical register families represented here.
- Display tests on DCN 1.0 hardware and video decode/encode tests on VCN 1.0 hardware provide integration coverage for the observed direct include sites.
- Debugfs/register dump comparison against vendor register specs or known-good kernels can validate that symbolic names resolve to expected offsets.
- Static checks can compare one-to-one presence of `mm*` offset macros with their `_BASE_IDX` companions and compare register names against the matching `mmhub_9_1_sh_mask.h`.

## Summary

`mmhub_9_1_offset.h` is a hardware contract header rather than executable code. It maps the MMHUB 9.1 register file into symbolic C preprocessor constants used by AMDGPU SOC15 register helpers. Its core value is precise naming and offset stability across VM translation, TLB invalidation, MMHUB arbitration, power management, performance counter, IOMMU, framebuffer aperture, and virtualization-related register spaces. The main engineering risk is silent hardware misprogramming if offsets, base indexes, or paired mask definitions drift from the actual ASIC register specification.
