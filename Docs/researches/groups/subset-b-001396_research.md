# Research Group: subset-b-001396

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_stream_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_stream_encoder.c

Purpose: implements the DCE110 stream encoder function table for DP, HDMI, DVI, LVDS, audio, info-frame packet programming, DP blank/unblank, AV mute, stereo sync, and OTG source routing. It is a hardware register programming file driven by `struct stream_encoder_funcs` and by register/field maps supplied from `dce_stream_encoder.h`.

Important APIs and functions: `dce110_stream_encoder_construct()` and `dce110_analog_stream_encoder_construct()` initialize the base object and assign either the full digital function table or the minimal analog table. The DP path is centered on `dce110_stream_encoder_dp_set_stream_attribute()`, `dce110_stream_encoder_dp_blank()`, `dce110_stream_encoder_dp_unblank()`, and `dce110_stream_encoder_set_throttled_vcp_size()`. HDMI/DVI/LVDS setup uses BIOS `encoder_control` before programming TMDS/HDMI registers. Audio exports include `dce110_se_dp_audio_setup/enable/disable()`, `dce110_se_hdmi_audio_setup/disable()`, and `dce110_se_audio_mute_control()`.

Control flow: stream-attribute setup first programs BIOS encoder mode for TMDS-style outputs or DP pixel/MSA registers for DisplayPort. HDMI setup then configures deep color, scrambler/clock-channel mode, generic-control packets, AVI/audio info-frame lines, and AV mute. DP blank disables the stream at next vertical blank, polls `DP_VID_STREAM_STATUS`, then resets the steer FIFO; unblank computes initial M/N from link rate and pixel clock, primes DIG, clears FIFO reset, waits briefly, then enables stream. Info packets use the AFMT generic packet RAM and per-packet send/continuous controls.

State and persistence: the encoder object stores only pointers to context, BIOS, register map, shifts, and masks. Hardware state persists in AFMT, HDMI, DP, DIG, and DAC registers. Audio packet master enable is shared with DP info packets, so stop/disable paths reread `DP_SEC_CNTL` and keep stream enable if another packet class remains active.

Dependencies and integration: depends on `dc_bios`, `reg_helper`, `hw_shared`, `audio_types`, timing/color-space enums, fixed-point helpers, and DC logging. Integrates with link encoder programming through higher-level resource code via `stream_encoder_funcs`.

Risks: register presence is checked for some generation-specific fields but not all calls; wrong masks/regs can misprogram packets. Poll loops use fixed retry counts and assert or continue on timeout. HDMI audio clock lookup falls back to calculated CTS/N for non-table modes. Info-packet content is cast to `uint32_t *`, so structure layout and endianness expectations matter. Test signals include DP/HDMI mode set, MST bandwidth update, YCbCr420 M/N behavior, HDMI >340 MHz scrambling, audio enable/disable interaction with DP secondary packets, and blank/unblank without stream-status hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_stream_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_stream_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_stream_encoder.h

Purpose: declares the DCE/DCE110 stream encoder private object, register lists, field shift/mask tables, and constructor/audio helper prototypes used by generation-specific AMD display resource code.

Important types and APIs: `struct dce110_stream_encoder` embeds `struct stream_encoder` and adds `regs`, `se_shift`, and `se_mask`. `struct dce110_stream_enc_registers` enumerates AFMT, HDMI, DP, DIG, DAC, MSA, and double-buffer control registers. `struct dce_stream_encoder_shift` and `struct dce_stream_encoder_mask` provide matching field metadata for `REG_UPDATE` macros. Public constructors are `dce110_stream_encoder_construct()` and `dce110_analog_stream_encoder_construct()`. Public audio helpers expose DP and HDMI audio setup/enable/disable/mute.

Control flow role: this header is not executable, but it shapes all register access in `dce_stream_encoder.c`. Resource constructors instantiate static register, shift, and mask tables using macros such as `SE_COMMON_REG_LIST()`, `SE_DCN_REG_LIST()`, and generation-specific `SE_COMMON_MASK_SH_LIST_*()` variants, then pass those tables into the constructor.

State and persistence: the header defines persistent per-instance state as table pointers, not owned register storage. Register addresses are immutable descriptors; actual state lives in hardware. Optional generation fields are represented as zero register addresses or zero masks, which implementation code uses for feature probing in selected paths.

Dependencies and integration: depends on `stream_encoder.h`, AMD register macro conventions (`SR`, `SRI`, field concatenation), `container_of`, DC audio types through prototypes, and engine identifiers. It bridges DCE8/10/11/12 and DCN10 naming differences by supplying alternate register and mask-list macros.

Risks: field-list drift is a major risk: implementation code assumes shift and mask structures contain every field it touches. Some register aliases differ between DCE and SOC/DCN naming, making macro selection important. Test signals are compile coverage across DCE80/100/110/112/120/DCN10 tables, successful construction for analog versus digital engines, and runtime validation that optional packet/update fields are zero-gated only where implementation checks them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_stream_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_transform.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_transform.c

Purpose: implements DCE transform/scaler/output-pixel-processor functions for scaler setup, line-buffer depth, clamp/round/dither, gamut remap, output CSC, regamma LUT programming, and tap selection. It binds these operations into `struct transform_funcs` for DCE and, conditionally, DCE6.

Important functions: `dce_transform_set_scaler()` programs line-buffer memory, overscan, taps, ratios, coefficient RAM, viewport, coefficient update, and alpha enable. `dce_transform_get_optimal_number_of_taps()` selects scaling taps subject to line-buffer capacity. `dce_transform_set_pixel_storage_depth()` maps LB depth to denorm, clamp, bit-depth reduction, and `LB_DATA_FORMAT`. CSC and color APIs are `dce110_opp_set_csc_adjustment()`, `dce110_opp_set_csc_default()`, `dce_transform_set_gamut_remap()`, and regamma APIs `dce110_opp_program_regamma_pwl()`, `dce110_opp_power_on_regamma_lut()`, `dce110_opp_set_regamma_mode()`.

Control flow: scaler programming is ordered to reset sharpness, program overscan, configure taps/mode, compute fixed-point init values, load coefficients only when selected coefficient pointers change, then program viewport and flip coefficient update. Bit-depth programming derives output color depth from LB depth, sets denorm, clamp, round/truncate, and dithering. Regamma programming powers LUT memory, waits for memory-on status, enables write mask, streams RGB and delta entries, then re-enables low-power mode.

State and persistence: `struct dce_transform` caches `filter_h` and `filter_v` pointers to avoid redundant coefficient RAM writes and stores line-buffer capabilities (`lb_memory_size`, `lb_bits_per_entry`, supported depth mask, `prescaler_on`). Hardware state persists in SCL, LB, DCP CSC/gamut/regamma, denorm, clamp, round, and dither registers. `dce_transform_reset()` clears only cached filter pointers.

Dependencies and integration: depends on `reg_helper`, fixed-point conversion/filter helpers, OPP/transform interfaces, DC debug flags, and generation-specific register maps from `dce_transform.h`. It integrates with resource and plane programming through `transform_funcs`.

Risks: tap selection and line-buffer capacity are mode-sensitive; off-by-one errors can reject valid scaling or program invalid taps. Coefficient cache compares pointers, not coefficient contents. Polling LUT/coefficient memory power has bounded waits but continues after timeout. Color matrix programming assumes table coverage for requested color spaces. Test signals include scaling/no-scaling transitions, coefficient update reuse, visual-confirm overscan adjustment, 6/8/10/12 bpc output, gamut bypass versus software matrix, regamma programming under power-gated memory, and DCE6 conditional builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_transform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_transform.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_transform.h

Purpose: declares the DCE transform private object, scaler/filter register maps, field metadata, helper structs, filter-type enum, and OPP/transform entry points used by DCE transform implementations.

Important types and APIs: `struct dce_transform` embeds `struct transform` and adds register/shift/mask pointers, cached filter pointers, line-buffer depth support, memory size, entry width, and `prescaler_on`. `struct dce_transform_registers` enumerates LB, SCL, DCP, CSC, gamut, regamma, memory-power, and DCE6-specific registers. `struct dce_transform_shift` and `struct dce_transform_mask` are generated from `XFM_REG_FIELD_LIST()`. API declarations include `dce_transform_construct()`, optional `dce60_transform_construct()`, `dce_transform_get_optimal_number_of_taps()`, CSC default/adjustment functions, and regamma controls.

Control flow role: generation resource files use macros such as `XFM_COMMON_REG_LIST_DCE80/100/110()` and `XFM_COMMON_MASK_SH_LIST_DCE110()` to build static descriptors, then pass them into constructors. Implementation code dereferences only those descriptor pointers via `REG()`/`FN()` helper macros.

State and persistence: persistent software state is small and per-transform: descriptor pointers, filter cache pointers, LB capacity, and capability flags. Persistent display behavior lives in hardware registers. Constants `LB_TOTAL_NUMBER_OF_ENTRIES` and `LB_BITS_PER_ENTRY` define DCE line-buffer capacity used for tap validation.

Dependencies and integration: depends on `transform.h`, AMD register macro naming, OPP/regamma enums, scaling data structures, fixed-point-derived filter tables, and conditional `CONFIG_DRM_AMD_DC_SI` for DCE6. It integrates into the broader DC resource model as the hardware-specific backing for the abstract transform interface.

Risks: the macro field list is long and shared by multiple generations, so missing or mismatched fields break register programming at compile or runtime. DCE6 variants omit some DCE110 fields, making conditional build coverage important. Test signals include compile coverage for all generation macro expansions, constructor initialization of LB constants, field/mask table completeness, and transform callers seeing the correct function table for DCE versus DCE6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_transform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm.c

Purpose: builds the DMUB-backed ABM object and adapts the generic `abm_funcs` interface to LCD/eDP-specific DMUB ABM operations.

Important functions: `dmub_abm_create()` allocates a `struct dce_abm` only when `ctx->dc->caps.dmcub_support` is true. `dmub_abm_construct()` attaches the function table and DCE ABM register descriptors. Wrapper callbacks include init, level, current/target backlight, config, pause, save/restore, pipe selection, and PWM backlight level. `abm_feature_support()` gates operations to detected eDP panels.

Control flow: most callbacks first map the requested panel instance through `dc_get_edp_links()`. Supported LCD panels call into `dmub_abm_lcd.c`; unsupported panels return false or no-op success depending on the legacy ABM API expectation. `set_level` builds a panel mask across all supported eDP instances and applies one DMUB level command to that mask.

State and persistence: software state is `struct dce_abm` with base `abm`, register tables, and `dmcu_is_running=false`. Runtime ABM state is maintained by hardware registers and DMUB firmware. The wrapper disables DC idle optimizations before reading current/target backlight, preventing low-power state from hiding register access.

Dependencies and integration: depends on `abm.h`, `dce_abm.h`, `core_types`, `dc_get_edp_links`, DMUB command support, and the LCD command helpers. It integrates with DC resource construction as the ABM provider when DMCUB is available.

Risks: panel instance is treated as eDP enumeration order, so multi-eDP mapping correctness matters. Unsupported panel calls may return true for config, which can mask missing support. Destroy assumes a non-null pointer to a DMUB-created object. Test signals include DMCUB-cap gating, multi-eDP panel masks, backlight reads with idle optimizations disabled, unsupported panel behavior, and create/destroy lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm.h

Purpose: declares the DMUB-backed ABM factory/destructor used by DC resource code.

Important APIs: `dmub_abm_create()` takes a DC context plus DCE ABM register, shift, and mask descriptors and returns a generic `struct abm *` when DMCUB support is present. `dmub_abm_destroy()` releases the allocated object and nulls the caller pointer.

Control flow role: this header hides the concrete `struct dce_abm` allocation behind the generic ABM interface. Callers include the header when they want a DMCUB implementation instead of older DMCU-backed ABM.

State and persistence: no state is owned by the header. The created object persists function pointers, context, and register descriptors; hardware/firmware store ABM runtime state.

Dependencies and integration: includes `abm.h` for the public interface and `dce_abm.h` for descriptor types. Integrates with `dmub_abm_lcd.h` indirectly through the implementation.

Risks and test signals: the prototypes require descriptor types to stay ABI-compatible with `dce_abm`. Test compile coverage should ensure all resource constructors pass valid tables. Runtime tests should cover create returning null on non-DMCUB systems and destroy nulling the pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm_lcd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm_lcd.c

Purpose: implements LCD/eDP-specific ABM hardware initialization and DMUB commands for adaptive backlight, PWM fractional mode, configuration upload, pause/save/restore, pipe selection, backlight level, and event control.

Important functions: `dmub_abm_init()` initializes ABM sampling, histogram, IPS CSC coefficient selection, PWM current/target/user levels, min/max thresholds, missed-frame clears, and fractional PWM. Command emitters include `dmub_abm_set_level()`, `dmub_abm_init_config()`, `dmub_abm_set_pause()`, `dmub_abm_save_restore()`, `dmub_abm_set_pipe()`, `dmub_abm_set_backlight_level()`, and `dmub_abm_set_event()`.

Control flow: register init uses `REG_WRITE`, `REG_SET_*`, and `REG_UPDATE` on DCE ABM/PWM registers, then sends `DMUB_CMD__ABM_SET_PWM_FRAC` with a panel mask covering current eDP count. Command helpers zero a `union dmub_rb_cmd`, populate type/subtype/version/payload fields, set panel masks or instances, and execute synchronously through `dc_wake_and_execute_dmub_cmd()`. Config and save/restore use DMUB scratch framebuffer memory: flush, copy CPU data to scratch, pass GPU address and byte count to firmware, then copy scratch back for save/restore.

State and persistence: backlight and ABM levels persist in hardware registers and firmware state. `dmub_abm_save_restore()` uses caller-provided `struct abm_save_restore` as a persistence exchange buffer. Scratch memory contents are transient but shared with DMUB firmware.

Dependencies and integration: depends on `dce_abm` register descriptors, DMUB command definitions, `dc_dmub_srv`, scratch memory framebuffer, DC config flags such as `disable_fractional_pwm`, and panel/eDP count in `dc_context`.

Risks: no explicit size validation before copying config/save data into scratch memory is visible here. Several functions always return true after issuing a synchronous command, so command failure propagation depends on lower layers. `dmub_abm_set_pause()` writes payload size through `cmd.abm_set_level.header`, which aliases the union but is fragile. Test signals include scratch-buffer bounds, command payload bytes for each subtype, fractional PWM panel masks, save/restore round trips, and backlight u16.16 values across multiple panels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm_lcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm_lcd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm_lcd.h

Purpose: declares the LCD-specific DMUB ABM helper surface used by the higher-level DMUB ABM wrapper.

Important APIs: initialization and query functions are `dmub_abm_init()`, `dmub_abm_get_current_backlight()`, and `dmub_abm_get_target_backlight()`. Control functions include `dmub_abm_set_level()`, `dmub_abm_init_config()`, `dmub_abm_set_pause()`, `dmub_abm_save_restore()`, `dmub_abm_set_pipe()`, `dmub_abm_set_backlight_level()`, and `dmub_abm_set_event()`.

Control flow role: callers pass a generic `struct abm *` plus panel or pipe identifiers. The implementation converts to `struct dce_abm` for register access and sends DMUB ABM commands for firmware-owned behavior.

State and persistence: the header forward-declares `struct abm_save_restore`, which is the caller-owned persistence payload used by firmware save/restore exchange. Backlight values are documented in implementation as 17-bit u1.16 hardware format.

Dependencies and integration: includes `abm.h` and relies on `dc_context`, DMUB command structs, and DCE ABM descriptors through the implementation. It is integrated by `dmub_abm.c`, not usually by generic callers directly.

Risks and test signals: because this is a low-level command API, callers must supply valid panel instances, panel masks, config byte counts, and scratch-compatible buffers. Test coverage should compile the prototypes against `dmub_abm.c`, exercise each command subtype, and validate save/restore buffer contents after firmware completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm_lcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_hw_lock_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_hw_lock_mgr.c

Purpose: centralizes decisions and command emission for DMUB hardware-lock coordination used by PSR/Replay and related embedded-panel paths.

Important functions: `dmub_hw_lock_mgr_cmd()` sends inbox1/ring-buffer `DMUB_CMD__HW_LOCK` commands with client, lock/release flag, hardware lock mask, and per-instance flags. `dmub_hw_lock_mgr_inbox0_cmd()` sends compact inbox0 lock commands and waits for ACK. Decision helpers are `dmub_hw_lock_mgr_does_link_require_lock()`, `dmub_hw_lock_mgr_does_context_require_lock()`, `should_use_dmub_inbox1_lock()`, and `should_use_dmub_inbox0_lock_for_link()`.

Control flow: link-level lock requirement returns true for PSR SU1, Replay on embedded signal, and PSR1 when there is exactly one eDP link. Context-level logic scans streams and delegates to the link helper. Inbox1 is used only when DMUB exists, DCN version is below 4.01, inbox0 lock support is absent, and the link requires a lock. Inbox0 is used when firmware metadata advertises `inbox0_lock_support` and the link requires the lock.

State and persistence: no long-lived state is held here. State is read from DC context, DMUB firmware metadata, link PSR/Replay settings, and command flags. Lock state persists in DMUB/hardware until released; unlock commands set `should_release`.

Dependencies and integration: depends on `dc_dmub_srv`, `core_types`, DMUB command unions, `dc_get_edp_links`, and DC hardware sequencing callbacks. It integrates with commit and power-feature paths that must interlock hardware programming with firmware autonomous PSR/Replay behavior.

Risks: incorrect feature detection can choose the wrong lock transport or skip a required lock, leading to races with firmware. Inbox0 support requires several function pointers and firmware metadata to be valid. Test signals include PSR1 single-eDP versus multi-eDP, PSR SU1, Replay embedded links, DCN 4.01 exclusion, inbox0 metadata presence, command release flag, and context scans with null contexts/links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_hw_lock_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_hw_lock_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_hw_lock_mgr.h

Purpose: declares the DMUB hardware-lock command and policy helpers used by DC hardware sequencing.

Important APIs: `dmub_hw_lock_mgr_cmd()` emits ring-buffer lock/unlock commands. `dmub_hw_lock_mgr_inbox0_cmd()` emits inbox0 lock commands. `should_use_dmub_inbox1_lock()` and `should_use_dmub_inbox0_lock_for_link()` choose transport. `dmub_hw_lock_mgr_does_link_require_lock()` and `dmub_hw_lock_mgr_does_context_require_lock()` expose feature-policy checks.

Control flow role: the header documents that inbox0 is not functionally equivalent to inbox1 because DMUB will not own programming of the relevant locking registers. This distinction guides callers that need either DMUB-owned sequencing or a lighter DMU interlock.

State and persistence: no header-owned state. The APIs operate on caller-owned DC, link, context, and DMUB service objects and on caller-provided lock flag structures.

Dependencies and integration: includes `dc_dmub_srv.h` and `core_types.h`, pulling in DC, link, state, and DMUB command types. Integrates with PSR/Replay commit paths and hardware sequencing code.

Risks and test signals: callers must not pass stale link/context pointers and must release locks through the same intended mechanism. Compile tests should verify command-union type visibility. Runtime tests should validate policy decisions for null links, unsupported DMUB, supported inbox0 metadata, PSR/Replay feature combinations, and release handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_hw_lock_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_outbox.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_outbox.c

Purpose: enables DMUB outbox1 notifications from firmware to the host CPU.

Important function: `dmub_enable_outbox_notification()` constructs a `DMUB_CMD__OUTBOX1_ENABLE` command, sets payload bytes to the command body size, enables the flag, and sends it synchronously with `dc_wake_and_execute_dmub_cmd()`.

Control flow: the function is single-purpose. It zeroes a `union dmub_rb_cmd`, fills header type/subtype/payload, sets `enable=true`, and waits for command completion.

State and persistence: no software state is stored here. The persistent effect is a firmware/DMUB configuration bit enabling outbox notifications until firmware or device state changes.

Dependencies and integration: depends on `dc.h`, `dc_dmub_srv.h`, `dmub_outbox.h`, and `dmub_cmd.h`. It integrates with DMUB service initialization paths that need firmware-originated notifications.

Risks: there is no null-check for `dmub_srv` or failure handling beyond lower-layer command execution. Payload size must match the firmware command definition. Test signals include command construction, DMUB service initialization with outbox enabled, notification delivery to x86, and behavior when DMUB service is absent or not ready.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_outbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_outbox.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_outbox.h

Purpose: declares the DMUB outbox notification enable helper.

Important API: `dmub_enable_outbox_notification(struct dc_dmub_srv *dmub_srv)` enables outbox1 notifications through the implementation command path.

Control flow role: this small header forward-declares `struct dc_dmub_srv` so users can request notification enablement without including full DMUB service internals.

State and persistence: no owned state. The function it declares changes firmware notification configuration.

Dependencies and integration: integrates with DMUB service startup and event handling code. Its only dependency is the forward declaration of the service structure.

Risks and test signals: API correctness depends on callers passing a live DMUB service. Compile coverage should ensure no include cycles are introduced; runtime signals are successful outbox notification delivery and no command timeouts during initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_outbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_psr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_psr.c

Purpose: implements the DMUB-backed Panel Self Refresh control object: PSR state query, version programming, enable/disable, level/power optimization, sink vtotal, settings copy, force-static, and residency query.

Important functions: `dmub_psr_get_state()` uses GPINT and `convert_psr_state()` to translate firmware raw state values to `enum dc_psr_state`. `dmub_psr_enable()` sends enable/disable then optionally waits up to about 500 ms using `udelay(500)` loops. `dmub_psr_copy_settings()` gathers pipe/link/PSR context, programs link encoder fast training and secondary packet registers, fills `dmub_cmd_psr_copy_settings_data`, and sends it to firmware. Other command helpers set PSR version, level, sink vtotal, power options, force static, and residency.

Control flow: copy settings first locates the active eDP pipe in current resource context, rejects missing pipe or unsupported PSR version, programs link encoder state, then sends hardware instance IDs and many policy/debug flags to DMUB. It includes sink-specific workarounds for DSC/FEC/TPS3 wakeup, FFU mode, vertical poweroff line, and relock delay. Enable/disable and level commands are guarded by firmware state where needed.

State and persistence: `struct dmub_psr` stores context and function table only. PSR runtime state is firmware-owned and queried by GPINT. Link settings, DPCD caps, debug flags, FEC/DSC state, and current pipe context are copied into firmware context and persist there until replaced or disabled.

Dependencies and integration: depends on `dc_dmub_srv`, DMUB command/GPINT infrastructure, `core_types`, link encoder PSR callbacks, DPCD capabilities, current DC state, and DC debug options. It integrates with eDP link power management and commit sequencing.

Risks: current implementation scans a fixed `MAX_PIPES=6` and notes multi-eDP refactor TODOs. Long retry loops can assert on firmware non-response. Sink-specific byte-string workarounds are brittle but necessary. `dmub_psr_force_static()` assigns payload bytes through the enable union member, which is fragile. Test signals include PSR1 and PSR SU1 setup, GPINT timeout handling, DSC/FEC sink workarounds, force-FFU behavior, residency modes, high-IRQ wait constraints, and no-pipe rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_psr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_psr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_psr.h

Purpose: declares the DMUB PSR object and function table used by DC code to control Panel Self Refresh through firmware.

Important types and APIs: `struct dmub_psr` stores `struct dc_context *ctx` and `const struct dmub_psr_funcs *funcs`. The function table covers settings copy, enable/disable with optional wait, state query, level, force-static, residency, sink vtotal in active PSR, and power options. Factory/destructor functions are `dmub_psr_create()` and `dmub_psr_destroy()`.

Control flow role: callers allocate the object, then use `funcs` to send PSR commands without depending on implementation details. Settings-copy is the setup gate before enable; state/residency queries provide firmware feedback.

State and persistence: the object is lightweight; firmware stores PSR state and copied hardware context. Caller-owned link and PSR context inputs must remain valid through command construction.

Dependencies and integration: includes `dc_types.h` and `dmub_cmd.h`, and forward-declares `struct dc_link`. It integrates with link power management, PSR policy, and hardware lock paths.

Risks and test signals: API users must handle `dmub_psr_create()` returning null and must not call function pointers after destroy. Versioned command structures in `dmub_cmd.h` must remain compatible. Test signals include compile compatibility with PSR enums and residency modes, lifecycle, settings-copy before enable, and wait/no-wait enable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_psr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_replay.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_replay.c

Purpose: implements DMUB-backed Panel Replay control: state query, enable/disable, settings copy, power optimization, coasting vtotal, residency collection, combined power/vtotal command, and generic replay command dispatch.

Important functions: `dmub_replay_get_state()` queries firmware by GPINT. `dmub_replay_enable()` sends `DMUB_CMD__REPLAY_ENABLE` and optionally waits up to about 500 ms for state transition. `dmub_replay_copy_settings()` locates the active eDP pipe, fills hardware instance IDs and replay policy data, handles DSC/FEC and ALPM details, then sends `DMUB_CMD__REPLAY_COPY_SETTINGS`. `dmub_replay_residency()` maps residency modes to GPINT parameters with bounded retries. `dmub_replay_send_cmd()` dispatches higher-level message enum values to concrete DMUB subtypes.

Control flow: setup scans current resource context for a pipe whose stream link matches the target eDP link. It copies AUX/DIG/DPP/OTG/DPPHY instance data, line time, panel instance, debug flags, PR DPCD deviation fields, SMU/timing-sync/fast-resync options, FEC/DSC flags, sink-specific TPS3 wakeup workaround, and AUX-less ALPM timing/LTTPR data. Runtime commands are synchronous DMUB submissions; residency GPINT retries twenty times with 100 us delays before returning zero.

State and persistence: `struct dmub_replay` stores only context and function table. Firmware owns Replay runtime state and copied context. Link `replay_settings`, DPCD `pr_info`, FEC/DSC state, debug ALPM timings, and LTTPR count are captured into firmware payloads.

Dependencies and integration: depends on `link_service`, `dc_dmub_srv`, `dmub_cmd`, current DC resource context, link encoder transmitter IDs, and DC debug/capability settings. It integrates with eDP Replay feature enablement and hardware lock policy.

Risks: fixed `MAX_PIPES=6` and multi-eDP TODO mirror PSR limitations. State query retries can assert after persistent invalid state. General command dispatch silently returns for unsupported messages or null inputs. Combined command payload sizes must match firmware layouts. Test signals include Replay enable/disable waits, copy settings with no pipe, AUX-less ALPM payloads, FEC/DSC sink workaround, residency retry failure returning zero, and every `replay_FW_Message_type` branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_replay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_replay.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_replay.h

Purpose: declares the DMUB Replay object and function table used by DC code to control Panel Replay through firmware.

Important types and APIs: `struct dmub_replay` stores a DC context and function table. `struct dmub_replay_funcs` includes state query, enable/disable, settings copy, power optimization, general command send, coasting vtotal, residency, and combined power-opt/coasting-vtotal commands. Lifecycle APIs are `dmub_replay_create()` and `dmub_replay_destroy()`.

Control flow role: callers use this vtable after allocation to setup replay context, enable/disable firmware replay, collect residency, and issue specialized firmware messages without knowing the command-union layout.

State and persistence: object state is minimal and non-owning except for allocation. Firmware owns persistent Replay state after commands are sent. Caller-provided `dc_link`, `replay_context`, and command-union inputs are consumed synchronously.

Dependencies and integration: includes `dc_types.h` and `dmub_cmd.h`, and forward-declares `struct dc_link`. It integrates with eDP Replay policy and link-service code.

Risks and test signals: API compatibility depends on `enum replay_state`, `enum replay_FW_Message_type`, `union dmub_replay_cmd_set`, and residency mode definitions in shared headers. Test signals include lifecycle, vtable completeness, settings-copy then enable ordering, and all residency/general-command paths compiling across firmware command revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_replay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/Makefile

Purpose: defines the DCE110 display core object list for the AMD display build.

Important build variables: it sets a file-specific warning flag for `dce110_resource.o` through `CFLAGS_$(AMDDALPATH)/dc/dce110/dce110_resource.o = -Wno-override-init`. `DCE110` lists object files for timing generator, compressor, OPP regamma/CSC/view, memory input, OPP, and transform view objects. `AMD_DAL_DCE110` prefixes each object with `$(AMDDALPATH)/dc/dce110/`, and `AMD_DISPLAY_FILES += $(AMD_DAL_DCE110)` contributes them to the larger AMD display build.

Control flow: make expansion is straightforward: object names are collected, prefixed, and appended. No conditional logic is present in this file.

State and persistence: no runtime state. Build state is the object-list contribution to the kernel module build graph.

Dependencies and integration: depends on the outer AMD display make infrastructure defining `AMDDALPATH` and consuming `AMD_DISPLAY_FILES`. The object list integrates `dce110_compressor.o` from this subset with neighboring DCE110 hardware blocks.

Risks: missing an object here prevents the corresponding DCE110 implementation from linking; adding stale objects breaks builds. The override-init warning suppression is narrow and should remain tied to `dce110_resource.o`. Test signals include kernel/driver build with DCE110 enabled, object inclusion checks, and ensuring `dce110_compressor.o` remains present while its APIs are referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_compressor.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_compressor.c

Purpose: implements the DCE110 framebuffer compression compressor object, including FBC power-up, enable/disable, compressed surface address/pitch programming, invalidation triggers, hardware state query, and object lifecycle.

Important functions: `dce110_compressor_power_up_fbc()` enables FBC, coherency mode, compression modes, min compression ratio, and indirect LUT defaults. `dce110_compressor_enable_fbc()` attaches FBC to a CRTC source, toggles `FBC_GRPH_COMP_EN` for a hardware bug workaround, configures misc invalidation/decompress behavior, then waits for enabled status. `dce110_compressor_disable_fbc()` turns off compression, clears software attachment state, waits for disabled status, and resets the line buffer on vblank for DCE100/110. `dce110_compressor_program_compressed_surface_address_and_pitch()` writes high address first, then low address and aligned pitch. `dce110_compressor_set_fbc_invalidation_triggers()` programs region masks and force-clear events.

Control flow: per-CRTC DCP/DMIF offsets are selected from a three-entry offset table before register access. Status waits poll FBC status up to 1000 times with 100 us delay. Line-buffer reset checks that CRTC position is moving, arms reset, waits for frame count change up to about 100 ms, then clears reset selection.

State and persistence: `struct dce110_compressor` embeds `struct compressor` and current offsets. The base compressor tracks options, min compression ratio, attached CRTC, enabled flag, memory bus width, and compressed surface address. Hardware state persists in global FBC registers and per-DCP compressed-surface registers.

Dependencies and integration: depends on DCE11/GMC register headers, `dm_services` raw register helpers, logger interface, and `compressor_funcs`. It is built by the DCE110 Makefile and consumed through the generic compressor interface.

Risks: offset table covers three pipes only; invalid `params->inst` would index out of bounds. Enable state mixes hardware status with software `attached_inst`. Pitch calculation assumes 1:1 compression ratio and logs otherwise. Wait timeouts log warnings but do not fail callers. Test signals include FBC support gating, enable/disable status polling, compressed address high-before-low order, pitch alignment for varied widths, vblank reset on active/inactive CRTC, and invalidation trigger masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_compressor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_compressor.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_compressor.h

Purpose: declares the DCE110 compressor concrete object and FBC/LPT-related API surface.

Important types and APIs: `struct dce110_compressor` embeds the generic `struct compressor` and stores current DCP/DMIF register offsets in `struct dce110_compressor_reg_offsets`. `TO_DCE110_COMPRESSOR()` converts generic compressor pointers. Lifecycle APIs are `dce110_compressor_create()`, `dce110_compressor_construct()`, and `dce110_compressor_destroy()`. FBC APIs include power up, enable, disable, invalidation triggers, compressed surface address/pitch, and hardware-state query. LPT prototypes are declared as well.

Control flow role: the header lets resource code allocate and use the DCE110 implementation through generic compressor callbacks while still exposing specific helpers for FBC programming.

State and persistence: persistent software state is inherited from `struct compressor` plus current register offsets. Hardware FBC state persists outside the object.

Dependencies and integration: includes `../inc/compressor.h`, which supplies generic compressor fields, address/pitch params, and compression ratio/controller types. It integrates with the DCE110 Makefile and compressor function table in the C file.

Risks and test signals: LPT functions are declared but not implemented in the read implementation, so callers must rely on linked objects or avoid those symbols. Offset state must be refreshed before per-pipe register access. Compile/link tests should catch unused or missing LPT definitions; runtime tests should cover create/construct/destroy and FBC helper compatibility with the generic compressor interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_compressor.h -->
