# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 4771-7223

## Scope

This chunk is a generated AMD DCN 3.0.1 register shift/mask header slice. It contains only preprocessor constants; there are no C functions, structs, enums, variables, allocation paths, locks, or executable branches. The exported API is the generated field namespace:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The requested range contains 2,157 `#define` entries across 246 register names. It starts at the tail of `DC_GPU_TIMER_START_POSITION_FLIP_AWAY`, covers display interrupt status and interrupt destination routing, DMCUB/RBBMIF/DMU register fields, MCIF writeback and MMHUBBUB fields, perfmon blocks, and HDA/Azalia stream fields, then ends mid-register in `DC_PERFMON4_PERFCOUNTER_STATE`. Because both boundaries are artificial chunk boundaries, whole-file reconciliation must merge adjacent chunks before making complete claims about either boundary register.

Although this file lives below a local `ceph-client` source mirror, the content is AMDGPU display hardware metadata, not distributed filesystem logic.

## Purpose

The purpose of this chunk is to publish exact bit positions and masks for DCN 3.0.1 display-controller MMIO register fields. Runtime AMDGPU display code combines these constants with matching register offsets from `dcn_3_0_1_offset.h` and register helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Major hardware areas represented here are:

- Display interrupt status continuation registers `DISP_INTERRUPT_STATUS_CONTINUE23` through `DISP_INTERRUPT_STATUS_CONTINUE25`, including DCPG power interrupts, DSC underflow/core/perfmon interrupts, DMCUB mailbox/timer/data/fault interrupts, HPO and MMHUBBUB interrupts, and ABM histogram/luma/backlight interrupts for ABM2 through ABM5.
- Interrupt destination routing registers for display blocks: `DCCG`, `DMU`, `DCPG`, `MMHUBBUB`, `WB`, `DCHUB`, DCHUB and DPP perf counters, `MPC`, `OPP`, `OPTC`, per-OTG instances 0 through 5, `DIG`, `I2C_DDC_HPD`, `DIO`, `DCIO`, `HPD`, `AZ`, `AUX`, and `DSC`.
- DMCUB and DMU interface control: RBBMIF security, timeout, status, timeout-disable, interrupt status, DMCUB memory regions and cache-window regions, interrupt enable/ack/status/type, extended interrupt status/context/ack, fault-address capture, security/reset controls, memory QoS/read/write spaces, mailbox base/size/read/write pointers, timers, scratch registers, GPINT data, light-sleep wake, memory power, timer current value, and processor ID.
- MCIF writeback and MMHUBBUB: writeback buffer manager control/status, four buffer slots with luma/chroma addresses, status, tags, locks, overrun/TMZ fields, pitch, resolution, sizes, arbitration, VCE handoff controls, NB pstate/self-refresh/QoS/watermark controls, VMID, warmup configuration, VGAIF latency and outstanding counters, memory power, clock gating, soft reset, and DMU interface error status.
- DC perfmon instances 3 and 4: counter control, counted-value type, hardware stop/count-off selection, counter state selection, perfmon state/report count, interrupt status/ack, current value high/low, and read selectors.
- HDA/Azalia stream indirection for streams 0 through 7 plus Azalia clock gating/test-clock fields.

## Important API Surface

This chunk's important API is the generated macro set consumed by register table builders and field access helpers. Representative high-risk or high-integration fields include:

- `DMCUB_REGION*_OFFSET`, `DMCUB_REGION*_OFFSET_HIGH`, and `DMCUB_REGION*_TOP_ADDRESS` fields for DMCUB firmware memory window programming. `*_TOP_ADDRESS` registers pack the top address with an enable bit at bit 31.
- `DMCUB_REGION3_CW*_BASE_ADDRESS`, `DMCUB_REGION3_CW*_TOP_ADDRESS`, `DMCUB_REGION3_CW*_OFFSET`, and `*_OFFSET_HIGH` for DMCUB cache-window setup used by firmware boot, inbox/outbox, trace, and other firmware-visible memory regions.
- `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, `DMCUB_INTERRUPT_STATUS`, and `DMCUB_INTERRUPT_TYPE` fields for timer, inbox, outbox, GPINT, and undefined-address-fault interrupt control.
- `DMCUB_INBOX0_*`, `DMCUB_INBOX1_*`, `DMCUB_OUTBOX0_*`, and `DMCUB_OUTBOX1_*` fields for firmware command/event ring base addresses, sizes, and read/write pointers.
- `DMCUB_SEC_CNTL`, `DMCUB_CNTL`, `DMCUB_MEM_CNTL`, `DMCUB_MEM_PWR_CNTL`, and `DMCUB_SCRATCH0` through `DMCUB_SCRATCH15` for boot/reset/security, memory access policy, firmware state exchange, and debug.
- `MCIF_WB_BUFMGR_SW_CONTROL`, `MCIF_WB_BUFMGR_STATUS`, `MCIF_WB_BUF_*_STATUS`, `MCIF_WB_BUF_*_STATUS2`, `MCIF_WB_BUF_*_ADDR_[YC]`, `*_HIGH`, `MCIF_WB_BUF_*_RESOLUTION`, `MCIF_WB_VMID_CONTROL`, and `MCIF_WB_MIN_TTO` for display writeback buffer management.
- `MMHUBBUB_WARMUP_*`, `MMHUBBUB_MEM_PWR_*`, `MMHUBBUB_CLOCK_CNTL`, `MMHUBBUB_SOFT_RESET`, and `DMU_IF_ERR_STATUS` for memory hub warmup, memory power, clock/reset, and interface error handling.
- `DC_PERFMON3_*` and `DC_PERFMON4_*` fields for display performance counter programming and interrupt/status handling.
- `AZF0STREAM<n>_AZALIA_STREAM_INDEX` and `AZF0STREAM<n>_AZALIA_STREAM_DATA` for indexed HDA stream register access.

The field constants are untyped numeric constants. Correctness depends on exact token names because AMD display code pastes register and field tokens into generated `__SHIFT` and `_MASK` macro names.

## Control Flow

There is no local runtime control flow. The runtime sequence is supplied by AMDGPU display code:

1. DCN 3.0.1 code includes `dcn_3_0_1_offset.h` and this `dcn_3_0_1_sh_mask.h`.
2. Resource, IRQ, DMUB, DWB/MMHUBBUB, audio, and link code build register and field tables with token-pasting macros.
3. Register helpers use the generated `__SHIFT` and `_MASK` values to read, write, update, set, poll, or acknowledge hardware fields.

Direct integration examples in this tree include `display/dmub/src/dmub_dcn301.c`, which includes this exact header and builds `dmub_srv_dcn301_regs` from `DMUB_COMMON_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_COMMON_FIELDS()`. `display/dc/resource/dcn301/dcn301_resource.c` also includes this header and uses DCN301 register-list and mask-list macros for display resources, audio, AUX/HPD, link encoders, panel control, DPP, OPP, and related DC objects.

The macros do not encode ordering requirements. Callers must still sequence DMCUB reset and memory-window setup, mailbox pointer initialization, interrupt clear/enable, writeback buffer locking, MMHUBBUB clock/power/reset changes, Azalia stream indexed writes, and perfmon start/stop/ack handling according to hardware rules.

## State And Persistence

This header stores no software state and persists nothing on its own. It describes MMIO-backed hardware state:

- DMCUB firmware state includes memory window mappings, cache-window enablement, secure reset state, mailbox ring locations and pointers, scratch registers used for boot/status/options, timers, GPINT data, interrupt status/ack/type bits, and fault address captures.
- Interrupt destination and status fields control how display block events are routed and observed by the interrupt handler.
- MCIF writeback state includes buffer slot ownership, active/next buffer selection, line counters, locks, overflow/overrun indicators, luma/chroma addresses, resolution, pitch, TMZ/security-related flags, VMID, arbitration, and pstate/watermark behavior.
- MMHUBBUB state includes warmup DMA address/range/VMID/QoS, memory and clock power controls, soft resets, outstanding counters, VGAIF controls, and DMU interface error bits.
- Perfmon state includes selected events, run/stop controls, counter states, current values, and sticky interrupt status/ack fields.
- Azalia stream state is accessed through per-stream index/data windows and audio clock gating controls.

Persistence is hardware-defined. Configuration fields normally remain until reprogrammed, power-gated, reset, or restored after suspend/resume. Status, fault, interrupt, ack, and counter fields may be sticky, read-only, write-one-to-clear, self-clearing, or timing-sensitive; this generated header does not distinguish those semantics.

## Dependencies And Integration Points

This chunk depends on:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h` for matching DCN 3.0.1 register offsets and base indexes.
- `vangogh_ip_offset.h` and DCN base-segment definitions used by DCN301 code to turn offsets into absolute MMIO addresses.
- AMD display register helper infrastructure (`reg_helper.h`, `dmub_reg.h`, and block-specific register-list macros) that expects the generated shift/mask naming convention.

Important integration paths:

- `display/dmub/src/dmub_dcn301.c`: exact include site for this header; constructs DMUB register offset, mask, and shift tables for `DMUB_ASIC_DCN301`.
- `display/dmub/src/dmub_srv.c`: selects `dmub_srv_dcn301_regs` for DCN301 ASICs.
- `display/amdgpu_dm/amdgpu_dm.c`: maps the relevant display ASIC to `DMUB_ASIC_DCN301`.
- `display/dc/resource/dcn301/dcn301_resource.c`: exact include site for DCN301 display resource construction and many field-table initializers.
- `display/dc/dcn10/dcn10_dwb.h`, `display/dc/dcn30/dcn30_dwb.h`, and `display/dc/dcn30/dcn30_mmhubbub.h`: consume MCIF writeback and MMHUBBUB-style field names represented in this range.
- `display/dc/irq/*/irq_service_*.c`: related IRQ service code consumes generated interrupt enable/status/ack/destination fields for display and DMCUB events.
- `display/dc/dce/dce_audio*` and DCN audio register-list code: consume Azalia/HDA index/data and clock-control fields for display audio.

## Risks And Edge Cases

- A wrong mask or shift compiles cleanly but can update the wrong bit in a live MMIO register. The highest-risk fields are reset, memory-window enable, mailbox pointer, interrupt ack, writeback buffer lock/status, pstate/watermark, and fault-clear fields.
- DMCUB boot is sensitive to address-window programming. Incorrect offset-high, top-address, enable, or secure-reset fields can prevent firmware boot, map the wrong memory, corrupt inbox/outbox traffic, or leave DMUB in reset.
- Mailbox pointers and interrupt fields are producer/consumer state. Bad masks in inbox/outbox read/write pointers or ready/done/GPINT ack bits can cause command hangs, lost notifications, or interrupt storms.
- Writeback buffer fields are repeated for four slots and for luma/chroma planes. Instance-like copy drift can affect only one buffer slot, one plane, or TMZ/overrun handling under capture/writeback workloads.
- Status and ack bits often share registers. Generic read-modify-write updates around `*_STATUS`, `*_ACK`, `*_INT_STATUS`, and `*_CLEAR` fields can accidentally clear sticky diagnostics or fail to clear an interrupt if the mask semantics are wrong.
- Power, clock, and reset fields interact with low-power transitions. Incorrect `MMHUBBUB_*`, `DMCUB_MEM_PWR_*`, or `AZ_CLOCK_CNTL` masks can produce suspend/resume failures, ignored writes while a block is gated, or stale state after reset.
- Perfmon fields are multiplexed and packed. Counter select, value high/low, interrupt status, and ack field drift may produce misleading diagnostics rather than obvious functional failures.
- The chunk ends before all `DC_PERFMON4_PERFCOUNTER_STATE` masks are visible, so this work item should not be used as the only source for the complete DC perfmon4 register-family description.

## Test Signals

Useful validation signals for this chunk are:

- Build AMDGPU display with DCN301/Van Gogh support enabled. Missing or renamed macros should fail in DMUB DCN301 register-table construction, DCN301 resource construction, DWB/MMHUBBUB code, audio code, or IRQ tables.
- Mechanically verify the generated naming contract in lines 4771-7223: each intended field has a `__SHIFT` and matching `_MASK`, repeated register families preserve expected bit positions, and boundary registers are reconciled with adjacent chunks.
- Diff against AMD's authoritative DCN 3.0.1 register database and nearby generated headers such as `dcn_3_0_0_sh_mask.h` where DCN 3.0 and DCN 3.0.1 are expected to align.
- Runtime DMUB tests: firmware boot, reset/reload, secure backdoor load, region/window setup, cached inbox/outbox use, GPINT handling, outbox interrupts, scratch/status readback, fault capture, and suspend/resume.
- Runtime display interrupt tests: hotplug, AUX/DDC, vblank/vupdate, DMCUB outbox ready/done, DSC underflow/core/perfmon, ABM2-5 events, and interrupt ack/reenable paths.
- Writeback tests: enable/disable DWB, exercise all buffer slots, luma/chroma addresses, pitch/resolution programming, software locks, overrun/overflow detection, VMID/TMZ cases, and pstate/watermark transitions.
- MMHUBBUB and low-power tests: warmup address programming, outstanding counter sanity, memory power state convergence, clock-gating/reset paths, and suspend/resume without stuck DMU interface errors.
- Audio tests: HDMI/DP audio stream setup across Azalia stream instances, indexed stream register access, audio clock gating, and audio recovery after modeset or power transition.
- Perfmon tests: select events, start/stop counters, read high/low values, trigger counter interrupts, and verify ack/status behavior for perfmon3 and the adjacent perfmon4 family after merged coverage is available.

## Chunk Notes

This is generated register metadata, not functional logic. The main research value is identifying which hardware surfaces the constants expose and where bad constants would have the largest blast radius: DMCUB boot/mailbox/control, interrupt routing and acknowledgement, MCIF writeback buffer ownership, MMHUBBUB power/warmup behavior, audio stream indirection, and display performance counters.
