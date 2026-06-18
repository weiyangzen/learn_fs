## sources/distributed-fs/ceph-client/lib/tests/memcpy_kunit.c

### Purpose
This KUnit suite validates kernel `memcpy()`, `memmove()`, `memset()`, and related structure-field clearing helpers. It covers small fixed buffers, argument side-effect behavior, overlap handling, architecture-sensitive large copies, and slow exhaustive-ish large-buffer movement patterns.

### Important APIs, types, and functions
`struct some_bytes` overlays a 32-byte byte array with named fields, enabling byte-level checks plus `memset_after()` and `memset_startat()` field-based tests. Macros `check()` and `compare()` verify byte contents and report the active `TEST_OP`. `memcpy_test()`, `memmove_test()`, and `memset_test()` exercise direct assignment, full overwrites, middle overwrites, pointer/count/value side effects, and helper semantics. Large static buffers `large_src`, `large_dst`, and `large_zero` support `copy_large_test()` for non-overlapping copies, `memmove_overlap_test()` for overlapping windows, and `inner_loop()` for verifying preserved source fragments and zero regions.

### Control flow
The suite initializes expected control patterns locally, mutates destination buffers, and compares every byte. Large-copy paths call `init_large()`, which fills source data with random bytes, forces non-zero edges, and clears the destination. `copy_large_test()` iterates copy sizes from 1 to 1024 and all destination offsets within the source-sized window, then checks before-copy zeros, copied bytes, after-copy zeros, and clears the touched region. `memmove_overlap_test()` reduces the full overlap search space with `next_step()` while emphasizing boundaries and cacheline-crossing offsets, periodically calling `cond_resched()`.

### State and persistence
Small tests are stack-local. Large tests share static buffers that are explicitly reinitialized before use. There is no persistent kernel object, no device, and no heap allocation. Random source contents are intentionally non-deterministic, but validation checks byte-for-byte consistency rather than fixed values.

### Dependencies and integration points
The suite depends on KUnit, slab/vmalloc headers only indirectly through includes, random bytes, overflow/kernel helpers, and scheduler rescheduling for long loops. KUnit marks large copy and overlap cases with `KUNIT_CASE_SLOW`, allowing runners to include or exclude expensive coverage.

### Risks and edge cases
The slow cases can be expensive: nested loops over 1024 byte lengths and offsets are intentionally broad. Random data makes reproducing a failing byte pattern harder unless the failure is structural. The tests validate memory contents after legal operations; they do not intentionally invoke undefined `memcpy()` overlap. Architecture-specific comments note i386 `rep movsl` behavior for 256/1024 offsets.

### Test signals
Signals include full byte comparison after each operation, explicit detection that macro/function arguments are evaluated once, large-copy guard-region checks, both backward and forward overlapping `memmove()` checks, and slow KUnit case tagging for broad memory primitive coverage.
