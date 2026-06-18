# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad_ethtool.c

## Purpose
Implements ethtool support for the BNA netdev: fixed 10G link settings, driver and firmware information, coalescing/DIM control, ring-depth reconfiguration, pause settings, extensive software/hardware/per-queue statistics, EEPROM/flash partition access, and firmware flashing.

## Important APIs, Types, and Functions
The exported entry point is `bnad_set_ethtool_ops`, which installs `bnad_ethtool_ops`. Link operations are `bnad_get_link_ksettings` and `bnad_set_link_ksettings`; info and WOL are `bnad_get_drvinfo` and `bnad_get_wol`; interrupt moderation is `bnad_get_coalesce`/`bnad_set_coalesce`; ring changes are `bnad_get_ringparam`/`bnad_set_ringparam`; pause is `bnad_get_pauseparam`/`bnad_set_pauseparam`. Stats are driven by `bnad_net_stats_strings`, dynamic string emitters for TxF/RxF/CQ/RxQ/TxQ, `bnad_get_strings`, `bnad_get_stats_count_locked`, `bnad_per_q_stats_fill`, `bnad_get_ethtool_stats`, and `bnad_get_sset_count`. Flash/EEPROM paths are `bnad_get_flash_partition_by_offset`, `bnad_get_eeprom_len`, `bnad_get_eeprom`, `bnad_set_eeprom`, and `bnad_flash_device`.

## Control Flow and State
Coalescing validates nonzero usec values within firmware units, toggles DIM under `conf_mutex` and `bna_lock`, starts or deletes the DIM timer, and pushes Tx/Rx coalescing timeouts into BNA objects. Ring reconfiguration validates power-of-two depths and, if the netdev is running, destroys and recreates affected Rx/Tx objects. Rx recreation replays VLANs, broadcast, MAC address, and receive mode.

Stats string/count/value generation is dynamic. Base netdev and driver stats are followed by hardware stats, active TxF/RxF stats selected from BNA RID masks, CQs, RxQs, optional second RxQs, and TxQs. Values are read under `bna_lock` after verifying the caller's expected stats count. EEPROM reads/writes map ethtool offsets to firmware flash partitions by first querying flash attributes, then issuing asynchronous flash commands and waiting for completions. Firmware flashing uses `request_firmware()` and updates the firmware image partition.

## State and Persistence Behavior
Etthool changes can persist for the lifetime of the device instance: queue depths, coalescing values, DIM enablement, pause configuration, and firmware/EEPROM writes. Statistics are live snapshots from BNAD software counters and BNA hardware stats. Firmware flashing and EEPROM writes are persistent hardware mutations.

## Dependencies and Integration Points
Depends on Linux ethtool, rtnetlink stats types, firmware loading, BNA flash/CEE/IOC APIs, BNAD setup/teardown helpers, `bna_rx_rid_mask`, `bna_tx_rid_mask`, and BNAD locking. It is installed by `bnad_netdev_init()` in `bnad.c`.

## Risks and Test Signals
High-risk operations are ring recreation under traffic, flash writes, EEPROM partition mapping, and coalescing timer races. Stats string/count/value ordering must stay perfectly aligned; `bnad_get_strings()` appears to shift the RxF RID bitmap both in the `for` increment and inside the loop body, unlike the count and value paths, so multi-RID RxF stats strings can become misaligned. `bnad_set_coalesce()` clears the DIM flag and then checks the same flag before deleting the timer, making the delete branch look unreachable; timer behavior should be tested. `bnad_flash_device()` calls `release_firmware(fw)` even when `request_firmware()` failed, leaving `fw` uninitialized. Test signals include `ethtool -S` count/string/value validation, DIM on/off under traffic, ringparam changes while up/down, pause toggles, EEPROM invalid offsets, firmware flash failure injection, and multiple active RIDs.
