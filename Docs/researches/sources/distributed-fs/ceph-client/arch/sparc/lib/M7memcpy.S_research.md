# sources/distributed-fs/ceph-client/arch/sparc/lib/M7memcpy.S

Purpose: High-performance SPARC M7 memory copy implementation and template for M7 user-copy variants.

Important APIs/functions: Emits `M7memcpy` unless overridden by wrappers. Macro hooks include `LOAD`, `STORE`, `STORE_INIT`, `STORE_INIT_MRU`, `EX_LD`, `EX_ST`, `EX_RETVAL`, and `PREAMBLE`.

Control flow: The function checks length sanity, handles alignment, then uses M7-specific VIS and block-init store strategies for large copies. It has dedicated paths for destination alignment, source alignment, medium sizes, small/tail copies, and cleanup labels such as `.Lexit_cp`. User-copy variants replace memory access and exception behavior through macro definitions.

State and persistence: Stateless data movement. It relies on temporary integer registers, VIS/FPU state, memory barriers, and `%asi` when specialized.

Dependencies/integration: Includes `asm/visasm.h` and `asm/asi.h`, relies on `Memcpy_utils.S` residual helpers, and is activated by `M7patch.S`.

Risks/test signals: This is performance-critical and architecture-sensitive. Test with randomized overlap-free buffers, cacheline/page-boundary alignments, large block sizes, user-copy fault injection, VIS state preservation, and comparisons against generic memcpy.
