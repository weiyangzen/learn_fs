# sources/distributed-fs/ceph-client/include/linux/mv643xx_eth.h

Purpose: defines platform data, register layout constants, and board configuration fields for the Marvell MV643xx Ethernet driver.

Important APIs and types: constants name the shared and port platform devices, shared register base/size, BAR and address enable registers, checksum default limit, PHY address encodings, and `MV643XX_ETH_PHY_NONE`. `struct mv643xx_eth_shared_platform_data` provides DRAM target info and optional TX checksum packet-size limit. `struct mv643xx_eth_platform_data` links a port to the shared platform device, port number, PHY address or node, override MAC address, fixed or autonegotiated speed/duplex, PHY interface mode, RX/TX queue counts and sizes, and optional SRAM descriptor regions.

Control flow: board or platform setup fills these structures before registering the shared Ethernet device and per-port devices. The driver reads shared data to program memory windows/checksum limits and per-port data to configure PHY, MAC identity, queue topology, descriptor rings, and optional SRAM-backed descriptors.

State and persistence: this header describes boot-time platform configuration. Runtime link state, descriptor state, and hardware registers live in the Ethernet driver and device.

Dependencies and integration points: depends on Marvell MBUS DRAM target info, Ethernet address constants, PHY definitions, `platform_device`, and device-tree nodes. It bridges legacy platform-data board files with the MV643xx netdev driver.

Risks and test signals: risks include invalid PHY address encoding, MAC override misuse, queue count/size mismatch with SRAM capacity, checksum limit assumptions, and stale platform-data use alongside device-tree descriptions. Test platform-data boot, multiple ports sharing registers, fixed and PHY-negotiated links, SRAM descriptor allocation, queue size overrides, and large-packet checksum behavior.
