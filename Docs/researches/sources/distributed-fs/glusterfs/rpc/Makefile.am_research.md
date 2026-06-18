## sources/distributed-fs/glusterfs/rpc/Makefile.am

Purpose: this Automake file declares the top-level RPC subdirectories built by GlusterFS: `xdr`, `rpc-lib`, and `rpc-transport`.

Important APIs and build contract: `SUBDIRS = xdr rpc-lib rpc-transport` is the only content. It establishes build traversal order for generated/compiled XDR code, the core RPC library, and transport plugins.

Control flow: Automake recursively descends into each subdirectory during build, install, clean, and distribution targets.

State and persistence: no runtime state. Build output state is created under the listed subdirectories by their own makefiles.

Dependencies and integration: this file integrates the RPC subtree into the repository-wide build. `rpc-lib` depends on XDR outputs and transport headers/plugins, so removing or reordering subdirectories can break compilation or install layout.

Risks: small but high-impact. Missing `xdr` would break generated protocol types, missing `rpc-lib` would remove `libgfrpc`, and missing `rpc-transport` would prevent dynamic transports from being built.

Test signals: `make`/`make distcheck` should visit all three subdirectories and produce expected libraries and installed headers.
