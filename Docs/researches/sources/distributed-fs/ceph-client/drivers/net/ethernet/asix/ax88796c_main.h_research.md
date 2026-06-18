# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_main.h

## Purpose
Defines the AX88796C driver's shared state structures, register map, bit fields, TX/RX descriptor header formats, flow-control flags, event flags, and convenience conversions used by main, ioctl, and SPI code.

## Important APIs, Types, and Functions
Important types include `struct ax88796c_device`, `struct ax88796c_pcpu_stats`, `struct skb_data`, `struct tx_pkt_info`, `struct rx_header`, and TX header substructures. Important constants define queue watermarks, register dump lengths, PHY id, multicast filter size, packet header masks, MAC/PHY/page registers, interrupt bits, checksum offload registers, SPI control bits, wake filters, and register offsets. `to_ax88796c_device()` converts a netdev private area to driver state.

## Control Flow and State
The header has no executable control flow, but it defines the state model. `ax88796c_device` persists per-interface driver state: SPI device, netdev, per-CPU stats, work item, SPI mutex, TX wait queue, MDIO bus/PHY, sequence numbers, multicast filter, link parameters, flow-control flags, compression private flags, and work event bits.

## Dependencies and Integration Points
Includes `netdevice.h`, `mii.h`, and `ax88796c_spi.h`. The register definitions are consumed by all driver components and represent the hardware ABI. The exported `ax88796c_no_regs_mask` connects main initialization with ethtool register dumping.

## Risks and Test Signals
Bitfield correctness is critical because most control paths are raw register programming. Test signals include correct TX/RX header construction, checksum offload behavior, register dump masking, and link/MAC configuration. Any kernel API changes to `netdev_priv`, per-CPU stats, or MII structures would surface through compile failures.
