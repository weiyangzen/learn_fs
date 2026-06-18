# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mac.h

Purpose: Declares Sunplus MAC/switch hardware control helpers.

Important APIs: Exports start/stop, address add/delete, full hardware initialization, RX mode programming, common MAC initialization, and soft reset. These functions form the boundary between netdev/interrupt code and raw switch register programming.

State and dependencies: Callers pass either `struct spl2sw_common` for global switch operations or `struct spl2sw_mac` for per-port MAC table/filter operations. Correctness depends on descriptors being initialized before `spl2sw_mac_hw_init()` programs base addresses.

Risks and test signals: The API assumes callers serialize lifecycle transitions with netdev state and TX locks where needed. Test build linkage across driver, interrupt, and PHY files plus runtime start/stop/reset paths.
