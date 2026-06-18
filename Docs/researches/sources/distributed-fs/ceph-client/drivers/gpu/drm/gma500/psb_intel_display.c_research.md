# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_display.c

## Purpose
This file provides Poulsbo-style CRTC mode setting, PLL helpers, mode readback, CRTC initialization, cursor setup, and connector-clone helpers for the shared GMA500 modeset stack.

## Important APIs, Types, and Functions
Exported objects/functions are `psb_intel_helper_funcs`, `psb_clock_funcs`, `psb_intel_crtc_mode_get()`, `psb_intel_crtc_init()`, `psb_intel_get_crtc_from_pipe()`, and `gma_connector_clones()`. Local helpers include `psb_intel_limit()`, `psb_intel_clock()`, `psb_intel_panel_fitter_pipe()`, `psb_intel_crtc_mode_set()`, `psb_intel_crtc_clock_get()`, and `psb_intel_cursor_init()`.

## Control Flow
CRTC mode set validates a framebuffer, discovers attached encoder type, selects a PLL limit, computes PLL divisors, programs LVDS pins before DPLL when needed, writes timing/source/plane registers, calls base programming, and waits for vblank. Mode readback pulls timing and PLL registers from live hardware or saved state when powered down. CRTC init allocates `gma_crtc` plus connector storage, initializes DRM CRTC and gamma, attaches chip helper functions, records pipe/plane mappings, and initializes cursor registers and optional stolen-memory cursor backing.

## State and Persistence Behavior
The file persists per-CRTC state in `gma_crtc`, `psb_intel_crtc_state`, `dev_priv->plane_to_crtc_mapping`, `pipe_to_crtc_mapping`, cursor GEM object/address, LUT adjustment, and saved modes. It writes live hardware timing/PLL/plane/cursor registers through `dev_priv->regmap`.

## Dependencies and Integration Points
It depends on DRM CRTC helpers, GEM framebuffer objects, generic GMA display helpers, Poulsbo register maps from `psb_device.c`, LVDS/SDVO encoder types, and clock helper callbacks. Chip ops point to `psb_intel_helper_funcs` and `psb_clock_funcs`.

## Risks
PLL selection returns without applying a mode if it cannot find settings but only logs. LVDS pipe restrictions are enforced in LVDS mode fixup, not here. Cursor allocation for platforms requiring physical cursor memory can fail, leaving cursor disabled. Mode readback mixes live and saved register paths depending on runtime power.

## Test Signals
Signals include successful CRTC creation for all configured pipes, correct PLL programming for LVDS/SDVO modes, mode readback matching active modes, cursor registers initialized to zero, framebuffer base updates via `gma_pipe_set_base()`, and clone masks matching connector types.
