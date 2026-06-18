# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 31802-34237

## Purpose

This chunk is an auto-generated AMD NBIO 7.4 register shift/mask slice for PCIe configuration-space fields under `BIF_CFG_DEV0_EPF0`. It contains no executable logic; its job is to expose compile-time constants that NBIO 7.4 consumers can pair with register offsets from `nbio_7_4_offset.h` when decoding or programming PCIe endpoint virtual-function configuration registers.

The selected range starts at the tail of the VF0 Advanced Error Reporting area, then covers full config-space decode blocks for `VF1`, `VF2`, and `VF3`, and begins the `VF4` block through the early `DEVICE_CNTL2` fields. These definitions model standard PCI/PCIe config registers plus MSI/MSI-X, AER, ATS, and ARI capability fields for SR-IOV virtual functions exposed by the GPU's NBIO/PCIe block.

## Public Surface In This Chunk

The public surface is preprocessor-only:

- 2,436 source lines in the assigned range.
- 2,138 `#define` lines.
- 1,067 `__SHIFT` definitions.
- 1,176 `_MASK`-bearing definitions.
- 290 generated register-comment or address-block comment lines.

Macro names follow the generated convention:

- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>__SHIFT` gives a field's low bit position.
- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>_MASK` gives the pre-shifted field mask.
- Names such as `*_ERR_MASK__DLP_ERR_MASK_MASK` are intentional: the hardware register is itself an error-mask register, so the generated field name also contains `MASK`.

There are no functions, structs, enums, storage objects, inline helpers, or runtime APIs. The ABI is the exact macro name/value set generated from AMD's NBIO 7.4 register database.

## Register Coverage

The VF0 portion continues from the previous chunk and covers the end of AER for `BIF_CFG_DEV0_EPF0_VF0_0`:

- Correctable error status/mask bits for receiver errors, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, internal correctable error, and header-log overflow.
- AER capability/control fields for first error pointer, ECRC generation/checking capability and enable bits, multiple-header recording, TLP-prefix logging, and completion-timeout logging.
- Header log and TLP prefix log dwords.
- ATS enhanced-capability header, ATS capability, and ATS control.
- ARI enhanced-capability header, ARI capability, and ARI control.

The VF1, VF2, and VF3 blocks are complete virtual-function config-space maps in this range. Each block includes:

- Conventional PCI identity and command/status fields: vendor/device ID, command enables, status flags, revision/class/program interface, cache line, latency, header type, BIST, six BARs, subsystem IDs, ROM BAR, capability pointer, and interrupt line/pin.
- PCIe capability fields: PCIe capability header, device/link capability, control, and status, plus capability/control/status 2 groups.
- MSI and MSI-X capability fields: enable bits, multi-message fields, 64-bit and per-vector masking support, message address/data, mask and pending vectors, MSI-X table/PBA BIR and offsets, table size, function mask, and global enable.
- Vendor-specific enhanced capability fields with VSEC header and scratch dwords.
- AER enhanced capability fields: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, and TLP prefix logs.
- ATS and ARI enhanced-capability groups with capability-list metadata and enable/control bits.

The VF4 block begins in this chunk and covers identity/config basics through part of PCIe device control 2:

- Conventional PCI identity, command/status, class/revision, BAR, subsystem, ROM, interrupt, PCIe capability, device/link capability/control/status, and early device capability 2 fields.
- The range ends mid-`BIF_CFG_DEV0_EPF0_VF4_0_DEVICE_CNTL2`, after fields such as completion timeout control, ARI forwarding, atomic request/egress behavior, ID-based ordering, LTR enable, and emergency power reduction request have begun. The remaining VF4 device-control-2 masks and later VF4 capability groups are in the following chunk.

## Important Fields And Semantics

The conventional PCI fields gate host-visible access for each VF. `COMMAND` fields control I/O access, memory access, bus mastering, parity/SERR reporting, and interrupt disable behavior. `STATUS` fields expose capability-list presence and legacy error indications. BAR and ROM fields describe or decode VF address apertures, while adapter/subsystem fields identify the virtual function to the host.

The PCIe device/link fields advertise and control transport behavior. `DEVICE_CAP` and `DEVICE_CAP2` expose payload size support, extended tags, FLR capability, completion-timeout support, ARI forwarding support, atomic operations, LTR, OBFF, 10-bit tags, TLP prefixes, and emergency power reduction support. `DEVICE_CNTL` and `DEVICE_CNTL2` enable error reporting, relaxed ordering, no-snoop, maximum payload/read request sizes, FLR, completion-timeout policy, ARI forwarding, atomics, ID-based ordering, LTR, OBFF, and prefix blocking.

The link fields describe negotiated PCIe link state for each VF's config view: supported/current link speed, link width, ASPM/PM support, exit latencies, clock power management, surprise-down/data-link-active reporting, bandwidth notification capability, retrain/link-disable controls, target link speed, compliance controls, de-emphasis, equalization status, crosslink status, and downstream presence.

The MSI/MSI-X fields drive interrupt routing for virtual functions. MSI macros expose enablement, number of messages, 64-bit addressing, per-vector masking, address/data payloads, mask vectors, and pending vectors. MSI-X macros expose table size, enable/function mask bits, table BIR/offset, and PBA BIR/offset. Misdecoding these fields can break VF interrupt delivery or isolation.

The AER fields define how PCIe errors are captured and classified. Uncorrectable status/mask/severity fields cover DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, multicast blocked TLP, atomic egress blocking, and TLP prefix blocking. Correctable fields cover receiver errors, bad TLP/DLLP, replay issues, advisory non-fatal, internal correctable errors, and header-log overflow. Header and prefix logs are full-register payload fields used for post-error diagnosis.

ATS and ARI capability groups expose virtualization and address-translation controls. ATS fields advertise invalidate queue depth, page-aligned request support, global invalidation, STU, and ATC enable. ARI fields advertise function grouping and next-function metadata and allow MFVC/ACS function-group enablement and function-group selection.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. NBIO 7.4-aware code includes `nbio/nbio_7_4_sh_mask.h` and the matching `nbio/nbio_7_4_offset.h`.
2. A caller selects a config-space offset such as `cfgBIF_CFG_DEV0_EPF0_VF1_0_COMMAND`, `cfgBIF_CFG_DEV0_EPF0_VF2_0_LINK_STATUS`, `cfgBIF_CFG_DEV0_EPF0_VF3_0_PCIE_UNCORR_ERR_STATUS`, or `cfgBIF_CFG_DEV0_EPF0_VF4_0_DEVICE_CNTL2`.
3. The caller uses these `__SHIFT` and `_MASK` constants through AMD's register helper macros or open-coded bit operations to extract, preserve, insert, or compare fields.
4. The actual access occurs through PCI config-space, MMIO, indirect PCIE access, firmware-mediated paths, or debug/register-dump logic outside this header.

The header stores no software state and persists nothing by itself. Persistent state lives in hardware config registers and may be owned by the host PCI core, AMDGPU, firmware, a hypervisor, or hardware state machines depending on platform mode. Control fields persist until reset, FLR, VF teardown/recreation, power transition, link retrain, or explicit reprogramming. Status, log, pending, and error fields may be hardware-updated, sticky, write-one-to-clear, or read-only according to the PCIe spec and AMD hardware rules.

## Dependencies And Integration Points

The direct generated-header dependency is `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`. The matching offset header defines the config addresses for the same register names; for example, `cfgBIF_CFG_DEV0_EPF0_VF<n>_0_COMMAND` at `0x0004`, `LINK_STATUS` at `0x0076`, `DEVICE_CNTL2` at `0x008c`, `PCIE_UNCORR_ERR_STATUS` at `0x0154`, `PCIE_ATS_CNTL` at `0x02b6`, and `PCIE_ARI_CNTL` at `0x032e` for VF0 through VF4.

NBIO 7.4 mask include sites in this source tree include `amdgpu/nbio_v7_4.c`, SMU power-management files for Arcturus/Aldebaran/SMU 13.0.6, and Vega20 PowerPlay code. A repository search did not find direct in-tree references to the long `BIF_CFG_DEV0_EPF0_VF<n>_0_*` macro names in AMDGPU/PM C files, which indicates this range is mostly generated register ABI surface for config decoders, diagnostics, future feature code, or paths not using these full macro names directly.

Semantic dependencies include the PCI and PCI Express configuration-space specifications plus the PCIe extended capabilities represented here: MSI, MSI-X, AER, ATS, ARI, LTR, OBFF, atomic operations, completion timeout, end-to-end TLP prefixes, and VF function-level reset. For virtualization, these fields also integrate with Linux PCI SR-IOV enumeration, hypervisor-managed VF lifecycle, VF BAR sizing/mapping, interrupt remapping, and AMDGPU firmware/PSP/SMU policy where those components configure or virtualize PCIe state.

## Risks And Maintenance Notes

- The assigned range starts and ends mid-context: it begins after part of VF0 AER severity and ends inside VF4 `DEVICE_CNTL2`. Adjacent chunks are required for a complete VF0 and VF4 view.
- Prefixes are not interchangeable. `VF1`, `VF2`, `VF3`, and `VF4` macros have repeated register names and often identical numeric masks, but they must be paired with the matching `cfgBIF_CFG_DEV0_EPF0_VF<n>_0_*` offset and function context.
- Generated names with doubled `MASK` are valid and should not be "cleaned up" manually.
- Full-width `0xFFFFFFFFL` masks identify whole-register BARs, addresses, logs, scratch registers, masks, pending vectors, or payload dwords; they do not imply all bits are writable or safe to set.
- AER status/severity/mask errors can change driver-visible fault classification, hide real hardware faults, or turn non-fatal conditions into fatal paths.
- MSI/MSI-X field mistakes can break VF interrupt delivery, vector masking, pending-bit handling, or isolation between functions.
- ATS and ARI control bits affect address translation and function routing. Incorrect decoding can cause IOMMU/PRI/ATS failures or cross-function behavior in virtualized deployments.
- PCIe link-control fields can trigger retraining, compliance behavior, power-management changes, or bandwidth notification state; consumers must preserve reserved bits and respect hardware sequencing.
- The header does not encode access width, reset value, read/write permissions, sticky/W1C behavior, firmware ownership, or side effects. Those rules must come from the PCIe spec, AMD register documentation, and surrounding driver code.

## Test Signals

Useful validation signals for this chunk are:

- Compile coverage for NBIO 7.4 include sites: `amdgpu/nbio_v7_4.c`, Arcturus/Aldebaran/SMU 13.0.6 power-management files, and Vega20 PowerPlay code.
- Generated-header consistency checks that every register represented here has the corresponding `cfgBIF_CFG_DEV0_EPF0_VF<n>_0_*` offset in `nbio_7_4_offset.h`.
- Static validation that masks fit the intended PCI config register widths and match their shifts, especially 8-bit identity/class fields, 16-bit command/status/link fields, and 32-bit AER/log/BAR fields.
- Hardware or simulator config-space dumps for VF1 through VF4 decoded with these masks and compared with `lspci -vvxxx`-style PCIe capability output.
- SR-IOV bring-up tests that create VFs, enumerate them, map BARs, issue FLR, and confirm command/status, device/link, MSI/MSI-X, ATS, and ARI fields decode consistently per VF.
- PCIe AER injection or fault-reporting tests that verify correct uncorrectable/correctable status bits, mask behavior, severity handling, first-error pointer, ECRC controls, header logs, and TLP-prefix logs.
- Interrupt tests that exercise MSI and MSI-X enablement, vector masking, pending bits, table/PBA offsets, and per-VF isolation.
- ATS/ARI virtualization tests with IOMMU enabled, checking ATC enablement, STU handling, invalidate support, ARI forwarding/function grouping, and absence of cross-VF leakage.
