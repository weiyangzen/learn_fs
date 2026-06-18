## sources/distributed-fs/glusterfs/rpc/rpc-lib/Makefile.am

Purpose: this Automake file delegates the RPC library build into the `src` subdirectory.

Important APIs and build contract: `SUBDIRS = src` is the whole file. It ensures the actual `libgfrpc.la` build recipe in `rpc/rpc-lib/src/Makefile.am` is included in recursive Automake operations.

Control flow: build, install, clean, and dist phases recurse into `src`.

State and persistence: no runtime state. It controls build traversal only.

Dependencies and integration: connects the top-level `rpc/Makefile.am` to core RPC library sources and headers. It is intentionally minimal.

Risks: deleting or changing this breaks recursive build discovery for `libgfrpc`.

Test signals: successful recursive Automake traversal into `rpc/rpc-lib/src`.
