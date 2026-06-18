<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_nic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_nic.c

## Purpose
Implements the EF100 NIC-type backend below the Linux netdevice layer: MCDI transport, firmware capability and design-parameter discovery, event queue processing, interrupts, PHY/filter/MAC/reset handling, statistics, MAE/representor initialization, client ID lookup, and PF/VF `struct efx_nic_type` operation tables.

## Important APIs, Types, And Functions
- MCDI transport: `ef100_mcdi_request()`, `ef100_mcdi_poll_response()`, `ef100_mcdi_read_response()`, `ef100_mcdi_poll_reboot()`.
- Capability and design parsing: `efx_ef100_init_datapath_caps()`, `ef100_check_design_params()`, `ef100_tlv_feed()`, `ef100_process_design_param()`, `ef100_check_caps()`.
- Runtime datapath hooks: `ef100_ev_probe()`, `ef100_ev_init()`, `ef100_ev_process()`, `ef100_ev_read_ack()`, `ef100_msi_interrupt()`, `ef100_filter_table_up()`, `ef100_filter_table_down()`, `ef100_reconfigure_mac()`, `ef100_reset()`.
- Probe/remove: `ef100_probe_main()`, `ef100_probe_netdev_pf()`, `ef100_probe_vf()`, `ef100_remove()`.
- Exported NIC types: `ef100_pf_nic_type` and `ef100_vf_nic_type`.

## Control Flow
`ef100_probe_main()` allocates `ef100_nic_data`, initializes default TSO design limits, reads TLV design parameters from MMIO, allocates an aligned MCDI DMA buffer, samples warm-boot count with retry, cancels stale requests, initializes MCDI, resets the function, enables logging, reads PF index/port/firmware version/privilege mask, rejects old firmware and unsolicited-event-credit firmware, then returns to the PCI/netdev layers. Event processing uses a per-channel phase bit, reads qwords until phase mismatch or quota, dispatches RX events to EF100 RX code, MCDI events to common MCDI, TX completions to EF100 TX code, and driver events to logging. PF netdev probe conditionally initializes TC, base/own mports, MAE, representor enumeration, and hardware TC feature flags.

## State And Persistence
`struct ef100_nic_data` stores MCDI buffer, datapath capability masks, PF index, warm boot count, port ID, event queue phase bitmap, statistics cache, base/own mports, local MAE interface, MAE privilege flag, and TSO limits derived from hardware design parameters. Statistics are cached in memory and refreshed from firmware DMA stats. Firmware allocations and MCDI state are runtime-only and cleaned by `ef100_remove()`.

## Dependencies And Integration Points
Depends on EF100 registers, common SFC lifecycle/channel helpers, MCDI protocol/functions/filters/port code, EF100 RX/TX files, SR-IOV, netdev bridge, TC/MAE, selftest, and RX common code. Its `efx_nic_type` tables are consumed by the PCI driver and common SFC core.

## Risks And Edge Cases
Design-parameter parsing rejects unsupported queue granularity, oversized TLVs, unknown compatibility bits, and truncated TLV streams. Firmware version `< 1.1.0.1000` and unsolicited-event credits are explicitly rejected. MCDI doorbell word order is unusual. `ef100_mcdi_reboot_detected()` is empty, so reboot recovery differs from EF10 and relies on higher-level reset behavior. Stats allocation is `GFP_ATOMIC`; failure yields no update. PF representor/MAE failures are mostly nonfatal but can leave traffic features unavailable.

## Test Signals
Test probe with valid/invalid design TLVs, warm-boot retry, MCDI RPCs, firmware version gating, interface up/down, RX/TX/MCDI/driver events, interrupt test generation, reset types, PHY configuration, filter table add/remove, ethtool stats, MAE privilege and representor creation, PF and VF probe/remove, and client handle lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_nic.c -->
