# sources/distributed-fs/openafs/src/WINNT/afsd/largeintdotnet.c

Purpose: supplies compatibility implementations of old Windows `LARGE_INTEGER` helper routines for MSVC 7.0 and newer builds where those functions are not available as expected.

Important APIs/types/functions: under `_MSC_VER >= 1300`, implements `LargeIntegerAdd`, `LargeIntegerSubtract`, `ExtendedLargeIntegerDivide`, `LargeIntegerDivide`, and `ConvertLongToLargeInteger`. The add/subtract routines manually handle low-part carry/borrow; divide routines combine high/low parts into `ULONGLONG`, divide, and split quotient/remainder back into `LARGE_INTEGER`.

Control flow: simple arithmetic helpers return zeroed results for divide-by-zero, return the original dividend for divide-by-one, and otherwise use unsigned 64-bit division.

State/persistence: no mutable state or persistence.

Dependencies/integration: depends on Windows `LARGE_INTEGER` layout and is used by older AFSD cache and raw I/O code that calls Windows-style large integer helpers.

Risks: signedness is subtle because `HighPart` is assigned into `ULONGLONG`; negative `LARGE_INTEGER` values are not clearly handled as signed arithmetic. `ExtendedLargeIntegerDivide` dereferences `remainder` without null checks in nontrivial cases. Divide-by-zero silently returns zero instead of surfacing an error. The `if (r1 > ULONG_MAX) /*XXX */;` branch is a no-op.

Test signals: verify carry/borrow boundaries, high-part propagation, division by zero/one, 64-bit values above 4 GiB, and behavior for negative high parts if any caller can pass signed offsets.
