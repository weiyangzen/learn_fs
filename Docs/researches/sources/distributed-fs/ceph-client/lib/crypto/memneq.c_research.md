# sources/distributed-fs/ceph-client/lib/crypto/memneq.c

## Purpose
Implements `__crypto_memneq()`, a constant-time memory inequality helper used by the public `crypto_memneq()` wrapper.

## Important APIs, Types, and Functions
- Exports `__crypto_memneq(const void *a, const void *b, size_t size)`.
- `__crypto_memneq_generic()` ORs all byte or word differences without early exit.
- `__crypto_memneq_16()` unrolls the common 16-byte comparison path.
- Uses `OPTIMIZER_HIDE_VAR()` to prevent compiler transformations that could reintroduce data-dependent exits or reductions.

## Control Flow and State
The function dispatches by size: exactly 16 bytes uses a loop-free fast path; all other sizes use the generic loop. It returns nonzero if any byte differs and zero if all compared bytes match. No persistent state is stored.

## Dependencies and Integration Points
Depends on `<crypto/utils.h>`, unaligned access helpers, and `CONFIG_HAVE_EFFICIENT_UNALIGNED_ACCESS` for word-sized loading. It integrates with MAC/tag verification code that must avoid `memcmp()` timing leakage.

## Risks and Test Signals
The function compares exactly the supplied length and does not hide length differences; callers must ensure lengths are public or separately checked safely. Compiler behavior is central to the security property, so generated code review and KUnit/static tests for no early exit are useful. Functional tests should cover equal buffers, first/last-byte differences, 16-byte and non-16-byte lengths, and unaligned inputs on architectures that allow them.
