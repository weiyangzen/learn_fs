# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashlsi3.S



Source read size: 2 lines, 75 bytes.



Purpose: tiny compressed-loader wrapper that includes the SH assembly helper `ashlsi3` from `arch/sh/lib` so the standalone decompressor can satisfy compiler-generated shift operations.

Important APIs/types/functions: the included helper provides the runtime symbol normally supplied by `arch/sh/lib/ashlsi3.S`; this wrapper exports no additional code of its own.

Control flow: Kbuild compiles the wrapper into the compressed image; any decompressor C code that emits the corresponding shift helper call resolves to the included assembly routine.

State and persistence: no local state; only executable helper text is linked into the transient boot loader.

Dependencies and integration points: depends on the relative include path to `arch/sh/lib`, the compressed loader object list, and compiler code-generation for arithmetic shifts.

Risks and test signals: missing helper inclusion causes link failures or early decompressor crashes on helper calls. Test by building compressed kernels with compiler options that emit libgcc-style shifts.
