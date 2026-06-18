# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_map_skip.c

Purpose: validates stack trace collection with skipped frames, expecting a reduced depth of two IPs and no internal failure flag. It uses `stacktrace_map_skip` skeleton.

Control flow loads skeleton, obtains stack maps, sets BSS `pid` to current process, attaches, sleeps for events, sets BSS `control=1` to stop collection, compares stack ID keys with stack map keys both directions, compares only `TEST_STACK_DEPTH` IPs against `stack_amap`, then checks BSS `failed == 0`. State is skeleton BSS and three map fds. Dependencies are stack comparison helpers, process-specific filtering, and generated BPF code implementing skip logic. Risks are event timing and false positives if stack depth or skip semantics change. Test signals are map fd assertions, attach success, two-way key comparison, IP comparison for depth two, and zero failure flag.
