# sources/distributed-fs/ceph-client/drivers/nvmem/s32g-ocotp-nvmem.c

Purpose: NXP S32G OCOTP read-only NVMEM provider with explicit keepout ranges.

Important APIs/types/functions: `struct s32g_ocotp_priv` holds device and MMIO base. `s32g_ocotp_read()` performs sequential 32-bit MMIO reads. `s32g_keepouts[]` defines inaccessible/reserved regions. Probe maps resource and registers NVMEM sized to the resource.

Control flow: probe allocates state, maps resource 0, stores private/device/size in a static NVMEM config, and registers. Reads iterate while at least one full word remains.

State/persistence: OCOTP fuses are persistent in hardware and exposed read-only. Driver state is MMIO mapping and keepout metadata.

Dependencies/integration: OF compatible `nxp,s32g2-ocotp`; uses NVMEM keepout support and legacy fixed cells.

Risks: partial trailing bytes are ignored by the read callback, relying on NVMEM word-size behavior. Keepout ranges are hard-coded and must match the SoC reference manual.

Test signals: keepout enforcement, aligned word reads, resource-size exposure, and attempts to read reserved ranges through fixed cells.
