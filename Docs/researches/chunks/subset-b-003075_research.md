# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 17236-19637

## Scope

This chunk covers 2,402 lines from the generated AMD NBIO 7.0 shift/mask header. It starts in the middle of the `BIFPLR1_0_SLOT_CAP` definition, continues through the remainder of the `BIFPLR1_0` PCIe capability and enhanced-capability register fields, switches at `// addressBlock: nbio_pcie0_bifplr2_cfgdecp`, and then covers the beginning of the `BIFPLR2_0` PCIe bridge/configuration-space field map through most of `BIFPLR2_0_PCIE_ROOT_ERR_STATUS`.

There are no C functions, structs, enums, globals, locks, allocations, branches, or direct register accesses in this range. The public surface is preprocessor symbols of the generated form:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The range is a register-definition fragment, not executable driver logic. It is still important because AMDGPU code and helper macros depend on these constants when decoding or composing NBIO and PCIe configuration-space register values for this ASIC generation.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.0 register interface. The matching generated headers provide complementary information:

- `nbio_7_0_offset.h` maps register names to MMIO/PCIE/config-space offsets.
- `nbio_7_0_default.h` provides reset/default values for many registers.
- `nbio_7_0_smn.h` provides SMN-addressed NBIO symbols.

This chunk describes PCIe root-port and bridge-facing register fields for two NBIO PCIe logical register blocks:

- `BIFPLR1_0`, mainly the latter part of its PCIe Capability and Enhanced Capability structures.
- `BIFPLR2_0`, from base PCI/PCI-to-PCI bridge configuration registers through AER root error status.

The macro names follow PCIe terminology closely: slot control/status, root control/status, Device Capabilities 2, Link Capabilities/Control/Status 2, MSI, virtual channels, advanced error reporting, link equalization, access control services, multicast, L1 PM substates, downstream port containment, root-port PIO logs, and ESM link-speed capability bitmaps. Consumers can use the generated shift/mask symbols with helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32*`, and `WREG32*` without embedding numeric bit constants in runtime code.

## Register Families Covered

The chunk begins with the tail of `BIFPLR1_0_SLOT_CAP`: power indicator, hot-plug, slot power-limit, electromechanical interlock, command-completed support, and physical slot-number fields. The first few `SLOT_CAP` shift definitions are in the previous chunk, but all `SLOT_CAP` masks are visible here.

The next `BIFPLR1_0` core PCIe capability fields include:

- `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS` for hot-plug, slot events, SERR/PME reporting, CRS software visibility, and PME requestor/status tracking.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, and `DEVICE_STATUS2` for completion timeout, ARI, AtomicOp, IDO, LTR, OBFF, end-to-end TLP prefixes, and reserved status bits.
- `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for supported/target link speeds, compliance-entry controls, de-emphasis, equalization phase status, and equalization requests.
- Reserved `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2` fields.

The chunk then covers `BIFPLR1_0` MSI and vendor/extended capabilities:

- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, address low/high, and data fields for MSI programming.
- `SSID_CAP_LIST` and `SSID_CAP` for subsystem vendor and subsystem IDs.
- `MSI_MAP_CAP_LIST`, `MSI_MAP_CAP`, and MSI-map address fields.
- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, and two scratch-style vendor-specific payload registers.

The `BIFPLR1_0` PCIe enhanced capability groups in this chunk include:

- Virtual Channel (`PCIE_VC_ENH_CAP_LIST`, port VC capability/control/status, `VC0` and `VC1` resource capability/control/status).
- Device Serial Number (`PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, `DW1`, `DW2`).
- Advanced Error Reporting (`PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable status/mask/severity, correctable status/mask, AER capability/control, TLP header logs, root error command/status, error source IDs, and TLP prefix logs).
- Secondary PCIe, Link Control 3, lane error status, and per-lane equalization control for lanes 0 through 15.
- Access Control Services (`ACS_CAP`, `ACS_CNTL`) for source validation, translation blocking, peer-to-peer redirect/egress, upstream forwarding, and direct translated P2P.
- Multicast capability/control/address/receive/block/overlay BAR registers.
- L1 PM Substates capability/control/control2.
- Downstream Port Containment (`DPC_CAP_LIST`, `DPC_CNTL`, `DPC_STATUS`, error source ID).
- Root Port PIO status, mask, severity, system-error, exception, header log, implementation-specific log, and prefix log registers.
- ESM capability headers/status/control and `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`, which are dense bitmaps for supported ESM data-rate points from 8.0G through 28.0G.

After the address-block transition, `BIFPLR2_0` starts at base PCI/bridge configuration fields:

- Vendor/device ID, command/status, revision/class-code fields, cache-line/latency/header/BIST fields.
- Bus-number, IO window, memory window, prefetchable window, upper-address, capability pointer, interrupt line/pin, bridge control, and extended bridge control.
- Power Management capability/status-control.
- PCIe capability, Device Capabilities/Control/Status, Link Capabilities/Control/Status, Slot Capabilities/Control/Status, Root Control/Capability/Status, Device/Link/Slot Capability 2 families, MSI, SSID, MSI map, vendor-specific, VC, serial number, and AER fields through root error status.

The final visible line is `BIFPLR2_0_PCIE_ROOT_ERR_STATUS__FATAL_ERROR_MSG_RCVD_MASK`. The `ADV_ERR_INT_MSG_NUM_MASK` field for that same register is on the next physical line and therefore belongs to the next chunk.

## Important APIs, Types, and Functions

This header segment exposes no callable APIs or C types. Its API is the generated macro namespace consumed by AMDGPU register helpers. The important contract is that each field has a matching shift and mask with a stable generated name.

Typical consumers use these symbols in patterns like:

- `REG_GET_FIELD(value, BIFPLR2_0_LINK_STATUS, NEGOTIATED_LINK_WIDTH)` to decode a field from a read register value.
- `REG_SET_FIELD(value, BIFPLR1_0_DEVICE_CNTL2, LTR_EN, 1)` to compose a read-modify-write value.
- `FIELD_MASK` constants directly when clearing, testing, or preserving specific status/control bits.

Important field groups by behavior:

- Capability IDs and next pointers (`*_CAP_LIST`, `*_ENH_CAP_LIST`) describe PCI/PCIe capability-chain layout.
- Capability registers (`*_CAP`, `*_CAP2`) advertise hardware support and should usually be treated as read-mostly hardware descriptions.
- Control registers (`*_CNTL`, `*_CNTL2`, `*_ROOT_ERR_CMD`, `*_ACS_CNTL`, `*_DPC_CNTL`) contain writable feature-enable, interrupt-enable, containment, link-control, or reporting-policy bits.
- Status registers (`*_STATUS`, `*_STATUS2`, AER status, DPC status, PIO status) report latched or live hardware state. Some status bits may be write-one-to-clear according to PCIe semantics even though this generated header does not encode access mode.
- Log registers (`*_HDR_LOG*`, `*_TLP_PREFIX_LOG*`, `*_RP_PIO_*_LOG*`) expose captured TLP headers/prefixes for error handling and diagnostics.
- Window/address registers (`MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `IO_BASE_LIMIT`, multicast address and overlay BAR fields, MSI message and mapping addresses) carry address bits and must be paired with correct size/alignment semantics from PCIe or the hardware database.

## Control Flow

There is no local control flow. The generated constants participate in external driver and platform flows:

1. AMDGPU, PCI core code, firmware-facing code, or diagnostics selects a register offset from `nbio_7_0_offset.h` or an SMN/MMIO/PCIE accessor path.
2. The caller reads a register or starts from a cached/default value.
3. The caller extracts a field using the `__SHIFT`/`_MASK` pair or composes a modified value with a helper such as `REG_SET_FIELD`.
4. For writable registers, the caller writes the value through the relevant MMIO, SOC15, PCIE, or SMN accessor.
5. PCIe/NBIO hardware consumes control bits or reports status/log bits asynchronously based on link, power, error, interrupt, and reset state.

Representative runtime flows that depend on this style of generated header include PCIe link bring-up and retraining, completion-timeout and LTR policy setup, MSI configuration, hot-plug and PME reporting, AER/DPC error handling, ACS/IOMMU isolation policy, L1 PM substate programming, GPU reset and secondary-bus reset handling, and register dumps used during hardware debug.

The file is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h` in this source tree. Direct references to every macro are not required; many generated field names are consumed only for specific ASICs, diagnostics, or conditionally compiled paths.

## State and Persistence Behavior

The header stores no software state. It names hardware-visible bits in PCIe configuration-space style registers for NBIO 7.0.

Persistence is hardware- and reset-domain-dependent:

- Capability registers are generally hardware-defined and stable across normal runtime operation, but can differ by ASIC, fuse/strap state, board wiring, firmware configuration, or PCIe port mode.
- Control registers can be programmed by BIOS/firmware, the Linux PCI core, AMDGPU, virtualization layers, or error-handling paths. Their values may need restoration after GPU reset, function-level reset, secondary bus reset, S3/S4 suspend/resume, or runtime power transitions.
- Status and error registers can be latched by hardware events. AER, DPC, root error status, PIO status, and PCI status bits may require explicit clearing with PCIe-defined write semantics.
- Log registers are transient diagnostic state. Header/TLP-prefix/PIO logs describe the transaction associated with an error and may be overwritten by later errors or cleared during recovery.
- Address/window registers define decoded IO, memory, prefetchable, MSI, and multicast regions. Incorrect persistence or restore behavior can affect reachability, interrupt delivery, peer routing, or isolation.

The chunk itself does not encode reset values, read/write permissions, write-one-to-clear behavior, volatile/live status behavior, or ownership. Those semantics must come from the PCIe specification, AMD register database, `nbio_7_0_default.h`, platform firmware policy, and the driver paths that use these fields.

## Dependencies and Integration Points

The immediate dependency is the generated NBIO 7.0 register-header set. This chunk is only useful when paired with the corresponding offset/default/SMN headers and the AMDGPU register helper macros.

Primary integration points in this source tree:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c` includes `nbio_7_0_sh_mask.h` and programs NBIO generation-specific behavior such as memory-controller access, doorbell aperture ranges, HDP remapping, clock gating, light sleep, and indirect sys-hub registers.
- `drivers/gpu/drm/amd/amdgpu/soc15.c` includes NBIO 7.0 headers as part of SOC15 ASIC initialization and common IP setup for Vega/Raven-era devices.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h` pulls NBIO 7.0 definitions into SMU10/power-management include stacks alongside MP and THM generated headers.
- Linux PCIe infrastructure can indirectly depend on the same hardware fields when AMDGPU or platform code surfaces link state, AER/DPC handling, MSI programming, bridge windows, power-management policy, and hot-plug/PME behavior.

Cross-file generated-header consistency is critical. Register names in this shift/mask header must match offsets in `nbio_7_0_offset.h`; otherwise code can compile while extracting the right field shape from the wrong register address. Default values in `nbio_7_0_default.h` should be consistent with read-only/reserved field masks and expected reset state.

## Risks and Edge Cases

- The chunk starts mid-register. `BIFPLR1_0_SLOT_CAP` is incomplete without the previous chunk, which contains the first shift definitions.
- The chunk ends mid-register. `BIFPLR2_0_PCIE_ROOT_ERR_STATUS__ADV_ERR_INT_MSG_NUM_MASK` is on the next source line and must be reconciled by the merge lane.
- Capability and control registers often share similar field names across `BIFPLR1_0` and `BIFPLR2_0`. A wrong prefix can compile but target a different PCIe port or config-decode block.
- Many fields mirror standardized PCIe bit positions. Small mask/shift mistakes can silently break Linux PCIe expectations for MSI, AER, DPC, ACS, L1 PM substates, hot-plug, or bridge-window setup.
- Status/error bits may be write-one-to-clear or otherwise side-effectful. The generated mask does not communicate access semantics, so generic read-modify-write code can accidentally clear or preserve the wrong error state.
- Reserved fields are explicitly named for some registers. Software should preserve reserved bits unless hardware documentation says otherwise.
- Address-window fields expose partial address bits and require PCIe-specified alignment. Treating mask width as the full address without applying implied low bits can produce invalid IO, memory, MSI, or multicast windows.
- ESM capability bitmaps are dense and regular. Off-by-one generation errors in data-rate bits are hard to notice in compile tests but can advertise or select unsupported link-speed/equalization behavior.
- ACS and peer-to-peer controls affect IOMMU/security isolation and GPU-to-GPU routing. Incorrect masks or restore policy can cause either lost P2P performance or unsafe peer access.
- DPC and AER controls affect recovery behavior after PCIe errors. Bad masks can suppress reporting, misclassify fatal/nonfatal errors, block poisoned TLP handling, or leave ports contained longer than expected.
- MSI and MSI-map fields affect interrupt delivery. Incorrect address/data masks can create lost or misrouted interrupts, especially across resume, reset, or virtualization transitions.

## Test Signals

Useful validation for this chunk is mostly compile-time, generated-header consistency, and hardware/PCIe behavior testing:

- Build AMDGPU configurations that include SOC15, NBIO 7.0, SMU10, AER/DPC-capable PCIe support, and power-management paths. This catches missing or renamed generated symbols.
- Run generated-register consistency checks: every register in this chunk should have matching offset entries in `nbio_7_0_offset.h`, and shift/mask pairs should agree with the authoritative AMD register database.
- Check boundary continuity with neighboring chunks: complete `BIFPLR1_0_SLOT_CAP` at the start and complete `BIFPLR2_0_PCIE_ROOT_ERR_STATUS` at the end.
- Validate PCIe enumeration on affected AMD GPUs: vendor/device IDs, class/header type, bridge windows, capability pointers, MSI capability, PCIe capability, and enhanced-capability chain should decode as expected.
- Exercise link training and retraining across supported speeds and widths; confirm `LINK_STATUS`, `LINK_STATUS2`, `LINK_CNTL2`, lane equalization, and ESM-related bits match observed link behavior.
- Test suspend/resume, GPU reset, secondary bus reset, and function reset to ensure control registers for LTR, OBFF, ACS, DPC, AER, MSI, and bridge windows are restored or intentionally reinitialized.
- Inject or observe PCIe AER/DPC events where supported and verify uncorrectable/correctable status, masks, severities, root error status, error source IDs, TLP header logs, and prefix logs decode correctly.
- Verify MSI delivery before and after reset/resume, including 64-bit MSI address and MSI-map fields where the platform uses them.
- For ACS/IOMMU-sensitive systems, verify isolation and peer-to-peer routing policy using PCIe topology tests and GPU P2P workloads.
- For power-management paths, verify L1 PM substate and LTR behavior does not regress idle power, wake latency, or link stability.

## Unresolved Cross-Chunk References

The previous chunk is needed for the first `BIFPLR1_0_SLOT_CAP` shift fields, including attention button, power controller, MRL sensor, and attention indicator presence. This chunk contains the remaining `SLOT_CAP` shifts and all `SLOT_CAP` masks.

The next chunk begins with the final mask for `BIFPLR2_0_PCIE_ROOT_ERR_STATUS` and then continues into `BIFPLR2_0_PCIE_ERR_SRC_ID`, TLP prefix logs, secondary PCIe enhanced capability, Link Control 3, lane error/equalization registers, and later `BIFPLR2_0` capability groups. The final per-file document should merge those boundaries before describing complete `BIFPLR1_0` and `BIFPLR2_0` coverage.
