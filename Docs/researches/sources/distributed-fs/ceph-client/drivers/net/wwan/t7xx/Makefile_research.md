# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/Makefile

Purpose: defines the object composition for the MediaTek/Intel t7xx WWAN PCIe modem driver module.

Important build behavior: `obj-${CONFIG_MTK_T7XX} := mtk_t7xx.o` builds a single composite module when the Kconfig symbol is enabled. The module links PCIe probing, PCIe MAC, MHCCIF, state monitor, modem ops, CLDMA, CLDMA HIF, port proxy/control, WWAN port, DPMAIF HIF/TX/RX, DPMAIF register layer, and t7xx netdev support. `t7xx_port_trace.o` is added only under `CONFIG_WWAN_DEBUGFS`.

Control flow and state: this file has no runtime state, but it determines which translation units are compiled into the single driver. That ordering captures the intended layering: bus and modem lifecycle, control path, port layer, data path, and netdev layer.

Dependencies and integration points: depends on kernel kbuild syntax and the `CONFIG_MTK_T7XX`/`CONFIG_WWAN_DEBUGFS` configuration symbols. It integrates every t7xx file in this research subset with neighboring files not individually researched here, such as `t7xx_hif_dpmaif_tx.c`, `t7xx_netdev.c`, and `t7xx_port_proxy.c`.

Risks and test signals: build omissions are the primary risk. Test with `CONFIG_MTK_T7XX=m/y`, with and without `CONFIG_WWAN_DEBUGFS`, and ensure all referenced object files compile and link into `mtk_t7xx`.
