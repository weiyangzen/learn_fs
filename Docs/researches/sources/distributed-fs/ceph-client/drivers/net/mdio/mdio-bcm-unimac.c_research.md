<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bcm-unimac.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bcm-unimac.c

Purpose: Broadcom UniMAC MDIO bus controller for GENET MACs and Broadcom switch blocks, supporting Clause 22 transactions with optional platform-data wait callbacks.

Important APIs/types/functions: `struct unimac_mdio_priv` holds mii_bus, base, wait function/data, optional clock, and requested bus frequency. Key callbacks are `unimac_mdio_read`, `unimac_mdio_write`, `unimac_mdio_reset`, `unimac_mdio_clk_set`, probe/remove, and resume.

Control flow: probe maps an integrated register range, chooses platform-data or default polling behavior, obtains optional clock, sets bus callbacks, programs optional clock-frequency, and registers via OF MDIO. Each transaction enables the clock, writes command fields, starts hardware, waits, handles read-fail/turnaround masking, and disables the clock. Reset performs dummy BMSR reads on visible PHYs to work around integrated PHY first-transaction failures.

State and persistence: runtime state is the bus object, clock enable state, register configuration, and PHY ignore-turnaround masks inherited from OF. No storage persists beyond driver lifetime.

Dependencies/integration: depends on Broadcom platform data (`mdio-bcm-unimac.h`), clocks, OF MDIO, phylib, and endian-aware MMIO access for MIPS big-endian systems.

Risks and test signals: risks include clock-frequency divisor overflow, platform-data wait callbacks, read-fail handling with broken TA devices, and reset scans touching unintended PHYs. Tests should include platform and OF modes, clock gating, dummy-read workaround, suspend/resume, and broken TA masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bcm-unimac.c -->
