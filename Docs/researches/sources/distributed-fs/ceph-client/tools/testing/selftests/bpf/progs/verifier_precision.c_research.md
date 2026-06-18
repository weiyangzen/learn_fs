# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_precision.c

## Purpose
This file is a precision-marking regression suite. It ensures verifier `mark_precise` backtracking works through negation, endian conversions, conditional operations, atomics, stack values, map values, and LSM return constraints.

## Important APIs, Types, And Functions
It defines `precision_map` and many raw tracepoint/LSM naked programs. It emits atomic instructions with raw `.8byte` encodings, uses `bpf_map_lookup_elem`, and asserts detailed `mark_precise:` log output. Conditional-op coverage includes a static subprogram `__bpf_cond_op_r10`.

## Control Flow
Tests transform scalar values and then use them as offsets or return values requiring precision. Atomic tests store/load stack or map values, perform fetch-add, xchg, OR/AND/XOR, cmpxchg, and 32-bit atomics, then force precision marking on the result or argument. LSM tests check whether precise negation yields allowed return ranges.

## State And Persistence
The array map is a fixture for map-value atomic tests. Verifier state includes precise register marks, stack precision marks, parent-state backtracking, atomic result typing, and return-range constraints.

## Dependencies And Integration Points
It depends on `filter.h` instruction helpers, map helper metadata, raw tracepoint and LSM program types, and stable verifier log text.

## Risks
Precision bugs often cause latent unsoundness in variable offsets or excessive false positives. This file also protects against missed precision propagation through atomic read-modify-write instructions.

## Test Signals
The main signals are exact `mark_precise:` log sequences, successful verification for valid precision propagation, and failures where LSM `R0` ranges remain invalid.
