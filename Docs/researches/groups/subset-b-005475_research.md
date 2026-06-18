# subset-b-005475 Research

Grouped source research for the Cadence CDNS3/CDNSP USB gadget trace, debug, PCI glue, endpoint-zero, memory, ring, and gadget-controller implementation files. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-trace.h -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-trace.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-trace.h` declares Linux ftrace tracepoints for the older Cadence CDNS3 USBSS gadget controller path. The complete 496-line file was read for this report. It is diagnostic infrastructure rather than controller logic: it records endpoint halt/workaround activity, doorbell writes, USB and endpoint IRQ decoding, control requests, request allocation/queue/dequeue/giveback, aligned-buffer handling, TRB preparation/completion, ring dumps, endpoint enable/disable state, and request-handled decisions.

## Important APIs, Types, and Functions

Important tracepoints and event classes include `cdns3_halt`, `cdns3_wa1`, `cdns3_wa2`, `cdns3_log_doorbell`, `cdns3_log_usb_irq`, `cdns3_log_epx_irq`, `cdns3_log_ep0_irq`, `cdns3_log_ctrl`, `cdns3_log_request`, `cdns3_ep0_queue`, `cdns3_log_aligned_request`, `cdns3_log_trb`, `cdns3_log_ring`, `cdns3_log_ep`, and `cdns3_log_request_handled`. `CDNS3_MSG_MAX` sizes decode buffers. The bottom `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `#include <trace/define_trace.h>` block makes the header usable by a paired trace translation unit.

## Control Flow

There is no independent runtime control flow. When tracepoints are enabled, the generated trace machinery calls each `TP_fast_assign` block at instrumentation sites in the CDNS3 driver. Those blocks snapshot request fields, endpoint names, register values, or decoded strings, then `TP_printk` formats the event for trace readers.

## State and Persistence Behavior

The file owns no persistent controller state. Trace records are transient ftrace entries. Several events read live MMIO registers or request/endpoint fields, so the record is a point-in-time snapshot of volatile driver and hardware state.

## Dependencies and Integration Points

Direct dependencies are Linux tracepoint headers, USB chapter 9 definitions, byte-order helpers, and local `core.h`, `cdns3-gadget.h`, and `cdns3-debug.h`. Integration is through instrumentation calls in the CDNS3 gadget implementation and through the kernel trace subsystem.

## Risks and Edge Cases

Trace events dereference endpoint/request objects supplied by callers, so instrumentation must only run while those objects are valid. IRQ tracepoints read controller registers as a side effect of tracing. Large ring dumps use dynamic buffers and can still be truncated or expensive under heavy traffic. The file is for CDNS3, not CDNSP, so naming proximity can mislead maintainers working on the newer `cdnsp-*` path.

## Test Signals

Build coverage with `CONFIG_TRACING` and tracepoints enabled is the primary signal. Runtime smoke tests can enable `cdns3:*` events while enumerating a gadget, queuing bulk/control traffic, forcing stalls, and exercising aligned request paths. Useful checks are readable decoded IRQ/control events, no crashes from tracing disabled/enabled transitions, and ring dump output that matches observed TRB movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-debug.h -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-debug.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-debug.h` provides inline string decoders for Cadence CDNSP TRBs, completion codes, rings, slot contexts, endpoint contexts, and port status registers. The complete 584-line file was read for this report. It is used by tracepoints and debug logging to turn raw xHCI-like controller fields into actionable text.

## Important APIs, Types, and Functions

Key helpers are `cdnsp_trb_comp_code_string()`, `cdnsp_trb_type_string()`, `cdnsp_ring_type_string()`, `cdnsp_slot_state_string()`, `cdnsp_decode_trb()`, `cdnsp_decode_slot_context()`, `cdnsp_portsc_link_state_string()`, `cdnsp_decode_portsc()`, `cdnsp_ep_state_string()`, `cdnsp_ep_type_string()`, and `cdnsp_decode_ep_context()`. They depend on TRB, endpoint, slot, stream, and PORTSC bit macros from `cdnsp-gadget.h`.

## Control Flow

All logic is synchronous formatting. `cdnsp_decode_trb()` switches on the TRB type and formats command, event, data, setup, status, isochronous, no-op, stream NRDY, reset, halt, and dequeue-pointer cases. Port and endpoint decoders unpack bitfields and append human-readable state.

## State and Persistence Behavior

The helpers own no hardware state. Most write into caller-provided buffers. `cdnsp_decode_slot_context()` uses a static 1024-byte buffer, which is persistent across calls and not reentrant.

## Dependencies and Integration Points

Integration is mainly with `cdnsp-trace.h` and debug prints in the CDNSP gadget, ring, and memory code. The header assumes the CDNSP register/TRB macros are already visible through the including translation unit.

## Risks and Edge Cases

The static buffer in `cdnsp_decode_slot_context()` can be overwritten by concurrent or nested use. Unknown completion and TRB types collapse to generic strings, so newer hardware codes require decoder updates. Endpoint-number formatting derives from TRB endpoint IDs and can be confusing if malformed hardware events contain zero or reserved endpoint IDs. Formatting truncation is only partially surfaced.

## Test Signals

Compile all users with tracing enabled. Unit-style checks can feed representative TRB words for command, transfer, setup, NRDY, and port events into the decoders and verify stable strings. Runtime signals are trace logs that correctly name endpoint state transitions, completion codes, and PORTSC link/speed/change bits during enumeration, transfer, suspend, resume, and stall/reset tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-ep0.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-ep0.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-ep0.c` implements endpoint-zero setup request handling for the CDNSP gadget controller. The complete 483-line file was read for this report. It handles USB standard requests that must update controller state locally and delegates class/vendor/function requests to the bound gadget driver.

## Important APIs, Types, and Functions

The exported functions are `cdnsp_status_stage()` and `cdnsp_setup_analyze()`. Important internal helpers include `cdnsp_ep0_stall()`, `cdnsp_ep0_delegate_req()`, `cdnsp_ep0_set_config()`, `cdnsp_ep0_set_address()`, `cdnsp_ep0_handle_status()`, `cdnsp_enter_test_mode()`, `cdnsp_ep0_handle_feature_device()`, `cdnsp_ep0_handle_feature_intf()`, `cdnsp_ep0_handle_feature_endpoint()`, `cdnsp_ep0_set_sel()`, `cdnsp_ep0_set_isoch_delay()`, and `cdnsp_ep0_std_request()`.

## Control Flow

`cdnsp_setup_analyze()` is called after a setup event is pulled from the event ring. It traces the request, validates gadget attachment, repairs EP0 software state after halts, removes an unfinished previous EP0 request, determines whether the request has a data stage, then dispatches standard requests locally or delegates to `gadget_driver->setup()` with the device spinlock dropped. Successful no-data requests queue a status stage; negative results stall EP0. Delayed status returns are honored without immediate status queuing.

## State and Persistence Behavior

The file mutates `pdev->setup`, `ep0_stage`, `three_stage_setup`, `ep0_expect_in`, `device_address`, `may_wakeup`, `u1_allowed`, `u2_allowed`, `test_mode`, `gadget.state`, `gadget.isoch_delay`, and EP0/endpoint halt bits. It uses the persistent internal `ep0_preq` and `setup_buf` allocated during gadget initialization.

## Dependencies and Integration Points

It depends on USB composite/gadget APIs, Chapter 9 request constants, CDNSP ring queueing, endpoint halt/reset helpers, device setup/reset commands, and tracepoints from `cdnsp-trace.h`. It integrates directly with the upper gadget driver through `setup()`.

## Risks and Edge Cases

State validation is critical: SET_ADDRESS is rejected above address 127 and from configured state; SET_CONFIGURATION is limited to address/configured states; U1/U2 feature changes require configured SuperSpeed; USB test mode requires configured high/full speed and a valid selector. Endpoint halt mapping from `wIndex` must stay aligned with CDNSP endpoint indexes. The interface remote-wakeup counter uses increment/decrement semantics and could drift if function drivers mishandle repeated suspend requests.

## Test Signals

Enumeration tests should cover SET_ADDRESS, SET_CONFIGURATION, GET_STATUS for device/interface/endpoint, CLEAR_FEATURE/SET_FEATURE endpoint halt, U1/U2 enable, remote wakeup, SET_SEL, SET_ISOCH_DELAY, class/vendor delegation, delayed status, and invalid request stalling. Tracepoints `cdnsp_ctrl_req`, EP0 request/status-stage events, and endpoint halt/reset traces are the best runtime observability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-ep0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-gadget.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-gadget.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-gadget.c` is the main CDNSP USB gadget controller implementation. The complete 2077-line file was read for this report. It initializes controller registers and DMA structures, registers the UDC, exposes USB endpoint and gadget operations, manages slot/device/endpoint commands, handles port speed/link state, and plugs the gadget role into the shared Cadence DRD core.

## Important APIs, Types, and Functions

Externally used helpers include `cdnsp_port_speed()`, `cdnsp_port_state_to_neutral()`, `cdnsp_find_next_ext_cap()`, `cdnsp_set_link_state()`, `cdnsp_halt()`, `cdnsp_died()`, `cdnsp_reset()`, `cdnsp_ep_enqueue()`, `cdnsp_ep_dequeue()`, `cdnsp_wait_for_cmd_compl()`, `cdnsp_halt_endpoint()`, `cdnsp_reset_device()`, `cdnsp_alloc_streams()`, `cdnsp_disable_slot()`, `cdnsp_enable_slot()`, `cdnsp_setup_device()`, `cdnsp_set_usb2_hardware_lpm()`, `cdnsp_update_erst_dequeue()`, `cdnsp_disconnect_gadget()`, `cdnsp_suspend_gadget()`, `cdnsp_resume_gadget()`, `cdnsp_irq_reset()`, and `cdnsp_gadget_init()`. Endpoint ops implement enable, disable, request allocation/free, queue, dequeue, halt, and wedge. Gadget ops implement get-frame, wakeup, self-powered, pullup, UDC start, and UDC stop.

## Control Flow

Initialization enters through `cdnsp_gadget_init()`, which installs a device-role driver. Starting the role allocates `struct cdnsp_device`, turns gadget mode on, initializes registers with `cdnsp_gen_setup()`, allocates memory through `cdnsp_mem_init()`, initializes endpoint objects, registers the UDC, and requests a threaded IRQ. Binding a gadget driver calls `cdnsp_gadget_udc_start()`, which runs the controller at the bounded maximum speed and enables interrupts. Endpoint enable builds an input context, allocates rings/streams, configures the endpoint, and marks it enabled. Queue maps a `usb_request`, appends it to the pending list, and dispatches to control, bulk/interrupt, or isochronous TRB queueing. Stop paths disable ports, slot, IRQs, consume events, and clear command ring state.

## State and Persistence Behavior

Persistent runtime state lives in `struct cdnsp_device`: register windows, cached capabilities, locks, gadget/driver pointers, contexts, command/event rings, endpoint array, port descriptors, DMA pools, setup buffer, and controller state flags. Endpoint state tracks enabled, stopped, halted, wedged, streams, and unconfigured state. No file-backed persistence exists; persistence is in memory and hardware registers while the role is active.

## Dependencies and Integration Points

This file integrates with the Linux USB gadget core (`usb_add_gadget_udc`, endpoint/gadget ops, request mapping, callbacks), Cadence DRD role framework (`struct cdns`, `cdns_drd_gadget_on/off`, VBUS helpers), platform/PCI resource data, DMA APIs, threaded IRQs, tracepoints, and the companion CDNSP memory/ring/EP0 files. It also programs controller-specific extended capabilities and workaround "chicken bits".

## Risks and Edge Cases

Command completion waits poll the command ring and then scan the event ring, so timeout handling marks the controller dying. Endpoint disable must stop hardware, dequeue all requests, invalidate queued events, update contexts, and avoid racing disconnect paths. Remote wakeup must respect `may_wakeup` and port power/link state. DMA mask selection, 64-bit register write ordering, and APB/chicken-bit workarounds are hardware-sensitive. Stream limits and endpoint existence depend on hardware capability registers.

## Test Signals

Primary signals are successful UDC registration, gadget bind/unbind, enumeration at full/high/super/super-plus speeds, endpoint enable/disable for all supported types, bulk/interrupt/isoc transfer loops, request cancellation, halt/wedge/clear-halt, disconnect/reconnect, suspend/resume, remote wakeup, pullup toggling, and controller timeout/fatal-path behavior. Trace events for command completion, endpoint configuration, port status, request giveback, and init/exit should align with expected state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-gadget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-gadget.h -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-gadget.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-gadget.h` is the central CDNSP gadget controller contract. The complete 1616-line file was read for this report. It defines the controller register layout, bitfields, TRB formats, contexts, rings, endpoint/request/device objects, state flags, helper macros, and cross-file function prototypes used by the CDNSP implementation.

## Important APIs, Types, and Functions

Important types include `struct cdnsp_cap_regs`, `cdnsp_op_regs`, `cdnsp_port_regs`, `cdnsp_intr_reg`, `cdnsp_run_regs`, port extended-capability structs, `cdnsp_rev_cap`, `cdnsp_doorbell_array`, `cdnsp_container_ctx`, `cdnsp_slot_ctx`, `cdnsp_ep_ctx`, `cdnsp_command`, `cdnsp_stream_ctx`, `cdnsp_stream_info`, `cdnsp_ep`, `cdnsp_device_context_array`, `cdnsp_transfer_event`, `cdnsp_link_trb`, `cdnsp_event_cmd`, `union cdnsp_trb`, `cdnsp_segment`, `cdnsp_td`, `cdnsp_dequeue_state`, `cdnsp_ring`, `cdnsp_erst`, `cdnsp_request`, `cdnsp_port`, and `cdnsp_device`. Prototypes cover memory management, controller glue, ring operations, command queueing, contexts, and gadget callbacks.

## Control Flow

The header has no executable flow except `cdnsp_read_64()`, `cdnsp_write_64()`, and `next_request()`. Its macros define how other files interpret and drive control flow: command ring doorbells, port changes, endpoint context add/drop flags, TRB type decoding, event completion codes, ring ownership cycle bits, stream IDs, and setup-stage metadata.

## State and Persistence Behavior

It defines all persistent in-memory state shapes for the driver. `struct cdnsp_device` owns controller lifetime state; `struct cdnsp_ep` owns endpoint lifetime state; `struct cdnsp_ring` and `struct cdnsp_td` own queued-transfer bookkeeping; context structs mirror hardware-visible DMA memory. The header itself owns no storage.

## Dependencies and Integration Points

It includes Linux USB gadget, IRQ, and 64-bit MMIO accessor helpers. It is included by the CDNSP gadget, memory, ring, EP0, trace, and debug files. Its layouts must match the Cadence CDNSP/xHCI-like device-controller hardware ABI and the Linux gadget API.

## Risks and Edge Cases

Bitfield definitions are hardware ABI: changing masks, shifts, context sizes, TRB types, endpoint indexes, or cycle-bit rules can break enumeration and DMA. `CDNSP_ENDPOINTS_NUM` and index conversions must remain consistent with endpoint discovery. Some names and comments carry typos, but the semantic risk is mostly register/descriptor drift. Stream constants cap supported streams and can reject hardware with unexpected capabilities.

## Test Signals

Build coverage across all CDNSP translation units catches many declaration or macro regressions. Runtime signals include correct context programming visible in trace decoders, stable ring cycle behavior under wraparound, accurate endpoint index/name mapping, correct speed reporting from PORTSC values, and successful command/transfer/event processing across control, bulk, interrupt, isochronous, and stream-capable endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-gadget.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-mem.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-mem.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-mem.c` allocates, initializes, expands, maps, and frees the CDNSP hardware-visible memory model. The complete 1336-line file was read for this report. It manages DMA rings, segments, device/input contexts, stream context arrays, event ring segment tables, port discovery, and controller memory initialization/cleanup.

## Important APIs, Types, and Functions

Exported or cross-file functions include `cdnsp_mem_init()`, `cdnsp_mem_cleanup()`, `cdnsp_setup_addressable_priv_dev()`, `cdnsp_copy_ep0_dequeue_into_input_ctx()`, `cdnsp_endpoint_zero()`, `cdnsp_endpoint_init()`, `cdnsp_ring_expansion()`, `cdnsp_dma_to_transfer_ring()`, `cdnsp_alloc_stream_info()`, `cdnsp_alloc_streams()` support, `cdnsp_free_endpoint_rings()`, `cdnsp_get_input_control_ctx()`, `cdnsp_get_slot_ctx()`, and `cdnsp_get_ep_ctx()`. Key internals include segment/ring allocation/free/linking, radix-tree stream mapping, ERST allocation, and extended-capability port scanning.

## Control Flow

`cdnsp_mem_init()` programs CONFIG, allocates the DCBAA, creates DMA pools, creates the command and event rings, writes the command-ring pointer, sets doorbell and interrupter pointers, builds the ERST, programs event-ring registers, discovers USB2/USB3 ports, and allocates the private device context plus EP0 ring. Endpoint init computes interval, mult, burst, type, max packet, ESIT payload, average TRB length, allocates the transfer ring, and optionally allocates streams for SuperSpeed bulk endpoints. Cleanup unwinds in reverse.

## State and Persistence Behavior

Persistent state includes coherent DCBAA and ERST memory, DMA-pool context blocks, ring segment DMA buffers, per-segment bounce buffers, stream context arrays, radix mappings from TRB DMA segment keys to stream rings, port descriptors, and `pdev` pointers to command/event/endpoint rings. This state persists for the active gadget role and is destroyed by `cdnsp_mem_cleanup()`.

## Dependencies and Integration Points

The file depends on Linux DMA, DMA pool, slab, USB descriptor helpers, radix trees, `cdnsp-gadget.h`, and `cdnsp-trace.h`. It integrates with ring queueing, event handling, endpoint enable/configure, and controller register programming in `cdnsp-gadget.c`.

## Risks and Edge Cases

Allocation unwind must free coherent memory, pools, rings, contexts, and ERST in the correct order. Stream radix mapping assumes DMA addresses align with `TRB_SEGMENT_SHIFT` and comments warn about DMA mask assumptions. Stream context arrays are limited by `CDNSP_CTX_SIZE`. Ring expansion must preserve cycle state and stream mappings. Endpoint interval and burst calculations differ by USB speed and transfer type, so descriptor edge cases can silently affect service timing.

## Test Signals

Signals include successful initialization/cleanup under fault injection at each allocation step, correct USB2/USB3 port detection, EP0 context programming for full/high/super/super-plus speeds, endpoint context traces matching descriptors, stream allocation and rejection limits, ring expansion under large SG requests, bounce-buffer allocation/unmap paths, and leak checks after gadget unbind or probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-pci.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-pci.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-pci.c` is the PCI glue for Cadence CDNSP USBSSP hardware. The complete 248-line file was read for this report. It pairs the host/device PCI function with the OTG/DRD PCI function, maps BAR resources into the shared Cadence core object, wires interrupts/resources, applies a PCI-specific APB timeout override, and registers suspend/resume hooks.

## Important APIs, Types, and Functions

Important functions are `cdnsp_get_second_fun()`, `cdnsp_pci_probe()`, `cdnsp_pci_remove()`, `cdnsp_pci_suspend()`, and `cdnsp_pci_resume()`. Static objects include `cdnsp_pci_pm_ops`, `cdnsp_pci_ids`, and `cdnsp_pci_driver`. Constants define BAR use, expected PCI function numbers, driver names, and `CHICKEN_APB_TIMEOUT_VALUE`.

## Control Flow

Probe validates function number and matching paired function, rejects xHCI-class ownership, enables the PCI device, allocates or reuses the shared `struct cdns`, maps device BAR2 for function 0, records xHCI memory/IRQ resources, records OTG BAR/IRQ for function 1, sets the APB timeout override, and when both functions are enabled calls `cdns_init()` with `cdnsp_gadget_init` as the gadget initializer. Remove calls `cdns_remove()` only when the paired function remains enabled; otherwise it frees the shared object.

## State and Persistence Behavior

Persistent state is the shared `struct cdns` stored in PCI driver data on both functions. It contains mapped device registers, xHCI and OTG resources, IRQ numbers, wake settings, and the gadget-init callback. No disk persistence exists.

## Dependencies and Integration Points

It depends on Linux PCI, platform resource, DMA mapping, PM, module, and Cadence core/gadget-export headers. It integrates PCI enumeration with the common `cdns_init/remove/suspend/resume` core and the CDNSP gadget role.

## Risks and Edge Cases

The probe path relies on both PCI functions appearing and on `pci_is_enabled(func)` to decide object ownership. Incorrect function order or class codes cause `-EINVAL`. Shared-object cleanup must avoid freeing while the paired function still uses it. Resource mapping assumes BAR layout. Runtime PM wake handling is conditional on `pci_dev_run_wake()`.

## Test Signals

PCI probe tests should cover both function probe orders, missing paired function, xHCI-class rejection, BAR request/mapping failure, `cdns_init()` failure unwind, remove order permutations, suspend/resume lock behavior, wake-capable runtime PM transitions, and the APB timeout override being visible to `cdnsp_set_apb_timeout_value()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-ring.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-ring.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-ring.c` implements the CDNSP command, event, endpoint transfer, and stream ring engine. The complete 2504-line file was read for this report. It owns TRB enqueue/dequeue movement, doorbells, command submission, transfer queueing for control/bulk/interrupt/isochronous requests, event handling, request cancellation, stream NRDY handling, port-status handling, bounce-buffer cleanup, and IRQ dispatch.

## Important APIs, Types, and Functions

Exported functions include `cdnsp_trb_virt_to_dma()`, `cdnsp_last_trb_on_seg()`, `cdnsp_last_trb_on_ring()`, `cdnsp_inc_deq()`, `cdnsp_ring_cmd_db()`, `cdnsp_ring_doorbell_for_active_rings()`, `cdnsp_remove_request()`, `cdnsp_thread_irq_handler()`, `cdnsp_irq_handler()`, `cdnsp_queue_bulk_tx()`, `cdnsp_queue_ctrl_tx()`, `cdnsp_cmd_stop_ep()`, `cdnsp_queue_isoc_tx()`, and command queue helpers such as `cdnsp_queue_slot_control()`, `cdnsp_queue_address_device()`, `cdnsp_queue_reset_device()`, `cdnsp_queue_configure_endpoint()`, `cdnsp_queue_stop_endpoint()`, `cdnsp_queue_new_dequeue_state()`, `cdnsp_queue_reset_ep()`, `cdnsp_queue_halt_endpoint()`, and `cdnsp_force_header_wakeup()`.

## Control Flow

Request queueing prepares a ring, appends a TD to the ring list, writes all TRBs with the first TRB held back by cycle-bit ownership, then gives the first TRB to hardware and rings the endpoint doorbell. Event handling is threaded: the hard IRQ acknowledges status and wakes the thread; the thread drains owned event TRBs under `pdev->lock`, dispatching command completions, port changes, transfers, setup events, NRDY stream events, and controller errors, then updates the ERST dequeue pointer. Transfer completion locates the endpoint ring by TRB DMA, validates the TD, computes actual length/status by transfer type, advances dequeue pointers, unmaps bounce buffers, and gives the request back.

## State and Persistence Behavior

Persistent state lives in ring pointers, segment lists, cycle states, free-TRB counts, TD lists, per-stream active/rejected/doorbell counters, endpoint skip flags, event ring dequeue state, and command status/TRB pointers. Hardware-visible state is persisted in TRB memory and controller registers until completion or cleanup.

## Dependencies and Integration Points

The file depends on Linux scatterlist, DMA mapping, delays, IRQs, CDNSP trace/debug macros, and the shared structures from `cdnsp-gadget.h`. It integrates with EP0 setup handling, gadget giveback, memory-managed rings/streams, command wait logic, port reset/suspend/resume callbacks, and USB request DMA mapping performed by gadget code.

## Risks and Edge Cases

Cycle-bit and link-TRB handling are correctness-critical, especially ring wrap, expansion, and the WA1 NOP-before-link workaround. Cancellation must distinguish hardware stopped inside the target TD from no-op conversion. Isochronous missed-service handling uses `pep->skip` to complete skipped TDs and can misreport if event DMA is corrupt. Stream endpoints can only receive two outstanding doorbells and depend on NRDY PRIME/REJECT events. Bounce-buffer direction handling is subtle and SG length mismatches are warned. Command timeout marks the controller dying.

## Test Signals

Use high-volume bulk SG transfers crossing 64 KiB TRB boundaries, zero-length and `request.zero` cases, stream-capable bulk transfers with PRIME/REJECT behavior, isochronous underrun/overrun/missed-service cases, request dequeue while running and while disconnecting, ring expansion, endpoint halt/reset, command timeout injection, event ring wrap, port attach/reset/suspend/resume, and trace validation of queued/completed TRBs and dequeue state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-trace.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-trace.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-trace.c` is the tracepoint definition translation unit for CDNSP. The complete 12-line file was read for this report. It defines `CREATE_TRACE_POINTS` and includes `cdnsp-trace.h`, causing the trace event declarations in that header to emit storage and registration code exactly once.

## Important APIs, Types, and Functions

There are no functions or data structures declared directly here. Its important API is the compile-time tracepoint pattern: `#define CREATE_TRACE_POINTS` followed by `#include "cdnsp-trace.h"`.

## Control Flow

The file has no runtime control flow of its own. Runtime behavior comes from generated tracepoint registration and call sites compiled from `cdnsp-trace.h`.

## State and Persistence Behavior

It owns generated tracepoint definitions at link time. Runtime trace state is managed by the Linux tracing subsystem, not by this source file.

## Dependencies and Integration Points

It depends entirely on `cdnsp-trace.h` and the kernel tracepoint framework. It integrates with all CDNSP source files that include the trace header without `CREATE_TRACE_POINTS`.

## Risks and Edge Cases

This file must remain the sole translation unit defining `CREATE_TRACE_POINTS` for CDNSP trace events. Duplicating the define elsewhere causes multiple-definition build failures; removing it causes unresolved tracepoint definitions when tracing is enabled.

## Test Signals

Build and link the CDNSP driver with tracepoints enabled. Runtime smoke tests should show CDNSP trace events appearing under ftrace after enabling the corresponding event group during gadget enumeration and transfer activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-trace.c -->
