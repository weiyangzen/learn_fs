# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h - subset-b-002059

## Scope

- Chunk id: `subset-b-002059`
- Source lines: 6598-8815
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h`
- Observed content: 2,218 lines, all `#define` entries, with 1,117 `__SHIFT` macros and 1,118 `_MASK` macros.

This chunk is part of the generated AMD DCN 3.5.0 register shift/mask header. It does not define executable C logic. Instead, it publishes bit positions and masks for display clock generation, audio codec control, display performance monitoring, display power gating, DMU/DMCUB-facing clock control, and display interrupt status registers. Runtime DCN code pairs these field constants with matching address macros from `dcn_3_5_0_offset.h` through AMD display register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, and `REG_WAIT`.

## Purpose

The purpose of this slice is to describe hardware register fields for several DCN 3.5 display subsystems:

- DCCG pixel clock and DTO programming for OTG instances, DP DTOs, DPPCLK DTOs, DTBCLK DTOs, DSCCLK DTOs, HDMI stream/character clocks, SYMCLK enables, DCCG soft reset, clock-gating delay controls, audio DTO source selection, and vsync counter controls.
- Azalia/HD-audio codec function, converter, pin, and input-pin controls for HDMI/DP audio capabilities, stream format, channel allocation, channel status, HBR, multichannel enable/mute/channel id, LPIB snapshots, unsolicited responses, configuration defaults, audio descriptors, sink info, and audio format-change status.
- DC performance monitor blocks `DC_PERFMON0`, `DC_PERFMON1`, and `DC_PERFMON2`, including counter control, count mode/window selection, counter state, interrupt mode, current values, and high/low latched values.
- Display power and management fields, including `CC_DC_PIPE_DIS`, `DOMAIN{0,1,2,3,16,17,18,19}_PG_CONFIG`, matching `DOMAIN*_PG_STATUS`, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_1`, `DC_IP_REQUEST_CNTL`, `SMU_INTERRUPT_CONTROL`, `DMU_CLK_CNTL`, and `DMU_MISC_ALLOW_DS_FORCE`.
- Z-state/ZSC fields (`ZSC_CNTL`, `ZSC_CNTL2`, `ZSC_STATUS`) for display idle/power-state coordination.
- Display interrupt status continuation registers from the base `DISP_INTERRUPT_STATUS` chain through the beginning of `DISP_INTERRUPT_STATUS_CONTINUE19`, covering OTG, HUBP, DWB, DMCUB, DMCUB outbox, DCHUBBUB, DSC, DIO/DCIO, DCPG, OPP, OPTC, MMHUBBUB, Azalia, and DIGG interrupt sources.

Driver code should not hard-code the numeric values in this header. These generated names form the field-layout contract between the ASIC register database and the display driver.

## Important APIs, Types, and Macros

There are no functions, structs, enums, or mutable declarations in this chunk. Its public interface is a generated macro namespace with names of the form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.

Important macro families include:

- Pixel and link clocks: `OTG1_PIXEL_RATE_CNTL` tail masks, complete `OTG2_PIXEL_RATE_CNTL` and `OTG3_PIXEL_RATE_CNTL`, `DP_DTO{1,2,3}_PHASE`, `DP_DTO{1,2,3}_MODULO`, `OTG{1,2,3}_PHYPLL_PIXEL_RATE_CNTL`, `DENTIST_DISPCLK_CNTL`, `DPPCLK_DTO_CTRL`, `DPPCLK{0..3}_DTO_PARAM`, `DTBCLK_DTO{0..3}_{PHASE,MODULO}`, `DTBCLK_DTO_DBUF_EN`, `DSCCLK_DTO_CTRL`, `HDMISTREAMCLK_CNTL`, `HDMISTREAMCLK0_DTO_PARAM`, and `HDMICHARCLK0_CLOCK_CNTL`.
- DCCG reset, gating, and timing: `DPPCLK_CGTT_BLK_CTRL_REG`, `DCCG_CAC_STATUS2`, `SYMCLK{A..E}_CLOCK_ENABLE`, `DCCG_SOFT_RESET`, `DCCG_GATE_DISABLE_CNTL3`, `FORCE_SYMCLK_DISABLE`, `DCCG_VSYNC_CNT_CTRL`, `DCCG_VSYNC_CNT_INT_CTRL`, and `DCCG_VSYNC_OTG{0..5}_LATCH_VALUE`.
- Audio DTO routing: `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO{0,1}_{PHASE,MODULE}`, and `DCCG_AUDIO_DTBCLK_DTO_{PHASE,MODULO}`. The source register includes DTO source selection and 512-FBR DTO selection fields for DTO0/1/2 and audio DTBCLK.
- Azalia codec function and converter fields: `AZALIA_F2_CODEC_ROOT_PARAMETER_*`, `AZALIA_F2_CODEC_FUNCTION_PARAMETER_*`, `AZALIA_F2_CODEC_FUNCTION_CONTROL_*`, `AZALIA_F2_CODEC_CONVERTER_PARAMETER_*`, `AZALIA_F2_CODEC_CONVERTER_CONTROL_*`, `AZALIA_F2_CODEC_CONVERTER_STRIPE_CONTROL`, and `AZALIA_F2_CODEC_CONVERTER_CONTROL_GTC_EMBEDDING`.
- Azalia pin/output audio fields: `AZALIA_F2_CODEC_PIN_PARAMETER_*`, `AZALIA_F2_CODEC_PIN_CONTROL_RESPONSE_*`, `AZALIA_F2_CODEC_PIN_CONTROL_WIDGET_CONTROL`, `CHANNEL_ALLOCATION`, `AUDIO_DESCRIPTOR`, `AUDIO_DESCRIPTOR_DATA`, `HBR`, `MULTICHANNEL*`, `LIPSYNC`, `AUDIO_SINK_INFO_*`, `DIGITAL_OUTPUT_STATUS`, `LPIB*`, `CODING_TYPE`, `FORMAT_CHANGED`, `WIRELESS_DISPLAY_IDENTIFICATION`, `REMOTE_KEEPALIVE`, `DOWN_MIX_INFO`, and pin association fields.
- Azalia input-pin/input-converter fields: `AZALIA_F2_CODEC_INPUT_PIN_PARAMETER_*`, `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_*`, `AZALIA_F2_CODEC_INPUT_CONVERTER_PARAMETER_*`, and `AZALIA_F2_CODEC_INPUT_CONVERTER_CONTROL_*`, covering input widget capabilities, multichannel controls, LPIB snapshots, stream format, and channel stream id.
- Display power and DMU fields: `CC_DC_PIPE_DIS`, `DOMAIN*_PG_CONFIG`, `DOMAIN*_PG_STATUS`, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_1`, `DC_IP_REQUEST_CNTL`, `SMU_INTERRUPT_CONTROL`, `DMU_CLK_CNTL`, and `DMU_MISC_ALLOW_DS_FORCE`.
- Performance monitor fields: `DC_PERFMON{0,1,2}_PERFMON_CNTL`, `*_PERFMON_CNTL2`, `*_PERFMON_LOW`, `*_PERFMON_HI`, `*_PERFMON_CVALUE_LOW`, `*_PERFMON_CVALUE_INT_MISC`, `*_PERFCOUNTER_CNTL`, `*_PERFCOUNTER_CNTL2`, and `*_PERFCOUNTER_STATE`.
- Interrupt status chain: `DISP_INTERRUPT_STATUS`, `DISP_INTERRUPT_STATUS_CONTINUE`, and `DISP_INTERRUPT_STATUS_CONTINUE2` through `DISP_INTERRUPT_STATUS_CONTINUE19`. The fields cover vertical blank/line/update/trigger events, HPD and HPD RX events, AUX/DDC/I2C/DIO events, DWB and DMCUB events, DCHUBBUB/DSC events, HUBP perfmon/IHC events, flip/flip-away events, DCIO DPCS errors, DCPG domain power-down events, Azalia endpoint audio events, and the first DIGG DP events in continue19.

## Control Flow

This header chunk has no local control flow. Runtime behavior comes from code that consumes these constants:

1. DCN 3.5 resource and block files include `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Resource initialization builds per-block register, shift, and mask tables. Observed consumers include `display/dc/resource/dcn35/dcn35_resource.c`, `display/dc/irq/dcn35/irq_service_dcn35.c`, and `display/dmub/src/dmub_dcn35.c`.
3. Block helpers pass those tables into DCCG, clock manager, audio, interrupt, DMUB, power-gating, and hardware-sequencer code.
4. The driver performs read-modify-write, poll, clear, and ack operations through the register helpers. The helper resolves a register address from the offset header and field positions/masks from this header.
5. Hardware then performs the actual state transition: selecting an OTG pixel-rate source, enabling a DTO, changing a DENTIST divider, routing audio DTOs, enabling/disabling a clock gate, servicing a power-domain request, reading a perf counter, acknowledging a status bit, or exposing an interrupt in the chained display status registers.

Common hardware flow idioms in this chunk include enable/status pairs (`DPDTO*_ENABLE_STATUS`, `DTBCLKDTO*_ENABLE_STATUS`), phase/modulo DTO programming, DENTIST write-divider plus change-done polling, soft-reset bits, power-gate request/status pairs, interrupt status/continue chains, perfmon start/stop/count-state fields, Azalia unsolicited-response and format-change response fields, and action-style interrupt clear or mask fields in DCPG interrupt control.

## State and Persistence Behavior

The macros themselves are compile-time constants and retain no state. They describe MMIO fields whose values are stored in DCN hardware registers.

Persistent or semi-persistent configuration state includes DTO phase/modulo values, OTG pixel-rate sources, PHYPLL pixel-rate source selection, DPPCLK/DSCCLK/DTBCLK enable and double-buffer controls, DCCG audio DTO source selections, SYMCLK source/enable fields, clock-gate disable overrides, DENTIST divider values, Azalia function/pin/converter configuration defaults, stream formats, channel allocation, multichannel enable/mute/channel ids, HBR enable, audio descriptors, power-domain force/gate settings, DMU clock-gate controls, and ZSC control values. These values generally remain programmed until the driver rewrites them or hardware reset clears them.

Transient and latched state includes DTO enable status, DIO FIFO error bits and error counters, DENTIST change-done bits, DCCG CAC status, DCCG vsync latch values, DCPG interrupt status, power-domain FSM status, DC perfmon counter current values and overflow/interrupt status, Azalia format-changed/enable/disable events, LPIB snapshots, ZSC status, and every `DISP_INTERRUPT_STATUS*` bit. Status, ack, clear, and interrupt-control fields must be treated according to their hardware semantics rather than as ordinary retained configuration.

Several fields are sensitive to ordering. DTO phase/modulo and enable bits must be programmed consistently with clock source selection. DENTIST divider changes are normally followed by polling `*_CHG_DONE`. Power-domain control fields are paired with status fields and can hang or power down an active block if used out of sequence. Interrupt status chains use continuation bits, so a reader must traverse the chain rather than treating a single register as complete coverage.

## Dependencies

This generated namespace depends on:

- Matching DCN 3.5.0 register addresses from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`.
- AMD display register-helper conventions, including `SR`, `SRI`, `SF`, `DCCG_SF`, `DCCG_SFI`, `HWS_SF`, `DMUB_SR`, `DMUB_SF`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and `REG_WAIT`.
- DCN 3.5 resource initialization in `display/dc/resource/dcn35/dcn35_resource.c`, which includes this header and wires its fields into block register tables.
- DCCG and clock-manager code such as `display/dc/dccg/dcn35/dcn35_dccg.[ch]`, `display/dc/dccg/dcn32/dcn32_dccg.[ch]`, and `display/dc/clk_mgr/dcn35/dcn35_clk_mgr.c`, which consume DCCG/DENTIST/DTO fields directly or via inherited macro lists.
- Audio support in `display/dc/dce/dce_audio.[ch]`, which consumes DCCG audio DTO source fields and Azalia endpoint access helpers.
- DMUB support in `display/dmub/src/dmub_dcn35.[ch]`, which consumes `DMU_CLK_CNTL` fields.
- Interrupt service code in `display/dc/irq/dcn35/irq_service_dcn35.c` plus source-id definitions such as `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which map status-register fields to driver interrupt sources.
- Power-gating and hardware sequencing code, including DCN family resource tables and later `pg` controllers, which use `DOMAIN*_PG_*`, `DCPG_INTERRUPT_*`, and `DC_IP_REQUEST_CNTL` style fields.

Correctness is tied to the ASIC register database that generated this file. Manual edits to numeric shifts or masks without a matching hardware definition change would silently corrupt MMIO programming.

## Integration Points

DCCG and clock-manager integration is the most direct. `dcn35_dccg.c` updates `DCCG_GATE_DISABLE_CNTL3` for DP stream and SYMCLK root/leaf gating, reads and writes `DENTIST_DISPCLK_CNTL`, waits for `DENTIST_DISPCLK_CHG_DONE`, and relies on DPPCLK DTO field arrays built from `DPPCLK_DTO_CTRL` and `DPPCLK*_DTO_PARAM`. `dcn35_clk_mgr.c` also carries local DENTIST definitions and uses the same hardware semantics for divider changes.

Audio integration spans both DCCG and Azalia. `dce_audio.[ch]` uses `DCCG_AUDIO_DTO_SOURCE` fields to choose DTO sources and 512-FBR DTO behavior. The Azalia F2 codec field set in this chunk describes the hardware endpoint registers used for audio capabilities, ELD-like sink data, stream format, channel status/allocation, HBR, multichannel layout, LPIB snapshots, and unsolicited/format-change events. Display link and audio enable paths depend on these fields matching the endpoint register model.

Interrupt integration is through `irq_service_dcn35.c` and IRQ source tables. The `DISP_INTERRUPT_STATUS*` continuation chain exposes many event domains: OTG timing events, HPD/HPD RX, AUX/I2C/DDC, DIO/DCIO, DWB, DMCUB, DCHUBBUB, DSC, HUBP, OPP, OPTC, MMHUBBUB, DCPG, Azalia endpoint, and DIGG DP status. The continuation bits (`DISP_INTERRUPT_STATUS_CONTINUE*`) are part of the chain walk and must remain aligned.

DMUB and DMU integration appears in `dmub_dcn35.c`, where `DMU_CLK_CNTL` gate-disable fields are updated for display, SoC, and DMCUB clocks. The `SMU_INTERRUPT_CONTROL`, `DMU_MISC_ALLOW_DS_FORCE`, and `DC_IP_REQUEST_CNTL` fields are part of the broader display/SMU/DMUB coordination surface.

Power-gating integration is shared with hardware sequencing and per-generation PG controllers. `DOMAIN0..3` and `DOMAIN16..19` config/status fields encode force-on, gate request, desired power state, and PGFSM status for display domains. `DCPG_INTERRUPT_STATUS*` and `DCPG_INTERRUPT_CONTROL_1` provide interrupt visibility and masking/clearing for domain power-down and miscellaneous PG events.

Performance monitoring integration is diagnostic and profiling oriented. The three `DC_PERFMON` instances expose counter selection, count modes, windowing, overflow/interrupt behavior, current value reads, and state transitions. These fields are typically exercised by debug/perf tooling rather than the steady-state modeset path.

## Risks and Edge Cases

- This is generated register metadata. A one-bit shift or mask error can program the wrong clock source, route audio to the wrong DTO, misread a power-domain state, lose an interrupt, or corrupt performance counter reads.
- The chunk begins in the middle of `OTG1_PIXEL_RATE_CNTL`; its early shifts and some masks are in the previous chunk. It ends inside `DISP_INTERRUPT_STATUS_CONTINUE19` after `DIGG_DP_FAST_TRAINING_COMPLETE_INTERRUPT__SHIFT`; the remaining continue19 masks and later continue registers are in the next chunk.
- DCCG clock fields are timing-sensitive. Incorrect DTO phase/modulo, double-buffer enable, or DENTIST divider fields can cause display underflow, pixel-rate mismatch, or waits that never observe change-done.
- Several clock-gating fields are override-style controls. Accidentally forcing gates disabled or enabled can increase power, break link clocks, or hide idle-power regressions.
- `DCCG_SOFT_RESET` contains many reset bits for refclk, DVO, audio DTO, DP refclk, AMCLK, and PLL config interfaces. Treating reset fields like ordinary state bits can glitch active clocks or leave blocks in reset.
- Azalia codec fields mix capability, control, status, and response registers with similar names. Confusing response/configuration-default/status fields can advertise wrong audio capabilities or mishandle format-change/unsolicited-response events.
- LPIB and audio timer snapshot fields are latched runtime values. Readers must account for snapshot locking and wrap count rather than assuming an always-current linear counter.
- Power-gate request/status pairs can be racy around suspend/resume, idle entry, and DMCUB-driven sequencing. Polling the wrong `DOMAIN*_PG_STATUS` field or using the wrong expected value can cause timeouts or premature access to a powered-down block.
- The interrupt status continuation chain is easy to truncate. Missing a continuation bit or mapping a field to the wrong source id can lose interrupts or create unhandled interrupt storms.
- DCIO/DPCS, DCPG power-down, DMCUB outbox, HUBP IHC timeout, and Azalia endpoint interrupts are often error or state-transition signals. Incorrect masks can make failures appear as display hangs without a useful interrupt trail.
- Perfmon control and state fields are shared diagnostic resources. Incorrect counter selection or clear/overflow handling can produce misleading performance data.

## Test Signals

Useful validation signals for this chunk include:

- DCN 3.5 display build coverage that compiles `dcn35_resource.c`, `irq_service_dcn35.c`, `dmub_dcn35.c`, `dcn35_dccg.c`, and the DCN 3.5 clock manager against this generated header.
- Generated-header consistency checks that every consumed `SF(..., field, __SHIFT)` has a matching `_MASK`, that masks align with shifts, and that field widths match the register database.
- Modeset tests across multiple pipes and links that exercise OTG pixel-rate selection, DP DTO enable/status, DPPCLK DTO phase/modulo programming, DENTIST divider changes, and clock-gating debug state.
- Audio validation over HDMI and DP with format changes, HBR, multichannel layouts, channel allocation/status, LPIB snapshot reads, endpoint enable/disable events, and audio DTO source changes.
- Hotplug, AUX/DDC/I2C, DIO/DCIO error, Azalia endpoint, DMCUB outbox, DWB, DSC, HUBP, OPP, OPTC, and OTG interrupt tests that confirm the status continuation chain and source-id mappings are correct.
- Suspend/resume and idle-power tests covering `DOMAIN*_PG_CONFIG`, `DOMAIN*_PG_STATUS`, `DCPG_INTERRUPT_*`, `DMU_CLK_CNTL`, `DMU_MISC_ALLOW_DS_FORCE`, `SMU_INTERRUPT_CONTROL`, and ZSC status.
- Perfmon/debug tooling tests that start, stop, clear, and read `DC_PERFMON0..2` counters and verify overflow/interrupt state handling.
- Register-dump comparison against known-good DCN 3.5 hardware after boot, modeset, audio enable, power-gate transitions, and interrupt events.

## Chunk Boundary Notes

Line 6598 starts after the beginning of `OTG1_PIXEL_RATE_CNTL`; the previous chunk contains the missing `OTG1_PIXEL_RATE_CNTL` shifts and first masks. Line 8815 stops inside `DISP_INTERRUPT_STATUS_CONTINUE19`; the next chunk contains the remaining fields and masks for that register and subsequent interrupt status continuation registers. The merge lane should combine adjacent chunk documents before making file-level conclusions about those boundary register blocks.
