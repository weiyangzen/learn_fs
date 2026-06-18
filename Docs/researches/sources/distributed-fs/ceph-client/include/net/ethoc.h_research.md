# sources/distributed-fs/ceph-client/include/net/ethoc.h

Read `sources/distributed-fs/ceph-client/include/net/ethoc.h` completely for this pass (23 lines, 439 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/ethoc.h_research.md`.

Purpose: defines platform data for the OpenCores Ethernet MAC driver.

Important APIs/types/functions: `struct ethoc_platform_data` contains a hardware MAC address array `hwaddr`, signed `phy_id`, Ethernet clock frequency `eth_clkfreq`, and `big_endian` flag.

Control flow: board/platform code supplies this structure to the ethoc driver at probe. The driver uses the MAC address, PHY identifier, bus clock, and endian mode to initialize registers and PHY attachment.

State and persistence: platform data is static or firmware-derived configuration that persists for the device lifetime. The header has no runtime logic.

Dependencies and integration points: depends on `linux/if.h` and basic types. It integrates platform device registration with the ethoc network driver.

Risks: wrong endianness or clock frequency prevents register access/timing from working. Invalid `phy_id` can bind the wrong PHY or fail link setup. MAC address validation is the driver's responsibility.

Test signals: platform probe with fixed MAC/PHY/clock values, big-endian and little-endian register access, invalid/missing MAC fallback, PHY attach/link tests, and device-tree/platform-data compatibility.
