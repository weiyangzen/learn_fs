# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-xtalk.c

Purpose: IP30 XIO/Crosstalk widget probing. It discovers active XBow links and registers Bridge/XBridge PCI bridge and 1-Wire NIC platform devices.

Important APIs and control flow: `bridge_platform_create()` creates `sgi_w1` and `xtalk-bridge` platform devices with resources based on the widget's small-window address and HEART interrupt address. `xbow_widget_active()` reads XBow link status. `xtalk_init_widget()` reads widget ID and creates bridge devices for Bridge/XBridge parts. `ip30_xtalk_init()` walks widgets from BaseIO downward so BaseIO IOC3 becomes `eth0`.

State, persistence, and integration: state is platform-device registration and bridge platform data. Dependencies include fixed IP30 XBow/HEART widget IDs, Bridge platform driver, SGI 1-Wire driver, and raw XIO MMIO. Risks include direct reads from inactive widgets if link status is wrong, partial registration cleanup complexity, and hard-coded ordering to preserve network naming. Test signals are xtalk bridge logs, PCI bridge discovery, BaseIO IOC3 as eth0, and bridge NIC IDs.
