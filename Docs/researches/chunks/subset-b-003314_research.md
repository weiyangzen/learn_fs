# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 132800-135239

## Scope

This chunk is a generated AMD NBIO 7.7.0 shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, storage, locks, callbacks, or runtime control flow. The covered lines finish the `BIFPLR5_1` PCIe lane margining/CCIX/ESM/32 GT/s capability masks, then define most of the `addressBlock: nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` PCIe root-complex configuration-space view, and finally begin the analogous `addressBlock: nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp` block through `BIF_CFG_DEV1_RC1_DEVICE_CAP2`.

## Purpose and Register Families

The `BIFPLR5_1` tail provides field layouts for late PCIe extended capability surfaces:

- Lane margining controls and status for lanes 12-15, using repeated fields for receiver number, margin type, usage model, and payload/status payload.
- CCIX capability list/header registers, CCIX ESM capability/status/control fields, required ESM data-rate support bits, a reserved optional-capability register, and CCIX transaction format capability/control bits.
- Per-lane ESM equalization presets for lanes 0-15 at 20 GT/s and 25 GT/s, with separate downstream-port and upstream-port TX preset nibbles.
- 32 GT/s link capability/control/status fields for equalization bypass, no-equalization-needed support, modified training sequence usage modes, equalization phase success, link equalization requests, enhanced link behavior control, and transmitter precoding.

The `BIF_CFG_DEV0_RC1` block models a PCI-to-PCI bridge/root-port configuration space:

- Standard PCI identity, class, header, command, status, BAR, bus-number, bridge aperture, ROM, interrupt, and bridge-control fields.
- PM and PCIe capability-list fields, including device capability/control/status, link capability/control/status, slot capability/control/status, root control/capability/status, and PCIe capability version/type/message fields.
- PCIe 2.0+ capability fields: completion timeout, ARI/atomic-op support, LTR/OBFF, EETLP, emergency power reduction, link speeds, target speed, retraining, equalization, compliance, transmit margin, link disable, selected de-emphasis, and slot power-limit updates.
- MSI and MSI mapping registers, subsystem/vendor-specific capabilities, virtual-channel port/resource controls, device serial number, Advanced Error Reporting, root error reporting, header/TLP prefix logs, and secondary PCIe link-control/lane-error fields.
- Per-lane equalization controls for lanes 0-15, ACS capability/control, Data Link Feature capability/status, 16 GT/s PHY capability/control/status, local/retimer parity mismatch status, 16 GT/s lane equalization controls for lanes 0-15, and PCIe margining port/lane controls and statuses for lanes 0-15.

The `BIF_CFG_DEV1_RC1` block begins the same root-complex configuration-space pattern for device 1. This chunk covers its standard identity/class/header/bridge-window registers, PM and PCIe capability list, device/link/slot/root capability-control-status registers, and starts at `DEVICE_CAP2`. Later chunks should continue the rest of this device-1 view.

## Important APIs, Types, and Macros

The important exported symbols are generated bitfield constants:

- `REGISTER__FIELD__SHIFT` gives the field's least significant bit.
- `REGISTER__FIELD_MASK` gives the unshifted raw mask used against the register value.
- Names are grouped by register, with comment lines naming each register and `addressBlock` comments marking a hardware configuration block transition.

These constants are not callable APIs. In AMDGPU they are consumed by SOC15/NBIO register helpers and bitfield helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and field-write wrappers. The matching `nbio_7_7_0_d.h` register-address header supplies the register offsets; this `*_sh_mask.h` file supplies field layout.

No local type system exists in the chunk. The semantic "types" are the hardware register groups: status fields, control fields, capability fields, configuration-space aperture fields, MSI fields, AER log/status fields, per-lane equalization fields, and per-lane margining fields.

## Control Flow and Data Flow

There is no executable control flow in this header. Runtime data flow is indirect:

1. AMDGPU or PCI/NBIO code selects a register address from the companion address-definition header.
2. The driver reads or prepares a 16-bit or 32-bit register value.
3. A helper macro expands a field name into the `__SHIFT` and `_MASK` constants from this header.
4. The helper extracts a status/capability field or inserts a control value while preserving unrelated bits.
5. Hardware observes writes immediately in the relevant PCIe/NBIO power/reset domain, while status and log registers may be set asynchronously by link, error, hotplug, margining, or PME events.

For repeated lane registers, call sites typically select a register per lane and apply identical field semantics. The generated constants make each lane explicit, which avoids arithmetic in the header but makes correctness dependent on every lane-specific symbol matching the hardware specification.

## State and Persistence

The header has no software state or persistence. State represented by these masks lives in hardware:

- Configuration-space state includes command enables, bus numbers, bridge memory/I/O windows, BARs, interrupt routing, PM state, PCIe device/link/slot/root controls, MSI address/data, VC resources, ACS controls, DLF controls, and capability list pointers.
- Diagnostic and event state includes PCI status bits, link status, slot/root status, AER status/mask/severity/log fields, root error status/source IDs, TLP prefix logs, lane error status, parity mismatch status, margining status, CCIX ESM calibration status, and 32 GT/s equalization status.
- Link-training and PHY tuning state includes target/current link speed, equalization phase completion, per-lane equalization presets, 16/20/25/32 GT/s controls, margining request payloads, retimer-related fields, and transmitter precoding state.

Persistence follows hardware rules, not kernel memory lifetime. Some fields survive until reset or power-domain changes, some are initialized by firmware or PCI enumeration, and status/log bits may require hardware-specific clear sequences. A wrong mask or shift compiles cleanly but can persistently misprogram the device until the next reset or reinitialization.

## Dependencies and Integration Points

This file integrates with the generated AMDGPU ASIC register database under `drivers/gpu/drm/amd/include/asic_reg/nbio`. The chunk depends on:

- The matching `nbio_7_7_0_d.h` address definitions and the including NBIO/IP-version selection logic.
- AMDGPU register-access and bitfield helper macros that expect the exact generated naming convention.
- PCI/PCIe configuration-space semantics for bridge windows, PM capability, MSI, PCIe device/link/slot/root capabilities, AER, ACS, VC, DLF, PHY, lane equalization, margining, CCIX, and 32 GT/s link behavior.
- Firmware and PCI core enumeration defaults for device identity, class code, bus numbering, aperture sizing, and capability list linkage.

Primary integration consumers are low-level AMDGPU NBIO/PCIe setup, RAS and PCIe error handling, link-training diagnostics, hotplug/slot status paths, power management, virtualization/isolation features that care about ACS and VC configuration, and debug tooling that decodes NBIO registers.

## Risks and Edge Cases

- Generated mask/shift drift from the hardware database can silently corrupt all driver users of a field. Control fields such as bridge apertures, command bits, MSI programming, ACS controls, link target speed, equalization controls, DLF enablement, and margining requests are the highest-impact cases.
- Many status, mask, severity, and log registers share similar bit names and positions. Mixing AER status/mask/severity, root error status/command, header logs, or TLP prefix logs can suppress the wrong error or report misleading diagnostics.
- Configuration-space bridge windows and command bits are coordinated with PCI core enumeration. Direct writes outside expected sequencing can break memory routing, bus mastering, interrupt delivery, or downstream device visibility.
- Per-lane registers are highly repetitive. A single lane-specific typo in generated definitions may only appear on wide links, degraded links, or tests that exercise the affected lane.
- Margining and equalization controls interact with active PCIe links. Writing receiver, type, payload, preset, target-speed, retrain, or 32 GT/s control fields at the wrong time can disturb link training or produce misleading status.
- Capability masks indicate field layout, not feature presence. Software must read capability/status registers and ASIC feature data before assuming CCIX, ESM, DLF, ACS, VC, 16 GT/s, 25 GT/s, or 32 GT/s behavior is usable.
- Reserved fields, write-one-to-clear status fields, and hardware-owned bits require conservative read/modify/write behavior; treating all masks as normal writable configuration risks losing diagnostic evidence or setting undefined bits.

## Test and Validation Signals

Validation is indirect because the chunk is compile-time metadata:

- Build AMDGPU configurations that include `nbio_7_7_0_sh_mask.h`; missing or renamed field symbols should fail compilation at consumer sites.
- Compare `lspci -vv` or equivalent PCI config-space dumps on NBIO 7.7.0 hardware against decoded `BIF_CFG_DEV0_RC1` and `BIF_CFG_DEV1_RC1` identity, bridge-window, PM, PCIe, MSI, AER, ACS, VC, DLF, PHY, and margining capability fields.
- Exercise PCIe link training across x1/x4/x8/x16 widths and multiple speeds, checking link status, target speed, equalization completion, per-lane equalization fields, lane error status, 16 GT/s parity mismatch status, and 32 GT/s status bits.
- Run AER/RAS/DPC-style error injection or hardware error tests and confirm status, masks, severity, source IDs, header logs, TLP prefix logs, root error command/status, and interrupt routing decode correctly.
- Test suspend/resume, hot reset, FLR, and power-state transitions to ensure hardware state programmed through these masks is restored or reinitialized and that stale status bits do not produce false errors.
- Validate PCIe margining and CCIX/ESM paths only on platforms that advertise those capabilities, confirming request/control fields line up with status payloads and calibration-complete data-rate observations.
