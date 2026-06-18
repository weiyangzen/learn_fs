# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port.c

Purpose: this file is the thin MCDI-backed port facade for SFC NICs. It connects the generic NIC type `probe_port`, `remove_port`, PHY capability, and MAC fault hooks to the common MCDI PHY/MAC implementation in `mcdi_port_common.c`.

Important APIs: `efx_mcdi_phy_get_caps()` returns `efx->phy_data->supported_cap`; `efx_mcdi_mac_check_fault()` issues `MC_CMD_GET_LINK` and reports any RPC failure as a MAC fault; `efx_mcdi_port_probe()` calls `efx_mcdi_phy_probe()` then `efx_mcdi_mac_init_stats()`; `efx_mcdi_port_remove()` tears down PHY data and MAC stats.

Control flow: probe first populates PHY data, loopback modes, link state, FEC, and flow-control defaults through the common helper. Only after that does it allocate the DMA statistics buffer. Remove performs the inverse, clearing `efx->phy_data` and freeing the stats buffer. MAC fault checking is synchronous and intentionally conservative: failed firmware communication returns `true`.

State and dependencies: all state lives on `struct efx_nic`, especially `phy_data`, `link_state`, `loopback_modes`, and `stats_buffer`. The file depends on `mcdi.h`, `mcdi_pcol.h`, `mcdi_port_common.h`, `nic.h`, and `selftest.h`.

Risks and tests: initialization ordering matters because other ethtool and link paths assume `phy_data` is valid after port probe. Test signals include probe/remove smoke tests, simulated `GET_LINK` failures, ethtool link capability reads, and MAC stats allocation/free leak checks.
