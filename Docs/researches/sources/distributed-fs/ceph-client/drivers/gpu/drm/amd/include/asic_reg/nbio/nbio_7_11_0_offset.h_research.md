# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003118`: lines 1-2478, `Docs/researches/chunks/subset-b-003118_research.md`
- `subset-b-003119`: lines 2479-4910, `Docs/researches/chunks/subset-b-003119_research.md`
- `subset-b-003120`: lines 4911-7345, `Docs/researches/chunks/subset-b-003120_research.md`
- `subset-b-003121`: lines 7346-9406, `Docs/researches/chunks/subset-b-003121_research.md`

## Chunk Research

### subset-b-003118: lines 1-2478

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h lines 1-2478

## Scope

This chunk covers the first 2,478 lines of the generated NBIO 7.11.0 register offset header. The complete file is larger; this slice starts at the license/header guard and covers early NBIO, RAS, IOMMU L2, USB4/PCIe direction, root-complex configuration, and the beginning of endpoint-function PCI configuration spaces through `regBIF_CFG_DEV0_EPF2_0_PCIE_ARI_CNTL`.

The file contains no executable C logic. Its functional role is to publish preprocessor constants that other AMDGPU code passes into SOC15 register access helpers. For almost every `reg...` offset macro, the chunk also defines a companion `..._BASE_IDX` macro, and in this slice those base indices are consistently `5`.

## Purpose

`nbio_7_11_0_offset.h` is the NBIO 7.11.0 address map for AMDGPU. It gives symbolic names to hardware register offsets so driver code can avoid hard-coded numeric addresses when programming the NBIO/PCIe/IOMMU portions of an ASIC. The companion `nbio_7_11_0_sh_mask.h` provides field shifts and masks for many of the same logical registers; driver code combines both headers with `RREG32_SOC15()`, `WREG32_SOC15()`, `SOC15_REG_OFFSET()`, `REG_SET_FIELD()`, and related AMDGPU register helpers.

Within this chunk, the register groups fall into several broad areas:

- Top-level NB configuration and scratch registers.
- NB miscellaneous registers for MMIO/DRAM windows, PSP/SMU/FASTREG/MISC aperture base addresses, trap registers, secondary-bus bridge registers, USB QoS, and MCA SMN interrupt routing.
- NB RAS and PSP RAS status/control offsets for parity, poison, sync flood, NMI, APML, and PSP poison reporting.
- Indirect SMN index/data windows for PCIe root-complex bridge configuration.
- IOMMU L2A performance, cache, credit, error-rule, page-size, and memory power-gating controls.
- USB4/PCIe direction registers used by the `nbio_v7_11` clock-gating path.
- Root-complex and endpoint-function PCI/PCIe configuration register offsets, including standard config-space registers and extended capabilities such as AER, ACS, ATS, PASID, SR-IOV, 16GT PHY, margining, and BAR/power-budget/DPA capability registers.

## Important Macros and Address Blocks

The chunk starts with an include guard `_nbio_7_11_0_OFFSET_HEADER` and the AMD MIT-style license. After that, it is organized by generated comments of the form `// addressBlock:` and `// base address:`.

Observed address blocks in this slice:

- `nbio_iohub_nb_nbcfg_nb_cfgdec`, base `0x0`: short config aliases for `cfgNBCFG_SCRATCH_0` through `cfgNBCFG_SCRATCH_4`.
- `nbio_iohub_iommu_l2_iommul2cfg`, base `0x0`: present as an empty address block in this chunk.
- `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, base `0x0`: defines `cfgPCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV`.
- `nbio_iohub_nb_nbcfg_nb_cfgdec`, base `0x13b00000`: `regNB_NBCFG0_*` aliases for NB vendor/device IDs, command/status, class code, header, adapter ID, capabilities pointer, scratch registers, PCI arbitration, DRAM slot base, index/data mutexes, and writable ID aliases.
- `nbio_iohub_nb_fastreg_fastreg_cfgdec`, base `0x13b07000`: `regFASTREG_APERTURE`.
- `nbio_iohub_nb_misc_misc_cfgdec`, base `0x13b10000`: the largest non-PCI-config block in this chunk. It includes `regNB_CNTL`, revision and bus/MMIO/DRAM mapping registers, software interrupt controls, CAM target registers, VDM controls, stall controls for xbar ports, PSP/SMU/FASTREG/MISC aperture base address low/high pairs, scratch and SMU block/status registers, trap request/response registers, trap comparators `regTRAP0_*` through `regTRAP15_*`, secondary-bus bridge window/control registers, `regUSB_QoS_CNTL`, and `regMCA_SMN_INT_*` registers.
- `nbio_iohub_nb_rascfg_ras_cfgdec`, base `0x13b20000`: parity controls, severity controls, RAS scratch registers, sync flood/NMI/internal poison/egress poison status and masks, egress poison severity, and APML status/control/trigger.
- `nbio_iohub_nb_psprascfg_pspras_cfgdec`, base `0x13b23000`: PSP poison status offsets.
- `nbio_iohub_nb_intSBdevindcfg0_devind_cfgdecp`, base `0x13b3c000`: internal secondary-bus device-indirect steering and latency registers.
- `nbio_iohub_nb_PCIE0rcbdg_indcfg[0-2]_pciercbdgind_cfgdec`, bases `0x13b7d600`, `0x13b7d700`, and `0x13b7d800`: three pairs of `RC_SMN_INDEX` and `RC_SMN_DATA` offsets.
- `nbio_iohub_iommu_l2a_l2acfg`, base `0x15700000`: IOMMU L2A performance counters, status/control, DTC/ITC/PTC controls, credit controls, update-filter control, error-rule controls, page-size control, memory power-gating controls, and ECO control.
- `nbio_iohub_nb_ioapiccfg_ioapic_cfgdec`, base `0x14300000`: `regFEATURES_ENABLE`.
- `nbio_pcie0_pciedir`, base `0x11180000`: USB4/PCIe adapter-layer and controller offsets such as `regPCIE_USB4_TXAL_CNTL1`, `regPCIE_USB4_RXAL_CNTL1`, `regPCIE_USB4_AL_CNTL*`, `regPCIE_USB4_ERR_CNTL5`, `regPCIE_USB4_LC_CNTL1`, and `regBIF_BIF256_CI256_RC3X4_USB4_*`.
- `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`, base `0x10100000`: root-complex config-space aliases with `regBIF_CFG_DEV0_RC0_*`.
- `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, base `0x10140000`: endpoint function 0 config-space aliases with `regBIF_CFG_DEV0_EPF0_0_*`.
- `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`, base `0x10141000`: endpoint function 1 aliases with `regBIF_CFG_DEV0_EPF1_0_*`.
- `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`, base `0x10142000`: endpoint function 2 aliases, ending in this chunk at `regBIF_CFG_DEV0_EPF2_0_PCIE_ARI_CNTL`.

The chunk contains 2,378 `#define` lines in total: 1,193 offset/config aliases and 1,185 `_BASE_IDX` aliases. The heavy macro concentration is under `regBIF_*`, which accounts for most PCIe root-complex and endpoint-function configuration definitions.

## API and Type Surface

This header does not define C functions, structs, enums, or runtime data. Its API is the macro namespace.

The key macro forms are:

- `cfg...`: raw config-space offsets that are not paired with `_BASE_IDX` in the same way as SOC15 `reg...` entries. Examples in this chunk include `cfgNBCFG_SCRATCH_0` through `cfgNBCFG_SCRATCH_4` and `cfgPCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV`.
- `reg...`: register offsets consumed by AMDGPU register helpers. Examples include `regNB_CNTL`, `regTRAP_REQUEST0`, `regPARITY_CONTROL_0`, `regL2_CONTROL_0`, `regBIF_BIF256_CI256_RC3X4_USB4_CPM_CONTROL`, `regBIF_CFG_DEV0_RC0_DEVICE_CNTL`, and `regBIF_CFG_DEV0_EPF0_0_PCIE_SRIOV_CONTROL`.
- `reg..._BASE_IDX`: base-index metadata used by SOC15 register macros. In this chunk, every observed `_BASE_IDX` value is `5`.

The standard PCI/PCIe configuration aliases map multiple logical fields to the same dword offset when the hardware register contains multiple fields. Examples include vendor/device ID sharing offset `0x0000` or `0x10000`, command/status sharing `0x0001` or `0x10001`, capability/control/status pairs sharing one dword, MSI message data variants sharing offsets, and PCIe lane equalization or DPA substate allocation registers packing multiple lanes/substates into the same dword. This sharing is intentional and requires the shift/mask companion header for field-level access.

## Control Flow

There is no branch, loop, call, or interrupt flow in this file. Runtime control flow appears in consumers that include this header.

The main direct consumer for this ASIC version is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes both `nbio/nbio_7_11_0_offset.h` and `nbio/nbio_7_11_0_sh_mask.h`. That C file uses the generated offsets to:

- Read and write NBIO registers with `RREG32_SOC15(NBIO, 0, reg...)` and `WREG32_SOC15(NBIO, 0, reg..., value)`.
- Convert generated register names into MMIO offsets with `SOC15_REG_OFFSET(NBIO, 0, reg...)`.
- Program USB4/PCIe clock-gating and light-sleep behavior using `regBIF_BIF256_CI256_RC3X4_USB4_CPM_CONTROL`, `regBIF_BIF256_CI256_RC3X4_USB4_PCIE_CNTL2`, `regBIF_BIF256_CI256_RC3X4_USB4_PCIE_TX_POWER_CTRL_1`, and `regBIF_BIF256_CI256_RC3X4_USB4_PCIE_MST_CTRL_3`, all of which appear in this chunk.

Most offsets used by `nbio_v7_11.c` are in later chunks of the same header, but the USB4/PCIe direction constants used by `nbio_v7_11_init_registers()`, `nbio_v7_11_update_medium_grain_clock_gating()`, `nbio_v7_11_update_medium_grain_light_sleep()`, and `nbio_v7_11_get_clockgating_state()` are present in this chunk.

## State and Persistence Behavior

This header itself stores no runtime state and has no persistence behavior. Its constants are compiled into the kernel driver and become part of the static hardware programming interface for NBIO 7.11.0.

The hardware registers named here do represent persistent device state while the GPU is powered:

- Scratch and RAS scratch registers may retain firmware/driver diagnostic values during a boot session.
- PCI/PCIe config registers hold device identity, command/status bits, BARs, capability lists, MSI/MSI-X state, AER status/masks/severity, SR-IOV configuration, PASID/ATS/ACS state, and link training/equalization state.
- NB misc aperture registers hold base addresses for PSP, SMU, FASTREG, and MISC windows.
- RAS poison, parity, sync flood, and APML status registers expose error state that may be sticky until explicitly cleared by hardware-specific flows.
- IOMMU L2 counters and controls represent performance, cache, credit, page-size, power-gating, and error-rule state.

Because the generated offsets are compile-time constants, changing them changes where the runtime driver reads and writes hardware state. An incorrect offset can silently target the wrong register and cause persistent malfunction until reset or power cycle.

## Dependencies and Integration Points

Primary dependencies and integration points:

- `nbio_7_11_0_sh_mask.h`: provides field masks and shifts for the same register families. The offset header names dwords; the shift/mask header names fields within those dwords.
- `amdgpu/soc15.h`: defines helper macro patterns such as `SOC15_REG_ENTRY`, `SOC15_REG_GOLDEN_VALUE`, and related constructs that depend on `reg##_BASE_IDX` and `reg` macro pairs.
- AMDGPU register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`: these use the generated offsets to resolve MMIO or indirect register accesses.
- `amdgpu/nbio_v7_11.c`: the ASIC-specific NBIO function table implementation. It directly includes this header and uses the USB4/PCIe direction registers from this chunk for clock-gating, light-sleep, and initialization programming.
- PCIe/AER/SR-IOV/IOMMU/KFD integration: although this chunk is only definitions, the named capabilities correspond to Linux-visible functionality such as PCIe link control, MSI/MSI-X, AER logging, SR-IOV virtual functions, PASID/ATS/ACS for IOMMU and process address spaces, and GPU doorbell/MMIO behavior in adjacent NBIO code.

The values are ASIC-version-specific. Similar generated headers exist for other NBIO versions (`nbio_7_0_*`, `nbio_7_2_0_*`, `nbio_7_7_0_*`, `nbio_7_9_0_*`, etc.), so consumers must include the matching header for the IP version being compiled.

## Risks and Edge Cases

- Offset drift from the hardware specification is the largest risk. These values are authoritative for low-level register access; a single wrong address or base index can corrupt unrelated state.
- Packed dword aliases can be misused if code writes a full register while intending to alter only one field. Many aliases share the same numeric offset, so consumers should use masks and read-modify-write helpers where appropriate.
- `_BASE_IDX` consistency matters. This chunk uses base index `5` throughout the SOC15-style register definitions. A mismatched base index would make otherwise correct offsets resolve through the wrong IP base.
- Some address blocks are intentionally empty or very small. The empty `nbio_iohub_iommu_l2_iommul2cfg` block and short config aliases should not be interpreted as missing driver logic by themselves; generated headers often preserve address-block structure even when no registers are emitted for a block.
- This chunk cuts off in the middle of the endpoint-function 2 block. Any per-file conclusions about the complete NBIO 7.11.0 address map must wait for later chunks.
- RAS and poison status offsets are sensitive because debug, health reporting, and recovery code may depend on exact bit locations from the matching shift/mask header.
- PCIe capability-list offsets encode standardized layout plus AMD-specific vendor capabilities. Misnaming or moving these can break capability discovery, SR-IOV setup, AER handling, or virtualization-related paths.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-probe oriented:

- Compile AMDGPU with `nbio_v7_11.c` included; missing or renamed macros from this header should fail compilation immediately.
- Verify that `nbio_v7_11.c` clock-gating paths can compile and use the chunk-local USB4/PCIe constants: `regBIF_BIF256_CI256_RC3X4_USB4_CPM_CONTROL`, `regBIF_BIF256_CI256_RC3X4_USB4_PCIE_CNTL2`, `regBIF_BIF256_CI256_RC3X4_USB4_PCIE_TX_POWER_CTRL_1`, and `regBIF_BIF256_CI256_RC3X4_USB4_PCIE_MST_CTRL_3`.
- On matching NBIO 7.11.x hardware, boot logs should show normal AMDGPU PCIe/NBIO initialization without register access faults, AER storms, failed BAR setup, or SR-IOV capability inconsistencies.
- Runtime power-management testing should exercise BIF medium-grain clock gating and light-sleep enable/disable paths and confirm expected flags from `nbio_v7_11_get_clockgating_state()`.
- PCIe capability visibility can be checked indirectly through normal Linux PCI enumeration, MSI/MSI-X availability, AER reporting, SR-IOV capability exposure where supported, and link status consistency.
- RAS diagnostics should be checked for sane parity/poison/APML/sync-flood status reporting on hardware and firmware combinations that expose those features.

## Chunk Summary

Lines 1-2478 provide the initial generated register-offset namespace for NBIO 7.11.0. The slice is definition-only, but it is critical infrastructure for the AMDGPU NBIO driver because it binds symbolic NBIO, PCIe, RAS, IOMMU L2, and USB4/PCIe register names to ASIC-specific offsets and SOC15 base indices. The most directly visible integration from this chunk is the `nbio_v7_11.c` USB4/PCIe clock-gating and light-sleep code; the broader register families support PCIe config-space access, RAS/error reporting, IOMMU L2 control, and low-level NB/MMIO aperture programming.

### subset-b-003119: lines 2479-4910

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h lines 2479-4910

## Scope

This chunk is a generated AMDGPU NBIO 7.11 register-offset header segment. It contains C preprocessor constants only: no functions, structs, enums, variables, allocations, locks, branches, loops, or direct hardware reads/writes. The exported data maps NBIF/BIF PCI configuration-space register names to 32-bit register offsets and emits a matching `<register>_BASE_IDX` constant for AMDGPU's SOC15 register access layer.

The range contains 2,400 `#define` entries: 1,200 register-offset symbols and 1,200 `_BASE_IDX` symbols. All `_BASE_IDX` values in this slice are `5`. The first line is a chunk-boundary tail for `regBIF_CFG_DEV0_EPF2_0_PCIE_ARI_CNTL_BASE_IDX`; then the slice closes the `DEV0_EPF2` routing-tail registers with `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`. It then covers full Type 0 endpoint-function config images for `DEV0_EPF3_0` through `DEV0_EPF7_0`, a Type 1/root-complex config image for `DEV1_RC0`, a richer endpoint/root-port-like `DEV1_EPF0_0` image, and the first part of `DEV1_EPF1_0` through `PCIE_VF_RESIZE_BAR2_CAP`.

Although the repository tree is under `sources/distributed-fs/ceph-client`, this file is AMD GPU hardware metadata. It has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_11_0_offset.h` gives AMDGPU compile-time names for NBIO 7.11 registers. This chunk focuses on NBIF/BIF PCI configuration-space decode blocks. Driver code pairs these `reg...` offsets with matching field shifts and masks from `nbio_7_11_0_sh_mask.h`, then reads or writes hardware through helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, `REG_GET_FIELD`, and `REG_SET_FIELD`.

The constants here describe where NBIO exposes PCI/PCIe configuration words for multiple device/function views. These include standard PCI identity and resource registers, PCIe capability and link state, MSI/MSI-X capability state, vendor-specific enhanced capability payloads, Advanced Error Reporting, BAR resize/power-budget/dynamic-power-allocation capabilities, ACS/PASID/ARI/SR-IOV capabilities, 16 GT/s physical-layer capability/status/equalization registers, lane margining, and routing-table capability data. The header supplies addresses only; field layout, reset values, side effects, and access policy live in companion generated files and the hardware specification.

## Address Blocks And Macro Families

The opening fragment belongs to the previous `DEV0_EPF2_0` block. Line 2479 is the `_BASE_IDX` for `PCIE_ARI_CNTL`, and lines 2480-2485 define the routing-table enhanced capability list and two routing data registers at offsets `0x1095c` through `0x1095e`.

`nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` through `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp` are complete, repeated endpoint-function images. Their base addresses are `0x10143000`, `0x10144000`, `0x10145000`, `0x10146000`, and `0x10147000`; their register offsets run from `0x10c00` to `0x10d5e`, `0x11000` to `0x1115e`, `0x11400` to `0x1155e`, `0x11800` to `0x1195e`, and `0x11c00` to `0x11d5e`. Each block has 128 register offsets plus 128 base-index macros. The repeated families include `VENDOR_ID`/`DEVICE_ID`, `COMMAND`/`STATUS`, revision/class/header/BIST, `BASE_ADDR_1` through `BASE_ADDR_6`, adapter and ROM base registers, capability pointers, interrupt-line/pin/min-grant/max-latency aliases, PMI, PCIe device/link capability and control/status registers, MSI/MSI-X, SATA IDP registers, vendor-specific enhanced capabilities, AER status/mask/severity/logs, resizable BAR registers, power-budget and DPA registers, ACS, PASID, ARI, and routing-table registers.

`nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp` starts at base address `0x10101000` and maps a Type 1/root-complex style PCIe configuration image at offsets `0x0400` through `0x055e`. It has 188 register offsets and 188 base-index macros. Unlike the Type 0 endpoint blocks, this block includes bridge-oriented registers such as `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `SECONDARY_STATUS`, `MEM_BASE_LIMIT`, prefetchable base/limit and upper registers, `IO_BASE_LIMIT_HI`, IRQ and extended bridge control, slot/root capability-control-status registers, MSI map and SSID capability registers, virtual-channel capability/resource registers, device serial number, root error command/status/source ID, secondary PCIe capability, lane error status, per-lane equalization for lanes 0-15, ACS, Data Link Feature, 16 GT/s PHY capability/status/equalization, and per-lane margining control/status. It closes with the same routing-table capability registers at `0x055c`-`0x055e`.

`nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp` starts at base address `0x10148000` and maps offsets `0x12000` through `0x1215e`. It has 221 register offsets and 221 base-index macros. The early portion resembles the Type 0 endpoint blocks, but the extended capability chain is richer: it includes VC registers, lane equalization, ACS/PASID/LTR/ARI, Data Link Feature, 16 GT/s PHY registers, and lane margining before the routing-table registers. This makes it closer to a physical endpoint/root-port-facing function than the simpler `DEV0_EPF3`-`EPF7` endpoint images.

`nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp` starts at base address `0x10149000`. This chunk covers offsets `0x12400` through `0x12533`, with 148 register-offset macros and 147 matching `_BASE_IDX` macros inside the requested line range because `regBIF_CFG_DEV1_EPF1_0_PCIE_VF_RESIZE_BAR2_CAP_BASE_IDX` is on the next line after the chunk. The covered part includes the standard Type 0 config header, PCIe device/link capability and status, MSI/MSI-X, SATA IDP, vendor-specific enhanced capability, AER logs, BAR resize, power budget, DPA, ACS, PASID, ARI, SR-IOV capability registers, VF BAR base registers, and the start of VF resizable BAR capability/control registers.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace:

- `regBIF_CFG_DEV*_...` symbols encode register offsets.
- `regBIF_CFG_DEV*_..._BASE_IDX` symbols encode the SOC15 base index used by AMDGPU register helpers.

The numeric values are untyped preprocessor integer literals. Some symbolic names alias the same offset because PCI config words pack multiple fields into one 32-bit register: for example vendor and device ID share offset `0x10c00` in `DEV0_EPF3_0`, command and status share `0x10c01`, and several MSI 32-bit/64-bit variants alias adjacent message-data, mask, or pending registers. Consumers must use the matching shift/mask macros to address subfields safely.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs in including AMDGPU code:

1. The NBIO 7.11 implementation or a PCIe/NBIO helper selects a generated `reg...` offset.
2. The code converts it through `SOC15_REG_OFFSET` or uses a PCIe/SOC15 read/write helper.
3. It applies matching `nbio_7_11_0_sh_mask.h` field masks and shifts when a subfield is needed.
4. The resulting read or write observes status, programs controls, configures resources, clears or masks errors, enables interrupt capabilities, or drives virtualization and PCIe-link policy.

`drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c` includes both this offset header and `nbio_7_11_0_sh_mask.h`. The visible NBIO 7.11 implementation uses the generated register database for revision ID reads, framebuffer access enablement, doorbell aperture/range programming, interrupt control, HDP flush offsets, PCIe index/data offsets, clock-gating controls, light-sleep controls, and register remapping. The specific BIF config symbols in this chunk are hardware metadata for PCIe config images and are most likely consumed by generic register access, diagnostics, display/resource include paths, virtualization/SR-IOV paths, or future/adjacent code rather than by a tight loop inside this header.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes hardware-backed PCI/PCIe configuration-space state exposed through NBIO/NBIF register windows. Persistence, reset behavior, ownership, and side effects are governed by PCIe semantics, GPU reset domains, firmware initialization, Linux PCI resource management, SR-IOV lifecycle, suspend/resume save-restore, function-level reset, and AMDGPU call-site policy.

Represented state includes identity/class registers, command/status bits, BAR/ROM/resource windows, bridge bus and memory windows, capability-list pointers, PCIe device/link controls and status, MSI/MSI-X message and mask state, AER status/mask/severity/header logs, virtual-channel and data-link-feature state, ACS/PASID/LTR/ARI controls, SR-IOV VF counts/stride/device IDs/page sizes/VF BAR bases, resizable BAR controls, DPA and power-budget information, 16 GT/s equalization status, lane margining controls/status, and routing-table data. Some registers are read-only capabilities, some are software-programmed controls, some are hardware-updated live status, and some diagnostic/error bits may be sticky or write-one-to-clear in the underlying hardware.

## Dependencies And Integration Points

The main dependency is consistency across the generated NBIO 7.11 register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h` supplies the matching field shifts and masks.
- Other generated NBIO 7.11 headers provide adjacent offsets, SMN addresses, and reset/default data where present.
- AMDGPU SOC15 and PCIe register helpers combine base index, register offset, and field masks to access the hardware.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c` is the primary NBIO 7.11 include user.
- `amdgpu_discovery.c` selects `nbio_v7_11_funcs` for NBIO IP versions 7.11.0 through 7.11.3, and `soc21.c`/`nbif_v6_3_1.c` contain NBIO 7.11 generation integration paths.
- Display resource files for DCN 3.5 and 3.5.1 include `nbio_7_11_0_offset.h`, so display bring-up may also depend on selected register offsets.

The hardware integration surfaces are PCIe enumeration, endpoint and root-complex config access, bridge window setup, MSI/MSI-X interrupt routing, PCIe AER diagnostics, VC/data-link features, ACS/PASID/ARI/IOMMU-related behavior, SR-IOV VF exposure, resizable BAR sizing, power-budget/DPA policy, 16 GT/s equalization, lane margining diagnostics, routing-table access, reset/FLR, and suspend/resume.

## Risks And Edge Cases

- Chunk boundaries are artificial. The first line is a `_BASE_IDX` for an earlier `DEV0_EPF2` register, and the final line defines `regBIF_CFG_DEV1_EPF1_0_PCIE_VF_RESIZE_BAR2_CAP` without its `_BASE_IDX`, which appears immediately after the requested range.
- Generated offset drift can compile cleanly while steering reads or writes to the wrong hardware register. This is especially risky because many register names alias the same dword by design, so accidental aliasing can look plausible.
- The repeated endpoint-function blocks are mechanically similar. A generation or copy error in only `DEV0_EPF3`, `EPF4`, `EPF5`, `EPF6`, or `EPF7` could affect one exposed function while other functions continue to work.
- Applying a Type 0 endpoint offset pattern to the `DEV1_RC0` Type 1/root-complex block would corrupt bridge, slot, root-error, lane, or link-training state rather than endpoint BAR/MSI state.
- PCI command, BAR, bridge memory-window, ROM, SR-IOV VF BAR, and resizable BAR registers directly affect MMIO decode, DMA visibility, and resource sizing.
- MSI/MSI-X register offsets affect interrupt delivery. Wrong offsets can cause lost, duplicated, masked, or misrouted interrupts.
- AER status, severity, mask, root-error, header-log, and TLP-prefix-log registers may have sticky or write-one-to-clear semantics. Incorrect read/modify/write handling can erase diagnostic evidence or leave errors uncleared.
- ACS, PASID, ARI, and SR-IOV registers are isolation-sensitive. Offset mistakes can affect VF enumeration, function routing, IOMMU behavior, and peer-to-peer access policy.
- 16 GT/s equalization and lane-margining registers are PCIe link-sensitive. Wrong register access can destabilize link training, margining diagnostics, or recovery behavior.
- `_BASE_IDX` value `5` is part of the SOC15 addressing contract. A mismatch between offset and base index would be as damaging as a wrong offset, even if the symbolic register name is correct.

## Test And Validation Signals

- Build AMDGPU with NBIO 7.11 support and display DCN 3.5/3.5.1 paths enabled. Missing or renamed macros should surface through `nbio_v7_11.c`, display resource includes, and related NBIF code.
- Run generated-header consistency checks that pair every non-`_BASE_IDX` register offset with a matching `_BASE_IDX`, allowing for this chunk's first-line and last-line boundary exceptions during whole-file reconciliation.
- Cross-check `nbio_7_11_0_offset.h` against `nbio_7_11_0_sh_mask.h` so every field mask has a valid register offset and every offset family has expected field definitions.
- Compare repeated `DEV0_EPF3_0` through `DEV0_EPF7_0` layouts for identical relative offsets, differing only by the function's offset window.
- On NBIO 7.11 hardware, validate PCIe enumeration, vendor/device/class fields, BAR sizing, command-bit transitions, capability-list traversal, MSI/MSI-X interrupt delivery, AER logging/clearing, ACS/PASID/ARI state, SR-IOV VF creation/removal where applicable, and resizable BAR behavior.
- Exercise suspend/resume, runtime power transitions, reset/FLR, and PCIe link retraining while monitoring link speed/width/status, AER events, 16 GT/s equalization status, and lane margining diagnostics.
- For bridge/root-complex paths, verify bus numbering, I/O and memory windows, root-error status/source IDs, slot/root status, and downstream device accessibility.

## Chunk Notes

- Lines 2479-2485: boundary tail for `DEV0_EPF2_0`, ending its ARI/routing-table capability offsets.
- Lines 2488-3787: complete repeated `DEV0_EPF3_0` through `DEV0_EPF7_0` endpoint-function config images.
- Lines 3788-4167: complete `DEV1_RC0` Type 1/root-complex config image with bridge, root, lane, 16 GT/s, margining, and routing registers.
- Lines 4168-4613: complete `DEV1_EPF0_0` extended endpoint/function image.
- Lines 4614-4910: partial `DEV1_EPF1_0` image, ending at the start of the VF resizable BAR capability family.

### subset-b-003120: lines 4911-7345

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h lines 4911-7345

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.11.0 register-offset header. It provides preprocessor constants for PCIe/NBIF configuration-space windows in the `nbio_nbif0` block, covering the end of device 1 endpoint-function 1, the device 2 root-complex function, device 2 endpoint functions 0 through 6, and the beginning of the RCC endpoint control block for device 0.

The constants map symbolic register names to dword offsets plus a companion `_BASE_IDX` value. In this range every `_BASE_IDX` is `5`, which tells AMDGPU's generated register-access layer which register base array entry to use when translating a symbolic register into an MMIO/config-space access. The source is hardware metadata rather than executable logic; it lets C code refer to PCIe capability, error-reporting, BAR, MSI/MSI-X, DPA, ACS, PASID, ARI, lane-training, and endpoint-control registers without hard-coding raw offsets.

## Important APIs, Types, and Macros

There are no C functions, structs, typedefs, or enums in this range. The public interface is the generated macro pattern:

- `reg<block/register>`: the register offset used by AMDGPU register helper macros.
- `reg<block/register>_BASE_IDX`: the generated base-index selector, consistently `5` in this chunk.

The chunk contains 2,399 `#define` lines. The address blocks inside the assigned line range are:

- Tail of `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`: only the final VF resizable-BAR registers for BAR2 through BAR6 and the RTR enhanced-capability/data registers remain in this chunk.
- `nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp`, base address `0x10102000`: device 2 root-complex configuration registers. It includes standard PCI configuration header aliases, bridge bus/window registers, PMI/PCIe/MSI/SSID/MSI-map capability registers, vendor-specific and VC capability registers, AER status/mask/severity/header-log registers, PCIe link/equalization and lane margining registers for lanes 0 through 15, and RTR capability/data registers.
- `nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp`, base address `0x10150000`: device 2 endpoint function 0. EPF0 is the broadest endpoint block in this chunk, including base PCI header/BAR registers, vendor and adapter IDs, MSI/MSI-X, SATA capability/IDP registers, VC resources, AER status/masks/logs, BAR enhanced capability registers, power-budgeting, DPA, ACS, PASID, LTR, ARI, 16 GT/s parity mismatch status, lane margining, and RTR registers.
- `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp`, base address `0x10151000`.
- `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp`, base address `0x10152000`.
- `nbio_nbif0_bif_cfg_dev2_epf3_bifcfgdecp`, base address `0x10153000`.
- `nbio_nbif0_bif_cfg_dev2_epf4_bifcfgdecp`, base address `0x10154000`.
- `nbio_nbif0_bif_cfg_dev2_epf5_bifcfgdecp`, base address `0x10155000`.
- `nbio_nbif0_bif_cfg_dev2_epf6_bifcfgdecp`, base address `0x10156000`.
- `nbio_nbif0_rcc_ep_dev0_RCCPORTDEC`, base address `0x10131000`: the beginning of an RCC endpoint port-control decode block. This chunk includes scratch, endpoint PCIe control, interrupt control/status, RX/bus/config controls, TX LTR control, function 0 DPA capability/control/status, and DPA substate power-allocation registers 0 through 7.

The endpoint-function blocks use a repeated schema. EPF0 has extra VC, LTR, parity mismatch, and lane-margining coverage. EPF1, EPF3, and EPF4 each have 256 macro lines in this range, while EPF2, EPF5, and EPF6 have 250 macro lines. Those smaller endpoint chunks omit a few registers present in the neighboring functions, so consumers should use the exact function-specific symbol rather than assuming all EPFs expose identical offsets.

Key register families are:

- Standard PCI configuration header aliases: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_*`, `CAP_PTR`, `ROM_BASE_ADDR`, and interrupt-line/pin fields.
- Root-complex bridge state: device 2 RC0 includes bus-number/latency, I/O base/limit, memory base/limit, prefetchable base/limit, upper window registers, bridge interrupt control, extended bridge control, slot/root capability/control/status registers, and secondary status.
- PCIe capability state: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, and the corresponding `*2` registers where present.
- MSI/MSI-X state: MSI message control, address, data, 64-bit data, mask, and pending registers, plus MSI-X table and PBA registers on endpoint functions.
- PCIe advanced error reporting: enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability control, header logs 0 through 3, and TLP prefix logs where present.
- Capability-extension blocks: vendor-specific capability, virtual-channel capability/resources, BAR enhanced capability controls, power-budgeting, dynamic power allocation, ACS, PASID, ARI, LTR, lane margining, and RTR registers.
- Low-level endpoint controls in the RCC block: `EP_PCIE_SCRATCH`, `EP_PCIE_CNTL`, `EP_PCIE_INT_CNTL`, `EP_PCIE_INT_STATUS`, `EP_PCIE_RX_CNTL2`, `EP_PCIE_BUS_CNTL`, `EP_PCIE_CFG_CNTL`, and `EP_PCIE_TX_LTR_CNTL`.

These macros are normally consumed through AMDGPU register helpers and SOC15/NBIO accessors that combine register offsets, base indices, instance selection, and field masks from companion headers.

## Control Flow and Runtime Behavior

This header chunk has no runtime control flow. It is included at compile time and contributes integer constants to later read, write, and read-modify-write operations in AMDGPU's NBIO/PCIe code.

The implied runtime flows are:

1. Device discovery and initialization code can read standard PCI header and capability-list registers for the device 2 root-complex and endpoint-function windows using these symbolic offsets.
2. PCIe setup code can program command/status, BARs, bridge windows, link control, slot/root control, MSI/MSI-X, and vendor-specific controls by pairing these offsets with the matching shift/mask definitions and access wrappers.
3. Error-handling paths can inspect AER uncorrectable/correctable status and logs, then mask or classify errors through the corresponding mask and severity registers.
4. Power and latency-management paths can access DPA, power-budgeting, LTR, and endpoint TX LTR controls. DPA state is split into capability/status/control registers plus repeated substate power-allocation entries.
5. I/O virtualization and isolation paths can use ACS, PASID, ARI, BAR enhanced capability, and the tail of the VF resizable-BAR registers to configure routing, function addressing, and BAR sizing behavior.
6. Link validation or debug code can use RC0 and EPF0 lane-equalization/lane-margining registers for lanes 0 through 15, plus parity mismatch status at 16 GT/s where defined.
7. RCC endpoint control paths can use the final block to adjust endpoint-specific PCIe control, interrupt routing/status, RX behavior, bus/config behavior, and LTR transmission controls.

The header does not prescribe sequencing. Any required ordering, polling, write-one-to-clear behavior, lock protection, reset handling, or firmware coordination must be implemented by the driver code that uses these constants and by the underlying hardware specification.

## State and Persistence

The file itself owns no mutable state, performs no I/O, allocates no memory, and persists nothing. The represented state lives in NBIO 7.11.0 hardware registers.

State represented by this chunk includes:

- PCI identity and configuration state for root-complex and endpoint functions, including command/status, BARs, bus windows, bridge controls, capability pointers, and interrupt descriptors.
- Interrupt-delivery state in MSI and MSI-X capability registers, including message address/data, mask, pending, table, and PBA offsets.
- PCIe link and topology state through device/link/slot/root capability, control, and status registers; RC0-specific bridge-window registers; VC resources; MSI map state; RTR data; and lane-specific equalization/margining registers.
- Error-observation and error-policy state through AER status/mask/severity, header-log, and TLP-prefix-log registers.
- Power-management state through PMI, power-budget, LTR, DPA capability/control/status, and DPA substate power-allocation registers.
- Isolation and multi-function state through ACS, PASID, ARI, vendor-specific, BAR enhanced-capability, and VF resizable-BAR registers.
- Endpoint-local RCC state through scratch/control/status registers and function 0 DPA/LTR controls.

Retention across GPU reset, FLR, BACO, suspend/resume, runtime power transitions, or PCIe link reset is not specified by the generated header. Callers must rely on NBIO hardware behavior and AMDGPU reinitialization paths to restore any policy registers that are not retained.

## Dependencies and Integration Points

Primary dependencies are the adjacent generated NBIO 7.11.0 headers:

- `nbio_7_11_0_sh_mask.h` supplies bit positions and masks for fields inside many of these registers.
- `nbio_7_11_0_default.h` supplies reset/default values where generated.
- `nbio_7_11_0_smn.h` supplies SMN-addressed registers for the same IP generation.
- Other chunks of this same offset header supply the earlier parts of device 1 endpoint function 1, the continuation of the RCC endpoint block after line 7345, and the surrounding NBIO address blocks.

Likely AMDGPU integration points include:

- NBIO 7.11 initialization and low-level access code that selects the generated NBIO register tables for this ASIC generation.
- SOC15-era register macros that use `reg...` and `reg..._BASE_IDX` names to construct MMIO/config-space accesses.
- PCIe link setup, ASPM/LTR/power-management, BAR sizing, bridge-window programming, and capability enumeration code.
- RAS and PCIe error paths that read AER status, masks, severity, header logs, TLP prefix logs, parity mismatch status, and endpoint interrupt status.
- SR-IOV, VF BAR sizing, PASID, ACS, and ARI paths that need function-specific offsets for isolation and function-addressing controls.
- Debug, bring-up, and validation paths that read lane equalization, lane margining, RTR, scratch, and RCC endpoint control/status registers.

The integration contract is purely symbolic. A consumer must include the NBIO 7.11.0 header that matches the ASIC/IP block it is programming; offsets from earlier NBIO generations may have similar names but are not interchangeable.

## Risks

- A wrong offset or base index can route a register access to the wrong NBIO window. Since most macros use the same `_BASE_IDX` value, simple compile-time type checking will not catch a symbol selected for the wrong device/function.
- The endpoint-function blocks are highly repetitive but not identical. Copying an EPF0 register name into EPF1-EPF6 code, or assuming all functions carry EPF0's VC/LTR/lane-margining/parity registers, can create build failures or incorrect hardware accesses.
- Many logical PCI registers share the same dword offset because they are subfields in one PCI configuration register, for example command/status, class-code bytes, link control/status, DPA status/control, ACS capability/control, and PASID capability/control. Offset-only users must pair the offset with the correct shift/mask header definitions.
- Root-complex and endpoint functions have similar AER and capability names but different address windows. Misclassifying RC0 versus EPF* can produce misleading error diagnosis or mask the wrong PCIe error source.
- MSI/MSI-X and BAR capability registers affect interrupt delivery and address decoding. Incorrect programming can break interrupt routing, expose unexpected BAR sizing, or disrupt virtual-function resource assignment.
- Error-reporting, DPA, LTR, ACS, PASID, ARI, and RTR registers can affect link behavior, isolation, power management, and recovery. Bad writes may have system-visible consequences beyond a single driver operation.
- The work item starts and ends mid-file. It begins after the start of device 1 endpoint-function 1 and ends after only the beginning of the RCC endpoint block, so merge/reconciliation must not treat missing neighboring registers as absent from the complete source.
- Generated headers are easy to validate mechanically but hard to validate semantically without ASIC documentation or hardware. A value can look structurally consistent while still being wrong for the hardware revision.

## Test and Validation Signals

Useful validation signals are a mix of generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU configurations that include NBIO 7.11.0 generated headers to catch malformed macro names, duplicate incompatible definitions, or missing symbols referenced by driver code.
- Run mechanical checks that every non-`_BASE_IDX` register macro in this chunk has the expected companion `_BASE_IDX` macro and that each companion value is `5`.
- Cross-check repeated endpoint-function sequences across EPF1 through EPF6 and separately compare EPF0, which intentionally has additional VC/LTR/parity/lane-margining coverage.
- Validate address-block boundaries: RC0 offsets should sit under base `0x10102000`, EPF0-EPF6 under `0x10150000` through `0x10156000`, and the RCC endpoint block under `0x10131000`.
- Cross-check register names against `nbio_7_11_0_sh_mask.h` and `nbio_7_11_0_default.h` so field masks/defaults exist where expected and absent masks are understood as whole-register or externally specified accesses.
- On hardware, read stable identity/capability registers such as vendor/device IDs, PCIe capability headers, MSI/MSI-X capability headers, AER capability headers, and lane-margining capability headers to confirm offsets land in plausible configuration-space locations.
- Exercise controlled PCIe error paths and confirm AER status, masks, severity registers, header logs, and TLP prefix logs are read from the expected RC0 or EPF window.
- Exercise suspend/resume, reset, and link retrain paths to confirm driver initialization restores command, BAR, interrupt, power-management, and link-policy registers that are expected to be programmed from these symbols.
- For SR-IOV or virtualization scenarios, validate VF BAR sizing, ACS/PASID/ARI behavior, MSI/MSI-X routing, and isolation with the function-specific symbols rather than shared offsets.

## Chunk Boundary Notes

Line 4911 starts in the middle of the previous `DEV1_EPF1` endpoint-function block. Only VF resizable-BAR entries for BAR2 through BAR6 and RTR entries are visible before the `DEV2_RC0` block begins at line 4938.

Line 7345 ends in the middle of `nbio_nbif0_rcc_ep_dev0_RCCPORTDEC`. This work item includes the RCC scratch/control/interrupt/RX/bus/config/TX-LTR and initial function 0 DPA substate power-allocation offsets, but the rest of the RCC endpoint block continues in a later chunk.

### subset-b-003121: lines 7346-9406

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h lines 7346-9406

## Scope

This chunk is the tail of AMDGPU's generated NBIO 7.11.0 register-offset header. It contains 1,891 preprocessor definitions: 948 register-address macros and 943 companion `_BASE_IDX` macros. There are no functions, structs, typedefs, enums, variables, locks, allocations, or executable statements.

The range starts in the middle of the `nbio_nbif0_rcc_ep_dev0_RCCPORTDEC` address block with endpoint PCIe control/status offsets for `regRCC_EP_DEV0_0_*`. It then covers RCC downstream/downstream-port/endpoint windows for devices 1 and 2, internal strap registers, BIF reset and miscellaneous blocks, SION scheduling offsets, BIF RAS offsets, BIFDEC1 and BIFPFVFDEC1 views for `BIF_BX0`, `BIF_BX1`, and `BIF_BX2`, GDC doorbell blocks, and finally closes the header with `#endif`.

## Purpose

`nbio_7_11_0_offset.h` provides symbolic register addresses for the NBIO 7.11 hardware block used by AMDGPU and display code. This line range describes the lower-level PCIe/NBIO address map for reset, function-level reset, D-state and D3hot/D0 reset tracking, interrupt routing, DMA attribute override, NBIF performance counters, SION credit/scheduling registers, RAS status/control, BIF_BX system and PF/VF windows, HDP coherency flush registers, GPU address LUTs, mailbox buffers, doorbell aperture controls, and per-engine doorbell range registers.

The macros are not a standalone API. They are the address half of a generated register interface. Callers pair these `reg...` offsets and `_BASE_IDX` values with sibling shift/mask definitions from `nbio_7_11_0_sh_mask.h`, AMDGPU register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and display register-list expansion macros that add `ctx->nbio_reg_offsets[base_idx]`.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro convention:

- `reg<REGISTER_NAME>`: a register offset or encoded address used by SOC15/NBIO access helpers.
- `reg<REGISTER_NAME>_BASE_IDX`: an index into the relevant NBIO base-address table. Most macros in this chunk use base index `5`; some BIF/GDC windows use indices `0`, `2`, or `3`.

Major macro families in this chunk are:

- `regRCC_EP_DEV0_0_*`, `regRCC_EP_DEV1_*`, and `regRCC_EP_DEV2_*`: endpoint PCIe scratch, control, interrupt, RX/TX, bus/config, LTR, PME, error-control, link-speed, and Dynamic Power Allocation offsets. DEV1 and DEV2 include repeated F0 DPA capability, latency indicator, control, and substate power allocation offsets.
- `regRCC_DWN_DEV*_*` and `regRCC_DWNP_DEV*_*`: downstream and downstream-port PCIe reserved/scratch/control/config/RX/bus/Cfg offsets plus downstream-port error, RX, link-speed, link-control, and LTR-message offsets.
- `regRCC_STRAP*` and `regRCC_DEV0_EPF*`: strap and endpoint-function offsets, including doorbell aperture enable and configured memory size registers. These are used by NBIO setup to read revision IDs, memory size, and doorbell aperture state.
- `regHARD_RST_CTRL`, `regSELF_SOFT_RST*`, `regBIF_RST_MISC_CTRL*`, `regDEV*_PF*_FLR_RST_CTRL`, `regBIF_*_INTR_STS`, `regBIF_*_INTR_MASK`, `regBIF_PF_FLR_RST`, `regBIF_DEV*_PF*_DSTATE_VALUE`, and `regDEV*_PF*_D3HOTD0_RST_CTRL`: reset, function-level reset, D-state, D3hot/D0, and reset interrupt surfaces for devices 0, 1, and 2.
- `regMISC_SCRATCH`, `regINTR_LINE_*`, `regOUTSTANDING_VC_ALLOC`, and the `regBIFC_*` family: miscellaneous BIF control, BME error logging, per-device DMA attribute overrides, PASID status/control, SDP controls, ATHUB action control, performance counter controls and low/high counter pieces, page-gating controls, SMN master controls, SDP voltage-change reset controls, SHUB timeout detection controls, pool-credit allocation, Z10 state, BDF control, early wakeup, and common-count status.
- `regSION_CL[0-2]_*` and `regSION_CNTL_REG*`: SION client scheduling and credit allocation offsets for read response, write response, request, data, and pool-credit registers.
- `regBIFL_RAS_*`: BIF leaf/central RAS control and status offsets plus IOHUB RAS interrupt/control and VWR-from-IOHUB offsets.
- `regBIF_BX0_*`, `regBIF_BX1_*`, and `regBIF_BX2_*`: BIF_BX system windows for PCIe indirect index/data, SBIOS/BIOS scratch registers, RLC/VCE/UVD interrupt controls, GFX MMIO CAM remap entries, reset controls, interrupt controls, doorbell controls, frame-buffer enables, transaction-pending status, BACO controls and exit timers, memory type control, NBIF GFX address LUT entries 0-15, GFX reset control, HDP remap flush controls, BIF ring-buffer pointers, mailbox index, GPUIOV config size, and pad controls.
- `regBIF_BX_PF0_*`, `regBIF_BX_PF1_*`, and `regBIF_BX_PF2_*`: PF/VF-facing BIF BME status, atomic error log, doorbell self-ring GPA aperture base/control, HDP coherency flush/invalidate controls, GPU HDP flush request/done registers, transaction-pending status, address-LUT bypass, mailbox transmit/receive dwords, mailbox control/interrupt, and VM/HV mailbox offsets.
- `regGDC0_*`, `regGDC1_*`, and `regGDC2_*`: GDC doorbell and queue-control offsets, including A2S queue FIFO arbitration, NBIF GFX doorbell status, SDMA/IH/VCN/RLC/CSDMA/VPE doorbell ranges, ATDMA misc control, and doorbell fence control. GDC0 additionally has `VPE1` and `S2A_MISC_CNTL` entries, while the tail-end GDC2 block ends at `regGDC2_BIF_DOORBELL_FENCE_CNTL`.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior is created by code that includes it and uses the offsets to access hardware registers.

Observed direct integration includes `amdgpu/nbio_v7_11.c`, which includes this offset header and the matching shift/mask header. That file uses offsets from this range to remap HDP flush registers, read the revision strap, enable/disable frame-buffer access, read configured memory size, program CSDMA/VPE/VCN/IH doorbell ranges, enable the doorbell aperture and self-ring aperture, program interrupt control, and return HDP flush and PCIe index/data offsets to generic AMDGPU code.

Display resource files for DCN 3.5 and DCN 3.5.1 also include this header. Their NBIO register-list macros expand selected `regBIF_BX1_BIOS_SCRATCH_*` offsets with `ctx->nbio_reg_offsets[...]` to populate BIOS scratch register tables used by display resource initialization.

The implied external flows are:

1. NBIO initialization selects a generated register macro and adds the corresponding base-index entry through `SOC15_REG_OFFSET` or display `NBIO_BASE`.
2. Driver code reads, writes, or read-modify-writes the hardware register using the computed address and field definitions from `nbio_7_11_0_sh_mask.h`.
3. Hardware performs the requested operation: reset sequencing, FLR/D-state transition observation, doorbell range routing, interrupt delivery, HDP flush synchronization, mailbox exchange, address-LUT translation, RAS reporting, SION credit scheduling, or PCIe indirect access.
4. Status and done registers are polled or sampled by higher-level AMDGPU paths; this header only names those registers and does not encode ordering, timeout, clear-on-write, or ownership rules.

## State And Persistence Behavior

The header owns no mutable software state and persists nothing. It describes hardware-visible state in NBIO 7.11 registers.

The represented state includes PCIe endpoint/downstream control, LTR and PME state, DPA state, reset and FLR command/status state, D-state and D3hot/D0 transition state, interrupt masks/status, BIF miscellaneous controls, BME and atomic error logs, DMA/PASID/SDP attributes, performance counters, page-gating and low-power controls, SION traffic scheduling and credit allocation, BIF RAS central/leaf controls and status, BIOS/SBIOS scratch registers, MMIO CAM remap state, doorbell aperture/range state, HDP coherency flush request/done state, BIF transaction-pending status, BACO controls and timers, NBIF GFX address LUTs, mailbox buffers, and pad controls.

Persistence across GPU reset, PCIe hot reset, FLR, BACO, suspend/resume, runtime power transitions, or firmware handoff is not specified here. Some scratch and strap registers may be firmware- or boot-initialized, and some status registers may be sticky or clear-on-write, but those semantics must come from hardware documentation and the matching shift/mask/default/access metadata.

## Dependencies And Integration Points

Primary source dependencies are the adjacent generated NBIO 7.11 headers:

- `nbio_7_11_0_sh_mask.h` for bit positions and masks inside the registers named here.
- Any generated default or SMN metadata for NBIO 7.11 where present in the same ASIC register tree.
- SOC15 register access infrastructure that interprets `_BASE_IDX` values and adds the correct per-IP base address.

Important integration points are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, the direct NBIO 7.11 consumer for HDP remap, revision strap, memory size, doorbells, interrupt setup, PCIe indirect offsets, and doorbell apertures.
- AMDGPU doorbell allocation and per-engine setup for SDMA, CSDMA, VPE, VCN, IH, RLC, and other engines routed through GDC doorbell range registers.
- AMDGPU reset and power-management flows that may interact with BIF reset, FLR, D-state, D3hot/D0, BACO, page-gating, Z10, and early-wakeup registers.
- HDP flush and coherency paths that use PF/VF BIF registers for GPU HDP flush request/done and remapped HDP flush controls.
- Display DCN 3.5/3.51 resource initialization, which uses NBIO BIOS scratch offsets via display register-list macros.
- Virtualization and firmware/hypervisor paths suggested by GPUIOV config-size registers, VM/HV mailbox registers, mailbox message buffers, BIF ring-buffer registers, and PF/VF-specific address windows.
- RAS and diagnostics paths for BIF leaf/central status, BME/atomic logs, performance counters, SION scheduling, and timeout/sync-flood controls.

## Risks And Edge Cases

- Generated address drift can compile cleanly while sending reads or writes to the wrong NBIO register. In this chunk that can break doorbell routing, HDP flush completion, reset handling, display BIOS scratch reads, RAS reporting, or virtualization mailbox traffic.
- The same logical register families appear through multiple address windows: `BIF_BX0`, `BIF_BX1`, and `BIF_BX2`; PF0/PF1/PF2; GDC0/GDC1/GDC2; and RCC device/function variants. Using the wrong instance can affect a different BIF, PF/VF, or doorbell aperture than intended.
- `_BASE_IDX` values are part of the ABI with SOC15 base tables. A correct offset with the wrong base index is still a bad final address.
- Several register names are intentionally aliased to the same offset, especially DPA capability/control/substate fields. Callers must use the matching shift/mask fields and avoid assuming one macro name means a unique 32-bit location.
- Reset, FLR, D-state, D3hot/D0, BACO, and page-gating registers interact with live hardware state machines. Bad ordering or missing polling can leave the GPU partially reset, power-gated, or inaccessible.
- Doorbell aperture and doorbell range programming affects command submission and interrupt delivery. A wrong offset, size, or engine instance can cause lost work submissions, spurious interrupts, or writes into the wrong doorbell range.
- HDP flush request/done and coherency-flush registers are synchronization points. Misaddressing them can cause stale CPU/GPU-visible memory or hangs in code waiting for completion.
- Mailbox and VM/HV registers imply firmware or hypervisor ownership. Writes without ownership coordination can corrupt messages or interfere with virtualization flows.
- The chunk starts in the middle of an RCC endpoint block inherited from prior lines, so whole-file reconciliation should combine this with the preceding chunk before treating the DEV0_0 endpoint family as complete.

## Test Signals

Useful validation combines generated-header checks with hardware-oriented AMDGPU coverage:

- Build AMDGPU configurations that include NBIO 7.11 and DCN 3.5/3.51 support to catch missing, renamed, or malformed macros.
- Run generated-header consistency checks to ensure each register macro has the expected `_BASE_IDX` companion, repeated device/PF/GDC families have coherent offsets, and all references in `nbio_v7_11.c` and DCN resource files resolve.
- Cross-check final computed addresses from `SOC15_REG_OFFSET(NBIO, 0, reg...)` against the ASIC register database for representative RCC, BIF reset/misc, BIF_BX, PF/VF, and GDC entries.
- On NBIO 7.11 hardware, validate doorbell setup for CSDMA, VPE, VCN, IH, SDMA, RLC, and related engines by confirming command submission, interrupts, and doorbell status after programming the listed range registers.
- Validate HDP coherency by exercising GPU/CPU memory-visible operations that require HDP flush request/done registers and remapped HDP flush controls.
- Exercise reset, FLR, D-state, D3hot/D0, suspend/resume, BACO, and runtime power paths while checking the related BIF status/mask/control registers for expected transitions and recovery.
- Confirm display initialization on DCN 3.5/3.51 ASICs can read expected BIOS scratch values through the `regBIF_BX1_BIOS_SCRATCH_3` and `regBIF_BX1_BIOS_SCRATCH_6` paths.
- For RAS and diagnostics, sample BIF RAS central/leaf status, BME/atomic logs, performance counters, and transaction-pending status before and after controlled events where platform validation permits.

## Chunk Boundary Notes

This is the final chunk of `nbio_7_11_0_offset.h`: line 9406 is the closing `#endif`. The range begins after the start of `nbio_nbif0_rcc_ep_dev0_RCCPORTDEC`, so the initial `regRCC_EP_DEV0_0_*` macros here are a continuation of a logical address block that starts in the previous chunk. Merge/reconciliation should join that preceding endpoint context with this tail section.
