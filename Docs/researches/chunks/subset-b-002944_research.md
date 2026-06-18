# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 98523-100975

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, variables, allocation, locking, persistence code, or executable control flow.

The range starts in the tail of `BIF_CFG_DEV0_EPF3_1_PCIE_TPH_ST_TABLE_*`, covering steering table entries 19 through 63. It then enters three complete SR-IOV virtual-function PCI configuration address blocks for `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp`, `vf1`, and `vf2`, and finally starts the `vf3` block. The VF0, VF1, and VF2 blocks run from standard PCI identity/header fields through PCIe, MSI/MSI-X, AER, ATS, and ARI capability masks. The VF3 block is partial and ends at `BIF_CFG_DEV0_EPF0_VF3_1_PCIE_CAP__VERSION__SHIFT`.

Although the repository path is under a local `ceph-client` mirror, this file is AMD GPU PCIe/NBIO hardware metadata, not Ceph filesystem logic.

## Purpose

The purpose of this header section is to publish the bit layout contract for NBIO 2.3 PCIe configuration-space registers. Each hardware field is represented by generated macros:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for encoding or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the mask for isolating, preserving, clearing, or updating the field.

Runtime AMDGPU code combines these definitions with the matching NBIO 2.3 offset header and register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. This header does not decide access order, read/write permissions, reset behavior, or side-effect semantics; it only names the field positions.

## Important Macro Families

The opening `BIF_CFG_DEV0_EPF3_1_PCIE_TPH_ST_TABLE_19` through `_63` entries define TPH steering-tag table fields for endpoint function 3 instance 1. Every table register has `TPH_ST_LOWER_ENTRY` at bits 7:0 and `TPH_ST_UPPER_ENTRY` at bits 15:8. These are mechanically regular, but table index and lower/upper half selection are part of the hardware ABI for TPH requester steering.

The `BIF_CFG_DEV0_EPF0_VF0_1_*`, `VF1_1_*`, and `VF2_1_*` blocks each describe a virtual function's PCI-compatible configuration image. Standard header definitions include vendor/device IDs, command and status bits, revision/class code bytes, cache line, latency, header type/device type, BIST controls, BAR1-BAR6, CardBus CIS pointer, subsystem vendor/device IDs, ROM base address, capability pointer, interrupt line/pin, min grant, and max latency.

The command/status fields expose common PCI controls and observations: IO and memory access enables, bus master enable, special cycle, memory-write-invalidate, PAL snoop, parity response, SERR, fast back-to-back, interrupt disable, capability-list presence, interrupt status, parity and system-error status, target/master abort status, and DEVSEL timing. These fields are part of how a VF presents itself to host PCI enumeration and guest drivers.

The PCIe capability blocks define `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. They cover max payload and max read request size, FLR capability/initiation, relaxed ordering, no-snoop, extended tags, phantom functions, completion timeout controls, ARI forwarding, atomic operation support, ID-based ordering, LTR, OBFF, ten-bit tags, end-to-end TLP prefixes, emergency power reduction, link speed/width capability and negotiation, ASPM/clock power management, link disable/retrain, common clock, bandwidth-management interrupts, DRS signaling, equalization status, crosslink reporting, and downstream-component presence.

The interrupt capability blocks cover MSI and MSI-X. MSI definitions include capability list IDs and next pointers, MSI enable, multi-message capability/enable, 64-bit support, per-vector masking support, message address/data fields, mask fields, and pending fields for both 32-bit and 64-bit layouts. MSI-X definitions include table size, function mask, MSI-X enable, table BIR/offset, and pending-bit-array BIR/offset.

The vendor-specific and AER families include `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, vendor payload dwords, `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable/correctable error status and mask fields, uncorrectable severity fields, advanced error capability/control fields, header log dwords, and TLP prefix log dwords. These macros support PCIe RAS/error-reporting paths and diagnostic capture.

The ATS and ARI extended capabilities appear at the end of each complete VF block. ATS fields define enhanced capability list metadata, invalidate queue depth, page-aligned request support, global invalidate support, smallest translation unit (`STU`), and address translation cache enable (`ATC_ENABLE`). ARI fields define enhanced capability list metadata, MFVC/ACS function group capabilities, next-function number, enable bits, and function group selection.

The final `BIF_CFG_DEV0_EPF0_VF3_1_*` subsection only covers the beginning of VF3's config image: vendor/device ID, command/status, revision/class bytes, cache/latency/header/BIST, BAR1-BAR6, CIS pointer, adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, max latency, `PCIE_CAP_LIST`, and the first shift macro for `PCIE_CAP`. Adjacent chunk `subset-b-002945` is needed for the rest of VF3.

## Control Flow

There is no runtime control flow in this chunk. The effective runtime pattern is supplied by AMDGPU NBIO, PCIe, interrupt, reset, and virtualization code:

1. Select the matching register offset from `nbio_2_3_offset.h` or another ASIC register table.
2. Read or construct the PCI config/MMIO value using AMDGPU register access helpers.
3. Use the `__SHIFT` and `_MASK` constants directly, or through helper macros, to extract or update a field.
4. Write the updated value, poll a status field, clear a sticky status, or pass decoded data to higher-level PCIe/SR-IOV logic.

The repeated VF0/VF1/VF2 blocks imply table-like hardware layout for virtual functions, but the header does not implement iteration. Any loop over VFs, capabilities, BARs, or interrupt vectors lives in consuming driver code that chooses the corresponding register offset and macro names.

## State And Persistence Behavior

This header stores no software state and persists nothing to disk. It describes state owned by the GPU, firmware, PCIe fabric, host kernel, and possibly guest drivers when SR-IOV is active.

Some represented fields are configuration that can remain in hardware until reset, FLR, suspend/resume, power transition, guest reconfiguration, or explicit driver reprogramming: PCI command enables, BAR values, ROM BAR, MSI/MSI-X message address/data and masks, max payload/read request settings, completion timeout controls, ATS `ATC_ENABLE`, ARI controls, link control bits, AER masks/severity, and interrupt masking.

Other represented fields are static capabilities, hardware-updated observations, command strobes, sticky status, or diagnostic logs: vendor/device/class identity, PCIe capability values, link status, device status, AER status, header/TLP prefix logs, MSI pending bits, FLR initiation, ATS invalidate capability, and ARI next-function information. The generated names do not distinguish safe read-modify-write fields from write-one-to-clear or side-effectful fields.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This shift/mask header must stay synchronized with sibling generated headers under `drivers/gpu/drm/amd/include/asic_reg/nbio/`, especially `nbio_2_3_offset.h`, which supplies the register addresses for the field layouts documented here.

Primary integration points are AMDGPU NBIO and PCIe code paths that expose, program, or diagnose PF/VF PCI configuration space. The VF blocks are relevant to SR-IOV and virtualized GPU operation because they describe what each virtual function presents for PCI identity, BARs, interrupts, PCIe capability negotiation, AER reporting, ATS address translation, and ARI routing/function grouping.

Interrupt integration depends on the MSI/MSI-X definitions. Reset and recovery integration depends on PCI command/status, FLR, AER, and link status/control fields. Memory/resource management integration depends on BAR and ROM BAR masks. IOMMU and virtualization integration depends on ATS, ARI, command bus-mastering, memory access enables, and error/isolation fields.

The macros are untyped integer constants. A missing or renamed macro usually fails at compile time, but an incorrect shift or mask can compile cleanly while making the driver read, clear, or program the wrong hardware bit.

## Risks And Edge Cases

- Chunk boundaries are partial. The opening lines continue an EPF3 TPH table sequence from the previous chunk, and the ending line stops inside VF3's `PCIE_CAP` register. Adjacent chunks are required before making complete-register claims for those areas.
- The VF0, VF1, and VF2 blocks are highly repetitive. Copy/paste or generation drift can cause one VF to expose different masks than another, which may only appear under SR-IOV or guest assignment testing.
- PCIe status and error fields can be sticky or write-one-to-clear. Treating AER status, device status, MSI pending, or link status as ordinary configuration can hide faults or erase useful logs.
- MSI/MSI-X fields are interrupt-delivery critical. Wrong enable, function-mask, table/PBA offset, message address/data, vector mask, or pending-bit masks can cause lost, misrouted, or unexpectedly unmasked interrupts.
- BAR fields are full-width and not self-validating in this header. Pairing the right full-width mask with the wrong VF or offset can expose the wrong aperture or corrupt virtual-function resource assignment.
- Link and PCIe capability controls affect enumeration and interoperability. Incorrect max payload/read request, completion timeout, relaxed ordering, no-snoop, FLR, ASPM, retrain, or target-speed masks can cause device resets, DMA ordering issues, or link instability.
- ATS and ARI fields are virtualization-sensitive. Wrong `ATC_ENABLE`, `STU`, function-group, next-function, or forwarding masks can break IOMMU translation behavior, VF routing, or guest isolation.
- TPH steering tables are dense and indexed. Off-by-one table selection or lower/upper entry confusion can silently steer traffic using the wrong tag.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU for ASICs using NBIO 2.3 headers with PCIe, MSI/MSI-X, AER, SR-IOV, ATS, ARI, and reset support enabled; macro name drift should surface as compile failures.
- Run generated-header consistency checks against the authoritative NBIO 2.3 register source and matching offset header, including shift/mask width, overlap, and per-VF consistency checks.
- Boot hardware using these headers and confirm PCI enumeration for the relevant PF/VF surfaces shows expected vendor/device IDs, class codes, BARs, capability-list traversal, PCIe capability data, and interrupt capability layout.
- Exercise SR-IOV VF creation, assignment, reset, and teardown for VF0 through VF3, checking that each virtual function presents consistent config-space fields.
- Test MSI and MSI-X delivery under physical and virtualized workloads, including vector masking, pending bits, function mask behavior, and table/PBA placement.
- Run PCIe reset and recovery paths covering FLR initiation, command/status changes, link retraining/status, completion timeout behavior, and suspend/resume.
- Use AER/error-injection or fault-observation tests to validate uncorrectable/correctable status, masks, severity, header logs, TLP prefix logs, and recovery handling.
- Validate ATS/ARI behavior in IOMMU and virtualization configurations, including address-translation enablement, STU settings, ARI function routing, and guest isolation.

## Chunk-Specific Notes For Merge

Merge this chunk with adjacent chunks for `nbio_2_3_sh_mask.h` before producing the final per-file research document. Preserve that this slice covers TPH steering table entries 19-63 for `BIF_CFG_DEV0_EPF3_1`, complete `BIF_CFG_DEV0_EPF0_VF0_1`, `VF1_1`, and `VF2_1` PCIe config-space field masks, and only the beginning of `BIF_CFG_DEV0_EPF0_VF3_1` through the first `PCIE_CAP` shift.
