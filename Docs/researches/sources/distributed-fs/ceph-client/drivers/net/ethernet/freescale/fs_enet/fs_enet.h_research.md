# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/fs_enet.h

## Purpose
Defines the shared `fs_enet` driver contract: backend operation table, platform/private state, buffer sizing, descriptor access macros, optional MPC5121 FEC register layout, and exported common descriptor helpers.

## Important APIs, Types, and Functions
Key types are `struct fs_ops`, `struct fs_platform_info`, `struct fs_enet_private`, optional `struct fec`/`struct fec_info`, and backend-specific private unions for FEC/FCC/SCC. It defines packet buffer constants (`PKT_MAXBUF_SIZE`, `PKT_MAXBLR_SIZE`, `ENET_RX_FRSIZE`), descriptor read/write macros (`CBDW_*`, `CBDR_*`, `CBDS_SC`, `CBDC_SC`), and extern backends `fs_fec_ops`, `fs_fcc_ops`, and `fs_scc_ops`.

## Control Flow and State
There is no standalone runtime control flow. The state model centers on `fs_enet_private`: locks, NAPI, netdev, phylink, ring memory, SKB arrays, current/dirty descriptor pointers, event masks, and backend-specific mapped registers/parameter RAM.

## Dependencies and Integration Points
Includes kernel netdev, PHY/phylink, DMA, CPM headers, and platform-specific CPM1/CPM2 declarations. It ties `fs_enet-main.c` to `mac-fec.c`, `mac-fcc.c`, `mac-scc.c`, and `mii-fec.c`.

## Risks and Test Signals
Risks include layout mismatches for MPC5121 FEC, endian/accessor mistakes for CPM descriptors, ring size/private allocation coupling, and backend unions being used with the wrong `fs_ops`. Test signals include build coverage across CPM1/CPM2/MPC512x, descriptor ring wrap under traffic, phylink state changes, ethtool register snapshots, and DMA debugging.
