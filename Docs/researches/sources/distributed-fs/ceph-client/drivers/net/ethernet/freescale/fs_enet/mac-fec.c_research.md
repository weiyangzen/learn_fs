# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mac-fec.c

## Purpose
Implements the FEC backend for `fs_enet` on CPM1 and MPC512x-style Fast Ethernet controllers. It programs FEC registers, descriptor rings, multicast filters, MII/RMII mode, and interrupt control via `fs_fec_ops`.

## Important APIs, Types, and Functions
The exported object is `const struct fs_ops fs_fec_ops`. Important functions include `whack_reset`, `do_pd_setup`, `setup_data`, `allocate_bd`, `restart`, `stop`, `set_multicast_list`, NAPI event helpers, `rx_bd_done`, `tx_kickstart`, `get_int_events`, `clear_int_events`, and `get_regs`.

## Control Flow and State
Setup maps the FEC register resource and IRQ, initializes multicast hash cache, and sets FEC event masks. Restart resets the controller, writes station and multicast hash registers, configures max receive size, Rx/Tx descriptor base addresses, DMA/endian function code, MII speed from the associated MDIO bus private `fec_info`, interrupt vector/control mode, duplex, multicast/promiscuous state, interrupt mask, Ethernet enable, and Rx descriptor activation. Stop performs graceful transmit stop with timeout, masks interrupts, disables Ethernet, and cleans descriptors.

## Dependencies and Integration Points
Depends on `fec.h`, optional MPC5121 register layout from `fs_enet.h`, OF IRQ/mapping APIs, common descriptor helpers, and a FEC MDIO bus whose `mii_bus->priv` contains `struct fec_info`. It is selected by `fs_enet-main.c` for FEC-compatible DT nodes.

## Risks and Test Signals
Risks include assuming `dev->phydev->mdio.bus->priv` is FEC-specific, reset timeout, FEC/MPC5121 register layout divergence, multicast hash calculation errors, MII/RMII mode mistakes, and DMA coherent ring lifetime. Test signals include FEC link-up on MII/RMII, MDIO-backed MII speed programming, multicast/allmulti/promisc behavior, RX/TX interrupts and descriptor activation, graceful stop warnings, and ethtool register reads.
