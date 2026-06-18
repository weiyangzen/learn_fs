<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/objdump-func -->
# sources/distributed-fs/ceph-client/scripts/objdump-func

## Purpose

`objdump-func` prints the disassembly for one named function from an object or binary, making targeted inspection easier than browsing full objdump output.

## Important APIs, Types, and Functions

It accepts an object file and function name, uses objdump disassembly output, and filters from the matching function label until the next function label.

## Control Flow

The script validates arguments, invokes objdump, searches for a line like `<function>:`, prints subsequent lines, and stops when another symbol label is reached.

## State and Persistence Behavior

It is read-only and writes filtered disassembly to stdout.

## Dependencies and Integration Points

It depends on shell, objdump, and awk/sed-style filtering. It integrates with developer debugging and codegen review.

## Risks and Edge Cases

Inlined functions, local symbol suffixes, duplicate names, stripped objects, or objdump syntax changes can cause no match or wrong range. It does not understand source-level scopes.

## Test Signals

Run against objects with global functions, static functions with suffixes, missing names, and stripped binaries. Compare range boundaries with full objdump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/objdump-func -->
