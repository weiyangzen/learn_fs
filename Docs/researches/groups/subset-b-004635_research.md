# subset-b-004635 research

This grouped report covers the requested Solarflare/SFC Siena network-driver files. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/selftest.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/selftest.c

## Purpose
This file implements the SFC driver's ethtool self-test execution path for the non-Siena top-level driver variant. It validates PHY liveness, NVRAM access, interrupt delivery, event queue DMA/interrupt signaling, optional PHY extended tests, chip memory/register tests, and MAC/PHY loopback behavior. It also owns the asynchronous event-queue interrupt smoke test scheduled when a netdev is opened.

## Important APIs, types, and functions
`struct efx_loopback_payload` defines the synthetic Ethernet/IP/UDP payload used to exercise RSS vectors. `struct efx_loopback_state` is temporary per-loopback state stored through `efx->loopback_selftest`.

`efx_selftest()` is the main entry point used by ethtool. It cancels async tests, runs online tests, and optionally performs disruptive offline tests while the netdev is detached. `efx_loopback_rx_packet()` is called from RX delivery while loopback self-test state is active. `efx_selftest_async_init()`, `efx_selftest_async_start()`, and `efx_selftest_async_cancel()` manage the delayed interrupt-test work.

Key internal helpers include `efx_test_phy_alive()`, `efx_test_nvram()`, `efx_test_interrupts()`, `efx_test_eventq_irq()`, `efx_test_phy()`, `efx_begin_loopback()`, `efx_end_loopback()`, `efx_test_loopback()`, and `efx_wait_for_link()`.

## Control flow
Online tests run first: PHY alive, optional NVRAM, direct interrupt generation, and per-channel event queue event/interrupt checks. Event queue testing records read pointers, generates test events per channel, temporarily stops/starts event queues to inspect DMA completion and interrupt CPU state, and returns timeout on incomplete delivery.

Offline mode detaches the device, optionally runs `efx->type->test_chip()`, powers the PHY out of low power, clears loopback, runs PHY tests, and then iterates all supported loopback modes up to `LOOPBACK_TEST_MAX`. Each loopback reconfigures the port under `mac_lock`, waits for link stability, sends bursts on enabled TX queue types, waits for RX callbacks, counts TX completions, and restores original PHY/loopback settings before reattaching the device.

## State and persistence behavior
Persistent NIC state touched includes `efx->phy_mode`, `efx->loopback_mode`, `efx->loopback_selftest`, async delayed work, and test result fields in `struct efx_self_tests`. Loopback state is allocated only for the test and freed before return. `state->flush` prevents in-flight packets from being interpreted during mode changes and cleanup. There is no on-disk persistence.

## Dependencies and integration points
The file depends on MCDI PHY helpers, NIC type callbacks (`test_nvram`, `test_chip`), event/interrupt abstractions, TX enqueue, channel iteration macros, reset scheduling, and netdev detach/attach helpers. RX code must call `efx_loopback_rx_packet()` when `efx->loopback_selftest` is active.

## Risks
Race sensitivity is high around loopback state visibility, RX callbacks, and event queue stop/start. The code uses memory barriers and atomic counters, but ordering mistakes could create false failures or use-after-free in loopback RX. Offline tests intentionally disrupt traffic. Timeout values trade off avoiding false hardware blame against long test duration. Error paths that fail before port restoration could leave link/PHY state inconsistent, though the main path restores at the end.

## Test signals
Strong signals are ethtool online/offline self-tests, successful direct IRQ and event queue tests across every channel, loopback counts with `tx_sent == tx_done == rx_good` and zero `rx_bad`, and logs showing restored link state after offline tests. Regression testing should include MSI-X, MSI, legacy interrupt modes, multiple RSS channels, checksum-offload TX queues, and failure injection for NVRAM/PHY/chip callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/selftest.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/selftest.h

## Purpose
This header declares the self-test result layout and public self-test entry points for the top-level SFC driver variant. It is the contract between ethtool, RX delivery, open/close lifecycle code, and `selftest.c`.

## Important APIs, types, and functions
`struct efx_loopback_self_tests` stores per-TX-queue transmit counts plus aggregate good/bad RX counts for each loopback mode. `struct efx_self_tests` stores online results (`phy_alive`, `nvram`, `interrupt`, per-channel event queue DMA and interrupt results) and offline results (`memory`, `registers`, PHY extended test array, and loopback table).

The header declares `efx_loopback_rx_packet()`, `efx_selftest()`, `efx_selftest_async_init()`, `efx_selftest_async_start()`, and `efx_selftest_async_cancel()`.

## Control flow and integration
Ettool allocates and passes `struct efx_self_tests` to `efx_selftest()`, then formats its fields into ethtool result arrays. RX code reports loopback packets through `efx_loopback_rx_packet()`. Driver initialization initializes delayed self-test work, open schedules async tests, and stop/remove paths cancel them.

## State and persistence behavior
The structures are in-memory result containers. Non-counter fields use `1` for pass, `-1` for fail, and `0` for not run or unsupported. Array sizes are tied to `EFX_MAX_CHANNELS`, `EFX_MAX_TXQ_PER_CHANNEL`, `EFX_MAX_PHY_TESTS`, and `LOOPBACK_TEST_MAX`.

## Dependencies
It depends on `net_driver.h` for core NIC, channel, queue, and loopback constants. The ABI is internal to the driver, not a userspace UAPI, but ethtool output ordering depends on these fields matching the formatter.

## Risks
Changing array dimensions, field ordering assumptions, or pass/fail encoding without updating ethtool formatting can corrupt self-test output. `EFX_MAX_PHY_TESTS` must remain large enough for firmware-reported tests. Result arrays indexed by channel or TX label rely on driver bounds discipline.

## Test signals
Compilation catches most declaration mismatches. Runtime validation is ethtool self-test output with expected string count, stable ordering, and correct per-channel/per-loopback values across device configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/selftest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/Kconfig

## Purpose
This Kconfig file exposes the Solarflare SFC9000/Siena driver and optional feature switches to the kernel configuration system.

## Important configuration symbols
`SFC_SIENA` is the main tristate driver option. It depends on PCI and PTP clock support, and selects MDIO and CRC32. `SFC_SIENA_MTD` exposes onboard flash/EEPROM as MTD devices when MTD linkage is compatible. `SFC_SIENA_MCDI_MON` enables firmware-managed hardware monitor support with HWMON. `SFC_SIENA_SRIOV` enables SR-IOV support when PCI IOV is available. `SFC_SIENA_MCDI_LOGGING` enables sysfs-controlled MCDI command logging.

## Control flow and integration
Kconfig selections determine which objects the Siena Makefile includes and which conditional code paths compile in the driver. The dependency expressions avoid built-in driver code depending on modular MTD/HWMON code.

## State and persistence behavior
Configuration persists in the kernel build configuration. At runtime these options control whether MTD devices, hwmon devices, SR-IOV callbacks, and MCDI logging sysfs attributes exist.

## Dependencies
The file integrates with the kernel networking, PCI, PTP, MTD, HWMON, and PCI_IOV configuration hierarchy. `select MDIO` and `select CRC32` ensure required helper code is present for the driver.

## Risks
Incorrect dependency expressions can create link failures for built-in vs module combinations. Default-y optional features increase compiled surface area. Disabling MTD or logging removes maintenance/debug interfaces that operations may expect.

## Test signals
Build matrix coverage should include built-in and module `SFC_SIENA`, optional MTD/HWMON modular combinations, SR-IOV enabled/disabled, and MCDI logging enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/Makefile

## Purpose
This Makefile defines the object composition for the `sfc-siena` kernel module or built-in driver.

## Important build entries
`sfc-siena-y` aggregates the core Siena objects: farch/Siena hardware support, probe/lifecycle, common reset/datapath code, channel handling, NIC ops, TX/RX, self-test, ethtool, PTP, MCDI, port, and monitor support. `sfc-siena-$(CONFIG_SFC_SIENA_MTD)` conditionally adds `mtd.o`. `sfc-siena-$(CONFIG_SFC_SIENA_SRIOV)` conditionally adds `siena_sriov.o`. `obj-$(CONFIG_SFC_SIENA)` emits `sfc-siena.o`.

## Control flow and integration
The object list controls link-time availability of callbacks referenced by `efx.c`, `efx_common.c`, `ethtool.c`, and hardware type tables. Conditional objects align with Kconfig feature flags.

## State and persistence behavior
The Makefile has no runtime state; it defines the persistent build recipe for the kernel tree.

## Dependencies
It depends on Kbuild composite-object behavior and on Kconfig symbols from `Kconfig`. The object order must provide all symbols used by the driver when options are enabled or stubbed when disabled.

## Risks
Removing or conditionally hiding a required object creates unresolved symbols. Adding feature code without updating this file leaves it unbuilt. Object-name mismatches are easy to miss until kernel build time.

## Test signals
Kernel builds for `SFC_SIENA=y`, `SFC_SIENA=m`, and feature toggles are the main validation. `modinfo sfc-siena` and successful probe on hardware confirm the linked module contains expected init/exit and PCI ID table symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/bitfield.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/bitfield.h

## Purpose
This header provides the low-level bitfield manipulation layer used for Siena/Falcon-style NIC registers, descriptors, and MCDI/DMA words. It abstracts 32-, 64-, and 128-bit little-endian hardware quantities so field extraction and population work efficiently on 32-bit and 64-bit hosts.

## Important APIs, types, and macros
It defines `efx_dword_t`, `efx_qword_t`, and `efx_oword_t` as little-endian unions. Field metadata macros such as `EFX_LOW_BIT`, `EFX_WIDTH`, `EFX_HIGH_BIT`, `EFX_MASK32`, and `EFX_MASK64` derive masks and offsets from generated field constants.

Extraction macros include `EFX_DWORD_FIELD`, `EFX_QWORD_FIELD`, and `EFX_OWORD_FIELD`, with 32/64 variants selected by `BITS_PER_LONG`. Population macros include `EFX_POPULATE_DWORD_*`, `EFX_POPULATE_QWORD_*`, `EFX_POPULATE_OWORD_*`, `EFX_ZERO_*`, and `EFX_SET_*`. Read-modify-write helpers include `EFX_SET_*_FIELD`, `EFX_AND_*`, `EFX_OR_OWORD`, and `EFX_INVERT_OWORD`.

## Control flow
There is no executable control flow; preprocessor expansion computes extract/insert expressions over little-endian array elements. Variadic-style numbered wrappers pad unspecified fields with `EFX_DUMMY_FIELD`, allowing callers to populate up to 19 fields with a common primitive.

## State and persistence behavior
The header manipulates caller-owned in-memory register or descriptor images. It does not persist state, allocate memory, or perform MMIO by itself.

## Dependencies and integration points
It depends on Linux endian types/conversion helpers and generated field naming conventions ending in `_LBN` and `_WIDTH`. It is consumed by NIC register access, descriptor construction, MCDI command layout, and debug formatting code.

## Risks
Field width and shift boundaries are the primary risk. Misdeclared `_LBN`/`_WIDTH` constants silently extract or insert the wrong bits. Callers must respect maximum mask widths and little-endian storage. Since many macros evaluate arguments in expressions, side-effectful arguments are unsafe. Architecture-dependent 32/64 selections must produce identical hardware images.

## Test signals
Build coverage across 32-bit and 64-bit architectures, sparse/endian checking, descriptor/register unit tests where available, and hardware smoke tests for TX/RX/event descriptor correctness are the strongest signals. Debug register dumps using `EFX_*_FMT` should match hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/bitfield.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx.c

## Purpose
This is the Siena driver's main module, PCI, netdev, and top-level lifecycle implementation. It probes supported Solarflare PCI IDs, allocates and registers `net_device` instances, configures NIC/port/channel resources, wires Linux netdev operations, handles XDP and PTP entry points, manages SR-IOV hooks, and implements suspend/resume/remove paths.

## Important APIs, types, and functions
Module parameters include interrupt mode, RSS CPU count, separate TX channels, PHY flash mode, and debug mask. `efx_pci_driver` binds the PCI probe/remove/shutdown/PM/error handlers. `efx_netdev_ops` wires open, stop, transmit, stats, ioctl, MTU, MAC, RX mode, features, VLAN, hwtstamp, SR-IOV, physical port, TC, RFS, XDP xmit, and BPF setup.

Key functions include `efx_probe_all()`, `efx_remove_all()`, `efx_pci_probe()`, `efx_pci_probe_main()`, `efx_pci_probe_post_io()`, `efx_pci_remove()`, `efx_net_open()`, `efx_net_stop()`, `efx_register_netdev()`, `efx_unregister_netdev()`, `efx_xdp_setup_prog()`, `efx_siena_init_irq_moderation()`, and PM helpers `efx_pm_freeze()`, `efx_pm_thaw()`, `efx_pm_poweroff()`, `efx_pm_resume()`, and `efx_pm_suspend()`.

## Control flow
Probe allocates an etherdev with queue capacity, initializes common driver state, maps PCI BAR/DMA through `efx_siena_init_io()`, then calls the main probe sequence. The main sequence probes NIC type resources, port, optional vswitching, filters, channels, NAPI, hardware init, port init, interrupts, affinity, and interrupt enablement. Post-I/O setup publishes netdev features, registers the netdev, optionally creates MTDs, and pushes UDP tunnel ports.

Open verifies the device is not disabled or in PHY special mode, handles pending MC reboot reset, publishes initial link state, starts all datapath/port work, detaches if a reset intervened, and starts async self-test. Stop calls `efx_siena_stop_all()`. Remove closes the netdev under RTNL, disables interrupts, unregisters netdev/sysfs, removes MTDs, tears down hardware/software resources, unmaps I/O, frees common state, and frees the netdev.

## State and persistence behavior
The file owns module-wide primary/secondary association lists keyed by VPD serial number. Per-NIC state transitions include `STATE_UNINIT`, `STATE_READY`, and disabled/recovery states delegated to common reset code. Runtime state includes netdev feature flags, XDP program RCU pointer, channel names, IRQ moderation values, VPD serial string, sysfs `phy_type`, and MCDI logging setup. No disk persistence is performed.

## Dependencies and integration points
It integrates Linux PCI, netdev, ethtool, BPF/XDP, PTP timestamping, VLAN, RFS, SR-IOV, MTD, MCDI, and firmware-specific `struct efx_nic_type` callbacks. It delegates datapath details to TX/RX/channel/common modules and hardware-specific Siena/Farch code.

## Risks
Probe and remove ordering is the main risk: interrupts, NAPI, filters, MTD, SR-IOV, and netdev registration must be undone in the exact reverse order on every failure path. XDP program replacement relies on RTNL/RCU and MTU bounds. Retry-on-probe failure can mask transient hardware-reset problems but must clear `reset_pending` carefully. Association lists are global and rely on RTNL serialization during netdev registration/removal. PM paths must not restart a disabled device.

## Test signals
Signals include successful module load/unload, PCI bind/unbind, netdev registration, interface up/down, traffic, XDP attach/xmit, ethtool feature visibility, MTD creation when enabled, SR-IOV configuration when enabled, suspend/resume, shutdown, and hot-remove/error-injection tests. Probe failure injection should verify every cleanup label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx.h

## Purpose
This header exposes Siena driver internal APIs shared across TX, RX, filters, ethtool, MTD, XDP, and common lifecycle code.

## Important APIs and definitions
It declares TX entry points (`efx_siena_hard_start_xmit()`, `__efx_siena_enqueue_skb()`, queue init, TC setup), RX delivery (`efx_siena_rx_packet()`, `__efx_siena_rx_packet()`, `efx_rx_flush_packet()`), queue sizing constants, RSS/filter wrappers, ethtool ops, IRQ moderation APIs, software stats update, optional MTD helpers, SR-IOV VF sizing, device detach/attach helpers, reset-lock assertion helper, and `efx_siena_xdp_tx_buffers()`.

Inline wrappers dispatch through `efx->type` where NIC families provide callbacks, including TX enqueue and filter operations.

## Control flow and integration
Most functions are implemented in sibling `.c` files and called from `efx.c`, `efx_common.c`, ethtool, TX/RX, and channel code. The inline `efx_enqueue_skb()` uses indirect-call optimization to route through the NIC type's TX enqueue implementation. Filter wrappers are safe public internal entry points for ethtool and RX mode code.

## State and persistence behavior
No state is stored in the header. Helpers act on `struct efx_nic`, channel, queue, filter, XDP, or netdev state owned elsewhere.

## Dependencies
The header depends on `net_driver.h`, `filter.h`, MCDI RSS constants, and Linux indirect-call support. Optional sections depend on `CONFIG_SFC_SIENA_MTD` and `CONFIG_SFC_SIENA_SRIOV`.

## Risks
Inline wrappers assume corresponding `efx->type` callbacks are valid. Queue sizing macros must remain aligned with hardware ring behavior and TX descriptor accounting. Device detach/attach helpers must be used around disruptive operations to avoid TX scheduler races.

## Test signals
Compile coverage across optional configs is essential. Runtime signals include successful TX/RX, ethtool filter operations, queue resizing, XDP transmit, MTD presence/absence by config, and reset or MTU-change flows using detach/attach helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_channels.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_channels.c

## Purpose
This file manages Siena interrupt mode selection, MSI-X/MSI/legacy interrupt resources, channel allocation, event queue lifecycle, XDP TX queue placement, queue resizing, start/stop of channels, and NAPI polling.

## Important APIs, types, and functions
Public APIs include `efx_siena_probe_interrupts()`, `efx_siena_remove_interrupts()`, `efx_siena_enable_interrupts()`, `efx_siena_disable_interrupts()`, `efx_siena_set_interrupt_affinity()`, `efx_siena_clear_interrupt_affinity()`, `efx_siena_init_channels()`, `efx_siena_probe_channels()`, `efx_siena_set_channels()`, `efx_siena_realloc_channels()`, `efx_siena_start_channels()`, `efx_siena_stop_channels()`, `efx_siena_init_napi()`, and `efx_siena_fini_napi()`.

Internal helpers count online cores, determine RSS parallelism, allocate MSI-X channels, probe/init/fini/remove event queues, allocate/copy/probe/remove channels, assign XDP TX queue lookup entries, process event queues, adapt IRQ moderation, and implement the NAPI poll callback.

## Control flow
Interrupt probing prefers MSI-X, falls back to MSI, then legacy if allowed by the NIC type. MSI-X allocation computes RX/TX channel counts, optional separate TX channels, extra channels, and XDP TX event queue mode (dedicated, shared, or borrowed). Channel probing allocates event queues, TX queues, and RX queues, in reverse channel order to preserve buffer table layout for extra channels.

Start initializes TX/RX queues and pushes RX descriptors. Stop disables RX refill, drains NAPI by stopping/starting event queues for RX channels, flushes DMA queues through hardware callbacks, then finalizes RX/TX queues. NAPI polling processes event queues, flushes coalesced RX packets, refills RX descriptors, updates BQL completions, delivers skb lists, flushes XDP actions, and acknowledges event queue reads when complete.

## State and persistence behavior
Persistent runtime state includes `efx->n_channels`, RX/TX channel counts, `tx_channel_offset`, `xdp_channel_offset`, `xdp_tx_queues`, per-channel IRQ numbers, event queue buffers/read pointers, NAPI state, RX/TX queue indices, adaptive IRQ moderation counters, and active queue counts. There is no on-disk persistence.

## Dependencies and integration points
The file depends on PCI MSI/MSI-X APIs, CPU masks and topology, NAPI, TX/RX queue modules, NIC event/interrupt callbacks, MCDI async mode switching, SR-IOV constraints, RFS acceleration, and XDP flush semantics.

## Risks
Resource accounting is complex around MSI-X vector count, VIs, XDP queues, and separate TX/RX channels. Queue reallocation must clone only copyable channels, preserve buffer table entries for non-copyable channels, and roll back safely. Interrupt disable must synchronize IRQs before tearing down event queues. NAPI and event queue enabled flags rely on memory barriers. XDP borrowed queues can reduce performance and must map every CPU to a valid TX queue.

## Test signals
Test MSI-X, MSI, and legacy fallback; RSS CPU counts; separate TX channel mode; XDP dedicated/shared/borrowed queue modes; ethtool ring resize rollback; interface up/down loops; NAPI traffic under RX/TX load; RFS expiry; interrupt affinity on NUMA systems; and reset while channels are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_channels.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_channels.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_channels.h

## Purpose
This header declares the channel, interrupt, event queue, and NAPI management API used by Siena probe, reset, ethtool ring sizing, and datapath lifecycle code.

## Important APIs
It exposes module parameters `efx_siena_interrupt_mode` and `efx_siena_rss_cpus`, interrupt probe/enable/disable/remove functions, interrupt affinity functions, event queue start/stop, channel realloc/init/probe/set/remove/fini/start/stop, NAPI init/fini, and a dummy channel operation.

## Control flow and integration
`efx.c` calls probe/remove/enable/disable functions during PCI lifecycle. `efx_common.c` calls start/stop channels from datapath start/stop and reset flows. Ettool ring changes call `efx_siena_realloc_channels()`. Event queue start/stop is also used by self-tests and RX-drain logic.

## State and persistence behavior
No state is stored in the header. The declared functions mutate `struct efx_nic` and `struct efx_channel` state.

## Dependencies
It depends on core driver types from `net_driver.h` included by implementation users. The declarations are specific to Siena naming and should match implementations in `efx_channels.c`.

## Risks
Callers must respect lifecycle order: interrupts must be probed before enabled, NAPI initialized before event queues are started, and channels stopped before removal. Misordered calls can race with IRQ/NAPI handlers.

## Test signals
Compile-time declaration checks plus runtime interface open/close, reset, channel resize, and interrupt self-test coverage validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_channels.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_common.c

## Purpose
This file implements common Siena runtime behavior: reset workqueue management, MAC reconfiguration, link notifications, MTU/XDP bounds, monitor work, datapath start/stop, port start/stop, statistics, reset down/up orchestration, common structure/I/O initialization, optional MCDI logging sysfs, PCI error recovery, encapsulated offload feature checks, and physical port identity helpers.

## Important APIs, types, and functions
Major exported functions include `efx_siena_create_reset_workqueue()`, `efx_siena_queue_reset_work()`, `efx_siena_destroy_reset_workqueue()`, `efx_siena_mac_reconfigure()`, `efx_siena_set_mac_address()`, `efx_siena_set_rx_mode()`, `efx_siena_set_features()`, `efx_siena_link_status_changed()`, `efx_siena_xdp_max_mtu()`, `efx_siena_change_mtu()`, `efx_siena_start_all()`, `efx_siena_stop_all()`, `efx_siena_net_stats()`, `efx_siena_reconfigure_port()`, `efx_siena_reset_down()`, `efx_siena_reset_up()`, `efx_siena_reset()`, `efx_siena_schedule_reset()`, `efx_siena_init_struct()`, `efx_siena_fini_struct()`, `efx_siena_init_io()`, `efx_siena_fini_io()`, and PCI error handlers.

It also defines reset and loopback string tables used by logging and ethtool formatting.

## Control flow
`start_all` exits unless the netdev should run and no reset is pending. It starts the port, computes RX buffer geometry, starts channels, starts PTP datapath, wakes TX queues, schedules monitor work, polls link, and starts stats. `stop_all` pulls/stops stats, stops port work, disables TX queues, stops PTP and channels, and leaves link state controlled by higher layers.

Reset scheduling maps reset reasons to methods, sets `reset_pending`, switches MCDI to polling mode, and queues a serialized work item if the NIC is ready. Reset work may wait for BIST or let EEH handle recovery, then takes RTNL and calls `efx_siena_reset()`. Reset detaches the device, tears down datapath/interrupts/hardware under MAC and filter locks, calls the NIC reset callback, clears covered pending bits, restores hardware, filters, SR-IOV, UDP tunnel ports, and either restarts or disables the netdev.

## State and persistence behavior
Persistent runtime state includes reset workqueue, `reset_pending` bitset, NIC state, port/datapath enable flags, link state counters, flow control advertising, RX buffer geometry, netdev feature flags, stats, workqueue/delayed work, PCI BAR mapping, VPD serial, MCDI logging sysfs state, and PCI recovery state. No disk persistence is performed.

## Dependencies and integration points
The file depends on netdev, PCI, DMA, workqueue, RTNL, MCDI, PHY, filter, TX/RX/channel, PTP, and NIC type callbacks. It is the main coordinator for `efx.c`, `efx_channels.c`, ethtool, and hardware-specific Siena/Farch code.

## Risks
The reset path holds locks across hardware teardown and must always release them in `reset_up`, including failure paths. Start/stop operations rely on RTNL serialization and correct `port_enabled` state. MTU changes must reject active XDP configurations that cannot fit in a page. PCI error recovery must not touch MMIO after permanent failure. Encapsulated offload checks are conservative and can disable offloads for packets with extension headers.

## Test signals
Signals include ifup/ifdown with traffic, MTU changes with and without XDP, MAC/promiscuous/multicast changes, link up/down logs, stats consistency, reset injection for watchdog/DMA/MCDI timeout, EEH/PCI error recovery, suspend/resume, MCDI logging sysfs toggling, and encapsulated tunnel offload validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_common.h

## Purpose
This header declares common Siena lifecycle, reset, datapath, port, stats, feature, PCI error, and utility APIs shared by the main module, channels, ethtool, and hardware-specific code.

## Important APIs and definitions
It declares common init/fini (`efx_siena_init_struct()`, `efx_siena_init_io()`), queue size constants, flow-control helpers, `start_all`/`stop_all`, netdev stats, reset workqueue functions, monitor start, port reconfiguration, reset down/up/reset/schedule, dummy port ops, disabled-device checks, NAPI scheduling helpers, optional MCDI logging hooks, MAC/RX mode/feature/MTU/phys-port APIs, PCI error handlers, and encapsulated feature check.

## Control flow and integration
`efx.c` uses these declarations during PCI probe/remove/open/stop/PM. Ettool uses reset, feature, and stats functions. Channel and NIC code use scheduling helpers and reset assertions. Optional MCDI logging compiles to real sysfs helpers or inline no-ops depending on config.

## State and persistence behavior
No state is stored in the header. Inline helpers read or mutate NIC state, including disabled checks, channel event-test CPU, NAPI scheduling, and netdev attach/detach.

## Dependencies
It depends on core driver structures, Linux netdev/PCI types, and `enum reset_type`. The queue constants must stay aligned with hardware limits used in channel and ethtool code.

## Risks
The `EFX_ASSERT_RESET_SERIALISED` macro documents locking expectations but cannot prevent all misuse. Calling lifecycle functions without RTNL or the expected locks can race with reset/open/close. Inline scheduling helpers assume channel/NAPI objects are initialized.

## Test signals
Compile coverage across MCDI logging configs, plus runtime reset, open/close, MTU, feature toggling, stats, and PCI error paths validate the declared contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/enum.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/enum.h

## Purpose
This header defines core Siena driver enumerations and bitmask helpers for loopback modes and reset types.

## Important APIs and definitions
`enum efx_loopback_mode` enumerates no-loopback, datapath/MAC/controller loopbacks, PHY loopbacks, external/cross-port loopbacks, and wireside loopbacks. `LOOPBACK_TEST_MAX` limits test iteration to `LOOPBACK_PMAPMD`. Masks such as `LOOPBACKS_INTERNAL`, `LOOPBACKS_WS`, `LOOPBACKS_EXTERNAL()`, `LOOPBACK_MASK()`, `LOOPBACK_INTERNAL()`, `LOOPBACK_EXTERNAL()`, `LOOPBACK_CHANGED()`, and `LOOPBACK_OUT_OF()` classify modes.

`enum reset_type` defines reset scopes and reasons, separating ordered reset methods (`INVISIBLE`, `ALL`, `WORLD`, `DATAPATH`, `DISABLE`, etc.) from reasons such as TX watchdog, DMA error, MC failure, and MCDI timeout.

## Control flow and integration
Loopback definitions drive MCDI link configuration, self-test loopback iteration, ethtool self-test naming, and MAC/PHY reconfiguration logic. Reset types drive reset scheduling, mapping from hardware error reasons to reset methods, pending-bit clearing, and log messages.

## State and persistence behavior
The header stores no runtime state. Its numeric values are persisted only as compiled constants and bit positions in runtime masks such as `efx->loopback_modes` and `efx->reset_pending`.

## Dependencies
It is included by core driver headers and must remain consistent with firmware MCDI loopback mode numbering and string tables in `efx_common.c`.

## Risks
Changing enum numeric values breaks firmware protocol mapping, bit masks, ethtool output, and reset-pending semantics. `RESET_TYPE_MCDI_TIMEOUT` is explicitly outside the ordered scope hierarchy, so generic reset-bit logic must treat it specially.

## Test signals
Build-time users catch missing enum names. Runtime signals include correct loopback self-test modes, correct loopback names in ethtool output, and reset logs/pending-bit behavior for each reset reason.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/enum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ethtool.c

## Purpose
This file defines the Siena driver's `struct ethtool_ops` table and implements Siena-specific operations not shared in `ethtool_common.c`, such as LED identification, register dumps, coalescing, ring sizing, Wake-on-LAN, FEC stats, and timestamp info.

## Important APIs and functions
`efx_siena_ethtool_ops` is exported through `efx.h` and assigned to `net_dev->ethtool_ops` during registration. Helpers include `efx_ethtool_phys_id()`, `efx_ethtool_get_regs_len()`, `efx_ethtool_get_regs()`, `efx_ethtool_get_coalesce()`, `efx_ethtool_set_coalesce()`, `efx_ethtool_get_ringparam()`, `efx_ethtool_set_ringparam()`, `efx_ethtool_get_wol()`, `efx_ethtool_set_wol()`, `efx_ethtool_get_fec_stats()`, and `efx_ethtool_get_ts_info()`.

## Control flow
Coalescing reads current IRQ moderation from common code, accepts both standard and legacy IRQ fields, validates shared-channel constraints through `efx_siena_init_irq_moderation()`, then pushes moderation to every channel. Ring sizing validates RX/TX bounds and calls `efx_siena_realloc_channels()`. The ops table delegates most stats, tests, link, FEC, RSS, filter, reset, and module EEPROM operations to `ethtool_common.c`.

## State and persistence behavior
Runtime state changed includes channel IRQ moderation, RX/TX queue entry counts after ring resize, WOL options through NIC callbacks, and LED state during physical identification. No disk persistence is performed.

## Dependencies and integration points
It depends on Linux ethtool APIs, NIC register helpers, MCDI LED and PTP helpers, common channel reallocation and IRQ moderation, TX descriptor sizing, and NIC type callbacks for WOL/FEC/registers.

## Risks
Coalescing compatibility behavior can surprise callers because standard and IRQ fields alias the same hardware timer. Ring resizing disrupts datapath and must roll back through channel code. Register dumps depend on NIC revision-specific formatting. WOL/FEC operations require valid NIC callbacks.

## Test signals
Run `ethtool -c/-C`, `-g/-G`, `-d`, `-p`, `-s wol`, FEC stats, timestamp info, and full ethtool ops enumeration. Ring resizing under traffic and with XDP active is especially important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ethtool_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ethtool_common.c

## Purpose
This file implements shared Siena ethtool behavior: driver info, debug mask, pause parameters, self-tests, statistics and string sets, link settings, FEC parameters, RX classifier rules, RSS hash configuration, reset, and module EEPROM/info access.

## Important APIs, types, and functions
`struct efx_sw_stat_desc` describes software stats sources and offsets. Public functions include `efx_siena_ethtool_get_drvinfo()`, message-level getters/setters, pause getters/setters, `efx_siena_ethtool_self_test()`, stats string/count/data functions, link ksettings getters/setters, FEC parameter getters/setters, RX NFC getters/setters, RSS indirection/key getters/setters, `efx_siena_ethtool_reset()`, and module EEPROM/info functions.

Internal helpers format self-test strings/results (`efx_fill_test()`, `efx_fill_loopback_test()`, `efx_ethtool_fill_self_tests()`), describe per-queue stats, translate filter specs to ethtool flow rules, and translate ethtool flow rules back to driver filter specs.

## Control flow
Self-test handling allocates a result structure, opens the device temporarily if needed to ensure RX buffers and interrupts exist, calls `efx_siena_selftest()`, closes if it opened the device, and fills ethtool data arrays. Stats handling first pulls hardware stats under `stats_lock`, then accumulates software, per-TX, per-RX, XDP TX, and PTP stats.

RX classifier get operations read manual-priority filter IDs/specs and translate exact supported match forms to ethtool rules. Set operations validate exact masks for IPv4/IPv6/TCP/UDP/user/Ether flows, optional VLAN extension and RSS, initialize an `efx_filter_spec`, and insert or remove filters through safe wrappers. RSS get pulls hardware config, then returns Toeplitz hash, indirection table, and key; RSS set validates hash function and pushes updated config.

## State and persistence behavior
Runtime state includes `efx->msg_enable`, `wanted_fc` and link advertising, netdev open state during self-test, stats arrays/counters, manual filter table entries, RSS context indirection/key, reset pending effects via reset call, and module EEPROM reads through PHY/MCDI. No file persistence exists.

## Dependencies and integration points
It depends on ethtool core types, MCDI firmware helpers, PHY/link/FEC/module EEPROM helpers, filter APIs, PTP stats, RX/TX/channel structures, `selftest.h`, and NIC type callbacks for stats/RSS/filter operations.

## Risks
Self-tests can open a down interface and offline tests can disrupt traffic. Stats string counts must exactly match stats data ordering. Classifier mask validation is strict; unsupported masks correctly fail but can surprise users. Filter insertion with `replace_equal=true` may replace existing equal-priority filters. RSS operations assume an active context and NIC callback correctness. Pause-setting rollback is limited if port reconfiguration fails after partial state change.

## Test signals
Signals include ethtool self-test string/data count consistency, stats count/string/data alignment, pause parameter changes, link setting/FEC get/set, RX classifier add/list/delete for IPv4/IPv6/TCP/UDP/Ether/VLAN/drop/RSS flows, RSS table/key get/set, reset through ethtool, and module EEPROM reads under `mac_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ethtool_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ethtool_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ethtool_common.h

## Purpose
This header declares the shared Siena ethtool implementation used by the concrete ethtool ops table in `ethtool.c`.

## Important APIs
The header declares driver info, message level, self-test, pause, string set count, string retrieval, stats retrieval, link ksettings, FEC parameters, RX NFC/filter operations, RX ring count, RSS indirection/key get/set, RSS hash fields, ethtool reset, and module EEPROM/info functions.

## Control flow and integration
`ethtool.c` binds these functions into `efx_siena_ethtool_ops`. Implementations in `ethtool_common.c` call into self-test, MCDI PHY, filter, RSS, stats, and reset subsystems.

## State and persistence behavior
The header itself stores no state. Declared functions mutate or read NIC runtime state, firmware state, filters, RSS context, and stats through their implementations.

## Dependencies
It depends on Linux netdev and ethtool types. Callers must provide a Siena `net_device` whose private data is `struct efx_nic`.

## Risks
Prototype drift from `struct ethtool_ops` API changes causes build failures. Any function added to the ops table must have a declaration here if shared across files. Locking expectations are implementation-specific and must be preserved by callers.

## Test signals
Compile coverage against the target kernel ethtool API and runtime invocation of every bound ethtool operation validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ethtool_common.h -->
