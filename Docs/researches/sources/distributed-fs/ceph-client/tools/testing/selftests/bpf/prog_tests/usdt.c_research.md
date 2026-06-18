# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/usdt.c

## Purpose
Tests libbpf USDT attach and argument decoding, including semaphores, cookies, zero/three/twelve argument probes, SIB addressing specs, optimized USDT patching, many inlined call sites, spec-id reuse, excessive distinct specs, deduplicated specs, and USDTs in helper binaries/shared libraries.

## APIs, Types, and Functions
Entry point `test_usdt()` runs `subtest_basic_usdt()`, x86 optimized variants, `subtest_multispec_usdt()`, and `subtest_urandom_usdt()`. It defines semaphore variables in `.probes`, trigger functions using `STAP_PROBE*`, x86 SIB inline assembly, optimized attach instruction scanners, many-call-site generators, and `urand_spawn()`/`urand_trigger()` helpers.

## Control Flow, State, and Persistence
Basic tests load `test_usdt`, attach skeleton and manual USDT links, trigger probes once or twice depending on optimized mode, and validate BSS call counts, cookies, argument counts, return codes, values, and byte sizes. Reattach tests destroy and recreate USDT links with a different cookie. x86 optimized attach verifies single-NOP probes use int3 while NOP+NOP5 probes use optimized call patching. Multispec tests trigger 100 sites, repeatedly detach/reattach to prove spec ids are freed, expect failure for too many distinct specs on supported builds, and expect success for 400 call sites sharing a deduplicated spec. Urandom tests attach automatically or manually to executable and shared-library USDTs and validate counts/sums.

## Dependencies and Integration
Depends on `../sdt.h`, generated `test_usdt` and `test_urandom_usdt` skeletons, selftest `urandom_read` and `liburandom_read.so`, libbpf USDT attach APIs, architecture-specific instruction patching on x86, and generated assembly symbols for optimized probes.

## Risks and Test Signals
Risks include compiler inlining/codegen changing USDT sites, architecture differences in argument specs, optimized patch instruction layout, semaphore cleanup, helper binary availability, and spec limit behavior differences. Signals are exact call counts, cookies, argument values/sizes, expected `-E2BIG` for excessive distinct specs, no dangling attachments after partial failure, optimized instruction bytes, and urandom call counts/sums of 256.
