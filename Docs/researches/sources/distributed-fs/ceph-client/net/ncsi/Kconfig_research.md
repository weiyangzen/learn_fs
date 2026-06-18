# sources/distributed-fs/ceph-client/net/ncsi/Kconfig

## Purpose
This Kconfig file exposes build-time options for Linux NCSI support and optional vendor OEM commands. NCSI is used by systems where a host network controller communicates with a management controller over the Network Controller Sideband Interface.

## APIs, Types, and Functions
The symbols are `NET_NCSI`, `NCSI_OEM_CMD_GET_MAC`, and `NCSI_OEM_CMD_KEEP_PHY`. `NET_NCSI` is a boolean depending on `INET`. The two OEM options depend on `NET_NCSI`; one enables retrieving MAC addresses from NCSI firmware and applying them to the controller, and the other enables Intel keep-PHY-link behavior during host load.

## Control Flow
There is no runtime control flow here. The selected symbols determine whether the NCSI object files are built and whether conditional branches in `ncsi-manage.c` issue OEM Get MAC Address or Keep PHY commands during probe/configuration.

## State and Persistence
The file contributes static kernel configuration state. Once built, these booleans shape compiled code paths and cannot change at runtime.

## Dependencies and Integration
`NET_NCSI` integrates with the networking stack and Ethernet drivers that explicitly register an NCSI device through the public NCSI API. The OEM symbols gate code paths using vendor IDs and command payload definitions from `internal.h`.

## Risks
Because NCSI is board/platform specific, enabling it without driver support has no useful effect. Enabling OEM commands on unsupported firmware should degrade through command failure paths, but vendor payload format mistakes can affect MAC assignment or PHY reset behavior.

## Test Signals
Build matrix coverage should include `NET_NCSI=n`, `NET_NCSI=y` without OEM options, and each OEM option enabled. Runtime signals are successful NCSI probing, MAC assignment when Get MAC is enabled, and absence of undesired PHY resets when Keep PHY is enabled.
