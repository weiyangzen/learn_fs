# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-xtalk.c

Purpose: IP27 Crosstalk/Xtalk probing and Bridge platform-device creation. It discovers Bridge/XBridge widgets on each node and creates companion 1-Wire NIC and PCI bridge platform devices.

Important APIs and control flow: `bridge_platform_create()` allocates `sgi_w1` and `xtalk-bridge` platform devices, builds NIC/MMIO/IO resources, copies platform data, and unwinds on errors. `probe_one_port()` reads widget ID and creates Bridge devices for recognized Bridge/XBridge part numbers. `xbow_probe()` finds KL XBow data, elects the master HUB widget, and probes enabled I/O ports only on the owning NASID. `xtalk_probe_node()` checks the HUB LLP link, reads widget 0, then handles direct Bridge or XBow/XXBow. `xtalk_init()` runs for each online node at arch init.

State, persistence, and integration: state is platform-device registration and bridge resources per widget/NASID. Dependencies include KL config, HUB raw widget address macros, Bridge platform driver, and SGI 1-Wire driver. Risks include volatile raw widget reads, partial device creation on memory pressure, master-widget election assumptions, and no removal path. Test signals are `xtalk:n/w bridge widget` logs, PCI bridge enumeration, and NIC 1-Wire device creation.
