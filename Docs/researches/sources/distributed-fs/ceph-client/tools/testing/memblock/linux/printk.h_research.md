<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/printk.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/linux/printk.h

## Purpose

`linux/printk.h` maps kernel logging macros to user-space `printf` for the memblock simulator.

## Important APIs, Types, and Functions

It includes `stdio.h` and `asm/bug.h`, suppresses GCC format warnings around the mapping, defines `printk` as `printf`, and aliases `pr_info`, `pr_debug`, `pr_cont`, `pr_err`, and `pr_warn` to `printk`.

## Control Flow

Logging call sites execute as direct `printf` calls. The diagnostic pragma suppresses known format mismatches from memblock debug calls using kernel integer types.

## State and Persistence Behavior

There is no logging state beyond stdout/stderr buffering controlled by the C runtime. Messages are not persisted unless the caller redirects process output.

## Dependencies and Integration Points

It integrates kernel memblock logging with the simulator's console output and common test verbosity controls. `MEMBLOCK_DEBUG=1` can route additional memblock debug text through these macros.

## Risks and Edge Cases

The file appears to use `#pragma GCC diagnostic push` twice instead of a final pop, which can leave warning state suppressed for subsequent includes in the translation unit. Mapping all severities to `printf` loses kernel log levels and rate limiting.

## Test Signals

Builds should not fail on memblock debug format strings. Verbose/debug simulator runs should print expected messages without changing allocation assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/printk.h -->
