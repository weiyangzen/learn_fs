# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 1-2944

## Scope

This chunk is the opening 2,944 lines of the generated AMDGPU NBIO 6.1 default-value header. It contains the MIT license, the `_nbio_6_1_DEFAULT_HEADER` include guard, and 2,779 preprocessor `#define` constants that name reset/default values for NBIO 6.1 PCIe configuration space, NBIF/RCC registers, GDC/SYSHUB/SION registers, and a small tail of a second RCC downstream-port block. There are no C functions, structs, enums, variables, locks, allocations, loops, or executable statements in this range.

Although the repository root is a `ceph-client` mirror, this file is AMD DRM/AMDGPU ASIC register metadata. The chunk has no direct distributed-filesystem behavior.

## Purpose

`nbio_6_1_default.h` publishes generated reset/default values for the NBIO 6.1 hardware block. Runtime code can include it together with `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h` to compare, initialize, decode, or document NBIO register state. This chunk covers two main regions.

The first region, lines 25-2104, describes PCIe configuration-space defaults:

- `cfgPSWUSCFG0_*` defaults for the PSW upstream-switch configuration decoder, including standard PCI header fields, PCIe capability chain pointers, MSI/SSID, vendor-specific capabilities, VC, AER, secondary PCIe capability, ACS, multicast, LTR, ARI, L1 PM substate, and ESM defaults.
- `cfgBIF_CFG_DEV0_EPF0_0_*` and `cfgBIF_CFG_DEV0_EPF1_0_*` defaults for endpoint functions 0 and 1. These include base BARs, MSI/MSI-X, PCIe BAR capability, power budgeting, Dynamic Power Allocation, ACS, ATS, page-request, PASID, TPH requester, multicast, LTR, ARI, SR-IOV, and AMD GPUIOV vendor-specific mailbox and scheduling register defaults.
- `cfgBIF_CFG_DEV0_SWDS0_*` bridge/downstream-port defaults, including interrupt pin `1`, PCIe capability type `0x62`, link status `0x00002001`, AER masks, VC resource defaults, lane equalization defaults, and ACS defaults.
- `cfgBIF_CFG_DEV0_EPF0_VF0_0_*` through `cfgBIF_CFG_DEV0_EPF0_VF15_0_*` default values for 16 virtual functions. These repeat a compact VF endpoint profile: PCI header defaults, BAR defaults, MSI/MSI-X defaults, vendor-specific capability, AER, ATS, and ARI. Common nonzero defaults include interrupt line `0xff`, PCIe capability pointer `0xa000`, device capability `0x10000000`, device control `0x2810`, link capability `0x11c03`, MSI control `0x80`, AER severity `0x00440010`, correctable-error mask `0x2000`, ATS capability-list pointer `0x2c000000`, and ARI capability-list pointer `0x33000000`.

The second region, lines 2107-2944, describes NBIF, RCC, GDC, SYSHUB, SION, and additional SMN-named defaults:

- Indexed MMIO and PCIe aperture defaults such as `mmMM_INDEX_DEFAULT`, `mmMM_DATA_DEFAULT`, `mmPCIE_INDEX_DEFAULT`, and `mmPCIE_DATA_DEFAULT`.
- Scratch, BIOS scratch, interrupt, GFX MMIO register CAM, and remap defaults in the `SYSDEC` block.
- RCC strap, endpoint, downstream, PF/PF-VF, reset, peer register range, bus-number, XDMA, link, LTR, mailbox, and doorbell aperture defaults.
- BIF defaults for reset enables, clock request pad control, BACO exit timers, VDDGFX address windows, doorbell global apertures, HDP flush remap registers, ring-buffer registers, GPUIOV configuration sizes, and pad controls.
- GDC defaults for SDP port controls, SDMA/IH/MMSCH doorbell ranges, and MSIX vector table defaults.
- SYSHUB direct defaults for clock-domain controls, QoS controls, DMA cache-line controls, clock gating, timers, NIC400 function modifiers, and scratch values.
- SION credit, burst-target, and time-slot defaults for client groups CL0 through CL5, all zero in this chunk.
- GDC reset/RAS defaults, a second `smnBIF_CFG_DEV0_SWDS1_*` downstream-port default set, PF1 mirrored BIF/PF-VF defaults, shadow PCI configuration defaults, and the beginning of `smnRCC_DWN_DEV0_1_*` downstream-port defaults.

## Important APIs, Types, And Functions

There are no callable APIs or C data types here. The public interface is the macro namespace. The macro prefixes encode the access domain:

- `cfg*` names PCI configuration-space defaults for generated config decoders.
- `mm*` names MMIO register defaults used through SOC15 register-offset helpers.
- `smn*` names System Management Network register defaults or SMN-addressed aliases.

The direct in-tree users of this header are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes `nbio_6_1_default.h` with the offset, shift/mask, and SMN headers for NBIO 6.1 runtime code. That file programs and reads registers such as `mmREMAP_HDP_MEM_FLUSH_CNTL`, `mmRCC_DEV0_EPF0_STRAP0`, `mmBIF_FB_EN`, `mmRCC_PF_0_0_RCC_CONFIG_MEMSIZE`, doorbell ranges, interrupt controls, and clock-gating fields through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `WREG32_FIELD15`, `SOC15_REG_OFFSET`, and `REG_SET_FIELD`.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`, which aggregates Vega10 ASIC register headers, including `nbio_6_1_default.h`, for power-management code.

Most macros in this exact chunk are not referenced directly by handwritten C code in the observed tree. They remain part of the generated ASIC register contract and may be used by generated tables, debugging, register-dump comparison, downstream code, or future initialization paths.

## Control Flow

This header has no local control flow. The effective runtime pattern is external:

1. An NBIO 6.1 consumer includes the default, offset, shift/mask, and SMN headers.
2. The consumer selects a register macro namespace appropriate to the access path: PCI config, MMIO, or SMN.
3. The consumer reads or writes hardware using AMDGPU access helpers and applies field masks from `nbio_6_1_sh_mask.h`.
4. Defaults from this file may be used as expected reset values, baseline values before `REG_SET_FIELD` updates, or documentation for hardware state after reset.

The actual ordering rules are in the consuming driver and hardware specification. For example, `nbio_v6_1.c` enables/disables FB access, remaps HDP flush registers, programs doorbell apertures and ranges, configures IH interrupt behavior, and toggles BIF clock gating. This default header only supplies constants and does not enforce any sequencing.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes hardware-visible defaults. Persistence is governed by GPU reset domains, PCI config-space save/restore, firmware initialization, suspend/resume, function-level reset, hot reset, and explicit driver/firmware writes after reset.

The represented state includes PCIe capability-chain state, BAR defaults, MSI/MSI-X defaults, AER masks/severity, lane equalization defaults, ATS/PASID/ARI/SR-IOV capability defaults, GPUIOV mailbox/scheduler defaults, RCC and BIF reset controls, BACO timing defaults, VDDGFX address windows, doorbell apertures, HDP flush remap values, SYSHUB clock/QoS/cache-line defaults, GDC reset/RAS defaults, and SION arbitration/credit defaults. Many defaults are zero, but the nonzero values are meaningful hardware ABI values and should not be treated as filler.

## Dependencies And Integration Points

The direct companion files are:

- `nbio_6_1_offset.h`, which provides the register/config offsets for these names.
- `nbio_6_1_sh_mask.h`, which provides field shifts and masks used to interpret or update values.
- `nbio_6_1_smn.h`, which provides SMN-addressed register names used with PCIE/SMN access helpers.

Broader integration points include AMDGPU NBIO initialization, Vega10 power management, PCIe capability exposure, interrupt/MSI setup, HDP flush remapping for KFD/compute paths, doorbell aperture programming, SR-IOV/GPUIOV virtualization, IOMMU-facing ATS/PASID behavior, AER/RAS reporting, BACO and clock-gating power states, and suspend/resume restore paths.

## Risks And Edge Cases

- Generated default drift can compile cleanly while changing hardware behavior assumptions. A wrong nonzero default can mislead initialization, reset validation, register-dump comparison, or downstream diagnostics.
- Names overlap across access domains. For example, `cfg*`, `mm*`, and `smn*` variants may refer to related hardware concepts but are not interchangeable access paths.
- The assigned chunk ends mid-block at `smnRCC_DWN_DEV0_1_DN_PCIE_RX_CNTL2_DEFAULT`; the rest of that RCC downstream-port block is in the next chunk. The final per-file report should not treat line 2944 as a semantic file boundary.
- PCIe configuration defaults are security- and virtualization-sensitive. Incorrect defaults around ACS, ATS, PASID, ARI, SR-IOV, GPUIOV mailboxes, and VF BAR/MSI state can affect isolation, address translation, function routing, and guest/host boundaries.
- Doorbell and HDP flush defaults are performance and correctness sensitive. Bad doorbell aperture ranges or remap values can break queue submission, interrupts, and CPU/GPU coherency.
- Reset and power-management defaults such as `mmBX_RESET_EN_DEFAULT`, `mmRCC_RESET_EN_DEFAULT`, BACO timers, clock-gating controls, and SYSHUB QoS/cache-line defaults can cause intermittent failures that only appear after suspend/resume, BACO entry/exit, FLR, or heavy DMA traffic.
- Many macros are unused by current handwritten code, so compile-only validation may miss semantic drift. Hardware validation or generated-register database comparison is needed for confidence.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU with Vega10/NBIO 6.1 support enabled. Include-guard damage, duplicate macros, missing macros, or syntax drift should fail compilation in `nbio_v6_1.c` or `vega10_inc.h` users.
- Compare the generated defaults against the authoritative NBIO 6.1 register database, especially all nonzero PCIe capability-chain, AER, VF, SR-IOV/GPUIOV, RCC, BIF, SYSHUB, GDC, and reset defaults.
- Boot affected AMD GPUs and check PCIe enumeration, capability traversal, BAR sizing, MSI/MSI-X setup, link speed/state reporting, and AER masks.
- Exercise SR-IOV or VF paths where available, validating VF config-space defaults, GPUIOV mailbox behavior, ATS/PASID/ARI visibility, and guest isolation.
- Exercise KFD/compute and graphics queue submission to validate doorbell ranges, HDP flush remap registers, interrupt delivery, and BIF transaction-pending behavior.
- Run suspend/resume, BACO entry/exit, FLR, and GPU reset tests to catch persistence and reset-domain mistakes.
- Check power-management and clock-gating paths for regressions in BIF light sleep, medium-grain clock gating, SYSHUB clock gating, DPA/LTR behavior, and BACO timers.

## Chunk-Specific Notes For Merge

This is the first chunk of `nbio_6_1_default.h`. Merge it with later chunks before producing the final per-file research document. Preserve that this slice covers the include guard, PCIe config defaults for PSW/EPF0/EPF1/SWDS0/VF0-VF15, first-instance NBIF/RCC/GDC/SYSHUB/SION defaults, mirrored `smn*` SWDS1 and PF1 defaults, shadow config defaults, and only the beginning of the `smnRCC_DWN_DEV0_1` downstream-port block.
