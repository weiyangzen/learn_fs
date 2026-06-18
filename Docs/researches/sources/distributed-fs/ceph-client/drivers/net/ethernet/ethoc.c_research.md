## sources/distributed-fs/ceph-client/drivers/net/ethernet/ethoc.c

## Purpose
Implements the OpenCores Ethernet MAC platform driver. It handles register and optional buffer-memory mapping, descriptor ring setup in MAC-accessible memory, MDIO/PHY integration, NAPI RX/TX completion, multicast filtering, ethtool register/ring controls, MAC address setup, and platform/OF probing.

## Important APIs, Types, and Functions
Key private types are `struct ethoc` and `struct ethoc_bd`. Important functions include `ethoc_probe`, `ethoc_remove`, `ethoc_open`, `ethoc_stop`, `ethoc_interrupt`, `ethoc_poll`, `ethoc_rx`, `ethoc_tx`, `ethoc_start_xmit`, `ethoc_init_ring`, `ethoc_reset`, `ethoc_mdio_read`, `ethoc_mdio_write`, `ethoc_mdio_probe`, `ethoc_set_multicast_list`, `ethoc_set_ringparam`, and ethtool/netdev ops tables.

## Control Flow and State
Probe allocates the netdev, maps MMIO and either platform-provided or coherent buffer memory, derives TX/RX descriptor counts, gets MAC address from platform/DT/register/random fallback, sets MDIO clocking, registers an MDIO bus, connects a PHY, adds NAPI, and registers the netdev. Open requests the shared IRQ, enables NAPI, initializes descriptors, resets/enables hardware, starts the queue, and starts PHY. Interrupt handling masks TX/RX events and schedules NAPI. RX copies frames from IO buffer memory into SKBs, strips CRC, updates stats, and returns descriptors to hardware. TX copies SKBs into the current TX buffer, marks descriptors ready, stops the queue when the software ring fills, and completion stats/wakeups happen in NAPI.

Persistent state includes buffer descriptor rings in device memory, software TX/RX cursors (`cur_tx`, `dty_tx`, `cur_rx`), MDIO/PHY state, endian mode, multicast hash registers, and netdev stats.

## Dependencies and Integration Points
Depends on platform resources, optional `ethoc_platform_data`, OF MAC/endian discovery, DMA coherent allocation fallback, MII/PHYLIB, NAPI, CRC32 multicast hashing, ethtool ring/register operations, and the OpenCores register/descriptor ABI.

## Risks and Test Signals
Risks include CPU-copy data path performance, fixed 1536-byte buffers with no MTU support, descriptor count assumptions requiring power-of-two TX entries, races while changing ring parameters on a running device, endian mismatches, legacy stats fields, and suspend/resume stubs returning `-ENOSYS`. Test with platform buffer and coherent-buffer modes, big- and little-endian DT, up/down, PHY link/duplex changes, ping/iperf, multicast/promisc/allmulti toggles, `ethtool -d/-g/-G`, TX timeout recovery, low-memory RX allocation failure, and MDIO timeout handling.
