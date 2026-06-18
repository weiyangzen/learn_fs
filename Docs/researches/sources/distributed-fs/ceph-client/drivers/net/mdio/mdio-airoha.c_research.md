<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-airoha.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-airoha.c

Purpose: platform MDIO controller driver for the Airoha AN7583 SoC, supporting Clause 22 and Clause 45 transactions through a syscon regmap register.

Important APIs/types/functions: `struct airoha_mdio_data` stores base register offset, parent regmap, clock, and reset control. Read/write callbacks are `airoha_mdio_read`, `airoha_mdio_write`, `airoha_mdio_cl45_read`, and `airoha_mdio_cl45_write`; probe is `airoha_mdio_probe`.

Control flow: probe reads the MMIO offset from `reg`, obtains the parent syscon regmap, enables clock/reset, programs optional `clock-frequency`, fills `mii_bus` callbacks, and registers with `devm_of_mdiobus_register`. Transactions compose AN7583 command fields, write the busy bit, poll for completion, and read/write data. Clause 45 reads/writes issue an address phase before data phase.

State and persistence: runtime state is in `mii_bus->priv`, clock/reset hardware state, and SoC MDIO register fields. A read-specific reset workaround clears stale data caused by a documented hardware bug.

Dependencies/integration: depends on OF MDIO, regmap/syscon, clocks, resets, and phylib. Compatible string is `airoha,an7583-mdio`.

Risks and test signals: risks include reset side effects on concurrent users, wrong `reg` offset, unsupported clock rates, and timeout handling. Tests should cover C22/C45 address/data phases, absent PHY stale-data workaround, clock-frequency programming, and registration cleanup on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-airoha.c -->
