# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_kms.c

## Purpose

`vc4_kms.c` contains global KMS logic that is not owned by a single plane, CRTC, or encoder. It initializes DRM mode config, vblank, and private atomic objects; implements the global atomic check and commit tail; manages HVS FIFO/channel assignment and muxing; tracks HVS/memory load and core clock requirements; supports VC4 CTM constraints; handles VC4 framebuffer modifier fallback; and coordinates mode-setting order across HVS, pixel valves, HDMI, and planes.

## Important APIs, Types, and Functions

- Private state types: `struct vc4_ctm_state` stores one active CTM matrix and FIFO, while `struct vc4_load_tracker_state` stores aggregate HVS and memory-bus load.
- CTM helpers: `vc4_get_ctm_state()`, private object create/duplicate/destroy functions, `vc4_ctm_s31_32_to_s0_9()`, `vc4_ctm_atomic_check()`, and `vc4_ctm_commit()`.
- HVS global state helpers: `vc4_hvs_get_new_global_state()`, `vc4_hvs_get_old_global_state()`, `vc4_hvs_get_global_state()`, plus HVS private-object create/duplicate/destroy/print/init functions.
- Muxing commit functions: `vc4_hvs_pv_muxing_commit()`, `vc5_hvs_pv_muxing_commit()`, and `vc6_hvs_pv_muxing_commit()`.
- Atomic orchestration: `vc4_atomic_commit_setup()`, `vc4_atomic_commit_tail()`, `vc4_pv_muxing_atomic_check()`, `vc4_load_tracker_atomic_check()`, `vc4_core_clock_atomic_check()`, and `vc4_atomic_check()`.
- Framebuffer and load: `vc4_fb_create()` preserves legacy VC4 tiling behavior when userspace omits modifiers; `vc4_load_tracker_obj_init()` sets up the aggregate load state.
- Entry point: `vc4_kms_load()` configures DRM limits, funcs, helper funcs, vblank, private objects, mode reset, and polling.

## Control Flow

`vc4_kms_load()` enables VC4 load tracking by default on GEN_4, initializes vblank, sets max dimensions by generation, selects mode config funcs (`vc4_fb_create` only for GEN_4), installs atomic helper hooks, initializes CTM/load/HVS private objects, resets mode config, and starts connector polling.

Atomic check first reserves/updates HVS channel assignment in `vc4_pv_muxing_atomic_check()`, validates CTM singleton/range restrictions, runs the DRM atomic helper check, updates load tracker totals from plane state deltas, enforces GEN_4 load limits if enabled, and computes HVS core-clock rate from per-FIFO load and aggregate pixel load.

Commit setup stores pending commit references per active HVS FIFO. Commit tail waits for pending commits on previously used FIFOs, temporarily raises VC5 core/disp clocks for modeset, disables old modesets, commits CTM on GEN_4/5, programs generation-specific HVS/pixelvalve muxing, commits planes, enables modesets, fakes vblank if needed, marks hardware done, waits for flips, cleans up planes, and finally drops VC5 clocks to the new computed steady-state requirement.

## State and Persistence

State is held in DRM private objects: CTM manager, load tracker, and HVS channel manager. `vc4_hvs_state` keeps per-channel `in_use`, `fifo_load`, pending commit references, and `core_clock_rate`. Load tracker state keeps aggregate HVS and memory-bus load. CTM state keeps a pointer to the active DRM CTM blob data and a 1-based FIFO selector. This state is copied and committed through DRM atomic transactions; it does not persist across driver reload.

## Dependencies and Integration Points

This file depends on DRM atomic core/helper APIs, vblank, GEM framebuffer helpers, sorting, clocks, VC4 CRTC/plane state, HVS registers, and local helpers in `vc4_drv.h`/`vc4_regs.h`. It integrates with `vc4_hvs.c` for actual dlist/channel programming, `vc4_crtc.c` and `vc4_txp.c` through assigned channels and encoder topology, HDMI through encoder modeset ordering and HVS clock capability, and VC4 tests through exported HVS global-state helpers.

## Risks and Edge Cases

- HVS FIFO assignment must consider existing enabled CRTCs not touched by the current atomic state; the check avoids pulling inactive CRTCs into the state because that could create page-flip waits on vblanks that never happen.
- FIFO changes require pixelvalve disable/enable, so channels are retained while a CRTC remains enabled.
- The current FIFO assignment heuristic relies on supported routing topologies sorted by HVS output; future routing layouts may need a real matching algorithm.
- CTM hardware supports one FIFO at a time and S0.9 coefficients only; user matrices outside `[-1.0, 1.0]` are rejected.
- Commit tail waits on old FIFO pending commits to prevent reusing a FIFO before previous updates finish; missed references would cause visible glitches.
- VC5 clock boost/drop during commit must match computed load or display underruns/performance waste can result.
- GEN_4 framebuffer creation preserves legacy tiling side-channel state; using generic GEM FB creation there would lose implicit T-tiled modifiers.

## Test Signals

The strongest test signals are KUnit PV muxing tests in `drivers/gpu/drm/vc4/tests`, atomic modeset/page-flip tests across HDMI0/HDMI1/TXP combinations, CTM rejection/commit tests, load tracker debugfs toggling on GEN_4, core-clock rate debug logs on GEN_5, vblank completion under single- and dual-display updates, and legacy framebuffer creation with and without explicit modifiers.
