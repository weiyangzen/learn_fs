# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/gen_vdso32_offsets.sh

## Purpose
Generates C preprocessor defines for offsets of `VDSO_*` symbols in the 32-bit PowerPC vDSO shared object.

## Important APIs, Types, And Functions
The script reads `nm` output on stdin and emits lines of the form `#define vdso32_offset_<name> 0x<addr>` for matching `VDSO_` symbols.

## Control Flow
It sets `LC_ALL=C`, runs a `sed` script that normalizes leading zeroes and captures hex addresses whose symbol type is a single arbitrary `nm` field and whose name begins with `VDSO_`.

## State And Persistence
No internal state. Its output is redirected by the Makefile into `include/generated/vdso32-offsets.h`.

## Dependencies And Integration Points
Used by the vDSO Makefile after linking `vdso32.so.dbg`. The generated header lets kernel C code refer to embedded vDSO symbol offsets without parsing ELF at runtime.

## Risks And Edge Cases
The parser depends on `nm` formatting and symbol names. It intentionally lives outside the Makefile because embedding the sed logic there interferes with Kbuild filtering and rebuild behavior.

## Test Signals
Build tests should confirm `include/generated/vdso32-offsets.h` contains expected `vdso32_offset_sigtramp*` symbols and does not regenerate on no-op builds.
