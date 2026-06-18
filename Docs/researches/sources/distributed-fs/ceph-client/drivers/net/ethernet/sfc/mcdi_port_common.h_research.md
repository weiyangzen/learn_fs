# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port_common.h

Purpose: this header defines the shared MCDI PHY data model and declares the common MCDI port/PHY/MAC helper surface used by SFC controller implementations.

Important types and APIs: `struct efx_mcdi_phy_data` stores firmware PHY flags, type, supported capabilities, channel, port, stats mask, media, MMD mask, name/revision strings, and saved forced capabilities. Declared functions cover PHY config fetch, link advertising and `SET_LINK`, loopback modes, link-mode conversion, PHY flags/media/link decode, FEC conversion, flow-control partner checks, PHY poll/probe/remove, ethtool link and FEC get/set, PHY tests and names, module EEPROM/info, MAC setup/MTU/stats lifecycle, port number lookup, and link-change event processing.

Control flow and integration: the header is consumed by `mcdi_port.c`, `mcdi_port_common.c`, and NIC type code that needs fine-grained helpers rather than only the port-level facade. It depends on `net_driver.h`, `mcdi.h`, and `mcdi_pcol.h`.

State and risks: the declared helpers expect `struct efx_nic` lifecycle invariants, especially valid `phy_data` after PHY probe and valid `stats_buffer` after MAC stats init. Adding fields to `struct efx_mcdi_phy_data` requires auditing MCDI response parsing and teardown. Test signals are compile coverage plus port probe, ethtool link/FEC operations, diagnostics, and link events.
