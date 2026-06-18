# sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/Makefile.am

Purpose: builds the `snapview-client.la` xlator module from `snapview-client.c`.

Important declarations: installs the module under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`, uses `-module $(GF_XLATOR_DEFAULT_LDFLAGS)`, links `libglusterfs.la`, and ships private headers `snapview-client.h`, `snapview-client-mem-types.h`, and `snapview-client-messages.h`. Include paths cover libglusterfs and rpc/xdr generated/source directories.

Control flow/state: no runtime behavior; it defines compile/link inputs and warning flags.

Dependencies/integration: depends only on libglusterfs at link time. It does not link libgfapi because the client side routes fops to children rather than reading snapshots directly.

Risks/test signals: build failures would show as missing xlator symbols, missing generated XDR include paths, or mismatched private headers. Validate with configured builds and module install path checks.
