# sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/Makefile

## Purpose
This Kbuild file defines the object composition of the Microsoft Azure Network Adapter driver module.

## Important APIs, Types, and Data
- `obj-$(CONFIG_MICROSOFT_MANA) += mana.o` builds the composite driver object.
- `mana-objs` is composed from `gdma_main.o`, `shm_channel.o`, `hw_channel.o`, `mana_en.o`, `mana_ethtool.o`, and `mana_bpf.o`.

## Control Flow
Kbuild links the listed objects into `mana.o` when the MANA config is enabled. For module builds, `mana.o` becomes `mana.ko`; for built-in builds, it is linked into vmlinux.

## State and Persistence
No runtime state. The file defines build-time object membership.

## Dependencies and Integration Points
- Connects the GDMA core, shared-memory channel, hardware command channel, Ethernet data path, ethtool support, and BPF/XDP support into one driver.
- Relies on symbols shared across the MANA sources and public headers under `include/net/mana/`.

## Risks and Edge Cases
- Omitting an object causes unresolved symbols or missing feature registration.
- Object order can matter for init/exit section placement and symbol availability during final link, though no custom ordering is expressed here beyond the list.

## Test Signals
- A successful `CONFIG_MICROSOFT_MANA=m` build should link all six objects into `mana.ko`.
- Feature-level tests for ethtool and XDP indirectly confirm that optional-looking objects are included.
