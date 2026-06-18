# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/static_linked.c

Purpose: verifies statically linked BPF subprogram/object behavior using `test_static_linked` skeleton and read-only data initialization before load.

Control flow opens skeleton, writes `rodata->rovar1=1` and `rodata->rovar2=4`, loads, attaches, triggers with `usleep`, then checks computed mutable data values. State is skeleton rodata inputs and data outputs `var1` and `var2`. Dependencies are skeleton generation for the statically linked BPF object and the attached program firing during sleep. Risks are minimal, mainly timing and mismatches in linked helper calculations. Test signals are expected equations `var1 = 1 * 2 + 2 + 3` and `var2 = 4 * 3 + 5 + 6`.
