# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 2671-4989

## Scope

This chunk is part of AMDGPU's generated NBIO 4.3.0 register offset header. It contains C preprocessor `#define` constants for NBIF/BIF PCIe configuration-space and NBIO decoder MMIO addresses. It is declarative hardware metadata: there are no C functions, structs, enums, variables, locks, allocation paths, executable control flow, or software persistence routines.

The covered range starts in the tail of the `cfgPSWUSCFG0_0_*` PCIe capability/configuration window, then contains:

- The complete root-complex config-space block `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` at base `0xfffe10100000`.
- Endpoint physical-function config-space blocks for `EPF0`, `EPF1`, `EPF2`, and `EPF3` at bases `0xfffe10200000`, `0xfffe10201000`, `0xfffe10202000`, and `0xfffe10203000`.
- NBIF/BIF system, downstream, endpoint, PF/VF, RCC, strap, GDC, SUM, and shadow-register decoder blocks around `0x30200000`, `0x100000`, and `0xfffe30000000`.
- Complete SR-IOV virtual-function config-space offset blocks for `EPF0_VF0` through `EPF0_VF10` at bases `0xfffe10300000` through `0xfffe1030a000`.
- The beginning of `EPF0_VF11`, ending at `cfgBIF_CFG_DEV0_EPF0_VF11_0_BASE_ADDR_4`.

Although this repository path is under a local `ceph-client` source mirror, this file is AMD GPU PCIe/NBIO register metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The header gives symbolic names to absolute or bus-relative NBIO 4.3.0 register addresses so AMDGPU code can avoid hard-coded magic offsets when accessing PCIe configuration registers, NBIF control/status registers, MSI-X tables, strap registers, doorbell apertures, mailbox registers, scratch registers, and virtualization-related decoder windows.

The macro families in this chunk follow a hardware-address map pattern:

- `cfgPSWUSCFG0_0_*` covers PCIe switch/upstream-style capability registers such as multicast, LTR, ARI, data-link feature, 16 GT/s PHY, lane equalization, lane margining, and 32 GT/s link registers.
- `cfgBIF_CFG_DEV0_RC0_*` covers a root-complex PCI bridge configuration image, including standard PCI header fields, bridge windows, PCIe capabilities, MSI, vendor-specific capabilities, virtual channels, device serial number, AER, secondary PCIe, ACS/PASID/MC/LTR/ARI, data-link feature, 16 GT/s, lane margining, and 32 GT/s registers.
- `cfgBIF_CFG_DEV0_EPF<n>_0_*` covers endpoint physical-function config spaces. `EPF0` is the richest block in this range and includes SR-IOV, resizable VF BAR, ACS, PASID, multicast, LTR, ARI, power budgeting, dynamic power allocation, lane equalization, lane margining, and 16/32 GT/s offsets. `EPF1` through `EPF3` expose smaller repeated endpoint function layouts with PCI/PCIe, MSI/MSI-X, vendor-specific, AER, BAR, power/DPA, ACS/PASID, and ARI subsets.
- `cfgBIF_CFG_DEV0_EPF0_VF<n>_0_*` covers per-virtual-function PCI configuration windows for SR-IOV VFs. Each full VF block in this chunk has 78 offsets, from standard identity/header/BAR registers through PCIe capability, MSI/MSI-X, vendor-specific extended capability, AER logs, and ARI capability/control registers.
- `cfgPCIE_*`, `cfgBIF_*`, `cfgRCC_*`, `cfgDN_PCIE_*`, `cfgEP_PCIE_*`, `cfgNGDC_*`, `cfgSUM_*`, `cfgSHADOW_*`, and related names cover direct NBIF/RCC/GDC/SUM decoder registers used for indirect access, scratch state, link control, resets, interrupts, doorbells, HDP coherency flush/invalidate, mailbox transport, GPUIOV regions, peer address ranges, bus numbering, MSI-X vectors, strap configuration, and shadowed bridge/window state.

These constants are the address side of the generated register contract. Companion `*_sh_mask.h` headers define bit positions and masks for fields inside the registers named here.

## Important APIs, Types, and Functions

There are no C APIs, type declarations, or functions in this chunk. The interface is the macro namespace itself.

Important offset groups:

- PCI/PCIe config header offsets: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class-code bytes, cache line, latency, header, BIST, BARs, ROM BAR, capability pointer, interrupt line/pin, bridge bus/window registers for `RC0`, and endpoint/VF BAR/config fields.
- PCIe capability offsets: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, version-2 device/link capability/control/status registers, and root/slot-specific registers where present.
- Interrupt offsets: MSI and MSI-X capability registers in config space, plus RCC GFX MSI-X vector registers `cfgRCC_DEV0_EPF0_GFXMSIX_VECT[0-3]_*` and `cfgRCC_DEV0_EPF0_GFXMSIX_PBA`.
- Error/reporting offsets: PCIe AER uncorrectable/correctable status, masks, severity, capability/control, header logs, TLP prefix logs, `cfgBIF_BX_PF_BIF_ATOMIC_ERR_LOG`, `cfgRCC_ERR_INT_CNTL`, and `cfgRCC_DEV0_EPF0_RCC_ERR_LOG`.
- Link and PHY offsets: data-link feature registers, 16 GT/s and 32 GT/s link capability/control/status, lane equalization and margining registers, endpoint/downstream link control registers, speed controls, and LTR controls.
- Virtualization and isolation offsets: SR-IOV capability/control/status and VF BAR registers in `EPF0`, ACS/PASID/ARI registers, GPUIOV region and function identifier registers, VF config-space windows, BME status, PF/VF transaction-pending registers, and PF/VF mailbox registers.
- Addressing, aperture, and coherency offsets: NBIF GFX address LUTs, peer FB offsets, config aperture sizing, XDMA address registers, doorbell aperture registers, HDP coherency flush/invalidate controls, and shadowed PCI bridge window registers.
- Firmware/driver communication offsets: SBIOS, BIOS, driver, and firmware scratch registers, mailbox transmit/receive dwords, mailbox control/interrupt registers, and `cfgBIF_BX_PF_BIF_VMHV_MAILBOX`.

Consumers normally combine these offsets with AMDGPU register-access helpers and generated shift/mask macros. The file itself does not prescribe access width, ordering, read/write permissions, or side-effect behavior.

## Control Flow

This chunk has no runtime control flow. Inclusion is governed by the full file's header guard outside this slice. At compile time, any source file that includes `nbio_4_3_0_offset.h` receives these macro constants.

The runtime flow is implemented by consuming driver code:

1. Select an NBIO 4.3.0 offset macro for the relevant PCIe config, NBIF, RCC, GDC, SUM, shadow, PF, or VF register.
2. Read or write through AMDGPU's SOC15, PCIe, indirect-index, or MMIO helper path.
3. Use companion shift/mask definitions when decoding or composing register values.
4. Poll hardware-owned status, program config/control bits, clear sticky errors according to register semantics, or expose decoded state to PCIe, interrupt, reset, virtualization, or RAS paths.

The repeated endpoint and VF blocks imply table-like hardware layout, but this header does not implement iteration. Any loop over functions or VFs is performed by higher-level code that selects the correct generated symbol or computes the appropriate config-space access path.

## State and Persistence Behavior

This header stores no software state and persists nothing to disk. The state represented by these offsets lives in GPU NBIO hardware registers, PCI/PCIe configuration space, firmware-programmed straps/scratch registers, and host/guest PCI configuration policy.

Configuration state represented in this range can persist until reset, function-level reset, hot reset, suspend/resume, GPU power transition, or explicit driver/firmware reprogramming. Examples include PCI command bits, BARs and bridge windows, MSI/MSI-X programming, link controls, DPA/power-budget controls, ACS/PASID/ARI/SR-IOV controls, doorbell aperture setup, HDP coherency controls, config aperture sizing, peer FB offsets, bus-number lists, and address LUT entries.

Other represented registers are volatile status, diagnostic, or mailbox state: link status, AER status and logs, transaction-pending indicators, interrupt status, scratch registers, mailbox buffers, MSI pending bits, lane error/equalization/margining status, GPUIOV identifiers, and reset-related state. The offset header does not encode whether individual fields are read-only, write-one-to-clear, self-clearing, sticky, firmware-owned, guest-owned, or power-gated; callers must rely on the hardware programming guide, PCIe specification semantics, and companion field metadata.

The VF config-space blocks are especially tied to SR-IOV lifecycle. PF setup, VF enable/disable, guest driver programming, FLR, host PCI core policy, IOMMU/ATS state, and virtualization firmware can all change the underlying registers independently of this header.

## Dependencies and Integration Points

The direct dependency is AMD's generated NBIO 4.3.0 register database. This offset header must remain synchronized with sibling NBIO generated headers, especially `nbio_4_3_0_sh_mask.h`, where per-register field shifts and masks are defined.

Known source integration includes SMU 13 power-management code that includes `nbio/nbio_4_3_0_offset.h`. Broader AMDGPU integration points include:

- NBIO and PCIe register access paths that use `cfg*` constants for config-space and MMIO-style register addressing.
- Linux PCI/PCIe enumeration and capability handling for standard config header, bridge window, PCIe capability, MSI/MSI-X, AER, ACS, PASID, LTR, ARI, DLF, 16/32 GT/s, and lane margining/equalization registers.
- SR-IOV and virtualization paths that expose or manage PF/VF config windows, VF BAR sizing, VF device IDs, function identifiers, GPUIOV regions, BME/transaction status, guest/host isolation controls, and PF/VF mailbox traffic.
- Interrupt delivery paths using MSI/MSI-X config-space offsets, RCC GFX MSI-X vector tables, interrupt control/status registers, and mailbox interrupt controls.
- Reset, power, and link-management paths using link controls, speed controls, BACO controls, reset enable/control registers, DPA/power-budget offsets, CLKREQ/PERST/WAKE/VAUX pad controls, and LTR controls.
- RAS/error-handling and diagnostics using AER status/log offsets, atomic error logs, RCC error logs, lane error status, TLP prefix/header logs, and scratch/mailbox registers.
- Address translation and coherency paths using PASID/ACS/ARI/SR-IOV offsets, NBIF address LUTs, peer FB offsets, XDMA registers, doorbell apertures, and HDP flush/invalidate controls.

Because the constants are untyped integer literals, missing or renamed macros typically produce build failures, while incorrect numeric addresses can compile cleanly and cause accesses to the wrong hardware register.

## Risks and Edge Cases

- Chunk boundaries are partial. The first line is already inside the `cfgPSWUSCFG0_0` block, and the last line stops early in `EPF0_VF11`. Adjacent chunks are required before making complete-file or complete-block claims for those two blocks.
- Generated address drift is the primary risk. If an offset diverges from the NBIO 4.3.0 register source, downstream code may read or write a valid but wrong hardware register.
- The range mixes config-space-like absolute addresses such as `0xfffe10200000`, normal MMIO-style addresses around `0x30200000`, SUM indirect access offsets around `0x1000e0`, and small PF1 index/data offsets at `0x0`, `0x4`, and `0x18`. Consumers must use the correct access path for each address space.
- Repeated PF and VF blocks are hard to audit manually. Off-by-one function numbers, base-address strides, or copy-generation mistakes may only appear when the affected function or VF is instantiated.
- Some symbols intentionally alias the same address because PCI layouts overlay 32-bit and 64-bit forms, for example MSI message data and MSI address/high or MSI mask/pending aliases. Consumers must interpret the alias according to capability state and access width.
- Link-control, lane-margining, equalization, 16/32 GT/s, DPA, power-budget, reset, and BACO registers are hardware-state sensitive. Incorrect writes can cause link retraining failures, enumeration failures, hangs, or power-management regressions.
- Error and AER registers can be sticky or write-one-to-clear. Reading or writing through the wrong offset can lose diagnostic evidence or mask serious PCIe errors.
- SR-IOV, ACS, PASID, ARI, GPUIOV, and mailbox registers are isolation-sensitive. Wrong offsets can break VF discovery, DMA address translation, guest interrupt delivery, or host/guest isolation.
- Scratch, strap, and shadow registers may be firmware-owned or latched from boot-time configuration. Treating them as ordinary driver-owned storage can conflict with firmware expectations.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU configurations that include `nbio_4_3_0_offset.h`, especially SMU 13 and NBIO/PCIe paths; missing macro names or duplicate definitions should fail at compile time.
- Run generated-header consistency checks against the authoritative NBIO 4.3.0 register database, including address-block base checks, monotonic-offset checks, expected PF/VF stride checks, and offset-to-shift/mask pairing checks against `nbio_4_3_0_sh_mask.h`.
- Compare repeated endpoint and VF config-space blocks for expected structural identity and expected differences: `EPF0` has SR-IOV/VF-resize/multicast/LTR/lane-margining breadth, while `EPF1` through `EPF3` and VF blocks are smaller repeated images.
- Boot affected AMD hardware and verify PCI enumeration, bridge/window setup, BAR sizing, MSI/MSI-X capability traversal, AER capability traversal, and PCIe link capability/status reporting.
- Exercise SR-IOV configurations that instantiate VFs 0 through 11; validate VF config-space reads, BAR sizing, VF device IDs, bus mastering/memory enable behavior, FLR/reset, ARI routing, and isolation-relevant ACS/PASID behavior.
- Exercise interrupt delivery through MSI/MSI-X and RCC GFX MSI-X vector registers; lost interrupts, stuck pending bits, or unexpected masking can indicate offset mismatches.
- Run PCIe link and power-management tests covering ASPM/LTR, DPA/power-budget, 16 GT/s and 32 GT/s capability/status, lane equalization, lane margining, BACO/reset, and suspend/resume transitions.
- Use AER fault observation or injection where available to validate correctable/uncorrectable status, masks, severity, header logs, TLP prefix logs, and recovery behavior.
- Validate mailbox, doorbell, HDP coherency, peer-address, address-LUT, and GPUIOV paths under virtualization or multi-function workloads, since these registers are concentrated in the NBIF/RCC decoder portion of the chunk.

## Chunk-Specific Notes for Merge

This chunk should be merged with adjacent chunks for the final per-file report. Preserve that this slice covers the tail of `cfgPSWUSCFG0_0`, complete `RC0`, complete `EPF0` through `EPF3`, the NBIF/RCC/GDC/SUM/shadow decoder middle section, complete `EPF0_VF0` through `EPF0_VF10`, and the beginning of `EPF0_VF11` through `BASE_ADDR_4`.
