# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_tag.c

## Purpose
This file tests BTF declaration tags and type tags in BPF programs, including module, vmlinux, `__user`, and per-CPU pointer cases. It ensures skeletons load when compiler/kernel support exists and skips cleanly when tag attributes are missing.

## APIs, Types, and Functions
It uses skeletons `test_btf_decl_tag`, `btf_type_tag`, `btf_type_tag_user`, and `btf_type_tag_percpu`, plus BTF APIs `btf__load_vmlinux_btf`, `btf__load_module_btf`, `btf__find_by_name_kind`, and `btf__free`. `load_btfs` centralizes vmlinux/module BTF loading and feature skips. The file defines a host `struct btf_type_tag_test` referenced by generated skeleton metadata.

## Control Flow
Basic subtests open/load skeletons and inspect `rodata->skip_tests`. The module/user paths call `load_btfs`, optionally set BTF custom paths on skeleton open options, load BPF objects, and validate whether program loading succeeds based on whether the referenced tagged type should be resolvable. Per-CPU variants follow the same pattern for per-CPU tag use. `test_btf_tag` dispatches all subtests.

## State, Dependencies, and Integration
State is limited to skeleton objects and loaded BTF handles. The test depends on `bpf_testmod`, vmlinux BTF, module BTF, compiler support for BTF tag attributes, and kernel support for tagged pointer validation.

## Risks and Test Signals
Signals are skeleton load success/failure and explicit skips. Risks include kernel/module BTF lacking `user` type tags, test module absence, and compiler-generated BTF differences that change `skip_tests` behavior.
