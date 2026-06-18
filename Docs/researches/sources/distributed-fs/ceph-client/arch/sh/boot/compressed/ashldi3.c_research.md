# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashldi3.c



Source read size: 2 lines, 82 bytes.



Purpose: compressed-loader wrapper for the 64-bit arithmetic left-shift helper normally provided by SH libgcc/kernel support.

Important APIs/types/functions: includes `arch/sh/lib/ashldi3.c`, providing the `__ashldi3`-style helper needed by 32-bit builds that manipulate 64-bit values in early decompression code.

Control flow: the helper is compiled into the standalone compressed image and is invoked only if generated C code needs a 64-bit left shift.

State and persistence: stateless arithmetic helper text only.

Dependencies and integration points: depends on the shared SH helper implementation and compressed Kbuild object list.

Risks and test signals: wrong include path or ABI mismatch breaks the boot-loader link. Test by building 32-bit compressed kernels with decompressor algorithms using 64-bit arithmetic.
