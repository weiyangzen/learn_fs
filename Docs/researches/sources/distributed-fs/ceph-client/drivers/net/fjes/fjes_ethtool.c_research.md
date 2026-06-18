# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_ethtool.c

## Purpose
`fjes_ethtool.c` provides ethtool integration for FJES. It exposes driver info, static link settings, adapter and per-endpoint statistics, MMIO register dumps, and device debug trace dump controls.

## Important APIs and Functions
The public hook is `fjes_set_ethtool_ops()`. The ethtool callbacks are `fjes_get_ethtool_stats()`, `fjes_get_strings()`, `fjes_get_sset_count()`, `fjes_get_drvinfo()`, `fjes_get_link_ksettings()`, `fjes_get_regs_len()`, `fjes_get_regs()`, `fjes_set_dump()`, `fjes_get_dump_flag()`, and `fjes_get_dump_data()`. `struct fjes_stats` plus `FJES_STAT()` maps adapter statistic fields to ethtool string/data rows.

## Control Flow
`fjes_set_ethtool_ops()` installs a static `ethtool_ops` table on the netdev during setup. Stats callbacks first copy global adapter counters, then iterate all remote endpoints and append 14 endpoint-specific command/interrupt/drop counters per endpoint. Register dump callbacks read selected FJES information, command, buffer-address, and interrupt registers through `rd32()`. Dump control uses `dump->flag` to start or stop hardware debug tracing under `hw_info.lock`; dump data copies `hw->hw_info.trace` to the ethtool buffer.

## State, Dependencies, and Integration
The file reads `struct fjes_adapter`, `struct fjes_hw`, per-endpoint `ep_stats`, `stats64`, MMIO register accessors from `fjes_regs.h`, and debug commands from `fjes_hw.c`. It reports a fixed synthetic full-duplex 20 Gb/s link with no autonegotiation. Debug trace state is `hw->debug_mode`, `hw->hw_info.trace`, and `trace_size`.

## Risks and Test Signals
Risks include stats/string count mismatches when `max_epid` changes, register reads while hardware is unavailable, trace start/stop error handling, and stale debug mode on failed commands. There is also a likely typo in the stat table where `"tx_bytes"` reads `stats64.rx_bytes`. Tests should compare `get_sset_count()` with emitted strings/data, validate register dump length, exercise dump enable/disable/data paths, and check stats on devices with multiple EPIDs.
