# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h lines 10474-12730

## Scope

This chunk covers the middle of AMDGPU's generated NBIO 2.3 register offset header. It contains 2,189 preprocessor constants mapping NBIO/BIF PCIe configuration-space register names to absolute config aperture addresses from `0xfffe10100070` through `0xfffe1030c03f`. The chunk is data-only: no functions, structs, control statements, or storage objects are defined here.

The chunk starts inside `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp`, whose base is declared just before the chunk at `0xfffe10100000`, then defines full or partial address blocks for physical endpoint functions and SR-IOV virtual functions:

- `cfgBIF_CFG_DEV0_SWDS1_*`, continuing the downstream/switch-device PCIe configuration block from slot control/status through PCIe 16 GT/s and lane margining registers.
- `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` at `0xfffe10200000`, with a large endpoint function 0 config-space window.
- `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` at `0xfffe10201000`, also large and feature-rich.
- `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` and `epf3` at `0xfffe10202000` and `0xfffe10203000`, with smaller but still extended endpoint-function windows.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp` through `vf11`, each with 79 repeated virtual-function config registers at `0xfffe10300000` plus a `0x1000` stride per VF.
- The beginning of `vf12`, from standard PCI config header registers through `MAX_LATENCY`.

## Purpose

`nbio_2_3_offset.h` is generated hardware metadata for the Navi-era NBIO 2.3 block. This chunk gives AMDGPU and display/power-management code stable symbolic names for PCIe configuration and extended-capability registers exposed through NBIO's BIF config decode path. Consumers can use these constants, usually with the companion shift/mask header, instead of open-coded addresses when programming PCIe capabilities, SR-IOV virtualization state, error reporting, power management, interrupts, and link behavior.

The `cfgBIF_CFG_*` names are especially important because they describe PCI-compatible configuration-space layout rather than ordinary MMIO registers. The low offsets within each base mirror conventional PCI/PCIe config offsets: vendor/device IDs at `+0x00`, command/status at `+0x04/+0x06`, BARs at `+0x10` and onward, capability pointers around `+0x34`, MSI/MSI-X around `+0xa0`/`+0xc0`, AER around `+0x150`, ATS/PASID/SR-IOV/LTR/ARI in extended-capability regions, and lane/equalization or margining controls in later PCIe extended space.

## Important APIs, Types, And Register Families

This header does not define C APIs or types. Its public surface is the set of `#define` register-address constants. The important register families in this chunk are:

- `cfgBIF_CFG_DEV0_SWDS1_*`: downstream port/bridge-style config registers, including slot control/status, MSI, subsystem ID, virtual channel, device serial number, AER status/masks/header logs, secondary PCIe capability, lane equalization, ACS, data-link feature, 16 GT/s capability, and per-lane margining controls.
- `cfgBIF_CFG_DEV0_EPF[0-3]_1_*`: physical endpoint function config windows. Common fields cover PCI header registers, BARs, ROM/capability pointers, MSI/MSI-X, PCIe device/link capability/control/status, AER, ACS/ATS/PASID/LTR/ARI, SR-IOV capability/control/VF BARs, and vendor-specific GPU IOV scheduler controls. EPF0 and EPF1 include broad virtualization and GPU IOV capability ranges; EPF2 and EPF3 are narrower and include dense TPH steering-table entries.
- `cfgBIF_CFG_DEV0_EPF0_VF[0-12]_1_*`: repeated SR-IOV virtual-function config windows. VF0 through VF11 each expose the standard PCI header, selected PCIe capability registers, MSI/MSI-X, vendor-specific registers, AER logs, ATS, and ARI. VF12 begins at the end of the chunk.

Companion generated headers in the same directory are part of the effective API:

- `nbio_2_3_sh_mask.h` supplies field shifts and masks for register names used by NBIO code.
- `nbio_2_3_default.h` supplies reset/default values for many of the same generated register symbols, including the VF ranges represented here.

## Control Flow

There is no local control flow in this chunk. At compile time, C preprocessor expansion substitutes these names into register access macros and address calculations. Runtime control flow is in the consumers:

- `amdgpu/nbio_v2_3.c` includes this offset header with the matching default and shift/mask headers, then programs NBIO and PCIe state via `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
- `amdgpu/mxgpu_nv.c` includes the same NBIO generated headers for SR-IOV mailbox and virtualization paths, using NBIO/BIF mailbox registers and BIF interrupt IDs to coordinate PF/VF events.
- SMU power-management files for Navi10 and Sienna Cichlid include the NBIO 2.3 headers when reading BIF/PCIe strap and power-management state.
- DCN resource files include the offset header so display code can share generation-correct NBIO register names when building resource tables.

The chunk's physical-function and VF config windows are usually reached through the driver's PCIe/NBIO access helpers rather than by branching inside the header. The repeated `0x1000` VF stride and matching register offsets give callers a predictable map if they need to target a specific function or virtual function.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It describes hardware-backed PCIe/NBIO configuration state. Reads from addresses named here observe live device configuration, link state, error logs, MSI/MSI-X programming, SR-IOV VF configuration, and capability structures. Writes to writable registers can persist in hardware until reset, power transition, driver reinitialization, or PF/VF management action.

State represented by these constants includes:

- Link and slot state: device/link/slot control and status, link capability 2, lane error/equalization status, 16 GT/s fields, and margining status.
- Interrupt and message state: MSI/MSI-X message control, address/data, masks, pending bits, tables, and PBAs.
- Error state: AER uncorrectable/correctable error status, masks, severity, capability control, header logs, and TLP prefix logs.
- Virtualization state: SR-IOV capability/control/status, VF counts, VF stride, VF device IDs, supported/system page size, VF BARs, and GPUIOV vendor-specific scheduler regions for physical functions; repeated VF config windows for guest-visible functions.
- Addressing resources: endpoint BARs, ROM BARs, capability pointers, ARI/ATS/PASID capability controls, and LTR capability for power-management interactions.

Because these registers model PCI configuration space, some values may be owned by firmware, host PCI core, PF management firmware, or the hypervisor in SR-IOV mode. Driver writes must respect ownership and access restrictions.

## Dependencies And Integration Points

The chunk depends on AMD's generated ASIC register database staying in sync with the NBIO 2.3 hardware specification. It is guarded by the file-level `_nbio_2_3_OFFSET_HEADER` include guard and is compiled only as part of the larger header.

Primary integration points are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which is the main generation-specific NBIO implementation. It programs PCIe config controls such as LTR, ASPM, link-width workarounds, clock gating, doorbells, HDP flush, and remap behavior using NBIO 2.3 register metadata.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which handles SR-IOV mailbox communication and interrupt setup for Navi virtualized GPUs.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which use NBIO 2.3 constants while deriving PCIe/power features and reading PCIe-related state.
- `drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c` and `dcn303_resource.c`, which include the generation-specific NBIO offset header as part of display resource integration.
- The matching `nbio_2_3_sh_mask.h` and `nbio_2_3_default.h` headers, which must describe fields and defaults for the same register names and addresses.

## Risks

- Address drift is high impact. If any generated constant maps to the wrong config-space address, the driver can read stale state or write a different PCIe/SR-IOV control register than intended.
- The chunk mixes physical-function, downstream-port, and virtual-function config spaces. Confusing `SWDS1`, `EPF*`, and `EPF0_VF*` symbols can cause writes to the wrong function class.
- Several symbols intentionally alias the same address for PCI layout variants, such as MSI high-address/data and mask/pending fields. Consumers must choose the symbol matching 32-bit vs 64-bit MSI interpretation rather than assuming each name is a distinct storage location.
- SR-IOV VF windows are repetitive and easy to update inconsistently. Missing or mis-strided VF entries would mainly surface under virtualization, where PF/VF ownership restrictions can make failures hard to reproduce on bare metal.
- Some config fields are controlled by platform firmware, the Linux PCI core, or the PF/hypervisor. Direct AMDGPU writes outside the expected init/reset paths can fight those owners.
- Build success only proves symbol availability. It does not prove that the generated address map matches silicon or that accesses are allowed in a particular PF/VF mode.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware tests:

- Compile coverage for all current include sites: `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, the SMU11 PPT files, and DCN resource files. Missing or renamed constants should fail at build time.
- Boot an NBIO 2.3 GPU and confirm AMDGPU initializes NBIO without PCIe config access faults, incorrect link setup, or doorbell/HDP remap failures.
- Exercise PCIe power-management paths: ASPM/LTR programming, clock gating/light-sleep toggles, suspend/resume, and link retraining or width reporting.
- Exercise SR-IOV PF and VF environments. Check VF enumeration, mailbox interrupts, MSI/MSI-X setup, VF BAR sizing, and guest-visible PCIe capability reads.
- Inspect PCIe AER and capability behavior with `lspci -vv` and kernel logs, looking for malformed capability chains, unexpected AER errors, or inconsistent MSI/MSI-X state.
- Compare generated offset/default/mask headers against the authoritative ASIC register database when regenerating NBIO 2.3 headers, especially around repeated EPF and VF ranges.
