# sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd.h

Purpose: shared private interface for the CTU CAN FD common driver and bus wrappers.

Important types and APIs: `struct ctucan_priv` embeds `struct can_priv`, stores the mapped register base, endian-aware register callbacks, TX buffer head/tail and priority state, NAPI context, runtime PM device/clock handles, IRQ flags, buffered first RX frame word, and PCI peer list linkage. The file declares `ctucan_probe_common()`, `ctucan_suspend()`, and `ctucan_resume()`.

Control flow and state: executable flow is implemented elsewhere, but all persistent driver state is shaped here. `ctucan_probe_common()` is designed as the bus-independent registration entry: bus drivers pass device, MMIO address, IRQ, TX buffer count, clock rate or clock lookup mode, runtime PM policy, and a driver-data callback. Dependencies include netdevice, SocketCAN, clocks, list management, and the generated register enum. Risks are concurrency and lifecycle coupling around `tx_lock`, NAPI, PM state, and `peers_on_pdev` for multi-core PCI cards. Test signals are successful common probe from both PCI and platform paths and clean suspend/resume transitions.
