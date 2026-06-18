
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/htab_reuse.c

## Purpose

`htab_reuse.c` stress-tests hash map element reuse under concurrent update/delete/lookup with `BPF_F_LOCK`, including a large-value consistency race.

## Important APIs, Types, and Functions

The file uses `htab_reuse.skel.h`, pthreads, `bpf_map_update_elem()`, `bpf_map_delete_elem()`, `bpf_map_lookup_elem_flags()` with `BPF_F_LOCK`, a pipe start barrier, and map values containing `bpf_spin_lock`.

## Control Flow and Data Flow

The basic subtest runs one writer repeatedly inserting/deleting two keys and four readers repeatedly locked-looking-up a key. The consistency subtest seeds a large locked value, starts locked updaters, delete+update threads, and locked lookup threads simultaneously, then scans all 256 data words from each lookup for torn writes.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is hash map contents, spin-lock-protected values, thread stop flags, and torn-write flag. Dependencies include BPF spin locks in map values, locked lookup/update support, pthread scheduling, and the paired map definitions. Integration is kernel htab element reuse and value-copy atomicity around `BPF_F_LOCK`. Risks are race sensitivity, long loop runtime, and missing failures due to scheduling. Test signals are no thread setup failures and `ctx.torn_write == false` after high-volume concurrent operations.
