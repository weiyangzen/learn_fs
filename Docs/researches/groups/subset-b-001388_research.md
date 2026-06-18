# subset-b-001388 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc.c

## Purpose

`dc.c` is the central implementation file for AMD Display Core's OS-agnostic display manager object. It creates and destroys `struct dc`, constructs links and resource pools from VBIOS/ASIC data, owns the current `dc_state`, validates stream and plane changes, commits display topology and surface updates to hardware through the HWSS abstraction, coordinates power and idle states, and forwards several DMUB/DMCU commands for modern display features.

The file sits above the ASIC-specific hardware sequencer and resource code. Its main job is to turn public DC API calls from display manager code into validated `dc_state`, `dc_stream_state`, `dc_plane_state`, and `pipe_ctx` changes, then sequence those changes safely across bandwidth programming, locks, front-end programming, link programming, cursor/plane address flips, SubVP/ODM/MPC transitions, and firmware notifications.

## Important APIs, types, and functions

- `dc_create()`, `dc_destroy()`, `dc_hardware_init()`, `dc_hardware_release()`, `dc_set_power_state()`, and `dc_resume()` are the high-level lifecycle entry points.
- `dc_construct_ctx()`, `dc_construct()`, and `dc_destruct()` allocate and tear down `dc_context`, BIOS parser state, GPIO service, resource pool, clock manager, links, link encoders, the current state, DML bounding data, VM helper, and performance trace storage.
- `create_links()` creates physical VBIOS links, USB4/DPIA links, and virtual links; `create_link_encoders()`/`destroy_link_encoders()` handle extra DIG link encoder objects required by DPIA-capable platforms.
- `dc_commit_streams()` validates and commits stream topology changes. It builds validation sets from requested streams and their existing planes, handles ODM 2:1 exit transitions, validates bandwidth, assigns link encoders, inserts minimal transition states when needed, and calls `dc_commit_state_no_check()`.
- `dc_commit_state_no_check()` is the full state commit engine. It disables idle optimizations, exits VBIOS mode if required, prepares bandwidth, locks SubVP/DMUB/interdependent paths, disables dangling planes, applies the new context to hardware, programs front end and planes, synchronizes timing, optimizes bandwidth, notifies stream masks, clears update flags, and swaps `dc->current_state`.
- `dc_commit_updates_for_stream()` and `dc_update_planes_and_stream()` are the surface/stream update entry points. They choose between v2 and v3 update flows based on DCN generation and drive prepare/execute/cleanup staging for newer paths.
- `dc_check_update_surfaces_for_stream()`, `det_surface_update()`, `get_plane_info_update_type()`, and `get_scaling_info_update_type()` classify updates as fast, medium, or full and set detailed plane/stream update flags.
- `update_planes_and_stream_state()` copies incoming stream and plane updates into state, validates full-update contexts, handles seamless boot flags, and backs up/restores scratch stream/plane state for transition handling.
- `commit_planes_for_stream()` is the main update commit path. `commit_planes_for_stream_fast()` is the optimized HWSS sequence path for fast-only updates, and `commit_plane_for_stream_offload_fams2_flip()` offloads eligible address-only FAMS2 flips to DMUB.
- Minimal transition helpers include `could_mpcc_tree_change_for_active_pipes()`, `create_minimal_transition_state()`, `commit_minimal_transition_state()`, `commit_minimal_transition_state_in_dc_update()`, `commit_minimal_transition_based_on_new_context()`, and `commit_minimal_transition_based_on_current_context()`.
- Timing and display helpers include `dc_validate_boot_timing()`, `dc_trigger_sync()`, `program_timing_sync()`, `dc_stream_adjust_vmin_vmax()`, `dc_stream_get_last_used_drr_vtotal()`, `dc_stream_configure_crc()`, `dc_stream_get_crc()`, `dc_stream_set_dither_option()`, `dc_stream_set_gamut_remap()`, and `dc_stream_program_csc_matrix()`.
- Power, idle, and clock helpers include `dc_allow_idle_optimizations_internal()`, `dc_exit_ips_for_hw_access_internal()`, `dc_dmub_is_ips_idle_state()`, `dc_enable_dcmode_clk_limit()`, `dc_lock_memory_clock_frequency()`, and `dc_unlock_memory_clock_frequency()`.
- DMUB/DPIA helpers include `dc_process_dmub_aux_transfer_async()`, `dc_process_dmub_set_config_async()`, `dc_process_dmub_set_mst_slots()`, `dc_process_dmub_dpia_set_tps_notification()`, `dc_process_dmub_dpia_hpd_int_enable()`, `dc_enable_dmub_outbox()`, and dirty-rect command builders.
- Diagnostics include `dc_capture_register_software_state()`, `dc_get_underflow_debug_data_for_otg()`, `dc_get_qos_info()`, `dc_print_dmub_diagnostic_data()`, and `dc_log_preos_dmcub_info()`.

## Control flow

Creation starts in `dc_create()`. Virtual hardware only constructs a minimal context and sets pitch alignment. Real hardware calls `dc_construct()`, which allocates helper state, constructs `dc_context`, builds or adopts a BIOS parser, creates GPIO services, constructs the ASIC resource pool, creates the clock manager and optional SOC/IP translator, creates links and extra link encoders, then creates `dc->current_state`. After construction, `dc_create()` fills display capability fields such as max streams, links, audio count, DP protocol version, and OTG count.

Hardware initialization runs through `dc_hardware_init()`: it probes eDP presence, calls `hwss.init_hw()` outside virtual environments, and notifies DMUB that DC is in D0. Power-state transitions are handled by `dc_set_power_state()`, which reconstructs/destructs the current state for D0/non-D0 transitions, restores Z10, initializes hardware and system context on D0, and notifies DMUB of ACPI state changes.

Stream topology commits enter through `dc_commit_streams()`. The function skips no-op stream arrays, exits IPS for hardware access, validates each non-virtual stream, carries over existing planes from stream status, optionally commits a minimal current-state transition to exit ODM 2:1, copies current state, validates the new state, assigns link encoders after validation, ensures pipe topology can transition seamlessly or inserts a minimal transition, and finally applies the new state through `dc_commit_state_no_check()`.

Full state commit first blocks idle optimizations and prepares for hardware programming. It may disable VBIOS mode, wait for pipe update if required, prepare bandwidth, acquire SubVP/DMUB/interdependent locks, power down DSC blocks before programming, disable planes that no longer belong to the new context, and apply the full context to hardware. After that it triggers timing sync, marks streams for full update, programs front-end state, applies SubVP config, updates changed-mode streams, waits for pending flips and ODM updates before optimizing bandwidth, updates DSC power gating, traces clocks, notifies DMUB of stream-mask changes, clears mode/update flags, and swaps the retained current state.

Plane and stream updates enter through `dc_commit_updates_for_stream()` or the staged `dc_update_planes_and_stream()` API. `update_planes_and_stream_state()` classifies updates, mutates the live stream/plane objects with requested values, validates dimensions, creates a copied context for full updates, removes and re-adds planes to the copied context, rebuilds scaling for medium position changes, validates bandwidth for full updates, and returns either the current state or a new validated state plus the update type.

For update commits, fast-only updates can use `commit_planes_for_stream_fast()`, which builds a compact DMUB/HWSS sequence for dirty rects and fast programming. Other updates use `commit_planes_for_stream()`, which restores Z10, prepares bandwidth for full updates, waits for outstanding updates, locks the relevant pipe set, sends dirty-rect commands, applies stream updates, programs or blanks front end as needed, updates triple buffering and plane addresses, handles DSC double-buffer locking, manages SubVP phantom stream enable/disable, commits SubVP config, releases locks, fires manual triggers, and updates the DMUB stream mask.

The v3 staged update path splits this into `prepare`, `execute`, and `cleanup` around `struct dc_update_scratch_space`. Prepare determines whether the update is current-context fast/current-context full/new-context seamless/new-context minimal-based-on-new/new-context minimal-based-on-current. Execute performs the selected commit. Cleanup swaps current state, releases intermediate or backup contexts, restores stream/plane scratch state, handles deferred minimal transitions, decrements the steady-state countdown, and clears update flags.

## State and persistence behavior

The persistent runtime anchor is `struct dc`, especially `dc->ctx`, `dc->res_pool`, `dc->clk_mgr`, `dc->links[]`, `dc->current_state`, `dc->debug`, `dc->config`, `dc->caps`, `dc->scratch`, and `dc->check_config`. The file does not persist data to disk; persistence is in kernel heap objects, retained state references, hardware programming, clock manager state, firmware-visible DMUB state, and link/stream/plane objects owned across commits.

`dc->current_state` is refcounted. Full commits replace it with a validated context and release the old one only after assigning the new pointer to avoid interrupt-time access to freed state. Update paths often mutate the stream and plane objects before context validation, so scratch backup/restore helpers preserve old and new stream/plane state across minimal-transition attempts.

Update flags on `dc_stream_state` and `dc_plane_state` are the transient contract between classification and hardware programming. They are intentionally cleared after commits on newer DCN versions to prevent redundant programming. Seamless boot uses `apply_seamless_boot_optimization` flags on streams; first flip or DPMS transition clears the flag and sets `dc->optimized_required` so a later post-update optimization lowers clocks and watermarks.

Power state is split across `dc->idle_optimizations_allowed`, `dc->config.disable_ips`, clock manager hard-min/hard-max state, current bandwidth context, and DMUB firmware notifications. `dc_allow_idle_optimizations_internal()` records whether idle optimizations are active and logs hard-min clocks and SubVP pipe classes when it changes.

The diagnostic software-state capture function snapshots many register-programming inputs from current pipe contexts into `dc_register_software_state`: HUBP surface/tiling/request/DLG/TTU data, HUBBUB DET and compbuf data, DPP scaler data, DCCG clocks, DSC configuration, MPC topology/blending, OPP format and DSC-forwarding state, and OPTC timing/ODM/DSC-derived fields. Several captured fields are approximations or TODO-backed defaults rather than direct register reads.

## Dependencies and integration points

This file integrates with nearly every major AMD DC subsystem: resource pool construction/validation, HWSS and HWSEQ callbacks, clock manager, BIOS parser, GPIO service, link service, link encoder configuration, DML/DML2 bandwidth validation, DC state management, stream and plane private helpers, DMUB service, DMCU, ABM, DSC, timing generators, OPP/DPP/HUBP/transform blocks, IRQ service, VM helper, and debug/trace logging.

The public callers are primarily the amdgpu display manager layer through DC APIs. Hardware-specific behavior is delegated through function tables such as `dc->hwss`, `dc->hwseq->funcs`, `dc->res_pool->funcs`, `dc->link_srv`, timing generator funcs, OPP funcs, ABM funcs, DPP funcs, and clock manager funcs. Firmware integration is through `dc_wake_and_execute_dmub_cmd()`, DMUB outbox/inbox commands, DMCU CRC forwarding, DMUB hardware locks, DMUB stream-mask notifications, and panel-instance helpers.

External protocols and hardware features surfaced here include eDP seamless boot, PSR, Replay, ABM, FreeSync/VRR, DSC, MST payload changes, USB4/DPIA AUX and SET_CONFIG commands, DPIA HPD/TPS notifications, ODM, MPC pipe splitting, SubVP phantom pipes, FAMS/FAMS2, IPS/Z10, dirty rect updates, secure display CRC windows, and smart-power OLED commands.

## Risks and edge cases

- The full update path mutates stream and plane objects before all validation and transition decisions are complete. Scratch backup/restore is therefore critical; missing a field can make current/new contexts inconsistent during minimal-transition fallback.
- `dc_commit_state_no_check()` assumes validation already happened. Misuse with an unvalidated context can program unsupported pipe topology, bandwidth, or link state.
- Minimal transition handling is complex and stateful. It changes global debug pipe-split/SubVP policy temporarily, may defer final transitions with a countdown, swaps current state through intermediate contexts, and must restore policy and refcounts in all failure paths.
- Update classification must be conservative. Under-promoting a plane format, tiling, DCC, scaling, DSC, DPMS, MST, or power-related change to fast/medium risks missing bandwidth validation or lock scope.
- Several paths rely on optional function pointers. Most are guarded, but a platform with unexpected NULL callbacks can silently skip features such as CRC, visual confirm, bandwidth optimization, idle optimization, DSC power gating, or specific stream updates.
- Locking order around SubVP, DMUB hardware locks, interdependent updates, pipe locks, DSC double-buffer locks, and post-unlock front-end programming is fragile. Incorrect ordering can cause underflow, missed double-buffer updates, visible corruption, or firmware/hardware deadlock.
- Dirty-rect and FAMS2 offload paths intentionally skip immediate flips and require address-only updates. Incorrect eligibility could send stale dirty rectangles or offload an update that still needs hardware locks.
- `dc_validate_boot_timing()` is strict by design. It rejects non-eDP, disabled DIG, non-preferred TG, timing mismatch, unsupported colorimetry/coding, DSC mismatch, and eDP ILR optimization cases; overly strict checks reduce seamless boot coverage, while loose checks risk inheriting incompatible firmware programming.
- `dc_capture_register_software_state()` mixes actual software state with inferred defaults and TODO approximations, so it is useful for diagnostics but should not be treated as an authoritative hardware register dump.
- `blank_and_force_memclk()` visibly blanks active pipes while forcing memory clock in platforms without p-state change support; callers must hold the expected display lock and tolerate disruption.

## Test signals

Build coverage should catch missing declarations, mismatched callback signatures, and configuration-gated sections such as secure display, DML FP, and DCN4.2 color-management history controls. Runtime validation signals include DC log messages, `TRACE_DCN_CLOCK_STATE`/`TRACE_DCE_CLOCK_STATE`, `DC_LOG_DC`, `DC_LOG_ERROR`, `BREAK_TO_DEBUGGER()` assertions, DMUB command return statuses, and stream-mask notifications.

High-value functional coverage includes: DC create/destroy on physical, virtual, and DPIA-capable platforms; eDP seamless boot validation and first-flip optimization; stream add/remove with existing planes; MPO plane add/remove with MPC/ODM/SubVP active; fast-only flip/address/gamma/CSC updates; full plane format/tiling/DCC/scaling updates; DSC config updates and double-buffer lock behavior; DPMS off/on; MST bandwidth increase/reduce; PSR/Replay dirty rects; FAMS2 offload eligibility; v2 versus v3 update paths by DCN version; deferred minimal transition countdown; suspend/resume and D0/D3 transitions; IPS enter/exit around hardware access; DMUB AUX/SET_CONFIG/MST/DPIA commands; ABM pause/save/restore; and diagnostic state capture/QoS reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_debug.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_debug.c

## Purpose

`dc_debug.c` contains lightweight Display Core debugging and formatting helpers. It logs surface update details when `dc->debug.surface_trace` is enabled, logs bandwidth clock data when `dc->debug.clock_trace` is enabled, and converts common DC status, pixel encoding, and color depth enums into human-readable strings for diagnostics.

The file is intentionally small and has no hardware programming responsibility. Its value is observability: it lets update paths in `dc.c` emit structured trace lines for flips, plane metadata, tiling, scaling, and clock calculations without embedding all of that formatting directly in the commit code.

## Important APIs, types, and functions

- `update_surface_trace(struct dc *dc, const struct dc_surface_update *updates, int surface_count)` iterates surface updates and conditionally logs fields from `flip_addr`, `plane_info`, and `scaling_info`.
- `post_surface_trace(struct dc *dc)` emits a short post-update trace marker.
- `context_clock_trace(struct dc *dc, struct dc_state *context)` logs current/calculated DCN clock values from `context->bw_ctx.bw.dcn.clk`.
- `dc_status_to_str(enum dc_status status)` maps DC status codes such as `DC_OK`, validation failures, bandwidth failures, DSC failures, DP link failures, unsupported values, and cursor/resource failures to readable strings.
- `dc_pixel_encoding_to_str(enum dc_pixel_encoding pixel_encoding)` maps RGB, YUV422, YUV444, and YUV420 encodings.
- `dc_color_depth_to_str(enum dc_color_depth color_depth)` maps common 6/8/9/10/11/12/14/16 bpc depth enums.
- `SURFACE_TRACE` and `CLOCK_TRACE` are local logging macros gated by `dc->debug.surface_trace` and `dc->debug.clock_trace`.

## Control flow

`update_surface_trace()` is called by the update-classification path in `dc.c` when the update type is at or above the local trace threshold. It initializes the logger macro, loops over each update, prints an update index, and logs only the optional substructures present in that update. Flip logging includes address type, graphics address, metadata address, and immediate-flip flag. Plane logging includes color space, format, pitch, surface dimensions, rotation, stereo format, GFX8 tiling fields, GFX9 swizzle, visibility, and alpha fields. Scaling logging includes source/destination/clip rectangles and scaling taps.

`post_surface_trace()` emits a marker after surface processing when post-update bandwidth optimization is being attempted. `context_clock_trace()` prints clock values from the bandwidth context; in the visible code both "Current" and "Calculated" lines use the same DCN clock fields, so it is a snapshot trace rather than a before/after comparison.

The enum conversion functions are straight switch statements with default "Unknown" or "Unexpected status error" fallbacks. They do not allocate memory and return string literals.

## State and persistence behavior

The file owns no persistent state. It reads `dc->debug` trace booleans, `dc->ctx->logger`, supplied update structures, and supplied state fields. It does not retain references, update counters, write hardware registers, or persist logs itself; actual log routing is delegated to the DC logging macros.

Because logging is conditional, the cost of most trace formatting is avoided unless the corresponding debug flag is set. The string conversion helpers are stateless and deterministic for known enum values.

## Dependencies and integration points

The implementation depends on `dm_services.h`, public `dc.h`, core status/types headers, and `resource.h`. It integrates with the DC logging infrastructure through `DC_LOG_IF_TRACE()` and `DC_LOG_BANDWIDTH_CALCS()`, and with update/commit code through calls from `dc.c` such as `update_surface_trace()`, `post_surface_trace()`, and `context_clock_trace()`.

The logged structures come from the broader DC API: `dc_surface_update`, `dc_flip_addrs`, `dc_plane_info`, `dc_scaling_info`, `dc_state`, and nested bandwidth-clock structures. Consumers of the enum-to-string helpers can use them in diagnostics without knowing the numeric enum values.

## Risks and edge cases

- `update_surface_trace()` assumes `dc`, `updates`, and any non-NULL nested pointers are valid. It is a diagnostic helper, not an input validator.
- Trace output can be verbose for large update batches, especially with plane tiling and scaling data enabled.
- The function logs selected GFX8 and GFX9 tiling fields unconditionally when `plane_info` is present; readers must know which fields are meaningful for the surface's tiling generation.
- `context_clock_trace()` prints DCN clock fields and does not branch for DCE bandwidth state, so it should only be used where those DCN fields are valid.
- Enum conversion switches need to be kept synchronized with new `enum dc_status`, `enum dc_pixel_encoding`, and `enum dc_color_depth` values. Unknown new values will fall back to generic strings.
- The returned strings are mutable `char *` in the signature even though they point to string literals; callers must not write through them.

## Test signals

Build coverage verifies that enum cases and structure fields still exist. Runtime signals are debug logs when `surface_trace` or `clock_trace` is enabled. Useful tests or manual debug checks include a fast flip with only `flip_addr`, a plane-info update with tiling changes, a scaling update with src/dst/clip changes, a full update that triggers `context_clock_trace()`, and calls to the string conversion helpers for every known enum plus an out-of-range value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_debug.c -->
