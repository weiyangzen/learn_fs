# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 2382-4886

## Purpose

This chunk is a generated AMD DCN 4.1.0 register shift/mask header segment. It contains no executable C functions or types; its exported API is a large set of preprocessor constants named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. DCN 4.1 code combines these masks with the matching `dcn_4_1_0_offset.h` register offsets and AMD Display Core register helpers so callers can update MMIO fields symbolically instead of hardcoding bit positions.

The range starts at the tail of `DCPG_INTERRUPT_DEST2`, covers many interrupt destination registers for display, hub, timing, link, hotplug, audio, DSC, HPO, and DMCUB events, then moves through DMU/DCPG power-gating controls, DMCUB firmware window/mailbox/control/status registers, writeback (`DWB`) frame capture and color-processing registers, and ends inside the MCIF writeback buffer status block. The chunk contains 2,144 `#define` entries, grouped by generated register comments and address-block comments.

## Important APIs and register groups

- Interrupt destination macros at the start of the chunk route event sources into the interrupt handling complex. These include `MMHUBBUB_INTERRUPT_DEST`, `WB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST2`, `MPC_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST`, `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `HDCP_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, `DSC_INTERRUPT_DEST`, and `HPO_INTERRUPT_DEST`.
- `DCHUB_INTERRUPT_DEST` maps per-HUBP vblank, vline, vline2, and timeout events for HUBP0-7. `DCHUB_INTERRUPT_DEST2` maps HUBP flip and flip-away events, plus HUBBUB VM fault, timeout, and compbuf-size-change events.
- `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST` repeat a timing-generator interrupt layout for six OTG instances: CPU static-screen, DRR timing, vupdate, snapshot, force-count, force-vsync-next-line, trigger A/B, GSL vsync gap, three vertical interrupt lines, vtotal-min event occurred, vstartup, vready, nominal vsync, vupdate-no-lock, and DRR vtotal-reach events.
- Link and connector interrupt destination groups cover digital stream disable and fast-training-complete events for DIGA-DIGH, I2C/DDC hardware and software completion, DDC read requests, HDCP success/fail/I2C transfer events for HDCP0-7, DCIO DPCS transmitter and receiver errors, HPD1-6 connect and HPD RX events, AUX1-6 software/low-speed completions, DSC0-5 core errors, HPO stream-encoder ALPM wake events, and AZ audio endpoint format/enabled/disabled events.
- `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `DMCUB_SMU_INTERRUPT_CNTL`, `SMU_INTERRUPT_CONTROL`, `DMU_MISC_ALLOW_DS_FORCE`, `DMU_DISPCLK_CGTT_BLK_CTRL_REG`, and `DMU_SOCCLK_CGTT_BLK_CTRL_REG` describe display management unit clock gating, clock stop allowance, DMCUB enablement, SMU interrupt selection, and low-power/deep-sleep controls.
- `DOMAIN*_PG_CONFIG` and `DOMAIN*_PG_STATUS` define power-gating register fields for domains 0-3 and 16-19, 22-25. Each config/status pair exposes power-down request/status and power-up request/status bits for a display power domain.
- `DCPG_INTERRUPT_STATUS`, `_STATUS_2`, `_STATUS_3`, and `DCPG_INTERRUPT_CONTROL_1`, `_CONTROL_2`, `_CONTROL_3` define power-gating interrupt occurrence, mask, and clear bits. The domain set is split across three status/control registers, with domain 0-3 in the first status/control group, domain 16-19 in the second, and domain 22-25 in the third.
- `DC_IP_REQUEST_CNTL` and `LONO_MEM_PWR_REQ_CNTL` expose coarse IP-request enable and LONO memory-power request disable bits.
- `DMCUB_REGION0/1/2/4/5/6/7_OFFSET`, `_OFFSET_HIGH`, and `_TOP_ADDRESS` plus `DMCUB_REGION3_CW0` through `CW7` base/top/offset macros define the firmware-visible address windows used by DMCUB boot and code/data window setup. Top-address registers pack a 29-bit top address with an enable bit at bit 31.
- `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, `DMCUB_INTERRUPT_STATUS`, and `DMCUB_INTERRUPT_TYPE` define the DMCUB interrupt matrix for timers, inbox/outbox ready/done events, GPINT0-6, GPINT IH, undefined address fault, instruction fetch fault, data write fault, power-up trigger, OTG resync trigger, register inbox ready events, and register outbox response events.
- `DMCUB_EXT_INTERRUPT_STATUS`, `DMCUB_EXT_INTERRUPT_CTXID`, and `DMCUB_EXT_INTERRUPT_ACK` provide the external interrupt status/context/ack path. `DMCUB_INST_FETCH_FAULT_ADDR`, `DMCUB_DATA_WRITE_FAULT_ADDR`, and `DMCUB_UNDEFINED_ADDRESS_FAULT_ADDR` expose full-width fault addresses.
- `DMCUB_SEC_CNTL`, `DMCUB_MEM_CNTL`, `DMCUB_CNTL`, `DMCUB_CNTL2`, `DMCUB_MEM_PWR_CNTL`, `DMCUB_LS_WAKE_INT_ENABLE`, `DMCUB_DBG_BUS_SELECT`, `DMCUB_PROC_ID`, and `DMCUB_REGION3_TMR_AXI_SPACE` cover DMCUB reset/security, memory power, enable, soft reset, trace port, power-wait status, debug bus selection, processor ID, and timer AXI-space controls.
- `DMCUB_INBOX*`, `DMCUB_OUTBOX*`, `DMCUB_TIMER_*`, `DMCUB_GPINT_DATAIN*`, `DMCUB_GPINT_DATAOUT`, `DMCUB_SCRATCH0` through `DMCUB_SCRATCH23`, `HOST_INTERRUPT_CSR`, and `DMCUB_REG_INBOX/OUTBOX*` define mailbox rings, register mailboxes, GPINT payloads, scratch registers, and host-visible interrupt status/ack/enable fields.
- `DWB_ENABLE_CLK_CTRL`, `DWB_MEM_PWR_CTRL`, `FC_MODE_CTRL`, `FC_FLOW_CTRL`, `FC_WINDOW_START`, `FC_WINDOW_SIZE`, `FC_SOURCE_SIZE`, `DWB_UPDATE_CTRL`, `DWB_CRC_*`, `DWB_OUT_CTRL`, `DWB_MMHUBBUB_BACKPRESSURE_*`, `DWB_HOST_READ_CONTROL`, `DWB_OVERFLOW_STATUS`, `DWB_OVERFLOW_COUNTER`, and `DWB_SOFT_RESET` cover the display writeback top block: writeback enable, clock/memory power, frame capture, crop/source sizing, update lock, CRC, output clamp/format, backpressure counters, host-read throttling, overflow interrupt state, and soft reset.
- `DWB_HDR_MULT_COEF`, `DWB_GAMUT_REMAP*`, `DWB_OGAM_CONTROL`, `DWB_OGAM_LUT_*`, and the `DWB_OGAM_RAMA_*`/`DWB_OGAM_RAMB_*` ranges define the DWB color pipeline: HDR multiplier, two gamut-remap matrix banks, output gamma mode, LUT access, region boundaries, start/end base/slope controls, offsets, and 34 expansion regions per RAM bank packed two regions per register.
- `MCIF_WB_BUFMGR_SW_CONTROL`, `MCIF_WB_BUFMGR_STATUS`, `MCIF_WB_BUF_PITCH`, and the beginning of `MCIF_WB_BUF_1_STATUS` describe memory-client interface writeback buffer manager enable/interrupt/lock/fence state, current/next buffer status, luma/chroma pitch, and buffer-1 activity/lock/overflow/disable/mode/tag/next-buffer/current-line fields.

## Control flow and usage model

This header has no local control flow. Its macros are compile-time data consumed by version-specific AMD Display Core and DMUB register tables. The normal usage pattern is:

1. Include `dcn_4_1_0_offset.h` for register addresses and this header for field encodings.
2. Populate ASIC-specific register tables with helper macros such as `SR`, `SF`, `FD_MASK`, and `FD_SHIFT`.
3. Use DC/DMUB register helpers such as `REG_GET`, `REG_SET`, `REG_SET_2`, `REG_UPDATE`, and `REG_UPDATE_2` to access named fields while preserving unrelated bits in packed registers.

Observed consumers include `display/dmub/src/dmub_dcn401.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/resource/dcn401/dcn401_resource.c`, `display/dc/gpio/dcn401/hw_translate_dcn401.c`, `display/dc/gpio/dcn401/hw_factory_dcn401.c`, and `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`. For example, DMCUB setup code uses fields from this chunk to reset/release DMCUB, program `DMCUB_REGION3_CW*` windows, clear inbox/outbox pointers, exchange GPINT commands, and poll scratch/pwait status. IRQ service code uses the corresponding interrupt destination/source model to map hardware events such as OTG vstartup, vline, HUBP flip, vupdate-no-lock, DMCUB outbox, HPD, and HPD RX events into `dc_irq_source` values.

## State and persistence behavior

The header itself has no mutable state and stores no persistent data. The state described by these masks lives in DCN hardware registers and persists according to display IP lifecycle: driver initialization, DMU/DMCUB boot, modeset, hotplug, runtime power management, suspend/resume, and GPU/display reset.

Important stateful areas in this chunk include:

- Interrupt destination registers. Their fields determine where hardware events are delivered; incorrect or stale routing can turn visible events into lost interrupts or unexpected IH traffic.
- Power-gating config/status and interrupt controls. Domain request/status fields and DCPG interrupt mask/clear fields are asynchronous hardware state and must be sequenced around power transitions.
- Clock/deep-sleep controls in `DMU_CLK_CNTL` and related DMU registers. These affect whether display, DMCUB, RBBMIF, LONO, and clock-stop paths remain available or can enter lower-power states.
- DMCUB firmware windows and code windows. Region offsets, base addresses, top addresses, and enable bits define which memory the microcontroller can fetch/execute/access; these are programmed during boot and reset paths and must match framebuffer address translation.
- DMCUB mailbox, GPINT, scratch, timer, fault, and interrupt registers. Many are producer/consumer state shared between host driver and firmware, with pointers and ready/done bits changing asynchronously.
- DWB frame capture, update-lock, CRC, overflow, and output-format state. These control whether writeback is running, which pixels are captured, how output is clamped/formatted, and whether overflow/backpressure events are reported.
- DWB color-processing state. Gamut-remap and OGAM RAMA/RAMB controls are banked and region-based; the active/current mode fields and LUT index/data registers imply ordering constraints when programming a curve.
- MCIF writeback buffer manager state. Buffer selection, lock, activity, next-buffer, overflow, and pitch fields describe active memory writeback buffering and can change while capture is running.

## Dependencies and integration points

- Must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`. The shift/mask file alone does not identify register addresses.
- Depends on AMDGPU Display Core register-access macros and table-generation conventions. The field names in this header are referenced indirectly through macro expansion, so renaming or deleting a field breaks build-time table generation.
- Integrates with the DCN 4.1 IRQ service through interrupt destination/source definitions for OTG, HUBP, HPD, HPD RX, DMCUB outbox, AUX/DDC, HDCP, DSC, HPO, audio, and link error paths.
- Integrates with DMUB/DMCUB firmware boot and runtime communication through region-window fields, `DMCUB_CNTL`, `DMCUB_SEC_CNTL`, `DMCUB_CNTL2`, `DMCUB_GPINT_DATAIN*`, scratch registers, inbox/outbox pointers, and host/DMCUB interrupt controls.
- Integrates with display power-management code through DMU clock gating, DMCUB/DMU clock-stop allowance, domain power-gating config/status, DCPG interrupt status/control, and LONO memory-power request controls.
- Integrates with display writeback and memory-client writeback paths through DWB frame-capture controls, color pipeline programming, CRC/overflow diagnostics, MCIF buffer-manager controls, buffer pitch, and buffer status fields.
- Shares repeated layouts with adjacent DCN generated headers such as DCN 3.2.x, DCN 3.5.x/3.6.x, and DCN 4.2.0, but this file is DCN 4.1.0-specific and should not be used as a substitute for another ASIC revision.

## Risks and edge cases

- Offset/mask drift is the primary risk. A correct mask paired with a stale offset, or a correct offset paired with a stale bit position, can silently write the wrong hardware field.
- This is a chunk boundary, not the whole header. It begins after the shift definitions for the earlier part of `DCPG_INTERRUPT_DEST2` and ends before the rest of the MCIF writeback buffer-status/register set. The final per-file report should reconcile adjacent chunks for complete register coverage.
- Many registers pack software-owned control bits beside hardware-owned status, current, pending, occurred, ack, or clear bits. Full-register writes can clobber events or status; read-modify-write helpers are expected for most fields.
- Interrupt clear/ack/mask fields are easy to confuse. Fields ending in `_ACK`, `_CLEAR`, `_MASK`, `_STATUS`, `_OCCURRED`, or `_INT_TYPE` have different semantics even when they share the same event source.
- DMCUB window fields are boot-critical. Incorrect offset-high, top-address, or enable programming can make firmware fetch from the wrong memory, hang during reset release, or fail GPINT/mailbox communication.
- DMCUB shared mailbox state can race with firmware. Pointer, ready, done, response, scratch, and GPINT fields should be accessed with the expected polling/ack protocol.
- Power-gating and clock-gating fields can break otherwise unrelated display flows if forced while a block is active. DMCUB, DWB, DMU, and domain PG controls must be coordinated with firmware, SMU, and display modeset state.
- DWB and MCIF writeback registers mix live capture, buffer management, color conversion, CRC, overflow, and update-lock state. Programming them during active capture without proper locks can cause dropped frames, stale buffers, incorrect color output, or missed overflow diagnostics.
- Repeated instance layouts invite copy/paste mistakes. OTG0-5, HUBP0-7, HDCP0-7, AUX1-6, HPD1-6, and DMCUB code windows have regular bit patterns but not all groups have identical event counts or bit positions.

## Test signals

- Build coverage with DCN 4.1.0 enabled should compile all consumers that include `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`, especially DMUB, IRQ, resource, GPIO, and clock-manager code.
- Static generated-header checks should verify every field has a consistent `__SHIFT`/`_MASK` pair and that masks align with shifts and expected widths for representative DMCUB, DCPG, DWB, and interrupt destination registers.
- IRQ tests should exercise OTG0-5 vblank/vstartup/vupdate/vline/vline2/vready/no-lock routing, HUBP flip/vblank/vline/timeout events, DMCUB outbox, HPD/HPD RX, AUX/DDC, HDCP, DSC, HPO ALPM wake, and DCIO error paths.
- DMUB boot/reset tests should validate DMCUB enable/soft-reset sequencing, secure reset release, code-window programming, inbox/outbox pointer reset, GPINT stop-response flow, scratch register exchange, fault-address capture, and host interrupt CSR ack/status behavior.
- Power-management tests should cover DMU clock-gating/deep-sleep bits, domain power-up/down request/status transitions, DCPG interrupt mask/clear paths, runtime PM, suspend/resume, and GPU reset.
- Writeback tests should cover DWB enable/disable, frame-capture window and source size programming, update-lock behavior, CRC reads, overflow interrupt ack/mask/status, backpressure counters, output format/clamp settings, and host-read throttling.
- Color pipeline tests should program gamut remap bank A/B, OGAM LUT index/data/control, RAMA/RAMB start/end/base/slope/offset values, and all 34 region descriptors, then validate captured output or CRC signatures.
- MCIF writeback tests should validate buffer-manager enable, software interrupts, slice/overrun interrupt status, software lock, address fencing, luma/chroma pitch, current/next buffer state, buffer activity/locks, overflow, and current-line reporting.
