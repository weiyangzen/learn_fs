# sources/distributed-fs/ceph-client/scripts/checkstack.pl

## Purpose
`checkstack.pl` analyzes `objdump -d` output and reports functions whose static stack growth exceeds a configurable threshold. It is a kernel build/debugging helper used after compiling objects or `vmlinux`, with optional architecture and minimum-stack arguments.

## Important APIs, Types, and Functions
The script is procedural Perl. Its main data structures are regex variables `$re` for fixed stack deltas, `$dre` for dynamic deltas, `$funcre` for objdump function headers, and `@stack` for report lines. Architecture dispatch selects instruction regexes for arm, arm64, x86, mips, powerpc, s390, sparc, riscv, loongarch, and others. `arm_push_handling()` estimates ARM frame-pointer push size. `sort_lines()` orders findings by descending byte count and then function name.

## Control Flow and State
Startup resolves `$arch` from argv or `uname -m`, sets `$min_stack` to the numeric argument or 512, and installs architecture-specific patterns. The main loop streams stdin once, tracks the current object file, function, starting address, and accumulated stack size, and pushes an output row when a function boundary is reached and the previous total is above the threshold. State is in memory only and resets per function.

## Dependencies and Integration
It depends on Perl and GNU-style objdump text. It integrates with kernel workflows as `objdump -d vmlinux | scripts/checkstack.pl [arch] [min_stack]`.

## Risks and Test Signals
Correctness depends on instruction formatting and regex coverage for each architecture. Dynamic x86 stack reductions are accumulated but are architecture-limited. Test with representative objdump snippets for each supported architecture, threshold boundaries, file format lines, ARM push sequences, and sorting ties.
