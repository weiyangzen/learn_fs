# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-ethtool.c

Purpose: Implements XLGMAC ethtool operations for driver info, debug message level, channel counts, interrupt coalescing, and hardware/stat counters.

Important APIs/functions: `xlgmac_get_ethtool_ops()` returns the static ops table. Driver info reports driver/version/bus and decoded hardware version tuple. Coalesce get/set maps RX usecs to DMA RIWT using `hw_ops->usec_to_riwt()`, validates RX/TX frame limits, stores new values, and calls hardware coalesce config. Stats support uses `xlgmac_gstring_stats[]` offsets into `struct xlgmac_pdata.stats`; `get_ethtool_stats()` refreshes MMC counters then copies u64 values.

Control flow and state: Ettool setters mutate `pdata->rx_riwt`, `rx_usecs`, `rx_frames`, and `tx_frames`, which directly affect RX descriptor interrupt bits and DMA RIWT. Stats are accumulated in software from reset-on-read MMC registers plus software events such as TSO packets and NAPI scheduling.

Dependencies and integration points: Consumes `struct xlgmac_hw_ops`, MMC read implementation in `dwc-xlgmac-hw.c`, stats layout in `dwc-xlgmac.h`, and standard ethtool/netdev APIs.

Risks and test signals: `supported_coalesce_params` advertises max-frames generally, but TX usecs are not configurable and `xlgmac_config_tx_coalesce()` is a no-op. Stats offsets depend on exact struct layout and u64 alignment. Test invalid coalesce bounds, live coalesce changes under traffic, ethtool stats after MMC overflow/interrupts, channel reporting with different hardware queue counts, and debug message level changes.
