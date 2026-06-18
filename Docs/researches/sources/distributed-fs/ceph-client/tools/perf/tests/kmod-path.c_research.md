# sources/distributed-fs/ceph-client/tools/perf/tests/kmod-path.c

## Purpose
Tests kernel-module path parsing and `is_kernel_module()` classification for plain modules, compressed paths, bracketed kernel DSOs, and special pseudo-DSOs.

## Important APIs, Types, and Functions
- `test()` wraps `__kmod_path__parse()` and validates `struct kmod_path` fields `kmod`, `comp`, and optional allocated `name`.
- `test_is_kernel_module()` validates `is_kernel_module(path, cpumode)` for unknown/kernel/user cpumodes.
- Macros `T()` and `M()` make the test table compact.
- `test__kmod_path__parse()` contains the table for module and non-module path forms.

## Control Flow
The suite runs table rows for `.ko` paths, optional `.ko.gz` and `.gz` behavior under `HAVE_ZLIB_SUPPORT`, bracketed module names, dotted module names, vDSO/vsyscall variants, and `[kernel.kallsyms]`. For each parse row it checks whether the path is a module, whether it is compressed, and whether allocated names match normalized bracketed module names. For each classification row it checks cpumode-dependent kernel-module status.

## State and Persistence
Only stack-local `struct kmod_path` and optional heap-allocated `m.name` are used; `m.name` is freed per row. No persistent state exists.

## Dependencies and Integration Points
Exercises DSO path parsing from `dso.h`, cpumode constants from perf events, zlib-conditional compressed module behavior, and test registration via `DEFINE_SUITE("kmod_path__parse", kmod_path__parse)`.

## Risks and Edge Cases
- Coverage differs by build configuration because compressed-path cases are compiled only with zlib support.
- The same `.ko` and bracketed cases are repeated, likely to catch idempotence/regression but not adding new scenarios.
- Module classification intentionally returns false for user cpumode even if the path string resembles a module.

## Test Signals
Passing confirms normalized module names, compression flags, and cpumode-sensitive module detection match expectations across path styles.
