# Research: subset-b-001073

Grouped source research for subset B work item `subset-b-001073`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdrom/gdrom.c -->
# sources/distributed-fs/ceph-client/drivers/cdrom/gdrom.c

## Purpose
This file implements the Sega Dreamcast GD-ROM block and CD-ROM interface. It talks directly to Dreamcast GD-ROM ATA-like registers, exposes the drive as a single read-only `gendisk`, registers a Linux CD-ROM device, handles media/session ioctls, and services block-layer read requests through DMA.

## Important APIs, Types, and Functions
Key device state is the singleton `gdrom_unit gd`, holding the `gendisk`, `cdrom_device_info`, blk-mq queue/tag set, pending command flags, transfer flag, cached TOC, and last status. `struct gdromtoc` models the device TOC format, while `struct gdrom_id` receives identify data.

Hardware helpers include `gdrom_is_busy()`, `gdrom_data_request()`, `gdrom_wait_clrbusy()`, `gdrom_wait_busy_sleeps()`, `gdrom_spicommand()`, `gdrom_identifydevice()`, `gdrom_execute_diagnostic()`, and `gdrom_hardreset()`. CD-ROM operations are provided by `gdrom_ops`; block operations by `gdrom_bdops`; blk-mq dispatch by `gdrom_queue_rq()` and `gdrom_readdisk_dma()`. Probe/remove entry points are `probe_gdrom()` and `remove_gdrom()`.

## Control Flow
Module init registers a platform driver and a synthetic platform device named `gdrom`, causing `probe_gdrom()` to run. Probe clears singleton state, executes an ATA diagnostic, reads firmware identity, registers a dynamic block major, allocates CD-ROM and blk-mq/gendisk structures, registers the universal CD-ROM interface, installs command/DMA IRQ handlers, programs DMA mode and access windows, allocates a TOC buffer, then calls `add_disk()`.

CD-ROM command flow allocates a `packet_command`, sets `gd.pending`, issues a packet via `gdrom_packetcommand()`/`gdrom_spicommand()`, and waits on `command_queue` until `gdrom_command_interrupt()` clears pending. Data reads use `gdrom_readdisk_dma()`: derive GD sectors from block-layer 512-byte sectors, program DMA start/length/direction registers, send a read packet, set both pending and transfer, start DMA, wait for `gdrom_dma_interrupt()`, and complete the request.

## State and Persistence Behavior
All driver state is volatile kernel memory or hardware register state. `gd.pending` and `gd.transfer` coordinate interrupt completion with wait queues; `gd.status` captures the command/status register. `gd.toc` persists only while the driver is loaded. Hardware state includes the G1 reset register, DMA control registers, transfer protection window, and drive sense/error state. There is no persistent on-disk metadata written by the driver; writes are rejected.

## Dependencies and Integration Points
The driver depends on Dreamcast SH platform headers (`mach/dma.h`, `mach/sysasic.h`), raw I/O accessors, CD-ROM core, block layer/blk-mq, platform devices, and Dreamcast IRQ events `HW_EVENT_GDROM_CMD` and `HW_EVENT_GDROM_DMA`. It integrates with user space through `/dev/gdrom`, CD-ROM ioctls, disk media-change events, and block reads.

## Risks
The driver is singleton and heavily serialized by global fields; unexpected concurrent packet and DMA activity can corrupt `gd.pending` or `gd.transfer`. DMA assumes one contiguous segment and uses the first bio page directly, so queue limits are essential. Timeouts often clear flags after wait completion, but lower-level hardware may still be active. `wait_event_interruptible_timeout()` return values are mostly ignored, so signals and timeouts collapse into status checks. Register polling uses raw busy loops and fixed timeouts. Probe error unwinding must keep block, CD-ROM, IRQ, and tag-set lifetimes aligned.

## Test Signals
Useful signals are Dreamcast boot/probe logs showing diagnostic success and firmware identity, successful `add_disk()`, media-change events after disc swap, correct multisession LBA from `get_last_session`, successful reads with 2048-byte logical blocks, rejected writes, clean module unload, and no stuck pending/transfer waits under forced IRQ loss or read timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdrom/gdrom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/cdx/Kconfig

## Purpose
This Kconfig file introduces `CONFIG_CDX_BUS`, the core Composable DMA Transfer bus support option, and includes the controller subdirectory configuration.

## Important APIs, Types, and Functions
There are no C APIs here. The key symbol is `CDX_BUS`, a boolean option named "CDX Bus driver". It depends on `OF && ARM64 || COMPILE_TEST`, which permits normal device-tree ARM64 builds and broader compile coverage.

## Control Flow
During kernel configuration, enabling `CDX_BUS` makes the bus core buildable and then sources `drivers/cdx/controller/Kconfig` so controller drivers can be selected beneath the bus option.

## State and Persistence Behavior
The selected configuration persists in the kernel `.config`. At runtime, this symbol controls whether the CDX bus core and optional MSI support from the Makefile are compiled into the kernel image.

## Dependencies and Integration Points
The help text describes CDX devices as firmware-discovered, memory-mapped FPGA fabric devices exposed to APUs through a CDX controller. The symbol gates `drivers/cdx/Makefile` and controller options.

## Risks
The dependency expression relies on Kconfig precedence: `(OF && ARM64) || COMPILE_TEST`. Real hardware support requires OF and ARM64 even though compile-test can build elsewhere. Disabling this symbol removes all CDX bus registration and controller integration.

## Test Signals
Configuration tests should verify that `CDX_BUS=y` is selectable on ARM64+OF and under `COMPILE_TEST`, and that selecting it causes `cdx.o` and controller choices to appear in the build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/cdx/Makefile

## Purpose
This Makefile builds the CDX bus core and the CDX controller subtree when `CONFIG_CDX_BUS` is enabled, and adds optional MSI support when generic MSI IRQ infrastructure is present.

## Important APIs, Types, and Functions
It sets `ccflags-y += -DDEFAULT_SYMBOL_NAMESPACE='"CDX_BUS"'`, so exported symbols default to the `CDX_BUS` namespace unless overridden. Build targets are `cdx.o`, `controller/`, and conditionally `cdx_msi.o`.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_CDX_BUS)` to include the bus core and descend into `drivers/cdx/controller/`. If `CONFIG_GENERIC_MSI_IRQ` is defined, it also compiles `cdx_msi.o` for bus-level MSI domain support.

## State and Persistence Behavior
No runtime state is present. The file affects object inclusion and exported symbol namespace metadata in the resulting kernel/module build.

## Dependencies and Integration Points
The Makefile ties `CONFIG_CDX_BUS` to `cdx.c`, `cdx_msi.c`, and the controller Makefile. The namespace aligns with controller modules importing `CDX_BUS_CONTROLLER` and bus/controller symbols exporting under namespace annotations.

## Risks
When `CONFIG_GENERIC_MSI_IRQ` is off, the bus core must tolerate absent MSI-domain code. Namespace changes can break module linking if import/export annotations drift. The `controller/` descent depends on the subdirectory Kconfig deciding whether a controller object is actually built.

## Test Signals
Build with `CDX_BUS=y/m` with and without `GENERIC_MSI_IRQ`; confirm expected objects appear and no namespace import warnings are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/cdx.c -->
# sources/distributed-fs/ceph-client/drivers/cdx/cdx.c

## Purpose
This is the CDX bus core. It registers the `cdx` bus type, matches CDX devices to CDX drivers, exposes sysfs/debugfs management files, maps device resources to user space, integrates DMA/IOMMU/MSI setup, and provides controller-facing APIs for adding buses and devices.

## Important APIs, Types, and Functions
Public bus APIs include `cdx_dev_reset()`, `cdx_set_master()`, `cdx_clear_master()`, `__cdx_driver_register()`, `cdx_driver_unregister()`, `cdx_device_add()`, `cdx_bus_add()`, `cdx_register_controller()`, and `cdx_unregister_controller()`. Important globals are `cdx_bus_type`, `cdx_controller_ida`, `cdx_controller_lock`, and `cdx_debugfs_dir`.

Sysfs attributes include device identity (`vendor`, `device`, `subsystem_*`, `revision`, `class`, `modalias`), `remove`, `reset`, `driver_override`, bus-device `enable`, and bus-level `rescan`. Per-resource binary files `resource<N>` support `mmap()` through `cdx_mmap_resource()`.

## Control Flow
`postcore_initcall(cdx_bus_init)` registers the bus and creates debugfs. Controllers call `cdx_register_controller()`, which allocates an ID, runs the controller `scan()` callback, and marks the controller registered. Scanning code calls `cdx_bus_add()` for each bus and `cdx_device_add()` for each device. `device_add()` then triggers normal driver-core matching through `cdx_bus_match()` and `cdx_probe()`.

Device reset, bus enable/disable, MSI configuration, and bus-master changes are delegated to controller callbacks via `cdx->ops`. Bus rescan removes existing CDX devices, walks OF compatible controller nodes, and invokes each registered controller's scan method.

## State and Persistence Behavior
The bus core persists runtime device objects, controller IDs, device resources, driver override strings, bus enabled state, MSI metadata, and debugfs/sysfs files. Per-device lifetime is tied to `device_initialize()`/`device_add()`/`put_device()` and `cdx_device_release()`. No state is saved across reboot; all topology is rediscovered from controller firmware.

## Dependencies and Integration Points
It depends on Linux driver core, OF platform lookup, IDA, sysfs, debugfs, irq/MSI domain APIs, IOMMU DMA configuration, and public CDX headers. Controllers supply `struct cdx_controller` and operations. CDX device drivers bind through `struct cdx_driver` ID tables and callback methods.

## Risks
Recursive device removal must preserve child-before-parent ordering and avoid freeing `cdx_device` before release. Resource binary attributes are allocated with `GFP_ATOMIC` and must be removed on all error and unregister paths. `driver_override_show()` prints a potentially NULL string with `%s`, which depends on `sysfs_emit()`/format behavior tolerating NULL on the target kernel. `rescan_store()` can return early after `of_find_device_by_node()` failure while holding scoped node iteration but under a mutex; partial rescans are possible. DMA configuration must undo IOMMU default-domain use on failure. `cdx_mmap_resource()` relies on resource size and exclusivity checks to prevent invalid user mappings.

## Test Signals
Test with a mock or real controller exposing multiple buses and devices: bus registration, uevents/modalias matching, driver probe/remove, reset sysfs behavior, driver override binding, resource file creation/mmap bounds checks, debugfs resource listing, rescan after topology change, bus enable/disable, IOMMU stream ID mapping, and MSI setup when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/cdx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/cdx.h -->
# sources/distributed-fs/ceph-client/drivers/cdx/cdx.h

## Purpose
This private CDX bus header defines the controller-to-bus handoff structure and declares internal bus/controller integration APIs.

## Important APIs, Types, and Functions
`struct cdx_dev_params` carries all data needed to instantiate a `struct cdx_device`: controller pointer, parent bus device, IDs, bus/device numbers, resource array, resource count, requester ID, class, revision, MSI device ID, and MSI count. Declared functions are `cdx_register_controller()`, `cdx_unregister_controller()`, `cdx_device_add()`, `cdx_bus_add()`, and `cdx_msi_domain_init()`.

## Control Flow
Controller drivers fill `cdx_dev_params` from firmware enumeration, then call `cdx_device_add()`. They call `cdx_bus_add()` before adding child devices and register/unregister themselves through the controller APIs.

## State and Persistence Behavior
The header owns no state. Its structure layout defines the transient parameter contract copied into persistent `cdx_device` objects by `cdx_device_add()`.

## Dependencies and Integration Points
It includes `<linux/cdx/cdx_bus.h>` for public CDX types and constants such as `MAX_CDX_DEV_RESOURCES`. It is included by bus core, MSI support, and controller code.

## Risks
This header is a narrow ABI inside the CDX subsystem: field mismatches between firmware decode and bus object population can misidentify devices, expose wrong MMIO resources, or configure DMA/MSI with incorrect requester IDs. The documentation typo `@us_num` for `cdx_bus_add()` is harmless but can confuse generated docs.

## Test Signals
Compile all CDX objects together, then validate that firmware-provided IDs/resources/MSI counts appear correctly in sysfs, resource files, DMA configuration, and MSI domain setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/cdx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/cdx_msi.c -->
# sources/distributed-fs/ceph-client/drivers/cdx/cdx_msi.c

## Purpose
This file provides CDX MSI support. It creates a CDX-specific MSI irq domain layered over a parent ITS/MSI domain and forwards MSI message programming and enable/disable operations to controller firmware.

## Important APIs, Types, and Functions
Exported APIs are `cdx_enable_msi()`, `cdx_disable_msi()`, and `cdx_msi_domain_init()`. The IRQ chip is `cdx_msi_irq_chip`, with parent mask/unmask/eoi, affinity support, and deferred `irq_write_msi_msg` handling. Domain callbacks are `cdx_msi_prepare()` and `cdx_msi_set_desc()`.

## Control Flow
When a CDX device probes, the bus core can call `msi_setup_device_data()` if the controller has `msi_domain`. During allocation, `cdx_msi_prepare()` maps the device's `msi_dev_id` through the controller node's `msi-map` into a parent device ID and calls the parent MSI domain prepare callback. `cdx_msi_write_msg()` stores the message in the MSI descriptor and marks the CDX device pending; `irq_bus_sync_unlock()` later programs firmware through `dev_configure(CDX_DEV_MSI_CONF)`.

## State and Persistence Behavior
Per-device state includes `msi_write_pending`, `irqchip_lock`, `num_msi`, `msi_dev_id`, and the generic MSI descriptors. MSI enable state and message routing live in controller firmware/hardware after `cdx_enable_msi()`, `cdx_disable_msi()`, or message writes.

## Dependencies and Integration Points
It depends on OF `msi-map`, irqdomain, generic MSI core, parent domain operations, GIC ITS-like parent domains, and CDX controller `dev_configure()` support. The bus core attaches the resulting domain to CDX devices.

## Risks
Message writes are intentionally deferred so sleeping controller firmware calls do not happen under the MSI core's low-level write callback; missing the bus unlock path would leave firmware unprogrammed. `cdx_msi_prepare()` assumes the parent MSI domain has valid `msi_domain_info` and an `msi_prepare` op. Incorrect `msi-map` entries or mismatched `msi_dev_id` break interrupt delivery. `cdx_msi_write_irq_unlock()` clears pending before calling firmware and does not report errors to the MSI core.

## Test Signals
Validate `msi-map` parsing, domain creation, MSI allocation/free, message programming callbacks, interrupt delivery from CDX devices, affinity changes, enable/disable sequencing, and behavior when firmware `dev_configure()` fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/cdx_msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/cdx/controller/Kconfig

## Purpose
This Kconfig file defines the CDX controller driver option under `CONFIG_CDX_BUS`.

## Important APIs, Types, and Functions
The sole symbol is `CDX_CONTROLLER`, a tristate "CDX bus controller". It depends on `HAS_DMA` and selects `REMOTEPROC` and `RPMSG`, matching the controller's firmware transport requirements.

## Control Flow
If `CDX_BUS` is enabled, the menu allows selecting the controller. When selected, the controller Makefile builds the combined `cdx-controller` object.

## State and Persistence Behavior
Selection persists in `.config` and controls whether the platform/rpmsg/MCDI controller stack is compiled. Runtime state is owned by the C files.

## Dependencies and Integration Points
The option integrates the CDX bus with a remote processor firmware path over RPMsg. `HAS_DMA` is required because exposed CDX devices and MSI programming involve DMA-capable hardware.

## Risks
Selecting `REMOTEPROC` and `RPMSG` pulls in substantial infrastructure. A kernel with `CDX_BUS` but without `CDX_CONTROLLER` can still host other controller providers, but the Versal-Net controller will not bind.

## Test Signals
Kconfig tests should confirm the option appears only under `CDX_BUS`, selects RPMsg/remoteproc, and produces `cdx-controller.o` for built-in and module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/Makefile -->
# sources/distributed-fs/ceph-client/drivers/cdx/controller/Makefile

## Purpose
This Makefile builds the CDX controller module/object from platform-controller, RPMsg transport, MCDI core, and MCDI helper sources.

## Important APIs, Types, and Functions
The target is `cdx-controller.o`, composed from `cdx_controller.o`, `cdx_rpmsg.o`, `mcdi.o`, and `mcdi_functions.o`.

## Control Flow
Kbuild includes the aggregate object when `CONFIG_CDX_CONTROLLER` is enabled. The combined object registers the platform driver and RPMsg driver pieces needed for the controller.

## State and Persistence Behavior
No runtime state exists in this file. It controls link composition and therefore which internal symbols are available in one module.

## Dependencies and Integration Points
It is reached from `drivers/cdx/Makefile` when the bus subtree is built. The object imports CDX bus controller namespace symbols from the bus core.

## Risks
All four sources are tightly coupled; omitting any object breaks probe, RPMsg transport, or firmware RPC wrappers. Link-order issues are minimal because the files communicate through normal C symbols.

## Test Signals
Build `CONFIG_CDX_CONTROLLER=y` and `=m`; verify `cdx-controller` contains the platform driver, RPMsg driver, MCDI RPC engine, and helper wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/cdx_controller.c -->
# sources/distributed-fs/ceph-client/drivers/cdx/controller/cdx_controller.c

## Purpose
This file is the AMD/Xilinx Versal-Net CDX platform controller driver. It connects the CDX bus core to firmware operations implemented through the MCDI RPC engine over RPMsg.

## Important APIs, Types, and Functions
The platform driver is `cdx_pdriver`, matching `xlnx,versal-net-cdx`. CDX controller callbacks are `cdx_bus_enable()`, `cdx_bus_disable()`, `cdx_scan_devices()`, and `cdx_configure_device()`, collected in `cdx_ops`. RPMsg lifecycle hooks exposed to `cdx_rpmsg.c` are `cdx_rpmsg_post_probe()` and `cdx_rpmsg_pre_remove()`.

## Control Flow
`xlnx_cdx_probe()` allocates `struct cdx_mcdi`, initializes MCDI state, allocates `struct cdx_controller`, attaches CDX ops and private MCDI state, creates an MSI domain, then calls `cdx_setup_rpmsg()`. Once the RPMsg endpoint appears, `cdx_rpmsg_post_probe()` registers the controller with the bus core, which triggers scanning.

Scanning asks firmware for the number of CDX buses, adds each bus with `cdx_bus_add()`, asks firmware for each bus's device count, fetches each device config, fills `cdx_dev_params`, and calls `cdx_device_add()`. Device configuration requests from the bus are switched by type into MCDI helpers for MSI writes, device reset, bus mastering, or MSI enable.

## State and Persistence Behavior
The controller stores MCDI state in `cdx->priv`, the platform device in `cdx->dev`, ops in `cdx->ops`, and optionally `msi_domain`. Firmware topology is not cached here beyond bus/device objects created by the bus layer.

## Dependencies and Integration Points
It depends on platform devices, OF matching, irq domains, the CDX bus core, RPMsg setup/teardown, and MCDI helper functions. It imports `CDX_BUS_CONTROLLER` namespace symbols.

## Risks
Probe treats missing MSI domain as fatal even though some bus code has conditional MSI handling; this is correct only if hardware requires MSI. `cdx_scan_devices()` continues on per-bus/per-device failures, producing partial topology. RPMsg post-probe is asynchronous, so remove must unregister the controller and wait for MCDI quiescence before tearing down transport. Firmware RPC errors directly affect sysfs reset/enable/MSI operations.

## Test Signals
Probe on a device-tree node with valid `xlnx,rproc` and `msi-map`, verify RPMsg channel creation, controller registration, bus/device enumeration, partial failure logging, reset/bus-master/MSI sysfs actions, and clean remove with no outstanding MCDI commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/cdx_controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/cdx_controller.h -->
# sources/distributed-fs/ceph-client/drivers/cdx/controller/cdx_controller.h

## Purpose
This private header declares the boundary between the CDX platform controller, its RPMsg transport, and MCDI response handling.

## Important APIs, Types, and Functions
It declares `cdx_rpmsg_post_probe()`, `cdx_rpmsg_pre_remove()`, `cdx_rpmsg_send()`, `cdx_rpmsg_read_resp()`, `cdx_setup_rpmsg()`, and `cdx_destroy_rpmsg()`.

## Control Flow
`cdx_controller.c` calls setup/destroy and receives post/pre remove callbacks from the RPMsg layer. `mcdi.c` sends requests through the `cdx_mcdi_ops.mcdi_request` callback implemented by `cdx_controller.c`, which delegates to `cdx_rpmsg_send()`.

## State and Persistence Behavior
The header owns no state. The prototypes define how `struct cdx_mcdi` state moves between platform-driver code and RPMsg callbacks.

## Dependencies and Integration Points
It includes public CDX bus types and MCDI helper declarations. It is shared by `cdx_controller.c` and `cdx_rpmsg.c`.

## Risks
The header declares `cdx_rpmsg_read_resp()`, but the listed source set does not define or use it, indicating stale API surface. Any future use would fail to link unless implemented.

## Test Signals
Build coverage should catch prototype/definition drift. Runtime coverage should confirm setup/destroy and post/pre callbacks are invoked in the expected RPMsg lifecycle order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/cdx_controller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/cdx_rpmsg.c -->
# sources/distributed-fs/ceph-client/drivers/cdx/controller/cdx_rpmsg.c

## Purpose
This file implements the RPMsg transport for CDX controller firmware communication. It attaches to the remote R5 processor, creates an RPMsg endpoint named `mcdi_ipc`, forwards MCDI requests to firmware, and feeds firmware responses back into the MCDI engine.

## Important APIs, Types, and Functions
Exported internal APIs are `cdx_rpmsg_send()`, `cdx_setup_rpmsg()`, and `cdx_destroy_rpmsg()`. Important callbacks are `cdx_rpmsg_probe()`, `cdx_rpmsg_remove()`, `cdx_rpmsg_cb()`, and `cdx_rpmsg_post_probe_work()`. Remoteproc helpers are `cdx_attach_to_rproc()` and `cdx_detach_to_r5()`.

## Control Flow
Controller probe calls `cdx_setup_rpmsg()`, which parses the `xlnx,rproc` phandle, boots/attaches to the remote processor, stores the controller pointer in the RPMsg ID table's `driver_data`, initializes work, and registers the RPMsg driver. When the `mcdi_ipc` channel probes, an endpoint is created, `struct cdx_mcdi` receives `ept` and `rpdev`, and deferred work registers the CDX controller with the bus. Incoming RPMsg payloads are length-checked and passed to `cdx_mcdi_process_cmd()`.

## State and Persistence Behavior
Transport state lives in `struct cdx_mcdi`: remoteproc pointer `r5_rproc`, RPMsg endpoint `ept`, RPMsg device `rpdev`, and work item. The static RPMsg ID table temporarily stores one controller pointer in `driver_data`, making this transport effectively single-controller during setup.

## Dependencies and Integration Points
It depends on `remoteproc`, `rpmsg`, OF phandles, the MCDI core, and controller/bus lifecycle callbacks. It is the concrete `mcdi_request` transport used by `mcdi.c`.

## Risks
The static `driver_data` handoff is fragile for multiple controllers probing concurrently. `cdx_rpmsg_send()` allocates a combined buffer for every command and does not retry RPMsg send failures. `cdx_attach_to_rproc()` calls `rproc_boot()` but teardown uses `rproc_detach()`, so semantics depend on the remoteproc provider. Remove flushes post-probe work before unregistering the controller, which is necessary to avoid registering after teardown. Payload length validation only checks upper bound and trusts MCDI parsing for structure.

## Test Signals
Exercise deferred probe when the remote processor is unavailable, RPMsg endpoint creation/removal, command send failure injection, oversized response rejection, controller registration only after RPMsg probe, and teardown with in-flight work or MCDI commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/cdx_rpmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/mc_cdx_pcol.h -->
# sources/distributed-fs/ceph-client/drivers/cdx/controller/mc_cdx_pcol.h

## Purpose
This generated-style protocol header defines the CDX subset of the MCDI management-controller protocol: message header fields, error codes, CDX bus/device commands, payload layouts, and v2 extended-command encapsulation.

## Important APIs, Types, and Functions
The file defines protocol constants rather than functions. Important groups are `MCDI_HEADER_*` bit fields, `MCDI_CTL_SDU_LEN_MAX_V2`, `MC_CMD_ERR_*` values, CDX commands `MC_CMD_CDX_BUS_ENUM_BUSES`, `MC_CMD_CDX_BUS_ENUM_DEVICES`, `MC_CMD_CDX_BUS_GET_DEVICE_CONFIG`, `MC_CMD_CDX_BUS_DOWN`, `MC_CMD_CDX_BUS_UP`, `MC_CMD_CDX_DEVICE_RESET`, `MC_CMD_CDX_DEVICE_CONTROL_SET`, `MC_CMD_CDX_DEVICE_CONTROL_GET`, `MC_CMD_CDX_DEVICE_WRITE_MSI_MSG`, and extended wrapper `MC_CMD_V2_EXTN`.

## Control Flow
Runtime code in `mcdi.c` uses the header layout to construct MCDI v2 request headers and parse responses. `mcdi_functions.c` uses command IDs, input lengths, output lengths, offsets, and field widths to populate firmware requests and decode returned topology/resource/control data.

## State and Persistence Behavior
No kernel state is allocated. The constants encode a firmware ABI; changes must be synchronized with firmware. Firmware-side state includes bus reset state, device control flags, device resources, MSI message data, and enumeration generation behavior described in comments.

## Dependencies and Integration Points
The macros depend on bitfield helpers from `<linux/cdx/bitfield.h>` through the MCDI wrapper headers. They integrate with RPMsg payloads and the controller firmware running on the RPU/R5.

## Risks
This header is the contract for every firmware operation. Wrong offsets or lengths corrupt requests, reject valid responses, or misconfigure device DMA/MSI. Comments indicate enumeration may return `EAGAIN` when resources change, so callers should be robust to retry needs. Some command comments describe quiescence guarantees for reset/bus-down; controller safety relies on firmware honoring them. The protocol supports 64-bit fields that are only 32-bit aligned, so access helpers must avoid unsafe direct casts.

## Test Signals
Protocol tests should compare structure lengths and offsets against firmware definitions, validate request byte streams for every command, decode sample responses, exercise each `MC_CMD_ERR_*` translation path, and test firmware behavior during bus reset, PL reload, MSI programming, and generation changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/mc_cdx_pcol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdi.c -->
# sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdi.c

## Purpose
This file implements the CDX Management-Controller-to-Driver Interface RPC engine. It serializes firmware commands, builds MCDI v2 request headers, tracks sequence numbers and command lifetimes, processes asynchronous responses, handles timeouts/cancellation, and provides synchronous and asynchronous RPC APIs.

## Important APIs, Types, and Functions
Exported APIs are `cdx_mcdi_init()`, `cdx_mcdi_finish()`, `cdx_mcdi_wait_for_quiescence()`, `cdx_mcdi_process_cmd()`, `cdx_mcdi_rpc()`, and `cdx_mcdi_rpc_async()`. Important internals include `cdx_mcdi_send_request()`, `cdx_mcdi_rpc_sync()`, `cdx_mcdi_cmd_work()`, `cdx_mcdi_complete_cmd()`, `cdx_mcdi_timeout_cmd()`, `cdx_mcdi_mode_fail()`, and `cdx_mcdi_process_cleanup_list()`.

## Control Flow
Initialization allocates `struct cdx_mcdi_iface`, creates an ordered workqueue, initializes locking and wait queues, and starts in event mode with a new epoch. Sync RPC allocates wait/completer data plus a command object, queues the command asynchronously, waits for completion with a command-specific timeout, and cancels on timeout. Command work grabs the iface mutex, assigns a handle, appends to the command list, and either starts immediately or queues behind a held doorbell/sequence. Sending builds an 8-byte v2 extended header, computes checksum into `XFLAGS`, and invokes the transport callback.

Responses enter `cdx_mcdi_process_cmd()`, lookup by response sequence, parse header/data/error, map firmware errors to Linux errno, release doorbell and sequence slots, remove or retry commands, start queued commands, and run completers outside the lock. Timeout moves the interface to fail mode and cancels outstanding commands.

## State and Persistence Behavior
Persistent runtime state includes the ordered workqueue, `iface_lock`, `cmd_list`, wait queue, command sequence ownership array, previous sequence/handle, doorbell owner, mode, outstanding cleanup count, and new-epoch flag. Command and wait data are reference-counted with `kref`. No state survives driver removal; `finish()` waits for cleanup before destroying the workqueue.

## Dependencies and Integration Points
It depends on MCDI protocol constants, CDX bitfield helpers, wait queues, krefs, workqueues, mutexes, and a transport-specific `cdx_mcdi_ops` implementation supplied by `cdx_controller.c` and `cdx_rpmsg.c`.

## Risks
The code assumes at most one active doorbell command while still allowing queued commands and sequence reuse. Timeout is severe: one timed-out command puts the whole iface into fail mode and cancels all outstanding work. `cdx_mcdi_rpc_async_internal()` ignores its `handle` argument and queues work without returning a handle, limiting cancellation by external users. Error handling for `MC_CMD_ERR_QUEUE_FULL` compares `rc` after conversion paths and must preserve raw queue-full semantics. Response buffers passed to completers point into RPMsg callback memory until copied by the sync completer; async completers must not retain them beyond callback semantics. Locking around completion and cleanup reference counts is delicate.

## Test Signals
Unit or integration tests should cover init/finish quiescence, multiple queued commands, sequence wrap, firmware error translation, queue-full retry, timeout fail mode, unexpected response sequence, short response lengths, sync response truncation, async completer exactly-once behavior, and remove while commands are outstanding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdi_functions.c -->
# sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdi_functions.c

## Purpose
This file provides typed CDX firmware operations on top of the generic MCDI RPC engine. It turns controller needs such as enumeration, device configuration, reset, bus control, MSI writes, and device control flags into concrete MCDI commands.

## Important APIs, Types, and Functions
Public helper APIs are `cdx_mcdi_get_num_buses()`, `cdx_mcdi_get_num_devs()`, `cdx_mcdi_get_dev_config()`, `cdx_mcdi_bus_enable()`, `cdx_mcdi_bus_disable()`, `cdx_mcdi_write_msi()`, `cdx_mcdi_reset_device()`, `cdx_mcdi_bus_master_enable()`, and `cdx_mcdi_msi_enable()`. Internal helpers `cdx_mcdi_ctrl_flag_get()` and `cdx_mcdi_ctrl_flag_set()` implement read-modify-write of device control flags.

## Control Flow
Enumeration first calls `MC_CMD_CDX_BUS_ENUM_BUSES`, then per bus `MC_CMD_CDX_BUS_ENUM_DEVICES`, then per device `MC_CMD_CDX_BUS_GET_DEVICE_CONFIG`. Device config decoding copies bus/device IDs, requester IDs, MSI device ID/count, identity fields, revision, class, and up to four non-empty MMIO resources into `struct cdx_dev_params`. Control helpers build small input buffers and call `cdx_mcdi_rpc()`.

## State and Persistence Behavior
The helpers do not keep state. They populate caller-owned `cdx_dev_params` and rely on firmware to persist bus reset state, device reset state, MSI enable state, bus-master state, and MSI message programming.

## Dependencies and Integration Points
It depends on MCDI buffer macros and protocol offsets from `mcdid.h`/`mc_cdx_pcol.h`, the generic `cdx_mcdi_rpc()` API, Linux resource flags, and the private CDX bus add parameter structure. It is used by `cdx_controller.c` controller callbacks.

## Risks
Strict output length checks return `-EIO` on version mismatch; firmware ABI changes will break enumeration until handled. `cdx_mcdi_get_dev_config()` appends resources without checking against `MAX_CDX_DEV_RESOURCES`, relying on exactly four protocol regions matching array capacity. `cdx_mcdi_ctrl_flag_set()` performs read-modify-write without concurrency protection at firmware level, so simultaneous flag updates can race unless firmware serializes per device. Bus/device number validity is delegated to firmware.

## Test Signals
Mock MCDI responses should verify length validation, all MMIO region combinations, class masking to 24 bits, requester/MSI device ID mapping, bus up/down commands, reset command payloads, MSI write payloads, and control flag preservation when toggling bus master or MSI enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdi_functions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdi_functions.h -->
# sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdi_functions.h

## Purpose
This header declares the typed MCDI helper API used by the CDX controller to enumerate and control CDX buses/devices.

## Important APIs, Types, and Functions
It declares bus enumeration (`cdx_mcdi_get_num_buses`, `cdx_mcdi_get_num_devs`), device configuration (`cdx_mcdi_get_dev_config`), bus state (`cdx_mcdi_bus_enable`, `cdx_mcdi_bus_disable`), MSI programming (`cdx_mcdi_write_msi`, `cdx_mcdi_msi_enable`), device reset (`cdx_mcdi_reset_device`), and bus mastering (`cdx_mcdi_bus_master_enable`).

## Control Flow
`cdx_controller.c` calls these functions from its scan path and `dev_configure`/bus callbacks. Each function synchronously issues one or more MCDI RPCs.

## State and Persistence Behavior
No state is defined here. The functions either return counts/status or populate caller-provided `struct cdx_dev_params`.

## Dependencies and Integration Points
The header includes Linux MCDI types, protocol constants, and the private CDX bus header. It is the typed API boundary between controller policy and generic RPC framing.

## Risks
Because helpers are synchronous and may sleep, callers must stay in process context. The API exposes only simple return codes, so richer firmware retry guidance such as `EAGAIN` generation-change handling must be implemented by callers if needed.

## Test Signals
Compile-time checks should ensure declarations match implementations. Controller tests should observe each declared helper being invoked for scan, reset, bus master, MSI enable, and MSI message programming paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdi_functions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdid.h -->
# sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdid.h

## Purpose
This private header defines CDX MCDI helper macros and forward declarations that bridge generic CDX bitfield accessors with the CDX protocol header.

## Important APIs, Types, and Functions
It defines debug warning macros, `MCDI_BUF_LEN`, `cdx_mcdi_if()`, declarations for `cdx_mcdi_rpc_async()` and `cdx_mcdi_wait_for_quiescence()`, and field access helpers `MCDI_BYTE`, `MCDI_WORD`, `MCDI_POPULATE_DWORD_1`, `MCDI_SET_QWORD`, and `MCDI_QWORD`.

## Control Flow
MCDI source files use `cdx_mcdi_if()` to access the active interface if initialized. Request-building code uses the field macros to populate and read protocol buffers without open-coding offsets.

## State and Persistence Behavior
No state is allocated. The inline accessor returns a pointer into `struct cdx_mcdi` state when present.

## Dependencies and Integration Points
It includes mutex, kref, rpmsg headers and `mc_cdx_pcol.h`. It depends on lower-level `MCDI_PTR`, `_MCDI_DWORD`, and CDX dword helpers from public CDX MCDI/bitfield headers.

## Risks
The macros enforce field widths for some accesses with `BUILD_BUG_ON_ZERO`, but they still rely on correct protocol constants. 64-bit access is split into two 32-bit dwords to avoid alignment assumptions; bypassing these macros would be risky. Debug warning macros compile to no-ops without `DEBUG`, so paranoid checks are not production safeguards.

## Test Signals
Build with and without `DEBUG`, compile protocol helper users, and validate qword/word/byte extraction against known little-endian MCDI buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/char/Kconfig

## Purpose
This Kconfig file defines the character-device driver menu and includes several char-related submenus. In this work item, its relevant additions are the SPARC64 ADI driver option and unconditional AGP submenu inclusion through the Makefile.

## Important APIs, Types, and Functions
It declares many config symbols including `TTY_PRINTK`, `PRINTER`, `PPDEV`, `VIRTIO_CONSOLE`, `/dev/mem` and `/dev/port` options, HPET, hardware-specific char drivers, and `ADI`. `ADI` is a tristate "SPARC Privileged ADI driver" depending on `SPARC64` and defaulting to module.

## Control Flow
During configuration, this menu sources TTY, IPMI, hardware random, TPM, s390 char, and xillybus Kconfigs. Selecting symbols controls object inclusion in `drivers/char/Makefile`.

## State and Persistence Behavior
The file only affects `.config`. Runtime state is in the selected drivers. `ADI` selection results in a privileged miscdevice for reading/writing SPARC ADI memory tags.

## Dependencies and Integration Points
It integrates architecture-specific drivers with generic char-device infrastructure. The `ADI` option depends on SPARC64 architecture support functions such as `adi_capable()` and `adi_blksize()`.

## Risks
Many options expose low-level hardware or physical memory interfaces; misconfiguration can expand user-space attack surface. The `ADI` help explicitly targets privileged consumers such as crash tooling, so permissions and architecture availability matter.

## Test Signals
Kconfig coverage should confirm architecture dependencies, module names, and that selected symbols produce expected Makefile objects. For `ADI`, verify it is offered only on SPARC64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/Makefile -->
# sources/distributed-fs/ceph-client/drivers/char/Makefile

## Purpose
This Makefile maps character-device Kconfig symbols to build objects and always descends into the AGP subdirectory.

## Important APIs, Types, and Functions
Key build entries include core `mem.o`, `random.o`, `misc.o`, optional TTY/parallel/HPET/NVRAM/hw_random/TPM/xillybus objects, `obj-y += agp/`, and `obj-$(CONFIG_ADI) += adi.o`.

## Control Flow
Kbuild includes always-on char core objects, then conditionally builds driver objects based on config symbols. The AGP subdirectory is always visited, but its own Makefile gates actual AGP objects.

## State and Persistence Behavior
No runtime state. It controls object inclusion in the kernel or modules.

## Dependencies and Integration Points
It connects `drivers/char/Kconfig` symbols to source files and subdirectories such as `agp/`, `hw_random/`, `tpm/`, and `xillybus/`.

## Risks
Because `agp/` is always descended into, AGP Makefile gating must remain correct. Symbol/object drift causes missing drivers or unexpected build attempts on unsupported architectures.

## Test Signals
Build matrix with common char options as built-in/module/off, especially `CONFIG_ADI=m/y` and `CONFIG_AGP` disabled/enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/adi.c -->
# sources/distributed-fs/ceph-client/drivers/char/adi.c

## Purpose
This file implements a privileged SPARC64 miscdevice exposing ADI/MCD memory version tags to user space. It is intended for crash dump and diagnostic tools that need to read or restore Application Data Integrity metadata.

## Important APIs, Types, and Functions
Core helpers are `read_mcd_tag()` and `set_mcd_tag()`, which use SPARC `ldxa`/`stxa` with `ASI_MCD_REAL` and exception-table fixups. File operations are `adi_read()`, `adi_write()`, and `adi_llseek()`, registered through `adi_miscdev`.

## Control Flow
Module init checks `adi_capable()` and registers a dynamic-minor miscdevice named after `KBUILD_MODNAME`. Reads allocate a temporary buffer up to one page, convert file offset units into real addresses by multiplying by `adi_blksize()`, read one tag per ADI block, batch-copy to user space, and advance `f_pos` by tags read. Writes copy user tag bytes in page-sized batches, set one tag per ADI block, advance the offset, and execute a final sync memory barrier.

## State and Persistence Behavior
The driver stores no per-open state. The persistent effect is modification of hardware-maintained ADI version tags for physical memory. File position is interpreted in tag units rather than bytes of physical memory. Failed reads/writes stop at the first hardware fault.

## Dependencies and Integration Points
It depends on SPARC64 ADI architecture helpers, ASI access, exception tables, miscdevice infrastructure, and user-copy helpers. Consumers are privileged user-space tools.

## Risks
This is a powerful low-level interface: writes can alter memory protection tags and affect corruption detection. `adi_read()` advances `*offp` by bytes/tags read, while address calculation multiplies by `adi_blksize()`, so API users must understand the unit. Partial progress before a fault is not returned if the code jumps to error, which may obscure how much work completed. The device relies on external permissions for privilege enforcement after registration.

## Test Signals
On ADI-capable SPARC64, verify miscdevice creation, reads/writes over valid and invalid physical ranges, offset seeking, zero-length write rejection, fault fixup returning `-EFAULT`, final memory barrier behavior, and access permissions for non-privileged users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/adi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/char/agp/Kconfig

## Purpose
This Kconfig file defines AGPGART support and chipset-specific AGP bridge drivers.

## Important APIs, Types, and Functions
The main symbol is `AGP`, a tristate `/dev/agpgart` option depending on PCI and one of Alpha, PA-RISC, PowerPC, or x86. Chipset symbols include `AGP_ALI`, `AGP_ATI`, `AGP_AMD`, `AGP_AMD64`, `AGP_INTEL`, `AGP_NVIDIA`, `AGP_SIS`, `AGP_SWORKS`, `AGP_VIA`, `AGP_PARISC`, `AGP_ALPHA_CORE`, `AGP_UNINORTH`, and `AGP_EFFICEON`. `INTEL_GTT` is an internal tristate selected by Intel AGP support.

## Control Flow
Selecting `AGP` enables the generic backend. Selecting chipset options causes matching PCI/platform bridge drivers to build and register with the generic AGP backend.

## State and Persistence Behavior
Configuration state controls whether `/dev/agpgart`, generic AGP memory management, and chipset-specific GART setup are built.

## Dependencies and Integration Points
The options reflect architecture and chipset restrictions: many legacy chipsets are x86_32-only, AMD64 uses AMD northbridge support, Alpha and PA-RISC use architecture-specific backends, and Intel selects `INTEL_GTT`.

## Risks
AGP is legacy but low-level: enabling unsupported chipset drivers can affect aperture setup and DMA mappings. `AGP_AMD64` supports a try-unsupported path at runtime, but Kconfig cannot validate actual bridge/NB compatibility.

## Test Signals
Kconfig build matrix across supported architectures, ensuring only valid chipset options appear and module names match Makefile outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/char/agp/Makefile

## Purpose
This Makefile builds the generic AGPGART backend and chipset-specific AGP bridge modules.

## Important APIs, Types, and Functions
`agpgart-y` combines `backend.o`, `generic.o`, and `isoch.o`. Other `obj-$(CONFIG_*)` lines map chipset config symbols to modules such as `ali-agp.o`, `ati-agp.o`, `amd-k7-agp.o`, `amd64-agp.o`, `alpha-agp.o`, and `efficeon-agp.o`.

## Control Flow
When `CONFIG_AGP` is enabled, the generic `agpgart` object is built. Chipset options compile their corresponding PCI/architecture bridge drivers.

## State and Persistence Behavior
No runtime state. It defines which AGP object code enters the kernel/module build.

## Dependencies and Integration Points
The Makefile aligns with AGP Kconfig symbols and driver filenames. Chipset drivers depend on backend symbols exported by `backend.o` and generic helpers from `generic.o`.

## Risks
The generic backend must be available before chipset modules can resolve symbols. Any Kconfig/Makefile mismatch leaves selected drivers unbuilt or built without dependencies.

## Test Signals
Build each listed AGP chipset option as module and built-in, confirming `agpgart` and chipset modules link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/agp.h -->
# sources/distributed-fs/ceph-client/drivers/char/agp/agp.h

## Purpose
This private AGPGART header defines the backend's internal bridge structures, driver callback table, aperture-size descriptors, register constants, helper prototypes, and shared globals used by generic and chipset-specific AGP drivers.

## Important APIs, Types, and Functions
Important types are `enum aper_size_type`, `struct gatt_mask`, aperture-size structs, `struct agp_bridge_driver`, `struct agp_bridge_data`, and `struct agp_device_ids`. The driver callback table covers size fetch, configure/cleanup, AGP enable, TLB flush, memory masking, cache flush, GATT creation/free, insertion/removal, type allocation, page allocation/destruction, and memory type conversion.

Exports/prototypes include bridge lifecycle (`agp_alloc_bridge`, `agp_add_bridge`, `agp_remove_bridge`, `agp_put_bridge`), generic memory/GATT operations, AGP enable helpers, version/mode helpers, cache flush, user memory allocation helpers, AGP3 helpers, and globals `agp_bridge`, `agp_off`, and `agp_try_unsupported_boot`.

## Control Flow
Chipset drivers allocate and fill `struct agp_bridge_data` with a `struct agp_bridge_driver`; backend initialization calls the callback table in a generic sequence. Generic ioctl/memory code uses the same callbacks for per-chipset operations.

## State and Persistence Behavior
The header describes persistent bridge state: current/previous aperture size, PCI device, GATT pointers and bus addresses, scratch page, mode, key list, memory counters, capability offsets, mapped memory list/lock, and chipset private data.

## Dependencies and Integration Points
It depends on architecture AGP cache helpers and Linux PCI/AGP public headers. It is the central integration point between `backend.c`, generic AGP code, and all chipset drivers.

## Risks
The shared global `agp_bridge` is a legacy singleton shortcut even though a list of bridges exists; drivers using it can misbehave with multiple bridges. Callback contracts are implicit and easy to violate, especially scratch-page masking, GATT address ownership, cache flushing, and aperture-size pointer types. Register constants must match AGP specs/chipsets.

## Test Signals
Compile all chipset drivers, verify callback tables populate required methods, and run AGP memory allocation/bind/unbind tests on each bridge class with debug options to catch type/size mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/agp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/ali-agp.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/ali-agp.c

## Purpose
This file implements AGPGART chipset support for ALi host bridges, including special cache-flush behavior for the M1541 chipset.

## Important APIs, Types, and Functions
Important functions include `ali_fetch_size()`, `ali_configure()`, `ali_cleanup()`, `ali_tlbflush()`, `m1541_cache_flush()`, `m1541_alloc_page()`, `ali_destroy_page()`, `m1541_destroy_page()`, `agp_ali_probe()`, and `agp_ali_remove()`. Bridge callback tables are `ali_generic_bridge` and `ali_m1541_bridge`.

## Control Flow
The PCI driver matches ALi host bridges. Probe verifies an AGP capability, matches known ALi device IDs, allocates an AGP bridge, chooses M1541-specific or generic callbacks, reads the AGP status mode, stores bridge data on the PCI device, and calls `agp_add_bridge()`. Configuration writes aperture size/GATT base into `ALI_ATTBASE`, sets TLB control, derives aperture bus address from BAR0, and enables the TLB.

## State and Persistence Behavior
The driver programs ALi PCI config registers for aperture size, GATT base, tag/TLB control, and optional cache flush address. It restores previous aperture size on cleanup. Persistent bridge state is stored in generic `agp_bridge_data`.

## Dependencies and Integration Points
It depends on PCI, AGP backend/generic helpers, ALi PCI IDs, and architecture page/cache helpers. User-facing AGP memory operations flow through generic AGP code into this callback table.

## Risks
The ALi path relies on global `agp_bridge`. The M1541 cache flush sequence writes one flush per GATT page and page allocation/destruction flushes physical addresses; incorrect cache handling can produce stale GART entries. Hidden M1621 ID decoding mutates the displayed chipset name. Cleanup uses previous size but does not fully undo every register bit changed by configure.

## Test Signals
Probe/remove on supported ALi chipsets, validate aperture size detection, GATT base programming, TLB flush on insert/remove, M1541 cache flush behavior, and errata-sensitive graphics cards such as Matrox G200 running in safe modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/ali-agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/alpha-agp.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/alpha-agp.c

## Purpose
This file provides AGP backend support for Alpha platforms whose AGP/GART behavior is supplied by architecture machine-vector operations rather than a normal PCI chipset driver.

## Important APIs, Types, and Functions
Core functions are `alpha_core_agp_setup()`, `alpha_core_agp_vm_fault()`, `alpha_core_agp_fetch_size()`, `alpha_core_agp_configure()`, `alpha_core_agp_cleanup()`, `alpha_core_agp_tlbflush()`, `alpha_core_agp_enable()`, `alpha_core_agp_insert_memory()`, and `alpha_core_agp_remove_memory()`. The bridge driver is `alpha_core_agp_driver`, and VM ops are `alpha_core_agp_vm_ops`.

## Control Flow
Module init checks `agp_off`, obtains `alpha_mv.agp_info()`, runs architecture setup, fills a fixed aperture descriptor, allocates a fake `pci_dev`, allocates an AGP bridge, attaches Alpha-specific ops and VM fault handler, then registers the bridge. Memory insertion/removal delegates to `agp->ops->bind()`/`unbind()` and flushes the Alpha PCI TBI.

## State and Persistence Behavior
State lives in architecture-provided `alpha_agp_info`, a fake PCI device, `alpha_bridge`, and generic bridge fields. VM faults translate aperture bus addresses through `agp->ops->translate()` and pin the backing page.

## Dependencies and Integration Points
It depends on Alpha machine vectors, `alpha_agp_info`, PCI hose data, generic AGP backend, and architecture TLB invalidation via `alpha_mv.mv_pci_tbi()`.

## Risks
The fake PCI device must be sufficient for generic AGP users. VM fault translation returns SIGBUS on missing mappings; wrong architecture translate behavior can expose incorrect physical pages. Cleanup assumes `alpha_bridge` was initialized. The bridge is fixed-size and `cant_use_aperture` is set, reflecting architecture constraints that generic users must respect.

## Test Signals
Boot Alpha systems with AGP machine-vector support, verify bridge registration, AGP enable programming, aperture mmap faults translating to correct pages, bind/unbind operations, TBI flushes, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/alpha-agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/amd-k7-agp.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/amd-k7-agp.c

## Purpose
This file implements AGPGART support for AMD K7-era Irongate/761/760MP host bridges using a two-level GATT and MMIO control registers.

## Important APIs, Types, and Functions
Important internals include `struct amd_page_map`, `amd_create_page_map()`, `amd_create_gatt_pages()`, `amd_create_gatt_table()`, `amd_irongate_fetch_size()`, `amd_irongate_configure()`, `amd_irongate_cleanup()`, `amd_irongate_tlbflush()`, `amd_insert_memory()`, and `amd_remove_memory()`. PCI lifecycle functions are `agp_amdk7_probe()`, `agp_amdk7_remove()`, and resume `agp_amdk7_resume()`.

## Control Flow
Probe matches AMD host-bridge IDs, verifies AGP capability, allocates a bridge, attaches `amd_irongate_driver`, applies known errata flags for AMD 751/761 revisions and NVIDIA graphics combinations, reads AGP mode, stores PCI driver data, and registers with the backend. GATT creation allocates an uncached page directory and per-4MB GATT pages, fills them with scratch-page mappings, and points directory entries at GATT pages. Configure ioremaps MMIO, writes GATT base, sync/indexing registers, enables GART translation, programs aperture size, and flushes TLB.

## State and Persistence Behavior
Driver state includes `amd_irongate_private.registers`, `gatt_pages`, and `num_tables`, plus generic bridge state. It changes page cacheability with `set_memory_uc()`/`set_memory_wb()`, writes MMIO GART registers, and restores aperture size/disables GART on cleanup.

## Dependencies and Integration Points
It depends on PCI host bridge IDs, generic AGP backend helpers, x86 memory attribute helpers, MMIO mapping, and AGP mode errata flags consumed by generic enable logic.

## Risks
Two-level GATT indexing macros depend on aperture bus address consistency. Page-table pages are made uncached and must be restored on free. Error unwind in GATT page allocation must free partially allocated tables. Probe errata uses global `agp_bridge` soon after bridge allocation, relying on singleton behavior. Resume only reruns configure and assumes GATT structures remain intact.

## Test Signals
Test supported AMD 751/761/760MP hardware, aperture size fetch, GATT allocation/free under memory pressure, bind/unbind occupancy checks, TLB flushes, errata mode limiting, suspend/resume, and module unload after AGP memory use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/amd-k7-agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/amd64-agp.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/amd64-agp.c

## Purpose
This file implements AGPGART support for AMD Opteron/Athlon64 on-CPU GARTs and external AGP bridges such as AMD 8151, VIA, SiS, ULi, and NVIDIA nForce3.

## Important APIs, Types, and Functions
Key functions are `amd64_insert_memory()`, `amd64_fetch_size()`, `amd64_configure()`, `amd_8151_configure()`, `amd64_cleanup()`, `agp_aperture_valid()`, `fix_northbridge()`, `cache_nbs()`, `amd8151_init()`, `uli_agp_init()`, `nforce3_agp_init()`, `agp_amd64_probe()`, `agp_amd64_remove()`, `agp_amd64_resume()`, and non-static `agp_amd64_init()`. The bridge driver is `amd_8151_driver`.

## Control Flow
Probe enforces one bridge, verifies AGP capability, allocates a bridge, applies AMD 8151 revision quirks, reads mode, validates/fixes each AMD northbridge aperture, optionally shadows aperture settings into NVIDIA or ULi bridge registers, then registers the bridge. Configuration writes the generic GATT table address into every AMD northbridge GART and flushes all GARTs. Memory insertion validates type/range/empty PTEs, flushes CPU caches once, converts physical pages into AMD GART PTE format, writes entries, and flushes GARTs.

If no supported bridge matches and `agp_try_unsupported` or boot `agp=try_unsupported` is allowed, init dynamically adds IDs for any AGP-capable PCI device on systems with AMD64 northbridges.

## State and Persistence Behavior
State includes a requested aperture memory resource, `agp_bridges_found`, generic GATT table state, and AMD northbridge GART registers. Cleanup disables GART translation on all northbridges and releases aperture resources during module exit/remove.

## Dependencies and Integration Points
It depends on x86 AMD northbridge helpers, e820/aperture validation, generic AGP backend, AMD GART/IOMMU helpers, PCI dynamic IDs, and chipset-specific shadow registers for ULi/nForce3.

## Risks
Aperture validation is critical because a bad aperture can conflict with PCI mappings or exceed 32-bit bridge limits. Multiprocessor systems must program all northbridges coherently. `agp_amd64_remove()` releases a region using `virt_to_phys(gatt_table_real)` and aperture size, while `agp_aperture_valid()` requested `aper`; resource accounting needs scrutiny. Unsupported dynamic IDs can bind to bridges with untested quirks. Built-in interaction with `gart_iommu_aperture` changes init/exit behavior.

## Test Signals
Test AMD64 systems with AMD 8151, VIA, ULi, nForce3, and unsupported-bridge paths; validate aperture conflict detection, all-node GART programming, memory bind/unbind, suspend/resume reconfiguration, dynamic-ID fallback, and coexistence with GART IOMMU aperture setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/amd64-agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/ati-agp.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/ati-agp.c

## Purpose
This file implements AGPGART support for ATI Radeon IGP host bridges using a two-level GATT and ATI GART MMIO registers.

## Important APIs, Types, and Functions
Key functions include `ati_create_page_map()`, `ati_free_page_map()`, `ati_create_gatt_pages()`, `is_r200()`, `ati_fetch_size()`, `ati_tlbflush()`, `ati_cleanup()`, `ati_configure()`, `ati_insert_memory()`, `ati_remove_memory()`, `ati_create_gatt_table()`, `ati_free_gatt_table()`, `agp_ati_probe()`, and `agp_ati_remove()`. The bridge callback table is `ati_generic_bridge`.

## Control Flow
Probe matches ATI host bridges, verifies AGP capability, checks the device against a supported chipset table, allocates a bridge, attaches ATI callbacks, reads mode, and calls `agp_add_bridge()`. GATT creation allocates an uncached AGP-mapped page directory and second-level pages, programs aperture size in RS100 or RS300 registers, records the aperture bus address, fills directory entries, and initializes PTEs to the scratch page. Configure ioremaps GART MMIO, sets AGP mode, enables the GART feature, sets a PCI command/status-related bit, and writes the GATT base.

## State and Persistence Behavior
State is held in `ati_generic_private.registers`, second-level `gatt_pages`, and generic bridge fields. Page-table pages are mapped into AGP-visible memory and changed to uncached, then restored on free. Cleanup restores the previous aperture size and unmaps MMIO.

## Dependencies and Integration Points
It depends on PCI, generic AGP backend, architecture AGP page mapping helpers `map_page_into_agp()`/`unmap_page_from_agp()`, x86 memory attribute helpers, and ATI PCI IDs.

## Risks
Correctly distinguishing RS100/RS200-style registers from RS300-style registers is essential. GATT page allocation has multi-level cleanup requirements. Insert/remove only support mask type 0 and must catch occupied entries before writes. The code does not explicitly bounds-check removal range against aperture size, relying on callers. Cacheability and AGP page mapping mistakes can produce stale or inaccessible GATT entries.

## Test Signals
Test supported ATI IGP variants, aperture size read/write, GATT allocation failure unwind, insert/remove occupancy checks, TLB flush register writes, resume reconfiguration, and module unload after active AGP mappings are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/ati-agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/backend.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/backend.c

## Purpose
This file implements AGPGART backend bridge registration and initialization. It manages bridge lifetime, backend acquisition/release, global bridge lists, boot options, scratch pages, GATT setup, key-list allocation, and generic cleanup.

## Important APIs, Types, and Functions
Exported APIs are `agp_backend_acquire()`, `agp_backend_release()`, `agp_alloc_bridge()`, `agp_put_bridge()`, `agp_add_bridge()`, and `agp_remove_bridge()`. Important internals are `agp_find_max()`, `agp_backend_initialize()`, and `agp_backend_cleanup()`. Globals include `agp_find_bridge`, `agp_bridge`, `agp_bridges`, `agp_off`, and `agp_try_unsupported_boot`.

## Control Flow
Chipset drivers allocate and fill a bridge, then call `agp_add_bridge()`. The backend rejects registration if `agp_off` is set or no PCI device exists, pins the chipset module, initializes the bridge by allocating scratch page, fetching aperture size, creating GATT table, allocating key list, running chipset `configure()`, and initializing mapped-memory tracking. On success it logs the first aperture and adds the bridge to `agp_bridges`. Removal cleans chipset state, frees GATT/key/scratch resources, removes the list entry, and drops the module reference.

## State and Persistence Behavior
The backend persists global bridge pointers/lists, per-bridge memory accounting, scratch page DMA/masked address, key list, current/previous aperture state, and mapped memory list. Boot parameter `agp=off` disables registration; `agp=try_unsupported` sets a global flag used by drivers such as AMD64.

## Dependencies and Integration Points
It depends on PCI, miscdevice AGP interfaces, generic AGP memory helpers, vmalloc, module references, and chipset callback tables from `agp.h`. User-space `/dev/agpgart` paths acquire/release bridges through this backend.

## Risks
Initialization error unwinding must destroy scratch page in both unmap and free phases and free partial GATT/key allocations. `agp_put_bridge()` sets global `agp_bridge` to NULL only when the list is empty, so singleton assumptions remain fragile. `agp_backend_acquire()` uses an atomic in-use flag but no compare-and-swap, so concurrent acquire attempts can race. The key list allocation comment notes vmalloc memory is not guaranteed contiguous, though it is used as a key bitmap/list.

## Test Signals
Test chipset registration failure at each initialization stage, multiple bridge registration/removal, backend acquire/release concurrency, boot `agp=off`, boot `agp=try_unsupported`, scratch-page allocation cleanup, and no leaks after module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/backend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/efficeon-agp.c -->
# sources/distributed-fs/ceph-client/drivers/char/agp/efficeon-agp.c

## Purpose
This file implements AGPGART support for Transmeta Efficeon TM8000 integrated northbridges. It uses Intel-like AGP control registers plus an Efficeon-specific two-level GATT programmed through the `EFFICEON_ATTPAGE` register.

## Important APIs, Types, and Functions
Key functions are `efficeon_fetch_size()`, `efficeon_configure()`, `efficeon_cleanup()`, `efficeon_tlbflush()`, `efficeon_create_gatt_table()`, `efficeon_free_gatt_table()`, `efficeon_insert_memory()`, `efficeon_remove_memory()`, `agp_efficeon_probe()`, `agp_efficeon_remove()`, and `agp_efficeon_resume()`. The bridge callbacks are collected in `efficeon_driver`; L1 page pointers live in `efficeon_private.l1_table`.

## Control Flow
Probe matches Transmeta host bridges, verifies AGP capability and exact Efficeon device ID, allocates a bridge, enables the PCI device, assigns BAR0 if BIOS left it unset, reads AGP status, and registers the bridge. GATT creation allocates zeroed second-level pages for the aperture size, flushes them with `clflush`, records them in a 64-entry L1 array, and writes physical page address plus PAT/present/index bits to `EFFICEON_ATTPAGE`. Insert/remove writes PTEs directly into the second-level pages, flushes modified cache lines, and toggles AGP TLB control.

## State and Persistence Behavior
Runtime state is the L1 table of allocated pages, generic bridge data, and Efficeon/Intel-compatible PCI config registers. Cleanup clears L1 hardware entries, frees pages, disables NBXCFG aperture bits, and restores previous aperture size.

## Dependencies and Integration Points
It depends on PCI, generic AGP backend, Intel AGP register definitions from `intel-agp.h`, x86 `cpuid_ebx()` and `clflush`, and Transmeta PCI IDs.

## Risks
The driver assumes a valid CLFLUSH line size from CPUID; a zero or unexpected value would break flush loops. Insert skips missing L1 pages rather than failing, which could hide inconsistent GATT setup. The comments note module unload/S3 concerns. BIOS resource repair through `pci_assign_resource()` is necessary to avoid crashes but can fail. Static `agp_initialised` prevents duplicate registration but is not synchronized.

## Test Signals
Test Efficeon hardware probe with and without BIOS BAR assignment, aperture sizes 32-256 MB, GATT allocation/free, bind/unbind with cache-line flush validation, suspend/resume reconfiguration, and repeated module load/unload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/agp/efficeon-agp.c -->
