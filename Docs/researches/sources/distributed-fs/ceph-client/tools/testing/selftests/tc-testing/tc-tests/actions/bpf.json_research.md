# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/bpf.json

## Purpose
Defines 12 tc action tests for classic BPF and eBPF action handling.

## Important APIs, Types, And Functions
Cases cover valid/invalid cBPF bytecode, valid/invalid eBPF object sections from `$EBPFDIR/action-ebpf`, replace behavior, delete, list, flush, duplicate and invalid indexes, cookies, and invalid `goto chain` control. Verification uses `tc action get/list action bpf` plus regex `matchPattern` and `matchCount`.

## Control Flow
Each case uses setup to establish any expected preexisting action state, runs a `tc action add/replace/delete/list/flush` command, checks the expected exit code, verifies state with another `tc` command, and tears down action state. eBPF cases use sections `action-ok` and `action-ko` from `action.c`.

## State And Persistence
Kernel tc action table state persists during each case and is removed in teardown or flush tests. Cookies and indexes are part of tc action state.

## Dependencies And Integration Points
Depends on `NET_ACT_BPF`, classic BPF parsing, eBPF verifier/object loading, the compiled action object, and the tc-testing runner. Unlike most other action JSON files, this one does not require `nsPlugin`.

## Risks
Regexes are sensitive to iproute2 output formatting, including JIT tag text. Invalid eBPF behavior depends on verifier rules. Large index boundary behavior may vary if tc parser changes.

## Test Signals
Expected signals are installed valid BPF actions with correct bytecode/object metadata, rejected invalid bytecode/object or invalid index cases, correct reference counts, cookie display, and successful list/flush count changes.
