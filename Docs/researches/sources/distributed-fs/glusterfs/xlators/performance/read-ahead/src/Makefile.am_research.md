# sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/Makefile.am

Purpose: builds the `read-ahead.la` performance translator module.

Important APIs, types, and functions: compiles `read-ahead.c` and `page.c`, links `libglusterfs.la`, installs under the performance xlator directory, and lists private headers `read-ahead.h`, `read-ahead-mem-types.h`, and `read-ahead-messages.h`.

Control flow: Automake compiles the two implementation files with Gluster and RPC XDR include paths, applies `-Wall`, and links a loadable module with standard xlator flags.

State and persistence: build metadata only; runtime read-ahead state lives in the C files referenced here, not in this Makefile.

Dependencies and integration: depends on libglusterfs, generated/source XDR include paths, and the consistency of source/header lists with the read-ahead implementation.

Risks and test signals: missing either `read-ahead.c` or `page.c` would break translator functionality at link time. Build validation should confirm module compilation, install path, and distribution inclusion of private headers.
