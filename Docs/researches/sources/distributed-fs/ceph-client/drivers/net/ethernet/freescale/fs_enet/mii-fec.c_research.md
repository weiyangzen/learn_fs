# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mii-fec.c

## Purpose
Implements the FEC hardware MDIO bus used by `fs_enet` FEC controllers on PQ1 and MPC512x platforms.

## Important APIs, Types, and Functions
Important functions are `fs_enet_fec_mii_read`, `fs_enet_fec_mii_write`, `fs_enet_mdio_probe`, and `fs_enet_mdio_remove`. Probe creates a `mii_bus`, allocates `struct fec_info`, maps FEC registers, computes the MII clock divider from platform bus frequency or `ppc_proc_freq`, enables MII/Ethernet control bits, programs `fec_mii_speed`, and registers child PHYs. OF compatibles include `fsl,pq1-fec-mdio` and optionally `fsl,mpc5121-fec-mdio`.

## Control Flow and State
Read/write build FEC MII command words with PHY and register address, poll `FEC_ENET_MII` for up to `FEC_MII_LOOPS`, clear the event bit, and return data or timeout-like `-1` for read. Probe stores the mapped FEC pointer and calculated `mii_speed` in bus private state; the FEC MAC backend later reuses this `mii_speed` during controller restart.

## Dependencies and Integration Points
Depends on FEC register layout from `fs_enet.h`, constants from `fec.h`, OF MDIO registration, MPC5xxx bus-frequency helper when enabled, and PowerPC processor frequency fallback. It is selected by `CONFIG_FS_ENET_MDIO_FEC`.

## Risks and Test Signals
Risks include `BUG_ON` if MII mode is not enabled, write returning success even if polling timed out, divider overflow or inaccurate clock source, shared FEC registers being modified while netdev is active, and bus private assumptions by `mac-fec.c`. Test signals include PHY discovery, MDIO read/write timeout tests, MII clock measurement, FEC restart using stored speed, and MPC512x/PQ1 DT probe coverage.
