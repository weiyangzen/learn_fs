# Research: subset-b-005433 VME user framework, TURBOchannel core, and TEE AMD interface

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme.c -->
# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme.c

## Purpose
Implements the staging VME bridge framework: a Linux bus type named `vme`, bridge registration, software enumeration of VME devices per bridge, and exported resource APIs for VME master windows, slave windows, DMA engines, interrupts, location monitors, bus errors, and bridge-local coherent allocation.

## Important APIs, Types, and Functions
Important exported APIs include `vme_register_bridge()`, `vme_unregister_bridge()`, `vme_register_driver()`, `vme_unregister_driver()`, `vme_slave_request/set/get/free()`, `vme_master_request/set/get/read/write/rmw/mmap_prepare/free()`, `vme_dma_request()`, `vme_new_dma_list()`, `vme_dma_*_attribute()`, `vme_dma_list_add/exec/free()`, `vme_irq_request/free/generate()`, `vme_lm_request/set/get/attach/detach/free()`, `vme_alloc_consistent()`, `vme_free_consistent()`, `vme_check_window()`, `vme_slot_num()`, and `vme_bus_num()`. The file also exports the `vme_bus_type` bus object.

## Control Flow
Bridge drivers call `vme_init_bridge()` and `vme_register_bridge()` after filling resource lists and callback function pointers. VME client drivers call `vme_register_driver()`, which registers the generic driver and creates up to `ndevs` synthetic `struct vme_dev` instances for every registered bridge. Matching requires the device `platform_data` to point to the same `struct vme_driver` and optionally pass the driver's `match()` callback. Resource requests scan the bridge's resource lists, lock the first compatible unlocked resource, and return a small `struct vme_resource` wrapper. Later operations validate the resource type and delegate to bridge-specific callbacks.

## State and Persistence Behavior
Global framework state is `vme_bus_numbers`, `vme_bus_list`, and `vme_buses_lock`. Per-resource locked state persists in bridge-owned resource structs until the corresponding free call. IRQ callback state persists in `bridge->irq[level - 1].callback[statid]` and `count`. Bus error handlers are bridge-local list entries with first-error and count accumulation. No state is persisted outside kernel memory or device registers.

## Dependencies and Integration Points
Depends on the Linux driver core, list/mutex/spinlock primitives, DMA mapping types, mmap helpers, and bridge contracts from `vme_bridge.h`. Provider implementations in `vme_fake.c` and `vme_tsi148.c` fill callbacks; `vme_user.c` consumes master/slave/IRQ APIs.

## Risks and Test Signals
Several APIs call `find_bridge(resource)` before fully validating `resource`, so callers must not pass null or stale resources. `vme_irq_request()` indexes `statid` without checking `0..255`; bad callers can corrupt callback state. DMA resource request logs that route attributes are not fully tested. `vme_bus_error_handler()` walks handler lists without an explicit lock. Test signals are clean bridge probe/remove, driver registration across multiple bridges, resource double-free warnings, master mmap bounds rejection, IRQ request/free refcounting per level, DMA busy/free rejection, and bus-error routing with `err_chk`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme.h -->
# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme.h

## Purpose
Defines the public VME framework ABI used by in-kernel VME client drivers. It names VME resource types, address spaces, cycle attributes, data widths, DMA route/attribute flags, device/driver objects, and the exported framework function prototypes implemented in `vme.c`.

## Important APIs, Types, and Constants
Key constants are `VME_A16/A24/A32/A64/CRCSR/USER*`, `VME_*_MAX`, cycle flags such as `VME_SCT`, `VME_BLT`, `VME_2eSST*`, privilege/data flags, `VME_D8/D16/D32/D64`, DMA attribute types and route flags, `VME_NUM_STATUSID`, `VME_MAX_BRIDGES`, `VME_MAX_SLOTS`, `VME_SLOT_CURRENT`, and `VME_SLOT_ALL`. `struct vme_resource` is the opaque client handle for master/slave/DMA/location-monitor resources. `struct vme_dev` wraps a driver-core `device`, bridge pointer, synthetic device number, and list links. `struct vme_driver` wraps a driver-core `device_driver` plus `match`, `probe`, and `remove` callbacks.

## Control Flow and State
This header has no executable flow, but it defines the contracts used when VME bridges register resources and VME client drivers request them. The `struct vme_resource.entry` points back into a bridge-owned resource list; its lifetime depends on the bridge and on the client calling the matching `vme_*_free()` API.

## Dependencies and Integration Points
Includes Linux bit operations and forward uses driver-core, DMA, list, and mmap descriptor types via included kernel headers in users. It is shared by the framework, fake bridge, TSI148 bridge, and user-space access driver.

## Risks and Test Signals
The flag model allows combinations that may not be valid for a particular bridge; runtime validation is split between `vme.c` and bridge callbacks. The `VME_A64_MAX` macro represents `U64_MAX + 1`, which cannot be stored in 64 bits and is used only as a conceptual bound. Test signals are successful compilation of bridge/client modules, correct compatibility filtering in resource requests, and user drivers not dereferencing `struct vme_resource.entry` directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_bridge.h -->
# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_bridge.h

## Purpose
Defines the private provider-side contract for VME bridge drivers. It describes bridge-owned resource structs, IRQ callback tables, error handlers, DMA list state, and the function-pointer table that concrete bridges must fill before registering with `vme.c`.

## Important APIs, Types, and Constants
Important structs are `vme_master_resource`, `vme_slave_resource`, `vme_dma_resource`, `vme_dma_list`, `vme_dma_pattern`, `vme_dma_pci`, `vme_dma_vme`, `vme_lm_resource`, `vme_error_handler`, `vme_callback`, `vme_irq`, and `vme_bridge`. `VME_CRCSR_BUF_SIZE` defines the 508 KiB CR/CSR backing image size. `struct vme_bridge` carries lists for every resource class, `driver_priv`, parent `device`, per-level IRQ callbacks, and callback pointers for slave, master, DMA, IRQ, location-monitor, slot, and coherent-allocation operations.

## Control Flow and State
Bridge drivers allocate and initialize resource structs, attach them to the lists in `struct vme_bridge`, set callback pointers, and then call `vme_register_bridge()`. Client-facing operations in `vme.c` recover the concrete resource with `list_entry()` from `struct vme_resource.entry` and invoke the relevant callback. Locks are per-resource: master windows use spinlocks to support interrupt-context access; slave/DMA/LM resources use mutexes.

## Dependencies and Integration Points
Includes `vme.h` and is consumed by both provider implementations (`vme_fake.c`, `vme_tsi148.c`) plus framework internals. The callback table is the integration seam between generic resource management and hardware-specific MMIO/software emulation.

## Risks and Test Signals
The framework assumes list entries remain valid while resources are checked out; bridge removal must unregister devices before freeing resources. Callback pointers are optional, so client APIs must handle unsupported operations. Test bridge registration/unregistration under client driver load, lockdep on mixed master spinlock and DMA/location-monitor mutex paths, and teardown with IRQ callbacks still registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_fake.c -->
# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_fake.c

## Purpose
Provides a fake VME bridge module for exercising the VME framework without VME hardware. It models eight master windows, eight slave windows, one four-address location monitor block, CR/CSR storage, and software-generated VME interrupts using heap memory and a tasklet.

## Important APIs, Types, and Functions
The bridge private state is `struct fake_driver`, with arrays of `fake_slave_window` and `fake_master_window`, location monitor callbacks, interrupt-generation fields, CR/CSR buffer, and a mutex for generated interrupts. Main callbacks are `fake_slave_set/get()`, `fake_master_set/get/read/write/rmw()`, `fake_irq_set()`, `fake_irq_generate()`, `fake_lm_set/get/attach/detach()`, `fake_slot_get()`, `fake_alloc_consistent()`, and `fake_free_consistent()`. Module entry/exit are `fake_init()` and `fake_exit()`.

## Control Flow
`fake_init()` validates `geoid`, creates a root `vme` device, allocates bridge/private state, initializes resources, fills callback pointers, initializes CR/CSR memory, and registers the bridge. Master reads/writes compute the VME address from the configured master window and scan matching fake slave windows by address space and cycle. Access helpers perform 8/16/32-bit operations and run location-monitor checks. `fake_irq_generate()` stores level/vector and schedules `fake_VIRQ_tasklet()`, which calls the generic `vme_irq_handler()`.

## State and Persistence Behavior
All bridge state is volatile kernel memory. Slave buffers are host pointers encoded as fake DMA addresses. Master/slave configuration persists in private arrays until changed or module exit. Location-monitor callbacks persist in arrays and are invoked during fake VME accesses.

## Dependencies and Integration Points
Depends on the VME framework, root device registration, module parameters, tasklets, locks, and heap allocation. It provides the same bridge callback table as hardware bridges, letting `vme_user` and other VME clients test framework paths.

## Risks and Test Signals
It intentionally lacks true hardware timing, posted-write, DMA, and PCI resource behavior. `fake_master_rmw()` appears to use logical `&&` rather than bitwise `&` in its compare expression, making RMW semantics suspect. Monitor indices are not range-checked in attach/detach. Test signals include fake bridge load/unload, `vme_user` reads/writes between configured master and slave windows, location monitor callback firing, IRQ generation to registered callbacks, and no leaks on failed allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_fake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_tsi148.c -->
# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_tsi148.c

## Purpose
Implements the real PCI driver for the Tundra/Tempe TSI148 VME-PCI bridge. It maps the chip register block, exposes VME framework resources, programs inbound/outbound translation windows, handles VME/PCI/DMA/location-monitor interrupts, builds DMA linked lists, supports RMW and generated VME IRQs, and configures CR/CSR space.

## Important APIs, Types, and Functions
Important regions are PCI probe/remove (`tsi148_probe()`, `tsi148_remove()`), interrupt setup/dispatch (`tsi148_irq_init()`, `tsi148_irqhandler()`, `tsi148_irq_set()`, `tsi148_irq_generate()`), slave translation (`tsi148_slave_set/get()`), master translation and access (`tsi148_master_set/get/read/write/rmw()`), DMA (`tsi148_dma_list_add/exec/empty()`, VME attribute encoders), location monitors (`tsi148_lm_set/get/attach/detach()`), CR/CSR (`tsi148_crcsr_init/exit()`), and coherent allocation wrappers.

## Control Flow
Probe enables the PCI device, requests BARs, maps BAR0, validates the vendor ID, initializes queues and mutexes, requests IRQs, allocates VME resource objects, fills bridge callbacks, configures CR/CSR space, registers the bridge, and clears board-fail/power-reset state. Resource callbacks translate framework attributes into big-endian TSI148 registers. Master set allocates a PCI memory resource and ioremaps it before programming outbound translation registers. DMA list add allocates a hardware descriptor, fills source/destination/count fields in big-endian format, maps it for DMA, and links descriptors. DMA exec writes the first descriptor address to channel registers, starts `DGO`, waits for IRQ wakeup, and checks `DSTA`.

## State and Persistence Behavior
Persistent runtime state lives in `struct tsi148_driver`: MMIO base, DMA/IACK wait queues, LM callbacks, CR/CSR coherent image, optional flush master image, and mutexes for RMW and generated IRQ serialization. Window configuration persists in chip registers and in allocated PCI resources. DMA descriptors persist in list entries until `tsi148_dma_list_empty()`.

## Dependencies and Integration Points
Depends on PCI, MMIO, DMA mapping, wait queues, IRQs, big-endian register access, and the VME framework. `vme_user` can consume the master/slave/IRQ callbacks. The `err_chk` module parameter integrates VME exception interrupts with generic VME error-handler windows.

## Risks and Test Signals
`tsi148_dma_busy()` returns false-like `0` when busy and true-like `1` when not busy, so its name is misleading but matches wait predicates. Generated IRQ wait lacks a timeout. Some callback paths do not range-check monitor/statid inputs at this layer. Error-check handlers are installed while holding master spinlocks, making interrupt/error-list behavior worth lockdep review. Test signals include PCI probe/remove, window alignment rejection, A16/A24/A32/A64 translations, master read/write with and without `err_chk`, DMA completion/abort/error paths, location monitor interrupts, VME IRQ request/generate/free, and CR/CSR mapping by geographic address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_tsi148.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_tsi148.h -->
# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_tsi148.h

## Purpose
Provides the TSI148 chip contract used by `vme_tsi148.c`: PCI IDs, resource counts, private driver state, DMA descriptor layout, and a comprehensive register/bitfield map for PCI config, local control/status, global CSR, CR/CSR, inbound/outbound windows, DMA engines, interrupts, VME status, errors, RMW, and location monitors.

## Important APIs, Types, and Constants
Key constants include `TSI148_MAX_MASTER`, `TSI148_MAX_SLAVE`, `TSI148_MAX_DMA`, register base arrays such as `TSI148_LCSR_OT[]`, `TSI148_LCSR_IT[]`, `TSI148_LCSR_DMA[]`, `TSI148_LCSR_VIACK[]`, `TSI148_GCSR_MBOX[]`, and mask arrays for LM/VIRQ interrupt enable/status/clear. `struct tsi148_driver` stores MMIO base, wait queues, callback arrays, CR/CSR image, flush image, and serialization mutexes. `struct tsi148_dma_descriptor` is the hardware-consumed big-endian linked-list descriptor; `struct tsi148_dma_entry` wraps it with list and DMA handle state.

## Control Flow and State
The header has no executable code, but every MMIO operation in `vme_tsi148.c` depends on these offsets and masks. Register arrays allow indexed programming of eight outbound and inbound windows, two DMA channels, seven VIRQ acknowledge registers, four mailboxes, and four location monitor bits.

## Dependencies and Integration Points
Depends on Linux PCI ID definitions and VME resource declarations indirectly through the C file. It integrates the generic VME attributes with TSI148-specific encodings such as `OTAT`, `ITAT`, `DSAT`, `DDAT`, `INTEN`, `INTEO`, `INTS`, `INTC`, `VICR`, and `VEAT`.

## Risks and Test Signals
Any offset or endian mismatch can corrupt bridge programming. The DMA descriptor layout must remain 64-bit aligned and big-endian for hardware. Static arrays in a header create per-translation-unit objects, acceptable here because the header is only used locally but worth avoiding for broader inclusion. Test signals are register readback after window programming, DMA descriptor dumps matching the hardware manual, interrupt mask/clear behavior per source, and successful CR/CSR and geographic-address setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_tsi148.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_user.c -->
# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_user.c

## Purpose
Implements the legacy `/dev/bus/vme/*` character-device access driver on top of the VME framework. It exposes four master devices, four slave devices, and one control device using major 221, allowing user space to configure windows, read/write mapped VME master space, access slave backing buffers, mmap master windows, and generate VME interrupts.

## Important APIs, Types, and Functions
Important state is `struct image_desc image[VME_DEVS]`, holding per-minor buffers, DMA addresses, mutexes, sysfs device pointers, VME resources, and mmap counts. File operations are `vme_user_read()`, `vme_user_write()`, `vme_user_llseek()`, `vme_user_unlocked_ioctl()`, and `vme_user_mmap_prepare()`. IOCTL helpers handle `VME_GET/SET_MASTER`, `VME_GET/SET_SLAVE`, and `VME_IRQ_GEN`. Driver lifecycle is `vme_user_match()`, `vme_user_probe()`, `vme_user_remove()`, `vme_user_init()`, and `vme_user_exit()`.

## Control Flow
Module load requires a `bus=` parameter and registers a VME driver for `VME_MAX_SLOTS`; matching admits the configured bus/slot only. Probe registers the fixed char region, adds a cdev, requests four slave resources and coherent 128 KiB buffers, requests four A32/SCT/D32 master resources and bounce buffers, registers a class, and creates device nodes. Reads/writes lock the image, clamp by current VME window size, then either delegate to VME master read/write through a bounce buffer or copy from/to the slave backing buffer. Master mmap delegates to `vme_master_mmap_prepare()` and tracks active mappings via VMA private refcounts.

## State and Persistence Behavior
State is global and supports only one probed VME user device at a time (`vme_user_bridge`). Master/slave image state persists from probe until remove. `mmap_count` blocks master window reconfiguration while mappings exist. Slave buffers are coherent allocations and are used as inbound VME storage.

## Dependencies and Integration Points
Depends on the VME framework, char devices, class/device sysfs, uaccess, mmap_prepare VMA hooks, and fixed device numbers documented for VME. It consumes ABI structs from `vme_user.h`.

## Risks and Test Signals
Probe error unwinds assume resources/buffers were initialized for every index in some paths; partial failures need careful testing. `vme_user_bridge` is not reset in remove. Reads/writes use `image_size - 1`, so a zero-size window can underflow. The ABI passes raw framework address/cycle/width flags to user space despite comments questioning this. Test signals include device-node creation, IOCTL get/set round trips, reconfiguration blocked during mmap, offset clamping, slave buffer DMA visibility, cleanup after partial probe failure, and unload/reload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_user.h -->
# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_user.h

## Purpose
Defines the user-visible ioctl ABI for the staging VME user-space access driver. It contains packed master/slave configuration structs, interrupt-generation arguments, ioctl command numbers, and the current limit of one configured bus.

## Important APIs, Types, and Constants
`VME_USER_BUS_MAX` limits module parameter handling to one bus. `struct vme_master` contains enable, VME base, size, address space, cycle flags, and data width. `struct vme_slave` contains enable, VME base, size, address space, and cycle flags. `struct vme_irq_id` carries an interrupt level and status/vector ID. IOCTLs are `VME_GET_SLAVE`, `VME_SET_SLAVE`, `VME_GET_MASTER`, `VME_SET_MASTER`, and `VME_IRQ_GEN`, all under magic `0xAE`.

## Control Flow and State
This header has no runtime logic. `vme_user.c` copies these packed structs to and from user space and translates them directly into VME framework calls.

## Dependencies and Integration Points
The structs use fixed-width `__u*` types and must stay compatible with user programs and compat ioctl handling. The constants mirror the legacy `/dev/bus/vme/*` ABI.

## Risks and Test Signals
Because structs are packed and contain 64-bit fields, ABI layout must be verified on 32-bit and 64-bit user space. The ABI exposes raw framework flag values, so mismatches with `vme.h` would break applications. Test with ioctl struct-size checks, compat users, invalid level/statid inputs, and get/set round trips for master and slave windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tc/Makefile

## Purpose
Builds the TURBOchannel bus support objects when `CONFIG_TC` is enabled.

## Important APIs, Types, and Functions
The only build rule is `obj-$(CONFIG_TC) += tc.o tc-driver.o`, which links bus probing/enumeration from `tc.c` with driver-core services from `tc-driver.c`.

## Control Flow and State
No runtime flow. Kbuild includes these objects in the kernel or module according to the `CONFIG_TC` tristate/bool configuration.

## Dependencies and Integration Points
Depends on the architecture/configuration exposing `CONFIG_TC` and public declarations in `<linux/tc.h>`.

## Risks and Test Signals
If either object is omitted, the TC bus either cannot enumerate devices or cannot match/register drivers. Test signals are successful builds for TC-enabled architectures and presence of `tc_bus_type` plus `tc_init()` in the final image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tc/tc-driver.c -->
# sources/distributed-fs/ceph-client/drivers/tc/tc-driver.c

## Purpose
Provides Linux driver-core services for TURBOchannel devices: driver registration/unregistration, device ID matching, and registration of the `tc` bus type.

## Important APIs, Types, and Functions
Exports `tc_register_driver()`, `tc_unregister_driver()`, and `tc_bus_type`. Internal helpers are `tc_match_device()` and `tc_bus_match()`. Matching compares `struct tc_dev` `name` and `vendor` strings with a driver's `struct tc_device_id` table until an all-zero sentinel.

## Control Flow
`tc_driver_init()` registers `tc_bus_type` at `postcore_initcall`. TC drivers call `tc_register_driver()`, which delegates to `driver_register()` on the embedded `device_driver`. When the driver core evaluates a device/driver pair, `tc_bus_match()` converts generic pointers to TC objects and returns true if the ID table has matching name and vendor strings.

## State and Persistence Behavior
The only persistent state is the registered `tc_bus_type` and registered device drivers in the driver core. This file does not own device instances; those are created in `tc.c`.

## Dependencies and Integration Points
Depends on `<linux/tc.h>`, module exports, and the generic driver core. `tc.c` assigns `tdev->dev.bus = &tc_bus_type`, and TC device drivers consume the exported registration helpers.

## Risks and Test Signals
ID matching is exact string matching on fixed firmware strings, so padding/termination from firmware probing must be correct. There are no probe/remove callbacks in `tc_bus_type`; TC driver binding relies on the generic driver callbacks embedded in `tdrv->driver`. Test signals include bus registration before TC devices are registered, module alias matching where available, and successful binding for known vendor/module strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tc/tc-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tc/tc.c -->
# sources/distributed-fs/ceph-client/drivers/tc/tc.c

## Purpose
Implements TURBOchannel bus discovery and device registration. It obtains platform bus geometry, reserves slot memory ranges, probes each slot for a ROM signature, extracts module metadata, sets DMA masks and resources, obtains IRQs, and registers `struct tc_dev` devices on the TC bus.

## Important APIs, Types, and Functions
The static `tc_bus` object represents the root TURBOchannel bus. `tc_init()` is the subsystem initializer. `tc_bus_add_devices()` scans slots and creates `struct tc_dev` instances. It uses platform helpers such as `tc_bus_get_info()`, `tc_get_speed()`, `tc_preadb()`, and `tc_device_get_irq()` declared by the TC subsystem/architecture.

## Control Flow
`tc_init()` asks the platform for bus info, registers the root bus device, reserves standard and optional extended slot memory resources, prints bus revision/speed/parity, and calls `tc_bus_add_devices()`. Each slot is ioremapped, old-card and then new-card ROM offsets are checked for the `55 00 aa ff` pattern, metadata strings are read at four-byte spacing, device size determines standard versus extended slot resource assignment, IRQ is filled, and `device_register()` publishes the device.

## State and Persistence Behavior
The root `tc_bus` and registered `tc_dev` objects persist for kernel lifetime. Each device stores firmware/vendor/name strings, slot number, memory resource, DMA mask, parent bus pointer, and list node. There is no removal path in this file, matching the mostly static platform bus model.

## Dependencies and Integration Points
Depends on architecture-specific TC probing/IRQ helpers, `iomem_resource`, MMIO mapping, DMA mask support, and `tc_bus_type` from `tc-driver.c`. TC device drivers bind via exact vendor/name matching.

## Risks and Test Signals
The slot ioremap uses `BUG_ON(!module)`, so mapping failure is fatal. `tc_init()` returns success even after several setup failures, which can hide missing TC hardware/resource reservation failures. Device allocation/register failures skip the slot but continue. Test signals include correct ROM pattern detection for old/new card offsets, resource reservation conflicts, extended slot sizing, IRQ assignment, DMA mask propagation, and driver binding by firmware strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tc/tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/tee/Kconfig

## Purpose
Defines the top-level Kconfig menu for generic Trusted Execution Environment support and includes provider-specific TEE backends.

## Important APIs, Types, and Constants
`menuconfig TEE` is a tristate depending on `HAVE_ARM_SMCCC || COMPILE_TEST || CPU_SUP_AMD` and selects `CRYPTO_LIB_SHA1`, `DMA_SHARED_BUFFER`, and `GENERIC_ALLOCATOR`. `TEE_DMABUF_HEAPS` is a bool enabled by default when TEE, DMA, and dmabuf heaps are available. The file sources OP-TEE, AMDTEE, ARM TSTEE, and QCOMTEE Kconfig files.

## Control Flow and State
No runtime flow. Build configuration decides whether the generic TEE core and backend drivers are built in, modular, or omitted.

## Dependencies and Integration Points
Integrates TEE core configuration with architecture SMCCC support, AMD CPU support, shared DMA buffers, crypto SHA1, generic allocator, and provider subdirectories.

## Risks and Test Signals
Dependency changes affect which platforms can even see TEE support. `TEE_DMABUF_HEAPS` defaults on only when heap infrastructure exists. Test signals are Kconfig coverage for ARM, AMD, and COMPILE_TEST builds, plus correct provider menu visibility under `TEE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tee/Makefile

## Purpose
Defines the build composition for the generic TEE core and provider backends.

## Important APIs, Types, and Functions
`obj-$(CONFIG_TEE) += tee.o` builds the generic aggregate object from `tee_core.o`, `tee_heap.o`, `tee_shm.o`, and `tee_shm_pool.o`. Provider directories are included through `obj-$(CONFIG_OPTEE)`, `obj-$(CONFIG_AMDTEE)`, `obj-$(CONFIG_ARM_TSTEE)`, and `obj-$(CONFIG_QCOMTEE)`.

## Control Flow and State
No runtime flow. Kbuild links generic TEE support and selected provider drivers according to Kconfig.

## Dependencies and Integration Points
Depends on the source files in `drivers/tee/` and provider subdirectories. The generic object supplies shared device, heap, shared-memory, and pool services consumed by backends.

## Risks and Test Signals
Omitting a generic object would break backend linkage or user ABI support. Test signals include all selected providers linking against `tee.o`, module/built-in combinations for `CONFIG_TEE=m/y`, and no orphan provider object when TEE core is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/tee/amdtee/Kconfig

## Purpose
Declares the AMD-TEE backend configuration option.

## Important APIs, Types, and Constants
`config AMDTEE` is a tristate named "AMD-TEE", defaults to module, and depends on `CRYPTO_DEV_SP_PSP` plus `CRYPTO_DEV_CCP_DD`. Its help text identifies it as AMD's TEE driver.

## Control Flow and State
No runtime flow. This option controls whether `drivers/tee/amdtee/` objects are built.

## Dependencies and Integration Points
Integrates AMDTEE with the AMD Secure Processor/PSP and CCP driver stack. It is sourced by the top-level TEE Kconfig only when `TEE` is enabled.

## Risks and Test Signals
Defaulting to module can expose build/link issues on systems with PSP/CCP enabled. Test signals are Kconfig dependency resolution for AMD and COMPILE_TEST builds, successful module builds, and backend probe only when required PSP services exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tee/amdtee/Makefile

## Purpose
Defines the AMDTEE backend aggregate object and its component source files.

## Important APIs, Types, and Functions
`obj-$(CONFIG_AMDTEE) += amdtee.o` builds the backend, and `amdtee-objs` includes `core.o`, `call.o`, and `shm_pool.o`.

## Control Flow and State
No runtime flow. Kbuild composes one AMDTEE module/built-in object from core registration, secure calls, and shared-memory pool support.

## Dependencies and Integration Points
Depends on the generic TEE core build and AMD PSP/CCP services selected by Kconfig. The component split maps to driver lifecycle, command invocation, and shared memory handling.

## Risks and Test Signals
Missing any component would break provider registration or command/shared-memory operations. Test signals include module link success and `modinfo`/built-in symbol presence for all three implementation areas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/amdtee_if.h -->
# sources/distributed-fs/ceph-client/drivers/tee/amdtee/amdtee_if.h

## Purpose
Defines the host-to-AMD Trusted OS command ABI used by the AMDTEE driver. The structures must match the secure-world TEE side and describe operation parameters, shared-memory mapping, Trusted Application load/unload, session open/close, and command invocation.

## Important APIs, Types, and Constants
`TEE_MAX_PARAMS` is 4. Parameter structs include `memref`, `value`, `tee_op_param`, and `tee_operation`. Parameter type constants match the GlobalPlatform TEE style, with helpers `TEE_PARAM_TYPE_GET()` and `TEE_PARAM_TYPES()`. Shared-memory descriptors are `tee_sg_desc`, `tee_sg_list`, and `tee_cmd_map_shared_mem`/`tee_cmd_unmap_shared_mem`. TA/session commands are `tee_cmd_load_ta`, `tee_cmd_unload_ta`, `tee_cmd_open_session`, `tee_cmd_close_session`, and `tee_cmd_invoke_cmd`.

## Control Flow and State
The header has no code, but command flow is map shared memory, optionally load a TA, open a session with `tee_operation`, invoke commands with in/out parameters, close the session, unload the TA, and unmap memory. Output fields such as `buf_id`, `ta_handle`, `session_info`, and `return_origin` carry secure-world state handles back to the host driver.

## Dependencies and Integration Points
Depends on fixed-width Linux integer types. It is included by AMDTEE implementation files that marshal command buffers to the PSP/Trusted OS interface and translate generic TEE parameters to AMDTEE commands.

## Risks and Test Signals
This is a binary ABI: field size, alignment, order, page alignment requirements, and maximum scatterlist count must match firmware. `TEE_MAX_SG_DESC` limits map commands to 64 contiguous segments. Test signals include ABI size/static assertions where available, shared-memory maps with multiple SG entries, oversized SG rejection, open/invoke parameter round trips for value and memref types, and correct propagation of `return_origin` and TA/session handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/amdtee/amdtee_if.h -->
