<!-- Source: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/Makefile -->
# sources/distributed-fs/ceph-client/fs/nfs/blocklayout/Makefile

## Purpose
Kbuild fragment for the pNFS block layout driver module.

## Important APIs, Types, And Functions
Adds `blocklayoutdriver.o` when `CONFIG_PNFS_BLOCK` is enabled. The composite object is built from `blocklayout.o`, `dev.o`, `extent_tree.o`, and `rpc_pipefs.o`.

## Control Flow
Build-time only. The parent NFS Makefile descends into this directory under `CONFIG_PNFS_BLOCK`, and this Makefile builds the block layout driver pieces as one module/object.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Depends on `PNFS_BLOCK` Kconfig, which itself depends on NFSv4 and device mapper support. The listed objects match the declarations in `blocklayout.h`: layout IO/registration, device resolution/registration, extent tree management, and rpc_pipefs communication.

## Risks
Missing any of the component objects breaks symbols used by `blocklayout.c`. Adding new blocklayout helpers requires updating this composite list.

## Test Signals
Build with `CONFIG_PNFS_BLOCK=y` and `m`, and verify module aliases for NFS layout types are present in the resulting object.
