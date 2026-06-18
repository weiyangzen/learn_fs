# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 43980-46461

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 shift/mask header. It defines bitfield geometry for PCI/PCIe configuration-space registers in the NBIF/BIF `BIF_CFG_DEV0_EPF*_1` decode namespace. The covered range starts inside endpoint function 4 (`EPF4_1`) at the tail of `LINK_STATUS2`, covers the remainder of the EPF4 capability layout, then covers complete visible endpoint-function blocks for `EPF5_1` and `EPF6_1`, and finally begins `EPF7_1` from standard PCI header fields through `ADAPTER_ID_W`.

The macros do not implement Ceph filesystem behavior despite living under the repository's `ceph-client` source mirror. They are AMD GPU hardware metadata consumed by DRM/AMDGPU code and generated register helpers to encode, decode, or document NBIO PCIe configuration registers.

The chunk contains 2,124 `#define` lines: 1,060 `__SHIFT` macros and 1,064 `_MASK` macros. It also includes three explicit address block comments for `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`, `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp`, and `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`. The source range boundaries are artificial: it begins after the first four `BIF_CFG_DEV0_EPF4_1_LINK_STATUS2` shift definitions and ends before the remaining `BIF_CFG_DEV0_EPF7_1_PMI_*` and later PCIe capability fields.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or typedefs in this slice. The public interface is a large set of C preprocessor constants following the generated form:

- `BIF_CFG_DEV0_EPF<n>_1_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF<n>_1_<REGISTER>__<FIELD>_MASK`

The `<n>` endpoint-function suffix identifies a PCIe endpoint function image under NBIO device 0. The `_1` qualifier distinguishes this generated config-space view from similarly named `_0` or non-suffixed endpoint and virtual-function views elsewhere in the NBIO headers.

Major covered register families:

- `EPF4_1` tail: `LINK_STATUS2`, reserved slot capability/control/status 2 registers, MSI/MSI-X capability registers, SATA capability and IDP registers, vendor-specific enhanced capability, Advanced Error Reporting (AER), BAR enhanced capability, power budget, Dynamic Power Allocation (DPA), ACS, and ARI.
- `EPF5_1`: standard PCI header fields, PM capability, SATA-specific fields, PCIe capability/device/link capability registers, MSI/MSI-X, vendor-specific capability, AER status/mask/severity/logs, BAR enhanced capability, power budget, DPA, ACS, and ARI.
- `EPF6_1`: the same generated endpoint-function layout shape as `EPF5_1`, including PCI header fields, PM/SATA/PCIe capabilities, interrupt capability registers, AER, BAR power sizing, DPA, ACS, and ARI.
- `EPF7_1` prefix: vendor and device IDs, command/status, revision/class/header/BIST, six base-address registers, adapter/ROM/capability pointer, interrupt line and pin, min/max latency, vendor capability list, and writable adapter ID fields.

Representative field groups and their role:

- Standard PCI command/status masks expose `IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `SERR_EN`, `INT_DIS`, `CAP_LIST`, abort/error status bits, and parity reporting bits.
- Identity/resource masks expose vendor/device IDs, revision/class codes, header type, BAR dwords, subsystem adapter IDs, ROM BAR, capability pointer, and legacy interrupt routing fields.
- PM masks expose PME support, power state, PME enable/status, data select/scale, and bus-power bits.
- PCIe capability masks expose device capability/control/status and link capability/control/status fields, including payload size, read request size, relaxed ordering, no-snoop, link speed/width, active state power management, retrain, clock configuration, and link equalization state.
- MSI/MSI-X masks expose enable bits, vector count encoding, 64-bit addressing support, MSI address/data/mask/pending dwords, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- AER masks expose uncorrectable status/mask/severity bits for DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receive overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress block, and TLP-prefix block. Correctable error status/mask fields cover receiver errors, bad TLP/DLLP, replay rollover, replay timeout, advisory nonfatal, correctable internal error, and header-log overflow.
- AER log registers expose `TLP_HDR` and `TLP_PREFIX` full-width 32-bit log payloads.
- BAR enhanced capability masks expose BAR size support and BAR index/total/count/size control fields for BAR1 through BAR6.
- Power-budget and DPA masks expose power-budget data selection, base power, scale, PM state/substate, type, rail, DPA substates, latency indicators, DPA status/control, and eight substate power allocation bytes.
- ACS and ARI masks expose peer-to-peer isolation/redirect capability and control bits, source validation, translation blocking, upstream forwarding, egress-control vector size, ARI next-function number, ARI function-group support, and ARI function-group control.
- SATA-specific masks expose `SBRN`, `FLADJ`, `DBESL_DBESLD`, `SATA_CAP_0`, `SATA_CAP_1`, `SATA_IDP_INDEX`, and `SATA_IDP_DATA`, indicating that these endpoint-function templates include SATA/xHCI-style config-space fields alongside generic PCIe fields.

## Control Flow and Runtime Behavior

This header chunk has no runtime control flow. Including it only makes numeric constants available at compile time. Runtime behavior appears when AMDGPU code combines these masks and shifts with register offsets from the companion NBIO 7.0 address headers and with access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, and `WREG32_FIELD15`.

The typical flow is:

1. Runtime code selects a register address from `nbio_7_0_offset.h`, `nbio_7_0_smn.h`, or an SOC15 register identifier.
2. It reads a 32-bit hardware value from the NBIO or PCIe configuration-space access path.
3. It uses a matching `BIF_CFG_DEV0_EPF*_1_*__SHIFT` and `_MASK` pair to extract a field, or clears and inserts a new field value.
4. If programming hardware, it writes the modified register value back through the AMDGPU register accessor.

The header does not encode sequencing rules. It does not say when to retrain PCIe links, enable MSI/MSI-X, acknowledge AER status, resize BARs, change DPA substates, or enable ACS/ARI. Those policies live in PCI core logic, AMDGPU NBIO code, firmware, platform enumeration, or hardware-specific initialization sequences. This chunk only defines the bit positions those policies rely on.

## State and Persistence

The file itself owns no mutable state, allocates no memory, and persists nothing. The represented state is hardware configuration and status state for NBIO PCIe endpoint-function config images.

Several covered fields are naturally writable configuration state, including PCI command bits, PM status/control, MSI/MSI-X enable and mask fields, BAR control fields, power-budget selection, DPA control, ACS control, and ARI control. Other fields are read-only or status-oriented from a PCIe perspective, such as link status, equalization status, AER status, AER header/TLP-prefix logs, capability IDs, supported sizes, and advertised capability bits. The generated header does not distinguish read-only from writable fields; callers must know the PCIe register semantics and hardware access rules.

Persistence is at the hardware and driver-build level. Reset values are described in `nbio_7_0_default.h`, where matching names such as `smnBIF_CFG_DEV0_EPF4_1_LINK_STATUS2_DEFAULT`, `smnBIF_CFG_DEV0_EPF5_1_*_DEFAULT`, and `smnBIF_CFG_DEV0_EPF6_1_*_DEFAULT` appear. If a mask or shift is wrong, every compiled consumer using that generated macro will continue reading or programming the wrong bits until the header is regenerated and rebuilt.

## Dependencies and Integration Points

This chunk belongs to the NBIO 7.0 generated-register header set:

- `nbio_7_0_sh_mask.h` supplies the field masks and shifts covered here.
- `nbio_7_0_default.h` supplies reset/default values for matching `smnBIF_CFG_DEV0_EPF*_1_*` registers.
- `nbio_7_0_offset.h` and `nbio_7_0_smn.h` supply addressing constants for the broader NBIO 7.0 register set.

Direct in-tree includes of `nbio_7_0_sh_mask.h` include `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. `nbio_v7_0.c` shows the expected integration pattern: it includes `nbio_7_0_default.h`, `nbio_7_0_offset.h`, `nbio_7_0_sh_mask.h`, and `nbio_7_0_smn.h`, then uses SOC15 accessors and field macros for NBIO programming. The specific `EPF4_1` through `EPF7_1` config-space masks may be used directly by register dump/debug paths, platform enumeration helpers, virtualization code, or generated diagnostics even when ordinary display or memory-controller paths do not name them explicitly.

The surrounding PCIe subsystem also matters. MSI/MSI-X, PM, AER, ACS, ARI, BAR sizing, and link-state fields must remain consistent with Linux PCI core expectations and with the hardware's advertised capability chain. Capability-list fields such as `CAP_ID`, `NEXT_PTR`, `CAP_VER`, and extended-capability `NEXT_PTR` make these generated definitions part of the config-space topology exposed to software.

## Risks

- Generated-header drift is the primary risk. A single incorrect mask or shift can cause all consumers to extract or write the wrong bits for PCI command, AER, interrupt, BAR, power, or isolation controls.
- The chunk starts and ends mid-register family. The first four `LINK_STATUS2` shifts for `EPF4_1` are outside the assigned range, and `EPF7_1_PMI_STATUS_CNTL` plus later EPF7 capability registers continue after it. Whole-file research must merge neighboring chunks before making complete conclusions.
- Repeated endpoint-function blocks are easy to cross-wire. `BIF_CFG_DEV0_EPF5_1_PCIE_UNCORR_ERR_STATUS` and `BIF_CFG_DEV0_EPF6_1_PCIE_UNCORR_ERR_STATUS` have the same field layout but refer to different config images. Using the wrong endpoint-function prefix would silently target the wrong function's logical register.
- The `_1` namespace must not be conflated with `_0`, non-suffixed, virtual-function, SMN, or `reg`/`cfg` address namespaces in other generated headers. The same semantic register name can exist in several address domains.
- Full-width masks such as BARs, MSI address high dwords, AER header logs, TLP-prefix logs, and vendor scratch registers are mechanically simple but broad. A caller writing through a full-width mask can overwrite an entire hardware-visible dword.
- Reserved fields such as slot capability/control/status 2 are still exposed as masks. Treating reserved masks as writable feature bits could create undefined hardware behavior.
- AER status and mask/severity registers are safety-sensitive for PCIe error reporting. Incorrect masks can hide link errors, misclassify fatal/nonfatal errors, or corrupt diagnostic logs.
- ACS and ARI fields affect device isolation and routing. Incorrectly programming ACS redirect/forwarding bits or ARI function-group bits can affect peer-to-peer routing, IOMMU expectations, and multi-function enumeration.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus hardware and PCIe enumeration coverage:

- Build AMDGPU users that include `nbio_7_0_sh_mask.h`, especially `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and the SMU10 PowerPlay include path.
- Run a generated-header consistency check that every `BIF_CFG_DEV0_EPF5_1_*` and `BIF_CFG_DEV0_EPF6_1_*` register in this chunk has matching shift/mask pairs and that field names mirror equivalent endpoint-function blocks where expected.
- Cross-check this range against `nbio_7_0_default.h` to confirm matching default entries exist for covered `EPF4_1`, `EPF5_1`, `EPF6_1`, and beginning `EPF7_1` registers.
- Reconcile with neighboring chunks before producing final per-file research: previous chunk contains the start of `EPF4_1_LINK_STATUS2`, and the next chunk contains the rest of `EPF7_1_PMI_STATUS_CNTL` and later EPF7 PCIe capability fields.
- On affected NBIO 7.0 ASICs, validate PCIe enumeration, capability-list traversal, BAR assignment, MSI/MSI-X setup, AER reporting, link training/equalization status, suspend/resume, FLR/reset behavior, and any register dump tooling that decodes `BIF_CFG_DEV0_EPF*_1` fields.
- For virtualization or multi-function scenarios, validate that `EPF5_1`, `EPF6_1`, and `EPF7_1` decode paths remain distinct and that ACS/ARI settings do not break isolation, routing, or function discovery.
