## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/Makefile

Purpose: this Makefile connects Kconfig symbols to the APM Ethernet subdirectories.

Important APIs, types, and functions: it contributes `xgene/` when `CONFIG_NET_XGENE` is enabled and `xgene-v2/` when `CONFIG_NET_XGENE_V2` is enabled.

Control flow, state, and dependencies: build state is purely Kbuild object inclusion. The file depends on matching Kconfig symbols and the existence of the two subdirectory Makefiles.

Integration points: parent kernel networking Makefiles recurse here; subdirectory Makefiles define the actual module objects.

Risks: symbol/name drift breaks module builds while leaving source code intact. Since both drivers are independent, accidental unconditional inclusion can build unsupported hardware paths.

Test signals: build `drivers/net/ethernet/apm/` with each symbol as built-in and module; verify `xgene-enet.o` and `xgene-enet-v2.o` are included only under their configured symbols.
