# sources/distributed-fs/ceph-client/tools/perf/util/cgroup.h

Purpose: declares the cgroup object model and APIs used by perf event lists, option parsing, and perf environment metadata.

Important APIs/types: defines `struct cgroup` with rb-node, id, name, fd, and refcount. Declares reference management, creation/find, expansion, default assignment, option parsing, id lookup, environment purge, full-system reading, and v2 detection.

Control flow: callers create/find cgroups, attach them to evsels/evlists, expand evlists over matched cgroups, and later release references or purge environment trees.

State and persistence: cgroup references persist through evsel attachment or perf env rb-trees. `read_cgroup_id` is a real API only with `HAVE_FILE_HANDLE`.

Dependencies and integration: includes Linux compiler/refcount/rbtree and `util/env.h`; bridges command-line cgroup selection with event opening and perf data metadata.

Risks: users must pair get/put and must not assume id lookup works on all builds. Global counters make repeated parsing sensitive to reset behavior.

Test signals: compile with and without `HAVE_FILE_HANDLE`; run cgroup attachment, expansion, lookup, purge, and v2 detection tests.
