# sources/distributed-fs/glusterfs/xlators/cluster/afr/Makefile.am

## Purpose

This file is the AFR translator directory handoff. It delegates all AFR build work to `src/`, where the `afr.la` translator module and private headers are defined.

## Important build variables

- `SUBDIRS = src` makes `xlators/cluster/afr/src/Makefile.am` authoritative for compilation and installation.
- `CLEANFILES` is empty.

## Control flow and integration

The parent cluster Makefile enters `afr/`, and this file immediately recurses into `src/`. There are no conditionals or distributed extra files here.

## State and persistence behavior

No runtime state is managed. Build state is delegated to the generated Makefile in `src/`.

## Dependencies and integration points

The only dependency is the `src` child directory. The integration point is the recursive Automake traversal from `xlators/cluster/Makefile.am`.

## Risks and edge cases

This file is intentionally minimal. The main risk is accidentally placing build definitions in `afr/` instead of `afr/src/`, which would not affect compilation unless this file is expanded.

## Test signals

`make -C xlators/cluster/afr` should recurse into `src` and produce the same result as building `xlators/cluster/afr/src` through the normal tree.
