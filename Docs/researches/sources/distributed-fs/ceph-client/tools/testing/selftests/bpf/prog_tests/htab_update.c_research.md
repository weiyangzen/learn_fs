
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/htab_update.c

## Purpose

`htab_update.c` verifies hash map update behavior for reentrant update prevention and concurrent user-space updates.

## Important APIs, Types, and Functions

The test uses `htab_update.skel.h`, selectively autoloads `bpf_obj_free_fields`, attaches fentry hooks, allocates values sized from `bpf_map__value_size()`, and uses `bpf_map_update_elem()` from the main thread and worker threads.

## Control Flow and Data Flow

The reentry subtest inserts an element, then replaces it. During old-value free, the BPF fentry program attempts a nested map update; the BPF-side `update_err` should record `-EDEADLK`. The concurrent subtest loads the skeleton and starts four threads, each updating key zero 1000 times, expecting no update errors.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the `htab` map, BPF-side `update_err`, and thread context. Dependencies include map value free hooks, fentry support, and htab locking. Integration is htab deadlock avoidance and update synchronization. Risks are race sensitivity and paired BPF program assumptions. Test signals are successful insert/replace with `update_err == -EDEADLK` and all concurrent updater threads returning NULL.
