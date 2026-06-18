# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 69195-71626

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask-header slice. It contains C preprocessor constants only: per-field `__SHIFT` and `_MASK` macros for PCI/PCIe configuration-space registers. There are no functions, structs, enums, variables, allocations, locks, loops, branches, or executable statements in this range.

The range starts at the tail of the `BIF_CFG_DEV0_EPF0_VF2_1` virtual-function capability block, covering ARI and Readiness Time Reporting fields, then defines full field layouts for `VF3_1`, `VF4_1`, and `VF5_1`, and ends partway through `VF6_1` at `LINK_CAP`. All of these live under NBIO address blocks named like `nbio_nbif0_bif_cfg_dev0_epf0_vf*_bifcfgdecp`.

Although this source tree is under a `ceph-client` mirror, this file is AMD DRM/AMDGPU hardware metadata. It has no Ceph distributed-filesystem control path.

## Purpose

`nbio_4_3_0_sh_mask.h` publishes generated bit positions and masks for NBIO 4.3.0 registers. This chunk maps PCIe configuration fields for SR-IOV-style virtual functions on device 0, endpoint function 0, instance 1:

- `VF2_1` tail fields for `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, `PCIE_ARI_CNTL`, `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`.
- Complete `VF3_1`, `VF4_1`, and `VF5_1` layouts from standard PCI identity/configuration registers through PCIe capability, MSI/MSI-X, vendor-specific enhanced capability, Advanced Error Reporting, ARI, and Readiness Time Reporting.
- Initial `VF6_1` fields through standard PCI identity/configuration, BARs, PCIe capability, device capability/control/status, and the beginning of `LINK_CAP`.

The macros let consumers extract or compose fields without embedding literal bit positions. Typical use is `value & FIELD_MASK`, `(value & FIELD_MASK) >> FIELD__SHIFT`, or a helper such as `REG_SET_FIELD` where the generated name is part of the hardware ABI.

## Important APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the macro namespace. The chunk contributes 2,140 `#define` lines: 1,072 shift definitions and 1,068 mask definitions.

Important field families visible here include:

- Standard PCI header fields: vendor/device IDs, command/status bits, revision/class codes, cache-line and latency timers, header/BIST, six BARs, CardBus CIS pointer, subsystem adapter IDs, ROM base address, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: capability list linkage, device type, max payload support/size, extended tags, no-snoop, relaxed ordering, FLR, error enables/status, link speed/width, ASPM and link disable/retrain controls, link training/status bits, slot clock, data-link active reporting, and bandwidth notification bits.
- PCIe Capability 2 fields: completion-timeout support/control, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, ten-bit tags, end-to-end TLP prefixes, emergency power reduction, FRS, supported link speeds, compliance/deemphasis controls, equalization status, crosslink/resolution, and DRS status.
- Interrupt capability fields: MSI enablement, multi-message support/enable, 64-bit addressing, per-vector masking, message address/data, MSI mask/pending bits, MSI-X table/PBA offsets and sizes.
- Extended capability fields: vendor-specific capability header/scratch fields, Advanced Error Reporting uncorrectable/correctable status/mask/severity bits, AER control bits, header logs, TLP prefix logs, ARI capability/control, and Readiness Time Reporting data.

The exact VF-suffixed macros in this chunk are mostly generated ABI surface rather than common hand-written call sites in the observed tree. Nearby NBIO 4.3 driver code uses the same register-field pattern for non-VF endpoint registers: `nbio_v4_3.c` reads `regBIF_CFG_DEV0_EPF0_DEVICE_CNTL2`, toggles `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK`, and writes it back through `RREG32_SOC15`/`WREG32_SOC15`. VF consumers would use this chunk's suffixed variants in the same style when addressing virtual-function config space.

## Control Flow

This header chunk has no local control flow. Runtime behavior is supplied by external driver paths:

1. AMDGPU code includes the NBIO 4.3.0 offset and shift/mask headers for matching ASICs.
2. A caller selects an address macro from the sibling offset header for a VF PCI/PCIe config register.
3. The caller reads or writes that hardware register through PCIe, MMIO, SOC15, or generated register helpers.
4. The caller applies this chunk's shift/mask macro to decode a field, test status, preserve unrelated bits, or compose a new value.
5. Hardware state changes or reports status according to the PCIe/NBIO specification.

Ordering, retry, reset, and write-one-to-clear behavior are not encoded here. Those rules must come from the consuming driver path and the hardware spec.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It names bitfields in hardware-visible PCI configuration state for virtual functions. Persistence is therefore controlled by GPU/NBIO reset domains, PCI config-space save/restore, firmware initialization, SR-IOV enablement/disablement, function-level reset, hot reset, suspend/resume, and explicit driver or firmware writes.

Some represented fields are static capabilities, such as max payload support, FLR capability, supported link speeds, MSI-X table size, ARI capability, and readiness-time support. Others are controls, such as bus mastering, interrupt disable, MSI/MSI-X enables, error-reporting enables, max payload size, no-snoop, link retrain, completion-timeout disable, ARI forwarding, LTR enable, OBFF mode, and AER ECRC controls. Several fields are status or diagnostic logs, including PCI status bits, device status, link status, AER error status, first-error pointer, header logs, TLP prefix logs, and readiness-time valid bits.

The macros do not distinguish read-only, read/write, sticky, write-one-to-clear, or firmware-owned fields. Consumers must preserve reserved bits and use the correct access width for each PCIe register.

## Dependencies And Integration Points

Direct dependencies are the sibling generated NBIO headers:

- `nbio_4_3_0_offset.h` supplies the register offsets that pair with these field masks.
- Other generated NBIO 4.3.0 headers provide related reset/default/SMN metadata outside this shift/mask file.

Broader integration points include AMDGPU NBIO initialization, PCIe capability enumeration, SR-IOV virtual-function exposure, PCI resource/BAR handling, MSI/MSI-X interrupt setup, PCIe AER/RAS diagnostics, link training and ASPM/LTR policy, IOMMU and virtualization policy, ARI function routing, FLR handling, and suspend/resume config restore. Similar generated field families exist for other NBIO generations, but these names and masks are specific to NBIO 4.3.0.

## Risks And Edge Cases

- Generated bit drift can compile cleanly while decoding or programming the wrong bit. That is highest risk for control fields such as bus mastering, interrupt disable, MSI/MSI-X enable, max payload size, no-snoop, FLR initiation, LTR, ARI forwarding, AER masks, and link controls.
- This is a chunk boundary. `VF2_1` begins in a preceding chunk, and `VF6_1` continues in a following chunk. The final per-file report must merge adjacent chunks before describing complete VF2/VF6 coverage.
- Multi-bit fields must be shifted after masking. Using the mask as a raw value or forgetting the shift can silently misconfigure fields such as payload sizes, link width/speed, OBFF mode, MSI vector counts, AER first-error pointer, and readiness-time values.
- Several mask names intentionally include repeated words, such as `PCIE_UNCORR_ERR_MASK__DLP_ERR_MASK_MASK`, because the register name and field name both contain `MASK`. String-based tooling must not try to normalize these names.
- PCIe error status bits may be sticky or write-one-to-clear depending on the register. A generic read-modify-write using these masks can accidentally clear diagnostic state if the access semantics are wrong.
- Link-control and compliance fields can affect negotiated link speed, link retraining, electrical compliance mode, and autonomous speed changes. Incorrect writes can cause performance loss or link instability.
- Interrupt table/PBA fields are offset and size descriptors for MSI-X. Wrong interpretation can break vector setup or point the driver at the wrong table aperture.
- VF configuration fields are virtualization-sensitive. Misprogramming ARI, ACS-related AER bits, FLR, MSI/MSI-X, or BAR metadata can affect guest isolation, function routing, reset behavior, or interrupt delivery.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU with NBIO 4.3.0 support enabled to catch syntax, include-order, and missing-macro failures.
- Run generated-register consistency checks against the authoritative NBIO 4.3.0 register database, especially across the repeated VF3/VF4/VF5 blocks and the VF2/VF6 chunk boundaries.
- Boot matching AMD GPUs and verify PCI config-space enumeration, capability-chain traversal, VF discovery, BAR/resource reporting, and interrupt setup.
- Exercise SR-IOV or virtualization paths that expose these virtual functions, including VF enable/disable, FLR, guest driver probing, MSI/MSI-X delivery, and suspend/resume restore.
- Validate PCIe link and power-management behavior around ASPM/LTR/OBFF settings, link retrain/status reporting, and negotiated speed/width.
- Inject or observe PCIe AER/RAS events where possible and confirm uncorrectable/correctable status, masks, severity, header logs, and TLP prefix logs decode as expected.

## Chunk-Specific Notes For Merge

When merging this chunk into the final `nbio_4_3_0_sh_mask.h` research document, preserve that lines 69195-71626 cover the tail of `VF2_1`, all of `VF3_1` through `VF5_1`, and the beginning of `VF6_1`. The range is generated register metadata only; its significance is the breadth of PCIe virtual-function field definitions rather than local algorithmic behavior.
