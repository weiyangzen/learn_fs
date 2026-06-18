# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 7580-10029

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains preprocessor constants only: no C functions, structs, enums, storage, locking, allocation, or executable statements are defined in this line range.

The range starts in the tail of the `RCC_DEV0_EPF0_VF15_GFXMSIX_*` MSI-X table definitions, then covers a large `PSWUSCFG0_0_*` PCIe switch/upstream configuration block, and finally begins the `BIF_CFG_DEV0_RC0_*` root-complex configuration block through `PCIE_VC1_RESOURCE_STATUS`. Adjacent chunks are needed for the complete file-wide picture because the first register family starts before line 7580 and the final root-complex VC1 status masks continue after line 10029.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of the generated NBIO 4.3.0 hardware interface. Each register field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, or preserve the field.

The companion `nbio_4_3_0_offset.h` supplies the register/config-space offsets, while runtime AMDGPU code consumes this file through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and SOC15 address calculation. These macros are generated hardware metadata; correctness depends on the masks matching the ASIC register database and matching offset/default headers.

This specific chunk documents three related hardware surfaces:

- VF15 graphics MSI-X vector table fields for SR-IOV/virtualized interrupt delivery.
- `PSWUSCFG0_0`, a PCIe upstream/switch configuration image with conventional PCI bridge fields, PCIe capability fields, AER, ACS, multicast, LTR, ARI, data-link feature, 16 GT/s, margining, and 32 GT/s capability fields.
- `BIF_CFG_DEV0_RC0`, the beginning of a root-complex PCI configuration image, including bridge/resource windows, power-management, PCIe link/device/slot controls, MSI, subsystem ID, vendor-specific capability, and virtual-channel fields.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware register metadata and has no direct distributed-filesystem behavior.

## Important Macro Families

The `RCC_DEV0_EPF0_VF15_GFXMSIX_*` tail defines the remaining VF15 graphics MSI-X table entries:

- `VECT1`, `VECT2`, and `VECT3` message address low/high fields, message data fields, and per-vector `MASK_BIT`.
- `RCC_DEV0_EPF0_VF15_GFXMSIX_PBA` pending-bit fields for the first two pending bits.
- These fields pair with offset definitions such as `regRCC_DEV0_EPF0_VF15_GFXMSIX_VECT*_...` in generated offset headers and describe the hardware layout that a hypervisor, PF path, or resume path may need to preserve or reprogram.

The `PSWUSCFG0_0_*` block is a complete PCI/PCIe configuration-space bit map for the `nbio_pcie0_pswuscfg0_cfgdecp` address block:

- Conventional PCI bridge header fields: vendor/device ID, command/status, revision/class bytes, cache-line/latency/header/BIST, BAR-like base addresses, primary/secondary/subordinate bus numbers, I/O and memory windows, prefetchable memory windows, ROM BAR, capability pointer, interrupt line/pin, adapter/subsystem IDs, and vendor capability metadata.
- Command/status and bridge-status fields: I/O/memory access, bus mastering, parity response, SERR, interrupt disable, immediate readiness, capability-list presence, DEVSEL timing, target/master abort, system error, and parity error reporting.
- Power-management capability fields: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` expose PM version, PME support, D-state control, PME enable/status, data scale/select, B2/B3 support, and related bridge power-management controls.
- PCIe base capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` cover PCIe version/device type, error-reporting enables, relaxed ordering, max payload/read request size, extended tag, no-snoop, FLR initiation, link speed/width, ASPM/PM control, retraining, common clock, bandwidth interrupts, and data-link active/training status.
- PCIe capability 2 fields: `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover completion-timeout controls, ARI forwarding, atomic-op routing/completion, ID-based ordering, LTR enable, emergency power reduction, ten-bit tags, OBFF, end-to-end TLP prefix support, target link speed, compliance mode, de-emphasis, crosslink, DRS, and 8 GT/s equalization status.
- MSI fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address high/low, and 32-bit/64-bit message-data fields define MSI enablement, vector count, 64-bit capability, extended message data capability, and message payload layout.
- Subsystem and VSEC fields: `SSID_CAP_LIST`, `SSID_CAP`, `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, and two scratch payload registers define subsystem identity and vendor-specific extended-capability metadata.
- Virtual-channel fields: `PCIE_VC_ENH_CAP_LIST`, port VC capabilities/control/status, and VC0/VC1 resource capabilities/control/status define VC counts, arbitration table controls, traffic-class mappings, VC IDs, enable bits, and negotiation status.
- AER fields: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four header-log registers, and four TLP-prefix-log registers cover PCIe error classes and diagnostics.
- Secondary PCIe enhanced capability fields: `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, and `PCIE_LANE_ERROR_STATUS` plus lane 0-15 equalization controls expose link-equalization policy and lane error reporting.
- ACS fields: `PCIE_ACS_CAP` and `PCIE_ACS_CNTL` cover source validation, translation blocking, peer-to-peer redirection, upstream forwarding, egress control, direct-translated peer-to-peer, I/O request blocking, memory target access controls, and unclaimed-request redirect behavior.
- Multicast, LTR, ARI, and data-link feature fields: the `PCIE_MC_*`, `PCIE_LTR_*`, `PCIE_ARI_*`, and `DATA_LINK_FEATURE_*` groups describe multicast groups/windows, latency tolerance reporting limits, ARI capability/control, and data-link feature exchange.
- 16 GT/s, margining, and 32 GT/s fields: `PCIE_PHY_16GT_*`, per-lane 16 GT/s equalization presets, per-lane margining control/status pairs, `PCIE_PHY_32GT_*`, 32 GT/s link capability/control/status, and per-lane 32 GT/s equalization presets represent high-speed PCIe link training, diagnostics, and margining surfaces.

The `BIF_CFG_DEV0_RC0_*` block begins the `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` address block:

- The initial fields mirror a PCI-to-PCI bridge/root-port configuration image: vendor/device ID, command/status, revision/class/header/BIST, BAR-like base addresses, bus-number/latency register, I/O/memory/prefetchable windows, ROM BAR, capability pointer, interrupt line/pin, and PM capability registers.
- PCIe capability fields in this block include device/link capability, control, and status, plus root-port slot capability/control/status. Slot fields cover attention button/indicator, power controller/indicator, MRL sensor, electromechanical interlock, hot-plug, physical slot number, software-controlled attention/power controls, interrupt enables, and hot-plug status bits.
- The block continues into device/link capability 2, slot capability/control/status 2, MSI configuration including extended message-data variants, subsystem ID, vendor-specific capability, and VC capability/control/resource fields.
- The final line in this chunk is inside `BIF_CFG_DEV0_RC0_PCIE_VC1_RESOURCE_STATUS`, so the merge lane should treat the VC1 status register as chunk-split.

## APIs, Types, And Functions

There are no callable APIs, C types, or local functions in this chunk. The macro namespace is the public interface. Consumers combine these constants with the companion offset macros and generic AMDGPU register helpers.

Important caller-side APIs and integration types observed in the tree include:

- `nbio_v4_3.c`, which includes `nbio/nbio_4_3_0_offset.h` and `nbio/nbio_4_3_0_sh_mask.h` and registers `nbio_v4_3_funcs` / `nbio_v4_3_sriov_funcs` as `struct amdgpu_nbio_funcs` implementations.
- `struct amdgpu_nbio_funcs` in `amdgpu_nbio.h`, which gives higher-level AMDGPU code function pointers for NBIO operations such as PCIe index/data offsets, revision ID, memory controller access, doorbell ranges, interrupt handling, clock gating, register remap, ROM offset, and ASPM programming.
- SMU13 power-management files `smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`, which include the same generated NBIO 4.3.0 headers for power and link-management register definitions.

The macros are untyped integer constants and do not encode read-only, write-one-to-clear, side-effect, reset-domain, or privilege information. Callers must know the register semantics from the hardware block and PCIe specification context.

## Control Flow

This header has no local control flow. Runtime control flow is external:

1. AMDGPU or firmware-facing code selects a register/config-space offset from `nbio_4_3_0_offset.h`.
2. The code reads, composes, masks, extracts, or writes a value using these `__SHIFT` and `_MASK` constants.
3. Hardware interprets the resulting register accesses as PCIe configuration, interrupt-routing, error-reporting, link-management, virtualization, or power-management operations.

Representative flows tied to this chunk include:

- MSI-X programming or restoration for SR-IOV virtual functions. `amdgpu_device.c` notes that QEMU programming of a VF `GFXMSIX_VECT0_ADDR_LO` register can be blocked by nBIF protection during VM resume until exclusive access is restored; the driver calls `amdgpu_restore_msix()` to force reprogramming. The VF15 MSI-X masks in this chunk belong to the same generated MSI-X table surface.
- PCIe ASPM/LTR setup in `nbio_v4_3_program_aspm()` and `nbio_v4_3_program_ltr()`. Those routines read/modify/write NBIO and PCIe config fields, including `DEVICE_CNTL2` LTR enable in the endpoint function block. The `PSWUSCFG0_0_*` and `BIF_CFG_DEV0_RC0_*` link/LTR fields in this chunk represent adjacent switch/root-complex control and status surfaces that must stay synchronized with platform PCIe policy.
- PCIe link diagnostics and training. Link status, 8 GT/s equalization, 16 GT/s equalization, margining, and 32 GT/s status fields are hardware-updated and can be used by debug, firmware, or platform validation paths to determine whether the negotiated width/speed and equalization state are healthy.
- PCIe error handling. AER status/mask/severity/header-log/prefix-log fields expose sticky diagnostic state that software may read, mask, or clear according to PCIe AER rules.

## State And Persistence Behavior

The header itself stores no state. It names hardware-visible state in NBIO PCI configuration registers, MSI-X tables, PCIe link controls/status registers, capability registers, and diagnostic registers.

State represented in this chunk includes:

- Static or strap-derived identity/capability state: vendor/device ID, revision/class codes, capability-chain IDs/versions/next pointers, supported link speeds, supported error/ACS/ARI/LTR/VC features, slot capabilities, and subsystem IDs.
- Host/programmed state: PCI command bits, bridge bus/resource windows, ROM enable/base, MSI enable/address/data, MSI-X per-vector mask bits, device/link controls, completion-timeout policy, LTR enable, ARI/ACS controls, multicast controls, VC arbitration/resource enables, and slot controls.
- Hardware-updated state: link training/current speed/current width, data-link active, equalization completion/phase status, DRS/crosslink/downstream component presence, slot status, AER status/logs, MSI-X pending bits, VC negotiation pending, margining status, and parity mismatch status.

Persistence is governed by GPU/NBIO reset domains, PCI configuration save/restore, firmware initialization, platform ASPM policy, SR-IOV PF/VF management, hypervisor accesses, FLR, suspend/resume, and explicit AMDGPU register writes. Some fields are sticky diagnostics or action bits, not ordinary storage. Examples include AER status bits and logs, MSI-X pending bits, `INITIATE_FLR`, link retrain/disable controls, slot power/attention controls, VC load-arbitration bits, and margining command/status fields.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 register header set:

- `nbio_4_3_0_offset.h` provides the matching `reg...` offsets for the same register names.
- Other generated NBIO headers provide defaults and adjacent masks outside this chunk.
- SOC15/NBIO register helpers in AMDGPU provide access paths and field helpers that consume the generated masks.

Integration points in this tree include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, the main NBIO 4.3 implementation that includes this header and programs related NBIO registers for doorbells, interrupt handling, HDP remap, clock gating, ROM offset, ASPM, and LTR.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_device.c`, where virtualization resume explicitly restores MSI-X after exclusive access is regained, because VF MSI-X table programming can be blocked by NBIF protection.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`, which include the NBIO 4.3.0 generated headers alongside SMU and MP register headers for SMU13 power/link-management code.
- Linux PCIe infrastructure and platform firmware indirectly integrate with these fields through enumeration, bridge window assignment, ASPM/LTR policy, AER handling, MSI/MSI-X setup, hot-plug/slot state, and SR-IOV virtualization.

## Risks And Edge Cases

- Generated bitfield drift is high impact. A wrong shift or mask can compile cleanly while causing software to touch the wrong PCIe control bit.
- Chunk boundaries are artificial. The VF15 MSI-X vector set starts before this range, and the root-complex VC1 status register continues after it.
- Many fields are side-effectful or sticky. Treating AER status/log, FLR, link retrain, slot control, MSI-X mask/pending, VC table load, or margining fields as normal read/write storage can lose diagnostics, interrupt delivery, or link stability.
- MSI-X VF registers are virtualization-sensitive. The resume comment in `amdgpu_device.c` shows that VF MSI-X programming can fail while NBIF protection blocks access; restore sequencing and PF/VF access mode matter.
- PCI command and bridge-window masks control memory access, bus mastering, resource windows, and interrupt-disable behavior. Incorrect masks can break enumeration or create DMA/resource exposure.
- ASPM/LTR/link-control fields interact with platform policy and device power states. Incorrect programming can produce link retraining failures, latency issues, power-management hangs, or performance regressions.
- AER, ACS, ARI, multicast, VC, and ATS-adjacent controls affect isolation, error routing, and traffic ordering. Misprogramming can weaken PCIe isolation or make error handling misleading.
- High-speed link fields are lane-repeated and mechanically similar. A generator mismatch for one lane can be hard to spot by code review but visible in link-training or margining failures.

## Test Signals

- Build coverage: compile AMDGPU with NBIO 4.3.0 and SMU13 support enabled. Missing or renamed generated macros should fail at compile time in `nbio_v4_3.c` or SMU13 files.
- Boot/probe coverage: affected AMD GPUs should enumerate normally, report expected PCI class/capability chains, and expose valid bridge/root-port resource windows.
- SR-IOV coverage: create/resume VFs under a hypervisor and verify MSI-X delivery after suspend/resume or VM resume, including no lost interrupts after `amdgpu_restore_msix()`.
- PCIe link coverage: verify negotiated link width/speed, data-link active state, no unexpected retraining loops, and expected 8 GT/s/16 GT/s/32 GT/s equalization status on supported hardware.
- Power-management coverage: exercise ASPM and LTR policy paths with `CONFIG_PCIEASPM`, checking that suspend/resume, runtime PM, and performance states do not regress.
- AER coverage: monitor kernel logs and PCIe AER counters for correctable/uncorrectable error storms; injected errors should populate status/header-log fields and clear according to PCIe rules.
- Slot/root-port coverage: hot-plug or slot-status tests, where applicable, should validate attention/power/MRL/interlock bits and interrupts.
- VC/ACS/ARI coverage: virtualization and IOMMU tests should verify enumeration, isolation, peer-to-peer routing policy, and traffic-class/virtual-channel negotiation on platforms that expose those features.
