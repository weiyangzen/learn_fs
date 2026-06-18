# sources/distributed-fs/ceph-client/drivers/nvmem/uniphier-efuse.c

Purpose: Socionext UniPhier eFuse read-only NVMEM provider.

Important APIs/types/functions: `struct uniphier_efuse_priv` stores MMIO base. `uniphier_reg_read()` copies bytes with `readb()`. Probe maps resource, sizes from resource, and registers byte-granular read-only NVMEM with legacy fixed OF cells.

Control flow: probe allocates private state, maps resource 0, fills local `nvmem_config`, and registers. Runtime reads are simple byte loops from base plus offset.

State/persistence: eFuse data persists in hardware and is read-only. Driver keeps no cache.

Dependencies/integration: OF compatible `socionext,uniphier-efuse`; uses platform MMIO and NVMEM provider APIs.

Risks: no special locking, power, or clock control is present, so the mapped block must be always accessible. Byte loop is simple but less efficient for large reads.

Test signals: resource-size exposure, byte and multi-byte fixed-cell reads, and probe failure for missing resource.
