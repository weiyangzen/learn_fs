# sources/distributed-fs/ceph-client/arch/xtensa/variants/dc232b/include/variant/tie.h

## Purpose
This generated header describes `dc232b` optional and TIE state layout.

## Important APIs, types, and functions
It declares CP7 `XTIOP` as the only coprocessor (`XCHAL_CP_MASK` `0x80`) with zero save size. Non-coprocessor state is 32 bytes aligned to 4 bytes; `XCHAL_NCP_SA_LIST()` contains eight registers: `acclo`, `acchi`, `m0`-`m3`, `scompare1`, and `threadptr`.

## Control flow
No runtime code is present. Consumers define `XCHAL_SA_REG` to expand the save-area list into metadata or code.

## State and persistence behavior
The layout captures MAC16 accumulator/multiplier state, conditional-store state, and thread pointer state. CP state is nominally present only for XTIOP and does not require save/restore.

## Dependencies and integration points
It is paired with `dc232b` `core.h` and `tie-asm.h`; the latter implements the concrete assembler ordering for this list. Kernel thread-switch, signal, and ptrace facilities depend on these sizes.

## Risks and edge cases
The save area is exactly 32 bytes with no larger total padding, unlike `csp`. Reordering list entries or mixing with another variant's assembler macros would silently misrestore registers.

## Test signals
Compile-time expansion of NCP and CP lists, plus runtime TLS/MAC16/conditional-store preservation across preemption and signal delivery, are the main signals.
