# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/Makefile

Purpose: this Makefile wires the Intel Ethernet Adaptive Virtual Function driver into the kernel build. It builds the composite `iavf.o` object when `CONFIG_IAVF` is enabled.

Important build APIs: it adds `$(src)` to both `ccflags-y` and `subdir-ccflags-y`, then defines `iavf-y` as `iavf_main.o`, `iavf_ethtool.o`, `iavf_virtchnl.o`, `iavf_fdir.o`, `iavf_adv_rss.o`, `iavf_txrx.o`, `iavf_common.o`, and `iavf_adminq.o`. It conditionally adds `iavf_ptp.o` when `CONFIG_PTP_1588_CLOCK` is set.

Control flow and dependencies: build selection starts from Kconfig via `obj-$(CONFIG_IAVF) += iavf.o`; kbuild then links the listed objects into the driver. The file establishes that admin queue, common AQ helpers, virtchnl, Tx/Rx, ethtool, Flow Director, and advanced RSS are always part of the iavf module, while PTP is optional.

State and persistence: no runtime state is defined here, but the object list determines which features are compiled and therefore which symbols must remain consistent across source files.

Risks and test signals: missing objects cause unresolved symbols or feature absence; stale include paths can hide header dependency issues. Test signals are `CONFIG_IAVF=m/y` builds with and without `CONFIG_PTP_1588_CLOCK`, plus modpost symbol checks.
