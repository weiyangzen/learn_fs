# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dp.c

## Purpose
`dp.c` provides reusable DisplayPort/eDP link-management logic for the Tegra DRM driver. It probes sink capabilities over AUX, stores link capability/configuration state, chooses a lane/rate combination for a mode, configures DPCD link registers, and performs fast or full link training with voltage swing, pre-emphasis, post-cursor, channel equalization, and fallback rate downgrade.

## Important APIs, Types, and Functions
The public API includes `drm_dp_link_caps_copy()`, `drm_dp_link_add_rate()`, `drm_dp_link_remove_rate()`, `drm_dp_link_update_rates()`, `drm_dp_link_probe()`, `drm_dp_link_configure()`, `drm_dp_link_choose()`, `drm_dp_link_train_init()`, and `drm_dp_link_train()`. These operate on the `struct drm_dp_link`, `struct drm_dp_link_caps`, and `struct drm_dp_link_train` types declared in `dp.h`.

Training is split into helpers: `drm_dp_link_apply_training()` calls the hardware-specific `link->ops->apply_training()` hook, writes DPCD training lane settings, optional post-cursor settings, and the training pattern. `drm_dp_link_clock_recovery()` loops pattern 1 recovery. `drm_dp_link_channel_equalization()` loops pattern 2 or 3 equalization. `drm_dp_link_train_full()` configures and retries with downgraded rates. `drm_dp_link_train_fast()` uses fixed pattern delays before checking final link status.

## Control Flow
`drm_dp_link_probe()` resets the link object, reads receiver capability DPCD bytes, fills revision/max rate/max lanes/capability flags, handles alternate scrambler reset and eDP revision lookup, computes clock-recovery and channel-equalization AUX read intervals, initializes current rate/lanes to max, and parses eDP 1.4 supported link rates if available.

`drm_dp_link_choose()` computes mode bandwidth from pixel clock and bits per color, then searches lanes `{1,2,4}` and link rates `{162000,270000,540000}` for the lowest combination with enough 8b/10b-adjusted capacity within sink limits. `drm_dp_link_configure()` optionally calls the driver-specific configure hook, writes link bandwidth/lane count/enhanced framing, writes channel coding, and enables alternate scrambler reset when supported.

`drm_dp_link_train()` reinitializes training state, attempts fast training only if the sink supports it and valid previous settings are already available, then falls back to full training. In this implementation fast training is effectively unreachable after reinitialization because `drm_dp_link_train_valid()` sees the freshly reset state as not recovered/equalized. Full training configures the link, runs clock recovery up to four iterations, downgrades from HBR2 to HBR to RBR on failure, runs channel equalization similarly, and always disables training before returning.

## State and Persistence
`struct drm_dp_link` persists sink capabilities, current selected rate and lanes, parsed additional eDP rates, read intervals, driver hooks, AUX pointer, and training state. Training request and adjustment arrays persist per train invocation. No state is written to disk; hardware/sink state is persisted by DPCD writes and source-specific hooks.

## Dependencies and Integration Points
The file depends on DRM DP helper DPCD accessors, DRM display modes, and `link->ops` supplied by the hardware-specific output driver. It does not touch Tegra registers directly. It expects a working `struct drm_dp_aux`, usually backed by `dpaux.c`, and is typically used by SOR/eDP output code that supplies source-side training register programming.

## Risks
Training retry behavior only downgrades the rate, not the lane count, so some marginal sinks may fail even if fewer lanes at a lower rate would work. `drm_dp_link_choose()` ignores eDP 1.4 custom supported-rate arrays when choosing from the fixed three-rate table. The fast-training path resets state before validity testing, so it will not use previously learned settings as written. AUX errors propagate directly and can abort modeset. DPCD parsing and interval defaults are sensitive to DP revision rules.

## Test Signals
Signals include successful DPCD capability reads, correct lane/rate selection for representative modes and bpc values, DPCD writes to `DP_LINK_BW_SET`, lane count, channel coding, and eDP configuration, training success across RBR/HBR/HBR2 sinks, downgrade logs when high rates fail, no lingering training pattern after failure, and hotplug/modeset tests on panels requiring TPS2/TPS3 and alternate scrambler reset.
