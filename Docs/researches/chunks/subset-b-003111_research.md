# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 104919-107381

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,077 `#define` field-layout macros and no functions, structs, enums, variables, allocations, locks, or executable statements.

The range starts at the tail of `BIF_CFG_DEV0_EPF0_3_PCIE_ACS_CNTL`, continues through the remaining EPF0 PCIe enhanced capability and GPU IOV field definitions, covers most of the `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` register field definitions, and ends just after `BIF_CFG_DEV0_EPF2_2_MIN_GRANT` begins in the next `addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` section. Adjacent chunks are required for complete EPF0 ACS context before this range and complete EPF2 config-space context after it.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield companion to AMDGPU's generated NBIO 7.0 register address/default headers. For every register field in this slice it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position for encoding or decoding the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, clear, preserve, or update the field.

This slice models PCIe endpoint-function configuration space and extended capabilities for NBIF device 0 functions, especially EPF0 and EPF1 plus the beginning of EPF2. It gives driver code symbolic field positions for PCIe identity/configuration registers, power management, PCIe link/device capabilities, MSI/MSI-X, virtual channels, AER, BAR sizing/control, dynamic power allocation, secondary PCIe equalization, ACS/ATS/PRI/PASID/TPH/multicast/LTR/ARI/SR-IOV, and AMD vendor-specific GPU IOV controls.

## Important Macro Families

The opening EPF0 tail covers PCIe security, translation, virtualization, and GPU IOV fields. It includes ACS control bits for source validation, translation blocking, peer-to-peer redirection, upstream forwarding, egress control, and direct translated peer-to-peer operation. It then defines ATS capability/control fields, PRI page-request control/status/capacity/allocation, PASID capability/control, TPH requester capability/control, multicast group/window controls, LTR latency capability, ARI capability/control, and SR-IOV capability/control/status/VF BAR/page-size/function-link fields.

The EPF0 GPU IOV VSEC section defines the vendor-specific enhanced capability list/header, SR-IOV shadow state, interrupt enable/status bits for GFX/UVD/VCE command completion, hang recovery, FLR-needed, VM-busy transitions, and HVVM mailbox events. It also defines `SOFT_PF_FLR`, HVVM mailbox dwords with VF index, transmit/receive message data, valid/ack bits, per-VF `TRN_ACK`/`RCV_VALID` bits for VF0 through VF15, PF mailbox status bits, context/current-VF fields, total frame-buffer size, VF frame-buffer offset/size pairs for VF0 through VF15, and full-dword scheduler payload registers for UVD, VCE, and GFX.

The EPF1 address block starts with standard PCI configuration-space fields: vendor/device ID, command bits, status bits, revision/class/subclass/prog-if, cache line, latency, header/BIST, BAR1 through BAR6, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency. It then defines vendor capability and power-management capability/status/control fields.

The EPF1 PCIe capability section covers device and link registers: max payload and read request sizes, relaxed ordering, no-snoop, FLR initiation, error enables/status, link speed/width, ASPM and clock power management, retrain/link-disable controls, link status, Device Capabilities 2, Device Control 2, Link Capabilities/Control/Status 2, and the PCIe slot capability/control/status 2 placeholders.

The EPF1 interrupt and extended capability groups include MSI and MSI-X control/table/PBA fields, generic vendor-specific scratch registers, virtual-channel capabilities and VC0/VC1 resource controls, device serial number dwords, and Advanced Error Reporting status/mask/severity/capability/header-log/TLP-prefix-log fields. AER fields cover DLP, surprise down, poisoned TLP/sequence number, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal error, correctable internal error, header-log overflow, ECRC generation/check enables, and multiple-header-record controls.

The later EPF1 capability groups define BAR enhanced capabilities for BAR1 through BAR6, power budget data selection/data/capability, DPA capability/status/control and eight substate power-allocation fields, secondary PCIe link-control/lane-error/equalization fields for lanes 0 through 15, ACS, ATS, PRI, PASID, TPH, multicast, LTR, ARI, SR-IOV, and the same GPU IOV VSEC/mailbox/frame-buffer/scheduler families seen for EPF0. The chunk ends after EPF2 standard identity/config/header/BAR/subsystem/ROM/capability-pointer/interrupt fields and the `MIN_GRANT` comment.

## APIs, Types, And Functions

There are no callable APIs or C types in this range. The public interface is the generated preprocessor macro namespace. All constants are integer literals, usually with an `L` suffix, intended for C bit manipulation.

Consumers combine these field definitions with companion register address/default headers and AMDGPU access helpers such as SOC15, PCIe config, MMIO, SMN, or indirect register read/write helpers. A typical consumer reads a register, extracts a field with `mask` and `shift`, or does a read/modify/write that clears the mask and inserts `(value << shift) & mask`.

These macros do not encode register addresses, access widths, access permissions, write-one-to-clear behavior, reset values, reserved-bit rules, firmware ownership, synchronization requirements, or required delays. Those properties must come from the hardware register database, sibling generated headers, and call-site-specific driver logic.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU, platform firmware, PCI core, or virtualization code selects a NBIO/PCIe configuration register address from the matching offset/SMN metadata.
2. The caller reads or composes a register value through the relevant access path.
3. The shift/mask constants in this chunk identify the field within the register value.
4. Hardware state machines then apply the change or report status for PCIe link/device control, AER, MSI/MSI-X, virtual-channel negotiation, ACS/ATS/PRI/PASID translation services, SR-IOV VF enumeration, GPU IOV mailbox exchange, or FLR/reset handling.

Several represented flows are asynchronous and require polling, interrupts, or sequencing outside this file: link retraining, FLR initiation, AER status clearing, MSI/MSI-X table setup, VC arbitration table loads and negotiation, DPA substate transitions, lane equalization phases, PRI/ATS/PASID enablement, SR-IOV VF enablement, GPU IOV mailbox valid/ack handshakes, and per-engine virtualization/hang-recovery interrupts.

## State And Persistence Behavior

The header owns no mutable software state and persists nothing. It describes hardware-visible state stored in PCIe configuration space and NBIO vendor-specific extended capability registers.

Represented state includes read-only identity/capability fields, writable command/control bits, sticky or latched status bits, BAR and ROM apertures, interrupt routing state, MSI/MSI-X masks and pending bits, link speed/width/training state, AER masks/severity/header logs, virtual-channel resource state, ACS/ATS/PRI/PASID/TPH controls, SR-IOV VF counts and BARs, and AMD GPU IOV mailbox/frame-buffer/scheduler state. Some fields are standard PCIe capability state exposed to the Linux PCI subsystem; others are AMD-specific PF/VF virtualization controls.

Persistence depends on the reset domain and access type: PCI conventional reset, FLR, hot reset, GPU reset, NBIO reset, platform firmware initialization, suspend/resume restore, SR-IOV enable/disable, and hypervisor or PF driver ownership. The shift/mask file does not indicate which fields are sticky, which are write-one-to-clear, which are read-only mirrors, or which are lost across PF/VF reset.

## Dependencies And Integration Points

This generated chunk must stay synchronized with `nbio_7_0_offset.h`, `nbio_7_0_default.h`, `nbio_7_0_smn.h`, and AMD's source register database. The register names in this file are useful only when paired with matching register offsets and default/access metadata.

Driver integration points include AMDGPU NBIO initialization, PCIe capability discovery, PCI command and BAR setup, MSI/MSI-X routing, AER policy, PCIe link management, runtime power management, FLR/GPU reset flows, SR-IOV PF/VF enablement, VF BAR sizing, GPU IOV frame-buffer partitioning, mailbox-based PF/VF communication, engine scheduling for GFX/UVD/VCE, ATS/PRI/PASID interactions with IOMMU support, ACS isolation, and debug/diagnostic register dumps.

The PCIe-standard fields intersect with the Linux PCI core and generic PCIe services. The AMD-specific GPU IOV VSEC fields are tighter integration points for virtualization stacks because they carry per-VF mailbox acknowledgements, per-VF frame-buffer partitions, and per-engine scheduler dwords. Incorrect ownership assumptions between PF, VF, firmware, and hypervisor code can break isolation or reset recovery.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while targeting the wrong bit, which can corrupt PCIe config-space programming, link state, interrupts, AER masks, SR-IOV layout, or GPU IOV mailbox semantics.
- This chunk begins and ends on logical boundaries split across neighboring chunks. EPF0 ACS control starts before line 104919, and EPF2 `MIN_GRANT` continues after line 107381.
- Several register families reuse similar field names across EPF0, EPF1, and EPF2. Accidentally mixing `EPF0_3`, `EPF1_2`, and `EPF2_2` constants can silently operate on the wrong endpoint-function layout.
- Status, mask, severity, and control registers have nearly identical AER field names. Using a status mask against a mask/severity/control register, or clearing a W1C status field with ordinary read/modify/write assumptions, can lose diagnostics or fail to unmask real faults.
- PCIe link and equalization fields are timing-sensitive. Retrain, link-disable, target speed, lane equalization, ASPM, and clock power-management writes need platform-aware sequencing and timeouts.
- SR-IOV fields affect VF count, function dependency, first VF offset, VF stride, VF device ID, VF BARs, and migration array placement. Bad programming can break VF enumeration or expose resources incorrectly.
- GPU IOV frame-buffer fields split each VF's offset and size. Unit mismatches, overflows, overlap, or stale values after reset can violate VF isolation.
- HVVM mailbox fields require valid/ack handshakes across PF and VF contexts. Reusing stale `VF_INDEX`, failing to clear valid bits, or racing per-VF ack/receive-valid bits can lose messages or attribute them to the wrong VF.
- Full-width `0xFFFFFFFFL` masks appear for BARs, serial-number dwords, message addresses, scratch registers, scheduler dwords, and frame-buffer related payloads. Full-width field masks do not imply that arbitrary writes are safe.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time coverage catches missing or renamed generated symbols referenced by consumers.
- Run generated-header consistency checks for this slice: every field should have matching `__SHIFT` and `_MASK` macros, masks should match their declared shift/width, and repeated VF/lane/BAR/scheduler patterns should be monotonic and complete.
- Cross-check each register family in this chunk against `nbio_7_0_offset.h` and `nbio_7_0_default.h` so field definitions map to known register addresses and reset/default values.
- On NBIO 7.0 hardware, validate PCI enumeration, BAR sizing, MSI/MSI-X setup, AER reporting/clearing, link speed/width reporting, link retrain, suspend/resume, FLR, GPU reset, and runtime power transitions.
- For SR-IOV capable configurations, enable/disable VFs, verify VF counts/strides/device IDs/BARs, test PF and VF FLR, and confirm VF resource isolation across reset and resume.
- For GPU IOV paths, exercise PF/VF mailbox transmit/receive/ack transitions, per-engine command-complete and hang/FLR-needed interrupts, frame-buffer partition programming for VF0 through VF15, and scheduler dword programming for GFX/UVD/VCE.
- Validate ACS/ATS/PRI/PASID interactions with the IOMMU and PCI core: translation enablement, page-request status/error handling, PASID width/permission bits, and peer-to-peer isolation policy.
