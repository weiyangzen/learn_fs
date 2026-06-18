# sources/distributed-fs/ceph-client/kernel/time/namespace.c

Purpose: implements time namespace creation, installation, fork commit, lifetime management, `/proc` namespace operations, and monotonic/boottime offset read/write support.

Important APIs and flow: `do_timens_ktime_to_host()` subtracts namespace offsets from absolute monotonic/boottime deadlines while clamping already-expired or overflowed values. `copy_time_ns()` either references the old namespace or clones a new `time_namespace`, charging user counts and allocating VDSO state. `timens_install()` requires a single-threaded caller plus `CAP_SYS_ADMIN` in both relevant user namespaces. `timens_on_fork()` switches a child from `time_ns_for_children` to active `time_ns` and commits VDSO layout. Proc offset setting validates clock ids, `CAP_SYS_TIME`, range against current host time, and refuses changes after offsets are frozen.

State and persistence: each namespace stores offsets, owner user namespace, ucounts, frozen flag, ns_common refcounting, and optional VVAR page. `timens_offset_lock` serializes offset writers and VDSO freezing. `init_time_ns` is frozen and registered at boot.

Dependencies and integration: user namespaces, nsproxy, proc ns operations, namespace tree, credentials/capabilities, timekeeping accessors, VDSO helpers, RCU freeing, and proc task files.

Risks and test signals: key risks are offset range validation, post-freeze mutation denial, namespace install permission rules, user-count exhaustion, and fork-time VDSO commitment. Test unshare/setns paths, `/proc/$pid/timens_offsets` writes, nested user namespaces, absolute sleeps under offsets, and remote task exit races.
