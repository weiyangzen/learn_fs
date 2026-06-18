# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_query.c

## Purpose

`i915_query.c` implements `DRM_IOCTL_I915_QUERY`, a multiplexed read-only ioctl for userspace discovery of i915 topology, engines, OA metric configs, memory regions, hardware configuration blobs, geometry subslices, and GuC submission version. It follows the common query pattern where a zero length asks for the required size and a nonzero length copies structured data to userspace.

## Important APIs, types, and functions

The external entry point is `i915_query_ioctl()`. Query handlers are stored in `i915_query_funcs[]` and include `query_topology_info()`, `query_engine_info()`, `query_perf_config()`, `query_memregion_info()`, `query_hwconfig_blob()`, `query_geometry_subslices()`, and `query_guc_submission_version()`. Supporting helpers include `copy_query_item()`, `fill_topology_info()`, `query_perf_config_data()`, `query_perf_config_list()`, and register-copy helpers for OA configs.

## Control flow

`i915_query_ioctl()` validates top-level flags, iterates user-provided `drm_i915_query_item` entries, rejects query ID zero and out-of-range IDs, applies `array_index_nospec()`, calls the selected handler, and writes the handler return value back to `item.length` when it differs. Each handler validates item flags, handles length-zero size discovery, validates reserved fields in user-provided headers, and copies output with `copy_to_user()` or unsafe user access blocks where appropriate.

Topology queries fill slice, subslice, and EU masks from `sseu_dev_info`; geometry-subsslice queries are restricted to XeHP-style render engines. Engine queries enumerate UABI engines and report class, instance, logical instance, flags, and capabilities. Perf config queries either list config IDs or return register arrays for a config by ID or UUID. Memory-region queries enumerate non-private regions and only report live unallocated sizes to `perfmon_capable()` callers. HW config returns the GT hwconfig blob if available. GuC submission version returns zero branch plus GuC major/minor/patch when GuC submission is active.

## State and persistence behavior

The ioctl is read-only from the driver's perspective except for copying lengths back to userspace. It snapshots mutable driver state: engine lists, memory-region availability, GT SSEU info, GuC version, hwconfig blobs, and `perf->metrics_idr`. OA configs are protected by RCU/krefs through `i915_perf_get_oa_config()` or explicit RCU scanning for UUID lookup. The returned data is not persistent; userspace must tolerate changes between size query and data query.

## Dependencies

The file depends on DRM user-copy helpers, nospec indexing, `i915_drv.h`, `i915_perf.h`, `i915_query.h`, engine user lookup, SSEU copy helpers, memory-region helpers, GuC state, and uAPI structures from `i915_drm.h`.

## Integration points

`i915_driver.c` registers this handler as render-node allowed. Mesa, compute runtimes, and diagnostics use it to discover engine topology, memory regions, and metric configs. The perf-config paths integrate tightly with dynamic OA config management in `i915_perf.c`, while memory-region reporting integrates with region accounting and perf capability policy.

## Risks

The main risks are ABI validation, user-copy correctness, and stale snapshots. Query handlers must reject nonzero reserved fields and invalid flags to preserve forward compatibility. Size calculations must avoid overflow and match uAPI struct layout. Perf config listing grows dynamically, so the allocation loop must tolerate concurrent config changes. Returning unallocated memory to unprivileged callers would leak system activity, so the capability check is security-relevant.

## Test signals

IGT query tests should cover zero-length size discovery, undersized buffers, reserved-field rejection, invalid IDs, topology mask sizes, engine enumeration, memory-region visibility with and without `CAP_PERFMON`, perf config list/data by ID and UUID, concurrent config add/remove during queries, hwconfig absence, geometry subslice validation, and GuC submission disabled/enabled behavior.
