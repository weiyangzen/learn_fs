# Research: subset-b-003583

Grouped research for the i915 display files assigned to `subset-b-003583`. Each section preserves the original source path so reconciliation can split this report into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc_state_dump.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc_state_dump.c

Purpose: debug-only KMS state dumping for `struct intel_crtc_state`, including pipe timing, link M/N values, infoframes, color/CSC/LUT state, VRR, DSC, scaler, fitter, DPLL, and current plane state. The main export is `intel_crtc_state_dump()`, which is gated by `drm_debug_enabled(DRM_UT_KMS)` and uses a DRM debug printer, so normal runtime behavior and persistence are unaffected unless KMS debug is enabled.

Important APIs and helpers: `intel_output_format_name()` maps `enum intel_output_format` to user-readable strings; `snprintf_output_types()` converts the output type bitmask to comma-separated names; `intel_dump_m_n_config()`, `intel_dump_crtc_timings()`, `intel_dump_plane_state()`, `ilk_dump_csc()`, and `vlv_dump_csc()` format substructures. HDMI/DP infoframes are delegated to DRM helpers such as `hdmi_infoframe_log()`, `drm_dp_vsc_sdp_log()`, and `drm_dp_as_sdp_log()`.

Control flow: `intel_crtc_state_dump()` prints the CRTC enable line and jumps directly to plane dumping when the pipe is disabled. For enabled pipes it walks feature groups in a fixed order: output identity, transcoder relationships, joiner/splitter, FDI/DP link state, PSR/replay/selective fetch, audio/infoframes/ELD, scanline/latency, VRR, requested/adjusted/pipe modes, port clock and cdclk, scalers, panel fitter, IPS/DRRS, DPLL, color/CSC/LUT, DSC, CASF, and then plane states from the supplied atomic state. Plane dumping only includes new plane states whose `plane->pipe` matches the CRTC.

State and persistence: the file does not mutate driver state. It reads `intel_crtc_state`, `intel_atomic_state`, `intel_plane_state`, display runtime/platform flags, and DRM framebuffer metadata for diagnostics. The only side effects are debug logs and possible `WARN_ON_ONCE()` when an unknown output type bit remains.

Dependencies and integration: used by modeset setup/verification and failure paths to compare software and hardware states. It depends on `intel_display_types.h` for state layout, `intel_hdmi.h` for infoframe enable mapping, `intel_vblank.h` and `intel_vrr.h` for derived timing values, `intel_vdsc.h` for DSC dumps, and `intel_dpll_dump_hw_state()` through included display types/core headers.

Risks: output is tightly coupled to `struct intel_crtc_state`; adding state fields without updating this dump reduces debug value. `snprintf_output_types()` depends on enum values matching the string table. The gamut metadata branch logs `infoframes.drm`, which may be intentional reuse or a possible naming ambiguity. Long debug output can be noisy during modeset failures but is gated by KMS debug.

Test signals: enable DRM KMS debug and exercise successful/failed atomic modesets, DP/eDP/HDMI cases, VRR/PSR/DSC/color-management configurations, and disabled CRTC cases. Useful validation is that software/hardware state mismatch reports contain enough fields to identify the mismatch and that unknown output bits trigger the one-time warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc_state_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc_state_dump.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc_state_dump.h

Purpose: public interface for CRTC state dumping and output-format name formatting. It forward-declares `struct intel_crtc_state`, `struct intel_atomic_state`, and `enum intel_output_format` to avoid pulling full display state definitions into callers.

Important APIs: `intel_crtc_state_dump(const struct intel_crtc_state *crtc_state, struct intel_atomic_state *state, const char *context)` logs a complete KMS diagnostic snapshot for one CRTC state, optionally including plane states from an atomic state. `intel_output_format_name(enum intel_output_format format)` returns a stable printable name or `"invalid"`.

Control flow and state: the header has no runtime behavior and no persistent state. It only exposes functions implemented in `intel_crtc_state_dump.c`.

Dependencies and integration: included by modeset setup, modeset verification, display commit/failure paths, DP code, and debugfs code that needs diagnostic output without depending on the implementation details.

Risks: the closing include guard comment names `__INTEL_CRTC_STATE_H__` while the guard macro is `__INTEL_CRTC_STATE_DUMP_H__`; this is cosmetic but can confuse readers. If `enum intel_output_format` changes, the implementation table must be updated to keep the API useful.

Test signals: compile coverage from all include sites is the main check. Functional validation comes from KMS debug logs that call the exported dump function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc_state_dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cursor.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cursor.c

Purpose: implements i915 cursor planes from legacy 845/865 hardware through modern i9xx+ cursor registers. It validates cursor framebuffers and geometry, programs cursor registers, supports a constrained legacy async update path, handles cursor framebuffer unpin after vblank, and creates cursor plane objects with the right callbacks/properties.

Important APIs and functions: `intel_cursor_plane_create()` allocates and initializes a cursor `struct intel_plane`; `intel_cursor_mode_config_init()` sets global cursor size limits; `intel_cursor_unpin_work()` releases old cursor FB state after vblank. Validation centers on `intel_check_cursor()`, `intel_cursor_check_surface()`, `i845_check_cursor()`, and `i9xx_check_cursor()`. Programming callbacks are `i845_cursor_update_arm()`/`disable_arm()` and `i9xx_cursor_update_arm()`/`disable_arm()`. `intel_legacy_cursor_update()` is the fast-path `drm_plane_funcs.update_plane` callback.

Control flow: generic checking rejects tiled framebuffers, runs clipping without scaling, restores unclipped rectangles because the hardware consumes original cursor coordinates, translates destination into pipe coordinates, computes GTT/aligned offset, and rejects arbitrary cursor panning. i845 checks add width alignment and limited stride encoding. i9xx checks require 64/128/256 widths, square cursors except IVB+ FBC-height cases, exact stride, and a CHV pipe C left-edge workaround. Update callbacks compute control/base/position/size values, write watermark/DDB registers for SKL+, handle PSR2 selective fetch, then arm hardware by ordering CURCNTR/CURPOS/CURBASE writes according to platform semantics.

State and persistence: cursor object state caches last programmed `base`, `cntl`, and `size`/FBC control to avoid full reprogramming when only position changes. Atomic plane state stores `ctl`, `surf`, `view.color_plane[0].offset`, and pinned GGTT VMA information. The legacy fast path swaps `plane->base.state` to a duplicated state, updates only `crtc_state->active_planes`, and schedules vblank work when the old VMA must remain alive for one more frame.

Dependencies and integration: integrated with DRM atomic helpers, i915 plane helper callbacks, frontbuffer tracking, framebuffer pinning, PSR locking, vblank evasion, display workarounds, selective fetch registers, and SKL watermark code. `intel_crtc.c` creates cursor planes through this module; display driver init calls `intel_cursor_mode_config_init()`.

Risks: register arming order is hardware-sensitive; removing the mandatory CURBASE write can break movement or shape updates. The async legacy path deliberately avoids modesets, fastsets, joiner pipes, pending commits, PSR2 selective fetch, and changes that affect watermarks; relaxing these checks risks state races or underruns. Cursor panning, non-linear modifiers, bad stride, and CHV pipe C negative X are rejected by design. Fast-path state swapping is delicate because CRTC state may be concurrently owned by atomic commit/page flip paths.

Test signals: cursor IGT coverage should include legacy `drmModeMoveCursor`/`drmModeSetCursor`, async position-only updates, disable/enable, vblank-delayed unpin, rotation 180, size-hints, damage clips on DISPLAY_VER >= 12, PSR2 selective fetch, SKL+ watermark writes, i845/i865 stride and size constraints, and CHV pipe C negative-X rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cursor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cursor.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cursor.h

Purpose: declares the cursor plane module interface used by display initialization and vblank work plumbing.

Important APIs: `intel_cursor_plane_create(struct intel_display *display, enum pipe pipe)` creates one DRM universal cursor plane for a pipe. `intel_cursor_unpin_work(struct kthread_work *base)` is the vblank work callback that unpins and destroys retired cursor plane state. `intel_cursor_mode_config_init(struct intel_display *display)` sets mode-config cursor dimensions based on platform.

Control flow and state: no direct behavior or state; it exposes functions implemented in `intel_cursor.c`. Forward declarations keep include dependencies small for `enum pipe`, `struct intel_display`, `struct intel_plane`, and `struct kthread_work`.

Dependencies and integration: used by CRTC construction, display driver mode-config initialization, and vblank work scheduling. Its functions bridge DRM plane creation with i915 cursor-specific callbacks.

Risks: callers must respect that created planes have platform-specific validation and programming callbacks. The unpin work callback expects `base` to be embedded in an `intel_plane_state` as initialized by cursor update code.

Test signals: build coverage from display initialization and runtime validation that every pipe gets a cursor plane with expected cursor size limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cursor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cursor_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cursor_regs.h

Purpose: register definition header for i915 cursor hardware. It centralizes MMIO offsets and bit fields for legacy CURCNTR/CURBASE/CURPOS/CURSIZE, modern MCURSOR controls, CUR_FBC_CTL, cursor watermarks/DDB, and PSR selective fetch cursor control.

Important definitions: `CURCNTR()`, `CURBASE()`, `CURPOS()`, `CURPOS_ERLY_TPT()`, `CURSIZE()`, `CUR_FBC_CTL()`, `CURSURFLIVE()`, `CUR_WM()`, `CUR_WM_TRANS()`, `CUR_WM_SAGV()`, `CUR_WM_SAGV_TRANS()`, `CUR_BUF_CFG()`, and `SEL_FETCH_CUR_CTL()`. Bit helpers encode enable, pipe gamma/CSC, pipe select, rotate-180, trickle-feed disable, cursor modes, signed position fields, FBC height, watermark enable/lines/blocks, and cursor DDB start/end.

Control flow and state: this header has no runtime control flow and stores no state. It provides typed MMIO macros consumed by `intel_cursor.c` and related display register code.

Dependencies and integration: depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PIPE`, `_MMIO_CURSOR2`, `REG_BIT`, `REG_GENMASK`, and field-prep helpers. The definitions map directly to hardware programming in cursor update and error-capture paths.

Risks: register encodings vary by display generation; comments document several generation boundaries such as old desktop 8xx control fields, new MCURSOR fields, IVB+ FBC control, SKL+ watermark registers, and TGL+ selective fetch. Incorrect field masks would corrupt hardware programming, so generation-specific callers must keep using the right fields.

Test signals: compile-time use by cursor programming plus runtime cursor movement/shape/watermark tests across pre-i9xx, i9xx/g4x, IVB+, SKL+, TGL+, and MTL+ hardware. Error-state capture should show sane CUR* register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cursor_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cx0_phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cx0_phy.c

Purpose: implements Meteor Lake/Lunar Lake/Panther Lake style CX0 PHY and PLL handling for C10 and C20 PHYs, including message-bus access, signal-level programming, PLL state calculation/readout/compare/dump, enable/disable sequences, Type-C/TBT clocking, powerdown transitions, ALPM LFPS setup, and PLL table self-verification.

Important APIs: public exports include `intel_encoder_is_c10phy()`, `intel_cx0_read()`, `intel_cx0_write()`, `intel_cx0_rmw()`, `intel_cx0_wait_for_ack()`, `intel_cx0_bus_reset()`, `intel_cx0_phy_set_signal_levels()`, `intel_cx0pll_calc_state()`, `intel_cx0pll_readout_hw_state()`, `intel_cx0pll_calc_port_clock()`, `intel_cx0pll_dump_hw_state()`, `intel_cx0pll_compare_hw_state()`, `intel_mtl_pll_enable()/disable()`, TBT clock helpers, `intel_mtl_port_pll_type()`, `intel_readout_lane_count()`, `intel_cx0_powerdown_change_sequence()`, `intel_cx0_setup_powerdown()`, `intel_lnl_mac_transmit_lfps()`, `intel_cx0_pll_power_save_wa()`, and `intel_cx0pll_verify_plls()`.

Control flow: every PHY message-bus transaction must run inside `intel_cx0_phy_transaction_begin()`/`end()`, which pauses PSR, takes `POWER_DOMAIN_DC_OFF`, and programs message-bus timers. Read/write helpers wait for idle, clear response flags, issue M2P commands, wait for P2M ACK, reset the bus on timeout/error, retry three times, and assert DC-off. C20 SRAM access layers 16-bit reads/writes over the byte-wide message bus.

PLL calculation and tables: C10 uses precomputed DP/eDP/HDMI tables and falls back to `intel_snps_hdmi_pll_compute_c10pll()` for HDMI rates not in the table. C20 uses MTL/XE2HPD/XE3LPD DP/eDP/HDMI tables, plus computed HDMI TMDS PLL values for 25.175-600 MHz when no table entry matches. `intel_c10pll_calc_port_clock()` and `intel_c20pll_calc_port_clock()` reverse-calculate effective port clocks and verify table entries. C20 VDR parameters encode DP vs HDMI/FRL, custom width, HDMI rate, and context toggle.

Enable sequence: `intel_cx0pll_enable()` computes port clock, warns on lane reversal in DP-alt mode, programs `PORT_CLOCK_CTL`, resets lanes, transitions PHY power to ready, programs C10 VDR or C20 SRAM PLL state, enables/disables owned TX lanes according to lane count and lane reversal, writes `DDI_CLK_VALFREQ`, requests the PLL/ref clock, waits for ACK/lock, and applies a C10 HDMI powerdown toggle workaround. Disable reverses the clock/power flow, clears PLL/refclk requests, writes VALFREQ zero, waits for ACK clear, and gates clocks.

State and persistence: persistent PLL data is stored in `struct intel_dpll_hw_state.cx0pll`, whose C10 state contains `tx`, `cmn`, and 20 PLL bytes, and whose C20 state contains TX/CMN/MPLLA/MPLLB arrays plus VDR fields. Runtime hardware state is in CX0 message-bus registers, C20 SRAM contexts A/B, port buffer control registers, `PORT_CLOCK_CTL`, `DDI_CLK_VALFREQ`, lane powerdown state, and DPLL manager state. The module does not allocate long-lived memory, but it mutates hardware and uses power wakerefs.

Dependencies and integration: DPLL manager delegates CX0 calc/readout/enable/disable/dump/compare operations to this file. DDI setup installs MTL clock hooks and signal-level hooks. Link training PHY code reuses raw CX0 message-bus helpers. Display reset and DPLL init call the power-save workaround and table verifier. Type-C mode helpers determine lane ownership, TBT/DP-alt behavior, and lane reversal constraints.

Risks: sequencing is highly hardware-sensitive: missing PSR pause/DC-off, wrong lane ownership in DP-alt mode, wrong context toggle for C20 SRAM, stale SSC bits, or incorrect powerdown state can cause PLL lock failures or display link instability. Several functions only warn on timeouts and continue, so failures may surface later as link training or modeset failures. `intel_cx0_phy.h` declares `intel_cx0_phy_check_hdmi_link_rate()` and `intel_cx0_is_hdmi_frl()` but this source tree search found no implementation in the display directory, which is a potential stale declaration or missing implementation risk.

Test signals: boot and modeset tests on C10 and C20 platforms, DP/eDP/HDMI TMDS/HDMI FRL/TBT/USB4/DP-alt cases, lane reversal, 1/2/4 lane DP, UHBR10/UHBR13.5/UHBR20, PSR/ALPM interactions, suspend/resume/reset power-save workaround, DPLL readout-vs-calculated comparison, table verification warnings, and forced message-bus timeout/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cx0_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cx0_phy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cx0_phy.h

Purpose: public interface for CX0 PHY/PLL operations, message-bus access, signal level programming, TBT clock handling, powerdown sequencing, and verification hooks.

Important APIs: the header exposes low-level message-bus helpers (`intel_cx0_read`, `write`, `rmw`, `wait_for_ack`, `bus_reset`, `clear_response_ready_flag`), PLL lifecycle helpers (`intel_cx0pll_calc_state`, `readout_hw_state`, `calc_port_clock`, `dump_hw_state`, `compare_hw_state`, `verify_plls`), MTL PLL/TBT clock wrappers, lane count readout, C10 PHY detection, signal-level setup, powerdown helpers, ALPM LFPS helper, and power-save workaround. It also defines `MB_WRITE_COMMITTED` and `MB_WRITE_UNCOMMITTED` boolean aliases used for message-bus writes.

Control flow and state: the header is declarative only. Callers must use these APIs in contexts where display power and encoder state are valid; the implementation handles PSR pause/DC-off for most PHY transactions.

Dependencies and integration: forward declarations keep DDI, DPLL manager, link training PHY, HDMI, reset, and display init code from including the large implementation headers. It depends on Linux integer types for `u8`/`u32`.

Risks: the header currently contains a duplicate declaration of `intel_mtl_pll_disable_clock()`. It also declares `intel_cx0_phy_check_hdmi_link_rate()` and `intel_cx0_is_hdmi_frl()`, but a display-tree search in this snapshot found declarations only and no implementation, so consumers would fail to link if these APIs are referenced unless implemented outside the searched scope. The raw read/write helpers are powerful and must not be called without respecting transaction/power sequencing.

Test signals: compile/link coverage for all declared APIs, plus DPLL manager and link-training call paths that exercise the raw and high-level CX0 operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cx0_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cx0_phy_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cx0_phy_regs.h

Purpose: register and bitfield map for CX0 PHY support. It covers DDI clock value, XeLPDP/Xe2LPD port message bus, port buffer control, port clock control, TCSS mailbox, C10 vendor registers, common PIPE registers, C20 VDR/SRAM windows, C20 context configuration addresses, C20 PLL math constants, and PICA eDP-on-TypeC configuration.

Important definitions: `DDI_CLK_VALFREQ`, `XELPDP_PORT_M2P_MSGBUS_CTL`, `XELPDP_PORT_P2M_MSGBUS_STATUS`, message-bus command/data/address/status bits, timeout constants, `XELPDP_PORT_BUF_CTL1/2/3`, powerdown and lane reset fields, `XELPDP_PORT_CLOCK_CTL` request/ack/clock-select/SSC fields, C10 `PHY_C10_VDR_*` registers, C20 byte access registers, C20 VDR custom rate/width/HDMI rate fields, C20 SRAM context address macros, and HDMI PLL computation constants.

Control flow and state: no executable logic; the macros encode platform-dependent MMIO offsets and field values consumed by `intel_cx0_phy.c`, link training PHY code, Type-C code, display device code, and SNPS HDMI PLL code.

Dependencies and integration: depends on display limits and register definition helpers. The `__xe2lpd_port_idx()` wrapper remaps non-TC ports into the second `_PICK_EVEN_2RANGES()` range for DISPLAY_VER >= 20, which is central to correct MMIO selection on newer platforms.

Risks: this file is a single source of truth for low-level hardware encodings; errors can cause message-bus transactions, lane resets, PLL requests, SSC, or context writes to target the wrong register. Generation-specific address differences for MTL vs XE2HPD C20 contexts and DISPLAY_VER >= 30 clock-select mask width are especially sensitive.

Test signals: build coverage, successful CX0 message-bus read/write, PLL enable/disable/readout on MTL/XE2HPD/XE3LPD, TBT clock select at DP1.4 and UHBR rates, HDMI TMDS/FRL programming, and register traces matching bspec expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cx0_phy_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dbuf_bw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dbuf_bw.c

Purpose: tracks the display data-buffer bandwidth pressure that contributes to minimum CDCLK selection on DISPLAY_VER >= 9. It models per-pipe, per-DBuf-slice maximum plane data rates and active plane counts, stores that model in an i915 global atomic object, and feeds old/new minimum CDCLK values into CDCLK recalculation.

Important APIs and types: private `struct intel_dbuf_bw` stores `max_bw[slice]` and `active_planes[slice]`; private `struct intel_dbuf_bw_state` embeds `struct intel_global_state` and per-pipe DBuf bandwidth arrays. Public helpers retrieve old/new/current global state, initialize the global object, update state from current hardware, clear one pipe during noatomic disable, compute minimum CDCLK, and participate in atomic CDCLK calculation.

Control flow: `skl_crtc_calc_dbuf_bw()` clears one pipe model, skips inactive CRTCs and cursor planes, then adds primary/sprite plane rates for their allocated DDB slices, including Y-plane DDB on DISPLAY_VER < 11. `intel_dbuf_bw_min_cdclk()` walks each DBuf slice, finds the maximum per-plane bandwidth and total active plane count across pipes, multiplies them to model equal-share arbiter limits, takes the maximum slice pressure, and divides by 64 rounded up. `intel_dbuf_bw_calc_min_cdclk()` compares old/new CRTC-derived bandwidth, obtains and updates global state only when needed, locks the global object when the aggregate state changes, and calls `intel_cdclk_update_dbuf_bw_min_cdclk()`.

State and persistence: persistent state lives in `display->dbuf_bw.obj.state` and is duplicated/destroyed through `intel_global_state_funcs`. Atomic transactions clone and mutate this global state; non-atomic setup/disable paths update it directly to keep software state in sync with hardware. No hardware registers are written by this file.

Dependencies and integration: depends on `skl_watermark.h` for DDB slice masks and watermark/DDB state, display core/types for pipes/planes/platform iteration, and CDCLK code for applying the derived minimum. Display driver init calls `intel_dbuf_bw_init()`, modeset setup refreshes state, CRTC disable can clear state noatomically, and `intel_cdclk.c` calls the calc/min helpers.

Risks: cursor planes are assumed too small to affect bandwidth; if future cursor behavior changes, this model may understate DBuf pressure. The equal-share arbiter approximation intentionally uses max plane rate times active plane count and may be conservative or inaccurate for unusual DDB splits. State must be locked when aggregate bandwidth changes to avoid racing other global-state users.

Test signals: atomic modeset tests that alter plane data rates, DDB allocations, pipe activity, and CDCLK requirements on SKL+ hardware; plane enable/disable and Y-plane cases on pre-Gen11; modeset setup/readout keeping `display->dbuf_bw.obj.state` synchronized; and CDCLK recalculation when only DBuf bandwidth changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dbuf_bw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dbuf_bw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dbuf_bw.h

Purpose: public interface for DBuf-bandwidth global state and minimum-CDCLK calculation.

Important APIs: `to_intel_dbuf_bw_state()` casts an `intel_global_state`; `intel_atomic_get_old_dbuf_bw_state()`, `intel_atomic_get_new_dbuf_bw_state()`, and `intel_atomic_get_dbuf_bw_state()` access the global object in an atomic transaction; `intel_dbuf_bw_init()` creates the global object; `intel_dbuf_bw_calc_min_cdclk()` updates atomic state and reports whether CDCLK recalculation is needed; `intel_dbuf_bw_min_cdclk()` computes the current minimum from a state object; `intel_dbuf_bw_update_hw_state()` and `intel_dbuf_bw_crtc_disable_noatomic()` keep non-atomic paths synchronized.

Control flow and state: declarative only. The opaque `struct intel_dbuf_bw_state` prevents callers from depending on internal arrays while allowing CDCLK and setup code to pass state objects around.

Dependencies and integration: includes `<drm/drm_atomic.h>` for atomic-related types and forward-declares i915 display structures. It is consumed by display driver init, CDCLK code, and modeset setup/disable paths.

Risks: callers must handle `ERR_PTR` from `intel_atomic_get_dbuf_bw_state()` and must not assume DBuf bandwidth is meaningful on DISPLAY_VER < 9, where implementation helpers return early or zero. Since state is global, misuse outside atomic locking rules can create inconsistent CDCLK decisions.

Test signals: compile coverage and integration tests for CDCLK recalculation with plane/DDB changes, plus noatomic disable/readout synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dbuf_bw.h -->
