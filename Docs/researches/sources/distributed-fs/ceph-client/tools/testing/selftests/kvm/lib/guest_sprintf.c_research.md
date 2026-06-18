# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/guest_sprintf.c

## Purpose
This file implements a small guest-safe `snprintf`/`vsnprintf` for KVM selftest guest code, avoiding reliance on full libc formatting inside the guest.

## Important APIs, Types, and Functions
`guest_vsnprintf()` parses format strings and writes bounded output. `guest_snprintf()` is the variadic wrapper. Helpers include `skip_atoi()`, `number()`, and `APPEND_BUFFER_SAFE`, which asserts before every write. Supported conversions include `%c`, `%s`, `%p`, `%n`, `%o`, `%x`, `%X`, `%d`, `%i`, `%u`, and `%%`, with common flags, width, precision, and `h`/`l`/`ll` handling.

## Control Flow
The formatter scans literals and `%` sequences, parses flags, width, precision, and qualifier, then either emits character/string/pointer/special cases or formats numeric output through `number()`. It terminates with NUL and returns the number of bytes written.

## State, Dependencies, and Integration
There is no persistent state. It depends on guest assertion macros and limited string helpers. It integrates with guest-side diagnostics such as `GUEST_ASSERT` formatting.

## Risks and Test Signals
The implementation is intentionally limited and asserts on buffer overflow instead of truncating like standard `snprintf`. Unsupported formats are emitted literally after `%`, which can hide formatting mistakes but preserves guest progress.
