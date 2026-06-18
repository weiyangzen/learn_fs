<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/string.h

Purpose: declares/selects optimized LoongArch string and memory routines.
Important APIs and types: wires architecture implementations of functions such as `memcpy`, `memmove`, `memset`, `strlen`, and related helpers when configured, falling back to generic routines otherwise.
Control flow: callers use normal C library-like APIs; the header controls whether architecture assembly/C implementations are visible.
State and persistence: no persistent state; routines modify caller buffers only.
Dependencies and integration: integrated with generic lib/string code, boot code, uaccess-adjacent memory copies, and compiler builtins.
Risks and test signals: wrong prototypes or overlap semantics cause broad memory corruption. Signals include lib/string selftests, KASAN/KMSAN, boot, and filesystem/network copy stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/string.h -->
