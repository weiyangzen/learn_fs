# sources/distributed-fs/ceph-client/drivers/net/usb/Kconfig

Purpose: Defines build-time configuration for USB networking drivers. It gates the USB network adapter menu on `USB && NET`, defines the shared `USB_USBNET` framework, exposes many vendor/class minidrivers, and declares dependency/select relationships for the ASIX and Aquantia drivers researched in this group.

Important options: `USB_NET_DRIVERS` is the enclosing tristate menu. `USB_USBNET` enables the common usbnet framework. `USB_NET_AX8817X` selects the ASIX AX88xxx USB 2.0 driver, depends on `USB_USBNET`, selects `CRC32`, `PHYLINK`, and `AX88796B_PHY`, implies `NET_SELFTESTS`, and defaults to `y`. `USB_NET_AQC111` selects Aquantia AQtion USB to 5/2.5GbE controller support, depends on `USB_USBNET`, and selects `CRC32`. The file also defines surrounding drivers such as CATC, Pegasus, RTL815x, LAN78xx, CDC Ethernet/NCM/MBIM, QMI WWAN, SMSC, SR9700/SR9800, and RTL8153 ECM fallback.

Control flow: Kconfig has no runtime execution; it controls which objects kbuild will compile as built-in, module, or not at all. Dependency clauses prevent driver selection without required core infrastructure, while `select` clauses pull in helper libraries and PHY/phylink support that the C files assume are present. Help text documents user-facing device support and module names.

State and persistence: The file contributes persistent kernel build configuration only. Resulting `.config` symbols determine whether `asix.o`, `aqc111.o`, `usbnet.o`, and other objects are linked into vmlinux or emitted as modules.

Dependencies and integration: Integrated with the adjacent USB net Makefile, the USB core, networking stack, `drivers/net/usb/usbnet.c`, PHYLIB/PHYLINK, CRC helpers, and class-specific CDC/RNDIS/WWAN dependencies. For this subset, `USB_NET_AX8817X` maps to `asix_devices.o`, `asix_common.o`, and `ax88172a.o`; `USB_NET_AQC111` maps to `aqc111.o`.

Risks and test signals: Risks are stale dependency expressions, missing selected symbols for code paths added in drivers, default-y surprises on small builds, and invalid built-in/module combinations around PHYLINK or usbnet. Test by building `USB_NET_DRIVERS=n`, `USB_USBNET=m/y`, `USB_NET_AX8817X=m/y`, `USB_NET_AQC111=m/y`, and combinations with `NET_SELFTESTS`, PHYLINK, and CRC32. Confirm module names, modpost dependencies, and that ASIX/AQC111 cannot be enabled without `USB_USBNET`.
