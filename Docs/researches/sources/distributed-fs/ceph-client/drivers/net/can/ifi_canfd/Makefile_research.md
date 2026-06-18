# sources/distributed-fs/ceph-client/drivers/net/can/ifi_canfd/Makefile

Purpose: this Makefile wires the IFI CANFD driver source into the kernel build.

Important APIs, types, and functions: the only build rule is `obj-$(CONFIG_CAN_IFI_CANFD) += ifi_canfd.o`, so the object is included when the Kconfig symbol is built-in or modular.

Control flow: Kbuild expands the conditional object assignment during kernel build. There is no source-level runtime behavior.

State and persistence: state is entirely build configuration. The output is either no object, a built-in object, or a loadable module depending on `CONFIG_CAN_IFI_CANFD`.

Dependencies and integration points: it depends on the sibling Kconfig symbol and the `ifi_canfd.c` translation unit. It fits the standard drivers/net/can subdirectory Kbuild pattern.

Risks: because there are no composite objects or extra flags, any future source split must update this file. A mismatched Kconfig symbol would silently omit the driver from builds.

Test signals: `make M=drivers/net/can/ifi_canfd` or an equivalent tree build should compile `ifi_canfd.o` when `CONFIG_CAN_IFI_CANFD` is enabled, and module builds should emit an `ifi_canfd` module.
