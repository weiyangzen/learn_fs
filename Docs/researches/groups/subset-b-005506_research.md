# subset-b-005506 Research

Grouped source research for USB gadget UDC drivers and tracing support. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/snps_udc_core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/snps_udc_core.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/snps_udc_core.c` is the core implementation for a Synopsys USB device controller derived from the AMD Geode 5536 UDC driver and reused by PCI or SoC-integrated instances. It exposes the Linux USB gadget UDC surface, programs endpoint and device registers, manages FIFO or DMA transfers, handles EP0 control traffic, and dispatches endpoint/device interrupts. The source was read as a complete 3192-line file for this report.

## Important APIs, Types, and Functions

The exported integration functions are `udc_probe`, `udc_remove`, `udc_irq`, `udc_basic_init`, `udc_mask_unused_interrupts`, `udc_enable_dev_setup_interrupts`, `empty_req_queue`, `init_dma_pools`, `free_dma_pools`, and `gadget_release`. Gadget endpoint operations are implemented through `udc_ep_ops`: `udc_ep_enable`, `udc_ep_disable`, `udc_alloc_request`, `udc_free_request`, `udc_queue`, `udc_dequeue`, and `udc_set_halt`. Gadget device operations are `udc_wakeup`, `udc_get_frame`, `amd5536_udc_start`, and `amd5536_udc_stop`.

Important internal flows include DMA descriptor construction in `udc_create_dma_chain` and `prep_dma`, request completion in `complete_req`, FIFO helpers `udc_txfifo_write` and `udc_rxfifo_read`, control endpoint setup in `activate_control_endpoints` and `setup_ep0`, timer callbacks `udc_timer_function` and `udc_pollstall_timer_function`, and ISR handlers `udc_data_out_isr`, `udc_data_in_isr`, `udc_control_out_isr`, `udc_control_in_isr`, and `udc_dev_isr`. The file depends heavily on types and register macros from `amd5536udc.h`, including `struct udc`, `struct udc_ep`, `struct udc_request`, `struct udc_data_dma`, and `union udc_setup_data`.

## Control Flow

Platform or PCI glue allocates and maps a `struct udc`, then calls `udc_probe`. `udc_probe` installs `udc_ops`, names the gadget, calls `startup_registers`, registers with `usb_add_gadget_udc_release`, initializes timers, sets soft-disconnect, and prints register mode state. `startup_registers` soft-resets the controller, masks interrupts, initializes the gadget context, wires endpoint structures, and chooses high-speed or full-speed operation.

When a gadget function binds, `amd5536_udc_start` stores the gadget driver, shares EP0 driver data between EP0 IN and OUT, activates EP0, clears soft-disconnect, and connects the device. Endpoint enable programs hardware type, max-packet, FIFO sizing, CSR endpoint fields, interrupt masks, and NAK state. Request queueing maps DMA when enabled, initializes request status, prepares FIFO or DMA descriptors, writes descriptor pointers, opens RX DMA when safe, and appends requests to the endpoint queue.

Interrupt flow is split between endpoint and device status registers. `udc_irq` holds `dev->lock`, dispatches EP0 OUT/IN interrupts first, iterates data endpoints, clears per-endpoint interrupt status, then clears and dispatches global device interrupts. Data IN handles FIFO pushes or DMA TDC completions; data OUT handles FIFO reads, DMA completion accounting, BNA recovery, and RX DMA rearming. EP0 OUT decodes SETUP versus data packets, reads the setup packet from DMA setup memory or FIFO, selects the active EP0 direction, calls `driver->setup`, then ACKs, stalls, or waits for a ZLP. Device interrupts synthesize `USB_REQ_SET_CONFIGURATION` and `USB_REQ_SET_INTERFACE` for requests partly handled by hardware, reset and reinitialize on USB reset and enumeration, call gadget suspend/resume hooks, and disconnect on session-valid loss.

## State and Persistence Behavior

State is volatile kernel and hardware state only. A file-global `udc` pointer is used by timers and some helper paths; global spinlocks protect reset and stall polling; global variables track pending CNAK bits, RX FIFO pending data, soft-reset workarounds, timer stop flags, and shared RX DMA enable state. Per-device state tracks gadget binding, current configuration/interface/alternate setting, EP queues, EP0 handshakes, speed, connection state, DMA pools, and mapped register bases.

No file-backed persistence exists. Persistent effects are hardware register programming, DMA descriptors allocated from DMA pools, and gadget core state exposed through `usb_gadget_set_state` or gadget callbacks. Timers are stopped and deleted in `udc_remove`; DMA pools are created and destroyed by the platform glue through exported helpers.

## Dependencies and Integration Points

The file integrates with the Linux USB gadget core (`usb_add_gadget_udc_release`, `usb_gadget_giveback_request`, `usb_gadget_udc_reset`, request map/unmap helpers), Linux DMA pool APIs, timers, spinlocks, interrupts, and MMIO accessors. Its primary local contract is `amd5536udc.h`, which defines register layouts, endpoint indexes, descriptor formats, module parameters such as `use_dma`, and SoC revision constants. `snps_udc_plat.c` supplies platform resource mapping, PHY/extcon handling, IRQ registration, and calls into these exported core routines.

## Risks and Edge Cases

The controller has a single global RX DMA enable bit for all OUT endpoints; the `set_rde` timer and BNA dummy descriptors are workarounds to avoid blocking control traffic while data OUT descriptors are absent. This is race-sensitive and depends on lock, timer, and FIFO-empty ordering. DMA modes have multiple variants (`PPB`, `PPBDU`, buffer-fill) with different byte accounting and descriptor-chain behavior; off-by-one ring or chain errors can corrupt transfer completion. EP0 control flow mixes hardware-handled requests, synthesized setup callbacks, ZLP ACK tracking, and stall handling, so descriptor/state drift can break enumeration. Some paths use global `udc` rather than the local `dev`, making multi-controller assumptions fragile. Remove and suspend paths must stop timers before memory disappears. Error paths around BNA, host errors, pending CNAK, and `udc_dequeue` cancellation are especially hardware-dependent.

## Test Signals

Useful test signals include successful build with `CONFIG_USB_GADGET` and the Synopsys/AMD UDC options, probe/remove on Broadcom-compatible platform glue, enumeration at full and high speed, EP0 standard request coverage, gadget function bind/unbind with queue draining, bulk IN/OUT transfer tests in FIFO and DMA modes, mass-storage reset and halt/clear-halt behavior, disconnect/session-valid transitions, suspend/resume callbacks, interrupt storm/regression checks, and DMA sanitizers or IOMMU faults during chained large requests and short-packet completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/snps_udc_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/snps_udc_plat.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/snps_udc_plat.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/snps_udc_plat.c` is the platform-device wrapper for the Synopsys UDC core. It allocates the UDC instance, maps MMIO resources, acquires IRQ and PHY resources from device tree, optionally tracks USB cable/device-mode state through extcon, creates DMA pools, registers the common core with the gadget framework, and handles remove and system sleep. The source was read as a complete 325-line file for this report.

## Important APIs, Types, and Functions

The main platform callbacks are `udc_plat_probe`, `udc_plat_remove`, `udc_plat_suspend`, and `udc_plat_resume`. The platform driver is `udc_plat_driver`, matched by `of_udc_match` entries `brcm,ns2-udc`, `brcm,cygnus-udc`, and `brcm,iproc-udc`. Role and cable helpers are `start_udc`, `stop_udc`, `udc_drd_work`, and `usbd_connect_notify`.

The file calls core functions declared by `amd5536udc.h`: `udc_probe`, `udc_remove`, `udc_irq`, `udc_basic_init`, `udc_enable_dev_setup_interrupts`, `udc_mask_unused_interrupts`, `empty_req_queue`, `init_dma_pools`, and `free_dma_pools`.

## Control Flow

Probe allocates `struct udc` with devres, initializes the spinlock, maps resource 0, derives CSR/device/endpoint/FIFO register windows from the mapped base, parses the IRQ, obtains and powers on the PHY, and optionally registers an extcon notifier for `EXTCON_USB`. If USB is already present, `conn_type` is initialized so delayed work can bring the controller up. When `use_dma` is enabled, DMA pools are initialized before requesting the shared IRQ and calling `udc_probe`.

Extcon notification stores the new connection state in `udc->conn_type` and schedules `udc_drd_work`. The work item calls `start_udc` on device connection, enabling setup interrupts, reinitializing the core, and marking connected. It calls `stop_udc` on disconnect, flushing the RX FIFO, masking interrupts, invoking the gadget driver's `disconnect` callback outside the spinlock, and emptying all endpoint queues.

Remove unregisters the gadget UDC, requires the gadget driver to already be detached, frees DMA pools, calls core remove, powers off/exits the PHY, unregisters extcon, and clears drvdata. Suspend forces `stop_udc`, powers down the PHY, and resume reinitializes and powers the PHY then restarts the UDC if extcon says USB is connected.

## State and Persistence Behavior

The platform file owns platform lifetime state inside `struct udc`: mapped register bases, physical address, IRQ, PHY, extcon device and notifier, delayed DRD work, connection type, and the core's gadget state. It has no file-backed persistence. Hardware state persists only while the device is powered and the PHY is active. Devres owns memory/MMIO/IRQ allocations, while DMA pools and PHY power are explicitly unwound.

## Dependencies and Integration Points

Dependencies include platform bus APIs, Open Firmware address/IRQ parsing, PHY framework, extcon, DMA pools, Linux interrupt handling, and module platform-driver registration. The local integration point is the common Synopsys core in `snps_udc_core.c`; this file supplies hardware resources and lifecycle calls while the core supplies gadget behavior and interrupt handling.

## Risks and Edge Cases

The extcon path has asymmetry risks: some error and remove paths call `extcon_unregister_notifier` based only on `udc->edev`, so no-extcon configurations and probe-defer cleanup need careful validation. Suspend/resume calls `extcon_get_state(udc->edev, EXTCON_USB)` unconditionally under `CONFIG_PM_SLEEP`, which is risky if no extcon property exists. `stop_udc` invokes gadget callbacks while coordinating spinlock-protected queue state, so callback reentrancy and disconnect timing matter. Probe error labels must keep PHY, DMA, and extcon unwind ordering correct.

## Test Signals

Build with platform UDC and Broadcom device-tree compatibles enabled; boot/probe on `brcm,ns2-udc`, `brcm,cygnus-udc`, or `brcm,iproc-udc`; verify IRQ registration and `udc_probe` success; plug/unplug through extcon and confirm start/stop transitions; bind a gadget function and verify disconnect queue draining; test no-extcon device-tree configurations, probe deferral from extcon/PHY, and system suspend/resume with and without a connected cable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/snps_udc_plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/tegra-xudc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/tegra-xudc.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/tegra-xudc.c` implements NVIDIA Tegra XUSB device-mode controller support for the Linux USB gadget framework. It programs Tegra XUSB device registers, endpoint contexts, transfer rings, event rings, PHY role state, SoC-specific link tuning, power domains, runtime PM, and EP0 standard request handling. The source was read as a complete 4095-line file for this report.

## Important APIs, Types, and Functions

Major hardware data structures are `struct tegra_xudc`, `struct tegra_xudc_ep`, `struct tegra_xudc_request`, `struct tegra_xudc_trb`, `struct tegra_xudc_ep_context`, `struct tegra_xudc_soc`, `struct tegra_xudc_setup_packet`, and `struct tegra_xudc_save_regs`. Register and TRB access is wrapped by generated inline readers/writers from `BUILD_EP_CONTEXT_RW` and `BUILD_TRB_RW`, plus helpers like `trb_read_data_ptr`, `trb_write_data_ptr`, `ep_ctx_read_deq_ptr`, and `ep_ctx_write_deq_ptr`.

Gadget endpoint operations are `tegra_xudc_ep_enable`, `tegra_xudc_ep_disable`, `tegra_xudc_ep_alloc_request`, `tegra_xudc_ep_free_request`, `tegra_xudc_ep_queue`, `tegra_xudc_ep_dequeue`, and `tegra_xudc_ep_set_halt`, with special EP0 enable/disable stubs. Gadget device operations are `tegra_xudc_gadget_get_frame`, `tegra_xudc_gadget_wakeup`, `tegra_xudc_gadget_pullup`, `tegra_xudc_gadget_start`, `tegra_xudc_gadget_stop`, `tegra_xudc_gadget_vbus_draw`, and `tegra_xudc_set_selfpowered`.

Important internal subsystems include TRB queueing (`tegra_xudc_queue_one_trb`, `tegra_xudc_queue_trbs`, `tegra_xudc_ep_ring_doorbell`, `tegra_xudc_ep_kick_queue`), dequeue/ring repair (`squeeze_transfer_ring`, `trb_in_request`, `trb_before_request`, `__tegra_xudc_ep_dequeue`), EP0 requests (`tegra_xudc_ep0_standard_req` and its set/get helpers), event dispatch (`tegra_xudc_handle_event`, `tegra_xudc_process_event_ring`, `tegra_xudc_irq`), port state (`tegra_xudc_port_connect`, `tegra_xudc_port_disconnect`, `tegra_xudc_port_reset`, suspend/resume handlers), resource allocation (`tegra_xudc_alloc_eps`, `tegra_xudc_alloc_event_ring`), SoC tuning (`tegra_xudc_device_params_init`), PHY/role handling (`tegra_xudc_phy_get`, `tegra_xudc_update_data_role`), and PM (`tegra_xudc_powergate`, `tegra_xudc_unpowergate`).

## Control Flow

Probe matches SoC data, maps `base`, `fpci`, and optional `ipfs` resources, requests the IRQ, gets clocks/regulators, obtains padctl and PHYs, attaches power domains, initializes PHYs, allocates event rings and endpoint rings, initializes work items and runtime PM, then registers `tegra-xudc` with the gadget core. USB PHY notifiers update `device_mode`; role work powers PHYs on/off and switches UTMI mode between device and none.

When a gadget driver starts, EP0 is enabled, controller interrupts and link-state events are enabled, pullup state is honored, and OTG peripherals are attached. Pullup toggles `CTRL_ENABLE`. Endpoint enable configures an endpoint context from descriptors, resets the transfer ring and link TRB, transitions to configured state when the first non-control endpoint is enabled, reloads/unhalts/unpauses hardware, and temporarily pauses bulk endpoints when enabling isochronous endpoints for bandwidth allocation. Queueing maps the request, computes required TRBs including ZLP handling, fills TRBs up to ring availability, and rings a doorbell. Completion events find the request by TRB range, calculate residual bytes, complete the request, advance EP0 state, and kick later queued work.

EP0 setup events are handled in `tegra_xudc_handle_ep0_event`. If another setup is in progress, the latest setup is queued until a sequence-number error allows it to replace the old transaction. Standard requests for status, address, feature, set-sel, and isoch delay are handled locally; other standard and class/vendor requests are delegated to the gadget driver. EP0 status/data stages are queued through a reserved `ep0_req` and advance `setup_state` in `tegra_xudc_ep0_req_done`.

The IRQ handler checks `ST_IP`, acknowledges it, and drains event-ring TRBs while cycle bits match. Event types dispatch to port-status, transfer, or setup handling. Port status changes drive connect, disconnect, reset, suspend, resume, link-state quirks, VBUS toggles, and completion notification for disconnect. Runtime/system PM saves `CTRL` and `PORTPM`, disables controller/clocks/regulators, and on resume reinitializes FPCI/IPFS, tuning registers, event rings, endpoint context base, and saved registers.

## State and Persistence Behavior

State is volatile controller, DMA, and gadget state. `struct tegra_xudc` owns the active gadget driver, endpoint contexts, event-ring pointers, transfer rings, setup state, device address, self-powered flag, pullup state, enabled endpoint counters, current PHYs, power flags, saved registers, delayed work flags, and disconnect completion. DMA-coherent event rings and endpoint contexts persist across normal operation but are reinitialized after powergate. No disk persistence exists.

## Dependencies and Integration Points

The driver integrates with the Linux USB gadget core, platform bus, OF matching, DMA coherent allocation and DMA pools, IRQ handling, runtime PM, generic power domains, reset/clock/regulator frameworks, Tegra XUSB padctl, generic PHY and USB PHY/OTG notifier APIs, USB role semantics, and kernel workqueues. SoC data selects supplies, clocks, number of PHYs, U1/U2/LPM support, invalid-sequence workaround, port link-state quirks, port reset workaround, SuperSpeed port-speed workaround, and IPFS availability.

## Risks and Edge Cases

TRB ring accounting is high-risk: enqueue/dequeue pointers, cycle state, link TRBs, short packets, ring-full repair, and request cancellation all must stay synchronized with hardware endpoint context. EP0 sequencing is complex because setup packets can arrive while a previous control transfer is active; invalid Tegra210 sequence numbers are explicitly halted. Runtime PM must not powergate while interrupts, role work, or disconnect handling still needs registers. PHY pairing logic relies on padctl companion mapping and optional PHYs. Port-change workarounds toggle VBUS or force link-state transitions and are SoC-specific. Error completions halt endpoints and can leave gadget functions dependent on clear-halt/reset recovery.

## Test Signals

Build with Tegra XUDC, USB gadget, PHY, PM, and OF support; probe on Tegra210/186/194/234 device-tree compatibles; enumerate at high-speed and SuperSpeed; exercise EP0 standard requests including set-address, get-status, U1/U2, remote wake, set-sel, isoch delay, and class/vendor delegation; run bulk, interrupt, isochronous, stream, short-packet, ZLP, dequeue, halt/clear-halt, and disconnect tests; validate runtime suspend/resume and system sleep while disconnected and connected; check VBUS role-switch notifications; and monitor event-ring, endpoint halt, DMA mapping, and power-domain errors under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/tegra-xudc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/trace.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/trace.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/trace.c` is the tracepoint-definition translation unit for USB gadget UDC trace events. It defines `CREATE_TRACE_POINTS` and includes `trace.h`, causing the tracepoint declarations in the header to emit storage and registration code exactly once. The source was read as a complete 10-line file for this report.

## Important APIs, Types, and Functions

This file has no functions or local types. Its important API action is the preprocessor contract `#define CREATE_TRACE_POINTS` followed by `#include "trace.h"`, which is the standard Linux tracing pattern for materializing `DECLARE_EVENT_CLASS` and `DEFINE_EVENT` entries from a trace header.

## Control Flow

There is no runtime control flow authored here. Build-time inclusion expands the trace event definitions; runtime event emission occurs at call sites elsewhere in the USB gadget codebase that include the generated tracepoint hooks.

## State and Persistence Behavior

No driver state or persistent storage is owned here. The generated tracepoint metadata and static keys live in kernel tracing infrastructure after compilation/loading.

## Dependencies and Integration Points

The only direct dependency is local `trace.h`, which itself depends on Linux tracepoint and USB gadget headers. Integration is with ftrace/perf/tracefs consumers and USB gadget framework instrumentation.

## Risks and Edge Cases

The main risk is duplicate or missing tracepoint definition. Only one translation unit may define `CREATE_TRACE_POINTS` for this trace header; omitting it would leave declared tracepoints without generated definitions, while defining it in multiple files would cause duplicate symbols.

## Test Signals

Build and modpost should succeed without duplicate tracepoint symbols. Runtime smoke tests can enable gadget trace events under tracefs and verify gadget, endpoint, and request events are visible when gadget core APIs run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/trace.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/trace.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/trace.h` declares Linux trace events for USB gadget UDC operations. It captures snapshots of `struct usb_gadget`, `struct usb_ep`, and `struct usb_request` state for common gadget, endpoint, and request APIs so failures and state transitions can be observed through kernel tracing. The source was read as a complete 299-line file for this report.

## Important APIs, Types, and Functions

The header sets `TRACE_SYSTEM gadget`, includes Linux tracepoint and USB gadget definitions, and declares three event classes. `udc_log_gadget` records gadget speed, max speed, state, power draw, OTG/HNP flags, quirks, self-powered/deactivated/connected flags, and a return code. It is reused by events such as `usb_gadget_set_state`, `usb_gadget_frame_number`, `usb_gadget_wakeup`, `usb_gadget_set_remote_wakeup`, `usb_gadget_set_selfpowered`, `usb_gadget_clear_selfpowered`, `usb_gadget_vbus_connect`, `usb_gadget_vbus_draw`, `usb_gadget_vbus_disconnect`, `usb_gadget_connect`, `usb_gadget_disconnect`, `usb_gadget_deactivate`, and `usb_gadget_activate`.

`udc_log_ep` records endpoint name, packet limits, streams, mult/burst, address, claimed/enabled flags, and return code. It backs endpoint events such as `usb_ep_set_maxpacket_limit`, `usb_ep_enable`, `usb_ep_disable`, `usb_ep_set_halt`, `usb_ep_clear_halt`, `usb_ep_set_wedge`, `usb_ep_fifo_status`, and `usb_ep_fifo_flush`. `udc_log_req` records endpoint name, request pointer, length/actual, scatter-gather counts, stream id, ZLP/short/no-interrupt flags, request status, and return code for allocation, free, queue, dequeue, and giveback events.

## Control Flow

The header has no ordinary runtime flow. When included normally, it declares tracepoint prototypes and event metadata. When included from `trace.c` with `CREATE_TRACE_POINTS`, the `DECLARE_EVENT_CLASS` and `DEFINE_EVENT` macros instantiate the actual tracepoints. Each event's `TP_fast_assign` copies fields from live gadget/endpoint/request objects into a trace entry, and `TP_printk` formats the stable trace output.

## State and Persistence Behavior

The file defines trace event schemas, not driver state. Trace records are transient and controlled by kernel tracing buffers. The copied fields make each event robust against later mutation of the underlying gadget, endpoint, or request except for the request pointer value intentionally logged for correlation.

## Dependencies and Integration Points

Dependencies include `<linux/types.h>`, `<linux/tracepoint.h>`, `<asm/byteorder.h>`, `<linux/usb/gadget.h>`, and `<trace/define_trace.h>`. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` bind the generated include machinery to this directory and file. The integration point is USB gadget core instrumentation rather than a single UDC driver.

## Risks and Edge Cases

Tracepoint field selection must track `struct usb_gadget`, `struct usb_ep`, and `struct usb_request` layout changes. Format strings need to match field types to avoid misleading trace output. Because events dereference live pointers in `TP_fast_assign`, callers must pass valid gadget, endpoint, and request objects. Include guard and `TRACE_HEADER_MULTI_READ` behavior must remain compatible with Linux trace event generation.

## Test Signals

Build coverage with tracing enabled is the primary signal. Runtime validation can enable `gadget:*` events in tracefs, run gadget bind/connect/endpoint/request operations, and confirm formatted output contains expected speed, state, endpoint, stream, request length, status, and return-code values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/trace.h -->
