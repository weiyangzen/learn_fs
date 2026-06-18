# sources/distributed-fs/glusterfs/xlators/features/index/src/Makefile.am

## Purpose
Builds the server-side `index.la` feature translator module.

## Important APIs, Types, and Functions
Declares `index_la_SOURCES = index.c`, private headers (`index.h`, `index-mem-types.h`, `index-messages.h`), links against `libglusterfs.la`, and installs under the GlusterFS feature xlator directory when `WITH_SERVER` is set.

## Control Flow
Automake conditionally builds the module only for server builds. Compiler flags include libglusterfs and RPC/XDR include paths.

## State and Persistence
No runtime state; it describes build artifacts only.

## Dependencies and Integration Points
Integrates with GlusterFS module loading through `-module` xlator flags and `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`.

## Risks and Edge Cases
Missing XDR or libglusterfs include paths would break compilation. Since only `index.c` is compiled, helper logic must stay in that file or be added here if split later.

## Test Signals
Server build should generate `index.la` and include all private headers in distribution checks.
