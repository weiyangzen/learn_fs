# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 4725-7166

## Purpose

This chunk is generated AMDGPU DCN 3.0 register field metadata. It contains no executable C logic; its API is a set of preprocessor constants that describe bit positions and already-shifted masks for DCN 3.0 display, DMU/DMCUB, MMHUBBUB/writeback, HDA audio, and display performance-monitor registers.

Each field is represented by paired macros:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the positioned bit mask.

The path sits under a local `ceph-client` source mirror, but this content is AMD display-driver hardware metadata, not distributed filesystem logic.

The range starts with the tail of `DISP_INTERRUPT_STATUS_CONTINUE21`, then covers `DISP_INTERRUPT_STATUS_CONTINUE22` through `CONTINUE25`, GPU timer start-position fields, many interrupt-destination registers, the DMCUB/DMU register block, MMHUBBUB and display writeback register fields, the MMHUBBUB perfmon block, HDA/Azalia stream register fields, and the start of HDA perfmon4. It ends at the `DC_PERFMON4_PERFMON_CNTL` comment; that register's actual field definitions are in the next chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime storage objects in this range. The important surface is the generated macro namespace consumed by AMD display register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `REG_UPDATE`, `REG_READ`, `REG_WRITE`, `SF(...)`, `SRI(...)`, `DMUB_SF(...)`, and IRQ register-table helpers.

Major macro families in this chunk:

- `DISP_INTERRUPT_STATUS_CONTINUE22`, `CONTINUE23`, `CONTINUE24`, and `CONTINUE25`: packed display interrupt status continuation fields for DCPG power-domain up/down events, ABM ready/backlight-update events, OTG v-update-no-lock and DRR v-total events, DSC underflow/core-error/perfmon events, DMCUB timer/mailbox/general/fault events, MMHUBBUB warmup, and ABM2-5 events. Bit 31 continues the chained status register series until `CONTINUE25`.
- `DC_GPU_TIMER_START_POSITION_*`: per-pipe start-position selectors for vready, flip, v-update-no-lock, and flip-away GPU timer capture. Vready/v-update-no-lock cover D1-D6; flip/flip-away cover D1-D8.
- Interrupt destination registers: `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST2`, `DCPG_INTERRUPT_DEST`, `DCPG_INTERRUPT_DEST2`, `DCIO_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `DIG_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST`, `DCHUB_PERFCOUNTER_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST2`, `DPP_PERFCOUNTER_INTERRUPT_DEST`, `MPC_INTERRUPT_DEST`, `OPP_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, and `DSC_INTERRUPT_DEST`. These fields route block-specific interrupt sources to the intended interrupt destination path.
- `dce_dc_dmu_dmcub_dispdec` address block: DMCUB region offsets/top-address enables, region3 code-window base/top/offset registers for windows 0-7, DMCUB interrupt enable/ack/status/type registers, external interrupt count/id/context/ack, instruction/data fault addresses, security and memory controls, inbox/outbox base/size/read/write pointers for two mailboxes, GPINT data in/out registers, scratch0-15, timer current/trigger/window registers, processor ID, control, low-speed wake enable, and memory power control.
- `dce_dc_mmhubbub_mcif_wb0_dispdec` address block: MCIF writeback buffer manager status/SW/VCE controls, pitch, four writeback buffer status/status2 groups, luma/chroma low/high addresses, buffer resolution, arbitration, SCLK/DRAM/P-state/self-refresh controls, QoS, luma/chroma size, VMID, and minimum time-to-urgent fields.
- `dce_dc_mmhubbub_mmhubbub_dispdec` and `dce_dc_mmhubbub_vgaif_dispdec`: MMHUBBUB watermarks and warmup programming, WBIF watermark-control/misc/outstanding counters, VGA source split, memory power status/control, clock gating, soft reset, DMU interface error status, client unit IDs, warmup VMID, VGAIF MCIF latency/write-combine controls, and outstanding counters.
- `DC_PERFMON3_*`: MMHUBBUB display perfmon control, counter configuration, counted-value type, hardware stop/count-off selection, per-counter state selection, perfmon run/control/interrupt/ack fields, counter value low/high fields, and read selectors.
- `AZF0STREAM0_*` through `AZF0STREAM7_*` and `AZ_CLOCK_CNTL`: HDA/Azalia stream indirect index/data fields and Azalia clock-gating/test-clock fields.
- `DC_PERFMON4_PERFCOUNTER_CNTL`, `DC_PERFMON4_PERFCOUNTER_CNTL2`, and `DC_PERFMON4_PERFCOUNTER_STATE`: start of the HDA perfmon block, covering counter event selection, value selection, increment/run/interrupt controls, count-off fields, active status, counted-value type, hardware stop selectors, and eight counter state selectors. The following `DC_PERFMON4_PERFMON_CNTL` register is only introduced by comment at the chunk boundary.

## Control Flow

This header chunk has no control flow. It is declarative hardware layout data used by code that builds register descriptor tables and performs MMIO read-modify-write operations.

Runtime use follows this pattern:

1. DCN 3.0 display code includes `dcn_3_0_0_offset.h` for register addresses and `dcn_3_0_0_sh_mask.h` for field masks/shifts.
2. Resource, IRQ, GPIO, DMUB, clock-manager, MMHUBBUB, DWB, and audio/perfmon code expands these generated names through register-list macros.
3. IRQ code uses the interrupt status and destination fields to enable, route, report, and acknowledge display, DMU/DMCUB, OTG, DSC, DCHUB, HPD, AUX, I2C, Azalia, and perfmon events.
4. DMUB code programs DMCUB memory windows, mailbox pointers, GPINT registers, scratch registers, timers, interrupts, fault handling, and power controls.
5. MMHUBBUB/DWB code programs display writeback buffer addresses, pitch, size, resolution, buffer status/control, watermark/QoS behavior, VMID, and power/clock controls.
6. Perfmon/debug paths configure perf counters, start/stop counter collection, read low/high counter values, and clear or inspect perf counter interrupt status.

The macros do not encode sequencing. Consumers must know whether a field is read-only status, write-one-to-clear ack, sticky fault state, self-clearing request, or persistent configuration.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes MMIO-backed GPU display hardware state.

The represented hardware state includes:

- Interrupt state and routing: chained interrupt status bits, DMCUB interrupt enables/types/acks/status, destination routing for display sub-blocks, and perfmon interrupt status/ack fields.
- DMCUB firmware interface state: memory region windows and enables, mailbox base/size/read/write pointers, GPINT input/output registers, scratch registers, timers, processor/control status, fault addresses, security reset/fault-clear bits, and memory power controls.
- Display writeback and MMHUBBUB state: buffer manager status, buffer locks, active/overflow/disable/mode/tag/current-line status, luma/chroma addresses and high bits, buffer resolution, pitch, buffer sizes, VCE/SW controls, p-state/watermark/self-refresh/QoS settings, VMID, outstanding counters, warmup address/config/control, clock gates, soft reset, and memory power state.
- Timing and diagnostic state: GPU timer start-position selectors for vready/flip/v-update-no-lock/flip-away, MCIF latency/write-combine counters, perfmon counter control/state/value/interrupt fields, and MMHUBBUB/DCHUB/DPP/DSC perf counter destination fields.
- HDA/Azalia state: per-stream indirect index/data windows and clock gate/test-clock controls for the display audio block.

Persistence is hardware-defined. Configuration fields usually remain until overwritten, power-gated, reset, or reinitialized during modeset, suspend/resume, or ASIC reset. Status, ack, fault-clear, interrupt, and pointer fields are side-effect-sensitive. Names containing `*_STATUS`, `*_STAT`, `*_ACK`, `*_CLEAR`, `*_FAULT`, `*_WPTR`, `*_RPTR`, `*_ACTIVE`, `*_LOCKED`, `*_OVERRUN`, `*_PWR_STATUS`, or `*_SOFT_RESET` should be treated as requiring hardware-specific access discipline.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which supplies matching register addresses and base indices. This file supplies only the bit layouts inside those addresses.

Direct include points for `dcn_3_0_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Close consumers visible in the tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`, which binds DMCUB interrupt registers and fields through IRQ register-entry macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c` and `dmub_dcn302.c`, which use the DMCUB register contract for firmware mailbox, GPINT, interrupt, scratch, and control paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_mmhubbub.c` and `dcn30_mmhubbub.h`, which program MCIF writeback buffer addresses, high address bits, and other MMHUBBUB/DWB fields using these masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which documents interrupt source IDs that correspond to several status names in this chunk, including DMCUB mailbox events under `DISP_INTERRUPT_STATUS_CONTINUE24`.

## Risks And Edge Cases

- These macros are a hardware ABI. Wrong masks or shifts compile successfully but can route interrupts incorrectly, miss acknowledgements, corrupt mailbox pointers, program wrong DMCUB memory windows, break display writeback, or produce misleading perf counter reads.
- The chunk boundaries are artificial. The first lines are only the tail of `DISP_INTERRUPT_STATUS_CONTINUE21`, and the last line is only the `DC_PERFMON4_PERFMON_CNTL` comment before that register's field definitions.
- Repeated fields create copy-drift risk. OTG0-5, AZF0STREAM0-7, MCIF writeback buffers 1-4, DMCUB region3 code windows 0-7, ABM2-5, DSC0-5, DPP0-7, HUBP0-7, and perf counter 0-7 fields are highly similar but not always semantically interchangeable.
- Packed interrupt registers require read-modify-write and ack discipline. Full-register writes to destination, enable, status, type, or ack registers can affect unrelated interrupt sources in the same word.
- DMCUB region and mailbox fields are firmware-interface critical. Bad base, top, offset, size, `WPTR`, or `RPTR` masks can hang DMUB communication, fault instruction/data fetches, or cause firmware-visible memory corruption.
- Fault and security fields are side-effect-sensitive. Misusing `DMCUB_SEC_RESET`, fault clear bits, fault address reads, or data fault interrupt disables can hide real firmware/memory bugs or leave the block wedged after a fault.
- Writeback address fields are split into low/high luma/chroma addresses. Mixing buffers, planes, or high-bit fields can write captured frames to the wrong memory, corrupt output, or violate VMID/protection expectations.
- Watermark, QoS, P-state, self-refresh, and clock-gating fields are workload-sensitive. Bad masks can appear only under high resolution, high refresh, display writeback, low memory-clock, suspend/resume, or multi-display stress.
- Destination fields do not by themselves define interrupt source IDs or Linux IRQ handlers. The driver must keep routing bits, source ID tables, enable/ack registers, and handler expectations aligned.

## Test Signals

Useful validation is compile-time plus hardware behavior:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.0.2 support; missing or renamed macros should fail at include sites and in generated IRQ, DMUB, GPIO, clock, resource, MMHUBBUB, and DWB register tables.
- Diff this generated chunk against AMD's DCN 3.0 register database and the adjacent `dcn_3_0_0_offset.h` addresses to catch shifted fields, stale masks, or instance drift.
- Exercise DCN 3.0 hardware with hotplug, modeset, vblank, page flip, DRR, vstartup/vready, v-update-no-lock, DSC, ABM, AUX, I2C/DDC, HPD, and Azalia audio interrupt activity. Watch for missed IRQs, IRQ storms, and wrong destination routing.
- Stress DMUB communication: firmware boot, inbox/outbox messages, GPINTs, scratch access, timers, suspend/resume, fault injection where available, and recovery after undefined-address or instruction/data fault events.
- Test display writeback through `dcn30_mmhubbub`: program all four buffers, luma/chroma addresses, high address bits, resolution, pitch, buffer locking, VCE/SW ownership, overflow/overrun reporting, and VMID behavior.
- Run bandwidth and power-state stress with writeback enabled: memory-clock changes, NB p-state changes, watermark updates, self-refresh, clock gating, MMHUBBUB warmup, and low-power transitions. Watch for underflow, stale frames, corruption, and resume failures.
- Use perfmon/debug tooling to configure `DC_PERFMON3` and the visible portion of `DC_PERFMON4`, start/stop counters, read low/high values, and verify interrupt status/ack behavior.

## Cross-Chunk Notes

Adjacent earlier chunks define the beginning of `DISP_INTERRUPT_STATUS_CONTINUE21`; this chunk starts at its final mask lines. Adjacent later chunks define the actual `DC_PERFMON4_PERFMON_CNTL` fields and the rest of the HDA perfmon4 block. The final per-file research document should merge these boundaries before making complete claims about either register family.
