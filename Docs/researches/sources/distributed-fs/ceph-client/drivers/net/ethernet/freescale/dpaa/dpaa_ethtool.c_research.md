# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_ethtool.c

## Purpose
This file implements DPAA1 ethtool operations for link settings, pause, message level, detailed statistics, RX hash controls, timestamp capabilities, QMan interrupt coalescing, and standard MAC/RMON/pause stats delegation.

## Important APIs, Types, and Functions
The exported object is `dpaa_ethtool_ops`. Link operations delegate to phylink (`dpaa_get_link_ksettings()`, `dpaa_set_link_ksettings()`, `dpaa_nway_reset()`, pause get/set). Stats are described by `dpaa_stats_percpu` and `dpaa_stats_global`, filled by `dpaa_get_ethtool_stats()`, and named by `dpaa_get_strings()`. RX hash controls are `dpaa_get_rxfh_fields()` and `dpaa_set_rxfh_fields()`. Timestamp info is `dpaa_get_ts_info()`. Coalescing is handled by `dpaa_get_coalesce()` and `dpaa_set_coalesce()`.

## Control Flow
Ettool calls enter through the ops table. Stats iterate online CPUs, copy per-CPU counters plus per-CPU BMan pool counts, aggregate RX error and ERN counters, query congestion status, and reset congestion time/count after reporting. RXFH enables or disables FMan keygen hashing based on supported IP/L4 field masks. Coalescing reads or writes QMan portal interrupt period/threshold on affine online CPUs, reverting prior portals if a later update fails.

## State and Persistence
This file reads and mutates live driver state: `msg_enable`, `keygen_in_use`, per-CPU stats, buffer pool counts, congestion counters, and QMan portal coalescing settings. Changes are runtime-only.

## Dependencies and Integration Points
It integrates with phylink, FMan MAC statistic callbacks, QMan portal APIs, OF/PTP lookup for PHC index, and DPAA private structures. It also uses ethtool's modern stats, RXFH, timestamp, and coalesce interfaces.

## Risks
Stats sizing depends on `num_online_cpus()` at get-count/get-strings/get-stats time; CPU hotplug between calls can confuse userspace buffer expectations. `dpaa_get_ethtool_stats()` resets congestion counters as a read side effect. `dpaa_get_coalesce()` reports the current CPU's portal values, while setting attempts all affine online portals. PTP lookup depends on the FMan node's `ptimer-handle`.

## Test Signals
Run `ethtool -S`, `-k`, `-c`, `-C`, `-n`/RXFH field operations, pause operations, link setting changes, and `ethtool -T`. Include CPU hotplug/coalescing failure injection and traffic that exercises ERN and congestion counters.
