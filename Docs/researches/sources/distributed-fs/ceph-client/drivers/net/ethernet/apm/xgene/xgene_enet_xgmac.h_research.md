## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_xgmac.h

Purpose: defines XGMAC/AXGMAC/PCS register offsets, reset/clock bits, pause/CLE/RSIF registers, MSS and link status registers, and exported XGMAC operation tables.

Important APIs, types, and functions: constants cover block offsets for X-Gene2 MAC CSR, AXG MAC/stats/CSR, PCS, XGENET config/reset/clock bits, AXGMAC configuration/address/frame length, RX gate, ECM/ICM drop counters, CLE bypass, link aggregation resume, link status, TSO MSS registers, PCS reset, and RSIF thresholds. Externs expose `xgene_xgmac_ops` and `xgene_xgport_ops`.

Control flow, state, and dependencies: included by `xgene_enet_main.c` and `xgene_enet_xgmac.c`. It carries no live state.

Integration points: main resource mapping uses these offsets to derive MAC/stats/PCS bases for XGMII; XGMAC implementation writes the listed registers during reset/init/link/flow-control paths.

Risks: offset errors affect all 10G operation. The header mixes X-Gene1 and X-Gene2 offsets, so edits must respect hardware generation differences.

Test signals: 10G probe, PCS reset, MAC address programming, link status reads, frame-size changes, pause control, and TSO MSS programming.
