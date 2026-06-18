# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch_prctl.c

## Purpose
This beautifier formats x86 `arch_prctl` command codes as symbolic `ARCH_*` names for `perf trace`.

## Important APIs, Types, And Functions
The file includes generated `x86_arch_prctl_code_array.c` and defines three offset strarrays: `x86_arch_prctl_codes_1`, `_2`, and `_3`. It combines them with `DEFINE_STRARRAYS(x86_arch_prctl_codes)`. Public formatter `syscall_arg__scnprintf_x86_arch_prctl_code()` delegates to `x86_arch_prctl__scnprintf_code()`.

## Control Flow
At formatting time, the syscall argument value is read from `arg->val`; `strarrays__scnprintf()` searches the grouped strarrays and writes either a symbolic name, with optional prefix based on `arg->show_string_prefix`, or a `%#x` fallback.

## State, Dependencies, And Integration
Static generated arrays hold the decode tables. The formatter is declared in `beauty.h` as `SCA_X86_ARCH_PRCTL_CODE` and is used by `perf trace` syscall argument format metadata for x86 arch-prctl-like operations.

## Risks And Test Signals
Risks include generated table drift as new prctl codes appear and incorrect offset grouping for sparse ranges. Tests should verify known codes such as `ARCH_SET_FS` and shadow-stack commands render symbolically, while unknown codes render hex.
