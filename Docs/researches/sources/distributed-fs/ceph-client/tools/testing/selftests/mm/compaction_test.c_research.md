# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/compaction_test.c

Purpose: tests whether compaction can produce enough huge pages after fragmenting/locking memory, targeting unevictable page compaction behavior.

Important APIs/types/functions: reads `/proc/meminfo` through `popen`, checks `/proc/sys/vm/compact_unevictable_allowed`, writes `/proc/sys/vm/nr_hugepages`, uses `mmap(MAP_LOCKED)`, `setrlimit(RLIMIT_MEMLOCK)`, and kselftest result APIs.

Control flow: requires root and compaction allowed. It resets huge pages to zero while remembering the original value, raises memlock limit, reads free memory/huge page size, maps and locks chunks covering about 80% of free memory while writing unique page content to avoid KSM merging, unmaps them, requests huge pages for about half of adjusted free memory, checks at least roughly one third of memory can be allocated as huge pages, restores original huge page count, and reports one test result.

State and persistence: mutates huge page pool and consumes/locks large memory temporarily.

Dependencies and integration points: root, `/proc/sys/vm/*`, huge page support, sufficient memory.

Risks: memory pressure is intentional and can affect host stability. Linked-list cleanup advances `entry` twice in the loop, which appears to skip nodes and leak some list allocations, though mappings are mostly short-lived process state.

Test signals: skip on unmet prerequisites; pass if compaction index is acceptable; fail on sysctl/meminfo/allocation errors.
