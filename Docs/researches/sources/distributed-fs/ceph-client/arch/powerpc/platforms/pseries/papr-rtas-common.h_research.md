# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-rtas-common.h

## Purpose
Declares the shared PAPR RTAS sequence and blob interface used by fd-oriented RTAS retrieval drivers.

## Important APIs, Types, And Functions
Defines sequence return constants `RTAS_SEQ_COMPLETE`, `RTAS_SEQ_MORE_DATA`, and `RTAS_SEQ_START_OVER`; `struct papr_rtas_blob`; and `struct papr_rtas_sequence`. Declares blob, sequence, setup, read, release, and seek helpers implemented in `papr-rtas-common.c`.

## Control Flow
No runtime flow is implemented in the header. The callback fields in `struct papr_rtas_sequence` define the expected begin/end/work lifecycle used by common code.

## State And Persistence
`struct papr_rtas_blob` represents immutable result data owned by a file handle. `struct papr_rtas_sequence` carries mutable in-progress error state and caller params. The header itself stores no state.

## Dependencies And Integration Points
Depends on Linux types and file operation types through translation units. It is included by PAPR miscdevice drivers that retrieve multi-call RTAS results.

## Risks And Edge Cases
Callers must use `papr_rtas_sequence_set_err` to preserve first-error semantics and must ensure callbacks allocate/free any RTAS work area even across retries. The struct names in comments say `papr_sequence`, but the actual exported type is `papr_rtas_sequence`.

## Test Signals
Compile coverage across all users, plus runtime tests in indices and physical-attestation paths, validate that the declared callback contract matches implementation behavior.
