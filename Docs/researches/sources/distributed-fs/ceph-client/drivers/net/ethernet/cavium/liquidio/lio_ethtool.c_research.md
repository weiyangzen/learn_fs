# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_ethtool.c

## Purpose

`lio_ethtool.c` provides the ethtool control and observability surface for LiquidIO PF and VF netdevs. It translates ethtool requests into local driver state reads, chip CSR reads/writes, firmware soft commands, and netdev/queue reconfiguration. It also selects separate PF and VF `struct ethtool_ops` tables through `liquidio_set_ethtool_ops()`.

## Important APIs, Types, and Functions

- `lio_get_link_ksettings()` reports port type, link modes, speed, duplex, FEC advertising, and 10G/25G support using `lio->linfo`, `oct->subsystem_id`, `oct->speed_setting`, and firmware-backed speed/FEC getters.
- `lio_set_link_ksettings()` supports 10G/25G speed changes only on supported CN23XX 25G PFs and delegates to `liquidio_set_speed()`.
- `lio_get_drvinfo()` and `lio_get_vf_drvinfo()` expose driver name, firmware version, and PCI bus name.
- `lio_ethtool_get_channels()` and `lio_ethtool_set_channels()` report and change combined RX/TX queue count, with CN23XX PF/VF-specific maximum discovery.
- `lio_reset_queues()` is the central queue teardown/rebuild helper used by channel count and ring descriptor count changes.
- `lio_ethtool_get_ringparam()` and `lio_ethtool_set_ringparam()` expose and reconfigure RX/TX descriptor counts for CN23XX PF/VF.
- `lio_set_phys_id()`, `octnet_gpio_access()`, `octnet_id_active()`, and `octnet_mdio45_access()` implement LED identification using GPIO, MDIO clause 45, or firmware commands depending on chip.
- `lio_get_pauseparam()` and `lio_set_pauseparam()` expose flow-control state and send `OCTNET_CMD_SET_FLOW_CTL` for CN23XX PF.
- `lio_get_ethtool_stats()` and `lio_vf_get_ethtool_stats()` assemble PF/VF stats from netdev stats, firmware link stats, IQ stats, and DROQ stats.
- `lio_get_strings()`, `lio_vf_get_strings()`, `lio_get_sset_count()`, and `lio_vf_get_sset_count()` keep ethtool string tables aligned with stats output.
- `octnet_get_intrmod_cfg()`, `octnet_set_intrmod_cfg()`, `lio_get_intr_coalesce()`, and `lio_set_intr_coalesce()` expose interrupt moderation, including adaptive firmware parameters and direct CSR updates.
- `lio_get_regs_len()` and `lio_get_regs()` provide register dumps for CN23XX PF, CN23XX VF, and CN6XXX variants.
- `lio_get_fecparam()` and `lio_set_fecparam()` expose FEC settings for supported 25G CN23XX cards through core FEC helpers.
- `lio_get_priv_flags()` and `lio_set_priv_flags()` expose driver private flags stored in `oct->priv_flags`; the visible private flag string table is currently empty.

## Control Flow

Normal ethtool reads are direct: link settings read `lio->linfo` and occasionally refresh speed/FEC from firmware; stats read netdev/IQ/DROQ/link-stat counters; register dumps read CSRs into the provided buffer. Writes are split between simple firmware control commands and disruptive queue reconfiguration.

Channel-count changes enter `lio_ethtool_set_channels()`. The function enforces firmware version `>= 1.6.1`, accepts only `combined_count`, validates chip-specific maximums, marks the interface `LIO_IFSTATE_RESETTING`, stops the netdev if it is running, calls `lio_reset_queues()`, reopens if needed, and clears reset state. Ring descriptor changes follow a similar flow in `lio_ethtool_set_ringparam()`, except they first update the configured descriptor counts and roll those values back if `lio_reset_queues()` fails.

`lio_reset_queues()` drains pending requests, turns queues off in firmware/hardware, disables all I/O queues, deletes NAPI entries, optionally tears down RX OOM workqueues and gather lists, deletes all active DROQs and IQs, updates SR-IOV ring allocation when queue count changes, re-runs chip register setup, recreates instruction/output queue structures, recreates PF mailbox and IRQs when needed, re-enables I/O queues, informs firmware about queue counts, calls `liquidio_setup_io_queues()`, and recreates gather lists plus RX OOM polling.

Coalesce changes first configure firmware adaptive interrupt moderation through `oct_cfg_adaptive_intr()`. If adaptive mode is disabled, the function programs RX interrupt time/count thresholds and TX interrupt count thresholds directly into CN6XXX or CN23XX PF/VF CSRs and mirrors values into `oct->rx_coalesce_usecs`, `oct->rx_max_coalesced_frames`, and `oct->tx_max_coalesced_frames`.

## State and Persistence Behavior

The file reads and writes several layers of state:

- Netdev-visible state: link settings, ring/channel parameters, stats, pause parameters, FEC, timestamp info, and register dumps.
- Local driver state: `lio->msg_enable`, `lio->ifstate`, `oct->num_iqs`, `oct->num_oqs`, `oct->priv_flags`, coalesce caches, pause flags, FEC/speed caches, and queue masks.
- Firmware state: speed, FEC, queue count, interrupt moderation policy, LED activity, MDIO values, flow control, and queue/ring configuration.
- Hardware state: MSI-X IRQ allocation, IQ/DROQ registers, interrupt thresholds, and CSR register dump contents.

No durable filesystem state is written. Persistence is in the adapter firmware, chip registers, and Linux in-memory driver structures. Some settings, especially FEC and speed, may require reload or reboot semantics described only through log messages, so callers should not assume immediate link renegotiation from local state alone.

## Dependencies and Integration Points

The file integrates Linux ethtool APIs, netdev queue APIs, NAPI list manipulation, PCI MSI-X APIs, chip-specific CN23XX/CN6XXX CSR macros, and LiquidIO firmware command helpers. It calls exported functions from `lio_core.c` for queue setup, gather-list management, RX OOM workqueue setup, interrupts, feature logging, speed/FEC, and RX drain waits. It also relies on chip-specific helpers such as `cn23xx_sriov_config()`, `octeon_allocate_ioq_vector()`, `octeon_setup_interrupt()`, `cn23xx_pf_get_oq_ticks()`, and `cn23xx_vf_get_oq_ticks()`.

`liquidio_set_ethtool_ops()` is called during netdev setup in `lio_main.c`, assigning the VF ops table for CN23XX VFs and the PF/full ops table otherwise. Several PF-only capabilities are hidden or rejected for VFs through the ops table or runtime checks.

## Risks and Edge Cases

- `lio_reset_queues()` performs broad teardown and rebuild under ethtool calls. Failure in the middle can leave NAPI, IRQs, mailbox state, config values, or queue objects partially changed; only ring descriptor counts have explicit config rollback.
- `lio_ethtool_set_channels()` sets `LIO_IFSTATE_RESETTING` and may return early on reset failure without clearing it or reopening a previously stopped netdev.
- Stats string counts must exactly match stats data order. Any change to `oct_stats_strings`, `oct_vf_stats_strings`, `oct_iq_stats_strings`, or `oct_droq_stats_strings` requires coordinated updates to the data fill loops and sset counts.
- Register dumps append many formatted strings into fixed-size ethtool buffers using `sprintf`. The advertised lengths are constants, so additions to dump content need explicit size validation to avoid overrun.
- Firmware version checks use string comparison for versions such as `"1.6.1"` and `"1.7.1"`, which can misorder multi-digit version components.
- LED identification paths differ sharply by chip and firmware version. MDIO restore failures can leave CN68XX LED registers in identification mode.
- Coalesce configuration mixes firmware adaptive moderation with direct CSR writes. Partial failure can leave firmware and cached local values inconsistent.
- PF/VF queue indexing differs between direct queue numbers and PF SRN-adjusted queue numbers; off-by-base mistakes can affect other functions or VFs.

## Test Signals

- Run `ethtool`, `ethtool -i`, `ethtool -k`, `ethtool -c`, `ethtool -g`, `ethtool -l`, `ethtool -S`, `ethtool -d`, `ethtool --show-fec`, and `ethtool --identify` on PF and VF devices.
- Change combined channels while traffic is active and while the netdev is down, then verify queue count, IRQ count, NAPI count, XPS affinity, and firmware queue count.
- Change ring sizes to minimum, maximum, and clamped values; verify rollback on reset failure and no stale descriptor counts.
- Validate stats string/data alignment by checking `ethtool -S` output length and counter plausibility before and after queue-count changes.
- Toggle adaptive and fixed interrupt coalescing and verify CSR values plus firmware moderation state.
- Test PF-only paths on VF devices and unsupported CN6XXX/CN23XX variants to confirm `-EOPNOTSUPP` or `-EINVAL` behavior.
- Run register dump paths under KASAN or hardened builds because fixed dump lengths and nested loops are sensitive to buffer growth.
