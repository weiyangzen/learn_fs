# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/htab_map_batch_ops.c

Purpose: validates lookup, delete, and lookup-and-delete batch operations for hash and per-CPU hash BPF maps.

Important APIs and functions: `map_batch_update()` fills normal or per-CPU values and calls `bpf_map_update_batch`; `map_batch_verify()` validates key/value pairs and coverage; `__test_map_lookup_and_delete_batch(is_pcpu)` runs empty-map, zero-count, full-count, stepped lookup/delete, and stepped lookup-and-delete scenarios. Public entries `htab_map_batch_ops`, `htab_percpu_map_batch_ops`, and `test_htab_map_batch_ops` run both variants.

Control flow: create a hash map, verify empty lookup-and-delete returns `ENOENT`, populate, test zero-count success, delete all entries, confirm map empty, then iterate step sizes. For each step, it tolerates `ENOSPC` for too-small buffers, otherwise verifies complete lookup, batch delete empties the map, and lookup-and-delete both returns all data and empties the map.

State and persistence: map fd and buffers are per test invocation. Per-CPU values use `BPF_DECLARE_PERCPU` layout, with stack array for `max_entries`.

Dependencies and integration points: uses libbpf batch APIs, `bpf_util.h` per-CPU helpers, possible CPU count, and `test_maps.h` `CHECK`.

Risks: `batch` cursor is not explicitly reset before every phase, relying on API behavior and assignment patterns; ENOSPC paths skip small step sizes, so total success check is important; fixed small map size limits scale coverage.

Test signals: pass messages for hash and per-CPU hash variants, plus `CHECK` failures on unexpected errno, count, value, or non-empty map state.
