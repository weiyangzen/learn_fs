# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_offset.h

## Purpose

`mmhub_3_0_1_offset.h` is a generated AMDGPU register-offset map for the MMHUB 3.0.1 hardware block. It contains preprocessor data only: each `reg...` symbol names a memory-management hub register and maps it to a register offset, and each paired `..._BASE_IDX` symbol selects SOC15 MMHUB base index `1`. The header is guarded by `_mmhub_3_0_1_OFFSET_HEADER` and exports 828 register-offset macros plus 827 base-index companions.

This file is part of the low-level hardware ABI for AMDGPU memory-hub programming. Consumers combine these offsets with SOC15 register helpers, field masks from the matching `mmhub_3_0_1_sh_mask.h`, and ASIC IP discovery metadata to program GPU virtual memory, GART/system apertures, TLB/cache controls, VM fault handling, invalidation engines, PCIe ATS/IOMMU controls, power management, performance counters, and diagnostic status registers.

## Register Map Contents

The generated address-block comments divide the map into MMHUB sub-blocks:

- `mmhub_dagbdec`, base `0x68000`: `regDAGB0_*` defines data/address gateway bridge controls. It includes read and write client slots `RDCLI0..29` and `WRCLI0..29`, RD/WR IO and GMI controls, address/data max-burst and lazy-timer controls, virtual-channel controls, TLB/data/misc credits, FIFO full/empty status, pending-request status, snoop override controls, SDP arbitration and credit registers, and DAGB performance counters.
- `mmhub_pctldec`, base `0x68e00`: `regPCTL_*` defines power-control and deep-sleep state registers. It exposes MMHUB deep-sleep overrides, slice busy/allow signals, register-save ranges, register engine RAM index/data registers, status, and PCTL performance counters.
- `mmhub_l1tlb_mmutcl1pfdec`, `mmhub_l1tlb_mmutcl1pldec`, and `mmhub_l1tlb_mmutcl1prdec`, bases `0x69600`, `0x69670`, and `0x69690`: L1 TLB status and L1 performance counter configuration/result registers.
- `mmhub_l1tlb_mmvmtlspfdec`, base `0x696c0`: `regMMMC_VM_MX_L1_TLS0_*` defines a large translation-stream window. It covers TLS controls `CNTL0..37`, start/end address low/high pairs for streams `0..37`, invalidation stream/pending registers, L1 protection fault status/address, IOMMU fault status/GVADDR, and a small `regMMVM_L2_SAW_*` walker control area.
- `mmhub_mmutcl2_mmatcl2dec`, base `0x69b00`: `regMM_ATC_L2_*` defines ATC L2 controls, cache data, status, clock-gating, memory light-sleep, and SDP port control.
- `mmhub_mmutcl2_mmvml2pfdec`, base `0x69c00`: `regMMVM_L2_*` defines MM VM L2 cache and fault machinery: L2 control/status, dummy-page fault registers, invalidate control, protection fault controls/status/address/default address, identity-aperture registers, group and bank selection, cache parity, clock control, SAW invalidation and busy state, and L2 mem-power controls.
- `mmhub_mmutcl2_mmvml2vcdec`, base `0x69d00`: VM context and invalidation-engine registers. It includes `regMMVM_CONTEXT0..15_CNTL`, context disable state, 18 invalidation engine semaphore/request/ack slots, per-engine invalidation address ranges, per-context page-table base/start/end address low/high pairs, and per-context PF/VF PTE cache fragment-size controls.
- `mmhub_mmutcl2_mmvml2pldec` and `mmhub_mmutcl2_mmvml2prdec`, bases `0x6a090` and `0x6a0e0`: VM L2 and UTCL2 performance counter control and result registers.
- `mmhub_mmutcl2_mmvmsharedhvdec`, base `0x6a130`: hypervisor-facing shared VM state, represented here by `regMMVM_PCIE_ATS_CNTL`.
- `mmhub_mmutcl2_mmvmsharedpfdec`, base `0x6a340`: PF/shared memory aperture state. It includes NB MMIO and PCI registers, top-of-DRAM and framebuffer offset registers, system aperture default address, VM steering, shared virtualization reset, memory power light-sleep, cacheable DRAM/local sysmem/local FB windows, local FB lock control, UTCL2 clock/busy/harvest controls, active function ID, and grouped return-fault status.
- `mmhub_mmutcl2_mmvmsharedvcdec`, base `0x6a3b0`: virtual-context shared aperture registers for framebuffer location, AGP aperture, system aperture low/high, and L1 TLB control.
- `mmhub_mmutcl2_mmatcl2pfcntrdec` and `mmhub_mmutcl2_mmatcl2pfcntldec`, bases `0x6a400` and `0x6a420`: ATC L2 performance counter results and configuration.
- `mmhub_mmutcl2_mmvml2pspdec`, `mmhub_mmutcl2_mml2tlbpspdec`, and `mmhub_mmutcl2_mmatcl2pspdec`, bases `0x6aa50`, `0x6aa80`, and `0x6aa90`: PSP-controlled translation-bypass, IOMMU, translation-fault, GPUVA VMID translation assist, and ATC L2 IOV mode registers.
- `mmhub_mmutcl2_mml2tlbpfdec`, `mmhub_mmutcl2_mml2tlbpldec`, and `mmhub_mmutcl2_mml2tlbprdec`, bases `0x6aac0`, `0x6ab00`, and `0x6ab20`: L2 TLB status, TMZ control, GPUVA translation-assist request/response, safety credit, and L2 TLB performance counter control/result registers.

## Important APIs, Types, and Functions

This header defines no C functions, structs, enums, or storage objects. Its public interface is the generated macro namespace:

- Register offset macros such as `regMMVM_L2_CNTL`, `regMMVM_L2_PROTECTION_FAULT_STATUS`, `regMMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, `regMMMC_VM_FB_LOCATION_BASE`, `regMMMC_VM_MX_L1_TLB_CNTL`, `regMM_ATC_L2_CNTL`, `regPCTL_CTRL`, and `regDAGB0_RD_CNTL`.
- Base-index macros such as `regMMVM_L2_CNTL_BASE_IDX` and `regDAGB0_RD_CNTL_BASE_IDX`. In this file the generated base index is consistently `1`, so consumers must resolve the offsets against MMHUB base segment 1 rather than segment 0 used by some older MMHUB maps.
- Repeated register families that consumers can address by stride, including VM contexts `0..15`, invalidation engines `0..17`, TLS streams `0..37`, and performance counter slots.

Bit-level programming is intentionally not in this file. Field shifts and masks come from the matching `*_sh_mask.h` header, while reset/default values come from companion generated default headers when present for the ASIC generation.

## Control Flow and Runtime Use

There is no runtime control flow inside the header. Runtime behavior appears when AMDGPU generation-specific MMHUB code includes this file and passes the offsets to register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, and `SOC15_REG_ENTRY`.

Typical control flow built on this register map is:

1. During device initialization, the MMHUB code reads framebuffer location and aperture registers such as `regMMMC_VM_FB_LOCATION_BASE`, `regMMMC_VM_FB_LOCATION_TOP`, `regMMMC_VM_SYSTEM_APERTURE_LOW_ADDR`, and `regMMMC_VM_SYSTEM_APERTURE_HIGH_ADDR`.
2. GART and VM setup programs context page-table base/start/end registers for context 0 and enables or disables VMID contexts through `regMMVM_CONTEXT*_CNTL` and `regMMVM_CONTEXTS_DISABLE`.
3. Cache/TLB initialization writes `regMMMC_VM_MX_L1_TLB_CNTL`, `regMMVM_L2_CNTL*`, ATC L2 controls, and memory power or clock-gating registers to select translation/cache policy.
4. Fault handling enables and reads protection-fault controls and status through `regMMVM_L2_PROTECTION_FAULT_*`, L1 TLS fault registers, IOMMU fault registers, and grouped return-fault status.
5. TLB invalidation setup programs the 18 invalidation engines with address ranges, request bits, semaphores, and acknowledgement polling through `regMMVM_INVALIDATE_ENG*_*`.
6. Power management and diagnostics touch PCTL, DAGB, ATC L2, VM L2, UTCL2, and L2 TLB performance counter registers to validate clock/power gating and collect low-level counters.

The header therefore shapes execution indirectly. A wrong offset compiles cleanly but changes which MMIO register a later read or write hits.

## State and Persistence Behavior

The file itself has only compile-time state. It does not allocate memory, execute code, persist data, or perform I/O. Its macro constants are embedded into the driver at build time.

The hardware state controlled through these offsets is persistent until reset, power-state transition, firmware action, or another driver write. Important affected state includes:

- VMID enablement, page-table roots, page-table ranges, context aperture boundaries, and per-PF/VF PTE fragment sizes.
- GART, AGP, framebuffer, system aperture, local sysmem, local framebuffer, cacheable DRAM, and NB MMIO windows.
- L1 TLB, L2 TLB, ATC L2, UTCL2, and VM L2 cache/TLB policy.
- Protection fault capture, default fault redirection, IOMMU fault reporting, dummy-page fault state, and GPUVA translation assist request/response registers.
- Invalidation engine request/ack/semaphore state used to synchronize page-table updates with hardware.
- PCTL register-save ranges, deep-sleep overrides, light-sleep controls, clock-gating controls, and memory-power controls.
- Hardware performance counters and diagnostic status registers.

Because every exported register in this file has `_BASE_IDX` `1`, the base-index contract is part of the persisted hardware addressing behavior. Accidentally mixing this header with code expecting base index `0` would direct reads and writes to the wrong MMHUB window.

## Dependencies and Integration Points

The header depends only on the C preprocessor, but in practice it is coupled to:

- The generated companion MMHUB 3.0.1 mask/default headers for field interpretation and reset values.
- AMDGPU SOC15 register access macros that translate hardware IP, instance, base index, and offset into MMIO addresses.
- Generation-specific MMHUB implementation files that initialize GART, VM contexts, apertures, TLB/cache policy, fault reporting, invalidation, power gating, and clock gating.
- The broader GMC and VM subsystems, which cache VM hub register offsets for later invalidation, fault reporting, page-table updates, and suspend/resume paths.
- RAS and debug paths that use `SOC15_REG_ENTRY`-style register descriptors for fault, status, EDC/parity, and performance counter collection.
- SR-IOV/virtualization and PSP integration points through shared PF/HV/VC aperture registers, active function ID, translation bypass, IOMMU controls, and IOV mode controls.

The repeated contiguous layout is an implicit dependency. Many AMDGPU MMHUB implementations compute distances between context, invalidation, and page-table-register families rather than naming every register individually.

## Risks and Maintenance Notes

- Offset drift is high impact. Incorrect VM context, page-table, aperture, invalidation, or fault-register offsets can break GPU virtual memory, cause protection-fault storms, hang invalidation polling, corrupt address windows, or prevent the driver from probing the device.
- The `reg` prefix and `_BASE_IDX == 1` pattern distinguish this generation from older `mm`-prefixed MMHUB maps. Cross-generation copy/paste can compile while silently targeting the wrong register layout.
- Repeated families must remain contiguous where consumers rely on stride calculations. A single missing or reordered context, engine, or TLS-stream macro can break loops even if nearby named macros still exist.
- Reserved or diagnostic-looking offsets should not be programmed without hardware documentation. Generated exposure does not imply driver ownership for arbitrary writes.
- PCTL, clock-gating, memory-power, and deep-sleep registers can interact with firmware and runtime power management; unexpected writes can create suspend/resume or idle-state failures that are hard to attribute to a register map change.
- Fault and IOMMU registers are security-sensitive in virtualized or ATS-enabled configurations because they control translation bypass, request routing, default addresses, and fault visibility.
- Manual edits should be avoided unless the same hardware source update also regenerates the matching mask/default headers and any generation-specific implementation code.

## Test Signals

Useful validation for changes involving this header or consumers includes:

- Build AMDGPU with the MMHUB 3.x generation enabled to catch missing or renamed macros in MMHUB, GMC, VM, RAS, and debug code.
- Boot affected ASICs and verify clean probe logs: no early GART setup failures, VM fault storms, invalidation timeouts, or GPU reset loops.
- Exercise VM and GART paths with buffer allocation, command submission, page-table updates, multiple VMIDs, and eviction/migration workloads.
- Stress TLB invalidation by running workloads that remap GPU virtual addresses and checking that invalidation request/ack polling completes for all engines in use.
- Trigger or inspect recoverable VM faults where possible and verify that fault status, address, client ID, and default fault handling are coherent.
- Run suspend/resume and runtime power-management tests to cover PCTL, clock-gating, memory light-sleep, and register-save ranges.
- Collect register dumps or perf counters for DAGB, ATC L2, VM L2, UTCL2, and L2 TLB blocks and compare them with known-good upstream/generated maps for the same ASIC.
- In SR-IOV or ATS-capable environments, run PF/VF smoke tests that cover framebuffer aperture setup, active function ID, IOMMU controls, translation bypass, and GPUVA translation assist registers.
