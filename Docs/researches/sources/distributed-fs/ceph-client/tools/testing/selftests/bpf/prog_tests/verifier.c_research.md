# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verifier.c

## Purpose

Central dispatcher for a large set of verifier selftests generated as libbpf skeletons. It runs each verifier object through `test_loader`, generally without effective `CAP_SYS_ADMIN`, and provides pre-execution map initialization for array/value pointer arithmetic cases. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_loader__run_subtests()`, `test_loader__set_pre_execution_cb()`, `cap_disable_effective()`, `cap_enable_effective()`, `bpf_object__find_map_by_name()`, `bpf_map_update_elem()`, and the `RUN()` macro binding skeleton ELF-byte factories to exported `test_verifier_*()` functions.

## Control Flow

`run_tests_aux()` drops `CAP_SYS_ADMIN`, installs an optional callback, runs subtests for the named skeleton, finalizes the loader, then restores capabilities. Most `test_verifier_*` entry points are thin wrappers. `test_verifier_array_access()` and `test_verifier_value_ptr_arith()` prepopulate array maps with `struct test_val` before verifier execution.

## State and Persistence Behavior

Persistent state is limited to temporary effective capability changes and map contents inserted before individual verifier object loads. There is no storage outside process/kernel BPF objects created by the test loader.

## Dependencies and Integration Points

It depends on many generated verifier skeleton headers, `cap_helpers.h`, `test_loader`, libbpf object/map APIs, and kernel verifier behavior across helper, pointer, scalar, context, arena, tail-call, socket, XDP, LSM, and other program-type rules.

## Risks and Edge Cases

Because this file is a dispatcher, incorrect skeleton naming or ELF-byte factory wiring silently drops coverage. Capability drop/restore failures affect subsequent tests. Pre-execution callbacks must match map names and value layouts expected by the BPF object.

## Test Signals

Signals are per-skeleton loader subtest pass/fail records, expected verifier accept/reject diagnostics in paired BPF sources, successful CAP restoration, and successful prepopulation of `map_array_ro`/`map_array_48b`.
