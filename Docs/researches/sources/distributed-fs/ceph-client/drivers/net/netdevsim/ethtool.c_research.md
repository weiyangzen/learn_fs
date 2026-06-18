# sources/distributed-fs/ceph-client/drivers/net/netdevsim/ethtool.c

## Purpose
This file provides ethtool operations for each netdevsim netdev. It simulates pause parameters and stats, coalescing, ring parameters, channels/queue counts, FEC settings and statistics, and timestamp PHC reporting, with debugfs knobs for selected failure and reporting behaviors.

## Important APIs, Types, and Functions
`nsim_ethtool_ops` installs handlers for pause stats/params, coalesce get/set, ring get/set, channels get/set, FEC get/set/stats, and timestamp info. Helper functions include `nsim_get_pause_stats()`, `nsim_get_pauseparam()`, `nsim_set_pauseparam()`, `nsim_get_coalesce()`, `nsim_set_coalesce()`, `nsim_get_ringparam()`, `nsim_set_ringparam()`, `nsim_get_channels()`, `nsim_set_channels()`, `nsim_get_fecparam()`, `nsim_set_fecparam()`, `nsim_get_fec_stats()`, `nsim_get_ts_info()`, and `nsim_ethtool_init()`.

## Control Flow
Initialization assigns the ethtool ops to the netdev, initializes default ring limits and pending sizes, enables pause stat reporting by default, sets FEC to none, sets channel count from the bus device queue count, and creates debugfs files under the port's `ethtool` directory. Getters mostly copy simulator state into ethtool structures. Setters copy user-requested state back into `ns->ethtool`, with validation for unsupported pause autoneg and injected FEC get/set errors. Channel setting calls `netif_set_real_num_queues()` for RX and TX and, when linked to a peer, synchronizes networking and wakes local and peer queues. FEC setting computes active FEC as the highest selected mode after normalizing AUTO/OFF/NONE semantics.

## State and Persistence
Per-netdevsim runtime state lives under `ns->ethtool`: pause reporting flags, pause rx/tx settings, coalesce structure, ring structure, channel count, FEC parameters, and injected `get_err`/`set_err` values. Debugfs files expose error injection and selected pause/ring maxima. There is no persistent storage beyond the lifetime of the simulated netdev.

## Dependencies and Integration Points
The file depends on ethtool core structures, `netdev_queues` queue count helpers, debugfs, RCU peer pointers from netdevsim linking, and mock PHC support through `mock_phc_index(ns->phc)`. It complements `bus.c` queue-count creation and `dev.c` port/debugfs lifecycle.

## Risks and Edge Cases
Pause autoneg is rejected because the simulator does not support link ksettings. Ring setters update pending values but not max values; max values can be adjusted through debugfs to exercise ethtool validation paths. Channel changes can fail if queue count changes are invalid, and linked peers require wakeups to avoid stuck queues. FEC error injection returns negative values of debugfs-controlled integers, so tests must set sensible errno values. Active FEC selection uses `fls()` on a normalized bitmask and assumes at least one bit is set.

## Test Signals
Tests should verify `ethtool -a/-A`, coalesce, ring, channels, FEC, FEC stats, and timestamp info on netdevsim devices. Debugfs `get_err` and `set_err` should force FEC failures. Channel tests should confirm real queue count changes and peer queue wakeups when devices are linked. Pause stat toggles should change reported RX/TX pause frame counters.
