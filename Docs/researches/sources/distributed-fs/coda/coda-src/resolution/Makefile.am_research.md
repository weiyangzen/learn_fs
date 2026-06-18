<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/Makefile.am -->
# sources/distributed-fs/coda/coda-src/resolution/Makefile.am

Purpose: Automake build recipe for the Coda server resolution support library. When `BUILD_SERVER` is true it builds `libres.la` as a non-installed libtool archive.

Important contents: `libres_la_SOURCES` enumerates the resolution subsystem: communication (`rescomm.*`), coordination (`rescoord.*`, `rvmrescoord.cc`), force/runt handling (`resforce.*`), lock/util/stats files, operation logs (`ops.*`, `recle.*`, `rsle.*`, `recov_vollog.cc`), conflict handlers (`ruconflict.*`, `rename.cc`, `subresphase*`, `subpreres.cc`), worker entry points (`weres.cc`), and public umbrella `resolution.h`.

Dependencies/integration: `AM_CPPFLAGS` includes RPC2/RVM flags plus Coda base, kernel dependency, util, vicedep, directory, ACL, partition, auth, version-vector, lockqueue, and volume headers. This makes resolution a server-side integration point across storage, RPC, vnode, ACL, and recovery layers.

State/persistence: no runtime state; build-time selection via `BUILD_SERVER` controls whether the library exists.

Risks/test signals: omissions in `libres_la_SOURCES` can hide source files from build and tests. Include path order matters because both source and build directories are used for generated headers. Test by regenerating with Automake/configure and building server with `BUILD_SERVER` enabled; watch for stale header prototypes across the listed sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/Makefile.am -->
