# sources/distributed-fs/ceph-client/include/linux/kmsan-checks.h

## Purpose

`kmsan-checks.h` declares one-off KMSAN annotation helpers for poisoning, unpoisoning, checking memory, user copies, and metadata propagation after non-instrumented memory moves. The source was read as a complete 98-line file.

## Important APIs, Types, and Functions

With `CONFIG_KMSAN`, APIs are `kmsan_poison_memory()`, `kmsan_unpoison_memory()`, `kmsan_check_memory()`, `kmsan_copy_to_user()`, and `kmsan_memmove()`. Disabled builds provide empty inline stubs.

## Control Flow

Subsystems call these helpers around memory whose initialization state cannot be inferred by compiler instrumentation. User-copy paths call `kmsan_copy_to_user()` after copy attempts, and assembly or non-instrumented memcpy paths call `kmsan_memmove()` to copy shadow/origin metadata.

## State and Persistence Behavior

KMSAN shadow and origin metadata are updated in memory. There is no durable persistence; metadata tracks runtime initialization state.

## Dependencies and Integration Points

It depends on kernel types and integrates with KMSAN runtime, uaccess, assembly string operations, and subsystem-specific annotation sites.

## Risks and Edge Cases

Incorrect poisoning or unpoisoning can hide real leaks or create false positives. `kmsan_copy_to_user()` must use the actual copied byte count derived from `left`. Non-instrumented copies require metadata propagation or shadow state diverges from data.

## Test Signals

KMSAN selftests, intentional uninitialized-use tests, user-copy leak tests, non-instrumented memcpy metadata tests, and disabled-config build coverage are useful.
