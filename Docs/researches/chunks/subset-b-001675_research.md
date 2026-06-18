# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 46847-49414

## Scope

This chunk is a generated constants-only slice of the AMDGPU DCN 2.1.0 register shift/mask header. It contains no functions, structs, enums, storage, or executable code. Its exported contract is preprocessor macros named as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`; register helper code uses those constants to place or extract bitfields in MMIO and indexed display/audio registers.

The requested range covers 2,568 source lines, with 2,121 `#define` entries: 1,060 shift constants and 1,061 mask constants. It contains 15 generated `addressBlock` sections and 402 register comments. The chunk begins at the final mask for `DSCC4_DSCC_B_CR_SQUARED_ERROR_UPPER`, continues through the tail of DSC instance 4 telemetry, all DSC instance 5 mask/shift definitions, DMCUB, MCIF writeback, DCHVM, legacy VGA indexed register windows, and Azalia F2 endpoint/audio descriptor metadata. It ends at the `//SINK_DESCRIPTION15` register comment, so the sink-description array continues in the next chunk.

## Purpose

The purpose of this header section is to encode the DCN 2.1 ASIC bit layout for several hardware blocks that are otherwise accessed through generic AMD display helpers. The matching offset header supplies register addresses; this header supplies the field positions and masks within each register.

Major hardware areas covered by the chunk are:

- DSC telemetry and DSC instance 5 control: DSCC4 tail error/fullness/debug fields, `DSC_TOP5_*`, `DSCCIF5_*`, `DSCC5_*`, and `DC_PERFMON23/24_*`.
- DMCUB firmware interface: `DMCUB_REGION*`, `DMCUB_INTERRUPT_*`, inbox/outbox ring registers, scratch registers, timer, fault address registers, security/memory controls, and GPINT data paths.
- MCIF writeback instance 2: `MCIF_WB2_*` buffer manager, buffer addresses, pitch, arbitration, watermark, power/self-refresh, QoS, luma/chroma size, high address, and resolution fields.
- Display core host VM: `DCHVM_CTRL0`, `DCHVM_CTRL1`, `DCHVM_CLK_CTRL`, `DCHVM_MEM_CTRL`, `DCHVM_RIOMMU_CTRL0`, and `DCHVM_RIOMMU_STAT0`.
- Legacy VGA indexed windows: sequencer (`SEQ*`), CRT controller (`CRT*`), graphics controller (`GRA*`), and attribute controller (`ATTR*`) bitfields.
- Azalia/HDA display-audio endpoint F2 metadata: converter controls, pin controls, audio descriptors, multichannel controls, HBR, lipsync, sink info access, channel-status overrides, LPIB snapshots, coding/format tracking, wireless display ID, remote keepalive, pin/widget capabilities, standalone audio descriptor records, and sink information strings.

Although this repository path is under `sources/distributed-fs/ceph-client`, the file is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed-storage, network, or on-disk persistence behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The relevant API surface is the generated macro namespace:

- `*_SHIFT` constants hold the low-bit position for a named field.
- `*_MASK` constants hold the already-positioned mask for the same field.
- `//REGISTER_NAME` comments group field macros by hardware register.
- `// addressBlock: ...` comments group registers by generated hardware address block.

The DSC portions include:

- Tail DSCC4 metric masks for squared-error upper bits, max absolute error, rate-buffer fullness, rate-control-buffer fullness, and debug-bus rotation.
- `DC_PERFMON23_*` and `DC_PERFMON24_*` performance monitor fields for event selection, counted-value type, hardware start/stop selection, counter states, perfmon state, report count, count-off interrupt enable/status/ack, counter interrupt status/ack, and high/low value reads.
- `DSC_TOP5_DSC_TOP_CONTROL` and `DSC_TOP5_DSC_DEBUG_CONTROL` fields for DSC clock enables, clock-gating controls, debug selection, and debug status.
- `DSCCIF5_DSCCIF_CONFIG0/1` fields for stream/source selection, clock enable, endianness, 4:2:0 native support, DSCCIF clock gating, OTG vertical start edge, and test seed.
- `DSCC5_DSCC_CONFIG*`, status, interrupt, 23 PPS configuration registers, memory power controls, error accumulators, buffer fullness counters, and test debug bus rotation.

The DMCUB block is the densest section in this chunk. It defines fields for:

- Region base/top/offset programming, including high address halves and region enable bits.
- Region 3 code-window base/top/offset entries `CW0` through `CW7`.
- Interrupt enables, status, ack, type, external interrupt status/context/ack, and low-power wake interrupt enable.
- Fault reporting for instruction fetch, data write, and undefined address faults.
- Security and memory control bits such as reset, memory unit ID, outbox/inbox selection, auto-increment, memory power state/force/disables, and dynamic power controls.
- Inbox and outbox base/size/read-pointer/write-pointer pairs for channels 0 and 1.
- Timer trigger/window/current registers, scratch registers 0 through 15, DMCUB enable/trace/wait/soft-status fields, GPINT data in/out, and processor ID.

The MCIF writeback block covers `MCIF_WB2_*` fields used by the memory-client side of display writeback. Important groups include buffer manager software control/status, current line readback, buffer pitch, four-buffer status and address programming, luma/chroma address offsets and high address halves, arbitration and SCLK-change handling, test debug index/data, VCE control, latency watermark and NB pstate control, self-refresh, clock gating, warm-up, multi-level QoS, buffer luma/chroma sizes, and per-buffer resolution.

The DCHVM block defines the masks used by host-VM/rIOMMU display memory setup. Representative fields are `HOSTVM_INIT_REQ`, `HVM_*_PWR_*`, `HVM_*CLK_*_GATE_DIS`, request/response clock request modes, `HOSTVM_PREFETCH_REQ`, `HOSTVM_POWERSTATUS`, `RIOMMU_ACTIVE`, and `HOSTVM_PREFETCH_DONE`.

The VGA indexed blocks expose legacy VGA register fields such as sequencer reset, clocking mode, map mask, character-map select, memory mode, CRT timing registers, cursor start/end/location, start address, offset, underline, mode control, line compare, graphics set/reset, color compare, rotate, read map select, graphics mode, miscellaneous graphics, color don't-care, bit mask, and attribute palette/control/overscan/plane-enable/pixel-panning/color-select fields.

The Azalia F2 endpoint block defines HDA-style HDMI/DP audio codec fields. Important groups include converter format fields, channel/stream IDs, digital converter state, stripe/ramp/GTC embedding controls, capability reports, pin widget control, unsolicited response, pin sense, configuration default words, speaker/channel allocation, downmix, audio descriptor selection/data, multichannel enables, lipsync, HBR, sink-info index/data windows, multichannel mode, channel-status override words 0-8, association/digital-output status, LPIB snapshot/control, coding type, format changed, wireless display identity, remote keepalive, pin/widget capabilities, and connection-list length. The separate `azendpoint_descriptorind` section defines `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, each with max channels, supported frequencies, descriptor byte 2, and stereo frequency fields. The `azendpoint_sinkinfoind` section begins manufacturer/product ID, sink description length, port ID, and sink-description byte records through the `SINK_DESCRIPTION15` comment at the requested boundary.

## Control Flow

This chunk has no local control flow. Runtime control flow appears in consumers that expand the generated macros into register tables, then use generic register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_WAIT`, `FD_MASK`, and `FD_SHIFT`.

The common flow is:

1. A DCN 2.1 component includes `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`.
2. The component declares generation-specific register tables by pasting register and field names through macros such as `SR`, `SRI`, `SRII`, `REG_OFFSET`, `FD_MASK`, and `FD_SHIFT`.
3. Runtime code calls the register helpers against those tables.
4. The helpers use these shifts and masks to construct read/modify/write values, decode status, acknowledge interrupts, poll hardware state, or program indexed audio/VGA windows.

Control-sensitive flows represented by this chunk include DSC compressor configuration and telemetry reads, DMCUB boot and mailbox setup, DMCUB outbox interrupt enable/ack handling, display writeback buffer programming, DCHVM/rIOMMU initialization and prefetch polling, legacy VGA indexed access, and HDMI/DisplayPort audio endpoint programming.

Concrete integration examples in this tree include:

- `display/dmub/src/dmub_dcn21.c` includes this header and builds `dmub_srv_dcn21_regs` from `DMUB_COMMON_REGS()` and `DMCUB_INTERNAL_REGS()`, with field masks and shifts from `DMUB_COMMON_FIELDS()`.
- `display/dc/irq/dcn21/irq_service_dcn21.c` includes this header and maps the DMCUB outbox interrupt through `DMCUB_INTERRUPT_ENABLE.DMCUB_OUTBOX1_READY_INT_EN` and `DMCUB_INTERRUPT_ACK.DMCUB_OUTBOX1_READY_INT_ACK`.
- `display/dc/resource/dcn21/dcn21_resource.c` includes this header, instantiates DSC register/mask/shift tables, creates DSC instances from `dsc_regs[]`, `dsc_shift`, and `dsc_mask`, and wires in DWB/MMHUB/DCHVM resources.
- `display/dc/hubbub/dcn21/dcn21_hubbub.[ch]` uses the DCHVM fields to request host-VM initialization, poll `RIOMMU_ACTIVE`, set host-VM power status, request prefetch, enable clock gating, and wait for `HOSTVM_PREFETCH_DONE`.

## State And Persistence Behavior

The header itself stores no software state and performs no persistence. It describes hardware-visible state whose lifetime is controlled by the ASIC, driver programming, firmware, reset domains, and display power-management transitions.

State represented by the DSC and DC perfmon fields includes DSC enable/configuration, picture parameter set values, native 4:2:0/4:2:2 and bits-per-component settings, slice geometry, rate-control and quantization parameters, memory power-control bits, interrupt status/ack/mask/type, error accumulators, rate-buffer fullness levels, debug-bus selectors, and perfmon counter configuration/state/value/interrupt state.

DMCUB state includes address windows for firmware regions, code windows, inbox/outbox rings, ring pointers, interrupt masks/status/acks, external interrupt context, security reset/memory controls, scratch registers used for firmware-driver handshake and diagnostics, GPINT payloads, timer state, fault addresses, low-power wake controls, memory power state, and processor identity. Some of these values are programmed during DMUB boot; others are live readbacks, firmware-owned handshake fields, or sticky fault/interrupt status.

MCIF writeback state includes capture buffer selection and address programming, pitch, luma/chroma offsets and sizes, buffer status, arbitration and pstate/watermark behavior, QoS, clock-gating/self-refresh/warm-up controls, current-line readback, VCE-facing controls, and debug selectors. These fields persist until the writeback pipeline is reprogrammed, reset, or power-gated.

DCHVM state includes host-VM initialization request, rIOMMU active/prefetch status, display host-VM power reflection, GPUVM return controls, and clock-gating policy. The driver code expects a specific sequence: request init, poll activity, reflect power, request prefetch, and wait for completion.

VGA indexed state is legacy display state. These fields can affect VGA-compatible mode timing, memory maps, palette attributes, cursor, text/graphics behavior, and controller resets. Modern DC paths may rarely touch them, but stale or wrong masks can still affect compatibility paths.

Azalia F2 state includes audio stream format, channel and stream binding, digital converter metadata, pin capabilities/control/status, ELD/sink-derived descriptors, multichannel mapping, HBR/lipsync settings, channel-status overrides, LPIB snapshots, format-change state, wireless display identity, remote keepalive, sink manufacturer/product/port IDs, and sink description bytes. Some fields are capability mirrors exposed through the HDA codec model, some are programmed from display sink data, and some are live or sticky status.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which defines the matching register addresses and base indices. This header is only useful together with those offsets and AMD's register-helper macro conventions.

Visible DCN 2.1 include sites are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`

DSC integration is through `dcn20_dsc` structures and `DSC_REG_LIST_DCN20` / `DSC_REG_LIST_SH_MASK_DCN20` expansions in the DCN 2.1 resource pool. Only a subset of the six generated DSC instances may be exposed by the resource capability; the full generated register layout still exists in the header.

DMCUB integration crosses both the DMUB service and DC IRQ service. The DMUB service programs region windows, scratch/inbox/outbox state, and common fields. IRQ service uses DMCUB interrupt enable/ack masks for outbox notification. Incorrect constants here can break the display microcontroller boot path, driver/firmware command rings, interrupt delivery, or fault diagnostics.

MCIF writeback integration is through DCN 2.0 writeback and MMHUB helper code reused by DCN 2.1 (`dcn20_dwb`, `dcn20_mmhubbub`). The `MCIF_WB2_*` fields line up with writeback buffer, watermark, arbitration, and memory-client programming.

DCHVM integration is through `dcn21_hubbub`. Its masks are consumed in host-VM/rIOMMU bring-up and power/clock policy programming.

Azalia integration is shared with HDMI/DP audio code and HDA endpoint indexed-register handling. The F2 endpoint and descriptor/sink-info windows are protocol-facing because they contribute to stream format, sink descriptor, channel allocation, and HDA codec responses.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong generated shift or mask will compile cleanly but can update the wrong bitfield, truncate a value, fail to clear a sticky status bit, or poll a bit that never changes.

DSC fields are display-quality and link-bandwidth sensitive. Bad PPS, rate-control, slice, BPC, native mode, memory-power, or interrupt fields can produce DSC validation failures, blank display, corrupt compressed output, wrong buffer-fullness/error telemetry, or interrupts that cannot be acknowledged. The range begins at line 46847 in the middle of the DSCC4 register family, so whole-instance conclusions require the previous chunk.

DMCUB fields are boot and firmware-communication critical. Errors in region offsets/top addresses, inbox/outbox sizes or pointers, scratch fields, interrupt ack/enable bits, security reset, memory power controls, or GPINT payloads can prevent DMUB firmware from starting, cause stuck command rings, lose outbox notifications, hide fault addresses, or break suspend/resume and low-power wake behavior.

MCIF writeback fields are memory-safety and capture-correctness sensitive. Wrong luma/chroma address high/low fields, offsets, buffer sizes, pitch, or resolution masks can write captured frames to the wrong memory location or with the wrong layout. Incorrect arbitration, pstate, watermark, QoS, or self-refresh fields can cause underrun/overrun, stalls, excessive latency, or power-management regressions.

DCHVM fields have ordering and polling requirements that are not encoded by the macros. Callers must still request initialization, observe rIOMMU activity, reflect power status, request prefetch, configure clock gating, and wait for prefetch completion in a safe order. Bad masks can create hangs in `REG_WAIT` paths or falsely mark the host-VM path active.

VGA fields are legacy but broad in effect. A bad field in an indexed VGA register can affect mode reset, palette, timing, memory map, or cursor behavior in compatibility paths. These indexed registers are also easy to misuse because address/data-window sequencing is outside this header.

Azalia fields are externally observable through HDA/HDMI/DP audio behavior. Incorrect converter format, stream ID, digital converter, audio descriptor, multichannel, HBR, channel allocation, LPIB, sink info, or channel-status masks can cause missing audio, wrong sample rate/channel count, bad non-PCM/HBR behavior, bad ELD/sink advertisement, stuck format-change events, or incorrect codec responses after hotplug.

Chunk boundaries are important. The first line is a lone DSCC4 mask whose shift and register heading are in the previous chunk. The final requested line is only the `//SINK_DESCRIPTION15` comment; its shift and mask definitions are immediately after the requested range and belong to the next chunk. The merge lane should reconcile those partial register groups before producing the final per-file document.

## Test Signals

Useful validation is mostly build coverage plus hardware/driver behavior:

- Compile coverage for DCN 2.1 display, DMUB, IRQ, GPIO, resource, DSC, DWB, MMHUB, hubbub, and audio paths that include `dcn_2_1_0_sh_mask.h`.
- Generated-header consistency checks that each `*_SHIFT` has a corresponding `*_MASK`, masks match shift and field width expectations, and all registers have matching addresses in `dcn_2_1_0_offset.h`.
- DSC validation on DCN 2.1 display modes that require DSC, including modeset, hotplug, suspend/resume, PPS programming, rate-control behavior, DSC interrupt status/ack, and error/fullness telemetry.
- DMUB boot and mailbox tests that verify region programming, firmware start, inbox/outbox pointer movement, scratch/status values, GPINT data exchange, outbox IRQ delivery, low-power wake, and fault capture.
- DCHVM/rIOMMU tests that exercise host-VM initialization, `RIOMMU_ACTIVE` polling, prefetch request/completion, clock gating, power transitions, and resume paths.
- Display writeback tests covering buffer address programming, pitch, luma/chroma sizes, four-buffer rotation, current-line/status reads, watermark/pstate behavior, QoS, and captured frame correctness.
- VGA compatibility smoke tests where applicable, especially modes that touch indexed sequencer/CRT/graphics/attribute registers.
- HDMI/DisplayPort audio tests for PCM and non-PCM formats, sample-rate changes, multichannel layouts, HBR, lipsync, channel-status overrides, LPIB snapshots, sink info/descriptors, hotplug, and format-change handling.

Regression symptoms from bad constants include DMUB firmware not booting, hung outbox interrupts, display init timeouts, DSC validation or visual failures, broken writeback captures, host-VM prefetch waits timing out, no HDMI/DP audio, wrong audio channel/rate advertisement, stuck audio status bits, and endpoint- or instance-specific failures that follow a generated register instance.

## Cross-Chunk Notes

This is an artificial line-range slice of a generated header, not a standalone module. It partially overlaps DSCC4 at the start and cuts the `azendpoint_sinkinfoind` sink-description sequence before the `SINK_DESCRIPTION15` field macros. The final merge should combine this document with adjacent chunks for whole-file conclusions about DCN 2.1.0 register coverage and repeated instance consistency.
