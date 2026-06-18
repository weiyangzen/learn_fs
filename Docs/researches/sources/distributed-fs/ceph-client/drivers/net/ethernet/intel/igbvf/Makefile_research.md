# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/Makefile

## Purpose
This Makefile builds the Intel 82576/I350 Virtual Function Ethernet driver when `CONFIG_IGBVF` is enabled.

## Important APIs, Types, And Functions
It declares `obj-$(CONFIG_IGBVF) += igbvf.o` and composes the module from `vf.o`, `mbx.o`, `ethtool.o`, and `netdev.o`.

## Control Flow
Kbuild includes this file from the parent driver tree. If the kernel configuration enables `IGBVF`, the listed objects are linked into `igbvf.o`; otherwise no module object is emitted.

## State And Persistence
No runtime state is stored here. The only persistent behavior is the object composition contract used by Kbuild.

## Dependencies And Integration Points
The object list defines the main integration boundaries: VF hardware operation setup (`vf.o`), PF/VF mailbox transport (`mbx.o`), ethtool support (`ethtool.o`), and the PCI/netdev driver (`netdev.o`).

## Risks
Missing an object from the list would produce link failures or silently omit driver features. Adding new source files in this directory requires updating this Makefile.

## Test Signals
Build coverage with `CONFIG_IGBVF=m` and `CONFIG_IGBVF=y` should produce `igbvf.ko` or built-in driver objects without unresolved symbols.
