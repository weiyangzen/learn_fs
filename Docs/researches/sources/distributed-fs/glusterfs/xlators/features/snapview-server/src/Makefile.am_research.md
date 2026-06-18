# sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/Makefile.am

Purpose: builds the `snapview-server.la` xlator module when `WITH_SERVER` is enabled.

Important declarations: sources are `snapview-server.c`, `snapview-server-mgmt.c`, and `snapview-server-helpers.c`. The module links `libglusterfs.la`, `libgfapi.la`, readline libs, `libgfxdr.la`, and `libgfrpc.la`. Include paths cover libglusterfs, api, rpc-lib, rpc/xdr source and build directories. `DATADIR` is defined from `$(localstatedir)` for snapshot log paths.

Control flow/state: build-only file; the conditional protects server-only builds.

Dependencies/integration: integration point for libgfapi and management RPC dependencies used by the implementation.

Risks/test signals: missing `WITH_SERVER`, XDR, gfapi, or rpc libs will break module build. Tests should cover server-enabled and server-disabled configure paths and installed xlator location.
