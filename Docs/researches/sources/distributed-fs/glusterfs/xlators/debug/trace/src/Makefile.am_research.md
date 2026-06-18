# sources/distributed-fs/glusterfs/xlators/debug/trace/src/Makefile.am

## Purpose
Builds and installs the `trace` debug xlator module.

## Important APIs, types, and functions
`xlator_LTLIBRARIES = trace.la` declares the module, with installation under the versioned debug xlator directory. `trace_la_SOURCES = trace.c`, `noinst_HEADERS = trace.h trace-mem-types.h`, `trace_la_LIBADD` links `libglusterfs.la`, and `trace_la_LDFLAGS` uses default xlator module flags. `AM_CPPFLAGS` includes libglusterfs and generated RPC/XDR headers.

## Control flow
The automake target compiles `trace.c` with private trace headers and links a loadable debug xlator.

## State and persistence behavior
No runtime state exists in this build file. It ensures `trace-mem-types.h` is available to the implementation but not installed as a public header.

## Dependencies and integration points
Integrates with the GlusterFS xlator build system, libglusterfs, and generated RPC/XDR include paths.

## Risks and test signals
Build risks include missing private headers and generated include paths. Test with a module build and installed-file check for the versioned debug xlator path.
