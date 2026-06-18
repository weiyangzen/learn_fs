<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt.h

## Purpose
`usdt.h` is a single-header USDT macro library for defining user statically-defined tracepoints with no semaphore, implicit semaphore, or explicit user-defined semaphore. It emits NOP probe sites, `.note.stapsdt` metadata, optional `.probes` semaphore storage, and architecture-aware argument descriptors.

## Important APIs, Types, And Functions
- Public macros include `USDT(group, name, ...)`, `USDT_WITH_SEMA(group, name, ...)`, `USDT_IS_ACTIVE(group, name)`, `USDT_DEFINE_SEMA(sema)`, `USDT_DECLARE_SEMA(sema)`, `USDT_SEMA_IS_ACTIVE(sema)`, `USDT_WITH_EXPLICIT_SEMA(sema, group, name, ...)`, and `USDT_SEMA(sema)`.
- `struct usdt_sema { volatile unsigned short active; }` is the semaphore storage type.
- Implementation macros create semaphore names, count variadic arguments up to 12, stringify assembly, choose address directive size, emit `.note.stapsdt`, and build operand metadata.
- Architecture macros customize `USDT_NOP`, `USDT_ARG_CONSTRAINT`, and operand references for PPC, ARM, LoongArch, x86, s390, and others.

## Control Flow
Public probe macros expand to a `do { ... } while (0)` block that optionally defines or references semaphore storage, then emits inline assembly containing a probe-site NOP, STAPSDT note fields for provider/name/location/base/semaphore, argument descriptors, and `.stapsdt.base`. `USDT_IS_ACTIVE()` and `USDT_SEMA_IS_ACTIVE()` read semaphore activity counters so callers can avoid expensive argument preparation.

## State And Persistence
Implicit and explicit semaphores are ELF/global variables in `.probes`; note metadata persists in the binary for tracing tools. Runtime mutable state is limited to semaphore counters updated by tracing infrastructure.

## Dependencies And Integration Points
It is a local alternative to system `sdt.h` and integrates with BPF/libbpf USDT tests, ELF note parsers, uprobes, and application test binaries such as `usdt_1.c`, `usdt_2.c`, and `urandom_read*`.

## Risks And Edge Cases
Inline assembly and operand metadata are architecture/compiler-sensitive. The header supports up to 12 arguments; more will fail macro expansion. Semaphore sharing across shared libraries is explicitly constrained because STAPSDT note relocations are limited. C++ signedness detection uses templates while C uses compiler builtins, so behavior must be maintained in both languages.

## Test Signals
Passing tests can discover probes by provider/name, attach with or without semaphores, observe active semaphore counters, decode argument descriptors correctly, and patch NOP sites for optimized attach cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt.h -->
