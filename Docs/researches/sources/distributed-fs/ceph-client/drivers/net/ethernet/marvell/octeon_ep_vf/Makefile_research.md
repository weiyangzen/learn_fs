# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/Makefile

## Purpose
This Makefile builds the OCTEON endpoint VF network driver object when `CONFIG_OCTEON_EP_VF` is enabled.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_OCTEON_EP_VF) += octeon_ep_vf.o` declares the module/built-in target.
- `octeon_ep_vf-y` lists the constituent objects: `octep_vf_main.o`, `octep_vf_cn9k.o`, `octep_vf_cnxk.o`, `octep_vf_tx.o`, `octep_vf_rx.o`, `octep_vf_mbox.o`, and `octep_vf_ethtool.o`.

## Control Flow
Kbuild links all listed objects into one logical driver object. The file order places `octep_vf_main.o` first, followed by chip-specific setup, queue helpers, mailbox protocol, and ethtool support.

## State And Persistence
There is no runtime state. Build state is produced by Kbuild as object files and, when configured as a module, `octeon_ep_vf.ko`.

## Dependencies And Integration Points
The Makefile integrates the VF directory with the kernel build system. It assumes all listed source files are present and that headers in the same directory provide shared definitions.

## Risks And Edge Cases
- Adding a new source file without updating `octeon_ep_vf-y` leaves code unlinked.
- Removing or renaming any object in the list breaks the build.
- The PF/VF protocol header duplication means build success does not prove runtime compatibility with the PF module.

## Test Signals
Build `CONFIG_OCTEON_EP_VF=m` and `=y`, inspect that `octeon_ep_vf.ko` includes all listed objects, and run modpost for unresolved symbols.
