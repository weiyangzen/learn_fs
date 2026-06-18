<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr.c

## Purpose
`intel_psr.c` implements Intel display Panel Self Refresh support for i915 DisplayPort/eDP outputs, including classic PSR1, PSR2 selective update, DisplayPort Panel Replay, Panel Replay selective update, ALPM coordination, DC3CO handling, frontbuffer tracking, IRQ/error handling, and debugfs status/control. The code bridges DP sink DPCD capability discovery, atomic mode computation, hardware register programming, software frontbuffer invalidation/flush callbacks, and runtime workqueue reactivation.

## Important APIs, Types, And Functions
The exported API is declared in `intel_psr.h`. Key entry points are `intel_psr_init()`, `intel_psr_init_dpcd()`, `intel_psr_compute_config()`, `intel_psr_compute_config_late()`, `intel_psr_pre_plane_update()`, `intel_psr_post_plane_update()`, `intel_psr_disable()`, `intel_psr_invalidate()`, `intel_psr_flush()`, `intel_psr_irq_handler()`, `intel_psr_short_pulse()`, and the pipe-update helpers `intel_psr_lock()`, `intel_psr_wait_for_idle_locked()`, and `intel_psr_unlock()`.

Internally, mode selection is represented in CRTC state as `has_psr`, `has_sel_update`, and `has_panel_replay`. Runtime state lives in `intel_dp->psr` (`struct intel_psr` in `intel_display_types.h`) with flags such as `enabled`, `active`, `sel_update_enabled`, `panel_replay_enabled`, `psr2_sel_fetch_enabled`, `su_region_et_enabled`, `busy_frontbuffer_bits`, `sink_not_reliable`, `link_ok`, ALPM wake-line fields, and delayed work state. The file uses register definitions from `intel_psr_regs.h` and DPCD definitions from the DRM DP helpers.

Important internal clusters include DPCD probing (`_psr_init_dpcd()`, `_panel_replay_init_dpcd()`), sink enable programming (`_psr_enable_sink()`, `_panel_replay_enable_sink()`, `intel_psr_enable_sink()`), source activation (`hsw_activate_psr1()`, `hsw_activate_psr2()`, `dg2_activate_panel_replay()`), validation (`intel_psr2_config_valid()`, `intel_sel_update_config_valid()`, `_panel_replay_compute_config()`), selective fetch damage calculation (`intel_psr2_sel_fetch_update()`), and status/debug helpers (`intel_psr_status()`, `i915_psr_sink_status_show()`).

## Control Flow
Initialization starts in `intel_psr_init()`, which checks hardware support, limits older platforms to supported ports, sets source support for eDP PSR or DP/eDP Panel Replay, initializes `psr.lock`, `psr.work`, and `psr.dc3co_work`. DPCD probing through `intel_psr_init_dpcd()` reads PSR and Panel Replay capabilities, records sink support/granularity/DSC support on the connector, and sets `intel_dp->psr.sink_support` or `sink_panel_replay_support`.

During atomic check, `intel_psr_compute_config()` rejects global disables, unreliable sinks, interlaced modes, and joiner modes, then tries Panel Replay first and falls back to PSR. It separately computes selective update eligibility and late guardband checks in `intel_psr_compute_config_late()`. During commit, `intel_psr_pre_plane_update()` disables PSR/Panel Replay when a modeset or incompatible state transition requires it, while `intel_psr_post_plane_update()` enables source and sink if the new state remains valid.

Enable flow is `intel_psr_enable_locked()` -> `intel_psr_enable_sink()` -> `intel_psr_enable_source()` -> `intel_psr_activate()`. Activation selects one mutually exclusive path: PSR1, PSR2, or Panel Replay. Disable flow exits the active mode, waits for the status register to become idle, clears workarounds, disables sink state when appropriate, and resets runtime flags.

Frontbuffer tracking calls `intel_psr_invalidate()` when rendering starts and `intel_psr_flush()` when rendering finishes. Invalidation tracks dirty pipe frontbuffer bits and exits PSR or configures full-frame selective fetch updates. Flush clears busy bits, handles flip/DC3CO special cases, forces updates, and queues `intel_psr_work()` to reactivate once hardware is idle and no dirty frontbuffers remain.

## State And Persistence Behavior
PSR state is not persistent across driver initialization, but the sink/source capability bits, connector DPCD caches, and `intel_dp->psr` runtime fields persist for the lifetime of the connector/DP object. `psr.lock` serializes all runtime PSR transitions. Workqueue callbacks deliberately drop/reacquire the lock around idle waits and then revalidate that PSR is still enabled and unpaused. `sink_not_reliable` is sticky once set after AUX, DPCD, capability-change, ALPM, or sink error signals, preventing future enable until a larger reinitialization path clears/recreates state.

## Dependencies And Integration Points
The file integrates with DP AUX/DPCD (`drm_dp_dpcd_read*`, `drm_dp_dpcd_writeb()`), atomic state and plane damage helpers, frontbuffer tracking, DSB programming, ALPM (`intel_alpm_*`), DMC/DC power state code, VRR, DSC, HDCP, display workarounds, debugfs, display IRQ routing, and register MMIO helpers. `intel_dp.c` calls the compute/probe/init paths, `intel_frontbuffer.c` calls invalidate/flush, `intel_display_irq.c` routes PSR IRQs, `intel_crtc.c` uses the lock/idle helpers around pipe updates, and `intel_vrr.c` consumes PSR guardband requirements.

## Risks
The main risks are hardware sequencing and race bugs: PSR is sensitive to vblank timing, AUX wake timing, ALPM wake lines, workqueue reactivation, dirty frontbuffer accounting, and platform-specific workarounds. Selective fetch can under-update if damage rectangles, cursor coverage, DSC slice alignment, or early transport sizing are wrong. Error handling intentionally marks sinks unreliable, which is conservative for display correctness but can disable power-saving features until re-probe. Debugfs mode changes force fastsets and can perturb active pipelines. Many checks are platform/stepping-specific, so adding new display versions without auditing register bit layouts and workarounds is high risk.

## Test Signals
Useful signals include debugfs `i915_psr_status`, `i915_psr_sink_status`, `i915_edp_psr_status`, PSR event logs, DPCD sink error status, PSR/PSR2 status registers, performance counters, frontbuffer invalidation/flush behavior, suspend/resume and hotplug/short-pulse tests, pipe CRC interactions, DSC/VRR/HDCP combinations, selective fetch damage tests with cursor, plane movement, rotation/scaling rejection, and platform power-state residency checks for DC5/DC6/DC3CO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr.c -->
