# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fdinfo.c

## Purpose
`amdgpu_fdinfo.c` implements AMDGPU's `/proc/<pid>/fdinfo` reporting. It prints PASID, DRM memory accounting by placement, legacy amdgpu memory aliases, AMD-specific requested/evicted memory counters, and per-engine runtime usage.

## Important APIs, types, and functions
The main function is `amdgpu_show_fdinfo()`. It uses the `amdgpu_ip_name[]` table to translate hardware IP indices to fdinfo engine names and relies on `amdgpu_vm_get_memory()` plus `amdgpu_ctx_mgr_usage()` for accounting.

## Control flow
When DRM core invokes the driver's `show_fdinfo` hook, the function retrieves `struct amdgpu_fpriv`, obtains the VM and context manager, fills memory stats for all AMDGPU placements, fills per-IP usage times, prints the PASID, emits generic DRM memory stats for named placements, prints legacy `drm-memory-vram/gtt/cpu` aliases, prints AMD-specific requested and evicted memory keys, and prints each nonzero engine usage counter.

## State and persistence behavior
No state is persisted or mutated here. The output is a point-in-time view of per-file VM memory accounting and context runtime usage. Values are derived from in-memory VM BO and context-manager state.

## Dependencies and integration points
It depends on DRM fdinfo printer APIs, DRM usage-stats format, AMDGPU VM accounting, AMDGPU context manager usage accounting, placement indices, and hardware IP constants. The hook is installed by the `amdgpu_kms_driver` in `amdgpu_drv.c`.

## Risks and edge cases
The output format is userspace-facing and should stay compatible with `drm-usage-stats.rst`. IP names are shared for some decode/encode variants, so aggregation interpretation matters. Placement arrays must stay synchronized with AMDGPU placement enum values. Statistics may be approximate under concurrent memory or context changes.

## Test signals
Signals include fdinfo reads for graphics and compute clients, PASID presence, correct placement names, nonzero engine counters after workload submission, memory resident/shared/private/purgeable accounting, legacy alias values matching generic counters, and format compatibility with DRM usage parsers.
