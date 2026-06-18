## sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftgmac100.h

## Purpose
Defines the FTGMAC100 register offsets, interrupt masks, MAC/PHY/flow-control fields, descriptor formats, checksum/VLAN bits, and error masks used by `ftgmac100.c`.

## Important APIs, Types, and Functions
Important declarations include MMIO offsets for interrupt, MAC address, hash, descriptor base, DMA arbitration, MAC control, PHY MDIO, flow control, statistics, and test-mode registers. It defines interrupt groups `FTGMAC100_INT_BAD`, `FTGMAC100_INT_RXTX`, and `FTGMAC100_INT_ALL`, MAC control flags, MDIO command/data fields, flow-control fields, aligned `struct ftgmac100_txdes` and `struct ftgmac100_rxdes`, TX descriptor size/first/last/own/checksum/VLAN bits, RX ready/first/last/error/checksum/VLAN bits, and `RXDES0_ANY_ERROR`.

## Control Flow and State
No runtime control flow exists in this header. It describes persistent hardware state in registers and DMA descriptors, including descriptor ownership, end-of-ring markers, packet size, checksum results, VLAN tag availability, multicast/broadcast status, and MAC enable/filter modes.

## Dependencies and Integration Points
Consumed by `ftgmac100.c` and tied to the FTGMAC100/Aspeed hardware ABI. The descriptor structs are shared with DMA hardware and therefore require the declared 16-byte alignment and little-endian fields.

## Risks and Test Signals
Risks are ABI-level: wrong bit positions can corrupt DMA ownership, interrupt masking, checksum offload, VLAN handling, or PHY MDIO transactions. Test signals include compile coverage, register dumps against datasheets, RX/TX descriptor traces, checksum/VLAN offload validation, interrupt error-path tests, and variant tests for Faraday versus Aspeed end-of-ring masks.
