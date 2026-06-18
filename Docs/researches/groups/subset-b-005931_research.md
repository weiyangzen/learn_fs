# subset-b-005931 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/op-common.h -->
# sources/distributed-fs/ceph-client/include/math-emu/op-common.h

Purpose: Provides the shared macro engine for GNU soft-fp operations after format-specific headers have defined exponent, fraction, and word-count parameters. It is the arithmetic core used by single, double, quad, and extended precision wrappers rather than a standalone C API.

Important APIs/types/functions: `_FP_DECL` declares canonical class/sign/exponent/fraction variables. `_FP_UNPACK_CANONICAL` classifies raw bitfields into `FP_CLS_NORMAL`, `FP_CLS_ZERO`, `FP_CLS_INF`, or `FP_CLS_NAN`, normalizing denormals and setting denorm/signaling-NaN exceptions. `_FP_PACK_CANONICAL` applies rounding, overflow, underflow, denormal packing, NaN quieting, and result inhibition. Arithmetic macros include `_FP_ADD`, `_FP_SUB`, `_FP_NEG`, `_FP_MUL`, `_FP_DIV`, `_FP_SQRT`, comparisons, integer conversions, and `FP_CONV`. The helper `__FP_CLZ` and `_FP_DIV_HELP_imm` support leading-zero count and word division.

Control flow: Every arithmetic macro switches on combined operand classes, handles NaN/Inf/zero special cases first, and only performs fraction math for normal operands. Add/sub aligns exponents, adds or subtracts fractions, detects cancellation, and renormalizes. Multiply delegates wide fraction product to `_FP_MUL_MEAT_*`; divide delegates quotient generation to `_FP_DIV_MEAT_*`; square root iterates through `_FP_SQRT_MEAT_*`.

State and persistence: State is compile-time macro state plus caller-local temporaries and `_fex` exception bits from `soft-fp.h`. No persistent storage exists.

Dependencies and integration: Depends on `op-1.h`, `op-2.h`, `op-4.h`, `op-8.h`, target `sfp-machine.h`, rounding mode macros, and format constants from `single.h`, `quad.h`, or siblings.

Risks and test signals: Risks are macro side effects, missing target meat macros, endian/word-size assumptions, exact exception semantics, denormal flush behavior, and unsigned shift edge cases. Test with IEEE edge vectors: signed zero arithmetic, NaN quieting, inf-invalid operations, denormal unpack/pack, directed rounding overflow, integer conversion saturation/truncation, and cross-word quad values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/op-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/quad.h -->
# sources/distributed-fs/ceph-client/include/math-emu/quad.h

Purpose: Defines IEEE 754 binary128/quad precision layout and public `FP_*_Q` macros for the generic soft-fp engine.

Important APIs/types/functions: Constants describe 113 fraction bits, 15 exponent bits, bias 16383, exponent max 32767, implicit bit, quiet-NaN bit, and overflow sentinel. `union _FP_UNION_Q` maps a `long double` to sign/exponent/fraction bitfields with separate 32-bit-word and 64-bit-word layouts. Public macros include `FP_DECL_Q`, raw and canonical unpack/pack variants, `FP_ADD_Q`, `FP_SUB_Q`, `FP_MUL_Q`, `FP_DIV_Q`, `FP_SQRT_Q`, comparisons, integer conversions, and `FP_FROM_INT_Q`.

Control flow: The header selects a four-word fraction implementation when `_FP_W_TYPE_SIZE < 64` and a two-word implementation on 64-bit words. Each public operation simply binds the quad format tag `Q` and the selected word count to the common machinery in `op-common.h` and the matching `op-N.h` primitives.

State and persistence: No runtime state is stored here. It establishes ABI-sensitive bitfield views and macro expansions used by callers' local variables.

Dependencies and integration: Requires `soft-fp.h`-provided `_FP_WORKBITS`, `_FP_W_TYPE_SIZE`, endian definitions, and fraction helpers. It is consumed by architecture math emulation routines implementing compiler/libgcc floating operations.

Risks and test signals: Risks include compiler bitfield packing, long-double ABI mismatch, endian errors, and different behavior on 32-bit versus 64-bit word targets. Test binary128 encode/decode across both layouts, NaN payload preservation, subnormal normalization, conversion to integer near 2^113, and operations where carries cross fraction-word boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/quad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/single.h -->
# sources/distributed-fs/ceph-client/include/math-emu/single.h

Purpose: Defines IEEE 754 binary32/single precision constants, raw representation, and `FP_*_S` macro aliases for the soft-fp operation core.

Important APIs/types/functions: `_FP_FRACBITS_S`, `_FP_EXPBITS_S`, `_FP_EXPBIAS_S`, `_FP_EXPMAX_S`, `_FP_QNANBIT_S`, `_FP_IMPLBIT_S`, and `_FP_OVERFLOW_S` configure the format. `union _FP_UNION_S` overlays a `float` with endian-sensitive sign, exponent, and fraction fields. Public macros cover declaration, raw/canonical unpack and pack, sign test, negation, add/subtract, multiply, divide, square root, compare/equality, integer conversion, and integer construction.

Control flow: All public operations delegate to one-word generic helpers: `_FP_UNPACK_RAW_1`, `_FP_PACK_RAW_1`, `_FP_UNPACK_CANONICAL(S,1,...)`, and `_FP_*` arithmetic macros. The header expects the target machine to supply single-precision multiply/divide meat macros.

State and persistence: Contains no persistent data. It defines local macro variables and uses caller-owned exception/rounding state from `soft-fp.h`.

Dependencies and integration: Includes no headers directly beyond the soft-fp inclusion context. It relies on `sfp-machine.h` for word types and on `op-1.h` and `op-common.h` for implementation.

Risks and test signals: Primary risks are endian bitfield correctness, insufficient `_FP_W_TYPE_SIZE`, and target-specific multiply/divide hooks. Test raw bit round-trips for normal, subnormal, signed zero, infinities, quiet/signaling NaNs, plus rounding and exception behavior for add/subtract cancellation and conversion boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/single.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/soft-fp.h -->
# sources/distributed-fs/ceph-client/include/math-emu/soft-fp.h

Purpose: Top-level GNU soft-fp configuration header. It defines guard/round/sticky work bits, rounding mode constants, exception bookkeeping defaults, classification constants, includes word-operation helpers, and exposes integer typedefs expected by `longlong.h`.

Important APIs/types/functions: `FP_DECL_EX`, `FP_INIT_ROUNDMODE`, `FP_HANDLE_EXCEPTIONS`, `FP_SET_EXCEPTION`, `FP_CLEAR_EXCEPTIONS`, `FP_CUR_EXCEPTIONS`, `_FP_ROUND_*`, `FP_CLS_*`, and `_FP_CLS_COMBINE` are the core public support macros. Rounding modes are nearest-even, toward zero, toward +inf, and toward -inf. Exception constants default to zero unless the architecture overrides them.

Control flow: Callers typically declare exceptions, initialize rounding mode, unpack operands with a format header, invoke arithmetic macros, pack the result, then handle exceptions. `_FP_ROUND` checks low work bits for inexactness and dispatches to the configured rounding strategy.

State and persistence: The only state is local `_fex` exception accumulation and macro-selected `FP_ROUNDMODE`; no global storage is introduced. `FP_INHIBIT_RESULTS` lets a target avoid writing results when traps are pending.

Dependencies and integration: Requires `<asm/sfp-machine.h>` for `_FP_W_TYPE`, `_FP_W_TYPE_SIZE`, and architecture policy; includes endian support, `op-1/2/4/8.h`, `op-common.h`, and `stdlib/longlong.h`. It integrates architecture math emulation with generic fraction primitives.

Risks and test signals: Risks include architecture overrides with incompatible exception bits, absent endian macros, and rounding mistakes in guard/sticky propagation. Test all rounding modes, trap/inhibit policies, denormal-zero policies, and builds on 32-bit and 64-bit word-size targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/soft-fp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/cadence/cdns-csi2rx.h -->
# sources/distributed-fs/ceph-client/include/media/cadence/cdns-csi2rx.h

Purpose: Declares a tiny V4L2 subdevice helper for Cadence CSI-2 receiver pixel-per-clock negotiation.

Important APIs/types/functions: `cdns_csi2rx_negotiate_ppc(struct v4l2_subdev *subdev, unsigned int pad, u8 *ppc)` negotiates the requested pixels-per-clock value for a source pad and returns zero or a negative errno.

Control flow: The caller supplies a subdevice, output pad, and mutable requested PPC. The implementation is expected to validate hardware/pad support and update `*ppc` with an accepted value.

State and persistence: No state is defined in the header. State lives in the V4L2 subdevice driver.

Dependencies and integration: Depends on `<media/v4l2-subdev.h>` and integrates Cadence CSI-2 RX bridge drivers with downstream media pipeline format negotiation.

Risks and test signals: Risks are invalid pad numbers, unsupported PPC values, and callers not handling modified requests. Test with all source pads, boundary PPC values, and media graph format negotiation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/cadence/cdns-csi2rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/cec-notifier.h -->
# sources/distributed-fs/ceph-client/include/media/cec-notifier.h

Purpose: Defines the notifier contract that lets HDMI connector/DRM/display drivers report CEC physical-address changes to CEC adapters.

Important APIs/types/functions: Registration APIs are `cec_notifier_conn_register`, `cec_notifier_conn_unregister`, `cec_notifier_cec_adap_register`, and `cec_notifier_cec_adap_unregister`. Update helpers are `cec_notifier_set_phys_addr`, `cec_notifier_set_phys_addr_from_edid`, `cec_notifier_parse_hdmi_phandle`, and inline `cec_notifier_phys_addr_invalidate`.

Control flow: HDMI-side code registers a notifier for a device/port tuple and pushes physical-address updates, often parsed from EDID. CEC adapter code registers with the same tuple and receives those updates through the CEC core. Refcounts keep the shared notifier alive until both sides unregister.

State and persistence: The opaque `struct cec_notifier` owns shared connector state and refcounting in the core. When CEC/notifier support is disabled, stubs return a sentinel non-NULL pointer for register calls and no-op updates.

Dependencies and integration: Depends on `<media/cec.h>`, `struct device`, EDID, device-tree `hdmi-phandle`, and optional `CONFIG_CEC_CORE`/`CONFIG_CEC_NOTIFIER`.

Risks and test signals: Risks include stale connector keys, missing unregister, disabled-config sentinel misuse, and EDID physical-address parse failures. Test multi-connector devices, refcount lifetime, invalidation on HPD loss, disabled-config builds, and phandle lookup error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/cec-notifier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/cec-pin.h -->
# sources/distributed-fs/ceph-client/include/media/cec-pin.h

Purpose: Provides the low-level bit-banging CEC pin framework interface for hardware that controls the HDMI CEC line directly instead of using a full CEC controller.

Important APIs/types/functions: `struct cec_pin_ops` supplies `read`, `low`, `high`, optional IRQ enable/disable, free/status, HPD/5V reads, and optional high-level `received` handling. `cec_pin_changed` reports interrupt-observed pin state changes. `cec_pin_allocate_adapter` creates a CEC adapter with monitor-all and monitor-pin capabilities added.

Control flow: A driver allocates a pin adapter, implements electrical line control callbacks, and calls `cec_pin_changed` from IRQ context when voltage changes. The core timing engine drives low/high transitions and decodes received bits.

State and persistence: Pin state is stored in `struct cec_adapter` and its optional `struct cec_pin`, not in this header. The ops table must remain valid for adapter lifetime.

Dependencies and integration: Depends on `media/cec.h` and integrates GPIO-like HDMI CEC implementations with the normal CEC character-device/core stack.

Risks and test signals: Risks are timing jitter, sleeping in IRQ path, incorrect open-drain high behavior, and stale ops lifetime. Test bit timing, arbitration, HPD/5V event propagation, IRQ and polling modes, and adapter delete cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/cec-pin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/cec.h -->
# sources/distributed-fs/ceph-client/include/media/cec.h

Purpose: Main kernel CEC core interface for HDMI Consumer Electronics Control adapters, filehandles, message/event queues, transmit completion, received-message injection, EDID physical-address parsing, and connector metadata.

Important APIs/types/functions: Key types are `cec_devnode`, `cec_data`, `cec_fh`, `cec_adap_ops`, and `cec_adapter`. Driver-facing APIs include `cec_allocate_adapter`, register/unregister/delete, `cec_s_log_addrs`, `cec_s_phys_addr`, `cec_s_conn_info`, `cec_transmit_msg`, `cec_transmit_done_ts`, `cec_transmit_attempt_done_ts`, `cec_received_msg_ts`, pin event queueing helpers, and EDID helpers. Inline helpers manage device references, driver data, logical-address tests, sink tests, registration state, and invalidation.

Control flow: Adapter drivers allocate and register an adapter with low-level ops. Userspace opens `/dev/cecX`; `cec_fh` tracks initiator/follower/monitor modes and queues events/messages. Transmits enter adapter queues, the core invokes `adap_transmit`, and drivers complete with timestamped done callbacks. Received messages are timestamped into the core and optionally passed to high-level callbacks.

State and persistence: `cec_adapter` holds mutex-protected adapter state, transmit and wait queues, kthreads, logical/physical addresses, monitor/follower counters, remote-control integration, connector info, debug counters, notifier/pin pointers, and device-node state. Nothing is persisted across driver removal.

Dependencies and integration: Depends on Linux device/cdev/fs/kthread/timer infrastructure, `linux/cec-funcs.h`, rc-core, optional notifier and pin frameworks, DRM connector info, and EDID parsing.

Risks and test signals: Risks include open/unregister races, queue overflow, wrong lock order, aborted transmit handling when physical address changes, disabled-core stubs, EDID bounds parsing, and CEC timing/retry compliance. Test registration lifetime, simultaneous filehandles, monitor/follower exclusivity, transmit completion statuses, queue limits, HPD/5V pin events, and EDID SPA extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/cec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/davinci/vpfe_types.h -->
# sources/distributed-fs/ceph-client/include/media/davinci/vpfe_types.h

Purpose: Platform-data definitions for TI DaVinci VPFE capture hardware interface wiring.

Important APIs/types/functions: `enum vpfe_pin_pol` encodes positive/negative signal polarity. `enum vpfe_hw_if_type` describes BT.656, BT.1120, raw Bayer, external-sync YCbCr 8/16-bit, and 10-bit BT.656. `struct vpfe_hw_if_param` groups interface type with horizontal and vertical polarity.

Control flow: Board/platform code fills `vpfe_hw_if_param`; the capture driver consumes it when configuring VPFE input timing and bus mode.

State and persistence: No runtime state. It is compile-time/platform configuration, guarded by `__KERNEL__`.

Dependencies and integration: Integrates old board-file style DaVinci media drivers with VPFE host configuration.

Risks and test signals: Risks are wrong polarity or bus-type selection producing unstable capture. Test each board mode with known video sources, sync polarity combinations, and raw/YCbCr bus formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/davinci/vpfe_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/davinci/vpif_types.h -->
# sources/distributed-fs/ceph-client/include/media/davinci/vpif_types.h

Purpose: Platform-data structures for TI DaVinci VPIF capture/display channels, subdevices, routing, and per-board callbacks.

Important APIs/types/functions: Defines channel maxima, `enum vpif_if_type`, `vpif_interface`, `vpif_subdev_info`, `vpif_output`, display channel/config structs, `vpif_input`, capture channel/config structs, and callback hooks such as `set_clock`, `setup_input_channel_mode`, and `setup_input_path`.

Control flow: Board data enumerates I2C subdevices, input/output routes, interface polarities, channel capabilities, and async subdevice connections. Capture/display drivers consume these tables during probe and when userspace selects inputs or outputs.

State and persistence: No internal runtime state. The structures persist as platform data owned by the board or platform driver.

Dependencies and integration: Depends on I2C board info, V4L2 input/output types, and V4L2 async connection pointers. Integrates VPIF with sensor/decoder/encoder subdevices.

Risks and test signals: Risks include mismatched routes, invalid I2C adapter IDs, incorrect async connection sizes, and board callbacks failing. Test multi-channel capture/display, input/output switching, clock programming, and async probe/unbind behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/davinci/vpif_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/demux.h -->
# sources/distributed-fs/ceph-client/include/media/demux.h

Purpose: Defines the hardware-independent DVB demux kABI used between low-level demux hardware/software implementations and DVB clients.

Important APIs/types/functions: Core types are `dmx_ts_feed`, `dmx_section_filter`, `dmx_section_feed`, callback typedefs `dmx_ts_cb` and `dmx_section_cb`, `dmx_frontend`, `dmx_demux_caps`, and `dmx_demux`. Feed methods set PIDs/types/timeouts, allocate/release section filters, and start/stop filtering. Demux callbacks open/close/write, allocate/release feeds, manage frontends, connect/disconnect inputs, and expose PES PIDs or private STC.

Control flow: A client opens a demux, allocates a TS or section feed, configures PID/filter parameters, starts filtering, then receives data through callbacks using one or two buffers for circular-buffer wrap. Frontend registration and connection determine whether TS data comes from memory or hardware.

State and persistence: Feed structures track filtering state, private pointers, CRC/section assembly buffers, and parent demux links. Demux state is implementation-owned and referenced through callback methods.

Dependencies and integration: Depends on DVB userspace `dmx.h`, list APIs, errno, and ktime. It is the foundation used by `dvb_demux.h`, `dmxdev.h`, network, CA, and device-node wrappers.

Risks and test signals: Risks include callback buffer lifetime, section CRC and wrap handling, overflow propagation, PID/filter resource exhaustion, frontend removal while connected, and unclear `get_stc` private behavior. Test allocation failures, concurrent feeds, memory write filtering, circular wrap callbacks, section timeouts, and connect/disconnect edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/demux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dmxdev.h -->
# sources/distributed-fs/ceph-client/include/media/dmxdev.h

Purpose: Defines the DVB demux character-device layer that exposes demux and DVR devices on top of `struct dmx_demux`, ring buffers, and optional VB2 mmap streaming.

Important APIs/types/functions: `enum dmxdev_type` differentiates section and PES filters. `enum dmxdev_state` tracks free, allocated, set, running, one-shot done, and timed-out filters. `dmxdev_feed`, `dmxdev_filter`, and `dmxdev` store feed lists, section/PES parameters, ring buffers, VB2 contexts, timers, locks, device nodes, capabilities, DVR frontend state, and release flags. APIs are `dvb_dmxdev_init` and `dvb_dmxdev_release`.

Control flow: Initialization registers demux and DVR DVB devices. Userspace ioctls allocate filters, set section or PES parameters, start feeds through `dmx_demux`, buffer data into `dvb_ringbuffer` or `dvb_vb2_ctx`, and transition states. Release tears down devices and active feeds.

State and persistence: Runtime state is per-filter and per-device: filter state machine, buffers, timers, mutex/spinlock, DVR buffer, mmap context, exit flag, and original frontend for DVR routing. No persistent storage exists.

Dependencies and integration: Depends on `dvbdev.h`, `demux.h`, `dvb_ringbuffer.h`, `dvb_vb2.h`, timers, wait queues, mutexes, spinlocks, and DVB `dmx.h` ioctl structures.

Risks and test signals: Risks include state transition bugs, timeout races, buffer overflow, mmap and read path divergence, duplex capability misreporting, and release while filters are active. Test one-shot and timed section filters, PES capture, DVR read/write, mmap streaming, poll behavior, and disconnect/release races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dmxdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/cx2341x.h -->
# sources/distributed-fs/ceph-client/include/media/drv-intf/cx2341x.h

Purpose: Common V4L2 control and firmware mailbox definitions for Conexant CX23415/6/8 MPEG encoder/decoder chips.

Important APIs/types/functions: `enum cx2341x_port` selects memory/streaming/serial output. `enum cx2341x_cap` advertises sliced VBI, TS, and AC3. `cx2341x_mpeg_params` mirrors all MPEG stream, audio, video, bitrate, mute, and filter controls. `cx2341x_mbox_func` abstracts firmware mailbox calls. Helper APIs update firmware from old/new params, query controls, get menus, process extended controls, fill defaults, log status, initialize/setup/busy-mark control handlers, and adjust 50 Hz mode. The file also enumerates encoder/decoder/OSD firmware command IDs and firmware names.

Control flow: Drivers initialize defaults/control handler, accept V4L2 MPEG controls, validate/update params, then `cx2341x_update` issues only changed settings through the mailbox callback. Handler ops provide driver-specific side effects for sampling frequency, audio mode, video encoding, and VBI format.

State and persistence: `cx2341x_handler` stores immutable capabilities/geometry, V4L2 control objects, private mailbox callback, and clustered controls. Firmware state lives in hardware and is synchronized from params.

Dependencies and integration: Depends on V4L2 controls and integrates ivtv/pvr-style bridge drivers with CX2341x firmware.

Risks and test signals: Risks include stale old/new params, busy control updates during capture, mailbox argument count mistakes, unsupported capability controls, and firmware command mismatches. Test defaults, all control clusters, 50/60 Hz geometry, AC3/TS/VBI capability gating, and mailbox traces for each changed control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/cx2341x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/cx25840.h -->
# sources/distributed-fs/ceph-client/include/media/drv-intf/cx25840.h

Purpose: Defines routing constants, output-format bitfields, GPIO/pad selectors, and platform data for cx25840-family audio/video decoder subdevices and related cx23885 pins.

Important APIs/types/functions: `enum cx25840_video_input` encodes composite, S-Video luma/chroma pairs, and explicit multi-channel frame input selections. `CX25840_VCONFIG_*` masks define video output formatting options such as BT.601/BT.656/VIP, bus width, raw VBI, ancillary data, task bit, active/valid signaling, clock gating, data-count mode, line counters, and clamp. Audio input, IO pin/pad/drive-strength enums, cx23885 pin/pad enums, and `cx25840_platform_data` for PVR-150 workaround complete the interface.

Control flow: Bridge drivers configure subdevice init/routing ops using encoded input IDs and VCONFIG bitfields. Firmware should be loaded lazily through `load_fw` or reset before relying on audio standard detection.

State and persistence: Header defines no live state; hardware state is programmed through V4L2 subdev ops. Platform data carries one board-specific workaround bit.

Dependencies and integration: Requires V4L2 subdev users and bit macros from kernel headers. It integrates analog capture bridge drivers with cx25840/cx23885 decoder configuration.

Risks and test signals: Risks include missing firmware load causing mono/audio detect failures, invalid S-Video luma/chroma combinations, register-bitfield misuse, and board-specific workaround misapplication. Test firmware load timing, every input route, output bus modes, raw VBI/ancillary options, GPIO/pad selections, and PVR-150 tuner variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/cx25840.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/exynos-fimc.h -->
# sources/distributed-fs/ceph-client/include/media/drv-intf/exynos-fimc.h

Purpose: Shared Samsung S5P/Exynos FIMC camera/media-pipeline definitions for inputs, bus types, formats, group IDs, and media pipeline operations.

Important APIs/types/functions: Defines `enum fimc_input`, `enum fimc_bus_type`, input-class macros, subdevice group IDs, `fimc_source_info`, notification `S5P_FIMC_TX_END_NOTIFY`, `fimc_fmt`, `exynos_media_pipeline_ops`, `exynos_video_entity`, `exynos_media_pipeline`, `vdev_to_exynos_video_entity`, and `fimc_pipeline_call`.

Control flow: Media graph entities use group IDs and source info to configure input muxes and bus formats. Video nodes call pipeline ops for prepare/unprepare/open/close/set_stream, with `fimc_pipeline_call` returning `-ENOENT` or `-ENOIOCTLCMD` when the pipeline/op is absent.

State and persistence: Pipeline state is carried by `exynos_media_pipeline`, embedded `media_pipeline`, video entity pointers, and driver-owned format tables. No persistence beyond device lifetime.

Dependencies and integration: Depends on media entity, V4L2 device, and media bus definitions. It integrates camera sensors, CSI receivers, FIMC/FLITE, writeback paths, and video nodes.

Risks and test signals: Risks are wrong bus/mux classification, format-plane metadata mismatches, aliasing writeback enum values, and missing pipeline ops. Test all input types, pipeline stream sequencing, single-frame notification, format table selection, and absent-op error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/exynos-fimc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/msp3400.h -->
# sources/distributed-fs/ceph-client/include/media/drv-intf/msp3400.h

Purpose: Documents and encodes routing bitfields for MSP3400-family analog TV audio processors.

Important APIs/types/functions: Macros select SCART and tuner inputs to DSP, choose DSP input for MAIN/AUX/SCART/I2S outputs, select SCART output sources, and build composite `input`/`output` arguments for V4L2 `s_routing`. `MSP_INPUT_DEFAULT` and `MSP_OUTPUT_DEFAULT` encode common reset/default routes.

Control flow: Bridge drivers pass packed routing values to the msp3400 subdevice. The driver decodes tuner, SCART, DSP output, and bypass selections to program internal audio routing.

State and persistence: No state in the header. Runtime routing state lives in the subdevice and chip registers.

Dependencies and integration: Integrates V4L2 bridge drivers with the msp3400 audio subdevice without including V4L2 headers directly.

Risks and test signals: Risks include selecting unsupported inputs/outputs for a chip revision, accidental mute/bypass, and bitfield overlap mistakes. Test routing matrices across chip families, default reset route, tuner/SCART/I2S combinations, stereo detection, and mute behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/msp3400.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/renesas-ceu.h -->
# sources/distributed-fs/ceph-client/include/media/drv-intf/renesas-ceu.h

Purpose: Platform-data interface for the Renesas CEU capture driver.

Important APIs/types/functions: `CEU_MAX_SUBDEVS` limits platform subdevices to two. `ceu_async_subdev` stores bus flags, bus width/shift, I2C adapter ID, and I2C address. `ceu_platform_data` carries the subdevice count and fixed subdevice array.

Control flow: Board/platform code fills CEU subdevice wiring; the CEU driver uses it to create async subdevice matches and configure parallel bus geometry.

State and persistence: Static platform data only; live capture and async state are in the CEU driver.

Dependencies and integration: Integrates legacy platform data with V4L2 async sensor discovery for Renesas CEU.

Risks and test signals: Risks are exceeding `CEU_MAX_SUBDEVS`, wrong bus shift/width, or bad I2C addresses. Test probe with zero/one/two subdevices, async bind/unbind, and capture on each declared bus layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/renesas-ceu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/s3c_camif.h -->
# sources/distributed-fs/ceph-client/include/media/drv-intf/s3c_camif.h

Purpose: Platform data for Samsung S3C24xx/S3C64xx CAMIF sensor wiring.

Important APIs/types/functions: `s3c_camif_sensor_info` embeds I2C board info, sensor clock frequency, media bus type, I2C bus number, bus polarity flags, and optional FIELD-signal usage. `s3c_camif_plat_data` adds sensor info plus `gpio_get`/`gpio_put` callbacks.

Control flow: Platform code provides sensor description and GPIO reservation callbacks. CAMIF probe/configuration uses this to register the sensor subdevice, program sensor clocking, and configure bus flags.

State and persistence: Configuration is static platform data; GPIO ownership and runtime capture state live in the CAMIF driver.

Dependencies and integration: Depends on I2C and V4L2 media-bus enums. Integrates old Samsung camera hosts with board-file sensor data.

Risks and test signals: Risks include invalid sensor clock, bus polarity mismatch, missing GPIO release, and wrong FIELD usage. Test probe/remove GPIO pairing, sensor I2C creation, clock rate, and frame capture with each bus flag combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/s3c_camif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/saa7146.h -->
# sources/distributed-fs/ceph-client/include/media/drv-intf/saa7146.h

Purpose: Core driver interface and register map for Philips SAA7146 PCI multimedia bridge devices.

Important APIs/types/functions: Provides MMIO access macros, debug macros, ISR clear, page-table and DMA structs, PCI extension descriptors, `saa7146_extension`, `saa7146_dev`, conversion helper `to_saa7146_dev`, core APIs for extension registration, I2C adapter preparation, format lookup, page-table allocation/build/free, vmalloc page-table helpers, GPIO control, and DEBI wait. It also defines I2C constants, GPIO modes, RPS commands/events, bit masks, register offsets, ISR masks, and inline interrupt-enable/disable helpers protected by `int_slock`.

Control flow: Extension modules register PCI IDs and probe/attach/detach callbacks. Core probe maps MMIO, initializes locks/DMA/I2C, registers extension support, and dispatches IRQ bits to extension and video/VBI layers. Page tables and RPS/DMA memory are built for streaming capture.

State and persistence: `saa7146_dev` owns PCI/MMIO state, V4L2 device/control handlers, spinlocks/mutexes, extension private data, video/VBI pointers, I2C DMA/wait state, and RPS DMA buffers. State lasts for the PCI device lifetime.

Dependencies and integration: Depends on PCI, I2C, V4L2, DMA/scatterlist, vmalloc/mm, IRQ, and architecture IO APIs. `saa7146_vv.h` layers video/VBI support over it.

Risks and test signals: Risks include register constant mistakes, interrupt mask races, DMA page-table lifetime, I2C timeout/retry behavior, and extension detach ordering. Test PCI probe/remove, IRQ enable/disable under load, I2C transfers, page-table mapping/unmapping, DEBI waits, and extension-specific IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/saa7146.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/saa7146_vv.h -->
# sources/distributed-fs/ceph-client/include/media/drv-intf/saa7146_vv.h

Purpose: Video/VBI layer definitions for SAA7146 bridge devices, covering DMA queues, pixel formats, standards, V4L2 ioctl hooks, resource locking, and capture programming helpers.

Important APIs/types/functions: Types include `saa7146_video_dma`, `saa7146_format`, `saa7146_standard`, `saa7146_buf`, `saa7146_dmaqueue`, `saa7146_vv`, `saa7146_ext_vv`, and `saa7146_use_ops`. APIs register/unregister video devices, queue/finish/advance buffers, handle timeouts, initialize/release VV support, program capture/DMA/HPS/GPIO, expose video/VBI ioctl and vb2 ops, and manage DMA resources. Defines resource bits, HPS source/sync, clipping modes, hardware pixel format encodings, planar detection, and byte-swap modes.

Control flow: Extension data advertises inputs, audio count, standards, flags, and optional callbacks. Capture queues hold `saa7146_buf` instances with per-plane page tables; buffer activation programs DMA/RPS, timer expiry marks failures, and IRQ completion advances queues.

State and persistence: `saa7146_vv` stores active VBI/video queues, formats, timers, sequence number, standard, flip/source/sync settings, and resource bitmask. Buffers own DMA page tables until completion/release.

Dependencies and integration: Depends on SAA7146 core, V4L2 ioctl/filehandle/common APIs, and videobuf2 DMA-SG. It bridges PCI core support to V4L2 capture devices.

Risks and test signals: Risks include buffer timeout races, resource leaks, incorrect planar/byte-swap programming, standard geometry mismatches, and shared setting semantics across opens. Test video and VBI streaming, queue cancellation, timeout recovery, resource contention, standard switching, clipping, and all advertised formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/saa7146_vv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/sh_vou.h -->
# sources/distributed-fs/ceph-client/include/media/drv-intf/sh_vou.h

Purpose: Platform-data interface for SuperH Video Output Unit boards.

Important APIs/types/functions: Bus polarity flags describe pixel clock, HSYNC, and VSYNC polarity. `enum sh_vou_bus_fmt` selects 8-bit, 16-bit, or BT.656 bus. `sh_vou_pdata` carries bus format, I2C adapter ID, encoder board info, and flags.

Control flow: Platform code supplies output encoder and bus wiring; the SH VOU driver configures output timing and creates/uses the I2C subdevice.

State and persistence: Static platform configuration only; runtime output state is in the VOU driver and connected subdevice.

Dependencies and integration: Depends on I2C board info and integrates SuperH VOU with external encoders.

Risks and test signals: Risks are bus-width and sync-polarity mismatches or missing encoder board data. Test each bus mode, sync polarity flags, I2C subdevice probe, and active video output timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/sh_vou.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/si476x.h -->
# sources/distributed-fs/ceph-client/include/media/drv-intf/si476x.h

Purpose: Common V4L2 control ID definitions for Silicon Labs SI476x radio receiver drivers.

Important APIs/types/functions: `enum si476x_ctrl_id` allocates private controls relative to `V4L2_CID_USER_SI476X_BASE`: RSSI threshold, SNR threshold, maximum tune error, harmonics count, diversity mode, and interchip link.

Control flow: The SI476x V4L2 driver registers these controls and translates control writes into MFD/radio commands; userspace reads/writes them through normal V4L2 control ioctls.

State and persistence: No state in the header. Control state is maintained by the V4L2 control handler and hardware/MFD layer.

Dependencies and integration: Depends on Linux V4L2 IDs and SI476x report definitions from the MFD subsystem.

Risks and test signals: Risks include ID collisions, unsupported firmware properties, and invalid threshold ranges. Test control enumeration, set/get behavior, range validation, event/report interaction, and builds with the MFD headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/si476x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/tea575x.h -->
# sources/distributed-fs/ceph-client/include/media/drv-intf/tea575x.h

Purpose: Shared V4L2/ALSA helper interface for Philips TEA5757/5759 AM/FM tuner chips.

Important APIs/types/functions: Defines IF constants, pin bits, `snd_tea575x_ops` for either direct value read/write or three-pin bit control, and `snd_tea575x` device state containing V4L2 device/file/video objects, chip capabilities, mute/stereo/tuned flags, hardware value, band/frequency, mutex, ops, private data, labels, control handler, and optional external init. APIs enumerate bands, get tuner state, perform hardware seek, initialize hardware, register/unregister helper, and set frequency.

Control flow: A card driver fills ops and state, calls `snd_tea575x_init`, and the helper exposes a radio video device. Tuning writes chip serial value via either direct or bit-level ops; status reads update stereo/tuned flags where possible.

State and persistence: `snd_tea575x` owns all runtime tuner state for the device lifetime. Hardware frequency/mute state persists in chip registers until reprogrammed or powered down.

Dependencies and integration: Depends on V4L2 controls, video device, V4L2 device, and file operations; often used by ALSA sound-card drivers with radio tuners.

Risks and test signals: Risks include incomplete ops combinations, unreadable data pin, mute capability mismatches, frequency unit mistakes, and AM/FM band errors. Test init/exit, FM/AM/Japan bands, mute, seek, direct and pin-based ops, and concurrent tuner ioctls under the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/drv-intf/tea575x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb-usb-ids.h -->
# sources/distributed-fs/ceph-client/include/media/dvb-usb-ids.h

Purpose: Central catalog of USB vendor/product IDs and convenience macros for DVB USB drivers.

Important APIs/types/functions: `DVB_USB_DEV(pid, vid)` and `DVB_USB_DEV_VER(pid, vid, lo, hi)` expand tokenized vendor/product macro names into `USB_DEVICE` or `USB_DEVICE_VER` table entries. The remainder of the file defines `USB_VID_*` vendor IDs and `USB_PID_*` product IDs for many DVB USB devices, including cold/warm firmware states.

Control flow: Individual USB DVB drivers include this header to build `usb_device_id` tables. On USB probe, kernel matching uses these constants to select the appropriate driver and sometimes distinguish pre- and post-firmware device identities.

State and persistence: No runtime state. It is a compile-time ID registry.

Dependencies and integration: Depends on `<linux/usb.h>` and integrates many DVB USB frontend/bridge drivers with USB core matching.

Risks and test signals: Risks include duplicate or incorrect IDs, swapped vendor/product tokens, missing warm IDs after firmware upload, and stale device naming. Test by compiling all including drivers, checking generated modalias tables, probing representative cold/warm devices, and comparing IDs to hardware descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb-usb-ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb_ca_en50221.h -->
# sources/distributed-fs/ceph-client/include/media/dvb_ca_en50221.h

Purpose: Defines the DVB Common Interface EN50221 conditional-access core interface between CI hardware drivers and the DVB CA device layer.

Important APIs/types/functions: Poll and IRQ flags describe CAM presence/change/ready and FR/DA events. `struct dvb_ca_en50221` contains module ownership, attribute-memory accessors, CAM control accessors, block-mode data read/write, slot reset/shutdown/TS-enable callbacks, slot status polling, driver private `data`, and core-private storage. APIs report CAM change, CAM ready, and FR/DA IRQs, plus initialize/release a CA device.

Control flow: A hardware driver fills callbacks and calls `dvb_ca_en50221_init` with flags and slot count. Slot access callbacks may run concurrently for different slots. Hardware IRQ handlers notify the core through the IRQ helpers; polling is used when CAM-change IRQs are unavailable.

State and persistence: Driver-private state hangs off `data`; core-private per-slot protocol/device state hangs off `private`. No persistent storage beyond device lifetime.

Dependencies and integration: Depends on DVB adapter/device core and Linux DVB CA userspace definitions. Integrates CAM slots with `/dev/dvb/adapterX/caY`.

Risks and test signals: Risks include callback concurrency, slot hotplug races, block transfer length handling, missing TS enable, and release during active CA sessions. Test multi-slot access, insertion/removal IRQs, ready and FR/DA events, userspace CA ioctls, polling fallback, and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb_ca_en50221.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb_demux.h -->
# sources/distributed-fs/ceph-client/include/media/dvb_demux.h

Purpose: Implements the software DVB demux-facing internal structures and exported filtering entry points built on top of the abstract `demux.h` API.

Important APIs/types/functions: Defines filter/feed type and state enums, PID/mask constants, `dvb_demux_filter`, `dvb_demux_feed`, and `dvb_demux`. Driver callbacks include `start_feed`, `stop_feed`, optional decoder write, CRC, and memcpy hooks. Exported APIs initialize/release demux internals and feed MPEG-TS buffers through software filtering: aligned 188-byte packets, resyncing 188-byte streams, 204-byte packets, and raw payload.

Control flow: Drivers configure capabilities, filter/feed counts, private data, and start/stop callbacks, then call `dvb_dmx_init`. Incoming packets enter one of the swfilter helpers, which selects active feeds by PID/type, handles continuity/section assembly, and invokes TS or section callbacks. `dvb_dmx_release` frees core-allocated arrays and continuity storage.

State and persistence: `dvb_demux` owns feed/filter arrays, frontend list, PES feed mappings, PID table, active feed list, TS staging buffer, mutex/spinlock, continuity storage, speed counters, users count, and legacy av7110 flags.

Dependencies and integration: Depends on `demux.h`, timers, ktime, mutexes, spinlocks, and DVB userspace PES/PID definitions. Used by hardware bridge drivers and `dmxdev`.

Risks and test signals: Risks include PID table bounds, continuity counter handling, TS resync on corrupt buffers, feed start/stop races, user count limits, and section CRC errors. Test init failure cleanup, feed allocation limits, corrupt sync bytes, 188/204/raw paths, discontinuity flags, CRC overrides, and concurrent start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb_demux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb_frontend.h -->
# sources/distributed-fs/ceph-client/include/media/dvb_frontend.h

Purpose: Main DVB frontend kABI for demodulator/tuner drivers, frontend registration, tuning algorithms, DVBv5 property cache, frontend lifecycle, and suspend/resume helpers.

Important APIs/types/functions: Types include tuning settings, tuner info, analog parameters, `dvbfe_algo`, `dvbfe_search`, `dvb_tuner_ops`, `analog_demod_ops`, `dvb_frontend_internal_info`, `dvb_frontend_ops`, `dtv_frontend_properties`, and `dvb_frontend`. APIs register/unregister/detach frontends, suspend/resume/reinitialize, and provide precise sleep helper. Ops cover tuner init/sleep/set_params/status/RF metrics, analog demod callbacks, digital demod set/get/read status/statistics, DiSEqC/SEC controls, I2C gate, TS bus, LNA, and custom search.

Control flow: Drivers instantiate `dvb_frontend` with ops and register it with a `dvb_adapter`. Userspace property ioctls update `dtv_property_cache`; the frontend core chooses hardware, software zig-zag, custom, or recovery tuning and calls demod/tuner ops. Lifecycle calls stop device nodes/kthreads before explicit detach releases tuner/demod/SEC resources.

State and persistence: `dvb_frontend` owns kref, ops, adapter pointer, private demod/tuner/frontend/SEC/analog data, cached properties/statistics, callback, ID, and exit reason. Cache persists while registered and is restored across resume where possible.

Dependencies and integration: Depends on DVB device core, I2C, module/refcounting, mutex/delay/slab, bitops, and Linux DVB frontend UAPI. Integrates demods, tuners, SEC/LNB control, analog hybrids, and media adapters.

Risks and test signals: Risks include inconsistent frequency units, stale property cache, wrong release ordering, I2C gate deadlocks, suspend/resume retune failures, legacy callback semantics, and statistics not updated on unlocked signals. Test each delivery system, DVBv3/v5 ioctls, custom search states, DiSEqC timing, detach after unregister, suspend/resume with SEC restoration, and tuner/demod error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb_frontend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb_net.h -->
# sources/distributed-fs/ceph-client/include/media/dvb_net.h

Purpose: DVB network interface wrapper for IP-over-DVB/MPE style data paths.

Important APIs/types/functions: `DVB_NET_DEVICES_MAX` is 10. With `CONFIG_DVB_NET`, `struct dvb_net` stores a DVB device, net_device array, per-device state, exit flag, demux pointer, ioctl mutex, and remove mutex. APIs are `dvb_net_init` and `dvb_net_release`. Without the config, a minimal stub struct and no-op/init-success functions are provided.

Control flow: The DVB adapter initializes DVB net with a demux. Userspace creates/removes network interfaces through DVB net ioctls; the implementation uses demux section/TS filters to feed network packets into Linux net devices. Release unregisters interfaces and the DVB device.

State and persistence: Runtime state includes registered net devices, in-use flags, exit/removal synchronization, and demux binding. No disk persistence.

Dependencies and integration: Depends on DVB device core, module infrastructure, net_device, and demux APIs. Integrates DVB adapters with Linux networking when enabled.

Risks and test signals: Risks include remove/ioctl races, exceeding device slots, stale demux filters, and disabled-config assumptions. Test interface create/delete, concurrent unplug and ioctl, max device count, packet receive path, and builds with and without `CONFIG_DVB_NET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb_ringbuffer.h -->
# sources/distributed-fs/ceph-client/include/media/dvb_ringbuffer.h

Purpose: DVB framework ring-buffer API for byte streams and packetized records used by demux, CA, and related character devices.

Important APIs/types/functions: `struct dvb_ringbuffer` stores data pointer, size, read/write offsets, error flag, wait queue, and spinlock. APIs initialize, query empty/free/available, reset/flush, read to user/kernel, write from user/kernel, and packet-write/read/dispose/next. Macros peek, skip, and write one byte. `DVB_RINGBUFFER_PKTHDRSIZE` is three bytes for packet length headers.

Control flow: Producers write bytes or packet records and wake waiters; consumers poll/read available data, possibly using packet iteration without advancing until dispose. Flush/reset adjusts read/write pointers, with a spinlock+wakeup variant for interrupt-safe paths.

State and persistence: State is entirely in `dvb_ringbuffer`: offsets, error, queue, and lock over caller-provided memory. Data is volatile and lost on reset/release.

Dependencies and integration: Depends on spinlocks and wait queues. Used by `dmxdev`, CA, and other DVB device implementations to bridge kernel callbacks and userspace reads.

Risks and test signals: Risks include wrap arithmetic, full/empty ambiguity, missing locking around macros, packet header corruption, user copy faults, and wakeup ordering. Test wraparound reads/writes, exact-full and exact-empty cases, packet iteration/dispose, concurrent producer/consumer, flush with waiters, and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb_ringbuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb_vb2.h -->
# sources/distributed-fs/ceph-client/include/media/dvb_vb2.h

Purpose: Videobuf2-based streaming I/O helper for DVB demux/DVR mmap buffer operations.

Important APIs/types/functions: Defines `enum dvb_buf_type`, `enum dvb_vb2_states`, `dvb_buffer`, and `dvb_vb2_ctx`. Context state includes VB2 queue, spinlock, pending buffer list, current buffer, offsets, state bitmask, buffer size/count, nonblocking flag, demux buffer flags, monotonic count, and name. APIs initialize/release, check streaming, fill buffers, poll, stream on/off, request/query/export/queue/dequeue buffers, and mmap. When `CONFIG_DVB_MMAP` is disabled, init/release succeed and streaming/fill/poll stubs return inactive results.

Control flow: Demux/DVR code initializes a context, userspace requests and queues buffers, stream_on starts filling, producer callbacks call `dvb_vb2_fill_buffer`, and userspace dequeues completed buffers with flags/count metadata.

State and persistence: All state is per `dvb_vb2_ctx`; queued buffers and counters persist until streamoff/release. No disk persistence.

Dependencies and integration: Depends on DVB demux UAPI buffer structs and VB2 core, DMA-contig, and vmalloc memory backends. Used by `dmxdev` for mmap capture paths.

Risks and test signals: Risks include state-machine misuse, disabled-config behavior divergence, buffer flag/count loss, nonblocking dequeue semantics, and fill/streamoff races. Test reqbufs zero/nonzero, qbuf/dqbuf order, mmap/export, poll, streamoff while filling, discontinuity flags, and builds without DVB mmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvb_vb2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvbdev.h -->
# sources/distributed-fs/ceph-client/include/media/dvbdev.h

Purpose: Core DVB adapter and device-node infrastructure for registering `/dev/dvb/adapterX/*` devices, media-controller links, generic file operations, usercopy ioctls, and frontend module attachment.

Important APIs/types/functions: Defines `DVB_MAJOR`, adapter count defaults, `DVB_UNSET`, `enum dvb_device_type`, module-parameter helper `DVB_DEFINE_MOD_OPT_ADAPTER_NR`, `dvb_adapter`, `dvb_device`, and `dvbdevfops_node`. APIs get/put device refs, register/unregister adapters and devices, remove/unregister devices, create media graphs, generic open/release/ioctl, `dvb_usercopy`, I2C module probe/release, and legacy `dvb_attach`/`dvb_detach`.

Control flow: Drivers register an adapter, then register frontend/demux/DVR/CA/net devices from templates. Generic open/release checks device validity and reader/writer/user counts. Generic ioctl copies user arguments, calls `kernel_ioctl`, and copies results back. Optional media-controller code links DVB entities. I2C helpers bind submodules; legacy attach dynamically requests symbols when enabled.

State and persistence: `dvb_adapter` tracks adapter number, device list, private data, module/device, mutually exclusive frontend state, locks, and optional media-controller objects. `dvb_device` tracks kref, fops, type/minor/id, open counters, wait queue, ioctl callback, optional media entities, and private data.

Dependencies and integration: Depends on Linux fs/poll/list/types, media-device, optional I2C and media controller. It is used by all DVB frontend, demux, CA, DVR, and network layers.

Risks and test signals: Risks include reference/open races, counter underflow, media graph mismatches, unregister while filehandles exist, ioctl copy-size bugs, and legacy module attach leaks. Test adapter numbering, multiple device types, RO/RW open limits, hot-unplug with open files, media graph creation, usercopy directions, I2C probe/release, and CONFIG_MEDIA_ATTACH variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/dvbdev.h -->
