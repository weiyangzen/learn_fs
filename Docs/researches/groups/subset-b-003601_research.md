# subset-b-003601 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite.c

Purpose: implements legacy i915 overlay or "sprite" plane support for G4x/ILK/SNB DVS registers, IVB/HSW/BDW sprite registers, and VLV/CHV SP registers. It creates DRM overlay planes and supplies the plane hooks that validate source/destination rectangles, compute display clock limits, program register state, disable planes, read hardware state, and capture error state.

Important APIs and functions: `intel_sprite_plane_create()` is the exported construction path. It chooses per-platform callbacks for `update_noarm`, `update_arm`, `disable_arm`, `capture_error`, `get_hw_state`, `check_plane`, stride/alignment/CDCLK helpers, formats, modifiers, and plane funcs. `vlv_plane_min_cdclk()`, `ivb_plane_min_cdclk()`, and `hsw_plane_min_cdclk()` model bandwidth requirements. `chv_plane_check_rotation()` rejects CHV rotate-plus-reflect combinations. Private helpers build control words (`vlv_sprite_ctl()`, `ivb_sprite_ctl()`, `g4x_sprite_ctl()`), write gamma/CSC/CLRC programming, and validate scaling.

Control flow: atomic plane validation enters `vlv_sprite_check()` or `g4x_sprite_check()`, clips, checks surface coordinates, enforces scaling limits, and stores the final hardware control word in `plane_state->ctl`. Commit code later calls no-arm writers for stride/position/size/scaler state, then arm writers for color key, offsets, control, and surface address. Surface register writes are intentionally last because they arm the update. Disable paths clear control/scaler and surface registers.

State and persistence: state is mostly transient atomic state plus MMIO. Persistent hardware state includes control, surface, colorkey, gamma, CSC, scaler, and live surface registers. The code uses power-domain refs before reading plane state and uses frontbuffer bits, immutable zpos, color properties, rotation properties, and modifier lists when creating planes.

Dependencies and integration: integrates with DRM atomic helpers, `intel_plane`, `intel_fb`, `intel_frontbuffer`, i9xx surface helpers, display power, and `intel_sprite_regs.h`. It is compiled only for I915 through the header. Test signals include kms_plane, rotation/reflection, colorkey, YUV limited/full range, scaling, X tiling, suspend/resume hardware readout, pipe underrun/error capture, and CDCLK bandwidth tests. Risks are hardware-specific bit programming, single-buffered gamma/CLRC updates, scaling fetch limits, CHV pipe-B special formats/CSC, VTD guard alignment, and register ordering around self-arming control/surface writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite.h

Purpose: declares the public interface for legacy sprite plane support. Under `I915` it exposes plane construction, source-coordinate validation, CHV rotation validation, and per-platform minimum CDCLK helpers. Outside `I915`, `intel_sprite_plane_create()` is an inline stub returning `NULL`, keeping shared display code buildable when this legacy implementation is absent.

Important APIs: `intel_sprite_plane_create(struct intel_display *, enum pipe, int)` builds one overlay plane for a pipe and sprite index. `intel_plane_check_src_coordinates()` is declared here although implemented elsewhere, so sprite validation can share source coordinate rules. `chv_plane_check_rotation()` enforces a Cherryview hardware limitation. `ivb_plane_min_cdclk()`, `hsw_plane_min_cdclk()`, and `vlv_plane_min_cdclk()` are reusable bandwidth calculators.

Control flow and integration: display plane enumeration calls the create helper when sprite planes exist. Atomic check paths can call the validation helpers through the `intel_plane` function pointers selected in `intel_sprite.c`. The header depends only on forward declarations and `linux/types.h`, minimizing include coupling.

State and persistence: no state is stored here. Its main persistence risk is ABI or compile-time contract drift: callers rely on I915-only declarations and the non-I915 stub behavior. Tests should cover I915 builds with sprite planes and non-I915 builds where the stub path compiles cleanly.

Risks: changing prototypes affects plane initialization and any primary-plane code reusing the CDCLK helpers. The `enum pipe` type differs from the stub argument type (`int pipe`), so cross-build compatibility should be checked if this interface changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite_regs.h

Purpose: defines MMIO register addresses and bitfields used by legacy sprite plane code. It covers three families: G4x/ILK/SNB DVS registers, IVB/HSW/BDW sprite registers, and VLV/CHV SP registers including CHV pipe-B sprite CSC registers.

Important definitions: DVS macros include `DVSCNTR`, `DVSSTRIDE`, `DVSPOS`, `DVSSIZE`, key registers, `DVSSURF`, `DVSSCALE`, and G4x/ILK gamma registers. IVB macros include `SPRCTL`, `SPRSTRIDE`, `SPRPOS`, `SPRSIZE`, key/surface/offset/scaler/gamma registers. VLV/CHV macros include `_VLV_SPR()`, `SPCNTR`, `SPSTRIDE`, `SPPOS`, `SPSIZE`, key/surface/tile/constant-alpha/CLRC/gamma registers, plus `SPCSC*` CSC coefficient and clamp registers.

Control flow and integration: `intel_sprite.c` composes control words and register payloads from these macros before calling `intel_de_write*()` or `intel_de_read()`. Field helpers such as `REG_FIELD_PREP`, `REG_BIT`, `_MMIO_PIPE`, and VLV base offsets make the register programming readable and constrain bit placement.

State and persistence: this header itself stores no state, but it defines all persistent hardware state touched by the sprite commit paths: enable bits, pixel formats, YUV order/range, rotation, tiling, source/destination keying, offsets, live surface, gamma, and CSC. It is therefore part of the hardware contract.

Risks and tests: risks are incorrect field widths, wrong pipe/plane address calculations, and family-specific bit reuse such as HSW `SPROFFSET` sharing an IVB tile offset address. Test signals are plane enable/disable, supported pixel formats, tiling, YUV conversion, gamma, color keying, scaling, CHV pipe-B CSC, and error-state capture matching live MMIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite_uapi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite_uapi.c

Purpose: implements the legacy `DRM_IOCTL_I915_SET_SPRITE_COLORKEY` path. It translates a userspace `drm_intel_sprite_colorkey` request into atomic plane state updates for overlay planes and, on newer hardware, the relevant primary plane.

Important functions: `intel_sprite_set_colorkey_ioctl()` validates flags, locates the requested DRM overlay plane, builds an internal atomic state, updates color-key fields, and commits it with deadlock retry. `intel_plane_set_ckey()` copies the requested key into `intel_plane_state::ckey` and masks unsupported placement. `has_dst_key_in_primary_plane()` currently returns true for display version 9 and newer.

Control flow: the ioctl clears the no-op `I915_SET_COLORKEY_NONE` bit, rejects unknown flags and simultaneous source/destination keying, rejects destination keying on VLV/CHV, rejects non-overlay or missing planes, and rejects SKL+ destination keying on plane 3 or later. It then obtains the overlay plane state and optionally the primary plane state for the same pipe, calls `intel_plane_set_ckey()` on each, and commits atomically, backing off on `-EDEADLK`.

State and persistence: the persistent software state is `plane_state->ckey`; hardware programming happens later in the plane update callbacks in `intel_sprite.c` and primary-plane code. On SKL+ destination keying is stored on the primary and cleared on sprite planes; source keying is stored on sprites and cleared on primary planes.

Dependencies and tests: depends on DRM plane lookup, modeset acquire contexts, atomic state helpers, `intel_crtc_for_pipe()`, and display version/platform data. Test signals include invalid flag rejection, source vs destination exclusivity, VLV/CHV destination-key rejection, SKL+ plane restrictions, primary-plane companion updates, atomic deadlock retry, and visual colorkey behavior. Risks include legacy UAPI compatibility and mismatched software placement versus hardware programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite_uapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite_uapi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite_uapi.h

Purpose: declares the legacy sprite colorkey ioctl handler. It keeps UAPI-facing implementation details out of broader display headers while forward-declaring only `drm_device` and `drm_file`.

Important API: `intel_sprite_set_colorkey_ioctl(struct drm_device *dev, void *data, struct drm_file *file_priv)` is the single exported entry point. It is intended to be registered in the i915 ioctl table and implemented by `intel_sprite_uapi.c`.

Control flow and integration: userspace reaches this function through DRM ioctl dispatch. The implementation parses `data` as `struct drm_intel_sprite_colorkey`, performs DRM plane lookup using `file_priv`, and commits an internal atomic update. The header deliberately does not expose plane-state internals.

State and persistence: no direct state. Its contract preserves the legacy ioctl ABI and ties the UAPI handler to DRM core types.

Risks and tests: prototype drift would break ioctl table registration. Build tests should include this header in ioctl code without requiring unrelated display internals. Behavioral testing belongs to `intel_sprite_uapi.c`, especially invalid input and atomic color-key placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite_uapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tc.c

Purpose: manages Intel Type-C display ports, including legacy, DP alternate mode, and Thunderbolt alternate mode. It hides platform-specific PHY ownership and power sequencing behind `intel_tc_phy_ops` and exposes a lock/refcount API that lets AUX, modeset, MST, hotplug, and link reset code treat a TC port as connected only when it is usable by display.

Important types and APIs: `enum tc_port_mode` tracks disconnected/TBT-alt/DP-alt/legacy. `struct intel_tc_port` stores the digital port, selected PHY ops, mutex, TC-cold wakeref, delayed works, link refcount, legacy flag, mode/init mode, FIA indices, pin assignment, and max lane count. Public functions include mode queries, `intel_tc_port_connected()`, lane/pin helpers, mode init/sanitize, lock/unlock, get/put link, suspend, link reset scheduling, init/cleanup, `intel_tc_cold_requires_aux_pw()`, and debug printing.

Control flow: init allocates `intel_tc_port`, selects ops by display version, initializes FIA mapping, reads hardware mode, possibly connects the PHY for readout, and pins the mode until sanitize. Locking cancels delayed disconnect and connects the PHY if no link reference is active. Link references keep a usable mode across modesets or AUX operations. Unlock without refs schedules delayed disconnect. DP-alt live-state changes can queue a reset work item that performs an internal atomic commit marking active connectors changed.

State and persistence: persistent driver state is `tc->mode`, `init_mode`, `legacy_port`, pin assignment, max lanes, `lock_wakeref`, and `link_refcount`; persistent hardware state includes PHY ownership bits, TCSS power requests, FIA lane selection, DDI buffer ownership, and HPD live status. Delayed work persists asynchronous disconnect/reset intent.

Dependencies and integration: depends on display power domains, hotplug ISR masks, DDI/DP/MST code, modeset locks, atomic commits, FIA/MG/DKL/CX0/TCSS registers, and platform runtime info. Risks include power-domain imbalance, stale HPD live mode, incorrect lane counts for DP-alt pin assignments, races between delayed disconnect and link use, firmware readiness timeouts, and platform-specific ownership semantics. Test signals include hotplug in all TC modes, AUX access under TC-cold, MST active streams, suspend/resume sanitize, DP-alt disconnect while active, lane count negotiation, legacy VBT mismatch fixup, and runtime PM wakeref leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tc.h

Purpose: defines the public Type-C display-port interface and the stable hardware-mapped pin-assignment enum. It is consumed by DDI, DP, hotplug, modeset, debugfs, and power-management code.

Important APIs and types: `enum intel_tc_pin_assignment` values must match PORT_TX_DFLEXPA1 and TCSS_DDI_STATUS fields. The comments document DP/USB lane use, cable types, and DP-alt standards. Query helpers report TC mode, HPD-glitch behavior, connection usability, max lanes, and pin assignment. State-management helpers initialize and sanitize modes, lock/unlock the port, get/put link references, check/cancel/schedule link resets, suspend, init/cleanup, and print debug info.

Control flow and integration: callers bracket operations that need a usable PHY with `intel_tc_port_lock()`/`unlock()` or longer-lived `get_link()`/`put_link()`. Modeset readout calls init/sanitize. Hotplug/link code uses `intel_tc_port_connected()` and reset helpers. Power code uses `intel_tc_cold_requires_aux_pw()` to decide whether AUX power blocks TC-cold.

State and persistence: state is opaque in `intel_tc.c`; this header exposes only stable queries and operations. The pin-assignment enum is effectively persistent ABI to register fields and should not be renumbered.

Risks and tests: changes can break TC mode arbitration, lane negotiation, or build-time users. Test signals include compiling all users, exercising each mode query, validating lane counts for pin C/D/E on DP2 platforms and legacy ICL assignments, suspend/resume, and DP-alt hot-unplug link reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tdf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tdf.h

Purpose: declares the Transient Data Flush display hook for Xe2+ cache-coherency handling. The comment explains that display surfaces rendered with special L3:XD PAT caching need KMD-enforced transient cache flushes before display flips because the display engine is not coherent with CPU/GPU caches.

Important API: `intel_td_flush(struct intel_display *display)`. Under `I915` it is an inline no-op. Non-I915 builds get an external declaration, allowing Xe display code to provide a real implementation.

Control flow and integration: flip or scanout paths can call `intel_td_flush()` through shared display code without branching on driver family. I915 keeps zero behavior because this cache mode is not active there.

State and persistence: the header stores no state. The relevant persistent behavior is cache visibility before a display flip; the no-op versus real implementation boundary is build-time.

Risks and tests: the main risk is forgetting to call the hook before a scanout surface becomes visible on platforms that enable transient caching. Tests should include Xe display flip coherency with PAT modes, I915 build coverage for the no-op inline, and static checks that shared code can include this header without pulling in driver-private cache definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tdf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tv.c

Purpose: implements integrated analog TV-out support for old Intel mobile chipsets. It creates a TV DAC encoder and S-Video connector, exposes legacy TV mode/margin properties, validates and generates scaled modes, programs TV timing/color/filter registers, and performs load-based connector detection.

Important types and functions: `struct intel_tv` wraps an encoder and detected connector type. `struct tv_mode` is the central mode table entry, holding timing, subcarrier DDA, colorburst, level, CSC, and filter data for NTSC/PAL/component modes. `intel_tv_compute_config()` derives pipe config and adjusted timings. `intel_tv_pre_enable()` writes TV_CTL, timing, subcarrier, CSC, levels, window, and filter tables. `intel_tv_detect_type()` temporarily enters monitor-detect test mode and interprets DAC sense bits. Connector funcs cover detect, mode validation, mode generation, atomic check, and property setup.

Control flow: init exits if TV fuse/VBT/register sanity checks fail, allocates encoder/connector objects, installs helper funcs and properties, and attaches the encoder. Detection requires load-detect pipe ownership for forced probes, disables TV hotplug interrupts during DAC sense, waits for vblank, restores registers, and updates connector type/format. Modes are generated by scaling static TV timings to common input resolutions while respecting component-only and gen3 wide-source limits. Atomic property changes force a modeset.

State and persistence: software state includes connector TV properties, `intel_tv->type`, duplicated connector state with adjusted margins and `bypass_vfilter`, and pipe mode flags. Hardware persistence includes TV_CTL, TV_DAC, CSC, color levels, horizontal/vertical timing registers, subcarrier DDA, filter control, window position/size, and 206 filter coefficient registers.

Dependencies and tests: depends on DRM connector/encoder helpers, EDID/mode helpers, load-detect, DPLL computation, display IRQ hotplug helpers, TV register definitions, and BIOS presence checks. Risks include load-detect register restoration, vblank wait requirements, gen3 wide-mode vertical-filter bypass, interlace clock handling, static timing table correctness, and analog DAC sense ambiguity. Test signals include forced detection for composite/S-Video/component, property-driven modesets, NTSC/PAL/component mode lists, suspend/resume readout, i965gm scanline-counter fallback, and no underruns when idle polling is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tv.h

Purpose: declares TV-out initialization for I915 and provides a no-op inline stub for non-I915 builds. This keeps shared display initialization code able to call `intel_tv_init()` without depending on legacy analog TV support.

Important API: `intel_tv_init(struct intel_display *display)` creates the TV encoder and connector when supported and present. The real implementation lives in `intel_tv.c`; the non-I915 stub performs no action.

Control flow and integration: display device initialization can call this function after MMIO and BIOS data are available. The implementation then checks fuses, VBT TV presence, TV DAC sanity, allocates DRM objects, and registers TV connector helpers.

State and persistence: no state in the header. Its compile-time contract determines whether TV-out is possible in a given build. For I915, successful init creates persistent DRM encoder/connector objects and hardware programming paths.

Risks and tests: interface changes affect display initialization. Test signals include I915 builds with TV enabled, non-I915 builds where the inline stub compiles away, and boot paths on machines without TV hardware where the call safely no-ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tv_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tv_regs.h

Purpose: defines the integrated TV encoder register map used by `intel_tv.c`. It covers encoder control, DAC sense/control, color-space conversion, color knobs/levels, horizontal and vertical timing, subcarrier DDA, window placement, scaling filters, closed-caption fields, and filter coefficient tables.

Important definitions: `TV_CTL` contains enable, pipe select, output type, oversample, progressive, PAL burst, test mode, and fuse-state bits. `TV_DAC` contains state-change, sense, DAC voltage, and override bits. `TV_CSC_*`, `TV_CLR_KNOBS`, and `TV_CLR_LEVEL` program color conversion and analog levels. `TV_H_CTL_*`, `TV_V_CTL_*`, and `TV_SC_CTL_*` program timings and subcarrier generation. `TV_WIN_POS`, `TV_WIN_SIZE`, `TV_FILTER_CTL_*`, `TV_CC_*`, and `TV_*_LUMA/CHROMA()` support scaling, captions, and coefficient tables.

Control flow and integration: `intel_tv_pre_enable()` writes most of these registers from a selected `tv_mode`; `intel_tv_get_config()` reads timing/window fields back; `intel_tv_detect_type()` uses TV_CTL test mode plus TV_DAC sense bits; `intel_tv_init()` checks fuse and DAC state-change behavior.

State and persistence: this header defines all persistent TV MMIO state. Some fields are explicitly save/preserve masks (`TV_CTL_SAVE`, `TV_DAC_SAVE`) and must not be clobbered by mode programming or load detection.

Risks and tests: risks include wrong preserve masks, off-by-one timing fields, DAC voltage/sense misuse during load detect, and register-table length mismatches for 60 horizontal and 43 vertical luma/chroma coefficients. Test signals include analog connector detection, mode programming readback, property changes, TV disable/enable cycles, and register state restoration after detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tv_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vblank.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vblank.c

Purpose: implements i915 display vblank counters, scanout position/timestamp helpers, scanline waits, active timing updates, interlace-aware timing accessors, and vblank evasion used to avoid unsafe atomic updates around double-buffer latch points.

Important functions: `i915_get_vblank_counter()` synthesizes a vblank counter from gen3/4 frame and pixel counters. `g4x_get_vblank_counter()` reads G4x frame count directly. `intel_crtc_get_vblank_timestamp()` bridges DRM vblank timestamping through `i915_get_crtc_scanoutpos()`. `intel_get_crtc_scanline()` returns adjusted scanline position. `intel_crtc_update_active_timings()` updates DRM timestamp constants and CRTC scanline/VRR state under locks. `intel_vblank_evade_init()` and `intel_vblank_evade()` compute and wait out the dangerous pre-vblank update window.

Control flow: scanout queries enter a timing-critical section with local IRQs disabled and, for I915, the uncore lock held. Depending on platform/mode flags they read scanline counters, timestamp registers, or pixel counters, normalize for interlace, vblank start/end, hsync timing, VRR, and scanline offsets, then return DRM's signed vblank-relative position. Vblank evasion prepares a wait on the vblank queue, repeatedly samples the scanline, sleeps up to a short timeout while inside the dangerous range, and applies a VLV/CHV DSI polling workaround for the first vblank line.

State and persistence: persistent software state includes `crtc->mode_flags`, `scanline_offset`, `vmax_vblank_start`, DRM timestamp constants, and vblank counter behavior. Hardware state includes frame/pixel counters, PIPEDSL, PIPE_FRMTMSTMP, IVB timestamp counter, and VRR-derived vblank limits.

Dependencies and tests: depends on DRM vblank helpers, display MMIO, color DSB decisions, VRR helpers, mode flags from TV/DSI/HDMI, and atomic state helpers. Risks are timestamp races across vblank, platform-specific scanline offsets, VRR dynamic vblank handling, uncore serialization, interlaced field math, and update failure if evasion misses latch windows. Test signals include vblank timestamp accuracy, page-flip jitter, VRR fastset/LRR/M/N updates, TV/DSI scanline fallback, suspend/resume counters, and atomic commit stress near vblank.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vblank.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vblank.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vblank.h

Purpose: declares the vblank, scanline, timing, and evasion interfaces used by i915 display modeset and DRM vblank integration.

Important types and APIs: `struct intel_vblank_evade_ctx` stores the target CRTC, min/max unsafe scanline range, vblank start, and VLV/CHV DSI workaround flag. Timing helpers expose interlace-aware `intel_mode_vdisplay()`, `intel_mode_vblank_start()`, `intel_mode_vblank_end()`, `intel_mode_vtotal()`, and `intel_mode_vblank_delay()`. Runtime APIs include vblank counter readers, timestamp helper, scanline getter, scanline moving/stopped waits, active timing updates, scanline offset calculation, pre-commit state selection, and vblank length.

Control flow and integration: atomic commit code initializes and executes vblank evasion before sensitive register writes. DRM vblank core calls the counter and timestamp helpers. Modeset code updates active timings after mode or VRR state changes. Encoder-specific code can force scanline-counter flags that affect the implementation.

State and persistence: no direct state in the header, but it exposes operations that mutate CRTC timing state and depend on active hardware counters. The evasion context is short-lived per commit.

Risks and tests: callers must enable vblank interrupts before `intel_vblank_evade()`, as documented. Prototype or semantic changes can affect page flips, timestamping, VRR, and atomic update correctness. Test signals include build coverage for all users, vblank timestamp tests, VRR mode changes, atomic commit stress, and scanline wait behavior on enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vblank.h -->
