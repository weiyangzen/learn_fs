# sources/distributed-fs/ceph-client/tools/perf/util/cgroup.c

Purpose: manages perf cgroup objects, command-line cgroup parsing, cgroup pattern expansion into event lists, cgroup id discovery, and environment cgroup lookup trees.

Important APIs/functions: `cgroup__new`, `cgroup__get`, `cgroup__put`, `evlist__findnew_cgroup`, `parse_cgroups`, `evlist__expand_cgroup`, `evlist__set_default_cgroup`, `cgroup__findnew`, `cgroup__find`, `perf_env__purge_cgroups`, `read_all_cgroups`, `read_cgroup_id`, and `cgroup_is_v2`.

Control flow: explicit parsing assigns comma-separated cgroups to existing evsels. Expansion splices original events out, gathers literal or regex-matched cgroups, clones each original evsel for every matched cgroup, repairs leader/metric/wildcard links through temporary `priv` pointers, copies metric events, and splices clones back.

State and persistence: globals `nr_cgroups`, `cgrp_event_expanded`, and temporary `cgroup_list`; `struct cgroup` persists name, fd, id, refcount, and rb-node while attached to evsels or perf env trees.

Dependencies and integration: uses cgroupfs mount discovery, `name_to_handle_at`, `statfs`, `nftw`, regex, evlist/evsel clone APIs, metricgroup copying, rbtrees/refcounts, and perf env locks.

Risks: cgroups can disappear between match and open. Regex traversal may be expensive. Global counters persist across parsing. Leader/metric repair depends on temporary pointer cleanup. File-handle id lookup can fail.

Test signals: comma parsing, empty entries, single-cgroup replication, regex expansion, no-match diagnostics, cgroup v1/v2, disappearing cgroups, metric cloning, leader preservation, and env purge.
