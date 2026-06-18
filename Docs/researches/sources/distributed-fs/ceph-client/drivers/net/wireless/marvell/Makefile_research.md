## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/Makefile

Purpose: this Makefile maps Marvell wireless Kconfig symbols to build outputs.

Important entries: `obj-$(CONFIG_LIBERTAS) += libertas/`, `obj-$(CONFIG_LIBERTAS_THINFIRM) += libertas_tf/`, `obj-$(CONFIG_MWIFIEX) += mwifiex/`, and `obj-$(CONFIG_MWL8K) += mwl8k.o`.

Control flow and integration: kbuild descends into subdirectories or compiles `mwl8k.o` based on the resolved `.config`. It is paired with `marvell/Kconfig`; each symbol must be declared there or in sourced children.

State and persistence: no runtime state. Build inclusion is determined by kernel configuration.

Risks and tests: symbol/name drift causes missing modules or dead build rules. Test signals are `make M=drivers/net/wireless/marvell`, `allmodconfig`, and verifying module names match help text.
