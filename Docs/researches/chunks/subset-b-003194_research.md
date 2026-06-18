# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 83096-85519

## Purpose

This chunk is a generated AMDGPU NBIO 7.2.0 register field map. It contains 2,165 C preprocessor constants that define bit shifts and masks for fields inside NBIO/PCIe root-port configuration and extended-capability registers. The span starts in the tail of `BIFPLR4_0_PCIE_ESM_STATUS`, covers the rest of the `BIFPLR4_0` extended-speed/data-link/16GT/margining/CCIX field definitions, then enters the `addressBlock: nbio_pcie0_bifplr5_cfgdecp` field map and runs through the beginning of `BIFPLR5_0_PCIE_RP_PIO_STATUS`.

The header is not executable driver logic. It is a hardware ABI description used by AMDGPU register helpers: the sibling `nbio_7_2_0_offset.h` provides register addresses such as `regBIFPLR4_0_PCIE_ESM_CTRL` or `regBIFPLR5_0_PCIE_DPC_CNTL`, while this file provides the field positions and masks needed to extract or update individual bits in those registers.

## Covered Register Areas

- `BIFPLR4_0_PCIE_ESM_STATUS`, `BIFPLR4_0_PCIE_ESM_CTRL`, and `BIFPLR4_0_PCIE_ESM_CAP_1..7`: extended speed mode status, enable bit, supported rates from 8.0 GT/s upward, equalization mode/counter capability, lane/reach/retimer metadata, preset support, lane count, calibration timing, required Tx enablement, crosslink, and related ESM capability fields.
- `BIFPLR4_0_PCIE_DLF_ENH_CAP_LIST`, `BIFPLR4_0_DATA_LINK_FEATURE_CAP`, and `BIFPLR4_0_DATA_LINK_FEATURE_STATUS`: PCIe Data Link Feature capability-list metadata, scaled flow-control exchange support/enablement, and feature exchange status.
- `BIFPLR4_0_PCIE_PHY_16GT_ENH_CAP_LIST`, `BIFPLR4_0_LINK_CAP_16GT`, `BIFPLR4_0_LINK_CNTL_16GT`, `BIFPLR4_0_LINK_STATUS_16GT`, parity status registers, and `BIFPLR4_0_LANE_0..15_EQUALIZATION_CNTL_16GT`: Gen4/16GT capability, control, status, equalization request/completion, local and retimer parity diagnostics, and per-lane downstream/upstream transmit preset fields.
- `BIFPLR4_0_PCIE_MARGINING_ENH_CAP_LIST`, `BIFPLR4_0_MARGINING_PORT_CAP`, `BIFPLR4_0_MARGINING_PORT_STATUS`, and `BIFPLR4_0_LANE_0..15_MARGINING_LANE_CNTL/STATUS`: PCIe lane margining capability, port ready/software readiness/interrupt metadata, sample-reporting capability, independent timing/voltage margin support, and per-lane margin receiver/type/usage/payload fields.
- `BIFPLR4_0_PCIE_CCIX_*`, `BIFPLR4_0_ESM_LANE_0..15_EQUALIZATION_CNTL_20GT`, `BIFPLR4_0_ESM_LANE_0..15_EQUALIZATION_CNTL_25GT`, and `BIFPLR4_0_PCIE_CCIX_TRANS_*`: CCIX capability headers, ESM required/optional/status/control fields, per-lane 20GT/25GT ESM preset controls, and optimized TLP format support/enablement.
- `BIFPLR5_0_VENDOR_ID` through `BIFPLR5_0_EXT_BRIDGE_CNTL`: standard PCI bridge configuration-space fields for identity, command/status, revision/class codes, cache/latency/header/BIST, bus numbering, IO/memory/prefetchable windows, capability pointer, ROM base, interrupts, and bridge-control behavior.
- `BIFPLR5_0_VENDOR_CAP_LIST`, `ADAPTER_ID_W`, `PMI_*`, `PCIE_*`, MSI, SSID, MSI map, vendor-specific, VC, serial-number, and AER families: capability-list metadata, power-management status/control, PCIe device/link/slot/root capability and control/status registers, MSI message fields, virtual-channel controls, serial-number dwords, uncorrectable/correctable error status/mask/severity, AER capability/control, header logs, root error command/status/source IDs, and TLP prefix logs.
- `BIFPLR5_0_PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0..15_EQUALIZATION_CNTL`: secondary PCIe capability metadata, link equalization request fields, lane error bits, and per-lane equalization controls.
- `BIFPLR5_0_PCIE_ACS_*`, `PCIE_MC_*`, `PCIE_L1_PM_SUB_*`, `PCIE_DPC_*`, and the first `PCIE_RP_PIO_STATUS` shifts: Access Control Services isolation fields, multicast routing/address/block/overlay fields, L1.1/L1.2 PM substate timing and enable fields, Downstream Port Containment capability/control/status/source-ID fields, and root-port PIO completion error status shifts.

## Important APIs, Types, and Functions

This chunk defines no C functions, types, variables, or inline helpers. Its public surface is macro-only:

- `<REGISTER>__<FIELD>__SHIFT`: the starting bit for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for the same field in the register value.

The practical API is indirect. Driver code includes this header with `nbio_7_2_0_offset.h`, then passes matching register and field names to AMDGPU macros such as `REG_GET_FIELD` and `REG_SET_FIELD`, or manually combines masks/shifts around values read by `RREG32_SOC15`, `RREG32_PCIE_PORT`, or similar accessors. The direct include points found in this tree are `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` for offset and mask headers, and display resource files that include the offset header for NBIO 7.2 register addresses.

## Control Flow

There is no runtime control flow in this generated header. The effective flow is compile-time substitution:

1. A consumer chooses a register offset macro from `nbio_7_2_0_offset.h`, for example `regBIFPLR5_0_PCIE_DPC_STATUS`.
2. The code reads or prepares a register value through an AMDGPU SOC15/NBIO register accessor.
3. The code extracts or updates a field using this header's matching `__SHIFT` and `_MASK` constants.
4. If the field is writable, the resulting value is written back to the NBIO/PCIe register.

The run-time sequencing rules are outside this file. PCIe capability rules and AMD NBIO hardware define whether a field is read-only, write-one-to-clear, sticky until reset, safe for read-modify-write, or only meaningful after link training, error containment, or margining operations.

## State and Persistence Behavior

The header itself has no state and persists nothing. The named fields describe hardware-backed state in NBIO PCIe root-port blocks:

- Capability fields report hardware or firmware-provided support: ESM data rates, 16GT PHY properties, margining support, CCIX capability, PM/PCIe/MSI/AER/ACS/MC/L1PM/DPC support, and standard PCI identity/class information.
- Control fields represent mutable hardware state: command bits, bridge-control bits, MSI controls, PCIe link/device/slot/root controls, DLF scaled flow-control enablement, 16GT equalization controls, margining lane controls, CCIX/ESM controls, ACS isolation controls, multicast controls, L1 PM substate enables/timers, and DPC controls.
- Status and log fields expose current or latched hardware state: PCI status, link/device/slot/root status, ESM status, DLF status, 16GT parity and equalization status, margining status, AER status and header/TLP prefix logs, DPC status/source ID, lane error status, and RP PIO status.

Persistence is hardware-defined. Some fields reset on GPU reset, FLR, or link reset; some status bits can latch until explicitly cleared; and bridge aperture, power-management, interrupt, ACS, multicast, and DPC settings can remain effective until firmware, the kernel PCI core, or AMDGPU reprograms them.

## Dependencies and Integration Points

- `nbio_7_2_0_offset.h` is the required sibling contract. In the matching offset slice, the relevant `BIFPLR4_0` and `BIFPLR5_0` registers use base index `5`; packed/aliased registers share offsets, for example `BIFPLR5_0_PCIE_DPC_CAP_LIST` and `BIFPLR5_0_PCIE_DPC_CNTL`, or `BIFPLR5_0_PCIE_DPC_STATUS` and `BIFPLR5_0_PCIE_DPC_ERROR_SOURCE_ID`.
- AMDGPU's SOC15 register access layer supplies the actual access path. This header only names fields; callers must choose the correct MMIO/config-space accessor and register width.
- PCI and PCI Express specifications define much of the semantic model: standard config-space bridge fields, PM, MSI, PCIe capability, AER, ACS, multicast, L1 PM substate, DPC, Data Link Feature, 16GT PHY, lane margining, and RP PIO diagnostics.
- AMD NBIO 7.2 hardware defines ASIC-specific availability, default values, packing, reserved bits, and side effects for the generated masks.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` includes this mask header and the offset header. Current exact macro references in C code do not target this chunk's `BIFPLR4_0`/`BIFPLR5_0` field names directly, but the constants are available to NBIO 7.2 code paths and future diagnostics or configuration paths through the same include.

## Risks and Edge Cases

- The chunk starts and ends mid-register context: it begins with two tail fields from `BIFPLR4_0_PCIE_ESM_STATUS` before the `BIFPLR4_0_PCIE_ESM_CTRL` comment, and ends after the first nine shift definitions for `BIFPLR5_0_PCIE_RP_PIO_STATUS`; its masks and later RP PIO fields continue in the following source chunk.
- Generated names are highly repetitive across ports and capability families. Mixing `BIFPLR4_0` with `BIFPLR5_0`, normal equalization with 16GT/20GT/25GT ESM equalization, or lane index fields can silently target the wrong bits.
- Several registers are packed or aliased at the same dword offset in the offset header. Consumers must use the exact field masks from this file rather than assuming each symbolic register is physically independent.
- Read-modify-write around PCIe status/error registers is risky. AER, DPC, RP PIO, parity, lane error, and status bits may have write-one-to-clear, sticky, or hardware-updated behavior.
- Control fields in ACS, multicast, bridge windows, MSI, L1 PM substates, DPC, ESM, CCIX, link training, and lane margining can affect DMA isolation, interrupt delivery, enumeration, power behavior, error containment, or link stability.
- Capability fields do not encode access permissions. A `_MASK` constant exists for read-only and capability-report fields as well as writable controls; callers need PCIe/ASIC rules before writing.
- Masks use a mix of narrow 16-bit fields, 32-bit fields, and full-width `0xFFFFFFFFL` payload/log fields. Access width and value truncation must match the hardware register layout.

## Test Signals

- Build coverage of AMDGPU NBIO 7.2 code that includes `nbio_7_2_0_sh_mask.h` and `nbio_7_2_0_offset.h`; missing or renamed generated macros should fail compilation when referenced.
- Static generated-header validation that every field in this span has a coherent `__SHIFT`/`_MASK` pair where expected, that masks align with shifts, and that register prefixes match names present in `nbio_7_2_0_offset.h`.
- Cross-generation comparison against adjacent NBIO 7.x mask headers for expected repeated structures while preserving NBIO 7.2-specific offsets, field names, and capability coverage.
- Hardware validation on NBIO 7.2 GPUs using PCI config-space dumps, AMDGPU debug register reads, `lspci -vvxxx`, kernel PCIe/AER logs, and DRM initialization logs to confirm identity, capability, link, AER/DPC, ACS, L1PM, DLF, 16GT, margining, ESM, and CCIX fields decode correctly.
- Runtime stress signals from suspend/resume, GPU reset, high-throughput DMA, MSI interrupt delivery, PCIe link retraining/speed changes, AER/DPC error injection or observation, and lane margining diagnostics. Regressions here would be consistent with wrong masks, wrong shifts, or unsafe use of side-effectful status/control fields.
