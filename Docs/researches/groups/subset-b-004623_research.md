# Research Report: subset-b-004623

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ethtool_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ethtool_common.c

## Purpose
`ethtool_common.c` implements shared ethtool handlers for the non-Falcon Solarflare `sfc` driver stack. It translates kernel ethtool operations into `struct efx_nic` state updates and NIC-type callbacks for driver identity, message level, self-tests, pause/FEC/link settings, software and hardware stats, RX classification, RSS indirection/hash configuration, reset, and optical module EEPROM queries.

## Important APIs, Types, and Functions
The file centers on `struct efx_sw_stat_desc`, `EFX_ETHTOOL_STAT()` descriptors, and the exported `efx_ethtool_*` functions declared in `ethtool_common.h`. Stats are built from NIC-type hardware stat callbacks, software counters in `struct efx_nic`, `struct efx_channel`, and `struct efx_tx_queue`, plus per-queue and PTP stats. Self-test reporting is kept consistent by `efx_ethtool_fill_self_tests()`, which is used for count, string, and data paths.

Link and PHY APIs include `efx_ethtool_get_link_ksettings()`, `efx_ethtool_set_link_ksettings()`, `efx_ethtool_get_fecparam()`, and `efx_ethtool_set_fecparam()`, all serialized with `efx->mac_lock` and delegated to MCDI PHY helpers. Flow-control APIs update `efx->wanted_fc` and `efx->link_advertising[0]`, then run MCDI port reconfiguration and MAC reconfiguration. RX classification APIs translate between `ethtool_rx_flow_spec` and `struct efx_filter_spec`; RSS APIs expose default and custom RSS contexts through `ethtool_rxfh_param` and `ethtool_rxfh_context`.

## Control Flow
Self-test flow allocates `struct efx_self_tests`, rejects inactive NIC state, opens the netdev if necessary, invokes `efx_selftest()`, closes the temporary open, fills the ethtool result array, and sets `ETH_TEST_FL_FAILED` on error. Stats flow takes `stats_lock` while reading hardware/software aggregate counters, releases it, then appends per TX/RX/XDP queues and PTP values in the same order used by the string/count routines.

RX NFC get paths switch on `info->cmd` to return rule count, one rule, or all rule IDs. Rule get maps an installed manual filter back into ethtool TCP/UDP IPv4/IPv6, user-IP, or Ethernet flow forms, adding `FLOW_EXT` for VLAN and `FLOW_RSS` plus `rss_context` when the filter carries RSS. Rule set validates location, queue/drop cookie, VLAN extensions, full-mask-only fields, and supported flow types before inserting a manual filter. RSS get/set pulls or pushes NIC RSS configuration; custom context create initializes default indirection/key when absent and then delegates to NIC-type context push.

## State and Persistence
The file does not own persistent storage; it mutates live driver state. Key fields include `msg_enable`, `wanted_fc`, `link_advertising[0]`, `rss_context.rx_indir_table`, `rss_context.rx_hash_key`, custom RSS context private IDs, and manual RX filters in the NIC filter table. `mac_lock` protects PHY/MAC and module EEPROM interactions, `stats_lock` protects stat snapshots, and filter operations rely on the type-specific safe filter callbacks.

## Dependencies and Integration Points
Dependencies include Linux ethtool/netdevice APIs, MCDI firmware/PHY helpers, NIC-type operation tables, `rx_common` RSS helpers, filter helpers, self-test structures, PTP stat helpers, and module EEPROM helpers. The exported functions are meant to be assembled into per-device `struct ethtool_ops` tables by higher-level driver files.

## Risks
String count, string generation, and data generation must remain exactly aligned or ethtool consumers will mislabel results. RX classifier translation only supports full masks for many fields; accepting partial masks would require hardware/filter support changes. RSS context operations depend on NIC-type support and use extack messages for unsupported custom contexts. Lock ordering around `mac_lock`, MCDI calls, and MAC reconfigure paths is important because these operations can sleep and interact with resets. The reset handler trusts `efx->type->map_reset_flags()` to clear/translate user flags correctly.

## Test Signals
Useful signals are successful `ethtool -i`, `-S`, `-t online/offline`, `-a/-A`, `--show-fec/--set-fec`, `-n/-N` classifier add/list/delete, `-x/-X` RSS indirection/key changes, custom RSS context netlink tests, and module EEPROM reads. Regression tests should compare `get_sset_count(ETH_SS_STATS/TEST)` with string/data array lengths and verify failure paths for unsupported masks, invalid queues, unsupported RSS contexts, and inactive NIC self-tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ethtool_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ethtool_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ethtool_common.h

## Purpose
`ethtool_common.h` is the public internal interface for the shared Solarflare `sfc` ethtool implementation. It declares reusable `efx_ethtool_*` handlers so NIC-specific driver files can build `struct ethtool_ops` tables without duplicating common logic.

## Important APIs, Types, and Functions
The header exports handlers for driver info, message level, self-test execution and self-test metadata, pause settings, stats string/data counts, link settings, FEC, RX NFC classification, RX ring count, RSS indirection/key/context operations, reset, and module EEPROM/module info access. It references kernel ethtool structures such as `struct ethtool_link_ksettings`, `struct ethtool_fecparam`, `struct ethtool_rxnfc`, `struct ethtool_rxfh_param`, and `struct ethtool_rxfh_context`, plus driver-owned `struct efx_nic` and `struct efx_self_tests`.

## Control Flow
The header has no executable control flow. Its design implies that consumers wire these declarations into ethtool operation tables and call `efx_ethtool_fill_self_tests()` consistently for test count, strings, and results.

## State and Persistence
No state is stored here. The declared functions mutate runtime NIC state in `struct efx_nic`, filter tables, RSS context tables, and PHY/MAC configuration through their implementations.

## Dependencies and Integration Points
The header depends on prior declarations for `struct net_device`, ethtool types, `struct efx_nic`, and `struct efx_self_tests` from surrounding driver headers and kernel headers. It is the coupling point between NIC-specific ethtool ops definitions and the common implementation in `ethtool_common.c`.

## Risks
Prototype drift between this file and `ethtool_common.c` or kernel ethtool API signatures will break compilation. The RSS context functions use newer ethtool context APIs, so kernel-version backports must keep signatures aligned. Because this header deliberately does not include all dependency headers itself, include order matters in consumers.

## Test Signals
Build coverage is the main signal: all consumers should compile with these prototypes, and sparse/clang warnings should catch mismatched pointer types. Runtime signals are the full ethtool command suite exercised through whichever `struct ethtool_ops` table imports these functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ethtool_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/Kconfig

## Purpose
This Kconfig fragment defines build-time configuration for the legacy Solarflare SFC4000/Falcon driver. `SFC_FALCON` enables the main network driver, and `SFC_FALCON_MTD` optionally exposes onboard flash/EEPROM as MTD devices for boot configuration updates.

## Important APIs, Types, and Functions
The file defines two symbols rather than C APIs. `SFC_FALCON` is a tristate depending on `PCI` and selecting `MDIO`, `CRC32`, `I2C`, and `I2C_ALGOBIT`. `SFC_FALCON_MTD` is a bool depending on `SFC_FALCON`, `MTD`, and a built-in/module compatibility condition that prevents built-in Falcon code from depending on modular MTD.

## Control Flow
Kconfig control flow is dependency resolution. Enabling `SFC_FALCON` permits the `sfc-falcon` module or built-in object to be built. Enabling `SFC_FALCON_MTD` causes `mtd.o` to be included by the Makefile and enables the MTD code paths guarded by `CONFIG_SFC_FALCON_MTD`.

## State and Persistence
The only persistence is generated kernel configuration. At runtime this affects whether the driver can be loaded and whether flash/EEPROM partitions appear as MTD devices.

## Dependencies and Integration Points
This integrates with the kernel networking, PCI, MDIO, I2C, CRC32, and MTD subsystems. The Makefile consumes `CONFIG_SFC_FALCON` and `CONFIG_SFC_FALCON_MTD` to build `sfc-falcon.o` and optional `mtd.o`.

## Risks
Incorrect dependency constraints can create invalid built-in/module combinations or missing subsystem symbols. The default `SFC_FALCON_MTD=y` means enabling MTD alongside the driver exposes device flash interfaces unless explicitly disabled, which may matter for systems that want to avoid flash write surfaces.

## Test Signals
Configuration tests should cover built-in and module combinations: `SFC_FALCON=m`, `SFC_FALCON=y`, `MTD=m`, `MTD=y`, and `SFC_FALCON_MTD` enabled/disabled. Build signals are successful linkage and the expected `sfc-falcon` module name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/Makefile

## Purpose
This Makefile defines the object composition for the legacy `sfc-falcon` driver module or built-in object.

## Important APIs, Types, and Functions
`sfc-falcon-y` aggregates core objects: `efx.o`, NIC/FArch/Falcon hardware support, TX/RX, self-test, ethtool, PHY/MDIO drivers, and board support. `sfc-falcon-$(CONFIG_SFC_FALCON_MTD)` conditionally adds `mtd.o`. `obj-$(CONFIG_SFC_FALCON)` emits the final `sfc-falcon.o` target.

## Control Flow
Kbuild evaluates the config variables and includes the listed object files in link order. The main entry point comes from `efx.o`, while the remaining objects provide hardware, PHY, queue, self-test, ethtool, and optional flash support referenced by the core driver.

## State and Persistence
No runtime state is stored here. It controls which compiled objects are present in the final kernel/module image.

## Dependencies and Integration Points
This file is coupled to `falcon/Kconfig` symbols and to the local source files named in `sfc-falcon-y`. It also relies on the kernel module build system's composite object convention.

## Risks
Removing or renaming an object without updating this file breaks the build. Link-order-sensitive initialization bugs are possible if objects provide tables or symbols expected by `efx.o` and hardware-specific files. Optional MTD code must remain fully guarded because it disappears when `CONFIG_SFC_FALCON_MTD` is unset.

## Test Signals
The direct signal is `make drivers/net/ethernet/sfc/falcon/` under configurations with and without `CONFIG_SFC_FALCON_MTD`. `modinfo sfc-falcon` or built-in symbol inspection should confirm the expected module/object composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/bitfield.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/bitfield.h

## Purpose
`bitfield.h` supplies the Falcon driver with endian-safe bitfield construction, extraction, testing, and modification macros for 32-bit dwords, 64-bit qwords, and 128-bit owords used in Solarflare MMIO registers, descriptors, and DMA-visible structures.

## Important APIs, Types, and Functions
The core data types are `ef4_dword_t`, `ef4_qword_t`, and `ef4_oword_t`, all represented with little-endian integer arrays. Field metadata is expected as `FIELD_LBN` and `FIELD_WIDTH`, consumed by `EF4_LOW_BIT()`, `EF4_WIDTH()`, and `EF4_HIGH_BIT()`. Extraction macros include `EF4_DWORD_FIELD`, `EF4_QWORD_FIELD`, and `EF4_OWORD_FIELD`; population macros include `EF4_POPULATE_DWORD_*`, `EF4_POPULATE_QWORD_*`, and `EF4_POPULATE_OWORD_*`; mutation macros include `EF4_SET_*_FIELD`. Formatting helpers expose `EF4_DWORD_FMT`, `EF4_QWORD_FMT`, and `EF4_OWORD_FMT`.

## Control Flow
There is no function control flow; behavior is macro expansion. The macros split bit ranges across native little-endian elements, convert to CPU endianness for extraction, and convert back for insertion. `BITS_PER_LONG` selects 64-bit or 32-bit implementations to fit architecture efficiency. Variadic-like fixed-arity populate wrappers pad missing fields with `EF4_DUMMY_FIELD`.

## State and Persistence
No global state exists. The macros write directly into caller-provided register/descriptor unions. Because these objects often represent MMIO or DMA structures, correctness persists into hardware-visible state.

## Dependencies and Integration Points
The header depends on Linux fixed-width types, endian conversion helpers, `BITS_PER_LONG`, and `dma_addr_t`. It is included by Falcon hardware code that defines register fields and needs portable access to hardware layouts.

## Risks
Macro arguments may be evaluated multiple times, so callers should pass simple lvalues and constants. Field definitions must be correct and non-overlapping; the helpers do not validate register specifications. Width handling is limited by `EF4_MASK32()`/`EF4_MASK64()` assumptions, and invalid widths or shifts can become compile-time or runtime undefined behavior. Endianness annotations are force-cast in all-ones/zero tests, so sparse warnings should be monitored carefully.

## Test Signals
Build coverage across 32-bit and 64-bit architectures is important because different macro variants are selected. Unit-style compile tests can populate and extract known 128-bit patterns, including fields crossing 32-bit and 64-bit boundaries. Runtime signals include correct descriptor programming, register dumps matching datasheet values, and absence of sparse endian warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/bitfield.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/efx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/efx.c

## Purpose
`efx.c` is the core of the legacy Falcon `sfc-falcon` network driver. It owns module parameters, PCI probe/remove, netdev registration, interrupt/channel setup, datapath start/stop, port lifecycle, filter table setup, reset and PCI error recovery, power management, NAPI polling, workqueues, and global Falcon loopback/reset name tables.

## Important APIs, Types, and Functions
Externally visible driver APIs include `ef4_net_open()`, `ef4_net_stop()`, `ef4_realloc_channels()`, `ef4_reconfigure_port()`, `ef4_mac_reconfigure()`, `ef4_schedule_reset()`, `ef4_reset()`, `ef4_reset_down()`, `ef4_reset_up()`, `ef4_try_recovery()`, interrupt moderation helpers, link-state helpers, dummy PHY ops, and `ef4_update_sw_stats()`. Static integration objects include `ef4_netdev_ops`, `ef4_pci_driver`, `ef4_pm_ops`, `ef4_err_handlers`, `ef4_pci_table`, and the global `reset_workqueue`.

## Control Flow
Probe allocates a multiqueue netdev, initializes `struct ef4_nic`, maps PCI BARs, probes NIC/port/filter/channel resources, initializes NAPI, initializes hardware/port/interrupts, sets netdev features, registers the netdev, and optionally probes MTD. Open checks disabled/special states, publishes current link state, starts the port and datapath, queues monitoring, and starts async self-test. Stop quiesces stats, monitor/self-test/MAC work, TX queues, DMA queues, RX refill, and datapath resources.

NAPI polling calls `ef4_process_channel()`, which processes event queues, flushes RX packets, refills RX descriptors, and completes BQL accounting. Channel probing allocates event queues, TX queues, and RX queues; reallocation detaches the device, stops traffic, soft-disables interrupts, clones copyable channels, swaps queue sizes, probes replacement channels, and rolls back on failure. Reset work chooses the highest pending reset bit, optionally tries EEH recovery, then runs `ef4_reset()` under RTNL. Reset down stops datapath/interrupts and tears down PHY/NIC state under `mac_lock`; reset up reinitializes hardware, PHY, interrupts, filters, unlocks, and restarts if allowed.

## State and Persistence
Persistent runtime state lives in `struct ef4_nic`: `state`, `reset_pending`, `port_enabled`, `port_initialized`, queue sizes, channel arrays, RSS indirection/key, interrupt mode, IRQ moderation, filters, MAC/PHY state, workqueues, VPD serial, and PCI BAR mappings. Global association lists track primary/secondary functions by VPD serial. Module parameters persist for module lifetime and affect channel split, RSS CPUs, interrupt mode, IRQ moderation thresholds, debug mask, and PHY flash mode.

## Dependencies and Integration Points
The file integrates with PCI, netdevice, NAPI, ethtool via `ef4_ethtool_ops`, MDIO ioctls, MSI/MSI-X, workqueues, PM callbacks, PCI AER/EEH recovery, MTD optional hooks, self-tests, Falcon NIC-type operation tables, TX/RX queue code, filter code, and PHY implementations. Type-specific callbacks in `efx->type` provide hardware behavior for probe/init/reset/stats/filter/interrupt/MAC operations.

## Risks
State transitions depend on RTNL, `mac_lock`, `stats_lock`, filter semaphores, IRQ synchronization, and workqueue cancellation being used in the intended order. Channel reallocation has rollback complexity and must not lose non-copyable channel buffer-table allocations. Reset masking assumes reset methods are ordered by scope. Probe/remove and PM paths must leave no live work item, IRQ, NAPI instance, or mapped BAR behind. The file uses legacy ethtool advertising bits and older MSI APIs, so kernel API changes can break backports.

## Test Signals
Important tests include PCI probe/remove, module unload, interface open/close, MTU and MAC address changes, TX watchdog reset, manual ethtool reset, suspend/resume/freeze/thaw, PCI error injection, MSI-X/MSI/legacy fallback, channel/ring resizing via ethtool, RSS CPU/module parameter variations, link change logging, async self-test execution, and netdev rename updating MTD/channel names. Lockdep, KASAN, interrupt storm checks, and repeated reset/remove cycles are high-value signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/efx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/efx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/efx.h

## Purpose
`efx.h` is the central internal header for the Falcon driver. It publishes constants, lifecycle functions, queue APIs, filter wrappers, reset APIs, interrupt moderation helpers, MTD hooks, scheduling helpers, and link/MAC helpers used across Falcon source files.

## Important APIs, Types, and Functions
The header declares netdev entry points (`ef4_net_open()`, `ef4_net_stop()`), TX/RX queue management, datapath transmit functions, RX refill and packet completion functions, channel reallocation, MAC/port reconfiguration, reset functions, IRQ moderation accessors, event queue start/stop, dummy PHY ops, software stat updates, MTD wrappers, link-state helpers, and `ef4_ethtool_ops`. Inline filter wrappers dispatch to `efx->type->filter_*` callbacks and document insertion/replacement semantics. Inline helpers include `ef4_rss_enabled()`, `ef4_schedule_channel()`, `ef4_schedule_channel_irq()`, `ef4_device_detach_sync()`, and a write-lock assertion helper.

## Control Flow
The header contributes inline control flow for filter operation dispatch, RFS expiration gating, NAPI scheduling, device detach synchronization, and optional MTD no-op behavior when `CONFIG_SFC_FALCON_MTD` is disabled. Most declared control flow is implemented in other C files.

## State and Persistence
No storage is allocated here, but the APIs operate on `struct ef4_nic`, `struct ef4_channel`, `struct ef4_tx_queue`, `struct ef4_rx_queue`, and `struct ef4_filter_spec`. Constants define queue/event queue sizing limits and minimums that shape persistent queue allocation decisions.

## Dependencies and Integration Points
The file includes `net_driver.h` and `filter.h`, so it sits above the core driver data structures and filter definitions. It ties together TX, RX, ethtool, MTD, RFS acceleration, reset, link, and NAPI code in the Falcon subtree.

## Risks
Because many helpers dispatch through `efx->type`, missing or incorrectly initialized NIC-type callbacks become runtime crashes. Queue-size constants must remain compatible with hardware ring limits and TSO descriptor requirements. Optional MTD and RFS branches must compile both enabled and disabled. The `ef4_rwsem_assert_write_locked()` helper temporarily attempts a read lock and should only be used in debug-style contexts where that behavior is acceptable.

## Test Signals
Full subtree build coverage with `CONFIG_SFC_FALCON_MTD` and `CONFIG_RFS_ACCEL` toggled is important. Runtime tests should exercise filter insertion/removal/get wrappers, NAPI scheduling, event queue start/stop, ring resize constraints, MTD probe/remove stubs, and reset/link helper callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/efx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/enum.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/enum.h

## Purpose
`enum.h` defines shared Falcon driver enumerations and masks for loopback modes and reset types. These values are used across ethtool self-tests, PHY/MAC configuration, reset scheduling, reset logging, and hardware recovery.

## Important APIs, Types, and Functions
`enum ef4_loopback_mode` assigns stable numeric IDs to no-loopback, datapath, MAC/internal, PHY, wireside, and external loopback modes. Macros such as `LOOPBACKS_INTERNAL`, `LOOPBACKS_WS`, `LOOPBACKS_EXTERNAL()`, `LOOPBACK_MASK()`, `LOOPBACK_INTERNAL()`, `LOOPBACK_EXTERNAL()`, `LOOPBACK_CHANGED()`, and `LOOPBACK_OUT_OF()` classify and compare modes. `LOOPBACK_TEST_MAX` limits which modes participate in self-tests. `enum reset_type` distinguishes reset methods/scopes from reset reasons such as watchdog, interrupt error, RX recovery, DMA error, and TX skip.

## Control Flow
The file contains no executable functions, but its masks drive branches in port reconfiguration, link settings, ethtool self-test enumeration, and reset scheduling. Reset methods are intentionally ordered by increasing scope, and `ef4_reset()` uses that ordering when clearing pending reset bits covered by a completed reset.

## State and Persistence
No state is stored here. Numeric enum values effectively become ABI-like internal constants for logs, string lookup tables, bitmasks, and pending reset bit positions, so changing them would affect runtime behavior across the driver.

## Dependencies and Integration Points
The definitions are consumed by `efx.c`, `ethtool.c`, PHY/MAC code, self-test code, and string-table helpers. The comments explicitly require loopback defines and enum values to stay synchronized.

## Risks
The loopback masks use `1 << mode`, so adding enough modes to exceed the width of `int` or failing to update masks will cause incorrect classification. Reset ordering is semantically significant; inserting new methods in the wrong location can cause `reset_pending` clearing bugs. `RESET_TYPE_INVSIBLE` is misspelled in the comment, but the enum constant is `RESET_TYPE_INVISIBLE`.

## Test Signals
Self-test string counts should include expected loopback modes, and loopback mode changes should drive PHY transmit-disable behavior correctly. Reset tests should verify that broader resets clear narrower pending reset bits while reason-based reset scheduling maps through NIC-type callbacks as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/enum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/ethtool.c

## Purpose
`falcon/ethtool.c` implements the legacy Falcon `ef4_ethtool_ops` table. It provides ethtool support for driver info, register dumps, message level, link settings, self-tests, stats, identify LED, IRQ coalescing, ring sizing, pause settings, Wake-on-LAN, reset, RX classification filters, RSS indirection, RSS hash fields, and module EEPROM/module info.

## Important APIs, Types, and Functions
The file defines `struct ef4_sw_stat_desc`, software stat descriptor macros, helpers for integer/atomic stat reads, and the exported `const struct ethtool_ops ef4_ethtool_ops`. Key handlers include `ef4_ethtool_get_link_ksettings()`, `ef4_ethtool_set_link_ksettings()`, `ef4_ethtool_self_test()`, `ef4_ethtool_get_sset_count()`, `ef4_ethtool_get_strings()`, `ef4_ethtool_get_stats()`, `ef4_ethtool_get/set_coalesce()`, `ef4_ethtool_get/set_ringparam()`, `ef4_ethtool_get/set_pauseparam()`, RX NFC get/set helpers, RSS get/set helpers, module EEPROM/info helpers, and reset/WOL/LED handlers.

## Control Flow
Self-test flow mirrors the newer shared implementation but uses Falcon `ef4_*` types and optional PHY-specific external tests. Stats flow appends NIC hardware stats, aggregate software counters, and per-channel TX/RX packet counts. Coalescing get/set maps the hardware's shared event-queue moderation model into ethtool's RX/TX and IRQ fields, then pushes moderation to every channel. Ring set validates RX/TX limits, enforces driver minimums, and calls `ef4_realloc_channels()`.

RX classifier get translates an `ef4_filter_spec` back to ethtool flow specs for TCP/UDP IPv4/IPv6, user IPv4/IPv6, and Ethernet flows, including VLAN extension masks. RX classifier set validates user-provided masks, queue/drop cookies, and location semantics, builds a manual filter spec, inserts it, and returns the allocated location. RSS support is Falcon-revision aware: pre-B0 or single-channel devices report no indirection table, and B0 supports Toeplitz RSS without key changes through this interface.

## State and Persistence
The file reads and mutates live `struct ef4_nic` state: `msg_enable`, `wanted_fc`, `link_advertising`, queue sizes, IRQ moderation fields, RX indirection table, manual filter table, WOL settings, and PHY module data. `mac_lock` serializes PHY/MAC, pause, link, and module EEPROM operations. `stats_lock` protects stat snapshots.

## Dependencies and Integration Points
It depends on Falcon driver headers (`net_driver.h`, `workarounds.h`, `selftest.h`, `efx.h`, `filter.h`, `nic.h`), Linux ethtool/netdevice/rtnetlink APIs, MDIO restart helpers, NIC-type callbacks, PHY operations, filter APIs, and reset code in `efx.c`. The ops table is installed in `ef4_register_netdev()`.

## Risks
The file duplicates much of the newer `ethtool_common.c` logic with legacy names, so fixes can diverge between Falcon and non-Falcon paths. String/count/data ordering must remain synchronized. Flow classification only accepts exact masks for supported fields and can reject valid-looking ethtool requests unsupported by hardware. Coalescing compatibility with legacy `*_irq` fields is subtle. RSS key changes are unsupported here, and pre-B0 hash behavior is intentionally limited due to hardware issues.

## Test Signals
Use `ethtool -i`, `-d`, `-S`, `-t`, `-c/-C`, `-g/-G`, `-a/-A`, `-s`, `-p`, `-n/-N`, `-x/-X`, `--show-module`, and WOL commands on Falcon hardware or a targeted test harness. High-value regressions include string/count alignment, ring resize rollback, invalid RX classifier masks, queue-drop filters, RSS disabled on pre-B0/single-channel devices, pause autoneg rejection, and module EEPROM unsupported PHY paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/ethtool.c -->
