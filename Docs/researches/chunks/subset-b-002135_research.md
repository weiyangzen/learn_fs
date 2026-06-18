# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 42167-44553

## Purpose

This chunk is a generated shift/mask register-field slice for AMD DCN 3.6.0 display hardware. It contains no executable C functions or declared C types; its interface is a set of `#define` constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. Consumers combine these constants with `dcn_3_6_0_offset.h` and AMDGPU Display Core register helpers such as `FD_MASK`, `FD_SHIFT`, `REG_SET`, `REG_UPDATE`, and register-list macros.

The covered lines span the tail of the DisplayPort AUX2 block, complete AUX3 and AUX4 blocks, DPIA mux controls, the DOUT I2C/DDC engine, DIO miscellaneous power/clock/link-routing controls, DIG stream mapper controls, a DC perfmon instance, DCIO/UNIPHY routing and reset controls, and GPIO/DDC pad mask/value/enable/readback definitions through the start of GENLK GPIO fields.

## Important APIs and register groups

- `DP_AUX2_*`, `DP_AUX3_*`, and `DP_AUX4_*` define AUX channel register fields for software AUX transactions, link-service reads, arbitration between SW and DMCU/firmware users, interrupt status/ack/mask bits, data FIFO/index access, DPHY TX/RX timing/status, GTC sync control/error/status, and AUX PHY wake handshakes. AUX2 begins mid-block at `AUX_ARB_CONTROL` masks and continues through PHY wake; AUX3 and AUX4 are complete in this chunk.
- `DP_AUX*_AUX_CONTROL` fields enable/reset the AUX block, select HPD, allow link-service reads, control HPD-disconnect behavior, enable mode detection, request impedance calibration, and enable deglitch/test behavior.
- `DP_AUX*_AUX_SW_STATUS`, `AUX_LS_STATUS`, and `AUX_GTC_SYNC_STATUS` are dense status bitmaps for done/request state, receive timeout and overflow, HPD disconnect, partial/invalid byte framing, invalid start/stop/sync/receptacle conditions, reply byte count, NACK, CP IRQ, update ack, and GTC master request by RX.
- `DIO_DPIA_MUX0_DIO_DPIA_MUX_CONTROL` through `DIO_DPIA_MUX3_DIO_DPIA_MUX_CONTROL` expose enable/reset and `DIG_DP_SOURCE_SELECT` fields for routing USB4/DisplayPort-in-Alt-mode input adapter streams to DIG DP sources.
- `DC_I2C_*` defines the DOUT I2C engine: transaction launch/reset/DDC select/count, arbitration and abort controls, software and per-DDC hardware interrupt bits, SW status/NACK/timeout/overflow fields, DDC1-DDC5 hardware EDID detect status, per-DDC speed/setup timing fields, transaction descriptor fields, data read/write/index fields, EDID detect control, and read-request interrupt status/ack/mask fields.
- `DIO_DCN_STATUS`, `DIO_SCRATCH0` through `DIO_SCRATCH7`, `DIO_DP_ALPM_WAKEUP_INTERRUPT_STATUS`, `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, and `DIO_MEM_PWR_CTRL2` cover DIO status/scratch state, DP ALPM wake interrupts, and light-sleep status/force/disable controls for I2C and DPA-DPG memory slices.
- `DIO_CLK_CNTL`, `DIO_POWER_MANAGEMENT_CNTL`, `DIO_HDMI_RXSTATUS_TIMER_CONTROL`, `DIO_PSP_INTERRUPT_STATUS`, `DIO_PSP_INTERRUPT_CLEAR`, and `DIO_STATUS` provide clock-gating overrides, DIO power-management reset/busy status, HDMI RX status timer control, PSP interrupt message/status/clear bits, and top-level DIO enable readback.
- `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL` select encoder type and HPO HDMI/DP encoder mapping for each DIO link. `DIG0_STREAM_MAPPER_CONTROL` through `DIG4_STREAM_MAPPER_CONTROL` select the link target for each DIG stream.
- `DC_PERFMON18_*` defines one display perfmon block: event selection, counted-value selection, increment/run/interrupt modes, counter state selection for counters 0-7, perfmon run-control and count-off interrupt controls, current value high/low readback, and per-counter interrupt status/ack fields.
- `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, `UNIPHYA/B/C_LINK_CNTL`, `UNIPHYA/B/C/D/E_CHANNEL_XBAR_CNTL`, `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `DCIO_SPARE`, `INTERCEPT_STATE`, `DCIO_PATTERN_GEN_*`, `DCIO_GSL_*_PAD_CNTL`, and `DCIO_SOFT_RESET` cover generic DCIO muxing, reference clock output selection, UNIPHY lane polarity and channel crossbar routing, write-command delay, pinstrap readback, spare bits, pattern-generation control, genlock/swaplock pad control, and soft resets for individual UNIPHY/DPCS/DPIA/DIO components.
- `DC_GPIO_GENERIC_*` and `DC_GPIO_DDC1_*` through `DC_GPIO_DDCVGA_*` define GPIO mask, output value (`_A`), output enable (`_EN`), and input/readback (`_Y`) fields. DDC mask fields include clock/data masks, pull-down enables, receive enables, AUX pad mode, AUX polarity, hardware pull-down permission, and drive-strength fields.

## Control flow and usage model

There is no local control flow. These generated constants are compile-time data for ASIC-specific register tables:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` for register addresses and this header for field layout.
2. Register-list macros such as `SR`, `SRI`, `SF`, `HWS_SF`, `DMUB_SF`, AUX/I2C engine macros, IRQ-entry macros, and GPIO translation code populate register, mask, and shift structs.
3. Runtime code uses those structs through register helpers to program MMIO fields without spelling the bit positions in handwritten code.

Direct DCN 3.6 users include `display/dmub/src/dmub_dcn36.c`, which initializes DMUB register offsets/masks/shifts from this header; `display/dc/resource/dcn36/dcn36_resource.c`, which builds AUX, I2C, DIO, HWSEQ, and resource register tables; and `display/dc/irq/dcn36/irq_service_dcn36.c`, which creates HPD, HPD RX, I2C, DP sink, GPIO pad, underflow, vupdate/vblank/vline, and DMUB outbox interrupt source entries using generated fields.

## State and persistence behavior

The header itself has no mutable state. The state lives in DCN 3.6 MMIO registers and persists according to display hardware lifecycle: boot-time resource construction, link bring-up, modeset, AUX/DDC transactions, runtime power management, suspend/resume, GPU reset, and display IP reset.

Several hardware groups in this chunk are explicitly stateful:

- AUX software and link-service transactions maintain request/done bits, FIFO indices, reply byte counts, DPHY timing/status, arbitration ownership, interrupt ack/mask state, GTC sync lock/error state, and PHY wake handshakes.
- I2C/DDC state includes transaction descriptors, data indices, selected DDC line, SW and hardware transfer status, EDID detect status/state/valid tries, per-DDC timing/prescale/setup values, aborts, reset bits, and read-request interrupt latches.
- DIO memory, clock, and power fields persist low-power policy and clock-gating overrides. These values are touched by HWSEQ/DIO resource code and can affect whether I2C, DP, and link memories enter light sleep.
- DIO link and stream-mapper fields determine which encoder/link path is active for a given stream, including HPO DP/HDMI selections and DIG-to-link targets.
- DCIO/UNIPHY fields persist lane inversion, lane crossbar sources, DOUT PHY channel enables, soft-reset bits, pattern generation, genlock/swaplock pad selection, and pinstrap/spare state.
- GPIO/DDC fields persist pad mode, drive strength, pull-down, output enable, output value, and readback routing for DDC and generic GPIO pins. These are shared with DDC/AUX discovery paths and GPIO translation helpers.

## Dependencies and integration points

- Requires the matching `dcn_3_6_0_offset.h`. The mask/shift symbols are only correct when paired with the same generated offset file and base-index definitions.
- Depends on the AMD Display Core register helper layer to interpret field names through `FD_MASK`/`FD_SHIFT` and read-modify-write helpers. Misspelled or stale fields generally fail at compile time; stale masks paired with valid but wrong offsets can compile and misprogram hardware.
- Integrates with DCN 3.6 resource construction in `dcn36_resource.c`: `aux_engine_regs_init(1..4)` maps AUX engines for raw AUX and DMUB AUX transfers, `i2c_inst_regs_init(1..5)` maps DDC/I2C engines, `DIO_MASK_SH_LIST` includes `DIO_MEM_PWR_CTRL__I2C_LIGHT_SLEEP_FORCE`, and `dcn36_get_preferred_eng_id_dpia()` ties DPIA routing policy to DIG encoder choices.
- Integrates with `dce_aux.c` transaction flow: acquire the AUX engine, submit the request, poll status, read reply bytes, and release the engine. The AUX status, data, interrupt, arbitration, and timeout fields in this chunk are the hardware-side representation of that flow.
- Integrates with DC I2C/DDC and link detection through the DDC service and I2C hardware engine. The `DC_I2C_*` fields encode transaction count/type/stop/start, data bytes, NACK status, timeout, and EDID detection used by monitor detection and EDID reads.
- Integrates with GPIO translation code such as `gpio/dcn32/hw_translate_dcn32.c`, where DDC line offsets (`DC_GPIO_DDC1_A` through `DC_GPIO_DDCVGA_A`) and `*_CLK_A`/`*_DATA_A` masks map logical GPIO IDs to hardware pins.
- Integrates with DIO link encoder, stream encoder, HPO encoder, and link management code through UNIPHY transmitters, DIG stream targets, `DIO_LINK*` encoder selection fields, and `DIO_DPIA_MUX*` controls.
- Integrates with DCN 3.6 IRQ service through I2C done bits, HPD/HPD RX paths, DP sink interrupts, GPIO pad interrupts, and display timing interrupts. This chunk includes I2C interrupt bit layouts and AUX interrupt controls relevant to those sources.
- Integrates with diagnostics/performance tooling through `DC_PERFMON18_*`, which exposes event selection, counter state, current-value readback, and interrupt/ack state.

## Risks and edge cases

- Generated-header drift is the primary risk. `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h` must be regenerated and consumed as a pair; otherwise valid-looking constants can target wrong registers or fields.
- AUX2 starts mid-block in this chunk and GENLK GPIO ends mid-block at the chunk boundary. Whole-file analysis must reconcile adjacent chunks before making complete claims about those blocks.
- AUX and I2C fields mix controls, latched status, interrupt acks, masks, and readback-only fields. Treating status/ack fields as ordinary controls can clear diagnostics, drop interrupts, or leave transfer state inconsistent.
- Arbitration fields are shared between SW and firmware/DMCU users. Incorrect sequencing around `*_USE_*_REG_REQ`, pending aliases, and `*_DONE_USING_*` can deadlock or race AUX/I2C ownership.
- FIFO/index fields such as AUX data indices and I2C data indices are narrow and often auto-incremented. Incorrect index, byte count, or autoincrement behavior can corrupt transaction payloads or read stale reply bytes.
- Per-instance repetition is easy to misuse: AUX2/3/4, DDC1-DDC5, DIO_LINKA-F, DPIA_MUX0-3, DIG0-4, UNIPHY A-E, and DDC GPIO lines have similar field layouts but different hardware instances.
- Power/clock fields can cause hangs or power regressions if altered outside expected display sequencing. DIO light-sleep force/disable, memory power force bits, DIO clock-gating disables, and soft resets are especially sensitive.
- Link-routing fields can silently miswire display output paths. Wrong `DIG_DP_SOURCE_SELECT`, `DIG_STREAM_LINK_TARGET`, `ENC_TYPE_SEL`, HPO encoder selection, UNIPHY xbar source, or lane inversion can look like AUX failures, link training failures, no display, or lane polarity issues.
- DDC GPIO mask and pad-mode fields share physical pins with AUX/DDC behavior. Incorrect AUX pad mode, polarity, drive strength, pull-down, or output enable can break EDID reads or hotplug behavior.
- Perfmon fields expose state and interrupt bits for one counter instance. Incorrect event selection or ack handling can make performance/debug data misleading or generate unexpected interrupts.

## Test signals

- Build DCN 3.6 display code with this header and its matching offset header included by `dmub_dcn36.c`, `dcn36_resource.c`, and `irq_service_dcn36.c`.
- Static checks should compare repeated field layouts across AUX3/AUX4, DDC1-DDC5 speed/setup/status, DIO link A-F, DIG0-4 stream mapper, and DDC GPIO1-5/VGA groups where hardware intends identical structure.
- AUX validation should cover native DP AUX reads/writes, I2C-over-AUX, defer/retry paths, timeout handling, HPD-disconnect handling, invalid reply paths, GTC sync status/error reporting, and DMUB-routed AUX transfers.
- I2C/DDC validation should cover EDID reads on DDC1-DDC5 and VGA, SW and hardware done interrupts, NACK reporting, timeout/abort/reset paths, transaction descriptors 0-3, data FIFO indexing, and EDID detect state.
- Link bring-up tests should cover DPIA mux paths 0-3, preferred DIG encoder choices for DPIA, DIO link A-F encoder selection, DIG stream mapper targets, HPO DP/HDMI paths, and UNIPHY lane crossbar/inversion behavior.
- Power-management tests should exercise DIO memory light sleep, DP ALPM wake interrupts, clock gating overrides, HDMI RX status timer behavior, suspend/resume, display idle, and GPU/display reset paths.
- GPIO tests should verify DDC clock/data output/readback/enable mapping, AUX pad mode/polarity, drive strength, pull-down behavior, generic GPIO mapping, and hotplug/DDC behavior on all exposed physical DDC lines.
- Diagnostics should include register dumps for `DP_AUX*_AUX_SW_STATUS`, `DP_AUX*_AUX_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, `DC_I2C_DDC*_HW_STATUS`, `DIO_MEM_PWR_STATUS`, `DIO_LINK*_CNTL`, `DIG*_STREAM_MAPPER_CONTROL`, `UNIPHY*_CHANNEL_XBAR_CNTL`, and `DC_GPIO_DDC*_MASK` when investigating link training, EDID, AUX, power, or routing failures.
