# sources/distributed-fs/ceph-client/arch/mips/include/asm/vdso/vdso.h

## Purpose

`vdso.h` describes MIPS VDSO image metadata used by the kernel when mapping user VDSO pages and signal trampolines.

## Important APIs, Types, And Functions

Important API is `struct mips_vdso_image` plus `vdso_image`, `vdso_image_o32`, and `vdso_image_n32` declarations. Includes: `asm/sgidefs.h`, `vdso/page.h`, `asm/asm.h`, `asm/vdso.h`. Macros/constants: `__ASM_VDSO_VDSO_H`, `__VDSO_PAGES`. Types/enums/unions: `vdso_time_data`.

## Control Flow

Runtime flow is in VDSO setup code: select the ABI-specific image, map its page-aligned data via `vm_special_mapping`, and use stored offsets for sigreturn trampolines.

## State And Persistence

Persistent state is static image metadata and runtime mapping descriptors; no filesystem state is involved.

## Dependencies And Integration Points

It integrates with exec, mmap special mappings, signal delivery, ABI selection, and generated VDSO artifacts.

## Risks

Risks are wrong ABI image selection, stale trampoline offsets, or non-page-aligned image sizes.

## Test Signals

Test signals are VDSO mapping inspection, signal return tests, O32/N32/N64 userspace, and `readelf`/symbol-offset validation.
Static review signal: this source currently has 78 lines and 1795 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
