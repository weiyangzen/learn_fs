# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 2496-4768

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask header. It contains no executable C code; it publishes preprocessor constants for bit positions and already-positioned masks used by DCN 2.0 display-controller register helpers.

The range begins in the `dce_dc_dmcu_dispdec` address block, at the tail of `DMCU_UC_INTERNAL_INT_STATUS`, and continues through DMCU interrupt, mailbox, performance-monitor, DisplayPort receiver, and DMCU interrupt-routing registers. It then switches to the `dce_dc_dmu_ihc_dispdec` address block and defines DMU/IHC GPU timer and display interrupt status registers through the beginning of `DISP_INTERRUPT_STATUS_CONTINUE22`.

The primary hardware domains described here are:

- DMCU internal interrupt status and static-screen interrupt status.
- DMCU interrupt occurrence/clear registers for ABM, MCP/SCP, UC internal events, DCPG power up/down, vblank, OTG range timing, and vupdate-no-lock events.
- DMCU host/UC interrupt masks and UC XIRQ/IRQ selection bits.
- DMCU scratch, interrupt counters, firmware checksum sampling, and UC clock gating controls.
- Master/slave communication mailbox registers used for DMCU, ABM, PSR, and command handshakes.
- DMCU performance monitor and DisplayPort receiver interrupt status/routing registers.
- DMU IHC GPU timer start/read controls and the top-level display interrupt status chain, including HUBP flip/detile/underflow, HPD/HPDRX, DMCU, OTG, DCIO, AUX/I2C, DP training/stream disable, audio endpoint, DCPG, ABM, and vupdate-no-lock interrupt status bits.

Each field appears as a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro. Driver code combines these values with register-address constants from `dcn_2_0_0_offset.h` and wrapper macros such as `REG_GET`, `REG_UPDATE`, `REG_WRITE`, `FD_MASK`, `FD_SHIFT`, and generation-specific register lists.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or object definitions in this chunk. The API surface is the generated macro namespace.

The DMCU interrupt status registers include:

- `DMCU_UC_INTERNAL_INT_STATUS` for UC IRQ, XIRQ, software interrupt, illegal opcode trap, timer compare/overflow/capture, real-time interrupt, and pulse accumulator status bits.
- `DMCU_SS_INTERRUPT_CNTL_STATUS` for static-screen interrupt status, occurred, and clear bits for static screen channels 1 through 6.
- `DMCU_INTERRUPT_STATUS`, `DMCU_INTERRUPT_STATUS_1`, `DMCU_INTERRUPT_STATUS_CONTINUE`, and `DMCU_INTERRUPT_STATUS_2` for DMCU-visible interrupt occurrence and clear bits covering ABM ready/update, MCP/SCP, external software, UC internal, UC register read timeout, DCPG IHC domain power up/down, vblank, OTG range timing, DIO/DCCG, DWB, DP link, FEC, HPD/HPDRX, DCIO, SDMA, DMCU I2C, and OTG vupdate-no-lock events.

The DMCU routing registers include `DMCU_INTERRUPT_TO_HOST_EN_MASK`, `DMCU_INTERRUPT_TO_UC_EN_MASK`, `DMCU_INTERRUPT_TO_UC_EN_MASK_1`, `DMCU_INTERRUPT_TO_UC_EN_MASK_CONTINUE`, and `DMCU_INTERRUPT_TO_UC_EN_MASK_2`. These expose interrupt delivery enables for host-facing and microcontroller-facing paths. The matching `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL`, `_1`, `_CONTINUE`, and `_CONT2` registers select whether routed events use the UC XIRQ or IRQ path for the same event families.

The DMCU command and mailbox families include:

- `DC_DMCU_SCRATCH`, `DMCU_INT_CNT`, `DMCU_INT_CNT_CONTINUE`, `DMCU_FW_CHECKSUM_SMPL_BYTE_POS`, and `DMCU_UC_CLK_GATING_CNTL` for scratch/debug, interrupt counters, firmware checksum sampling byte positions, and UC clock-gating controls.
- `MASTER_COMM_DATA_REG1..3`, `MASTER_COMM_CMD_REG`, and `MASTER_COMM_CNTL_REG` for host-to-DMCU payload bytes, command bytes, and the master communication interrupt bit.
- `SLAVE_COMM_DATA_REG1..3`, `SLAVE_COMM_CMD_REG`, and `SLAVE_COMM_CNTL_REG` for DMCU-to-host payload, command, and slave communication interrupt state.

The performance-monitor and DPRX register groups include:

- `DMCU_PERFMON_INTERRUPT_STATUS1..5` for display pipe performance-monitor interrupt status across HUBP, DPP, MPC, OPP, OTG, DIO, and secondary interrupt groups.
- `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1..5` and `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1..5` for enabling and selecting the UC interrupt line for those performance-monitor sources.
- `DMCU_DPRX_INTERRUPT_STATUS1` for DisplayPort receiver sideband, training, service IRQ, AUX reply/timeout/error, sink request, and DPCD/automated test style events across HPD RX instances.
- `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1` and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` for routing the DPRX event set to the UC.

The DMU/IHC timer macros include `DC_GPU_TIMER_START_POSITION_V_UPDATE`, `DC_GPU_TIMER_START_POSITION_VSTARTUP`, `DC_GPU_TIMER_READ`, and `DC_GPU_TIMER_READ_CNTL`. These describe per-display start-position fields for GPU timer capture around vupdate and vstartup, a 32-bit readback register, and read-control fields for reference-clock selection, read mode, and selected display signal.

The `DISP_INTERRUPT_STATUS*` chain is the top-level display interrupt status map. In this chunk it covers `DISP_INTERRUPT_STATUS` through the beginning of `DISP_INTERRUPT_STATUS_CONTINUE22`. The chain includes:

- HUBP flip, detile, and underflow events for multiple pipes.
- DC HPD and HPD RX events, DMCU SCP, DMCU software, and DMIF/DCPG-style power events.
- DIO, DCCG, DWB, GPIO pad, DCIO, SDMA, and DMCU I2C events.
- OTG static-screen, vupdate, GSL vsync gap, vstartup, and vready status for six timing generators, plus vupdate-no-lock entries for OTG0 through OTG5 at the end of the chunk.
- AUX/DIO, DC I2C DDC/VGA/generic read request, and DOUT I2C hardware-done events.
- DisplayPort fast training complete and video-stream disable events for DIG instances.
- Audio endpoint format-changed, enabled, and disabled events for endpoints 0 through 7.
- DCPG IHC domain 8 through 15 power up/down events and ABM0 high-gain, low-sense, and backlight-update events.

The `DISP_INTERRUPT_STATUS_CONTINUE*__DISP_INTERRUPT_STATUS_CONTINUE*` fields at bit 31 are continuation indicators linking the status-register chain.

## Control Flow

This chunk has no runtime control flow. It is compile-time hardware metadata.

A typical runtime path is:

1. DCN 2.0 component code includes `dcn_2_0_0_offset.h` for register addresses and this file for field masks and shifts.
2. Per-generation tables or helper structures materialize the generated constants through macros such as `SR`, `SRI`, `FD_MASK`, `FD_SHIFT`, `DMCU_SF`, `ABM_SF`, `REG_OFFSET`, and `REG_FIELD` style lists.
3. Register helper calls read, write, extract, or update the target register field by pairing the address with the `*_MASK` and `*__SHIFT` constants.
4. Hardware then performs the interrupt routing, event status latching/clearing, mailbox handshake, timer read/capture, or diagnostic counter behavior.

The direct DCN 2.0 include points in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

The most obvious control-sensitive consumer in this range is the display IRQ service. `irq_service_dcn20.c` maps IV source IDs from `ivsrcid/dcn/irqsrcs_dcn_1_0.h` to DAL IRQ sources such as vblank, vline, page flip, HPD, HPDRX, and vupdate. It also builds per-source enable and ack metadata with generated address/mask constants. Some display interrupt status bits from this chunk are also mirrored in `irqsrcs_dcn_1_0.h` comments, for example I2C hardware-done, audio endpoint state changes, OTG static-screen/vupdate/vstartup/vready events, and continuation status registers.

The DMCU mailbox fields are consumed through the older DCE DMCU/ABM abstractions. `dce_dmcu.h`, `dce_dmcu.c`, `dce_abm.h`, and `dce_abm.c` define register lists and field lists for `MASTER_COMM_*`, `SLAVE_COMM_*`, and `DMCU_INTERRUPT_TO_UC_EN_MASK`, then use waits and read/modify/write helpers to send PSR, ABM, backlight, PHY sync, EDID, and related commands to the microcontroller. For DCN 2.0-specific files, DMUB supersedes many firmware interactions, but this generated DMCU namespace remains part of the shared register contract.

## State And Persistence Behavior

The header stores no software state. It describes hardware state in display controller registers.

The represented state classes include:

- Sticky interrupt occurrence and clear bits in DMCU and display IHC status registers. Many `*_OCCURRED` and `*_CLEAR` fields deliberately share the same bit position and mask, implying write-one-to-clear behavior for the clear alias while reads report the occurred alias.
- Enable masks that persist in hardware until changed by the driver, reset, suspend/resume restore, power gating, or ASIC reset.
- UC interrupt line selection bits that determine whether an enabled event is signaled through XIRQ or IRQ.
- Communication mailbox state, including command bytes, payload bytes, and master/slave interrupt handshakes. These fields must be sequenced with polling/wait helpers so host and microcontroller do not overwrite each other's in-flight messages.
- Counter/readback state such as DMCU interrupt counters, firmware checksum sample byte positions, GPU timer readback, and performance/DPRX interrupt status.
- Live top-level display interrupt status chain state. These bits reflect hardware events from many display subblocks and may be level, pulse, sticky, or continuation status depending on the event.

Persistence is hardware-defined and not encoded by the generated macros. Some fields are read-only status, some are write-one-to-clear, some are read/write enables, and some are self-clearing triggers or latches. Driver code must preserve unrelated bits during read/modify/write operations and must know the access type from hardware documentation and the surrounding DC/DCE sequencing code.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` supplies the matching register addresses and base-index constants.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h` supplies the field masks and shifts described here.
- SOC base headers such as `navi10_ip_offset.h`, `vega10_ip_offset.h`, and `soc15_hw_ip.h` provide block base information used by generated address macros.
- Display helper headers under `drivers/gpu/drm/amd/display/` convert these macros into per-generation register, shift, and mask structures.

Integration points by functional area:

- Display IRQ handling: `display/dc/irq/dcn20/irq_service_dcn20.c` uses the DCN 2.0 generated headers with `SRI` and `IRQ_REG_ENTRY` macros to construct IRQ source metadata. The `DISP_INTERRUPT_STATUS_CONTINUE*` fields in this chunk correspond to source IDs documented in `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, even when the DCN 2.0 IRQ table acknowledges more specific subblock registers for common sources.
- DMCU and ABM command paths: `display/dc/dce/dce_dmcu.*`, `display/dc/dce/dce_abm.*`, and `display/dc/dce/dce_link_encoder.h` define reusable register/field lists for the `MASTER_COMM_*`, `SLAVE_COMM_*`, and `DMCU_INTERRUPT_TO_UC_EN_MASK` names present in this chunk.
- DMUB path: `display/dmub/src/dmub_dcn20.c` includes the same generated headers and uses the field-mask infrastructure for DMCUB registers. This particular chunk's legacy DMCU mailbox fields are distinct from the DMCUB register set, but the include contributes to the shared generated namespace used by DMUB DCN 2.0 support.
- Power and clock/display-resource setup: DCN 2.0 resource, clock manager, and GPIO factory files include the header for the same generation-specific register map. Their direct field usage is mostly outside this chunk, but compile-time namespace consistency matters across the whole generated file.
- GMC path: `amdgpu/gmc_v10_0.c` includes the DCN 2.0 header alongside MMHUB and ATHUB headers. The chunk itself is display-focused and does not implement memory-management behavior.

Although this repository path is under a local `ceph-client` source tree, the file is AMDGPU display hardware metadata. It has no Ceph, filesystem, or distributed-storage logic.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Incorrect generated masks or shifts can compile successfully while enabling the wrong interrupt, clearing the wrong sticky bit, corrupting unrelated enable bits, or routing an event to the wrong microcontroller interrupt line.

High-risk fields in this chunk include:

- `*_OCCURRED` and `*_CLEAR` aliases that share a bit. Misusing the clear alias can drop pending interrupts; failing to clear sticky events can cause interrupt storms or repeated work.
- DMCU interrupt enable and XIRQ/IRQ selection registers. A one-bit error can strand PSR, ABM, DP RX, HPD RX, vblank, DCPG, or firmware events on the wrong target.
- `MASTER_COMM_*` and `SLAVE_COMM_*` mailbox fields. Wrong byte shifts or interrupt bits can hang DMCU/ABM/PSR command handshakes, corrupt firmware commands, or make wait loops time out.
- Top-level `DISP_INTERRUPT_STATUS_CONTINUE*` fields. The register chain is dense, repeated, and instance-indexed; copy-generation mistakes can isolate failures to one pipe, one HPD/DDC instance, one audio endpoint, or one DIG instance.
- Power-domain and vupdate/vstartup/vready status bits. Misreported power events or timing events can affect suspend/resume, runtime power management, modesets, vblank accounting, page flips, and atomic update pacing.
- DPRX/AUX/I2C events. Incorrect status or routing can break link training, DPCD access, EDID reads, HPD RX service IRQ handling, or automated test responses.

This chunk starts after the `DMCU_UC_INTERNAL_INT_STATUS` register declaration has already begun in the previous lines and ends in the middle of `DISP_INTERRUPT_STATUS_CONTINUE22`, before its full mask list and the following `DC_GPU_TIMER_START_POSITION_VREADY` block. The final merged per-file document should treat those as chunk boundaries, not missing definitions.

The generated macros do not encode access type, reset value, valid enum values, locking requirements, or ordering constraints. Consumers must know whether a field is read-only, write-one-to-clear, level-sensitive, pulse-sensitive, self-clearing, or double-buffered from hardware documentation and the surrounding driver code.

## Test Signals

Useful validation signals include both generated-header checks and hardware/display behavior:

- AMDGPU/DCN 2.0 builds should compile all direct include users of `dcn_2_0_0_sh_mask.h`, especially `irq_service_dcn20.c`, `dmub_dcn20.c`, `dcn20_resource.c`, `dcn20_clk_mgr.c`, `hw_factory_dcn20.c`, and `gmc_v10_0.c`.
- Register-generation validation should compare every `*_MASK` and `*__SHIFT` pair in this range against AMD's source register database and the matching addresses in `dcn_2_0_0_offset.h`.
- Static checks can verify that every `*_CLEAR` alias that shares a mask with `*_OCCURRED` is intentional and that continuation bits remain at bit 31 where present.
- IRQ tests should exercise HPD, HPD RX, I2C/DDC hardware-done, AUX/DPCD, DP training complete, DP stream disable, vblank/vstartup/vupdate/vready, vupdate-no-lock, static-screen, page-flip, underflow, DCPG power, ABM, and audio endpoint interrupts.
- DMCU/ABM/PSR command tests should validate mailbox waits, command byte packing, payload register writes, master/slave interrupt handshakes, and timeout behavior.
- Suspend/resume and runtime power-management stress should verify that DCPG domain power events and interrupt enable/clear state are restored without stale status bits or lost notifications.
- Multi-display stress should cover all six OTG/HUBP/HPD/DDC style instances and all relevant audio endpoints, because the register chains are heavily repeated and instance-specific.
- Link training and hotplug tests should watch for DPRX/AUX/HPDRX status correctness, service IRQ handling, and EDID/I2C completion.
- Regression symptoms from bad constants include missed or repeated interrupts, stuck DMCU mailbox waits, broken backlight or PSR commands, link training failures, hotplug failures, bad audio endpoint notifications, vblank/page-flip timing failures, underflow handling failures, and failures isolated to one display pipe or connector.

## Cross-Chunk Notes

The previous chunk contains the DMCU RAM access and event-trigger definitions and the beginning of `DMCU_UC_INTERNAL_INT_STATUS`. This chunk continues through the DMCU interrupt and mailbox region, then enters the DMU IHC display interrupt status region. The next chunk continues `DISP_INTERRUPT_STATUS_CONTINUE22` and the later GPU timer/display interrupt mask definitions. The final per-file merge should describe the whole header as a generated DCN 2.0 hardware register layout contract rather than algorithmic code.
