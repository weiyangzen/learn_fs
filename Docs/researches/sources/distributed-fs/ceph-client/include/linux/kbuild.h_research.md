# sources/distributed-fs/ceph-client/include/linux/kbuild.h

## Purpose
Provides assembler-output macros used by kernel build helpers to export C constants, offsets, blank lines, and comments for generated assembly headers.

## Important APIs, Types, And Functions
`DEFINE(sym, val)` emits a magic `->sym value expression` marker through inline assembly. `BLANK()` emits a blank marker. `OFFSET(sym, str, mem)` emits `offsetof(struct str, mem)`. `COMMENT(x)` emits a comment marker.

## Control Flow
There is no runtime flow. During build, small C programs compile these inline assembly strings; scripts parse the emitted assembly to generate offset headers.

## State And Persistence
No runtime state. Generated headers persist as build artifacts and are consumed by assembly code.

## Dependencies And Integration Points
Depends on `offsetof()` being available in the including context. Integrates with `asm-offsets.c` style build steps and architecture assembly.

## Risks
The marker format is a build contract; changing it breaks parsers. `DEFINE()` requires immediate constants through the `"i"` constraint. Incorrect offsets can break low-level assembly ABI.

## Test Signals
Build tests across architectures, generated `asm-offsets.h` diffs, and assembly code using task/thread offsets are the primary signals.
