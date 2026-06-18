<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_irq_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_irq_kms.c

## Purpose

`radeon_irq_kms.c` implements KMS interrupt setup and interrupt-source reference management. It installs the shared PCI interrupt handler, configures MSI policy, initializes vblank support, schedules hotplug/DisplayPort/audio work outside hard IRQ context, exposes helpers for enabling/disabling software fence interrupts, page-flip/vblank interrupts, AFMT audio interrupts, and hotplug-detect pins, and provides a small register update helper for per-ASIC IRQ code.

## Important APIs, Types, and Functions

- `radeon_driver_irq_handler_kms()`: DRM IRQ handler wrapper that calls the per-ASIC `radeon_irq_process()` callback and updates runtime PM activity when an IRQ was handled.
- `radeon_hotplug_work_func()` and `radeon_dp_work_func()`: deferred connector walks that call `radeon_connector_hotplug()` under mode-config locking; hotplug work also sends a DRM HPD uevent.
- `radeon_driver_irq_preinstall_kms()`, `radeon_driver_irq_postinstall_kms()`, and `radeon_driver_irq_uninstall_kms()`: reset software IRQ state, program hardware IRQ masks, clear pending bits, and set vblank counter width.
- `radeon_irq_install()` / `radeon_irq_uninstall()`: request/free the shared PCI IRQ around the DRM/Radeon pre/post/uninstall callbacks.
- `radeon_msi_ok()`: hardware and quirk policy for enabling MSI.
- `radeon_irq_kms_init()` / `radeon_irq_kms_fini()`: top-level IRQ lifecycle, including spinlock init, vblank init, MSI enable/disable, work item setup, request_irq, and teardown flushing.
- `radeon_irq_kms_sw_irq_get*()` / `put()`: reference-count software interrupts per ring for fence signaling.
- `radeon_irq_kms_pflip_irq_get()` / `put()`: reference-count pageflip interrupts per CRTC.
- `radeon_irq_kms_enable_afmt()` / `disable_afmt()` and `enable_hpd()` / `disable_hpd()`: boolean interrupt source toggles under `rdev->irq.lock`.
- `radeon_irq_kms_set_irq_n_enabled()`: read-modify-write helper for numbered interrupt enable registers.

## Control Flow

Initialization sets up `rdev->irq.lock`, requests immediate vblank disable for power savings, initializes DRM vblank accounting for `rdev->num_crtc`, applies MSI policy, initializes deferred work, marks IRQs installed, and calls `request_irq()`. Preinstall clears all software state under the IRQ spinlock, calls the per-ASIC `radeon_irq_set()` to disable hardware interrupt sources, then processes pending bits once to clear stale status. Postinstall configures the DRM maximum vblank counter based on Avivo vs legacy width.

Runtime consumers call get/put helpers around features needing interrupt delivery. Atomic counters are used for ring software interrupts and page flips so the first user enables hardware and the last user disables it. Boolean HPD/AFMT/vblank states are updated under the same spinlock before reprogramming hardware through `radeon_irq_set()`.

The hard IRQ handler does little policy work itself: it delegates to ASIC-specific status decoding and only marks runtime PM activity on handled interrupts. HPD/DP work later walks connectors under `mode_config->mutex` to avoid doing modeset operations in IRQ context.

## State and Persistence Behavior

Persistent IRQ state lives in `rdev->irq`: `installed`, spinlock, per-ring `ring_int[]` atomics, per-CRTC `pflip[]` atomics and `crtc_vblank_int[]`, HPD booleans, AFMT booleans, and DPM thermal state. MSI state persists in `rdev->msi_enabled`. Deferred work items persist until device teardown. Hardware enable registers are reprogrammed from this state after each transition.

## Dependencies and Integration Points

This file integrates with PCI/MSI, runtime PM, DRM vblank core, DRM probe-helper hotplug events, Radeon ASIC IRQ callbacks (`radeon_irq_process`, `radeon_irq_set`), connector hotplug handling, DisplayPort link work, HDMI audio update work, fence signaling, page flipping, and per-family register programming helpers.

## Risks and Edge Cases

- MSI policy is quirk-heavy; enabling MSI on broken IGPs or disabling it on systems requiring MSI can cause missed interrupts or lockups.
- `radeon_irq_kms_disable_hpd()` uses `rdev->irq.hpd[i] &= !(mask bit)`, which works as boolean clearing but is easy to misread and fragile if the field ever becomes non-boolean.
- `radeon_irq_kms_sw_irq_get_delayed()` increments without programming hardware; callers must later call a path that applies `radeon_irq_set()`.
- `radeon_irq_kms_fini()` flushes delayed hotplug work but not the plain `dp_work` or `audio_work` here, so teardown ordering must ensure those cannot run after device state is invalid.
- All IRQ state changes depend on per-ASIC `radeon_irq_set()` honoring the software state consistently.

## Test Signals

Validation should include boot with legacy INTx and MSI, vblank enable/disable on each CRTC, pageflip completion interrupts, fence signaling on every ready ring, HPD storms and startup spurious HPD, DisplayPort hotplug work, HDMI AFMT interrupt toggles, suspend/resume IRQ reinstall, runtime PM last-busy updates, and quirk systems that require or reject MSI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_irq_kms.c -->
