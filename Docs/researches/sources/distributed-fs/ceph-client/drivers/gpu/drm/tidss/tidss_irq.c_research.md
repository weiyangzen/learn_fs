# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_irq.c

## Purpose

`tidss_irq.c` manages the TIDSS interrupt mask and top-level IRQ handler. It enables/disables vblank IRQs, installs/uninstalls the platform IRQ, restores masks after resume, and dispatches packed DISPC status bits to CRTC and plane error handlers.

## Important APIs, Types, and Functions

- `tidss_irq_update()` writes `tidss->irq_mask` to DISPC and asserts that `irq_lock` is held.
- `tidss_irq_enable_vblank()` and `tidss_irq_disable_vblank()` update the even/odd VSYNC bits for a CRTC's hardware videoport.
- `tidss_irq_handler()` reads and clears DISPC status under `irq_lock`, then routes VP VSYNC, frame-done, sync-lost, and plane underflow statuses.
- `tidss_irq_resume()` rewrites the saved mask after DISPC runtime resume.
- `tidss_irq_install()` requests the IRQ, initializes `irq_mask` with always-on sync-lost, frame-done, and plane underflow bits, but leaves actual enable programming to later update/resume paths.
- `tidss_irq_uninstall()` frees the IRQ.

## Control Flow

After KMS objects are created, `tidss_probe()` calls `tidss_irq_install()`. During normal operation DRM vblank core calls enable/disable vblank callbacks in CRTC code, which delegate here. Hardware IRQs enter `tidss_irq_handler()`, which performs the MMIO read/clear atomically with respect to mask updates, then iterates currently registered CRTCs and planes to deliver events. Runtime resume calls `tidss_irq_resume()` after DISPC initial config.

## State and Persistence Behavior

The persistent state is `tidss->irq_mask`, protected by `tidss->irq_lock`. CRTC/plane arrays are read locklessly after initialization. DISPC IRQ enable registers are hardware state that is lost across runtime suspend and restored from `irq_mask`.

## Dependencies and Integration Points

The file depends on Linux request/free IRQ and DRM device/private conversion. It integrates with `tidss_dispc.c` for hardware status/mask access, `tidss_crtc.c` for vblank/framedone/sync-lost callbacks, and `tidss_plane.c` for FIFO underflow reporting.

## Risks and Edge Cases

- `tidss_irq_install()` computes the initial mask but does not call `tidss_irq_update()` immediately; initial enable depends on resume or later vblank operations.
- The handler always returns `IRQ_HANDLED` even if no known bits were set.
- CRTC and plane arrays must be fully initialized before installation; otherwise the initial mask and dispatch loops are wrong.
- Plane underflow errors are routed by hardware plane ID, so feature-table plane ordering must match IRQ packing.

## Test Signals

Signals include vblank enable/disable toggling only the target VP bits, IRQ dispatch producing page-flip/vblank completion, sync-lost and FIFO-underflow ratelimited logs, runtime resume restoring masks, and no lockdep warnings for concurrent vblank toggles and interrupt handling.
