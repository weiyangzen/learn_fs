# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 7360-9821

## Scope

This chunk is part of AMDGPU's generated NBIO 7.2.0 shift/mask register header. It contains C preprocessor constants for hardware bitfield positions and masks; it has no functions, types, variables, locks, allocations, sysfs/debugfs handlers, persistence code, or executable control flow.

The range covers 2,107 `#define` lines: 1,056 `__SHIFT` constants and 1,051 `_MASK` constants. The mismatch is expected for this slice because the range ends inside `BIF_CFG_DEV0_EPF3_LINK_CNTL`: the field shifts and the first masks are present, while the remaining masks are in the next chunk. The chunk starts cleanly at `BIF_CFG_DEV0_EPF1_LANE_3_MARGINING_LANE_STATUS`, continues through the rest of the EPF1 PCIe margining, VF resize BAR, and GPUIOV vendor-specific capability fields, covers a full `addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`, and then enters `addressBlock: nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` through the beginning of EPF3 PCIe link control.

Although the repository path is under a Ceph client mirror, this file is AMD GPU NBIO register metadata and has no direct distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_sh_mask.h` is the bitfield-description layer for NBIO 7.2.0 registers. For each hardware register field, it exposes:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the raw bit mask used to isolate or preserve that field.

Runtime AMDGPU code pairs these macros with register offsets from `nbio_7_2_0_offset.h` and with register helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and PCIe/NBIO indirect access helpers. The header does not encode register addresses, reset values, read/write permissions, side-effect rules, sequencing, locking, or firmware ownership.

## Important Macro Families

The opening EPF1 margining block describes per-lane PCIe margining control/status fields for the tail of lane 3 status and lanes 4 through 15. Each lane uses the same field schema: receiver number, margin type, usage model, and payload, with status variants for observed lane response. These fields are part of PCIe link characterization and diagnostics rather than normal rendering or command-submission paths.

The EPF1 VF resize BAR section defines resizable BAR capability/control fields for VF BAR1 through VF BAR6. Capability registers expose supported VF BAR sizes, while control registers expose BAR index, total BAR count, selected BAR size, and upper supported-size bits. These fields are virtualization-sensitive because they describe how virtual functions expose MMIO aperture sizes to the PCIe fabric.

The EPF1 GPUIOV vendor-specific capability is the dominant nonstandard block in the first half of the chunk. It includes the PCIe enhanced capability header, VSEC ID/revision/length, SR-IOV shadow state (`VF_EN`, `VF_NUM`), interrupt enable/status bits for GFX, UVD, UVD1, VCE, and HVVM mailbox conditions, a soft PF FLR control bit, compact HVVM mailbox dwords, context size/location/offset fields, total framebuffer sizing, offset/region controls, P2P-over-XGMI enablement, and per-VF framebuffer assignment registers `VF0_FB` through `VF30_FB`.

The same GPUIOV block also defines scheduling tables for media and graphics engines: `UVDSCH_DW0..DW8`, `VCESCH_DW0..DW8`, `GFXSCH_DW0..DW8`, and `UVD1SCH_DW0..DW8`. The schedule fields include offsets, sizes, and time-slice style values for multiple logical functions. These are not software data structures; they are hardware-visible virtualization scheduling controls that the driver or platform firmware can use to partition GPU engines among PF/VF contexts.

The EPF2 address block is a full PCI endpoint-function configuration-space layout for device 0 function 2. It starts with standard PCI identity and command/status fields: vendor/device ID, I/O and memory access enables, bus mastering, SERR, INTx disable, interrupt status, capability-list support, target/master abort status, parity status, revision/class codes, cache-line and latency fields, header type, BIST, BAR1-BAR6, CardBus CIS pointer, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, and min-grant/max-latency bytes.

EPF2 power-management and base PCIe capability fields include vendor and PMI capability list pointers, PME capabilities, D-state support, power-state control, PME enable/status, PMI data fields, USB-related SBRN/FLADJ/DBESL fields, PCIe capability version/device type/message number fields, device capabilities, device control/status, link capabilities, and link control/status. These macros describe both capabilities reported to software and writable policy bits such as error reporting enables, relaxed ordering, no-snoop, payload size, read-request size, link disable/retrain, common clock configuration, and bandwidth interrupt enables.

The EPF2 PCIe 2.0/3.0 capability continuation includes `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. These fields cover completion-timeout ranges and controls, LTR, OBFF, atomic operation routing and enablement, ID-based ordering, emergency power reduction, 10-bit tags, supported/target link speeds, compliance controls, de-emphasis, 8 GT/s equalization phase status, retimer presence, crosslink state, DRS support, and downstream component presence.

The EPF2 MSI/MSI-X block defines capability IDs and next pointers, MSI enable/multi-message/64-bit/per-vector-mask/extended-data fields, MSI message address and data fields for 32-bit and 64-bit layouts, mask and pending-bit arrays, MSI-X table size/function mask/enable, and table/PBA BIR plus offset fields. These macros are part of interrupt delivery programming and must match the PCI core's understanding of the endpoint's config-space layout.

The EPF2 vendor-specific and AER block exposes VSEC headers and scratch fields, then Advanced Error Reporting status/mask/severity/capability/log fields. Uncorrectable AER fields include DLP, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable AER fields include receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, corrected internal error, and header-log overflow. Diagnostic fields include first-error pointer, ECRC support/enablement, multi-header support/enablement, TLP prefix log presence, completion-timeout log capability, four TLP header log dwords, and four TLP prefix log dwords.

The EPF2 enhanced capability section continues through resizable/enhanced BAR support, power budgeting, Dynamic Power Allocation, ACS, PASID, ARI, and TPH requester capability. BAR fields cover supported sizes and per-BAR selected size/index/count for BAR1-BAR6. Power budget fields cover selected power data, base power, data scale, PM substate/state, rail, type, and system-allocation status. DPA fields cover transition latency, power-allocation scale, max/current substate, enable/status/control, and substate power allocations 0-7. ACS fields cover source validation, translation blocking, peer-to-peer redirects, upstream forwarding, egress control, direct-translated P2P, and egress vector size. PASID fields expose max PASID width plus execute-permission and privileged-mode support/enables. ARI fields expose next-function number, function group support, and MFVC/ACS function group controls.

The EPF2 TPH requester block defines capability and control fields for steering tags plus `PCIE_TPH_ST_TABLE_0` through `PCIE_TPH_ST_TABLE_63`. Each table register has lower and upper 8-bit steering-tag entries. This is a large repeated hardware table: generated-name drift, off-by-one table indexing, or treating the table as wider than 16 bits would silently program the wrong steering-tag entry.

The EPF3 address block begins near the end of the chunk and repeats the standard PCI/PCIe endpoint-function pattern for device 0 function 3. This slice includes EPF3 identity, command/status, class/revision, BARs, subsystem IDs, ROM BAR, capability pointers, interrupt/min/max fields, vendor and PMI capability fields, SBRN/FLADJ/DBESL, PCIe capability, device capability/control/status, link capability, and the beginning of link control. The chunk ends after `BIF_CFG_DEV0_EPF3_LINK_CNTL__EXTENDED_SYNC_MASK`, so the rest of `LINK_CNTL` and following EPF3 fields are owned by the next chunk.

## APIs, Types, And Functions

This header exports only preprocessor constants. There are no callable APIs and no C types in this range.

The practical interface is the generated macro namespace used by AMDGPU NBIO code. Direct consumers in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both `nbio/nbio_7_2_0_offset.h` and this shift/mask header. Discovery and ASIC setup code select `nbio_v7_2_funcs` for matching hardware, and display resource code includes the matching offset header for DC resource setup. Local generated files for this NBIO version include `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h`; there is no sibling `nbio_7_2_0_default.h` in this directory.

Representative matching offset symbols exist in `nbio_7_2_0_offset.h` for registers in this slice, including `cfgBIF_CFG_DEV0_EPF1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_TOTAL_FB`, `cfgBIF_CFG_DEV0_EPF2_VENDOR_ID`, and `cfgBIF_CFG_DEV0_EPF3_LINK_CNTL`. The offset symbols use the `cfg` prefix because these are PCIe configuration-space-style registers rather than ordinary MMIO register names.

## Control Flow

There is no software control flow in this chunk. Runtime flow is external:

1. AMDGPU code selects a config-space or NBIO register offset from `nbio_7_2_0_offset.h`.
2. It reads or prepares a register value through the appropriate PCIe/NBIO/SOC15 access path.
3. It applies this header's `__SHIFT` and `_MASK` constants to extract a field or compose a new value while preserving unrelated bits.
4. Hardware state machines act on the result: PCIe enumeration, link management, margining, interrupt routing, AER reporting, power management, DPA substates, ACS/PASID/ARI isolation, TPH steering, GPUIOV scheduling, VF framebuffer partitioning, HVVM mailbox handshakes, or soft PF FLR.

The implicit hardware workflows represented by the fields include PCIe lane margining commands and statuses, SR-IOV shadow capability reporting, per-VF resource sizing, GPUIOV interrupt signaling, mailbox valid/ack exchange, PCI capability traversal, MSI/MSI-X setup, AER logging and masking, link retraining and equalization, DPA state transitions, ACS/PASID/ARI virtualization policy, and TPH steering-tag selection.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. It describes hardware-visible state in NBIO PCIe configuration registers and AMD vendor-specific virtualization registers.

Represented state categories include:

- Capability and identity state reported through PCI/PCIe config space.
- Writable endpoint policy bits for command/status, device control, link control, MSI/MSI-X, power management, AER masks/severity, ACS/PASID/ARI, DPA, BAR sizing, TPH control, and GPUIOV operation.
- Live or latched status bits for link status, error status, interrupt status, MSI pending state, mailbox acknowledgement/valid state, DPA status, AER logs, and margining status.
- Virtualization resource state for VF BAR sizing, framebuffer allocation per VF, engine scheduling windows, and P2P-over-XGMI enablement.
- Diagnostic log state such as AER header and TLP prefix logs.

Persistence depends on the hardware reset domain, PCIe hot/cold reset, FLR, D3hot-to-D0 transitions, suspend/resume restore, firmware/BIOS initialization, SR-IOV enablement, and explicit driver writes. The generated header does not say which fields are read-only, write-one-to-clear, sticky, firmware-owned, strap-derived, or safe for read/modify/write. Full-width masks such as `0xFFFFFFFFL` describe field width only; they are not evidence that arbitrary writes are safe.

## Dependencies And Integration Points

The direct dependency is AMD's generated NBIO 7.2.0 register database. This shift/mask header must remain synchronized with `nbio_7_2_0_offset.h`; mismatches can compile successfully while targeting or decoding the wrong bit.

Important integration points are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, the NBIO 7.2 implementation that includes this header and exposes `nbio_v7_2_funcs`.
- PCI/PCIe configuration-space handling, including enumeration-visible capabilities, command/status bits, link capabilities, MSI/MSI-X, AER, ACS, PASID, ARI, DPA, power budgeting, and TPH requester support.
- AMD GPU virtualization and SR-IOV/GPUIOV flows, especially VF BAR sizing, per-VF framebuffer assignment, engine scheduling, mailbox signaling, and soft PF FLR.
- AMDGPU reset and recovery paths that may interact with FLR, mailbox, AER, GPUIOV hang/need-FLR interrupts, and link retraining controls.
- Hardware debug paths that decode lane margining and AER/TLP logs.

The macros rely on external access code for width, endianness, config-space window selection, indirect-index ordering, locking, polling, memory barriers, and reserved-bit preservation.

## Risks And Edge Cases

- The chunk ends mid-register at `BIF_CFG_DEV0_EPF3_LINK_CNTL`; any complete EPF3 link-control analysis must merge the next chunk.
- Generated field drift is high risk in repetitive families: EPF1 lanes, VF BAR1-BAR6, VF0-VF30 framebuffer registers, schedule dwords, EPF2 TPH table entries 0-63, and repeated EPF2/EPF3 PCIe capability blocks.
- PCIe control fields can affect link stability, interrupt delivery, enumeration, power behavior, and error containment. Incorrect writes to link retrain/disable, target speed, ASPM/PM control, MSI/MSI-X enablement, AER masks, ACS/PASID/ARI, DPA, TPH, or BAR sizing can be externally visible to the host and peer devices.
- GPUIOV fields are virtualization-sensitive. Bad VF framebuffer sizes, offsets, scheduling windows, mailbox state, P2P-over-XGMI enablement, or SR-IOV shadow values can break VF isolation or leave guest-visible resources inconsistent.
- Status and log fields may be live, sticky, clear-on-read, or write-one-to-clear depending on hardware semantics. This header provides masks only, so generic read/modify/write logic can accidentally clear errors or acknowledge interrupts.
- Full-width and high-bit masks use untyped C integer literals with an `L` suffix. Consumers should keep using established AMDGPU register helpers and fixed-width `u32` values to avoid signedness or truncation mistakes.
- Offset symbols for this generation use `cfg...` names. Code that assumes only `reg...` offset names may miss that these are config-space definitions.

## Test Signals

- Build AMDGPU with NBIO 7.2 enabled, including `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, to catch missing, renamed, or incompatible generated symbols.
- Run generated-header consistency checks: every complete field should have one shift and one mask, masks should align with shifts, field masks in each register should not overlap unexpectedly, and the only expected imbalance in this slice is the truncated `EPF3_LINK_CNTL` tail.
- Cross-check representative names against `nbio_7_2_0_offset.h`, especially EPF1 GPUIOV registers, the EPF2 config-space block, EPF2 TPH table registers, and the EPF3 block start.
- On NBIO 7.2 hardware, compare decoded PCIe config state against `lspci -vvxxx` or AMDGPU register dumps: command/status, BARs, PM capability, PCIe link speed/width, MSI/MSI-X, AER status/masks, ACS/PASID/ARI, DPA, power budgeting, and TPH fields should decode correctly.
- Validate SR-IOV/GPUIOV behavior with VF creation and teardown: VF BAR sizes, framebuffer allocation, mailbox valid/ack bits, GPUIOV interrupt status/enable bits, engine scheduling dwords, and soft PF FLR behavior should match expected PF/VF state.
- Exercise error and recovery paths where possible: AER injection or observed PCIe errors should set and clear the intended status bits; hang/need-FLR interrupt bits should route correctly; link retrain/equalization state should match hardware traces.
- For lane margining diagnostics, verify per-lane receiver/type/usage/payload fields decode consistently across lanes 3-15 and that lane status registers are not treated as writable control fields.
