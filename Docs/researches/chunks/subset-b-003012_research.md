# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 17127-19667

## Scope

This chunk covers the middle of the generated NBIO 6.1 shift/mask header. It begins at the tail of PCIe link-control fields (`PCIE_LC_SPEED_CNTL`, `PCIE_LC_CNTL2`, `PCIEP_STRAP_MISC`, `LTR_MSG_INFO_FROM_EP`) and then spans NBIO address blocks for RCC, BIF/BX, GDC, SYSHUB MMREG direct, SION, GDC reset, GDC RAS, and the start of `BIF_CFG_DEV0_SWDS1` PCI/PCIe configuration-space fields. The requested range contains 2,112 `#define` entries: 1,060 `__SHIFT` constants, 1,052 `_MASK` constants, and 394 register comment blocks across these address blocks:

- `nbio_nbif_rcc_pf_0_BIFPFVFDEC1[13440..14975]`
- `nbio_nbif_rcc_pf_0_BIFDEC1[13440..14975]`
- `nbio_nbif_bif_bx_pf_BIFDEC1[13440..14975]`
- `nbio_nbif_bif_bx_pf_BIFPFVFDEC1`
- `nbio_nbif_gdc_GDCDEC[14976..15487]`
- `nbio_nbif_rcc_pf_0_BIFDEC2`
- `nbio_nbif_gdc_GDCDEC`
- `nbio_nbif_syshub_mmreg_direct_syshubdirect`
- `nbio_nbif_nbif_sion_SIONDEC`
- `nbio_nbif_gdc_rst_GDCRST_DEC`
- `nbio_nbif_gdc_ras_gdc_ras_regblk`
- `nbio_nbif_bif_cfg_dev0_swds_bifcfgdecp`

The range ends inside the `BIF_CFG_DEV0_SWDS1_LINK_CNTL` register definition after `PM_CONTROL_MASK`; the following `LINK_CNTL` masks, `LINK_STATUS`, and later slot capability fields belong to the next chunk.

## Purpose

The file is a generated hardware register bitfield ABI for AMD NBIO 6.1 devices. This chunk supplies field offsets and bit masks used by AMDGPU code to compose, update, and decode 32-bit MMIO, SMN, PCIe, and NBIO register values. It defines constants only; it has no C functions, structs, variables, runtime allocation, or executable logic.

Each field follows the common register helper contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register value.

These definitions pair with sibling headers such as `nbio_6_1_offset.h`, `nbio_6_1_smn.h`, and `nbio_6_1_default.h`, which provide register addresses/defaults, while this file provides bit layout. Consumers use helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### PCIe Link and RCC Control

The first lines finish a PCIe/RCC-adjacent section:

- `PCIE_LC_SPEED_CNTL` exposes Gen2/Gen3 strap-enable bits.
- `PCIE_LC_CNTL2` includes link bandwidth notification disable.
- `PCIEP_STRAP_MISC` exposes multifunction strap enable.
- `LTR_MSG_INFO_FROM_EP` maps a full 32-bit LTR message payload.

The RCC PF/VF decode blocks define register access, SR-IOV, bus, peer, and configuration fields. `RCC_PF_0_0_RCC_ERR_LOG` records invalid SR-IOV register access and doorbell read access. `RCC_PF_0_0_RCC_DOORBELL_APER_EN` enables the BIF doorbell aperture. `RCC_PF_0_0_RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_*` fields expose memory aperture sizing, reserved config state, and function identifiers. `RCC_PF_0_0_RCC_IOV_FUNC_IDENTIFIER` includes both the function identifier and an `IOV_ENABLE` bit.

`RCC_BUS_CNTL` is a high-impact register with fields for disabling PMI I/O, memory, and bus mastering paths, controlling upstream/downstream PMI behavior, root error logging, host poisoned completion logging, completion-abort/unsupported-request error signaling for primary and secondary downstream paths, and private max payload/read request size overrides. Incorrect masks here can affect PCIe request routing, error reporting, and payload sizing.

`RCC_FEATURES_CONTROL_MISC` exposes many protocol-behavior gates: poison packet unsupported-request behavior, FLR CRS return behavior, ATC/PASID response behavior, whether specific unsupported request types are ignored, MSI/MSI-X pending clear behavior, BME checks on pending packet generation, ECRC device-error reporting, and host poison flag checking. These are compatibility and error-containment controls rather than ordinary software state.

`RCC_BUSNUM_*`, `RCC_CAPTURE_HOST_BUSNUM`, `RCC_HOST_BUSNUM`, `RCC_PEER*_FB_OFFSET_*`, `RCC_CMN_LINK_CNTL`, `RCC_EP_REQUESTERID_RESTORE`, `RCC_LTR_LSWITCH_CNTL`, and `RCC_MH_ARB_CNTL` provide bus-number matching, peer framebuffer offset, common-link behavior, requester ID restore, LTR switch settings, and multi-host arbitration masks.

### BIF/BX Core, Interrupt, Doorbell, BACO, and Power-Gating Fields

The BIF decode block starts with indirect-access and bus-control fields. `BIF_MM_INDACCESS_CNTL` selects indirect access behavior. `BUS_CNTL` covers BIOS/ROM write enable, VGA/IO routing, PME/status controls, master abort mode, memory type, PM interrupt disable, clock gating, error signaling, and BME status/int enable behavior. `BIF_SCRATCH0/1` provide full-width scratch registers.

Reset and interrupt controls include:

- `BX_RESET_EN`, with FLR/LINK_RESET/HOT_RESET/SOFT_RESET/PERST reset enables plus FLR delay and reset assertion time.
- `MM_CFGREGS_CNTL`, controlling MMIO config register access.
- `BX_RESET_CNTL`, `INTERRUPT_CNTL`, and `INTERRUPT_CNTL2`, including dummy read address, IH dummy read override/enable, non-snoop, and page request interrupt bits.
- `CLKREQB_PAD_CNTL` and `BIF_*_PAD_CNTL` pad-control fields for PERSTB, PX_EN, REFPADKIN, and CLKREQB.

Doorbell control is a central theme. `BIF_DOORBELL_CNTL` covers self-ring disable, translation check disable, untranslated loopback, non-consecutive byte-enable handling, monitor enable, and monitor interrupt-generation mode. `BIF_DOORBELL_INT_CNTL` provides status/clear bits for doorbell and IOHC RAS interrupts. `BIF_DOORBELL_GBLAPER{1,2}_{LOWER,UPPER}` define global doorbell apertures, and GDC `BIF_*_DOORBELL_RANGE` registers define offset/size pairs for SDMA0, SDMA1, IH, and MMSCH0 doorbells. `BIF_DOORBELL_FENCE_CNTL` controls doorbell fence enable, and `S2A_MISC_CNTL` disables 64-bit doorbell support per engine or AXI host completion error propagation.

`BIF_FEATURES_CONTROL_MISC` exposes requester/completer endpoint disable bits, ring-buffer overflow behavior, atomic error interrupt disable, BME handling, FLR pending-check disables, and a 48-bit self-ring GPA aperture check. `BIF_FB_EN` controls framebuffer read/write enable and is used by NBIO memory-controller access setup.

`BACO_CNTL` and `BIF_BACO_EXIT_TIME*`/`TIMER*` describe bus-active chip-off sequencing: BACO enable, LCLK switching, dummy enable, power-off, D-state bypass, reset interrupt mask, mode, RCU config-done, auto-exit, and hardware exit timers. Vega power-management code uses these masks in BACO command tables to enter and exit low-power states.

The `BIF_VDDGFX_*` group defines comparison windows and stall enables for GFX0-GFX5 and reserved ranges, plus framebuffer comparison controls for HDP, XDMA, and VGA. These masks describe address-range comparators and power-stall behavior around VDDGFX power state. `SMU_BIF_VDDGFX_PWR_STATUS` exposes whether VDDGFX graphics power is off.

`REMAP_HDP_MEM_FLUSH_CNTL` and `REMAP_HDP_REG_FLUSH_CNTL` hold remapped flush addresses. `BIF_RB_*` fields describe BIF ring-buffer enable, size, writeback, base, read/write pointer offsets, overflow clear, and writeback address registers.

### PF0 Virtualization, Mailbox, and HDP Flush

The PF0 BIF/PF/VF block provides masks directly used by virtualization and HDP flush paths:

- `BIF_BX_PF0_BIF_BME_STATUS` records DMA while BME is low and has a clear bit.
- `BIF_BX_PF0_BIF_ATOMIC_ERR_LOG` logs unsupported atomic opcode, request-enable-low, length, and non-relaxed conditions with corresponding clear bits.
- `BIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_BASE_{LOW,HIGH}` and `_CNTL` define the self-ring doorbell GPA aperture base, enable, mode, and size.
- `BIF_BX_PF0_HDP_{REG,MEM}_COHERENCY_FLUSH_CNTL` expose single-bit flush-address fields.
- `BIF_BX_PF0_GPU_HDP_FLUSH_REQ` and `BIF_BX_PF0_GPU_HDP_FLUSH_DONE` map CP0-CP9 and SDMA0/SDMA1 request/done bits.
- `BIF_BX_PF0_BIF_TRANS_PENDING` exposes master/slave pending transaction bits.

`BIF_BX_PF0_MAILBOX_MSGBUF_TRN_DW0..DW3` and `RCV_DW0..DW3` are full 32-bit transfer/receive message data registers. `BIF_BX_PF0_MAILBOX_CONTROL` provides transmit valid/ack and receive valid/ack bits. `BIF_BX_PF0_MAILBOX_INT_CNTL` enables valid/ack interrupts. `BIF_BX_PF0_BIF_VMHV_MAILBOX` provides a compact mailbox with small transmit/receive data fields, valid/ack bits, and interrupt enables.

These fields are consumed by `amdgpu/mxgpu_ai.c` for SR-IOV PF/VF mailbox traffic. That code writes `BIF_BX_PF0_MAILBOX_MSGBUF_TRN_DW*`, sets `TRN_MSG_VALID`, polls or handles acks, reads `RCV_DW*`, and enables mailbox interrupts with `VALID_INT_EN` and `ACK_INT_EN`.

### GDC and SYSHUB Direct Registers

Two GDC decode blocks appear: one with unprefixed register names and one with `GDC1_` names. Both provide SDP disconnect hysteresis fields, a `SHUB_REGS_IF_CTL` bit to control how non-PF MMREG requests are dropped/set-error, reserved full-width registers, SOCCLK-specific SDP hysteresis, per-engine doorbell range controls, doorbell fence enable, and S2A miscellaneous doorbell/AXI host completion behavior.

The `SYSHUB_MMREG_DIRECT_SYSHUBDIRECT` block is a dense system-hub control section. It includes:

- `SYSHUB_MMREG_DIRECT_SYSHUB_DS_CTRL_SOCCLK` and `_SHUBCLK`, with per-HST CL0-CL7 and DMA CL0-CL7 deep-sleep allow bits plus global SYSHUB deep-sleep allow/enable.
- `SYSHUB_MMREG_DIRECT_SYSHUB_DS_CTRL2_*`, with deep-sleep timer fields.
- `SYSHUB_MMREG_DIRECT_SYSHUB_BGEN_ENHANCEMENT_BYPASS_EN_*` and `_IMM_EN_*`, with HST and DMA switch bypass/immediate-enable bits.
- `SYSHUB_MMREG_DIRECT_DMA_CLK{0,1}_SW*_SYSHUB_QOS_CNTL`, defining QoS mode, max value, and min value.
- `SYSHUB_MMREG_DIRECT_DMA_CLK{0,1}_SW*_CL*_CNTL`, with FLR-on-reset, link-reset-on-reset, QoS static override, read WRR weight, and write WRR weight fields for multiple DMA clock/switch/client lanes.
- `SYSHUB_MMREG_DIRECT_HST_CLK0_SW*_CL*_CNTL`, with FLR/link reset enables for host client lanes.
- `SYSHUB_MMREG_DIRECT_SYSHUB_CG_CNTL`, `TRANS_IDLE`, `HP_TIMER`, and `MGCG_CTRL_{SOCCLK,SHUBCLK}`, exposing clock gating enable/timers, per-VF/PF transaction-idle state, a high-priority timer, and medium-grain clock gating controls.
- `SYSHUB_MMREG_DIRECT_SYSHUB_SCRATCH` and `SYSHUB_CL_MASK` scratch/mask controls.
- `SYSHUB_MMREG_DIRECT_NIC400_*_FN_MOD*` fields, all mapping read/write outstanding-issue override bits for NIC400 ASIB/AMIB ports.

This block is mostly low-level fabric policy: clock/deep-sleep entry, reset propagation, QoS arbitration, transaction-idle observation, and interconnect outstanding-issue override.

### SION Credit/Timing and Control Registers

The `SIONDEC` block is dominated by repeated per-client credit/timing registers for clients `CL0` through `CL5`. For each client, the chunk defines full-width 64-bit values split into `_REG0` low 31:0 and `_REG1` high 63:32 halves for:

- `RdRsp_BurstTarget`
- `RdRsp_TimeSlot`
- `WrRsp_BurstTarget`
- `WrRsp_TimeSlot`
- `Req_BurstTarget`
- `Req_TimeSlot`
- `ReqPoolCredit_Alloc`
- `DataPoolCredit_Alloc`
- `RdRspPoolCredit_Alloc`
- `WrRspPoolCredit_Alloc`

These masks are all full-width `0xFFFFFFFFL` halves, so software treats them as raw programmed values rather than packed subfields. `SION_CNTL_REG0` then exposes 20 soft override bits for NBIFSION glue LCLK clock-gate controls across two clock-control groups. `SION_CNTL_REG1` exposes livelock watchdog threshold and clock-gate-off hysteresis.

### GDC Reset and RAS Registers

The `GDCRST_DEC` block defines reset control masks:

- `SHUB_PF_FLR_RST` covers PF0-PF7 FLR reset bits for device 0.
- `SHUB_GFX_DRV_VPU_RST` exposes a GFX driver mode reset.
- `SHUB_LINK_RESET` exposes link reset.
- `SHUB_PF0_VF_FLR_RST` covers VF0-VF15 FLR reset bits plus PF0 soft-PF FLR reset at bit 31.
- `SHUB_HARD_RST_CTRL` and `SHUB_SOFT_RST_CTRL` enable resets for COR, REG, STY, NIC400, and SDP port blocks.
- `SHUB_SDP_PORT_RST` and `SHUB_RST_MISC_TRL` cover SDP reset and RSMU soft reset atomic/cycle fields.

The `gdc_ras_regblk` block defines six identical `GDC_RAS_LEAF{0..5}_CTRL` registers. Each leaf has poison detection, poison error-event, poison stall, parity detection, parity error-event, parity stall, received error-event/link-disable status, poison/parity error detected status, error-event sent status, and egress-stalled status. These are RAS enable/status fields for fabric leaves and should be treated as hardware-owned status plus policy bits, not simple local variables.

### BIF_CFG_DEV0_SWDS1 PCI/PCIe Configuration Space

The final address block starts `BIF_CFG_DEV0_SWDS1` PCI bridge/downstream configuration-space masks:

- Identity and basic config: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, and `BASE_ADDR_1`.
- Bridge routing: `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`, `IO_BASE_LIMIT_HI`, and `IRQ_BRIDGE_CNTL`.
- Capability lists: `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `PCIE_CAP_LIST`, and `PCIE_CAP`.
- PCIe device/link fields: `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, and the beginning of `LINK_CNTL`.

This block mirrors standard PCI/PCIe config-space concepts: command enable bits, status/error bits, class/header/BIST fields, bridge bus/window ranges, MSI/interrupt routing surfaces, PM capability/state/PME fields, PCIe device capability/control/status, link speed/width/latency/ASPM/reporting capabilities, and link-control commands such as disable/retrain/common-clock/extended-sync/clock-power-management. Because the chunk ends mid-register, consumers must combine this chunk with the next one for the complete `BIF_CFG_DEV0_SWDS1_LINK_CNTL` mask set.

## APIs, Types, and Functions

There are no C APIs, types, functions, or data objects declared in this chunk. The important "API" is the generated macro namespace consumed by register helper macros. The field names are part of a compile-time interface: changing a mask name, shift value, or register prefix can break driver compilation or silently target the wrong hardware bit.

The most visible consumers in this repository are:

- `amdgpu/nbio_v6_1.c`, which includes `nbio_6_1_sh_mask.h` and uses fields from this chunk for memory-controller access (`BIF_FB_EN`), doorbell aperture enable, SDMA/IH doorbell ranges, self-ring aperture programming, interrupt control, HDP flush request/done masks, remapped HDP flush registers, and PCIe/LTR/clock-gating programming.
- `amdgpu/mxgpu_ai.c`, which uses PF0 mailbox data/control/interrupt masks for AI SR-IOV mailbox communication.
- `pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`, which include this header for PowerPlay/BACO and NBIO register tables.
- `pm/powerplay/hwmgr/vega10_baco.c` and `vega12_baco.c`, which use `BIF_DOORBELL_CNTL` and `BACO_CNTL` fields to script BACO entry/exit commands.

## Control Flow and Hardware Protocols

The header has no executable control flow, but several groups encode hardware protocols with ordering requirements:

- Doorbell range programming updates `OFFSET` and `SIZE` fields before the engine uses doorbells. The `nbio_v6_1_sdma_doorbell_range()` and `nbio_v6_1_ih_doorbell_range()` helpers read-modify-write the relevant range registers.
- Doorbell aperture enable and self-ring aperture setup require base-low/base-high writes followed by the control register enable/mode/size fields.
- HDP flush uses request and done bits per engine. `nbio_v6_1_hdp_flush_reg` maps `BIF_BX_PF0_GPU_HDP_FLUSH_DONE__CP*` and `__SDMA*` masks so common flush code can request and wait for the correct engines.
- Mailbox traffic in `mxgpu_ai.c` writes transmit dwords, toggles valid bits, waits for ack bits, reads receive dwords, and clears/acks messages. The valid/ack fields are handshake state, not persistent configuration.
- BACO entry/exit fields are sequenced by command tables and wait operations. `BACO_EN`, `BACO_POWER_OFF`, `BACO_MODE`, timers, and reset interrupt masks must be driven in order.
- Reset fields such as PF/VF FLR, link reset, hard reset, and soft reset are command-like bits whose effects depend on hardware reset sequencing.
- RAS leaf controls mix enable bits and sticky/latched status bits; status handling normally requires hardware-specific clear semantics outside this header.
- SYSHUB deep-sleep, clock-gating, QoS, and transaction-idle fields are hardware fabric state. Enabling deep sleep or MGCG interacts with outstanding transactions and idle status.

## State and Persistence Behavior

All state represented by this chunk lives in hardware registers, not in kernel memory owned by the header. Persistence depends on hardware reset and power domains:

- Configuration and policy fields such as PCIe command/control, doorbell range, BACO settings, SYSHUB QoS, deep-sleep, clock-gating, and SION credit targets persist until rewritten or until affected by reset/power transitions.
- Status fields such as transaction pending, mailbox valid/ack, HDP flush done, PCI/PCIe device status, RAS detected/sent/stalled bits, and power-off state are hardware-updated.
- Command bits such as reset assertions, mailbox valid/ack toggles, HDP flush requests, BACO power-off/enable, and write-pointer overflow clear may be edge-like, sticky-until-clear, or self-clearing depending on the underlying register.
- BACO, VDDGFX, and reset domains can discard or reinitialize many NBIO fields; driver resume, GPU reset, SR-IOV reset, and BACO exit paths must reprogram required apertures and policy registers.

The generated constants themselves have no persistence and compile into immediate constants wherever used.

## Dependencies and Integration Points

This chunk depends on the generated SOC15 register naming ecosystem:

- `nbio_6_1_offset.h` supplies `mm*` register offsets for `WREG32_SOC15`, `RREG32_SOC15`, and `SOC15_REG_OFFSET`.
- `nbio_6_1_smn.h` and local SMN defines supply addresses for `RREG32_PCIE`/`WREG32_PCIE` paths.
- `nbio_6_1_default.h` provides reset/default values used for comparison and documentation.
- AMDGPU register helper macros assume the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention.
- Power-management command-table structures consume masks/shifts directly in entries such as BACO read-modify-write and wait commands.

Integration crosses several AMDGPU subsystems: PCIe/NBIO initialization, VRAM/MMIO aperture setup, HDP coherency flush, doorbell management for SDMA/IH/MMSCH, interrupt handling, SR-IOV mailbox communication, BACO/power management, clock/deep-sleep gating, fabric QoS, reset, and RAS.

## Risks

- A wrong shift or mask can silently modify the wrong hardware bit. This is higher risk than ordinary C refactoring because many fields control reset, power, error reporting, address apertures, or PCIe protocol state.
- Several registers mix control and status bits. Blind writes can clear sticky status, trigger resets, request HDP flushes, or acknowledge mailbox messages unintentionally.
- Doorbell and aperture masks include address-alignment assumptions, often shifting from bit 2 and masking aligned ranges. Incorrect composition can expose the wrong doorbell page or break engine interrupts/submission.
- The PF/VF and SR-IOV fields affect isolation between physical and virtual functions. Misprogramming IOV identifiers, invalid-access logging, mailbox fields, or FLR reset bits can break virtualization or leak control between PF/VF contexts.
- BACO and VDDGFX fields affect low-power transitions. Bad timer, mode, or stall/comparator values can cause hangs across suspend/resume, runtime power management, or BACO exit.
- SYSHUB QoS/deep-sleep/clock-gating fields can interact with outstanding transactions. Enabling sleep or reset without checking idle/pending state risks fabric timeouts.
- This chunk ends in the middle of `BIF_CFG_DEV0_SWDS1_LINK_CNTL`; generated or merged documentation must not treat the register definition as complete until the next chunk is reconciled.

## Test Signals

Useful validation signals for consumers of these masks include:

- Build coverage for `amdgpu/nbio_v6_1.c`, `amdgpu/mxgpu_ai.c`, and Vega powerplay/BACO files after any generated-header update.
- Register helper compile checks: `REG_SET_FIELD`/`REG_GET_FIELD` calls must still find matching `__SHIFT` and `_MASK` macro names.
- Doorbell functional tests: SDMA, IH, CP, and MMSCH doorbell ranges program correctly; GPU rings submit work; interrupt handler doorbells fire; self-ring aperture maps to `adev->doorbell.base`.
- HDP flush tests: CP0-CP9 and SDMA0/1 flush request/done masks match observed completion bits under command submission and memory coherency stress.
- SR-IOV mailbox tests: PF/VF valid/ack interrupts and message dwords work under init, reset, full GPU access request/release, and timeout paths in `mxgpu_ai.c`.
- BACO and power-management tests: BACO enter/exit command tables complete, `BACO_MODE` reaches expected values, VDDGFX power status transitions are sane, and runtime suspend/resume reprograms required apertures.
- Reset/RAS tests: PF/VF FLR paths, link reset, soft/hard reset controls, and GDC RAS poison/parity enable/status handling behave as expected without spurious interrupts or stuck transaction bits.
- PCIe capability/control sanity: lspci/config-space-visible fields such as command/status, bridge windows, device control/status, link capability, and partial link control match hardware expectations for NBIO 6.1 devices.
