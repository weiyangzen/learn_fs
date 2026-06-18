# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_kern.c

## Purpose
Tests lightweight skeleton CO-RE relocations against kernel BTF for prototype/type existence behavior.

## Important APIs, types, and functions
Uses `core_kern.lskel.h`. `test_core_kern_lskel()` calls `core_kern_lskel__open_and_load()`, attaches `core_relo_proto`, triggers tracepoints with `usleep(1)`, and checks `proto_out[]`.

## Control flow and state
State is limited to the lightweight skeleton and BSS `proto_out`. Link FD is returned by generated attach helper and cleaned by skeleton destruction.

## Dependencies and integration points
Depends on vmlinux BTF and lightweight skeleton support. Integrated as `test_core_kern_lskel()`.

## Risks and test signals
Risk is kernel BTF or lskel attach support drift. Passing signals are true/false/true values in `proto_out` for expected type-existence queries.
