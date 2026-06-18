# subset-b-001446 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/hw_shared.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/hw_shared.h

## Purpose

`hw_shared.h` is the common AMD Display Core hardware type header used by multiple virtual hardware blocks. It centralizes hardware topology limits, color/gamma lookup-table data shapes, shared pixel-processing enums, DisplayPort test-pattern enums, and compact audio-channel bit layout. It does not implement algorithms; it publishes stable data contracts used by IPP, DPP/transform, OPP, MPC, stream/timing encoders, and resource code.

## Important APIs, Types, And Functions

The header defines global sizing constants such as `MAX_PIPES`, `MAX_LINKS`, `MAX_DIG_LINK_ENCODERS`, `MAX_DWB_PIPES`, and HPO DP encoder limits. `pipe_topology_line`, `pipe_topology_snapshot`, and `pipe_topology_history` describe recorded pipe layout snapshots with phantom-pipe, plane, slice, stream, DPP, OPP, and TG identifiers. Color-management structures include `gamma_curve`, `curve_points`, `curve_points3`, `pwl_result_data`, `dc_rgb`, `tetrahedral_*`, `tetrahedral_params`, and `pwl_params`.

Shared enums cover line-buffer pixel depth, CSC adjustment type, IPP degamma/gamcor/output-format modes, expansion mode, gamut remap, OPP regamma, OPTC DSC mode, DP/controller test patterns, DP color space, test-pattern component depth, and LUT RAM selection. `default_adjustment`, `out_csc_color_matrix`, and `dc_bias_and_scale` carry color-conversion setup. `union audio_cea_channels` maps CEA speaker bits onto named channel flags.

## Control Flow

There is no runtime control flow. Include-time behavior is limited to the header guard and type publication. The key behavioral contract is that consumers can use the same enums and structures when programming different hardware blocks, avoiding divergent definitions for LUT layout, color-space setup, test patterns, and display topology logging.

## State And Persistence Behavior

The file creates no runtime state. Its persistent effect is ABI-like source compatibility inside DC: array sizes, enum numeric values, bit-vector encodings, and large LUT structures must remain consistent with hardware programming code and any state snapshots stored in DC state objects. `lb_pixel_depth` explicitly states that values are used as bit vectors, so numeric changes are behavioral.

## Dependencies And Integration Points

It depends on `os_types.h`, `fixed31_32.h`, and `dc_hw_types.h`. It is included by multiple hardware abstraction headers in this group, especially IPP, OPP, MPC, transform, stream encoder, and timing generator paths. Resource and debug code consume the topology snapshot structures when logging pipe layout changes.

## Risks And Test Signals

Risks are mostly compatibility risks: changing `MAX_*` constants can under-size or over-size arrays in resource pools; changing enum values can misprogram hardware registers; and large tetrahedral LUT arrays are memory-heavy and sensitive to dimension assumptions. Good test signals are clean AMDGPU display builds across DCE/DCN variants, color-management validation with PWL/3D LUT programming, DSC/test-pattern CTS paths, pipe topology logging, and audio speaker-channel mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/hw_shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/ipp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/ipp.h

## Purpose

`ipp.h` defines the input pixel processor abstraction used by older DC hardware paths. IPP handles cursor programming, input format expansion/conversion, prescale, input LUT programming, and degamma setup before pixels move further into the display pipeline.

## Important APIs, Types, And Functions

`struct input_pixel_processor` stores the DC context, hardware instance, and `ipp_funcs` vtable. `enum ipp_prescale_mode` and `struct ipp_prescale_params` describe signed/unsigned fixed or float prescale programming. `enum ovl_color_space` provides overlay color-space selectors. The `ipp_funcs` table includes cursor position/attribute programming, full bypass, generic IPP setup, DCE-specific prescale, input LUT programming, degamma mode selection, degamma PWL programming, and destruction.

## Control Flow

The header defines a classic hardware object pattern: resource construction creates an IPP object, assigns an ASIC-specific vtable, and higher layers call through `ipp->funcs`. Typical setup moves from cursor updates and input-format setup to optional LUT/degamma programming. `ipp_full_bypass` is the escape path for disabling processing.

## State And Persistence Behavior

The IPP object persists as part of the resource pool. Runtime state lives in hardware registers and in the chosen function table, not in this header. Programming cursor attributes, LUTs, and degamma settings persists until the pipe is reprogrammed, disabled, or reset.

## Dependencies And Integration Points

The file depends on `hw_shared.h` and `dc_hw_types.h` for pixel format, expansion, color matrix, cursor, and PWL structures. It integrates with transform/DPP-era code because `transform.h` exposes compatible IPP function hooks while newer hardware folds IPP behavior into DPP/transform blocks.

## Risks And Test Signals

Main risks are NULL vtable slots on ASICs that do not implement a feature, mismatched PWL data, and incorrect bypass/setup ordering during modeset. Test signals include cursor movement/format validation, input LUT and degamma IGT or color tests, plane format conversion checks, and suspend/resume or hotplug modesets that reapply IPP state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/ipp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/link_encoder.h

## Purpose

`link_encoder.h` defines the hardware abstraction for physical display link encoders. It covers legacy DIO/DIG, analog/LVDS/TMDS/DP encoders, USB-C/DPIA cases, and HPO DP2 link encoders used for 128b/132b DisplayPort paths.

## Important APIs, Types, And Functions

`encoder_init_data` carries connector, HPD, encoder object, analog encoder, channel, transmitter, and context data used during construction. `encoder_feature_support` is a bitfield-backed capability set for HBR2/HBR3/TPS3/TPS4, HDMI 6G, DP2/UHBR rates, USB-C, deep color, YCbCr 4:2:0, and FEC. `struct link_encoder` stores the vtable, AUX offset, IDs, output-signal mask, preferred engine, features, transmitter, HPD GPIO/source, and USB-C combo PHY flag.

`link_encoder_funcs` covers state readout, output validation, hardware init/setup, enabling TMDS/DP/MST/LVDS/analog/DPIA, disabling outputs, DP lane settings and PHY patterns, MST allocation updates, PSR secondary packets, DIG frontend routing, HPD enable/disable/state/filtering, FEC control, maximum link capability, DIG mode, DIO PHY mux selection, and destruction. `link_enc_assignment` tracks dynamic endpoint-to-engine ownership. HPO DP support is represented by `hpo_dp_link_encoder`, `hpo_dp_link_encoder_funcs`, `hpo_dp_link_enc_state`, and DP2 training/test-pattern enums.

## Control Flow

Modeset/link training code selects or dynamically assigns a link encoder, initializes it, sets signal mode, enables the appropriate physical output, then programs DP lane settings or HDMI/TMDS clocking. MST and DP2 paths update allocation tables and VCP throttling after the link is active. Disable paths call signal-specific shutdown and may release dynamic assignments.

## State And Persistence Behavior

Persistent state is split between the software object fields and hardware registers. Capability flags persist for the lifetime of the link encoder object. Dynamic assignment entries persist in `resource_context` across current and transient states. FEC-ready/active state and training completion are read from hardware into `link_enc_state` or `hpo_dp_link_enc_state`.

## Dependencies And Integration Points

The header depends on graphics-object, signal, and DC type definitions. It integrates with `link_enc_cfg.h` for dynamic DIG assignment, `link_hwss.h` for signal-specific link sequencing, DP link-training code, MST payload management, HPD handling, and resource-pool construction.

## Risks And Test Signals

Risks include stale capability flags, incorrect encoder-to-endpoint assignment during transient commits, mismatched DP2/HPO versus DIO paths, FEC readiness races, and HPD filter differences. Test signals include DP/HDMI/eDP link training, MST payload changes, USB4 DPIA links, FEC enablement, DP2 UHBR modes, hotplug storms, suspend/resume, and link-status readback after modesets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/mcif_wb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/mcif_wb.h

## Purpose

`mcif_wb.h` defines the memory-controller interface for display writeback. It abstracts MCIF writeback enablement, buffer programming, arbitration, IRQ setup, warmup, and frame dumping for DWB output paths.

## Important APIs, Types, And Functions

`enum mmhubbub_wbif_mode` selects packed RGB/FP16 and planar 4:2:0 8/10 bpc modes. `mcif_arb_params` holds watermark, slice, timing, max scaled time, and DRAM speed-change duration settings. `mcif_irq_params` controls software, slice, overrun, and VCE interrupt enables. `mcif_wb_frame_dump_info` captures dump size, dimensions, pitches, and format. `struct mcif_wb` stores vtable, context, and instance. `mcif_wb_funcs` includes warmup, enable/disable, buffer config, arbitration config, IRQ config, and `dump_frame`.

## Control Flow

DWB users configure destination buffers and arbitration before enabling MCIF. IRQs may be configured to signal slices or overruns. `dump_frame` reads or transforms captured luma/chroma buffers into destination buffers according to output format and dimensions.

## State And Persistence Behavior

The object carries instance identity only. Runtime persistence is in MCIF/DWB registers and programmed frame buffers. Arbitration and watermark settings persist until rewritten, and dump metadata describes a captured frame rather than long-lived driver state.

## Dependencies And Integration Points

The header depends on `dc_hw_types.h` for DWB scaler, warmup, and buffer parameter types. It integrates with DWB resource blocks, MPC DWB muxing, memory hub arbitration, and debug/capture workflows that dump frames.

## Risks And Test Signals

Risks include incorrect pitch/format handling, stale buffer addresses, underflow/overrun IRQ configuration errors, and bad watermarks during p-state or DRAM changes. Test signals include DWB capture in packed and planar modes, overrun interrupt tests, frame dump integrity, and stress during clock or memory speed transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/mcif_wb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/mem_input.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/mem_input.h

## Purpose

`mem_input.h` defines the older memory-input hardware abstraction used to feed display pipes from memory. It covers tiling, page flip, watermark, stutter, blanking, compression, and surface-address programming for DCE-era front-end memory blocks.

## Important APIs, Types, And Functions

The file defines request modes, stutter modes, tiling settings, DCP GRPH surfaces, MI register update callbacks, and `struct mem_input` with context, instance, and vtable. The function table includes allocation/destruction style hooks plus register programming for addresses, tiling, surface configuration, memory requests, page flips, watermarks, stutter, blanking, and compression behavior.

## Control Flow

Plane programming code configures tiling and surface parameters, programs base/flip addresses, updates memory request parameters, and may enable stutter or compression after the pipe is ready. Page-flip paths use the flip-specific hooks and depend on interrupt service paths to signal completion.

## State And Persistence Behavior

The software object is stable in the resource pool, while programmed surface addresses and memory-controller settings persist in hardware until the next page flip or modeset. Watermark and stutter settings persist across frames and interact with power-management decisions.

## Dependencies And Integration Points

The header depends on DC hardware types and is a predecessor to HUBP-style memory input in DCN. It integrates with resource mapping, plane state, IRQ page-flip sources, and power-management watermarks.

## Risks And Test Signals

Risks include stale surface addresses, tiling mismatches, incorrect blanking before address changes, and power-saving watermarks that cause underflow. Test signals include page-flip completion, tiled/compressed framebuffer scanout, stutter enablement, underflow logs, and multi-plane modesets on ASICs that still use this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/mem_input.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/mpc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/mpc.h

## Purpose

`mpc.h` defines the Multiple Pipe/Plane Combiner abstraction. MPC blends DPP outputs into OPP outputs, supports flexible M-input to N-output composition, programs background color, stereo mixing, DWB routing, output CSC/gamma, gamut remap, and newer movable color-management LUT blocks.

## Important APIs, Types, And Functions

Constants define `MAX_MPCC`, `MAX_OPP`, and `MAX_DWB`. Blend and color enums include `mpc_output_csc_mode`, `mpcc_blend_mode`, `mpcc_alpha_blend_mode`, movable CM location, and `MCM_LUT_ID`. Configuration structs cover 3D LUT fast-load (`mpc_fl_3dlut_config`), LUT parameters (`mcm_lut_params`), blending (`mpcc_blnd_cfg`), gamut adjustment, RMCM register snapshots, stereo mix, denorm clamp, and DWB flow control.

`struct mpcc` is the node for an MPC tree and stores MPCC ID, DPP ID, bottom link, blend/stereo config, and shared-bottom state. `struct mpc_tree` associates a tree with an OPP and the top MPCC list. `struct mpc` owns the vtable, context, MPCC array, blender PWL params, and CM bypass flag. `mpc_funcs` is large: it reads state, inserts/removes planes in OPP or DWB trees, initializes MPCCs, updates blending, locks cursors, waits/asserts idle, initializes from hardware, programs denorm/output CSC/output gamma, controls MPC memory power, sets DWB muxes, programs output rate control, gamut remap, 1D/shaper/3D LUTs, RMU acquire/release, background color, low-power mode, movable CM location, fast-load status, and RMCM sequential programming.

## Control Flow

Composition control flows through tree mutation: allocate/select MPCC, insert it into an OPP or DWB tree, program blend/stereo/background settings, and wait for idle before reconnecting. Color programming either uses classic output gamma/CSC hooks or newer RMU/RMCM hooks for shaper and 3D LUT operation. DWB capture routes through MPC muxes. Removal detaches MPCCs and returns them to idle.

## State And Persistence Behavior

MPC state is both software topology and hardware mux state. The `mpcc_array` mirrors physical MPCC nodes, while hardware registers define active links, LUT RAM banks, RMU ownership, DWB muxes, and memory power. LUT programming is persistent and banked; RMU acquire/release must remain synchronized with MPCC ownership.

## Dependencies And Integration Points

The file depends on `dc_hw_types.h`, `hw_shared.h`, `transform.h`, and `dc_types.h`. It integrates with resource pipe topology code, OPP/OPTC timing paths, DPP/transform output, DWB, color management, cursor locking, and debug state dump paths.

## Risks And Test Signals

Risks include MPCC tree corruption, idle wait failures, incorrect blend order, shared-bottom DWB/OPP mistakes, RMU ownership leaks, LUT bank mismatches, and underflow during reconnect. Test signals include multi-plane blending, ODM/MPC slice composition, DWB capture, cursor locking across planes, color-management PWL/3D LUT tests, RMCM fast-load status, and underflow register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/mpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/opp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/opp.h

## Purpose

`opp.h` defines the Output Plane Processor abstraction. OPP formats blended pixels for display output, handling formatter setup, clamping, bit-depth reduction, dithering, stereo formatting, display pattern generation, blank colors, ABM-facing state, CRC/debug readout, and the interface between MPC and OPTC.

## Important APIs, Types, And Functions

The header defines clamping ranges and `clamping_and_pixel_encoding_params`, `bit_depth_reduction_params` with truncation, spatial dither, and temporal modulation bitfields, wide-gamut regamma modes, gamma helper structures, hardware adjustment ranges, overlay CSC adjustment items, OPP buffer segmentation, and `dcn_opp_reg_state`. `struct output_pixel_processor` stores context, instance, regamma parameters, MPC tree params, pending MPCC disconnect flags, vtable, and dynamic expansion mode.

`opp_funcs` includes formatter programming, dynamic expansion, bit-depth reduction, underlay adjustment range lookup, destruction, stereo programming, pipe clock control, pattern generator programming, DPG dimension/pending/blank-color handling, left-edge extra pixel setup/readback, and register state readout.

## Control Flow

During stream enablement, resource/hardware sequencing programs OPP format according to color depth and pixel encoding, applies dithering or truncation, configures stereo or test pattern state when needed, and coordinates with MPC/OPTC for pipe connection. DPG operations can blank or generate patterns independent of normal stream data.

## State And Persistence Behavior

OPP software state tracks regamma params, MPC tree parameters, disconnect-pending MPCCs, and dynamic expansion. Hardware state persists in formatter, DPG, ABM, DSC forwarding, CRC, and OPP buffer registers until reprogrammed.

## Dependencies And Integration Points

The header includes `hw_shared.h`, `dc_hw_types.h`, `transform.h`, and `mpc.h`. It integrates with MPC composition, timing generator output, ABM, test-pattern/CTS code, and debug register dumps.

## Risks And Test Signals

Risks include wrong dither depth, clamping range errors, stale disconnect flags, incorrect extra-pixel programming for YCbCr/ODM, and blank/pattern state leaking into normal scanout. Test signals include color-depth modes, DP/HDMI test patterns, stereo modes, CRC captures, ABM-enabled panels, and visual checks for dithering/clamping artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/opp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/optc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/optc.h

## Purpose

`optc.h` defines the DCN Output Pipe Timing Combiner wrapper around the generic timing generator. OPTC combines ODM and OTG responsibilities: mapping OPP inputs into display output segments and generating timing signals.

## Important APIs, Types, And Functions

`struct optc` embeds `struct timing_generator base`, register/shift/mask tables, OPP count, timing limits, blank/sync limits, vstartup/vupdate/vready/pstate offsets, original patched timing, signal type, and max frame count. It declares `optc1_read_otg_state()` for reading OTG state into the shared timing-generator state struct.

## Control Flow

ASIC-specific constructors create an OPTC by filling the embedded timing-generator vtable and register tables. Higher layers call the base timing-generator functions, while implementation code uses the extra OPTC fields for limits, ODM segment count, DSC mode, and vupdate/pstate programming.

## State And Persistence Behavior

`optc` stores persistent software limits and the last patched timing information. Hardware state lives in OTG/ODM registers and can be read back through state-dump hooks.

## Dependencies And Integration Points

The file depends on `timing_generator.h`. It integrates with OPP output routing, ODM combine/split resource logic, DSC timing configuration, vblank/vupdate IRQ programming, and debug readout.

## Risks And Test Signals

Risks include invalid timing limits, stale original timing after patching, ODM segment mismatches, and incorrect vupdate/pstate offsets. Test signals include timing validation, ODM combine modes, DSC modes, vblank/vline IRQs, frame-count readback, and DCN register state dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/optc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/panel_cntl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/panel_cntl.h

## Purpose

`panel_cntl.h` defines the panel-control abstraction used for embedded panels. It centralizes panel power, backlight, and panel-specific control hooks behind a small DC hardware object.

## Important APIs, Types, And Functions

The header defines `struct panel_cntl` with context, instance, stored state, and `panel_cntl_funcs`. The function table covers panel control destruction and panel/backlight operations such as hardware initialization, power control, backlight enabling, PWM/backlight level programming, and state reads depending on ASIC implementation.

## Control Flow

eDP enablement sequences typically power the panel, wait required T7/T9/T12 intervals in link/panel code, enable backlight PWM or AUX backlight, then set brightness. Disable paths reverse brightness/backlight/panel power ordering.

## State And Persistence Behavior

The object persists in the resource pool and may cache current panel/backlight state. Hardware state persists in panel power and PWM/backlight registers or firmware-controlled panel state.

## Dependencies And Integration Points

Panel control integrates with eDP link service functions, DMUB panel replay/PSR flows, backlight exports to DRM, and power sequencing in DPMS and suspend/resume.

## Risks And Test Signals

Risks include incorrect panel power sequencing, brightness scaling bugs, missing waits, and NULL hooks on unsupported ASICs. Test signals include eDP boot display, backlight sysfs/DRM brightness changes, suspend/resume, PSR/replay transitions, and panel power-off/on hot paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/panel_cntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/pg_cntl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/pg_cntl.h

## Purpose

`pg_cntl.h` defines a power-gating controller abstraction for display hardware blocks. It gives DC a vtable for enabling, disabling, and querying power-gated domains without baking register details into common resource code.

## Important APIs, Types, And Functions

The file defines `struct pg_cntl` with context, instance, and a `pg_cntl_funcs` table. The function table provides block power-on/off and state-related callbacks implemented by ASIC-specific code.

## Control Flow

Resource or hardware-sequencing code calls the power-gating callbacks before programming a block that may be gated and after disabling unused resources. The abstraction lets ASIC implementations handle register handshakes and polling internally.

## State And Persistence Behavior

Software state is minimal. Persistent behavior is hardware power state: gated blocks lose or ignore register programming until powered, and ungated blocks consume power until the controller gates them again.

## Dependencies And Integration Points

This interface integrates with display resource construction, block initialization, low-power modes, and memory/LUT power controls such as MPC memory power.

## Risks And Test Signals

Risks include programming blocks while gated, failing to gate unused blocks, and missing wait/ack sequences. Test signals include runtime power-management counters, suspend/resume, modeset after idle, display underflow after ungating, and register access warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/pg_cntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/stream_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/stream_encoder.h

## Purpose

`stream_encoder.h` defines the stream encoder abstraction that converts DC stream timing and pixel data into protocol-specific stream attributes for DP, HDMI, DVI, LVDS, and HPO DP. It also handles audio packet setup, info packets, blank/unblank, DSC PPS packets, ODM combine, FIFO control, and stream-to-link mapping.

## Important APIs, Types, And Functions

The header defines DP pixel encoding and component depth enums, audio clock info, stream encoder state, DP PHY pattern state, and `struct stream_encoder`. `stream_encoder_funcs` includes DP/HDMI/DVI/LVDS attribute setup, throttled VCP sizing, HDMI and DP info packet updates/stops, immediate SDP, DP blank/unblank, audio mute/setup/enable/disable, stereo sync, AV mute, DIG-to-OTG connection, stream enable, reset/readback, DSC config and PPS packet programming, dynamic metadata, ODM combine, FIFO level/control, stream-to-link mapping, and pixels-per-cycle queries.

HPO DP support is represented by `struct hpo_dp_stream_encoder`, `hpo_dp_stream_encoder_state`, and `hpo_dp_stream_encoder_funcs`, with DP2 stream enable/blank/disable, attributes, SDP/info packets, DSC PPS, stream-link mapping, audio, state readout, and hblank minimum symbol width.

## Control Flow

During enablement, stream setup programs attributes from `dc_crtc_timing`, maps the stream encoder to OTG/link encoder, emits protocol info packets, configures DSC when used, sets up audio, and unblanks. Disable paths blank the stream, stop packets/audio, and may disable FIFO or reset attributes.

## State And Persistence Behavior

The software object stores identity and vtable; protocol state persists in stream encoder registers and packet RAM. HPO stream state readback exposes enabled state, mapping, MSA timing, ODM, and DSC status.

## Dependencies And Integration Points

The file depends on audio types and `hw_shared.h`. It integrates with link encoders, `link_hwss` sequencing, timing generators, audio resources, DSC code, MST bandwidth allocation, HDR/dynamic metadata, and DP/HDMI compliance tests.

## Risks And Test Signals

Risks include packet programming races, wrong pixel encoding/depth, audio N/CTS errors, stale DSC PPS packets, bad stream-link mapping during transient link encoder assignment, and FIFO under/overflow. Test signals include DP/HDMI bring-up, audio playback, HDR metadata, DSC displays, MST streams, DP2/HPO modes, blank/unblank transitions, and protocol compliance test patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/stream_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/timing_generator.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/timing_generator.h

## Purpose

`timing_generator.h` defines the generic timing generator interface used by DCE CRTC and DCN OTG/OPTC implementations. It validates/programs timings, drives CRTC enable/disable, blanking, interrupts, global swap lock, DRR, CRC, DSC, ODM, and timing/debug readback.

## Important APIs, Types, And Functions

Types include CRTC position, global-swap-lock parameters, DRR and long-vtotal settings, CRTC state, keepout/stereo flags, CRC selection and parameters, OTG output mux destinations, timing synchronization mode, OTG/OPTC register-state structures, and the `timing_generator` object. `timing_generator_funcs` is the main API and covers timing validation/programming, vertical interrupt setup, CRTC enable/disable and phantom CRTC handling, position/frame count/scanout, blank colors, VGA disable, global swap lock, reset triggers, DRR/vtotal controls, static screen control, test patterns, `arm_vert_intr`, global sync, OPTC clock, stereo, DWB source, OPTC source, CRC configure/read, manual trigger, hardware timing readback, VTG params, DSC config/status, ODM bypass/combine/source segments, h-timing division, GSL, output mux, vblank alignment, long vtotal, double-buffer pending waits, vupdate keepout, lock status, OTG/OPTC register readout, and PWA frame sync.

## Control Flow

Modeset code validates timing, programs it with vready/vstartup/vupdate/pstate offsets, enables the CRTC/OTG, connects output muxes, and configures optional DSC/ODM/DRR/GSL state. IRQ code can arm vertical interrupts through the vtable before enabling interrupt masks. Disable paths blank, wait for pending updates, disable/reset, and optionally handle phantom pipes.

## State And Persistence Behavior

Timing generator objects persist in the resource pool. Hardware state includes active timing registers, counters, locks, blank colors, DRR ranges, CRC enablement, DSC mode, ODM mapping, and interrupt windows. State readout structs provide debug snapshots for reconstruction after hardware init or failures.

## Dependencies And Integration Points

The header depends on DC BIOS, CRTC timing, hardware color, and DSC definitions. It integrates with OPP/OPTC, IRQ vblank/vline setup, resource pipe topology, VRR/DRR, CRC debug, DSC, ODM, and global sync across multiple displays.

## Risks And Test Signals

Risks include invalid timing acceptance, lock/unlock deadlocks, missed vblank/vupdate interrupts, ODM segment errors, DRR limit bugs, and CRC/DSC state leaks. Test signals include modesets across timing ranges, VRR/DRR tests, vblank interrupt delivery, CRC captures, ODM combine, DSC modes, suspend/resume, and register-state dumps after underflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/timing_generator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/transform.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/transform.h

## Purpose

`transform.h` defines the transform/DPP-side abstraction for scaling, line-buffer setup, gamut/CSC adjustment, regamma/degamma, input LUTs, cursor attributes, and scaler filter selection. It bridges older transform naming with newer DPP capabilities.

## Important APIs, Types, And Functions

The file defines `struct transform`, colorimetry and AVI infoframe-related enums, graphics gamut adjustment type, CSC adjustment, overscan, scaling ratios, sharpness, line-buffer parameters, scaler initialization, and `scaler_data`. `transform_funcs` includes reset, scaler programming, pixel-storage depth, optimal tap calculation, gamut remap, OPP CSC default/adjustment, regamma LUT power/config/programming, regamma mode, IPP degamma/input LUT/setup/bypass, and cursor attributes.

It also declares scaler filter selectors such as `get_filter_2tap_16p`, `get_filter_4tap_64p`, and higher-tap 64-phase filters. `dpp_caps` exposes scaler processing format, line-buffer partition limits, and an ASIC-specific partition calculator.

## Control Flow

Plane programming computes scaler ratios/taps and line-buffer settings, asks the transform implementation for optimal taps, programs scaler/filter state, sets pixel storage depth, and applies color transforms/LUTs. Bypass hooks are used when no transform work is required.

## State And Persistence Behavior

Transform object state is minimal, but programmed scaler, line buffer, LUT, CSC, degamma, and cursor state persists in DPP/transform hardware until reprogrammed. Filter tables are read-only data selected by ratio and tap count.

## Dependencies And Integration Points

The header depends on `dc_hw_types.h`, fixed-point math, cursor/gamma types, and shared color enums. It integrates with resource scaling validation, DPP construction, MPC/OPP color management, cursor programming, and infoframe colorimetry decisions.

## Risks And Test Signals

Risks include wrong tap selection, line-buffer partition miscalculation, color-space mismatch, LUT bank errors, and cursor attribute regressions. Test signals include scaled planes, rotation/viewport cases, cursor on scaled surfaces, color-management tests, scaler filter visual quality, and underflow checks with high-bandwidth scaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/transform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/vmid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/vmid.h

## Purpose

`vmid.h` defines the VMID hardware abstraction for display virtual memory contexts. It lets DC set page-table base/range and invalidate or manage VMID state used by GPU virtual-address scanout paths.

## Important APIs, Types, And Functions

The file defines `struct vmid` with context, instance, and `vmid_funcs`. The vtable exposes VMID setup and invalidation style operations for page-table address/range programming and hardware synchronization, implemented by ASIC-specific VM helpers.

## Control Flow

When a plane uses GPU virtual addressing, resource or VM helper code programs a VMID with page-table information before scanout. Updates must occur before the hubp/memory input consumes the virtual address, and invalidation must be coordinated with page-table changes.

## State And Persistence Behavior

VMID state persists in hardware VM registers and affects address translation for display fetches. Software object state is only context/instance/vtable.

## Dependencies And Integration Points

The header integrates with `vm_helper.h`, resource pools, GPUVM/page-table code, and HUBP/memory input programming. It is part of the path that keeps display scanout coherent with memory-management state.

## Risks And Test Signals

Risks include stale page tables, wrong VMID assignment, missing invalidation, and scanout faults. Test signals include GPUVM-backed framebuffer scanout, page-table updates during flips, virtual-address fault logs, multi-plane VMID use, and suspend/resume with active framebuffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/vmid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/vpg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/vpg.h

## Purpose

`vpg.h` defines the Video Packet Generator abstraction. VPG hardware emits secondary data packets such as DP/HDMI infoframes or stream metadata from the display pipeline.

## Important APIs, Types, And Functions

The header defines `struct vpg` with context, instance, and a `vpg_funcs` table. The vtable provides packet generation controls, update hooks, and destruction or state management depending on the ASIC implementation.

## Control Flow

Stream encoder and link sequencing code prepares packet contents, then calls VPG operations to enable, update, or stop packet emission. Dynamic metadata paths update packet data while a stream is active.

## State And Persistence Behavior

Packet contents and enable bits persist in VPG/register packet RAM until overwritten or disabled. The software object only persists identity and function dispatch.

## Dependencies And Integration Points

VPG integrates with stream encoders, DP/HDMI info packet paths, HDR metadata, audio/video packet scheduling, and link hardware sequencing.

## Risks And Test Signals

Risks include stale metadata, packet timing issues, NULL implementations on ASICs without VPG separation, and packet RAM corruption. Test signals include HDMI/DP infoframe validation, HDR metadata changes, audio/video packet tests, and blank/unblank transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/vpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/link_enc_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/link_enc_cfg.h

## Purpose

`link_enc_cfg.h` declares the dynamic DIG link encoder assignment service. It tracks which display endpoints own which DIG encoders, especially where endpoints are mappable or unmappable and where USB4/DPIA changes the traditional PHY relationship.

## Important APIs, Types, And Functions

APIs include `link_enc_cfg_init`, `link_enc_cfg_copy`, assignment and unassignment routines, mappability checks, queries for streams or links using an encoder, query for encoder used by a link or stream, next-available encoder lookup, availability checks, assignment validation, and `link_enc_cfg_set_transient_mode`.

## Control Flow

At state initialization or copy, assignment tables are prepared in `resource_context`. During stream assignment, the algorithm loops over streams twice: first unmappable endpoints, then mappable endpoints. Commit-time transitions can expose both old and new assignments by putting current state into transient mode after validating the new assignment set.

## State And Persistence Behavior

The persistent state is the encoder assignment table and availability list inside DC resource contexts. Transient mode is explicitly stateful and exists so hardware programming can refer to old and new assignments while a commit is in progress.

## Dependencies And Integration Points

The header depends on `core_types.h` and integrates with `link_encoder.h`, resource mapping, link hardware sequencing, DPMS, MST, USB4/DPIA routing, and stream commit state handling.

## Risks And Test Signals

Risks include duplicate encoder ownership, losing an assignment during a transient commit, treating an unmappable endpoint as mappable, or returning stale encoders to link code. Test signals include multi-display DP/HDMI on shared DIG resources, USB4 DPIA links, hotplug during commit, MST changes, validation failures, and debug inspection of assignment tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/link_enc_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/link_hwss.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/link_hwss.h

## Purpose

`link_hwss.h` defines the link hardware sequencing interface used by DC to abstract signal-specific link programming. It separates mandatory stream/audio/link operations from optional DP-specific extension hooks.

## Important APIs, Types, And Functions

`link_hwss_ext` contains optional hooks for hblank minimum symbol width, throttled VCP size, DP link output enable, DP test patterns, DP lane settings, and MST allocation-table updates. `link_hwss` embeds those extensions and requires core hooks for stream encoder setup/reset, stream attributes, link output disable, audio output setup, audio packet enable, and audio packet disable.

## Control Flow

Higher-level link code selects a `link_hwss` implementation based on link/signal/resource characteristics, then invokes mandatory hooks for stream setup and DPMS. DP paths call extension hooks when present for training, test patterns, MST, and bandwidth throttling.

## State And Persistence Behavior

This header defines no state. The selected vtable acts as persistent dispatch for the link operation and programs stream encoder, link encoder, audio, and MST state in hardware.

## Dependencies And Integration Points

It depends on basic DP, signal, graphics object, and fixed-point types and forward-declares DC core objects. It integrates with link service, stream encoder, link encoder, MST allocation, audio, and DP test paths.

## Risks And Test Signals

Risks include missing mandatory hooks, optional hooks used without NULL checks, and selecting a HWSS variant that does not match the link resource. Test signals include DP/HDMI enable/disable, audio packet control, MST allocation changes, DP test patterns, and DP2/HPO versus DIO link sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/link_hwss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/link_service.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/link_service.h

## Purpose

`link_service.h` is the private DC link-component interface. It intentionally exposes a broad function-pointer service to DC internals while keeping DM consumers behind `dc.h`, preventing DM from depending on private link implementation headers.

## Important APIs, Types, And Functions

The file declares `link_create_link_service`, `link_destroy_link_service`, `link_init_data`, `ddc_service_init_data`, and the large `struct link_service`. The service groups factory, detection, resource, validation, DPMS, DDC/AUX, DP capability, DP PHY/DPIA, DP IRQ handling, eDP panel control, DP CTS, and DP trace functions. It covers link creation/destruction, sink detection, remote sinks, HPD, MST topology reset, HDCP capability, resource maps, mode timing validation, tunnel bandwidth, DPMS on/off, MST payload updates, DSC, DDC/AUX transfers, retimer config, FEC/link settings/LTTPR decisions, DPIA USB4 bandwidth, drive settings, HPD IRQ parsing/handling, eDP backlight/PSR/replay/ALPM/panel power, DP automated tests, preferred link/training settings, and trace counters/timestamps.

## Control Flow

Callers obtain one service from the factory and invoke category-specific function pointers. Detection creates or updates links and sinks; validation chooses timings and bandwidth; DPMS sequences link output; DDC/AUX performs sideband transactions; IRQ handlers parse HPD RX/link loss; panel-control hooks manage eDP backlight and PSR/replay; CTS hooks drive compliance patterns.

## State And Persistence Behavior

The service object is dispatch-only, but it mutates persistent `dc_link`, `dc_sink`, DDC, panel, trace, MST, and resource-map state. Link training decisions, verified caps, trace counters, and panel power/backlight state persist outside the service table.

## Dependencies And Integration Points

It depends on `core_types.h` and intentionally remains private to DC and link subcomponents. It integrates with `dc_link_exports.c`, `link_factory.c`, DP training, AUX/DDC, HDCP, MST, DSC, eDP panel features, HPD IRQ service, and DMUB-assisted PSR/replay.

## Risks And Test Signals

Risks include DM accidentally including this private header, missing service assignments in `link_factory.c`, NULL function pointers for expected features, and broad interface churn. Test signals include all connector detection paths, AUX/I2C transactions, MST, DSC, USB4 DPIA, HPD IRQ/link loss, eDP backlight/PSR/replay, DP CTS patterns, and trace output after link training.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/link_service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/reg_helper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/reg_helper.h

## Purpose

`reg_helper.h` provides the register access macro layer used throughout AMD DC hardware blocks. It standardizes direct and indexed register reads, writes, field sets, field gets, updates, waits, and register-sequence offload around caller-provided `CTX`, `REG`, `FD`, and indexed-register macros.

## Important APIs, Types, And Functions

Direct access macros include `REG_READ`, `REG_WRITE`, `REG_SET_N`, `REG_SET`, `REG_SET_2` through `REG_SET_10`, `REG_GET` through `REG_GET_8`, `REG_WAIT`, and `REG_UPDATE` variants including large multi-field helpers up to 20 fields. `REG_UPDATE_SEQ_2/3` and `REG_SEQ_START`, `REG_SEQ_SUBMIT`, `REG_SEQ_WAIT_DONE` support sequence gathering/execution.

Generic helper declarations include `generic_reg_get*`, indirect register read/write, indirect get/update, synchronous indirect get/update, and indexed-register macros such as `IX_REG_SET_N`, `IX_REG_READ`, `IX_REG_GET_N`, `IX_REG_UPDATE_N`, and sync variants.

## Control Flow

Callers define register offset and field descriptor macros, then use concise register operations. Set/update macros build field descriptor/value lists and delegate to generic helpers. Wait macros poll through generic wait logic. Sequence macros switch the context into gather/execute/wait modes for batched register programming.

## State And Persistence Behavior

The header itself stores no state, but every macro mutates hardware registers or reads their current state. Sequence macros depend on state inside the DC context/register service for gathering and offloaded execution.

## Dependencies And Integration Points

It depends on `dm_services.h` for low-level register IO and generic helper implementations. It is included by many DC hardware implementations that define local `CTX`, `REG`, `FD`, and indexed-register mapping macros.

## Risks And Test Signals

Risks include caller macro collisions, field descriptor mismatch, read-modify-write races, overly broad updates, indirect index/data ordering bugs, and sequence offload synchronization issues. Test signals include register traces, hardware block bring-up, underflow-free modesets, static build coverage for macro expansion, and targeted tests for indirect and sequence-programmed blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/reg_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/resource.h

## Purpose

`resource.h` declares the central DC resource-management API. It constructs/destroys resource pools, maps streams and planes onto hardware resources, manages pipe topology, clock sources, scaling, encoder resources, pipe synchronization, and shared topology helpers for MPC/ODM and DML.

## Important APIs, Types, And Functions

The header defines memory type constants, pipe-sync bit macros, `resource_caps`, `resource_straps`, `dc_mcache_allocations`, and `resource_create_funcs` for straps, audio, stream encoders, HPO DP encoders, and HW sequencer creation. It declares pool construction/destruction, stream-to-resource mapping, test pattern/scaling/infoframe builders, clock source refcount helpers, timing/vblank synchronization tests, PLL sharing/free lookup, surface attachment, cursor-disable eligibility, and a detailed `enum pipe_type` for OTG master, OPP head, DPP pipe, MPC combine, ODM, and related topology roles.

Topology APIs add/remove OTG masters, append/remove DPP pipes, update slice counts for streams/planes, query OTG master/OPP head/primary DPP, compute MPC/ODM slice index/count and rects, detect topology changes, log topology updates, find free pipes under several current-context constraints, validate surface attachment, map clock/PHY resources, decide pipe reprogramming, build bit-depth reduction, update audio usage, compute bpp, get temporary DP link resources, reset/check syncd pipes, choose link HWSS, acquire secondary pipes, update DP encoder resources for test harnesses, expose DSCL program data, initialize DML2 callbacks, calculate DET, detect HPO acquisition, and get temporary DIO encoders.

## Control Flow

Resource creation parses ASIC capabilities and builds a pool. During validation/commit, mapping functions assign streams, planes, clocks, encoders, pipes, and topology slices. Helper queries then let hardware sequencing walk OTG/OPP/DPP relationships and update only changed topology. Free-pipe search routines reuse current-context pipes when possible.

## State And Persistence Behavior

Resource state persists in `resource_pool`, `resource_context`, `dc_state`, pipe contexts, clock-source reference counts, link encoder assignments, and pipe sync flags. The macros encode synced-pipe validity in the high bit of `pipe_idx_syncd`.

## Dependencies And Integration Points

The file depends on core DC types/status, ASIC IDs, and SMU/PP interfaces. It integrates with almost every display path: link encoders, stream encoders, timing generators, OPP/MPC/DPP, DML2 validation, audio, clocks, DP test harnesses, and pipe topology logging.

## Risks And Test Signals

Risks include resource leaks, incorrect pipe reuse, topology role confusion, stale clock references, bad slice counts, and transient commit mismatches. Test signals include multi-monitor modesets, plane scaling/slicing, ODM/MPC combine, MST/DP encoder allocation, audio route changes, DML validation, topology logs, and resource leak/assert checks across hotplug and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/soc_and_ip_translator.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/soc_and_ip_translator.h

## Purpose

`soc_and_ip_translator.h` declares a small translation boundary between DC/DML resource state and SoC/IP parameter structures. It is used where display validation needs SoC and IP capabilities in a translated form.

## Important APIs, Types, And Functions

The header is intentionally tiny. It forward-declares or includes the structures needed by the translation function and declares the translator entry point that fills SoC/IP data from DC context or resource data for DML consumers.

## Control Flow

Validation or resource setup calls the translator before DML calculations. The translator reads DC capabilities and populates the SoC/IP structures consumed by bandwidth and mode validation.

## State And Persistence Behavior

No state is stored by the header. Generated SoC/IP parameter structures are transient inputs to validation, but their values affect accepted display configurations and resource decisions.

## Dependencies And Integration Points

It integrates with DML/DML2, resource validation, ASIC capability tables, and display mode validation. Because the header is minimal, include-order and forward declaration correctness are the main source-level concern.

## Risks And Test Signals

Risks include stale translations after capability changes and mismatch between DC resource caps and DML expectations. Test signals include DML validation on multiple ASIC families, bandwidth-limit modes, high-resolution multi-display configurations, and compile coverage when DML structures change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/soc_and_ip_translator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/vm_helper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/vm_helper.h

## Purpose

`vm_helper.h` declares helper APIs for display virtual-memory setup. It provides a small common layer for mapping DC state to VMID programming and page-table related hardware setup.

## Important APIs, Types, And Functions

The header declares VM helper routines that operate on DC objects, VMID hardware objects, and address/page-table parameters. These helpers coordinate VMID use for display scanout and abstract ASIC-specific details behind VMID or resource interfaces.

## Control Flow

When virtual-addressed surfaces are used, display setup prepares VM information, programs VMID state through helper calls, and ensures hardware translation is valid before memory fetch begins. Invalidation and reset paths coordinate with modeset or page-table changes.

## State And Persistence Behavior

The header stores no state. Persistent behavior is hardware VMID/page-table configuration and any associated DC resource state tracking which VMID belongs to which pipe or surface.

## Dependencies And Integration Points

It integrates with `vmid.h`, resource mapping, GPU memory management, HUBP/memory input programming, and page-flip paths for virtual-address framebuffers.

## Risks And Test Signals

Risks include programming order bugs, stale page-table bases, missing invalidation, and address translation faults during scanout. Test signals include GPUVM framebuffers, page flips under memory pressure, VM fault logs, multi-plane virtual scanout, and resume after VRAM/page-table changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/vm_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/Makefile

## Purpose

This Makefile contributes AMD Display Core IRQ service objects to the AMDGPU display build. It lists the common `irq_service.o` plus ASIC-generation-specific IRQ service implementations from DCE 6 through DCN 4.2.

## Important APIs, Types, And Functions

Build variables include `IRQ`, `AMD_DAL_IRQ`, per-generation lists such as `IRQ_DCE60`, `IRQ_DCE80`, `IRQ_DCE11`, `IRQ_DCE12`, `IRQ_DCN1`, and later `IRQ_DCN*` variables. Each list is prefixed with `$(AMDDALPATH)/dc/irq/...` and appended to `AMD_DISPLAY_FILES`. `CONFIG_DRM_AMD_DC_SI` gates DCE60/Southern Islands IRQ service inclusion.

## Control Flow

During kbuild evaluation, this file appends object paths for all supported IRQ service generations. The only conditional branch is the SI/DCE60 block. The parent display Makefile consumes `AMD_DISPLAY_FILES` to build the selected objects into the AMD display driver.

## State And Persistence Behavior

There is no runtime state. Persistent build state is the object list determining which IRQ service constructors are available to resource creation and ASIC initialization.

## Dependencies And Integration Points

It depends on `AMDDALPATH`, `AMD_DISPLAY_FILES`, and Kconfig symbols supplied by the parent build. It integrates with the common IRQ service core and all generation-specific constructors used by DC resource pools.

## Risks And Test Signals

Risks include missing object entries for a new ASIC generation, stale object names, or accidentally building DCE60 without the SI config gate. Test signals are successful AMDGPU display builds for SI and non-SI configurations and link-time availability of each generation's `dal_irq_service_*_create` symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce110/irq_service_dce110.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce110/irq_service_dce110.c

## Purpose

`irq_service_dce110.c` implements the DCE 11 IRQ source table, source-id translator, HPD acknowledge behavior, dummy handlers, vblank enable helper, constructor, and allocator for the DCE110 IRQ service.

## Important APIs, Types, And Functions

`hpd_ack` acknowledges an HPD interrupt, reads delayed sense status, toggles interrupt polarity based on current connection status, and writes the control register. `dal_irq_service_dummy_set` and `dal_irq_service_dummy_ack` log errors for unsupported sources. `dce110_vblank_set` arms the timing generator vertical interrupt when enabling vblank, then delegates generic mask programming. `irq_source_info_dce110` maps DAL IRQ sources to DCE110 HPD, HPDRX, PFLIP, VUPDATE, VBLANK, GPIO, DDC, sink, underflow, DMCU, and VBIOS entries. `to_dal_irq_source_dce110` maps Vislands IV source/ext IDs to DAL IRQ sources. `dal_irq_service_dce110_create` allocates and constructs the service.

## Control Flow

Runtime interrupt handling calls the service's `to_dal_irq_source` function to translate IV source IDs. Generic IRQ service code indexes `irq_source_info_dce110` to enable, disable, or acknowledge sources. HPD uses custom ack/polarity handling; vblank enable arms TG interrupt width before unmasking.

## State And Persistence Behavior

The IRQ service object stores context, info table pointer, and funcs pointer. Hardware interrupt mask, ack, status, polarity, and TG vertical interrupt registers persist until changed. Dummy handlers deliberately do not change hardware.

## Dependencies And Integration Points

It depends on DCE 11 register/mask headers, Vislands IV source IDs, `dm_services`, logger, `dc`, `core_types`, and common IRQ service helpers. It integrates with timing generators for vblank, HPD handling, page flips, and the common DC interrupt dispatcher.

## Risks And Test Signals

Risks include wrong source/ext mapping, HPD polarity bugs causing interrupt storms or missed hotplugs, invalid pipe offset in vblank enable, and unsupported sources being called unexpectedly. Test signals include HPD plug/unplug on six connectors, HPDRX IRQs, page-flip/vblank delivery, log absence of dummy-handler errors for active sources, and modesets after vblank enable failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce110/irq_service_dce110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce110/irq_service_dce110.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce110/irq_service_dce110.h

## Purpose

`irq_service_dce110.h` publishes the DCE110 IRQ service constructor and shared helper functions used by later DCE IRQ service implementations.

## Important APIs, Types, And Functions

It declares `dal_irq_service_dce110_create`, `to_dal_irq_source_dce110`, `dal_irq_service_dummy_set`, `dal_irq_service_dummy_ack`, and `dce110_vblank_set`. These helpers are reused by DCE80/DCE120 and DCE60 variants where source translation or dummy/vblank behavior is compatible.

## Control Flow

ASIC resource code calls the constructor to obtain an IRQ service. Other IRQ services include this header to assign the shared translator or function pointers in their own IRQ tables.

## State And Persistence Behavior

The header stores no state. It exposes functions that mutate IRQ masks, acknowledgements, logging, and timing-generator vertical interrupt state in implementation files.

## Dependencies And Integration Points

It depends on the common `irq_service.h` definitions. It integrates with DCE generation IRQ services, common IRQ dispatch, and timing-generator vblank programming.

## Risks And Test Signals

Risks include signature drift with common IRQ service types, accidental reuse of DCE110 source mapping on incompatible hardware, and missing dummy-handler visibility. Test signals are build coverage for all includers and runtime vblank/HPD/PFLIP IRQs on DCE110-compatible ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce110/irq_service_dce110.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c

## Purpose

`irq_service_dce120.c` implements the DCE 12 IRQ service table and constructor. It adapts the DCE IRQ patterns to SOC15/Vega10-style register address calculation while reusing DCE110 source translation and dummy/vblank helpers.

## Important APIs, Types, And Functions

The file defines IRQ source function tables for HPD, HPDRX, PFLIP, VBLANK, VUPDATE, and dummy sources. SOC15 helper macros compute register addresses using base-index data. Entry macros describe HPD, HPDRX, PFLIP, VUPDATE, VBLANK, I2C, DP sink, GPIO pad, and underflow entries. `irq_source_info_dce120` populates `DAL_IRQ_SOURCES_NUMBER` entries. `irq_service_funcs_dce120` points to `to_dal_irq_source_dce110`. `dal_irq_service_dce120_create` allocates and constructs the service.

## Control Flow

Generic IRQ handling translates IV source IDs with the shared DCE110 translator, then uses the DCE120 table to mask, unmask, or acknowledge SOC15 register locations. HPD uses the shared `hpd0_ack` helper from DCE110-era code, while vblank uses `dce110_vblank_set`.

## State And Persistence Behavior

Service state is the table and funcs pointer. Hardware state persists in SOC15 interrupt control/status registers and timing-generator vblank-arm registers.

## Dependencies And Integration Points

It depends on DCE 12 offset/mask headers, SOC15 and Vega10 IP offsets, Vislands IV IDs, logger, common IRQ service code, and DCE110 helper declarations. It integrates with Vega/DCE12 resource initialization and common DC interrupt dispatch.

## Risks And Test Signals

Risks include incorrect SOC15 base-index arithmetic, using DCE110 translation where a DCE12-specific source differs, HPD ack helper mismatch, and missing table entries. Test signals include HPD, HPDRX, PFLIP, VUPDATE, VBLANK, and underflow behavior on DCE12 hardware plus build/link coverage for SOC15 register names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.h

## Purpose

`irq_service_dce120.h` declares the DCE120 IRQ service constructor.

## Important APIs, Types, And Functions

The single public API is `dal_irq_service_dce120_create(struct irq_service_init_data *init_data)`, returning a constructed `struct irq_service` or NULL on allocation failure.

## Control Flow

Resource initialization calls the constructor for DCE12 ASICs. The returned service uses the DCE120 source table and shared DCE translator.

## State And Persistence Behavior

No state is stored in the header. Constructed service state lives in the allocated `irq_service` object and hardware registers programmed by the implementation.

## Dependencies And Integration Points

It depends on `../irq_service.h` and integrates with DCE12 resource-pool creation and common interrupt dispatch.

## Risks And Test Signals

Risks are limited to constructor declaration drift or missing build inclusion. Test signals are successful DCE12 builds and runtime interrupt delivery on DCE12 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce60/irq_service_dce60.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce60/irq_service_dce60.c

## Purpose

`irq_service_dce60.c` implements the DCE 6 IRQ service, mainly for SI-era display support. It builds a DCE60-specific source table and source translator while reusing DCE110 dummy and vblank helper functions where compatible.

## Important APIs, Types, And Functions

The file defines D1-D6 vblank source IDs, function tables for HPD, HPDRX, PFLIP, VBLANK, DCE60-specific vblank, and dummy sources. Entry macros use DCE 6 register names such as `mmDC_HPD*_INT_CONTROL`, `mmDCP*_GRPH_INTERRUPT_CONTROL`, `mmCRTC*_CRTC_INTERRUPT_CONTROL`, and `mmLB*_VBLANK_STATUS`. `irq_source_info_dce60` maps DAL IRQ sources. `to_dal_irq_source_dce60` maps Vislands source/ext IDs for VBLANK, VUPDATE, PFLIP, HPD, and HPDRX. `dal_irq_service_dce60_create` allocates and constructs the service.

## Control Flow

Generic DC interrupt dispatch uses `to_dal_irq_source_dce60` and then table entries to program masks and acknowledge status. HPD uses `hpd1_ack`; VUPDATE uses the DCE110 vblank set helper in this table, while VBLANK entries use a DCE60-specific function table without a set hook because LB vblank registers differ.

## State And Persistence Behavior

The service object persists with DCE60 info/funcs pointers. Hardware mask/ack state persists in HPD, DCP, CRTC, and LB registers. Source translation is stateless.

## Dependencies And Integration Points

It depends on Linux slab allocation, DCE 6 register/mask headers, Vislands IV IDs, common services/logger, `dc_types`, and DCE110 helpers. It is included in the build only under `CONFIG_DRM_AMD_DC_SI`.

## Risks And Test Signals

Risks include one-based HPD register numbering, LB-based vblank differences, SI-only build coverage gaps, and helper reuse mismatches. Test signals include SI build coverage, HPD plug/unplug, vblank/page-flip interrupts, vupdate interrupts, and absence of dummy-handler logs on supported sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce60/irq_service_dce60.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce60/irq_service_dce60.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce60/irq_service_dce60.h

## Purpose

`irq_service_dce60.h` declares DCE60 IRQ-service entry points for SI-era display support.

## Important APIs, Types, And Functions

It declares `to_dal_irq_source_dce60` for source/ext translation and `dal_irq_service_dce60_create` for allocation/construction.

## Control Flow

Resource code calls the constructor when selecting the DCE60 IRQ service. Common interrupt dispatch later calls the translator through the service vtable.

## State And Persistence Behavior

The header stores no state. Created services carry the DCE60 source table and mutate hardware interrupt registers through common IRQ helpers.

## Dependencies And Integration Points

It depends on `../irq_service.h` and integrates with SI/DCE60 resource initialization and common IRQ dispatch.

## Risks And Test Signals

Risks include SI build exclusion hiding declaration drift and incorrect translator assignment. Test signals are `CONFIG_DRM_AMD_DC_SI` builds and runtime HPD/vblank/PFLIP interrupts on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce60/irq_service_dce60.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce80/irq_service_dce80.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce80/irq_service_dce80.c

## Purpose

`irq_service_dce80.c` implements the DCE 8 IRQ service table and constructor. It adapts DCE110-style interrupt handling to DCE 8 register names while reusing the DCE110 source translator and helpers.

## Important APIs, Types, And Functions

Function tables are defined for HPD, HPDRX, PFLIP, VBLANK, VUPDATE, and dummy sources. Entry macros map DAL sources to DCE 8 HPD, DCP graphics flip, CRTC vupdate/vblank, GPIO, DDC, DP sink, and underflow registers. `irq_source_info_dce80` contains the mapping table. `irq_service_funcs_dce80` uses `to_dal_irq_source_dce110`. `dal_irq_service_dce80_create` allocates and constructs the service.

## Control Flow

Interrupt dispatch translates source IDs with the shared DCE translator, then uses the DCE80-specific table for enable/disable/ack. HPD uses `hpd1_ack`; vblank uses `dce110_vblank_set`; unsupported sources route to dummy functions.

## State And Persistence Behavior

Service state is the info table and funcs pointer. Hardware state persists in DCE 8 HPD, DCP, and CRTC interrupt registers.

## Dependencies And Integration Points

It depends on DCE 8 register/mask headers, Vislands IV IDs, logger/services, `dc_types`, and DCE110 helper declarations. It integrates with DCE80 resource-pool construction and common DC IRQ handling.

## Risks And Test Signals

Risks include register-name/index mismatches, helper reuse assumptions, and unsupported sources being enabled. Test signals include HPD, HPDRX, page-flip, vblank, vupdate, and underflow behavior on DCE8 ASICs plus clean build/link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce80/irq_service_dce80.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce80/irq_service_dce80.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce80/irq_service_dce80.h

## Purpose

`irq_service_dce80.h` declares the DCE80 IRQ service constructor.

## Important APIs, Types, And Functions

The public API is `dal_irq_service_dce80_create(struct irq_service_init_data *init_data)`.

## Control Flow

DCE80 resource initialization calls this constructor and receives an IRQ service using DCE80 table entries and shared DCE source translation.

## State And Persistence Behavior

No state is in the header; constructed service state lives in the allocated IRQ service object.

## Dependencies And Integration Points

It depends on common IRQ service definitions and integrates with DCE80 build and resource initialization.

## Risks And Test Signals

Risks are declaration/implementation drift or missing Makefile inclusion. Test signals include DCE80 build coverage and runtime HPD/vblank/page-flip interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce80/irq_service_dce80.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c

## Purpose

`irq_service_dcn10.c` implements the DCN 1.0 IRQ service. It maps DCN source IDs to DAL IRQ sources and builds SOC15/base-indexed IRQ source entries for HPD, HPDRX, HUBP flips, OTG vstartup/vupdate-no-lock/vline0, GPIO, DDC, sink, and underflow placeholders.

## Important APIs, Types, And Functions

`to_dal_irq_source_dcn10` translates DCN 1.0 source IDs: OTG vstartup to VBLANK, vertical interrupt control to VLINE0, OTG vupdate-no-lock to VUPDATE, HUBP flip to PFLIP, and HPD source/ext contexts to HPD or HPDRX. Function tables exist for HPD, HPDRX, PFLIP, VBLANK, VLINE0, VUPDATE_NO_LOCK, and dummy sources. Macros `BASE`, `SRI`, and `IRQ_REG_ENTRY` compute SOC15 register addresses and masks. `irq_source_info_dcn10` maps DAL sources, with PFLIP5/6 dummy because DCN10 exposes four HUBP flip entries. `dal_irq_service_dcn10_create` allocates and constructs the service.

## Control Flow

The common dispatcher calls the DCN translator and then programs IRQ masks/acks from `irq_source_info_dcn10`. HPD uses `hpd0_ack`; vblank and vupdate entries directly use OTG global sync status events; vline0 entries use OTG vertical interrupt control. Unsupported sources use DCE110 dummy handlers.

## State And Persistence Behavior

The service stores the DCN10 table and funcs pointer. Hardware state persists in HPD, HUBP request, OTG global sync, and vertical interrupt registers. The translator is stateless but must match firmware interrupt source IDs.

## Dependencies And Integration Points

It depends on DCN 1.0 offset/mask headers, SOC15/Vega10 offsets, DCN IRQ source IDs, DCE110 helper declarations, logger/services, and common IRQ service code. It integrates with HUBP page flips, OTG timing/vblank/vline interrupts, HPD handling, and DCN resource construction.

## Risks And Test Signals

Risks include source ID mismatches, base-index calculation errors, treating DCN vstartup as DCE-style vblank without accounting for timing differences, PFLIP5/6 dummy surprises, and missed vupdate-no-lock semantics. Test signals include DCN10 HPD/HPDRX, four-HUBP page flips, vblank/vline0 IRQs, vupdate delivery, underflow diagnostics, and SOC15 register trace validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.h

## Purpose

`irq_service_dcn10.h` declares the DCN10 IRQ service constructor.

## Important APIs, Types, And Functions

The public API is `dal_irq_service_dcn10_create(struct irq_service_init_data *init_data)`, returning a constructed IRQ service for DCN 1.0 hardware.

## Control Flow

DCN10 resource initialization calls the constructor. The returned service provides the DCN10 source table and translation vtable to common IRQ dispatch.

## State And Persistence Behavior

The header stores no state. Constructed service state is allocated in the implementation and hardware interrupt state is programmed by common IRQ operations.

## Dependencies And Integration Points

It depends on common IRQ service definitions and integrates with DCN10 resource-pool creation and display interrupt handling.

## Risks And Test Signals

Risks are constructor declaration drift or missing object linkage. Test signals include DCN10 build coverage and runtime HPD, page-flip, vblank, vline0, and vupdate interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.h -->
