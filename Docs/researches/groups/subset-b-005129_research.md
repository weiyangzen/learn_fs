# Research: subset-b-005129

Grouped research report for Surface Aggregator protocol and platform integration sources. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file artifacts.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_packet_layer.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_packet_layer.c

## Purpose
Implements the SSH packet transport layer for the Surface Aggregator Module serial hub. It turns raw SSH frames into reliable packet delivery over `serdev`, including ACK/NAK handling, sequence tracking, retransmission, RX parsing, TX serialization, cancellation, and shutdown. It is the lower transport used by the request layer and controller stack.

## Important APIs, Types, And Functions
The exported packet lifetime APIs are `ssh_packet_get()`, `ssh_packet_put()`, and `ssh_packet_init()`. Public transport entry points are implemented here for declarations in `ssh_packet_layer.h`: `ssh_ptl_init()`, `ssh_ptl_destroy()`, `ssh_ptl_tx_start()`, `ssh_ptl_tx_stop()`, `ssh_ptl_rx_start()`, `ssh_ptl_rx_stop()`, `ssh_ptl_submit()`, `ssh_ptl_cancel()`, `ssh_ptl_rx_rcvbuf()`, and `ssh_ptl_shutdown()`. Internal helpers manage priority insertion (`__ssh_ptl_queue_find_entrypoint()`), queue/pending membership, TX completion, ACK pop, NAK resubmission, timeout reaping, RX frame evaluation, and control-packet allocation. `ssh_ctrl_packet_cache_init()` and `ssh_ctrl_packet_cache_destroy()` set up a kmem cache used for ACK/NAK packets.

## Control Flow
Transmit flow starts with `ssh_ptl_submit()`, which validates flush/data invariants, binds the packet to the PTL, inserts it into the priority queue, and wakes the TX kthread. `ssh_ptl_tx_threadfn()` pops sendable packets, adds sequenced packets to the pending set, writes data via `serdev_device_write_buf()`, and completes unsequenced packets immediately. Sequenced packets remain pending until `ssh_ptl_acknowledge()` receives a matching ACK from RX. RX data enters via `ssh_ptl_rx_rcvbuf()` into a kfifo, is copied into `rx.buf`, then `ssh_ptl_rx_eval()` aligns to SYN, validates frames via `sshp_parse_frame()`, dispatches ACK, NAK, sequenced data, and non-sequenced data, sends ACKs for sequenced inbound data, and forwards payloads to `ptl->ops.data_received()`.

## State And Persistence Behavior
The layer is runtime-stateful only. It persists no data outside memory. Packet state lives in bit flags on `struct ssh_packet`, while ownership is controlled by krefs held by the queue, pending set, TX thread, RX/ACK path, and timeout logic. `queue.lock` protects queue state and priority, `pending.lock` protects pending membership and timestamps, and the documented ordering is pending lock before queue lock. `rtx_timeout.reaper` periodically resubmits timed-out packets up to `SSH_PTL_MAX_PACKET_TRIES` and then completes with `-ETIMEDOUT`. A ring of eight recently received sequence IDs suppresses duplicate sequenced frames caused by EC retransmit after ACK loss.

## Dependencies And Integration Points
Depends on Linux kthreads, kfifo, spinlocks, krefs, delayed work, wait queues, `serdev`, `ssh_parser.c`, `ssh_msgb.h`, and protocol definitions in `linux/surface_aggregator/serial_hub.h`. Tracepoints in `trace.h` observe submissions, completions, timeouts, allocation/free, and error-injection paths. When `CONFIG_SURFACE_AGGREGATOR_ERROR_INJECTION` is enabled, injectable hooks simulate dropped ACK/NAK/data packets, write failures, and corrupt TX/RX data.

## Risks
The code is concurrency-sensitive: missed barriers or wrong lock order can cause lost cancellation, double completion, or leaked references. `sshp_find_syn()` is called with spans expected to contain at least one byte; callers currently satisfy that through RX-buffer loop structure, but this invariant is worth preserving. In `ssh_ptl_shutdown()`, the pending-list loop moves `pending_node` entries to `complete_q` while `complete_p` remains unused; the comments describe two completion lists, so this deserves scrutiny for list-node misuse or missed pending reference drops. RX FIFO overflow returns a short count to serdev callers; upstream caller behavior should be checked for backpressure handling.

## Test Signals
Useful tests include injected dropped ACK/NAK/data frames, injected CRC/SYN corruption, forced `serdev_device_write_buf()` errors, flush during active pending packets, cancellation before submit/during TX/while pending, shutdown with queued and pending packets, duplicate inbound sequence handling, and tracepoint validation that each packet gets one completion and one release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_packet_layer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_packet_layer.h -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_packet_layer.h

## Purpose
Defines the in-kernel interface and state container for the SSH packet transport layer. It exposes packet-layer lifecycle, submission, cancellation, RX ingress, and control packet cache APIs to the surrounding Surface Aggregator serial hub code.

## Important APIs, Types, And Functions
`enum ssh_ptl_state_flags` currently defines `SSH_PTL_SF_SHUTDOWN_BIT`. `struct ssh_ptl_ops` contains the upper-layer `data_received()` callback. `struct ssh_ptl` embeds the full packet-layer state: serdev pointer, shutdown state, queue, pending set, TX kthread state, RX kthread/fifo/parser buffer/retransmit suppression state, retransmission timeout work, and callbacks. Public declarations include `ssh_ptl_init()`, `ssh_ptl_destroy()`, TX/RX start/stop functions, `ssh_ptl_shutdown()`, `ssh_ptl_submit()`, `ssh_ptl_cancel()`, `ssh_ptl_rx_rcvbuf()`, `ssh_packet_init()`, and control-packet cache lifecycle. `ssh_ptl_get_device()` and `ssh_ptl_tx_wakeup_transfer()` are inline helpers.

## Control Flow
This header establishes the layering contract. Lower serial code pushes bytes through `ssh_ptl_rx_rcvbuf()` and wakes transfer availability through `ssh_ptl_tx_wakeup_transfer()`. Upper layers submit `struct ssh_packet` instances with initialized ops and data. The packet layer then calls `data_received()` for validated inbound data payloads and packet completion/release callbacks through packet ops defined in the public serial-hub header.

## State And Persistence Behavior
All fields in `struct ssh_ptl` are volatile runtime state. The queue and pending sets are list-based and protected by spinlocks. TX uses completions and a wait queue; RX uses kfifo plus an `sshp_buf` parsing buffer. The retransmission reaper tracks timeout interval and currently scheduled expiration. No disk, firmware, or NVRAM state is stored.

## Dependencies And Integration Points
Includes kernel atomic, kfifo, ktime, list, serdev, spinlock, wait, workqueue, and Surface Aggregator protocol definitions. It depends on `ssh_parser.h` for RX buffer handling. Consumers are expected to supply a live `serdev_device` and `ssh_ptl_ops`; the request layer embeds `struct ssh_ptl` inside `struct ssh_rtl`.

## Risks
Because `struct ssh_ptl` exposes internal synchronization fields, maintainers must preserve lock semantics documented in the `.c` file. `ssh_ptl_tx_wakeup_transfer()` ignores wakeups after shutdown, so callers must tolerate dropped TX-space notifications during teardown. `ssh_ptl_get_device()` may return `NULL` if called before serdev setup or after partial teardown.

## Test Signals
Compile-time coverage should catch declaration drift against `ssh_packet_layer.c`. Runtime checks should exercise initialization/destruction ordering, shutdown wakeup suppression, RX byte injection, packet submission/cancel paths, and embedding via `to_ssh_ptl()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_packet_layer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_parser.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_parser.c

## Purpose
Provides zero-copy parsing and validation helpers for SSH messages used by the Surface Aggregator serial hub. It validates SYN alignment, frame and payload CRCs, maximum message length, and command payload shape.

## Important APIs, Types, And Functions
`sshp_find_syn()` searches a span for complete or partial SSH SYN bytes and returns the remaining aligned span. `sshp_parse_frame()` validates a complete SSH frame and returns a `struct ssh_frame *` plus payload span. `sshp_parse_command()` validates command payload length and returns a `struct ssh_command *` plus command-data span. Internal helpers `sshp_validate_crc()` and `sshp_starts_with_syn()` implement CRC comparison and SYN prefix detection.

## Control Flow
RX code first calls `sshp_find_syn()` to align to the next possible message. `sshp_parse_frame()` then confirms the span starts with SYN, has enough bytes for a minimal message, validates the frame CRC over `struct ssh_frame`, checks payload length against caller-provided `maxlen`, waits for a complete payload if needed, validates payload CRC, and finally returns pointers into the source buffer. Request-layer code later calls `sshp_parse_command()` on data-frame payloads to interpret command headers and payload bytes.

## State And Persistence Behavior
The parser is stateless. It mutates only output pointers and lengths. It does not allocate memory, retain references, or copy message payloads. Returned frame and command pointers alias the caller's RX buffer and are valid only while that buffer remains stable.

## Dependencies And Integration Points
Uses `linux/unaligned.h`, device logging, and SSH protocol macros/types from `linux/surface_aggregator/serial_hub.h`. Integrated directly by `ssh_packet_layer.c` for frame parsing and by `ssh_request_layer.c` for command parsing.

## Risks
`sshp_find_syn()` indexes `src->ptr[src->len - 1]`; callers must not pass zero-length spans. `sshp_parse_frame()` treats incomplete frames as success with `*frame == NULL`, so callers must distinguish incomplete data from valid complete frames. Length and CRC validation are robust, but any future protocol extension must keep `maxlen` consistent with the RX buffer capacity.

## Test Signals
Parser tests should cover valid ACK/NAK/data frames, bad SYN, partial SYN at buffer end, incomplete minimal frame, invalid frame CRC, oversized payload length, incomplete payload, invalid payload CRC, command payload too short, zero-length command data, and aliasing behavior where returned spans point inside the original buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_parser.h -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_parser.h

## Purpose
Declares the SSH parser API and provides small inline buffer helpers used by the packet RX thread to accumulate bytes and expose parseable spans.

## Important APIs, Types, And Functions
`struct sshp_buf` tracks a byte pointer, used length, and capacity. Inline helpers initialize, allocate, free, drop consumed bytes with `memmove()`, drain bytes from a `kfifo`, and create an `ssam_span` at a buffer offset. The declared parser functions are `sshp_find_syn()`, `sshp_parse_frame()`, and `sshp_parse_command()`.

## Control Flow
The packet RX thread allocates one `sshp_buf`, repeatedly reads from its kfifo into the unused tail with `sshp_buf_read_from_fifo()`, creates spans with `sshp_buf_span_from()`, parses frames, then drops consumed bytes with `sshp_buf_drop()`. The helpers assume the caller manages bounds and buffer lifetime.

## State And Persistence Behavior
`sshp_buf` owns no memory by itself unless initialized via `sshp_buf_alloc()`. `sshp_buf_free()` releases the backing allocation and zeroes the struct. Buffer contents are transient RX data only. `sshp_buf_drop()` preserves unconsumed bytes for the next RX iteration, allowing partial frames to persist in memory across wakeups.

## Dependencies And Integration Points
Uses kfifo, slab allocation, and `struct ssam_span` from `linux/surface_aggregator/serial_hub.h`. It is included by `ssh_packet_layer.h` and the parser implementation.

## Risks
The inline helpers are intentionally low-level. `sshp_buf_drop()` assumes `n <= buf->len`; `sshp_buf_span_from()` warns that the offset is not validated; and `sshp_buf_read_from_fifo()` trusts capacity accounting. Incorrect caller arithmetic can cause underflow or out-of-bounds spans.

## Test Signals
Exercise allocation failure, FIFO-to-buffer transfer with partial capacity, dropping zero/some/all bytes, preserving incomplete frames across drops, span creation at valid offsets, and parser behavior when the RX buffer reaches capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_request_layer.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_request_layer.c

## Purpose
Implements the SSH request transport layer above the packet layer. It maps request objects to packet submissions, correlates responses by request ID, dispatches EC events, enforces pending limits, supports flush and cancellation, and times out requests that have been transmitted but did not receive a response.

## Important APIs, Types, And Functions
Public APIs are `ssh_request_init()`, `ssh_rtl_init()`, `ssh_rtl_destroy()`, `ssh_rtl_start()`, `ssh_rtl_submit()`, `ssh_rtl_cancel()`, `ssh_rtl_flush()`, and `ssh_rtl_shutdown()`. Key internal paths include queue/pending helpers, `ssh_rtl_tx_work_fn()`, `ssh_rtl_packet_callback()`, `ssh_rtl_complete()`, `ssh_rtl_timeout_reap()`, `ssh_rtl_rx_data()`, and `ssh_rtl_rx_command()`. The request layer wraps each request's packet ops with `ssh_rtl_packet_ops`.

## Control Flow
`ssh_rtl_submit()` validates that response-bearing requests are sequenced, binds the embedded packet to the underlying PTL, queues the request, and schedules TX work. `ssh_rtl_tx_work_fn()` processes up to `SSH_RTL_TX_BATCH` requests per workqueue run, moves requests to pending, and submits embedded packets. Packet completion calls `ssh_rtl_packet_callback()`: failed packet status completes the request; successful transmission either starts a response timeout or completes no-response requests. Inbound data from the packet layer is parsed as a command, filtered to host-targeted messages, routed to `ops.handle_event()` if the request ID encodes an event, or matched to a pending request by RQID and completed with response data.

## State And Persistence Behavior
State is in-memory only. `struct ssh_request` state bits track queued, pending, transmitting, transmitted, response received, canceled, completed, and type flags. `struct ssh_rtl` holds queue and pending lists, an atomic pending count, TX work, and delayed timeout work. Request timestamps are set once after successful packet transmission for response timeouts. Flush requests are stack-allocated wrappers with a completion and special packet/request type bits.

## Dependencies And Integration Points
Embeds and initializes `struct ssh_ptl`, uses `sshp_parse_command()`, Surface Aggregator controller/request definitions, workqueues, spinlocks, completions, tracepoints, and optional response-drop error injection. Upper layers interact through `ssam_request_do_sync*()` and controller/event infrastructure, while lower-layer data and packet completions arrive via packet-layer callbacks.

## Risks
The layer relies on precise memory ordering around `packet.ptl` publication and cancellation. Cancel paths differ for unsubmitted, queued, pending, and already transmitted requests, making race regressions likely if flags are changed. `ssh_rtl_complete()` scans pending requests by RQID and assumes responses usually arrive in order. If an unexpected or early response appears before packet ACK/transmitted state, it completes with `-EREMOTEIO`. `ssh_rtl_submit()` sets `packet.ptl` before checking RTL shutdown and does not reset it on `-ESHUTDOWN`; callers should not reuse failed request objects without reinitialization.

## Test Signals
Test response/no-response requests, unsequenced response rejection, queue saturation at `SSH_RTL_MAX_PENDING`, flush ordering, response timeout, packet failure propagation, event dispatch, host-TID filtering, cancellation before submit/in queue/in pending/after packet success, shutdown with queued and pending requests, and error-injected dropped responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_request_layer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_request_layer.h -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_request_layer.h

## Purpose
Defines the request transport layer API and state structure that sits above the SSH packet layer. It provides request submission/cancellation/lifecycle declarations and the event callback interface for the controller layer.

## Important APIs, Types, And Functions
`enum ssh_rtl_state_flags` defines `SSH_RTL_SF_SHUTDOWN_BIT`. `struct ssh_rtl_ops` exposes `handle_event()`. `struct ssh_rtl` embeds `struct ssh_ptl`, queue and pending lists, TX work, timeout reaper fields, and callback ops. Inline helpers include `ssh_rtl_get_device()` and `ssh_request_rtl()`. Declared APIs are `ssh_rtl_submit()`, `ssh_rtl_cancel()`, `ssh_rtl_init()`, `ssh_rtl_start()`, `ssh_rtl_flush()`, `ssh_rtl_shutdown()`, `ssh_rtl_destroy()`, and `ssh_request_init()`.

## Control Flow
Consumers initialize an `ssh_rtl` with serdev and ops, start the underlying packet TX/RX threads through `ssh_rtl_start()`, initialize individual `struct ssh_request` objects, set their data via serial-hub helpers, and submit them. Events received by the packet layer are lifted to `handle_event()` through the request-layer parser path.

## State And Persistence Behavior
All state is volatile runtime transport state. The request layer owns no persistent storage. The embedded PTL handles raw packet state; RTL adds request queueing, pending count, and response-timeout scheduling. `ssh_request_rtl()` recovers the containing request layer through the embedded packet's PTL pointer and returns `NULL` when a request has not yet been bound.

## Dependencies And Integration Points
Includes `linux/surface_aggregator/serial_hub.h`, `controller.h`, and `ssh_packet_layer.h`. The request layer is consumed by the Surface Aggregator controller implementation and any code using synchronous request helpers.

## Risks
The header exposes internals needed by the controller and tests, so structure layout changes affect embedding assumptions. `ssh_request_rtl()` depends on `packet.ptl` pointing to the embedded PTL of an `ssh_rtl`; using an `ssh_request` with a plain PTL would break the container cast. `rtl_info()` names its first macro argument `p` unlike adjacent macros, a minor readability hazard.

## Test Signals
Build checks should catch function signature drift. Runtime tests should validate `ssh_request_rtl()` before and after submission, shutdown rejection, flush semantics, event callback invocation, and proper teardown through `ssh_rtl_shutdown()` followed by `ssh_rtl_destroy()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_request_layer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/trace.h -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/trace.h

## Purpose
Defines ftrace tracepoints for SSAM/SSH protocol activity, packet/request state transitions, allocation/free events, pending counts, and error-injection events. It gives maintainers observability into the highly asynchronous packet and request transport layers.

## Important APIs, Types, And Functions
The header defines trace enums for SSH frame types, packet/request flags, and SSH target categories. Helper functions derive display-safe fields from packets: pointer UIDs, sequence IDs, request IDs, TID/SID/TC, CID, and IID. Event classes cover frames, commands, packets, packet status, requests, request status, allocation, free, pending counts, and data lengths. Concrete events include `ssam_rx_frame_received`, `ssam_rx_response_received`, `ssam_packet_submit`, `ssam_packet_complete`, `ssam_request_submit`, `ssam_request_complete`, timeout reap events, error-injection events, and cache/event-item allocation/free events.

## Control Flow
Transport code calls tracepoints at packet submit/resubmit/cancel/timeout/complete/release, request submit/cancel/timeout/complete, RX frame/command reception, timeout reaper execution, and error-injection branches. Trace event formatting converts raw bitfields and protocol IDs into compact symbolic strings for debugging.

## State And Persistence Behavior
Tracepoints persist no driver state. The only local transformation is `ssam_trace_ptr_uid()`, which derives a short non-address UID string from `%p` output to correlate events without exposing full kernel pointers. Trace output is consumed by ftrace/perf infrastructure depending on runtime tracing configuration.

## Dependencies And Integration Points
Depends on Linux tracepoint infrastructure, unaligned access helpers, and protocol definitions in `linux/surface_aggregator/serial_hub.h`. It must be included in exactly one trace-definition context with `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` outside the include guard, following kernel tracepoint conventions.

## Risks
Trace helpers inspect packet data lengths before reading protocol fields, but any mismatch in `SSH_COMMAND_MESSAGE_LENGTH()` offsets would produce misleading traces. The symbolic table for target categories must be kept in sync with protocol enum additions. Tracepoint format changes can break external scripts that parse trace output.

## Test Signals
Build with tracepoints enabled, enable each event class under `/sys/kernel/tracing/events/surface_aggregator`, run packet/request traffic, verify symbolic formatting for known TID/TC/flag combinations, and use error injection to confirm diagnostic tracepoints fire.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface3-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/surface3-wmi.c

## Purpose
Implements a Surface 3-specific WMI/platform driver that replaces the default ACPI lid handling with a WMI-backed lid switch tied to touchscreen hotplug behavior. It reports lid state via the input subsystem.

## Important APIs, Types, And Functions
`struct surface3_wmi` stores touchscreen and PNP0C0D ACPI devices, an ACPI hotplug context, and an input device. `s3_wmi_query_block()` serializes WMI queries with a global mutex and expects integer results. `s3_wmi_send_lid_state()` reports `SW_LID`. Discovery helpers scan platform devices for the lid ACPI node and SPI touchscreen child `NTRG`. Probe/remove are `s3_wmi_probe()` and `s3_wmi_remove()`, registered through a manually allocated platform device in module init.

## Control Flow
Module init creates a platform device and probes only on DMI-matched Microsoft Surface 3 systems. Probe scans platform devices, finds the SPI touchscreen and lid ACPI devices, trims the original ACPI lid device, registers an input lid switch, installs a hotplug notify callback on the touchscreen ACPI device, and sends the initial lid state. Hotplug notifications and resume both query WMI GUID `F7CC25EC-D20B-404C-8903-0ED4359C18AE` instance 0 and report the result.

## State And Persistence Behavior
Driver state is global singleton state (`s3_wmi` and `s3_wmi_pdev`) with one mutex around WMI query operations. It persists no state across unload or reboot. Remove clears the hotplug context and rescans the original ACPI lid device handle to restore default lid handling.

## Dependencies And Integration Points
Depends on ACPI, WMI, DMI, input, platform bus enumeration, SPI ACPI naming, and ACPI hotplug internals. Integrates with userspace through a normal input `SW_LID` device named `Lid Switch`.

## Risks
The driver assumes one Surface 3 platform and uses global mutable state. `s3_wmi_probe()` calls `acpi_bus_trim(s3_wmi.pnp0c0d_adev)` without explicitly validating that the lid ACPI device was found, so discovery failures could lead to a null dereference. The WMI query parser accepts only integer objects and logs buffer length conditionally. ACPI hotplug context manipulation is fragile across ACPI core changes.

## Test Signals
Test on Surface 3 DMI only, verify no binding elsewhere, check lid input events across attach/detach/resume, simulate missing SPI touchscreen or lid ACPI node, unload/reload and confirm PNP0C0D restoration, and validate WMI error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface3-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface3_power.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/surface3_power.c

## Purpose
Implements support for the Surface 3 `MSHW0011` power IC arrangement. It creates a secondary battery I2C client, services ACPI GSBus OperationRegion requests for battery/adapter data, polls for changes, and triggers ACPI DSM notifications for adapter, battery status, and battery info updates.

## Important APIs, Types, And Functions
Core state is `struct mshw0011_data`, holding adapter and battery I2C clients, notify mask, polling task, cached charging/full-capacity state, and trip point. ACPI buffer layouts include `struct bix`, `struct bst`, `struct gsb_command`, and `struct gsb_buffer`. Important functions are `mshw0011_notify()`, `mshw0011_bix()`, `mshw0011_bst()`, `mshw0011_adp_psr()`, `mshw0011_isr()`, `mshw0011_poll_task()`, `mshw0011_space_handler()`, and space-handler install/remove helpers.

## Control Flow
I2C probe allocates state for ACPI HID `MSHW0011`, treats the probed client as adapter `ADP1`, creates a battery client at ACPI index 1, queries DSM version/mask, starts a polling kthread, installs an ACPI GSBus address-space handler, and clears ACPI dependencies. The space handler decodes raw-process GSB buffers: adapter `PSR` queries read adapter status, battery commands serve `_STA`, `_BIX`, `_BST`, `_BTP`, or reject unsupported commands. The poll task wakes every two seconds, reads adapter status, battery status, and battery info, compares cached values, and notifies ACPI via DSM when changes are detected.

## State And Persistence Behavior
Cached state tracks last adapter charging state, battery charging state, trip point, and full-charge capacity for change detection. No persistent storage is written. The polling kthread is freezable and stopped on remove/error if running. The ACPI private handler data is allocated at install and freed on remove.

## Dependencies And Integration Points
Depends on ACPI DSM and GSBus OperationRegion APIs, I2C/SMBus reads, `i2c_acpi_new_device()`, kthreads/freezer, unaligned access, and packed ACPI battery structures. It integrates with ACPI battery devices indirectly by satisfying their OperationRegion accesses and by firing DSM notifications.

## Risks
Polling exits permanently on the first `mshw0011_isr()` error, which may make transient SMBus failures stop future notifications. `notify_mask` is assigned the boolean result of `mask == MSHW0011_EV_2_5_MASK`, so it becomes 0/1 rather than the returned mask value; this matches the code as written but is worth checking against firmware expectations. The space handler uses `value64` as a packed GSB buffer pointer and depends on exact ACPI layout. Unsupported battery commands return `AE_BAD_PARAMETER`, which may surface as firmware-visible errors.

## Test Signals
Test adapter plug/unplug, charge/discharge transitions, BIX full-capacity changes, serial-number read `-EREMOTEIO`, ACPI battery methods backed by GSBus, remove while poll task runs, suspend/freezer behavior, and transient SMBus error recovery expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface3_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_acpi_notify.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_acpi_notify.c

## Purpose
Implements the Surface ACPI Notify (SAN) shim. It translates ACPI GSB OperationRegion requests into SSAM controller requests, relays SSAM battery/thermal events back into ACPI `_DSM` notifications, and exposes a notifier interface for ACPI-originated discrete GPU events.

## Important APIs, Types, And Functions
`struct san_data` stores device, bound SSAM controller, ACPI connection info, and battery/thermal SSAM notifiers. The exported dGPU interface is `san_client_link()`, `san_dgpu_notifier_register()`, and `san_dgpu_notifier_unregister()`. Event helpers include `san_evt_bat_*()`, `san_evt_tmp_*()`, delayed battery work, and `san_acpi_notify_event()`. GSB handlers include `san_opreg_handler()`, `san_rqst()`, `san_rqsg()`, `san_etwl()`, and response helpers. Driver setup uses `san_probe()`, `san_remove()`, and a global `san_wq`.

## Control Flow
Probe binds to the SSAM controller, creates ACPI consumer device links for devices depending on the SAN ACPI node, allocates state, installs a GSBus address-space handler, registers SSAM BAT/TMP event notifiers, exposes the RQSG provider device, and clears ACPI dependencies. ACPI RQST buffers become synchronous SSAM requests with optional response and retry. RQSG buffers become `san_dgpu_event` notifications to registered clients. ETWL buffers log firmware messages. SSAM BAT/TMP events call ACPI DSM functions, with delays for adapter and battery-state updates to avoid stale ACPI battery data.

## State And Persistence Behavior
SAN keeps only runtime state. The dGPU notifier singleton uses an rwsem-protected provider device pointer and blocking notifier chain. Delayed battery work allocates a copy of the event payload and is flushed on remove after notifier unregister. No persistent state is written.

## Dependencies And Integration Points
Depends on ACPI DSM/GSBus APIs, Surface Aggregator controller sync requests, SSAM event notifiers, device links, workqueues, notifier chains, and power-management state. It binds ACPI HID `MSHW0091` and acts as a bridge for ACPI battery, thermal, DPTF, and GPU-related firmware methods.

## Risks
OperationRegion parsing trusts firmware-provided lengths after validation; off-by-one mistakes can affect ACPI communication. `san_set_rqsg_interface_device(NULL)` returns `-EBUSY` because the helper only sets when no device and `dev` is non-null; remove ignores the return, so the global provider pointer may not actually be cleared in this source. Suspended-device fixup special-cases BAS command `0x0d`; other ACPI requests while suspended return an encoded error. Delayed work uses copied flexible event storage and must remain consistent with `struct ssam_event` layout.

## Test Signals
Test ACPI RQST success/error/response truncation behavior, ETWL logging, RQSG notifier registration and client device links, BAT/TMP event DSM calls, delayed ADP/BST behavior, remove/unload clearing global provider state, suspended BAS fixup, and retry behavior on transient SSAM errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_acpi_notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_cdev.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_cdev.c

## Purpose
Provides a misc character device `/dev/surface/aggregator` for debugging and development access to the SSAM EC. Userspace can issue synchronous SSAM requests, enable/disable events, register observer notifiers, and read event records from per-client FIFOs.

## Important APIs, Types, And Functions
`struct ssam_cdev` tracks controller binding, miscdevice, shutdown flag, and open clients. `struct ssam_cdev_client` tracks notifier registrations, read/write locks, a 4 KiB FIFO, wait queue, and fasync state. Notifier functions translate `struct ssam_event` to `struct ssam_cdev_event`. IOCTL handlers are `ssam_cdev_request()`, notifier register/unregister, event enable/disable. File ops implement open, release, ioctl, read, poll, and fasync. Platform probe/remove create and destroy the misc device.

## Control Flow
Module init creates a platform device and registers a platform driver. Probe binds to the SSAM controller and registers the misc device. Open allocates a client and attaches it to the client list unless shutdown is set. IOCTLs take the cdev rwsem, reject shutdown, then issue controller operations or notifier changes. Incoming SSAM events are copied into the client's FIFO and wake blocking, polling, and async readers. Release unregisters all client notifiers, detaches the client, and frees it. Remove marks shutdown, unregisters all notifiers for live clients, signals readers, nulls controller pointers under lock, deregisters the misc device, and drops the cdev kref.

## State And Persistence Behavior
Each open file has independent in-memory notifier state and event FIFO. Events are dropped when the FIFO lacks room. No data persists across close or module unload. The cdev object is kref-managed so lingering file descriptors can release safely after device removal, but controller access is blocked once shutdown is set and `ctrl` is nulled.

## Dependencies And Integration Points
Depends on miscdevice, uaccess, kfifo, fasync, poll, Surface Aggregator cdev UAPI, controller APIs, SSAM notifier APIs, and protocol event target-category helpers. It is intentionally an observer and does not consume events from functional drivers.

## Risks
The debug interface can send arbitrary EC requests and enable/disable events, so it should remain appropriately permissioned by device node policy. Large user-provided payload/response lengths are bounded by UAPI field widths but can still allocate sizable buffers. `ssam_cdev_notifier_unregister_all()` loops all `SSH_NUM_EVENTS` and ignores unregister errors, which is reasonable for cleanup but may hide inconsistencies. Event FIFO overflow drops events without backpressure.

## Test Signals
Test open/read/poll/fasync, blocking read wake on event and on removal, IOCTL request with and without response, invalid user pointers, notifier duplicate/unregister-missing cases, event FIFO overflow, concurrent clients, remove with open descriptors, and event enable/disable calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_cdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_hub.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_hub.c

## Purpose
Implements SSAM subsystem hub drivers for dynamically present device groups, especially KIP keyboard-cover devices and Surface Book base devices. It registers/removes SSAM child devices when hub connection state changes.

## Important APIs, Types, And Functions
Generic hub state is represented by `enum ssam_hub_state`, `enum ssam_hub_flags`, `struct ssam_hub`, and `struct ssam_hub_desc`. Core functions are `ssam_hub_update_workfn()`, `ssam_hub_update()`, `ssam_hub_probe()`, and `ssam_hub_remove()`. Base hub support queries BAS opmode via `ssam_bas_query_opmode()` and handles connection CID `0x0c`. KIP hub support queries KIP state via `__ssam_kip_query_state()` and handles connection CID `0x2c`.

## Control Flow
Probe obtains match-data descriptor, allocates a hub, configures a high-priority event notifier, registers it, and schedules immediate update work. Update work calls the descriptor's `get_state()`, handles hot-remove correction, compares previous and current state, and either registers child clients with `ssam_device_register_clients()` or removes them with `ssam_remove_clients()`. Notifier callbacks validate event command and payload, then schedule update work immediately for disconnect or after a connect delay for attach.

## State And Persistence Behavior
The hub stores current state, hot-removed flag, delayed work, connect delay, and notifier registration. Child-device state lives in the SSAM device core. No persistent storage is used. On disconnect, existing children are marked hot-removed in reverse order before removal so re-added devices can be distinguished.

## Dependencies And Integration Points
Depends on `linux/surface_aggregator/device.h`, SSAM event notifiers, synchronous request helper macros, delayed work, and SSAM child registration/removal helpers. It binds virtual SSAM hub devices via `SSAM_VDEV(HUB, SAM, ...)`.

## Risks
Correctness depends on firmware connection events and query commands agreeing. The hot-remove race mitigation reschedules work when a disconnect/connect pair is collapsed, but unusual event loss can still delay child registration. Base hub notifier deliberately returns unhandled so detachment-system drivers can consume the event; changing that would break event sharing.

## Test Signals
Test initial connected/disconnected query, KIP cover attach/detach, Surface Book base attach/detach, rapid remove/re-add races, resume update scheduling, child devices marked hot-removed before removal, delayed connect registration, and notifier return semantics with other drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_hub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_registry.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_registry.c

## Purpose
Provides the SSAM platform/meta-hub registry for Surface devices whose SSAM clients cannot be auto-discovered. It defines software nodes for virtual SSAM devices and maps ACPI/OF platform IDs to model-specific node groups.

## Important APIs, Types, And Functions
The file defines many `struct software_node` instances following the `ssam:dd:cc:tt:ii:ff` naming scheme: root, KIP/base hubs, batteries, AC adapter, performance profile, thermal sensors, fan, tablet switches, DTX, and HID functions. Node groups cover generations and models including Surface Book, Surface Laptop, Surface Laptop Studio, Surface Laptop Go, Surface Pro Intel, and ARM/QCOM variants. Driver functions are `ssam_platform_hub_probe()` and `ssam_platform_hub_remove()`.

## Control Flow
Probe selects a node group from ACPI match data or OF machine match data, binds to the SSAM controller for ordering and access, registers the software-node group, sets the root software node as the platform device's secondary fwnode, and calls `__ssam_register_clients()` to instantiate SSAM child devices. Remove reverses this by removing clients, clearing the secondary fwnode, and unregistering the node group.

## State And Persistence Behavior
The registry stores only static const node definitions and the selected node-group pointer in platform driver data. No runtime state is persisted. Child-device lifetime is tied to software-node registration and platform hub binding.

## Dependencies And Integration Points
Depends on ACPI IDs, OF compatible matching, software nodes, property entries, platform bus, and SSAM device registration helpers. It is the source of virtual devices later consumed by drivers such as battery, HID, hub, tablet switch, performance profile, fan, and DTX drivers.

## Risks
Model mapping mistakes can instantiate missing, duplicate, or wrong SSAM clients. Some nodes with identical names intentionally appear under different parents; parent relationships must be preserved. New Surface models require careful ACPI/OF ID assignment and selection of fan/sensor/tablet-switch variants. Probe registers nodes before child creation and must clean up correctly on partial failure, which it does for missing root and child-registration failure.

## Test Signals
Test each ACPI ID and OF compatible maps to the intended node group, software nodes register/unregister cleanly, child devices appear with expected modaliases, parented hub children register only under their hub, probe defer occurs when controller is absent, and remove unloads all child clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_registry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_tabletsw.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_tabletsw.c

## Purpose
Implements SSAM tablet-mode switch devices. It supports KIP cover-state based tablet mode and POS posture-source based tablet mode, reports `SW_TABLET_MODE` through the input subsystem, and exposes the current textual state via sysfs.

## Important APIs, Types, And Functions
Generic framework types are `struct ssam_tablet_sw_state`, `struct ssam_tablet_sw_ops`, `struct ssam_tablet_sw`, and `struct ssam_tablet_sw_desc`. Core lifecycle functions are `ssam_tablet_sw_probe()`, `ssam_tablet_sw_remove()`, `ssam_tablet_sw_update_workfn()`, resume handling, and `state_show()`. KIP-specific functions map cover states and query command `0x1d`. POS-specific functions query source lists, select a source, query posture for that source, map cover/SLS postures, and handle posture-change events. The module parameter `tablet_mode_in_slate_state` controls SLS slate behavior.

## Control Flow
Probe gets descriptor match data, allocates state, reads initial state through descriptor ops, allocates/registers an input device, registers a sequenced SSAM event notifier, creates the `state` sysfs attribute, and schedules an update to catch missed setup-time events. Notifier callbacks validate command IDs and schedule update work. Update work re-queries firmware, compares source/state with cached values, updates state, maps it to tablet mode, and reports/input-syncs `SW_TABLET_MODE`.

## State And Persistence Behavior
Runtime state caches the latest source and state values plus input device and notifier registration. No persistent storage exists. Sysfs reads return the cached state name, not a fresh firmware query. Work is canceled and notifier/sysfs removed on driver remove.

## Dependencies And Integration Points
Depends on SSAM device/controller APIs, synchronous request helpers, SSAM event notifiers, input subsystem, sysfs attribute groups, unaligned access, and module parameters. It binds `SSAM_SDEV(KIP, SAM, 0x00, 0x01)` and `SSAM_SDEV(POS, SAM, 0x00, 0x01)`, which are instantiated by the registry for relevant models.

## Risks
Unknown posture/source values default to tablet mode for safety but may produce unexpected userspace behavior. POS currently warns if more than one posture source exists and uses the first source; future multi-source devices need policy changes. Event payload-size mismatches only warn, because state is always re-queried. Sysfs state can be stale if a firmware query fails during update.

## Test Signals
Test KIP states disconnected/closed/laptop/folded/book, POS cover and SLS states, module parameter behavior for slate, event-triggered updates, resume re-query, sysfs state output, unknown states, malformed event payload lengths, and probe/remove notifier cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_tabletsw.c -->
