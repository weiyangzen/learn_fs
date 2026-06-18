# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_mtl.h

Purpose: Declares SXGBE MTL constants, threshold encodings, flow-control encodings, and the `struct sxgbe_mtl_ops` callback interface consumed by the common driver.

Important APIs and types: Defines ETS/RAA masks and encodings, TX/RX FIFO divisors, RX forwarding flags, flow-control enable bits, dynamic RX queue mapping value, flow-control threshold bit shifts, `enum ttc_control`, `enum rtc_control`, `enum flow_control_th`, and the MTL operations table with callbacks for initialization, FIFO sizing, TX queue enable/disable, threshold mode selection, dynamic RX queue mapping, flow control, and FEP/FUP toggles. `sxgbe_get_mtl_ops()` is the exported accessor.

State and dependencies: This header is a hardware contract shared by `sxgbe_mtl.c` and `sxgbe_main.c`. It depends on kernel bit macros and `__iomem` pointer usage from included call sites.

Risks and test signals: Constants must match the SXGBE hardware register layout; incorrect shifts or threshold values silently program wrong queue behavior. Build coverage should catch signature drift between the header and implementation. Runtime validation should compare programmed MMIO values against expected queue modes for all supported TX/RX thresholds and flow-control levels.
