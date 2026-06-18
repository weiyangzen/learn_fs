<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/locks.c -->
## sources/distributed-fs/ceph/src/mds/locks.c

`locks.c` defines the static lock state-machine tables used by CephFS MDS cache locks. It is C rather than C++ and duplicates capability bit constants from `ceph_fs.h` so it can initialize plain C structures declared in `locks.h`.

The exported tables are `sm_simplelock`, `sm_scatterlock`, `sm_filelock`, and `sm_locallock`. Each points at a `sm_state_t[LOCK_MAX]` array describing, per lock state, the stable target state, loner mode, replica-visible state, read/projected-read/read-lock/write-lock/force-write/lease/xlock permissions, and cap masks for normal/loner/xlocker/replica cases. The `sm_t` wrapper also declares capabilities that may ever be issued to auth or replica holders, which cap bits require careful handling, and whether remote xlock is allowed.

Control flow is table-driven outside this file: locker code indexes these arrays by `LOCK_*` enum values and interprets permission fields such as `ANY`, `AUTH`, `XCL`, and `REQ`. `simplelock` covers generic metadata locks, `scatterlock` adds sync/lock/mix/temp-sync behavior for distributed counters, `filelock` adds file cap states including cache/read/write/buffer/lazyio and xsync/excl/mix transitions, and `locallock` is a minimal auth-local lock state.

Persistence is indirect: these tables are not persisted themselves, but their state numbers and capability masks govern journaled/cache lock transitions and client cap issuance. Changing table entries can alter replay behavior for locks restored from encoded inode/dir state.

Risks: enum/table index drift, incorrect cap mask combinations causing client over-issuance or unnecessary recalls, C/C++ constant duplication, and subtle transition regressions. Test signals are locker state-machine unit tests, client cap recall/issue integration tests, scatterlock flush tests, failover replay with dirty locks, and mixed auth/replica lock transition coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/locks.c -->
