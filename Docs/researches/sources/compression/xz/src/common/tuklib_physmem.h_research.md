# sources/compression/xz/src/common/tuklib_physmem.h

Purpose: declares the portable physical-memory helper used internally by liblzma and other xz components.

Important APIs/types/functions: includes `tuklib_common.h`, wraps declarations with `TUKLIB_DECLS_BEGIN/END`, maps `tuklib_physmem` through `TUKLIB_SYMBOL(tuklib_physmem)`, and declares `extern uint64_t tuklib_physmem(void)`.

Control flow: no runtime control flow. The header establishes C/C++ linkage and symbol-prefix behavior at compile time.

State and persistence: no state. The returned value and failure behavior are implemented in the `.c` file.

Dependencies/integration: depends on `tuklib_common.h` for integer types, linkage macros, and symbol prefixing. `src/liblzma/Makefile.am` compiles the `.c` file into liblzma with prefix `lzma_`, allowing `hardware_physmem.c` to wrap it without exporting raw tuklib names.

Risks: callers must treat zero as unknown/error and not as a real RAM size. Any change to symbol prefixing affects library-private ABI and the public `lzma_physmem()` wrapper.

Test signals: validated indirectly by `tests/test_hardware.c` through `lzma_physmem()` and by build/link tests that require the prefixed symbol to resolve.
