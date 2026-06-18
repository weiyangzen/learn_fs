## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/fake_32bit_build.h

Purpose: adjusts preprocessor configuration so a 32-bit vDSO can be built inside a 64-bit kernel build.

Important definitions: undefines `CONFIG_64BIT`, `CONFIG_X86_64`, `CONFIG_COMPAT`, page-table and memory options, `CONFIG_NR_CPUS`, and `CONFIG_PARAVIRT_XXL`; defines `CONFIG_X86_32`, `CONFIG_PGTABLE_LEVELS 2`, `CONFIG_PAGE_OFFSET 0`, `CONFIG_ILLEGAL_POINTER_VALUE 0`, `CONFIG_NR_CPUS 1`, and `BUILD_VDSO32_64`.

Control flow: header is force-included by the vdso32 Makefile only under `CONFIG_X86_64`. It has no runtime behavior.

State/persistence: affects preprocessor-visible configuration for generated vDSO object files.

Integration points: common vDSO time/getcpu code, asm headers that branch on 32-bit versus 64-bit config, and Kbuild flags.

Risks: stale config overrides can silently change ABI layout or type selection. Test signals include preprocessor/build checks for vdso32 on x86_64, symbol ABI inspection, and comparing native i386 versus compat vDSO behavior.
