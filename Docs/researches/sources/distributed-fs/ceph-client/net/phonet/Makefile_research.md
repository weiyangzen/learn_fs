# sources/distributed-fs/ceph-client/net/phonet/Makefile

## Purpose
The Makefile maps `CONFIG_PHONET` to Phonet object builds. It builds the core `phonet.o` aggregate and the pipe endpoint `pn_pep.o` aggregate.

## Important APIs, types, and functions
`obj-$(CONFIG_PHONET) += phonet.o pn_pep.o` includes both modules when Phonet is enabled. `phonet-y` links `pn_dev.o`, `pn_netlink.o`, `socket.o`, `datagram.o`, `sysctl.o`, and `af_phonet.o`; `pn_pep-y` links `pep.o` and `pep-gprs.o`.

## Control flow and state
There is no runtime control flow. Link composition determines which initialization functions land in each module: core protocol family/device/datagram/sysctl code in `phonet.o`, and pipe protocol plus GPRS netdev adapter in `pn_pep.o`.

## Dependencies and integration points
The file integrates Kbuild with the Kconfig symbol and reflects a module split where the core can autoload transport protocol modules through PF_PHONET protocol aliases.

## Risks and edge cases
Changing object membership can alter module load ordering and symbol availability. For example, `pep-gprs.o` depends on PEP helpers from `pep.o`, while core `af_phonet.o` calls `isi_register()` from `datagram.o`.

## Test signals
Build `CONFIG_PHONET=y` and `CONFIG_PHONET=m`, inspect linked symbols/modules, and verify module autoload aliases for PF_PHONET datagram and pipe protocols.
