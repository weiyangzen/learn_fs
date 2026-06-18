<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_deps.h -->
# sources/compression/zstd/contrib/linux-kernel/zstd_deps.h

## Purpose
`zstd_deps.h` supplies the dependency abstraction layer that lets upstream zstd sources compile in the Linux kernel environment or the local user-space kernel test harness.

## Important APIs, Types, And Functions
It defines feature blocks for common memory functions, allocator stubs, 64-bit division via `div_u64`, assertion mapping through `WARN_ON`, IO/debug macros, and stdint-style integer inclusion. `ZSTD_malloc`, `ZSTD_free`, and `ZSTD_calloc` intentionally return no heap allocation in kernel mode.

## Control Flow
The header is controlled by `ZSTD_DEPS_*` macros. Each block emits exactly the needed replacement definitions when the corresponding zstd source component requests them.

## State And Persistence
No state is owned. It controls compile-time behavior and allocation policy only.

## Dependencies And Integration Points
It integrates imported zstd C files with Linux headers such as `linux/kernel.h`, `linux/math64.h`, `linux/printk.h`, and test stubs under `test/include`.

## Risks
Macro ordering is fragile: definitions must appear before zstd internals include dependency blocks. Allocator stubbing means code paths requiring heap allocation must be avoided or converted to workspace APIs.

## Test Signals
`macro-test.sh`, `test.c`, and module compilation validate that all requested dependency blocks are present and kernel-compatible.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_deps.h -->
