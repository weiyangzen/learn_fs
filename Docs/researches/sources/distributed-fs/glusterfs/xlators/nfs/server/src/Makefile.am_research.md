# sources/distributed-fs/glusterfs/xlators/nfs/server/src/Makefile.am

## Purpose
Builds the GlusterFS NFS server translator module `server.la` and declares its source, header, include, link, and distribution settings.

## APIs, Types, and Functions
When `WITH_SERVER` is enabled, `xlator_LTLIBRARIES = server.la`. `server_la_SOURCES` includes NFS core, common helpers, FOPs, inode handling, generic helpers, MOUNTv3, NFSv3 file handles and helpers, NLM, callback services, ACLv3, netgroups, exports, mount authorization, and auth cache sources. `server_la_LIBADD` links libglusterfs, libgfapi, gfrpc, and gfxdr. `noinst_HEADERS` lists internal headers, and `EXTRA_DIST` ships `nfsserver.sym`.

## Control Flow, State, and Persistence
There is no runtime control flow. At build time, libtool creates a module with `-module`, exports symbols constrained by `nfsserver.sym`, and installs it under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/nfs`. Preprocessor flags define `LIBDIR` for auth modules and `DATADIR` for runtime data paths.

## Dependencies and Integration
Depends on the GlusterFS core library, gfapi, RPC library, XDR library, generated RPC/XDR headers, `CONTRIBDIR` rbtree headers, and configure variables such as `GF_CPPFLAGS`, `GF_CFLAGS`, and `GF_XLATOR_LDFLAGS`. It integrates the NFS translator into Gluster's loadable xlator plugin layout.

## Risks and Test Signals
Risks include source list drift when adding/removing NFS server files, missing headers in distribution tarballs, symbol export mismatches, and conditional server builds accidentally disabling NFS artifacts. Test signals are `WITH_SERVER` and non-`WITH_SERVER` build variants, module load tests, symbol checks against `nfsserver.sym`, and link failures catching missing library dependencies.
