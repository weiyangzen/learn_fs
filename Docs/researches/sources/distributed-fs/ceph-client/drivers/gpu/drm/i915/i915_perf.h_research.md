# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf.h

## Purpose

`i915_perf.h` is the public internal header for the i915 OA performance subsystem. It exposes lifecycle hooks, DRM ioctl handlers, OA config reference helpers, context-state initialization, metric config lookup, and OA timestamp frequency reporting to the rest of the i915 driver while keeping implementation details in `i915_perf.c` and state layout in `i915_perf_types.h`.

## Important APIs, types, and functions

The header declares `i915_perf_init()`, `i915_perf_fini()`, `i915_perf_register()`, `i915_perf_unregister()`, `i915_perf_ioctl_version()`, `i915_perf_sysctl_register()`, `i915_perf_sysctl_unregister()`, `i915_perf_open_ioctl()`, `i915_perf_add_config_ioctl()`, `i915_perf_remove_config_ioctl()`, `i915_oa_init_reg_state()`, `i915_perf_get_oa_config()`, `i915_oa_config_release()`, and `i915_perf_oa_timestamp_frequency()`. Inline helpers `i915_oa_config_get()` and `i915_oa_config_put()` wrap `kref_get_unless_zero()` and `kref_put()` for `struct i915_oa_config`.

## Control flow

There is no runtime control flow in the header beyond the inline kref helpers. Driver lifecycle code includes this header to call init/register during device bring-up and unregister/fini during teardown. The DRM ioctl table points directly at the declared ioctl handlers. Context creation and reset paths call `i915_oa_init_reg_state()` to synchronize logical-ring context images with any active OA stream.

## State and persistence behavior

The header owns no storage. It defines the access contract for `struct i915_perf` and `struct i915_oa_config` state. The kref helpers are important for persistence: dynamic metric configs can be removed from the IDR/sysfs while still referenced by open streams or query paths, and the actual memory is released only when the final reference reaches `i915_oa_config_release()`.

## Dependencies

It depends on Linux `kref`, fixed-width types, and `i915_perf_types.h`. It forward-declares DRM and i915 structures to avoid pulling heavy headers into all users. Consumers include `i915_driver.c`, `i915_getparam.c`, `i915_module.c`, `i915_query.c`, and `i915_debugfs.c`.

## Integration points

The declared ioctls are registered as render-node-allowed DRM ioctls. `i915_perf_ioctl_version()` feeds `I915_PARAM_PERF_REVISION`, and `i915_perf_oa_timestamp_frequency()` feeds timestamp-frequency getparam/query paths. The config lookup helpers are shared with query code so userspace can inspect dynamic metric register programming without opening a stream.

## Risks

The main risk is reference lifetime misuse: callers that obtain configs through `i915_perf_get_oa_config()` must eventually call `i915_oa_config_put()`. The inline `get` only succeeds if the kref is nonzero, so callers must handle `NULL`. Any prototype drift between this header and `i915_perf.c` would break ioctl or lifecycle registration.

## Test signals

Build coverage of driver lifecycle, query, and ioctl files validates the declarations. Dynamic OA config add/remove while streams or queries hold references exercises the kref helpers. Module load/unload and bind/unbind paths exercise the init/register/sysctl/fini declarations.
