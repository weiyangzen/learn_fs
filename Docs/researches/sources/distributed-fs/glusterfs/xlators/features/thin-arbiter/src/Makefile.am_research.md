# sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/Makefile.am

Purpose: builds the `thin-arbiter.la` translator module.

Important declarations: enables `subdir-objects`, installs into the GlusterFS feature xlator directory, compiles `thin-arbiter.c` plus shared `xlators/lib/src/libxlator.c`, links `libglusterfs.la`, and declares noinst headers including thin-arbiter headers and `libxlator.h`. Include paths cover libglusterfs, xlators/lib, rpc-lib, and rpc/xdr source/build dirs.

Control flow/state: no runtime behavior; build configuration only.

Dependencies/integration: links the shared libxlator implementation directly and depends on RPC/libglusterfs headers used by thin-arbiter code outside this subset.

Risks/test signals: path drift in `top_builddir` references can break out-of-tree builds. Validate with Automake build, module install path, and clean/dist targets.
