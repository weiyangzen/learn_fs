<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/string_override.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/string_override.c

## Purpose
`string_override.c` supplies minimal `memcmp()`, `memcpy()`, `memset()`, and `strnlen()` implementations that can be linked into KVM guest code. This prevents compiler-generated calls to out-of-line libc or PLT entries, which are not available inside selftest guests.

## Important APIs, Types, and Functions
The file defines standard C string/memory entry points with simple byte loops. `memcmp()` returns the first unsigned-byte difference, `memcpy()` copies forward and returns `dest`, `memset()` fills bytes and returns `s`, and `strnlen()` counts until NUL or the supplied limit.

## Control Flow
All functions are straight-line loops with no helper calls. They intentionally avoid optimized library dispatch, dynamic loading, vector routines, and platform-specific code.

## State and Persistence
There is no persistent state. The only side effects are writes to caller-provided memory in `memcpy()` and `memset()`.

## Dependencies and Integration Points
The only include is `<stddef.h>`. These symbols override basic built-ins when guest payloads are linked, integrating with any guest C code that the compiler lowers to standard memory/string functions.

## Risks and Test Signals
The risk is semantic drift from standard functions, especially overlapping `memcpy()` behavior, signedness in `memcmp()`, and bounded termination in `strnlen()`. Test signals are indirect: guest code that uses these helpers should execute without jumping to unresolved host/runtime text and should preserve expected C-library behavior for simple byte operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/string_override.c -->
