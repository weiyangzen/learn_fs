# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 8804-11021

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata. It contains no executable C logic; it publishes `#define` constants that describe bit shifts and bit masks for fields inside DCN 3.5.1 display registers. The companion `dcn_3_5_1_offset.h` file supplies register addresses and base indices, while this file supplies field layout for register read/modify/write helpers.

The assigned range covers a broad middle slice of display interrupt routing/status, DMUB/DMCUB control and mailbox registers, display writeback and MMHUBBUB controls, DC perfmon instance 3, Azalia audio stream windows, Azalia clock control, and the beginning of DC perfmon instance 4. Although the repository path is under a local `ceph-client` source mirror, this is AMDGPU display-driver hardware metadata and is unrelated to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, or locks in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- Repeated instance prefixes such as `OTG0_INTERRUPT_DEST`, `OTG1_INTERRUPT_DEST`, `AZF0STREAM0_AZALIA_STREAM_INDEX`, and `DMCUB_REGION3_CW0_TOP_ADDRESS` describe replicated hardware blocks.

Major macro families in this slice:

- `DISP_INTERRUPT_STATUS_CONTINUE19` through `DISP_INTERRUPT_STATUS_CONTINUE25`: status-chain fields for Azalia audio endpoint format/enabled/disabled events, OTG CPU static-screen/v-update/GSL/vstartup/vready events, I2C DDC hardware done/read request events, DP fast-training/stream-disable events, OTG no-lock vupdate and DRR total reach events, DMCUB mailbox/fault/GPINT/security events, DMU/DWB/DCHUBBUB/EXTERNAL_SW/MALL underflow events, and low-priority/high-priority DMCUB outbox readiness.
- `DC_GPU_TIMER_START_POSITION_VREADY`, `DC_GPU_TIMER_START_POSITION_FLIP`, `DC_GPU_TIMER_START_POSITION_V_UPDATE_NO_LOCK`, and `DC_GPU_TIMER_START_POSITION_FLIP_AWAY`: compact per-pipe 3-bit selectors for GPU timer start-position events across display pipes.
- Interrupt destination registers: `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, `DCPG_INTERRUPT_DEST`, `MMHUBBUB_INTERRUPT_DEST`, `WB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST`, `DCHUB_PERFCOUNTER_INTERRUPT_DEST`, `DPP_PERFCOUNTER_INTERRUPT_DEST`, `MPC_INTERRUPT_DEST`, `OPP_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST`, `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, `DSC_INTERRUPT_DEST`, and `HPO_INTERRUPT_DEST`. These route many display, link, audio, power, perfcounter, and debug interrupts to IH, GPIO, DMCUB, or other destinations depending on hardware programming.
- `DMCUB_RBBMIF_SEC_CNTL`, `RBBMIF_TIMEOUT`, `RBBMIF_STATUS`, `RBBMIF_INT_STATUS`, `RBBMIF_TIMEOUT_DIS`, `RBBMIF_TIMEOUT_DIS_2`, and `RBBMIF_STATUS_FLAG`: DMCUB register-bus interface security, timeout, interrupt, timeout-disable, and status-flag fields.
- DMCUB region/window fields: `DMCUB_REGION0_OFFSET` through `DMCUB_REGION7_OFFSET_HIGH`, top-address/enable fields for regions 0, 1, 2, 4, 5, 6, and 7, and code-window `DMCUB_REGION3_CW0` through `DMCUB_REGION3_CW7` base/top/offset fields.
- DMCUB interrupt and control fields: `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, `DMCUB_INTERRUPT_STATUS`, `DMCUB_INTERRUPT_TYPE`, external interrupt status/context/ack, instruction-fetch/data-write/undefined-address fault addresses, `DMCUB_SEC_CNTL`, `DMCUB_MEM_CNTL`, inbox/outbox base/size/read/write pointers, timer trigger/window/current registers, scratch registers 0 through 15, `DMCUB_CNTL`, `DMCUB_CNTL2`, GPINT data-in/data-out registers, low-speed wake interrupt enable, memory power control, and processor ID.
- Display writeback and memory-client fields: `MCIF_WB_BUFMGR_SW_CONTROL`, `MCIF_WB_BUFMGR_STATUS`, buffer pitch/status/status2 for buffers 1 through 4, arbitration, SCLK change, Y/C buffer addresses and high address halves, VCE control, NB pstate control/latency watermark, clock gating, self-refresh, multi-level QoS, security level, luma/chroma sizes, buffer resolutions, VMID control, minimum TTO, and watermark fields.
- MMHUBBUB/WBIF/DMU fields: warmup config/status/address/VMID, minimum TTO, control, memory power status/control, clock control, soft reset, WBIF SMU watermark and outstanding counters, and `DMU_IF_ERR_STATUS`.
- `DC_PERFMON3_*`: performance counter control, counter control 2, counter state, perfmon control, perfmon control 2, counter-value interrupt/ack/high bits, counter value low, high, and low readout fields for DC perfmon block 3.
- `AZF0STREAM0_AZALIA_STREAM_INDEX/DATA` through `AZF0STREAM7_AZALIA_STREAM_INDEX/DATA` and `AZ_CLOCK_CNTL`: indexed Azalia stream register access windows and audio clock-gating/test-clock fields.
- `DC_PERFMON4_PERFCOUNTER_CNTL`: the first perfmon 4 counter-control field set; the rest of perfmon 4 continues after this chunk.

Within lines 8804-11021 there are more than 200 distinct register names represented by paired or grouped shift/mask macros. The range starts in the middle of `DISP_INTERRUPT_STATUS_CONTINUE19` masks and ends in the middle of `DC_PERFMON4_PERFCOUNTER_CNTL`, so adjacent chunks are required for complete file-level coverage.

## Control Flow

This header has no runtime control flow. Runtime use is through token-pasting register helper macros:

1. DCN 3.5.1-specific code includes `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`.
2. Macros such as `SR`, `SRI`, `SRI_DMUB`, `HWS_SF`, `FD_MASK`, and `FD_SHIFT` paste register and field tokens into the names defined here.
3. Resource construction, IRQ construction, DMUB register initialization, writeback/MMHUBBUB setup, and performance-monitor code populate offset, mask, and shift tables.
4. Operational code later calls register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and polling/wait helpers. Those helpers use this chunk's masks and shifts to preserve unrelated bits while programming or reading hardware state.

The macros do not encode ordering. Correct sequencing still lives in driver code: IRQ routes must be programmed before interrupts are enabled, DMCUB memory windows and mailboxes must be initialized around firmware reset/startup, writeback buffers must be configured before capture, and clock/power/status fields must be handled according to hardware access rules.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- Interrupt status and destination registers expose sticky, routed, or latched hardware interrupt state for OTG, DMCUB, DMU, DCHUB, DPP, MPC, OPP, OPTC, link, HPD, AUX, DSC, HPO, audio, writeback, and perfcounter sources.
- GPU timer start-position fields configure which display-pipe events can anchor GPU timer sampling for vready, flip, no-lock vupdate, and flip-away cases.
- DMCUB region, security, control, scratch, GPINT, timer, fault, inbox, and outbox registers describe the host-visible control surface for DMCUB firmware boot, memory aperture setup, command submission, notification delivery, and debug capture.
- RBBMIF fields track or mask timeout/security behavior for DMCUB register-bus accesses.
- MCIF_WB fields hold writeback buffer manager state, buffer addresses, formats/sizes/resolutions, arbitration, watermark, security, VMID, pstate, self-refresh, and clock-gating controls.
- MMHUBBUB and WBIF fields hold memory warmup, power, reset, watermark, and outstanding-counter state.
- DC perfmon 3 and the start of perfmon 4 hold programmable event selection, counting mode, state selection, counter-off interrupt/ack/status, current-value, threshold, and readout fields.
- Azalia stream and clock fields hold audio stream indexed-register access state and audio clock-gating/test-clock selection.

Persistence is hardware-defined. Configuration fields generally remain until modeset reprogramming, DMCUB reset, power gating, suspend/resume, or ASIC reset. Status, ack, fault, scratch, mailbox pointer, timeout, and interrupt fields may be sticky, write-one-to-clear, self-clearing, read-only, or timing-sensitive. This generated mask file does not identify field access types.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, where `dmub_srv_dcn351_regs_init()` includes this header and converts `FD_MASK`/`FD_SHIFT` expansions into the DMUB DCN35 register table.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, which uses the DMCUB fields for firmware reset/startup, region setup, inbox/outbox rings, GPINT handling, scratch/debug capture, timer reads, and DMCUB interrupt ack/enable operations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`, which includes this header and uses generated masks/offsets to build HPD, pflip, vupdate-no-lock, vblank, vline0, and DMCUB outbox IRQ source tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which includes the DCN 3.5.1 generated headers during resource construction and wires DCN351 capabilities, IRQ service, DIO, HUBBUB, writeback, and power/clock-control resources.
- Shared DCN35/DCN32 helper headers and implementations for MCIF writeback, MMHUBBUB, DMCUB, IRQ, and perfmon behavior, which use token-pasted register names that must match these generated definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which maps interrupt source IDs and context IDs to the status/destination concepts represented here.

The main integration pattern is source-level token pasting. Missing or renamed macros usually fail compilation; incorrect numeric shifts or masks can compile successfully while corrupting hardware programming.

## Risks And Edge Cases

- Generated constants are untyped. A wrong mask or shift can silently alter adjacent fields in a read/modify/write sequence.
- The chunk boundary is artificial. `DISP_INTERRUPT_STATUS_CONTINUE19` begins before this range, and `DC_PERFMON4_PERFCOUNTER_CNTL` continues after it. Merge/reconciliation must use adjacent chunks for complete register-family analysis.
- Interrupt status/destination fields are high-risk because incorrect routes or masks can cause missed vblank/vline/hotplug/audio/AUX/DMCUB events, interrupt storms, or acknowledgements that fail to clear the intended source.
- DMCUB region and security fields are boot-critical. Incorrect base/top/offset/enable masks can prevent firmware fetches, map the wrong memory window, trip access faults, or break PSP/security expectations.
- DMCUB inbox/outbox and GPINT fields are synchronization-sensitive. Bad pointer, ready, ack, or enable masks can stall command submission, lose notifications, or leave host/firmware rings inconsistent.
- RBBMIF timeout-disable/status fields can hide or misreport register-bus access failures, complicating debug of firmware and display block hangs.
- MCIF_WB buffer address/size/resolution/security/VMID fields affect display writeback DMA. Incorrect masks can write to the wrong address, corrupt capture output, violate isolation, or trigger underflow/backpressure.
- MMHUBBUB memory power, warmup, and reset fields affect low-power transitions and memory-client readiness. Bad masks can cause resume failures, underflow, or clock/power gating regressions.
- Perfmon fields are diagnostic but side-effect-sensitive; wrong event, enable, clear, threshold, or ack masks can invalidate telemetry or leave counter interrupts asserted.
- Azalia indexed stream register fields require correct write-enable and index/data handling. Bad masks can corrupt HDMI/DP audio stream programming or clock-gating state.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN351 support enabled. Token-pasting consumers in DMUB, IRQ, resource, writeback, MMHUBBUB, and perfmon paths should catch missing or renamed macros.
- Mechanically verify that every `__SHIFT` macro in this line range has the expected matching `_MASK` macro and that masks align with field shifts and widths.
- Diff this generated slice against AMD's authoritative DCN 3.5.1 register database and against nearby generated headers where DCN 3.5.0 or DCN 3.6 compatibility is expected.
- Exercise interrupt behavior: hotplug/HPD RX, vblank/vline0, page flip, vupdate-no-lock, DMCUB outbox, AUX/I2C, audio endpoint changes, DSC/link events, and perfcounter interrupts. Watch for missed events, storms, or stuck ack bits.
- Exercise DMCUB firmware lifecycle: cold boot, reset, suspend/resume, secure-region setup, inbox/outbox command traffic, GPINT notifications, scratch/debug collection, and fault-address reporting.
- Exercise writeback paths using display writeback capture with multiple formats, buffer rotations, VMID/security settings, watermark pressure, and power-management transitions.
- Exercise memory and power transitions involving MMHUBBUB warmup, memory power status/control, soft reset, self-refresh, and clock gating.
- Use perfmon/debug validation where available: program DC perfmon 3 and perfmon 4 counters, trigger threshold/overflow cases, ack counter interrupts, and compare readback against expected event activity.
- Monitor kernel logs, DC traces, DMCUB traces, register readback, IRQ counters, writeback output, and display behavior for underflow, timeout, DMCUB fault, stuck mailbox pointer, missing hotplug/vblank, black screen, audio loss, or resume instability.

## Cross-Chunk Notes

The previous chunk is required for the beginning of `DISP_INTERRUPT_STATUS_CONTINUE19`. The following chunk is required for the rest of `DC_PERFMON4_PERFCOUNTER_CNTL` and subsequent perfmon 4 fields. The final per-file report should treat this as one generated DCN 3.5.1 hardware metadata slice, not as an independent software module.
