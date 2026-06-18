# sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/Makefile

Purpose: this Kbuild file defines the TSNEP module composition.

Important APIs, types, and functions: `obj-$(CONFIG_TSNEP) += tsnep.o` emits the driver object when the Kconfig symbol is enabled. `tsnep-objs` links `tsnep_main.o`, `tsnep_ethtool.o`, `tsnep_ptp.o`, `tsnep_tc.o`, `tsnep_rxnfc.o`, and `tsnep_xdp.o`. `tsnep-$(CONFIG_TSNEP_SELFTESTS)` conditionally adds `tsnep_selftests.o`.

Control flow and state: the file has build-time behavior only; no runtime state exists. Its object list shows the driver's functional split: core platform/netdev, ethtool diagnostics, PTP timestamping, traffic control/gate control, RX flow classification, XDP/AF_XDP, and optional selftests.

Dependencies and integration points: it must stay aligned with declarations in `tsnep.h` and symbols selected in `Kconfig`. Missing an object would cause link errors for exported helper references like `tsnep_ptp_init`, `tsnep_tc_setup`, `tsnep_rxnfc_*`, `tsnep_xdp_*`, or self-test hooks.

Risks: changing object ordering or conditional inclusion can break module links. Optional selftests are compiled into the main module rather than as a separate module, so self-test code must remain compatible with the same driver-private ABI.

Test signals: build `M=drivers/net/ethernet/engleder` with `CONFIG_TSNEP=m`, built-in, and with/without `CONFIG_TSNEP_SELFTESTS`; verify the resulting `tsnep` module exposes ethtool, PTP, TC, RXNFC, and XDP symbols without unresolved references.
