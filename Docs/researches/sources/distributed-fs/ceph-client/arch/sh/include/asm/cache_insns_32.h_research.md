# sources/distributed-fs/ceph-client/arch/sh/include/asm/cache_insns_32.h



Source read size: 22 lines, 642 bytes.



Purpose: inline SH cache instructions.

Important APIs/types/functions: `__icbi`, `__ocbp`, `__ocbi`, `__ocbwb`, `register_align()`.

Control flow: emits cache block invalidate/purge/writeback instructions or fallback barrier.

State and persistence: mutates cache state for addressed lines.

Dependencies and integration points: cache flush, boot relocation, control barriers.

Risks and test signals: wrong instruction on unsupported CPU faults. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
