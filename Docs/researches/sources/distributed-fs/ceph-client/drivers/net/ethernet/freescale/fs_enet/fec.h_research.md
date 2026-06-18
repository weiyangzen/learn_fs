# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/fec.h

## Purpose
Defines Fast Ethernet Controller event and control bit masks shared by the `fs_enet` FEC MAC backend and FEC MDIO driver.

## Important APIs, Types, and Functions
Constants cover interrupt events (`FEC_ENET_*`), Ethernet control bits (`FEC_ECNTRL_*`), receive control bits including MII/RMII/promiscuous/duplex controls, transmit control bits including full duplex and graceful stop, `FEC_MAX_MULTICAST_ADDRS`, and `FEC_RESET_DELAY`.

## Control Flow and State
There is no runtime control flow. The macros describe persistent FEC hardware register state and event bits consumed by register read-modify-write code.

## Dependencies and Integration Points
Included by `mac-fec.c` and `mii-fec.c`, and indirectly complements the `struct fec` register layout conditionally declared in `fs_enet.h`.

## Risks and Test Signals
Risks are incorrect bit masks causing missed interrupts, wrong duplex/RMII setup, failed MII operations, or broken reset sequencing. Test signals include FEC link-up in MII and RMII modes, multicast/promiscuous filtering, graceful stop, FEC MDIO reads/writes, and event mask behavior under RX/TX traffic.
