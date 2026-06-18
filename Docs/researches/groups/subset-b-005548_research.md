# subset-b-005548 Research

Grouped research for `subset-b-005548`. Each section preserves the source path in the title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/main.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/main.c

## Purpose
This file implements `xe-vfio-pci`, a VFIO PCI driver variant for Intel Xe graphics devices with SR-IOV VF migration support. It wraps `vfio_pci_core_device`, delegates standard PCI BAR/config/IRQ handling to VFIO PCI core, and adds Intel Xe PF/VF hooks for live migration state transitions, FLR coordination, and migration data streams.

## Important APIs, types, and functions
Key local types are `struct xe_vfio_pci_core_device`, which embeds the VFIO PCI core device plus Xe PF pointer, VF id, migration state, reset deferral state, and locks, and `struct xe_vfio_pci_migration_file`, which represents an anonymous save or resume data file. The driver exports `xe_vfio_pci_ops` to VFIO core, `xe_vfio_pci_migration_ops` to the VFIO migration feature path, and a `pci_driver` matching Intel PTL, WCL, and BMG IDs through `PCI_DRIVER_OVERRIDE_DEVICE_VFIO`. Important functions include `xe_vfio_pci_open_device`, `xe_vfio_pci_close_device`, `xe_vfio_pci_set_device_state`, `xe_vfio_set_state`, `xe_vfio_pci_reset_prepare`, and `xe_vfio_pci_reset_done`.

## Control flow
Probe allocates the extended VFIO PCI object with `vfio_alloc_device`, stores driver data, and registers with `vfio_pci_core_register_device`. VF initialization detects VFs, obtains the PF `xe_device` through `xe_sriov_vfio_get_pf`, derives the PF-facing VF id as `pci_iov_vf_id() + 1`, and enables migration if `xe_sriov_vfio_migration_supported()` is true. Open enables the VFIO PCI core and starts in `VFIO_DEVICE_STATE_RUNNING`. Migration SET state requests are decomposed by `vfio_mig_get_next_state()` and applied through Xe SR-IOV helper calls: suspend/resume for running-p2p, stop-copy enter/exit with a read-only save file, and resume-data enter/exit with a write-only resume file. Reset prepare/done calls let the PF prepare and wait for VF FLR, then schedule migration cleanup through the state lock path.

## State and persistence behavior
State is in memory only: `mig_state`, `migf`, `deferred_reset`, `xe`, and `vfid` are stored per device instance. Migration data is exposed through anonymous inode files and is not persisted by this driver. `xe_vfio_pci_put_file()` disables a migration file before `fput()`, making later reads/writes fail with `-ENODEV`. The `state_mutex` serializes migration state and migration data access setup, while `reset_lock` protects `deferred_reset`; reset cleanup may be deferred if the migration state mutex is already held to avoid ABBA deadlocks with higher VFIO locks.

## Dependencies and integration points
The file depends on VFIO PCI core, generic VFIO migration feature handling, PCI AER/reset callbacks, Intel Xe SR-IOV VFIO DRM helpers, and Intel PCI ID macros. It integrates with userspace through VFIO device feature ioctls that consume `core_vdev->mig_ops`, and with the PF driver through `xe_sriov_vfio_*` calls.

## Risks and test signals
Migration correctness depends on the PF helper functions being ordered exactly with VFIO state changes and file lifetimes. Reset races are the main concurrency risk: test FLR during active stop-copy/resume streams, repeated state transitions, and close while a migration fd remains open. Test signals include successful bind/probe only for VFIO-overridden Intel IDs, VF open/close, migration state matrix coverage, read/write returning `-ESPIPE` for positioned I/O, `-ENODEV` after reset-disabling migration fds, and PF FLR wait failure logging without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/Kconfig

## Purpose
This Kconfig file defines VFIO support for platform and AMBA devices, plus the menu that includes optional VFIO platform reset handlers. It scopes the platform VFIO family to ARM, ARM64, or compile-test builds.

## Important APIs, types, and functions
The important symbols are `VFIO_PLATFORM_BASE`, `VFIO_PLATFORM`, and `VFIO_AMBA`. `VFIO_PLATFORM_BASE` is a hidden tristate that selects `VFIO_VIRQFD`, providing the common platform base and IRQ eventfd support. `VFIO_PLATFORM` enables the generic platform bus binder. `VFIO_AMBA` enables the deprecated AMBA binder when `ARM_AMBA` or `COMPILE_TEST` is available.

## Control flow
Kconfig selection flows from a user-visible bus driver to the shared base. Selecting either generic platform support or AMBA support selects `VFIO_PLATFORM_BASE`; the reset-driver submenu is visible only when the base is enabled. The file then sources `drivers/vfio/platform/reset/Kconfig`.

## State and persistence behavior
There is no runtime state. The persistent effect is the kernel configuration choice that decides which objects are built into the kernel or as modules.

## Dependencies and integration points
This file integrates with `drivers/vfio/platform/Makefile`, the reset subdirectory Kconfig, and generic VFIO virqfd support. The AMBA option is explicitly deprecated in help text, which affects maintenance expectations.

## Risks and test signals
Risk centers on accidental enablement without reset support, because the generic platform driver defaults to requiring reset at runtime. Configuration tests should cover `allyesconfig`, module builds, `COMPILE_TEST`, ARM/ARM64 visibility, and builds where only `VFIO_AMBA` or only `VFIO_PLATFORM` is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/Makefile

## Purpose
This Makefile maps VFIO platform Kconfig symbols to kernel objects. It builds the shared base module, optional reset subdirectory, generic platform binder, and AMBA binder.

## Important APIs, types, and functions
`vfio-platform-base-y` combines `vfio_platform_common.o` and `vfio_platform_irq.o`. `obj-$(CONFIG_VFIO_PLATFORM_BASE)` emits `vfio-platform-base.o` and descends into `reset/`. `vfio-platform-y` maps to `vfio_platform.o`, and `vfio-amba-y` maps to `vfio_amba.o`.

## Control flow
The build dependency mirrors Kconfig: once the base symbol is enabled, common code and reset handlers can be built. The generic and AMBA binders are independent object modules that depend on the base symbols and exported functions at link/load time.

## State and persistence behavior
No runtime state exists. The file persists build composition by deciding which object code is part of the kernel image or module set.

## Dependencies and integration points
The Makefile depends on the platform Kconfig symbols and on reset Makefile contents. It integrates common code with bus-specific frontends, so symbol exports in `vfio_platform_common.c` and `vfio_platform_irq.c` must remain available to both binders.

## Risks and test signals
Build risks include missing reset subdirectory descent, mismatched object names, or unresolved exports if common code changes. Test signals are clean builds for built-in and module combinations of `VFIO_PLATFORM_BASE`, `VFIO_PLATFORM`, `VFIO_AMBA`, and reset modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/Kconfig

## Purpose
This Kconfig file defines optional, deprecated device-specific reset handlers for VFIO platform devices. These handlers let `vfio_platform_common.c` discover and call reset functions for compatible strings.

## Important APIs, types, and functions
The symbols are `VFIO_PLATFORM_CALXEDAXGMAC_RESET`, `VFIO_PLATFORM_AMDXGBE_RESET`, and `VFIO_PLATFORM_BCMFLEXRM_RESET`. All are tristate and visible only under `if VFIO_PLATFORM`. The Broadcom FlexRM option depends on `ARCH_BCM_IPROC || COMPILE_TEST` and defaults to `ARCH_BCM_IPROC`.

## Control flow
When the generic platform driver is enabled, users may select one or more reset handler modules. Those modules register compat-string callbacks through `module_vfio_reset_handler()` in their C files. The generic platform open/close/reset ioctl path then finds callbacks by device `compatible` string.

## State and persistence behavior
There is no runtime state here. Kconfig choices persist in the kernel build configuration and decide whether reset handlers are available for autoloading via `MODULE_ALIAS("vfio-reset:<compat>")`.

## Dependencies and integration points
This file integrates with the reset Makefile and the reset-handler registry in `vfio_platform_common.c`. The deprecation notices indicate these platform-specific resets are legacy maintenance points.

## Risks and test signals
The major risk is a platform device being assigned without a reset callback when `reset_required` is true, causing open or init failure. Test signals include module autoload by alias, compile coverage for each symbol, Broadcom dependency gating, and platform open/close reset behavior with and without selected handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/Makefile

## Purpose
This Makefile builds the optional VFIO platform reset handler modules selected by reset Kconfig.

## Important APIs, types, and functions
It maps `VFIO_PLATFORM_CALXEDAXGMAC_RESET` to `vfio-platform-calxedaxgmac.o`, `VFIO_PLATFORM_AMDXGBE_RESET` to `vfio-platform-amdxgbe.o`, and `VFIO_PLATFORM_BCMFLEXRM_RESET` to `vfio_platform_bcmflexrm.o`. The first two use `*-y` variables that point at C object names.

## Control flow
Kbuild emits each reset handler only when its Kconfig symbol is enabled. At module load time, each handler registers a compat callback with the VFIO platform reset registry.

## State and persistence behavior
No runtime state exists in the Makefile. Its persistent output is module/object availability.

## Dependencies and integration points
The build artifacts depend on `vfio_platform_private.h` for registration macros and on exported reset registry functions from the platform base module.

## Risks and test signals
Risk is mostly naming mismatch: two modules use hyphenated output module names while the Broadcom object keeps an underscore object path. Test signals are clean module builds, `modinfo` aliases, and successful reset handler registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_amdxgbe.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_amdxgbe.c

## Purpose
This file provides a deprecated VFIO platform reset handler for AMD XGBE devices with compatible string `amd,xgbe-seattle-v1a`. It reuses native-driver register knowledge to reset PHY/MAC state before or after VFIO userspace ownership.

## Important APIs, types, and functions
The reset entry point is `vfio_platform_amdxgbe_reset(struct vfio_platform_device *vdev)`. Helper functions `xmdio_read()` and `xmdio_write()` access MDIO MMD registers through the XPCS register window. The handler uses `struct vfio_platform_region` entries 0 and 1 for XGMAC and XPCS MMIO regions.

## Control flow
The handler logs a one-time deprecation warning, ioremaps both required regions if not already mapped, resets the PHY through `MDIO_MMD_PCS/MDIO_CTRL1`, polls up to 50 times with 20 ms sleeps for reset completion, disables auto-negotiation and AN interrupts, clears AN IRQ state, then sets the MAC software reset bit in `DMA_MR` and polls for completion.

## State and persistence behavior
The only persistent runtime state is the cached `ioaddr` mapping stored in the VFIO platform region. Hardware state is modified by disabling AN/interrupts and resetting PHY/MAC logic. The handler returns success even when PHY or MAC reset times out, after logging warnings.

## Dependencies and integration points
It depends on VFIO platform private data, Linux I/O accessors, MDIO constants, and module reset registration through `module_vfio_reset_handler`. It is discovered by `vfio_platform_get_reset()` and called by platform open, close, and reset ioctl paths.

## Risks and test signals
Risks include assuming region ordering, returning success after hardware timeout, and leaving a partially reset device assigned to userspace. Test signals include compat alias autoload, ioremap failure handling, PHY reset polling, DMA reset polling, and assignment open/close cycles on matching AMD XGBE hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_amdxgbe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_bcmflexrm.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_bcmflexrm.c

## Purpose
This file provides a deprecated VFIO platform reset handler for Broadcom FlexRM ring manager devices with compatible string `brcm,iproc-flexrm-mbox`. Its purpose is to discover valid ring register blocks and flush them to a quiescent state for device assignment.

## Important APIs, types, and functions
`vfio_platform_bcmflexrm_reset()` is the VFIO reset callback. `vfio_platform_bcmflexrm_shutdown()` disables a single ring, asserts flush state in `RING_CONTROL`, polls `RING_FLUSH_DONE`, then clears flush state and waits for flush-done deassertion. Constants define ring block size, version magic, and register offsets.

## Control flow
Reset logs a deprecation warning, maps region 0 if necessary, then walks the region in `RING_REGS_SIZE` increments. Blocks whose `RING_VER` equals `RING_VER_MAGIC` are treated as rings and passed to the shutdown helper. Individual ring failures are logged and ORed into the final return value while discovery continues.

## State and persistence behavior
The callback caches the MMIO mapping in `vdev->regions[0].ioaddr`. It changes hardware state by disabling rings and forcing flush transitions. No software state survives beyond the cached mapping.

## Dependencies and integration points
It depends on VFIO platform region discovery, relaxed MMIO accessors, polling delays, and reset-handler registration. It integrates with the generic VFIO platform reset lookup by compat alias.

## Risks and test signals
Risks include pointer-range arithmetic over `void __iomem *`, assuming region 0 covers all rings, and returning a bitwise OR of negative errno values rather than the first error. Test signals include multi-ring discovery, timeout paths for flush set/clear, no-ring behavior, and module unload after open/close cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_bcmflexrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_calxedaxgmac.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_calxedaxgmac.c

## Purpose
This file provides a deprecated reset handler for Calxeda XGMAC platform devices with compatible string `calxeda,hb-xgmac`. It quiesces the MAC and DMA engines so the device can be safely handed to VFIO userspace or released.

## Important APIs, types, and functions
The main callback is `vfio_platform_calxedaxgmac_reset()`. `xgmac_mac_disable()` clears DMA transmit/receive start bits and MAC TX/RX enable bits. Register constants cover MAC control, DMA control, and DMA interrupt enable.

## Control flow
The reset handler logs deprecation once, maps region 0 if needed, writes zero to `XGMAC_DMA_INTR_ENA` to disable DMA interrupts, then calls `xgmac_mac_disable()` to stop TX/RX at DMA and MAC levels.

## State and persistence behavior
The only software state is a cached region mapping. Hardware state persists as disabled interrupts and disabled TX/RX engines. There is no polling or explicit full hardware reset.

## Dependencies and integration points
It depends on VFIO platform region metadata, Linux MMIO accessors, and the reset-handler registration macro. The common platform code discovers it by `compatible` and calls it during init/open/close/reset operations.

## Risks and test signals
Risks include incomplete reset semantics, reliance on region 0, and no verification that the MAC has actually stopped. Test signals include matching module alias, ioremap failure handling, interrupt masking verification, and repeated VFIO open/close assignment tests on Calxeda XGMAC hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_calxedaxgmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_amba.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_amba.c

## Purpose
This deprecated driver binds ARM AMBA devices into VFIO using the shared VFIO platform base. It is a bus-specific wrapper that provides AMBA resource and IRQ discovery and delegates device operations to `vfio_platform_common.c`.

## Important APIs, types, and functions
`get_amba_resource()` exposes only `adev->res` as region 0. `get_amba_irq()` returns AMBA IRQ slots, translating zero to `-ENXIO`. `vfio_amba_init_dev()` fills `vfio_platform_device` fields including name, flags, callbacks, and `reset_required = false`. `vfio_amba_ops` supplies VFIO callbacks for open, close, ioctl, region info, read, write, mmap, and iommufd physical binding.

## Control flow
Probe logs a deprecation warning, allocates a VFIO platform device with `vfio_alloc_device`, registers it as a VFIO group device, enables runtime PM, and stores driver data. Removal unregisters the group device, disables runtime PM, and drops the VFIO device reference. Init and release callbacks set up and tear down common platform state.

## State and persistence behavior
Per-device state lives in `struct vfio_platform_device`: generated name, AMBA opaque pointer, callbacks, IRQ/resource arrays initialized on open, and reset metadata. Runtime PM is enabled for the device while bound. No disk persistence exists.

## Dependencies and integration points
The file depends on the AMBA bus, VFIO core, VFIO platform base exports, runtime PM, and iommufd physical attach operations. Its `driver_managed_dma = true` flag integrates with DMA ownership expectations for VFIO.

## Risks and test signals
Risks include deprecated status, lack of required reset by default, only one AMBA memory resource being exposed, and unset IRQ semantics. Test signals include AMBA probe/remove, VFIO device info flags, region 0 access, IRQ enumeration, runtime PM balancing, and iommufd bind/attach calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_amba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform.c

## Purpose
This file is the generic platform-bus VFIO binder. It adapts Linux `platform_device` resources and IRQs to the shared VFIO platform base, allowing eligible platform devices to be assigned to userspace.

## Important APIs, types, and functions
`get_platform_resource()` calls `platform_get_mem_or_io()`, and `get_platform_irq()` calls `platform_get_irq_optional()`. `vfio_platform_init_dev()` fills the embedded `vfio_platform_device` with platform callbacks, name, flags, and the `reset_required` module parameter. `vfio_platform_ops` delegates VFIO operations to common platform code and physical iommufd binding helpers.

## Control flow
Probe allocates a VFIO platform device, registers it with VFIO group core, enables runtime PM, and stores driver data. Device initialization probes ACPI/OF metadata and reset availability through the common layer. Open/close/read/write/mmap/ioctl paths all flow through common platform exports. Removal unregisters, disables runtime PM, and puts the VFIO device.

## State and persistence behavior
The `reset_required` module parameter defaults to true and persists for the module lifetime. Per-device state is in memory in `vfio_platform_device`: resource callbacks, IRQ arrays, reset callback/module, compatible/HID, and runtime PM state. Regions and IRQs are allocated on open and freed on close.

## Dependencies and integration points
This file depends on the platform bus, VFIO core, runtime PM, shared VFIO platform base, and iommufd. It integrates with reset handlers via OF compatible strings or ACPI `_RST`.

## Risks and test signals
Main risks are assigning devices without reliable reset, resource ordering assumptions from userspace, and runtime PM imbalance on error paths. Test signals include probe/open failure without reset when required, `reset_required=0`, ACPI and OF devices, region and IRQ enumeration, runtime PM get/put, and iommufd attach/detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_common.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_common.c

## Purpose
This shared base implements most VFIO platform device behavior: firmware probing, reset-handler lookup and invocation, region discovery, IRQ initialization, VFIO ioctls, MMIO read/write, mmap, and reset handler registry management.

## Important APIs, types, and functions
Exported APIs include `vfio_platform_init_common`, `vfio_platform_release_common`, `vfio_platform_open_device`, `vfio_platform_close_device`, `vfio_platform_ioctl`, `vfio_platform_ioctl_get_region_info`, `vfio_platform_read`, `vfio_platform_write`, `vfio_platform_mmap`, `__vfio_platform_register_reset`, and `vfio_platform_unregister_reset`. Internally, `reset_list` and `driver_lock` manage registered OF-compatible reset handlers. `VFIO_PLATFORM_INDEX_TO_OFFSET` and `VFIO_PLATFORM_OFFSET_TO_INDEX` encode region indexes into VFIO file offsets.

## Control flow
Device init tries ACPI first and then OF compatible probing. It initializes the IRQ gate mutex and obtains a reset path, either ACPI `_RST` or OF reset handler module autoloaded through `vfio-reset:<compat>`. Open initializes regions, initializes IRQs, resumes runtime PM, and calls reset; failure unwinds IRQs, regions, and PM. Close calls reset, runtime-PM put, region cleanup, and IRQ cleanup. Ioctl handles device info, IRQ info, `VFIO_DEVICE_SET_IRQS`, and `VFIO_DEVICE_RESET`, while region info is served through the VFIO core region callback.

## State and persistence behavior
Per-open state includes allocated `regions`, `irqs`, cached `ioaddr` mappings, runtime PM usage, and eventfd IRQ state from the IRQ layer. Reset module references are held after lookup and released during common release. Region MMIO mappings are lazily ioremapped during reset or read/write and unmapped on close. No disk persistence exists.

## Dependencies and integration points
The file depends on ACPI, device properties, IOMMU/VFIO uAPI structs, runtime PM, module autoloading, and the platform IRQ module. It integrates with bus binders through resource/IRQ callbacks and with reset modules through `vfio_platform_reset_node`.

## Risks and test signals
Security hinges on reset reliability, page-aligned mmap checks, and correct resource flags. Risks include PIO resources being exposed but unimplemented, reset handlers returning success after partial hardware failure, and stale module references if registration changes. Test signals include ACPI `_RST`, OF reset autoload, read/write width splitting, mmap bounds and permission failures, IRQ ioctl validation, and close-time reset warning behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_irq.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_irq.c

## Purpose
This file implements VFIO platform interrupt setup and `VFIO_DEVICE_SET_IRQS` handling. It bridges hardware IRQs to userspace eventfds and supports mask/unmask control through direct ioctl data or virqfd eventfd triggers.

## Important APIs, types, and functions
Exported functions are `vfio_platform_irq_init`, `vfio_platform_irq_cleanup`, and `vfio_platform_set_irqs_ioctl`. Important helpers include `vfio_platform_mask`, `vfio_platform_unmask`, `vfio_set_trigger`, `vfio_automasked_irq_handler`, and `vfio_irq_handler`. Each IRQ is represented by `struct vfio_platform_irq`.

## Control flow
Initialization counts bus IRQs, allocates an IRQ array, names each IRQ, marks level-triggered IRQs as maskable and automasked, then requests each IRQ with `IRQF_NO_AUTOEN`. SET_IRQS validation is done in VFIO core and this file dispatches action type to mask, unmask, or trigger handling. Trigger setup obtains an eventfd context, enables the IRQ, and stores it as the interrupt notification target. Level-triggered interrupts are disabled in the handler before signaling userspace.

## State and persistence behavior
Runtime state includes `trigger`, `mask`, and `unmask` eventfd/virqfd pointers, `masked` boolean, IRQ name pointer or ERR_PTR request failure, and per-IRQ spinlock. Cleanup disables virqfd objects, frees IRQs, drops eventfd contexts, frees names, and clears the IRQ array.

## Dependencies and integration points
It depends on Linux IRQ APIs, eventfd, VFIO IRQ uAPI flags, and `vfio_virqfd_enable/disable`. It is called by platform common open/close and ioctl paths.

## Risks and test signals
Risks include IRQ request failure being deferred until SET_IRQS for compatibility, race-sensitive mask/unmask locking, and eventfd lifetime management. Test signals include edge and level IRQs, trigger fd enable/disable, direct trigger with DATA_NONE/DATA_BOOL, mask/unmask virqfd paths, cleanup after eventfd close, and polling fallback when `request_irq()` returns an error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_private.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_private.h

## Purpose
This private header defines the shared data model and prototypes for VFIO platform and AMBA drivers, including region indexing, IRQ state, platform device state, and reset handler registration.

## Important APIs, types, and functions
Key macros are `VFIO_PLATFORM_OFFSET_SHIFT`, `VFIO_PLATFORM_OFFSET_MASK`, `VFIO_PLATFORM_OFFSET_TO_INDEX`, and `VFIO_PLATFORM_INDEX_TO_OFFSET`. Key structs are `vfio_platform_irq`, `vfio_platform_region`, `vfio_platform_device`, and `vfio_platform_reset_node`. The header declares common lifecycle, ioctl, read/write/mmap, IRQ, and reset registry functions. `module_vfio_reset_handler()` creates module init/exit functions plus `MODULE_ALIAS("vfio-reset:<compat>")`.

## Control flow
Bus-specific binders fill `vfio_platform_device` callbacks and flags, then common code uses these fields to discover resources, interrupts, firmware identity, and reset support. Reset modules instantiate a static reset node and register it on module init.

## State and persistence behavior
The structs describe all important in-memory state: regions with physical addresses and cached `ioaddr`, IRQ eventfd state, reset module ownership, compatible/HID strings, and bus-specific opaque pointers. There is no persistent storage.

## Dependencies and integration points
The header depends on Linux VFIO and interrupt types. It integrates platform C files, AMBA C files, reset modules, and VFIO core uAPI behavior.

## Risks and test signals
ABI-adjacent risk lies in offset encoding: changing the 40-bit index shift would break userspace region offsets. Reset registration macros depend on unique reset function names. Test signals include compile coverage for all platform modules, region offset round trips, reset module autoload aliases, and lockdep coverage around IRQ state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/vfio.h

## Purpose
This internal VFIO header defines core-private interfaces shared among VFIO main, group, container, iommufd, cdev, debugfs, and virqfd components. It abstracts optional Kconfig features behind real prototypes or stubs.

## Important APIs, types, and functions
Important types include `struct vfio_device_file`, `enum vfio_group_type`, `struct vfio_group`, `struct vfio_iommu_driver_ops`, and `struct vfio_iommu_driver`. It declares device registration refs, device file operations, group/container attach and pin APIs, iommufd bind/attach helpers, cdev helpers, virqfd init/exit, KVM association helpers, and debugfs hooks.

## Control flow
VFIO core and submodules include this header to call feature-specific operations without open-coding `#ifdef` at each call site. When a feature is disabled, inline stubs return `-EOPNOTSUPP`, false, true, or no-op as appropriate so callers can keep a uniform control flow.

## State and persistence behavior
The header declares the shape of in-memory state but does not allocate it. `vfio_device_file` tracks an opened VFIO device fd, group association, iommufd context, access-granted bit, KVM pointer, and cdev device id. `vfio_group` tracks group device state, container/iommufd association, device list, cdev open count, KVM pointer, and locking.

## Dependencies and integration points
It depends on Linux file/device/cdev/module/vfio types and optionally on `CONFIG_VFIO_GROUP`, `CONFIG_VFIO_CONTAINER`, `CONFIG_IOMMUFD`, `CONFIG_VFIO_DEVICE_CDEV`, `CONFIG_VFIO_VIRQFD`, `CONFIG_KVM`, and `CONFIG_VFIO_DEBUGFS`. It is the central contract between VFIO core and IOMMU backend drivers.

## Risks and test signals
Risks include stub behavior masking missing feature support, lock ownership assumptions around group/device set paths, and ABI changes in device-file handling. Test signals include build matrices with each optional VFIO config on/off, group and cdev open paths, iommufd bind failures, KVM set/clear, and virqfd-disabled platform IRQ builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio_iommu_spapr_tce.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/vfio_iommu_spapr_tce.c

## Purpose
This file implements the POWER sPAPR TCE VFIO IOMMU backend. It manages TCE table ownership, DMA window creation/removal, v1 and v2 map/unmap behavior, optional preregistered memory, and EEH PE operations for VFIO containers.

## Important APIs, types, and functions
Key state types are `struct tce_container`, `struct tce_iommu_group`, and `struct tce_iommu_prereg`. The exported backend contract is `tce_iommu_driver_ops`, with `open`, `release`, `ioctl`, `attach_group`, and `detach_group`. Important functions include `tce_iommu_enable/disable`, `tce_iommu_register_pages`, `tce_iommu_build`, `tce_iommu_build_v2`, `tce_iommu_clear`, `tce_iommu_create_window`, `tce_iommu_remove_window`, `tce_iommu_take_ownership`, and `vfio_spapr_ioctl_eeh_pe_op`.

## Control flow
Open allocates a container for either `VFIO_SPAPR_TCE_IOMMU` or `VFIO_SPAPR_TCE_v2_IOMMU`. Attach validates table group data, v2 dynamic-window support, v1 single-group restrictions, compatibility with already attached groups, and takes ownership of any existing windows. V1 users enable the container before map/unmap; v2 users register memory and may create/remove dynamic windows. Map finds the TCE table for the IOVA, validates flags and alignment, translates userspace pages to HPAs, exchanges TCE entries, and flushes. Unmap clears TCE entries and releases pinned or preregistered memory references. Release detaches groups, frees VFIO-created tables, unregisters preregions, disables accounting, drops the mm, and frees the container.

## State and persistence behavior
State is per-container and in memory: attached groups, up to `IOMMU_TABLE_GROUP_MAX_TABLES` table pointers, preregistered memory list, owning mm, enabled flag, default-window pending flag, and locked page accounting. V1 accounts locked memory by worst-case DMA window size at enable/disable. V2 uses preregistered memory references and dynamic table allocation accounting.

## Dependencies and integration points
The backend depends on POWER IOMMU/TCE APIs, EEH, VFIO container IOMMU driver registration, user copy helpers, and mm IOMMU preregistration helpers. It integrates with userspace through VFIO sPAPR TCE ioctls and with platform firmware/hypervisor behavior through TCE table group operations.

## Risks and test signals
Risks include strict current-mm ownership, hot map/unmap paths with coarse locked-memory accounting, dynamic window compatibility across groups, and cleanup correctness for preregistered memory. Test signals include v1 enable/disable and single-group enforcement, v2 register/unregister memory, default window creation, dynamic window create/remove, map/unmap alignment failures, EEH operations, group detach while windows exist, and release cleanup with active preregions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio_iommu_spapr_tce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio_iommu_type1.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/vfio_iommu_type1.c

## Purpose
This file implements the generic VFIO Type1 IOMMU backend used for DMA mapping userspace memory into IOMMU domains. It supports v1 and v2 semantics, page pinning, IOVA aperture and reserved-region management, dirty page tracking, external device pin/unpin, and CPU-mediated DMA read/write.

## Important APIs, types, and functions
Main state types are `struct vfio_iommu`, `struct vfio_domain`, `struct vfio_dma`, `struct vfio_iommu_group`, `struct vfio_iova`, and `struct vfio_pfn`. The backend registers `vfio_iommu_driver_ops_type1`. Important functions include `vfio_dma_do_map`, `vfio_dma_do_unmap`, `vfio_pin_map_dma`, `vfio_unmap_unpin`, `vfio_iommu_replay`, `vfio_iommu_type1_attach_group`, `vfio_iommu_type1_detach_group`, `vfio_iommu_type1_dirty_pages`, `vfio_iommu_type1_pin_pages`, `vfio_iommu_type1_unpin_pages`, and `vfio_iommu_type1_dma_rw`.

## Control flow
Open allocates an IOMMU object, initializes domain/IOMMU lists and DMA rb-tree, sets `dma_avail`, and distinguishes v1 from v2. Attach allocates an IOMMU domain for the group, attaches it, validates interrupt remapping unless explicitly unsafe, intersects domain apertures, excludes reserved regions, attempts compatible-domain sharing, replays existing mappings into a new domain, and updates supported page sizes. MAP_DMA validates overflow, permissions, alignment, overlap, IOVA validity, and mapping limits, then pins userspace pages in batches, accounts memlock, maps them into every domain, and inserts a `vfio_dma` rb-tree node. UNMAP_DMA validates v1/v2 granularity rules, optionally invalidates vaddrs for update, notifies device DMA-unmap users, returns dirty bitmaps if requested, unmaps IOMMU entries, unpins pages, and removes DMA nodes. Dirty tracking allocates per-DMA bitmaps, populates them when scope changes, and reports by user bitmap.

## State and persistence behavior
All state is in kernel memory tied to a VFIO container: domain list, emulated groups, valid IOVA ranges, rb-tree of user DMA mappings, per-DMA pinned PFN tree, per-DMA dirty bitmap, owning task/mm, memlock accounting, dirty tracking flag, and device callback list. No disk persistence exists. Mappings can outlive the task thread because the mm and group leader references are retained.

## Dependencies and integration points
The backend depends on IOMMU API, mm/GUP long-term pinning, rbtree, VFIO core IOMMU driver registration, user access helpers, iova bitmap helpers, and optional emulated-IOMMU devices that use external pin/unpin callbacks. It feeds VFIO container ioctls and device helper APIs such as `vfio_pin_pages()` and `vfio_dma_rw()`.

## Risks and test signals
Risks include long-term pin accounting errors, reserved-region/aperture conflicts, unsafe-interrupt opt-in, dirty bitmap size validation, invalid-vaddr update races, and detach cleanup with external pinned pages. Test signals include v1 versus v2 unmap granularity, map overlap/overflow/alignment failures, `dma_entry_limit`, dirty tracking start/stop/get, update-vaddr rejection with mdevs, attach replay after mappings exist, detach of last domain, memlock limit failures, and kthread `dma_rw`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio_iommu_type1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio_main.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/vfio_main.c

## Purpose
This is the VFIO core implementation. It manages VFIO device allocation, registration, device sets, device fd operations, migration feature ioctls, DMA logging feature ioctls, region capability chains, IRQ-set validation, KVM association, cdev/group integration, module initialization, and helper APIs used by VFIO drivers.

## Important APIs, types, and functions
Major exported functions include `_vfio_alloc_device`, `vfio_register_group_dev`, `vfio_register_emulated_iommu_dev`, `vfio_unregister_group_dev`, `vfio_df_open`, `vfio_df_close`, `vfio_mig_get_next_state`, `vfio_file_is_valid`, `vfio_file_enforced_coherent`, `vfio_file_set_kvm`, `vfio_info_cap_add`, `vfio_info_cap_shift`, `vfio_set_irqs_validate_and_prepare`, `vfio_pin_pages`, `vfio_unpin_pages`, and `vfio_dma_rw`. The global `vfio` object tracks device IDs and a pseudo filesystem mount for anonymous inodes. `vfio_device_fops` is the device fd file operation table.

## Control flow
VFIO drivers allocate devices through `_vfio_alloc_device`, which initializes IDs, pseudo-fs inode, driver private init, and device model fields. Registration sets a device set if needed, assigns a VFIO group type, enforces IOMMU cache coherency for physical IOMMU devices, adds the device/cdev, initializes registration refcounting, registers group metadata, and creates debugfs. Opening a VFIO device file increments open count under the device-set lock; the first open binds iommufd or uses the group IOMMU, then calls the driver open callback. File ioctls require `access_granted`, runtime-PM resume, and dispatch built-in feature/region operations before driver-specific ioctls. Unregister blocks new opens, removes cdev/device visibility, requests userspace release while waiting for refs, then removes debugfs and group state.

## State and persistence behavior
State is in memory: device IDs, device sets in an xarray, per-device refcount/open count, pseudo-fs inode, access-granted bit, KVM pointer, cdev/group/iommufd association, and optional migration/logging state fields inside `struct vfio_device`. There is no disk persistence. Module parameters include unsafe no-IOMMU enablement when configured.

## Dependencies and integration points
The file integrates almost every VFIO subsystem: group, container, iommufd, cdev, virqfd, debugfs, KVM, runtime PM, IOMMU, pseudo filesystem, and driver-supplied `vfio_device_ops`. Userspace ABI is through VFIO device file operations and feature ioctls.

## Risks and test signals
Risks include registration/unregistration lifetime races, access gating before read/write/mmap/ioctl, optional migration FSM correctness, DMA logging range validation, and KVM symbol-get lifetime. Test signals include group and cdev open paths, repeated unregister while fd is open, migration state matrix, feature probe/get/set combinations, region capability sizing, IRQ validation data-size calculations, no-IOMMU taint/permissions, runtime PM failure, `vfio_pin_pages`/`vfio_dma_rw` through container and iommufd paths, and module init/cleanup ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/virqfd.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/virqfd.c

## Purpose
This file implements VFIO generic virqfd support: a small eventfd polling bridge that invokes a handler and optional threaded callback when userspace signals an eventfd, and cleans itself up when the eventfd is closed.

## Important APIs, types, and functions
Exported APIs are `vfio_virqfd_init`, `vfio_virqfd_exit`, `vfio_virqfd_enable`, `vfio_virqfd_disable`, and `vfio_virqfd_flush_thread`. Important helpers include `virqfd_wakeup`, `virqfd_ptable_queue_proc`, `virqfd_shutdown`, and `virqfd_inject`. Global state is a single-thread cleanup workqueue and `virqfd_lock`.

## Control flow
Initialization creates `vfio-irqfd-cleanup`. Enabling allocates a `struct virqfd`, obtains the eventfd context from the supplied fd, installs the virqfd pointer under lock if no existing virqfd is active, registers a custom poll wait callback, and handles already-pending `EPOLLIN`. On `EPOLLIN`, it reads the eventfd counter, runs the handler, and schedules optional thread work. On `EPOLLHUP`, it clears the owner pointer under lock and queues shutdown. Disable clears the pointer, queues shutdown if active, and flushes the cleanup workqueue.

## State and persistence behavior
State is per enabled virqfd: eventfd context, wait queue entry, poll table, owner pointer, opaque/data callbacks, and work items. Cleanup removes the wait queue, flushes inject work, drops the eventfd context, and frees memory. No persistent storage exists.

## Dependencies and integration points
It depends on eventfd, file/poll APIs, workqueues, and VFIO internal `struct virqfd` from UAPI/private headers. Platform IRQ and PCI IRQ paths use it for mask/unmask or interrupt injection control.

## Risks and test signals
Risks include double shutdown races, eventfd HUP ordering, handler/thread callback lifetime, and cleanup workqueue flushing latency. Test signals include enable with invalid fd, duplicate enable returning `-EBUSY`, pending event delivery at registration, eventfd close cleanup, disable while inject work is pending, and module exit after all virqfds are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/virqfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vhost/Kconfig

## Purpose
This Kconfig file defines vhost core, ring, IOTLB, and frontend/backend accelerator options for virtio net, SCSI, vsock, and vDPA. It also defines optional cross-endian and fork-owner controls.

## Important APIs, types, and functions
Core symbols are `VHOST_IOTLB`, `VHOST_RING`, `VHOST_TASK`, and `VHOST`. User-visible symbols under `VHOST_MENU` include `VHOST_NET`, `VHOST_SCSI`, `VHOST_VSOCK`, `VHOST_VDPA`, `VHOST_CROSS_ENDIAN_LEGACY`, and `VHOST_ENABLE_FORK_OWNER_CONTROL`.

## Control flow
Driver options select the hidden core symbols they need. `VHOST_NET`, `VHOST_SCSI`, `VHOST_VSOCK`, and `VHOST_VDPA` select `VHOST`; `VHOST_RING` selects `VHOST_IOTLB`; `VHOST` selects both `VHOST_IOTLB` and `VHOST_TASK`. Dependency expressions ensure required subsystems such as `EVENTFD`, `TARGET_CORE`, `VSOCKETS`, `VDPA`, TUN/TAP, and IRQ bypass are present.

## State and persistence behavior
There is no runtime state. The persistent output is the configured kernel/module feature set and default enablement of fork-owner control.

## Dependencies and integration points
The file integrates with the vhost Makefile and with networking, target core, vsock, vDPA, eventfd, and virtio subsystems. The fork-owner option changes availability of vhost worker mode ioctls and a module parameter in the core.

## Risks and test signals
Risks include dependency drift causing build breaks or exposing ioctls unexpectedly. Test signals include config combinations for each vhost driver as built-in and module, absence of EVENTFD, cross-endian ioctl availability only when enabled, and fork-owner ioctl/module-parameter presence when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vhost/Makefile

## Purpose
This Makefile maps vhost Kconfig symbols to vhost object modules.

## Important APIs, types, and functions
It builds `vhost_net.o` from `net.o`, `vhost_scsi.o` from `scsi.o`, `vhost_vsock.o` from `vsock.o`, `vringh.o` for `VHOST_RING`, `vhost_vdpa.o` from `vdpa.o`, `vhost.o` for core, and `vhost_iotlb.o` from `iotlb.o`.

## Control flow
Kbuild includes each object according to the corresponding `CONFIG_VHOST_*` symbol. Hidden core symbols selected by Kconfig ensure shared dependencies such as vhost core and IOTLB support are available before dependent drivers link.

## State and persistence behavior
No runtime state exists. The file persists only build composition and module naming.

## Dependencies and integration points
It depends on the Kconfig symbols in the same directory and integrates vhost frontend accelerators with core and IOTLB support.

## Risks and test signals
Risk is limited to object naming and missing dependencies between hidden symbols. Test signals are clean builds for every vhost module as `m` and `y`, plus link coverage when multiple frontends select the same core object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/iotlb.c -->
# sources/distributed-fs/ceph-client/drivers/vhost/iotlb.c

## Purpose
This file implements a generic software IOTLB mapping cache used by vhost and vringh code. It stores IOVA-to-host-address ranges in an interval tree plus an insertion-order list for optional retirement.

## Important APIs, types, and functions
Exported functions include `vhost_iotlb_map_free`, `vhost_iotlb_add_range_ctx`, `vhost_iotlb_add_range`, `vhost_iotlb_del_range`, `vhost_iotlb_init`, `vhost_iotlb_alloc`, `vhost_iotlb_reset`, `vhost_iotlb_free`, `vhost_iotlb_itree_first`, and `vhost_iotlb_itree_next`. `INTERVAL_TREE_DEFINE` creates static interval-tree helpers for `struct vhost_iotlb_map`.

## Control flow
Initialization sets an empty cached rb-root, map limit, flags, count, and list head. Add validates `last >= start`, splits the full `[0, ULONG_MAX]` range to avoid size overflow, optionally retires the oldest mapping when the limit is reached with `VHOST_IOTLB_FLAG_RETIRE`, allocates a map, inserts it into the interval tree, and appends it to the list. Delete repeatedly finds and frees overlapping mappings. Reset deletes the entire IOVA range.

## State and persistence behavior
State lives in the caller-owned or allocated `struct vhost_iotlb`: interval-tree root, FIFO list, map count, limit, and flags. Each map stores start, last, size, translated address, permissions, and opaque context. No persistence exists outside memory.

## Dependencies and integration points
The code depends on `linux/vhost_iotlb.h`, slab allocation, module exports, and Linux interval tree infrastructure. It is consumed by vhost core, vDPA, vringh, or tests that need software IOTLB lookups.

## Risks and test signals
Risks include overlapping additions not being rejected, FIFO retirement semantics surprising callers, atomic allocation failure, and full-range split correctness. Test signals include add/delete overlap queries, limit-retire behavior, reset/free idempotence, full-range mapping split into two entries, permission propagation, opaque pointer preservation, and interval iteration ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/iotlb.c -->
