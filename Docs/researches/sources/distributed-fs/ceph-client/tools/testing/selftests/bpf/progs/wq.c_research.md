<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/wq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/wq.c

## Purpose
This BPF workqueue test validates successful `struct bpf_wq` use from array, hash, no-prealloc hash, and LRU maps, with both sleepable and non-sleepable callbacks.

## Important APIs, Types, and Functions
It defines map value types `struct hmap_elem` and `struct elem`, maps `hmap`, `hmap_malloc`, `array`, and `lru`, and global bitmasks `ok` and `ok_sleepable`. It uses experimental helpers `bpf_wq_init`, `bpf_wq_set_callback`, `bpf_wq_start`, plus test kfuncs `bpf_kfunc_common_test` and `bpf_kfunc_call_test_sleepable`.

## Control Flow
`test_elem_callback()` and `test_hmap_elem_callback()` initialize or look up a map value, locate its embedded workqueue, initialize it with the owning map, set the callback, and start it. Callback `wq_callback` marks `ok`; callback `wq_cb_sleepable` validates the key against `ok_offset`, calls a sleepable kfunc, and marks `ok_sleepable`. Several tc/syscall entry points test each map flavor with a unique key. `test_map_no_btf` attempts lookup of a missing key and only initializes if present.

## State and Persistence
Persistent state lives in maps containing embedded workqueue objects and in BSS bitmasks recording callback completion. Hash/LRU map updates create elements before workqueue initialization.

## Dependencies and Integration Points
The file depends on `bpf_experimental.h`, `bpf_misc.h`, and `bpf_testmod_kfunc.h`. It integrates with workqueue selftests that load programs, invoke entry points, and check callback side effects.

## Risks
Workqueue behavior is asynchronous; tests must account for callback timing. Correctness depends on the workqueue pointer being an embedded field in the map value and the map pointer matching that value. Sleepable callback support depends on kfunc and context rules.

## Test Signals
Entry points return negative error codes for setup failures. The strongest signals are zero return from setup programs and bit transitions in `ok`/`ok_sleepable` after callbacks run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/wq.c -->
