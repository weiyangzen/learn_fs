# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/pm_helpers.h

This header defines the Venus PM operation table and small inline helpers used by decoder/encoder code. It abstracts generation-specific power and load-scaling behavior behind `struct venus_pm_ops`.

Important API elements are `POWER_ON`, `POWER_OFF`, `struct venus_pm_ops`, `venus_pm_get()`, `venus_pm_load_scale()`, `venus_pm_acquire_core()`, and `venus_pm_release_core()`. The ops table separates core power from vdec/venc subdevice power, optional per-core power routing, and per-instance load scaling.

Control flow is callback-based. Core probe selects ops by HFI version; decoder and encoder runtime PM call vdec/venc callbacks; stream start/stop use the inline acquire/release helpers; buffer processing and configuration call load scaling when dimensions, payloads, or session state change.

The header owns no state. It reads `inst->core`, `core->pm_ops`, and optional callback pointers. Dependencies are forward declarations for `struct device`, `struct venus_core`, and `struct venus_inst` from included compile context.

Risks are silent no-op behavior if callbacks are absent. That is intentional for unsupported generations but can hide missing PM setup. Test signals include non-null selected ops for each supported HFI version, successful stream start with `coreid_power`, load scaling returning zero where unsupported, and balanced release on close/error paths.
