## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/enet.h

Purpose: declares ENET CSR offsets, reset/coherency bit values, traffic-resume registers, and the public ENET helper API for v2.

Important APIs, types, and functions: constants include `ENET_CLKEN`, `ENET_SRST`, `ENET_SHIM`, memory shutdown/readiness registers, `DEVM_ARAUX_COH`, `DEVM_AWAUX_COH`, forced link status, link aggregation resume, and RX data valid gate registers. It declares `xge_wr_csr`, `xge_rd_csr`, `xge_port_reset`, and `xge_port_init`.

Control flow, state, and dependencies: it is included by `main.h`, making ENET access available to `main.c`, `mac.c`, `ring.c`, `mdio.c`, and `ethtool.c`. It has no runtime state itself.

Integration points: its offsets must match the hardware resource mapped by `xge_get_resources`; its prototypes are implemented in `enet.c`.

Risks: incorrect register offsets affect reset, DMA coherency, and traffic gating globally. The include guard comment has a typo but does not affect compilation.

Test signals: compile all v2 objects, then validate reset and traffic resume by observing successful probe and packet I/O.
