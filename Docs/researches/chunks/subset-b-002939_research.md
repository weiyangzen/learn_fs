# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 86242-88736

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 2.3 register mask header. It starts in the tail of the `RCC_DEV0_EPF0_VF26_GFXMSIX_*` MSI-X table definitions, covers the repeated virtual-function register blocks for `VF27` through `VF30`, and then enters the `nbio_pcie0_pswuscfg0_cfgdecp` PCIe upstream-switch configuration space register set through the beginning of `PSWUSCFG0_1_PCIE_ESM_CAP_5`.

The file is generated hardware metadata. It defines preprocessor constants only: no functions, structs, variables, allocation, locking, or executable control flow live in this chunk. Each field normally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit position.
- `<REGISTER>__<FIELD>_MASK`, the bit mask for extracting or composing that field.

## Purpose

The purpose of this section is to provide the bit-level ABI used by AMDGPU/NBIO code when programming NBIO 2.3 hardware registers and PCIe configuration-space views. The matching `nbio_2_3_offset.h` header supplies register offsets such as `mmBIF_BX_DEV0_EPF0_VF27_GPU_HDP_FLUSH_REQ` or PCIe config-space offsets; this header supplies field positions and masks for those register values.

This chunk is particularly focused on two surfaces:

- SR-IOV virtual-function NBIF/RCC state for high-numbered VFs (`VF27` through `VF30`) plus the final MSI-X entries for `VF26`.
- PCIe upstream-port configuration, capability, error-reporting, virtual-channel, ACS, multicast, LTR, ARI, L1 PM substate, and electrical-speed-margining fields under `PSWUSCFG0_1_*`.

Driver code consumes these constants through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### VF26 Tail MSI-X Fields

The chunk begins mid-family with the tail of the `VF26` graphics MSI-X table:

- `RCC_DEV0_EPF0_VF26_GFXMSIX_VECT3_MSG_DATA`
- `RCC_DEV0_EPF0_VF26_GFXMSIX_VECT3_CONTROL`
- `RCC_DEV0_EPF0_VF26_GFXMSIX_PBA`

These define the message-data dword, vector mask bit, and pending-bit-array bits for vector 3 and the four-vector pending status. The previous chunk contains the earlier `VF26` vector address/control definitions, so this chunk is not a complete `VF26` MSI-X description by itself.

### VF27 Through VF30 System PF/VF Decode Windows

Each of `VF27`, `VF28`, `VF29`, and `VF30` begins with a `SYSPFVFDEC` address block:

- `BIF_BX_DEV0_EPF0_VF*_MM_INDEX`, with `MM_OFFSET` and `MM_APER`.
- `BIF_BX_DEV0_EPF0_VF*_MM_DATA`, with full-width `MM_DATA`.
- `BIF_BX_DEV0_EPF0_VF*_MM_INDEX_HI`, with full-width `MM_OFFSET_HI`.

These macros describe the indirect MMIO index/data window exposed per virtual function. The split low/high offset fields are the register-level encoding used when a VF needs an indirect MMIO aperture rather than direct PF-owned access.

### VF RCC SR-IOV, Doorbell, and Identity Fields

The repeated `RCC_DEV0_EPF0_VF*_BIFPFVFDEC1` blocks expose RCC-side VF status and configuration:

- `RCC_ERR_LOG` contains sticky/status bits for invalid SR-IOV register access and doorbell read access.
- `RCC_DOORBELL_APER_EN` enables the BIF doorbell aperture.
- `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` are full-width configuration dwords.
- `RCC_IOV_FUNC_IDENTIFIER` exposes the VF function identifier and an `IOV_ENABLE` bit.

These are virtualization-sensitive fields. They encode whether a VF is allowed to participate in SR-IOV access paths and whether doorbell apertures are visible for that function.

### VF BIF Error, Doorbell, HDP Flush, and Mailbox Fields

The `BIF_BX_DEV0_EPF0_VF*_BIFPFVFDEC1` blocks repeat the same register layout for each VF:

- `BIF_BME_STATUS` tracks DMA activity while bus mastering is low and has a clear bit.
- `BIF_ATOMIC_ERR_LOG` records unsupported-request atomic error classes: opcode, request-enable low, length, and non-relaxed/non-request attributes, with matching clear bits.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `...BASE_LOW`, and `...CNTL` define the self-ring doorbell guest physical address aperture, enable bit, mode bit, and size field.
- `HDP_REG_COHERENCY_FLUSH_CNTL` and `HDP_MEM_COHERENCY_FLUSH_CNTL` expose flush-address fields for HDP coherency remap/control paths.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` define CP0 through CP9 and SDMA0/SDMA1 request/done bits.
- `BIF_TRANS_PENDING` exposes master and slave transaction-pending status.
- `NBIF_GFX_ADDR_LUT_BYPASS` controls or reports LUT bypass for the VF graphics address path.
- `MAILBOX_MSGBUF_TRN_DW0..3` and `MAILBOX_MSGBUF_RCV_DW0..3` provide four dwords each for transmit and receive message buffers.
- `MAILBOX_CONTROL` defines transmit valid/ack and receive valid/ack handshake bits.
- `MAILBOX_INT_CNTL` enables valid and ack interrupts.
- `BIF_VMHV_MAILBOX` packs hypervisor/VM mailbox interrupt enables, 4-bit transmit/receive data fields, valid bits, and ack bits.

The PF version of similar fields is actively consumed by `amdgpu/nbio_v2_3.c`: for example, the NBIO 2.3 implementation programs doorbell apertures, reports HDP flush request/done offsets, and builds `nbio_v2_3_hdp_flush_reg` from `BIF_BX_PF_GPU_HDP_FLUSH_DONE__CP*` and `__SDMA*` masks. The VF27-VF30 definitions are the per-VF layout equivalents for virtualization and remap paths.

### VF Graphics MSI-X Fields

Each complete `VF27` through `VF30` RCC `BIFDEC2` block defines four graphics MSI-X vectors plus a pending-bit array:

- `GFXMSIX_VECT0..3_ADDR_LO` use `MSG_ADDR_LO` at bit 2 with a `0xFFFFFFFC` mask, preserving PCI MSI/MSI-X address alignment.
- `GFXMSIX_VECT0..3_ADDR_HI` provide the upper 32 bits of the message address.
- `GFXMSIX_VECT0..3_MSG_DATA` provide the interrupt message data.
- `GFXMSIX_VECT0..3_CONTROL` expose each vector's mask bit.
- `GFXMSIX_PBA` exposes pending bits 0 through 3.

This family is tied to VM and SR-IOV interrupt routing. `amdgpu_device.c` has a resume path note that QEMU programming of VF MSI-X tables, specifically `GFXMSIX_VECT0_ADDR_LO`, may be blocked by NBIF protection until VF exclusive access is restored; the driver then disables/enables MSI-X so QEMU reprograms the table.

### PCI/PCIe Type-1 Configuration Header

The `PSWUSCFG0_1_*` block starts at `nbio_pcie0_pswuscfg0_cfgdecp` and maps a PCIe upstream switch/bridge configuration-space view. The first group mirrors conventional PCI/PCIe header fields:

- Identity and class-code fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command and status fields: `COMMAND` bits for IO/memory/bus-master enables, parity/SERR behavior, fast back-to-back, and interrupt disable; `STATUS` and `SECONDARY_STATUS` bits for capability list, interrupt status, target/master aborts, parity, and system errors.
- Bridge topology fields: `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, upper prefetchable base/limit, `IO_BASE_LIMIT_HI`, and bridge-control bits in `IRQ_BRIDGE_CNTL`.
- Capability and ROM/interrupt fields: `CAP_PTR`, `ROM_BASE_ADDR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, vendor capability list, adapter ID, and power-management capability/status registers.

These masks describe PCI config-space semantics, but they are still generated into the ASIC register namespace because NBIO exposes the PCIe block through AMD register-access mechanisms.

### PCIe Capability, Link, MSI, and Vendor Capabilities

The chunk includes the PCIe capability and several standard/extended capabilities:

- `PCIE_CAP_LIST` and `PCIE_CAP` describe the PCIe capability ID, next pointer, version, device/port type, slot implementation, and interrupt-message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` cover payload size, phantom functions, extended tags, endpoint L0s/L1 acceptable latency, attention/power indicators, role-based error reporting, error enables, no-snoop, max read request, function-level reset, and error/status bits.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` cover max speed/width, ASPM, exit latencies, clock power management, bandwidth notifications, active-state link control, retrain/common-clock/extended-synch, negotiated speed/width, training, slot clock, and bandwidth status.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover completion timeouts, ARI forwarding, atomic ops, LTR, OBFF, 10-bit tags, end-to-end TLP prefixes, FRS, supported link speeds, compliance settings, de-emphasis, equalization, crosslink, and downstream-component presence.
- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO/HI`, `MSI_MSG_DATA`, and `MSI_MSG_DATA_64` define MSI capability layout.
- `SSID_CAP_LIST`, `SSID_CAP`, `MSI_MAP_CAP_LIST`, `MSI_MAP_CAP`, and vendor-specific capability/header/scratch fields define subsystem ID, MSI mapping, and vendor-specific extension data.

NBIO 2.3 code directly programs related PCIe/ASPM/LTR state through `RREG32_PCIE` and `WREG32_PCIE` in `amdgpu/nbio_v2_3.c`. Not every `PSWUSCFG0_1_*` macro is referenced by name in the driver, but this generated mask family supplies the same kind of field encodings used by PCIe link-management and power-management code.

### Virtual Channel, Serial Number, AER, and Link Equalization

The virtual-channel and error-reporting portions include:

- `PCIE_VC_ENH_CAP_LIST`, `PCIE_PORT_VC_CAP_REG1/2`, `PCIE_PORT_VC_CNTL`, and `PCIE_PORT_VC_STATUS`.
- `PCIE_VC0_RESOURCE_CAP/CNTL/STATUS` and `PCIE_VC1_RESOURCE_CAP/CNTL/STATUS`, including traffic-class-to-VC mapping, arbitration table load/select/status, VC ID, enable, and negotiation pending.
- `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST` and serial-number low/high dwords.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, and `PCIE_ADV_ERR_CAP_CNTL`.
- Header and TLP prefix logs: `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3`.
- Secondary PCIe capability fields: `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`.

These definitions are important for PCIe reliability and diagnostics. AER status/mask/severity fields cover data-link protocol errors, surprise down, poisoned TLPs, flow-control protocol errors, completion timeout/abort, unexpected completions, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violations, internal errors, multicast blocked TLPs, atomic-op egress blocking, TLP prefix blocking, and poisoned TLP egress blocking. Lane equalization fields provide per-lane downstream/upstream port transmit preset and preset hint encodings.

### ACS, Multicast, LTR, ARI, L1 PM Substates, and ESM

The end of the chunk covers additional PCIe extended capabilities:

- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress control vector size.
- `PCIE_MC_ENH_CAP_LIST`, `PCIE_MC_CAP`, `PCIE_MC_CNTL`, `PCIE_MC_ADDR0/1`, receive/block-all masks, block-untranslated masks, and overlay BAR fields for PCIe multicast.
- `PCIE_LTR_ENH_CAP_LIST` and `PCIE_LTR_CAP` for maximum snoop and no-snoop latency values and scales.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` for next-function number and function-group behavior.
- `PCIE_L1_PM_SUB_CAP_LIST`, `PCIE_L1_PM_SUB_CAP`, `PCIE_L1_PM_SUB_CNTL`, and `PCIE_L1_PM_SUB_CNTL2` for PCI-PM L1.1/L1.2, ASPM L1.1/L1.2, L1 PM substate support, common-mode restore time, power-on scale/value, T_POWER_ON programming, and threshold fields.
- `PCIE_ESM_CAP_LIST`, `PCIE_ESM_HEADER_1/2`, `PCIE_ESM_STATUS`, `PCIE_ESM_CTRL`, and `PCIE_ESM_CAP_1..5` for PCIe electrical speed margining presence/status/control and per-speed capability bits.

The ESM capability macros in this chunk enumerate fine-grained supported margining speeds from `ESM_2P5G` upward. `PCIE_ESM_CAP_1` covers 2.5G through 10.9G; `PCIE_ESM_CAP_2` covers 11.0G through 13.9G; `PCIE_ESM_CAP_3` covers 14.0G through 15.9G; `PCIE_ESM_CAP_4` covers 16.0G through 18.9G; and this chunk ends inside `PCIE_ESM_CAP_5`, after defining shift fields through `ESM_21P4G`. The matching masks and any remaining higher ESM fields continue in the next chunk.

## Control Flow and State Behavior

There is no runtime control flow in this header. Its effect is compile-time substitution of constants into register reads, writes, field composition, and field extraction.

The persistent state described by these macros is hardware state:

- VF MMIO indirect-window state for index/data/high-index access.
- VF RCC SR-IOV status, doorbell aperture enablement, memory-size/configuration dwords, and function identity.
- VF BIF error logs, bus-master/DMA state, atomic error state, transaction-pending bits, and address-LUT bypass state.
- VF doorbell self-ring GPA aperture base/mode/size and mailbox valid/ack/message state.
- VF HDP flush request/done state for CP and SDMA engines.
- VF graphics MSI-X table and PBA state.
- PCI/PCIe bridge configuration, command/status, memory and IO windows, power-management state, PCIe link capabilities/control/status, MSI programming, AER logs/masks/severity, lane equalization state, ACS/ARI/LTR/multicast/L1 PM substate state, and ESM capability/control/status state.

Some fields are ordinary configuration bits, some are status bits, and some are clear or handshake bits. Examples include `CLEAR_DMA_ON_BME_LOW`, `CLEAR_UR_ATOMIC_*`, mailbox valid/ack bits, MSI-X mask bits, AER status bits, VC arbitration load/status bits, link retrain/control bits, L1 PM enable fields, and ESM control/status fields. The header does not encode ordering, privilege rules, write-one-to-clear behavior, or required polling loops; those rules must come from the hardware specification and owning AMDGPU/NBIO/PCIe code.

## Dependencies and Integration Points

Direct dependencies are the generated NBIO 2.3 register-header set:

- `nbio_2_3_offset.h` supplies the offsets and base indices for the register names defined here.
- `nbio_2_3_default.h` supplies reset/default values for generated registers where available.
- AMDGPU's register helper macros consume the `__SHIFT` and `_MASK` definitions.

Observed integration points in this source tree include:

- `amdgpu/nbio_v2_3.c`, which includes this header and implements the NBIO 2.3 function table. It programs PF doorbell apertures, HDP flush remap registers, interrupt control, clock gating, ASPM/LTR, and exposes HDP flush offsets and masks. The VF27-VF30 register families in this chunk mirror the PF/VF machinery used by those flows.
- `amdgpu/amdgpu_discovery.c`, which selects `nbio_v2_3_funcs` and `nbio_v2_3_hdp_flush_reg` for matching hardware.
- `amdgpu/mxgpu_nv.c`, which includes the NBIO 2.3 offset and mask headers for SR-IOV/MxGPU flows.
- `pm/swsmu/smu11/navi10_ppt.c` and `pm/swsmu/smu11/sienna_cichlid_ppt.c`, which include the NBIO 2.3 headers for power-management interactions.
- Display resource code for DCN generations that includes NBIO 2.3 offsets, tying display bring-up to the same NBIO register map.
- `amdgpu_device.c` resume handling for SR-IOV VFs, which notes that `GFXMSIX_VECT0_ADDR_LO` programming by QEMU can be blocked by NBIF protection until exclusive VF access is restored.

The `PSWUSCFG0_1_*` PCIe names appear mostly as generated definitions rather than direct high-level driver identifiers. The actual driver code often uses SMN constants, Linux PCI helpers, or related register names for ASPM, LTR, ESM, and link-management behavior, but those code paths rely on the same hardware contract represented here.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write the wrong hardware field, breaking SR-IOV isolation, doorbell routing, HDP coherency flushes, MSI-X delivery, PCIe link training, ASPM/LTR policy, AER handling, or PCI resource-window programming.
- The VF blocks are mechanically repeated for `VF27` through `VF30`. Copy-generation errors are easy to miss because the field layouts are almost identical but the register prefixes and offsets must stay VF-specific.
- Virtualization fields are privilege-sensitive. Incorrect `IOV_ENABLE`, function identifier, MMIO index/data aperture, doorbell aperture, mailbox, MSI-X, or error-clear definitions can let the PF, guest VF, or hypervisor observe or modify the wrong state.
- HDP flush request/done masks are engine-specific. Confusing CP bits with SDMA bits, or using PF masks against VF registers, can cause stale CPU/GPU memory visibility or flush waits that never complete.
- MSI-X table fields affect interrupt routing. Incorrect address-low alignment, message-data, vector mask, or PBA bits can lose interrupts or re-enable masked vectors. This is especially risky around VM resume, where the driver already documents NBIF protection interactions.
- PCIe config and capability fields are standardized but packed densely. Incorrect AER masks/severity, link-control bits, VC arbitration fields, ACS controls, ARI forwarding, L1 PM substate fields, or ESM control bits can cause link instability, incorrect error reporting, or security/isolation regressions.
- L1 PM and ASPM fields interact with platform firmware, Linux PCIe ASPM policy, and device removability. Programming these without path capability checks can create resume failures or poor link power behavior.
- This chunk starts and ends mid-family: it begins after most `VF26` MSI-X vector fields and ends inside `PSWUSCFG0_1_PCIE_ESM_CAP_5`. A merged report must connect adjacent chunks before treating either family as complete.

## Test and Validation Signals

Useful validation is mostly build-time and hardware/integration coverage:

- Build AMDGPU, SW SMU, display, and MxGPU/SR-IOV code that includes `nbio_2_3_sh_mask.h`; this catches missing, renamed, or syntactically invalid macros.
- Exercise NBIO 2.3 initialization through `nbio_v2_3_funcs`: doorbell aperture enable/disable, self-ring aperture programming, IH doorbell range setup, HDP remap setup, memory-size reads, and clock-gating state.
- Validate HDP coherency flush behavior for CP0-CP9 and SDMA0/SDMA1 paths by confirming request/done polling completes and no stale memory is observed across CPU/GPU synchronization.
- Run SR-IOV VF boot, reset, suspend/resume, and exclusive-access transitions with many VFs enabled, specifically covering high-numbered VFs if the platform exposes them.
- Verify VF MSI-X programming and interrupt delivery across VM resume. The expected signal is that MSI-X vectors are reprogrammed after exclusive access and guest interrupts continue arriving.
- Test VF mailbox transmit/receive valid/ack and interrupt enable paths, including hypervisor mailbox data, valid, and ack fields if supported by the platform.
- Run PCIe ASPM/LTR tests on removable and non-removable devices. Link state should enter expected low-power states without training failures or wake/resume regressions.
- Exercise PCIe AER injection or error-reporting diagnostics where available, checking uncorrectable/correctable status, mask, severity, header log, and TLP prefix log decoding.
- Validate PCIe link equalization and link status on different widths/speeds, including x4-specific workarounds in NBIO 2.3 code and downstream component presence/equalization status.
- Confirm ACS, ARI, multicast, VC, and L1 PM substate capability fields match Linux PCI enumeration and do not regress IOMMU/SR-IOV isolation expectations.
- For hardware that exposes electrical speed margining, read ESM capability/status/control and confirm the enumerated speed bits match platform expectations.

## Unresolved Cross-Chunk References

This chunk starts in the middle of the `VF26` MSI-X table and does not include `VF26` vector 0 through most of vector 3 address fields. It also ends inside `PSWUSCFG0_1_PCIE_ESM_CAP_5`, after shift definitions through `ESM_21P4G`; the matching masks and any remaining ESM fields belong to the next chunk. The merge/reconciliation lane should stitch those adjacent chunks before producing the final per-file research report.
