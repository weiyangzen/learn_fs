# Group Research: group_1750_spdk_sources_virtualization_spdk_lib_nvme_nvme_vfio_user_c_sources__87199479f0f8

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_vfio_user.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_vfio_user.c

## Purpose
Implements SPDK NVMe transport operations for `SPDK_NVME_TRANSPORT_VFIOUSER`, adapting the existing PCIe NVMe controller/qpair machinery to a vfio-user PCI endpoint.

## Main Responsibilities
- Defines `struct nvme_vfio_ctrlr`, embedding `struct nvme_pcie_ctrlr` and adding vfio-user device state plus a mapped doorbell base.
- Implements NVMe register accessors through `spdk_vfio_user_pci_bar_access()` against BAR0 or PCI config space.
- Maps BAR0 doorbells with `spdk_vfio_user_get_bar_addr()`.
- Constructs a controller from `trid->traddr/cntrl`, sets up vfio-user, initializes PCI command bits for bus mastering and INTx disable, reads CAP, builds admin qpair, and registers process state.
- Enables the controller by programming ASQ, ACQ, and AQA through vfio-user register writes.
- Destructs by destroying admin qpair, finishing generic controller teardown, releasing vfio-user device, and freeing the wrapper.

## Key Interfaces
- Exports `vfio_ops` as `const struct spdk_nvme_transport_ops`.
- Reuses PCIe qpair operations for I/O queues, polling, request submission, completion, and admin AER abort.
- Registers itself with `SPDK_NVME_TRANSPORT_REGISTER(vfio, &vfio_ops)`.

## Important Details
- Transfer constraints are hardcoded as `NVME_MAX_XFER_SIZE = 131072` and `NVME_MAX_SGES = 1`.
- Admin queue size is clamped to at least `NVME_PCIE_MIN_ADMIN_QUEUE_SIZE`.
- Doorbell stride is derived from CAP.DSTRD as `1 << cap.bits.dstrd`, matching PCIe controller expectations in units of 32-bit doorbells.
- `ctrlr_scan` only accepts `SPDK_NVME_TRANSPORT_VFIOUSER` and validates the target address exists before probing.

## Storage Relevance
This file is the host-side bridge that lets SPDK’s NVMe stack operate against a virtualized vfio-user NVMe PCI device while preserving the normal NVMe PCIe queue and completion model.

## Risks / Notes
- BAR/register access errors generally abort setup or return `-EIO` from enable paths.
- The code assumes the vfio-user endpoint exposes a controller path under `<traddr>/cntrl`.
- This transport disables CMB SQ use, so queue memory stays in host-managed memory.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_vfio_user.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_zns.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_zns.c

## Purpose
Provides the public SPDK NVMe Zoned Namespace helper APIs and command wrappers for ZNS operations.

## Main Responsibilities
- Exposes namespace and controller ZNS identify data through `spdk_nvme_zns_ns_get_data()` and `spdk_nvme_zns_ctrlr_get_data()`.
- Computes zone sizing and counts from namespace ZNS identify data and active LBA format.
- Returns max open zones, max active zones, and controller max zone append size.
- Wraps zone append commands, including metadata and vectored SGL variants.
- Builds Zone Management Receive commands for report and extended report operations.
- Builds Zone Management Send commands for close, finish, open, reset, offline, and set zone descriptor extension.

## Key Interfaces
- Uses lower-level internal command helpers such as `nvme_ns_cmd_zone_append_with_md()` and `nvme_ns_cmd_zone_appendv_with_md()`.
- Allocates NVMe requests with `nvme_allocate_request_user_copy()` or `nvme_allocate_request_null()`.
- Submits commands through `nvme_qpair_submit_request()`.

## Important Details
- Zone size in bytes is `zone_size_sectors * sector_size`.
- Zone report receive uses `SPDK_NVME_OPC_ZONE_MGMT_RECV`, sets SLBA in CDW10/CDW11, NUMD in CDW12, and report action/options in CDW13.
- Zone management send uses `SPDK_NVME_OPC_ZONE_MGMT_SEND`; when `select_all` is true it omits SLBA and sets the select-all bit in CDW13.
- `spdk_nvme_zns_set_zone_desc_ext()` validates nonzero payload size and non-null buffer before creating a host-to-controller copy request.

## Storage Relevance
This is the user-facing ZNS command layer for applications managing zone lifecycle, zone reports, zone append writes, and zone descriptor extensions over NVMe.

## Risks / Notes
- The helper assumes `ns->nsdata_zns` and active format index are valid for the namespace.
- Most validation is limited to obvious payload checks; device-level semantic errors are returned asynchronously through NVMe completions.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_zns.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/Makefile -->
# File Research: sources/virtualization/spdk/lib/nvmf/Makefile

## Purpose
Build definition for the SPDK NVMe-oF target library `nvmf`.

## Main Responsibilities
- Sets SPDK root include context and common make infrastructure.
- Defines shared library version fields `SO_VER := 23` and `SO_MINOR := 0`.
- Builds core NVMf sources: controller, discovery controller, bdev command path, subsystem, RPC, transport, TCP, stubs, and mDNS server.
- Conditionally includes RDMA, DH-HMAC-CHAP authentication, vfio-user, and Fibre Channel sources.
- Adds external include/library flags for optional providers.

## Key Build Conditions
- `CONFIG_RDMA=y` adds `rdma.c` and links `-libverbs`; FreeBSD builds opportunistically add Mellanox/Chelsio provider libraries if present.
- `CONFIG_HAVE_EVP_MAC=y` adds `auth.c`, tying authentication support to OpenSSL EVP MAC availability.
- `CONFIG_VFIO_USER=y` adds `vfio_user.c`, vfio-user include/library paths, and links `-lvfio-user -ljson-c`.
- `CONFIG_FC=y` adds Fibre Channel sources and include paths.

## Storage Relevance
The file controls which NVMe-oF transport and feature modules are compiled into the target, directly affecting available storage fabrics, authentication, and vfio-user behavior.

## Risks / Notes
- Authentication code is not built unless EVP MAC support is detected.
- Optional provider linkage is platform/config dependent, so runtime capability differs across builds.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/auth.c -->
# File Research: sources/virtualization/spdk/lib/nvmf/auth.c

## Purpose
Implements target-side NVMe-oF DH-HMAC-CHAP authentication for qpairs.

## Main Responsibilities
- Maintains per-qpair authentication state in `struct spdk_nvmf_qpair_auth`.
- Handles authentication send messages: negotiate, DHCHAP reply, DHCHAP success2, and failure2.
- Handles authentication receive messages: challenge, success1, and failure1.
- Negotiates the strongest mutually supported digest and DH group from target policy and host descriptors.
- Generates challenges, sequence numbers, optional DH keys, and derives shared secrets.
- Validates host challenge responses and optionally authenticates the controller back to the host.
- Enforces authentication timeout behavior with SPDK pollers.
- Exposes qpair auth init/destroy/dump and reports support via `nvmf_auth_is_supported()`.

## State Machine
- Starts in `NEGOTIATE`.
- Moves to `CHALLENGE` after successful algorithm selection.
- Sends challenge and moves to `REPLY`.
- Validates host reply and moves to `SUCCESS1`.
- If the host did not request controller authentication, success1 completes and the qpair becomes enabled.
- If controller authentication is requested, moves to `SUCCESS2` and waits for host success2 or failure2.
- Failure paths move through `FAILURE1` or `ERROR`; completed authentication moves to `COMPLETED`.

## Key Interfaces
- Called from controller fabric command routing via `nvmf_auth_request_exec()`.
- Uses `nvmf_subsystem_get_dhchap_key()` for host/controller DHCHAP secrets.
- Uses NVMe DHCHAP helpers for digest length, names, DH key generation, shared secret derivation, and HMAC calculation.
- Uses OpenSSL `RAND_bytes()` for initial subsystem sequence number and challenge values.

## Important Details
- Timeout defaults to 120 seconds if KATO is zero, otherwise follows controller keep-alive timer.
- Reauthentication timeout on an already enabled qpair is nonfatal and returns to `COMPLETED`.
- Negotiation preference arrays are ordered strongest to weakest: SHA512, SHA384, SHA256 and DH groups 8192 down to NULL.
- Failure1 is returned as a successful NVMe command completion carrying an authentication failure payload, then the qpair is disconnected after a short delay.
- JSON dump includes auth state, digest, and DH group.

## Storage Relevance
This file protects NVMe-oF controller sessions before namespace access, making it part of the storage target’s access-control boundary.

## Risks / Notes
- Correctness depends on target-level `dhchap_digests` and `dhchap_dhgroups` bitmasks.
- It carefully validates payload lengths, transaction IDs, hash lengths, DH value alignment, and controller challenge flags before cryptographic checks.
- Controller-authentication support requires a controller DHCHAP key; if absent while requested, authentication fails.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/ctrlr.c -->
# File Research: sources/virtualization/spdk/lib/nvmf/ctrlr.c

## Purpose
Core NVMe-oF controller implementation for SPDK’s target: connection setup, virtual controller properties, admin command handling, I/O dispatch, qpair lifecycle, async events, migration data, ANA, reservations, passthrough, and public request/controller helpers.

## Main Responsibilities
- Creates and destroys `spdk_nvmf_ctrlr` instances for admin connect requests.
- Validates fabric Connect capsules, host access, queue sizes, controller IDs, listener affinity, and duplicate QIDs.
- Manages qpair association, controller qpair masks, admin/I/O queue enablement, and delayed duplicate-QID retry.
- Maintains keep-alive, association, shutdown/reset, and controller fatal-state behavior.
- Implements property get/set for virtual NVMe registers: CAP, VS, CC, CSTS, NSSR, AQA, ASQ, ACQ, and CRTO.
- Handles admin commands: Identify, Get Log Page, Abort, Get/Set Features, AER, Keep Alive, and selected passthrough/custom admin paths.
- Handles fabric commands: Connect, Property Get/Set, and Authentication Send/Recv.
- Dispatches I/O commands to bdev or passthrough paths, including reservation checks, ANA checks, fused compare/write, zcopy, ZNS, and copy.
- Completes requests, tracks outstanding management and namespace I/O, and coordinates subsystem pause/resume accounting.
- Provides public helpers for bdev lookup, request buffers, command/response accessors, controller ID/subsystem access, custom admin handlers, and DIF context retrieval.

## Controller Lifecycle
- `nvmf_ctrlr_create()` allocates controller state, initializes identify/controller data, feature defaults, visible namespace bit array, virtual register state, listener association, and qpair mask.
- Admin qpair addition is routed to the subsystem thread, then controller thread, then poll group thread for connect response completion.
- `nvmf_ctrlr_destruct()` removes the controller from its subsystem and asynchronously frees qpair masks, logs, pending async events, visible namespace state, and controller memory.
- CC disable or shutdown starts I/O qpair disconnect across poll groups, uses timers for reset/shutdown deadlines, and may reset bdev namespaces on timeout.
- NSSR dispatches namespace subsystem reset or bdev reset and disables all controllers in the subsystem.

## Admin and Fabric Command Flow
- `spdk_nvmf_request_exec()` first checks subsystem/namespace active state and qpair state, queues inactive work if needed, inserts the request into outstanding, then routes to fabric, admin, or I/O handlers.
- Fabric Connect is valid before a qpair has a controller; once connected, admin queues allow property and authentication commands, while I/O queues only allow authentication fabric commands.
- Admin commands are rejected if sent while CC.EN is disabled, if fused, or if controller-scoped commands include an NSID.
- Discovery controllers are restricted to Identify, Get Log Page, Keep Alive, Get/Set Features, and AER.
- Custom admin handlers can intercept opcodes; passthrough admin commands are routed to a namespace bdev when configured.

## Identify and Log Pages
- Identify Controller populates fabric, discovery, NVM, ANA, optional command, reservation, and copy capability fields from transport/subsystem/controller state.
- Identify Namespace delegates bdev-derived namespace data to `ctrlr_bdev.c`, then optionally merges selected physical NVMe identify fields for passthrough bdevs.
- Supports active namespace lists, namespace ID descriptors, I/O command-set-specific Identify data for NVM/ZNS, I/O command-set vectors, and independent namespace data.
- Log pages include supported log pages, firmware slot, ANA, command effects, changed namespace list, reservation notification, feature ID effects, discovery log, and selected zero-filled/placeholder pages.
- Async event masks prevent repeated notices until the corresponding log page is read with RAE clear behavior.

## Feature Handling
- Supports arbitration, power management, temperature threshold validation, error recovery, volatile write cache, number of queues, interrupt vector configuration readback, write atomicity, async event config, keep-alive timer, host identifier, reservation notification mask/persistence, and host behavior support.
- Saveable feature requests are rejected.
- ANA inaccessible/persistent-loss/change states can convert certain namespace-affecting Get/Set Features into path status errors.
- Volatile write cache disabling is rejected as not changeable because SPDK cannot force backend cache bypass/drain semantics.
- Number of queues cannot be changed after I/O qpairs are active and returns the preconfigured queue count.

## I/O Dispatch
- `nvmf_ctrlr_process_io_cmd()` validates CC.EN, namespace visibility/bdev presence, ANA path state, and reservation conflicts.
- Standard commands map to bdev handlers: read, write, flush, compare, write zeroes, DSM, copy, and reservation operations.
- Reservation commands are forwarded to the subsystem thread.
- Unsupported optional opcodes are rejected unless command passthrough is enabled and a passthrough namespace exists.
- Fused compare/write enforces sequence and opcode rules, stores the first request on the qpair, and completes both requests consistently.
- Zcopy is only used for READ/WRITE on non-admin queues, when transport zcopy is enabled and the namespace supports it.

## Async Events and Reservations
- AER requests are stored up to `SPDK_NVMF_MAX_ASYNC_EVENTS`; pending events are queued if no AER is outstanding.
- Provides notices for namespace attribute changes, ANA changes, reservation log availability, discovery log changes, and error events.
- Reservation notification logs are capped at 255 queued pages and include per-namespace mask filtering.
- Reservation conflict checks enforce holder/registrant rules before I/O execution.

## Migration
- Saves/restores controller virtual registers, features, controller ID, ACRE state, pending async events, AER command IDs, and notice mask through `spdk_nvmf_ctrlr_migr_data`.
- Uses size fields and copy helpers for version-tolerant migration data handling.
- Includes a static assertion on `struct spdk_nvmf_ctrlr` size to force migration-field review when the structure changes.

## Storage Relevance
This file is the central NVMe-oF target control plane and request dispatch layer. It determines how remote NVMe hosts connect, authenticate, observe controller/namespace capabilities, issue storage I/O, receive async namespace/path/reservation events, and interact with bdev-backed storage.

## Risks / Notes
- Many operations are thread-affine and use `spdk_thread_send_msg()` or `spdk_for_each_channel()`; correctness depends on executing controller, subsystem, and poll-group work on the expected threads.
- Request completion performs important accounting and namespace/passthrough NSID restoration; bypassing it would corrupt pause/resume or outstanding I/O state.
- ANA, reservation, and subsystem pause states can queue or reject otherwise valid commands.
- Passthrough paths intentionally rewrite NSID and must restore it before accounting and completion.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/ctrlr.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/ctrlr_bdev.c -->
# File Research: sources/virtualization/spdk/lib/nvmf/ctrlr_bdev.c

## Purpose
Implements the NVMe-oF controller’s bdev-backed namespace command path and bdev-derived Identify data.

## Main Responsibilities
- Determines whether all subsystem namespaces support UNMAP, WRITE ZEROES, or COPY.
- Completes bdev I/O by translating bdev NVMe status into NVMf request completions.
- Builds Identify Namespace and NVM I/O command-set namespace data from bdev properties.
- Parses NVMe read/write parameters and extended command flags into bdev I/O options.
- Implements bdev-backed READ, WRITE, COMPARE, fused COMPARE+WRITE, WRITE ZEROES, FLUSH, DSM/UNMAP, COPY, NVMe passthrough, admin passthrough, ABORT, DIF context creation, and zero-copy start/end.

## Identify Behavior
- Namespace size, capacity, and utilization are taken from bdev block count.
- LBA format is based on bdev descriptor block size and metadata size, or data block size when DIF insert/strip hides metadata.
- DIF/DIX protection fields are mapped from bdev DIF type and metadata placement.
- Preferred write/unmap granularity/alignment and optimal write size are populated from bdev hints, with physical block size fallbacks.
- NGUID, EUI64, reservation capabilities, copy limits, and shared namespace flag are filled from namespace/bdev options.
- NVM-specific Identify data reports PI format details for 16/32/64-bit guard formats.

## I/O Command Behavior
- READ/WRITE/COMPARE validate LBA range and SGL length before issuing vector bdev operations.
- Fused compare/write validates same SLBA/NLB and submits `spdk_bdev_comparev_and_writev_blocks()`.
- WRITE ZEROES validates range, logs WZSL exceedance, rejects deallocate, and submits zeroing.
- FLUSH succeeds immediately if the bdev does not support flush, matching the controller’s volatile-write-cache behavior.
- DSM handles deallocation by splitting NVMe DSM ranges into bdev unmap calls, honoring DMRL/DMRSL-style limits and waiting for all submitted unmaps.
- COPY supports exactly one source range and descriptor format 0, then calls `spdk_bdev_copy_blocks()`.
- NVMe I/O/admin passthrough forwards commands through bdev NVMe passthrough interfaces.

## Resource Handling
- `-ENOMEM` from bdev submission queues the request with `spdk_bdev_queue_io_wait()` and resubmits through the controller command path.
- Request NSID is restored before resubmission because passthrough may have rewritten it.
- Unmap uses a context object to count outstanding range operations and resume after bdev resource waits.
- Abort uses `spdk_bdev_abort()` and updates completion CDW0 when the target command is successfully aborted.
- Zero-copy start preserves the bdev I/O in `req->zcopy_bdev_io` until zcopy end commits or releases it.

## DIF and Zcopy
- DIF context creation derives the initial reference tag from SLBA and enables guard/reference checks according to bdev descriptor settings.
- Zcopy is available only when the bdev supports `SPDK_BDEV_IO_TYPE_ZCOPY`.
- Zcopy start validates range and SGL size, obtains bdev-owned iovecs, and leaves the bdev I/O alive for end-zcopy.

## Storage Relevance
This file is the core data-plane adapter between NVMe-oF protocol commands and SPDK’s block-device abstraction. It is where remote NVMe operations become local bdev I/O.

## Risks / Notes
- Most range validation protects against overflow by checking both end beyond media and wraparound.
- DSM range values are copied from request iovecs via `spdk_iov_xfer`; incorrect host lengths are rejected before use.
- Flush success on non-flush bdevs is a deliberate compatibility choice and does not imply backend persistence semantics.
- Copy and fused operations intentionally expose only limited NVMe functionality based on bdev capabilities.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/ctrlr_bdev.c -->