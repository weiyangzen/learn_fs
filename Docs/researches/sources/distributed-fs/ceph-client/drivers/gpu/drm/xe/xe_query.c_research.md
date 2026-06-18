<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_query.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_query.c

Purpose: implements `DRM_XE_DEVICE_QUERY` dispatch. It reports engines, memory regions, device config, GT list, GuC hardware config, topology masks, engine cycles, firmware versions, OA units, PXP status, and EU stall capabilities.

Important APIs and control flow: `xe_query_ioctl()` validates extensions/reserved fields, bounds-checks `query->query`, uses `array_index_nospec()`, and dispatches through `xe_query_funcs`. Most query handlers implement the two-call size-discovery ABI: if `query->size == 0`, set expected size and return; otherwise require exact size. `query_engine_cycles()` reads user input for clock ID and engine instance, obtains forcewake, reads upper/lower ring timestamp with CPU timestamp/delta, and writes only output fields back. `query_pxp_status()` directly forwards `xe_pxp_get_readiness_status()`.

State and dependencies: relies on device topology, GT/engine lists, TTM memory managers, VRAM accounting, GuC hwconfig, GT fuse topology, UC firmware structures, OA unit metadata, PXP state, and EU stall helpers. SR-IOV VF mode blocks engine-cycle queries with `-EOPNOTSUPP`.

Risks and test signals: exact-size uAPI checks can regress compatibility if struct sizes or ordering change. Tests should cover zero-size discovery, bad sizes, bad user pointers, invalid clock/engine class/GT IDs, SR-IOV VF denial, PXP disabled/error/not-ready/ready responses, and topology copy failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_query.c -->
