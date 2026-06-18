<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras.c

## Purpose
`xe_drm_ras.c` registers Xe error counters with the DRM RAS core. It creates per-device nodes for correctable and uncorrectable error severities and exposes counters by hardware error component.

## Important APIs, types, and functions
`hw_query_error_counter()` validates a counter table entry and returns its name and atomic count. Severity-specific query callbacks select `xe->ras.info[DRM_XE_RAS_ERR_SEV_*]`. `allocate_and_copy_counters()` allocates component counters from `DRM_XE_RAS_ERROR_COMPONENT_NAMES`. `assign_node_params()` formats the PCI device name, fills `drm_ras_node`, allocates severity counters, and selects query callback. `register_nodes()` registers each severity. `xe_drm_ras_init()` allocates node storage with drmm, registers nodes, and installs cleanup action.

## Control flow and integration points
Initialization loops over `for_each_error_severity()`, assigns node metadata, registers with `drm_ras_node_register()`, then registers `xe_drm_ras_unregister_nodes()` as a managed cleanup action. Query flow comes from DRM RAS into the severity callback and then into the severity/component counter table.

## State and persistence behavior
`xe->ras.node` is drmm-managed. Per-severity `ras->info[]` arrays and node device-name strings are manually allocated and freed on cleanup. Counters are atomic and currently initialized to zero; hardware error reporters can increment them through the stored arrays.

## Dependencies, risks, and test signals
Dependencies are DRM RAS, UAPI component/severity name arrays, PCI identity, and managed DRM cleanup. Risks include leaks if `assign_node_params()` fails after `device_name` allocation, incomplete cleanup on partial register failure, name-array/index mismatch, and unconnected hardware increment paths. Test signals are RAS node creation/removal, sysfs/debugfs RAS counter reads, injected correctable/uncorrectable increments, probe-failure cleanup, and PCI BDF formatting checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras.c -->
