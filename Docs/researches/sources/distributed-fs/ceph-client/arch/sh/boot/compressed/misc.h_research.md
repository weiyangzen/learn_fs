# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/misc.h



Source read size: 9 lines, 183 bytes.



Purpose: local declarations shared by compressed-loader assembly/C code.

Important APIs/types/functions: declares `decompress_kernel()`, `ftrace_stub()`, and `arch_ftrace_ops_list_func()`.

Control flow: no runtime flow; it provides prototypes so the loader links cleanly when generic linker scripts or instrumentation references ftrace symbols.

State and persistence: none.

Dependencies and integration points: used by `misc.c` and the compressed boot link; shields the early loader from full kernel headers.

Risks and test signals: missing prototypes or ftrace stubs can cause early boot link failures. Test by building compressed kernels with and without ftrace/profile options.
