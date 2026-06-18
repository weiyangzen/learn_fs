# Research: subset-b-005887

This grouped report covers the exact source files assigned to work item `subset-b-005887`. Each section preserves the source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm97xx.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm97xx.h

## Purpose
This compact MFD interface header defines the platform-data handoff for WM97xx AC97 companion devices. It does not implement behavior; it provides the shared contract that lets board or parent MFD code pass an AC97 codec handle, a regmap, and optional battery platform data to child drivers.

## Important APIs, Types, And Functions
The only exported type is `struct wm97xx_platform_data`. Its fields are `struct snd_ac97 *ac97`, `struct regmap *regmap`, and `struct wm97xx_batt_pdata *batt_pdata`. The header forward-declares all three dependent structures and intentionally avoids including the full AC97, regmap, or battery headers.

## Control Flow
There is no executable control flow in this header. Runtime behavior is established by users that allocate/populate `wm97xx_platform_data` before child-device registration, after which consumer drivers dereference the pointers according to their own probe path.

## State And Persistence
The state is pointer-owned externally. The header does not define lifetime rules, reference counting, or persistence; callers must keep `ac97`, `regmap`, and `batt_pdata` valid for the lifetime of consumers.

## Dependencies And Integration Points
It integrates the MFD layer with sound AC97 codec support, regmap-backed register access, and WM97xx battery support. The include guard prevents duplicate declarations and keeps the dependency footprint low.

## Risks
The main risk is lifetime mismatch or partially initialized platform data because the structure does not encode ownership. A missing `regmap` or stale `snd_ac97` pointer would fail only in the consuming driver.

## Test Signals
Useful signals are probe success for WM97xx child devices, valid regmap accesses, AC97 codec operations, and battery child-device registration when `batt_pdata` is supplied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm97xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mhi.h -->
# sources/distributed-fs/ceph-client/include/linux/mhi.h

## Purpose
This header is the public host-side API for the MHI bus framework. It defines controller configuration, MHI device and client driver objects, state and execution-environment enums, transfer flags, and lifecycle/transfer APIs used by bus controller drivers and MHI client drivers.

## Important APIs, Types, And Functions
Core enums include `mhi_callback`, `mhi_flags`, `mhi_device_type`, `mhi_ch_type`, `mhi_ee_type`, `mhi_state`, channel EE masks, event-ring data type, and doorbell burst mode. `struct mhi_channel_config`, `struct mhi_event_config`, and `struct mhi_controller_config` describe controller topology. `struct mhi_controller` is the central state object containing MMIO register bases, IOVA window, firmware/RDDM image data, channel/event/command contexts, power-management locks, transition work, execution environment, callbacks, IRQ information, bounce-buffer state, and controller-specific register/map/reset hooks. `struct mhi_device`, `struct mhi_result`, and `struct mhi_driver` define the client-facing bus device, transfer completion result, and driver callbacks.

Key APIs allocate/register/unregister controllers (`mhi_alloc_controller`, `mhi_register_controller`, `mhi_unregister_controller`), register/unregister drivers (`mhi_driver_register`, `mhi_driver_unregister`), run power transitions (`mhi_prepare_for_power_up`, `mhi_async_power_up`, `mhi_sync_power_up`, `mhi_power_down`, `mhi_pm_suspend`, `mhi_pm_resume`, `mhi_pm_resume_force`), manage runtime device wake (`mhi_device_get_sync`, `mhi_device_put`), prepare channels (`mhi_prepare_for_transfer`, `mhi_unprepare_from_transfer`), queue buffers or SKBs, inspect queue capacity, force/download RDDM, reset, and read state.

## Control Flow
Controller drivers allocate and fill required `mhi_controller` fields, provide bus-specific callbacks, then register with a `mhi_controller_config`. Power-up prepares contexts, downloads firmware when configured, transitions through READY/BHI/M0-style states, creates channel devices, and dispatches client probes. Client drivers bind through `mhi_driver`, prepare channels, queue buffers or SKBs, and receive transfer and status callbacks. Power-down and suspend paths reset/retain channel devices depending on the selected API.

## State And Persistence
The controller owns persistent per-controller state: register mappings, IOVA bounds, firmware image references, channel/event/command arrays, PM state, execution environment, transition list, wake counters, pending packet counts, and workqueue state. Locks (`pm_mutex`, `pm_lock`, `transition_lock`, `wlock`) protect state transitions and wake handling. Firmware/RDDM buffers persist across relevant boot or crash-dump phases until unprepare/free.

## Dependencies And Integration Points
The header depends on Linux device model, DMA direction, mutex/spinlock/waitqueue/workqueue primitives, SKBs, and slab allocation. Integration points are PCI or other physical bus controller drivers, MHI client drivers, firmware loading, runtime PM, debugfs, DMA/IOMMU mapping, IRQ handling, and panic/RDDM recovery.

## Risks
Risks center on incorrect required callback population, MMIO/IOMMU range mistakes, PM races, invalid channel/event-ring configuration, wake reference leaks, execution-environment mismatches, and queueing buffers without prepared channels. `mhi_pm_resume_force()` explicitly tolerates devices outside the spec's expected M3 state, so tests must cover device-specific resume quirks.

## Test Signals
Validate controller registration, sync and async power-up, firmware boot, EE/state reads, channel probe/remove, buffer and SKB transfer callbacks, queue-full reporting, suspend/resume including forced resume, RDDM download paths, graceful and ungraceful power-down, IRQ/event delivery, and callback sequencing under concurrent PM activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mhi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mhi_ep.h -->
# sources/distributed-fs/ceph-client/include/linux/mhi_ep.h

## Purpose
This header defines the endpoint-side MHI framework interface. It lets endpoint controller drivers expose MHI registers, host-memory access callbacks, doorbell handling, workqueues, context caches, and endpoint client devices/drivers.

## Important APIs, Types, And Functions
`MHI_EP_DEFAULT_MTU` sets the default endpoint MTU. `struct mhi_ep_channel_config` and `struct mhi_ep_cntrl_config` describe endpoint-supported channels and controller limits. `struct mhi_ep_db_info` tracks doorbell interrupt mask/status. `struct mhi_ep_buf_info` describes host/endpoint transfer buffers and optional async completion callbacks. `struct mhi_ep_cntrl` is the endpoint controller object, holding MMIO, channel/event/command structures, state machine pointer, cached host contexts and physical addresses, doorbell state, locks, transition and channel-doorbell lists, workqueue/work items, slab caches, IRQ callback, host memory map/read/write callbacks, MHI state, channel/event counts, doorbell offsets, index, IRQ, and enabled state. `struct mhi_ep_device` and `struct mhi_ep_driver` mirror the host-side device/driver model for endpoint clients.

Public APIs register/unregister endpoint drivers and controllers, power the endpoint stack up/down, test transfer queue emptiness, and queue SKBs to the host.

## Control Flow
An endpoint controller fills `mhi_ep_cntrl`, registers it with channel configuration, then powers up. Host doorbells and state transitions are serialized through the endpoint workqueue: state, reset, command-ring, and channel-ring workers consume list entries and context caches. Endpoint client drivers bind to channel devices, receive UL/DL callbacks, and queue DL SKBs back to the host.

## State And Persistence
Persistent state includes cached host channel/event/command contexts, mapped endpoint memory for host contexts, doorbell status, state transition lists, workqueue state, slab caches, controller state, and enabled flag. Mutexes protect event rings and state transitions; `list_lock` protects transition and doorbell lists.

## Dependencies And Integration Points
It depends on DMA direction and the host-side MHI definitions from `linux/mhi.h`. It integrates with endpoint PCI or similar controllers that can map host physical addresses, raise host IRQs, read/write host memory synchronously and asynchronously, and expose MHI client devices.

## Risks
The highest risks are host-address mapping lifetime errors, async transfer callback ordering, doorbell-list races, stale host context caches, and mismatched channel direction semantics. Controller callbacks are mandatory for real data movement but are only typed here, so registration-time validation is critical.

## Test Signals
Exercise controller registration, power-up/down, host doorbell interrupt delivery, command-ring processing, channel-ring UL/DL transfers, async completion callbacks, SKB queueing, queue-empty checks, reset worker behavior, and teardown with outstanding mapped host buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mhi_ep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/micrel_phy.h -->
# sources/distributed-fs/ceph-client/include/linux/micrel_phy.h

## Purpose
This header centralizes Micrel/Microchip KSZ/LAN PHY IDs, PHY ID masks, device flags, and selected vendor-specific register/bit definitions used by PHY drivers and board code.

## Important APIs, Types, And Functions
It exports constants such as `MICREL_OUI`, `MICREL_PHY_ID_MASK`, many `PHY_ID_*` values for KSZ8xxx/KSZ9xxx/LAN88xx/LAN9645X devices, `MICREL_PHY_50MHZ_CLK`, `MICREL_PHY_FXEN`, `MICREL_KSZ8_P1_ERRATA`, KSZ9021 extended-register addresses, and KSZ886X BMCR/control bits for MDI-X, far-end fault, transmit, LED, force link, power save, and loopback behavior.

## Control Flow
There is no runtime control flow. PHY drivers include this header to match `phy_device` IDs and interpret or modify vendor registers during probe, config init, link setup, and diagnostics.

## State And Persistence
The file defines no storage. The constants affect persistent hardware state only when drivers write the referenced PHY registers or set `phy_device->dev_flags`.

## Dependencies And Integration Points
It expects generic bit macros such as `BIT()` from the broader kernel include environment. It integrates with phylib match tables, Micrel/Microchip PHY drivers, MDIO register access, and board/device-tree code that sets PHY flags.

## Risks
PHY ID aliasing is intentional for some parts, so overly specific matching can bind the wrong quirk. Vendor register writes can alter link mode, MDI-X, power saving, or LED behavior and should be gated by the correct PHY family.

## Test Signals
Test signals include correct PHY driver binding, MDIO reads matching expected IDs under `MICREL_PHY_ID_MASK`, link negotiation across MDI/MDI-X modes, KSZ9021 pad skew programming, and regression checks for shared IDs such as KSZ8001/KS8721 and KSZ8081/KS8091.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/micrel_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/microchipphy.h -->
# sources/distributed-fs/ceph-client/include/linux/microchipphy.h

## Purpose
This header defines Microchip LAN88xx/LAN78xx PHY register offsets and bit masks for interrupts, extended page access, MDIX mode, chip ID/revision MMD registers, LED/control fields, downshift, and DSP tuning.

## Important APIs, Types, And Functions
Important constants include `LAN88XX_INT_MASK`, `LAN88XX_INT_STS`, all interrupt mask/status bits, `LAN88XX_EXT_PAGE_ACCESS` and page selectors, `LAN88XX_EXT_MODE_CTRL` MDIX masks and values, MMD3 chip ID/revision registers, `LAN78XX_PHY_LED_MODE_SELECT`, `LAN78XX_PHY_CTRL3` downshift controls, and Ardennes DSP page/test register constants.

## Control Flow
No executable control flow is defined. Drivers use these constants in MDIO read/modify/write sequences for interrupt setup, interrupt acknowledgement, page switching, MDIX control, LED mode setup, downshift configuration, and DSP workarounds.

## State And Persistence
State is hardware-resident in PHY registers. Page-selection state is especially important because writes after changing `LAN88XX_EXT_PAGE_ACCESS` affect different register banks until restored.

## Dependencies And Integration Points
The header relies on kernel bit helpers such as `BIT()` and `GENMASK()`. It integrates with Microchip PHY drivers, LAN7800/LAN7850 embedded PHY handling, MDIO/MMD access helpers, interrupt handlers, and ethtool link diagnostics.

## Risks
Risks include leaving the PHY on the wrong extended page, confusing similarly named interrupt mask/status bits, accidentally clearing latched interrupt state, and applying LAN78xx or Ardennes-specific settings to an incompatible device.

## Test Signals
Validate interrupt enable/status behavior, link-change and autoneg-done IRQs, MDIX mode switching, chip ID/revision reads via MMD3, downshift configuration, LED mode behavior, and DSP workaround application on the intended PHY revisions only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/microchipphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/migrate.h -->
# sources/distributed-fs/ceph-client/include/linux/migrate.h

## Purpose
This header exposes the memory-management page and folio migration interface, including generic migration callbacks, CONFIG-gated fallbacks, NUMA balancing migration hooks, and device-private/device-coherent VMA migration helpers.

## Important APIs, Types, And Functions
It defines callback typedefs `new_folio_t` and `free_folio_t`, `struct movable_operations` for driver-managed movable pages, and the external `migrate_reason_names`. Under `CONFIG_MIGRATION`, it exports `putback_movable_pages`, `migrate_folio`, `migrate_pages`, `alloc_migration_target`, `isolate_movable_ops_page`, `isolate_folio_to_list`, huge-page mapping migration, softleaf wait, folio flag/mapping migration helpers, and `set_movable_ops`. Without migration support, safe inline stubs return `-ENOSYS`, `NULL`, or `false`.

The device migration portion defines `MIGRATE_PFN_*` encoding flags, `migrate_pfn_to_page`, `migrate_pfn`, `enum migrate_vma_direction`, `struct migrate_vma`, and APIs for setup, page migration, finalization, device PFN ranges, and device-page finalization.

## Control Flow
Generic migration isolates pages/folios into lists, allocates targets via caller-provided callbacks, migrates mappings and flags, then either frees old pages or puts them back. Driver movable pages follow `isolate_page` -> `migrate_page` -> success/free or `putback_page`. Device VMA migration follows `migrate_vma_setup`, caller allocation/population of destination PFNs, `migrate_vma_pages`, and `migrate_vma_finalize`.

## State And Persistence
Migration changes page ownership, mappings, flags, PFN arrays, and device/private memory residency. `struct migrate_vma` persists migration window state across setup/pages/finalize; its `src` and `dst` arrays must remain stable between phases. `pgmap_owner` and `fault_page` encode device-MMU and fault-context state.

## Dependencies And Integration Points
The header depends on core MM, memory policy, hugetlb, and `migrate_mode.h`. Integration points include compaction, memory hotplug, memory failure, NUMA balancing, long-term pin handling, DAMON, HMM/device-private memory, GPU drivers, and filesystems/address spaces.

## Risks
Risks include touching `page->lru` incorrectly in movable callbacks, blocking in async modes, stale PFN flags, missing putback on failure, migration with long-term pins, MMU notifier ordering mistakes for device pages, and assuming stubs perform work when migration is disabled.

## Test Signals
Use compaction and memory-hotplug migration, NUMA balancing, huge-page migration, driver movable-page migration, HMM/device-private migration, failure injection for `-EAGAIN` and permanent errors, CONFIG_MIGRATION=n builds, and lockdep/MMU notifier checks around device VMA migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/migrate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/migrate_mode.h -->
# sources/distributed-fs/ceph-client/include/linux/migrate_mode.h

## Purpose
This header defines the small shared enum vocabulary for migration blocking behavior and migration reason accounting.

## Important APIs, Types, And Functions
`enum migrate_mode` has `MIGRATE_ASYNC`, `MIGRATE_SYNC_LIGHT`, and `MIGRATE_SYNC`, describing progressively more blocking migration behavior. `enum migrate_reason` enumerates reasons such as compaction, memory failure, memory hotplug, syscall/cpuset, mempolicy mbind, NUMA misplaced pages, contiguous range allocation, long-term pin migration, demotion, DAMON, and `MR_TYPES` as the count.

## Control Flow
There is no control flow. Callers pass `migrate_mode` to migration APIs and use `migrate_reason` to label statistics, tracepoints, logs, and policy paths.

## State And Persistence
The header defines no state. The enums influence runtime policy and accounting in MM migration users.

## Dependencies And Integration Points
It is included by `migrate.h` and other MM code that needs reason or mode declarations without pulling the full migration API.

## Risks
Adding or reordering reasons affects arrays sized by `MR_TYPES`, especially `migrate_reason_names`. Misusing `MIGRATE_ASYNC` in paths that may block can introduce latency problems.

## Test Signals
Build coverage should catch enum/name-array mismatches. Runtime signals include correct migration trace reason labels and latency behavior under async, sync-light, and sync migration callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/migrate_mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mii.h -->
# sources/distributed-fs/ceph-client/include/linux/mii.h

## Purpose
This header provides generic MII/GMII helper interfaces and inline translations between PHY advertisement registers, ethtool legacy advertisement bits, modern linkmode bitmaps, duplex/flow-control resolution, and fixed BMCR encoding.

## Important APIs, Types, And Functions
`struct mii_if_info` stores PHY address masks, advertising state, duplex/autoneg/GMII flags, a netdev pointer, and MDIO read/write callbacks. External helpers cover link checks, autoneg restart, ethtool get/set, GMII support detection, media checks, and generic MII ioctl handling. Inline helpers include `if_mii`, `mii_nway_result`, `mii_duplex`, ethtool/linkmode to MII advertisement encoders, MII to ethtool/linkmode decoders, 1000Base-T and 1000Base-X helpers, flow-control advertisement and resolution, and `mii_bmcr_encode_fixed`.

## Control Flow
Drivers initialize `mii_if_info`, route MDIO accesses through callbacks, and call generic helpers from ioctl, ethtool, link check, or autoneg paths. Inline control flow is mostly bit-test/bit-set translation. `mii_nway_result` picks the best negotiated mode by priority, and `mii_resolve_flowctrl_fdx` applies IEEE pause-resolution logic.

## State And Persistence
The persistent state is held by the driver-owned `mii_if_info` and the PHY registers accessed by MDIO. Inline helpers do not store data but may prepare values that drivers persist to advertisement, control, or BMCR registers.

## Dependencies And Integration Points
The header depends on network interface definitions, linkmode helpers, UAPI MII register constants, ethtool structures, PHY advertisement bits, and netdev/MDIO driver callbacks. It bridges older MII helpers with ethtool link settings.

## Risks
Risks include stale legacy `ethtool_cmd` usage, incomplete translation for newer speeds, wrong handling of 1000Base-X versus 1000Base-T meanings, assuming `in_range`-style overflow semantics elsewhere, and using `mii_bmcr_encode_fixed` for unsupported speeds without noticing fallback to 10 Mbps.

## Test Signals
Validate ethtool advertisement round trips, ioctl register access, autoneg restart, link mode/duplex result selection, pause negotiation matrices, GMII support detection, fixed speed/duplex BMCR encodings, and PHY drivers using both legacy and modern ethtool APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mii.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mii_timestamper.h -->
# sources/distributed-fs/ceph-client/include/linux/mii_timestamper.h

## Purpose
This header defines generic timestamping callback interfaces for devices attached to MII buses, especially PHY timestamping devices, plus registration helpers gated by `CONFIG_NETWORK_PHY_TIMESTAMPING`.

## Important APIs, Types, And Functions
`struct mii_timestamper` defines callbacks for RX timestamp deferral, TX timestamp completion, hardware timestamp set/get ioctls, link-state notifications under the PHY mutex, ethtool timestamp info, and an owning `struct device`. `struct mii_timestamping_ctrl` defines controller callbacks to probe and release a timestamping channel. Public APIs register/unregister timestamping controllers and register/unregister per-port timestampers, with disabled-config stubs returning `-EOPNOTSUPP` or `NULL`.

## Control Flow
PHY or controller drivers register a controller or timestamper. Network receive paths can call `rxtstamp`; accepted SKBs are later delivered via `netif_rx()` after timestamping. TX paths call `txtstamp`; completion is later reported through `skb_complete_tx_timestamp()`. Ioctl/ethtool paths delegate to `hwtstamp_set`, `hwtstamp_get`, and `ts_info`.

## State And Persistence
State lives in driver-private structures embedding `mii_timestamper`. The header itself stores only the callback table and owning device pointer. Timestamp configuration persists in the hardware/driver after `hwtstamp_set`.

## Dependencies And Integration Points
It depends on device, ethtool, SKB, and timestamping types. It integrates with phylib, network RX/TX paths, PTP packet classification, SIOCSHWTSTAMP/SIOCGHWTSTAMP, ethtool timestamp info, device tree channel lookup, and optional controller multiplexing.

## Risks
Risks include SKB ownership mistakes when `rxtstamp` accepts a packet, missing TX completion callbacks, link-state callbacks invoked without respecting the PHY mutex contract, and silent feature absence under disabled `CONFIG_NETWORK_PHY_TIMESTAMPING`.

## Test Signals
Validate hardware timestamp ioctl set/get, ethtool timestamp info, RX PTP packet deferral and delivery, TX timestamp completion, link transition callbacks, registration/unregistration cleanup, and CONFIG-disabled callers handling `NULL` or `-EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mii_timestamper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/min_heap.h -->
# sources/distributed-fs/ceph-client/include/linux/min_heap.h

## Purpose
This header implements a generic typed min-heap API for kernel users. It provides typed heap declarations, inline and out-of-line heap operations, callback-based ordering, optional custom swapping, and optimized default swap routines.

## Important APIs, Types, And Functions
`MIN_HEAP_PREALLOCATED` and `DEFINE_MIN_HEAP` declare typed heap structures with `nr`, `size`, `data`, and optional preallocated storage. `struct min_heap_callbacks` supplies `less` and optional `swp`. Public macro wrappers include `min_heap_init`, `peek`, `full`, `sift_down`, `sift_up`, `heapify_all`, `pop`, `pop_push`, `push`, and `del`, with `_inline` variants mapping to static inline implementations. Internal helpers include alignment checks, 32/64-bit/byte swapping, swap-function selection, `do_swap`, and byte-offset `parent` calculation.

## Control Flow
Push copies an element to the end, increments `nr`, then sifts up. Pop verifies non-empty, moves the last element to root, decrements `nr`, then sifts down. Pop-push overwrites root and sifts down. Delete swaps the target with the last element, decrements `nr`, then applies both sift-up and sift-down. Heapify uses Floyd's O(n) bottom-up sift-down pass.

## State And Persistence
The heap state is entirely caller-owned: element storage, current count, capacity, and callback private arguments. Inline functions mutate `nr` and the array in place. No locking is provided; concurrent users must serialize externally.

## Dependencies And Integration Points
The header depends on bug warnings, string copy, types, pointer arithmetic, and architecture alignment properties. It integrates with kernel subsystems needing priority queues without open-coding heap maintenance.

## Risks
Risks include pushing full heaps or popping empty heaps, invalid `less` ordering, using a custom swap that does not preserve element invariants, element-size/alignment assumptions, zero-length heap misuse, and concurrent mutation without locks. `peek` returns `NULL` on empty heaps but otherwise a direct pointer into mutable storage.

## Test Signals
Validate ordering after heapify/push/pop/delete/pop-push, full/empty boundary warnings, custom swap callbacks, preallocated and external storage initialization, odd element sizes requiring byte swaps, 32-bit versus 64-bit swap behavior, and randomized heap property checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/min_heap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/minmax.h -->
# sources/distributed-fs/ceph-client/include/linux/minmax.h

## Purpose
This header defines the kernel's type-checked min/max/clamp family, array min/max helpers, range tests, swap macro, and unsafe constant-only legacy forms. Its main value is preventing signedness bugs and multiple evaluation while preserving efficient code generation.

## Important APIs, Types, And Functions
Public macros include `min`, `max`, `umin`, `umax`, `min3`, `max3`, `min_t`, `max_t`, `min_not_zero`, `clamp`, `clamp_t`, `clamp_val`, `min_array`, `max_array`, `in_range`, `swap`, and constant-only `MIN`, `MAX`, `MIN_T`, `MAX_T`. Internal helpers compute signed/unsigned comparison compatibility through `__sign_use`, `__is_nonneg`, `__types_ok`, and `__types_ok3`, then perform single-evaluation comparisons through unique temporaries.

## Control Flow
The macros expand into compile-time type checks plus simple conditional comparisons. Clamp checks constant low/high ordering when possible, then bounds the value. Array helpers walk backward over non-empty arrays/pointers and reduce via min or max. `in_range` selects 32-bit or 64-bit arithmetic based on operand sizes.

## State And Persistence
There is no persistent state. Macro temporaries exist only within statement expressions. `swap` mutates its two lvalue operands directly.

## Dependencies And Integration Points
It depends on build-bug, compiler, const, and type helpers. It is widely integrated across kernel code wherever scalar comparisons, clamping, min/max reductions, and range tests are needed.

## Risks
Risks include compile failures from intentional signedness checks, misuse of `MIN`/`MAX` with side effects, `min_array`/`max_array` with zero length, misunderstanding `in_range` overflow semantics, and relying on pointer comparisons beyond normal C rules. `clamp_t` and `clamp_val` bypass parts of the normal compatibility checking by design.

## Test Signals
Build-time tests should cover signed/unsigned combinations, non-negative constants, side-effect single evaluation, clamp low/high ordering, array reductions with pointers and arrays, 32/64-bit `in_range` behavior including overflow cases, and unsafe macro misuse caught by review or sparse-style checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/minmax.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/misc/keba.h -->
# sources/distributed-fs/ceph-client/include/linux/misc/keba.h

## Purpose
This header defines KEBA Industrial Automation auxiliary-device wrapper structures for platform subdevices such as I2C, SPI, fan, battery, and UART controllers.

## Important APIs, Types, And Functions
It declares `struct keba_i2c_auxdev`, `keba_spi_auxdev`, `keba_fan_auxdev`, `keba_batt_auxdev`, and `keba_uart_auxdev`. Each embeds `struct auxiliary_device` and a memory `struct resource`; I2C and SPI variants also carry board-info arrays and sizes, while the UART variant carries an IRQ.

## Control Flow
No functions are defined. Parent KEBA drivers instantiate these wrappers, register the embedded auxiliary devices, and child auxiliary drivers recover the enclosing structure to access IO resources, board-info data, and IRQs.

## State And Persistence
State is parent-owned and persists while the auxiliary device is registered. Resource ranges, board-info pointers, and IRQ numbers must remain valid through child probe/remove.

## Dependencies And Integration Points
It depends on the auxiliary bus and forward declarations for I2C/SPI board info. Integration points are KEBA MFD/industrial parent drivers, auxiliary bus child drivers, I2C/SPI device creation, hwmon/fan/battery drivers, and serial drivers.

## Risks
Risks include mismatched wrapper type between parent and child, invalid board-info array lifetime, resource range overlap, missing IRQ propagation for UART, and incomplete auxiliary-device release handling outside this header.

## Test Signals
Validate auxiliary-device registration, child probe data recovery, IO resource mapping, I2C/SPI child enumeration from board-info arrays, UART IRQ delivery, and clean remove/unregister ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/misc/keba.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/misc_cgroup.h -->
# sources/distributed-fs/ceph-client/include/linux/misc_cgroup.h

## Purpose
This header defines the miscellaneous cgroup controller interface for accounting and limiting non-standard host resources, currently including confidential-computing resources such as AMD SEV/SEV-ES ASIDs and Intel TDX HKIDs when configured.

## Important APIs, Types, And Functions
`enum misc_res_type` is conditionally populated by architecture/security features and ends with `MISC_CG_RES_TYPES`. Under `CONFIG_CGROUP_MISC`, `struct misc_res` tracks max, watermark, usage, events, and local events with atomics. `struct misc_cg` embeds `cgroup_subsys_state`, event files, and per-resource accounting. APIs include `misc_cg_set_capacity`, `misc_cg_try_charge`, `misc_cg_uncharge`, `css_misc`, `get_current_misc_cg`, and `put_misc_cg`. Disabled-config stubs accept operations without accounting.

## Control Flow
Resource providers set global capacity, then charge a task's current misc cgroup before allocating a protected resource and uncharge on release. `get_current_misc_cg` obtains a referenced cgroup via `task_get_css`; callers later use `put_misc_cg`.

## State And Persistence
Persistent state is per-cgroup resource accounting and event counters. Watermarks and events survive across individual charges until cgroup lifetime/reset semantics clear them. References from `get_current_misc_cg` must be balanced.

## Dependencies And Integration Points
It integrates with cgroup core, KVM SEV, Intel TDX host support, atomic counters, cgroup files `misc.events` and `misc.events.local`, and resource providers that need hierarchical accounting.

## Risks
Risks include enum count changing with Kconfig, charge/uncharge imbalance, using stubs as if enforcement exists when `CONFIG_CGROUP_MISC=n`, cgroup reference leaks, and capacity mismatches across hotplug or firmware changes.

## Test Signals
Validate capacity setting, charge success/failure at limits, watermark updates, global and local event increments, cgroup file reads, charge/uncharge balance under VM create/destroy, Kconfig-disabled behavior, and reference leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/misc_cgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/miscdevice.h -->
# sources/distributed-fs/ceph-client/include/linux/miscdevice.h

## Purpose
This header defines the misc character-device registration interface for devices sharing major 10, including fixed minor assignments, dynamic minor selection, the `miscdevice` descriptor, helper registration macros, and module alias support.

## Important APIs, Types, And Functions
It exports many fixed minor constants such as watchdog, RTC, hwrng, tun, fuse, kvm, rfkill, and vhost minors, plus `MISC_DYNAMIC_MINOR`. `struct miscdevice` contains minor, name, file operations, list node, parent/created device pointers, attribute groups, nodename, and mode. APIs are `misc_register` and `misc_deregister`. Helper macros are `builtin_misc_device`, `module_misc_device`, and `MODULE_ALIAS_MISCDEV`.

## Control Flow
Drivers initialize a `miscdevice`, set either a fixed minor or `MISC_DYNAMIC_MINOR`, and register it. The misc core allocates/registers the char device and device node. On removal, drivers call `misc_deregister` to tear down the node and release the minor.

## State And Persistence
The driver-owned `miscdevice` persists while registered. The core fills/uses `this_device` and internal list linkage. File operations persist independently and must remain valid for open files.

## Dependencies And Integration Points
It depends on major number definitions, list handling, types, and the device model. It integrates with char-device registration, udev/devtmpfs node creation, module aliases, sysfs groups, and many simple kernel drivers.

## Risks
Risks include fixed-minor collisions, using a stack-allocated descriptor, deregistering while file operations still assume device private state exists, incorrect mode/nodename, and forgetting module aliases for fixed-minor autoloading.

## Test Signals
Validate `/dev` node creation, dynamic minor allocation, fixed-minor autoload aliases, sysfs attribute groups, file operation dispatch, open-file behavior across deregistration, and duplicate minor rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/miscdevice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/cmd.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx4/cmd.h

## Purpose
This header defines the mlx4 firmware command opcode namespace, mailbox format, command invocation wrappers, virtual-function configuration APIs, checksum/offload configuration structures, and command-channel helpers for ConnectX-3-era devices.

## Important APIs, Types, And Functions
Large opcode enums cover initialization, HCA/port, memory translation, EQ/CQ/SRQ/QP state transitions, multicast, Ethernet, communication channel, virtualization, flow steering, debug, statistics, and congestion-control commands. It defines command timeout classes, mailbox size/alignment, set-port modifiers, MAD demux modifiers, native/wrapped command modes, RX checksum mode bits, `struct mlx4_config_dev_params`, congestion-control enums, `struct mlx4_cmd_mailbox`, and command wrappers around `__mlx4_cmd`: `mlx4_cmd`, `mlx4_cmd_box`, and `mlx4_cmd_imm`.

Other APIs allocate/free command mailboxes, retrieve counters and VF stats/configuration, set VF MAC/VLAN/rate/spoof/link state, retrieve config-device parameters, wake command completions, report internal errors, get slave default VLAN, and read command-channel interface revision.

## Control Flow
Callers build immediate parameters or DMA mailboxes, choose opcode/modifiers, and invoke `__mlx4_cmd` through a wrapper. Mailbox commands pass DMA addresses; immediate commands copy returned scalar output. VF and stats helpers encapsulate specific command sequences. Wrapped versus native mode controls whether commands are mediated for SR-IOV guests.

## State And Persistence
Firmware command execution changes device state: HCA/port lifecycle, resource ownership, QP/CQ/SRQ state, steering tables, VF policy, counters, and offload settings. Mailbox buffers are transient DMA objects. Command completions and command-channel versioning are maintained by mlx4 core.

## Dependencies And Integration Points
It depends on DMA mapping, if_link VF structures, mlx4 device definitions, and netdevice types. Integration points include mlx4 core, Ethernet and IB auxiliary drivers, SR-IOV management, ethtool stats, devlink/error handling, and firmware command queues.

## Risks
Risks include wrong opcode modifiers, mailbox alignment/size mistakes, timeout misuse, endian mistakes in mailbox payloads, native/wrapped confusion in virtualized mode, and applying VF settings to the wrong port or slave.

## Test Signals
Validate command success/failure status mapping, mailbox allocation DMA validity, HCA/port lifecycle commands, QP/CQ/SRQ transitions, VF configuration via iproute/ethtool, stats retrieval, checksum/offload parameter retrieval, internal-error completion wakeups, and SR-IOV command mediation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/cq.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx4/cq.h

## Purpose
This header defines mlx4 completion queue entry layouts, CQE status/opcode/syndrome masks, CQ moderation limits, and inline CQ doorbell helpers.

## Important APIs, Types, And Functions
It defines `struct mlx4_cqe`, `struct mlx4_err_cqe`, and packed `struct mlx4_ts_cqe` for normal, error, and timestamped completions. Enums describe tunnel/VLAN/QPN masks, owner/send/opcode masks, error syndromes, L3/L4 status bits, bad-FCS/LLC/SNAP flags, CQ DB request commands, and maximum CQ period/count. `mlx4_cq_arm` writes the arm doorbell record, applies `wmb()`, then rings MMIO via `mlx4_write64`; `mlx4_cq_set_ci` updates the consumer-index doorbell record. APIs `mlx4_cq_modify` and `mlx4_cq_resize` adjust moderation and queue size.

## Control Flow
Consumers process CQEs by owner/opcode, update `cq->cons_index`, write CI, and arm the CQ when interrupts are wanted. Arming first persists the host memory doorbell record, then rings the device UAR/CQ doorbell.

## State And Persistence
CQ state lives in `struct mlx4_cq` from `device.h`: CQN, consumer index, arm sequence number, doorbell records, vector, callbacks, and refcount. CQE rings and doorbell records are DMA-visible shared state between host and device.

## Dependencies And Integration Points
It depends on mlx4 device structures, doorbell MMIO helpers, Ethernet address sizing, and endian types. It integrates with mlx4 EQ interrupt handling, RDMA and Ethernet completion processing, timestamping, CQ resize/moderation firmware commands, and tasklet completion dispatch.

## Risks
Risks include missing the write memory barrier before MMIO, incorrect owner-bit interpretation after wraparound, wrong endian conversion, CQE layout mismatch when timestamp or 64-byte modes are enabled, and moderation values exceeding firmware bit widths.

## Test Signals
Validate send/receive completions, error CQE syndrome decoding, VLAN/tunnel checksum flags, timestamp CQEs, CQ arming and interrupt generation, CI updates, moderation changes, resize behavior, and wraparound ownership handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/cq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/device.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx4/device.h

## Purpose
This is the primary public mlx4 device contract. It describes ConnectX-3 device capabilities, port/SR-IOV state, resources, queue objects, event formats, flow-steering rules, memory-registration objects, and a broad set of core service APIs used by mlx4 Ethernet, RDMA, and auxiliary drivers.

## Important APIs, Types, And Functions
The file defines feature flags (`MLX4_FLAG_*`, capability flags, steering modes, tunnel modes), limits, port/resource enums, opcodes, event enums, permissions, rate-limit capability structures, device capability structures (`mlx4_caps`, `mlx4_phys_caps`, `mlx4_spec_qps`), DMA buffer and MTT/MR/MW/UAR/BF/DB/HWQ resources, CQ/QP/SRQ state objects, address-vector formats, counters, quotas, persistent device state, auxiliary device wrapper, clock params, EQE layout, port initialization params, MAD IFC format, and active-port/slave bitmap helpers.

APIs cover buffer allocation, PD/XRCD/UAR/BF allocation, MTT/MR/MW lifecycle, doorbell allocation, hardware queue resources, CQ/QP/SRQ allocation and lookup, port init/close, unicast/multicast attach/detach, flow steering/promisc rules, MAC/VLAN registration, SET_PORT variants, interrupt/EQ assignment, diagnostics, WOL, counters, admin GUIDs, slave port events and state, RoCE GID mapping, VXLAN/RoCEv2 configuration, virtual-to-physical port mapping, VF SMI admin, MR reregistration, module EEPROM access, internal clock parameters, and reserved-UAR calculations.

## Control Flow
mlx4 core populates `mlx4_dev` and `mlx4_caps` from firmware, then services resource allocation and command APIs for upper-layer drivers. Port setup flows through INIT/CLOSE and SET_PORT helpers. Queue users allocate backing buffers/MTTs, create CQ/QP/SRQ objects, register callbacks, and receive EQE-driven events. Flow steering builds software rule lists/specs and serializes them into hardware rule formats. SR-IOV paths translate slave/port identities, synthesize EQEs, and enforce reserved QP/QKey ranges.

## State And Persistence
Persistent state spans `mlx4_dev_persistent` hardware/software/PPCI state, current port types, catastrophic-error workqueue, firmware crash-dump regions, `mlx4_dev` flags/caps/quotas/radix tree, per-resource refcounts/completions, registered MAC/VLAN/flow IDs, active port/slave mappings, and DMA-visible memory tables. Many resources persist until explicit free or device teardown.

## Dependencies And Integration Points
It depends on auxiliary bus, PCI, completions, radix tree, CPU rmap, crash dump, refcount, timecounter, Ethernet constants, and devlink-facing structures. Integration points are mlx4_core, mlx4_en, mlx4_ib, SR-IOV PF/VF management, devlink, ethtool, RDMA core, netdevice flow steering, EQ interrupt handling, and firmware command code.

## Risks
Risks include capability flag drift, port-index off-by-one errors because arrays are `MAX_PORTS + 1`, SR-IOV slave mapping mistakes, resource leak or double-free around refcount/completion objects, incorrect endian packing of hardware rules/EQEs, reserved QP/QKey violations, port bonding state races, and low-memory profile behavior during kdump.

## Test Signals
Validate capability parsing, HCA/port bring-up, Ethernet and IB auxiliary driver attach, PD/MR/CQ/QP/SRQ lifecycle, flow steering and promisc rules, MAC/VLAN registration, SR-IOV VF port mappings/events/config, RoCE GID mapping, EQ vector assignment, WOL and module-info reads, counter allocation, catastrophic error handling, and teardown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/doorbell.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx4/doorbell.h

## Purpose
This header defines mlx4 send and CQ doorbell offsets plus a portable 64-bit doorbell write helper for MMIO doorbells.

## Important APIs, Types, And Functions
Constants `MLX4_SEND_DOORBELL` and `MLX4_CQ_DOORBELL` give UAR offsets. On 64-bit builds, doorbell lock macros are no-ops and `mlx4_write64` performs a raw 64-bit write. On 32-bit builds, lock macros declare/init/pass a spinlock and `mlx4_write64` serializes two 32-bit MMIO writes under IRQ-safe locking.

## Control Flow
CQ and send paths compose two big-endian 32-bit doorbell words, ensure prior memory writes are ordered in callers, then call `mlx4_write64`. The helper either writes atomically as one 64-bit operation or emits two protected 32-bit writes.

## State And Persistence
There is no persistent state beyond optional caller-owned spinlocks on 32-bit systems. Doorbell writes update device MMIO state and trigger hardware processing.

## Dependencies And Integration Points
It depends on types and IO accessors. It integrates with CQ arming, send queue ringing, UAR mappings, and architecture word-size assumptions.

## Risks
Risks include missing external ordering before ringing, passing no lock on 32-bit paths, endian/pointer aliasing mistakes in doorbell words, and using raw MMIO writes where relaxed or ordered variants might be architecture-sensitive.

## Test Signals
Validate send/CQ doorbell delivery on 64-bit and 32-bit builds, lockdep coverage for 32-bit doorbell lock use, CQ interrupt generation after arm, send queue progress, and stress tests with concurrent doorbells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/doorbell.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/driver.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx4/driver.h

## Purpose
This header defines the mlx4 auxiliary-driver and event-notifier interface used by protocol drivers layered on mlx4_core.

## Important APIs, Types, And Functions
It defines `MLX4_ADEV_NAME`, `MLX4_MAC_MASK`, device event enum values for catastrophic error, port up/down/reinit/management change, and slave init/shutdown, the `MLX4_INTFF_BONDING` interface flag, and `struct mlx4_adrv` embedding `auxiliary_driver` with protocol and flags. APIs register/unregister auxiliary drivers, register/unregister event notifiers, and retrieve a devlink port for a physical port.

## Control Flow
Protocol drivers create an `mlx4_adrv`, register it, and bind through the auxiliary bus to `mlx4_adev` instances from `device.h`. Event subscribers register notifier blocks and receive core events as hardware or SR-IOV state changes occur.

## State And Persistence
Registered auxiliary drivers and notifier blocks persist until explicit unregister. Devlink port objects are core-owned and returned for integration with higher-level networking management.

## Dependencies And Integration Points
It depends on devlink, auxiliary bus, notifier infrastructure, and mlx4 device definitions. Integration points include mlx4_en, mlx4_ib, bonding-aware interfaces, devlink, and mlx4_core event dispatch.

## Risks
Risks include notifier lifetime errors, unregister ordering while events are in flight, protocol mismatch in auxiliary drivers, and stale devlink-port pointers after device teardown.

## Test Signals
Validate auxiliary driver probe/remove, event notifier registration and delivery for port and catastrophic events, bonding flag behavior, devlink port lookup, and teardown under concurrent event generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/qp.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx4/qp.h

## Purpose
This header defines mlx4 queue-pair states, option masks, RSS context, QP path/context layout, WQE segment formats, QP update parameters, and QP lifecycle/query helpers.

## Important APIs, Types, And Functions
It defines `MLX4_INVALID_LKEY`, QP optional parameter flags, QP states, service types, path migration states, send/receive permission bits, RSS hash flags and context, `struct mlx4_qp_path`, `struct mlx4_qp_context`, `struct mlx4_update_qp_context`, update mask bits, WQE control flags, WQE segment structures for control, MLX, datagram, LSO, bind, FMR, protection, local invalidate, remote address, atomic, data, inline data, and update-QP attribute/parameter structures. APIs include `mlx4_qp_lookup`, `mlx4_update_qp`, `mlx4_qp_modify`, `mlx4_qp_query`, `mlx4_qp_to_ready`, inline `__mlx4_qp_lookup`, `mlx4_qp_remove`, `folded_qp`, `mlx4_qp_roce_entropy`, and `mlx4_put_qp`.

## Control Flow
QP setup allocates/reserves a QPN, fills a hardware context, transitions through firmware states such as RST->INIT->RTR->RTS via `mlx4_qp_modify` or `mlx4_qp_to_ready`, posts WQEs with the defined segment layouts, and receives completions/events. Runtime updates use mask bits to change selected QP or path fields without rebuilding the whole QP.

## State And Persistence
QP state is split between the software `struct mlx4_qp`, the radix-tree lookup table, firmware QP context, doorbell record, MTT-backed queues, and posted WQE ring contents. Refcounts and completions coordinate teardown.

## Dependencies And Integration Points
It depends on mlx4 device definitions and Ethernet constants. It integrates with RDMA verbs, mlx4_en RSS and Ethernet QPs, RoCE entropy, CQ/SRQ objects, firmware QP commands, and the core QP radix tree.

## Risks
Risks include wrong state transition ordering, endian/packing mistakes in QP context/WQE segments, invalid update mask selection, RSS context offset assumptions, QPN folding collisions if misused, reserved LKey misuse, and refcount teardown races.

## Test Signals
Validate QP create/query/modify/to-ready/remove, state transition errors, RSS hashing for IPv4/IPv6/TCP/UDP and inner headers, VLAN/source-check update attributes, WQE posting for send/RDMA/atomic/LSO/inline/FMR, RoCE entropy output, and QP lookup/refcount behavior under events and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/qp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/srq.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx4/srq.h

## Purpose
This header provides the mlx4 shared receive queue WQE next-segment layout and SRQ lookup API.

## Important APIs, Types, And Functions
`struct mlx4_wqe_srq_next_seg` contains reserved fields and `next_wqe_index`, matching the hardware-linked-list layout for SRQ receive WQEs. `mlx4_srq_lookup` retrieves a software `struct mlx4_srq` by SRQ number.

## Control Flow
SRQ users build receive WQEs with next indices and post them through mlx4 SRQ management. Event/completion paths can resolve an SRQ number back to the software object via `mlx4_srq_lookup`.

## State And Persistence
The WQE next segment is DMA-visible queue state. The SRQ object and lookup table are owned by mlx4 core and persist from allocation until free.

## Dependencies And Integration Points
It relies on `struct mlx4_dev` and `struct mlx4_srq` definitions from `device.h`. It integrates with RDMA receive queue management, SRQ events, CQ completions, and firmware SRQ commands.

## Risks
Risks include endian mistakes in `next_wqe_index`, corrupted WQE free lists, lookup after SRQ teardown, and event handling without holding a safe SRQ reference.

## Test Signals
Validate SRQ allocation/free, receive WQE chain integrity, lookup by SRQN during events, limit and last-WQE events, and teardown under outstanding completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx4/srq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/cq.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx5/cq.h

## Purpose
This header defines mlx5 core completion-queue state, CQE syndrome/opcode enums, CQ modification parameters, CQ stride encodings, doorbell helpers, refcount helpers, and core CQ management APIs.

## Important APIs, Types, And Functions
`struct mlx5_core_cq` holds CQN, CQE size, doorbell records, refcount/free completion, vector/IRQ, completion and event callbacks, consumer index, arm sequence number, debug handle, process id, tasklet context, reset notifier, EQ pointer, and UID. Enums define CQE syndromes, CQE request/response/error opcodes, modify masks, resize opmods, stride encodings, and CQ DB request commands. Helpers include `cqe_sz_to_mlx_sz`, `mlx5_cq_set_ci`, `mlx5_cq_arm`, `mlx5_cq_hold`, `mlx5_cq_put`, and `mlx5_dump_err_cqe`. APIs add CQ to tasklet, create/destroy/query/modify CQ, modify moderation, and add/remove debug CQ tracking.

## Control Flow
CQ users create a CQ with firmware input/output buffers, process CQEs, update CI doorbell records, and arm the CQ by writing host memory then ringing the UAR doorbell. Refcounts hold CQ objects during callback/event processing; final put completes teardown.

## State And Persistence
Persistent CQ state includes firmware CQN, doorbell records, consumer index, arm sequence, callback pointers, EQ association, debug object, reset notifier, and UID. CQ rings and doorbell records are shared with hardware.

## Dependencies And Integration Points
It depends on mlx5 driver definitions, EQE/event types, refcounting, completions, and mlx5 doorbell writes. It integrates with mlx5_core command handling, RDMA and Ethernet completion paths, EQ tasklets, debugfs/resource tracking, and reset notification.

## Risks
Risks include incorrect CQE stride selection, missing memory barrier before doorbell MMIO, refcount leaks or use-after-free around callbacks, moderation values exceeding field size, and 32-bit doorbell atomicity assumptions inherited from `mlx5_write64`.

## Test Signals
Validate CQ create/query/modify/destroy, moderation programming, resize inputs, CI updates, arm interrupt behavior, completion callback dispatch through tasklets, error CQE dumps, reset notifier handling, and refcount completion on final put.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/cq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/device.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx5/device.h

## Purpose
This header defines mlx5 device ABI helpers and hardware-facing structures: IFC bitfield access macros, command/init segments, event/CQE layouts, work-queue and memory-key constants, capability accessors, flow table enums, vport/WOL/protocol constants, and command/status/counter vocabulary.

## Important APIs, Types, And Functions
The bitfield macro family (`MLX5_SET`, `GET`, `SET64`, `GET64`, `GET16`, `SET16`, `ADDR_OF`, size/offset helpers, and big-endian getters) accesses generated `mlx5_ifc_*_bits` layouts. Enums define inline modes, command limits, CQ states, permissions, PCI controls, BFREG/UAR limits, MKey/UMR masks, event queue types, hardware events, driver events, tracer/general/port-change subtypes, RoCE versions/L3 types, opcodes, TLS WQE opmods, set-port fields, bandwidth units, ODP caps, command status codes, and counter groups.

Structures include `mlx5_cmd_layout`, `health_buffer`, `mlx5_init_seg`, many `mlx5_eqe_*` event payloads, `union ev_data`, packed `struct mlx5_eqe`, command data blocks, error CQE and normal `mlx5_cqe64`/`mlx5_cqe128` layouts, mini CQE layout, signature-error CQE, SRQ next segment, MKey segment, and ODP caps. Inline helpers decode CQE format/opcode, enhanced mini-CQE count, LRO flags, L4 header type, tunnel/TLS/VLAN state, timestamps, flow tags, LRO segment count, MPWQE byte counts/stride consumption/filler status/stride index, and pkey table size.

Capability macros read current/max HCA capability blocks for general, Ethernet, IPoIB, RoCE, atomic, flow table, eswitch, port selection, advanced virtualization/RDMA, ODP, QoS, debug, PCAM/MCAM/QCAM, FPGA, device memory, TLS, device events, vDPA/TLP emulation, IPsec, crypto, MACsec, SHAMPO, and PSP capabilities.

## Control Flow
mlx5 core maps the initialization segment, brings up the command interface, queries capabilities into `mdev->caps`, then higher layers use capability macros to gate features. Command queues use `mlx5_cmd_layout` and chained command blocks. EQ polling decodes `mlx5_eqe` by event type/subtype into typed payloads. CQ processing reads `mlx5_cqe64`/mini-CQEs, decodes flags, timestamps, checksums, RSS, LRO/MPWQE state, and error syndromes.

## State And Persistence
Persistent hardware-shared state includes init segment fields, health buffer, command queue doorbells, firmware timers, EQEs, CQEs, MKeys, UMR translation metadata, capability snapshots, and vport/flow-table configuration. Many structures are packed or bit-addressed because they mirror firmware ABI.

## Dependencies And Integration Points
It depends on RDMA verbs, generated `mlx5_ifc` definitions, bitfield helpers, endian conversions, and core mlx5 device structures from driver headers. Integration points include mlx5_core, mlx5e, mlx5_ib, eswitch, flow steering, ODP/HMM, TLS/IPsec/MACsec/crypto offloads, vDPA/TLP emulation, devlink health, firmware reset/live patch events, and PTP/PPS timestamping.

## Risks
Risks include generated IFC layout drift, bit offset or endian misuse, assuming capability blocks are allocated for newly added cap types, interpreting compressed CQEs incorrectly, packed-structure ABI changes, 32-bit overflow in masks, event subtype collisions, and stale capability checks when current and max caps differ.

## Test Signals
Validate bitfield macro set/get round trips, capability query coverage for every allocated cap type, init segment health/status reads, command status decoding, EQ event decoding for port/module/page-fault/PPS/temp/vhca/object changes, CQE parsing for checksum/RSS/VLAN/tunnel/TLS/LRO/MPWQE/compressed paths, MKey/UMR programming, flow-table capability gating, and endian tests on big-endian or sparse builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/doorbell.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx5/doorbell.h

## Purpose
This header defines mlx5 BlueFlame/CQ doorbell offsets and a low-level 64-bit doorbell MMIO write helper.

## Important APIs, Types, And Functions
Constants `MLX5_BF_OFFSET` and `MLX5_CQ_DOORBELL` identify UAR offsets. `mlx5_write64` writes two big-endian 32-bit words to MMIO as a raw 64-bit write on 64-bit builds, or two raw 32-bit writes on 32-bit builds.

## Control Flow
Callers build doorbell words, perform any required memory ordering, and invoke `mlx5_write64` to notify hardware. Unlike mlx4, this helper does not provide locking for 32-bit systems; callers must protect multiword writes when needed.

## State And Persistence
The header holds no software state. Doorbell writes update hardware-visible UAR/MMIO state and trigger CQ or send processing.

## Dependencies And Integration Points
It integrates with mlx5 CQ arming, send queue ringing, BlueFlame writes, and UAR mappings. It relies on raw IO accessors and architecture word-size behavior made available through surrounding includes.

## Risks
Risks include assuming 32-bit writes are atomic, missing caller-side locking on 32-bit, missing memory barriers before MMIO, and using raw writes in contexts requiring stricter ordering.

## Test Signals
Validate CQ doorbells, BlueFlame/send queue ringing, 32-bit build review for locking, stress tests with concurrent doorbells, and hardware progress after caller-side barriers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/doorbell.h -->
