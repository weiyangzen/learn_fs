# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_const.c

## Purpose

`verifier_const.c` verifies verifier enforcement for writes to global-data sections, especially `.rodata` versus mutable `.bss` and `.data`. The tests ensure helpers and direct stores cannot mutate read-only global map values while equivalent writes to mutable globals are accepted.

## Important APIs, Types, and Functions

The file uses `vmlinux.h`, libbpf helpers, tracing helpers, and `bpf_misc.h`. It defines global variables in normal C rather than explicit map structs, relying on libbpf to materialize `.rodata`, `.bss`, and `.data` maps. Helper coverage includes `bpf_strtol`, `bpf_check_mtu`, `bpf_get_prandom_u32`, and `bpf_copy_from_user`. Programs are mostly `SEC("tc/ingress")`; the final dynamic-write test is an LSM sleepable section `SEC("lsm.s/bprm_committed_creds")`.

## Control Flow

The test matrix writes through helper output pointers or direct pointer arithmetic. `tcx1` and `tcx4` attempt helper writes into rodata-backed globals and must fail with `write into map forbidden`. Parallel `.bss` and `.data` variants pass. The dynamic cases compute an unknown offset or address using `bpf_get_prandom_u32` and still expect rodata rejection, proving the verifier does not require a fully constant store target to protect read-only map values.

## State and Persistence Behavior

Global variables persist as BPF global data maps for the lifetime of the loaded object. The key state is the verifier's map mutability bit: `.rodata` must remain immutable even when accessed through helper pointer arguments or uncertain register offsets, while `.bss` and `.data` remain writable.

## Dependencies and Integration Points

The file integrates with libbpf global-data map creation, tc and LSM program loaders, helper argument verification, and verifier map-value permission checks. It is a regression guard for global data lowering and helper output pointer handling.

## Risks and Test Signals

Main risks are accidentally treating rodata as mutable when helper arguments are involved, or over-restricting mutable global sections. Test signals are four expected `write into map forbidden` failures and successful writes through the same helpers into `.bss` and `.data`.
