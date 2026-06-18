# Research Report: subset-b-005500

This grouped report covers USB gadget UDC framework and controller files from `sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/`. Each file section is bounded for deterministic splitting into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-gadget.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-gadget.h

## Purpose

`cdns2-gadget.h` is the private hardware and software contract for the Cadence USBHS-DEV CDNS2 gadget controller driver. It defines the MMIO register layouts for EP0, non-control endpoints, interrupt registers, common USB registers, and ADMA registers, plus the transfer-ring/TRB formats and the in-memory `cdns2_device`, `cdns2_endpoint`, and `cdns2_request` objects used by the implementation files. The header does not implement behavior, but it fixes the bit-level interface that all CDNS2 gadget, EP0, PCI, tracing, and debug code rely on.

## Important APIs, Types, And Constants

The register structures are packed/aligned views over the device MMIO aperture: `struct cdns2_ep0_regs`, `struct cdns2_epx_regs`, `struct cdns2_interrupt_regs`, `struct cdns2_usb_regs`, and `struct cdns2_adma_regs`. Their companion bit masks define EP0 control/status bits (`EP0CS_STALL`, `EP0CS_HSNAK`, `EP0CS_TXBSY_MSK`, `EP0CS_RXBSY_MSK`, `EP0CS_DSTALL`, `EP0CS_CHGSET`), endpoint configuration fields (`EPX_CON_TYPE_*`, `EPX_CON_STALL`, `EPX_CON_VAL`), USB/LPM/pullup bits (`USBCS_SIGRSUME`, `USBCS_DISCON`, `SPEEDCTRL_*`, `CPUCTRL_*`), and ADMA endpoint status/command bits (`DMA_EP_CMD_DRDY`, `DMA_EP_CMD_DFLUSH`, `DMA_EP_STS_IOC`, `DMA_EP_STS_TRBERR`, `DMA_EP_STS_DBUSY`, `DMA_EP_IEN`, `DMA_EP_ISTS`).

The DMA ring contract is encoded by `struct cdns2_trb` and the TRB constants. `TRBS_PER_SEGMENT` is 600, with two additional reserved TRBs for isochronous handling. `TRB_NORMAL` and `TRB_LINK` describe data and link descriptors; `TRB_CYCLE`, `TRB_TOGGLE`, `TRB_ISP`, `TRB_CHAIN`, and `TRB_IOC` drive hardware ownership and completion signaling. `TRB_BUFF_LEN_UP_TO_BOUNDARY()` exists because TRB buffer pointers must not cross 4 KiB boundaries for performance/correctness.

The core driver state is split among `struct cdns2_ring` for producer/consumer positions and cycle state, `struct cdns2_endpoint` for a USB endpoint plus pending/deferred request lists and hardware state flags, `struct cdns2_request` for a `usb_request` plus TRB bookkeeping, and `struct cdns2_device` for controller-wide state. `struct cdns2_device` holds all register bases, IRQ, DMA pool, EP0 setup/request state, endpoint table, selected DMA endpoint, wake/self-powered flags, pending status work, supported endpoint bitmap, burst optimization table, and on-chip buffer sizes.

The exported private prototypes include endpoint and EP0 helpers such as `cdns2_select_ep()`, `cdns2_next_preq()`, `cdns2_gadget_ep_alloc_request()`, `cdns2_gadget_ep_dequeue()`, `cdns2_gadget_giveback()`, `cdns2_init_ep0()`, `cdns2_ep0_config()`, `cdns2_handle_ep0_interrupt()`, `cdns2_handle_setup_packet()`, `cdns2_gadget_suspend()`, `cdns2_gadget_resume()`, `cdns2_gadget_init()`, `cdns2_gadget_remove()`, and `cdns2_halt_endpoint()`.

## Control Flow And State

The header implies a ring-driven data path: gadget requests are wrapped as `cdns2_request`, mapped to one or more TRBs, placed on a `cdns2_endpoint.ring`, and moved between `pending_list` and `deferred_list` according to ring space and hardware progress. Completion uses `start_trb`, `end_trb`, `finished_trb`, and `num_of_trb` to account for partial descriptor progress. EP0 is modeled as a small state machine using `CDNS2_SETUP_STAGE`, `CDNS2_DATA_STAGE`, and `CDNS2_STATUS_STAGE`, with `ep0_preq`, `setup`, and `pending_status_request` in `struct cdns2_device`.

Endpoint persistence is in memory and MMIO only. `ep_state` bit flags track enabled, stalled, wedge, claimed, full ring, pending stall, and deferred doorbell state. Ring cycle bits (`pcs` and `ccs`) persist producer/consumer ownership while the driver is loaded. The controller state is not durable across driver removal or reset; initialization code must reconstruct rings, register bases, and endpoint state from platform data and hardware registers.

## Dependencies And Integration Points

The header depends on Linux USB gadget APIs (`linux/usb/gadget.h`), DMA direction definitions, kernel bit helpers, endianness types, and MMIO access conventions used by implementation files. `cdns2-pci.c` fills `struct cdns2_device` platform fields and calls `cdns2_gadget_init()`/`cdns2_gadget_remove()`. `cdns2-trace.h` inspects `struct cdns2_endpoint`, `struct cdns2_request`, `struct cdns2_trb`, and ADMA registers for tracepoints. Other CDNS2 source files, not in this subset, provide the function bodies declared here.

## Risks

The main risks are hardware contract drift and bitfield misuse. Register structures rely on exact offsets, packed layout, alignment, and mixed 8/16/32-bit accesses; a wrong field size or offset will corrupt controller programming. The endpoint existence macro `CDNS2_IF_EP_EXIST()` encodes direction bits in `eps_supported`, so platform glue must populate the bitmap consistently. TRB boundaries, ring wrap, and cycle toggling are subtle failure points that can cause stuck transfers, duplicate completions, or DMA reading stale descriptors. The `burst_opt[MAX_ISO_SIZE + 1]` table and ISO-specific reserved TRBs indicate special care is needed for isochronous endpoints and missed TD recovery.

## Test Signals

Useful signals include successful gadget registration through the CDNS2 platform glue, EP0 enumeration through setup/data/status stages, tracepoints for request enqueue/giveback and TRB completion, DMA endpoint interrupt status without `DMA_EP_STS_TRBERR` or `DMA_EP_STS_DESCMIS`, and suspend/resume/LPM handling through the declared gadget callbacks. Ring pressure tests should watch `EP_RING_FULL`, `EP_DEFERRED_DRDY`, and deferred request behavior. Endpoint halt/wedge tests should validate `EP_STALLED`, `EP_STALL_PENDING`, and hardware STALL bits remain synchronized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-gadget.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-pci.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-pci.c

## Purpose

`cdns2-pci.c` is the PCI glue layer for the Cadence CDNS2 USBHS device controller. It discovers a Cadence PCI USB device-function, maps BAR0, fills platform-specific fields in `struct cdns2_device`, delegates controller setup to the CDNS2 gadget core, and wires system sleep callbacks to gadget suspend/resume.

## Important APIs And Functions

`cdns2_pci_probe()` is the primary entry point. It validates that the matched function is function 0 and has `PCI_CLASS_SERIAL_USB_DEVICE`, enables the PCI device with managed PCI helpers, sets bus mastering, allocates `struct cdns2_device` with devres, requests and maps BAR0, stores the IRQ, hard-codes the supported endpoint bitmap and on-chip buffer sizes, then calls `cdns2_gadget_init(priv_dev)`. On success it stores private data with `pci_set_drvdata()`, enables wakeup, and drops runtime PM usage if the device can run-wake.

`cdns2_pci_remove()` reverses runtime wake handling and calls `cdns2_gadget_remove()`. `cdns2_pci_suspend()` and `cdns2_pci_resume()` fetch the private device from driver data and delegate to `cdns2_gadget_suspend()` and `cdns2_gadget_resume(priv_dev, 1)`. The PM operations are installed through `SYSTEM_SLEEP_PM_OPS`. The PCI match table binds `PCI_VENDOR_ID_CDNS`/`PCI_DEVICE_ID_CDNS_USB` with the USB device class, and `module_pci_driver()` registers the driver.

## Control Flow And State

Probe is linear and mostly devm-managed. It refuses unexpected PCI functions/classes before touching hardware. After `pcim_enable_device()` and `pci_set_master()`, all durable state for the CDNS2 gadget implementation is stored in the allocated `struct cdns2_device`: `regs`, `irq`, `dev`, `eps_supported`, `onchip_tx_buf`, and `onchip_rx_buf`. The real UDC state machine starts only after `cdns2_gadget_init()`. Removal does not manually unmap BARs or free memory because those are managed by devres/pcim; it only asks the gadget layer to unregister and quiesce the controller.

Runtime/system power state is shallow in this file. Wakeup is enabled unconditionally after gadget init, and runtime PM usage is adjusted when `pci_dev_run_wake()` is true. System sleep uses the gadget layer as the source of controller-specific sequencing. The `hibernated` argument to resume is passed as `1`, so downstream CDNS2 resume code must treat PCI system resume as a hibernation-like restoration path.

## Dependencies And Integration Points

The file depends on Linux PCI, PM runtime, devres, and the private CDNS2 gadget header. It integrates with the implementation behind `cdns2_gadget_init()`, which must interpret `regs` as a full USBHS MMIO aperture and derive sub-register bases. It integrates with Linux module autoloading through `MODULE_DEVICE_TABLE(pci, cdns2_pci_ids)` and `MODULE_ALIAS("pci:cdns2")`.

## Risks

The endpoint support and on-chip buffer sizing are hard-coded (`0x000f000f`, 16 KiB TX, 16 KiB RX). If future Cadence PCI variants expose different endpoint counts or buffer resources, this glue layer could over-advertise or under-utilize hardware. The class check is strict, so devices with correct IDs but unexpected class encoding will be rejected. BAR0 is requested under the generic name `"dev"`, which is harmless but less descriptive during resource conflicts. The driver assumes the IRQ is already configured in `pdev->irq`.

## Test Signals

Positive test signals are successful PCI bind, BAR0 mapping, `cdns2_gadget_init()` success, UDC appearance under `/sys/class/udc`, and gadget enumeration after binding a gadget function. Suspend/resume tests should confirm `cdns2_gadget_suspend()` and `cdns2_gadget_resume(..., 1)` preserve endpoint and EP0 state. Wake tests should verify that `device_wakeup_enable()` and `pci_dev_run_wake()` behavior does not leave runtime PM references unbalanced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-trace.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-trace.c

## Purpose

`cdns2-trace.c` is the tracepoint definition translation unit for the CDNS2 USBHS device controller. It defines `CREATE_TRACE_POINTS` and includes `cdns2-trace.h`, causing the trace event classes and trace events declared in the header to allocate their tracepoint storage exactly once.

## Important APIs And Functions

There are no runtime functions in this file. Its only functional statement is `#define CREATE_TRACE_POINTS` followed by `#include "cdns2-trace.h"`. This is the standard Linux tracing pattern: other source files include the trace header to use `trace_cdns2_*()` helpers, while this file instantiates them.

## Control Flow, State, And Persistence

This file has compile-time effect rather than direct runtime control flow. The state it creates is the kernel tracepoint metadata and static event descriptors generated by `trace/define_trace.h` through `cdns2-trace.h`. Persistence lasts for the loaded module or built-in kernel lifetime. Runtime event enablement, buffering, and filtering are managed by ftrace/tracefs rather than by this file.

## Dependencies And Integration Points

The file depends entirely on `cdns2-trace.h` and the kernel tracepoint infrastructure. It must be built into the same module or object collection as the CDNS2 gadget driver users of the trace events. If this file is omitted while other files call trace helpers, linking will fail; if more than one translation unit defines `CREATE_TRACE_POINTS` for the same header, duplicate definitions can occur.

## Risks

The risk surface is build integration. The file must remain minimal and must not include trace headers in an order that breaks `CREATE_TRACE_POINTS`. Any changes to `cdns2-trace.h` that reference driver-private structs, helper decoders, or register fields must still compile in this translation unit.

## Test Signals

Build success is the primary signal. Runtime signals are tracefs events appearing under the CDNS2 trace system (`cdns2-dev`/`cdns2_dev` naming as generated by the header), and events being emitted when enabled during endpoint operations, IRQ handling, request queueing, and TRB completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-trace.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-trace.h

## Purpose

`cdns2-trace.h` defines the trace event schema for the Cadence CDNS2 USBHS gadget driver. It converts low-level controller activity into structured ftrace events for pullup transitions, endpoint halt/configuration, EP0 setup/status flow, USB and DMA interrupts, request lifecycle, TRB queuing/completion, ring snapshots, and request progress. It is an observability layer and does not alter device behavior.

## Important APIs, Event Classes, And Events

The trace system is named `cdns2-dev` with variable name `cdns2_dev`. The header includes Linux tracepoint APIs, USB Chapter 9 definitions, `cdns2-gadget.h`, and `cdns2-debug.h`, relying on decode helpers such as `cdns2_decode_usb_irq()`, `cdns2_decode_epx_irq()`, `cdns2_decode_ep0_irq()`, `usb_decode_ctrl()`, `cdns2_decode_trb()`, and `cdns2_raw_ring()`.

Event classes reduce duplication. `cdns2_log_enable_disable` backs `cdns2_pullup`. `cdns2_log_simple` backs string events such as `cdns2_no_room_on_ring`, `cdns2_ep0_status_stage`, `cdns2_ep0_setup`, and `cdns2_device_state`. `cdns2_log_doorbell` backs EP0/EPX doorbell events and records endpoint name plus transfer-ring address. `cdns2_log_request` backs enqueue, enqueue error, allocation, free, dequeue, and giveback events while capturing request pointers, buffer, length/actual, status, DMA address, zero/short/no-interrupt flags, SG metadata, and TRB bounds.

Dedicated `TRACE_EVENT`s include `cdns2_ep_halt`, `cdns2_wa1`, `cdns2_dma_ep_ists`, and ring/endpoint/config events. `cdns2_log_epx_irq` and `cdns2_log_ep0_irq` read ADMA registers at trace time to include endpoint interrupt status and transfer-ring address. `cdns2_log_trb` snapshots TRB buffer/length/control fields. `cdns2_log_ring` copies the endpoint and the full TRB segment into dynamic arrays, then formats the raw ring.

## Control Flow And State

Trace calls are passive hooks placed in implementation code. When disabled, tracepoints compile to low-overhead checks; when enabled, they snapshot selected driver and MMIO state into trace buffers. Some events read hardware registers (`ep_sts`, `ep_ists`, `ep_traddr`) and some copy a full transfer ring (`TR_SEG_SIZE`), so event placement matters: these should be used where the driver already has coherent endpoint state and, for ring dumping, where the copy cost is acceptable.

The trace state is not driver-owned persistence. Trace buffers are managed by the kernel tracing subsystem. The header does copy transient request, endpoint, and TRB data into trace entries so later analysis is not dependent on object lifetime, except for pointer values that remain diagnostic only.

## Dependencies And Integration Points

The header integrates with CDNS2 private structs and debug decoders. It also depends on `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE cdns2-trace`, which require build rules to make the header visible from the trace generation context. Runtime consumers are developers using tracefs/perf/ftrace while debugging gadget enumeration, endpoint stalls, DMA errors, missed isochronous TDs, and ring fullness.

## Risks

The biggest risk is tracepoint cost and safety. `cdns2_ring` copies `TR_SEG_SIZE`, which with 600 TRBs plus ISO reserve is a sizable trace payload; enabling it heavily can perturb timing or flood buffers. Trace events that dereference request, endpoint, descriptor, or ring pointers assume valid objects at the call site. Events that read MMIO in `TP_fast_assign` can observe racing hardware state and must not be mistaken for an atomic transaction log. Format strings expose kernel pointers as diagnostic fields, which is normal for kernel tracing but subject to pointer restrictions in output.

## Test Signals

Build tests should catch trace generation mistakes. Runtime validation should enable individual events and confirm expected output during pullup, EP0 setup, request enqueue/dequeue/giveback, endpoint halt, DMA interrupt, and TRB completion paths. For ring events, a useful signal is coherent enqueue/dequeue/cycle output from `cdns2_raw_ring()` around ring-full or ISO error scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/core.c

## Purpose

`core.c` implements the Linux USB Device Controller core framework. It is the shared mediation layer between gadget function drivers and hardware-specific UDC drivers. It exports endpoint APIs (`usb_ep_*`), gadget APIs (`usb_gadget_*`), DMA mapping helpers, request giveback, endpoint matching, UDC registration/removal, gadget-driver registration, driver binding/unbinding, sysfs attributes, uevents, and the `gadget` bus used to match gadget drivers to available UDCs.

## Important APIs, Types, And Functions

The central private type is `struct usb_udc`, which binds a `usb_gadget`, optional `usb_gadget_driver`, class device, list node, VBUS status, started state, connect permission, VBUS work item, and `connect_lock`. `udc_list` tracks registered UDCs under `udc_lock`, and `gadget_id_numbers` assigns gadget device IDs.

Endpoint exports validate and delegate to endpoint ops: `usb_ep_set_maxpacket_limit()`, `usb_ep_enable()`, `usb_ep_disable()`, `usb_ep_alloc_request()`, `usb_ep_free_request()`, `usb_ep_queue()`, `usb_ep_dequeue()`, `usb_ep_set_halt()`, `usb_ep_clear_halt()`, `usb_ep_set_wedge()`, `usb_ep_fifo_status()`, and `usb_ep_fifo_flush()`. Gadget exports similarly delegate to gadget ops for frame number, wakeup, remote wakeup, self-powered status, VBUS session/draw, connect/disconnect, deactivate/activate, and state changes.

DMA helpers `usb_gadget_map_request_by_dev()`, `usb_gadget_map_request()`, `usb_gadget_unmap_request_by_dev()`, and `usb_gadget_unmap_request()` map either SG lists or linear buffers and reject vmalloc/stack buffers for linear DMA. `usb_gadget_giveback_request()` calls the request completion callback and emits USB LED activity on successful completions. `usb_gadget_ep_match_desc()` is the endpoint autoconfiguration predicate checking claim state, direction, maxpacket, transfer type, high-bandwidth constraints, and SuperSpeed streams.

UDC lifecycle APIs include `usb_initialize_gadget()`, `usb_add_gadget()`, `usb_add_gadget_udc_release()`, `usb_add_gadget_udc()`, `usb_del_gadget()`, `usb_del_gadget_udc()`, and `usb_get_gadget_udc_name()`. Gadget driver APIs are `usb_gadget_register_driver_owner()` and `usb_gadget_unregister_driver()`.

## Control Flow

UDC hardware drivers initialize a `usb_gadget` and call `usb_add_gadget_udc*()`. The core allocates `struct usb_udc`, creates a UDC class device, links the gadget device, assigns a gadget ID, adds the gadget to the `gadget` bus, creates a sysfs link, and sets initial state to `USB_STATE_NOTATTACHED`.

Gadget drivers register as drivers on the `gadget` bus. `gadget_match_driver()` requires an optional `udc_name` match and rejects already-bound drivers. `gadget_bind_driver()` marks the driver bound under `udc_lock`, stores it in the UDC, sets maximum speed, calls the gadget driver's `bind()`, starts the hardware through `udc_start`, enables async callbacks, allows connection, and applies VBUS-driven connect control. Error paths unwind in reverse: disable callbacks, synchronize IRQ if present, stop UDC, unbind, and clear binding state.

Unbind flow (`gadget_unbind_driver()`) prevents new connects, cancels VBUS work, disconnects pullup, disables async callbacks, synchronizes IRQ, calls gadget `unbind()`, stops the UDC, clears binding state, and emits a uevent. VBUS changes from UDC drivers go through `usb_udc_vbus_handler()`, which records status and schedules work because pullup and disconnect callbacks may sleep or need mutexes.

## State And Persistence

State is in memory and sysfs only. `usb_udc.started`, `allow_connect`, `vbus`, `gadget->connected`, and `gadget->deactivated` determine whether pullup calls actually reach hardware or are just remembered for later activation. `connect_lock` serializes start/stop/pullup/deactivate transitions, while `udc_lock` serializes the global UDC list and binding pointers. Gadget state changes are protected by `gadget->state_lock` and reported asynchronously by `usb_gadget_state_work()` through sysfs `state` notification.

The class exposes sysfs attributes `srp`, `soft_connect`, `state`, `function`, `current_speed`, `maximum_speed`, and several OTG/selfpowered flags. Uevents include `USB_UDC_NAME` and, when bound, `USB_UDC_DRIVER`.

## Dependencies And Integration Points

This file is a core kernel subsystem component. It depends on device model classes, buses, IDA, DMA mapping, workqueues, USB gadget structures, and UDC tracepoints from `trace.h`. UDC drivers integrate by providing `usb_ep_ops` and `usb_gadget_ops`, especially `udc_start`, `udc_stop`, optional `pullup`, speed-setting, async callback gating, wakeup, and VBUS operations. Gadget function drivers integrate by registering `struct usb_gadget_driver` with `bind`, `setup`, `unbind`, and optional suspend/resume/disconnect/reset callbacks.

## Risks

The main risks are concurrency and callback ordering. The code intentionally separates `udc_lock` and `connect_lock`; violating that ordering in UDC or gadget drivers can deadlock. Request completion callbacks must not be called from `usb_ep_queue()`, and UDC drivers must honor async callback disablement during unbind. `soft_connect_store()` invokes start/stop manually and can expose UDC-driver assumptions about idempotency. DMA mapping rejects non-DMA-capable buffers, so gadget drivers relying on stack or vmalloc buffers fail at map time. The `USB_UDC_ATTR` macro uses integer formatting for boolean-ish gadget fields; changes to field types would need care.

## Test Signals

Core tests should cover UDC registration/removal, binding by explicit `udc_name`, failed bind unwinding, VBUS connect/disconnect work, deactivate/activate preserving desired connection state, endpoint autoconfig matching, DMA mapping failure for invalid buffers, request giveback callback execution, sysfs `soft_connect`, and unbind with async callbacks disabled. Runtime signs include correct `/sys/class/udc` entries, `state` notifications, uevents on bind/unbind, and no callbacks after gadget unbind except permitted request completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/dummy_hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/dummy_hcd.c

## Purpose

`dummy_hcd.c` implements the Linux dummy USB host plus gadget emulator. It creates paired platform devices: a host-controller side (`dummy_hcd`) visible to USB host drivers and a gadget-controller side (`dummy_udc`) visible to gadget function drivers. USB traffic is simulated in software, allowing gadget and host code to be developed and tested without physical USB hardware. The file explicitly does not support isochronous transfers.

## Important APIs, Types, And Functions

The module parameters are `is_super_speed`, `is_high_speed`, and `num`, selecting emulated speed capabilities and number of controller pairs. `struct dummy` is the shared state object containing the gadget endpoints, address, callback usage count, gadget object, current gadget driver, small FIFO request, device status, interrupt/callback flags, pullup/suspend state, and pointers to high-speed and SuperSpeed HCD objects. `struct dummy_hcd` stores root-hub state, hrtimer, port status, active/resume state, current emulated device, queued URBs, and SuperSpeed stream configuration. `struct dummy_ep`, `struct dummy_request`, and `struct urbp` represent gadget endpoints, gadget requests, and host URB wrappers.

The gadget-side endpoint ops are `dummy_enable()`, `dummy_disable()`, `dummy_alloc_request()`, `dummy_free_request()`, `dummy_queue()`, `dummy_dequeue()`, `dummy_set_halt()`, and `dummy_set_wedge()`. Gadget ops include `dummy_g_get_frame()`, `dummy_wakeup()`, `dummy_set_selfpowered()`, `dummy_pullup()`, `dummy_udc_start()`, `dummy_udc_stop()`, `dummy_udc_set_speed()`, and `dummy_udc_async_callbacks()`. Host-side HCD ops include `dummy_urb_enqueue()`, `dummy_urb_dequeue()`, `dummy_hub_status()`, `dummy_hub_control()`, `dummy_bus_suspend()`, `dummy_bus_resume()`, `dummy_alloc_streams()`, and `dummy_free_streams()`.

The module lifecycle is `dummy_hcd_init()` and `dummy_hcd_cleanup()`, with platform drivers for both UDC and HCD sides. `dummy_hcd_probe()` creates and registers USB2 and optional shared USB3 HCDs; `dummy_udc_probe()` initializes and registers the gadget with UDC core.

## Control Flow

Initialization allocates `num` HCD and UDC platform devices, one shared `struct dummy` per pair, registers HCD and UDC platform drivers, adds HCD devices first, verifies their probe created required HCD state, then adds UDC devices. UDC probe clears and initializes the embedded gadget, builds a list of fixed and configurable endpoints, sets max speed from module parameters, initializes EP0, and calls `usb_add_gadget_udc()`.

When a gadget driver binds, UDC core calls `dummy_udc_start()` to store the driver and reset device status. Pullup changes go through `dummy_pullup()`, which updates `dum->pullup`, recalculates root-hub port state with `set_link_state()`, and polls root-hub status. Root-hub control requests power, reset, suspend, resume, and query the single emulated port. Port reset eventually sets enable and speed bits if pullup is active.

Host URBs are wrapped in `struct urbp`, linked to the HCD endpoint, appended to `urbp_list`, and processed by `dummy_timer()` at microframe-like intervals. The timer scans queued URBs, finds the matching gadget endpoint, handles EP0 setup packets, then uses `transfer()` to copy bytes between host URB buffers/SG lists and gadget request buffers. Gadget request completion uses `usb_gadget_giveback_request()`, and host completion uses `usb_hcd_giveback_urb()`.

## State And Persistence

All state is in memory. `port_status`, `old_status`, `active`, `old_active`, `resuming`, and `rh_state` emulate root-hub state transitions. `dum->devstatus` tracks standard device features such as self-powered, remote wakeup, HNP, U1/U2/LTM. Endpoint state tracks descriptors, halted/wedged flags, stream enablement, setup stage, request queues, and last I/O time. `callback_usage` plus `ints_enabled` emulates interrupt callback quiescing so unbind can wait for callbacks to finish.

The hrtimer is the transfer scheduler. It persists while URBs are queued and is cancelled on HCD stop. The `urbs` sysfs attribute exposes queued URBs for diagnostics.

## Dependencies And Integration Points

The file integrates with both the USB gadget core and USB HCD framework. It uses `usb_add_gadget_udc()`, `usb_gadget_udc_reset()`, gadget endpoint ops, `usb_create_hcd()`, `usb_add_hcd()`, `usb_hcd_link_urb_to_ep()`, `usb_hcd_giveback_urb()`, root-hub polling, and platform driver/device APIs. It also supports SuperSpeed streams through HCD stream allocation and endpoint companion descriptors, though max streams are stored compactly in nibbles and limited to 16.

## Risks

This emulator is intentionally approximate. Isochronous transfers always fail. Interrupt timing is not accurate and may poll too fast. Bandwidth accounting is simplified and omits transaction overhead. It uses one shared spinlock across gadget and host state and deliberately drops it around callbacks, so rescan/restart logic is needed to handle queues changing under callbacks. The small single-request FIFO optimization completes some IN gadget requests immediately by copying to `fifo_buf`, which can expose ordering differences from real hardware. Root-hub and link-state emulation must keep USB2/USB3 speed compatibility straight; mismatches suppress connection. Error paths in multi-device init must unwind arrays carefully.

## Test Signals

Useful tests include loading with different speed parameters and `num` values, verifying UDC and root hub creation, binding common gadget functions, enumerating from the host side, exercising control requests handled locally (`SET_ADDRESS`, `GET_STATUS`, feature set/clear), bulk/interrupt IN and OUT transfers, endpoint halt/wedge behavior, URB unlink, scatterlist transfers, SuperSpeed stream allocation/validation, suspend/resume and remote wakeup, and module unload after active queues. The key success signal is that both host-side URBs and gadget requests complete exactly once with expected statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/dummy_hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_qe_udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_qe_udc.c

## Purpose

`fsl_qe_udc.c` is the Freescale QE/CPM USB peripheral controller driver for SoCs such as MPC8360, MPC8323, and MPC8272. It implements a four-endpoint USB gadget UDC using QE/CPM parameter RAM, buffer descriptor rings, controller registers, tasklets, and interrupts. It registers with the generic UDC core and exposes the standard gadget endpoint and controller operations.

## Important APIs, Types, And Functions

The implementation uses types from `fsl_qe_udc.h`: `struct qe_udc`, `struct qe_ep`, `struct qe_req`, and `struct qe_frame`. The endpoint ops are `qe_ep_enable()`, `qe_ep_disable()`, `qe_alloc_request()`, `qe_free_request()`, `qe_ep_queue()`, `qe_ep_dequeue()`, and `qe_ep_set_halt()`. Gadget ops are `qe_get_frame()`, `fsl_qe_start()`, and `fsl_qe_stop()`.

Low-level hardware helpers include `qe_eprx_stall_change()`, `qe_eptx_stall_change()`, `qe_eprx_nack()`, `qe_eprx_normal()`, `qe_ep_cmd_stoptx()`, `qe_ep_cmd_restarttx()`, `qe_ep_flushtxfifo()`, `qe_ep_filltxfifo()`, `qe_epbds_reset()`, `qe_ep_reset()`, `qe_ep_bd_init()`, `qe_ep_rxbd_update()`, and `qe_ep_register_init()`. Transfer helpers include `qe_ep0_rx()`, `qe_ep_rxframe_handle()`, `ep_rx_tasklet()`, `qe_ep_rx()`, `qe_ep_tx()`, `txcomplete()`, `qe_usb_senddata()`, `sendnulldata()`, `frame_create_tx()`, `ep0_prime_status()`, `ep0_req_complete()`, `qe_ep0_txconf()`, `qe_ep_txconf()`, `ep_req_send()`, `ep_req_rx()`, and `ep_req_receive()`.

Chapter 9 helpers include `setup_received_handle()`, `ch9setaddress()`, and `ch9getstatus()`. Interrupt handlers are split into `idle_irq()`, `reset_irq()`, `tx_irq()`, `rx_irq()`, `bsy_irq()`, `txe_irq()`, with `qe_udc_irq()` as the registered ISR. Platform lifecycle is handled by `qe_udc_probe()`, `qe_udc_remove()`, `qe_udc_config()`, `qe_udc_reg_init()`, `qe_ep_config()`, and `qe_udc_release()`.

## Control Flow

Probe first requires device-tree property `mode = "peripheral"`. `qe_udc_config()` allocates `struct qe_udc`, maps USB parameter RAM from the second address resource, allocates endpoint parameter blocks in MURAM, initializes lock and USB state, and returns the controller object. Probe then records QE vs CPM match data, maps controller registers, initializes registers, configures gadget fields, initializes four endpoint objects, initializes EP0 with a control descriptor, allocates ZLP and GET_STATUS buffers, maps the null buffer for DMA if needed, sets up the RX tasklet, maps and requests the IRQ, and registers the gadget with `usb_add_gadget_udc_release()`.

When a gadget driver binds, `fsl_qe_start()` stores the driver, sets gadget speed from the driver maximum, enables the controller, clears event bits, enables default interrupts, and moves state to attached/EP0 wait-for-setup. Stop disables the controller, resets state, nukes EP0 and all enabled endpoint queues, and clears the driver pointer.

Endpoint enable validates descriptor type, transfer type, speed/maxpacket constraints, direction, and endpoint naming. It allocates RX/TX BD rings in MURAM, allocates RX frame/buffer resources for OUT/control endpoints, allocates TX frame state for IN/control endpoints, initializes endpoint registers, and leaves hardware NAKing until requests are queued.

Requests are queued under `udc->lock`. `__qe_ep_queue()` validates completion/buffer/list state, maps or syncs DMA, marks the request in progress, appends it to the endpoint queue, then starts immediate send or receive handling depending on direction. IN endpoints keep one active `tx_req` and send up to maxpacket per frame. OUT endpoints either un-NACK or drain existing RX BDs. EP0 updates `ep0_state` to transmit or receive for data phases.

The IRQ path reads `usb_usber & usb_usbmr`, acknowledges bits, and handles idle, TX complete, RX, reset, busy, and TX error events. RX for non-EP0 may schedule `ep_rx_tasklet()` to copy completed RX BDs into queued requests outside the hard IRQ path. TX confirmation recycles completed TX BDs, handles errors by flushing/retrying with restored data toggle, completes requests when sent, and primes the next packet. Reset disables USB, clears address, resets initialized endpoints, resets queues, notifies the gadget driver through `usb_gadget_udc_reset()`, and re-enables USB.

## State And Persistence

The driver maintains controller state in `qe_udc`: USB state, resume state, EP0 state/direction, device address pending write, MURAM parameter pointers, endpoint objects, RX tasklet, IRQ, and DMA buffers. Endpoint state includes BD ring bases/current pointers, RX/TX frames, RX data buffers, active TX request, data toggle, queue, NACK/stall state, local NACK, and queued RX data count. State is volatile and reconstructed on probe or endpoint enable; MURAM allocations are freed on endpoint disable, EP0 cleanup, device release, or probe failure.

EP0 is a state machine with `WAIT_FOR_SETUP`, `DATA_STATE_XMIT`, `DATA_STATE_NEED_ZLP`, `WAIT_FOR_OUT_STATUS`, and `DATA_STATE_RECV`. Standard GET_STATUS, SET_ADDRESS, and endpoint feature set/clear can be handled locally. Other setup requests are passed to the gadget driver's `setup()` callback after setting EP0 direction and state.

## Dependencies And Integration Points

This driver depends on the generic UDC core, Linux DMA mapping, device tree, platform drivers, IRQ APIs, QE/CPM command APIs (`qe_issue_cmd()`, `cpm_command()`), MURAM allocation (`cpm_muram_alloc()`, `cpm_muram_addr()`, `cpm_muram_free()`), and big-endian register/BD accessors. It matches `fsl,mpc8323-qe-usb`, `fsl,mpc8360-qe-usb`, and `fsl,mpc8272-cpm-usb`, with match data selecting QE or CPM command paths.

## Risks

The code is highly hardware-specific and has several subtle risk areas. It uses `virt_to_phys()` first and falls back to DMA mapping only when the result equals `DMA_ADDR_INVALID`, which is unusual on modern DMA/IOMMU systems. RX buffers are allocated with `kzalloc()` and manually aligned by pointer arithmetic for BD buffer addresses. Request queueing has a local `reval` variable that is not returned to callers in all paths; transfer-start errors may be hidden. EP0 control flow drops and reacquires `udc->lock` around gadget callbacks and halt changes, so queue state must be revalidated afterward. Some paths use `GFP_ATOMIC` allocations during endpoint initialization under lock. Suspend/resume return `-ENOTSUPP` under PM. Error handling must free MURAM, DMA mappings, frames, IRQs, tasklets, and gadget references in the right order.

## Test Signals

Key tests are device-tree probe with each compatible string, UDC registration, EP0 enumeration through SET_ADDRESS and GET_STATUS, endpoint enable/disable for bulk/interrupt/iso descriptors at valid and invalid maxpacket sizes, IN transfers including ZLP requests, OUT transfers under RX BD pressure and local NACK recovery, endpoint halt/clear-halt, bus reset recovery, suspend/resume IRQ callbacks, TX underrun/timeout retry behavior, and remove/probe-failure cleanup. Hardware-level signals include stable BD ring pointers, no stuck `T_R` or `R_E` ownership bits, correct `usb_usber` acknowledgment, and no leaked MURAM allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_qe_udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_qe_udc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_qe_udc.h

## Purpose

`fsl_qe_udc.h` is the private hardware and state header for the Freescale QE/CPM USB device controller driver. It defines controller register bits, endpoint parameter RAM layouts, frame metadata, request/endpoint/controller structures, EP0 state constants, transfer modes, and QE/CPM buffer descriptor status bits used by `fsl_qe_udc.c`.

## Important APIs, Types, And Constants

Top-level constants describe hardware capabilities and allocation sizes: `USB_MAX_ENDPOINTS` is 4, EP0 max packet is 64, `USB_MAX_CTRL_PAYLOAD` is 0x4000, RX rings can have 256 BDs, TX rings 16 BDs, and `MIN_EMPTY_BDS` controls RX NACK pressure. `PORT_CPM` and `PORT_QE` select command paths. Register masks cover USB mode (`USB_MODE_EN`, `USB_MODE_HOST`, `USB_MODE_RESUME`), endpoint register fields (`USB_EPNUM_MASK`, `USB_TRANS_*`, `USB_THS_*`, `USB_RHS_*`), command register bits (`USB_CMD_STR_FIFO`, `USB_CMD_FLUSH_FIFO`), event/mask bits (`USB_E_RESET_MASK`, `USB_E_IDLE_MASK`, `USB_E_TXB_MASK`, `USB_E_RXB_MASK`, `USB_E_TXE_MASK`), frame number masks, and bus mode fields.

`struct usb_device_para` and `struct usb_ep_para` model QE/CPM USB parameter RAM. They hold endpoint parameter pointers, RX/TX state, frame counters, BD bases/pointers, max receive buffer length, CRC/temp fields, and transaction counters. `struct qe_frame` is the driver's abstract RX/TX frame with data pointer, length, status, info flags, private data, and list node. Inline helpers `qe_frame_clean()` and `qe_frame_init()` reset it.

`struct qe_req` wraps `struct usb_request` with a queue node, owning endpoint pointer, and mapped flag. `struct qe_ep` wraps `struct usb_ep` and stores queue, controller/gadget pointers, endpoint state, RX/TX BD ring pointers, RX/TX frames and buffers, active TX request accounting, direction, transfer mode, data toggle, tasklet/setup flags, DMA metadata, local NACK state, and endpoint name. `struct qe_udc` stores the gadget object, gadget driver, device pointer, endpoint array, EP0 setup buffer, spinlock, SoC type, parameter RAM pointers, USB state, EP0 state/direction, temporary/status/null buffers, IRQ/register pointers, RX tasklet, and removal completion.

Buffer descriptor flags define ownership, wrap, interrupt, last, CRC, PID, and error bits for TX (`T_R`, `T_W`, `T_I`, `T_L`, `T_TC`, `T_PID_DATA0`, `T_PID_DATA1`, `DEVICE_T_ERROR`) and RX (`R_E`, `R_W`, `R_I`, `R_L`, `R_F`, `R_PID_SETUP`, `R_ERROR`). CPM command constants define stop/restart transmit opcodes.

## Control Flow And State

This header defines the state machine used by the C file. EP0 progresses through `WAIT_FOR_SETUP`, `DATA_STATE_XMIT`, `DATA_STATE_NEED_ZLP`, `WAIT_FOR_OUT_STATUS`, and `DATA_STATE_RECV`. Endpoint state is tracked as idle, NACK, or stall. RX/TX data toggle is stored in `qe_ep.data01` and converted into PID bits in BDs and frame info. Request queue state lives in `qe_ep.queue`, while one active IN request can be tracked as `qe_ep.tx_req` with `sent` and `last` counters.

Persistence is volatile. BD rings and endpoint parameter RAM reside in QE/CPM MURAM for the lifetime of the endpoint/controller setup. `qe_udc` owns cleanup coordination with `done`, but no state is durable across driver unload or hardware reset.

## Dependencies And Integration Points

The header depends on Linux USB gadget types, list heads, DMA addresses, timer/tasklet-capable kernel infrastructure, and QE/CPM BD definitions from included architecture headers in the C file. It is tightly coupled to `struct usb_ctlr` register layout from the Freescale QE/CPM platform headers. The generic UDC core sees only `struct usb_gadget`, `struct usb_ep`, and `struct usb_request`; all other types are private to this driver.

## Risks

Risks center on bit-level hardware correctness. BD status words overlay status and length fields, so masks must match the platform definition. RX buffer sizing includes CRC and alignment slop; changing maxpacket or ring length without matching allocation logic can corrupt memory or produce bad DMA. `ep_index()` assumes `ep.desc` exists, so callers must not use it on unconfigured endpoints except EP0 paths that account for it. `ep_is_in()` treats EP0 direction specially via `udc->ep0_dir`, making EP0 direction state critical for DMA mapping and completion. The structures mirror parameter RAM and hardware behavior, so padding or type changes can break the driver.

## Test Signals

Compile-time tests catch missing platform definitions. Runtime signals include correct EP0 setup parsing, data toggle progression, RX NACK/normal transitions, TX and RX BD ownership cycling, endpoint halt state reflected in `usb_usep`, and clean allocation/free of MURAM parameter blocks and BD rings. Stress tests should watch for ring wrap handling, RX BD exhaustion below `MIN_EMPTY_BDS`, and correct request completion statuses after reset or dequeue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_qe_udc.h -->
