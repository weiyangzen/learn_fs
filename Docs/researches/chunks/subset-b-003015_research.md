# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 24572-27020

## Scope

This chunk is a 2,449-line slice of AMDGPU's generated NBIO 6.1 shift/mask header. It contains 2,085 preprocessor `#define` constants and register-family comments only. There are no C functions, structs, enums, variables, allocations, locks, loops, or executable statements.

The range starts inside the `BIF_CFG_DEV0_EPF0_1_PCIE_SRIOV_CONTROL` mask definitions, covers the tail of the endpoint function 0 SR-IOV and AMD GPUIOV vendor-specific capability layout, then switches to the `nbio_nbif_bif_cfg_dev0_epf1_bifcfgdecp` address block for a full endpoint function 1 PCI/PCIe configuration-space template. The final section starts the `nbio_nbif_bif_cfg_dev0_epf0_vf0_bifcfgdecp` address block for virtual function 0 and ends inside `BIF_CFG_DEV0_EPF0_VF0_1_LINK_CAP2`.

Although this repository path is under a `ceph-client` source mirror, this file is AMD DRM/AMDGPU hardware metadata. This chunk has no direct distributed-filesystem behavior.

## Purpose

`nbio_6_1_sh_mask.h` publishes generated bitfield layouts for NBIO 6.1 registers and PCI configuration-space words. For each register field it supplies:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position of the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to extract, preserve, or update the field.

Runtime AMDGPU code pairs this file with `nbio_6_1_offset.h`, `nbio_6_1_default.h`, and `nbio_6_1_smn.h`. Consumers pass these constants to helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `WREG32_FIELD15`.

This chunk's specific purpose is to describe the software-visible bit layout for NBIO PCIe endpoint virtualization. It covers SR-IOV capability fields, AMD GPUIOV mailbox/interrupt/framebuffer/scheduler fields, a complete PF-like EPF1 PCIe config image, and the beginning of the VF0 PCIe config image.

## Important Macro Families

The opening EPF0 tail covers SR-IOV resource and capability fields:

- `BIF_CFG_DEV0_EPF0_1_PCIE_SRIOV_CONTROL` masks for VF enablement, migration enablement, migration interrupt enablement, VF memory-space enable, and ARI-capable hierarchy.
- SR-IOV status and sizing registers: migration status, initial/total/current VF counts, function dependency link, first VF offset, VF stride, VF device ID, supported and selected page sizes, six VF BAR base-address fields, and migration-state-array offset/BIF selector.

The EPF0 AMD GPUIOV vendor-specific capability section defines:

- VSEC list/header fields: capability ID, version, next-pointer, VSEC ID, revision, and VSEC length.
- SR-IOV shadow state: `VF_EN` and `VF_NUM`.
- GPUIOV interrupt enable/status bits for GFX, UVD, and VCE command completion, self-recovered hangs, hangs needing FLR, VM-busy transitions, and hypervisor/VM mailbox transmit-ack and receive-valid events.
- Reset control through `SOFT_PF_FLR`.
- Hypervisor/VM mailbox fields in `HVVM_MBOX_DW0` and per-VF ack/valid bits in `HVVM_MBOX_DW1`, covering VF0 through VF15.
- Context, total framebuffer, offset, and per-VF framebuffer assignment fields for VF0 through VF15.
- Scheduler dwords for UVD, VCE, and GFX, each exposing raw 32-bit scheduler fields across `*_SCH_DW0` through `*_SCH_DW8`.

The `BIF_CFG_DEV0_EPF1_1_*` address block is a full endpoint function 1 PCIe configuration template:

- Conventional PCI header fields: vendor/device ID, command, status, revision, programming interface, subclass, base class, cache line, latency, header type, BIST, BAR1-BAR6, adapter/subsystem ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, and vendor capability data.
- PCI command/status bits: I/O and memory decode, bus mastering, special cycles, memory-write-invalidate, palette snoop, parity response, SERR, fast back-to-back, interrupt disable, immediate readiness, interrupt status, capability-list presence, DEVSEL timing, target/master aborts, system error, and parity error detection.
- Power Management capability and status/control fields: PME support/status/enable, D-state support, auxiliary current, data select/scale, bus-power control, and current power state.
- PCIe base capability fields: capability list header, PCIe version, device/port type, slot implementation, interrupt message number, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2, and slot capability/control/status 2 placeholders.
- MSI and MSI-X fields: message control, multi-message support/enable, 64-bit support, per-vector masking, message address/data, mask and pending registers, MSI-X table size/function mask/enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific, virtual channel, device serial number, Advanced Error Reporting, enhanced BAR, power budgeting, Dynamic Power Allocation, and Secondary PCIe extended capability fields.
- AER status/mask/severity fields for data link protocol errors, surprise down, poisoned TLP, flow control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, posted/non-posted request discard, and corrected error classes. It also defines AER control/log fields, header logs, and TLP prefix logs.
- Per-lane 8 GT/s equalization controls for lanes 0 through 15, including downstream/upstream TX presets and RX preset hints.
- Isolation and I/O virtualization capabilities: ACS capability/control, ATS capability/control, Page Request Interface control/status/capacity/allocation, PASID capability/control, TPH requester capability/control, multicast capability/control/address/receive/block masks, LTR capability, ARI capability/control, and SR-IOV capability/control/status/resource fields.
- A second EPF1 AMD GPUIOV vendor-specific section mirroring the EPF0 GPUIOV field layout: SR-IOV shadow, interrupts, soft PF FLR, HVVM mailbox, per-VF framebuffer assignment, and UVD/VCE/GFX scheduler dwords.

The final `BIF_CFG_DEV0_EPF0_VF0_1_*` section begins the virtual function 0 PCI configuration image:

- VF0 conventional PCI header fields: vendor/device ID, command/status, revision/class, cache/latency/header/BIST, BAR1-BAR6, adapter ID, ROM BAR, capability pointer, interrupt line/pin, and PCIe capability list header.
- VF0 PCIe capability fields through the chunk end: PCIe capability metadata, device capability/control/status, link capability/control/status, device capability 2, device control 2, device status 2, and the beginning of link capability 2.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace.

The constants are untyped preprocessor integer literals, mostly with an `L` suffix. They describe only bit positions and masks. They do not encode access width, reset value, read/write permissions, sticky status behavior, write-one-to-clear semantics, privilege constraints, or hardware sequencing. Those rules live in the PCIe specification, AMD hardware specifications, firmware policy, and the consuming driver code.

Direct in-tree include users of `nbio_6_1_sh_mask.h` include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which integrates NBIO 6.1 shift/mask macros with NBIO register access, memory-size reads, doorbell aperture programming, HDP flush remapping, interrupt controls, LTR/ASPM setup, and clock/power handling.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, which includes this header with NBIO offsets for AI SR-IOV mailbox handling. The specific mailbox code uses neighboring `BIF_BX_PF0_MAILBOX_*` fields, while this chunk documents related GPUIOV/HVVM mailbox and virtualization config-space fields.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`, which aggregate ASIC register headers for power-management builds.

## Control Flow

This header has no local control flow. Effective runtime flow is external:

1. The driver selects an NBIO 6.1 register or PCI configuration-space offset from a companion offset/SMN header.
2. It reads a hardware value, extracts fields using the `__SHIFT` and `_MASK` constants, or composes a write value with field helpers.
3. The result configures PCIe endpoint behavior, services virtualization/mailbox events, exposes VF resources, handles interrupts, reports errors, or drives diagnostics.

Likely flows represented by this chunk include PCI enumeration of EPF1 and VF0, BAR sizing and decode, command-bit programming, MSI/MSI-X setup, PCIe link capability/status reporting, AER collection and masking, ATS/PASID/PRI setup, ACS/ARI routing policy, SR-IOV VF discovery, GPUIOV host/VF coordination, hypervisor/VM mailbox signaling, VF framebuffer partition exposure, media/graphics scheduler state exchange, and PF/VF reset or FLR coordination.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It names hardware-visible state in NBIO PCIe configuration registers and AMD vendor-specific virtualization registers. Persistence is determined by ASIC reset domains, PCI conventional reset, function-level reset, hot reset, D-state transitions, suspend/resume save-restore, firmware initialization, hypervisor policy, and explicit driver writes.

Represented state includes PCI identity and class fields, resource decode and BAR state, interrupt routing and MSI/MSI-X state, PCIe device/link controls, link/device status, AER sticky status/masks/severity/logs, power-management state, virtual-channel controls, per-lane equalization controls, ACS/ATS/PRI/PASID/TPH/multicast/LTR/ARI/SR-IOV capability state, GPUIOV interrupt enables/status, mailbox valid/ack/data fields, per-VF framebuffer allocation, and scheduler dwords for GFX/UVD/VCE.

Several fields are stateful protocol or command fields rather than passive storage. `BUS_MASTER_EN` and `MEM_ACCESS_EN` gate DMA/MMIO access; `INITIATE_FLR` and `SOFT_PF_FLR` start reset behavior; MSI/MSI-X enables and masks affect interrupt delivery; GPUIOV interrupt status bits may be sticky or clear-on-write depending on hardware semantics; mailbox valid/ack bits implement handshakes; AER status/log fields preserve diagnostic evidence; ACS/ATS/PASID/ARI/SR-IOV controls affect isolation and routing; and VF framebuffer/scheduler fields expose partitioning state to host, guest, or firmware code.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 6.1 register database and must stay aligned with sibling generated files:

- `nbio_6_1_offset.h` supplies matching register/config offsets.
- `nbio_6_1_default.h` supplies reset/default values for the same generated names.
- `nbio_6_1_smn.h` supplies SMN-addressed aliases used by NBIO access helpers.
- Shared AMDGPU register helper macros consume the shift/mask constants for extraction and update.

Broader integration points include AMDGPU NBIO initialization, PCI probing, Vega10/Vega12 power-management inclusion, SR-IOV VF/PF detection, virtualization full-access handshakes, GPUIOV scheduling and framebuffer partition metadata, MSI/MSI-X interrupt delivery, PCIe AER and RAS diagnostics, IOMMU-facing ATS/PASID/PRI behavior, ACS/ARI routing/isolation, PCIe link management, GPU reset and FLR handling, and suspend/resume restore paths.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing software to read, preserve, clear, or set the wrong hardware bit.
- The chunk starts mid-register and ends mid-family. Earlier lines are needed for the full EPF0 SR-IOV control definition, and later lines are needed for the rest of VF0 link capability 2 and subsequent VF0 capability fields.
- EPF0 and EPF1 GPUIOV blocks are intentionally similar. A suffix mismatch between EPF0/EPF1, VF index, scheduler block, or mailbox bit can silently target the wrong function or guest.
- SR-IOV, ACS, ATS, PRI, PASID, ARI, multicast, and GPUIOV fields are isolation-sensitive. Wrong masks can expose incorrect VF BARs, break IOMMU translation behavior, misroute requests, or weaken PF/VF separation.
- Mailbox valid/ack and interrupt status fields are protocol fields. Misinterpreting status as ordinary storage can lose host/guest notifications or deadlock a PF/VF handshake.
- VF framebuffer fields affect partition accounting. Incorrect masks can report the wrong memory slice to a guest or firmware component.
- AER fields are diagnostic and sometimes sticky or write-one-to-clear. Incorrect clearing or masking can hide real PCIe errors or produce persistent interrupt storms.
- PCI command, BAR, MSI/MSI-X, and FLR fields are high-impact control fields. Bad bit definitions can break enumeration, DMA enablement, interrupt routing, reset sequencing, or recovery.
- Repeated lane and VF definitions invite generator/copy drift. Per-lane or per-VF consistency checks are important because compile tests often cannot detect a wrong numeric bit position.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU with NBIO 6.1, Vega10, Vega12, and AI SR-IOV support enabled. Syntax errors, missing macros, or renamed generated symbols should fail direct include users.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database: offset-to-field pairing, shift/mask width checks, non-overlap checks within registers, EPF0/EPF1 mirror consistency, VF0 field continuity, per-VF repetition, and capability-list continuity.
- Boot affected ASICs and verify PCI enumeration for PF/EPF and VF paths: vendor/device/class values, capability traversal, BAR sizing, command-bit transitions, link speed/width reporting, and MSI/MSI-X setup.
- Exercise SR-IOV where available: VF enumeration, VF BAR exposure, VF stride/offset/count/page-size reporting, ARI routing, ACS isolation, ATS/PASID/PRI enablement, VF FLR behavior, and guest reset/reload.
- Validate GPUIOV mailbox and interrupt behavior under host/guest handshakes: transmit ack, receive valid, interrupt enable/status, timeout handling, and absence of stale valid/ack bits after reset.
- Check framebuffer partition reporting for VF0-VF15 and scheduler dword read/write paths for GFX, UVD, and VCE virtualization flows.
- Use PCIe AER injection or observed fault paths to confirm status/mask/severity/header-log/TLP-prefix decoding and clearing behavior.
- Run suspend/resume, D3hot-to-D0, FLR, and GPU reset tests to catch persistence or save-restore mistakes in PCIe, SR-IOV, mailbox, and interrupt state.

## Chunk-Specific Notes For Merge

This is only the lines 24572-27020 chunk of `nbio_6_1_sh_mask.h`. The final per-file report should merge this with adjacent chunks before claiming complete coverage of `BIF_CFG_DEV0_EPF0_1_PCIE_SRIOV_CONTROL` or `BIF_CFG_DEV0_EPF0_VF0_1_LINK_CAP2`. Preserve that this slice covers EPF0 SR-IOV/GPUIOV tail fields, the full EPF1 PCIe/SR-IOV/GPUIOV configuration block, and the beginning of the EPF0 VF0 configuration block.
