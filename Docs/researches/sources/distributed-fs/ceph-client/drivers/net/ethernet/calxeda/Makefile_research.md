# sources/distributed-fs/ceph-client/drivers/net/ethernet/calxeda/Makefile

## Purpose
This Makefile maps `CONFIG_NET_CALXEDA_XGMAC` to the Calxeda XGMAC object file.

## Important build rule
`obj-$(CONFIG_NET_CALXEDA_XGMAC) += xgmac.o` builds the XGMAC driver as built-in, module, or not at all according to the Kconfig tristate.

## Control flow, state, dependencies, and tests
There is no runtime control flow or persisted state. The file integrates with kbuild and relies on the sibling Kconfig symbol. The main risk is object-name drift from the implementation file. Test by compiling with `NET_CALXEDA_XGMAC=y` and `NET_CALXEDA_XGMAC=m`.
