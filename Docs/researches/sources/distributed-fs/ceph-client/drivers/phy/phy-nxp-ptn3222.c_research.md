# sources/distributed-fs/ceph-client/drivers/phy/phy-nxp-ptn3222.c

This I2C driver models the NXP PTN3222 eUSB2 redriver as a generic PHY. Its state is `struct ptn3222`, containing the I2C client, created PHY, optional reset GPIO, and two bulk regulators.

Probe allocates state, requests optional `reset` GPIO initially high, gets constant regulator descriptors for `vdd3v3` and `vdd1v8` with load hints, creates a PHY bound to the device node, stores private data, and registers `of_phy_simple_xlate`. `ptn3222_init()` enables both supplies and deasserts reset by driving the GPIO low. `ptn3222_exit()` asserts reset high and disables regulators.

There is no register access despite the I2C transport; the chip is controlled through supplies and reset only. Dependencies are I2C core, GPIO consumer API, regulators, and generic PHY. Integration is with eUSB2 PHY/controller users that need a redriver brought up in sequence. Risks include no delay between regulator enable and reset release, no cleanup of regulators if reset GPIO operation were to fail, no runtime PM, and a probe error message that prints an uninitialized `ret` when `devm_phy_create()` fails. Test signals are limited to resource acquisition and board-level USB behavior.
