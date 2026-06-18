# sources/distributed-fs/ceph-client/arch/xtensa/variants/de212/include/variant/tie.h

## Purpose
This generated header defines the `de212` optional-state save-area layout.

## Important APIs, types, and functions
It declares no coprocessors (`XCHAL_CP_NUM` 0, masks 0), a 28-byte NCP save area aligned to 4 bytes, and a 32-byte padded total. `XCHAL_NCP_SA_LIST()` contains seven registers: `acclo`, `acchi`, `scompare1`, and `m0`-`m3`.

## Control flow
No code executes here. Consumers expand list macros to derive offsets and save metadata.

## State and persistence behavior
Only MAC16 and conditional-store optional state are persistent across context save. There is no thread-global user register state in this variant.

## Dependencies and integration points
The file is consumed by kernel low-level Xtensa save-area code and must match `de212` `tie-asm.h`.

## Risks and edge cases
The absence of CP and threadptr state is semantically important. Importing another variant's save-area size or assuming 32 bytes of real payload would create ABI drift.

## Test signals
Compile save-list users and run context-switch/signal tests focused on MAC16 and `SCOMPARE1`, with checks that CP state paths remain disabled.
