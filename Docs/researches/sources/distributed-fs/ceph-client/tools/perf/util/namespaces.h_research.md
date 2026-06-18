
# sources/distributed-fs/ceph-client/tools/perf/util/namespaces.h

Purpose: declares namespace metadata and refcounted process namespace information for perf utilities.

Important APIs/types/functions: `struct namespaces` contains a list node, `end_time`, and flexible `perf_ns_link_info` array. `DECLARE_RC_STRUCT(nsinfo)` defines pid, tgid, nstgid, `need_setns`, `in_pidns`, mount namespace path, and refcount. `struct nscookie` stores old/new namespace fds and old cwd for restoration. Public functions allocate/free/copy/get/put namespace objects, inspect and mutate flags, enter/exit mount namespaces, perform namespace-aware `realpath`/`stat`, check root namespace status, and map namespace index to name. If libc lacks setns support, it declares a fallback `setns`.

Control flow: no local execution; it defines the lifecycle contract for `namespaces.c`.

State and persistence: structs represent transient snapshots of `/proc` namespace data and live namespace-switch cookies. Callers must balance `nsinfo__get`/`put` and `mountns_enter`/`exit`.

Dependencies: sys/types/stat, Linux perf event namespace link info, refcount, internal rc-check helpers, and list support.

Integration points: included by map/symbol/session code that needs namespace-aware filesystem resolution and by event code handling namespace records.

Risks: flexible array allocation must size by namespace count. `nsinfo__zput` macro assumes an lvalue variable. Namespace switching is process-wide, so callers must avoid concurrent path operations without coordination. Test signals include compile coverage without `HAVE_SETNS_SUPPORT`, refcount checks, and namespace path lookup tests.
