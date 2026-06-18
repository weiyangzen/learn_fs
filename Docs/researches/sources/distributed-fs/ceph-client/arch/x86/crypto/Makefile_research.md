# sources/distributed-fs/ceph-client/arch/x86/crypto/Makefile

## Purpose
Kbuild manifest mapping x86 crypto Kconfig symbols to object modules and their glue/assembly components.

## Important APIs, Types, And Functions
No runtime APIs are defined. Important object groupings include `aegis128-aesni-y := aegis128-aesni-asm.o aegis128-aesni-glue.o` and `aesni-intel-$(CONFIG_64BIT)` adding `aes-ctr-avx-x86_64.o`, `aes-gcm-aesni-x86_64.o`, VAES GCM variants, and AES-XTS AVX code to the AES-NI module.

## Control Flow And State
Kbuild uses `obj-$(CONFIG_...)` to include modules and `*-y` variables to compose multi-object modules. This file preserves source/module boundaries: common glue objects register algorithms, while architecture assembly objects provide hot paths.

## Dependencies And Integration
Consumes Kconfig symbols from `Kconfig`, integrates with the kernel crypto module build, and defines link composition that glue C files depend on for external assembly symbols.

## Risks And Test Signals
Risks are missing assembly objects for declared glue symbols, incorrect module grouping causing duplicate or unresolved exports, and 64-bit object leakage into 32-bit builds. Signals include x86 randconfig builds, module link tests, `modprobe` of AES-NI and AEGIS modules, and crypto selftests verifying registered driver names.
