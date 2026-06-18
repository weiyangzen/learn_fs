<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-pic64hpsc.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-pic64hpsc.c

Purpose: Microchip PIC64-HPSC/HX Clause 22 MDIO controller driver.

Important APIs/types/functions: `struct pic64hpsc_mdio_dev` stores MMIO base. Core functions are `pic64hpsc_mdio_wait_trigger`, `pic64hpsc_mdio_c22_read`, `pic64hpsc_mdio_c22_write`, and probe.

Control flow: probe maps registers, obtains/enables the clock, reads optional `clock-frequency` defaulting to 2.5 MHz, computes/publishes the prescaler, assigns C22 callbacks, and registers with `devm_of_mdiobus_register`. Reads wait for idle, program frame config with trigger/read/PHY/register/SOF, wait, validate READOK unless ignored by `phy_ignore_ta_mask`, and return data. Writes wait, program write-data register, then trigger a write frame.

State and persistence: runtime state is prescaler and frame registers plus bus private data. No persistent storage exists.

Dependencies/integration: depends on ARCH_MICROCHIP or compile test, OF MDIO, HAS_IOMEM, clock framework, and phylib. Compatible string is `microchip,pic64hpsc-mdio`.

Risks and test signals: risks include prescaler range validation, READOK interpretation, write completion not re-polled after trigger, and no Clause 45 support. Tests should cover clock-frequency bounds, read timeout, ignored TA mask, and OF registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-pic64hpsc.c -->
