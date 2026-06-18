## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/main.h

Purpose: shared v2 driver header that imports kernel dependencies and defines resource, statistics, descriptor ring, packet metadata, and private device state structures.

Important APIs, types, and functions: `XGENE_ENET_STD_MTU`, `XGENE_ENET_MIN_FRAME`, and `IRQ_ID_SIZE` set common limits. `struct xge_resource` holds the mapped CSR base, PHY mode, and IRQ. `struct xge_stats` accumulates software TX/RX packets, bytes, and RX errors. `struct xge_pkt_info` records an SKB, DMA address, and optional coherent TX packet buffer. `struct xge_desc_ring` stores netdev pointer, coherent descriptor memory, DMA base, packet metadata array, and head/tail indexes. `struct xge_pdata` holds platform/netdev pointers, resources, TX/RX rings, NAPI, IRQ name, stats, buffer count, and current PHY speed.

Control flow, state, and dependencies: all v2 C files include this header, so it is the shared ABI between probe, ring setup, MAC, ENET reset, MDIO, and ethtool code. Runtime state is owned by `xge_pdata` and ring structures allocated in `main.c`.

Integration points: includes Linux ACPI, platform, OF, PHY, DMA/I/O, VLAN, NAPI, and networking headers, then local `mac.h`, `enet.h`, `ring.h`, and `ethtool.h`.

Risks: broad includes can hide missing direct dependencies in individual C files. The private data is small and assumes one TX ring, one RX ring, and one IRQ; extending queues requires structural changes.

Test signals: compile every v2 object; runtime checks should confirm head/tail ring state, stats accumulation, and PHY speed persistence across link changes.
