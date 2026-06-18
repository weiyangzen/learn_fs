# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tracing_struct.c

## Purpose
Validates BPF tracing argument decoding for structs, many arguments, unions, return values, and register extraction from test-module functions.

## APIs, Types, and Functions
Public entry point `test_tracing_struct()` runs subtests `test_struct_args()`, `test_struct_many_args()`, and `test_union_args()`. It uses `tracing_struct` and `tracing_struct_many_args` skeletons plus `trigger_module_test_read()`.

## Control Flow, State, and Persistence
Each subtest opens/loads/attaches a skeleton, triggers the BPF test module read path, and validates BSS fields populated by BPF programs. The assertions cover nested struct fields, register-slot values, return values, wide argument lists, and union member interpretation. State is transient in BSS counters/fields.

## Dependencies and Integration
Depends on the BPF test module, fentry/fexit or tracing BTF support, generated skeletons, and `test_progs` module trigger helper.

## Risks and Test Signals
Risks include ABI-specific argument passing, compiler/kernel BTF layout changes, and missing test module. Signals are exact BSS field equality for all struct/union arguments and return values after `trigger_module_test_read()`.
