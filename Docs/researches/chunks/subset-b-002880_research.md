# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 7324-9850

## Purpose

This chunk is part of the generated AMD NBIF 6.3.1 register field header. It defines C preprocessor constants for bit shifts and bit masks used to read, compose, and update PCIe/NBIO register fields for AMDGPU. The companion offset header supplies register addresses; this header supplies field layout. The chunk contains about 2,109 `#define`s across roughly 390 register names, mostly in one-to-one `__SHIFT` and `_MASK` pairs.

The slice starts in the tail of the `BIF_CFG_DEV0_EPF0_VF7` PCIe virtual-function capability space, covers the full `BIF_CFG_DEV0_EPF1` endpoint function configuration space, then moves through NBIF/BIF system, RCC downstream/upstream/endpoint, doorbell, RAS, BACO, HDP remap, framebuffer access, and BIF ring controls. It ends at the start of `nbif_rcc_dev0_BIFDEC1`.

## Important Definitions

There are no functions, structs, or runtime types in this chunk. The public API is the macro naming convention consumed by register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and display register table initializers.

Key macro families in this chunk:

- `BIF_CFG_DEV0_EPF0_VF7_*`: final PCIe capability fields for virtual function 7, including MSI-X table/PBA, vendor-specific capabilities, AER uncorrectable/correctable status/mask/severity, header/TLP-prefix logs, and ARI capability/control.
- `BIF_CFG_DEV0_EPF1_*`: endpoint function 1 PCI configuration and extended capability space. This includes standard PCI IDs and BARs, command/status, PM capability, PCIe capability, MSI/MSI-X, VSEC, device serial number, AER, resizable BAR, power budget, DPA, secondary PCIe capability, lane equalization, ACS, PASID, LTR, ARI, SR-IOV, and VF resizable BAR definitions.
- `BIF_BX_PF0_*`: PF0 MMIO/RSMU index/data access registers that act as indirect access windows.
- `BIF_BX0_*`: NBIF system registers for PCIe indirect access, S/BIOS/driver/firmware scratch registers, interrupt controls, GFX MMIO register CAM/remap controls, doorbell controls, framebuffer access enables, BACO power controls, HDP remap flush controls, BIF ring controls, mailbox index, MP1 interrupt state, and physical pad controls.
- `RCC_DWN_DEV0_0_*`, `RCC_DWNP_DEV0_0_*`, and `RCC_EP_DEV0_0_*`: RCC downstream, downstream-port, and endpoint-side PCIe control/status/strap fields, including link speed/control, LTR messaging, DPA power allocation, PME, requester ID, error, RX, and TX controls.

Representative high-impact fields include:

- `BIF_CFG_DEV0_EPF1_DEVICE_CNTL__INITIATE_FLR_MASK`, error reporting enables, max payload size, max read request size, relaxed ordering, no-snoop, and extended tag controls.
- `BIF_CFG_DEV0_EPF1_DEVICE_CNTL2__LTR_EN_MASK`, completion timeout, ARI forwarding, atomic operation, ID-based ordering, OBFF, and ten-bit tag controls.
- `BIF_CFG_DEV0_EPF1_PCIE_SRIOV_CONTROL__SRIOV_VF_ENABLE_MASK`, `SRIOV_VF_MSE`, migration enables, ARI hierarchy, and VF ten-bit tag requester enable.
- AER fields for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic egress blocking, TLP-prefix blocking, and poisoned TLP egress blocking.
- `BIF_BX0_BIF_FB_EN__FB_READ_EN_MASK` and `__FB_WRITE_EN_MASK`, which gate NBIF access to framebuffer memory.
- `BIF_BX0_REMAP_HDP_MEM_FLUSH_CNTL__ADDRESS_MASK` and `BIF_BX0_REMAP_HDP_REG_FLUSH_CNTL__ADDRESS_MASK`, which encode remapped KFD HDP flush registers.
- `BIF_BX0_BIF_DOORBELL_INT_CNTL__RAS_*`, `DOORBELL_INTERRUPT_*`, and `TIMEOUT_ERR_EVENT_INTERRUPT_ENABLE_MASK`, which expose RAS and doorbell interrupt status/clear/disable bits.
- `BIF_BX0_BACO_CNTL__BACO_EN_MASK`, `BACO_DUMMY_EN`, `BACO_POWER_OFF`, `BACO_MODE`, `RCU_BIF_CONFIG_DONE`, `PWRGOOD_VDDSOC`, and `BACO_AUTO_EXIT`, plus the BACO exit timer fields.
- `BIF_BX0_BIF_RB_CNTL__RB_ENABLE_MASK`, `RB_SIZE`, writeback, overflow-clear, FLR-reset-disable, and BIF ring pointer/base address fields.

## Control Flow And Data Flow

This file has no executable control flow. Its effect is compile-time expansion into constants used by the AMDGPU NBIF implementation and related display code.

The normal data flow is:

1. A driver source includes `nbif_6_3_1_offset.h` for register addresses and `nbif_6_3_1_sh_mask.h` for field positions.
2. The driver reads a 32-bit register with an SOC15 access macro, or receives a value from PCI config/indirect access.
3. `REG_GET_FIELD()` extracts a field by applying `<register>__<field>_MASK` and `<register>__<field>__SHIFT`.
4. `REG_SET_FIELD()` clears and inserts a field value using the same macro pair.
5. The updated value is written back through `WREG32_SOC15()` or a related MMIO helper.

Observed integration in this source tree:

- `amdgpu/nbif_v6_3_1.c` includes this header directly. It programs `BIF_BX0_REMAP_HDP_MEM_FLUSH_CNTL` and `BIF_BX0_REMAP_HDP_REG_FLUSH_CNTL` from `adev->rmmio_remap.reg_offset`, toggles framebuffer access through `BIF_BX0_BIF_FB_EN`, configures interrupt handling through `BIF_BX0_INTERRUPT_CNTL`, and manipulates `BIF_BX0_BIF_DOORBELL_INT_CNTL` for RAS ATHUB error-event interrupt enable/clear handling.
- The same implementation programs endpoint LTR behavior through `RCC_EP_DEV0_0_EP_PCIE_TX_LTR_CNTL` and PCIe config-space `PCI_EXP_DEVCTL2` when `CONFIG_PCIEASPM` is enabled.
- Display resource code such as `display/dc/resource/dcn401/dcn401_resource.c` uses `regBIF_BX0_*` offset names through `NBIO_SR()`-style macros. This chunk provides field masks, while the offset header provides addresses for those display-facing NBIF register tables.
- Similar field names also appear in adjacent NBIO generations, making this generated header part of a versioned hardware-description contract. Drivers select the proper header by IP version rather than probing field layout dynamically.

## State And Persistence Behavior

The macros themselves are stateless. The state they describe is hardware state in PCIe config space, NBIF MMIO registers, scratch registers, and power/interrupt control registers.

Persistent or semi-persistent hardware state described here includes:

- PCIe config-visible state for endpoint function 1 and VF7, such as BAR values, MSI/MSI-X state, AER status/masks, SR-IOV configuration, DPA allocation, ACS/PASID/LTR/ARI controls, and resizable BAR controls. Some fields are OS/programmed policy; others are capability or status fields owned by hardware/firmware.
- Scratch registers for SBIOS, BIOS, driver, and firmware, which are explicitly intended as cross-component communication or diagnostic storage across parts of device initialization and runtime.
- Doorbell and BIF ring state: enable bits, aperture behavior, interrupt status/clear bits, ring base/pointers, writeback address, and overflow status.
- BACO state and timers, which affect device power transitions and low-power exit sequencing.
- HDP remap addresses, which persist until reprogrammed and influence how later KFD/HDP flush requests reach hardware.

Because these are register definitions, persistence depends on reset domain. FLR, BACO, full GPU reset, PCIe link reset, and firmware initialization can each clear or reinterpret parts of this state.

## Dependencies And Integration Points

Direct dependencies:

- `nbif_6_3_1_offset.h` supplies matching `reg*` and `cfg*` addresses/base indices.
- SOC15 register access macros in AMDGPU provide `RREG32_SOC15()`, `WREG32_SOC15()`, `SOC15_REG_OFFSET()`, and field helper macros.
- Linux PCI helpers and constants, such as `pcie_capability_read_word()`, `pcie_capability_set_word()`, `pcie_capability_clear_word()`, and `PCI_EXP_DEVCTL2`, interact with the PCIe capability fields represented here.
- KFD remap constants such as `KFD_MMIO_REMAP_HDP_MEM_FLUSH_CNTL` and `KFD_MMIO_REMAP_HDP_REG_FLUSH_CNTL` are programmed through the HDP remap fields in this chunk.
- RAS handling uses `BIF_BX0_BIF_DOORBELL_INT_CNTL` status/clear/disable fields before calling higher-level RAS interrupt flow.

Integration points:

- AMDGPU NBIF IP block setup, especially `nbif_v6_3_1.c`.
- GPU reset and power management paths that need BACO and FLR-related fields.
- Interrupt and RAS setup paths that use doorbell interrupt controls and AER status/mask/severity fields.
- SR-IOV/vGPU paths that rely on endpoint function, virtual function, ARI, ACS, PASID, and SR-IOV capability definitions.
- Display resource initialization that builds NBIO register tables from matching offset names.

## Risks

- Generated-header drift: a wrong shift or mask silently corrupts unrelated register bits. This is especially risky for packed PCIe fields such as command/status, device control, AER status, SR-IOV control, BACO control, and doorbell interrupt control.
- Name/address mismatch: these masks must match `nbif_6_3_1_offset.h`. Reusing a field macro with the wrong generation or wrong `reg*` address can produce valid C that programs the wrong hardware field.
- Read-modify-write hazards: status/clear registers such as AER and doorbell interrupt controls may have write-one-to-clear or mixed status/control semantics. Generic field updates must preserve reserved bits and avoid accidentally clearing latched status.
- Virtualization sensitivity: EPF1, VF7, SR-IOV, ARI, ACS, PASID, and VF BAR fields are security and isolation relevant. Incorrect masks could expose memory apertures, break VF enumeration, or interfere with function-level reset.
- Power sequencing sensitivity: BACO enable, dummy enable, auto-exit, timer, and power-good fields can hang resume, leave the device inaccessible, or cause spurious reset interrupts if misprogrammed.
- Interrupt routing risk: doorbell/RAS interrupt status, clear, disable, vector-select, and BIF ring bits influence whether faults reach the interrupt handler or remain latched.

## Test Signals

Useful validation signals for this chunk are hardware- and integration-oriented:

- Build coverage for `amdgpu/nbif_v6_3_1.c` and display resource code that includes the NBIF 6.3.1 headers; compile failures catch missing or renamed field macros.
- Boot and probe on NBIF 6.3.1 hardware with successful AMDGPU initialization, no MMIO timeout, and correct NBIF IP version selection.
- Framebuffer access smoke tests: enabling/disabling MC access through `BIF_BX0_BIF_FB_EN` should not break VRAM access, GPU memory tests, or display bring-up.
- KFD/HDP flush tests should confirm remapped HDP flush registers work after `nbif_v6_3_1_remap_hdp_registers()`.
- RAS interrupt tests should exercise `BIF_BX0_BIF_DOORBELL_INT_CNTL` enable/disable, status detection, and clear paths, including the no-BIF-ring ATHUB handling path.
- ASPM/LTR tests under `CONFIG_PCIEASPM` should verify LTR enablement and link power transitions without malformed PCIe errors.
- SR-IOV tests should validate PF/VF enumeration, VF BAR sizing, ARI/ACS/PASID exposure, FLR behavior, and VF memory-space enablement.
- BACO suspend/resume and runtime power-management tests should check entry/exit completion, `BACO_EXIT_*` timing, and `BACO_EXIT_DONE` interrupt behavior.
- PCIe AER injection or error-reporting tests should verify uncorrectable/correctable status, mask, severity, header-log, and TLP-prefix-log fields line up with hardware-visible error reports.
