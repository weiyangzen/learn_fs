# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/map_percpu_stats.c

Purpose: exercises BPF map element accounting as observed through both userspace key iteration and a BPF iterator program, with emphasis on per-CPU maps, LRU maps, non-preallocated maps, hash-of-maps, batch deletion, and maximum per-CPU value sizing.

Important APIs/types/functions: `map_info`, `map_count_elements`, `delete_and_lookup_batch`, `delete_all_elements`, `patch_map_thread`, `upsert_elements`, `get_cur_elements`, and `check_expected_number_elements` are the core helpers. The file uses generated `map_percpu_stats.skel.h` to attach an iterator program `dump_bpf_map` and read the current element count from an iterator FD. Map creators cover hash, percpu hash, preallocated variants, common and no-common LRU, percpu LRU, and hash-of-maps.

Control flow: each map scenario calls `__test`. It obtains map metadata, reduces the update count to avoid expected capacity failures, spawns eight worker threads that upsert overlapping key ranges, compares real key iteration count to BPF iterator count, deletes all elements via element-by-element paths, rechecks zero, then repeats update/count/delete using batch lookup-and-delete. Hash-of-maps creates small inner maps as temporary values. The final value-size test attempts to create large per-CPU values and treats either success or `E2BIG` as acceptable depending on kernel support.

State and persistence behavior: maps are transient. For hash-of-maps each update creates a temporary inner map FD, updates the outer map, then closes the local FD while the outer map keeps its reference. Per-CPU maps use a shared static 8 KiB blob as value storage for all update threads. Iterator state is opened, read once, and destroyed for each count.

Dependencies and integration points: relies on libbpf map APIs, BPF iterator skeleton generation, pthreads, `map_update_retriable` from `bpf_util.h`, and `test_maps.h`. Exported entry is `test_map_percpu_stats`.

Risks: thread updates race on identical keys by design; the expected count is element presence, not value stability. For LRU maps the real count may be below inserted count because eviction is allowed. Non-preallocated per-CPU maps can temporarily return `ENOMEM`, so retry logic is used only for that class. The static value buffers assume enough size for up to 1024 CPUs.

Test signals: core signal is equality between userspace `get_next_key` counting and BPF iterator counting after updates and after deletions. Additional signals are successful mixed delete/lookup-delete paths, successful batch lookup-and-delete of all counted keys, map creation across variants, and accepted handling of oversized per-CPU value creation.
