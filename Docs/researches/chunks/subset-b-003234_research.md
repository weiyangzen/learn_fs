# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 19456-22067

## Scope

This chunk covers generated shift and mask macros from the AMDGPU NBIO 7.4 register mask header. It starts at the tail of the VF15 PCIe extended capability area and runs through the beginning of the GDC RAS status block, ending inside `GDCSOC_RAS_LEAF4_STATUS`.

The range is organized by the source file's `addressBlock` comments:

- VF15 PCIe ATS and ARI extended capability fields.
- `nbio_nbif0_bif_bx_pf_SYSPFVFDEC` and `nbio_nbif0_bif_bx_SYSDEC`, including MM/PCIE indirect indexes, system hub indirect windows, BIOS scratch registers, interrupt controls, and graphics MMIO register CAM mappings.
- RCC strap, endpoint, downstream, PF/VF, and device-level BIF decode fields for PCIe policy, LTR, DPA, error reporting, peer apertures, bus numbers, reset, BACO, and address LUTs.
- BIF decode fields for interrupt control, doorbells, framebuffer access, HDP flush/remap, ring-buffer state, mailbox registers, and VM-hypervisor mailbox signaling.
- GDC and duplicated `GDC0_` blocks for NGDC/SYSHUB control, SDMA/IH/MMSCH/ACV doorbell ranges, doorbell fences, and S2A arbitration controls.
- MSI-X vector register fields for graphics vectors 0 through 2 and the pending bit array.
- SYSHUB direct clock, deep-sleep, transaction-idle, scratch, reset, QoS, and NIC400 interconnect controls.
- SION credit, burst, time-slot, and control registers.
- GDC reset and GDC RAS central/leaf control/status fields.

The file is purely generated register metadata. This chunk defines preprocessor constants only; it has no C functions, structs, global variables, runtime storage, or executable control flow.

## Purpose

The purpose of this section is to describe the bit-level ABI for NBIO 7.4 hardware registers. Each hardware register field is represented by the standard pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field bit offset.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, test, or compose that field in a 32-bit register value.

The sibling `nbio_7_4_offset.h` header supplies register addresses such as `mmBIF_FB_EN`, `mmGPU_HDP_FLUSH_REQ`, `mmGPU_HDP_FLUSH_DONE`, `mmBIF_DOORBELL_INT_CNTL`, `mmBIF_IH_DOORBELL_RANGE`, and `mmREMAP_HDP_MEM_FLUSH_CNTL`; this header supplies the field layout at those addresses. Driver code consumes these constants through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### PCIe ATS, ARI, and Indirect Windows

The opening lines finish the VF15 PCIe capability area. `BIF_CFG_DEV0_EPF0_VF15_0_PCIE_ATS_ENH_CAP_LIST`, `BIF_CFG_DEV0_EPF0_VF15_0_PCIE_ATS_CAP`, and `BIF_CFG_DEV0_EPF0_VF15_0_PCIE_ATS_CNTL` define capability-list linkage, invalidate queue depth, page-aligned/global invalidate capability, STU, and `ATC_ENABLE`. `BIF_CFG_DEV0_EPF0_VF15_0_PCIE_ARI_*` fields expose ARI capability, next-function number, function-group capabilities, and ARI control.

`MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`, `SYSHUB_INDEX_OVLP`, `SYSHUB_DATA_OVLP`, `PCIE_INDEX`, `PCIE_DATA`, `PCIE_INDEX2`, and `PCIE_DATA2` are indirect access windows. In `nbio_v7_4.c`, `nbio_v7_4_get_pcie_index_offset()` and `nbio_v7_4_get_pcie_data_offset()` return the SOC15 offsets for `mmPCIE_INDEX2` and `mmPCIE_DATA2`, so other AMDGPU code can route PCIe register accesses through this NBIO aperture.

### Scratch, Interrupt, and MMIO CAM Registers

`SBIOS_SCRATCH_0..3` and `BIOS_SCRATCH_0..15` are full-width scratch registers used as firmware/BIOS-visible state exchange slots. The masks are full `0xFFFFFFFFL`, meaning the header documents storage width but not ownership or protocol.

`BIF_RLC_INTR_CNTL`, `BIF_VCE_INTR_CNTL`, and `BIF_UVD_INTR_CNTL` expose command-complete, self-recovered hang, FLR-needed hang, and VM-busy transition interrupt controls for RLC, VCE, and UVD. `BIF_UVD_INTR_CNTL` also includes an `UVD_INST_SEL` field in the top nibble.

`GFX_MMIOREG_CAM_ADDR0..7`, matching `GFX_MMIOREG_CAM_REMAP_ADDR0..7`, `GFX_MMIOREG_CAM_CNTL`, and the completion policy registers describe a small CAM for graphics MMIO address remapping. The address/remap masks cover 20-bit values, `GFX_MMIOREG_CAM_CNTL__CAM_ENABLE_MASK` enables eight entries, and the zero/one/programmable completion registers are full-width. Incorrect CAM values can redirect MMIO accesses to the wrong block or change completion behavior.

### RCC PCIe Endpoint, Downstream, and Device Control

The RCC strap and endpoint/downstream groups cover PCIe behavior visible early in device setup:

- `RCC_BIF_STRAP0` and `RCC_DEV0_EPF0_STRAP0` include strap-derived revision/device behavior, including `STRAP_ATI_REV_ID_DEV0_F0`, which `nbio_v7_4_get_rev_id()` reads and shifts.
- `EP_PCIE_*`, `DN_PCIE_*`, and unprefixed `PCIE_*` registers define endpoint/downstream scratch, control, config, RX/TX policy, error reporting, link-speed control, LTR control, PME, DPA capabilities, and DPA per-substate power allocation.
- `EP_PCIE_TX_LTR_CNTL` includes LTR message policy fields. `nbio_v7_4_program_ltr()` in `nbio_v7_4.c` writes the corresponding SMN register and clears `EP_PCIE_TX_LTR_CNTL__LTR_PRIV_MSG_DIS_IN_PM_NON_D0_MASK` as part of ASPM/LTR programming.
- `RCC_ERR_LOG`, `RCC_ERR_INT_CNTL`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_IOV_FUNC_IDENTIFIER`, `RCC_BACO_CNTL_MISC`, `RCC_RESET_EN`, `RCC_VDM_SUPPORT`, `RCC_MARGIN_PARAM_CNTL0/1`, peer range registers, bus-number controls, peer framebuffer offsets, common link control, requester-id restore, and multi-host arbitration fields provide the low-level knobs for PCIe error handling, memory-size discovery, SR-IOV, peer apertures, link/power policy, and multi-host traffic.

`nbio_v7_4_get_memsize()` reads `mmRCC_CONFIG_MEMSIZE`, and `nbio_v7_4_enable_doorbell_aperture()` writes the `RCC_DOORBELL_APER_EN__BIF_DOORBELL_APER_EN` field.

### BIF Doorbells, Framebuffer Access, HDP Flush, and Mailboxes

The `nbio_nbif0_bif_bx_BIFDEC1` and PF decode groups are the highest-impact driver integration area in this chunk.

`BUS_CNTL`, `BIF_FEATURES_CONTROL_MISC`, `BIF_DOORBELL_CNTL`, and `BIF_DOORBELL_INT_CNTL` control coherency, endpoint path disable bits, atomic error interrupts, self-ring/doorbell translation behavior, doorbell monitor interrupt generation, and doorbell/RAS interrupt status/clear/disable bits. `nbio_v7_4_handle_ras_controller_intr_no_bifring()` and `nbio_v7_4_handle_ras_err_event_athub_intr_no_bifring()` read `BIF_DOORBELL_INT_CNTL` status fields and write the matching clear fields when the BIF ring is disabled. `nbio_v7_4_enable_doorbell_interrupt()` toggles `DOORBELL_INTERRUPT_DISABLE`.

`BIF_FB_EN` has `FB_READ_EN` and `FB_WRITE_EN`; `nbio_v7_4_mc_access_enable()` writes these bits to allow or block memory-controller framebuffer access through NBIO.

`BIF_INTR_CNTL__RAS_INTR_VEC_SEL` selects the RAS interrupt vector. The v7.4 RAS interrupt setup paths set it to vector 1 for the bare-metal case.

`BACO_CNTL` and the `BIF_BACO_EXIT_TIMER*` registers describe BACO enable, dummy mode, power-off, D-state bypass, interrupt masking, auto-exit, and exit timing. `nbio_v7_4_init_registers()` clears `BACO_DUMMY_EN` and `BACO_EN` for IP version 7.4.4 when not running as an SR-IOV VF.

`BIF_SDMA0_DOORBELL_RANGE`, `BIF_SDMA1_DOORBELL_RANGE`, `BIF_IH_DOORBELL_RANGE`, `BIF_MMSCH0_DOORBELL_RANGE`, `BIF_ACV_DOORBELL_RANGE`, plus duplicated `GDC0_` range registers, all use the same `OFFSET`/`SIZE` layout. `nbio_v7_4_sdma_doorbell_range()`, `nbio_v7_4_vcn_doorbell_range()`, and `nbio_v7_4_ih_doorbell_range()` use these masks to program doorbell ownership windows for SDMA, VCN/MMSCH, and IH.

`HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ`, `GPU_HDP_FLUSH_DONE`, `REMAP_HDP_MEM_FLUSH_CNTL`, and `REMAP_HDP_REG_FLUSH_CNTL` define the HDP flush interface. `nbio_v7_4_get_hdp_flush_req_offset()` and `nbio_v7_4_get_hdp_flush_done_offset()` return the request/done offsets, while `nbio_v7_4_hdp_flush_reg` publishes done masks for CP0..CP9 and SDMA0..SDMA1. `nbio_v7_4_remap_hdp_registers()` writes remap offsets used by KFD MMIO remapping. The chunk's request/done masks are the synchronization contract for cache flush completion.

The mailbox group (`MAILBOX_MSGBUF_TRN_DW*`, `MAILBOX_MSGBUF_RCV_DW*`, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX`) provides transmit/receive message data, valid/ack handshakes, interrupt enables, and compact VM/hypervisor mailbox fields. These fields are stateful protocol registers: valid and ack bits must be ordered with the associated data fields.

### GDC, SYSHUB, NIC400, SION, Reset, and RAS

The GDC/SYSHUB blocks define clock/power and fabric controls:

- `NGDC_MGCG_CTRL`, `GDC0_NGDC_MGCG_CTRL`, `SYSHUB_MGCG_CTRL_SOCCLK`, and `SYSHUB_MGCG_CTRL_SHUBCLK` control medium-grain clock gating enable/mode/hysteresis and sub-block disables.
- `SYSHUB_DS_CTRL_*`, `SYSHUB_DS_CTRL2_*`, and bgen bypass/immediate-enable registers control deep-sleep and bus-generator behavior for HST/DMA/SYSHUB clients.
- `SYSHUB_TRANS_IDLE_SOCCLK` provides per-VF and PF transaction-idle status bits. These are especially relevant to SR-IOV teardown, FLR, and reset sequencing.
- `HST_CLK*`, `DMA_CLK*`, and `NIC400_*` fields configure FLR/link-reset behavior, static QoS overrides, read/write weighted round-robin values, outstanding transaction limits, rate/fairness controls, target flow-control latency, and QoS ranges.
- `SION_CL*` registers define request/data/read-response/write-response burst targets, time slots, and pool-credit allocation across four client lanes. `SION_CNTL_REG0/1` collect force, idle, sleep, credit, reset, and timeout behavior.

`SHUB_PF_FLR_RST`, `SHUB_PF0_VF_FLR_RST`, `SHUB_LINK_RESET`, `SHUB_HARD_RST_CTRL`, `SHUB_SOFT_RST_CTRL`, `SHUB_SDP_PORT_RST`, and `SHUB_RST_MISC_TRL` define reset triggers and reset-domain selection for PFs, VFs, links, NIC400, SDP ports, SION, and RSMU-assisted soft reset.

The final RAS block starts with `GDCL_RAS_CENTRAL_STATUS` and `GDCSOC_RAS_CENTRAL_STATUS`, then covers `GDCSOC_RAS_LEAF0_CTRL` through `GDCSOC_RAS_LEAF6_CTRL`, `GDCSOC_RAS_LEAF2_MISC_CTRL`, and status registers from `GDCSOC_RAS_LEAF0_STATUS` through the start of `GDCSOC_RAS_LEAF4_STATUS`. Leaf controls expose detection enables, poison/parity error event enables, stall enables, generated/propagated event enables, and, on leaf 2, RAS interrupt/stall/drop/mask-disabling fields. Leaf status registers expose received error events, poison/parity detection, generated-event state, and egress-stall/propagation state.

## Control Flow and State Behavior

There is no local control flow in this header. The runtime flow is created by consumers that read or write registers with these masks:

1. Read a register through `RREG32_SOC15`, `RREG32_PCIE`, or a raw register offset.
2. Extract fields with `REG_GET_FIELD` or test masks directly.
3. Compose updated values with `REG_SET_FIELD` or mask operations.
4. Write the register back with `WREG32_SOC15`, `WREG32_PCIE`, `WREG32_FIELD15`, or a raw write.

Several fields represent persistent hardware configuration until reset or later reprogramming: doorbell ranges, framebuffer access enablement, BACO control, PCIe LTR/DPA policy, SYSHUB deep-sleep/clock-gating, NIC400 QoS, SION credits, reset-domain enables, and RAS control bits.

Other fields represent transient hardware state or command handshakes: `GPU_HDP_FLUSH_REQ`/`GPU_HDP_FLUSH_DONE`, mailbox valid/ack bits, doorbell interrupt status/clear bits, transaction-pending bits, SYSHUB transaction-idle bits, FLR/reset strobes, and RAS central/leaf status bits. These require ordering and polling discipline; treating a status bit as durable configuration, or vice versa, can deadlock reset/flush paths or lose interrupts.

## Dependencies and Integration Points

Direct compile-time dependencies are the AMDGPU register helper macros and the corresponding offset header. Runtime dependencies are the NBIO, PCIe, GDC/SYSHUB, HDP, RAS, KFD, and SR-IOV paths that program the registers.

Important consumers observed in this tree include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, which includes this header and uses fields from this chunk for revision ID extraction, memory-controller access, doorbell apertures and ranges, IH control, HDP flush request/done offsets, BACO cleanup, RAS doorbell interrupt handling, RAS interrupt vector selection, HDP register remapping, and ASPM/LTR programming.
- SMU/PowerPlay files such as `pm/swsmu/smu11/arcturus_ppt.c`, `pm/swsmu/smu13/aldebaran_ppt.c`, `pm/swsmu/smu13/smu_v13_0_6_ppt.c`, and `pm/powerplay/hwmgr/vega20_hwmgr.c`, which include the NBIO 7.4 masks for power-management register programming on supported ASICs.
- HDP implementations use the same register-helper idiom for power/flush state, and NBIO v7.4 publishes HDP flush masks from this chunk through `nbio_v7_4_hdp_flush_reg`.

The constants also integrate with firmware and virtualization protocols. BIOS scratch fields, RCC straps, `BIF_VMHV_MAILBOX`, PF/VF FLR reset bits, per-VF transaction-idle bits, and doorbell aperture/range fields are shared boundaries between host driver, firmware/PSP/SMU, hypervisor, and guest-visible device state.

## Risks and Review Notes

- Generated-header drift is high risk. A wrong mask or shift silently writes the wrong hardware bit and can break PCIe link policy, memory access, HDP coherency, reset sequencing, RAS delivery, or VF isolation.
- Full-width scratch/mailbox/data masks do not define ownership. Callers must know the firmware or hypervisor protocol before writing them.
- Doorbell range `OFFSET` and `SIZE` fields are security-sensitive. Incorrect values can expose another engine's doorbells, disable an engine's doorbells, or let a VF ring queues outside its intended aperture.
- HDP flush request/done masks are synchronization-sensitive. Missing or stale `DONE` masks can cause cache flush waits to time out or complete before writes are visible.
- RAS status/clear fields are easy to mishandle. The v7.4 driver explicitly clears doorbell interrupt status and harvests counters when the BIF ring is disabled; changes must preserve that ordering.
- Reset and FLR bits can affect PF/VF isolation and fabric stability. Writes to `SHUB_PF0_VF_FLR_RST`, `SHUB_LINK_RESET`, `SHUB_HARD_RST_CTRL`, or `SHUB_SOFT_RST_CTRL` should be reviewed with transaction-idle and pending-status handling.
- Some fields are ASIC-variant-sensitive. `nbio_v7_4.c` carries ALDEBARAN-specific register aliases and temporary masks, showing that this header may not fully describe every v7.4.x derivative.

## Test Signals

Useful validation signals for changes touching consumers of this chunk include:

- Successful kernel build with `W=1` coverage for AMDGPU configurations that include NBIO 7.4 ASICs.
- Driver probe on affected ASICs with correct `get_rev_id`, memory-size reporting, and no unexpected BACO dummy-mode warnings.
- Doorbell smoke tests: SDMA, IH, VCN/MMSCH, KFD queues, and interrupt delivery continue to function after range/aperture programming.
- HDP flush tests: CP and SDMA flush request/done paths do not time out and memory visibility is correct across VRAM/GTT/KFD paths.
- ASPM/LTR and power-management tests: suspend/resume, runtime power transitions, BACO entry/exit, and SMU power-state changes remain stable.
- SR-IOV tests: VF FLR, PF/VF transaction-idle, mailbox valid/ack, and VF doorbell isolation behave correctly.
- RAS tests: injected or simulated NBIF/ATHUB error events increment CE/UE counters, clear status, and invoke the expected global RAS ISR path without repeated stale interrupts.
- Register audit tests comparing generated mask/shift pairs against the hardware register database for NBIO 7.4 and known derivatives.
