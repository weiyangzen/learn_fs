# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/Makefile



Source read size: 57 lines, 1708 bytes.



Purpose: builds the self-extracting SH compressed kernel loader and binary payload object.

Important APIs/types/functions: object list `head_32.o`, `misc.o`, `piggy.o`, compiler libgcc helper wrappers, `IMAGE_OFFSET`, `LDFLAGS_vmlinux`, compression-specific `*_with_size` rules, and binary `piggy.o` linker conversion.

Control flow: computes the loader link address differently for 32-bit and 64-bit SH, links the startup/decompressor/libgcc stubs at `startup`, objcopies to binary, compresses with the selected algorithm, and links the compressed payload through `vmlinux.scr` as `piggy.o`.

State and persistence: produces build artifacts only; it removes mcount profiling and branch profiling to keep the loader minimal.

Dependencies and integration points: depends on kernel linker script, Kbuild compression helpers, `CONFIG_MEMORY_START`, `CONFIG_BOOT_LINK_OFFSET`, `CONFIG_PAGE_OFFSET`, and helper routines included from `arch/sh/lib` and `lib/` decompressors.

Risks and test signals: address arithmetic, profiling instrumentation, or missing helper stubs can break early boot before diagnostics. Test each compression format and inspect that `.empty_zero_page` is removed from the compressed image.
