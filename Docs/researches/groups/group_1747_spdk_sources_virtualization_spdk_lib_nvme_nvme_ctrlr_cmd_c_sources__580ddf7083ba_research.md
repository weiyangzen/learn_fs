# Group Research: group_1747_spdk_sources_virtualization_spdk_lib_nvme_nvme_ctrlr_cmd_c_sources__580ddf7083ba

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/spdk` is included in subset A. Every source file listed for this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_ctrlr_cmd.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_ctrlr_cmd.c

This file implements SPDK NVMe controller-level command wrappers. It builds and submits raw I/O commands, raw admin commands, Identify, namespace management, feature get/set, log page retrieval, aborts, firmware operations, security send/receive, sanitize, and directive send/receive.

Raw I/O entry points allocate `nvme_request` objects on the supplied qpair and copy a caller-provided `spdk_nvme_cmd` into the request. `spdk_nvme_ctrlr_io_cmd_raw_no_payload_build()` is PCIe-only and uses a no-payload request. `spdk_nvme_ctrlr_cmd_io_raw()` uses a contiguous payload. The metadata variants compute metadata length from the command NSID namespace geometry when a metadata buffer is present, and the SGL raw path rejects missing reset/next-SGE callbacks.

Admin commands are serialized with `nvme_ctrlr_lock()`. Most allocate either a user-copy request or null request on `ctrlr->adminq`, fill opcode-specific CDWs, submit through `nvme_ctrlr_submit_admin_request()`, then unlock. User-copy direction is significant: Identify, Get Features, Get Log Page, Security Receive, and Directive Receive are controller-to-host; Set Features, namespace attach/detach/create, firmware image download, Security Send, and Directive Send are host-to-controller.

Identify support is centralized in `nvme_ctrlr_cmd_identify()`, which sets CNS, CNTID, NSID, and CSI. Namespace management helpers wrap Namespace Attachment and Namespace Management opcodes for attach, detach, create, and delete. Format, doorbell-buffer config, Number of Queues, async event config, and Host Identifier are small command builders on top of the same admin submission path.

Log page retrieval validates nonzero payload size and 4-byte-aligned offset. If an offset is requested, the controller must advertise extended data support through `ctrlr->cdata.lpa.lpeds`. The function converts byte count to NUMD, splits offset into LPOL/LPOU, accepts caller-supplied extra CDW fields, and has a simpler wrapper that passes zeros for the extension fields.

Abort handling is the most stateful part of the file. `_nvme_ctrlr_submit_abort_request()` limits concurrent aborts by the controller ACL value and queues excess aborts in `ctrlr->queued_aborts`. Abort completions decrement `outstanding_aborts` and retry queued aborts unless the controller/admin qpair is failing. `spdk_nvme_ctrlr_cmd_abort_ext()` creates a parent abort request, iterates outstanding requests on a qpair, adds child abort commands for requests matching a callback argument, separately aborts queued requests with the same callback argument, and completes the parent when all child aborts finish.

The firmware, security, sanitize, and directive helpers are thin but preserve NVMe wire encodings: firmware download uses NUMD and DWORD offset, security commands split SPSP into fields and use payload size in CDW11, sanitize copies the sanitize structure into CDW10, and directives encode DOPER/DTYPE/DSPEC plus optional CDW12/CDW13.

Important invariants are request ownership, admin lock coverage, correct user-copy direction, and abort accounting. Any change to abort paths must maintain `outstanding_aborts`, queued abort retry behavior, child-parent completion, and request freeing. Metadata raw commands assume a valid namespace and nonzero sector size when metadata is supplied.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_ctrlr_cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_ctrlr_ocssd_cmd.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_ctrlr_ocssd_cmd.c

This file provides controller-level Open-Channel SSD helpers.

`spdk_nvme_ctrlr_is_ocssd_supported()` gates support on `NVME_QUIRK_OCSSD`, then applies a CNEX Labs/QEMU-specific check: it finds the first active namespace, fetches namespace vendor-specific identify bytes, and returns true only when `vendor_specific[0] == 0x1`. The comment notes there is no standardized OCSSD detection rule and vendors may need different conditions.

`spdk_nvme_ocssd_ctrlr_cmd_geometry()` sends the OCSSD geometry admin command. It requires a non-null payload exactly sized as `struct spdk_ocssd_geometry_data`, allocates a user-copy admin request in controller-to-host direction, sets opcode `SPDK_OCSSD_OPC_GEOMETRY` and NSID, submits under `nvme_ctrlr_lock()`, and returns allocation or submission status.

The main dependencies are `spdk/nvme_ocssd.h`, controller quirks, namespace lookup, vendor-specific namespace data, and normal admin request submission. The detection path is intentionally heuristic; adding OCSSD device support likely means extending this vendor-specific logic.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_ctrlr_ocssd_cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_cuse.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_cuse.c

This file exposes SPDK NVMe controllers and namespaces as Linux CUSE character devices compatible with common NVMe ioctls. It owns CUSE device objects, a detached FUSE polling thread, ioctl dispatch, passthrough command marshalling, namespace read/write ioctl support, namespace device creation/removal, controller index claiming, and public CUSE registration APIs.

`struct cuse_device` represents a controller or namespace CUSE node. Controller devices have `nsid == 0` and own a tailq of namespace devices. Namespace devices point back to their controller device. The global state includes a controller-device list, a bit array of claimed controller indexes, a pending-device queue, an active-device queue, an fd group, and an eventfd used to notify the CUSE thread of new sessions.

Passthrough ioctl handling maps Linux `struct nvme_passthru_cmd` into `struct spdk_nvme_cmd`. `cuse_nvme_passthru_cmd()` uses libfuse ioctl retry iovecs to make user buffers accessible, limits aggregate request size to `FUSE_MAX_SIZE`, rejects bidirectional transfers, copies host-to-controller payloads into DMA buffers, and queues execution through `nvme_io_msg_send()`. Execution runs on the controller’s external I/O message qpair: admin ioctl commands go through `spdk_nvme_ctrlr_cmd_admin_raw()`, while namespace I/O passthrough uses `spdk_nvme_ctrlr_cmd_io_raw_with_md()`.

Reset and rescan ioctls are controller-only. Reset queues either `spdk_nvme_ctrlr_reset()` or `spdk_nvme_ctrlr_reset_subsystem()` through the I/O message bridge. Rescan iterates active namespaces and calls `nvme_ns_identify()` without failing the ioctl if a namespace identify fails.

`NVME_IOCTL_SUBMIT_IO` on namespace devices supports read and write opcodes. The file uses the namespace sector size and metadata size to build retry iovecs, allocates DMA data and optional metadata buffers, then submits `spdk_nvme_ns_cmd_read_with_md()` or `spdk_nvme_ns_cmd_write_with_md()` through the external qpair. Completion callbacks translate NVMe completion status into the FUSE ioctl result and return read data/metadata when needed.

Other namespace ioctls include `NVME_IOCTL_ID`, `BLKPBSZGET`, `BLKSSZGET`, `BLKGETSIZE`, and `BLKGETSIZE64`. As read, `BLKGETSIZE64` replies with `spdk_nvme_ns_get_num_sectors(ns)` rather than a byte count; that is worth checking before relying on block-device-size compatibility.

CUSE session creation uses `cuse_lowlevel_setup()` with unrestricted ioctl support and per-device low-level ops. The CUSE thread polls the SPDK fd group, receives FUSE buffers, processes sessions, handles session exit, and frees devices only after `force_exit` sessions are torn down. New sessions are added by queueing them on `g_pending_device_head` and writing the eventfd.

Controller device startup claims a stable `spdk/nvme<N>` name by locking `/var/tmp/spdk_nvme_cuse_lock_<N>` with `fcntl()`, recording the owner pid in an mmap’d int, setting the started bit, creating the controller CUSE session, and creating namespace sessions for all active namespaces. Namespace updates remove disappeared namespace devices and add newly active namespaces.

Public APIs are `spdk_nvme_cuse_register()`, `spdk_nvme_cuse_unregister()`, `spdk_nvme_cuse_update_namespaces()`, `spdk_nvme_cuse_get_ctrlr_name()`, and `spdk_nvme_cuse_get_ns_name()`. Registration is primary-process-only, registers the CUSE producer with `nvme_io_msg_ctrlr_register()`, starts the CUSE thread if needed, and starts the controller device. Unregister stops devices and unregisters the I/O message producer.

Key risks are asynchronous lifetime and lock ordering: FUSE requests own `cuse_io_ctx` until NVMe completion, CUSE devices are removed from logical lists before the CUSE thread frees them, and producer stop/update callbacks interact with both controller locks and `g_cuse_mtx`. The ioctl retry paths also depend on correct iovec sizing to prevent oversized FUSE requests.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_cuse.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_cuse.h -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_cuse.h

This small private header declares the internal CUSE registration interface used by the NVMe library.

It includes `spdk/nvme.h` for `struct spdk_nvme_ctrlr` and declares:

- `nvme_cuse_register(struct spdk_nvme_ctrlr *ctrlr, const char *dev_path)`
- `nvme_cuse_unregister(struct spdk_nvme_ctrlr *ctrlr)`

As read, these prototypes differ from the public functions implemented in `nvme_cuse.c`, which are named `spdk_nvme_cuse_register()` and `spdk_nvme_cuse_unregister()` and do not take a `dev_path`. This header may be stale or used by older integration code; any caller should be checked before relying on it.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_cuse.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_discovery.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_discovery.c

This file implements asynchronous retrieval of the NVMe-oF discovery log page with generation-counter consistency checking.

`spdk_nvme_ctrlr_get_discovery_log_page()` allocates a discovery context plus an initial one-page discovery log buffer, then submits Get Log Page for `SPDK_NVME_LOG_DISCOVERY`. `discovery_log_header_completion()` validates that the completion is not an error, checks `recfmt == 0`, records the starting `genctr`, reads `numrec`, reallocates the buffer to hold all advertised entries when needed, and submits a second Get Log Page for the full page.

After the full page is fetched, `get_log_page_completion()` submits another small Get Log Page request to read the latest generation counter into `end_genctr`. `get_log_page_completion_final()` compares `start_genctr` and `end_genctr`: if they match, the callback receives the allocated log page; if they differ, the page is freed and retrieval restarts by calling `spdk_nvme_ctrlr_get_discovery_log_page()` again.

Errors are delivered through the caller callback with either a completion pointer or an integer error and null page. Memory ownership is important: on success the callback receives `ctx->log_page`; on failure or restart the file frees the buffer itself. The implementation assumes callers understand the asynchronous callback contract and that a changing discovery controller may force repeated retries.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_discovery.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_fabric.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_fabric.c

This file contains transport-independent NVMe-oF helpers for fabrics property access, discovery probing, discovery-controller scanning, and fabrics qpair connect.

Property Set/Get helpers build `SPDK_NVME_OPC_FABRIC` commands with `SPDK_NVMF_FABRIC_COMMAND_PROPERTY_SET` or `PROPERTY_GET`, encode register offset and 4- or 8-byte size, then submit through `spdk_nvme_ctrlr_cmd_admin_raw()`. Synchronous wrappers allocate `nvme_completion_poll_status`, wait on the admin qpair, decode get responses, and return register values. Asynchronous wrappers allocate `nvme_fabric_prop_ctx`, call a register callback with the set value or decoded get value, and free the context on completion.

Discovery probing converts each `spdk_nvmf_discovery_log_page_entry` into a transport ID. `nvme_fabric_discover_probe()` skips discovery referrals and unknown subtypes, checks that the transport is available, validates SUBNQN null termination, trims padded `traddr` and `trsvcid`, copies discovery priority, and calls `nvme_ctrlr_probe()` for NVMe subsystem entries.

`nvme_fabric_ctrlr_scan()` distinguishes direct subsystem connects from discovery-controller scans. Non-discovery NQNs are probed directly. Discovery NQN scans construct a temporary discovery controller, drive initialization until ready, identify controller data, and either attach it directly for `spdk_nvme_connect()` style direct connect or call `nvme_fabric_ctrlr_discover()` then destruct the discovery controller. `nvme_fabric_ctrlr_discover()` reads the discovery log in 4 KiB chunks, validates record format, handles the header-entry offset for the first buffer, and probes each entry.

`nvme_fabric_qpair_connect_async()` builds a Fabrics Connect command using the qpair’s reserved request. It validates queue size, allocates DMA connect data and a poll status object, fills QID, SQSIZE, KATO, host ID, host NQN, and subsystem NQN, uses CNTLID `0xFFFF` for admin queues or the controller CNTLID for I/O queues, submits the reserved request, and installs an optional timeout. `nvme_fabric_qpair_connect_poll()` polls for completion, logs transport identity on failure, copies CNTLID from admin connect responses, records authentication-required flags, and cleans up DMA status memory unless timed out. `nvme_fabric_qpair_connect()` is the synchronous loop around async plus poll.

The main invariants are reserved request ownership, timeout memory ownership, and the fact that zone/fabrics authentication state is updated from the connect response before normal qpair use. Discovery parsing also treats malformed SUBNQN and unsupported transport types as skip conditions rather than fatal scan errors.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_fabric.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_internal.h -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_internal.h

This is the central private header for SPDK’s NVMe library. It defines controller quirks, queue/request defaults, payload/request structures, qpair and controller state, namespace state, logging macros, controller initialization states, process tracking, transport abstractions, request allocation/completion helpers, and internal function declarations shared across the NVMe implementation.

The quirk section documents vendor and platform exceptions, including Intel latency log support, readiness/init delays, driver-assisted striping, read-zero-after-deallocate, Identify CNS limitations, OCSSD detection, VMware shutdown behavior, queue-size adjustments, max PCI access width, OPAL security false positives, DSM SGL avoidance, MDTS metadata behavior, forced PRP use, admin queue sizing, and MSI-X vector count differences.

`struct nvme_payload` represents contiguous, SGL-callback, or iovec payloads, with data size, payload offset, metadata pointer/size, metadata offset, and optional extended I/O options. `struct nvme_request` wraps an NVMe command, retry and timeout state, payload type, qpair reservation flag, callback data, qpair pointer, admin pid/completion storage, optional accel sequence, and cold split-request fields for parent/child tracking. The layout deliberately keeps split fields later to avoid touching extra cachelines on normal I/O.

Qpair state includes connection/enabling states, deletion-in-completion flags, transport failure reasons, request free/queued lists, poll-group membership, error injection lists, per-process ownership, a reserved Fabrics Connect request, fabric connect poll status, queued-abort list, request buffer, and in-band authentication state. Poll groups group transport poll groups and hold accel function tables, fd-group interrupt support, and disconnected-qpair signaling.

`struct spdk_nvme_ns` stores controller pointer, sector and extended LBA sizes, metadata size, PI type/format, max I/O sectors with and without metadata, stripe boundaries, NSID, flags, active/identify-pending state, CSI, descriptor list, ANA data, Identify Namespace data, and a union of command-set-specific identify data for ZNS, KV, or NVM.

The controller state machine enum covers the full initialization sequence: optional delay, admin connect, register reads, disable/enable transitions, admin queue reset, Identify controller and IOCS data, command-effects log retrieval, queue count setup, active namespace and per-namespace identify, supported log/features, host behavior/doorbell/host ID setup, transport-ready, ready, error, and disconnected states. `struct spdk_nvme_ctrlr` then holds hot-path flags/state/page-size/max-SGE fields, reset/failure flags, namespace tree, transport ID, CAP/VS, keepalive timing, supported log/features arrays, max transfer size, adminq, doorbell buffers, identify data, qpair lists, options, quirks, process list, queued aborts, external I/O message ring/qpair, ANA data, zone append size, PMR size, boot partition and firmware download state, register completions, and authentication counters.

The header also defines process tracking for multiprocess access, probe/detach contexts, global driver state, and helper macros such as `nvme_ns_cmd_get_ext_io_opt()` for ABI-compatible optional fields in extended I/O options.

Inline helpers cover qpair classification, robust mutex lock/unlock, controller lock depth tracking, namespace data access, request initialization for contiguous/SGL/iov payloads, request allocation from a qpair free list, null and contiguous request allocation, request freeing, completion callback invocation with accel abort and error injection, user-copy cleanup, abort matching, qpair state setting, child request add/remove/free, and child completion aggregation.

The declaration surface is broad: controller construction/destruction/init/fail, admin submission and register access, qpair lifecycle/submission/abort/resubmit, namespace identify/clear and zone append internals, fabrics register/connect/discovery/authentication, ANA parsing, transport-specific controller/qpair/poll-group hooks, multiprocess refcounting, timeout checks, quirk lookup, address parsing, default Host NQN, and transport enumeration.

Key invariants are cache-sensitive request layout, correct qpair outstanding request accounting, reserved Fabric Connect request handling, split-child parent completion semantics, controller lock depth balance, multiprocess locking rules, and ABI-safe use of optional extended I/O option fields.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_io_msg.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_io_msg.c

This file implements an external I/O message bridge that lets modules such as CUSE queue work into a controller-owned SPDK I/O context.

`nvme_io_msg_send()` allocates `struct spdk_nvme_io_msg`, fills controller, NSID, function pointer, and argument, then enqueues it on `ctrlr->external_io_msgs` under `external_io_msgs_lock`. The ring is multi-producer/single-consumer. Enqueue failure frees the message and returns `-ENOMEM`.

`nvme_io_msg_process()` is the single-consumer polling function. It only runs in the primary process, returns early when the ring or external qpair is unavailable or reset preparation is active, applies deferred producer updates, processes completions on `external_io_msgs_qpair`, dequeues up to eight messages, calls each message function, frees the message, and returns the number processed.

Producer registration is tracked with `struct nvme_io_msg_producer` entries in `ctrlr->io_producers`. `nvme_io_msg_ctrlr_register()` rejects null producers and duplicates, initializes the mutex, creates a 65536-entry SPDK ring, allocates an I/O qpair, and inserts the first producer. If producers are already registered or the controller is resetting, it only appends the producer because messaging is already started or will be handled later.

`nvme_io_msg_ctrlr_update()` calls every registered producer’s `update()` callback in the primary process. If invoked from a secondary process, it sets `needs_io_msg_update` so the primary-side process loop performs the update later. `nvme_io_msg_ctrlr_detach()` stops all producers, removes them, frees the ring and external qpair, and destroys the mutex. `nvme_io_msg_ctrlr_unregister()` removes a specific producer and detaches the infrastructure when the producer list becomes empty.

Important invariants are single-threaded processing per controller, primary-process ownership of the qpair/ring consumer, correct ring lifetime relative to producer callbacks, and lock ordering when unregistering triggers detach and producer `stop()` callbacks while controller state is being modified.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_io_msg.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_io_msg.h -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_io_msg.h

This private header declares the NVMe external I/O message bridge.

It defines `spdk_nvme_io_msg_fn`, a callback taking controller, NSID, and opaque argument. `struct spdk_nvme_io_msg` stores one queued callback invocation. `struct nvme_io_msg_producer` names a producer and provides `update()` and `stop()` hooks, linked through the controller’s producer list.

The declared functions are `nvme_io_msg_send()`, `nvme_io_msg_process()`, `nvme_io_msg_ctrlr_register()`, `nvme_io_msg_ctrlr_unregister()`, `nvme_io_msg_ctrlr_detach()`, and `nvme_io_msg_ctrlr_update()`.

The header documents the central contract: `nvme_io_msg_process()` is nonblocking, must be polled by an SPDK thread, and each controller must be polled by only one thread at a time. This is what makes external ioctl-style producers safe to integrate with SPDK NVMe request completion.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_io_msg.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_kv.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_kv.c

This file implements SPDK helpers for NVMe Key Value command set namespaces.

The data accessors return command-set-specific identify data: `spdk_nvme_kv_ns_get_data()` returns `ns->nsdata_kv`, and `spdk_nvme_kv_ctrlr_get_data()` returns `ctrlr->cdata_kv`.

`nvme_kv_cmd_set_key()` encodes keys into command dwords. It asserts the key is non-null and within the allowed length range, records key length in CDW11, copies the first up to 8 key bytes into CDW2/CDW3, and copies the next up to 8 key bytes into CDW14/CDW15.

`nvme_kv_cmd_with_data()` builds Store, Retrieve, and List-style requests with contiguous payloads. It validates key and data pointers/lengths, allocates a contiguous request, sets opcode and NSID, sets CDW10 value/host-buffer size, stores request options in CDW11, encodes the key, and submits. `nvme_kv_cmd_without_data()` does the same for Delete and Exist without a payload.

Public commands are `spdk_nvme_kv_store()`, `spdk_nvme_kv_retrieve()`, `spdk_nvme_kv_delete()`, `spdk_nvme_kv_exist()`, and `spdk_nvme_kv_list()`. List allows a null start key only when start key length is zero, validates non-null output buffer and length, and encodes an optional start key.

The file assumes KV key sizes match SPDK constants and uses contiguous payload allocation only. It does not check whether the namespace CSI is KV; callers are expected to use it only with KV-capable namespaces.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_kv.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_ns.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_ns.c

This file owns NVMe namespace identify processing, namespace geometry/feature derivation, public namespace accessors, namespace identification descriptor parsing, command-set-specific identify data management, ANA accessors, and namespace clearing.

`nvme_ns_set_identify_data()` recalculates derived namespace state after Identify Namespace data changes. It marks identify complete, determines active state from nonzero NSID and nonzero NCAP, clears inactive namespaces, selects the active LBA format, computes sector size, extended LBA size, metadata size, max I/O sector counts, stripe boundary, namespace flags, PI type/format, and optional quirks such as MDTS excluding metadata and Intel striping. Controller identify capabilities determine deallocate, compare, flush, write zeroes, write uncorrectable, and reservation support.

The synchronous identify helpers allocate `nvme_completion_poll_status`, issue Identify commands through `nvme_ctrlr_cmd_identify()`, wait for admin completion, and install data on success. Separate helpers fetch base namespace data, ZNS-specific namespace data, NVM-specific namespace data when extended LBA format data is supported, KV-specific namespace data, and the namespace identification descriptor list. Descriptor-list retrieval is skipped for older controllers without IOCS support and for controllers with the Identify CNS quirk.

Public accessors expose NSID, active state, controller pointer, max transfer size, sector sizes, number of sectors, byte size, flags, PI type/format, metadata size, active format index, LBA format data, vendor-specific identify bytes, base identify data, NVM-specific identify data, deallocated-block read behavior, optimal I/O boundary, NGUID, UUID, CSI, ANA group ID, and ANA state. The deprecated format-index accessor logs a deprecation warning and delegates to the active-format helper.

Descriptor parsing walks the 4096-byte NS ID descriptor list using fixed four-byte descriptor headers and NIDL lengths. It returns null for zero-length terminators or malformed descriptors that overrun the buffer. UUID, NGUID, EUI64, and CSI descriptors are length-checked. NGUID and EUI64 descriptor values backfill Identify Namespace fields only when the identify fields are all zero; mismatches are logged and Identify Namespace values win.

Command-set-specific data is stored in a union pointer and freed through CSI-aware helpers. `nvme_ns_has_supported_iocs_specific_data()` returns true for ZNS and KV, and for NVM only when controller ELBAS is supported. Unsupported CSI values are logged and treated as unsupported.

`nvme_ns_identify()` performs the overall sequence: base Identify Namespace, inactive namespace shortcut, ID descriptor list, and supported IOCS-specific namespace data when multiple I/O command sets are enabled. `nvme_ns_clear()` zeroes identify data and descriptor list, frees IOCS-specific data, resets geometry, flags, CSI, active state, and identify-pending state.

Important invariants are that derived geometry must match active LBA format and metadata placement, descriptor values must not silently override nonzero Identify Namespace IDs, and IOCS-specific data lifetime must be cleared before replacing namespace state.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_ns.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_ns_cmd.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_ns_cmd.c

This file implements namespace I/O command construction and submission for reads, writes, compares, zone append, write zeroes, verify, write uncorrectable, dataset management, copy, flush, reservations, and I/O management send/receive. It supports contiguous buffers, callback-driven SGLs, iovec payloads, metadata buffers, protection information tags, and extended I/O options.

The core helpers compute transfer sizing and splitting. PRACT with extended LBA, PI, and 8-byte metadata can exclude metadata from host transfer size. `_nvme_get_host_buffer_sector_size()` and `_nvme_get_sectors_per_max_io()` choose sector sizing with or without metadata based on that rule. `nvme_ns_map_failure_rc()` maps allocation failures to `-EINVAL` when the requested I/O would need too many child requests for queue depth.

Requests are initialized through `_nvme_ns_cmd_rw_req_init_contig()`, `_nvme_ns_cmd_rw_req_init_sgl()`, and `_nvme_ns_cmd_rw_req_init_iov()`, each filling payload size, metadata size, offsets, callback state, and optional accel sequence. `_is_io_flags_valid()` enforces `SPDK_NVME_IO_FLAGS_VALID_MASK`, and `_is_accel_sequence_valid()` allows accel sequences only when the controller supports them and the qpair is in a poll group.

`_nvme_ns_cmd_setup_request()` fills common read/write/compare/append command fields: opcode, NSID, SLBA in CDW10/11, PI reference tag for type 1/2, fused-operation bits, NLB and CDW12 flags, CDW13, and application tag mask/tag in CDW15.

`_nvme_ns_cmd_rw()` decides whether to submit as a single request or split. It splits across namespace stripe boundaries, maximum transfer size, PRP page-alignment constraints, SGL max-SGE constraints, and iovec max-SGE constraints. Split requests are represented by parent/child `nvme_request` objects; child completions aggregate into the parent. Splitting with accel sequences is explicitly unsupported and fails. If no split is required, the original request is configured directly.

PRP splitting validates that child SGL segments start and end on controller page boundaries except for first and last child positions. SGL splitting limits children by `ctrlr->max_sges`, trimming child length to LBA boundaries when an SGE crosses a block boundary. IOV variants perform the same logic using `spdk_iov_sgl`.

Read, write, and compare public APIs are repetitive wrappers around the core path. Each validates flags, validates SGL callbacks where applicable, allocates the right payload type, calls `_nvme_ns_cmd_rw()` with the opcode and metadata/tag options, maps failures, and submits. Extended variants read optional fields from `struct spdk_nvme_ns_cmd_ext_io_opts` using the ABI-safe macro from `nvme_internal.h`, attach metadata, CDW13, protection tags, and accel sequence when supplied. IOV calls with one element collapse to contiguous payloads.

Zone append has stricter handling. `nvme_ns_cmd_check_zone_append()` requires controller zone-append support and rejects payloads larger than `ctrlr->max_zone_append_size`. The append builders still call `_nvme_ns_cmd_rw()` to validate SGL/PRP constraints, but they assert and enforce that no child requests are produced because zone append commands cannot be split.

Non-read/write commands are direct builders. Write Zeroes and Verify require `1 <= lba_count <= UINT16_MAX + 1` and fill normal LBA/count fields. Write Uncorrectable has the same count range and no payload. Dataset Management validates range count and range pointer, copies DSM ranges as host-to-controller payload, sets NR and type. Copy validates source ranges, copies them as payload, sets destination LBA and range count. Flush is a no-payload NSID command.

Reservation helpers build Register, Release, Acquire, and Report commands. Register/Release/Acquire use user-copy payloads and encode action, ignore-key, cptpl, and reservation type bits. Report requires DWORD-aligned length, sets zero-based DWORD count, and enables extended data when the controller selected 128-bit Host Identifier support. I/O Management Receive requires DWORD-aligned length and sets management operation/suboperation plus transfer count; Send copies the payload and sets operation fields.

Key invariants are child request lifetime, parent completion aggregation, correct payload/metadata offsets during splitting, zone append no-split enforcement, extended option size checks, and consistent error mapping when an I/O cannot be represented within queue/request limits.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_ns_cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_ns_ocssd_cmd.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_ns_ocssd_cmd.c

This file implements namespace-level Open-Channel SSD vector commands.

`spdk_nvme_ocssd_ns_cmd_vector_reset()` validates an LBA list with 1 to `SPDK_NVME_OCSSD_MAX_LBAL_ENTRIES` entries, allocates a null request, sets opcode `SPDK_OCSSD_OPC_VECTOR_RESET` and NSID, optionally puts chunk-info physical address in MPTR, encodes either the single LBA directly in CDW10/11 or the physical address of the LBA list for multiple entries, sets zero-based LBA count in CDW12, and submits.

`_nvme_ocssd_ns_cmd_vector_rw_with_md()` is shared by vector read/write variants. It permits only `SPDK_OCSSD_IO_FLAGS_LIMITED_RETRY`, validates data buffer and LBA list/count, allocates a request, initializes contiguous data and optional metadata transfer sizes as `num_lbas * sector_size` and `num_lbas * md_size`, fills opcode/NSID, encodes single-LBA or LBA-list physical address in CDW10/11, stores zero-based count and flags in CDW12, and submits.

Public wrappers provide vector write/read with and without metadata by passing either `SPDK_OCSSD_OPC_VECTOR_WRITE` or `SPDK_OCSSD_OPC_VECTOR_READ`.

`spdk_nvme_ocssd_ns_cmd_vector_copy()` validates source and destination LBA lists, count, and limited-retry flags. It builds a no-payload vector copy command, encoding either single source/destination LBAs directly or physical addresses of source/destination LBA lists in CDW10/11 and CDW14/15, then sets zero-based count plus flags in CDW12.

The file depends on callers providing physically addressable LBA-list and chunk-info memory because it uses `spdk_vtophys()` directly. It also assumes namespace sector and metadata sizes are already populated by normal namespace identify processing.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_ns_ocssd_cmd.c -->