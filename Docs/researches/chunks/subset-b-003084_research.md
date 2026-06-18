# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 39059-41512

## Scope

This chunk is a generated register bitfield header segment for AMD NBIO 7.0 PCIe/NBIF configuration space. It contains 2,095 `#define` entries and 357 register/comment markers. The definitions are all preprocessor constants of the form `<register>__<field>__SHIFT` and `<register>__<field>_MASK`, used by AMDGPU register helpers such as `REG_GET_FIELD()`, `REG_SET_FIELD()`, `WREG32_FIELD15()`, `RREG32_PCIE()`, `WREG32_PCIE()`, and SOC15 offset/index accessors.

The chunk has two major regions:

- Lines 39059-40006 finish the `BIF_CFG_DEV0_EPF0_2_*` PCIe configuration block, beginning mid-way through its BAR capability/control definitions and continuing through SR-IOV and AMD GPU IOV vendor-specific fields.
- Lines 40008-41512 start `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` and define the beginning of the `BIF_CFG_DEV0_EPF1_1_*` PCI configuration block through `BIF_CFG_DEV0_EPF1_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW1`.

## Purpose

The header gives the driver named masks and shift values for fields inside NBIO 7.0 PCI/PCIe configuration registers. The constants make register access code self-documenting and reduce hard-coded bit arithmetic in AMDGPU platform code. The source is not executable and has no functions, types, static storage, or runtime control flow by itself; its behavior is realized when included by C files that read, write, or decode NBIO/PCIe registers.

This particular chunk is centered on PCIe endpoint function configuration. It covers BAR sizing, power budget and dynamic power allocation, link equalization, access/security services, address translation, page requests, PASID, TPH requester, multicasting, latency tolerance reporting, ARI, SR-IOV, and AMD vendor-specific GPU IOV state and mailbox fields. It also begins a second endpoint/function namespace with conventional PCI config header fields, PCIe capabilities, MSI/MSI-X, virtual channels, device serial number, advanced error reporting, BARs, and the same advanced PCIe/SR-IOV/GPU-IOV facilities.

## Important Register Families

### `BIF_CFG_DEV0_EPF0_2_*`

The `EPF0_2` region starts at `PCIE_BAR3_CAP` and includes:

- BAR capability/control registers for BAR3 through BAR6. Each BAR capability exposes `BAR_SIZE_SUPPORTED`; each BAR control exposes `BAR_INDEX`, `BAR_TOTAL_NUM`, and `BAR_SIZE`.
- PCIe power budget extended capability fields: enhanced capability header, data selector, base power, scale, PM state/substate, type, power rail, and system-allocation state.
- PCIe Dynamic Power Allocation fields: DPA capability, latency indicator, status/control, and substate power allocations 0-7.
- Secondary PCIe capability fields including link control 3 and per-lane error/equalization registers for lanes 0-15. Each lane equalization register has downstream/upstream TX preset and RX preset hint fields plus reserved bits.
- Access Control Services: enhanced capability header, ACS capability bits (`SOURCE_VALIDATION_CAP`, `TRANSLATION_BLOCKING_CAP`, P2P redirect/completion/upstream/egress/direct-translated-P2P capabilities), and matching ACS control enables.
- ATS, Page Request Interface, PASID, and TPH requester capability/control fields used by IOMMU/SVM and PCIe requester features.
- Multicast capability/control/address/receive/blocking fields.
- LTR and ARI capability/control fields.
- SR-IOV capability/control/status and sizing/addressing fields: initial/total/current VFs, dependency link, first VF offset, VF stride, VF device ID, supported/system page sizes, VF BAR base addresses 0-5, and VF migration-state array offset.
- AMD GPU IOV vendor-specific extended capability fields: VSEC header, SR-IOV shadow, interrupt enable/status bits for GFX/UVD/VCE completion, hang recovery, FLR-needed, VM-busy transitions, and HVVM mailbox events.
- GPU IOV mailbox and resource accounting fields: `HVVM_MBOX_DW0` through `DW2`, context, total framebuffer, offset layout, per-VF framebuffer ranges for VF0-VF15, UVD/VCE/GFX scheduler dwords 0-8.

### `BIF_CFG_DEV0_EPF1_1_*`

The `EPF1_1` region begins with an explicit address block marker and then defines a separate PCI function's config space fields:

- Standard PCI header fields: vendor/device ID, command, status, revision/program interface/subclass/base class, cache line, latency, header, BIST, base address registers 1-6, adapter ID, ROM base, capability pointer, interrupt line/pin, and min/max latency/grant.
- Power management capability and status/control fields, including PME clock/version, D-state support, PME support, power/data scale/value, PME enable/status, and data select/scale.
- PCIe capability, device capability/control/status, link capability/control/status, device/link capability/control/status 2, and slot 2 placeholders. These fields describe max payload, phantom functions, L0s/L1 latency, role/error reporting controls, relaxed ordering, no-snoop, extended tags, FLR, completion timeout, atomic operations, OBFF, LTR, target link speed, equalization status, and related PCIe link behavior.
- MSI and MSI-X capability fields: capability IDs/pointers, message enable/count, 64-bit and per-vector-mask flags, MSI address/data/mask/pending fields, MSI-X table and PBA BIR/offset fields.
- PCIe vendor-specific capability header and two vendor-specific data registers.
- Virtual channel capability/control/status and VC0/VC1 resource capability/control/status fields.
- Device serial number and Advanced Error Reporting fields: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, and TLP prefix logs.
- BAR capability/control for BAR1-BAR6 and the same power budget, DPA, secondary PCIe, per-lane equalization, ACS, ATS, page request, PASID, TPH, multicast, LTR, ARI, SR-IOV, and GPU IOV groups seen in `EPF0_2`, through `GPUIOV_HVVM_MBOX_DW1`.

## APIs, Types, and Functions

This chunk defines no C APIs, structs, enums, or functions. Its API surface is the macro namespace consumed by AMDGPU code and by other generated register headers. The important contract is macro naming consistency:

- `__SHIFT` constants provide the bit offset for a register field.
- `_MASK` constants provide the positioned mask for the same field.
- The register name segment must match the second argument expected by `REG_GET_FIELD(value, REG, FIELD)` and `REG_SET_FIELD(value, REG, FIELD, field_value)`.
- The register-level address constants are not in this chunk; they are supplied by companion headers such as `nbio_7_0_offset.h` and `nbio_7_0_smn.h`.

Direct include users observed in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. `nbio_v7_0.c` uses the generated NBIO mask/header set for NBIO initialization, PCIe indirect index/data offsets, HDP flush registers, doorbell aperture ranges, clock gating, light sleep, memory controller access, and interrupt handling. `soc15.c` includes the same header set while composing SOC15 IP blocks and PCIe performance/link helpers. The SMU include path exposes the register macros to power-management code.

## Control Flow and Data Flow

There is no local control flow. Downstream control flow is indirect:

1. AMDGPU code selects an NBIO register address through `SOC15_REG_OFFSET(...)`, an SMN address, or PCIe index/data helpers.
2. The driver reads a 32-bit register value, updates fields with the `__SHIFT`/`_MASK` macros, and writes it back; or it reads a value and decodes fields for status/debug behavior.
3. Hardware persists or reports the corresponding PCIe/NBIO state until reset, link retraining, FLR, power transition, firmware action, or another driver/hypervisor write changes it.

Because this chunk includes PCI config capability structures, some fields represent software-visible PCI configuration state rather than normal MMIO-only state. Fields like MSI/MSI-X, command/status, BARs, SR-IOV control, ACS/ATS/PASID/PRI controls, and AER masks/status are externally meaningful to Linux PCI core, IOMMU code, virtualization layers, and platform firmware/hypervisor policy.

## State and Persistence Behavior

The macros have no persistence, but the registers they describe are persistent hardware state for the current device lifetime. Important state classes include:

- Link training and quality state: lane error status, equalization control, link status/control, speed/width fields, and equalization phase/completion bits.
- Address decoding state: standard BARs, enhanced BAR sizing controls, ROM base address, VF BAR base registers, and SR-IOV page-size/stride/offset fields.
- Interrupt routing state: MSI/MSI-X message controls, masks, pending bits, and GPU IOV vendor-specific interrupt enable/status bits.
- Virtualization state: SR-IOV enable/MSE/ARI hierarchy, VF counts, VF migration state array offsets, GPU IOV VF enable/count shadow, VF framebuffer allocations, scheduler dwords, and HVVM mailbox ack/valid bits.
- Error handling state: AER uncorrectable/correctable status, mask, severity, header log, TLP prefix log, and FLR-related vendor reset control.
- IOMMU/SVM-facing state: ACS, ATS, Page Request, PASID, TPH, and multicast capability/control fields.
- Power/link policy state: PM capability/status, power budget data, DPA controls/substates, LTR latency fields, and link control fields.

Some status registers are likely write-one-to-clear or hardware-updated according to PCIe semantics, but this header does not encode access policy. Call sites must rely on the hardware specification, PCI core rules, or existing AMDGPU helpers before writing a mask back.

## Dependencies and Integration Points

This chunk depends on the rest of the generated NBIO 7.0 register set:

- `nbio_7_0_offset.h` for MMIO/config register address constants.
- `nbio_7_0_smn.h` for SMN addresses used by `RREG32_PCIE()`/`WREG32_PCIE()` paths.
- `nbio_7_0_default.h` for reset/default values.
- AMDGPU register helper macros that concatenate `REG__FIELD_MASK` and `REG__FIELD__SHIFT`.

The runtime integration points are broader than the direct symbol references suggest. The fields map to hardware-visible PCIe capability layouts, so any driver, kernel PCI subsystem path, guest VF driver, hypervisor, firmware component, or diagnostic tool that reads/writes the corresponding config space is part of the behavioral contract. The AMDGPU side of that contract appears through NBIO setup (`nbio_v7_0_funcs`), SOC15 device bring-up, power management include paths, interrupt programming, PCIe performance counters, and virtualization support such as SR-IOV/MxGPU.

## Risks

- Field drift from hardware XML/specification would silently corrupt register manipulation because `REG_SET_FIELD()` composes writes from these constants. A wrong mask or shift can affect adjacent reserved or control bits.
- The chunk crosses from `EPF0_2` into `EPF1_1`; copy/paste or generation errors can easily produce a correct-looking macro name in the wrong endpoint/function namespace.
- ACS/ATS/PRI/PASID/SR-IOV fields are security-sensitive. Incorrect masks can weaken DMA isolation, peer-to-peer routing controls, address translation, VF enablement, or VF BAR exposure.
- MSI/MSI-X and vendor-specific interrupt fields are interrupt-routing sensitive. Wrong masks can drop completion/hang/FLR mailbox notifications or produce spurious interrupts.
- AER status/mask/severity fields are reliability-sensitive. Incorrect error masks can hide fatal link/device errors or over-report correctable errors.
- GPU IOV fields are hypervisor/guest contract fields. VF framebuffer ranges, scheduler dwords, HVVM mailbox ack/valid bits, and VF count/enable shadows must line up with firmware and virtualization manager expectations.
- Reserved-bit masks appear in several registers. Call sites must avoid writing arbitrary values through reserved masks unless the hardware programming guide requires it.
- Many fields are duplicated across endpoint/function namespaces. Search/replace use can accidentally mix `BIF_CFG_DEV0_EPF0_2_*` and `BIF_CFG_DEV0_EPF1_1_*`.

## Test and Validation Signals

Useful signals for changes to this chunk are mostly compile-time, boot-time, and hardware/virtualization validation:

- Build AMDGPU configurations that include SOC15/NBIO 7.0 and SMU10 paths; macro name mismatches surface as compile errors in `nbio_v7_0.c`, `soc15.c`, and power-management includes.
- Exercise GPU boot/resume/reset on NBIO 7.0 ASICs and check that NBIO init, HDP flush, doorbells, interrupt setup, clock gating, and light sleep still work.
- Inspect PCI config space with `lspci -vvv` for expected capabilities: AER, ACS, ATS, PRI, PASID, LTR, ARI, SR-IOV, MSI/MSI-X, and vendor-specific GPU IOV capability layout.
- Validate SR-IOV/MxGPU flows: enable VFs, bind guest drivers, verify VF BAR sizing/addressing, VF counts/stride/offsets, mailbox ack/valid transitions, FLR handling, and per-VF framebuffer allocation visibility.
- Validate IOMMU/SVM behavior where ATS/PRI/PASID are enabled, including DMA isolation and page-request behavior.
- Trigger or observe AER and lane/link events where possible; confirm error status, mask, severity, header log, TLP prefix log, lane error status, and link equalization status decode correctly.
- Confirm no generated register-mask changes alter reserved-bit writes in code paths that use read-modify-write helpers.

## Research Notes

This chunk was read as a generated register definition table rather than hand-written logic. The most important source-tree-aligned conclusion is that the chunk is a hardware contract layer: its correctness is measured by whether AMDGPU and PCIe/virtualization code can address the intended NBIO 7.0 fields without bit corruption. The final merged per-file research should correlate this chunk with the adjacent `nbio_7_0_offset.h` address definitions and with neighboring chunks that contain the start/end of the same endpoint-function blocks.
