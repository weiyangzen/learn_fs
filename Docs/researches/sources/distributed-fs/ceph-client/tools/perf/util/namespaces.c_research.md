
# sources/distributed-fs/ceph-client/tools/perf/util/namespaces.c

Purpose: handles perf namespace metadata and process namespace information, especially mount-namespace switching for resolving paths as seen by profiled processes.

Important APIs/types/functions: `perf_ns__name` maps namespace indexes to names. `namespaces__new`/`namespaces__free` allocate a variable-length `struct namespaces` from `PERF_RECORD_NAMESPACES`. `nsinfo__new`, `nsinfo__copy`, `nsinfo__get`, and `nsinfo__put` manage refcounted `struct nsinfo`. Accessors expose pid, tgid, nstgid, need-setns, and pid-namespace status. `nsinfo__mountns_enter` opens current and target mount namespaces, calls `setns`, and records old cwd; `nsinfo__mountns_exit` restores namespace and cwd. `nsinfo__realpath`, `nsinfo__stat`, and `nsinfo__is_in_root_namespace` provide namespace-aware helpers.

Control flow: `nsinfo__new(pid)` initializes default pid/tgid/nstgid, then `nsinfo__init` compares `/proc/self/ns/mnt` with `/proc/<pid>/ns/mnt`; differing inodes cause `need_setns` and store the target namespace path. It also parses `/proc/<pid>/status` for `Tgid:` and `NStgid:` to identify innermost tgid and pid namespace membership. Path operations wrap `realpath` or `stat` between mount namespace enter/exit calls when required.

State and persistence: `nsinfo` stores pid-derived namespace state, a heap `mntns_path`, and a refcount. `namespaces` stores copied namespace link info and an `end_time`. State is process memory only and may become stale if the target process exits or changes namespaces.

Dependencies: `/proc`, `stat`, `open`, `setns`, `getcwd`, `chdir`, Linux refcount/rc-check helpers, perf event namespace record structures, and zalloc utilities.

Integration points: symbol, DSO, map, build-id, and path resolution code use `nsinfo` to inspect files in the target process's mount namespace. Event processing uses `namespaces` records to track namespace lifetime.

Risks: target processes can exit while `/proc` is being read; the code tolerates init failure by clearing `need_setns`. `setns` and cwd restoration failures can affect subsequent path lookups. `nsinfo__get_nspid` depends on `/proc/<pid>/status` formatting and tab positions. Test signals include namespace unit tests, perf record/report against containers, mount namespace path resolution, root namespace detection, and leak/refcount checks.
