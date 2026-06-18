# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 12284-15100

## Scope

This chunk covers lines 12284-15100 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, variables, allocation, locking, persistence code, or direct register accesses.

The range starts at the tail of `BIF_CFG_DEV0_EPF1_0_PCIE_UNCORR_ERR_MASK`, then covers the rest of the PCIe extended capability and RCC/RCCPFC field map for device 0, endpoint function 1 / RCC device 1. It ends inside the MSI-X table field map after `PCIEMSIX_VECT162_ADDR_LO`, with line 15100 only introducing the `PCIEMSIX_VECT162_ADDR_HI` register heading; that register's shift and mask definitions continue in the next chunk.

Although this repository path is under a `ceph-client` source tree mirror, the content is AMD GPU NBIO/PCIe register metadata. It has no Ceph or distributed-filesystem runtime behavior.

## Purpose

`nbio_7_9_0_sh_mask.h` is the bitfield-definition companion to the NBIO 7.9.0 register map. Each macro provides one of two pieces of field geometry:

- `REGISTER__FIELD__SHIFT`: the least-significant bit index for a hardware field.
- `REGISTER__FIELD_MASK`: the bit mask for that field in the containing register.

AMDGPU NBIO and RAS code includes this header with the matching NBIO 7.9.0 offset header, then uses common register helpers such as `REG_GET_FIELD` and `REG_SET_FIELD` around SOC15/MMIO/PCI configuration accesses. This chunk supplies symbolic field names for PCIe AER/capability registers, RCC endpoint/downstream controls, sticky restore registers, and a large MSI-X vector table.

## Important Definitions

The opening `BIF_CFG_DEV0_EPF1_0` section completes and extends endpoint-function PCIe configuration-space capability definitions:

- AER uncorrectable error mask tail bits for atomic-operation egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked.
- AER uncorrectable error severity fields for DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked classifications.
- Correctable error status and mask fields for receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory nonfatal, internal correctable error, and header-log overflow.
- Advanced error capability/control fields for first-error pointer, ECRC generation/checking capability and enables, multi-header logging, TLP prefix log presence, and completion timeout log capability.
- Header log and TLP prefix log registers, each modeled as 32-bit `TLP_HDR` or `TLP_PREFIX` payload fields.
- BAR enhancement capability and per-BAR capability/control fields for BAR1 through BAR6, including supported size bitmaps, selected BAR index, total BAR count, active BAR size, and upper supported-size bits.
- Power budgeting fields: capability list metadata, data select, base power, scale, PM substate/state, type, power rail, and system-allocated indication.
- Dynamic Power Allocation fields: capability list, substate maximum, transition latency units/values, power allocation scale, latency indicator, current substate status, control enablement, and substate power allocation entries 0-7.
- ACS fields for capability and control: source validation, translation blocking, peer-to-peer request/completion redirection, upstream forwarding, egress control, direct translated peer-to-peer, enhanced capability, egress vector size, I/O request blocking, downstream/upstream memory target access controls, and unclaimed request redirection.
- PASID and ARI capability/control fields for process address-space IDs, execute/privileged mode support and enablement, maximum PASID width, ARI next function number, multifunction VC/ACS function groups, and function-group selection.

The RCC/RCCPFC sections describe nonstandard NBIO-side PCIe control and restore registers:

- `RCC_DEV0_1` fields for vendor-defined message support, bus-disable policy, DMA/disconnect behavior, memory/io decode checks, AER and LTSSM/root-complex behavior, local/remote ordering controls, requester ID restoration, LTR switch control, multi-host arbitration, and link margining parameters.
- `RCC_EP_DEV0_1` endpoint fields for scratch/control/status, interrupt control/status, configuration decode, LTR transmit policy, strap mirrors, function-0 DPA state, PME control, transmit control/requester ID, error controls, receiver error-ignore policy, completion-timeout controls, TPH handling, and per-generation link speed straps up through Gen5.
- `RCC_DWN_DEV0_1` downstream fields for reserved/scratch storage, hardware-init write lock, unsupported-request reporting, LTR unsupported-request handling, extended tag override, FLR extend mode, immediate PMI disable, AER completion timeout read-only disable, hidden register decode enables for Gen2-Gen5, and function/clock/64-bit/master-completion-timeout strap mirrors.
- `RCC_DWNP_DEV0_1` downstream-port fields for error reporting disable, AER header-log timeout, error message behavior, received-error clear bits, receiver ignore controls, FLR timeout control, Gen2-Gen5 link speed straps, data-link/link-bandwidth notification disables, multifunction strap mirror, and LTR message information from the endpoint.
- `RCC_PFC_AMDGFX` fields for programmed LTR snoop/nonsnoop latency values/scales/requirements, PME restore, sticky restore of selected AER status bits, TLP header/prefix restore payloads, and auxiliary power/current override.

The closing `PCIEMSIX` section begins `addressBlock: aid_nbio_nbif0_pciemsix_0_usb_MSIXTDEC` and defines the MSI-X table field layout for vectors 0 through 161, plus vector 162 address-low. Each complete vector has:

- `PCIEMSIX_VECTn_ADDR_LO__MSG_ADDR_LO`: low message address bits, shifted by 2 and masked with `0xFFFFFFFC`.
- `PCIEMSIX_VECTn_ADDR_HI__MSG_ADDR_HI`: high message address bits, full 32-bit mask.
- `PCIEMSIX_VECTn_MSG_DATA__MSG_DATA`: MSI-X message data, full 32-bit mask.
- `PCIEMSIX_VECTn_CONTROL__MASK_BIT`: per-vector mask bit at bit 0.

## APIs, Types, And Functions

There are no callable APIs, C types, or functions in this range. The exported interface is the generated macro namespace for NBIO 7.9.0 register fields.

Consumers combine these macros with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h` for register offsets and base indices.
- AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_SOC15_EXT`, `REG_GET_FIELD`, and `REG_SET_FIELD`.
- NBIO/RAS integration code that includes the header, including `amdgpu/nbio_v7_9.c` and `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`.

The macros encode only bit positions and masks. They do not encode access permissions, reset/default values, read-clear or write-one-to-clear semantics, firmware ownership, ordering requirements, or side effects.

## Control Flow

This header has no local runtime control flow. Runtime use is external and generally follows this pattern:

1. Driver code selects an NBIO 7.9.0 register offset for PCIe configuration, RCC control, RCCPFC restore, or MSI-X table state.
2. It reads the register through an AMDGPU SOC15/MMIO/PCI configuration access path.
3. It decodes a field with the matching `__SHIFT` and `_MASK`, or constructs a read-modify-write value while preserving unrelated bits.
4. Hardware applies the corresponding PCIe/NBIO behavior: AER reporting and classification, correctable-error masking, ECRC control, BAR sizing advertisement, DPA/PM policy, ACS/PASID/ARI capability exposure, RCC decode/error/link controls, sticky AER/TLP restore, LTR/PME/aux-power handling, or MSI-X interrupt delivery.

The order in the file follows the generated register database rather than an execution sequence. Similar names in status, mask, severity, control, clear, and restore registers can imply different hardware operations even when the bit positions are related.

## State And Persistence Behavior

The chunk owns no software state and persists nothing. It names fields whose state lives in NBIO hardware registers, PCIe configuration-space decode/shadow registers, RCC sideband/control registers, and MSI-X table storage. Persistence depends on PCIe reset rules, GPU/NBIO reset domains, firmware initialization, function-level reset, runtime power transitions, suspend/resume restore, and explicit driver writes.

Represented hardware state includes:

- Error state and policy: AER uncorrectable severity, correctable status/masks, header and TLP-prefix logs, RCC error reporting controls, received-error clear bits, receiver ignore controls, completion-timeout controls, and sticky restore fields for AER/TLP diagnostics.
- Configuration and capability state: BAR enhancement, power budgeting, DPA, ACS, PASID, ARI, VDM support, bus decode disables, requester ID restore, LTR, PME, aux power, strap mirrors, function enablement, multifunction capability, hidden register decode, and Gen2-Gen5 link speed strap fields.
- Operational interrupt state: MSI-X message address, message data, and per-vector mask bits for vectors 0-161, with vector 162 starting at the chunk boundary.

Callers must rely on hardware documentation and surrounding AMDGPU policy to decide which fields are read-only, sticky, write-one-to-clear, write-lockable, firmware-owned, security-sensitive, or unsafe to modify while the link/function is active.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.9.0 register-header set staying synchronized:

- `nbio_7_9_0_offset.h` supplies matching register offsets and base indices.
- Any generated default/reset header for NBIO 7.9.0, where present in the source tree, supplies reset values separately from these masks.
- AMDGPU's SOC15 register access layer, NBIO platform code, interrupt code, RAS code, PCIe support, and KFD/GPU memory-management paths consume NBIO register definitions indirectly.

Practical integration points are GPU PCIe and interrupt behavior rather than filesystem behavior: GPU PCIe enumeration, AER/RAS diagnosis, BAR sizing and resource setup, power budgeting, Dynamic Power Allocation, ACS/IOMMU isolation, PASID and ARI exposure for virtualization and process address spaces, LTR/PME/power restore, link training and Gen5 capability gating, endpoint/downstream port error policy, MSI-X table programming, interrupt masking, reset recovery, and debug register dumps.

## Risks And Edge Cases

- The chunk begins in the middle of `BIF_CFG_DEV0_EPF1_0_PCIE_UNCORR_ERR_MASK` and ends immediately after the `PCIEMSIX_VECT162_ADDR_HI` heading. Adjacent chunks are required for whole-register conclusions at both boundaries.
- A wrong generated shift or mask can compile cleanly while decoding or writing the wrong hardware bit, corrupting adjacent PCIe configuration, hiding errors, changing severity policy, misprogramming BAR capability, or masking the wrong MSI-X vector.
- AER status, mask, severity, control, and restore registers use overlapping terminology. Copying field handling between these groups can accidentally change fatality classification, suppress reporting, clear diagnostics, or restore stale error state.
- Correctable error status and RCC received-error clear fields may have sticky or write-one-to-clear behavior. Generic read-modify-write code can lose diagnostic evidence if it writes these registers without W1C-aware handling.
- ACS and PASID fields are security- and isolation-sensitive. Incorrect programming can affect IOMMU grouping, peer-to-peer routing, VFIO/passthrough assumptions, process-address-space routing, and privileged/executable PASID behavior.
- RCC hidden decode, strap mirror, link speed, FLR, LTR, PME, requester ID, and error-message controls are platform-sensitive. Misuse can destabilize PCIe links, break reset recovery, or create mismatches between advertised PCIe capabilities and hardware behavior.
- MSI-X table fields represent interrupt routing state. Incorrect address/data/mask handling can route interrupts to the wrong CPU vector, drop interrupts, violate expected per-vector masking, or race with the PCI/MSI core if accessed outside the kernel's MSI-X programming rules.
- Repeated `PCIEMSIX_VECTn_*` macro groups are mechanically similar. Off-by-one vector use or prefix mix-ups are easy to miss in review because every vector has the same field layout.
- Full-width `0xFFFFFFFFL` masks and narrow `0xFFL`/`0x01L` masks mix 32-bit and smaller configuration fields. Callers must preserve register width and reserved bits when composing writes.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.9.0 support. Compile failures catch malformed generated symbols, missing offsets, or mismatches between generated headers and driver users.
- Run generated-header consistency checks against the authoritative NBIO 7.9.0 register database: every field should have the expected shift/mask, every register should have a matching offset, and repeated MSI-X vector records should maintain the same four-register stride.
- Cross-check `BIF_CFG_DEV0_EPF1_0` PCIe capability fields against PCIe capability decoding from matching hardware, including AER, power budgeting, DPA, ACS, PASID, ARI, and BAR enhancement entries.
- Validate PCIe enumeration and diagnostics with tools such as `lspci -vv` on matching hardware: capability chain pointers, AER status/mask/severity, ACS/PASID/ARI capabilities, BAR sizing, power-management data, and link/PME behavior should decode coherently.
- Exercise GPU reset, FLR, suspend/resume, runtime power transitions, and PME/LTR restore paths to confirm RCC/RCCPFC state is preserved, restored, or reinitialized as intended.
- Exercise AER/RAS paths where available: correctable and uncorrectable error reporting, severity classification, header/TLP-prefix logs, sticky restore behavior, received-error clear bits, and error-message generation should match hardware expectations.
- Exercise MSI-X setup and interrupt handling: vector address/data programming, per-vector mask/unmask, interrupt delivery under load, reset recovery, and teardown should not lose or misroute interrupts.
- Validate ACS/IOMMU, PASID, ARI, and peer-to-peer DMA behavior on systems exposing these NBIO 7.9.0 blocks, especially in virtualization, passthrough, or process-address-space use cases.
