# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 2435-4812

## Scope

This chunk covers lines 2435-4812 of the generated AMD DCN 3.6.0 shift/mask header. The slice starts in the middle of the `DISP_INTERRUPT_STATUS_CONTINUE13` field list and ends at the `DMCUB_GPINT_DATAIN0` register marker. Within the assigned range there are 2,378 source lines, 196 commented register blocks, 1,082 `__SHIFT` macros, and 1,094 `_MASK` macros.

## Purpose

The file is a hardware register field map for the DCN 3.6 display block in the AMDGPU display driver. This chunk does not implement runtime logic; it defines the compile-time constants that let driver code extract, compose, enable, acknowledge, and route register bitfields without embedding literal bit positions in C code.

The covered registers describe three major areas:

- Display interrupt status continuation registers, including HUBBUB/HUBP, OPP, OPTC/OTG, audio (`AZ`), DCIO/DIG, DDC/I2C, DSC, HPO, and DMCUB interrupt status bits.
- Interrupt destination routing registers for DMU, DCPG, MMHUBBUB, WB, DCHUB, DPP, MPC, OPP, OPTC, OTG, DIG, I2C/DDC/HPD, HDCP/DIO/DCIO, AUX, DSC, and HPO sources.
- DMU, display power-gating, and DMCUB control/status registers, including clock gating, low-power/Z-state controls, domain power gate state, DMCUB memory window layout, DMCUB interrupts, security fault state, mailbox pointers, timers, scratch registers, and core control.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or callable APIs in this chunk. The effective interface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- `REGISTER__FIELD_MASK` gives the already-shifted bit mask.
- Comment lines such as `//DISP_INTERRUPT_STATUS_CONTINUE24` and `// addressBlock: dce_dc_dmu_dmcub_dispdec` mark register and address-block boundaries used by generated address headers and driver-side register-list macros.

Important register groups in this chunk include:

- `DISP_INTERRUPT_STATUS_CONTINUE13` through `DISP_INTERRUPT_STATUS_CONTINUE25`: chained display interrupt status bitmaps. Bit 31 commonly carries the continuation flag to the next status register.
- `DC_GPU_TIMER_START_POSITION_*`: start-position field maps for vready, flip, v-update-no-lock, and flip-away GPU timer events across display pipes.
- `*_INTERRUPT_DEST`: destination selection fields that route many interrupt sources to an interrupt destination.
- `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `DMCUB_SMU_INTERRUPT_CNTL`, `SMU_INTERRUPT_CONTROL`, `ZSC_*`, and low-power clock-gating delay registers in the DMU misc address block.
- `DOMAIN*_PG_CONFIG` and `DOMAIN*_PG_STATUS` for display power-gating domains 0-3, 16-19, and 22-25.
- `DCPG_INTERRUPT_STATUS*` and `DCPG_INTERRUPT_CONTROL_*` for power-gate event status/type/enable fields across domain power-up and power-down events.
- `DMCUB_REGION*`, `DMCUB_REGION3_CW*`, and their high/top/offset fields for DMCUB memory aperture and code-window configuration.
- `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, `DMCUB_INTERRUPT_STATUS`, and `DMCUB_INTERRUPT_TYPE` for DMCUB timer, inbox/outbox, GPINT, fault, power-up, and OTG resync interrupt handling.
- `DMCUB_SEC_CNTL`, `DMCUB_MEM_CNTL`, inbox/outbox base/size/read/write pointer registers, `DMCUB_TIMER_*`, `DMCUB_SCRATCH0` through `DMCUB_SCRATCH18`, and `DMCUB_CNTL`.

## Control Flow

This header has no local control flow. Its constants enter control flow when included by DCN 3.6 driver code:

- `display/dmub/src/dmub_dcn36.c` includes this header and uses `FD_MASK(reg, field)` / `FD_SHIFT(reg, field)` to populate the DCN 3.5-style DMUB register descriptor used for DCN 3.6. The macros expand directly to names from this header.
- `display/dc/irq/dcn36/irq_service_dcn36.c` includes this header and uses generated `_MASK` constants in `IRQ_REG_ENTRY` and `IRQ_REG_ENTRY_DMUB` expansions to build `irq_source_info_dcn36`. For example, the DMCUB outbox entry uses `DMCUB_INTERRUPT_ENABLE__DMCUB_OUTBOX1_READY_INT_EN_MASK` and `DMCUB_INTERRUPT_ACK__DMCUB_OUTBOX1_READY_INT_ACK_MASK`.
- `display/dc/resource/dcn36/dcn36_resource.c` includes this header alongside the offset header, then register-helper macros build register/field tables for DCN 3.6 display components.

The continuation status macros matter for interrupt traversal: status registers expose many independent sources, and the `DISP_INTERRUPT_STATUS_CONTINUE*` bit indicates that later continuation registers may also contain pending sources.

## State And Persistence Behavior

The header itself stores no runtime state. The state it describes is hardware-resident MMIO state:

- Interrupt status bits are latched by display hardware until acknowledged or cleared through companion control/ack registers.
- Interrupt destination fields affect where hardware reports events.
- Power-gating config/status fields reflect desired and finite-state-machine power state for display domains.
- DMCUB mailbox base/size/pointer fields persist in MMIO while the device is powered and define shared communication rings between host driver and DMCUB firmware.
- DMCUB scratch registers are general-purpose firmware/driver communication state and can carry diagnostic or boot/runtime metadata.
- DMCUB security and fault registers expose persistent fault status until cleared through fields such as `DMCUB_INST_FETCH_FAULT_CLEAR` and `DMCUB_DATA_WRITE_FAULT_CLEAR`.

## Dependencies And Integration Points

This header depends on matching generated address definitions in `dcn_3_6_0_offset.h`; shift/mask constants are only useful when paired with the corresponding register address macro. Driver code also depends on helper macros such as `FD_MASK`, `FD_SHIFT`, `SR`, `SRI`, and `IRQ_REG_ENTRY` to compose register tables.

Integration points are concentrated in AMDGPU display code:

- DMUB service setup initializes DMCUB register offset/mask/shift tables from these constants.
- DC IRQ service maps hardware source IDs to `dc_irq_source` values and uses these masks to describe enable and acknowledge register operations.
- DCN 3.6 resource construction feeds display blocks with register and field descriptors for hub, pipe, timing, link, DSC, clocking, power, and firmware paths.
- DMCUB firmware communication uses the inbox/outbox, GPINT, interrupt type, scratch, memory region, and security/fault fields from this range.

## Risks

- A wrong shift or mask silently targets the wrong hardware bit. In interrupt paths this can lose events, acknowledge the wrong source, or leave an interrupt storm uncleared.
- Continuation-register chain bits must align with hardware. A bad `DISP_INTERRUPT_STATUS_CONTINUE*` mask can make the IRQ handler stop early or read beyond the intended status chain.
- DMCUB inbox/outbox pointer or size masks are full-width; mismatched address/pointer interpretation can corrupt firmware communication rings.
- Power-gating and DMCUB security-control fields affect device bring-up, low-power transitions, and fault recovery. Incorrect bit definitions can cause hangs that only appear on specific ASIC revisions or power-management paths.
- This is generated ASIC-specific data. Manual edits are high risk because adjacent DCN versions have similar names but not necessarily identical register coverage.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/runtime oriented:

- Build the AMDGPU display driver with DCN 3.6 enabled; missing or renamed field macros should fail where `FD_MASK`, `FD_SHIFT`, and IRQ register macros expand.
- Exercise display hotplug, HPD RX, page flip, vblank/vstartup, vupdate-no-lock, AUX/DDC, DSC, and DMCUB outbox paths on DCN 3.6 hardware and confirm interrupts are delivered and acknowledged once.
- Validate DMCUB firmware boot and command processing, including inbox/outbox pointer movement and low-priority outbox-ready interrupts.
- Run suspend/resume and display power-gating scenarios to catch bad `DOMAIN*_PG_*`, `DCPG_INTERRUPT_*`, `DMU_CLK_CNTL`, and `ZSC_*` field definitions.
- Check kernel logs for AMDGPU DC IRQ storms, DMCUB timeout/fault messages, HPD failures, AUX transaction failures, and display pipe underflow after display mode changes.
