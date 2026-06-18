# sources/distributed-fs/ceph-client/arch/parisc/include/asm/string.h

Purpose: advertises PA-RISC optimized string/memory routines to generic code.

Important APIs/types/functions: defines `__HAVE_ARCH_MEMSET`, declares `memset`, defines `__HAVE_ARCH_MEMCPY`, and declares `memcpy`.

Control flow: generic code links to architecture implementations instead of generic C versions for these operations.

State and persistence: functions mutate caller-provided memory only. Dependencies and integration: used by lib/string, boot, mm, and drivers.

Risks and test signals: optimized routines must handle overlap rules where applicable and all alignments. Test string/memcpy selftests, KASAN/KMSAN builds where possible, and early boot memory clearing.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
