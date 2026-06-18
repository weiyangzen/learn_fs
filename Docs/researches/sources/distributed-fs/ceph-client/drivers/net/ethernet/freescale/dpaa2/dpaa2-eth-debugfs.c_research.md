# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-debugfs.c

## Purpose
This optional debugfs sidecar exposes DPAA2 Ethernet internal counters for per-CPU stats, frame queues, channels, and buffer pools under a `dpaa2-eth` debugfs root.

## Important APIs, Types, and Functions
Show functions are `dpaa2_dbg_cpu_show()`, `dpaa2_dbg_fqs_show()`, `dpaa2_dbg_ch_show()`, and `dpaa2_dbg_bp_show()`, each wrapped by `DEFINE_SHOW_ATTRIBUTE`. Lifecycle functions are `dpaa2_eth_dbg_init()`, `dpaa2_eth_dbg_exit()`, `dpaa2_dbg_add()`, and `dpaa2_dbg_remove()`.

## Control Flow
Module init creates the root directory. Per-interface probe calls `dpaa2_dbg_add()`, which creates a `dpni.<id>` directory and files `cpu_stats`, `fq_stats`, `ch_stats`, and `bp_stats`. Reads format current state through seq_file. Remove recursively deletes the per-interface directory, and module exit removes the root.

## State and Persistence
Debugfs state consists of dentries only. File contents are live views of `dpaa2_eth_priv` counters, FQ state, channel state, and buffer pool state. Nothing is persisted.

## Dependencies and Integration Points
The file depends on `debugfs`, `seq_file`, DPAA2 private structures, DPIO query helpers (`dpaa2_io_query_fq_count()` and `dpaa2_io_query_bp_count()`), and `fsl_mc_device` object IDs.

## Risks
`dpaa2_dbg_ch_show()` divides frames by CDAN count without a zero guard, so a channel with zero CDANs can fault during debugfs read. Debugfs creation errors are not checked in `dpaa2_dbg_add()`. Names are limited to 10 bytes, which fits `dpni.%d` for typical IDs but truncation is possible for large object IDs.

## Test Signals
Mount debugfs and read all files before and after traffic, with idle channels, multiple CPUs, multiple buffer pools, and interfaces removed while files are open. Specifically validate zero-CDAN behavior.
