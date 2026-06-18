<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena.c

## Purpose
Provides hardware control for the SFC9000/Siena NIC family and publishes `siena_a0_nic_type`, the callback table that connects the common driver to Siena-specific probe, reset, MCDI, stats, RX/TX/event/filter, WoL, PTP, MTD, self-test, and optional SR-IOV behavior.

## Important APIs, Types, And Functions
- Exported type object: `const struct efx_nic_type siena_a0_nic_type`.
- Lifecycle: `siena_probe_nic()`, `siena_init_nic()`, `siena_remove_nic()`, `siena_dimension_resources()`.
- Reset/test: `siena_map_reset_flags()`, `siena_test_chip()`, `efx_siena_prepare_flush()`, `siena_finish_flush()`.
- RSS/statistics: `siena_rx_push_rss_config()`, `siena_rx_pull_rss_config()`, `siena_try_update_nic_stats()`, `siena_update_nic_stats()`, `siena_describe_nic_stats()`.
- Control plane: `siena_mcdi_request()`, `siena_mcdi_poll_response()`, `siena_mcdi_read_response()`, `siena_mcdi_poll_reboot()`.
- Feature hooks: `siena_mac_reconfigure()`, `siena_get_wol()`, `siena_set_wol()`, `siena_init_wol()`, `siena_ptp_set_ts_config()`.

## Control Flow
Probe allocates `struct siena_nic_data`, rejects FPGA builds, initializes MCDI, resets the NIC, initializes WoL, allocates `irq_status`, reads board/NVRAM config, probes monitoring, optionally probes SR-IOV, and defers PTP setup. NIC init handles firmware assertions, programs TX/RX hardware registers, pushes RSS config, enables event logging, routes flush events, disables user events until SR-IOV enables them, and calls farch common init. Removal tears down monitoring, buffers, resets/detaches MCDI, and frees private data.

## State And Persistence Behavior
Runtime state lives under `efx` and `struct siena_nic_data`: timer quantum, port number, WoL filter id, IRQ status buffer, DMA stats, and optional SR-IOV backing data. Statistics are read from a DMA buffer using generation start/end fields and then copied into local cumulative software counters. WoL filter state persists in firmware/NVRAM-facing management controller state and is synchronized during initialization.

## Dependencies And Integration Points
Integrates with farch register access, MCDI protocol helpers, MCDI port/common/MTD/PTP helpers, RX common, filters, IRQ/event paths, ethtool stats and resets, PCI WoL, and optional `CONFIG_SFC_SIENA_SRIOV` hooks. The `siena_a0_nic_type` table is the main integration point consumed by generic probe/netdev code.

## Risks And Test Signals
Failure paths must unwind MCDI, IRQ buffers, monitor probe, and private state in the right order. Stats reads can race DMA updates and rely on generation retry loops. MCDI shared-memory polling must treat all-ones as reset. Test signals include successful probe/reset, RSS hash/indir updates, ethtool stats consistency, WoL enable/disable behavior across suspend, MCDI reboot detection, offline chip register tests, and SR-IOV hook availability when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena.c -->
