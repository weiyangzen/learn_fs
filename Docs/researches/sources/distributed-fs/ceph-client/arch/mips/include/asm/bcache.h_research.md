<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bcache.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bcache.h

**Purpose:** Abstracts board-level secondary/cache controller operations for older MIPS systems.

**Important APIs/types/functions:** `struct bcache_ops` contains enable, disable, writeback-invalidate, invalidate, and prefetch operations. Inline wrappers call `bcops` under `CONFIG_BOARD_SCACHE`; otherwise they compile to no-ops.

**Control flow:** Runtime board cache users call wrappers that dispatch through `bcops` only when board cache support exists.

**State, dependencies, integration:** `bcops` is global platform state; `indy_sc_init()` initializes SGI Indy secondary cache support. ARC PROM I/O disables board cache through this API.

**Risks and test signals:** Null `bcops` under enabled config would crash; missing disable around firmware calls can corrupt IO. Test board-cache configs and no-op configs, plus prefetch optional callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bcache.h -->
