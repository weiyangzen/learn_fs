# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/Makefile

Purpose: Defines the object composition of the Ionic Ethernet driver.

Important APIs/types/functions: Builds `ionic.o` from bus, devlink, device, debugfs, LIF, RX filter, ethtool, TX/RX, stats, firmware, and auxiliary-bus objects. `ionic-$(CONFIG_PTP_1588_CLOCK) += ionic_phc.o` adds PHC/PTP support only when enabled.

Control flow: Kbuild links all listed objects into one built-in or module target selected by `CONFIG_IONIC`.

State and dependencies: Encodes module-level integration boundaries. Files in this subset depend on objects outside it (`ionic_main.o`, `ionic_lif.o`, `ionic_stats.o`, `ionic_txrx.o`, `ionic_phc.o`) for adminq waits, LIF lifecycle, statistics, datapath, and timestamping.

Risks and test signals: Missing an object here causes link failures or absent features. Test both PTP enabled and disabled builds, and module load/unload to verify init/exit references across objects.
