# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc.h

## Purpose
Declares the public GSC lifecycle, interrupt, reset-workaround, and diagnostic APIs used by Xe GT/uC code.

## Important APIs
- `xe_gsc_init` and `xe_gsc_init_post_hwconfig` split software firmware discovery/proxy setup from hardware-dependent queue/BO setup.
- `xe_gsc_load_start`, `xe_gsc_wait_for_worker_completion`, and `xe_gsc_stop_prepare` control asynchronous load/proxy work around runtime and stop paths.
- `xe_gsc_hwe_irq_handler` is the GSCCS interrupt hook for GSC engine-reset completion.
- `xe_gsc_wa_14015076503` is a GT reset preparation/cleanup workaround.
- `xe_gsc_print_info` emits firmware and HECI status diagnostics.

## Control Flow and Integration
This header is consumed by GT reset/init code, uC debugfs, and GSC implementation. It intentionally hides `struct xe_gsc` internals behind forward declarations, with state defined in `xe_gsc_types.h`.

## Risks and Test Signals
- Callers must honor the split init ordering: firmware/proxy state before post-hwconfig resources and load start only after a GSCCS queue exists.
- Reset paths should call the workaround only while holding the right forcewake domains, as enforced in implementation-side assertions.
