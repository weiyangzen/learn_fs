# sources/distributed-fs/ceph-client/drivers/net/can/ifi_canfd/Kconfig

Purpose: this Kconfig entry exposes the IFI CAN_FD soft-IP SocketCAN driver as `CONFIG_CAN_IFI_CANFD`.

Important APIs, types, and functions: the entry is `tristate "IFI CAN_FD IP"` and depends on `HAS_IOMEM`. Its help text describes an I/F/I CAN_FD soft IP block attached through the Linux platform bus, typically synthesized into FPGA or CPLD logic.

Control flow: the file contributes configuration metadata only. When selected as built-in or module, it enables compilation of the matching object through the directory Makefile.

State and persistence: there is no runtime state. Persistent behavior is the kernel build configuration symbol.

Dependencies and integration points: `HAS_IOMEM` ensures MMIO accessor support, matching the driver's use of `devm_platform_ioremap_resource()` and `readl()/writel()`. The symbol is consumed by `ifi_canfd/Makefile`.

Risks: Kconfig does not express dependencies on OF or platform bus support even though the driver probes through OF-compatible platform devices; builds without useful platform instantiation may compile but never bind.

Test signals: `CONFIG_CAN_IFI_CANFD=m` should produce `ifi_canfd.ko`, `=y` should link the object built-in, and disabling `HAS_IOMEM` should hide or reject the symbol.
