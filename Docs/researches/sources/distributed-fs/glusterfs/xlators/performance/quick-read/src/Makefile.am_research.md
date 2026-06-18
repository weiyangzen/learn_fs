# sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/Makefile.am

Purpose: builds the `quick-read.la` performance translator module.

Important APIs, types, and functions: compiles `quick-read.c`, links `libglusterfs.la`, installs under the performance xlator directory, and lists private headers `quick-read.h`, `quick-read-mem-types.h`, and `quick-read-messages.h`.

Control flow: Automake compiles the single C implementation with Gluster include paths and links a module with `$(GF_XLATOR_DEFAULT_LDFLAGS)`.

State and persistence: build metadata only.

Dependencies and integration: depends on libglusterfs and RPC XDR include paths.

Risks and test signals: module build breaks if header or source lists drift. Compile and install packaging tests are sufficient for this file.
