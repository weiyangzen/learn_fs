<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/string_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/string_64.h

Purpose: declares x86-64 optimized memory/string functions and inline memset-size helpers. Important APIs include `memcpy`, `__memcpy`, `memset`, `__memset`, `memset16/32/64`, `memmove`, `memcmp`, `strcmp`, and `memcpy_flushcache()` for persistent-memory/cache-flush users.

Control flow: generic callers use optimized external assembly/C routines; inline `memset16/32/64` use `rep stos*`; flushcache copies call cache-flushing implementations when `CONFIG_ARCH_HAS_UACCESS_FLUSHCACHE` is enabled. KMSAN can redirect to sanitizer-specific string helpers.

State and persistence: mutates caller buffers and may flush destination cachelines for persistence-domain users. Dependencies include jump labels, sanitizer config, fortify, persistent-memory copy support, and x86-64 string instruction semantics. Risks include sanitizer visibility, non-temporal/persistent copy ordering, and overlap handling. Test signals include lib/string, pmem/DAX copy tests, KMSAN/KASAN, fortify, and memset width-specific tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/string_64.h -->
