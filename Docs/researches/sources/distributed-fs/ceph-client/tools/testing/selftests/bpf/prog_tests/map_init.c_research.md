<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_init.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_init.c

Purpose: verifies that per-CPU hash and LRU per-CPU hash map values are zero-initialized correctly when slots are reused or evicted by BPF-side insertion.

Important APIs and functions: `map_populate()` fills all CPU slots with `FILL_VALUE`. `setup()` configures `hashmap1` as a chosen map type and size before skeleton load. `prog_run_insert_elem()` writes input key/value/PID into BSS, attaches the skeleton, triggers `getpgid`, and detaches. `check_values_one_cpu()` ensures only one CPU slot contains `TEST_VALUE`.

Control flow: `test_pcpu_map_init()` populates a one-entry percpu hash, deletes key 1, inserts key 1 from BPF, and checks one CPU value plus zeroed others. `test_pcpu_lru_map_init()` fills a two-entry LRU map, inserts key 3 from BPF to reuse/evict a slot, and checks initialization. Top-level skips on single-CPU systems.

State and persistence: state is temporary map contents and skeleton BSS inputs. The behavior under test is reused per-CPU value memory.

Dependencies and integration: depends on `test_map_init.skel.h`, multi-CPU availability, tracepoint/syscall trigger, and per-CPU map helpers.

Risks and test signals: one nonzero CPU and all other CPUs zero is the signal. Risks include CPU-count assumptions, current CPU scheduling, and BPF fixture attach trigger changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_init.c -->
