# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/kabi_ex.h

## Purpose
`examples/kabi_ex.h` is an executable specification for stable kABI features. It defines example types and embeds FileCheck expectations for `--dump-dies` and `--dump-versions`.

## Important APIs, Types, and Functions
The header exercises declaration-only rules, ignored/overridden enumerators, reserved fields, reserved arrays, ignored hole fields, replacement fields, byte-size overrides, type-string overrides, and type strings for non-existent types or symbols.

## Control Flow
At compile time it defines structures/enums and static assertions proving replacement layouts remain size-compatible. At test time the comments drive FileCheck over `gendwarfksyms` output.

## State and Persistence Behavior
It emits kABI rule section entries through macros from `kabi.h` and creates type DWARF for the example object.

## Dependencies and Integration Points
It depends on `kabi.h`, `kabi_ex.c`, `nm`, `gendwarfksyms`, and FileCheck for validation.

## Risks and Test Signals
Expectations can be compiler-sensitive, especially type spelling (`unsigned long` variants) and DWARF member ordering. It is the primary regression signal for stable kABI rendering behavior.
