# subset-b-003356 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_7_1_0_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_7_1_0_sh_mask.h

### Purpose
`osssys_7_1_0_sh_mask.h` is the generated shift/mask companion for the AMD OSSSYS 7.1.0 register block. It defines the bit positions and field masks used to program and decode the OSS interrupt handler registers, VMID-to-PASID lookup registers, retry CAM, interrupt flood/storm controls, ring-buffer controls, virtualization violation logs, mailbox registers, and client configuration tables. It contains no executable code; its value is that it binds driver logic to the exact hardware register layout for OSSSYS 7.1.0.

### Important APIs, Types, And Functions
There are no C functions or types. The public API is the macro namespace consumed by AMDGPU register helpers:

- `IH_VMID_*_LUT__PASID_*` and `IH_VMID_*_LUT_MM__PASID_*` define the 16-bit PASID fields for GC and MM VMID lookup tables.
- `IH_COOKIE_0` through `IH_COOKIE_7` describe the interrupt vector cookie layout: client/source/ring/VMID, timestamp, PASID source, force-to-PF, and up to 128 bits of context ID.
- `IH_RB_CNTL`, `IH_RB_RPTR`, `IH_RB_WPTR`, `IH_RB_BASE`, `IH_RB_BASE_HI`, `IH_RB_WPTR_ADDR_*`, and matching `*_RING1` fields describe the primary and secondary IH ring buffers, including enable bits, ring size, overflow handling, writeback, MC space, VMID, and doorbell read-pointer configuration.
- `IH_CNTL`, `IH_CNTL2`, `IH_CLK_CTRL`, `IH_MEM_POWER_CTRL`, and `IH_MEM_POWER_CTRL2` cover global IH timing, self-interrupt write-pointer forcing, clock overrides, and memory power gating delays.
- `IH_STORM_CLIENT_LIST_CNTL`, `IH_LIMIT_INT_RATE_CNTL`, `IH_INT_FLOOD_CNTL`, `IH_MSI_STORM_*`, and `IH_INT_DROP_*` configure flood control, interrupt rate limiting, MSI storm mitigation, and selective interrupt dropping.
- `IH_RETRY_INT_CAM_CNTL`, `IH_RETRY_CAM_ACK`, and `IH_DOORBELL_RETRY_CAM` support recoverable page-fault retry CAM operation and acknowledgement.
- `IH_STATUS`, `IH_RB_STATUS`, `IH_VF_RB*_STATUS*`, `IH_INT_FLAGS`, `IH_CLIENT_CREDIT_ERROR`, `IH_CREDIT_STATUS`, `IH_GPU_IOV_VIOLATION_LOG*`, and `IH_COOKIE_REC_VIOLATION_LOG` expose status and diagnostics.
- `SEM_MAILBOX`, `SEM_MAILBOX_CLEAR`, `IH_VIRT_RESET_REQ`, `IH_CLIENT_CFG*`, `IH_RING1_CLIENT_CFG_*`, `IH_CID_REMAP_*`, `IH_CHICKEN`, and `IH_MMHUB_CNTL` provide virtualization, client routing, remapping, firewall, and MMHUB control fields.

These macros are intended for use through common AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and PSP-mediated register programming paths.

### Control Flow
The header has no runtime control flow. At compile time it is included with `oss/osssys_7_1_0_offset.h` by OSSSYS 7.1.0 users. Runtime control flow appears in consumers:

- `gmc_v12_1.c` includes this header and uses `regIH_VMID_LUT_INDEX`, `regIH_VMID_0_LUT`, and `regIH_VMID_0_LUT_MM` from the offset header with the PASID layout defined here to read VMID/PASID mappings for GC and MM instances.
- IH implementations such as `ih_v7_0.c` use the same register-field model when initializing ring offsets, setting ring buffer base addresses, enabling/disabling ring interrupts, clearing write-pointer overflow, configuring doorbells, enabling flood control, adding MSI storm delay, routing selected clients to ring 1, and enabling retry CAM for OSSSYS 7.1.0 devices.
- Fault handling in `gmc_v12_1.c` depends on IH cookie parsing performed elsewhere in the IRQ path; the field definitions here define the hardware-side layout that becomes `amdgpu_iv_entry` data such as client ID, source ID, VMID, PASID, timestamp, node ID, and source data.

### State, Persistence, And Dependencies
The header has no in-memory state and no persistence of its own. The state it describes lives in GPU MMIO registers and ring-buffer memory:

- IH ring state persists in hardware registers and in the writeback/ring buffers allocated by the driver.
- VMID-to-PASID mappings persist in OSSSYS LUT registers and are sampled by GMC fault-handling code.
- Interrupt storm/drop/flood state, retry CAM entries, client credit status, IOV violation logs, and mailbox values persist until hardware or driver writes clear or update them.

The file depends on the companion `osssys_7_1_0_offset.h` for register addresses and on AMDGPU SOC15 access infrastructure for address calculation. It also implicitly depends on generated-header consistency with the ASIC register specification: every `__SHIFT`/`_MASK` pair must match the offset header and the hardware revision selected by `amdgpu_ip_version()`.

### Integration Points
This header integrates with the AMDGPU interrupt, VM fault, and virtualization paths:

- `gmc_v12_1.c` uses the OSSSYS 7.1.0 headers to read VMID/PASID mappings, which feeds page-fault attribution and KFD/HSA process lookup.
- IH setup code uses the corresponding field names for ring enablement, ring size, MC-space selection, write-pointer writeback, overflow recovery, doorbell read pointers, retry CAM doorbells, and storm/flood mitigation.
- SR-IOV paths depend on fields such as VF/PF selectors, VF ring status, IOV violation logs, client configuration, credit return status, and PSP register programming identifiers.
- Debug and RAS-facing code can use status and error fields to diagnose dropped interrupts, client credit faults, MMHUB response errors, and cookie-record violations.

### Risks
The main risk is silent hardware misprogramming if any generated constant is stale or paired with the wrong ASIC/IP version. Incorrect ring-buffer masks can corrupt interrupt delivery, lose write-pointer updates, or leave overflow conditions uncleared. Wrong `IH_VMID_*_LUT` layout breaks PASID attribution and can send GPU page faults to the wrong process. Retry CAM and doorbell masks are security and reliability sensitive because the fault handler acknowledges retry entries through a doorbell. Interrupt storm/drop fields are also risky: enabling the wrong field can mask real page faults or flood the host with repeated MSI interrupts. Some OSSSYS 7.1.0 registers moved relative to OSSSYS 7.0.0, and `ih_v7_0.c` carries local address overrides for 7.1-specific ring1 client config and chicken registers, so future cleanup must not assume offsets are invariant just because field layouts are similar.

### Test Signals
Useful validation signals are compile coverage for all AMDGPU configurations that include OSSSYS 7.1.0, boot/resume tests on matching hardware, IH ring initialization logs without PSP programming failures, working MSI interrupt delivery, no write-pointer overflow after stress, correct routing of page-fault interrupts to ring 1 when enabled, and successful recoverable page-fault retry CAM handling. Fault-injection or stress tests should watch `IH_RB_STATUS`, `IH_STATUS`, `IH_INT_FLOOD_STATUS`, `IH_RB*_INT_FLOOD_STATUS`, `IH_CLIENT_CREDIT_ERROR`, and VMID/PASID lookup results. Static checks should verify every `REG_SET_FIELD(..., IH_*, FIELD, ...)` field has matching `__SHIFT` and `_MASK` definitions and that the companion offset header exposes the corresponding `regIH_*` address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_7_1_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pcie/pcie_6_1_0_offset.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pcie/pcie_6_1_0_offset.h

### Purpose
`pcie_6_1_0_offset.h` is the generated offset table for the AMD PCIe 6.1.0 register block. It maps symbolic `reg*` names to register offsets and `*_BASE_IDX` selector values for PCIe/DXIO hardware identification, PCI config-space views, link control, lane equalization, flow-control, performance counters, PRBS diagnostics, soft reset, power-management, RX margining, SMU fencing, and transaction tracking. It contains addresses only; field interpretation comes from `pcie_6_1_0_sh_mask.h`.

### Important APIs, Types, And Functions
There are no functions or C types. The exported interface is the generated macro set:

- DXIO and MAC discovery: `regDXIO_HWDID`, `regDXIO_LINKAGE_*`, `regMAC_CAPABILITIES1`, and `regMAC_CAPABILITIES2`.
- PCI configuration and capabilities: `regCOMMAND`, `regSTATUS`, `regLATENCY`, `regHEADER`, `regPCIE_LTR_*`, `regPCIE_L1_PM_SUB_*`, and `regPCIE_MARGINING_ENH_CAP_LIST`.
- Per-lane and link training registers: `regPCIE_LANE_ERROR_STATUS`, `regPCIE_LANE_0_EQUALIZATION_CNTL` through `regPCIE_LANE_15_EQUALIZATION_CNTL`, `regPCIE_LC_CNTL*`, `regPCIE_LC_TRAINING_CNTL`, `regPCIE_LC_LINK_WIDTH_CNTL`, `regPCIE_LC_SPEED_CNTL`, `regPCIE_LC_SPEED_CNTL2`, `regPCIE_LC_EQ_CNTL_8GT`, `regPCIE_LC_EQ_CNTL_16GT`, `regPCIE_LC_EQ_CNTL_32GT`, and status registers `regPCIE_LC_STATE*`/`regPCIE_LC_STATUS*`.
- Packet, replay, and credit controls: `regPCIE_RX_*`, `regPCIE_TX_*`, `regPCIE_FC_*`, and advertised/allocated/init credit registers.
- Common PCIe control, strap, and debug: `regPCIE_CNTL`, `regPCIE_CONFIG_CNTL`, `regPCIE_DEBUG_CNTL`, `regPCIE_BUS_CNTL`, `regPCIE_CFG_CNTL`, `regPCIE_STRAP_*`, `regPCIE_HIP_REG*`, and `regSMN_APERTURE_ID_*`.
- Diagnostics and counters: `regPCIE_PERF_*`, `regPCIE_PRBS_*`, `regPCIE_LANE_ERROR_COUNTERS_*`, `regPCIE_RX_LAST_TLP*`, `regPCIE_TX_LAST_TLP*`, and tracking registers.
- Reset and power management: `regSWRST_*`, `regCPM_*`, `regLC_CPM_CONTROL_*`, `regCLKREQB_PAD_CNTL`, `regLNCNT_CONTROL`, `regPCIE_PGMST_CNTL`, and `regPCIE_PGSLV_CNTL`.

Each `*_BASE_IDX` value selects the register base used by SOC15 access helpers; in this file the PCS/DXIO block uses base index `0`, while most PCIe configuration and controller blocks use base index `1`.

### Control Flow
The header has no runtime control flow. At compile time it provides constants to drivers that call SOC15 register access macros. The visible consumer in this tree is `amdgpu/nbif_v6_3_1.c`, which includes this offset header and `pcie_6_1_0_sh_mask.h`.

In `nbif_v6_3_1.c`, the PCIe offset macros feed ASPM/LTR setup when `CONFIG_PCIEASPM` is enabled. The driver reads and writes PCIe link-control registers such as `regPCIE_LC_CNTL`, `regPCIE_LC_CNTL3`, `regPCIE_LC_CNTL4`, `regPCIE_LC_CNTL7`, and `regPCIE_LC_RXRECOVER_RXSTANDBY_CNTL`, while field masks from the companion sh/mask header set inactivity timers, L1/L0s behavior, NBIF ASPM input, L23 behavior after PME acknowledgement, and RX standby behavior. The same NBIF implementation exposes PCIe indirect index/data offsets through NBIO registers, so code that needs indexed PCIe access depends on the offset table being synchronized with the NBIF access path.

### State, Persistence, And Dependencies
The header has no mutable state. The state it identifies is hardware state in the PCIe block: link training state, negotiated width/speed status, PCIe capability registers, ASPM/LTR controls, flow-control credit counters, PRBS diagnostics, lane error counters, and reset/power-management controls. These values persist in hardware until reset or reprogramming and can affect host/device connectivity immediately.

Dependencies include the SOC15 register addressing layer, the companion `pcie_6_1_0_sh_mask.h` field definitions, NBIF access infrastructure in `nbif_v6_3_1.c`, Linux PCI capability helpers such as `pcie_capability_read_word()` and `pcie_capability_set_word()`, and build-time feature gating through `CONFIG_PCIEASPM`. Hardware selection is controlled by AMDGPU IP-version checks, so the file must be used only for ASICs whose PCIe IP block matches 6.1.0.

### Integration Points
This table is part of the NBIF/PCIe bring-up and power-management path:

- `nbif_v6_3_1_program_aspm()` uses PCIe 6.1.0 offsets and masks to disable unsafe link power states while programming LTR/strap values, then re-enable desired ASPM behavior.
- Linux PCI config-space helpers are used alongside MMIO register writes, so hardware register state and kernel PCI core state must stay consistent.
- Link diagnostics and RAS/debug flows can use the PRBS, lane error, replay, credit, last-TLP, and performance counter offsets to inspect failures.
- Low-level reset and power-management routines depend on the `SWRST`, `CPM`, `PGMST`, and `PGSLV` offsets when manipulating PCIe block resets or power states.

### Risks
Incorrect offsets or base indexes can write to the wrong PCIe register, which is high impact because these registers control link training, ASPM, reset, and transaction flow. A stale `regPCIE_LC_*` offset can break resume, cause link instability, or leave LTR/ASPM inconsistent with the PCI core. Lane equalization and speed-control offsets are especially sensitive on Gen4/Gen5 style links because a bad write can degrade negotiated width or speed. Some address blocks share offsets for paired lane controls, so users must combine this offset header with the correct field masks instead of assuming one register per lane. The file also includes diagnostic/error-injection style registers; accidental writes to error-inject or reset registers can create hard-to-debug PCIe faults.

### Test Signals
Validation should include build coverage for `nbif_v6_3_1.c`, boot and suspend/resume on matching hardware, `lspci` confirmation that negotiated link speed/width and LTR/ASPM state remain expected, and stress runs that exercise GPU DMA while ASPM/LTR programming is enabled. Register-level tests should read back `regPCIE_LC_CNTL*`, `regPCIE_LC_SPEED_CNTL*`, `regPCIE_LC_STATUS*`, lane error counters, PRBS counters, and PCIe performance counters after link training and after resume. Static checks should confirm every `RREG32_SOC15(PCIE, ..., regPCIE_*)`/`WREG32_SOC15(PCIE, ..., regPCIE_*)` use has a corresponding offset here and field definitions in `pcie_6_1_0_sh_mask.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pcie/pcie_6_1_0_offset.h -->
