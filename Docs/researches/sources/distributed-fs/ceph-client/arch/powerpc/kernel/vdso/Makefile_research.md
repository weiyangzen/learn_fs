# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/Makefile

## Purpose
Defines Kbuild rules for building PowerPC 32-bit and 64-bit vDSO shared objects, their C and assembly objects, linker scripts, generated offset headers, and vDSO validation.

## Important APIs, Types, And Functions
The file declares `obj-vdso32`, `obj-vdso64`, `targets`, `VDSOCC`, `CC32FLAGS`, `LD32FLAGS`, `AS32FLAGS`, `LD64FLAGS`, `AS64FLAGS`, `gen-vdso32sym`, `gen-vdso64sym`, and build commands `vdso32ld_and_check`, `vdso64ld_and_check`, `vdso32as`, `vdso32cc`, and `vdso64as`. It includes `lib/vdso/Makefile.include` for validation and generic C-vDSO inputs.

## Control Flow
Kbuild compiles assembly files twice with 32-bit and 64-bit defines, compiles C helpers with appropriate included generic vDSO sources, links `vdso32.so.dbg` and `vdso64.so.dbg` with explicit linker scripts, runs vDSO checks, and then uses `NM` plus generator scripts to create `include/generated/vdso{32,64}-offsets.h`.

## State And Persistence
State is build artifacts under the object tree: vDSO objects, `.so.dbg` files, linker scripts, and generated offset headers. There is no runtime state.

## Dependencies And Integration Points
Integrates PowerPC vDSO sources with generic vDSO C implementations, Kconfig flags, compiler/linker feature flags, `CROSS32_COMPILE`, LLD, orphan-section warnings, and wrappers that later embed the produced `.so.dbg` into the kernel image.

## Risks And Edge Cases
Flag filtering is fragile because kernel-wide 64-bit flags may be invalid for 32-bit vDSO builds. The fixed `r30` workaround preserves compatibility with older Go assumptions. Linker script ordering and generated offsets are ABI-sensitive. Missing `CROSS32_COMPILE` support can break 32-bit vDSO builds on some toolchains.

## Test Signals
Build `allyesconfig` and representative 32/64-bit PowerPC configs with GCC and Clang/LLD, verify `cmd_vdso_check`, inspect exported symbols with `readelf`, and ensure generated offset headers are stable across no-op rebuilds.
