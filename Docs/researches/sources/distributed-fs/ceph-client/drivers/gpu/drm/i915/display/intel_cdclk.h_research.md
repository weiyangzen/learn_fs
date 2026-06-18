# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cdclk.h

## Purpose

`intel_cdclk.h` is the public CDCLK/RAWCLK interface for i915 display code. It defines the hardware clock configuration structure and exposes lifecycle, atomic, commit, readout, debugfs, PM Demand, and timing helper APIs while leaving the private global-state layout in `intel_cdclk.c`.

## Important APIs, Types, And Functions

`struct intel_cdclk_config` contains `cdclk`, `vco`, `ref`, `bypass`, `voltage_level`, and `joined_mbus`. The `joined_mbus` field is valid for Xe2LPD and newer. The header forward-declares the global `struct intel_cdclk_state` and exposes conversion/access macros `to_intel_cdclk_state()`, `intel_atomic_get_old_cdclk_state()`, and `intel_atomic_get_new_cdclk_state()`.

Public APIs cover hardware lifecycle (`intel_cdclk_init_hw()`, `intel_cdclk_uninit_hw()`, `intel_init_cdclk_hooks()`), readout/capabilities (`intel_update_max_cdclk()`, `intel_update_cdclk()`, `intel_read_rawclk()`, `intel_cdclk_get_cdclk()`, `intel_cdclk_read_hw()`), atomic validation and state mutation (`intel_cdclk_atomic_check()`, `intel_atomic_get_cdclk_state()`, `intel_cdclk_state_set_joined_mbus()`, `intel_cdclk_update_dbuf_bw_min_cdclk()`, `intel_cdclk_force_min_cdclk()`), commit sequencing (`intel_set_cdclk_pre_plane_update()`, `intel_set_cdclk_post_plane_update()`, `intel_cdclk_is_decreasing_later()`), diagnostics (`intel_cdclk_dump_config()`, `intel_cdclk_debugfs_register()`), state accessors, PM Demand detection, and prefill/minimum helpers.

## Control Flow And Integration

Display initialization sets hooks and reads/programs hardware through these declarations. Atomic check code updates per-pipe and DBUF constraints, then calls `intel_cdclk_atomic_check()`. Commit code calls pre/post plane update functions to program increases before plane updates and decreases afterward. Watermark, DBUF, PM Demand, audio, and prefill code query current or computed CDCLK state through the accessors.

## State And Persistence

The header exposes only `struct intel_cdclk_config`; the persistent `struct intel_cdclk_state` remains opaque except for container macros that operate on global-state pointers. This preserves central control over logical vs actual CDCLK, active/enabled pipe masks, and transition flags.

## Dependencies, Risks, And Test Signals

The header includes `<linux/types.h>` and relies on atomic global object helper declarations from surrounding include context for its macros. Risks are mostly API-ordering risks: hooks must be initialized before calls through `display->funcs.cdclk`, global state must exist before atomic accessors are used, and joined MBUS must be sequenced with DBUF updates. Tests should compile all display platforms, run atomic modesets that change CDCLK, verify PM Demand update detection, and validate debugfs/readout consistency.
