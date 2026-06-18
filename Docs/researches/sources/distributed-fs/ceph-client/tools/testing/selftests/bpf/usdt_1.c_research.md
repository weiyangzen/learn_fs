<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt_1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt_1.c

## Purpose
`usdt_1.c` defines an x86_64-only optimized-attach USDT target that uses a single-byte NOP at an aligned function.

## Important APIs, Types, And Functions
- `USDT_NOP` is overridden as `.byte 0x90` before including `usdt.h`.
- `usdt_1()` is 16-byte aligned and fires `USDT(optimized_attach, usdt_1)`.

## Control Flow
Calling `usdt_1()` executes the single-byte NOP probe site and returns.

## State And Persistence
USDT metadata is embedded in ELF notes; no runtime data is kept.

## Dependencies And Integration Points
It depends on x86_64 assembly encoding and `usdt.h`. Optimized attach tests compare this one-byte NOP case with the default multi-byte NOP case in `usdt_2.c`.

## Risks And Edge Cases
The source compiles to no probe on non-x86_64 due to the preprocessor guard. Alignment and exact NOP size are the purpose of the test and should not be changed casually.

## Test Signals
Attach tests should discover provider `optimized_attach`, probe `usdt_1`, and patch/trigger the single-byte NOP site correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt_1.c -->
