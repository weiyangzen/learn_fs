# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/Makefile

Purpose: Kbuild file for the LAN966x switch driver.

Important behavior: builds `lan966x-switch.o` when `CONFIG_LAN966X_SWITCH` is enabled. The composite object contains main switch lifecycle, phylink, port, MAC, ethtool/stats, switchdev, VLAN, FDB/MDB, PTP, FDMA, LAG, TC, MQPRIO, TAPRIO/TBF/CBS/ETS, matchall police/mirror, XDP, VCAP implementation/API, flower, and goto support. DCB and debugfs VCAP sources are conditionally appended. Include paths for shared Microchip `vcap` and `fdma` headers are added with `ccflags-y`.

Control flow and state: no runtime state. It defines object composition and include-path contracts for the driver.

Dependencies and integration points: integrates local files with shared `drivers/net/ethernet/microchip/vcap` and `fdma` directories. Conditional lines must match Kconfig symbols and the no-op stubs in `lan966x_main.h`.

Risks and test signals: missing objects cause unresolved symbols across the tightly coupled modules. Include path changes affect VCAP/FDMA users. Test with `CONFIG_LAN966X_DCB` and `CONFIG_DEBUG_FS` enabled/disabled, and confirm the composite object links.
