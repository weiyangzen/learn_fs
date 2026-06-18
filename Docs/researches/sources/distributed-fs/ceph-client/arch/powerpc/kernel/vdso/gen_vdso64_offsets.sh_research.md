# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/gen_vdso64_offsets.sh

## Purpose
Generates C preprocessor defines for offsets of `VDSO_*` symbols in the 64-bit PowerPC vDSO shared object.

## Important APIs, Types, And Functions
The script reads `nm` output and emits `#define vdso64_offset_<name> 0x<addr>` for `VDSO_` symbols.

## Control Flow
It sets `LC_ALL=C` and applies the same symbol-matching `sed` transform as the 32-bit variant, with the output prefix changed to `vdso64_offset_`.

## State And Persistence
No internal state. The Makefile redirects output to `include/generated/vdso64-offsets.h`.

## Dependencies And Integration Points
Runs after `vdso64.so.dbg` is linked and provides offsets used by kernel code for embedded 64-bit vDSO symbols, especially signal trampoline entry points.

## Risks And Edge Cases
Depends on stable `nm` output and linker-script-provided `VDSO_*` symbols. Missing or renamed symbols would silently omit defines and fail later at compile time.

## Test Signals
Build coverage should verify generated `vdso64_offset_*` definitions, especially `vdso64_offset_sigtramp_rt64`, and ensure no spurious rebuilds.
