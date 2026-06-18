# Research: subset-b-005518

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/image/mdc800.c -->
# sources/distributed-fs/ceph-client/drivers/usb/image/mdc800.c

## Purpose
`mdc800.c` is a legacy USB driver for the Mustek MDC800 digital camera. It exposes a character device through `usb_register_dev()` with minor base 32 and implements the camera's private 8-byte command protocol over one interrupt-in endpoint, one bulk-out command endpoint, and one bulk-in download endpoint. The driver explicitly supports only one camera instance through the global `static struct mdc800_data *mdc800`.

## Important APIs, Types, And Functions
The central state is `struct mdc800_data`, which stores the `usb_device`, endpoint addresses, three URBs, wait queues, camera protocol state, command/input buffers, output/download buffers, cached image length, open flag, and a coarse `io_lock` mutex. The `mdc800_state` enum models `NOT_CONNECTED`, `READY`, `WORKING`, and `DOWNLOAD`.

USB integration is handled by `mdc800_usb_driver`, `mdc800_usb_probe()`, and `mdc800_usb_disconnect()`. File operations are `mdc800_device_open()`, `mdc800_device_release()`, `mdc800_device_read()`, and `mdc800_device_write()`. Protocol helpers include `mdc800_isBusy()`, `mdc800_isReady()`, `mdc800_usb_waitForIRQ()`, and `mdc800_getAnswerSize()`. URB callbacks are `mdc800_usb_irq()`, `mdc800_usb_write_notify()`, and `mdc800_usb_download_notify()`.

## Control Flow
Module init allocates the singleton object, three transfer buffers, three URBs, initializes wait queues and mutex state, then registers the USB driver. Probe validates that the camera has exactly one configuration, vendor-specific interface class, four endpoints matching hard-coded descriptors, registers the character device, fills the interrupt/write/download URBs, sets `state = READY`, and stores interface data.

Open refuses disconnected or already-open devices, resets command/output/download caches, submits the interrupt URB, and marks the device open. Writes accumulate bytes until an 8-byte command is complete. A full command first waits for ready status through interrupt traffic, submits the command on bulk-out, waits for write completion, then either enters `DOWNLOAD` for image/thumbnail commands or waits for an interrupt response for small command answers. Reads drain `out[]`; in `DOWNLOAD` state, empty output triggers another 64-byte bulk-in URB until `download_left` reaches zero. Release and disconnect kill all URBs, with disconnect first marking `NOT_CONNECTED`.

## State And Persistence
All state is volatile kernel memory plus hardware/USB state. `pic_len` caches the image size returned by command `0x07` and is consumed by image download commands `0x05` and `0x3e`. `out[]`, `out_ptr`, and `out_count` stage read data for userspace. `camera_busy`, `camera_request_ready`, `irq_woken`, `written`, and `downloaded` synchronize URB callbacks with sleeping file operations. No data persists beyond module lifetime or device unplug.

## Dependencies And Integration Points
The file depends on Linux USB core URBs, `usb_class_driver`, character-device file operations, wait queues, user-copy helpers, signals, mutexes, and module init/exit. Userspace must understand the camera protocol and drive `/dev/mdc800*` or the historical `/dev/mustek` node. The code assumes tree-local allocation helpers such as `kzalloc_obj()`.

## Risks
The singleton global blocks multiple cameras and makes state sharing simple but fragile. `mdc800_usb_waitForIRQ()` sleeps while callers hold `io_lock`, so callbacks must not need that mutex. Several paths return `len-left`, which can be zero after failed download URB submission or status errors, potentially hiding errors as EOF-like behavior. Interrupt URB resubmission is not visible in `mdc800_usb_irq()`, so behavior depends on USB interrupt polling semantics around the submitted URB. Protocol constants are hard-coded and old hardware-specific. Disconnect races are mitigated by `io_lock` and `usb_kill_urb()`, but callback-visible fields remain globally shared.

## Test Signals
Useful tests include probe rejection for wrong endpoint layouts, single-open enforcement, unplug during open/read/write/download waits, command sequences for no-answer, 8-byte answer, thumbnail, and full image download, signal interruption during blocking reads/writes, and fault injection for `usb_submit_urb()` and allocation failures. Runtime signals include timeout logs from `mdc800_usb_waitForIRQ()`, command/download URB status logs, and correct transition back to `READY` after downloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/image/mdc800.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/image/microtek.c -->
# sources/distributed-fs/ceph-client/drivers/usb/image/microtek.c

## Purpose
`microtek.c` implements a USB-to-SCSI bridge for Microtek Scanmaker X6 USB scanners and related devices. It registers both as a USB interface driver and as a SCSI host adapter, translating SCSI commands from the scanner stack into a private USB protocol with command, data, and one-byte status phases.

## Important APIs, Types, And Functions
The driver uses `struct mts_desc` and `struct mts_transfer_context` from `microtek.h`. `mts_usb_driver` binds supported USB IDs, while `mts_scsi_host_template` exposes one emulated SCSI host with `queuecommand`, abort, reset, `sdev_init`, `can_queue = 1`, `SG_ALL`, and 511-byte DMA alignment.

Core functions are `mts_usb_probe()`, `mts_usb_disconnect()`, `mts_scsi_queuecommand_lck()`, `mts_build_transfer_context()`, `mts_command_done()`, `mts_data_done()`, `mts_get_status()`, `mts_transfer_done()`, `mts_do_sg()`, `mts_scsi_abort()`, and `mts_scsi_host_reset()`. The command direction table `mts_direction[]` and special `mts_read_image_sig[]` select response versus image endpoints.

## Control Flow
Probe verifies exactly three endpoints, finds one bulk-out and two bulk-in endpoints, allocates the descriptor, URB, and status byte, then allocates/adds a SCSI host and scans it. SCSI queueing rejects nonzero channel/id/lun as `DID_BAD_TARGET`; otherwise it submits the raw SCSI CDB to the command endpoint. The command completion callback handles command URB errors, then either reads request-sense data into `sense_buffer`, transfers SCSI data through the selected pipe, or reads status directly. Data completion updates residuals and host status, then requests the final one-byte SCSI status. Final completion merges scanner status into `srb->result` and calls `scsi_done()`.

## State And Persistence
State is per USB interface in `struct mts_desc`: endpoint numbers, one shared URB, SCSI host pointer, status byte storage, and current transfer context. There is no durable state. Only one command can be active because the host template sets `can_queue = 1` and the descriptor owns a single URB/context pair. Scatter/gather progress is stored in `context.curr_sg`.

## Dependencies And Integration Points
The driver integrates with USB core, SCSI midlayer, SCSI error handling, and scatterlist helpers. It reuses usb-storage style direction inference instead of trusting `sc_data_direction`. User-visible scanner access is through the SCSI scanner path, not a custom char device. USB IDs cover Microtek and related vendor/product pairs.

## Risks
Endpoint role assignment assumes the first discovered bulk-in endpoint is response and the second is image data; unusual descriptor ordering can be warned about but still used incorrectly. `mts_do_sg()` advances to `sg_next()` before checking whether the current segment was the last, so scatter/gather edge cases depend on the callback choice made during submission. Short transfers set residuals but still proceed to status. Abort kills the single URB and returns `FAILED`, leaving recovery to the SCSI layer. The protocol was reverse-engineered and comments mark big-endian and multi-scanner behavior as historically untested.

## Test Signals
Exercise SCSI INQUIRY/REQUEST_SENSE, image READ commands that must use `ep_image`, normal response reads via `ep_response`, write-like commands via `ep_out`, scatter/gather requests with multiple segments, nonzero LUN/ID/channel rejection, USB reset through SCSI host reset, disconnect during active command, and URB status paths for abort and hard errors. Scanner-specific tests should validate final status-byte propagation into `srb->result`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/image/microtek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/image/microtek.h -->
# sources/distributed-fs/ceph-client/drivers/usb/image/microtek.h

## Purpose
`microtek.h` defines the private state structures and endpoint constants shared by the Microtek USB scanner driver. It is intentionally small and exists to separate the SCSI transfer context and USB descriptor state from the implementation file.

## Important APIs, Types, And Functions
`typedef void (*mts_scsi_cmnd_callback)(struct scsi_cmnd *)` records the SCSI completion callback type. `struct mts_transfer_context` tracks the active SCSI command, final callback, data pointer and length, selected USB pipe, current scatterlist element, returned SCSI status byte, and owning `mts_desc`. `struct mts_desc` stores endpoint numbers, `usb_device`, `usb_interface`, `Scsi_Host`, one active URB, and embedded transfer context.

Constants define expected endpoint numbers: `MTS_EP_OUT` 1, `MTS_EP_RESPONSE` 2, `MTS_EP_IMAGE` 3, and `MTS_EP_TOTAL` 3. `MTS_SCSI_ERR_MASK` preserves upper SCSI result bits while replacing status bits.

## Control Flow
The header has no executable control flow. Its structures are filled in `mts_usb_probe()`, updated by `mts_build_transfer_context()`, and consumed by URB completion callbacks. The endpoint constants are used as warnings/sanity checks after endpoint discovery.

## State And Persistence
State described here lives for the lifetime of a bound USB interface and is freed on disconnect. The embedded transfer context is mutable per command and relies on the host template limiting queue depth to one.

## Dependencies And Integration Points
The types assume Linux USB, SCSI command, SCSI host, URB, scatterlist, and integer types are already included by `microtek.c`. The header is private to this driver and is not a general subsystem API.

## Risks
The header documents a single-URB, single-context architecture. Raising queue depth or adding parallel transfers would require redesigning `struct mts_transfer_context`, status storage, and URB ownership. The `next`/`prev` fields in `struct mts_desc` are unused by the current implementation and could mislead future maintainers into assuming a descriptor list exists.

## Test Signals
Build coverage should catch structure/API drift against SCSI and USB core types. Runtime tests are indirect through `microtek.c`: endpoint discovery, SCSI command completion, scatter/gather, and disconnect cleanup validate that the state layout remains coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/image/microtek.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/isp1760/Kconfig

## Purpose
This Kconfig file exposes build-time configuration for the NXP ISP1760/1761/1763 USB controller driver. It defines the top-level `USB_ISP1760` option plus internal host and gadget role symbols used by the Makefile and C stubs.

## Important APIs, Types, And Functions
`USB_ISP1760` is a tristate depending on `USB || USB_GADGET` and selects `REGMAP_MMIO`. Internal bools `USB_ISP1760_HCD` and `USB_ISP1761_UDC` gate compilation of `isp1760-hcd.o` and `isp1760-udc.o`. The mode choice offers host-only, gadget-only, and dual-role configurations with dependency expressions that keep module/built-in relationships compatible with USB core and gadget core.

## Control Flow
Kconfig evaluation selects a default mode based on whether `USB` and/or `USB_GADGET` are enabled. Host-only selects the HCD symbol, gadget-only selects the UDC symbol, and dual-role selects both. The C code then uses `IS_ENABLED(CONFIG_USB_ISP1760_HCD)` and `IS_ENABLED(CONFIG_USB_ISP1761_UDC)` to decide runtime registration.

## State And Persistence
There is no runtime state. The selected symbols persist in the kernel configuration and determine which objects and inline stubs are built.

## Dependencies And Integration Points
The file integrates with the USB host stack, USB gadget stack, regmap MMIO, and the local Makefile. Help text documents lack of isochronous and OTG support, which matches limitations in the HCD and core code.

## Risks
The dependency expressions must keep role objects linkable in built-in and module combinations. The prompt mentions ISP1760 in gadget mode even though the implementation is primarily ISP1761/ISP1763-capable for UDC; changing role support should keep help text and C `udc_enabled` logic aligned.

## Test Signals
Build matrix coverage is the main signal: host-only, gadget-only, dual-role, module, built-in, `USB=n USB_GADGET=y`, `USB=y USB_GADGET=n`, and compile-test style configurations should all link with the expected stubs or objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/isp1760/Makefile

## Purpose
The Makefile builds the ISP1760 composite module/object. It always includes common core and bus glue and conditionally adds host-controller and gadget-controller implementations.

## Important APIs, Types, And Functions
`isp1760-y` includes `isp1760-core.o` and `isp1760-if.o`. `isp1760-$(CONFIG_USB_ISP1760_HCD)` appends `isp1760-hcd.o`; `isp1760-$(CONFIG_USB_ISP1761_UDC)` appends `isp1760-udc.o`. `obj-$(CONFIG_USB_ISP1760) += isp1760.o` exposes the final object to kbuild.

## Control Flow
kbuild expands the role-dependent object list from Kconfig selections. The final linked object contains only the selected role implementation(s), with headers providing no-op inline stubs for disabled roles.

## State And Persistence
There is no runtime state. Build output composition persists only as generated kernel objects/modules.

## Dependencies And Integration Points
This file is coupled to `Kconfig` symbols and to the C headers' conditional declarations. It must remain synchronized with any new source files or role symbols added under this directory.

## Risks
Incorrect object gating can cause unresolved symbols or silently omit a role selected by configuration. Because `isp1760-core.o` calls HCD/UDC registration functions, the disabled-role inline stubs in headers are required for configurations where an object is not linked.

## Test Signals
Build tests for all three role selections should confirm the final object list and successful linking. `make M=drivers/usb/isp1760` or equivalent subtree builds are sufficient for this file's direct behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-core.c

## Purpose
`isp1760-core.c` is the common device layer for NXP ISP1760/1761/1763 controllers. It maps MMIO, creates regmaps and regmap fields for host and device register layouts, performs chip reset and board-mode setup, selects memory layout, and registers the HCD and/or UDC role.

## Important APIs, Types, And Functions
Public functions are `isp1760_register()`, `isp1760_unregister()`, and `isp1760_set_pullup()`. Internal setup is in `isp1760_init_core()`. The file defines memory layouts for ISP1760/1761 and ISP1763, host and device `regmap_config` structures, volatile register ranges, and large `reg_field` arrays keyed by enums from `isp1760-regs.h`.

## Control Flow
`isp1760_register()` first checks that at least one compiled/enabled role can be registered. It allocates `struct isp1760_device`, records devflags, validates bus width constraints, chooses ISP1763 versus ISP1760/1761 register tables, gets an optional reset GPIO, maps the memory resource, initializes host and device regmaps on the same base, allocates all host and device regmap fields, selects the memory layout, and calls `isp1760_init_core()`.

`isp1760_init_core()` toggles reset GPIO if present, performs all-device reset, applies bus width, overcurrent, DACK/DREQ polarity, interrupt polarity, and edge/level flags, configures common IRQ and initial device-controller interrupt state for ISP1761, and programs OTG control for host or peripheral mode. After core init, `isp1760_register()` conditionally calls `isp1760_hcd_register()` and `isp1760_udc_register()`, unwinding HCD if UDC registration fails. Unregister removes UDC then HCD.

## State And Persistence
State is held in devm-managed `struct isp1760_device`, `struct isp1760_hcd`, `struct isp1760_udc`, regmaps, regmap fields, optional reset GPIO, and hardware registers. No durable persistence exists; hardware mode is reprogrammed on probe/reset. `dev_set_drvdata()` ties the state to the platform/PCI device for removal.

## Dependencies And Integration Points
The file depends on regmap MMIO, GPIO descriptors, USB role configuration, IRQ flags, memory resources, and the local HCD/UDC/register headers. It integrates with platform and PCI glue through `isp1760_register()` and with gadget pullup control through `isp1760_set_pullup()`.

## Risks
Regmap-field arrays must stay exactly aligned with enum values; missing or wrong `REG_FIELD()` entries can redirect register writes. ISP1763 has 16-bit register access and different field widths; regressions often appear only on that variant. Device and host regmaps share the same MMIO base with different register maps, so volatile ranges and max registers must remain correct. UDC enablement is inferred from ISP1761/ISP1763 flags, not only peripheral mode, so role logic must be changed carefully.

## Test Signals
Test probe on ISP1760, ISP1761, and ISP1763 descriptions; validate scratch/chip ID reads in role code; verify bus-width flags, reset GPIO timing, interrupt polarity flags, and peripheral-host OTG control writes. Build/test host-only, gadget-only, and dual-role configurations. Failure-injection should cover regmap field allocation, HCD registration failure, and UDC registration failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-core.h -->
# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-core.h

## Purpose
`isp1760-core.h` declares the common ISP1760 device container, board/chip flags, public registration API, pullup API, and small regmap helper wrappers used by both HCD and UDC code.

## Important APIs, Types, And Functions
`struct isp1760_device` owns `dev`, `devflags`, optional `rst_gpio`, embedded `struct isp1760_hcd`, and embedded `struct isp1760_udc`. Flags describe bus width, peripheral enablement, analog overcurrent, DACK/DREQ polarity, chip variant, interrupt polarity/triggering, and 8-bit mode. Public functions are `isp1760_register()`, `isp1760_unregister()`, and `isp1760_set_pullup()`. Inline helpers wrap `regmap_field_read/write`, set/clear full fields, and raw `regmap_read/write`.

## Control Flow
The header has no standalone runtime flow. Its helpers are called throughout core, HCD, and UDC paths to abstract field operations. The device flags are produced by bus glue and consumed by core initialization.

## State And Persistence
The state shape declared here persists for the lifetime of the bound device. It embeds both role states regardless of whether both roles are active; disabled role functions become stubs through their own headers.

## Dependencies And Integration Points
The header depends on Linux ioport and regmap plus the local HCD and UDC headers. It is the shared contract between bus glue, common core, host controller, and gadget controller.

## Risks
`isp1760_field_read()` and register helpers ignore regmap return values, so bus faults are not propagated. `isp1760_field_set()` writes `0xFFFFFFFF`, relying on regmap-field masking to constrain writes. Adding flags requires updates in platform/PCI parsing, core setup, and documentation/bindings.

## Test Signals
Compile coverage catches enum/type mismatches. Runtime signals come from probe and role operation across all chip variants, especially field writes for bus width, interrupts, pullup, and reset. Fault-injection of regmap operations would expose the current lack of error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-hcd.c

## Purpose
`isp1760-hcd.c` implements the USB host-controller driver for ISP1760/1761/1763 chips. It presents an `hc_driver` to USB core, packetizes URBs into Philips PTDs/QTDs, manages the chip's on-controller payload memory, handles completion interrupts, provides root-hub control, and works around known interrupt errata.

## Important APIs, Types, And Functions
Key private types are `struct ptd`, `struct isp1760_qtd`, `struct isp1760_qh`, and `struct urb_listitem`. Public entry points are `isp1760_init_kmem_once()`, `isp1760_deinit_kmem_cache()`, `isp1760_hcd_register()`, and `isp1760_hcd_unregister()`. The `hc_driver` callbacks include `isp1760_hc_setup()`, `isp1760_run()`, `isp1760_stop()`, `isp1760_shutdown()`, `isp1760_urb_enqueue()`, `isp1760_urb_dequeue()`, `isp1760_endpoint_disable()`, `isp1760_get_frame()`, `isp1760_hub_status_data()`, `isp1760_hub_control()`, and `isp1760_clear_tt_buffer_complete()`.

Important internals include register helpers, `mem_read()/mem_write()` variant dispatch, `ptd_read()/ptd_write()`, `init_memory()/alloc_mem()/free_mem()`, `packetize_urb()`, `create_ptd_atl()`, `create_ptd_int()`, `schedule_ptds()`, `handle_done_ptds()`, and `isp1760_irq()`.

## Control Flow
Registration creates a USB HCD, links `struct isp1760_hcd` through `hcd_priv`, allocates ATL and interrupt slot arrays sized by variant memory layout, initializes memory chunks, and calls `usb_add_hcd()`. Setup validates scratch register access, clears buffer-fill and skip maps, performs EHCI reset, resets ATL/INT hardware, configures ISP1763-specific OTG/lock bits, enables ATL/INT interrupts, and initializes queue lists.

URB enqueue selects the endpoint queue by pipe type, rejects isochronous transfers, packetizes data into setup/data/status or bulk/interrupt QTDs, links the URB to USB core, creates or reuses a QH, appends QTDs, and calls `schedule_ptds()`. Scheduling first collects completed/retired QTDs and gives back URBs outside the lock, then starts queued control, interrupt, and bulk transfers when chip memory and PTD slots are available. Completion IRQs read/ack interrupt status, merge done maps, parse PTD status, reload NAK/error cases, retire failed URBs, update data toggle/ping, read IN payloads back to URB buffers, and reschedule. Root-hub operations translate hub requests to `PORTSC1` fields and EHCI state transitions.

## State And Persistence
Runtime state lives in `struct isp1760_hcd`: USB HCD pointer, regmap fields, variant flag, memory layout, spinlock, ATL/INT slot arrays, done maps, memory chunk free list, QH lists, periodic scheduling values, reset timing, and next-state timestamps. QH/QTD/URB-list objects use kmem caches. Hardware state includes PTD tables, payload memory, skip/done/last maps, buffer-fill bits, port status, interrupt masks, and command/config registers. There is no durable persistence.

## Dependencies And Integration Points
The file depends on USB HCD core, EHCI shared reset semaphore, hub/TT helpers, regmap fields from core, MMIO accessors, timers, kmem caches, unaligned access, and cache flushing for IN transfers. It integrates with `isp1760-core.c` through preinitialized regmaps and memory layout, and with Kconfig through HCD stubs.

## Risks
Isochronous transfers are explicitly unsupported. The PTD scheduler is lock-heavy and sensitive to ordering: payload writes must precede valid-bit writes, done-map bits must be masked against skip maps, and URB giveback can reenter the HCD. Memory allocation is first-fit by fixed chunk sizes; large URBs are split to the largest block size. The global errata timer stores a single `errata2_timer_hcd`, which is a risk for multiple controllers. `isp1760_stop()` unconditionally deletes that timer even for ISP1763 where it may not have been added. Root-hub resume/reset handling uses timing assumptions and direct `PORTSC1` read-modify-write special cases. TT buffer dirty handling must prevent scheduling behind failed low/full-speed split transfers.

## Test Signals
Run USB host enumeration and `usbtest` with control, bulk, and interrupt endpoints on high-speed plus full/low-speed devices behind a hub. Test short bulk packets with and without `URB_SHORT_NOT_OK`, zero-length packets, dequeue during active transfers, endpoint disable, disconnect during transfers, root-hub reset/suspend/resume/power requests, and ISP1760 versus ISP1763 memory access paths. Stress tests should look for stuck PTD slots, memory-pool leaks, timer behavior, and URB giveback races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-hcd.h -->
# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-hcd.h

## Purpose
`isp1760-hcd.h` defines host-controller private state, memory-layout descriptors, slot tracking, queue categories, and HCD registration/cache APIs. It also provides no-op inline stubs when host role support is not compiled.

## Important APIs, Types, And Functions
`struct isp1760_slotinfo` binds a PTD slot to an active QH/QTD and timestamp. `struct isp1760_memory_layout` describes chip payload memory block counts, block sizes, slot count, payload block count, and payload area size. `struct isp1760_memory_chunk` tracks runtime allocation units. `enum isp1760_queue_head_types` separates control, bulk, and interrupt queues. `struct isp1760_hcd` stores USB HCD pointer, MMIO base, regmap/fields, variant flag, memory layout, spinlock, slot arrays, done maps, memory pool, QH lists, and root-hub scheduling/timing fields.

Public HCD functions are `isp1760_hcd_register()`, `isp1760_hcd_unregister()`, `isp1760_init_kmem_once()`, and `isp1760_deinit_kmem_cache()`, or stubs when disabled.

## Control Flow
The header has no standalone execution. Core registration fills regmaps and memory layout before calling `isp1760_hcd_register()`. The HCD implementation mutates the declared state under `lock` during enqueue, completion, dequeue, and hub control.

## State And Persistence
The structures define all host-side volatile state for a bound controller. PTD slot state and memory-pool state mirror hardware use and must be synchronized with skip/done maps and payload allocations.

## Dependencies And Integration Points
The header depends on spinlocks, regmap, local register enums, USB HCD declarations, and Kconfig. It is included by core so `struct isp1760_device` can embed HCD state.

## Risks
Constants `ISP176x_BLOCK_MAX` and `ISP176x_BLOCK_NUM` must match all memory layouts. If a new chip has more block classes or payload blocks, both array sizes and allocation loops need review. Inline stubs returning success mean core code can call HCD registration unconditionally in disabled builds, but a wrong Kconfig selection could hide missing host support until runtime.

## Test Signals
Build host-disabled and host-enabled configurations. Runtime host tests should monitor slot arrays and memory chunks for leaks after transfer enqueue/dequeue, endpoint disable, and controller unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-hcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-if.c -->
# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-if.c

## Purpose
`isp1760-if.c` is bus glue for the ISP1760 common driver. It supports OpenFirmware/platform devices and, under `CONFIG_USB_PCI`, the PLX PCI evaluation-card path for ISP1761.

## Important APIs, Types, And Functions
PCI-specific functions are `isp1761_pci_init()`, `isp1761_pci_probe()`, `isp1761_pci_remove()`, and `isp1761_pci_shutdown()`, with `isp1761_pci_driver` matching a PLX bridge. Platform functions are `isp1760_plat_probe()` and `isp1760_plat_remove()` with OF matches for `nxp,usb-isp1760`, `nxp,usb-isp1761`, and `nxp,usb-isp1763`. Module entry/exit are `isp1760_init()` and `isp1760_exit()`.

## Control Flow
Module init creates HCD kmem caches, registers the platform driver, and optionally registers the PCI driver; if neither registration succeeds it destroys caches and returns `-ENODEV`. Platform probe obtains MMIO and IRQ resources, reads IRQ trigger type, parses OF compatibility and properties into devflags (`bus-width`, `dr_mode`, `analog-oc`, DACK/DREQ polarity), then calls `isp1760_register()`. PCI probe enables the device, runs PLX setup, sets bus mastering, and calls `isp1760_register()` on resource 3 and the PCI IRQ.

PCI init probes scratch access through resource 3, adjusts PCI latency, configures PLX interrupt pass-through via resource 0, and releases temporary mappings/regions before common registration.

## State And Persistence
Bus glue itself keeps no long-lived state beyond registered platform/PCI drivers. Device state is owned by `isp1760_register()` and stored as driver data on the device. PCI enablement and PLX interrupt bits are hardware state lasting until remove/shutdown.

## Dependencies And Integration Points
The file depends on platform devices, OF helpers, USB OTG/dr-mode parsing, IRQ trigger helpers, PCI APIs when enabled, MMIO mapping, and the common ISP1760 registration API. It is the bridge from device tree or PCI IDs to `devflags`.

## Risks
Platform probe rejects non-OF devices with `-ENXIO`, so board-file platform data is not supported. PCI error paths call `pci_disable_device()` but common registration failures rely on the common layer for partial cleanup. `isp1761_pci_shutdown()` only logs and does not stop hardware. PCI temporary resource names and scratch-test assumptions are evaluation-card specific. `isp1760_init()` ignores the return from `isp1760_init_kmem_once()`, so cache allocation failure can surface later.

## Test Signals
Test OF probe for each compatible and bus-width value, missing IRQ/resource failures, peripheral dr_mode flagging, analog overcurrent rejection on ISP1763, and remove/unregister. PCI tests should validate scratch mismatch, resource request failures, PLX interrupt enabling, and disable paths. Build with and without `CONFIG_USB_PCI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-regs.h -->
# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-regs.h

## Purpose
`isp1760-regs.h` is the register map and field enum contract for ISP1760/1761/1763 host and peripheral controllers. It centralizes MMIO offsets, bit masks, endpoint interrupt macros, endpoint type constants, and enum indexes used by regmap-field arrays.

## Important APIs, Types, And Functions
The host section defines ISP1760/1761 EHCI capability/operational offsets, PTD done/skip/last maps, hardware mode, chip ID, scratch, reset, buffer status, memory, interrupt masks, and OTG control registers. `enum isp176x_host_controller_fields` assigns stable indexes for host regmap fields.

The device section defines endpoint interrupt macros (`DC_IEPTX`, `DC_IEPRX`, `DC_IEPRXTX`), interrupt/status bit masks, OTG bit masks, endpoint type values, ISP176x DC register offsets, `enum isp176x_device_controller_fields`, and ISP1763 DC register offsets.

## Control Flow
There is no executable control flow. Core code maps enum values to `REG_FIELD()` definitions; HCD and UDC code use enum values through regmap-field helpers and raw offsets for data/FIFO and interrupt access.

## State And Persistence
The file describes hardware register state but stores none itself. The enum order is persistent ABI within this driver: every array indexed by these enums must match exactly.

## Dependencies And Integration Points
The header integrates core, HCD, and UDC. It depends on the kernel `BIT()` macro from including contexts. Device-tree bindings and datasheets must remain aligned with compatible-specific offset sets and chip IDs.

## Risks
Enum ordering is a high-risk maintenance point. Adding a field in the middle without updating all ISP1760 and ISP1763 `reg_field` arrays corrupts field access. Some names are shared between set/clear alias registers and normal registers, so variant-specific code must choose correct offsets. Host and device register spaces differ significantly between ISP1760/61 and ISP1763.

## Test Signals
Compile tests catch only missing enum entries if arrays use sentinel indexes; runtime scratch, chip ID, port control, endpoint FIFO, and interrupt tests are needed for real offset validation. Variant-specific tests should cover both 32-bit ISP1760/61 and 16-bit ISP1763 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-udc.c

## Purpose
`isp1760-udc.c` implements the USB gadget/device-controller role for ISP1761/ISP1763 hardware. It registers a `usb_gadget`, implements endpoint operations, handles EP0 control transfers, moves data through endpoint FIFOs, processes shared IRQ status, monitors VBUS, and exposes pullup/start/stop operations to gadget drivers.

## Important APIs, Types, And Functions
The request wrapper is `struct isp1760_request`. Conversion helpers map gadget/endpoint/request objects back to UDC structures. Public functions are `isp1760_udc_register()` and `isp1760_udc_unregister()`. Endpoint operations are `isp1760_ep_enable()`, `isp1760_ep_disable()`, `isp1760_ep_alloc_request()`, `isp1760_ep_free_request()`, `isp1760_ep_queue()`, `isp1760_ep_dequeue()`, `isp1760_ep_set_halt()`, `isp1760_ep_set_wedge()`, and `isp1760_ep_fifo_flush()`. Gadget ops are `get_frame`, `wakeup`, `set_selfpowered`, `pullup`, `udc_start`, and `udc_stop`.

Core data paths are `isp1760_udc_receive()`, `isp1760_udc_transmit()`, `isp1760_ep_rx_ready()`, `isp1760_ep_tx_complete()`, `isp1760_ep0_setup()`, `isp1760_ep0_setup_standard()`, `isp1760_udc_irq()`, and `isp1760_udc_vbus_poll()`.

## Control Flow
Registration initializes the UDC lock/timer, validates hardware through scratch/chip ID, resets DC mode, allocates an IRQ name, requests a shared IRQ, initializes gadget static fields and endpoints, and calls `usb_add_gadget_udc()`. Gadget start validates speed, records the driver, sets attached state, enables global device interrupts, initializes hardware interrupt modes/masks, sets pullup if connected, and enables the device. Stop deletes the VBUS timer, clears the mode register, and drops the gadget driver.

EP0 setup IRQ reads the 8-byte setup packet, advances the EP0 state to data-in, data-out, or status, then handles standard requests internally where possible. GET_STATUS writes a two-byte IN response directly. SET_ADDRESS writes address/dev-enable and sends status. SET/CLEAR_FEATURE endpoint halt manipulates endpoint stall state. Nonstandard or configuration requests are passed to the gadget driver's setup callback. Data endpoint queueing starts IN transmission immediately when idle or consumes pending OUT FIFO data if `rx_pending` was set.

## State And Persistence
`struct isp1760_udc` holds the gadget driver pointer, gadget object, spinlock, VBUS timer, endpoint array, EP0 state/direction/length, connected flag, variant flag, and device status bits. Each `struct isp1760_ep` tracks descriptor, request queue, maxpacket, address, halted/wedged/rx_pending flags. State is volatile and reset by disconnect, bus reset, endpoint disable, and gadget stop. Hardware endpoint registers are banked by `DC_EPINDEX`.

## Dependencies And Integration Points
The file depends on USB gadget core, IRQ APIs, timers, regmap/raw FIFO access, local core pullup helper, and register definitions. It integrates with the common ISP1760 device through embedded UDC state and shared regmaps. Gadget drivers interact through standard `usb_ep_ops` and `usb_gadget_ops`.

## Risks
The FIFO read/write loops use 32-bit and 16-bit raw accesses and comments note hardware quirks around extra bytes and CLBUF not fully flushing transmit FIFO. `short_not_ok` is not implemented for OUT requests. Endpoint disable has a TODO to synchronize with the IRQ handler. Clearing halt on an IN endpoint with queued data can restart transmission, so queue and stall ordering is delicate. VBUS interrupt only reports attach; detach is detected by polling. EP array indexing maps IRQ endpoint numbers to IN/OUT entries in a compact way, which is easy to break. Remote wakeup/test mode are not implemented.

## Test Signals
Use gadget functions such as loopback, mass storage, ECM/RNDIS, or configfs to test enumeration, SET_ADDRESS, SET_CONFIGURATION, GET_STATUS, endpoint halt/wedge clear, IN/OUT bulk and interrupt transfers, zero-length packets, disconnect/reconnect, suspend/resume, high-speed status, VBUS removal polling, and bus reset. Fault tests should cover IRQ sharing, request dequeue, endpoint disable with active queues, and gadget driver unbind during traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-udc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-udc.h

## Purpose
`isp1760-udc.h` declares the device-controller private state and public registration API for the ISP1761/ISP1763 gadget role. It also provides disabled-role stubs when UDC support is not compiled.

## Important APIs, Types, And Functions
`enum isp1760_ctrl_state` models EP0 as setup, data-in, data-out, or status. `struct isp1760_ep` embeds a `usb_ep`, request queue, endpoint address/name, maxpacket, descriptor pointer, and flags for pending RX, halt, and wedge. `struct isp1760_udc` embeds the common device pointer, IRQ metadata, regmap and fields, gadget driver and gadget object, spinlock, VBUS timer, endpoint array, EP0 state fields, connection flag, variant flag, and device status bits. Public functions are `isp1760_udc_register()` and `isp1760_udc_unregister()`, or stubs.

## Control Flow
The header has no executable flow. Registration and endpoint logic in `isp1760-udc.c` mutate these structures under `lock`, especially around banked endpoint register selection and EP0 state transitions.

## State And Persistence
The structures define all volatile UDC state for a bound controller. Endpoint queues persist while a gadget function is bound and endpoints are enabled. Device status tracks self-powered state and is reported through standard GET_STATUS.

## Dependencies And Integration Points
The header depends on ioport, list, spinlock, timer, USB gadget types, and local register definitions. It is embedded by `struct isp1760_device` in the common core.

## Risks
The endpoint array is fixed at 15 entries, representing EP0 plus IN/OUT pairs for endpoints 1-7. Hardware or driver changes for more endpoints require array, IRQ dispatch, and naming changes. The spinlock comment defines ownership for driver, timer, endpoint, EP0, and `DC_EPINDEX`; violating that contract can corrupt banked endpoint register accesses.

## Test Signals
Build gadget-disabled and gadget-enabled configurations. Runtime gadget tests should validate endpoint enumeration, queue lifetime, halt/wedge state, EP0 transitions, and unregister after active gadget use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-udc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/Kconfig

## Purpose
This Kconfig file defines user-selectable options for miscellaneous USB drivers that do not fit better in other USB subdirectories. The subset-relevant options are `USB_ADUTUX`, `USB_APPLEDISPLAY`, and `APPLE_MFI_FASTCHARGE`, but the file also aggregates many unrelated misc USB drivers and sources the SIS USB VGA Kconfig.

## Important APIs, Types, And Functions
`USB_ADUTUX` enables Ontrak ADU device support. `USB_APPLEDISPLAY` selects `BACKLIGHT_CLASS_DEVICE` and enables USB control of Apple Cinema Display backlights. `APPLE_MFI_FASTCHARGE` selects `POWER_SUPPLY` and exposes fast-charge control for Apple MFi devices. Other options configure firmware loaders, USB test drivers, USB-to-parallel, HID-like devices, bridge adapters, hub controllers, random generators, and onboard USB device support.

## Control Flow
Kconfig symbol selection determines which objects the misc Makefile builds. Some symbols select dependencies, such as backlight or power-supply frameworks, while others depend on platform capabilities such as ACPI, OF, I2C, HW_RANDOM, or QCOM SCM.

## State And Persistence
There is no runtime state in the file. The kernel configuration persists selected drivers and dependency choices.

## Dependencies And Integration Points
The file integrates the misc USB directory with subsystem dependencies and user-visible menu prompts. It must stay synchronized with object names in `drivers/usb/misc/Makefile` and with each driver's required frameworks.

## Risks
Wrong dependency/select clauses lead to link failures or missing runtime framework support. User-facing help text can become stale when driver behavior changes. Since this file covers many unrelated drivers, edits for one option can unintentionally alter menu structure or dependency resolution for others.

## Test Signals
Build coverage for the relevant options as built-in and modules is the primary signal. Configuration tests should verify that `USB_APPLEDISPLAY` pulls in backlight support and `APPLE_MFI_FASTCHARGE` pulls in power-supply support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/Makefile

## Purpose
The misc USB Makefile maps Kconfig symbols to object files for the miscellaneous USB driver directory. It is the build manifest for this collection of independent drivers.

## Important APIs, Types, And Functions
Relevant mappings are `obj-$(CONFIG_USB_ADUTUX) += adutux.o`, `obj-$(CONFIG_USB_APPLEDISPLAY) += appledisplay.o`, and `obj-$(CONFIG_APPLE_MFI_FASTCHARGE) += apple-mfi-fastcharge.o`. It also maps many other misc driver symbols and descends into `sisusbvga/` for `USB_SISUSBVGA`.

## Control Flow
kbuild evaluates each `obj-*` assignment from the active configuration and compiles the selected objects either into vmlinux or as modules.

## State And Persistence
There is no runtime state. Build artifacts reflect the configured object list.

## Dependencies And Integration Points
This file depends on Kconfig symbol names and source filenames remaining synchronized. It is consumed by top-level kernel kbuild.

## Risks
Renaming a source file or Kconfig symbol without updating this mapping causes missing drivers or build failures. Because the file is flat and broad, merge conflicts or nearby edits can easily misplace a mapping.

## Test Signals
Subtree builds with each relevant config enabled should produce `adutux.o`, `appledisplay.o`, and `apple-mfi-fastcharge.o`. Module packaging should produce expected module names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/adutux.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/adutux.c

## Purpose
`adutux.c` is a character-device USB driver for Ontrak Control Systems ADU devices. It exposes interrupt-in and interrupt-out endpoint traffic to userspace through `/dev/usb/adutux%d`, with single-open policy and buffered reads/writes.

## Important APIs, Types, And Functions
`struct adu_device` stores the USB device/interface, minor, serial, open/disconnect state, primary and secondary read buffers, interrupt buffers, endpoints, URBs, wait queues, mutexes, and spinlock-protected completion flags. USB binding uses `adu_driver`, `device_table`, `adu_probe()`, and `adu_disconnect()`. Character operations are `adu_open()`, `adu_release()`, `adu_read()`, and `adu_write()`. URB callbacks are `adu_interrupt_in_callback()` and `adu_interrupt_out_callback()`. Cleanup helpers are `adu_abort_transfers()` and `adu_delete()`.

## Control Flow
Probe allocates device state, initializes locks/waits, finds interrupt-in and interrupt-out endpoints, allocates double read buffers plus endpoint buffers and URBs, reads a serial string, stores interface data, and registers the USB class device. Open finds the interface by minor, enforces one opener, resets read buffer length, submits an initial interrupt-in URB, and marks the interrupt-out path idle.

Read drains the secondary buffer first. If empty, it swaps in primary data filled by the interrupt callback or submits/waits for an input URB. It handles timeout, signals, and copy errors while using `mtx` for high-level serialization and `buflock` for callback-shared buffer flags. Write waits for any prior interrupt-out URB to complete, copies up to endpoint maxpacket from userspace, submits an interrupt-out URB, and repeats until the user buffer is consumed. Disconnect deregisters the devnode, poisons URBs, marks disconnected under locks, and frees immediately only when not open; release frees after unplug if it is the last user.

## State And Persistence
State is per ADU device and lasts from probe until disconnect plus final close. Read data is staged in a primary buffer filled by interrupt callbacks and a secondary buffer drained by userspace. Completion flags `read_urb_finished` and `out_urb_finished` coordinate sleepers. No data persists beyond driver lifetime.

## Dependencies And Integration Points
The driver depends on USB core, `usb_class_driver`, interrupt URBs, user-copy helpers, wait queues, mutexes, spinlocks, and dynamic/static minor allocation. It integrates with userspace as a simple char device rather than a higher-level subsystem.

## Risks
The locking scheme is documented but delicate: global `adutux_mutex` covers open count, `mtx` covers sleeping operations, and `buflock` covers callback-visible buffers. `adu_interrupt_out_callback()` returns without setting `out_urb_finished` or waking waiters for nonzero status, which can cause write-side timeout behavior. The read buffer capacity is `4 * maxpacket`; overflow is logged and data is dropped. `adu_abort_transfers()` waits for output completion while handling disconnect/open lifetime. Serial string retrieval failure rejects the device.

## Test Signals
Test open exclusivity, read/write with endpoint maxpacket boundaries, partial reads from secondary buffer, timeout paths, signal interruption, unplug during blocking read/write, open-after-disconnect, disconnect while open followed by release, and URB completion errors. Dynamic minor and static minor configurations should both be built.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/adutux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/apple-mfi-fastcharge.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/apple-mfi-fastcharge.c

## Purpose
`apple-mfi-fastcharge.c` registers a USB device-level driver that exposes Apple MFi fast-charge control as a power-supply device. It matches Apple devices with product IDs in the `0x12nn` range and lets userspace switch charge type between trickle and fast.

## Important APIs, Types, And Functions
`struct mfi_device` stores the USB device, registered `power_supply`, power-supply descriptor, and current charge type. `mfi_fc_driver` is a `usb_device_driver`, not an interface driver. Matching is split between `mfi_fc_id_table` for vendor and `mfi_fc_match()` for product range. Power-supply callbacks are `apple_mfi_fc_get_property()`, `apple_mfi_fc_set_property()`, and `apple_mfi_fc_property_is_writeable()`. The hardware command is issued by `apple_mfi_fc_set_charge_type()`.

## Control Flow
Driver init calls `usb_register_device_driver()`. Probe validates the product range, allocates state and a per-device power-supply name, copies the descriptor, sets initial charge type to trickle, registers the power supply, stores the USB device pointer, and attaches driver data to `udev->dev`. Setting `POWER_SUPPLY_PROP_CHARGE_TYPE` runtime-resumes the USB device, maps requested charge type to 0 mA or 2500 mA, sends a vendor OUT control request `0x40` with current in both `wValue` and `wIndex`, updates cached state on success, then autosuspends. Disconnect unregisters the power supply and frees the descriptor name and state.

## State And Persistence
The only persistent runtime state is `charge_type` in memory and whatever charging mode the device applies after the vendor request. The power-supply descriptor name is dynamically allocated per bus/device number. State disappears on disconnect or module unload.

## Dependencies And Integration Points
The driver depends on USB device-driver APIs, runtime PM, and the power-supply class. Userspace observes and writes `POWER_SUPPLY_PROP_CHARGE_TYPE` and sees scope as `POWER_SUPPLY_SCOPE_DEVICE`.

## Risks
The match table initially matches all Apple vendor devices and relies on `.match()` and `.probe()` to narrow to `0x1200..0x12ff`. The vendor control request is based on MFi behavior and may fail or be unsupported on some devices. `usb_control_msg()` uses `USB_CTRL_GET_TIMEOUT` despite being an OUT request, which is unusual but probably only a timeout constant. Probe sets `mfi->udev` after power-supply registration, so callbacks before that assignment would dereference NULL; normal registration paths likely prevent immediate property calls, but it is a lifetime assumption.

## Test Signals
Test matching for Apple product IDs inside and outside `0x12nn`, power-supply registration naming, charge-type get/set, invalid charge types returning `-EINVAL`, runtime PM failure, control-transfer failure, disconnect after registration, and repeated set to the same charge type avoiding USB traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/apple-mfi-fastcharge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/appledisplay.c -->
# sources/distributed-fs/ceph-client/drivers/usb/misc/appledisplay.c

## Purpose
`appledisplay.c` is a USB HID-interface driver for Apple Cinema Displays. It registers a Linux backlight device, sends HID class control reports to get/set brightness, and listens to interrupt reports for display brightness buttons.

## Important APIs, Types, And Functions
`struct appledisplay` stores the USB device, interrupt URB, backlight device, interrupt/control buffers, delayed work, button state, and `sysfslock` mutex. Matching uses `APPLEDISPLAY_DEVICE()` entries for Apple vendor/product IDs with HID class and protocol 0. Key functions are `appledisplay_probe()`, `appledisplay_disconnect()`, `appledisplay_complete()`, `appledisplay_bl_update_status()`, `appledisplay_bl_get_brightness()`, and `appledisplay_work()`.

## Control Flow
Probe finds the first interrupt-in endpoint, allocates state, control buffer, interrupt URB, and coherent interrupt buffer, submits the URB, registers a backlight device named with an atomic display count, reads initial brightness through a HID GET_REPORT control transfer, stores brightness, and attaches interface data. The interrupt completion callback interprets report byte 1 as brightness-up/down/none, schedules delayed work while a button is pressed, and resubmits the interrupt URB. Work reads brightness and updates the backlight property, then reschedules every 125 ms while the button remains pressed. Backlight sysfs updates send HID SET_REPORT control transfers. Disconnect kills the URB, cancels work, unregisters backlight, and frees buffers.

## State And Persistence
State is per display interface and volatile. Brightness is stored in hardware and mirrored in `bd->props.brightness`. `button_pressed` drives polling while a hardware button is held. `count_displays` is a module-global atomic used only to generate unique names.

## Dependencies And Integration Points
The driver depends on USB core, HID request constants, interrupt URBs, coherent DMA buffer allocation, backlight class, delayed work, mutexes, and atomic counters. Userspace integrates through the standard backlight sysfs interface.

## Risks
The error path checks `if (!IS_ERR(pdata->bd))` even when `bd` may be NULL from zeroed allocation, which can call unregister on NULL depending on helper semantics. Probe submits the interrupt URB before backlight registration, and the callback has a comment about a window where no device is registered. Interrupt resubmission failures stop button monitoring. Brightness control serializes control messages with `sysfslock`, but disconnect must kill URB and cancel work before freeing. The driver assumes two-byte HID reports and uses fixed report IDs/values.

## Test Signals
Test probe with missing interrupt endpoint, allocation failures at each step, initial brightness GET_REPORT failure, sysfs brightness set/get, hardware brightness buttons causing delayed polling, disconnect while work is pending, URB shutdown statuses, and multiple displays generating unique backlight names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/misc/appledisplay.c -->
