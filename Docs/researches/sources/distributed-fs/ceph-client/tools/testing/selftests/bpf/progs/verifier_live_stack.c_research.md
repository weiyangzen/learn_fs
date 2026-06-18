# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_live_stack.c

## Purpose
This large verifier selftest suite validates stack liveness analysis across direct stack reads/writes, subprogram calls, callbacks, parent-frame forwarding, helper arguments, stack-slot granularity, and pruning. It targets verifier logic that records which stack slots are used, defined, killed, or propagated across frame boundaries.

## Important APIs, Types, And Functions
The file defines a hash map `map`, an array map `array_map_8b`, a `snprintf_u64_fmt` format string, and many `SEC("socket")` naked programs with `__log_level(2)` and `__msg` expectations. It uses `bpf_map_lookup_elem`, `bpf_get_prandom_u32`, `bpf_loop`, iterator kfuncs (`bpf_iter_num_new/next/destroy` through BTF root forcing), `bpf_snprintf`, tail-call program arrays, and inline assembly helper immediates.

## Control Flow
Tests begin with simple same-frame reads/writes, then expand to joins, variable stack offsets, must-write tracking, caller/callee stack propagation, callback contexts, transitive parent reads, dynamic callbacks, spill/reload cases, and multi-offset joins. Several tests deliberately build paths where a callee or helper reads a caller stack slot only on some branch, forcing conservative liveness merging.

## State And Persistence
Only verifier state persists during analysis. Runtime maps are fixtures for pointer/nullability and helper argument typing. The critical state is stack slot liveness bitmaps, stack spill metadata, parent-frame aliases, callback instance state, and pruning records.

## Dependencies And Integration Points
It includes `filter.h` plus BPF helper headers and is tightly coupled to verifier log formatting. The selftest harness checks both accept/reject outcomes and detailed `use:`/`def:` log lines, so it acts as a regression suite for `analyze_subprog()` and stack liveness internals.

## Risks
Unsound stack liveness can let stale pointers, map-value-or-null pointers, or scalar-confused stack values survive pruning. Overly conservative liveness can also block pruning and cause verifier complexity growth. The many log assertions make this file sensitive to intentional verifier diagnostic wording changes.

## Test Signals
Signals include exact liveness log lines (`use: fp...`, `def: fp...`), success/failure annotations, `BPF_F_TEST_STATE_FREQ`, invalid memory access messages, and specific state-pruning `safe` messages.
