# sources/distributed-fs/glusterfs/xlators/cluster/Makefile.am

## Purpose

This is the cluster-translator recursive Automake file. It builds the three cluster translator families: AFR replication, DHT distribution, and EC erasure coding.

## Important build variables

- `SUBDIRS = afr dht ec` defines traversal order.
- `CLEANFILES` is empty.

## Control flow and integration

Automake enters `afr`, then `dht`, then `ec`. AFR's position first is relevant because it is a core cluster translator and has its own recursive `src` build. This file has no conditionals.

## State and persistence behavior

No runtime state is involved. The file determines which cluster translator modules are built and included in recursive clean/install targets.

## Dependencies and integration points

It depends on valid child Automake files under `afr/`, `dht/`, and `ec/`. The parent `xlators/Makefile.am` reaches this file through its `SUBDIRS` list.

## Risks and edge cases

- Adding a new cluster translator requires updating this file or it will not be built.
- Removing or renaming a child directory without updating `SUBDIRS` breaks recursive Automake.
- Empty `CLEANFILES` means cleanup responsibility sits in child directories.

## Test signals

Recursive `make -C xlators/cluster`, `make install`, and `make distcheck` should traverse all three cluster translators. A packaging check should confirm each translator module is included as intended.
