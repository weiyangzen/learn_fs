# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h lines 14995-17881

## Scope

This chunk is part of AMDGPU's generated NBIO 2.3 register-default header. It contains C preprocessor `#define` constants only, with default reset/configuration values for NBIF PCIe configuration-space registers. There are no functions, structs, enums, allocations, locks, or executable branches in this line range.

The range starts in the tail of the `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` address block and ends in the middle of `nbio_nbif0_bif_cfg_dev0_epf0_vf27_bifcfgdecp`. It covers 2,797 default-value macros. Adjacent chunks are required for a complete per-file view of the EPF1 block before line 14995 and the VF27 and later VF blocks after line 17881.

Although this repository path is under a Ceph client tree, the file is Linux AMDGPU hardware-description data for GPU NBIO/NBIF PCIe programming.

## Purpose

`nbio_2_3_default.h` supplies compile-time defaults for NBIO 2.3 registers. The companion headers provide addresses and bitfields: `nbio_2_3_offset.h` maps register names to offsets and base indices, while `nbio_2_3_sh_mask.h` maps register fields to shifts and masks. AMDGPU runtime code includes all three so it can compare against, initialize, restore, or document ASIC-default values without hard-coding raw reset constants at every use site.

This chunk describes default PCI configuration-space images for device 0 endpoint functions and virtual functions:

- The tail of physical function `EPF1`, including secondary PCIe, ACS, ATS, page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data link feature, 16 GT/s PHY, margining, VF resizable BAR, and GPU IOV vendor-specific capability defaults.
- Full physical functions `EPF2` and `EPF3`, including PCI identity/class-code defaults, power-management, PCIe capability, MSI/MSI-X, SATA/USB-like capability fields, AER, BAR, DPA, ACS, PASID, ARI, TPH requester, and TPH steering-table defaults.
- Virtual functions `EPF0_VF0` through `EPF0_VF26` and the beginning of `EPF0_VF27`, each with a compact repeated PCIe VF config-space default image.

## Important Macro Families

The `cfgBIF_CFG_DEV0_EPF1_1_*` tail continues a physical endpoint function. It sets PCIe lane equalization defaults (`0x00007f00` for Gen3-style lane controls and `0x000000f0` for 16 GT/s lane controls), leaves most error/status/capability control registers at zero, and encodes capability-list linkage constants such as ACS `0x2b000000`, ATS `0x2c000000`, page request `0x2d000000`, PASID `0x2f000000`, multicast `0x32000000`, LTR `0x32800000`, ARI `0x33000000`, SR-IOV `0x37000000`, TPH requester `0x40000000`, data link feature `0x41010025`, 16 GT/s PHY `0x44010026`, and margining `0x4c010027`.

The EPF1 SR-IOV and GPU IOV defaults are mostly disabled or zeroed. Notable non-zero values are `PCIE_SRIOV_SYSTEM_PAGE_SIZE_DEFAULT` at `0x00000001`, `PCIE_PASID_CAP_DEFAULT` at `0x00001000`, `DATA_LINK_FEATURE_CAP_DEFAULT` at `0x00000001`, VF resize BAR1 control at `0x00000020`, and GPU IOV offsets at `0x0012000c`. The GPU IOV area includes hypervisor/VM mailbox words, interrupt enable/status, reset control, total framebuffer and per-VF framebuffer slots for VF0-VF30, P2P-over-XGMI enable, and scheduler dwords for UVD, VCE, GFX, and UVD1. Their zero defaults mean the driver or firmware must actively provision virtualization resources before use.

`cfgBIF_CFG_DEV0_EPF2_1_*` describes a physical function with AMD vendor ID `0x1002`, device ID `0x7316`, adapter ID `0x73161002`, class code `0x0c0330`, interrupt pin 3, and multifunction header `0x80`. It has PCIe, PM, MSI, AER, BAR, power budget, DPA, ACS, PASID, ARI, and TPH requester defaults. It also has function-specific USB/SATA-style defaults such as `SBRN`, `FLADJ`, `DBESL_DBESLD`, `SATA_CAP_*`, and `SATA_IDP_*`.

`cfgBIF_CFG_DEV0_EPF3_1_*` is similar to EPF2 but with device ID `0x7314`, adapter ID `0x73141002`, class code `0x0c8000`, interrupt pin 4, and no enabled PM capability bits by default. It repeats the same PCIe, MSI, AER, BAR, DPA, ACS, PASID, ARI, and TPH requester shape, including a 64-entry TPH steering table initialized to zero.

The `cfgBIF_CFG_DEV0_EPF0_VF*_1_*` families define virtual-function config-space defaults for VF0 through VF26 and the start of VF27. Each full VF block contains 82 macros. Common defaults include zero vendor/device IDs, command/status/class fields, BARs, MSI address/data/mask/pending fields, MSI-X table/PBA fields, vendor-specific dwords, AER status/mask/severity/log fields, ATS capability/control, and ARI capability/control. The repeated non-zero defaults are adapter ID `0x73101002`, capability pointer `0x00000048`, PCIe capability list `0x0000a000`, PCIe capability `0x00000002`, link capability `0x00000d04`, device capability 2 `0x00010000`, link capability 2 `0x0000001e`, MSI capability list `0x0000c000`, MSI message control `0x00000082`, vendor-specific extended capability list `0x11000000`, AER extended capability list `0x20020000`, and ATS extended capability list `0x2c000000`.

## Control Flow and State

This header has no direct control flow. The implicit hardware workflow is:

1. ASIC-generated defaults define the reset/configuration image for physical and virtual PCIe functions.
2. Driver code includes this header with the offset and shift/mask headers.
3. Runtime NBIO code reads and writes actual hardware registers through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `WREG32_FIELD15`.
4. PCIe enumeration, SR-IOV setup, VF reset, AER handling, MSI/MSI-X programming, ATS/PASID enablement, TPH steering, BAR sizing, and power-management paths observe or modify the corresponding live registers.

State is persistent in hardware registers, not in this header. The default values represent reset-time or generated baseline state. Runtime state can be changed by the kernel driver, firmware, BIOS/platform code, PCI core, hypervisor, guest VFs, or device reset/power transitions.

Several defaults are intentionally inert. Error status and log fields start at zero, BAR address/control defaults avoid preprogrammed host apertures, MSI/MSI-X message fields are zero until the OS programs interrupts, and most virtualization resource registers are zero until SR-IOV or GPU IOV provisioning occurs. Capability-list dwords are different: their non-zero defaults encode the advertised PCIe extended capability chain and must remain consistent with the offset/header layout.

## Dependencies and Integration Points

The direct dependency is the C preprocessor. The header is guarded by `_nbio_2_3_DEFAULT_HEADER` and is normally included by AMDGPU NBIO 2.3 code alongside:

- `nbio/nbio_2_3_offset.h` for register offsets and base indices.
- `nbio/nbio_2_3_sh_mask.h` for field shifts and masks.
- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes this header and implements the NBIO 2.3 function table.

`nbio_v2_3.c` is the main in-tree runtime integration point. It handles revision ID reads, memory-controller access enablement, memsize reads, SDMA/VCN/IH doorbell ranges, doorbell aperture and self-ring aperture setup, HDP flush remapping, interrupt control, clock gating/light sleep, PCIe index/data offsets, ASPM/LTR programming, link-width workarounds, doorbell interrupt clearing, and MMIO remap selection. This chunk's config-space defaults are not the core fields directly manipulated by most of those helpers, but they are part of the same NBIO 2.3 generated register ABI consumed by that implementation and by PCIe/SR-IOV-facing code.

Broader integration points include Linux PCI enumeration, AMDGPU device discovery, physical-function capability advertisement, virtual-function config-space exposure, hypervisor-mediated SR-IOV, AER diagnostics, MSI/MSI-X interrupt programming, ATS/PASID address-translation features, PCIe link training/status reporting, BAR probing/resizing, and GPU IOV framebuffer/scheduler partitioning.

## Risks

Generated default-value headers are easy to treat as passive data, but incorrect constants can still be high impact. A wrong PCIe capability-list pointer can make the OS or hypervisor parse the wrong extended capability chain. A wrong device/class ID can bind the wrong driver or change how Linux enumerates the function. Wrong MSI/MSI-X defaults can affect interrupt capability discovery. Wrong AER masks or severity defaults can hide or misclassify PCIe errors.

The physical-function defaults encode different function personalities. EPF2 advertises class `0x0c0330` and device `0x7316`; EPF3 advertises class `0x0c8000` and device `0x7314`; EPF1's earlier identity fields are outside this chunk. Copying defaults across EPFs without preserving those distinctions can break function-specific kernel binding and platform assumptions.

The VF blocks are extremely repetitive. Off-by-one generation mistakes in `VF0` through `VF27` names or values would compile successfully while exposing the wrong virtual-function config image. Because the range ends inside VF27, final file-level reconciliation must ensure VF27 is completed and later VFs are covered by adjacent chunks.

Virtualization-facing defaults carry isolation risk. SR-IOV, ATS, PASID, ARI, VF BAR sizing, GPU IOV framebuffer allocation, P2P-over-XGMI enablement, and per-engine scheduling registers affect guest-visible resource assignment and DMA/address-translation behavior. Incorrect defaults or incorrect runtime assumptions based on them can produce guest enumeration failures, stale VF state after reset, DMA isolation problems, or unusable GPU partitions.

Many status and control registers are defaulted to zero because hardware or software fills them later. Tests that only compare against this header can miss runtime-only failures in AER logging, MSI delivery, TPH steering, lane margining, or SR-IOV provisioning.

## Test and Validation Signals

Useful validation is mostly build, enumeration, and hardware integration based:

- Build AMDGPU with NBIO 2.3 support; missing or renamed default macros should fail at include or use sites.
- Boot NBIO 2.3 hardware and confirm `nbio_v2_3_funcs` initializes normally, including doorbells, HDP flush remaps, clock/power setup, ASPM/LTR programming, and MMIO remap selection.
- Inspect `lspci -vvv` for the relevant physical functions and verify vendor/device IDs, class codes, capability pointer chains, PCIe capability versions, link capability/status, MSI/MSI-X capabilities, AER capability, ACS/ATS/PASID/ARI exposure, and TPH requester capability match expectations.
- Exercise suspend/resume, D3 transitions, FLR, and GPU reset paths while checking that capability and AER state is restored or reinitialized correctly.
- On SR-IOV-capable platforms, enable VFs and verify VF0 through VF27 enumerate with the expected config-space image, receive working MSI/MSI-X interrupts if enabled by the stack, and survive guest FLR/reset cycles.
- Validate ATS/PASID/page-request related behavior with IOMMU enabled when those capabilities are advertised or consumed by the platform.
- Use AER injection or platform error reporting to confirm uncorrectable/correctable error masks, severities, header logs, and TLP prefix logs behave according to PCIe expectations.
- For GPU IOV paths, verify framebuffer partitioning, mailbox/reset control, scheduler dwords, and P2P-over-XGMI state are provisioned by firmware/driver before guest use rather than relying on the zero defaults in this chunk.

## Cross-Chunk Notes

This report covers only lines 14995-17881 of `nbio_2_3_default.h`. It starts after the beginning of the EPF1 physical-function config-space defaults and ends before the full VF27 block is visible. The final per-file research document should merge this with neighboring chunks before making complete claims about EPF1, VF27, or the full set of NBIO 2.3 PF/VF default registers.
