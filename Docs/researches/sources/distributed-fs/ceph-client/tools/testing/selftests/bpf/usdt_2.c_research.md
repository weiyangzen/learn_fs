<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt_2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt_2.c

## Purpose
`usdt_2.c` defines an x86_64-only optimized-attach USDT target using the default NOP sequence from `usdt.h`.

## Important APIs, Types, And Functions
- `usdt_2()` is 16-byte aligned and fires `USDT(optimized_attach, usdt_2)`.
- Unlike `usdt_1.c`, it does not override `USDT_NOP`, so x86_64 uses the default combined NOP sequence.

## Control Flow
Calling `usdt_2()` executes the default probe-site NOP sequence and returns.

## State And Persistence
USDT note metadata is embedded in the object; no mutable runtime state exists.

## Dependencies And Integration Points
It depends on `usdt.h` and x86_64 compilation. It pairs with `usdt_1.c` to test optimized attach handling for different NOP encodings.

## Risks And Edge Cases
No probe is emitted on non-x86_64. The default NOP sequence length is central to the test and affects attach patching expectations.

## Test Signals
Attach tests should discover provider `optimized_attach`, probe `usdt_2`, and correctly patch/trigger the default NOP sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt_2.c -->
