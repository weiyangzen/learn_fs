<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpumask_types.h -->
# sources/distributed-fs/ceph-client/include/linux/cpumask_types.h

## Purpose

`cpumask_types.h` defines the fundamental `struct cpumask`, `cpumask_t`, `cpumask_bits()`, and `cpumask_var_t` type model. The source was read as a complete 66-line file.

## Important APIs, Types, and Functions

`typedef struct cpumask { DECLARE_BITMAP(bits, NR_CPUS); } cpumask_t` is the fixed-size mask type. `cpumask_bits(maskp)` exposes the bitmap storage. `cpumask_var_t` is either `struct cpumask *` when `CONFIG_CPUMASK_OFFSTACK=y`, or `struct cpumask[1]` otherwise.

## Control Flow

There is no runtime control flow. The preprocessor chooses pointer or array semantics at build time based on off-stack cpumask configuration.

## State and Persistence Behavior

Fixed `cpumask_t` objects contain `NR_CPUS` bits. Allocated `cpumask_var_t` objects may contain only `nr_cpumask_bits` worth of storage when off-stack, which is smaller than `NR_CPUS` on some systems.

## Dependencies and Integration Points

It depends on `linux/bitops.h` and `linux/threads.h`. It is included by `cpumask.h` and any code needing declarations without the whole API.

## Risks and Edge Cases

The header explicitly warns not to assign or return whole cpumask objects casually. Dereferencing `cpumask_var_t` and copying it by value can overrun allocation in off-stack builds. Per-CPU `cpumask_var_t` access must use `this_cpu_cpumask_var_t` style helpers from `cpumask.h`.

## Test Signals

Signals include builds with `CONFIG_CPUMASK_OFFSTACK` both enabled and disabled, static analysis for direct `*mask` copies, KASAN checks for allocated mask size, and compile tests for per-CPU cpumask variable access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpumask_types.h -->
