# sources/distributed-fs/ceph-client/arch/sparc/lib/NG2memcpy.S

Purpose: Niagara2 optimized memcpy engine and template for NG2 copy-to/from-user routines.

Important APIs/functions: Emits `NG2memcpy` by default, defines `__restore_fp`, `__restore_asi`, several `NG2_retl_*` residual helpers, and macro hooks for loads, stores, block operations, and store initialization.

Control flow: Validates length, handles tiny copies, aligns destination, chooses block/VIS paths for larger copies, uses store-init ASIs for cache-friendly writes, and falls back to word/byte tail loops. Wrapper files override access macros and exception behavior.

State and persistence: Stateless memory movement with transient VIS/FPU and ASI state.

Dependencies/integration: Includes `linux/linkage.h`, `asm/visasm.h`, and `asm/asi.h`; built under `CONFIG_SPARC64`; patched by `NG2patch.S`.

Risks/test signals: Complex alignment thresholds and block stores are risky. Test exact boundary lengths around 16, 64, and block thresholds, all source/destination low bits, user fault recovery, and comparison to generic memcpy.
