<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/Makefile.am

## Purpose
Top-level Automake manifest for feature translators under GlusterFS `xlators/features`.

## APIs, Types, and Functions
Defines conditional directory variables for `cloudsync` and `metadisp`, then lists feature subdirectories in `SUBDIRS`: locks, quota, read-only, quiesce, marker, index, barrier, arbiter, upcall, compress, changelog, gfid-access, snapview, trash, shard, bit-rot, leases, selinux, sdfs, namespace, thin-arbiter, utime, simple-quota, and optional directories. `CLEANFILES` is empty.

## Control Flow, State, and Persistence
Automake traverses `SUBDIRS` in order during build, install, clean, and dist operations. There is no runtime state.

## Dependencies and Integration
Integrated by the GlusterFS build system and configure-time flags `BUILD_CLOUDSYNC` and `BUILD_METADISP`. Child `Makefile.am` files define each translator module.

## Risks and Test Signals
Risks are build omissions, conditional directory mismatch with configure output, or ordering problems if one translator depends on another generated artifact. Test signals are `make`, `make install`, and distribution builds with optional flags both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/Makefile.am -->
