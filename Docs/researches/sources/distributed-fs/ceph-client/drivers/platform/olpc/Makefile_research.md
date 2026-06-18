# sources/distributed-fs/ceph-client/drivers/platform/olpc/Makefile

Purpose: Build mapping for OLPC platform drivers.

Important APIs, types, and functions: `obj-$(CONFIG_OLPC_EC) += olpc-ec.o` builds the generic EC command/regulator/debugfs layer; `obj-$(CONFIG_OLPC_XO175_EC) += olpc-xo175-ec.o` builds the XO-1.75 SPI transport and platform integration.

Control flow: kbuild includes each object according to Kconfig symbols. Since `OLPC_XO175_EC` selects `OLPC_EC`, the transport normally links with the generic EC service.

State and persistence: no runtime state; build state follows `.config`.

Dependencies and integration points: integrates Kconfig symbols with kbuild and the broader `drivers/platform` build.

Risks: module/built-in combinations must leave the generic EC layer available before the transport registers the platform device. If future transports select `OLPC_EC`, object ordering and symbol export assumptions should be reviewed.

Test signals: inspect `make V=1 drivers/platform/olpc/` for expected object inclusion under `CONFIG_OLPC_EC=y/m` and `CONFIG_OLPC_XO175_EC=y/m`.
