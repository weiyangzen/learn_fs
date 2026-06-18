# sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/Makefile.am

Purpose: builds the `open-behind.la` performance translator module.

Important APIs, types, and functions: compiles `open-behind.c`, links `libglusterfs.la`, installs to the performance xlator directory, and lists private headers `open-behind-mem-types.h` and `open-behind-messages.h`.

Control flow: Automake compiles the single source with Gluster include paths and `-Wall`, then links as a loadable xlator module.

State and persistence: build metadata only.

Dependencies and integration: depends on `libglusterfs/src`, RPC XDR include paths, and Gluster xlator linker flags.

Risks and test signals: source/header list drift would break packaging or module build. Validation should include module compilation and install path checks.
