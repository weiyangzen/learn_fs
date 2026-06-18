# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/subprogs_extable.c

Purpose: verifies exception table handling for BPF subprograms through the `test_subprogs_extable` skeleton.

Control flow opens/loads and attaches the skeleton, triggers bpf_testmod read with size `456`, asserts BSS `triggered` is nonzero, detaches, and destroys. State is limited to skeleton link state and BSS `triggered`. Dependencies are bpf_testmod read trigger and generated BPF code using subprogram exception table behavior. Risks are missing test module or trigger path not firing. Test signals are skeleton open/load/attach success, trigger success, and `triggered != 0`.
