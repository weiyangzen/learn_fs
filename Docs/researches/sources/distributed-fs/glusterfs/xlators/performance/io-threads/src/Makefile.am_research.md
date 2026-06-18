# sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/Makefile.am

## Purpose
Builds the `io-threads` performance translator as a loadable GlusterFS module.

## Important APIs, types, and functions
`xlator_LTLIBRARIES = io-threads.la` declares the plugin. `io_threads_la_SOURCES = io-threads.c` compiles the implementation. `noinst_HEADERS` tracks `io-threads.h`, `iot-mem-types.h`, and `io-threads-messages.h`. `io_threads_la_LIBADD` links `libglusterfs.la`.

## Control flow
Autotools compiles `io-threads.c`, links it with default xlator flags, and installs it under the performance xlator directory.

## State and persistence behavior
No runtime state is stored. The file fixes the module identity and include/link dependencies.

## Dependencies and integration points
Depends on libglusterfs, generated RPC/XDR include directories, and the xlator loader's expected module location.

## Risks and test signals
Risks include missing the `xlator_api` implementation at link/load time or mismatched install names. Test signals include successful build, installed `.so`, and runtime loading of `performance/io-threads`.
