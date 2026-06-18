# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 133633-136075

## Scope And Purpose

This chunk is a generated AMD NBIO 7.2.0 register shift/mask header segment. It contains preprocessor constants only: every hardware field is represented as a `__SHIFT` value and a corresponding `MASK` value. There are no functions, C types, data structures, or executable control-flow branches in this slice.

The covered range maps two related hardware surfaces:

- The tail of the EPF0 GPU IOV vendor-specific PCIe capability block, including SR-IOV shadow state, GPU/VCN/VCE/GFX virtualization interrupts, PF FLR control, HV/VM mailbox handshakes, frame-buffer partitioning for VFs, P2P-over-XGMI enablement, and per-engine scheduling descriptor words.
- The start and most of the EPF1 PCI configuration space and PCIe capability chain, including standard PCI IDs/BARs, power management, PCIe device/link controls, MSI/MSI-X, vendor-specific and virtual-channel capabilities, AER, resizable BARs, power budgeting, DPA, link equalization, ACS, ATS, PRI, PASID, multicast, LTR, ARI, SR-IOV, TPH, data-link feature, 16 GT/s PHY controls, lane margining, and VF resizable BAR controls.

The file's purpose is to provide exact bit positions for AMDGPU NBIO register access helpers. Consumers combine these constants with register offsets from `nbio_7_2_0_offset.h` and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

## Important APIs, Types, And Constants

This chunk defines hardware-field constants, not callable APIs. The important "interfaces" are the macro naming contracts:

- `BIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV*` describes EPF0 GPU IOV vendor-specific registers. Key fields include `VSEC_ID`, `VSEC_REV`, `VSEC_LENGTH`, `VF_EN`, `VF_NUM`, engine interrupt enable/status bits, `SOFT_PF_FLR`, HVVM mailbox fields, context sizing, total/consumed FB accounting, scheduler offsets, XGMI P2P enable bits, VF frame-buffer size/offset fields, and scheduler DWORD fields for UVD/VCN, VCE, GFX, and UVD1.
- `BIF_CFG_DEV0_EPF1_1_*` describes the EPF1 config-space view. The prefix covers ordinary PCI config registers (`VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, class code, BARs, ROM BAR, cap pointer, interrupt pin/line) and the PCIe capability list.
- `*_CAP_LIST`, `*_ENH_CAP_LIST`, `*_HDR`, and `*_NEXT_PTR` fields encode PCI/PCIe capability chain metadata. These are used to expose or decode the device's advertised PCIe capabilities.
- `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, and their version-2 equivalents define payload sizing, read request sizing, FLR initiation, error reporting enables, link speed/width, ASPM/link training, DRS, LTR, atomic operations, 10-bit tags, and OBFF-related controls.
- `MSI_*` and `MSIX_*` blocks define MSI/MSI-X enablement, table/PBA location, message address/data, masking, pending state, 64-bit variants, and extended data fields.
- `PCIE_ADV_ERR_*`, `PCIE_HDR_LOG*`, and `PCIE_TLP_PREFIX_LOG*` define AER status/mask/severity, ECRC capability/control, error source IDs, first-error pointer, and captured header/TLP logs.
- `PCIE_BAR*_CAP` and `PCIE_BAR*_CNTL` define PF resizable BAR support and selected BAR size. The tail also defines `PCIE_VF_RESIZE_BAR*_CAP` and `PCIE_VF_RESIZE_BAR*_CNTL` for VF BAR sizing.
- `PCIE_ACS_*`, `PCIE_ATS_*`, `PCIE_PAGE_REQ_*`, and `PCIE_PASID_*` expose I/O virtualization controls: ACS redirection/translation blocking, ATS enablement and invalidation depth, PRI control/status/capacity/allocation, and PASID enable/width/permission support.
- `PCIE_SRIOV_*` defines SR-IOV capability, control/status, VF counts, VF offset/stride/device ID, page size, VF BAR bases, and migration state-array offset.
- `PCIE_PHY_16GT_*`, `LINK_*_16GT`, per-lane 16 GT/s equalization controls, and per-lane margining control/status fields define high-speed link training and diagnostic controls for lanes 0-15.

All definitions are compile-time constants. Their correctness depends on AMD's generated register database matching the hardware programming guide for NBIO 7.2.0.

## Control Flow

There is no runtime control flow in this chunk. The effective flow is generated-data lookup:

1. A driver source identifies a register by an offset macro from the companion offset header.
2. It reads or constructs a register value.
3. It uses these `__SHIFT` and `MASK` macros, usually through local AMDGPU field helpers, to isolate, test, set, or clear a field.
4. It writes the resulting value back to the PCIe/NBIO register aperture when changing hardware state.

The only direct C include found for this ASIC-generation mask header in the AMDGPU tree is `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`. That file handles NBIO revision ID, memory-controller access, doorbell ranges, interrupt control, clock/light-sleep gating, HDP flush register selection, and PCIe register access. This particular chunk mostly covers PCI config-space and virtualization capability fields that may also be used indirectly through generic PCI enumeration, firmware, hypervisor, SR-IOV setup, or future NBIO code paths.

## State And Persistence Behavior

The header itself has no state and persists nothing. The fields it describes are hardware-backed state:

- SR-IOV and GPU IOV fields persist in NBIO/PCI config registers until reset, FLR, firmware reinitialization, or driver writes change them. `VF_EN`, `VF_NUM`, VF BAR sizing, VF frame-buffer partitioning, and VF mailbox state influence virtual-function enumeration and behavior.
- Interrupt enable/status bits are live hardware latches or masks for GPU virtualization events such as command completion, hangs requiring self recovery or FLR, VM-busy transitions, and HVVM mailbox traffic.
- `SOFT_PF_FLR` and `DEVICE_CNTL__INITIATE_FLR` are reset-triggering controls. Misuse can disrupt the PF and all dependent VFs.
- Mailbox fields encode transient PF/VF or hypervisor/VM message handshakes. `TRN_ACK` and `RCV_VALID` are exposed per VF, with one DWORD covering VFs 0-15 and another covering VFs 16-30 plus PF status.
- FB partition fields give each VF a size and offset, and total consumed/available accounting describes the partitioning state exposed to virtualization management.
- Link, error, MSI/MSI-X, AER, ACS/ATS/PRI/PASID, SR-IOV, equalization, margining, power, and BAR controls are PCIe-visible state that can also be observed or modified by PCI core code, firmware, platform firmware, hypervisors, or privileged management tooling.

Because this is a shared hardware definition file, an incorrect mask does not corrupt software memory directly; instead it causes wrong register bits to be read or written. That can silently misreport capability state, program the wrong PCIe feature, or destabilize the bus.

## Dependencies And Integration Points

This chunk depends on the surrounding AMDGPU register-generation scheme:

- `nbio_7_2_0_offset.h` supplies the register offsets. This `*_sh_mask.h` file supplies the field layout for those offsets.
- `amdgpu/nbio_v7_2.c` includes this header and uses the broader file with SOC15 and PCIe-port register helpers.
- AMDGPU bitfield helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` rely on the macro stem matching the register name and field name exactly.
- Linux PCI core concepts are mirrored by many fields: standard config-space headers, PCIe capabilities, MSI/MSI-X, AER, ACS, ATS, PRI, PASID, SR-IOV, ARI, LTR, TPH, DPA, and resizable BARs.
- GPU virtualization and SR-IOV management code depends on the GPUIOV vendor-specific capability layout for mailbox signaling, per-VF FB assignment, engine scheduling descriptors, P2P-over-XGMI toggles, and VF interrupt reporting.
- KFD/ROCm integration is indirect: NBIO register programming controls doorbells, interrupts, memory access, and virtualization boundaries that compute queues and VM contexts rely on.

The constants are ASIC-specific. They should not be reused for unrelated NBIO, NBIF, or PCIe generations unless those headers intentionally define the same layout.

## Risks And Edge Cases

- Generated-header drift is the main risk. If a field shift or mask no longer matches silicon, every consumer compiles cleanly but reads or writes the wrong bits.
- PCIe capability-chain fields (`CAP_ID`, `CAP_VER`, `NEXT_PTR`, `CAP_PTR`) are small but high impact. Wrong masks can break capability discovery or cause software to walk an invalid capability chain.
- SR-IOV fields are security and isolation sensitive. Incorrect VF count, VF BAR, ACS/ATS/PRI/PASID, mailbox, or FB partition fields can expose resources across VFs, hide VFs from the host, or make a hypervisor's GPU-management state inconsistent with hardware.
- Reset and FLR fields can be destructive if programmed accidentally. `SOFT_PF_FLR` and `INITIATE_FLR` must only be changed by code that owns the reset sequence.
- Interrupt enable/status definitions must match the hardware latch semantics. Confusing enable and status bits, or using the wrong engine bit group, can mask virtualization events or leave status uncleared.
- Per-lane equalization/margining definitions are repetitive for lanes 0-15. Copy-generation errors are easy to miss and can affect only a subset of lanes, making failures platform- or link-width-specific.
- The chunk mixes standard PCIe-defined fields with AMD vendor-specific GPUIOV fields. Reviewers should avoid assuming standard Linux PCI definitions fully cover the vendor-specific portions.
- Many masks use `L` suffixed constants and some cover bit 31. Consumers should keep values in unsigned 32-bit temporaries to avoid sign-extension or integer-promotion surprises.

## Test Signals

There are no unit tests for this header alone. Useful validation signals are integration- and hardware-facing:

- AMDGPU builds without missing macro errors after regenerating or editing the header.
- NBIO v7.2 devices boot with `amdgpu` loaded, the driver reads the expected revision ID and memory size, and PCIe/NBIO register access paths do not fault.
- `lspci -vv` and kernel PCI logs show coherent PCIe capabilities for EPF1: link speed/width, MSI/MSI-X, AER, ACS, ATS, PRI, PASID, SR-IOV, resizable BAR, and related capability chain pointers.
- SR-IOV enablement creates the expected VF count and VF BAR layout, and VFs can bind/unbind without PF FLR or mailbox failures.
- GPU virtualization telemetry reports command-complete, hang/recovery, VM-busy, and HVVM mailbox events with correct routing and no interrupt storms.
- VF frame-buffer partitions match management expectations: total FB consumed/available is coherent, each VF size/offset is non-overlapping, and P2P-over-XGMI policy matches platform configuration.
- PCIe error-injection or AER observation, where available, records correct uncorrectable/correctable status, masks, severities, and header logs.
- Link training diagnostics on high-speed links show correct per-lane equalization and margining status for lanes 0-15, especially on x16 links where copy/paste mistakes across lane fields would be visible.

## Chunk Summary

This chunk is a hardware definition surface rather than behavior-bearing code. Its substantive value is the exact register contract for NBIO 7.2.0 EPF0 GPU IOV and EPF1 PCIe capability/configuration fields. Any code change involving these macros should be reviewed as a silicon-interface change: the source compiles regardless of whether a mask is semantically correct, so validation must come from ASIC documentation, generated-register provenance, PCIe enumeration output, SR-IOV behavior, and hardware integration tests.
