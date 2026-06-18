# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h lines 2948-5828

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-default header fragment. It contains preprocessor `*_DEFAULT` constants only; there are no functions, structs, enums, allocations, locks, or direct branches. The constants describe reset or hardware-default values for NBIO/BIF PCI configuration-space registers and PCIe extended capability structures.

The range starts in the middle of the `smnBIF_CFG_DEV0_EPF0` physical-function 0 default block and ends in the middle of the `smnBIF_CFG_DEV0_EPF0_VF23` virtual-function block. Within the range there are 2,800 `#define` entries: 206 trailing PF0 defaults, complete PF1/PF2/PF3 blocks, complete PF0 VF0 through VF22 blocks, and the first 46 defaults for PF0 VF23. Adjacent chunks are required to reconstruct the full PF0 and VF23 sections.

Although this repository path is under `distributed-fs/ceph-client`, the source is Linux AMD GPU driver hardware-description data under `drivers/gpu/drm/amd/include/asic_reg/nbio`; it is not Ceph client or filesystem logic.

## Purpose

The chunk provides default values for PCI endpoint functions exposed through NBIO 2.3. Driver code and generated register tooling use these values alongside register address and shift/mask headers to understand the expected reset image of PCI configuration space, PCIe capability chains, SR-IOV/VF capability templates, MSI/MSI-X state, AER logging state, link capability state, and vendor-specific GPU virtualization data.

The constants are not active initialization logic by themselves. They are hardware contract data: each macro names an SMN-visible BIF configuration register and records its default value for this ASIC generation.

## Important Macro Families

`smnBIF_CFG_DEV0_EPF0_*` in this range covers the tail of physical function 0. It includes ACS, ATS, Page Request Interface, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data-link feature, 16 GT/s PHY, lane equalization, PCIe margining, VF resize BAR, and GPU IOV vendor-specific defaults. This is the most virtualization-heavy part of the chunk. Many values are zero, but the capability-list defaults encode the extended capability chain offsets, and several non-zero defaults matter: page request status `0x00000100`, PASID cap `0x00001000`, SR-IOV supported/system page sizes `0x00000553` and `0x00000001`, data-link feature list/header `0x41010025`, per-lane equalization `0x000000f0`, per-lane margining control `0x00009c38`, VF resize BAR1 control `0x00000020`, and GPUIOV offsets `0x0012000c`.

`smnBIF_CFG_DEV0_EPF1_*` is a complete PF1 PCI configuration/default block. It starts with AMD vendor ID `0x1002`, device ID `0xab38`, adapter ID `0xab381002`, header type `0x80`, capability pointer `0x48`, interrupt line `0xff`, and interrupt pin `2`. It carries normal PCI/PCIe capability defaults plus MSI, AER, resize BAR, power budget, DPA, ACS, ATS, page request, PASID, multicast, LTR, ARI, SR-IOV, TPH, DLF, 16 GT/s PHY, per-lane equalization/margining, VF resize BAR, and a large GPUIOV vendor-specific region. PF1 has the largest complete block in this chunk, with 349 defines.

`smnBIF_CFG_DEV0_EPF2_*` and `smnBIF_CFG_DEV0_EPF3_*` are complete secondary physical-function blocks with 191 defines each. PF2 identifies as AMD vendor `0x1002`, device `0x7316`, adapter ID `0x73161002`, class code `0x0c0300` style values (`BASE_CLASS` `0x0c`, `SUB_CLASS` `0x03`, `PROG_INTERFACE` `0x30`), interrupt pin `3`, device capability `0x00000f81`, device control `0x00002810`, link defaults, MSI control `0x86`, AER masks/severity, resize BAR, power budget, DPA, ACS, PASID, ARI, TPH requester, and a 64-entry TPH steering-table default region. PF3 identifies as AMD vendor `0x1002`, device `0x7314`, adapter ID `0x73141002`, base class `0x0c`, subclass `0x80`, interrupt pin `4`, and otherwise follows the same PCIe/MSI/AER/BAR/power/DPA/ACS/PASID/ARI/TPH pattern as PF2.

`smnBIF_CFG_DEV0_EPF0_VF0_*` through `smnBIF_CFG_DEV0_EPF0_VF22_*` are repeated virtual-function templates under PF0. Each complete VF block has 79 defaults. The VF identity fields default mostly to zero, while `ADAPTER_ID` defaults to `0x73101002`, `CAP_PTR` to `0x48`, `PCIE_CAP_LIST` to `0x0000a000`, `PCIE_CAP` to `0x00000002`, `LINK_CAP` to `0x00000d04`, `DEVICE_CAP2` to `0x00010000`, `LINK_CAP2` to `0x0000001e`, `MSI_CAP_LIST` to `0x0000c000`, and `MSI_MSG_CNTL` to `0x00000082`. Each complete VF block includes MSI and MSI-X registers, vendor-specific PCIe capability headers, AER status/mask/severity/log registers, ATS enhanced capability defaults, and ARI placeholders.

`smnBIF_CFG_DEV0_EPF0_VF23_*` begins another VF template but this chunk stops after `MSI_MASK_DEFAULT`. The remaining VF23 MSI, MSI-X, vendor-specific, AER, ATS, and ARI defaults are outside this work item.

## APIs, Types, and Functions

There are no callable APIs or C types in this chunk. The interface is a set of C preprocessor symbols consumed at compile time. Names encode the register path, function identity, capability/register name, and that the value is a default. For example, `smnBIF_CFG_DEV0_EPF2_PCIE_UNCORR_ERR_MASK_DEFAULT` is the default value for PF2's PCIe uncorrectable error mask register.

The companion generated files are required to use these constants meaningfully: `nbio_2_3_offset.h` provides register addresses or offsets, and `nbio_2_3_sh_mask.h` provides bit shifts and masks. The C implementation `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` includes this default header along with those companion headers and uses the NBIO register definitions through AMDGPU access helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `WREG32_FIELD15`.

## Control Flow

This header has no direct runtime control flow. The implicit flow comes from PCIe/NBIO hardware enumeration and driver register programming:

1. Hardware or firmware exposes configuration-space defaults for PFs and VFs after reset.
2. Linux PCI enumeration reads IDs, class codes, headers, BARs, capability pointers, MSI/MSI-X capability records, PCIe link/device capability records, and extended capability chains.
3. AMDGPU NBIO code programs runtime policy for link power management, LTR, doorbells, interrupt handling, clock gating, and reset behavior using the generated offset and shift/mask headers; these defaults describe the expected baseline for the same register space.
4. SR-IOV and VF paths rely on the PF0 SR-IOV capability defaults and the repeated VF templates to expose or validate virtual function config-space state.
5. AER, ATS, ARI, PASID, DPA, TPH, LTR, margining, and 16 GT/s link capability records are interpreted by PCI/AMDGPU code according to the capability-chain defaults.

## State and Persistence Behavior

The state described here lives in GPU hardware configuration registers, PCIe capability registers, status latches, BAR controls, MSI/MSI-X message storage, AER log/status fields, SR-IOV/VF controls, and vendor-specific GPUIOV mailbox or scheduling registers. Many default values are zero because the register is disabled, empty, write-owned by software, or a status/log field that starts clear.

Some defaults represent stable reset identity or topology, such as vendor/device IDs, class codes, adapter IDs, capability pointers, PCIe capability chain entries, link capability values, and TPH table size. Others represent mutable runtime state, such as command/status, BAR values, MSI message address/data/mask/pending fields, AER status/log registers, SR-IOV controls, page request status, margining status, and GPUIOV mailbox/context/scheduling fields.

The header does not enforce persistence, ordering, locking, polling, or clear-on-write behavior. Callers must follow PCIe and NBIO hardware rules when writing registers, especially across reset, FLR, SR-IOV enable/disable, suspend/resume, and virtualization transitions.

## Dependencies and Integration Points

The file depends only on the C preprocessor, but its practical dependencies are the generated NBIO 2.3 offset and shift/mask headers. `amdgpu/nbio_v2_3.c` includes this header as part of the NBIO 2.3 support set, tying the constants to ASIC-specific register access code.

Integration points include:

- PCI enumeration and capability decoding for AMD NBIO 2.3 physical and virtual functions.
- AMDGPU NBIO initialization and power-management code that configures PCIe link control, LTR, ASPM, clock gating, and related strap/capability registers.
- SR-IOV setup and teardown paths that depend on PF0 SR-IOV defaults, VF BAR defaults, VF page-size support, VF capability chains, and repeated VF config-space templates.
- GPU virtualization and GPUIOV flows using vendor-specific headers, interrupt enable/status fields, reset control, hypervisor/VM mailbox dwords, framebuffer partition registers for VF0-VF30, and scheduler dwords for UVD/VCN/GFX engines.
- PCIe error handling through AER status, mask, severity, header log, and TLP prefix log defaults.
- PCIe MSI/MSI-X interrupt setup through message control, address, data, mask, and pending defaults.
- Link training, signal-quality, and high-speed PCIe validation through 16 GT/s capability, lane equalization, and margining defaults.

## Risks

Default-value accuracy is hardware critical. An incorrect identity, class-code, capability-list, BAR-control, or MSI default can change PCI enumeration or cause Linux to bind the wrong driver, size resources incorrectly, miss interrupts, or misread the available PCIe capabilities.

Virtualization fields are isolation-sensitive. Mistakes in SR-IOV, VF resize BAR, ATS, PASID, ARI, page request, multicast, GPUIOV mailbox, framebuffer partition, or scheduler defaults can break VF creation, expose incorrect VF resources, confuse guest-visible config space, or destabilize PF/VF reset flows.

The chunk is highly repetitive. Generation or copy errors are plausible across `EPF1`, `EPF2`, `EPF3`, and especially `VF0` through `VF23` suffixes. Because VF blocks are nearly identical, a single off-by-one suffix or missed value can be hard to see in review while still affecting one VF only.

Range boundaries are a reconciliation risk. This work item begins after PF0's earlier PCI config and capability defaults and ends before VF23 is complete. The merge lane must combine neighboring chunks to avoid treating PF0 or VF23 as complete from this document alone.

Several non-zero values encode capability-chain offsets and capability IDs rather than ordinary scalar configuration. Changing values such as `0x2c000000`, `0x33000000`, `0x41010025`, or `0x4c010027` without matching the generated offset/mask model could corrupt the extended capability list.

## Test Signals

Useful validation is mostly build-time and hardware-facing:

- AMDGPU should compile with `nbio_2_3_default.h`, `nbio_2_3_offset.h`, and `nbio_2_3_sh_mask.h` included by `amdgpu/nbio_v2_3.c` without missing, duplicate, or mismatched macro errors.
- PCI enumeration on NBIO 2.3 ASICs should expose the expected PF1/PF2/PF3 vendor IDs, device IDs, class codes, header types, interrupt pins, BAR behavior, PCIe capability chain, MSI capability, AER capability, resize BAR support, and TPH/DPA/ACS/PASID/ARI/LTR capability visibility.
- SR-IOV tests should create and remove VFs cleanly, verify VF0 through at least VF23 config-space templates, and confirm VF BAR sizing, MSI state, ATS/ARI capability behavior, and GPUIOV resource partition defaults.
- Reset and power tests should include FLR, VF FLR, suspend/resume, D3 transitions, ASPM/LTR programming, and hot reset to catch defaults that interact with status or capability restoration.
- Error-handling tests should confirm AER status/mask/severity/log defaults and TLP prefix log fields behave as expected after injected or observed PCIe errors.
- Link validation should inspect 16 GT/s link capability, lane equalization defaults, and PCIe margining controls/status on hardware that supports those features.
- Generated-header consistency checks should compare this default header against the matching register database so repeated PF/VF blocks, capability-list offsets, and range-boundary blocks are not truncated or shifted.
