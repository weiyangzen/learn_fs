
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers_aldebaran.h

## Purpose
Adds the Aldebaran/GFX9.4.x `MAP_PROCESS` packet variant with per-debug-VMID fields used when KFD needs debug trap state, watch points, and SPI debug controls in process mapping.

## Important APIs, types, and functions
- `struct pm4_mes_map_process_aldebaran` extends the AI map-process layout.
- Extra fields include `single_memops`, `tmz`, `spi_gdbg_per_vmid_cntl`, and `tcp_watch_cntl[4]`.

## Control flow
No executable control flow. `pm_map_process_aldebaran` in `kfd_packet_manager_v9.c` writes this struct and advertises its `sizeof` through `kfd_aldebaran_pm_funcs`.

## State and persistence behavior
No owned runtime state. The packet layout persists as a firmware ABI for process-debug mapping.

## Dependencies and integration points
Requires `PM4_MES_TYPE_3_HEADER` from an already included generation header. Integrates with `kfd_process_device` debug fields (`spi_dbg_override`, `spi_dbg_launch_mode`, `watch_points`) and process debug flags.

## Risks
This header has no standalone include guard for the common PM4 header, so include order matters. Any size or bitfield mismatch breaks Aldebaran process mapping. Watch-point array size is fixed at four and must match device debug capability assumptions.

## Test signals
Build with `kfd_pm4_headers_ai.h` included first; inspect Aldebaran map-process dwords with debug trap enabled, watch points configured, and single-mem-op flag set.
