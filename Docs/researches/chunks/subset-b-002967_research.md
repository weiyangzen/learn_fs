# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 14940-17466

## Scope

This chunk covers 2,527 lines from the generated NBIO 4.3.0 shift/mask header. It starts in the tail of the `BIF_CFG_DEV0_EPF2_0_DEVICE_CAP2` register and ends inside `BIF_BACO_EXIT_TIMER1`, after the `BACO_EXIT_SIDEBAND_TIMER` and `BACO_HW_AUTO_FLUSH_EN` shift definitions but before their masks. Within the range there are 379 register/comment sections, about 996 `__SHIFT` definitions, and about 1,140 `_MASK` definitions.

The covered range is a hardware bitfield map only. It has no C functions, structs, variables, executable branches, or in-memory persistence. It defines preprocessor constants consumed by AMDGPU NBIO, SMU, RAS, PCIe, power-management, and virtualization paths together with register offsets from `nbio_4_3_0_offset.h`.

## Purpose

The header is the bit-level ABI for programming AMD NBIO 4.3.0 registers. Each register field is represented by the usual pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to right-shift extracted fields or position new values.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, or compose the field.

Driver code combines these macros with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`. The companion offset header provides addresses such as `regRCC_EP_DEV0_0_EP_PCIE_TX_LTR_CNTL`, `regBIF_BX0_BIF_DOORBELL_INT_CNTL`, and `regBIF_BX0_BIF_FB_EN`; this header supplies the field encodings.

## Important Macro Families

### EPF2 PCIe Capability Tail

The chunk begins in the final fields of `BIF_CFG_DEV0_EPF2_0_DEVICE_CAP2`, including completion timeout support, ARI forwarding, AtomicOp support, LTR, TPH completer support, 10-bit tag support, OBFF, TLP prefix support, emergency power reduction, and FRS support.

It then covers EPF2 Device Control/Status 2 and Link Capability/Control/Status 2 fields:

- Device Control 2 fields configure completion timeout, ARI forwarding, AtomicOp request/egress behavior, IDO request/completion, LTR enablement, emergency power reduction requests, 10-bit tag requester enablement, OBFF, and TLP prefix blocking.
- Link Capability 2 and Link Control 2 define supported PCIe speeds up to the hardware-advertised mask, crosslink, skip ordered-set support, retimer presence detection, DRS support, target link speed, compliance entry, autonomous speed disable, deemphasis, transmit margin, and compliance SOS.
- Link Status 2 exposes equalization completion and phases, equalization requests, retimer detection, crosslink resolution, downstream component presence, and DRS message status.

These fields are PCIe config-space representations for function 2. A mismatch between these masks and the real hardware layout would cause Linux PCIe capability programming to toggle or report the wrong bits.

### EPF2 MSI, MSI-X, Vendor, AER, BAR, Power, DPA, ACS, PASID, ARI, and RTR

The EPF2 section includes conventional MSI and MSI-X capability fields: capability IDs and next pointers, MSI enable/multiple-message/64-bit/per-vector/extended-data controls, MSI address/data/mask/pending registers, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.

The extended capability macros cover:

- Vendor-specific enhanced capability headers and scratch registers.
- PCIe Advanced Error Reporting status, mask, and severity fields for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, multicast blocked TLP, AtomicOp egress blocking, TLP prefix blocking, and poisoned TLP egress blocking.
- Correctable error status/mask fields for receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal error, corrected internal error, header log overflow, and optional semantic-error classes.
- AER capability/control fields for first error pointer, ECRC generation/checking capability and enablement, multiple header recording, TLP prefix log presence, completion timeout prefix/header log capability, and poison TLP egress blocking.
- Header log and TLP prefix log registers, each represented as full-width log data.
- BAR enhanced capability controls for BAR1 through BAR6, including capability flags and 64-bit/memory/io/prefetch/size fields.
- Power budget, Dynamic Power Allocation, Access Control Services, PASID, ARI, and Reset Time Reporting capability/control/data fields.

These macros mostly describe PCIe capability state exposed to the host and firmware. They can be read for diagnostics and may be written by low-level setup code when advertising or masking device capabilities.

### EPF3 Complete PCI Configuration Space

Lines 15596-16611 introduce `addressBlock: nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`, a full config-space map for endpoint function 3. It includes:

- Standard PCI header fields: vendor/device ID, command, status, revision, class code, cache line, latency, header type, BIST, BAR1-BAR6, CardBus CIS pointer, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- Vendor capability and power management capability/status fields, including power state, PME control/status, data select/scale, B2/B3 support, and bus power enable.
- PCIe capability, Device/Link Capability/Control/Status, Device/Link 2, MSI/MSI-X, vendor-specific, AER, BAR, power budget, DPA, ACS, PASID, ARI, and RTR groups with the same general semantics as the EPF2 capability tail.

The EPF3 command and status fields include bus master, memory/io enable, interrupt disable, parity/SERR, target/master abort, system error, and parity detected state. EPF3 Device/Link fields include max payload/read request, phantom functions, extended tags, relaxed ordering, no-snoop, bridge config retry, FLR, ASPM/link disable/retrain/common-clock, slot clock config, link bandwidth management, equalization, LTR, OBFF, and TLP prefix controls. These definitions matter for multi-function or SR-IOV-related device exposure because they encode per-function configuration semantics.

### Indirect PCIe Access and Scratch Windows

The `nbio_nbif0_bif_bx_SYSDEC` block defines indirect access and scratch registers:

- `PCIE_INDEX`, `PCIE_DATA`, `PCIE_INDEX2`, `PCIE_DATA2`, `PCIE_INDEX_HI`, and `PCIE_INDEX2_HI` provide indexed PCIe register windows.
- `SBIOS_SCRATCH_0` through `SBIOS_SCRATCH_15`, `BIOS_SCRATCH_0` through `BIOS_SCRATCH_15`, `DRIVER_SCRATCH_0` through `DRIVER_SCRATCH_15`, and `FW_SCRATCH_0` through `FW_SCRATCH_15` are full-width scratch registers for firmware, BIOS, driver, and SBIOS coordination.
- `BIF_EngineA_INTR_CNTL` and `BIF_EngineB_INTR_CNTL` expose per-engine interrupt status/ack/enable fields for poll, read, write, and trap conditions.
- `GFX_MMIOREG_CAM_ADDR0-7`, `GFX_MMIOREG_CAM_REMAP_ADDR0-7`, and related CAM completion/control registers describe MMIO register remapping windows and completion behavior.

Scratch registers are persistent hardware state across short driver phases and can carry firmware/driver handoff information. They are not C storage; reads and writes affect device registers.

### Downstream and Endpoint PCIe Control Blocks

The `nbio_nbif0_rcc_dwn_dev0_BIFDEC1`, `nbio_nbif0_rcc_dwnp_dev0_BIFDEC1`, and `nbio_nbif0_rcc_ep_dev0_BIFDEC1` blocks define lower-level PCIe link, error, configuration, LTR, DPA, strap, and DVSEC controls.

Important downstream fields include:

- `DN_PCIE_CNTL`, `DN_PCIE_CONFIG_CNTL`, `DN_PCIE_RX_CNTL2`, `DN_PCIE_BUS_CNTL`, and `DN_PCIE_CFG_CNTL` for unsupported-request reporting, malformed atomic operations, hidden register decode, invalid PASID handling, immediate PMI behavior, and generation-specific hidden register decode.
- `DN_PCIE_STRAP_F0`, `DN_PCIE_STRAP_MISC`, and `DN_PCIE_STRAP_MISC2` for F0 DPA/PASID support and TPH/multifunction strap behavior.
- `PCIE_ERR_CNTL`, `PCIE_RX_CNTL`, `PCIE_LC_SPEED_CNTL`, and `PCIE_LC_CNTL2` for AER reporting disablement, header-log timeout, immediate error messages, clearing received errors, ignoring RX protocol classes, completion timeout disablement, link generation strap enablement, and link bandwidth/state notifications.

Important endpoint fields include:

- `EP_PCIE_CNTL`, `EP_PCIE_INT_CNTL`, and `EP_PCIE_INT_STATUS` for UR reporting, malformed atomic handling, LTR-message UR behavior, corrected/nonfatal/fatal/user/misc/power-state interrupt enablement and status.
- `EP_PCIE_TX_LTR_CNTL` for snooped and non-snooped private LTR values, LTR requirement bits, disabling LTR messages outside D0, resetting LTR when data link is down, checking flow control for L1, and D-state-driven LTR write data.
- Function 0 and function 1 DPA capability, latency, control, and eight substate power allocation registers.
- Endpoint TX control and requester ID fields for SNR/relaxed-ordering override, per-function TPH disablement, and requester ID bus/device/function composition.
- Endpoint error/RX/link-control fields for AER header log timers across functions 0-7, poisoned advisory nonfatal strap, invalid PASID/not-PASID/prefix/TPH receive handling, and Gen2-Gen5 link-speed straps.
- `DVSEC_PRIV_CNTL*` and `DVSEC_VF_PRIV_CNTL*` full-width private DVSEC registers.

The concrete direct consumer observed in `amdgpu/nbio_v4_3.c` is `nbio_v4_3_program_ltr()`, which reads `regRCC_EP_DEV0_0_EP_PCIE_TX_LTR_CNTL`, programs a target value, and explicitly clears `EP_PCIE_TX_LTR_CNTL__LTR_PRIV_MSG_DIS_IN_PM_NON_D0_MASK` and `EP_PCIE_TX_LTR_CNTL__LTR_PRIV_RST_LTR_IN_DL_DOWN_MASK` before writing the register back when needed.

### BIF/BX Control, Interrupts, Doorbells, Framebuffer Access, and BACO

The final `nbio_nbif0_bif_bx_BIFDEC1` block defines general NBIO bus interface controls:

- `BIF_MM_INDACCESS_CNTL`, `BUS_CNTL`, `MM_CFGREGS_CNTL`, and `BX_RESET_CNTL` gate indirect MMIO access, VGA/HDP coherency and flush stalls, zero-byte-enable behavior, transaction-class selection, config-space function/device selection, MM write-to-config enablement, and link training.
- `INTERRUPT_CNTL` and `INTERRUPT_CNTL2` configure IH dummy reads, nonsnoop/relaxed-ordering interrupt requests, interrupt delay, general IH interrupt enablement, dummy-read bypass in MSI, and dummy-read address.
- `CLKREQB_PAD_CNTL` defines pad control, slew, wake, Schmitt enable, output, and enable bits.
- `BIF_FEATURES_CONTROL_MISC` and `HDP_ATOMIC_CONTROL_MISC` expose request/completion error path disables, MSI vector behavior, BIF ring overflow, atomic error interrupt disablement, non-virtual bus-master handling, HDP outstanding limits, 48-bit GPA aperture checking for doorbell self-ring, and HDP atomic outstanding limits.
- `BIF_DOORBELL_CNTL` controls self-ring, translation checks, untranslated loopback, non-consecutive byte-enable policy, monitor enablement, and monitor interrupt generation modes.
- `BIF_DOORBELL_INT_CNTL` exposes doorbell/RAS/ATHUB interrupt status, clear, enable, disable, and "set status when ring buffer enabled" bits.
- `BIF_FB_EN` gates framebuffer reads and writes. The prefixed version of the same concept, `BIF_BX0_BIF_FB_EN`, is used by `nbio_v4_3_mc_access_enable()` to enable or disable memory-controller framebuffer access.
- `BIF_INTR_CNTL`, `BIF_MST_TRANS_PENDING_VF`, and `BIF_SLV_TRANS_PENDING_VF` cover RAS interrupt vector selection and pending master/slave VF transactions.
- `BACO_CNTL`, `BIF_BACO_EXIT_TIME0`, and the beginning of `BIF_BACO_EXIT_TIMER1` define bus-active chip-off controls: BACO enable, dummy enable, power-off, D-state bypass, reset interrupt mask, BACO mode, RCU BIF config done, VDDSOC power-good, auto-exit, and exit timers.

`amdgpu/nbio_v4_3.c` also uses the doorbell interrupt area for RAS ATHUB error events. It reads `regBIF_BX0_BIF_DOORBELL_INT_CNTL`, toggles the RAS ATHUB interrupt disable bit when enabling/disabling the IRQ source, checks `BIF_DOORBELL_INT_CNTL__RAS_ATHUB_ERR_EVENT_INTERRUPT_STATUS`, sets `BIF_DOORBELL_INT_CNTL__RAS_ATHUB_ERR_EVENT_INTERRUPT_CLEAR`, writes the register back, and invokes the global RAS ISR when BIF ring handling is disabled.

## Control Flow

There is no local control flow in this chunk. The runtime flow is imposed by consumers:

1. Include `nbio_4_3_0_offset.h` and `nbio_4_3_0_sh_mask.h`.
2. Read a SOC15 register with `RREG32_SOC15` or via an indexed PCIe access path.
3. Extract fields with `REG_GET_FIELD` or clear/compose fields with masks and shifts.
4. Write changed values back with `WREG32_SOC15` or field-specific helpers.
5. For status/clear registers, poll status bits or write clear bits according to the hardware contract.

Register operations are order-sensitive. For example, LTR programming must preserve unrelated bits while clearing only the two LTR disable/reset bits; RAS doorbell handling must clear the interrupt status after observing it; BACO and link/power fields normally participate in larger power-state sequences coordinated with SMU or firmware.

## State and Persistence

The macros themselves are compile-time constants and persist only in object code after preprocessing. The state they address is hardware state:

- PCIe config-space capability bits advertise device/function behavior to the host and may persist across driver phases until reset or firmware reinitialization.
- Scratch registers can carry handoff data between SBIOS, BIOS, firmware, and the driver.
- Doorbell interrupt status/clear bits are event state and must be serviced carefully to avoid lost or repeated interrupts.
- LTR, DPA, ASPM/link, RX ignore, and AER controls alter live PCIe behavior.
- `BIF_FB_EN`, transaction pending bits, and BACO controls affect memory access, virtualization teardown/reset safety, and power transitions.

Because this is generated hardware ABI data, persistence behavior is determined by the underlying register block, reset domain, and firmware policy rather than by this header.

## Dependencies and Integration Points

Key dependencies are:

- `nbio_4_3_0_offset.h` for register addresses and base indices.
- AMDGPU register helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.
- SOC15 NBIO IP versioning and register routing.
- Linux PCI/PCIe concepts: standard config header, MSI, MSI-X, PM, PCIe capability, AER, DPA, ACS, PASID, ARI, LTR, OBFF, FLR, and link equalization.
- AMDGPU NBIO, SMU, RAS, interrupt, doorbell, SR-IOV, and power-management code.

Observed includes/users in this source tree include `amdgpu/nbio_v4_3.c`, `pm/swsmu/smu13/smu_v13_0_0_ppt.c`, and `pm/swsmu/smu13/smu_v13_0_7_ppt.c`. Direct use from this specific chunk includes the endpoint LTR control masks in `nbio_v4_3_program_ltr()` and unprefixed `BIF_DOORBELL_INT_CNTL` field names in RAS ATHUB interrupt handling. Similar or prefixed equivalents exist earlier in the same header, so consumers can mix prefixed register names (`BIF_BX0_BIF_DOORBELL_INT_CNTL`) with unprefixed field names (`BIF_DOORBELL_INT_CNTL`) when the field layout is identical.

## Risks

- Bitfield drift is high impact. If generated masks or shifts do not match the silicon register layout, the driver can silently program unrelated PCIe, doorbell, power, or error-reporting bits.
- The slice boundary is mid-register for `BIF_BACO_EXIT_TIMER1`; merge/reconciliation must combine the following chunk before treating that register as fully documented.
- Many fields are write-one-to-clear, status, or command-like strobes. Treating all masks as ordinary persistent configuration can lose events or trigger unintended hardware actions.
- PCIe capability fields interact with Linux PCI core assumptions. Incorrect ACS/PASID/ARI/DPA/AER/LTR advertisement or enablement can break IOMMU isolation, peer-to-peer behavior, power management, or error recovery.
- Doorbell and RAS interrupt bits are shared between normal driver interrupt flow, RAS, and BIF ring behavior. Incorrect status clearing or disable-bit polarity can suppress critical RAS events or cause repeated interrupts.
- BACO, framebuffer access, link training, and transaction-pending fields are power/reset sensitive. Writes outside the expected SMU/NBIO sequence can hang memory access, strand VF transactions, or fail power transitions.
- Scratch registers are coordination channels; treating them as disposable debug storage can overwrite firmware or driver handoff state.

## Test Signals

Useful validation signals for changes touching these definitions or consumers include:

- Build coverage for AMDGPU with NBIO 4.3.0 and SMU 13 paths enabled, catching missing or renamed macro definitions.
- Runtime boot/probe on NBIO 4.3.0 hardware, checking that PCI config space enumerates all functions, BARs, MSI/MSI-X, AER, ACS, PASID, ARI, and power capabilities as expected.
- ASPM/LTR validation under `CONFIG_PCIEASPM`: verify `nbio_v4_3_program_ltr()` writes `regRCC_EP_DEV0_0_EP_PCIE_TX_LTR_CNTL` without disabling private LTR messages unexpectedly and honors `pdev->ltr_path`.
- RAS ATHUB interrupt testing with BIF ring disabled: inject or simulate an ATHUB RAS event, observe `RAS_ATHUB_ERR_EVENT_INTERRUPT_STATUS`, verify the clear bit is written, and confirm the global RAS ISR runs once.
- Doorbell tests for self-ring, monitor, and interrupt generation behavior, including SR-IOV/VF cases where transaction-pending and VF reset bits matter.
- BACO enter/exit and suspend/resume stress, especially around `BACO_CNTL` mode/power-good/config-done/auto-exit and the exit timer registers split across this and the next chunk.
- PCIe AER injection or error-reporting tests for correct fatal/nonfatal/correctable status, mask, severity, header log, and TLP prefix log behavior.
- Static generation checks that every `__SHIFT` has a matching `_MASK` within the complete file, allowing for chunk boundaries where a pair may be split.
