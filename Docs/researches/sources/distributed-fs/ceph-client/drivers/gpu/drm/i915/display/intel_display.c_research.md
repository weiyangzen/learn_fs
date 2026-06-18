# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display.c

## Purpose

`intel_display.c` is the central Intel i915 display modeset and atomic commit coordinator for the display engine. It translates DRM atomic CRTC/plane/connector state into Intel pipe, transcoder, PLL, watermark, scaler, color, power-domain, joiner, PSR/FBC/VRR, and encoder operations. The file covers both legacy display generations and modern DDI/SKL+ display paths by selecting an `intel_display_funcs` table at initialization.

The file is not a standalone filesystem component despite its repository path under `distributed-fs/ceph-client`; it is Linux GPU display driver code. Its correctness depends on exact hardware sequencing, register programming, power-domain lifetime, and DRM atomic state ownership.

## Important APIs, Types, And Functions

- DRM/i915 state types: `struct drm_atomic_state`, `struct intel_atomic_state`, `struct intel_crtc_state`, `struct intel_plane_state`, `struct intel_crtc`, `struct intel_encoder`, `struct intel_display`, `struct intel_link_m_n`, `struct intel_power_domain_mask`, and `struct intel_display_funcs`.
- Joiner helpers: `intel_crtc_is_bigjoiner_primary()`, `intel_crtc_is_bigjoiner_secondary()`, `intel_crtc_is_ultrajoiner()`, `intel_crtc_joiner_secondary_pipes()`, `intel_crtc_num_joined_pipes()`, `intel_primary_crtc()`, `_intel_modeset_primary_pipes()`, and `_intel_modeset_secondary_pipes()` interpret `crtc_state->joiner_pipes` for bigjoiner, ultrajoiner, and uncompressed joiner configurations.
- Transcoder and pipe programming: `intel_enable_transcoder()`, `intel_disable_transcoder()`, `intel_set_transcoder_timings()`, `intel_set_transcoder_timings_lrr()`, `intel_set_pipe_src_size()`, `i9xx_set_pipeconf()`, `ilk_set_pipeconf()`, `hsw_set_transconf()`, and `bdw_set_pipe_misc()` write timing, pipe source, BPC, dither, colorspace, interlace, DSC/FEC workaround, and HDR-related registers.
- CRTC enable/disable paths: `i9xx_crtc_enable()/disable()`, `valleyview_crtc_enable()`, `ilk_crtc_enable()/disable()`, and `hsw_crtc_enable()/disable()` implement generation-specific sequencing for PLLs, FDI/PCH, DDI, DSC, pfit/scalers, color, watermarks, vblank, encoders, DMC, and DPLL handling.
- Hardware readout: `i9xx_get_pipe_config()`, `ilk_get_pipe_config()`, `hsw_get_pipe_config()`, `intel_crtc_get_pipe_config()`, `intel_encoder_get_config()`, `intel_get_transcoder_timings()`, `intel_get_pipe_src_size()`, and `intel_crtc_readout_derived_state()` reconstruct software state from live registers.
- Atomic validation: `intel_atomic_check()`, `intel_atomic_check_config_and_link()`, `intel_atomic_check_config()`, `intel_modeset_pipe_config()`, `intel_crtc_compute_config()`, `intel_crtc_atomic_check()`, `intel_crtc_check_fastset()`, `intel_pipe_config_compare()`, `intel_async_flip_check_uapi()`, and `intel_async_flip_check_hw()` validate modes, link bandwidth, DPLL, scalers, color, watermarks, joiner relationships, async flips, and fastset eligibility.
- Atomic commit: `intel_atomic_commit()`, `intel_atomic_commit_tail()`, `intel_commit_modeset_disables()`, `intel_commit_modeset_enables()`, `skl_commit_modeset_enables()`, `intel_pre_update_crtc()`, `intel_update_crtc()`, `commit_pipe_pre_planes()`, `commit_pipe_post_planes()`, `intel_post_plane_update()`, and `intel_post_plane_update_after_readout()` execute the hardware transition and final verification.
- DSB/FlipQ paths: `intel_atomic_dsb_prepare()`, `intel_atomic_dsb_finish()`, `intel_atomic_dsb_wait_commit()`, and `intel_atomic_dsb_cleanup()` opportunistically use display state buffers or flip queues for eligible non-modeset plane/color updates.
- Output setup and mode validation: `intel_setup_outputs()`, `intel_init_display_hooks()`, `intel_mode_valid()`, `intel_cpu_transcoder_mode_valid()`, `intel_mode_valid_max_plane_size()`, `intel_max_uncompressed_dotclock()`, and the encoder possible clone/CRTC helpers initialize encoder objects and reject impossible modes.

## Control Flow

The normal atomic path begins in `intel_atomic_check()`. It rejects display access when the driver is unavailable, clears inherited BIOS state after user commits, lets DRM core perform modeset checks, validates async flip UAPI constraints, computes pipe/link configuration with retryable link bandwidth limits, propagates joiner secondary state, attempts to downgrade full modesets to fastsets via `intel_pipe_config_compare()`, resolves external dependencies such as MST master transcoders and port sync, checks digital port conflicts, validates planes, global watermarks, bandwidth, CDCLK, Pmdemand, per-CRTC color/scaler/watermark/PSR/FBC constraints, and finally dumps modeset/fastset state for debugging.

`intel_atomic_check_config()` is the core modeset configuration builder. It first pulls in affected joiner and FDI CRTCs. For non-modeset CRTCs it copies UAPI blobs into hardware state. For modeset primaries it clears most computed hardware state while preserving selected persistent fields, computes baseline pipe BPP from platform limits and connector EDID/max_bpc, sets pipe source from the requested mode, validates encoder cloning, lets encoders compute and late-compute mode/link details, computes DPLL, set-context latency, pipe source/mode, pixel rate, FDI or VRR guardband, and records the pipe that failed so link bandwidth code can retry with lower BPP.

Commit entry is `intel_atomic_commit()`. It takes a runtime PM wakeref, prepares planes, sets up DRM and Intel global commits, swaps DRM/global/DPLL state, tracks frontbuffers, and dispatches `intel_atomic_commit_tail()` either synchronously or on the modeset/flip workqueue for nonblocking commits.

`intel_atomic_commit_tail()` is the main hardware sequencing routine. It prepares DSB/FlipQ state, waits fences, flushes TDF, reads fast-clear colors, prepares FBC dirty rectangles, waits dependency fences, disables DC states, acquires required CRTC power domains, disables old modeset pipes, allocates DP tunnel bandwidth, updates `crtc->config`, updates Pmdemand/CDCLK/SAGV/DBUF ordering, enables async flip-done interrupts, calls the selected `commit_modeset_enables()` hook, waits flip completion, waits DSB completion, optimizes watermarks, runs post-plane updates, verifies CRTC state and planes, checks FIFO underruns, restores SAGV/CDCLK/Pmdemand state, completes global commit state, arms unclaimed MMIO detection after modesets, drops power refs asynchronously, and queues old-state cleanup work.

For SKL+ hardware, `skl_commit_modeset_enables()` adds DDB allocation ordering. It first updates already-active pipes in an order that avoids overlapping old/new DBUF allocations, then enables independent modeset pipes, then dependent MST/port-sync/joiner pipes, and finally performs plane updates in reverse order so joiner primary events are emitted after secondaries complete.

## State And Persistence Behavior

The durable state here is kernel driver memory and hardware register state, not filesystem persistence. Important persistent-in-runtime fields include `crtc->active`, `crtc->config`, `crtc->enabled_power_domains`, `crtc->hw_readout_power_domains`, `intel_crtc_state` hardware/uapi substate, DPLL assignments, DSB pointers, and framebuffer/frontbuffer tracking.

Atomic state has strict ownership transitions. `intel_atomic_swap_state()` swaps DRM state, Intel global state, DPLL state, and frontbuffer tracking before the commit tail programs hardware. Old CRTC state later receives transferred `dsb_color` and `dsb_commit` pointers so cleanup aligns with framebuffer cleanup in `intel_atomic_cleanup_work()`.

Joiner state is replicated from the primary CRTC to secondary CRTCs. `copy_joiner_crtc_state_modeset()` clones the primary computed state while preserving secondary UAPI, scaler, DPLL, CRC, and DP tunnel references; `copy_joiner_crtc_state_nomodeset()` mirrors color blob state. `kill_joiner_secondaries()` restores secondaries to independent CRTC state when a joiner link is torn down.

Power state is managed explicitly. `intel_modeset_get_crtc_power_domains()` computes pipe, transcoder, pfit, encoder, audio, display core, and DSC power domains required by a CRTC state and takes missing refs in `crtc->enabled_power_domains`; `intel_modeset_put_crtc_power_domains()` drops domains no longer needed after verification. Commit tail holds `POWER_DOMAIN_DC_OFF` through register programming to avoid DC state save/restore races with noarm/arm register pairs and PSR.

Hardware readout paths populate software state from live registers after boot, resume, or verification. They use power-domain guards to avoid reading powered-off blocks. Derived state reconstructs full user/adjusted/pipe modes from raw transcoder timings, MSO splitter data, joiner pipe counts, pfit scaling, and pixel rates.

## Dependencies And Integration Points

This file integrates deeply with DRM core atomic helpers (`drm_atomic_helper_check_modeset`, `drm_atomic_helper_prepare_planes`, `drm_atomic_helper_swap_state`, commit setup, flip waits, event delivery), DRM DP/MST/tunnel helpers, HDMI/DP infoframe logging, DMA fences, runtime PM, workqueues, and vblank APIs.

It depends on many i915 display subsystems through local headers: DDI/DP/HDMI/DSI/LVDS/SDVO/TV/CRT encoder initialization and hooks, DPLL manager, FDI/PCH, CDCLK, SAGV, DBUF, bandwidth, watermarks, FBC, PSR, DRRS, VRR, ALPM/LOBF, CASF, color management, scalers, pipe CRC, frontbuffer tracking, DMC/PipeDMC, Pmdemand, DSB, FlipQ, DSC, DPT, and platform workarounds.

The `intel_display_funcs` tables are the central generation dispatch point:

- `skl_display_funcs` uses HSW-style pipe readout/enable/disable, SKL initial plane hooks, and SKL DDB-aware commit ordering.
- `ddi_display_funcs` uses HSW-style DDI paths without SKL DDB commit ordering.
- `pch_split_display_funcs` uses ILK/PCH split paths.
- `vlv_display_funcs` uses i9xx readout with Valleyview enable behavior.
- `i9xx_display_funcs` covers older GMCH platforms.

Encoder integration is hook-based. This file calls encoder hooks for `pre_pll_enable`, `pre_enable`, `enable`, `disable`, `post_disable`, `post_pll_disable`, `update_pipe`, `audio_enable`, `audio_disable`, `compute_config`, `compute_config_late`, `get_config`, `get_hw_state`, and optional initial fastset checks.

## Risks And Edge Cases

- Register sequencing is high risk. Many comments document platform workarounds where changing enable order, vblank waits, or noarm/arm timing can cause FIFO underruns, corrupted frames, hangs, or state checker failures.
- Power-domain mistakes can hang MMIO reads or leave registers inaccessible. DSI readout explicitly avoids register access unless PLL state is valid, and most readout paths use `intel_display_power_get_if_enabled()` or power-domain sets.
- Joiner and ultrajoiner handling is fragile. Primary/secondary masks have hardware-specific bit patterns, ultrajoiner has a special enable-bit exception, async flips are disabled with joiner, and state replication must preserve selected secondary-owned fields.
- Fastset eligibility depends on `intel_pipe_config_compare()` matching a large set of fields while intentionally excluding or relaxing some fields for LRR, M/N updates, PSR/VRR infoframes, and inherited fastboot. A missed compare field can allow unsafe register updates; an over-strict compare can cause unnecessary full modesets.
- Async flip is intentionally narrow. It requires active non-modeset CRTCs, async-capable planes, no joiner, stable active plane masks, no format/modifier/stride/rotation/size/blend/color/decrypt changes once true async flipping is active, and special VTD workarounds.
- Legacy platforms have special behavior: i830 keeps pipes enabled and may force a 640x480 pipe for power/quirk reasons; Gen2 underrun reporting is disabled when all planes are off; old GMCH memory self-refresh and IVB LP watermark restrictions require vblank waits.
- Output probing relies on platform straps, VBT, BIOS-derived port presence, and exceptions for eDP/LVDS/PPS sharing. Incorrect VBT or strap data can produce missing or wrong encoders, so the code includes fallback and guard logic.
- Cleanup ordering is subtle. DSB cleanup is deferred with old state, DC-off is dropped asynchronously, and blocking/nonblocking commit workqueues have different latency and synchronization concerns.

## Test Signals

Useful functional signals include successful `drm_atomic_commit()` paths for modeset, fastset, async flip, legacy cursor update, suspend/resume inherited state, MST, port sync, DSC, joiner/ultrajoiner, VRR/LRR, PSR/FBC, and DSB/FlipQ updates.

Runtime diagnostics are extensive. State mismatches are reported by `intel_pipe_config_compare()` and `intel_modeset_verify_crtc()`. Plane/transcoder assertions, FIFO underrun checks, unclaimed MMIO detection, `drm_WARN_ON()` guards, and `drm_dbg_kms()` messages expose sequencing and readout failures.

Mode validation signals include `intel_mode_valid()`, `intel_cpu_transcoder_mode_valid()`, and `intel_mode_valid_max_plane_size()` returning expected `MODE_*` statuses for clock, timing, vscan, sync flag, line-time, and plane-size limits across display generations and joined-pipe counts.

Hardware readout parity is a key regression signal: after commit, live register-derived state should compare with software state, including timings, pipe source, BPP, DPLL state, infoframes, DSC config, VRR/CMRR, joiner masks, scalers, color LUT/CSC state, M/N values, and output formats.

Targeted stress tests should cover DC-state/PSR interactions, vblank evasion, two-step watermark updates, DDB reallocation ordering, power-domain on/off transitions, nonblocking commit workqueue ordering, DP tunnel/MST dependency waits, encoder cloning conflict rejection, and framebuffer cleanup after pending unpins.
