## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/Makefile

Purpose: this Makefile assembles Libertas common and bus-specific modules.

Important entries: the `libertas-y` composite includes `cfg.o`, `cmd.o`, `cmdresp.o`, `debugfs.o`, `ethtool.o`, `main.o`, `rx.o`, `tx.o`, and `firmware.o`, with `mesh.o` added under `CONFIG_LIBERTAS_MESH`. Bus composites are `usb8xxx-objs += if_usb.o`, `libertas_cs-objs += if_cs.o`, `libertas_sdio-objs += if_sdio.o`, and `libertas_spi-objs += if_spi.o`. Final `obj-*` rules build the core and selected bus modules.

Control flow and integration: kbuild links shared core code into `libertas.o`; bus modules depend on exported core functions and register actual hardware transports.

State and persistence: no runtime state. The build graph determines which objects exist.

Risks and tests: missing common objects would surface as unresolved symbols in bus modules. Mesh conditionality must match C preprocessor guards. Test signals are per-symbol module builds and checking that selected frontends can link against `libertas.o`.
