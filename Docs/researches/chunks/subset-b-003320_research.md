# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 147481-149938

## Scope

This chunk is a generated AMD NBIO 7.7.0 shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, runtime branches, allocation, locking, persistence code, or direct register access. The constants define bit positions and masks for NBIO/BIF PCI configuration-space registers in AMDGPU's ASIC register headers.

The range contains 2,124 `#define` entries: 1,057 `__SHIFT` constants and 1,067 `_MASK` constants. The imbalance is caused by chunk boundaries and by this slice beginning and ending inside register definitions. The first line continues `BIF_CFG_DEV0_EPF7_1_DEVICE_CNTL2`, whose earlier field shifts are in the previous chunk, and the final line stops before `BIF_CFG_DEV1_EPF1_1_VENDOR_CAP_LIST__LENGTH_MASK`, which is on the next source line outside this work item.

## Purpose

NBIO is the GPU northbridge and PCIe-facing I/O block. This slice defines the bit-level ABI for PCIe endpoint/function configuration regions exposed through the NBIO 7.7.0 register map:

- The tail of `DEV0_EPF7`, covering PCIe capability 2 controls, link capability/control/status 2, MSI/MSI-X, SATA capability and indexed data-port fields, vendor-specific PCIe extended capability, AER, enhanced BAR capability, power budget, dynamic power allocation, ACS, PASID, and ARI.
- The full `addressBlock: nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`, covering the standard PCI header, PM capability, PCIe base capability, MSI/MSI-X, vendor-specific and virtual-channel extended capabilities, AER, enhanced BAR capability, power budget, DPA, secondary PCIe link/lane equalization, ACS/PASID/LTR/ARI, data link feature, 16 GT/s PHY, and PCIe margining lane controls/status for lanes 0 through 15.
- The beginning of `addressBlock: nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`, covering the standard PCI header and vendor capability list through the first two masks of `VENDOR_CAP_LIST`.

The public interface pattern is:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for extracting, testing, or composing that field.

Runtime code uses these macros with register offsets from `nbio_7_7_0_offset.h` and AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The `DEV0_EPF7` continuation starts at `DEVICE_CNTL2`, defining masks for completion timeout value/disable, ARI forwarding enable, atomic operation request and egress blocking, IDO request/completion enablement, LTR, emergency power reduction, 10-bit tag requester enablement, OBFF, and end-to-end TLP prefix blocking. It then maps `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`, including supported link speeds, crosslink support, lower SKP ordered-set support, RTM presence detection, DRS support, target link speed, compliance controls, de-emphasis, equalization phases, downstream presence, and DRS message reception.

The `DEV0_EPF7` interrupt capability area covers MSI and MSI-X capability list pointers, MSI enable/multi-message/64-bit/per-vector/extended-data fields, MSI message address/data registers, MSI mask and pending registers, MSI-X table size/function mask/enable, MSI-X table BIR/offset, and MSI-X PBA BIR/offset. These are the field maps used when PCI interrupt capability state is read, restored, virtualized, or debugged.

The `DEV0_EPF7` SATA and vendor-specific regions define SATA capability headers, BAR location/offset, IDP index/data, PCIe vendor-specific enhanced capability list/header fields, and two scratch registers. The AER region maps uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header log registers, and TLP prefix logs. Important status bits include data link protocol error, surprise down, poisoned TLP, flow-control protocol error, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic egress block, TLP prefix blocked, receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal error, corrected internal error, header-log overflow, and completion-timeout log support.

The `DEV0_EPF7` BAR, power, and DPA extended capabilities define enhanced BAR capability/control for BAR1 through BAR6, power-budget data select/data/capability fields, DPA capability, latency indicator, DPA status/control, and eight DPA substate power allocation entries. The access-control/request-routing tail defines ACS capability/control bits, PASID capability/control, and ARI capability/control fields.

The `DEV1_EPF0` address block begins with the standard PCI configuration header: vendor/device ID, command, status, revision and class code, cache line, latency timer, header/BIST, six BARs, CardBus CIS pointer, subsystem identity, ROM base address, capability pointer, interrupt line/pin, min grant, max latency, vendor capability list, and adapter ID write fields. Command/status fields include I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, parity/SERR, interrupt disable, immediate readiness, capability-list presence, abort/error status, DEVSEL timing, and parity detection.

The `DEV1_EPF0` PM and PCIe base capability families include PMI capability/status/control, SBRN, FLADJ, DBESL/DBESLD, PCIe capability list/header, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2. These cover payload and read request sizing, phantom/extended tags, endpoint latency, role-based error reporting, FLR, relaxed ordering, no-snoop, AUX power, transaction pending, ASPM, RCB, link disable/retrain, common clock, extended sync, clock power management, autonomous width, link bandwidth notifications, completion timeout, ARI, atomic operations, IDO, LTR, OBFF, 10-bit tags, supported speeds, compliance, de-emphasis, and equalization state.

The `DEV1_EPF0` MSI/MSI-X, SATA, and vendor-specific capability groups mirror the `DEV0_EPF7` layout for the dev1 function 0 aperture. The virtual-channel region adds VC enhanced capability list, port VC capability/control/status, and VC0/VC1 resource capability/control/status fields for arbitration table capability, VC arbitration selection/loading, negotiation pending state, TC/VC maps, reject-snoop behavior, maximum time slots, arbitration selection/loading, and VC identifiers.

The `DEV1_EPF0` AER, enhanced BAR, power budget, and DPA families mirror the same error, diagnostic, aperture, and power allocation concepts for this function. The secondary PCIe capability adds link control 3, lane error status, and per-lane equalization control for lanes 0 through 15. Each lane equalization register maps downstream/upstream port transmit preset fields and preset hints.

The `DEV1_EPF0` later extended capability families define ACS capability/control, PASID capability/control, LTR capability, ARI capability/control, data link feature capability/status, PCIe PHY 16 GT/s capability/control/status, parity mismatch status registers, per-lane 16 GT/s equalization control for lanes 0 through 15, margining port capability/status, and margining lane control/status for lanes 0 through 15. The margining lane registers consistently encode receiver number, margin type, usage model, and payload/status payload fields.

The `DEV1_EPF1` block starts a new endpoint/function aperture and maps the same standard PCI header pattern through `VENDOR_CAP_LIST`. This chunk ends in that vendor capability list definition, so the next chunk is required for the final `LENGTH_MASK` and any following capabilities.

## Control Flow

There is no executable control flow in this header chunk. Runtime behavior is imposed by consumers:

1. ASIC-specific AMDGPU code includes `nbio_7_7_0_offset.h` for register addresses and `nbio_7_7_0_sh_mask.h` for fields.
2. The driver selects the NBIO, SOC15, or PCIe-port register aperture and reads a register.
3. The driver uses generated shifts and masks, usually through `REG_SET_FIELD` or `REG_GET_FIELD`, to compose writes or interpret status.
4. Hardware semantics determine whether a field is read-only, writable, write-one-to-clear, sticky, self-clearing, reset by FLR, or reset only by a wider GPU/platform reset.

Chunk boundaries are not semantic boundaries. This range begins in `BIF_CFG_DEV0_EPF7_1_DEVICE_CNTL2` and ends in `BIF_CFG_DEV1_EPF1_1_VENDOR_CAP_LIST`, so adjacent chunks are needed before making complete per-register claims for those two boundary registers.

## State And Persistence Behavior

The header stores no software state. It describes hardware-backed PCI configuration and PCIe extended capability state in the NBIO/BIF block.

Configuration-like state in this slice includes PCI command bits, BAR and ROM decode fields, MSI/MSI-X message and mask state, PCIe device/link controls, completion timeout controls, ARI/atomic/IDO/LTR/OBFF/10-bit tag controls, VC controls, enhanced BAR controls, DPA controls, ACS controls, PASID controls, LTR capability values, data-link feature controls, PHY 16 GT/s controls, and margining lane controls.

Status-like state includes PCI status/error bits, interrupt status, link state, equalization results, AER correctable and uncorrectable error state, AER header and TLP prefix logs, MSI pending bits, VC negotiation state, DPA status, lane error status, data-link feature status, PHY 16 GT/s link/parity status, and margining port/lane status.

Persistence is hardware-defined. Capability fields commonly reflect straps or generated hardware capability tables. Writable configuration may survive until FLR, function reset, link reset, suspend/resume, or full GPU reset depending on the register. Error and diagnostic status/log registers may be sticky until cleared through PCIe/AER-defined sequences. Consumers cannot infer access type or persistence from a mask name alone.

## Dependencies And Integration Points

This chunk is paired with the generated NBIO 7.7.0 offset and consumer code:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h` supplies register offsets and base indices for the register names whose fields are defined here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h` supplies the field masks and shifts documented in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes this header and registers `nbio_v7_7_funcs`.

The direct NBIO 7.7 implementation uses the same generated-mask pattern for revision ID extraction, framebuffer access enablement, doorbell ranges and apertures, interrupt control, HDP flush registers, PCIe index/data offsets, clock gating, light sleep, register remap, and init-time hardware setup. The exact PCI config-space fields in this chunk are lower-level capability maps that may be consumed by PCIe accessors, SR-IOV/PF policy, firmware bring-up, diagnostics, AER handling, platform workarounds, or future driver paths even when `nbio_v7_7.c` does not program each field directly.

The PCIe capability names align with standard PCI/PCIe concepts, but the macros are ASIC-specific because the register address blocks, base indices, and available field sets are generated for AMD NBIO 7.7.0. Dev/function prefixes such as `DEV0_EPF7`, `DEV1_EPF0`, and `DEV1_EPF1` are part of the hardware register map and should not be substituted across otherwise similar capability layouts.

## Risks And Edge Cases

- Shift/mask drift is silent at compile time when a macro still exists but no longer matches hardware. A wrong mask can corrupt neighboring PCIe configuration fields.
- This slice contains many write-sensitive controls: MSI/MSI-X address/data/mask state, link retrain/compliance controls, completion timeout, ARI, atomic operations, IDO, LTR, OBFF, VC configuration, DPA controls, ACS/PASID controls, data-link controls, PHY 16 GT/s controls, and margining controls.
- AER status, mask, severity, and log fields affect fault visibility and classification. Incorrect programming can hide real PCIe faults or create misleading diagnostics.
- ACS, PASID, ARI, VC, and data-link feature fields influence routing, isolation, request tagging, traffic class mapping, and transaction behavior. Bugs can surface as DMA isolation issues, guest-visible SR-IOV problems, link stalls, or ordering problems.
- MSI/MSI-X state is security and reliability sensitive. Bad message address/data or mask handling can drop interrupts, deliver interrupts to the wrong vector, or expose stale pending state after reset/resume.
- Lane equalization, 16 GT/s PHY, and margining fields are signal-integrity sensitive. Misuse may reproduce only on particular boards, link partners, speeds, widths, ASPM states, warm boots, or resume paths.
- Repeated dev/function definitions are copy-sensitive. `DEV0_EPF7`, `DEV1_EPF0`, and `DEV1_EPF1` share many register names but do not have identical capability coverage in this chunk.
- The range starts and ends in partial registers, so chunk-local validation must tolerate unmatched shift/mask pairs at `DEVICE_CNTL2` and `VENDOR_CAP_LIST`.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with NBIO 7.7.0 support enabled; missing or renamed macros should fail in consumers of the generated register headers.
- Mechanically check that fields wholly contained in lines 147481-149938 have paired `__SHIFT` and `_MASK` constants and that masks align with their shifts and expected widths.
- Diff this slice against AMD's authoritative NBIO 7.7.0 register database or generated source before accepting regenerated output.
- On NBIO 7.7 hardware, exercise PCIe enumeration, BAR sizing/programming, MSI/MSI-X delivery and masking, AER injection/reporting, FLR, suspend/resume, warm reset, link retrain, ASPM/LTR behavior, and 16 GT/s link training.
- For virtualization or SR-IOV scenarios, test PF/VF isolation, ACS routing, PASID behavior, ARI enumeration, MSI/MSI-X remapping, guest reset recovery, and guest-visible AER behavior.
- For signal-integrity and performance-sensitive changes, monitor negotiated PCIe speed/width, equalization phase status, lane error status, PHY 16 GT/s status, margining status payloads, AER counters/logs, VC negotiation pending bits, DPA status, interrupt pending/mask state, and kernel PCIe timeout or unsupported-request logs.

## Cross-Chunk Notes

The previous chunk owns most of `BIF_CFG_DEV0_EPF7_1_DEVICE_CNTL2`, including the initial field shift definitions for completion timeout, ARI, atomic, IDO, LTR, emergency power reduction, 10-bit tags, and OBFF. This chunk contributes the final `END_END_TLP_PREFIX_BLOCKING` shift and all `DEVICE_CNTL2` masks before continuing through the rest of the `DEV0_EPF7` tail.

The next chunk owns `BIF_CFG_DEV1_EPF1_1_VENDOR_CAP_LIST__LENGTH_MASK` and any following `DEV1_EPF1` capability definitions. The final per-file report should reconcile these partial boundary registers and avoid treating line 149938 as a semantic end of the `DEV1_EPF1` capability block.
