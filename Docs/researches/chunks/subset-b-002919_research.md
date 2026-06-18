# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 36636-39061

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, variables, allocation, locking, persistence code, or executable control flow.

The range starts in the middle of `BIF_CFG_DEV0_EPF0_VF11_LINK_CAP2`, continues through the rest of virtual function 11's PCIe config capability block, then covers nearly complete repeated config-space field definitions for virtual functions 12, 13, and 14. It ends inside the VF14 ARI enhanced-capability list definition, before the VF14 ARI capability/control fields that follow in the next chunk. Although the repository path is under a local `ceph-client` source mirror, this file is AMD GPU NBIO/PCIe hardware metadata, not Ceph filesystem logic.

## Purpose

The purpose of this header chunk is to publish the bit layout contract for NBIO 2.3 virtual-function PCI/PCIe configuration decoder registers. Each represented field is exposed as one or both of:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position for encoding or decoding the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update the field.

The companion `nbio_2_3_offset.h` file maps these same `BIF_CFG_DEV0_EPF0_VF*_0_*` register names to PCI configuration offsets. AMDGPU code includes both the offset header and this shift/mask header from NBIO paths such as `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU power-management files. Runtime code then uses AMDGPU register helpers and field helpers such as `RREG32_*`, `WREG32_*`, `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC15/NBIO register-address macros to access the actual hardware fields.

## Important Macro Families

The VF11 portion begins at the tail of second-generation link capability fields. It includes supported link speed masks, crosslink support, lower SKP ordered-set generation/receive support, retimer presence-detect support, DRS reserved/support bit naming, link control 2 fields for target speed, compliance entry, autonomous speed disable, de-emphasis, transmit margin, modified compliance, and compliance SOS. It also defines link status 2 fields for current de-emphasis, 8 GT/s equalization completion and phase success, link equalization request, retimer detection, crosslink resolution, downstream-component presence, and DRS message receipt.

The MSI and MSI-X blocks repeat for VF11 through VF14. MSI definitions cover capability list ID/next pointer, enable, multi-message capability and enable fields, 64-bit support, per-vector masking capability, low/high MSI message address, message data, mask, 64-bit data/mask aliases, and pending bits. MSI-X definitions cover capability list ID/next pointer, table size, function mask, MSI-X enable, table BIR/offset, and pending-bit-array BIR/offset.

The PCIe vendor-specific capability block defines enhanced-capability list metadata, VSEC header fields, and two scratch dwords for each VF. These are generic vendor-specific config-space slots; the macros only describe the field placement and do not define firmware or hypervisor policy for the scratch registers.

The advanced error reporting block is dense and repeated. For VF11 through VF14 it defines AER enhanced-capability list metadata, uncorrectable error status/mask/severity fields, correctable error status/mask fields, advanced error capability/control bits, four TLP header-log dwords, and four TLP-prefix-log dwords. The uncorrectable families include data link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress blocked, and TLP prefix blocked bits. The correctable families include receiver error, bad TLP, bad DLLP, replay number rollover, replay timer timeout, advisory nonfatal error, correctable internal error, and header-log overflow.

VF12, VF13, and VF14 each start with a full standard PCI header and conventional PCIe capability layout. The standard fields include vendor/device ID, command, status, revision and class-code bytes, cache-line size, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency. Command/status masks expose ordinary PCI access enables, bus mastering, SERR and interrupt-disable controls, capability-list presence, parity and target/master abort status, DEVSEL timing, and detected parity error.

The PCIe capability and device/link blocks for VF12 through VF14 include PCIe capability list metadata, port type, slot implementation, interrupt message number, max payload support, phantom functions, extended tags, endpoint L0s/L1 acceptable latencies, role-based error reporting, captured slot power limit, FLR support, max payload/read request programming, relaxed ordering, no-snoop, auxiliary power PM, phantom function enable, extended tag enable, error reporting enables, unsupported request reporting, fatal/nonfatal/correctable detected status, transaction pending, link speed/width/aspm capability, L0s/L1 exit latencies, clock power management, surprise down reporting, data link active reporting, link bandwidth notification support, ASPM control, common clock, retrain, link disable, read completion boundary, extended sync, hardware autonomous width disable, link bandwidth interrupt enables/status, target link speed, compliance controls, equalization status, and Gen2+ link capability/status fields.

The second-generation device capability/control fields cover completion timeout support/disable, ARI forwarding, AtomicOp support and request enable, AtomicOp egress blocking, ID-based ordering request/completion enable, latency tolerance reporting, OBFF support/enable, ten-bit tag support/enable, end-to-end TLP prefix support/blocking, emergency power reduction, fast role swap, and reserved device-status 2 words. The ATS blocks define enhanced-capability list metadata, invalidate queue depth, page-aligned request support, global invalidate support, small translation unit, and ATC enable. The chunk ends at the beginning of the VF14 ARI enhanced-capability list, after its `CAP_ID`, `CAP_VER`, `NEXT_PTR`, and `CAP_ID_MASK` definitions.

## Control Flow

There is no runtime control flow in this chunk. The effective use pattern is supplied by consuming driver code:

1. Choose the appropriate virtual-function register offset from `nbio_2_3_offset.h` or another ASIC-specific register-address path.
2. Read the corresponding PCIe config or NBIO register through AMDGPU register access helpers.
3. Decode a field by applying the generated `_MASK` and `__SHIFT` constants directly or through helper macros such as `REG_GET_FIELD`.
4. For writable fields, merge a new field value with preserved register bits, commonly through `REG_SET_FIELD`, then write the value back through the same access path.

The repeated VF12/VF13/VF14 layout is table-like hardware metadata, but the header does not implement iteration over VFs or capabilities. Any loop, VF selection, SR-IOV policy, reset sequencing, interrupt setup, link training, or error-recovery behavior is implemented in AMDGPU/NBIO/PCIe/SR-IOV code outside this generated header.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-visible PCI configuration and PCIe extended capability state owned by the GPU, PCIe fabric, firmware, host kernel, and virtualization stack.

Some represented fields are configuration that can persist until reset, FLR, suspend/resume, power transition, VF teardown, or explicit reprogramming: command access enables, bus mastering, interrupt disable, BAR values, MSI/MSI-X message address/data/masks, device/link controls, completion timeout controls, AER masks and severity bits, ECRC controls, ATS control, ARI capability-list metadata, and vendor-specific scratch dwords.

Other fields are hardware-owned observations, sticky status, logs, pending bits, or write-one-to-clear style status in real PCIe hardware: PCI status errors, device and link status, link equalization state, bandwidth status, AER uncorrectable/correctable error status, first-error pointer, multi-header received state, TLP header logs, TLP prefix logs, MSI pending bits, and MSI-X pending-bit-array state. The macro names do not encode access permissions or clear semantics; consumers must follow PCIe and AMDGPU register programming rules.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This shift/mask header must stay synchronized with sibling generated headers under `drivers/gpu/drm/amd/include/asic_reg/nbio/`, especially `nbio_2_3_offset.h`, because offset macros select the register address while this file selects the fields within the register value.

Primary integration points are AMDGPU NBIO initialization, PCIe configuration, interrupt setup, AER/RAS diagnostics, power-management paths, suspend/resume, reset/FLR handling, and SR-IOV virtualization. `nbio_v2_3.c` and `mxgpu_nv.c` include this header directly, and SMU power-management files include it for ASIC-specific NBIO register programming. The VF-oriented macro families are especially relevant when a PF, host driver, hypervisor, or guest-visible path needs to reason about virtual-function PCI headers, link capability reporting, MSI/MSI-X programming, AER exposure, ATS enablement, or ARI traversal.

Because these are untyped preprocessor constants, missing or renamed macros usually fail at compile time, but incorrect numeric shifts or masks can compile cleanly and produce wrong hardware programming. Manual edits should be treated as changes to an ASIC register ABI and checked against AMD's authoritative register source.

## Risks And Edge Cases

- Chunk boundaries are partial. The first lines are already inside VF11 `LINK_CAP2`, and the final line stops inside VF14 `PCIE_ARI_ENH_CAP_LIST`; adjacent chunks are needed for whole-register and whole-VF conclusions.
- Access width matters. The range mixes 8-bit PCI config bytes, 16-bit command/status/capability words, and 32-bit dwords. Using a 32-bit read-modify-write against byte/word fields without preserving neighboring bytes can corrupt adjacent PCI config state.
- Status and log fields are not distinguished by type. AER status, PCI status, link status, MSI pending, and log registers may be sticky or write-one-to-clear in hardware; generic read-modify-write treatment is unsafe without the relevant PCIe semantics.
- Interrupt definitions are delivery-critical. Bad MSI/MSI-X enable, function mask, message address/data, table/PBA offset, vector mask, or pending-bit interpretation can cause lost interrupts, spurious interrupts, or incorrect VF isolation.
- Link and equalization fields are interoperability-sensitive. Incorrect target speed, compliance, de-emphasis, autonomous speed disable, equalization, DRS, retimer, or downstream-presence masks can cause link training failures, misleading diagnostics, or resume regressions.
- VF repetition creates off-by-one risk. VF11 through VF14 names are nearly identical; selecting the wrong VF register family or offset can expose, configure, or diagnose the wrong virtual function.
- AER mask/severity mistakes can hide real PCIe faults, escalate recoverable errors as fatal, or make header/TLP-prefix logs decode against the wrong bit layout.
- ATS and ARI fields affect isolation and enumeration. Incorrect ATC enable, translation unit, invalidate capability, or ARI capability-list metadata can break IOMMU-assisted operation or VF function discovery.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU for ASICs using NBIO 2.3 headers, with PCIe, MSI/MSI-X, AER, SR-IOV, ATS, ARI, reset, and power-management support enabled; missing macros should surface as compile failures.
- Run generated-header consistency checks against the NBIO 2.3 register source and sibling offset headers, including shift/mask pair presence, field width validation, and non-overlap checks within each register.
- Boot and PCI enumeration tests confirming VF12 through VF14 expose expected vendor/device IDs, class codes, BAR layout, command/status bits, capability pointers, PCIe capability structures, MSI/MSI-X capabilities, AER capability, ATS capability, and ARI enhanced-capability links.
- MSI/MSI-X interrupt tests for virtual functions, including enable/disable, function mask, vector mask, pending bits, 32-bit versus 64-bit message address/data handling, and table/PBA placement.
- PCIe link tests covering target speed, negotiated speed/width, retrain, autonomous speed controls, de-emphasis, equalization phase reporting, retimer detection, DRS reporting, bandwidth status, and suspend/resume transitions.
- AER or fault-injection tests validating uncorrectable/correctable status, mask, severity, first-error pointer, ECRC controls, header logs, TLP prefix logs, and recovery paths for each represented VF.
- SR-IOV and IOMMU tests validating that ATS enablement, invalidate capability reporting, ARI capability-list traversal, and per-VF PCI config access affect only the intended VF.

## Chunk-Specific Notes For Merge

Merge this chunk with adjacent `nbio_2_3_sh_mask.h` chunks before producing the final source-tree-aligned per-file research document. Preserve that this slice covers the VF11 PCIe capability tail plus full VF12/VF13 and almost-full VF14 standard PCI, PCIe, MSI/MSI-X, vendor-specific, AER, ATS, and partial ARI field definitions.
