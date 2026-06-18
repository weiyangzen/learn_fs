# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_late_bind_fw.c

## Purpose
`xe_late_bind_fw.c` loads optional late-binding firmware blobs, currently fan-control firmware, and pushes them to a MEI/GSC late-bind component when available.

## Important APIs, Types, And Functions
- Public functions: `xe_late_bind_init()`, `xe_late_bind_fw_load()`, and `xe_late_bind_wait_for_worker_completion()`.
- Firmware parsing uses `parse_lb_layout()` for FPT layout and `parse_cpd_header()` for CPD/manifest version extraction.
- `__xe_late_bind_fw_init()` validates hardware need, builds the `xe/<name>_8086_<device>_<subvendor>_<subdevice>.bin` path, requests firmware, validates size/layout, stores payload, and initializes work.
- `xe_late_bind_work()` waits for component binding, retries `push_payload()` on `-EBUSY`, logs component status codes, and drops failed payloads to prevent repeated attempts.
- Component integration uses `component_add_typed()`, bind/unbind callbacks, and managed remove.

## Control Flow
Initialization exits when the platform lacks late-bind support or required MEI components are disabled. Otherwise it registers a typed component, installs managed cleanup, creates an ordered workqueue, initializes each firmware slot, and queues any available payloads. Work can be queued before component binding; it waits up to 20 seconds for component ops, then retries payload push for up to 6 seconds on busy. Runtime PM is held while queued work is pending.

## State And Persistence
`struct xe_late_bind` tracks component ops/device, firmware slots, ordered workqueue, component-added flag, and a `disable` flag used to suppress reloads during PM flows. Firmware payloads are DRM-managed allocations; failed upload frees and nulls the payload so it will not be retried. Successful payloads remain available for future reload unless freed by device teardown.

## Dependencies And Integration Points
The file depends on Linux component framework, firmware loader, MEI late-bind component interfaces, GSC firmware layout ABI types, Xe PCode fan-count query, Xe PM runtime, and PCI IDs. It is tied to fan-control hwmon/firmware support through PCode-reported fan count.

## Risks
`parse_lb_layout()` returns without releasing firmware on parse failure in `__xe_late_bind_fw_init()`, which is a leak risk unless ownership is otherwise handled. Component binding races are handled by polling, but long waits during workqueue execution can delay ordered work. Positive MEI status codes and negative errno values share the same logging path. Missing firmware is non-fatal, which is intentional but can hide deployment errors unless debug logs are enabled.

## Test Signals
Test missing firmware, oversized firmware, bad FPT/CPD layouts, missing manifest entries, no-fan platforms, late component bind/unbind, busy retry behavior, runtime PM reference balance, and PM reload disable paths.
