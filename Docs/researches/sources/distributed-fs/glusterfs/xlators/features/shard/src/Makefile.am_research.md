# sources/distributed-fs/glusterfs/xlators/features/shard/src/Makefile.am

## Purpose
This Automake file builds the shard feature translator module.

## Important APIs and build outputs
It builds `shard.la` unconditionally as an xlator module under the versioned GlusterFS feature xlator directory. The only implementation source listed is `shard.c`; private headers are `shard.h`, `shard-mem-types.h`, and `shard-messages.h`. It links against `libglusterfs.la` and uses `GF_XLATOR_DEFAULT_LDFLAGS`.

## Dependencies and integration
The module inherits GlusterFS CPP/C flags and includes libglusterfs plus RPC XDR source/build include directories. It integrates shard into the normal module install layout.

## Risks and test signals
Unlike the SELinux module, there is no `WITH_SERVER` guard here, so build environments must always be able to compile shard. Adding new source files requires updating `shard_la_SOURCES`. Build tests should confirm the module links and installs to the feature xlator path.
