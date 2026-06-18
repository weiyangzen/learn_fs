# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port.h

Purpose: this header declares the port-level MCDI entry points used by NIC type tables and driver core code. It intentionally hides the larger PHY/MAC helper surface in `mcdi_port_common.h` behind a compact port interface.

Important API: it declares `efx_mcdi_phy_get_caps()`, `efx_mcdi_mac_check_fault()`, `efx_mcdi_port_probe()`, and `efx_mcdi_port_remove()`. These functions operate on `struct efx_nic` and are backed by the MCDI management-controller protocol.

Control flow and integration: controller-specific NIC type instances can wire these functions into `struct efx_nic_type` callbacks. Probe and remove become lifecycle hooks; capability and fault methods become ethtool/link-monitor support. The only dependency is `net_driver.h` for the core NIC type.

State and risks: the header owns no state, but callers must obey lifecycle assumptions: `efx_mcdi_phy_get_caps()` requires `efx->phy_data` to have been populated by probe, and `remove` should only run after probe or a partial-probe cleanup path that is prepared for common helper teardown. Test signals are compile coverage of NIC type tables and probe/remove paths.
