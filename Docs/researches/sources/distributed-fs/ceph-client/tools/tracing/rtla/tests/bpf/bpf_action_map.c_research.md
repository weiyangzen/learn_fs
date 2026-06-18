# sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/bpf/bpf_action_map.c

## Purpose

`bpf_action_map.c` is a minimal BPF program used by rtla tests to verify that timerlat BPF action programs can be loaded, attached, and mutate a BPF map when a timerlat action tracepoint fires.

## Important APIs, Types, and Functions

It declares `rtla_test_map`, a one-entry `BPF_MAP_TYPE_ARRAY` keyed by `unsigned int` with `unsigned long long` values. `action_handler()` is attached to `SEC("tp/timerlat_action")` and writes value `42` at key `0`. `LICENSE` is GPL.

## Control Flow and Data Flow

When the `timerlat_action` tracepoint runs, the BPF handler updates the test map with `bpf_map_update_elem(..., BPF_ANY)` and returns 0. User-space test code can read the map to confirm the action ran.

## State and Persistence Behavior

State persists in the BPF map while the program/map are loaded. The source file itself has no user-space lifecycle logic.

## Dependencies and Integration Points

The program depends on kernel BPF tracepoint support, `linux/bpf.h`, `bpf/bpf_tracing.h`, the `timerlat_action` tracepoint type, and rtla's `--bpf-action` loading path.

## Risks and Edge Cases

The tracepoint struct is forward-declared and unused, so ABI changes matter only for attach compatibility. The fixed value tests action execution but not argument parsing. Loading requires appropriate privileges and BPF tooling support.

## Test Signals

Pass signals are successful BPF compilation/loading, action attachment, timerlat threshold/action execution, and a map value of `42` at key `0`.
