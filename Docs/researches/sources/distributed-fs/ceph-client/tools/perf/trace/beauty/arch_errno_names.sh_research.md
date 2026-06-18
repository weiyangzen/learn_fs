# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch_errno_names.sh

## Purpose
This generator emits C code mapping errno numbers to names for each architecture with a specific UAPI `errno.h`, plus a dispatcher that chooses the lookup function by architecture string.

## Important APIs, Types, And Functions
Shell functions are `arch_string()`, `asm_errno_file()`, `create_errno_lookup_func()`, `process_arch()`, and `create_arch_errno_table_func()`. Inputs are a gcc command and `toolsdir`; output is C source using `strcmp()` and type `arch_syscalls__strerrno_t`.

## Control Flow
The script prints a C header block, discovers architectures under `$toolsdir/arch/*/include/uapi/asm/errno.h`, processes `generic` and each discovered architecture, and finally emits `arch_syscalls__strerrno_function()`. Each architecture preprocesses the relevant errno header with `$gcc -E -dM`, filters `#define E... <number>` lines, sorts by numeric value, and converts them into a switch returning the symbolic name or `"(unknown)"`.

## State, Dependencies, And Integration
It has no persistent state besides generated stdout redirected by the Makefile. It depends on gcc preprocessing, grep, awk, sort, sed, shell pipelines, and the tools UAPI header tree. Architecture names are normalized by replacing spaces/hyphens with underscores and lowercasing.

## Risks And Test Signals
Regex assumptions can miss aliases, expressions, or non-decimal definitions. Build-time generation should be tested by checking generated C compiles and maps representative errno values on generic and architecture-specific headers.
