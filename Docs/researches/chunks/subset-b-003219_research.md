# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 143503-145969

## Scope

This chunk is a generated AMD NBIO 7.2.0 shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, runtime branches, allocation, locking, persistence logic, or direct hardware access. The constants describe bit positions and masks for NBIO/BIF PCI configuration-space registers exposed by AMDGPU's ASIC register headers.

The range contains 2,119 `#define` entries: 1,058 `__SHIFT` constants and 1,061 `_MASK` constants. The mismatch is caused by artificial chunk boundaries. The first lines continue `BIF_CFG_DEV0_EPF7_1_LINK_CNTL`, whose earlier field shifts are in the previous chunk, and the final line starts `BIF_CFG_DEV1_EPF0_1_PCIE_TPH_ST_TABLE_39__TPH_ST_LOWER_ENTRY__SHIFT`, whose upper-entry shift and masks are in the next chunk.

## Purpose

NBIO is the GPU northbridge and PCIe-facing I/O block. This slice defines the bit-level ABI for two PCIe endpoint/function configuration regions:

- The tail of `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`, covering `DEV0_EPF7` PCIe link control/status, PCIe capability extensions, interrupts, AER, BAR virtualization, power and DPA capabilities, ACS/PASID/ARI, and TPH steering tables.
- The beginning and middle of `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`, covering the standard PCI header, PCI/PCIe capabilities, MSI/MSI-X, vendor-specific and VC extended capabilities, AER, BAR enhanced capability, power budget, DPA, secondary PCIe link-equalization capability, ACS/PASID/LTR/ARI, and TPH steering tables through table 39.

The public interface pattern is consistent:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the mask for extracting or composing the field.

Runtime code combines these macros with register offsets from `nbio_7_2_0_offset.h` and AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The `DEV0_EPF7` tail starts inside `LINK_CNTL`, defining link control masks for PM control, read completion boundary, link disable, retrain, common clock, extended sync, clock power management, autonomous width disable, bandwidth interrupt enablement, autonomous bandwidth interrupt enablement, and DRS signaling. It then defines `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`, including current link speed/width, training state, data link active, completion timeout support/control, ARI/atomic/IDO/LTR/OBFF/10-bit tag controls, supported link speeds, compliance/equalization state, crosslink state, downstream presence, and DRS message status.

The `DEV0_EPF7` interrupt capability registers cover MSI and MSI-X capability list pointers, MSI message control, 32-bit and 64-bit message address/data fields, extended message data, mask and pending bits, MSI-X table BIR/offset, and MSI-X PBA BIR/offset. These macros are the field map used when PCI interrupt capability state is read, exposed, restored, or emulated.

The `DEV0_EPF7` PCIe extended capability region includes vendor-specific capability headers/data, AER capability list and control fields, uncorrectable error status/mask/severity bits, correctable error status/mask bits, AER capability controls, header log registers, and TLP prefix logs. The AER status families include data link protocol, surprise down, poisoned TLP, flow control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic egress block, TLP prefix blocked, and related correctable status bits.

The `DEV0_EPF7` BAR, power, and DPA extended capabilities describe PCIe enhanced BAR capability/control registers for BAR1 through BAR6, power budget data select/data/capability fields, dynamic power allocation capability/status/control, latency indicator, and eight DPA substate power-allocation entries.

The `DEV0_EPF7` access-control and request-tagging region defines ACS capability/control bits for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector size. It also defines PASID capability/control, ARI capability/control, TPH requester capability/control, and TPH steering table entries 0 through 63. Each TPH ST table packs lower and upper 8-bit steering entries into a 16-bit register-shaped field.

The `DEV1_EPF0` block begins a new address block. It maps the standard PCI config header: vendor/device ID, command, status, revision and class code, cache line, latency timer, header type, BIST, six base address registers, CardBus CIS pointer, adapter/subsystem identity, ROM base address, capability pointer, interrupt line/pin, and min-grant/max-latency fields. Command/status fields include I/O, memory, bus mastering, parity/SERR, interrupt disable, capability-list presence, abort/error state, DEVSEL timing, and parity detection.

The `DEV1_EPF0` PCI power-management and PCIe base capabilities include vendor capability headers, adapter ID write fields, PMI capability/status/control, SBRN, FLADJ, DBESL/DBESLD, PCIe capability list/header fields, device capability/control/status, link capability/control/status, and capability-2/control-2/status-2 fields. These describe payload/read-request sizing, phantom/extended tags, endpoint L0s/L1 latency, FLR, relaxed ordering, no-snoop, AUX power, transaction pending, ASPM, common clock, retrain, link bandwidth notifications, link speed/width, completion timeout, ARI, atomic operations, IDO, LTR, OBFF, 10-bit tags, and equalization state.

The `DEV1_EPF0` MSI/MSI-X and vendor-specific capability families mirror the `DEV0_EPF7` interrupt layout, then extend into PCIe virtual-channel support. The VC capability/control/status families describe extended VC count, low-priority VC count, arbitration table capability, VC arbitration select, load-table strobe, VC negotiation pending, and VC0/VC1 resource capability/control/status, including port arbitration capability, TC/VC maps, reject snoop transaction, maximum time slots, arbitration select, load table, VC ID, and negotiation pending state.

The `DEV1_EPF0` AER, enhanced BAR, power budget, and DPA families mirror the `DEV0_EPF7` fields but for the dev1 function 0 configuration aperture. The secondary PCIe extended capability adds link control 3, lane error status, and per-lane equalization control for lanes 0 through 15, with downstream/upstream port preset fields and preset hints. The chunk then continues through ACS, PASID, LTR capability, ARI, TPH requester capability/control, and TPH ST table entries 0 through the first field of table 39.

## Control Flow

There is no executable control flow in this header chunk. Runtime behavior is imposed by consumers:

1. ASIC-specific AMDGPU code includes `nbio_7_2_0_offset.h` for register addresses and `nbio_7_2_0_sh_mask.h` for fields.
2. The driver selects the appropriate NBIO register aperture and offset through SOC15 or PCIe-port helpers.
3. The driver reads a register, composes or extracts fields with the generated shift/mask macros, and writes back when needed.
4. For status, clear, reset, interrupt, link training, equalization, and AER fields, the hardware register semantics determine whether a field is read-only, write-one-to-clear, sticky, self-clearing, or write-sensitive.

Chunk boundaries are not semantic boundaries. This range begins mid-register and ends mid-register, so adjacent chunks are required for complete field coverage of `DEV0_EPF7_1_LINK_CNTL` and `DEV1_EPF0_1_PCIE_TPH_ST_TABLE_39`.

## State And Persistence Behavior

The header stores no software state. It describes MMIO/config-space hardware state owned by the NBIO/BIF block and, for PCIe-visible capability registers, state that may also be visible through PCI configuration mechanisms or virtualization layers.

Configuration-like state in this chunk includes PCI command bits, BAR decode fields, ROM aperture bits, MSI/MSI-X message and mask state, PCIe device/link controls, completion timeout, ARI/atomic/IDO/LTR/OBFF/10-bit-tag controls, ACS/PASID/LTR/ARI/TPH capability controls, VC controls, DPA controls, BAR enhanced controls, and link-equalization control.

Status-like state includes PCI status/error bits, interrupt status, device/link status, equalization results, AER correctable and uncorrectable error status, AER header/TLP prefix logs, DPA status, VC status, lane error status, MSI pending bits, and TPH steering entries where firmware or hardware may populate values.

Persistence is hardware-defined. Some fields reflect straps or read-only capabilities, some are writable configuration that survives until FLR, link reset, function reset, suspend/resume, or full GPU reset, and some status/error-log fields are sticky until explicitly cleared by the PCIe/AER-defined sequence. Consumers must not infer persistence or clear behavior from the mask name alone.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.2.0 register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h` supplies register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h` supplies the field masks and shifts documented here.
- The AMDGPU SOC15 register helper layer supplies field composition/extraction and MMIO access macros.

The direct NBIO 7.2 implementation, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, includes this header and registers `nbio_v7_2_funcs`. That file uses the same generated-mask pattern for revision ID, framebuffer access enablement, doorbell ranges and apertures, interrupt control, clock/power gating, PCIe index/data offsets, and related NBIO setup. The exact PCI config-space fields in this chunk are mostly lower-level capability maps and diagnostic/control surfaces; they may be consumed by platform workarounds, SR-IOV/PF policy, AER handling, firmware bring-up, or future code paths even when current `nbio_v7_2.c` does not program each field directly.

The PCIe capability names align with standard PCI/PCIe concepts, but the macros are ASIC-specific because the register address block and field availability are generated for AMD NBIO 7.2.0. Dev/function naming is part of the hardware register map: `DEV0_EPF7` and `DEV1_EPF0` should not be treated as interchangeable even where the capability layouts look similar.

## Risks And Edge Cases

- Shift/mask drift is silent at compile time. A wrong mask can corrupt neighboring PCIe configuration fields while all C code still builds.
- This range contains many write-sensitive PCIe controls: link retrain/disable, completion timeout, FLR-related capability bits, MSI/MSI-X mask/message state, AER status and mask bits, VC controls, DPA controls, ACS controls, PASID controls, LTR controls, ARI controls, and TPH controls.
- The repeated dev/function layout is copy-sensitive. `DEV0_EPF7` and `DEV1_EPF0` share many capability names, but their available extended capabilities and table ranges differ across the chunk.
- AER status, mask, and severity bits can hide or reclassify real PCIe faults if programmed incorrectly.
- ACS, PASID, ARI, TPH, and VC fields affect isolation, request routing, transaction ordering, and traffic class behavior. Incorrect values can become DMA isolation bugs, guest-visible SR-IOV issues, or intermittent fabric stalls.
- MSI/MSI-X message address/data/mask/pending fields are security and reliability sensitive. Bad programming can drop interrupts, deliver them to the wrong vector, or expose stale pending state after reset/resume.
- Link capability/control/status and lane equalization fields interact with platform signal integrity and power management. Misuse may only reproduce on specific link speeds, widths, ASPM states, warm boots, or resume paths.
- The range starts and ends in partial registers, so chunk-local mechanical checks will show unmatched field pairs unless adjacent chunks are considered.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with NBIO 7.2 support enabled; renamed or missing macros should fail at compile time in users of the generated register headers.
- Mechanically check that fields wholly contained in lines 143503-145969 have paired `__SHIFT` and `_MASK` constants and that regular masks correspond to their shift and width.
- Diff this generated slice against AMD's authoritative NBIO 7.2.0 register database or adjacent generated headers before accepting regenerated output.
- On NBIO 7.2 hardware, exercise PCIe link training and retraining, speed/width negotiation, ASPM/LTR behavior, MSI/MSI-X delivery, AER injection/reporting, FLR/reset/resume, BAR aperture programming, and suspend/resume.
- For virtualization or SR-IOV scenarios, test PF/VF isolation, PASID behavior, ACS routing, ARI enumeration, MSI/MSI-X remapping, FLR recovery, and guest-visible AER behavior.
- For performance-sensitive changes, monitor link equalization status, lane error status, AER counters/logs, VC negotiation pending bits, DPA status, interrupt pending/mask state, and kernel logs for PCIe timeouts or unsupported requests.

## Cross-Chunk Notes

The previous chunk owns the beginning of `BIF_CFG_DEV0_EPF7_1_LINK_CNTL`, including the initial shift definitions for PM control, read completion boundary, link disable, and retrain. This chunk owns the rest of that register's masks and then the `DEV0_EPF7` capability region through TPH ST table 63.

The next chunk completes `BIF_CFG_DEV1_EPF0_1_PCIE_TPH_ST_TABLE_39` and continues the remaining `DEV1_EPF0` TPH steering table entries. The final per-file report should reconcile these boundaries before making complete claims about all TPH steering table coverage or all fields in either boundary register.
