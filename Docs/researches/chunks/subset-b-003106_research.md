# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 92894-95298

## Purpose

This chunk is an auto-generated AMD NBIO 7.0 register shift/mask slice for PCIe configuration-space fields. It covers the end of the `BIFPLR2_2` root-port configuration decode block, starting inside `BIFPLR2_2_PCIE_VC1_RESOURCE_CAP`, then continues through many `BIFPLR2_2` PCIe extended capabilities. It then starts a new generated address block, `nbio_pcie0_bifplr3_cfgdecp`, and defines the standard and extended PCI/PCIe configuration fields for `BIFPLR3_2` through the `PCIE_DPC_ENH_CAP_LIST` header.

The file does not implement algorithms or direct register I/O. Its public surface is preprocessor constants that let AMDGPU code extract and compose fields from hardware registers using companion register offset/default headers.

## Public Surface In This Chunk

The exported API is a dense set of `#define` macros following the generated pattern:

- `REGISTER__FIELD__SHIFT` for the bit position of a field.
- `REGISTER__FIELD_MASK` for the field mask in the raw register value.

The first lines continue `BIFPLR2_2_PCIE_VC1_RESOURCE_CAP` with virtual-channel resource fields such as `REJECT_SNOOP_TRANS`, `MAX_TIME_SLOTS`, and `PORT_ARB_TABLE_OFFSET`. The chunk then includes `BIFPLR2_2_PCIE_VC1_RESOURCE_CNTL` and `STATUS`, serial-number enhanced capability fields, AER status/mask/severity/control/log fields, secondary PCIe capability fields, per-lane equalization fields for lanes 0-15, ACS, multicast, L1 PM substate, DPC, RP PIO, and ESM register groups.

The new `BIFPLR3_2` block starts at the `// addressBlock: nbio_pcie0_bifplr3_cfgdecp` marker and exposes a root-port style PCI config space. It includes vendor/device IDs, command/status, revision/class-code bytes, bus-number and bridge-window registers, interrupt/bridge controls, PM capability, PCIe capability, MSI/MSI-map and SSID fields, vendor-specific enhanced capability fields, virtual channel resources, serial number, AER, secondary PCIe link/equalization, ACS, multicast, L1 PM substate, and the DPC enhanced capability header.

## Important Register Families

The `BIFPLR2_2` portion is mostly PCIe extended capability coverage. Virtual Channel fields expose traffic-class to VC mapping, port arbitration table load/select state, VC ID, VC enable, and negotiation status. Device Serial Number fields split the serial number into low/high doublewords. Advanced Error Reporting fields cover uncorrectable error status, masks, and severity for DLP, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable AER fields cover receiver, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, correctable internal, and header-log overflow conditions.

The `BIFPLR2_2` logging and root-error groups provide full-width header log and TLP prefix log masks, root error command/status bits, and error source IDs. The secondary PCIe group defines link control 3, lane error status, and uniform lane equalization controls for lanes 0 through 15 with downstream/upstream TX preset and RX preset-hint fields. ACS fields expose source validation, translation blocking, peer-to-peer redirection, upstream forwarding, egress control, and direct-translated P2P capability/control bits.

The `BIFPLR2_2` multicast and power-management groups include multicast group count, enable, base address, receive/block masks, overlay BAR settings, and L1 PM substate support/control fields. The DPC and RP PIO groups expose containment capability/control/status, error source IDs, PIO status/mask/severity/sys-error/exception fields, header logs, implementation-specific logs, and prefix logs. The ESM group defines enhanced capability list fields, ESM headers, status/control bits, and capability registers.

The `BIFPLR3_2` standard PCI/PCIe block maps the bridge-like root-port config space: vendor/device IDs, command/status bits, class code, bus numbers, IO/memory/prefetchable windows, capability pointer, interrupt line/pin, bridge control, PM capability/status-control, PCIe device/link/slot/root capability/control/status fields, and PCIe 2.0 device/link/slot extended capability fields. These macros describe negotiated link speed/width, target speed, retraining controls, ASPM and link disable state, payload/read-request sizes, error-reporting enables, FLR, ARI, AtomicOp, LTR, OBFF, equalization state, slot power/hotplug bits, and root error/status fields.

The `BIFPLR3_2` interrupt and extended capability groups include MSI control/address/data fields, MSI mapping controls, SSID fields, vendor-specific capability headers/data, VC capability/control/status/resource fields, serial-number fields, AER status/mask/severity/log/root-error/source-ID fields, TLP prefix logs, secondary PCIe equalization controls for lanes 0-15, ACS capability/control, multicast controls, L1 PM substate controls, and the DPC enhanced capability list header. The chunk ends immediately before the `BIFPLR3_2_PCIE_DPC_CAP_LIST` field definitions, so DPC capability/control/status detail is expected in the adjacent chunk.

## Control Flow And State

There is no runtime control flow in this slice. The effective flow is compile-time substitution:

1. A translation unit includes `nbio_7_0_sh_mask.h`.
2. Driver code reads or prepares a 16-bit or 32-bit PCI/NBIO register value using a matching address macro from an offset header.
3. The caller applies the generated `*_MASK` and `*_SHIFT` constants to decode or compose an individual field.

The header stores no C state and defines no persistence layer. Persistent state is in the GPU's NBIO PCIe configuration registers and is affected only when code outside this header reads, writes, or clears those registers. Many named fields correspond to hardware state with side effects or externally visible behavior: AER status and masks, root error reporting, VC negotiation, link retraining and equalization, ACS isolation controls, multicast receive/block vectors, L1 PM substate enable/threshold values, DPC control/status, MSI routing, and bridge window configuration.

## Dependencies And Integration Points

This chunk depends on the generated AMD register-header convention. The `_sh_mask` header supplies bit positions and masks; sibling offset headers supply register addresses and base indices; `nbio_7_0_default.h` supplies reset/default values for corresponding `smn...` register names. Spot checks show matching default entries for registers such as `smnBIFPLR2_2_PCIE_VC1_RESOURCE_CAP_DEFAULT`, `smnBIFPLR3_2_VENDOR_ID_DEFAULT`, and `smnBIFPLR3_2_PCIE_DPC_ENH_CAP_LIST_DEFAULT`, and matching offset entries are present in related NBIO offset headers.

The file is included by AMDGPU NBIO and SOC paths, including `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and PowerPlay/SMU support via `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Consumers are expected to use the macros with AMDGPU register access helpers or PCI config-space access paths, not by including this header alone.

The semantic dependencies are the PCI and PCIe specifications for standard configuration headers, PM capability, MSI, PCIe capability, AER, VC, secondary PCIe extended capability/equalization, ACS, multicast, L1 PM substates, DPC, RP PIO, and vendor-specific capability layout. The generated names encode those architectural fields but do not enforce legal combinations or ordering.

## Risks And Maintenance Notes

- The chunk starts mid-register at `BIFPLR2_2_PCIE_VC1_RESOURCE_CAP` and ends at the comment for `BIFPLR3_2_PCIE_DPC_CAP_LIST`; adjacent chunks are required for complete register-family analysis.
- These masks must match the exact NBIO 7.0 hardware definition and the companion offset/default headers. A stale mask can silently corrupt field extraction or program the wrong bit.
- The generated blocks are highly repetitive across `BIFPLR2_2` and `BIFPLR3_2`, especially lane equalization, AER, ACS, VC, multicast, and L1 PM fields. Generation drift is hard to notice in review because the names differ only by port/function prefix or lane number.
- Some status fields are write-one-to-clear or otherwise side-effectful at the hardware level. The presence of a mask does not imply that read-modify-write is safe.
- Control fields for AER, ACS, DPC, VC, MSI, bridge windows, link retraining, equalization, and L1 PM substates can affect isolation, interrupt delivery, error containment, power behavior, and PCIe link stability.
- Masks use C integer constants with `L` suffixes and include full-width values such as `0xFFFFFFFFL`; callers should keep the established AMDGPU register helper types to avoid signedness or truncation surprises.
- Cross-generation comparison shows nearby NBIO generations can change field widths or add fields, so these macros should not be mechanically reused for other NBIO versions without validating the version-specific generated header.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for translation units that include `nbio_7_0_sh_mask.h`, especially `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `smu10_inc.h`.
- Static checks that every field in the slice has a consistent `*_SHIFT`/`*_MASK` pair, that masks are aligned with shifts, and that contiguous multi-bit masks have the expected width.
- Cross-header checks that register names in this chunk have matching address macros in NBIO offset headers and reset/default entries in `nbio_7_0_default.h` where applicable.
- Runtime PCIe config-space validation on NBIO 7.0 hardware: decoded vendor/device IDs, bridge windows, PM state, link speed/width, MSI state, AER masks/status, VC resources, ACS controls, multicast controls, L1 PM substate controls, and DPC capability header should match hardware dumps such as `lspci -vvxxx` and AMDGPU debug register reads.
- Error-path tests that inject or observe AER/DPC/RP PIO conditions and verify the driver decodes, reports, masks, and clears the intended bits without touching unrelated status.
- Link and power-management tests around retrain-link, equalization completion, lane error status, L1.1/L1.2 enablement, common-mode restore time, LTR threshold fields, and wake/PME behavior.
