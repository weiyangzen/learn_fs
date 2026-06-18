# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pcie/pcie_6_1_0_offset.h

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
