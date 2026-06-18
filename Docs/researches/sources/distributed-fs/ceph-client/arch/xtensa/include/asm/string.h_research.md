<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/string.h

Purpose: supplies Xtensa-specific inline implementations or declarations for common string/memory operations. It defines inline `strcpy`, `strncpy`, `strcmp`, and `strncmp`, declares `memset`, `__memset`, `memcpy`, `__memcpy`, `memmove`, and `__memmove`, and redirects memops to non-instrumented versions under KASAN for non-instrumented files.

Control flow is tight inline assembly loops for byte loads/stores and comparisons; memory block functions live in arch library code. Persistent state is only caller memory. Dependencies include Xtensa load/store instructions, `size_t`, `uintptr_t`, KASAN, and FORTIFY interaction. Integration points are the whole kernel C library layer, uaccess clear/copy helpers, boot code, and sanitizer instrumentation. Risks include missing NUL padding semantics in `strncpy`, inline asm constraints/memory clobbers, KASAN/FORTIFY bypass mistakes, and unaligned or inaccessible pointers. Test signals include lib/string selftests, KASAN builds, boot smoke, memmove overlap tests, and compiler warning checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/string.h -->
