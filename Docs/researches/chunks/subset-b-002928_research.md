# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 59037-61469

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-field shift/mask header slice. It contains only C preprocessor constants: no functions, structs, enums, variables, allocation, locking, persistence code, or executable control flow.

The range starts inside `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_STATUS`, after the first uncorrectable-error field shifts and before the corresponding masks. It then completes the tail of endpoint PF0 virtual function 1 (`BIF_CFG_DEV0_EPF0_VF1_0_*`) advanced error reporting and ATS/ARI definitions, covers full repeated PCI/PCIe configuration field layouts for virtual functions 2, 3, and 4 (`BIF_CFG_DEV0_EPF0_VF2_0_*`, `BIF_CFG_DEV0_EPF0_VF3_0_*`, `BIF_CFG_DEV0_EPF0_VF4_0_*`), and begins virtual function 5 (`BIF_CFG_DEV0_EPF0_VF5_0_*`) through `PCIE_CAP`. The final line is followed by `BIF_CFG_DEV0_EPF0_VF5_0_DEVICE_CAP` in the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMD GPU NBIO/PCIe hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bit layout contract for NBIO 2.3 PCI configuration decoder registers that expose PF0 virtual-function PCI and PCIe capabilities. Each field is represented by generated macros of the form:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to pack or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update the field.

The matching register offsets live in sibling NBIO generated headers, especially `nbio_2_3_offset.h`, where config-space symbols identify the register address. AMDGPU consumers combine those offsets with these masks through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. This file names bitfields only; it does not define access ordering, read/write permissions, reset values, or side-effect semantics.

## Important Macro Families

The VF1 tail is focused on PCIe Advanced Error Reporting and translation/routing enhanced capabilities. It includes uncorrectable error status/mask/severity fields for DLP, surprise down, poisoned TLP, flow control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC-blocked TLP, atomic operation egress blocked, and TLP prefix blocked conditions. It also defines correctable error status/mask fields for receiver error, bad TLP/DLLP, replay rollover and timeout, advisory non-fatal error, internal correctable error, and header log overflow. The same VF1 tail carries AER capability/control bits for first error pointer, ECRC generation/checking, multiple-header recording, TLP prefix log presence, completion-timeout log capability, four 32-bit TLP header log words, four 32-bit TLP prefix log words, ATS enhanced capability/capability/control fields, and ARI enhanced capability/capability/control fields.

The VF2, VF3, and VF4 blocks are structurally identical full virtual-function PCI configuration images. Each begins with ordinary PCI header fields: vendor/device ID, command/status, revision and class-code bytes, cache line size, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency. The command/status masks cover I/O, memory, bus mastering, parity/SERR, interrupt disable, immediate readiness, capability-list presence, target/master abort status, system error, and parity detection.

For each full VF block, the PCIe capability section defines capability-list metadata and device/link capability/control/status fields. These include max payload support and size, max read request size, relaxed ordering, no-snoop, extended tags, phantom functions, auxiliary power management, function-level reset initiation/capability, correctable/non-fatal/fatal/unsupported-request reporting enables, transactions pending, link speed and width capability/status, ASPM and clock power management controls, retrain/link disable/common clock/extended sync controls, bandwidth-management and autonomous-bandwidth interrupts, DRS signaling, data-link active status, Gen2+ supported link speeds, compliance and de-emphasis controls, 8 GT/s equalization phase status, crosslink/presence reporting, and downstream-component presence.

The PCIe capability version 2 portions for VF2 through VF4 add completion timeout range/disable, ARI forwarding support and enable, atomic operation routing/request/egress control, ID-based ordering request/completion enables, latency tolerance reporting, OBFF, end-to-end TLP prefix support/blocking, ten-bit tag requester/completer support and enable, emergency power reduction support/request, and fast role swap support. `DEVICE_STATUS2` is represented as a reserved 16-bit field in these VF blocks.

The interrupt capability groups for VF2 through VF4 define MSI and MSI-X layouts. MSI fields cover capability-list metadata, MSI enable, multiple-message capability and enable, 64-bit support, per-vector masking capability, message address low/high, message data, mask, 64-bit data/mask aliases, and pending bits. MSI-X fields cover table size, function mask, MSI-X enable, table BIR and offset, and PBA BIR and offset.

The vendor-specific and AER enhanced-capability groups for VF2 through VF4 include PCIe vendor-specific enhanced capability list fields, vendor-specific header fields, two vendor-specific payload dwords, AER enhanced capability list fields, uncorrectable/correctable error status and masks, uncorrectable severity, AER capability/control, header logs, and TLP prefix logs. These macros are diagnostic and recovery oriented: they identify status bits that may be sticky, masked, severity-classified, or used to preserve error evidence for later decoding.

The ATS and ARI groups for VF2 through VF4 define PCIe enhanced capability headers plus control/capability payloads. ATS fields include invalidate queue depth, page-aligned requests, global invalidate support, STU, and ATC enable. ARI fields include MFVC and ACS function group capability/enable bits, next function number, and function group selection.

The VF5 block in this chunk is only the beginning of the next repeated virtual-function configuration image. It covers the same standard PCI header and BAR-related fields as VF2 through VF4, then reaches `PCIE_CAP_LIST` and `PCIE_CAP` metadata. Its device capability and later PCIe/AER/MSI/ATS/ARI fields are outside this chunk.

## Control Flow

There is no runtime control flow in this header. The effective use pattern in AMDGPU code is:

1. Select the corresponding NBIO 2.3 config-space register offset from the generated offset header or a per-ASIC register table.
2. Read or prepare a PCIe config register value through the driver's PCIe/SOC15 access helpers.
3. Use the `__SHIFT` and `_MASK` constants directly, or through helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`, to decode or update a specific field.
4. Write the value back, poll a hardware-owned status bit, clear sticky error state according to PCIe rules, or hand the decoded value to reset, interrupt, virtualization, or RAS/error handling code.

The repeated VF2/VF3/VF4 layout implies table-like hardware, but this header does not implement iteration. Any loop over virtual functions or capability families is implemented by driver code that chooses the matching register offset and macro family.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes GPU PCI configuration and enhanced-capability state owned by hardware, firmware, the PCIe fabric, the host kernel, and the AMDGPU driver.

Some represented fields are configuration that can persist until reset, function-level reset, suspend/resume, power transition, or explicit driver reprogramming: PCI command enables, BAR values, MSI/MSI-X message address/data/mask state, PCIe device/link controls, completion timeout controls, ARI forwarding, atomic operation controls, ID-based ordering, LTR/OBFF controls, ATS ATC enablement, and ARI function grouping.

Other fields are hardware-owned status, command strobes, or sticky diagnostic state: PCI status bits, device and link status, link training/equalization status, transactions pending, MSI pending bits, AER correctable/uncorrectable status, AER header logs, and TLP prefix logs. The masks do not encode whether a bit is read-only, write-one-to-clear, write-one-to-set, self-clearing, firmware-owned, or volatile; callers must follow the hardware programming guide and PCIe specification behavior for each register.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This `*_sh_mask.h` slice must stay synchronized with the companion offset/default headers under `drivers/gpu/drm/amd/include/asic_reg/nbio/`; the offset header gives address names while this file gives field positions for values at those addresses.

Primary integration is with AMDGPU NBIO, PCIe, interrupt, reset, RAS/AER, SR-IOV, and virtualization paths. These macros support virtual-function config-space exposure and driver-side interpretation of function identity, BARs, command/status, PCIe device/link capabilities, MSI/MSI-X delivery, AER status/logging/masking/severity, ATS address-translation services, ARI routing/function grouping, and function-level reset behavior.

The macros are untyped integer constants. Missing or renamed macro names usually fail at compile time in consuming code, but an incorrect shift or mask can compile cleanly and cause adjacent PCIe fields to be read, cleared, or programmed incorrectly. Because this file is generated ASIC metadata, manual changes should be treated as hardware ABI changes and checked against the authoritative register source.

## Risks And Edge Cases

- Chunk boundaries are partial. The first line is already inside VF1 `PCIE_UNCORR_ERR_STATUS`, and the last line stops after VF5 `PCIE_CAP`; adjacent chunks are required before making whole-register or whole-VF claims for VF1 and VF5.
- The range mixes 8-bit PCI header fields, 16-bit PCI/PCIe capability words, and 32-bit enhanced-capability dwords. Wrong access width or offset pairing can corrupt neighboring fields even when a mask is locally correct.
- AER fields are side-effect sensitive. Treating uncorrectable/correctable status bits, severity bits, header logs, or TLP prefix logs as ordinary retained configuration can clear evidence, hide real errors, or misclassify recovery severity.
- Link and device-control fields are interoperability-sensitive. Incorrect max payload/read request, completion timeout, relaxed ordering, no-snoop, FLR, ASPM, retrain, target speed, equalization, or DRS masks can cause enumeration failures, link retraining problems, performance regressions, or reset hangs.
- MSI/MSI-X fields are interrupt-delivery critical. Wrong enable, message address/data, mask, pending, table, PBA, or function-mask fields can cause lost interrupts, spurious interrupts, or poor isolation between virtual functions.
- ATS and ARI fields affect I/O address translation and PCIe function routing. Incorrect STU/ATC enable, queue-depth, global invalidate, ARI forwarding, next-function, or function-group masks can break DMA address translation, virtual-function discovery, or isolation.
- The VF2, VF3, and VF4 blocks are highly repetitive. Off-by-one copy or generation errors are plausible and may only appear on configurations that instantiate or exercise the affected virtual function.
- Full-width BAR, ROM base, CIS pointer, MSI address, AER log, and vendor-specific dword fields are not self-validating. Pairing a correct full-width mask with the wrong offset can overwrite or decode unrelated hardware state.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU for ASICs using NBIO 2.3 headers with PCIe, MSI/MSI-X, AER, SR-IOV, ATS, and ARI support enabled; missing symbols should surface as compile failures in NBIO/PCIe/interrupt/virtualization code.
- Run generated-header consistency checks against the NBIO register database and sibling offset headers, including shift/mask pair checks, field width checks, non-overlap checks within each register, and repeated VF layout comparison for VF2 through VF4.
- Boot affected hardware and confirm PCI enumeration exposes stable VF vendor/device IDs, class codes, BARs, capability-list traversal, PCIe capability blocks, MSI/MSI-X capability blocks, AER capability blocks, ATS capability blocks, and ARI capability blocks.
- Exercise SR-IOV or other virtual-function configurations that instantiate VF2, VF3, VF4, and VF5; validate VF config-space reads, BAR sizing, bus mastering/memory enable behavior, FLR, and isolation-relevant capabilities.
- Exercise MSI and MSI-X interrupt delivery from virtual functions under graphics, compute, reset, and virtualization workloads; lost, stuck-pending, or unexpectedly masked interrupts point to field-layout or offset mismatches.
- Run PCIe link/reset tests covering link speed/width reporting, retraining, data-link active reporting, completion timeout handling, FLR initiation/completion, suspend/resume, and error recovery.
- Use AER fault observation or injection where available to validate uncorrectable/correctable status bits, masks, severity mapping, header logs, TLP prefix logs, and driver recovery decisions.
- Validate ATS/ARI behavior in IOMMU and virtualization scenarios, including ATC enablement, invalidation-related fields, ARI forwarding, and function-number routing.

## Chunk-Specific Notes For Merge

This chunk should be merged with adjacent chunks for `nbio_2_3_sh_mask.h` before producing the final source-tree-aligned per-file research document. Preserve that this slice specifically covers the PF0 VF1 AER/ATS/ARI tail, complete repeated VF2/VF3/VF4 PCIe config masks, and the start of VF5 through `PCIE_CAP`.
