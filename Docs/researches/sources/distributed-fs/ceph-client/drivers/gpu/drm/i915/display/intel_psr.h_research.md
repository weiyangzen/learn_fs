<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr.h

## Purpose
`intel_psr.h` is the public header for i915 display PSR, PSR2 selective update, Panel Replay, ALPM-related PSR queries, and debugfs registration. It exposes the PSR lifecycle and atomic-commit hooks used by the rest of the display driver.

## Important APIs, Types, And Functions
The header forward-declares display objects used by the API and defines `CAN_PANEL_REPLAY(intel_dp)`, which requires both source and sink Panel Replay support. Exported functions cover capability checks (`intel_encoder_can_psr()`, `intel_psr_enabled()`, `intel_psr_link_ok()`), DPCD/init (`intel_psr_init_dpcd()`, `intel_psr_init()`), atomic config (`intel_psr_compute_config()`, `intel_psr_compute_config_late()`, `intel_psr_get_config()`), commit sequencing (`intel_psr_pre_plane_update()`, `intel_psr_post_plane_update()`, `intel_psr_disable()`), frontbuffer tracking (`intel_psr_invalidate()`, `intel_psr_flush()`), selective fetch programming, IRQ/short-pulse handling, pause/resume, and debugfs setup.

## Control Flow
Callers use this header to stitch PSR into connector probing, atomic checking, pipe update locking, frontbuffer invalidation, IRQ handling, and debugfs. The expected sequence is capability discovery, atomic mode computation, pre-plane disable if necessary, post-plane enable, frontbuffer-driven exit/re-entry during rendering, and explicit disable before pipe shutdown.

## State And Persistence Behavior
The header does not define storage except through referenced structs. It exposes functions that operate on persistent `intel_dp->psr` state owned by `struct intel_dp`. State mutation is serialized in the implementation by `psr.lock`.

## Dependencies And Integration Points
It depends only on Linux integer types and forward declarations, minimizing include fan-out. Integration points include `intel_dp.c`, `intel_crtc.c`, `intel_cursor.c`, `intel_frontbuffer.c`, `intel_display_irq.c`, `intel_display_debugfs.c`, ALPM, VRR, and DSB paths.

## Risks
Because this header is a broad cross-subsystem contract, signature changes have a large blast radius across atomic commit, IRQ, frontbuffer, and debugfs paths. The macro `CAN_PANEL_REPLAY()` assumes `intel_dp` is valid and that source/sink capability bits have already been initialized.

## Test Signals
Build coverage is the primary signal for declaration consistency. Runtime signals come from successful connector probe, atomic modesets, PSR debugfs registration, IRQ routing, and frontbuffer callbacks compiling and linking against these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr.h -->
