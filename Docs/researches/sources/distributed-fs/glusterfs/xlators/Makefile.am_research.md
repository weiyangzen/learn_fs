# sources/distributed-fs/glusterfs/xlators/Makefile.am

## Purpose

This Automake file is the top-level build entry point for GlusterFS translators under `xlators/`. It defines which translator families are always traversed and conditionally includes the legacy GNFS translator directory when `BUILD_GNFS` is enabled.

## Important build variables

- `GNFS_DIR = nfs` is set only inside `if BUILD_GNFS`.
- `DIST_SUBDIRS` lists all distributable translator families, including `nfs` unconditionally so release tarballs contain it.
- `SUBDIRS` lists build traversal order: `cluster`, `storage`, `protocol`, `performance`, `debug`, `features`, `mount`, conditional `${GNFS_DIR}`, `mgmt`, `system`, `playground`, and `meta`.
- `EXTRA_DIST = xlator.sym` distributes the translator symbol file.
- `CLEANFILES` is empty.

## Control flow and integration

Automake evaluates `BUILD_GNFS` at configure time. When disabled, `nfs` remains in the distribution set but is not built. `cluster` is first in `SUBDIRS`, so cluster translators such as AFR are built before later translator families that may depend on shared installed headers or conventions.

## State and persistence behavior

The file only controls generated Makefile state. It does not persist runtime data, but it affects installed translator availability and source distribution completeness.

## Dependencies and integration points

This file depends on the configure-time `BUILD_GNFS` conditional and the existence of child `Makefile.am` files in every listed subdirectory. It integrates with recursive Automake from the repository root and with `xlator.sym` packaging.

## Risks and edge cases

- A directory in `SUBDIRS` without a generated Makefile breaks recursive builds.
- Omitting a directory from `DIST_SUBDIRS` can create incomplete release tarballs even if local builds pass.
- Conditional GNFS inclusion means NFS-related build failures can be hidden in default builds where `BUILD_GNFS` is off.

## Test signals

Run `autoreconf`/configure with GNFS both enabled and disabled, then run `make -C xlators` and `make distcheck` or equivalent distribution checks. Verify that `xlator.sym` is present in source archives.
