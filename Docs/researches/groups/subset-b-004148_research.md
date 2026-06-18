# subset-b-004148 research

This grouped report covers Qualcomm CAMSS CSIPHY, ISPIF, format helper, and VFE hardware-version files. Each section preserves the original source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy-3ph-1-0.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy-3ph-1-0.c

## Purpose
Implements the 3-phase CSIPHY hardware operation table used by the common CAMSS CSIPHY subdev code. It knows the register layout, reset/interrupt sequence, lane mask calculation, settle-count programming, and SoC-specific lane register tables for gen1 and gen2 PHY blocks.

## Important APIs, Types, and Functions
`struct csiphy_lane_regs` encodes register address, data, optional delay, and parameter type. Large tables cover SDM845, SC8280XP, SM8250/7280, QCM2290/SM6150, SM8550, SM8650, SA8775P/SM8300, and X1E80100. The exported contract is `csiphy_ops_3ph_1_0`, filling `get_lane_mask`, `hw_version_read`, `reset`, `lanes_enable`, `lanes_disable`, `isr`, and `init`. Key helpers are `csiphy_settle_cnt_calc()`, `csiphy_gen1_config_lanes()`, `csiphy_gen2_config_lanes()`, `csiphy_is_gen2()`, and `csiphy_init()`.

## Control Flow
`csiphy_init()` allocates `csiphy->regs`, chooses the SoC table, and sets common register offsets. Power-on in `camss-csiphy.c` calls `reset()` and version read. Stream-on calls `get_lane_mask()` and `lanes_enable()`: it computes settle count from link frequency and timer clock, powers common control bits, programs either gen1 per-lane registers or the selected gen2 table, skips DNP/skew-cal entries, and disables/masks PHY interrupts. The ISR mirrors status bytes into clear registers, pulses common clear, and resets clear registers.

## State and Persistence
State is volatile hardware state plus the devm-owned `csiphy_device_regs` pointer. No persistent storage exists. Register ordering relies on relaxed I/O with explicit barriers in higher-level stream setup and in selected paths.

## Dependencies and Integration Points
Depends on `camss.h` SoC version IDs, `camss-csiphy.h`, Linux I/O and delay primitives, and the common CSIPHY subdev code. It integrates via resource tables that select `csiphy_ops_3ph_1_0`.

## Risks and Test Signals
Risks are table accuracy, lane-position interpretation, settle-count overflow/underflow, incomplete skew-cal support, and SoC offset mismatches. Test signals include a readable HW version, no reset/IRQ storms, correct lane enable masks for 1-4 data lanes, successful streams across supported link frequencies, and stable capture on each SoC table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy-3ph-1-0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy.c

## Purpose
Provides the common CSIPHY V4L2 subdevice implementation: supported media-bus formats, resource initialization, runtime power, clock-rate selection from sensor link frequency, stream enable/disable, pad format handling, media link setup, and entity registration.

## Important APIs, Types, and Functions
Exports `csiphy_formats_8x16`, `csiphy_formats_8x96`, `csiphy_formats_sdm845`, `msm_csiphy_subdev_init()`, `msm_csiphy_register_entity()`, and `msm_csiphy_unregister_entity()`. Core helpers include `csiphy_set_clock_rates()`, `csiphy_set_power()`, `csiphy_stream_on()`, `csiphy_try_format()`, and pad ops for enum/get/set format. Hardware-specific behavior is dispatched through `struct csiphy_hw_ops`.

## Control Flow
Probe-time init maps MMIO and optional clock mux, requests an IRQ with `IRQF_NO_AUTOEN`, builds clock/rate arrays, identifies clocks whose rates are set dynamically, and gets regulators. Power-on resumes runtime PM, enables regulators, computes timer clock rate from sink format bpp and CSI-2 lane count, enables clocks and IRQ, resets hardware, and logs HW version. Stream-on computes link frequency, programs the CSID clock mux when present, then calls hardware `lanes_enable()`. Media link setup stores the downstream CSID id and prevents multiple enabled source links.

## State and Persistence
`struct csiphy_device` stores current pad formats, CSI-2 lane config, selected CSID, power resources, clocks, and hardware ops. State is in memory and registers only; format state is active or TRY state via V4L2 subdev state.

## Dependencies and Integration Points
Integrates sensors to CSID blocks in the media graph, uses `camss_get_link_freq()`, PM runtime, regulators, clocks, platform resources, and V4L2/media APIs. It depends on hardware files such as `camss-csiphy-3ph-1-0.c`.

## Risks and Test Signals
`csiphy_try_format()` references `MSM_CSID_PAD_SINK` while copying the CSIPHY sink format; this is currently equivalent to zero but brittle. Clock-rate selection assumes sorted frequency tables and can reject high pixel clocks. Test via media graph link exclusivity, format propagation sink-to-source, runtime PM unwind on failures, timer clock rate programming, mux selection for combo mode, and stream-on/off with real sensors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy.h

## Purpose
Defines the private CSIPHY contract shared by common CSIPHY code, SoC resource tables, and hardware-version implementations.

## Important APIs, Types, and Functions
Pad constants define one sink and one source pad. `struct csiphy_lane`, `csiphy_lanes_cfg`, `csiphy_csi2_cfg`, and `csiphy_config` carry CSI-2 lane and target CSID configuration. `struct csiphy_format_info` and `csiphy_formats` describe accepted media-bus codes and bpp. `struct csiphy_hw_ops` is the version-specific vtable for lane mask, HW version, reset, lane enable/disable, ISR, and init. `struct csiphy_device` stores CAMSS ownership, subdev/media pads, MMIO, IRQ, clocks, regulators, formats, resource pointer, and hardware register metadata.

## Control Flow
The header shapes initialization by letting resource tables provide `csiphy_subdev_resources` with an id, ops, and format list. Common code initializes `csiphy_device`, calls `hw_ops->init()`, then dispatches power and stream transitions through the vtable.

## State and Persistence
All state is in `struct csiphy_device` and related config structs. Hardware register metadata is held in `struct csiphy_device_regs`; no on-disk persistence exists.

## Dependencies and Integration Points
Depends on Linux clk/interrupt/media/V4L2 headers and forward declarations from CAMSS. It exposes `msm_csiphy_subdev_init/register/unregister` to the top-level CAMSS driver and extern declarations for available format sets and `csiphy_ops_2ph_1_0`/`csiphy_ops_3ph_1_0`.

## Risks and Test Signals
This header is a cross-file ABI; field ordering and enum values affect all CSIPHY implementations. Tests are compile-time coverage of all SoC resource tables plus runtime validation that lane config, formats, IRQ, clocks, and subdev pads line up with the media graph.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-format.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-format.c

## Purpose
Provides small shared CAMSS media-bus and pixel-format lookup helpers used by newer CAMSS components to avoid duplicating format search logic.

## Important APIs, Types, and Functions
Exports `camss_format_get_bpp()`, `camss_format_find_code()`, and `camss_format_find_format()`. They operate on arrays of `struct camss_format_info` declared in `camss-format.h`.

## Control Flow
`camss_format_get_bpp()` scans by media-bus code and returns `mbus_bpp`, warning and falling back to the first format if unknown. `camss_format_find_code()` either returns a requested code if present, returns the code at an enumeration index, returns zero for out-of-range enumeration, or falls back to the first supported code. `camss_format_find_format()` first searches exact bus-code plus fourcc, then falls back to bus-code-only, then returns `-EINVAL`.

## State and Persistence
The file is stateless. It reads caller-provided constant format tables and returns values only.

## Dependencies and Integration Points
Depends on Linux errno/bug helpers and `camss-format.h`. It integrates with VFE/CSID-style format tables and V4L2 pad/video format negotiation.

## Risks and Test Signals
Fallback-to-first behavior is convenient but can hide unsupported user requests; callers must validate negative indices where required. Test signals include exact format matches, bus-code fallback, enumeration out-of-range returning zero, unknown bpp warning, and no out-of-bounds access for empty or malformed tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-format.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-format.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-format.h

## Purpose
Declares shared CAMSS format descriptors and lookup helpers for media-bus format negotiation and memory-plane layout.

## Important APIs, Types, and Functions
`struct fract` represents plane subsampling factors. `struct camss_format_info` stores media-bus code, bus bpp, V4L2 fourcc, number of planes, per-plane horizontal/vertical subsampling, and per-plane memory bits-per-pixel. `PER_PLANE_DATA()` is a designated-initializer helper for table entries. `struct camss_formats` wraps a table and count. Prototypes expose the helpers implemented in `camss-format.c`.

## Control Flow
The header is consumed by components that enumerate or choose formats. The data model lets callers derive bytesperline/sizeimage and match media-bus code to memory format.

## State and Persistence
No runtime state is stored. Constant format tables in other files provide the data.

## Dependencies and Integration Points
Depends only on Linux integer types. It integrates with V4L2 media-bus codes and pixel fourcc users across CAMSS.

## Risks and Test Signals
The plane arrays are fixed at three entries, so new formats with more planes would require ABI changes. Table correctness is critical: wrong subsampling or bpp propagates into buffer sizes and hardware stride. Compile coverage of table initializers plus format negotiation and buffer layout tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-ispif.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-ispif.c

## Purpose
Implements the legacy ISPIF subdevice that routes CSID outputs to VFE PIX/RDI inputs on older Qualcomm CAMSS platforms. It owns ISPIF reset, power reference counting, clock mux selection, CID/CSID/interface programming, interrupt handling, pad formats, media links, and entity registration.

## Important APIs, Types, and Functions
Exports `msm_ispif_subdev_init()`, `msm_ispif_register_entities()`, and `msm_ispif_unregister_entities()`. Key routines include `ispif_isr_8x16()`, `ispif_isr_8x96()`, `ispif_reset()`, `ispif_set_power()`, `ispif_select_clk_mux()`, `ispif_validate_intf_status()`, `ispif_wait_for_stop()`, `ispif_select_csid()`, `ispif_select_cid()`, `ispif_config_irq()`, `ispif_config_pack()`, `ispif_set_intf_cmd()`, `ispif_set_stream()`, and format/link helpers.

## Control Flow
Init chooses line count by SoC, assigns 8x16 or 8x96 format lists, maps base and clock-mux registers, requests the version-specific IRQ handler, gets clocks and reset clocks, and initializes locks/completions. Power-on resumes PM, enables clocks, resets the selected VFE side, and initializes cached interface commands. Stream-on validates a linked sink, locks config, selects the CSID clock mux, checks idle status, enables CSID/CID/IRQs/optional packed-RDI mode, and commands frame-boundary enable. Stream-off commands frame-boundary disable, waits for idle, then unwinds pack, IRQ, CID, CSID, and mux state.

## State and Persistence
`struct ispif_device` stores MMIO, clocks, reset completions, global `power_count`, command cache per VFE, locks, line array, and CAMSS pointer. `struct ispif_line` stores selected CSID, VFE id, interface, formats, pads, and subdev. State is volatile in memory and registers.

## Dependencies and Integration Points
Depends on platform resources, runtime PM, clocks, completions, mutexes, V4L2/media APIs, CSID id helpers, VFE line identity, and CAMSS power domains. It exists only for SoCs with an ISPIF block.

## Risks and Test Signals
Power reset error paths can leave one PM domain on if the second domain enable fails. `ISPIF_VFE_m_RDI_INTF_n_PACK_CFG_0_CID_c_PLAIN(c)` references `cid` rather than macro argument `c`, currently relying on local variable naming. Test reset completions, overflow ratelimited logs, link exclusivity, CSID/VFE selection, stream-on/off races, packed 10-bit RDI formats, and timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-ispif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-ispif.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-ispif.h

## Purpose
Defines the ISPIF private data model and public CAMSS entry points for older platforms that route CSID streams through ISPIF before VFE.

## Important APIs, Types, and Functions
Pad constants describe one sink and one source pad per ISPIF line. `enum ispif_intf` names PIX0, RDI0, PIX1, RDI1, and RDI2 interfaces. `struct ispif_intf_cmd_reg` caches command register values. `struct ispif_line` stores per-line media subdev state and selected routing endpoints. `struct ispif_device` stores global MMIO, IRQ, clocks, reset completions, power/config locks, interface commands, line array, and CAMSS pointer. Public functions are init/register/unregister.

## Control Flow
Common CAMSS probe calls `msm_ispif_subdev_init()`, then entity registration exposes one V4L2 subdev per ISPIF line. Link setup fills `csid_id`, `vfe_id`, and `interface`, which stream control later consumes.

## State and Persistence
All persistence is in RAM and hardware registers. The `power_count` is shared across lines, while format/routing state is per `ispif_line`.

## Dependencies and Integration Points
Depends on clock and V4L2/media headers plus `struct camss_subdev_resources`. Integrates with CSID and VFE media entities and CAMSS platform resource tables.

## Risks and Test Signals
The shared power counter and per-line routing fields are sensitive to link setup/teardown ordering. Compile tests should cover all users of the struct layout; runtime tests should validate multi-line stream concurrency, media graph links, and clean unregister with initialized mutexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-ispif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-17x.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-17x.c

## Purpose
Implements VFE 17x hardware ops for a newer bus-oriented VFE generation. It focuses on RDI write-master streaming, bus IRQ/status handling, reset acknowledgement, register updates, and buffer completion.

## Important APIs, Types, and Functions
Exports `vfe_ops_170`. Important functions include `vfe_global_reset()`, `vfe_wm_start()`, `vfe_wm_update()`, `vfe_reg_update()`, `vfe_enable_irq_common()`, `vfe_isr()`, `vfe_get_output()`, `vfe_enable()`, `vfe_isr_reg_update()`, and `vfe_isr_wm_done()`. It installs `vfe_isr_ops_170` and `vfe_video_ops_170`.

## Control Flow
Reset masks reset ack and writes broad reset bits. Enabling the first stream enables common IRQs, reserves one WM for the line, and calls generic v2 output enable. WM start configures debug/status, address sync, CGC override, burst, default width/stride, packer, and MIPI RAW mode. IRQ handling clears top and bus statuses, dispatches reset ack, RDI reg-update, RDI SOF, composite done, and WM done. WM done timestamps and sequences the completed buffer, rotates queued buffers, updates the next address, and completes the vb2 buffer.

## State and Persistence
Uses `vfe->reg_update`, `stream_count`, `wm_output_map`, and each line's `vfe_output` buffers/state. There is no durable state outside registers and in-memory queues.

## Dependencies and Integration Points
Depends on generic VFE helpers in `camss-vfe.c`, v2 queue/output helpers, vb2 completion, and CAMSS PM-domain functions. It is selected through SoC resource `vfe_hw_ops`.

## Risks and Test Signals
The ISR checks `STATUS_1_RDI_SOF()` against `status0`, which is suspicious because that macro belongs to status1. WM done requires correct `wm_output_map` before dereferencing. Test reset completion, RDI register update completion, buffer rotation under empty queue, stream_count unwind, and overflow/violation visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-17x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-340.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-340.c

## Purpose
Implements TFE/VFE 340 ops, a compact top/bus register model for RDI streaming with subgroup-to-line mapping and bus write-client interrupts.

## Important APIs, Types, and Functions
Exports `vfe_ops_340`. It defines `enum tfe_iface`, `enum tfe_subgroups`, mapping arrays, `__line_to_iface()`, `__iface_to_line()`, `__subgroup_to_line()`, `vfe_global_reset()`, `vfe_isr()`, `vfe_enable_irq()`, `vfe_wm_start()`, `vfe_wm_update()`, `vfe_reg_update()`, and `vfe_reg_update_clear()`.

## Control Flow
Reset enables reset-done IRQ and writes core reset. Stream setup through generic v2 calls WM start, which programs image config, frame increment, PLAIN64 packer, no frame drop, IRQ subsampling, enables IRQ masks, and enables the write client. ISR clears top status, handles reset done, then if bus write IRQ fired it clears bus status, clears register-update bits by interface, completes buffers by subgroup-to-line mapping, and logs configuration/input/image-size violations. Overflow status is separately read, cleared, and logged per WM.

## State and Persistence
State is generic VFE line/output state plus `vfe->reg_update`. Hardware client state is volatile. No persistent storage.

## Dependencies and Integration Points
Uses generic `vfe_enable_v2()`, `vfe_disable()`, `vfe_buf_done()`, `vfe_queue_buffer_v2()`, PM-domain helpers, and V4L2 active pixel format data.

## Risks and Test Signals
Invalid line/interface mappings fall back to RDI0 or `VFE_LINE_NONE`, so bad caller state may become wrong-stream programming. Buffer done for PIX-related subgroups is mapped even though this implementation is mainly RDI. Test RDI0-2 WM mapping, bus violation logs, overflow logs, register-update clear, reset done, and frame stride/height programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-340.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-4-1.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-4-1.c

## Purpose
Implements first-generation VFE 4.1 ops for MSM8916-style CAMSS. It supports RDI and PIX paths, CAMIF programming, demux/scale/crop/clamp blocks, bus write masters, UB allocation, IRQ dispatch, halt/reset, and optional PM domains.

## Important APIs, Types, and Functions
Exports `vfe_ops_4_1` and the gen1 vtable `vfe_ops_gen1_4_1`. Key helpers include WM enable/frame/line programming, ping/pong address setup, UB config, bus RDI connect/disconnect, xbar config, RDI CID selection, reg update, per-line/common IRQ enables, CAMIF config/cmd/stop polling, module config, QoS/VBIF setup, and ISR read/dispatch.

## Control Flow
Generic gen1 enable code calls this file through `vfe->ops_gen1`. RDI paths connect a WM to the selected RDI, configure frame-based bus writes and UB, then issue register updates. PIX paths configure demux, scaler, crop, clamp, CAMIF dimensions and pixel order, xbar streams, composite masks, and CAMIF frame-boundary commands. The ISR reads/clears status, dispatches reset ack, violations, halt ack, line reg updates, SOF, composite done, and WM ping-pong completions.

## State and Persistence
Uses common `vfe_device` state: output locks, per-line `vfe_output`, `reg_update`, WM maps, power/stream counts, and completions. Registers are volatile; no disk persistence.

## Dependencies and Integration Points
Integrates with `camss-vfe-gen1.c`, VBIF settings, PM-domain helpers, V4L2 formats, media graph VFE lines, and buffer queues.

## Risks and Test Signals
VFE 4.1 only returns UB size for VFE id 0; dual-VFE assumptions must be resource-matched. Pixel path math assumes YUV widths and subsampling. Test RDI and PIX streaming, CAMIF halt timeout, VBIF failures, IRQ masks, UB partitioning, scaler/crop output, and PM-domain conditional paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-4-1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-4-7.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-4-7.c

## Purpose
Implements VFE 4.7 gen1 ops for later dual-VFE platforms. It extends the gen1 model with revised register offsets, per-instance UB sizes, realign buffer support for packed YUV, data-shaper/QoS programming, and updated scaling/cropping formulas.

## Important APIs, Types, and Functions
Exports `vfe_ops_4_7` and `vfe_ops_gen1_4_7`. Important helpers mirror VFE 4.1: reset/halt, WM enable/frame/line setup, word-per-line calculations, UB config, bus xbar/RDI connection, realign config, RDI CID, reg update, IRQ enables, demux/scale/crop/clamp, QoS/DS, CAMIF config/cmd/wait, ISR read, and violation read.

## Control Flow
The gen1 core invokes this vtable during stream enable/disable. RDI streaming programs MIPI enable, RDI stream select, xbar, WM dimensions and addresses, IRQs, and reg updates. PIX streaming configures demux, scale, crop, clamp, realign when needed, module enables, CAMIF frame/window/subsample registers, composite masks, and CAMIF start/stop. Interrupt flow is status read/clear, reset/violation/halt handling, reg-update and SOF callbacks, composite done with PIX WM suppression, then WM done.

## State and Persistence
All state is common VFE in-memory state and volatile registers. UB size depends on VFE instance id: VFE0 and VFE1 have different RDI partition sizes.

## Dependencies and Integration Points
Depends on gen1 helper code, V4L2 pixel formats, CAMSS PM and media plumbing, and buffer queue helpers. It is selected by SoC resource tables for VFE 4.7 hardware.

## Risks and Test Signals
Register formulas differ subtly from 4.1, especially word-per-line and scaler phase. Realign only applies to packed YUV and must match xbar swap bits. Test both VFE instances, NV12/NV16 and packed YUYV variants, RDI0-2, CAMIF stop, composite and WM IRQs, bus overflows, QoS/DS writes, and no stale `reg_update` bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-4-7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-4-8.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-4-8.c

## Purpose
Implements VFE 4.8 gen1 ops for SDM845-class CAMSS. It is close to VFE 4.7 but uses another register map, equal UB size across instances, a WM command register for enable/disable, and specific QoS/data-shaper programming.

## Important APIs, Types, and Functions
Exports `vfe_ops_4_8` and `vfe_ops_gen1_4_8`. Key functions cover reset/halt, WM frame/line programming, bus reload, address programming, ping-pong status, RDI xbar, realign, RDI CID, register update, IRQ masks, demux/scale/crop/clamp, CAMIF, QoS/DS, ISR read, and violation read.

## Control Flow
Generic gen1 code calls the vtable. Start paths program bus write interface, WMs, UB, xbar/RDI or PIX pipeline modules, then issue register updates and CAMIF commands. `vfe_wm_enable()` writes enable/disable commands through `VFE_0_BUS_IMAGE_MASTER_CMD` and barriers before later commands. ISR dispatch matches 4.7: reset, violation, halt, per-line reg update, CAMIF/RDI SOF, composite done, and WM ping-pong done.

## State and Persistence
Uses generic `vfe_device` state and volatile VFE registers. `vfe_get_ub_size()` returns a common RDI UB partition regardless of VFE id.

## Dependencies and Integration Points
Integrates with gen1 helpers and V4L2 formats, CAMSS PM domains, buffer queues, and SoC resource tables selecting `vfe_ops_4_8`.

## Risks and Test Signals
WM enable semantics changed from bit set/clear to command values, so ordering barriers are important. Scale formulas use minus-one dimensions and can underflow on invalid zero dimensions if upstream validation fails. Test WM command ordering, RDI and PIX streams, realign for packed YUV, UB partitioning, QoS/DS values, CAMIF halt, and interrupt completion ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-4-8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-480.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-480.c

## Purpose
Implements VFE 480 ops for a newer RDI-focused generation with separate register offsets for full VFE and VFE-lite instances.

## Important APIs, Types, and Functions
Exports `vfe_ops_480`. Offset macros depend on `vfe_is_lite(vfe)`. Key helpers are `reg_update_rdi()`, bus IRQ mask helpers, `vfe_global_reset()`, `vfe_wm_start()`, `vfe_wm_stop()`, `vfe_wm_update()`, `vfe_reg_update()`, `vfe_enable_irq()`, `vfe_isr()`, and `vfe_isr_reg_update()`.

## Control Flow
Reset masks reset ack and writes hardware/register reset. WM start maps logical RDI to actual WM, configures frame increment, burst, image config, stride, packer, no frame drops, IRQ subsampling, and enables MIPI RAW WM. IRQ enable keeps masks for already reserved/on lines. ISR clears top status, handles reset ack, then on bus-top IRQ clears bus status, processes RDI register updates, and calls `vfe_buf_done()` for matching composite groups. Halt is delegated to generic output stop.

## State and Persistence
State is generic VFE v2 output state plus `vfe->reg_update`; actual full/lite differences are computed at access time. No persistent storage.

## Dependencies and Integration Points
Depends on generic VFE v2 helpers, `vfe_is_lite()`, PM-domain functions, vb2 queue helpers, and V4L2 pixel format state.

## Risks and Test Signals
`vfe_buf_done_480()` is a no-op in the ops table while the ISR directly calls generic `vfe_buf_done()`, so callers using the ops callback may not get completion. IRQ mask calculation loops over `MAX_VFE_OUTPUT_LINES` and must match resource line counts. Test full vs lite offsets, concurrent RDI lines, reset ack, reg-update completion, buffer completion path, and no stale IRQ masks after stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-480.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-680.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-680.c

## Purpose
Implements VFE 680 ops for very new CAMSS hardware where RDI streaming uses write clients and external CAMSS register-update plumbing, with no meaningful local global reset or top-level IRQ processing in this driver.

## Important APIs, Types, and Functions
Exports `vfe_ops_680`. Important functions are `vfe_global_reset()`, `vfe_disable_irq()`, `vfe_wm_start()`, `vfe_wm_stop()`, `vfe_wm_update()`, `vfe_reg_update()`, and `vfe_reg_update_clear()`. Register macros switch between full VFE and VFE-lite offsets and define bus write-client image config, MMU prefetch, frame-drop, IRQ subsample, and diagnostics.

## Control Flow
`vfe_global_reset()` simply completes `reset_complete` because this hardware has no local global reset path. WM start maps logical RDI to actual WM, programs image dimensions/stride, packer, frame increment, MMU prefetch, no-drop/no-subsample settings, disables local IRQs for RDI mode, and enables the write client. Buffer address updates write the current image address. Register updates call `camss_reg_update()` with clear=false/true instead of local VFE update registers.

## State and Persistence
State is generic VFE v2 output and queue state plus volatile hardware registers. There is no local IRQ state for RDI completion in this file; external CAMSS paths are expected to drive update behavior.

## Dependencies and Integration Points
Depends on `vfe_is_lite()`, CAMSS top-level `camss_reg_update()`, generic VFE v2 queue/output helpers, PM-domain helpers, and V4L2 pixel format state.

## Risks and Test Signals
The ISR is a stub returning handled and local IRQs are disabled in RDI mode, so integration with external interrupt/update handling is mandatory. `RDI_WM()` is documented as RDI-only and would be wrong for stats/AWB/BHIST clients. Test external register-update completion, full/lite offsets, MMU prefetch configuration, write-client enable/disable, address updates, and streaming without local IRQ completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-680.c -->
