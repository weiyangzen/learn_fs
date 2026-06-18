# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/sk_storage_map.c

Purpose: tests `BPF_MAP_TYPE_SK_STORAGE` creation, BTF requirements, locked updates/lookups, deletion semantics, invalid creation arguments, and two stress modes around socket lifetime and concurrent update/delete behavior.

Important APIs/types/functions: `load_btf` builds raw BTF for a value containing `bpf_spin_lock`; `create_sk_storage_map` creates the storage map with BTF type IDs and `BPF_F_NO_PREALLOC`. `test_sk_storage_map_basic` covers functional operations. `insert_close_thread` plus `do_sk_storage_map_stress_free` stress map destruction while many sockets with storage are closed. `update_thread`, `delete_thread`, and `do_sk_storage_map_stress_change` race updates and deletes on one socket. Environment-controlled entry is `test_sk_storage_map`.

Control flow: the basic test loads BTF, creates an IPv6 stream socket and storage map, performs `BPF_NOEXIST | BPF_F_LOCK`, `BPF_EXIST | BPF_F_LOCK`, `BPF_EXIST`, duplicate `BPF_NOEXIST` failure, plain update, lookup with `BPF_F_LOCK`, deletion, missing lookup/delete checks, then invalid map create variants. Stress-free creates worker threads that wait for a shared map FD, create many sockets, attach storage, signal completion, wait for the main thread to close the map, then close sockets and repeat until alarm/stop. Stress-change creates one socket and one map, then runs alternating updater/deleter threads until timeout or error.

State and persistence behavior: global variables track stop state, thread done/error counters, thread/socket counts, runtime, and the shared map FD. Signals set the stop flag. Socket storage is attached to socket FDs and should be released when sockets or maps are closed. BTF FDs are closed after map creation.

Dependencies and integration points: uses raw BTF encoding macros from `test_btf.h`, libbpf map/BTF APIs, pthreads, signals, sockets, resource limits, and `test_maps.h`. The exported `test_sk_storage_map` can select `basic`, `stress_free`, or `stress_change` by environment variables.

Risks: stress tests are timing-sensitive and depend on `RLIMIT_NOFILE`, system socket capacity, and scheduler behavior. `wait_for_map_close` spins without sleeping. Global stop/counter state is reused across subtests, so test order and environment overrides matter. Error acceptance for concurrent update includes `EAGAIN`; delete accepts `ENOENT`.

Test signals: functional checks expect exact locked lookup values, duplicate/missing errors, and `EINVAL` for bad BTF/key/max_entries/map_flags. Stress tests pass when all threads join without an unexpected error before the alarm-driven stop.
