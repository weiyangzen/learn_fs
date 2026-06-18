<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-ipq8064.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-ipq8064.c

Purpose: Qualcomm IPQ8064 Clause 22 MDIO interface driver using a regmap over NSS GMAC registers.

Important APIs/types/functions: `struct ipq8064_mdio` stores the regmap. Key routines are `ipq8064_mdio_wait_busy`, `ipq8064_mdio_read`, `ipq8064_mdio_write`, `ipq8064_mdio_probe`, and remove.

Control flow: probe maps the DT resource manually, allocates a devm mii_bus, initializes an MMIO regmap with locking disabled, assigns read/write callbacks, registers with OF MDIO, and stores the bus. Reads/writes program address/data registers with a fixed clock range, sleep briefly, and poll busy clear. Writes to register 31 delay longer to avoid subsequent bad reads.

State and persistence: runtime state is regmap/MMIO register state and bus private data. No persistent storage exists.

Dependencies/integration: depends on MFD_SYSCON/regmap-style MMIO, OF MDIO, platform bus, and phylib. Compatible string is `qcom,ipq8064-mdio`.

Risks and test signals: risks include disabled regmap locking relying on mii_bus serialization, fixed clock range, manual resource mapping, and the special register-31 delay. Tests should cover timeout, regmap failure paths, read/write command fields, and OF PHY discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-ipq8064.c -->
