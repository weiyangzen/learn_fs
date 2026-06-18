## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/enet.c

Purpose: provides basic CSR access, ENET block reset, memory/ECC readiness polling, coherency configuration, and initial port bring-up for the v2 driver.

Important APIs, types, and functions: `xge_wr_csr` and `xge_rd_csr` wrap `iowrite32`/`ioread32` against `pdata->resources.base_addr`. `xge_port_reset` enables ENET clocks, asserts/deasserts reset, toggles memory shutdown, polls `BLOCK_MEM_RDY` until `MEM_RDY`, then configures coherent read/write auxiliary bits in `ENET_SHIM`. `xge_port_init` sets default speed to `SPEED_1000`, initializes the MAC, and resumes traffic.

Control flow, state, and persistence: `main.c` calls `xge_init_hw`, which calls `xge_port_reset` and `xge_port_init` during probe before MDIO setup and registration. The reset path updates hardware state only; persistent driver state is `pdata->phy_speed`, later adjusted by PHY link callbacks in `mdio.c`.

Dependencies and integration points: depends on register constants in `enet.h`, MAC setup in `mac.c`, platform resource mapping in `main.c`, and Linux delay/MMIO APIs.

Risks: the readiness loop has a small fixed retry count; slow hardware initialization will fail probe with `-ETIMEDOUT`. The code assumes a single MMIO base and coherent DMA support; wrong resource mapping or missing coherency bits can cause descriptor corruption.

Test signals: probe logs should not show "ECC init failed"; `ip link set up` should receive and transmit after `xge_port_init`; fault injection around `BLOCK_MEM_RDY` should produce deterministic `-ETIMEDOUT`.
