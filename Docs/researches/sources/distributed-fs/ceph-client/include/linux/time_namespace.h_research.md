<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time_namespace.h -->
# sources/distributed-fs/ceph-client/include/linux/time_namespace.h

## Purpose
declares time namespace structures and helpers that virtualize monotonic and boottime offsets for containers.

## Important APIs, Types, and Functions
The file is 178 lines and exports these visible symbol families: types/enums `user_namespace`, `seq_file`, `vm_area_struct`, `timens_offsets`, `time_namespace`, `proc_timens_offset`, `page`; macros/constants none; function-like macros none; inline helpers `put_time_ns`, `timens_add_monotonic`, `timens_add_boottime`, `timens_add_boottime_ns`, `timens_sub_boottime`, `timens_ktime_to_host`, `time_ns_init`, `timens_on_fork`, `timens_commit`; external prototypes `container_of`, `time_ns_init`, `free_time_ns`, `timens_on_fork`, `proc_timens_show_offsets`, `proc_timens_set_offset`, `do_timens_ktime_to_host`, `ERR_PTR`, `timens_commit`.

## Control Flow
Namespace creation copies or shares a `time_namespace`, fork hooks attach it, procfs shows/sets offsets before commit, and helpers add/subtract namespace offsets for monotonic/boottime values or convert namespace ktime back to host time.

## State and Persistence Behavior
`time_namespace` stores refcounted namespace identity, user namespace, frozen offsets, VVAR page pointer, and per-clock offsets. A task commits a namespace when offsets become active. Disabled configs use init namespace stubs.

## Dependencies and Integration Points
It depends on nsproxy, user namespaces, procfs seq/file interfaces, VMA/VVAR support, ktime, and CONFIG_TIME_NS. Direct includes are `linux/sched.h`, `linux/nsproxy.h`, `linux/ns_common.h`, `linux/err.h`, `linux/time64.h`, `linux/cleanup.h`.

## Risks and Edge Cases
Offsets must be immutable after namespace activation, and conversions must only apply to supported clocks. VVAR page handling and user namespace ownership affect container isolation.

## Test Signals
Run time namespace selftests, unshare/setns/fork offset tests, proc offset write permission tests, VDSO/VVAR time reads, and CONFIG_TIME_NS=n builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time_namespace.h -->
