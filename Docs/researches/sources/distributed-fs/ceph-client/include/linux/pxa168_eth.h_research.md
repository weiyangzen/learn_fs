# sources/distributed-fs/ceph-client/include/linux/pxa168_eth.h

Purpose: defines platform data for the Marvell/PXA168 Ethernet driver.

Important APIs and types: `struct pxa168_eth_platform_data` carries port number, PHY address, optional fixed speed and duplex, PHY interface mode, optional RX/TX queue sizes, and a board-specific init callback.

Control flow: board code provides platform data; the Ethernet driver uses it to select port/PHY/interface, choose autonegotiation or fixed link settings, size queues, and run board initialization such as PHY transceiver setup.

State and persistence: platform data is static boot-time configuration. Link state, queues, and PHY state are runtime driver/hardware state.

Dependencies and integration points: depends on PHY constants and the PXA168 Ethernet platform driver. Integrates board files with network device initialization.

Risks and test signals: risks include invalid PHY address, mismatched fixed speed/duplex, wrong interface mode, queue size extremes, and init callback failures. Test autonegotiated and fixed-link modes, PHY init, queue sizing, and platform remove/error paths.
