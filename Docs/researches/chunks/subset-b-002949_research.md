# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 110671-113093

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-field shift/mask header slice. It contains only C preprocessor constants: no functions, structs, enums, variables, allocation, locking, persistence code, or executable control flow.

The range starts inside the PF0 virtual-function 17 block (`BIF_CFG_DEV0_EPF0_VF17_1_*`) at the mask for `BASE_ADDR_1`, after the matching register comment and shift definition in the previous chunk. It then covers the rest of VF17 from BAR2 and PCI header tail fields through PCIe, MSI/MSI-X, vendor-specific, AER, ATS, and ARI capability masks. It includes complete repeated PCI/PCIe configuration images for VF18 and VF19 (`BIF_CFG_DEV0_EPF0_VF18_1_*`, `BIF_CFG_DEV0_EPF0_VF19_1_*`). It begins VF20 (`BIF_CFG_DEV0_EPF0_VF20_1_*`) and carries that block through MSI capability address/data/mask fields, ending at the comment for `MSI_PENDING`; the VF20 MSI pending definitions and later VF20 MSI-X/AER/ATS/ARI fields are outside this chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMD GPU NBIO/PCIe hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bit layout contract for NBIO 2.3 PCI configuration decoder registers that expose PF0 virtual-function PCI and PCIe capabilities. Each register field is represented by generated macros of the form:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to pack or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update the field.

The companion generated offset headers provide the register addresses; this `*_sh_mask.h` file only gives the bit positions and masks within those registers. AMDGPU consumers normally combine these macros with register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. The header does not define access width, reset values, ownership, read/write permissions, or side-effect behavior.

## Important Macro Families

The VF17 tail starts with standard PCI configuration-space tail fields. It defines BAR2 through BAR6 and carries a dangling `BASE_ADDR_1` mask from the previous chunk, CardBus CIS pointer, subsystem adapter ID, ROM base, capability pointer, interrupt line and pin, min grant, and max latency. These fields use full 32-bit masks for BAR-like registers, 8-bit masks for legacy byte fields, and split 16-bit masks for subsystem vendor/device identifiers.

The VF17 PCIe capability section defines capability-list metadata, PCIe capability version/device-type fields, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2, and MSI/MSI-X layout fields. Important feature bits include maximum payload and read request sizing, relaxed ordering, no-snoop, extended tags, function-level reset capability/initiation, correctable/non-fatal/fatal/unsupported request reporting enables, transactions pending, link speed and width, ASPM and clock power management, retrain/link disable/common clock/extended sync, bandwidth-management interrupts, data-link active reporting, DRS signaling, completion timeout controls, ARI forwarding, atomic operation controls, ID-based ordering, LTR, OBFF, ten-bit tag support, emergency power reduction, fast role swap, supported link speeds, compliance/de-emphasis controls, 8 GT/s equalization status, crosslink resolution, and downstream-component presence.

The VF17 interrupt groups define MSI and MSI-X capability layouts. MSI fields cover capability-list metadata, MSI enable, multiple-message capability and enable, 64-bit support, per-vector masking capability, message address low/high, message data, mask, 64-bit data/mask aliases, and pending bits. MSI-X fields cover capability-list metadata, table size, function mask, MSI-X enable, table BIR/offset, and pending-bit-array BIR/offset.

The VF17 vendor-specific and PCIe Advanced Error Reporting groups define enhanced-capability list metadata, vendor-specific header and payload dwords, AER uncorrectable error status/mask/severity, AER correctable error status/mask, AER capability/control, four header-log dwords, and four TLP-prefix-log dwords. The represented AER conditions include DLP, surprise-down, poisoned TLP, flow-control protocol, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC-blocked TLP, atomic operation egress blocking, and TLP prefix blocking. Correctable-error fields include receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, internal correctable, and header-log overflow.

The VF17 ATS and ARI enhanced-capability groups define capability-list headers plus payload fields for address-translation services and alternative routing-ID interpretation. ATS fields include invalidate queue depth, page-aligned request support, global invalidate support, smallest translation unit, and ATC enable. ARI fields include MFVC and ACS function-group capability/enable bits, next-function number, and selected function group.

The VF18 and VF19 blocks are complete repeated virtual-function PCI configuration images. Each begins with ordinary PCI header fields: vendor/device ID, command/status, revision and class-code bytes, cache line size, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency. Each then repeats the same PCIe device/link capability, MSI/MSI-X, vendor-specific, AER, ATS, and ARI macro families described for VF17.

The VF20 block is partial. It includes the standard PCI header and BAR-related fields, PCIe capability metadata and device/link capability/control/status fields through link status 2, then begins MSI with `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address low/high, message data, mask, 64-bit data alias, and 64-bit mask alias. The chunk stops before the `MSI_PENDING` shift/mask definitions and before VF20 MSI-X, vendor-specific, AER, ATS, and ARI groups.

## Control Flow

There is no runtime control flow in this header. The effective use pattern in AMDGPU code is:

1. Select the corresponding NBIO 2.3 config-space register offset from the generated offset header or a per-ASIC register table.
2. Read or prepare a PCIe config register value through the driver's PCIe/SOC15 access helpers.
3. Use the `__SHIFT` and `_MASK` constants directly, or through helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`, to decode or update a specific field.
4. Write the value back, poll a hardware-owned status bit, clear sticky error state according to PCIe rules, or hand the decoded value to reset, interrupt, virtualization, or RAS/error handling code.

The repeated VF17/VF18/VF19/VF20 naming implies a table-like hardware layout, but this header does not implement iteration. Any loop over virtual functions or capability families is implemented by driver code that chooses the matching register offset and macro family.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes GPU PCI configuration and enhanced-capability state owned by hardware, firmware, the PCIe fabric, the host kernel, and the AMDGPU driver.

Some represented fields are configuration state that can remain programmed until reset, function-level reset, suspend/resume, power transition, or explicit driver reprogramming: PCI command enables, BAR values, MSI/MSI-X message address/data/mask state, PCIe device/link controls, completion timeout controls, ARI forwarding, atomic operation controls, ID-based ordering, LTR/OBFF controls, ATS ATC enablement, and ARI function grouping.

Other fields are hardware-owned status, command strobes, or sticky diagnostic state: PCI status bits, BIST start/completion, device/link status, link training and equalization status, transactions pending, MSI pending bits, AER correctable/uncorrectable status, AER header logs, and TLP prefix logs. The masks do not encode whether a bit is read-only, write-one-to-clear, write-one-to-set, self-clearing, firmware-owned, or volatile; callers must follow the hardware programming guide and PCIe specification behavior for each register.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This `*_sh_mask.h` slice must stay synchronized with sibling generated headers under `drivers/gpu/drm/amd/include/asic_reg/nbio/`, especially offset headers that give the register addresses for these field names.

Primary integration is with AMDGPU NBIO, PCIe, interrupt, reset, RAS/AER, SR-IOV, and virtualization paths. These macros support virtual-function config-space exposure and driver-side interpretation of function identity, BARs, command/status, PCIe device/link capabilities, MSI/MSI-X delivery, AER status/logging/masking/severity, ATS address-translation services, ARI routing/function grouping, and function-level reset behavior.

The macros are untyped integer constants. Missing or renamed macro names usually fail at compile time in consuming code, but an incorrect shift or mask can compile cleanly and cause adjacent PCIe fields to be read, cleared, or programmed incorrectly. Because this file is generated ASIC metadata, manual changes should be treated as hardware ABI changes and checked against the authoritative register source.

## Risks And Edge Cases

- Chunk boundaries are partial. The first line is already inside VF17 `BASE_ADDR_1`, and the last line is only the comment for VF20 `MSI_PENDING`; adjacent chunks are required before making whole-register or whole-VF claims for VF17 and VF20.
- The range mixes 8-bit PCI header fields, 16-bit PCI/PCIe capability words, and 32-bit enhanced-capability dwords. Wrong access width or offset pairing can corrupt neighboring fields even when a mask is locally correct.
- Full-width BAR, ROM base, CIS pointer, MSI address, AER log, TLP-prefix log, and vendor-specific dword fields are not self-validating. Pairing a correct full-width mask with the wrong offset can overwrite or decode unrelated hardware state.
- AER fields are side-effect sensitive. Treating uncorrectable/correctable status bits, severity bits, header logs, or TLP prefix logs as ordinary retained configuration can clear evidence, hide real errors, or misclassify recovery severity.
- Link and device-control fields are interoperability-sensitive. Incorrect max payload/read request, completion timeout, relaxed ordering, no-snoop, FLR, ASPM, retrain, target speed, equalization, or DRS masks can cause enumeration failures, link retraining problems, performance regressions, or reset hangs.
- MSI/MSI-X fields are interrupt-delivery critical. Wrong enable, message address/data, mask, pending, table, PBA, or function-mask fields can cause lost interrupts, spurious interrupts, or poor isolation between virtual functions.
- ATS and ARI fields affect I/O address translation and PCIe function routing. Incorrect STU/ATC enable, queue-depth, global invalidate, ARI forwarding, next-function, or function-group masks can break DMA address translation, virtual-function discovery, or isolation.
- The VF18 and VF19 blocks are highly repetitive and VF20 repeats the same pattern until the chunk boundary. Off-by-one copy or generation errors are plausible and may only appear on configurations that instantiate or exercise the affected virtual function.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU for ASICs using NBIO 2.3 headers with PCIe, MSI/MSI-X, AER, SR-IOV, ATS, and ARI support enabled; missing symbols should surface as compile failures in NBIO/PCIe/interrupt/virtualization code.
- Run generated-header consistency checks against the NBIO register database and sibling offset headers, including shift/mask pair checks, field width checks, non-overlap checks within each register, and repeated VF layout comparison for VF17 through VF20.
- Boot affected hardware and confirm PCI enumeration exposes stable VF vendor/device IDs, class codes, BARs, capability-list traversal, PCIe capability blocks, MSI/MSI-X capability blocks, AER capability blocks, ATS capability blocks, and ARI capability blocks.
- Exercise SR-IOV or other virtual-function configurations that instantiate VF17, VF18, VF19, and VF20; validate VF config-space reads, BAR sizing, bus mastering/memory enable behavior, FLR, and isolation-relevant capabilities.
- Exercise MSI and MSI-X interrupt delivery from virtual functions under graphics, compute, reset, and virtualization workloads; lost, stuck-pending, or unexpectedly masked interrupts point to field-layout or offset mismatches.
- Run PCIe link/reset tests covering link speed/width reporting, retraining, data-link active reporting, completion timeout handling, FLR initiation/completion, suspend/resume, and error recovery.
- Use AER fault observation or injection where available to validate uncorrectable/correctable status bits, masks, severity mapping, header logs, TLP prefix logs, and driver recovery decisions.
- Validate ATS/ARI behavior in IOMMU and virtualization scenarios, including ATC enablement, invalidation-related fields, ARI forwarding, and function-number routing.

## Chunk-Specific Notes For Merge

This chunk should be merged with adjacent chunks for `nbio_2_3_sh_mask.h` before producing the final source-tree-aligned per-file research document. Preserve that this slice specifically covers the PF0 VF17 tail from BAR masks through ARI, complete repeated VF18 and VF19 PCIe config masks, and the start of VF20 through the MSI mask aliases with the `MSI_PENDING` comment as the terminal boundary.
