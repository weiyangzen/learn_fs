
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ksyms_module.c

## Purpose

`ksyms_module.c` verifies module ksym resolution through both light skeleton and normal libbpf skeleton paths.

## Important APIs, Types, and Functions

It uses `test_ksyms_module.lskel.h`, `test_ksyms_module.skel.h`, `bpf_prog_test_run_opts()`, and BSS field `out_bpf_testmod_ksym`.

## Control Flow and Data Flow

Two subtests load the lskel and normal skeleton, run the `load` program with empty test-run options, assert zero retval, and check that the module ksym value read by BPF equals 42.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BSS module-symbol output and loaded skeleton resources. Dependencies include `bpf_testmod` and module BTF/ksym exposure. Integration is module ksym relocation in both skeleton implementations. Risks are missing module or changed test symbol value. Test signals are zero test-run retval and `out_bpf_testmod_ksym == 42` in both subtests.
