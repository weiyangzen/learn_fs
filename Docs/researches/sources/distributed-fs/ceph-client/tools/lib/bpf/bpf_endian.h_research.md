<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_endian.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_endian.h

## Purpose
`bpf_endian.h` provides byte-order conversion macros usable from both BPF programs and userspace code. It avoids relying on libc byte-order headers and accounts for LLVM BPF target endianness behavior.

## Important APIs, types, and functions
Internal macros `___bpf_mvb()`, `___bpf_swab16()`, `___bpf_swab32()`, and `___bpf_swab64()` implement constant byte swaps. Public macros are `bpf_htons()`, `bpf_ntohs()`, `bpf_htonl()`, `bpf_ntohl()`, `bpf_cpu_to_be64()`, and `bpf_be64_to_cpu()`. They choose constant swabs or `__builtin_bswap*()` with `__builtin_constant_p()`.

## Control flow
Preprocessor branches inspect compiler `__BYTE_ORDER__`. Little-endian builds define conversions as swaps; big-endian builds define them as identity. Unsupported byte order triggers a compile-time error.

## State and persistence behavior
There is no state. The macros compile into constants, bswap operations, or identity expressions.

## Dependencies and integration points
It assumes Linux integer typedefs such as `__u16`, `__u32`, and `__u64` are already available, typically via `vmlinux.h`, `<linux/types.h>`, or related BPF headers. It is installed as a public libbpf BPF-program helper header.

## Risks and edge cases
Using compiler `__BYTE_ORDER__` is intentional for BPF cross-targets, but builds with misconfigured target endianness will silently produce wrong conversions. Macro arguments may be evaluated within builtin/constant expressions; callers should avoid side effects.

## Test signals
Compile BPF and userspace tests for little-endian and big-endian targets, compare constant and variable conversions, inspect generated BPF instructions for expected endian operations, and build with missing byte-order macros to confirm the compile error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_endian.h -->
