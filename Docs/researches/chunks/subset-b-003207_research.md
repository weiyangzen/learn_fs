# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 114203-116617

## Purpose

This chunk is a generated AMDGPU NBIO 7.2.0 register field map for the `nbio_pcie0_bifplr2_cfgdecp` address block. It contains 2,415 lines of C preprocessor constants, including 1,080 `__SHIFT` definitions and 1,121 `_MASK` definitions, for PCI/PCIe bridge configuration-space, PCIe extended capability, error-reporting, link-training, lane-margining, ESM, and CCIX fields on the `BIFPLR2_1` root-port instance.

The header is not executable C logic. It is a hardware ABI description: `nbio_7_2_0_offset.h` supplies register addresses and base indices such as `regBIFPLR2_1_PCIE_DPC_STATUS` or `regBIFPLR2_1_PCIE_CCIX_ESM_CNTL`, while this file supplies the bit positions and masks needed to decode or update fields inside those registers.

## Covered Register Areas

- Standard PCI bridge configuration fields: the span begins in the tail of `BIFPLR2_1_SECONDARY_STATUS`, then covers memory/prefetchable/IO aperture windows, capability pointer, ROM base address, interrupt line/pin, bridge control, external bridge control, vendor capability list, adapter subsystem IDs, and power-management capability/status/control fields.
- PCIe capability structure: `BIFPLR2_1_PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS` expose device/link/slot/root support, controls, and live status bits.
- PCIe Capability 2 structure: `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, and slot capability/control/status 2 fields cover completion timeout policy, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, emergency power reduction, equalization phases, target speed/vector settings, retimers, compliance controls, and related status.
- MSI and identity capabilities: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address/data fields, SSID capability, MSI map capability, and vendor-specific enhanced capability headers/payload fields.
- Virtual Channel, serial number, and AER families: VC port/resource capability/control/status registers, device serial-number dwords, AER uncorrectable/correctable status/mask/severity registers, advanced error capability/control, header logs, root error command/status/source ID, and TLP prefix logs.
- Secondary PCIe, ACS, multicast, L1 PM, DPC, and RP PIO: secondary enhanced capability metadata, link control 3, lane error status, per-lane equalization controls for lanes 0-15, ACS capability/control isolation bits, multicast control/address/block/overlay fields, L1 PM substate capability/control/timing fields, DPC capability/control/status/source-ID fields, and RP PIO status/mask/severity/sys-error/exception/log registers.
- Extended speed, data-link, 16GT PHY, margining, and CCIX: ESM capability list/header/status/control and `PCIE_ESM_CAP_1..7`, Data Link Feature capability/status, 16GT PHY capability/link/parity/per-lane equalization controls, PCIe lane margining port/lane control/status for lanes 0-15, CCIX capability/header/ESM/status/control fields, and per-lane 20GT/25GT ESM equalization presets. The chunk ends after `BIFPLR2_1_ESM_LANE_12_EQUALIZATION_CNTL_25GT`; lanes 13-15 and CCIX transaction fields continue in the next source chunk.

## Important APIs, Types, and Functions

This chunk defines no C functions, data structures, enums, storage, or inline helpers. Its only public surface is macro constants:

- `<REGISTER>__<FIELD>__SHIFT`: starting bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: mask covering that field in the register value.

The practical API is indirect. AMDGPU code includes this header with `nbio_7_2_0_offset.h`, reads or writes the relevant NBIO register through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, or `WREG32_PCIE_PORT`, and then applies these constants via `REG_GET_FIELD`, `REG_SET_FIELD`, or explicit mask/shift operations. In this tree, `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` is the direct C include point for both NBIO 7.2.0 offset and mask headers.

## Control Flow

There is no runtime control flow in the header. The effective flow is compile-time substitution:

1. A consumer selects a register address from `nbio_7_2_0_offset.h`, for example `regBIFPLR2_1_DEVICE_CNTL2`, `regBIFPLR2_1_PCIE_UNCORR_ERR_STATUS`, or `regBIFPLR2_1_LANE_7_MARGINING_LANE_STATUS`.
2. The driver reads an MMIO, SMN, or PCIe-port register value using the AMDGPU register access layer.
3. The caller extracts or modifies a field using this chunk's matching shift and mask macros.
4. Writable control fields are written back through the same register access path, subject to PCIe and ASIC sequencing rules.

All sequencing semantics are external to this file. Link training, equalization, lane margining, error logging, DPC containment, L1 PM substate programming, MSI configuration, ACS isolation, and bridge window changes are governed by PCIe specifications, Linux PCI core ownership, firmware policy, and AMD NBIO hardware behavior.

## State and Persistence Behavior

The header itself has no state and persists nothing. The fields describe hardware-backed state in the `BIFPLR2_1` PCIe root-port register block:

- Capability fields report static or firmware-programmed support, such as max payload, FLR, link widths/speeds, ASPM/L1 substate support, AER/DPC/ACS/multicast support, lane margining support, 16GT/20GT/25GT ESM support, CCIX support, and MSI/SSID/vendor capability layout.
- Control fields represent mutable hardware or PCI configuration state, including bridge decode windows, command and bridge controls, PME/MSI controls, PCIe device/link/slot/root controls, VC and ACS controls, L1 PM timers/enables, DPC enables and software trigger, ESM controls, 16GT equalization controls, margining lane commands, and CCIX ESM controls.
- Status and log fields expose live or latched state, including PCI status, link speed/width/training, device/slot/root status, AER corrected and uncorrected error bits, AER header/TLP prefix logs, lane error bits, DPC trigger/source/busy state, RP PIO diagnostics, ESM calibration/current-rate state, data-link feature status, 16GT parity/equalization status, and margining lane results.

Persistence is hardware-defined. Some fields reset on GPU reset, FLR, power transition, or link reset; some configuration fields remain active until rewritten by firmware, the PCI core, or AMDGPU; and many error/status bits may be sticky or write-one-to-clear. This header does not encode those side effects.

## Dependencies and Integration Points

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h` is the required address companion. The matching `BIFPLR2_1` offsets in this region use base index `5`; several symbolic registers share a dword offset because they represent packed 16-bit config-space fields or subfields of a single PCIe capability register.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` includes this generated mask header and demonstrates the normal access model: SOC15/NBIO and PCIe-port reads/writes combined with `REG_SET_FIELD` and masks.
- AMDGPU's SOC15 register infrastructure supplies the access path and device/IP instance selection. This file only names bit layout; it does not decide whether a register should be accessed as PCI config space, SMN, MMIO, or via an indirect PCIE_PORT helper.
- Linux PCI/PCIe subsystems and the PCI Express specification define the semantics of standard PCI bridge fields, PM, MSI, PCIe capability, AER, ACS, multicast, L1 PM substates, DPC, Data Link Feature, PHY 16GT, lane margining, and RP PIO capabilities.
- AMD NBIO 7.2 hardware and generated register databases define ASIC-specific availability, reserved fields, default values, packed offsets, and side effects.

## Risks and Edge Cases

- The work item starts and ends mid-context. It begins with remaining `BIFPLR2_1_SECONDARY_STATUS` masks whose shifts are partly in the previous chunk, and ends before completing the 25GT ESM lane set and before later CCIX transaction fields.
- Register families are highly repetitive across root-port instances and lanes. Mixing `BIFPLR2_1` with another `BIFPLR*_ *` instance, or mixing ordinary PCIe equalization, 16GT equalization, 20GT ESM equalization, 25GT ESM equalization, and margining lane fields can compile but target the wrong hardware bits.
- Packed config-space offsets require the exact field mask. For example, control/status halves often share one dword, and DPC capability/control or status/source-ID definitions can map to the same register address in the offset header.
- `_MASK` does not imply writability. Capability and status fields are defined with masks just like writable controls; writing status/error fields can clear latched errors or trigger side effects.
- Read-modify-write is risky for AER, DPC, RP PIO, lane error, parity, margining, and link status registers because hardware can update them asynchronously and some bits are clear-on-write or sticky.
- Control fields can affect system behavior outside AMDGPU: bridge aperture decode, MSI delivery, DMA isolation through ACS, link speed/training, L1 PM residency, DPC containment, CCIX/ESM operation, and lane margining can influence enumeration, interrupt delivery, power, error recovery, or link stability.
- Full-width fields such as logs or reserved payloads use `0xFFFFFFFFL`, while other fields are 8-bit, 16-bit, or packed sub-dword fields. Consumers must match the access width and preserve reserved bits.

## Test Signals

- Compile AMDGPU NBIO 7.2 code that includes `nbio_7_2_0_sh_mask.h` and `nbio_7_2_0_offset.h`; generated macro name drift should show up as build failures when referenced.
- Static validation that each expected field has a coherent `__SHIFT`/`_MASK` pair, masks align with shifts, and register prefixes in this chunk have matching `regBIFPLR2_1_*` addresses in `nbio_7_2_0_offset.h`.
- Cross-generation comparison against nearby NBIO 7.x mask headers to catch accidental field omissions, lane-index swaps, or incorrect masks in repeated PCIe capability structures.
- Hardware validation on NBIO 7.2 GPUs with PCI config-space dumps, `lspci -vvxxx`, AMDGPU debug register reads, DRM initialization logs, AER/DPC logs, and link-status diagnostics to confirm identity, capability, link, AER, ACS, DPC, L1 PM, DLF, margining, ESM, and CCIX decodes.
- Runtime stress signals from suspend/resume, GPU reset, PCIe link retraining or speed changes, high-throughput DMA, MSI interrupt delivery, AER/DPC error injection or observation, and lane-margining diagnostics. Regressions in these paths are consistent with incorrect masks, wrong shifts, wrong register instance selection, or unsafe handling of side-effectful status/control fields.
