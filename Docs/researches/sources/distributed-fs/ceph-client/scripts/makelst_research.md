<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/makelst -->
# sources/distributed-fs/ceph-client/scripts/makelst

## Purpose

`makelst` creates mixed source/assembly listings with relocation addresses adjusted against `System.map`. It is intended for Makefile rules that compile a `.c` file with debug info and pipe objdump output into a `.lst` artifact.

## Important APIs, Types, and Functions

The only helper is `field()`, a shell function that returns a numbered whitespace field after shifting. The script expects three positional arguments: object file, `System.map`, and objdump binary.

## Control Flow

It asks objdump for symbols in the object, selects the first text function, extracts its symbol name and object VMA, finds the same symbol in `System.map`, computes the address delta, and runs objdump with `-r --source --adjust-vma=<delta>`. If no readable `System.map` is present, it warns and defaults adjustment to zero.

## State and Persistence Behavior

There is no persistent state. Output is written to stdout and diagnostics to stderr.

## Dependencies and Integration Points

It depends on POSIX shell, `grep`, arithmetic expansion, `printf`, and the provided objdump. It integrates with optional Kbuild listing targets that know the object and `System.map` paths.

## Risks and Edge Cases

Symbol matching is simple text grep and can pick ambiguous names. Missing or mismatched `System.map`, object files without `.text` functions, non-GNU objdump output, and very large address deltas can degrade listings. The script does not quote all command substitutions robustly around unusual symbol data.

## Test Signals

Test with an object whose first text function appears in `System.map`, a missing map, no text symbols, and cross-objdump output. Validate that adjusted addresses match the linked kernel addresses and relocations remain visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/makelst -->
