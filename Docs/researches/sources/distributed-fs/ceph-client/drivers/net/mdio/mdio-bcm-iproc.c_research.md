<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bcm-iproc.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bcm-iproc.c

Purpose: Broadcom iProc Clause 22 MDIO bus controller driver.

Important APIs/types/functions: `struct iproc_mdio_priv` stores the mii_bus and MMIO base. Core functions are `iproc_mdio_wait_for_idle`, `iproc_mdio_config_clk`, `iproc_mdio_read`, `iproc_mdio_write`, `iproc_mdio_probe`, `iproc_mdio_remove`, and resume clock restore.

Control flow: probe allocates private state and a bus, maps registers, assigns C22 callbacks, configures MDC divisor/preamble, registers with OF MDIO, and stores platform data. Reads/writes wait for idle, write an encoded MII data command with start, opcode, PHY, register, TA, and data fields, wait again, and return data or status. Resume reprograms clock configuration.

State and persistence: state is volatile in hardware registers and allocated bus/private structures. Remove unregisters and frees the bus.

Dependencies/integration: depends on Broadcom iProc architecture or compile test, OF MDIO, HAS_IOMEM, platform bus, and phylib.

Risks and test signals: risks include one-second busy-loop timeout, no Clause 45 support, clock divisor assumptions, and bus ID collisions for platform IDs. Tests should cover busy timeout, resume register restore, read/write encoding, and OF child PHY registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bcm-iproc.c -->
