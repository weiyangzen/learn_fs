<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_vars.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_vars.c

Purpose: validates libbpf linker behavior for BSS, data, rodata, and weak variable resolution across linked BPF object files.

Important APIs and functions: `test_linked_vars()` opens the `linked_vars` skeleton before load so it can seed BSS inputs, then loads, attaches, triggers `SYS_getpgid`, and checks BSS outputs.

Control flow: open, set `input_bss1`, `input_bss2`, and `input_bss_weak`, load, attach, trigger syscall, compare output accumulations, destroy.

State and persistence: state is skeleton data/BSS/rodata. The test depends on weak data and rodata winners from the first object file (`10` for data, `100` for rodata). It has no persistent resources after destroy.

Dependencies and integration: depends on `linked_vars.skel.h`, syscall-based trigger programs, and libbpf skeleton variable accessors.

Risks and test signals: output sums prove that global variable references in different sections resolved to the intended linked definitions. Fragility is mostly from changing the linked BPF fixture values or weak symbol selection rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_vars.c -->
