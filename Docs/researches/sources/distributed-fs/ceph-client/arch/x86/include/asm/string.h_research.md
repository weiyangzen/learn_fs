<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/string.h

Purpose: selects x86 optimized string/memory operation declarations for 32-bit or 64-bit builds. It includes `string_32.h` or `string_64.h` and supplies architecture `memcpy/memset/memmove` feature markers.

Control flow: generic libc-like kernel callers resolve to x86 optimized routines or sanitizer-safe fallbacks depending on config. State is only caller-provided memory. Dependencies include architecture string assembly, KMSAN/KASAN/fortify constraints, and compiler builtins.

Risks include sanitizer bypass, overlap semantics for memmove, and ABI conflicts with compiler intrinsics. Test signals include lib/string tests, KASAN/KMSAN builds, fortify tests, boot-time memory operations, and 32/64-bit build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/string.h -->
