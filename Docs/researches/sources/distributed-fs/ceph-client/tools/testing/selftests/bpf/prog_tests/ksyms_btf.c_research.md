
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ksyms_btf.c

## Purpose

`ksyms_btf.c` validates typed BTF ksyms, percpu DATASEC handling, null-check enforcement, weak ksyms in normal and light skeletons, and write protection for ksym references.

## Important APIs, Types, and Functions

The file uses `test_ksyms_btf.skel.h`, null-check, weak, lskel, and write-check skeletons; `libbpf_find_kernel_btf()`, `btf__find_by_name_kind()`, `kallsyms_find()`, skeleton attach, and BSS result fields.

## Control Flow and Data Flow

The top-level test confirms kernel BTF and PERCPU DATASEC support, then runs subtests. Basic resolves `runqueues` and `bpf_prog_active`, attaches the skeleton, and compares addresses/values. Null-check expects load failure when required checks are absent. Weak ksym tests verify existing/missing typed and typeless symbol outputs for both skeleton styles. Write checks disable one handler at a time and expect load rejection.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is kernel BTF handle, skeleton BSS outputs, and verifier load results. Dependencies include vmlinux BTF with percpu DATASEC, kallsyms, and typed ksym support. Integration is libbpf ksym relocation with BTF types and verifier protections. Risks are kernel BTF shape differences, symbol visibility, and CHECK-style legacy assertions. Test signals are address/value matches, expected null-check load failure, weak symbol outputs, and write-check load failures.
