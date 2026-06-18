<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-hisi-femac.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-hisi-femac.c

Purpose: Hisilicon Fast Ethernet MAC MDIO controller driver exposing Clause 22 read/write callbacks.

Important APIs/types/functions: `struct hisi_femac_mdio_data` stores clock and MMIO base. Core routines are `hisi_femac_mdio_wait_ready`, `hisi_femac_mdio_read`, `hisi_femac_mdio_write`, probe, and remove.

Control flow: probe allocates mii_bus/private data, maps registers, gets/enables the clock, assigns read/write callbacks, registers with OF MDIO, and stores the bus. Reads wait for `MDIO_RW_FINISH`, write PHY/register fields, wait again, then read `MDIO_RO_DATA`. Writes wait, write command/data fields with `MDIO_WRITE`, then wait for completion.

State and persistence: runtime state is the enabled clock, MMIO registers, and bus private data. Remove unregisters bus, disables clock, and frees bus.

Dependencies/integration: depends on HAS_IOMEM, OF MDIO, clock framework, platform bus, and phylib. Compatible string is `hisilicon,hisi-femac-mdio`.

Risks and test signals: risks include clock lifecycle leaks on registration failure, timeout values, no Clause 45 support, and register field width assumptions. Tests should cover wait timeout, read/write command encoding, clock error paths, and OF PHY registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-hisi-femac.c -->
