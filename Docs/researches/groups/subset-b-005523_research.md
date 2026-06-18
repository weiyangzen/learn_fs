# subset-b-005523 Research

Grouped source research for the MUSB gadget, host, EP0, virtual root hub, register/I/O, trace, Mentor HSDMA, OMAP2430 glue, and Allwinner sunxi glue files. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_gadget.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_gadget.c

## Purpose

`musb_gadget.c` implements the peripheral-side USB gadget controller support for the Mentor MUSB HDRC core. It exposes non-EP0 endpoint operations to Linux gadget drivers, manages endpoint enable/disable, request allocation and queueing, PIO/DMA transfer progression, gadget registration, pullup/wakeup/VBUS operations, and gadget-side bus lifecycle events. The source was read as a complete 2095-line file.

## Important APIs, Types, and Functions

The exported surface is `musb_g_giveback`, `musb_g_tx`, `musb_g_rx`, `musb_alloc_request`, `musb_free_request`, `musb_ep_restart`, `musb_gadget_setup`, `musb_gadget_cleanup`, `musb_g_resume`, `musb_g_suspend`, `musb_g_wakeup`, `musb_g_disconnect`, and `musb_g_reset`. The file defines the non-control `usb_ep_ops` table through `musb_gadget_enable`, `musb_gadget_disable`, `musb_gadget_queue`, `musb_gadget_dequeue`, `musb_gadget_set_halt`, `musb_gadget_set_wedge`, `musb_gadget_fifo_status`, and `musb_gadget_fifo_flush`, plus the `usb_gadget_ops` table through frame, wakeup, self-powered, VBUS draw, pullup, start, and stop callbacks. Transfer helpers include `map_dma_buffer`, `unmap_dma_buffer`, `nuke`, `txstate`, `rxstate`, and `init_peripheral_ep`.

## Control Flow

Gadget setup initializes `musb->g`, enters device mode, builds endpoint objects from `musb->endpoints`, and registers the UDC with `usb_add_gadget_udc`. A gadget function driver starts through `musb_gadget_start`, which binds the transceiver or generic PHY to device mode, marks the controller active, and starts the MUSB core. Endpoint enable validates descriptor direction, endpoint number, maxpacket and high-bandwidth support, programs TXMAXP/RXMAXP and CSR bits, enables endpoint interrupts, and optionally allocates a DMA channel. Queueing maps the buffer if the DMA engine accepts it, links the `musb_request`, and schedules resume work to call `musb_ep_restart`; TX requests call `txstate`, RX requests wait for RXPKTRDY and use `rxstate`. IRQ handlers from the core call `musb_g_tx` and `musb_g_rx`, which finish DMA or PIO segments, handle stalls/underruns/overruns, complete requests with `musb_g_giveback`, and start the next queued request.

## State and Persistence Behavior

State is runtime-only and protected mainly by `musb->lock`: endpoint descriptors, queue lists, DMA channel pointers, endpoint busy/wedged flags, softconnect, `is_active`, suspend state, negotiated speed, HNP flags, and endpoint CSR state. DMA mappings are tracked per `musb_request` with `UN_MAPPED`, `PRE_MAPPED`, or `MUSB_MAPPED` and are synchronized/unmapped before giveback. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on USB gadget core APIs, runtime PM, DMA mapping APIs, MUSB core state (`musb_core.h`), tracepoints (`musb_trace.h`), platform hooks for VBUS/idling, PHY/OTG helpers, and controller register definitions. It integrates with `musb_gadget_ep0.c` through EP0 ops and shared request helpers, with core interrupt dispatch through `musb_g_tx/rx/reset/suspend/resume/disconnect`, and with platform glue through mode, VBUS, and idle hooks.

## Risks and Edge Cases

Risk is concentrated around DMA fallback and CSR sequencing: several paths must clear DMAENAB before DMAMODE, handle double-buffered FIFOs, avoid stale INDEX selection after callbacks release the lock, and recover if DMA programming fails. Queueing maps DMA before taking the main lock, so failures after queue validation must unmap correctly. Endpoint stall clearing can restart queued requests, while wedged endpoints intentionally ignore clear-halt requests. Pullup work and runtime PM introduce asynchronous ordering with gadget driver bind/unbind.

## Test Signals

Useful signals are gadget enumeration with configfs or common gadget functions, bulk IN/OUT stress with and without DMA, short packet and zero-length packet tests, endpoint halt/wedge/clear-halt tests, disconnect during active DMA, runtime PM resume while requests are queued, high-bandwidth ISO descriptor rejection/acceptance, and tracepoint coverage for request enqueue, transfer, and giveback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_gadget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_gadget.h -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_gadget.h

## Purpose

`musb_gadget.h` is the peripheral-side internal interface for MUSB gadget support. It declares gadget IRQ and lifecycle entry points used by the core, defines request and endpoint state containers used by `musb_gadget.c` and `musb_gadget_ep0.c`, and provides no-op stubs when gadget or dual-role support is not built. The source was read as a complete 116-line file.

## Important APIs, Types, and Functions

The header declares `musb_g_ep0_irq`, `musb_g_tx`, `musb_g_rx`, `musb_g_reset`, `musb_g_suspend`, `musb_g_resume`, `musb_g_wakeup`, `musb_g_disconnect`, `musb_gadget_cleanup`, and `musb_gadget_setup` for enabled configurations. It defines `enum buffer_map_state`, `struct musb_request`, `struct musb_ep`, `to_musb_request`, `to_musb_ep`, `next_request`, `musb_alloc_request`, `musb_free_request`, `musb_g_ep0_ops`, `musb_g_giveback`, and `musb_ep_restart`.

## Control Flow

The header has no runtime flow, but it defines the contracts used by the gadget implementation. Core interrupt dispatch calls the declared IRQ/endpoint handlers. Gadget endpoint operations allocate `struct musb_request`, attach them to `struct musb_ep.req_list`, and use `next_request` to find the active request.

## State and Persistence Behavior

`struct musb_request` wraps `struct usb_request` with list membership, owning endpoint/controller pointers, direction, endpoint number, and DMA mapping state. `struct musb_ep` stores the Linux `usb_ep`, hardware endpoint backlink, descriptor/type/maxpacket, DMA channel, request list, wedge state, busy flag, and high-bandwidth multiplier. All state is in-memory controller state.

## Dependencies and Integration Points

The header depends on Linux list support and USB gadget/core types included by surrounding MUSB headers. It integrates with `musb_gadget.c`, `musb_gadget_ep0.c`, and `musb_core.h`; the stubs let host-only builds compile without gadget code.

## Risks and Edge Cases

The main risks are structure contract drift between EP0 and non-EP0 gadget code, misuse of `busy` semantics during callbacks, and incorrect assumptions around shared FIFO endpoints where one `musb_hw_ep` may expose bidirectional gadget capabilities.

## Test Signals

Build matrix coverage for gadget-only, host-only, and dual-role configurations is the key signal. Runtime tests should confirm request allocation/free, EP0 and non-EP0 queue progression, and correct no-op behavior in host-only builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_gadget.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_gadget_ep0.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_gadget_ep0.c

## Purpose

`musb_gadget_ep0.c` implements peripheral-mode endpoint zero control transfer handling for MUSB. It services standard USB requests that the controller driver must handle itself, forwards class/vendor or configuration requests to the gadget driver, drives the EP0 state machine, queues the gadget driver's EP0 response buffers, and exposes `musb_g_ep0_ops`. The source was read as a complete 1058-line file.

## Important APIs, Types, and Functions

The externally used entry point is `musb_g_ep0_irq`, and the exported operation table is `musb_g_ep0_ops`. Important helpers are `decode_ep0stage`, `service_tx_status_request`, `service_in_request`, `service_zero_data_request`, `musb_g_ep0_giveback`, `musb_try_b_hnp_enable`, `ep0_rxstate`, `ep0_txstate`, `musb_read_setup`, `forward_to_driver`, `musb_g_ep0_queue`, and `musb_g_ep0_halt`.

## Control Flow

The core calls `musb_g_ep0_irq` when EP0 interrupts arrive. The handler selects EP0, reads CSR0 and COUNT0, acknowledges sent stalls and SETUPEND, then dispatches based on `musb->ep0_state`. In setup state it reads an eight-byte `usb_ctrlrequest`, clears any previous queued EP0 request, sets `ackpend`, decides whether the request has no data, IN data, or OUT data, and handles mandatory standard requests locally where possible. Unhandled requests are forwarded to `gadget_driver->setup` with the controller lock dropped. For IN data, `musb_g_ep0_queue` can immediately call `ep0_txstate` to load the FIFO; for OUT data, the queued buffer is filled by `ep0_rxstate`. Status phases update address/test-mode state, complete any remaining request, and return to idle/setup.

## State and Persistence Behavior

EP0 state lives in `musb->ep0_state`, `ackpend`, `set_address`, `address`, `test_mode`, `test_mode_nr`, wakeup/HNP flags, and the EP0 request list (`musb->endpoints[0].ep_in`). The controller lock protects both queue and state except during gadget driver callbacks. There is no persistent storage.

## Dependencies and Integration Points

The file depends on USB control request definitions, gadget driver setup callbacks, MUSB CSR0/FADDR/TESTMODE registers, `musb_g_giveback` and `musb_ep_restart` from gadget support, FIFO helpers, OTG/HNP state, and EP0 stage constants from `musb_core.h`. It is tightly integrated with `musb_gadget.c` for request allocation and completion.

## Risks and Edge Cases

The delicate areas are correct delayed acknowledgement through `ackpend`, handling setup/status coalescing, preventing address changes until after status, not accepting OUT data without a driver-provided buffer, and allowing callbacks to stall while the lock is temporarily dropped. Test mode and HNP feature requests also depend on speed and OTG capability checks. EP0 dequeue is unsupported, so gadget functions must tolerate that contract.

## Test Signals

USB Chapter 9 enumeration tests are the primary signal: GET_STATUS, SET_ADDRESS, SET_CONFIGURATION delegation, endpoint halt set/clear, remote wakeup feature, malformed setup length, EP0 IN/OUT data stages, zero-data status handling, test mode requests at high speed, and gadget driver setup returning stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_gadget_ep0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_host.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_host.c

## Purpose

`musb_host.c` implements MUSB host-controller support for Linux usbcore. It creates the HCD, maps URBs onto MUSB hardware endpoints, schedules control/bulk/interrupt/isochronous transfers, programs endpoint registers for PIO or DMA, handles host endpoint interrupts, cleans up/unlinks URBs, and bridges root hub operations into MUSB virtual hub helpers. The source was read as a complete 2765-line file.

## Important APIs, Types, and Functions

Externally visible functions include `hcd_to_musb`, `musb_h_ep0_irq`, `musb_host_tx`, `musb_host_rx`, `musb_host_alloc`, `musb_host_cleanup`, `musb_host_free`, `musb_host_setup`, `musb_host_resume_root_hub`, and `musb_host_poke_root_hub`. Key internal functions are `musb_start_urb`, `musb_ep_program`, `musb_advance_schedule`, `musb_schedule`, `musb_urb_enqueue`, `musb_urb_dequeue`, `musb_cleanup_urb`, `musb_h_disable`, `musb_host_packet_rx`, `musb_rx_reinit`, `musb_bulk_nak_timeout`, `musb_h_ep0_continue`, and DMA helpers for TX/RX mode selection.

## Control Flow

Host setup creates an HCD with `musb_hc_driver`, sets host PHY/OTG mode, adds the HCD, and enables wakeup. URB enqueue validates active host state, links the URB to usbcore's endpoint list, creates a `musb_qh` when needed, precomputes type/interval/address/hub fields, and schedules it. Control transfers always use EP0; bulk transfers prefer reserved bulk endpoint rings; periodic transfers claim the best-fitting free hardware endpoint. `musb_start_urb` initializes queue offsets and calls `musb_ep_program`, which selects endpoint registers, configures address/type/interval/maxpacket/toggles, programs DMA when possible, or loads/requests FIFO data for PIO. IRQ dispatch calls `musb_h_ep0_irq`, `musb_host_tx`, or `musb_host_rx`; they handle stalls, errors, NAK timeouts, DMA completion, PIO FIFO movement, short packets, iso frame status, and queue advancement. Completion calls `musb_advance_schedule`, which saves toggles, gives back the URB with the lock dropped, releases DMA channels when queues empty, and starts the next URB/QH.

## State and Persistence Behavior

Host state is in-memory: HCD private pointer, per-endpoint `in_qh/out_qh`, bulk/control rings, `musb_qh` offsets/segment sizes/iso index/toggle metadata, endpoint reinit flags, DMA channel pointers, root port status, and runtime MUSB OTG state. Temporary aligned buffers may replace URB transfer buffers for DMA on RTL 1.8+ and are copied/free on unmap. There is no persistent state outside usbcore's runtime device model.

## Dependencies and Integration Points

The file depends on Linux usbcore HCD APIs, DMA mapping APIs, scatterlist iterators, MUSB core/register/FIFO helpers, `musb_host.h`, tracepoints, and virtual hub functions from `musb_virthub.c`. Platform operations provide toggle access, endpoint/busctl offsets, VBUS, root reset quirks, DMA controller implementation, and endpoint interrupt clearing.

## Risks and Edge Cases

Risks include hardware CSR ordering constraints, endpoint toggle preservation, bulk fairness under NAK timeout, shared FIFO reconfiguration, double-buffered FIFO flushing, DMA mode 1 terminal packet behavior, CPPI/TUSB/Inventra differences, unaligned DMA buffers, URB unlink races while callbacks drop the lock, and iso error accounting. Several comments document known partial behavior and silicon quirks, so regressions often appear only under stress or specific controller variants.

## Test Signals

Signals include usbtest control/bulk/iso/interrupt cases, high-throughput bulk with multiple devices behind a hub, disconnect during active TX/RX DMA, URB unlink tests, short-packet and `URB_SHORT_NOT_OK` tests, unaligned buffer DMA tests on RTL 1.8+, periodic endpoint scheduling exhaustion, bulk NAK fairness with network/serial adapters, and root hub suspend/resume/reset sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_host.h -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_host.h

## Purpose

`musb_host.h` defines the host-side queue-head structure and internal host API for the MUSB HCD implementation. It gives `musb_host.c`, virtual hub code, and the core common declarations for scheduling, endpoint queues, root hub control, and host-only stubs. The source was read as a complete 124-line file.

## Important APIs, Types, and Functions

The central type is `struct musb_qh`, which stores usbcore endpoint/device pointers, bound hardware endpoint, ring linkage, transfer offset and segment size, precomputed type/interval/address/hub registers, readiness/type/endpoint/high-bandwidth fields, iso index/frame, and scatterlist iterator state. Helpers include `first_qh` and `next_urb`. Declarations include host IRQ handlers, allocation/setup/cleanup/free, TX/RX handlers, root disconnect, root hub resume/poke, port suspend/reset, finish resume, and hub status/control.

## Control Flow

The header has no executable driver flow except small queue helpers. `first_qh` maps a control or bulk list head to the active queue head. `next_urb` maps a `musb_qh` to the first URB on its usbcore endpoint list.

## State and Persistence Behavior

The queue head is transient scheduling state owned by the HCD. Its fields persist only while an endpoint has queued URBs or is bound to a MUSB hardware endpoint.

## Dependencies and Integration Points

The header depends on scatterlist APIs and usbcore structures. It is included by `musb_host.c` and by core paths needing host stubs; it also declares the `musb_virthub.c` interfaces used by the HCD.

## Risks and Edge Cases

The `musb_qh` contract is shared by scheduling, DMA, PIO, and cleanup paths. Misinterpreting `is_ready`, `mux`, or direction parameters can cause URBs to be started on the wrong hardware endpoint, lost during giveback, or freed while still referenced.

## Test Signals

Build coverage across host-only, gadget-only, and dual-role configs matters because the header supplies stubs. Runtime host tests should exercise multiple URBs per endpoint, bulk ring multiplexing, scatterlist PIO, and endpoint disable/unlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_io.h -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_io.h

## Purpose

`musb_io.h` defines the platform-abstracted register and FIFO I/O interface for the MUSB core. It lets common host/gadget code call generic MUSB register helpers while platform glue supplies address translation and special read/write implementations. The source was read as a complete 49-line file.

## Important APIs, Types, and Functions

The key type is `struct musb_io`, with callbacks for `ep_offset`, `ep_select`, `fifo_offset`, `read_fifo`, `write_fifo`, `busctl_offset`, `get_toggle`, and `set_toggle`. It declares global function pointers `musb_readb`, `musb_writeb`, `musb_clearb`, `musb_readw`, `musb_writew`, `musb_clearw`, plus `musb_readl` and `musb_writel`. The `musb_ep_select` macro routes endpoint selection through `musb->io.ep_select`.

## Control Flow

There is no independent control flow. Common code selects endpoints and accesses registers through these callbacks/function pointers, allowing standard flat-register controllers and indexed or remapped controllers such as sunxi to share host/gadget logic.

## State and Persistence Behavior

The header owns no storage except declared function pointers defined elsewhere. Runtime state is the platform-provided `musb->io` callback table and global register accessor pointers.

## Dependencies and Integration Points

It depends on Linux I/O accessors and MUSB structure declarations. It integrates with platform ops in glue drivers, core register helpers, endpoint programming, FIFO movement, host toggle handling, and bus-control addressing for external hubs.

## Risks and Edge Cases

Because register access is indirect, callback mismatches can corrupt the wrong register silently. The `musb_ep_select` macro assumes a visible `musb` variable in scope, which is a local coding convention rather than a self-contained API. Platform-specific layouts must keep offsets, busctl mapping, and toggle semantics consistent with common code expectations.

## Test Signals

Signals are compile coverage for platform glue, tracing of register reads/writes, enumeration on indexed and non-indexed controllers, hub/multipoint addressing tests, and endpoint toggle preservation across host transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_regs.h

## Purpose

`musb_regs.h` is the shared register map and bit-definition header for the MUSB HDRC core. It names common USB, endpoint, bus-control, power, interrupt, CSR, FIFO, ULPI, and test-mode registers and provides small inline helpers for config data and host multipoint address registers. The source was read as a complete 362-line file.

## Important APIs, Types, and Functions

Important definitions include POWER bits, INTRUSB bits, DEVCTL bits, TESTMODE bits, CSR0 peripheral/host bits, TXCSR/RXCSR peripheral and host bits, write-zero-clear masks, type register encodings, CONFIGDATA capability bits, FIFO sizing masks, common register offsets, endpoint register offsets, and bus-control offsets. Inline helpers include `musb_read_configdata`, `musb_write_rxfunaddr`, `musb_write_rxhubaddr`, `musb_write_rxhubport`, `musb_write_txfunaddr`, `musb_write_txhubaddr`, `musb_write_txhubport`, and matching read helpers.

## Control Flow

The header has no standalone runtime flow. Its inline helpers perform ordered register writes/reads through the abstracted `musb_readb/writeb` interfaces and the platform `busctl_offset` callback.

## State and Persistence Behavior

The file defines hardware state bits, not software storage. Values written through these definitions persist in controller registers until changed by software, hardware transfer completion, reset, suspend, or platform power loss.

## Dependencies and Integration Points

The header depends on `tusb6010.h` for an EP0 configuration constant and on MUSB I/O accessors. It is included throughout core, host, gadget, DMA, and platform glue files to keep register semantics consistent.

## Risks and Edge Cases

Incorrect bit masks are high risk because many registers have write-zero-clear behavior and mode-dependent meanings. CSR bits differ between host and peripheral modes, while EP0 reuses TX offsets with special semantics. Platform register remapping must preserve these logical offsets.

## Test Signals

Signals include successful compile across all MUSB platforms, register trace validation during enumeration, host/gadget control transfer tests, FIFO dynamic sizing tests, hub multipoint address tests, suspend/resume transitions, and hardware-specific tests for write-zero-clear behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_trace.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_trace.c

## Purpose

`musb_trace.c` instantiates the MUSB tracepoint definitions and implements the formatted debug logging bridge used by `musb_dbg`. The source was read as a complete 25-line file.

## Important APIs, Types, and Functions

The file defines `CREATE_TRACE_POINTS`, includes `musb_trace.h`, and implements `musb_dbg(struct musb *musb, const char *fmt, ...)`. `musb_dbg` wraps varargs in `struct va_format` and emits `trace_musb_log`.

## Control Flow

Callers invoke `musb_dbg`; the function starts a `va_list`, points a `va_format` at the format and arguments, calls the trace event, and ends the `va_list`. There is no direct printk path in this file.

## State and Persistence Behavior

The function is stateless apart from stack-local varargs. Trace records are runtime diagnostic output managed by the kernel tracing subsystem.

## Dependencies and Integration Points

It depends on tracepoint machinery generated from `musb_trace.h` and on the `struct musb` controller object for device naming in the trace event. It is used broadly by host, gadget, DMA, virtual hub, and platform glue paths.

## Risks and Edge Cases

The main risk is format-string/argument mismatch at call sites. Because output is tracepoint-based, diagnostics may be invisible unless tracing is enabled. The `va_format` must not outlive the call, which this implementation satisfies.

## Test Signals

Build with tracing enabled, enable `musb:musb_log` in ftrace/perf, trigger enumeration and transfers, and confirm formatted log records include the expected controller device name and message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_trace.h -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_trace.h

## Purpose

`musb_trace.h` defines the Linux tracepoint events for MUSB diagnostics. It covers formatted driver logs, controller state, register accesses, interrupt summaries, host URB lifecycle, gadget request lifecycle, and optional CPPI 4.1 DMA channel events. The source was read as a complete 389-line file.

## Important APIs, Types, and Functions

Trace events include `musb_log`, `musb_state`, `musb_isr`, register event classes for byte/word/long reads and writes, host URB events (`musb_urb_start`, `musb_urb_gb`, `musb_urb_rx`, `musb_urb_tx`, `musb_urb_enq`, `musb_urb_deq`), gadget request events (`musb_req_gb`, `musb_req_tx`, `musb_req_rx`, `musb_req_alloc`, `musb_req_free`, `musb_req_start`, `musb_req_enq`, `musb_req_deq`), and optional `musb_cppi41_*` events. It sets `TRACE_SYSTEM` to `musb` and includes `trace/define_trace.h`.

## Control Flow

The header is consumed by tracepoint generation. Runtime call sites execute the generated trace hooks, which capture selected fields from `struct musb`, `struct urb`, `struct musb_request`, or `struct cppi41_dma_channel` and format them for tracing.

## State and Persistence Behavior

The file defines trace metadata only. Trace records are ephemeral kernel tracing data, and no driver state is mutated by these events.

## Dependencies and Integration Points

It depends on Linux tracepoint APIs, USB types, `musb_core.h`, and optionally `cppi_dma.h`. It is integrated into register accessors, host/gadget transfer paths, IRQ handling, and CPPI DMA code.

## Risks and Edge Cases

Trace events dereference live driver objects at trace time, so call sites must provide valid pointers. Capturing too much data can have runtime overhead when enabled. Optional CPPI events must stay in sync with `struct cppi41_dma_channel`.

## Test Signals

Compile with tracepoints and optional CPPI config, list events under `/sys/kernel/tracing/events/musb`, enable URB/request/register events during usbtest, and confirm fields such as pipe, endpoint, lengths, status, and register offsets match observed transfer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_virthub.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_virthub.c

## Purpose

`musb_virthub.c` implements the single-port virtual root hub used when MUSB operates as a host. It translates usbcore hub class requests into MUSB port power, reset, suspend, resume, test-mode, disconnect, and status-change behavior. The source was read as a complete 439-line file.

## Important APIs, Types, and Functions

Public functions are `musb_host_finish_resume`, `musb_port_suspend`, `musb_port_reset`, `musb_root_disconnect`, `musb_hub_status_data`, and `musb_hub_control`. `musb_has_gadget` is an internal helper used to avoid starting sessions in OTG mode before a gadget is available.

## Control Flow

USB hub requests enter through `musb_hub_control`. Clear/set hub features are mostly NOPs; port feature requests drive suspend, reset, power, and test behavior; descriptor/status requests synthesize a one-port hub descriptor and return `musb->port1_status`. Setting port power may call `musb_start` after dropping the lock. Port reset asserts MUSB_POWER_RESET and schedules delayed deassertion; deassertion updates high-speed status, enable/change bits, and polls root hub status. Suspend sets SUSPENDM and updates OTG state; resume sets RESUME and schedules `musb_host_finish_resume`, which clears resume and reports status changes.

## State and Persistence Behavior

The file mutates `musb->port1_status`, `is_active`, OTG state, timers/delayed work, VBUS retry count, and gadget A-peripheral flags during HNP transitions. State is runtime-only but visible to usbcore through root hub status polling.

## Dependencies and Integration Points

It depends on usbcore HCD hub callbacks, MUSB power/devctl/testmode registers, delayed work, OTG state helpers, platform VBUS and root-reset hooks, and `usb_hcd_poll_rh_status`. Host setup in `musb_host.c` registers these functions through `hc_driver`.

## Risks and Edge Cases

Root hub state must match both USB hub semantics and OTG state transitions. Reset/resume timing is compliance-sensitive, and the code has platform hooks for root reset end. Host-only and OTG behavior differs around gadget availability, VBUS power, B-host/A-host transitions, and HNP. Incorrect change-bit clearing can make usbcore miss connect/reset/suspend events.

## Test Signals

Signals include hub descriptor/status queries, connect/disconnect notification, port power on/off, reset timing during enumeration, suspend/resume compliance, high-speed detection, OTG HNP paths, USB test-mode feature requests, and status-change polling through `usb_hcd_poll_rh_status`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_virthub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musbhsdma.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/musbhsdma.c

## Purpose

`musbhsdma.c` implements support for Mentor's high-speed DMA controller used by some MUSB instances. It allocates and manages up to eight DMA channels, programs channel address/count/control registers, handles DMA interrupts, aborts channels, and exposes controller create/destroy functions to platform glue. The source was read as a complete 455-line file.

## Important APIs, Types, and Functions

Important types are `struct musb_dma_channel` and `struct musb_dma_controller`. The DMA controller operations are `dma_channel_allocate`, `dma_channel_release`, `dma_channel_program`, and `dma_channel_abort`. Other key functions are `configure_channel`, `dma_controller_irq`, `musbhs_dma_controller_create`, `musbhs_dma_controller_create_noirq`, `musbhs_dma_controller_destroy`, `dma_controller_alloc`, and `dma_controller_stop`. Exported symbols include `dma_controller_irq`, create, create_noirq, and destroy.

## Control Flow

Platform glue creates the controller, optionally requests the named `"dma"` IRQ, and hands the `dma_controller` to core host/gadget code. Endpoint code allocates a free channel, then calls `channel_program`; programming rejects busy/unknown channels and unaligned DMA addresses on RTL 1.8+, records start/length/maxpacket metadata, writes address/count, and writes control bits for mode, burst, endpoint, direction, IRQ, and enable. The DMA IRQ handler clears interrupt status, detects spurious completion by checking zero counts, updates actual length from current address, marks channels free or bus-aborted, performs TX packet-ready fixups when needed, and calls `musb_dma_completion`.

## State and Persistence Behavior

The controller tracks used channels as a bitmask, per-channel endpoint/direction/start/length/maxpacket, channel status, desired mode, and actual length. Hardware channel registers persist until abort, completion, or controller reset. No disk persistence exists.

## Dependencies and Integration Points

The file depends on `musb_core.h`, `musb_dma.h`, MUSB HSDMA register offsets, IRQ APIs, platform devices, and the core `musb_dma_completion` callback. OMAP2430 platform ops can use this controller when `CONFIG_USB_INVENTRA_DMA` is enabled.

## Risks and Edge Cases

Risks include active channels during controller stop, DMA address alignment fallback, bus errors, spurious or coalesced DMA interrupts, correct TXCSR sequencing when aborting or completing mode 1 transfers, and actual length calculation by subtracting programmed start from current DMA address. `BUG_ON` is used for invalid busy/unknown programming states and mode 1 length smaller than packet size.

## Test Signals

Signals include DMA channel allocation exhaustion/release, unaligned DMA fallback to PIO, bulk TX/RX with mode 0 and mode 1, abort during active transfer, spurious interrupt handling, bus-error injection if possible, and platform create paths with and without a separate DMA IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/musbhsdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/omap2430.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/omap2430.c

## Purpose

`omap2430.c` is the TI OMAP2+/OMAP3/OMAP4 MUSB glue driver. It creates a child `musb-hdrc` platform device from device tree data, wires OMAP-specific PHY/control-module/mailbox behavior into MUSB platform ops, handles interrupts, configures ULPI/UTMI interface selection, and implements runtime/system PM for the wrapper. The source was read as a complete 623-line file.

## Important APIs, Types, and Functions

The main private type is `struct omap2430_glue`, holding the parent device, child MUSB device, mailbox status, work item, control-module device, and PM flags. Important functions include `omap2430_musb_mailbox`, `omap_musb_set_mailbox`, `omap2430_musb_interrupt`, `omap2430_musb_init`, `omap2430_musb_enable`, `omap2430_musb_disable`, `omap2430_musb_exit`, `omap2430_probe`, `omap2430_remove`, runtime/system PM callbacks, and low-level standby helpers. `omap2430_ops` supplies MUSB platform operations and optional Inventra DMA hooks.

## Control Flow

Probe requires a device tree node, allocates glue and a child `musb-hdrc` device, reads mode/interface/endpoint/RAM/power/multipoint properties, resolves the optional control module, copies resources or legacy IRQ resources, attaches platform data, enables runtime PM, and registers the child device. MUSB core init obtains the USB2 PHY and USB PHY, powers on the PHY, installs the OMAP ISR, and programs `OTG_INTERFSEL` for UTMI or ULPI. Mailbox callbacks update `glue->status` and schedule work; the work item switches between host, device, and disconnected modes, drives VBUS, updates OTG state and last events, and notifies the transceiver chain.

## State and Persistence Behavior

Runtime state lives in `struct omap2430_glue`, the global `_glue` pointer, `musb->context.otg_interfsel`, PHY power/init state, OTG state, runtime-suspend flags, and control-module USB mode. There is no persistent storage. The global `_glue` means the implementation assumes only one wrapper instance.

## Dependencies and Integration Points

The driver depends on platform device, OF, IRQ, runtime PM, DMA mask, generic PHY, legacy USB PHY, `omap_control_usb_set_mode`, and OMAP platform data. It integrates with MUSB core through `struct musb_platform_ops`, the child `musb-hdrc` device, Inventra DMA support, and the `phy_callback` mailbox.

## Risks and Edge Cases

Risks include probe deferral when PHY or MUSB core is not ready, singleton `_glue` behavior, ordering between runtime PM and mailbox work, control-module reference lifetime, legacy `ti,hwmods` resource handling, long resume orientation delay to avoid babble, and PHY suspend/resume sequencing split across normal and late PM callbacks.

## Test Signals

Signals include OF probe on `ti,omap3-musb` and `ti,omap4-musb`, mailbox ID/VBUS transitions, host and gadget enumeration, ULPI versus UTMI configuration, runtime suspend/resume preserving `OTG_INTERFSEL`, system suspend/resume with PHY sequencing, DMA IRQ availability, and cleanup of the child platform device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/omap2430.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/omap2430.h -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/omap2430.h

## Purpose

`omap2430.h` defines OMAP2430/OMAP2+ wrapper register offsets and bit fields used by the OMAP MUSB glue driver. The source was read as a complete 48-line file.

## Important APIs, Types, and Functions

The header defines offsets for `OTG_REVISION`, `OTG_SYSCONFIG`, `OTG_SYSSTATUS`, `OTG_INTERFSEL`, `OTG_SIMENABLE`, and `OTG_FORCESTDBY`. It also defines bit positions and values for idle/standby modes, wakeup, soft reset, autoidle, reset done, interface selection (`UTMI_8BIT`, `ULPI_12PIN`, `ULPI_8PIN`), external charge pump, simulation enable, and force standby.

## Control Flow

There is no runtime control flow. `omap2430.c` reads and writes these offsets during low-level init/exit, PHY interface selection, debug logging, and PM context save/restore.

## State and Persistence Behavior

The header defines wrapper hardware state bits. Values programmed through these macros persist in OMAP wrapper registers while the wrapper remains powered.

## Dependencies and Integration Points

It includes OMAP USB platform data and is private to the OMAP MUSB glue layer. It integrates with MUSB core only indirectly through wrapper configuration before common core operation.

## Risks and Edge Cases

Incorrect register definitions can break standby, reset, or PHY interface selection. PM save/restore of `OTG_INTERFSEL` relies on these constants matching hardware.

## Test Signals

Signals include OMAP glue compile coverage, successful ULPI/UTMI selection, runtime suspend/resume standby transitions, and debug register dumps showing expected revision/sysconfig/sysstatus/interfsel values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/omap2430.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/sunxi.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/sunxi.c

## Purpose

`sunxi.c` is the Allwinner sunxi MUSB glue driver. It adapts the common MUSB core to Allwinner's nonstandard register layout, manages clocks/resets/SRAM/PHY/extcon state, supplies platform ops and FIFO configuration, handles role changes and VBUS, and registers a child `musb-hdrc` device. The source was read as a complete 870-line file.

## Important APIs, Types, and Functions

Important types are `struct sunxi_musb_cfg` and `struct sunxi_glue`. Key functions include `sunxi_musb_work`, `sunxi_musb_set_vbus`, root reset squelch hooks, `sunxi_musb_interrupt`, `sunxi_musb_host_notifier`, `sunxi_musb_init`, `sunxi_musb_exit`, `sunxi_musb_enable`, `sunxi_musb_disable`, `sunxi_musb_set_mode`, `sunxi_musb_recover`, register translation callbacks `sunxi_musb_readb/writeb/readw/writew`, offset callbacks, `sunxi_musb_probe`, and `sunxi_musb_remove`. `sunxi_musb_ops` exposes these to the MUSB core.

## Control Flow

Probe validates `dr_mode`, selects host/peripheral/OTG mode and initial PHY mode, loads SoC-specific config from OF match data, obtains clock/reset/extcon/PHY, registers a generic USB PHY, and registers a child `musb-hdrc` platform device using the parent resources. MUSB init claims SRAM where required, enables clock and reset, forces PIO mode, registers the extcon host notifier before `phy_init`, installs the custom ISR, and pins runtime PM active because sunxi does not support MUSB runtime PM. Extcon host notifications set pending host-mode state; `sunxi_musb_work` performs sleepable PHY power and mode changes and updates DEVCTL/session bits under the MUSB lock. Interrupt handling reads and clears sunxi-specific interrupt registers, forces FADDR to zero on peripheral reset, and calls common `musb_interrupt`.

## State and Persistence Behavior

State is in `struct sunxi_glue.flags`, PHY mode, clock/reset/SRAM ownership, extcon notifier, child platform device, and a file-scope `sunxi_musb` pointer used by register access callbacks. Hardware state includes translated register layout, DEVCTL session state, VBUS/PHY power, FIFO config, and endpoint index. No file-backed persistence exists.

## Dependencies and Integration Points

The driver depends on Allwinner SRAM claiming, clocks, resets, extcon, generic PHY, `phy-sun4i-usb` squelch control, generic USB PHY registration, OF match data, and MUSB platform ops. It integrates deeply through custom read/write callbacks because common MUSB offsets do not match the sunxi layout.

## Risks and Edge Cases

The global `sunxi_musb` limits assumptions around multiple controllers and is required because accessor callbacks lack a MUSB pointer. Register translation must handle generic, indexed endpoint, FIFO, busctl, missing configdata, missing testmode, and missing ULPI registers correctly. Role and PHY mode changes are deferred because PHY calls may sleep while callers may hold spinlocks. DMA is intentionally disabled by returning NULL controller ops. Runtime PM is pinned active.

## Test Signals

Signals include OF probe across supported compatibles, host/peripheral/OTG role selection, extcon ID changes, PHY mode switching, VBUS power sequencing, FADDR reset on peripheral reset, register trace validation against sunxi offsets, endpoint FIFO sizing for four- and five-endpoint SoCs, SRAM/reset variants, and root reset squelch behavior during enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/sunxi.c -->
