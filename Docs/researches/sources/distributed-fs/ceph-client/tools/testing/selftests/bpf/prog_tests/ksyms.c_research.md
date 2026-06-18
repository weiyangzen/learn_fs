
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ksyms.c

## Purpose

`ksyms.c` validates BPF kernel symbol resolution for normal symbols, weak/missing symbols, percpu symbols, and vmlinux BTF size exposure.

## Important APIs, Types, and Functions

The test uses `test_ksyms.skel.h`, `kallsyms_find()`, `stat()` on the vmlinux BTF path, skeleton attach, and BSS data fields such as `out__bpf_link_fops`, `out__btf_size`, and `out__per_cpu_start`.

## Control Flow and Data Flow

The harness finds `bpf_link_fops` and `__per_cpu_start` in kallsyms, reads BTF file size, loads/attaches the skeleton, triggers it, and compares BPF-resolved outputs with user-space discovered values. Weak missing symbol output is expected to be zero.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BSS output values and kallsyms/BTF file metadata. Dependencies include kallsyms access, vmlinux BTF file, and ksym extern support. Integration is BPF ksym relocation. Risks are symbol visibility restrictions and missing BTF. Test signals are exact address matches for visible symbols, zero for missing weak symbol, and BTF size equality.
