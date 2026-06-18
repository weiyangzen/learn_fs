# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 36941-39386

## Scope

This chunk is a generated AMDGPU NBIO 7.11.0 shift/mask header segment. It contains 2,127 `#define` macros and 317 register/address-block comments over 2,446 source lines. There are no functions, structs, enums, globals, allocations, locks, or executable statements in this range.

The range starts in the middle of `BIF_CFG_DEV1_RC0_PCIE_UNCORR_ERR_MASK`, covers the tail of the `BIF_CFG_DEV1_RC0` root-complex PCIe capability block, transitions at `addressBlock: nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`, then covers most of the `BIF_CFG_DEV1_EPF0_0` endpoint-function PCI/PCIe configuration block through lane 14 margining control. It ends immediately before `BIF_CFG_DEV1_EPF0_0_LANE_14_MARGINING_LANE_STATUS`, so adjacent chunks are required for both boundary register families.

Although this source mirror is under `sources/distributed-fs/ceph-client`, the file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem control path.

## Purpose

`nbio_7_11_0_sh_mask.h` is the bitfield-layout half of AMD's generated NBIO 7.11.0 register interface. For each hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, clear, preserve, or compose the field.

This chunk describes PCIe root-complex and endpoint-function configuration-space fields for device 1. The constants support AMDGPU code that needs to inspect or program PCIe error reporting, link negotiation, equalization, power-management, interrupt, virtual-channel, access-control, PASID, ARI, LTR, data-link feature, 16 GT/s PHY, and lane-margining registers without hard-coding bit positions at call sites.

## Important Macro Families

The opening `BIF_CFG_DEV1_RC0` section completes and extends a root-complex Advanced Error Reporting and secondary PCIe capability layout:

- AER uncorrectable error mask/severity bits for DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked.
- Correctable error status/mask bits for receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory nonfatal, and internal correctable error.
- AER control and logging fields: first error pointer, ECRC generation/check capabilities and enables, multi-header receive controls, four TLP header log words, root error command/status, error source IDs, and four TLP prefix log words.
- Secondary PCIe enhanced capability fields: capability ID/version/next pointer, link control 3 equalization triggers, lane error status, per-lane 8 GT/s equalization controls for lanes 0-15, ACS capability/control, Data Link Feature capability/status, 16 GT/s enhanced capability, 16 GT/s link cap/control/status, local and retimer parity mismatch status, per-lane 16 GT/s equalization controls for lanes 0-15, margining port capability/status, per-lane margining control/status for lanes 0-15, and RTR capability/data registers.

The `BIF_CFG_DEV1_EPF0_0` section begins after the address-block marker and describes the endpoint-function configuration space:

- Conventional PCI identity and header registers: vendor/device ID, command/status, revision and class-code bytes, cache-line/latency/header/BIST fields, BAR1-BAR6, adapter ID, ROM base, capability pointer, interrupt line/pin, grant/latency, and adapter/vendor capability words.
- Power-management and USB-like timing fields: PMI capability/list/status/control, SBRN, FLADJ, and DBESL/DBESLD fields.
- PCIe capability fields: PCIe capability header, device capability/control/status, link capability/control/status, device/link capability 2 and control/status 2, MSI and MSI-X capability/control/address/data/mask/pending/table/PBA fields, SATA capability/index/data, vendor-specific enhanced capability words, and virtual-channel capability/control/status/resource fields for VC0 and VC1.
- Endpoint AER and BAR enhanced capabilities: uncorrectable/correctable error status/mask/severity, AER cap/control, header logs, TLP prefix logs, BAR1-BAR6 capability/control, power-budgeting, and dynamic power allocation substate fields.
- Endpoint secondary PCIe and isolation/translation features: secondary link control 3, lane error status, lanes 0-15 8 GT/s equalization controls, ACS capability/control, PASID capability/control, LTR capability, ARI capability/control, Data Link Feature capability/status, 16 GT/s link/retimer/parity/equalization fields, margining port capability/status, and lane 0 through lane 14 margining controls/statuses through the chunk boundary.

The repeated lane families use consistent four-field patterns. Equalization control entries expose downstream/upstream transmit presets and receive preset hints. Margining lane control/status entries expose receiver number, margin type, usage model, and payload fields. This regularity is useful for generated-header consistency checks and for driver code that iterates lane instances through tables or macro-expanded accessors.

## APIs, Types, And Functions

There are no callable APIs or C data types in this range. The public interface is the generated C preprocessor namespace. The macro values are integer literals, mostly with an `L` suffix, and encode field geometry only.

These definitions do not encode register addresses, reset values, access width, read/write permissions, write-one-to-clear behavior, firmware ownership, hardware sequencing rules, or side effects. Runtime code must combine these masks with sibling address/default metadata and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the appropriate NBIO/SMN/PCIe configuration access path for the target register.

## Control Flow

This header has no local runtime control flow. Runtime behavior is external:

1. AMDGPU or platform code selects a `BIF_CFG_DEV1_RC0_*` or `BIF_CFG_DEV1_EPF0_0_*` register from sibling generated offset/SMN metadata.
2. Code reads a hardware register and decodes fields using the `__SHIFT` and `_MASK` constants, or composes a write while preserving unrelated and reserved bits.
3. The decoded or programmed value affects PCIe enumeration, link training, link speed/width negotiation, equalization, lane margining, ASPM/power management, MSI/MSI-X routing, AER/DPC-style diagnostics, ACS/PASID/ARI/LTR policy, VC mapping, BAR sizing/control, and endpoint/root-complex error reporting.

Many fields represent asynchronous hardware or protocol state rather than ordinary software state: AER status latches, TLP header/prefix logs, root error receive bits, data-link feature exchange status, link equalization request/completion bits, lane error vectors, 16 GT/s parity mismatch reports, retimer presence, margining command completion, power-management event status, MSI pending bits, VC negotiation/pending flags, and link status readbacks.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO PCIe root-complex and endpoint-function configuration registers. Persistence is determined by the GPU reset domain, PCIe fundamental or hot reset, link retrain, power-state transitions, firmware/BIOS setup, suspend/resume restore, and explicit AMDGPU writes.

Represented state includes writable control bits, read-only capability bits, readback status bits, policy masks, severity selectors, interrupt routing data, BAR controls, power-budget/DPA entries, link/equalization training state, lane margining commands and results, virtual-channel controls, ACS/PASID/ARI/LTR policy, and error/status logs. Some PCIe status fields are typically write-one-to-clear and some capability fields are read-only, but that access behavior is not visible in these shift/mask macros alone.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.11.0 register database and must stay synchronized with companion metadata for the same IP version:

- `nbio_7_11_0_offset.h` and `nbio_7_11_0_smn.h` provide address metadata for matching registers.
- `nbio_7_11_0_default.h`, when present for the register family, provides reset/default values.
- AMDGPU SOC15/NBIO register access helpers and generic bitfield helper macros apply these masks at runtime.

Integration points include AMDGPU NBIO bring-up, PCIe endpoint and root-complex configuration, GPU reset and resume restore, PCIe capability discovery, link retrain/equalization code, 16 GT/s PHY diagnostics, margining diagnostics, AER logging, MSI/MSI-X programming, BAR setup, VC/ACS/PASID/ARI/LTR feature enablement, power budgeting/DPA handling, and low-level debug or RAS flows that collect PCIe error context.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing writes to the wrong PCIe configuration bits, which can break link training, interrupt delivery, BAR decode, traffic isolation, power management, or error reporting.
- The chunk starts inside `BIF_CFG_DEV1_RC0_PCIE_UNCORR_ERR_MASK` and ends after `BIF_CFG_DEV1_EPF0_0_LANE_14_MARGINING_LANE_CNTL`; whole-file research must reconcile adjacent chunks before treating either boundary family as complete.
- AER and PCIe status/log registers often have ordering-sensitive clear semantics. Software should capture source IDs, header logs, prefix logs, and lane status before clearing status bits.
- Link equalization, retraining, 16 GT/s controls, and lane margining are asynchronous hardware operations. Writers need timeouts and must handle non-converging training, link down events, reset races, and retimer-related parity/status behavior.
- ACS, PASID, ARI, LTR, VC, and BAR controls affect DMA routing, isolation, address translation, latency reporting, and resource decoding. Incorrect programming can create enumeration failures or security/isolation regressions in virtualized systems.
- MSI/MSI-X address/data/mask/pending fields are interrupt-routing sensitive. Stale restore values or incorrect masks can drop, duplicate, or misroute interrupts.
- The RC0 and EPF0_0 prefixes describe different PCIe roles. Reusing a mask across the wrong instance may appear type-compatible because all values are plain macros, but it can target unrelated register layouts.

## Test Signals

- Build AMDGPU with NBIO 7.11.0 support enabled. Compile-time coverage catches missing, renamed, or malformed generated symbols referenced by consumers.
- Run generated-header consistency checks: every `__SHIFT` should have a compatible `_MASK`, masks should not overlap unexpectedly within a register, and repeated lane 0-15 families should match where the hardware layout is intended to be identical.
- Cross-check this chunk against `nbio_7_11_0_offset.h`, `nbio_7_11_0_smn.h`, and default-value metadata so each field layout maps to the expected register address and reset value.
- On supported hardware, validate PCIe enumeration, BAR decode, MSI/MSI-X delivery, negotiated link speed/width, link retraining, equalization status, 16 GT/s link status, suspend/resume restore, and GPU reset recovery.
- Exercise diagnostic/error paths: AER correctable and uncorrectable reporting, root error command/status reporting, TLP header/prefix log capture, lane error status reads, retimer parity mismatch reporting, Data Link Feature status, and lane margining command/status readback.
- For any code that writes these fields, inspect register traces to ensure reserved bits are preserved, status/log fields are cleared only after capture, and RC0 versus EPF0_0 instance selection matches the intended PCIe role.
