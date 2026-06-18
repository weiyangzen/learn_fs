# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h lines 11800-14994

## Purpose

This chunk is part of AMDGPU's generated NBIO 2.3 register-default header. It provides compile-time `_DEFAULT` constants for NBIO/NBIF PCIe, BIF, RCC, SR-IOV virtual-function, MSI/MSI-X, GPUIOV, and endpoint configuration registers. The constants are not executable logic; they are the reset/default values paired with the related `nbio_2_3_offset.h` register addresses and `nbio_2_3_sh_mask.h` bit layouts.

The mapped source range contains 2,718 `#define` constants. Most values are zero reset values, with non-zero defaults marking enabled/masked capability bits, PCI capability-list offsets, device/vendor IDs, interrupt defaults, MSI-X vector mask state, doorbell aperture mode bits, PCIe link capability values, lane equalization presets, and GPUIOV layout metadata.

## Important API, Types, And Macro Families

- Header contract: guarded by `_nbio_2_3_DEFAULT_HEADER`; exports only preprocessor constants.
- Per-VF MMIO defaults:
  - `mmBIF_BX_DEV0_EPF0_VF*_..._DEFAULT` appears for the tail of VF23 and then VF24-VF30 / VF0-VF30 blocks in this chunk.
  - `mmRCC_DEV0_EPF0_VF*_..._DEFAULT` covers RCC VF state and four GFX MSI-X vector table entries.
- Config-space per-VF defaults:
  - `cfgBIF_BX_DEV0_EPF0_VF*_..._DEFAULT` and `cfgRCC_DEV0_EPF0_VF*_..._DEFAULT` mirror the VF BIF/RCC defaults for config-access views.
  - `cfgBIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VF*_FB_DEFAULT` reserves per-VF framebuffer assignment fields for VF0-VF30.
- PCIe switch/upstream config defaults:
  - `cfgPSWUSCFG0_1_*_DEFAULT` describes the `nbio_pcie0_pswuscfg0_cfgdecp` PCIe config block, including standard header, PCIe capability, AER, VC, lane equalization, 16 GT, ESM, DLF, margining, CCIX, and related enhanced-capability fields.
- Endpoint function config defaults:
  - `cfgBIF_CFG_DEV0_EPF0_1_*_DEFAULT` is the large EPF0 config image. It includes AMD vendor ID `0x1002`, device ID `0x7310`, PCI/PCIe capability pointers, AER defaults, BAR controls, SR-IOV, ATS, PRI, PASID, ACS, DLF, 16 GT, margining, and GPUIOV fields.
  - `cfgBIF_CFG_DEV0_EPF1_1_*_DEFAULT` begins the EPF1 config image. It includes vendor ID `0x1002`, device ID `0xab38`, a type/multifunction-looking header default `0x80`, interrupt pin `0x2`, and a shorter PCIe capability set.

Representative non-zero defaults in this chunk include:

- VF self-ring doorbell control: `*_DOORBELL_SELFRING_GPA_APER_CNTL_DEFAULT = 0x00000100`.
- VF MSI-X vector controls: `*_GFXMSIX_VECT[0-3]_CONTROL_DEFAULT = 0x00000001`, leaving vector entries masked/disabled until programmed.
- PCI config identity/capabilities: `VENDOR_ID_DEFAULT = 0x00001002`, EPF0 `DEVICE_ID_DEFAULT = 0x00007310`, EPF1 `DEVICE_ID_DEFAULT = 0x0000ab38`, `CAP_PTR_DEFAULT = 0x00000048`, `PCIE_CAP_LIST_DEFAULT = 0x0000a000`, `MSI_CAP_LIST_DEFAULT = 0x0000c000`.
- PCIe link/control defaults: `DEVICE_CNTL_DEFAULT = 0x00002810`, `LINK_CAP_DEFAULT = 0x00000d04` for EPF functions and `0x00011c04` for PSWUSCFG0, `LINK_CNTL2_DEFAULT = 0x00000004`, `LINK_CAP2_DEFAULT = 0x0000001e`.
- AER defaults: `PCIE_UNCORR_ERR_MASK_DEFAULT = 0x00400000` or `0x04400000` for PSWUSCFG0, `PCIE_UNCORR_ERR_SEVERITY_DEFAULT = 0x00440010`, `PCIE_CORR_ERR_MASK_DEFAULT = 0x00006000`.
- Lane defaults: Gen3-style `PCIE_LANE_*_EQUALIZATION_CNTL_DEFAULT` often uses `0x00007f00` or `0x00007f7f`, 16 GT equalization uses `0x000000f0` or `0x000000ff`, and margining lane control uses `0x00009c38`.
- GPUIOV layout: `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_OFFSETS_DEFAULT = 0x0012000c`, with per-VF FB and engine scheduler DW fields defaulting to zero.

## Control Flow

There is no runtime control flow in this header. The effective flow is build-time inclusion:

1. `amdgpu/nbio_v2_3.c` includes `nbio/nbio_2_3_default.h`, `nbio/nbio_2_3_offset.h`, and `nbio/nbio_2_3_sh_mask.h`.
2. Driver code uses offset macros to read/write NBIO registers and mask/shift macros to update fields.
3. `_DEFAULT` constants from this file provide reset/reference values for generated register definitions or code paths that need known hardware defaults.

Within the chunk, register families are ordered by generated address-block comments. VF blocks repeat the same BIF/RCC field pattern across virtual functions, then the source transitions into PCIe config-space blocks for the upstream/switch view and endpoint functions.

## State And Persistence Behavior

The constants model hardware reset/configuration state; they do not store mutable driver state and do not persist across boots. Runtime state is held by the GPU hardware registers, PCI config space, firmware/BIOS initialization, and AMDGPU device structures. Defaults such as MSI-X vector control, doorbell aperture control, AER masks, and PCI capability pointers are baseline values that can be superseded by firmware, PCI enumeration, SR-IOV setup, VF provisioning, interrupt setup, and AMDGPU register writes.

Because many VF fields default to zero, the hardware starts with unprogrammed mailbox buffers, no VF framebuffer assignment, no VF BAR base values, no MSI/MSI-X addresses/data, and no enabled doorbell aperture base until the PF/hypervisor/driver provisions them. Non-zero control defaults indicate reset-time masking or capability advertisement, not necessarily enabled runtime behavior.

## Dependencies And Integration Points

- Direct include integration: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` includes this header with the matching offset and shift/mask headers.
- Register access integration: `nbio_v2_3.c` uses AMDGPU helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `SOC15_REG_OFFSET`, and `REG_SET_FIELD` against NBIO registers whose names are defined by the generated headers.
- PCI subsystem integration: endpoint and upstream config defaults align with Linux PCI enumeration, capability parsing, MSI/MSI-X setup, AER handling, ACS/ATS/PRI/PASID capabilities, BAR sizing, and power-management capability exposure.
- SR-IOV/virtualization integration: the repeated VF0-VF30 BIF/RCC fields, SR-IOV capability fields, GPUIOV vendor-specific header, mailbox registers, per-VF framebuffer fields, and MSI-X vector defaults are the hardware contract used by PF/VF virtualization flows.
- Doorbell/HDP integration: VF and PF BIF doorbell aperture, HDP coherency flush, GPU HDP flush request/done, and mailbox defaults are tied to AMDGPU ring submission, interrupt, KFD, and host-data-path flush programming performed outside this generated header.

## Risks And Edge Cases

- Generated-header drift is the main risk. If a `_DEFAULT` value no longer matches the ASIC register database, the driver may compare against or initialize from stale reset assumptions.
- The chunk has many repeated VF patterns. Mechanical edits can easily alter one VF but not the others, causing asymmetric behavior that may only appear under SR-IOV with specific VF numbers.
- `mm*` and `cfg*` families expose similar register names through different access paths. Mixing config-space defaults with MMIO register offsets can produce incorrect programming.
- Non-zero defaults are semantically loaded. Examples include MSI-X vector control `0x1`, doorbell self-ring control `0x100`, AER masks/severity values, capability-list encodings, and lane equalization presets. Treating them as arbitrary constants can break enumeration, interrupt delivery, link training, or virtualization isolation.
- EPF0 and EPF1 intentionally differ: EPF0 advertises GPUIOV/SR-IOV-oriented fields and device ID `0x7310`; EPF1 advertises device ID `0xab38` and a reduced visible capability set in this range. Code assuming one endpoint layout for all functions would be fragile.
- Most GPUIOV per-VF FB and scheduler fields default to zero, so runtime provisioning code must not infer that a VF is assigned resources merely because the capability exists.

## Test Signals

- Kernel build should compile `amdgpu/nbio_v2_3.c` without macro redefinition or missing-symbol errors when this generated header is included with `nbio_2_3_offset.h` and `nbio_2_3_sh_mask.h`.
- PCI enumeration on NBIO 2.3 ASICs should report AMD vendor ID `1002`, expected EPF0/EPF1 device IDs, valid capability-list traversal, correct MSI/MSI-X capability behavior, and sane AER/ACS/ATS/PRI/PASID exposure for the supported hardware mode.
- SR-IOV validation should create/provision VFs consistently across VF0-VF30: mailbox buffers start clear, per-VF FB fields are zero until assigned, VF MSI-X vectors are masked until programmed, and doorbell/HDP controls are initialized by PF or host logic.
- Interrupt tests should verify MSI/MSI-X setup after the driver writes vector address/data/control fields, since reset defaults intentionally leave vector address/data as zero and controls at `0x1`.
- PCIe link training and power-management tests should catch incorrect `LINK_CAP`, `LINK_CAP2`, lane equalization, DLF, LTR, L1 PM, DPA, and margining defaults through link width/speed, AER error reporting, and suspend/resume behavior.
- Register-database regeneration tests or diffs should flag any change to non-zero defaults in this range, especially `VENDOR_ID`, `DEVICE_ID`, capability-list offsets, AER masks/severity, `GPUIOV_OFFSETS`, SR-IOV page-size values, and lane equalization/margining constants.
