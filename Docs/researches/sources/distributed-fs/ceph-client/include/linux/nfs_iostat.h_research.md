# sources/distributed-fs/ceph-client/include/linux/nfs_iostat.h

Purpose: Defines NFS per-mount IO statistics versioning and counter indexes exposed through client instrumentation.

Important APIs, types, and functions: Exports `NFS_IOSTAT_VERS`, byte counter enum values, and event counter enum values. Detected source surface: 122 lines; includes none; macros `NFS_IOSTAT_VERS`, `_LINUX_NFS_IOSTAT`; structs none; enums `nfs_stat_bytecounters`, `nfs_stat_eventcounters`; typedefs none; function-like declarations/helpers none.

Control flow: NFS read/write/metadata paths increment counters by enum index; proc/debug presentation code formats them according to the version.

State and persistence behavior: The header defines indexes only; per-mount counter storage is elsewhere. Counter names are persistent user-visible diagnostic ABI.

Dependencies and integration points: Consumed by NFS superblock/client stats and procfs reporting.

Risks and test signals: Risks are enum reordering breaking tooling and missing increments in new paths. Test read/write/direct/commit/readdir/workload stats and proc output compatibility.
