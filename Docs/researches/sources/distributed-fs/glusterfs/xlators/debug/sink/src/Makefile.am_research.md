# sources/distributed-fs/glusterfs/xlators/debug/sink/src/Makefile.am

## Purpose
Builds and installs the `sink` debug xlator module.

## Important APIs, types, and functions
`xlator_LTLIBRARIES = sink.la` declares the module and `xlatordir` installs it under the versioned debug xlator directory. `sink_la_SOURCES = sink.c`, `sink_la_LIBADD` links `libglusterfs.la`, `sink_la_LDFLAGS` uses default xlator module flags, and `AM_CPPFLAGS` adds libglusterfs and generated RPC/XDR include paths.

## Control flow
The build compiles `sink.c`, links a loadable module, and installs it for graph loading.

## State and persistence behavior
No runtime state is stored by this build file.

## Dependencies and integration points
Integrates with GlusterFS libtool module conventions and libglusterfs. There are no private headers.

## Risks and test signals
The sink translator is small, so build coverage is the main signal: successful compilation and module installation with the expected debug xlator path.
