# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_distill.c

## Purpose
This file validates libbpf BTF base distillation and split-BTF relocation behavior. It fabricates base and split BTF graphs, distills only referenced base types into a compact base BTF, and verifies that relocation back against a full base BTF succeeds or fails for the right ambiguity and missing-type cases.

## APIs, Types, and Functions
The test uses libbpf BTF construction APIs such as `btf__new_empty`, `btf__new_empty_split`, `btf__add_int`, `btf__add_struct`, `btf__add_field`, `btf__add_union`, `btf__add_enum`, `btf__add_enum64`, `btf__add_func_proto`, `btf__add_array`, `btf__distill_base`, and `btf__relocate`. `VALIDATE_RAW_BTF` from `btf_helpers.h` is the main structural oracle. The important local routines are `test_distilled_base`, the duplicate-name and error variants, `test_distilled_base_vmlinux`, and `test_distilled_endianness`.

## Control Flow
Each subtest builds one or more BTF objects, validates their raw type layout, calls `btf__distill_base`, validates the distilled split/base pair, and optionally calls `btf__relocate` against a candidate base. The primary path checks named composites are represented as empty references while anonymous composites, function prototypes, and arrays needed by split BTF are copied into split BTF. Error subtests intentionally create indistinguishable or missing base types and expect `-EINVAL`.

## State, Dependencies, and Integration
State is in-memory `struct btf` objects only; cleanup frees every BTF handle. The vmlinux test depends on loadable kernel BTF and the host's `int` type. Endianness coverage deliberately serializes and reparses raw BTF with the inverse endianness.

## Risks and Test Signals
The signal is exact raw BTF text and expected success/error returns. Regressions are likely if libbpf changes type-id remapping, anonymous type copy rules, duplicate-name disambiguation, or BTF endianness propagation. The file is environment-sensitive only for vmlinux BTF availability.
