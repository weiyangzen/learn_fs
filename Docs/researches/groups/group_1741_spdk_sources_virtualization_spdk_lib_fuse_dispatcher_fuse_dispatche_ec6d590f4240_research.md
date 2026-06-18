# Group Research: group_1741_spdk_sources_virtualization_spdk_lib_fuse_dispatcher_fuse_dispatche_ec6d590f4240

Scope checked against `Docs/research_subset_a.md`: the subset includes `sources/virtualization/spdk`, so every file in this group is in scope. I read each listed source file completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/fuse_dispatcher/fuse_dispatcher.c -->
# File Research: sources/virtualization/spdk/lib/fuse_dispatcher/fuse_dispatcher.c

`fuse_dispatcher.c` implements SPDK’s deprecated FUSE dispatcher bridge between Linux FUSE request wire structures and the SPDK `fsdev` API. It owns dispatcher creation/deletion, per-channel fsdev channel binding, request parsing, FUSE protocol negotiation, opcode dispatch, output formatting, and async completion lifetime management.

The dispatcher tracks an opened `spdk_fsdev_desc`, the fsdev thread, negotiated protocol version, request-source architecture, root file object, event callback, and fsdev name. Per-dispatcher channels wrap `spdk_fsdev_get_io_channel()` channels. A global `spdk_fuse_mgr` provides a shared mempool for `struct fuse_io` objects, reference-counted across dispatcher instances under a pthread mutex.

The file translates FUSE node IDs and file handles to SPDK pointers. Root maps to `FUSE_ROOT_ID`; other inode values are pointer-cast `spdk_fsdev_file_object` values. File handles are similarly pointer-cast `spdk_fsdev_file_handle` values. This makes the dispatcher tightly coupled to in-process fsdev object lifetimes rather than stable kernel inode identities.

Request parsing is iovec-offset based. Helpers walk input and output iovec arrays, reserve the output header, decode string arguments in place, and copy or directly fill output payloads. Completion helpers fill `fuse_out_header`, preserve the request unique ID, enforce negative error conventions, free the `fuse_io` before invoking the caller completion callback, and special-case `FORGET`/`BATCH_FORGET` as no-reply requests.

The FUSE protocol handlers cover lookup, forget, getattr/setattr, readlink/symlink, mknod/mkdir/unlink/rmdir, rename/rename2, link, open/create, read/write, statfs, release/fsync/flush, xattr get/set/list/remove, init/destroy, opendir/readdir/readdirplus/releasedir/fsyncdir, flock-style locking, interrupt/abort, fallocate, batch forget, and copy-file-range. Unsupported handlers return `-ENOSYS` for GETLK, SETLKW, ACCESS, BMAP, IOCTL, POLL, SETUPMAPPING, REMOVEMAPPING, and SYNCFS.

`FUSE_INIT` negotiates major/minor protocol behavior, supports legacy input/output struct sizes, advertises selected capabilities such as async read, auto invalidation, async DIO, atomic truncate, flock locks, readdirplus, export support, big writes, and optional writeback cache, then mounts the fsdev. If preparing the init reply fails after mount, the code rolls back by issuing `spdk_fsdev_umount()` and retries rollback initiation if fsdev I/O objects are temporarily unavailable.

Architecture support is limited to translating selected open flags between native, x86/x86_64, and ARM/ARM64 layouts. Other integer endian conversion helpers are identity functions, so this is not a general cross-endian FUSE bridge.

Creation opens the named fsdev, creates the shared `FUSE_disp_ios` mempool on first use, registers an SPDK io_device using an offset pointer derived from the dispatcher allocation, and walks all existing dispatcher channels to acquire fsdev I/O channels. Create failure paths close fsdev, free the dispatcher, and unwind channel acquisition. Delete walks channels to put fsdev channels, posts fsdev close back to the original fsdev thread, unregisters the io_device, frees the dispatcher, and releases the global mempool when the last dispatcher is gone.

Fsdev remove events trigger a for-each-channel pass that drops fsdev channels and then calls the dispatcher event callback with `SPDK_FUSE_DISP_EVENT_FSDEV_REMOVE`, preventing later submissions from using stale channels.

Research notes: the most sensitive areas are pointer-as-inode lifetime assumptions, iovec offset accounting, protocol-version struct sizing, `FORGET` no-reply completion paths, and async teardown ordering. The file also explicitly logs a deprecation notice: the `fuse_dispatcher` library is being removed in `v26.09`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/fuse_dispatcher/fuse_dispatcher.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/idxd/Makefile -->
# File Research: sources/virtualization/spdk/lib/idxd/Makefile

This Makefile builds the SPDK `idxd` library. It always compiles `idxd.c` and `idxd_user.c`, and conditionally adds `idxd_kernel.c` when `CONFIG_IDXD_KERNEL=y`.

It sets `SPDK_ROOT_DIR`, includes common SPDK make rules, declares shared-object version `14.0`, names the library `idxd`, uses `spdk_idxd.map` as the symbol map, and includes `spdk.lib.mk`.

Research notes: kernel IDXD support is build-time optional; the user-space PCI implementation is always part of the library.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/idxd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/idxd/idxd.c -->
# File Research: sources/virtualization/spdk/lib/idxd/idxd.c

`idxd.c` is the common SPDK Intel IDXD/DSA/IAA datapath implementation. It is backend-agnostic: user-mode PCI and kernel accel-config backends register `spdk_idxd_impl` objects, while this file owns channel allocation, descriptor pools, batching, address translation, operation submission, completion polling, and DIF/DIX validation.

Global implementation selection is explicit through `spdk_idxd_set_config(bool kernel_mode)`, which chooses the registered `user` or `kernel` implementation. Once devices are initialized, changing implementations is rejected. Probing and detach delegate to the selected backend’s `probe()` and `destruct()` hooks.

Each `spdk_idxd_io_channel` gets a descriptor pool, completion/operation pool, portal address/offset, and for DSA a pool of preallocated batch objects. Channel count is limited by `chan_per_device`, guarded by `num_channels_lock`, and portal offsets are distributed by channel. Address translation uses virtual addresses when PASID/shared virtual addressing is enabled; otherwise it uses `spdk_vtophys()` and rejects non-contiguous mappings that cannot satisfy a descriptor segment.

Submission uses 64-byte descriptor writes via `movdir64b()` after a write memory barrier. Regular descriptors come from `ops_pool`; batch descriptors are built inside `idxd_batch` objects and later submitted as either a single converted descriptor or an `IDXD_OPCODE_BATCH` descriptor. Batches flush automatically at `IDXD_MIN_BATCH_FLUSH` entries and are also submitted from `spdk_idxd_process_events()` if still open.

DSA operations include copy, dualcast, compare, fill, CRC32C, copy+CRC32C, raw descriptor submission, DIF check/insert/strip, and DIX generate. Copy and compare walk source/destination iovecs with `spdk_ioviter`, split on physical contiguity boundaries, and use parent/child completion counting so one logical user callback fires after all split descriptors complete. Dualcast enforces 4 KiB destination alignment. CRC operations chain seeds through prior completion records and copy only the final CRC to the caller.

IAA operations include compression and decompression. The current implementation only supports simple single-buffer compression/decompression cases; vectored support returns `-EINVAL`. Compression uses the device AECS address and IAA flags, and completion records can return the output size.

DIF/DIX helpers validate SPDK DIF context restrictions before building descriptors. Supported cases are narrow: zero data offset, zero guard seed, PI format 16, metadata sizes 8 or 16 depending on operation, interleaved metadata for DIF operations, separate metadata for DIX generate, 512/4096 data blocks plus 520/4104 interleaved forms, and required guard/app/ref tag flags for insert/generate. Buffer lengths must align to block or data-block sizes because DSA handles each iovec independently.

Completion polling scans `ops_outstanding` in order, stops at the first incomplete record, handles up to `IDXD_MAX_COMPLETIONS`, checks failure status, dumps software error registers via the backend, writes CRC/output-size results, maps compare results and DIF errors, returns completed regular ops to `ops_pool`, decrements batch reference counts, frees batches back to the pool, and invokes callbacks after operation accounting is complete.

Research notes: key correctness points are descriptor lifetime, batch refcounting, parent/child count handling for split operations, PASID-vs-physical-address behavior, and strict DIF/DIX parameter validation. Some error paths decrement `chan->batch->index` to roll back partially prepared descriptors, so edits to operation builders must keep `count` accurate.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/idxd/idxd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/idxd/idxd_internal.h -->
# File Research: sources/virtualization/spdk/lib/idxd/idxd_internal.h

`idxd_internal.h` defines private IDXD structures and helpers shared by the common datapath and backend implementations.

It provides the inline `movdir64b()` descriptor-write primitive, IDXD timing/config constants, DSA/IAA device type enum, batch metadata, per-channel state, PCI ID helper structure, operation/completion wrapper, backend implementation interface, and the common `spdk_idxd_device` structure.

`spdk_idxd_io_channel` stores the target device, portal address and offset, PASID state, current open batch, descriptor and operation pools, outstanding operations, and batch pool. `idxd_ops` wraps either DSA or IAA completion records, callback data, descriptor pointer, optional CRC/output-size destination, parent op pointer, and split-operation count; a static assertion fixes its size at 128 bytes.

`spdk_idxd_impl` abstracts backend-specific probing, destruction, software-error dumping, and portal address lookup. The `SPDK_IDXD_IMPL_REGISTER` constructor macro registers backend implementations at load time.

Research notes: this header is the private ABI between `idxd.c`, `idxd_user.c`, and `idxd_kernel.c`. Layout changes affect descriptor pool allocation, completion interpretation, and backend registration.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/idxd/idxd_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/idxd/idxd_kernel.c -->
# File Research: sources/virtualization/spdk/lib/idxd/idxd_kernel.c

`idxd_kernel.c` implements the optional kernel-backed IDXD implementation using `libaccel_config`. It discovers enabled kernel IDXD devices and user work queues, maps the kernel work-queue portal, and registers an `spdk_idxd_impl` named `kernel`.

The probe path creates an accel-config context, iterates enabled devices, checks PASID/shared-memory compatibility with SPDK IOMMU state, allocates `spdk_kernel_idxd_device`, records device limits, NUMA node, version, PASID state, and scans enabled user work queues. Only dedicated work queues are supported. For the selected WQ it opens `/dev/char/<major>:<minor>`, mmaps a 4 KiB write portal, records total WQ size, derives `chan_per_device`, and records batch size.

Devices with a usable WQ are passed to the attach callback. Devices without a usable WQ are destructed. Destruction unmaps the portal, closes the fd, unreferences the accel-config context, and frees the wrapper.

The backend’s `portal_get_addr()` returns the mmapped portal. Software-error dumping is currently a stub.

Research notes: this backend depends on kernel provisioning of enabled DSA/IAA devices and dedicated user WQs. It rejects IOMMU-enabled systems without PASID/shared-memory support because userspace cannot supply usable IOVA addresses to the kernel work queue.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/idxd/idxd_kernel.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/idxd/idxd_user.c -->
# File Research: sources/virtualization/spdk/lib/idxd/idxd_user.c

`idxd_user.c` implements the default user-space PCI IDXD backend. It enumerates IDXD PCI devices, claims devices, maps MMIO and work-queue BARs, programs groups and work queues directly, enables the device, initializes DSA or IAA-specific state, and registers an `spdk_idxd_impl` named `user`.

Device configuration maps `IDXD_MMIO_BAR` and `IDXD_WQ_BAR`, resets the device, reads version/capability registers, configures one group containing all engines and one work queue, writes WQ configuration for dedicated mode, full WQ size, max batch shift, max transfer shift, enabled state, and priority, then enables the device and WQ through command registers.

The probe path is serialized by `g_driver_lock`, calls the caller’s probe callback, claims accepted PCI devices, attaches them, and calls the attach callback. Attach determines device type from PCI ID: DSA devices use DSA operations, while IAA devices allocate a DMA AECS table and fill fixed Huffman tables required for RFC-1951 fixed compression. The attach path also enables PCI bus mastering, initializes the channel-count mutex, and calls the hardware configuration routine.

Destruction disables the device, unmaps BARs, detaches the PCI device, frees IAA AECS state when present, and frees the wrapper. Software-error dumping reads and logs the device SWERR register fields. Portal lookup returns the mapped work-queue BAR address.

Research notes: this backend owns hardware programming policy and currently configures one dedicated WQ. The IAA fixed Huffman tables are static data used to initialize AECS for compression. Error paths around BAR mapping/configuration are important because failed attach calls into the destructor for cleanup.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/idxd/idxd_user.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/init/Makefile -->
# File Research: sources/virtualization/spdk/lib/init/Makefile

This Makefile builds the SPDK `init` library from `json_config.c`, `subsystem.c`, `subsystem_rpc.c`, and `rpc.c`.

It sets `SPDK_ROOT_DIR`, includes common SPDK make rules, declares shared-object version `8.0`, names the library `init`, uses `spdk_init.map` for exports, and includes `spdk.lib.mk`.

Research notes: the library combines subsystem lifecycle, JSON config loading, and framework RPC server/control-plane helpers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/init/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/init/json_config.c -->
# File Research: sources/virtualization/spdk/lib/init/json_config.c

`json_config.c` loads SPDK JSON configuration by replaying configured JSON-RPC methods against a temporary in-process RPC server. It parses the `"subsystems"` array, walks subsystem config entries, filters methods by RPC state, sends requests over a temporary Unix-domain JSON-RPC client/server pair, and optionally advances subsystem initialization between startup and runtime phases.

The expected JSON shape is a root object with `"subsystems"` entries, each containing a subsystem name and a `"config"` array. Config entries can be individual RPC objects with `"method"` and optional `"params"`, or explicit arrays that are sent as JSON-RPC batch requests.

`load_json_config_ctx` owns the parsed JSON buffer/token array, current subsystem/config iterators, current method request ID, stop-on-error behavior, temp RPC socket path, JSON-RPC client connection, poller, active response handler, timeout, and a flag controlling whether subsystem initialization should be performed.

The loader copies and parses JSON with comment support, locates the `"subsystems"` array, starts a temporary RPC server with a unique socket name derived from `SPDK_DEFAULT_RPC_ADDR`, pid, and ticks, connects a JSON-RPC client, and drives connection/request progress through SPDK pollers on the app thread.

Individual requests preserve raw `"params"` JSON rather than decoding it locally. Method state masks from `spdk_rpc_get_method_state_mask()` determine whether a method should run in STARTUP or RUNTIME. Methods allowed in both states are skipped during the second runtime pass to avoid duplicate execution. Missing methods can be skipped when the referenced subsystem is not linked into the application, supporting reuse of config files across SPDK apps with different linked subsystems.

Batch handling builds one JSON-RPC batch request from an explicit config array, computes the intersection of allowed state masks for all batch elements, skips batches not applicable to the current state, and rejects batches whose methods have incompatible state requirements. Empty or invalid batches are treated as errors.

When subsystem initialization is enabled, the first pass runs STARTUP methods. After all entries are walked in STARTUP state, it calls `spdk_subsystem_init()`, switches RPC state to RUNTIME in the init callback, then walks the config again for runtime methods. `spdk_subsystem_load_config()` uses the same machinery without initializing subsystems.

Timeout handling intentionally warns every 10 seconds for outstanding RPC requests rather than failing them, because SPDK RPC commands generally do not have hard timeouts. Connection setup has a shorter 1 second timeout.

Research notes: the file’s important behavior is the state-aware two-pass replay model and the temporary RPC-loopback design. The code relies on app-thread execution, async pollers, raw JSON forwarding, and careful cleanup of poller/client/server resources in `app_json_config_load_done()`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/init/json_config.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/init/rpc.c -->
# File Research: sources/virtualization/spdk/lib/init/rpc.c

`rpc.c` manages framework RPC server instances during SPDK initialization/runtime. It supports multiple listen addresses, a shared poller that accepts connections on active servers, server pause/resume, and global finish cleanup.

Each `init_rpc_server` stores the RPC server object, listen address, active flag, and list link. `spdk_rpc_initialize()` validates registered RPC methods and options, rejects duplicate listen addresses, starts `spdk_rpc_server_listen()`, applies JSON-RPC log options, inserts the server into the global list, and registers the accept poller when the first server starts.

The accept poller walks all servers and calls `spdk_rpc_server_accept()` only for active ones. `spdk_rpc_server_pause()` and `spdk_rpc_server_resume()` toggle the active flag without closing the server.

`spdk_rpc_server_finish()` closes and removes one server by listen address, and unregisters the shared poller when no servers remain. `spdk_rpc_finish()` closes all servers. Option helpers provide size-versioned copy/default handling for `spdk_rpc_opts`, currently covering log file and log level with a static size assertion.

Research notes: all public functions assert app-thread execution. The global JSON-RPC log settings are only applied from opts for the first/default initialization path unless explicit opts are supplied.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/init/rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/init/subsystem.c -->
# File Research: sources/virtualization/spdk/lib/init/subsystem.c

`subsystem.c` implements SPDK subsystem registration, dependency ordering, initialization, finalization, and config dumping.

Subsystems and dependency records are stored in global TAILQs populated by constructor-style registration elsewhere. Helpers expose lookup and iteration over subsystems and dependencies. `spdk_subsystem_exists()` asserts app-thread execution and checks by name.

Before initialization, dependency records are validated to ensure both the dependent subsystem and dependency target are registered. `subsystem_sort()` then performs a simple topological ordering by repeatedly moving subsystems whose dependencies are already in a temporary sorted list. The sorted list replaces the original initialization order.

`spdk_subsystem_init()` records the completion callback and starts `spdk_subsystem_init_next()`. The init-next routine advances through the sorted list, invokes each subsystem’s `init()` callback if present, and expects subsystems to call back into `spdk_subsystem_init_next(rc)` when done. On success after the final subsystem, it marks subsystems initialized and calls the original completion callback.

Finalization runs in reverse sorted order through `spdk_subsystem_fini_next()`, invoking each subsystem’s `fini()` if present. It handles the case where finalization interrupts initialization by setting `g_subsystems_init_interrupted` and backing up from the current subsystem. Completion calls the stop callback registered by `spdk_subsystem_fini()`.

`subsystem_config_json()` delegates to a subsystem’s `write_config_json()` hook or writes JSON null if no hook is present.

Research notes: dependency sorting assumes the dependency graph can make progress; a cycle would leave the while loop unable to drain `g_subsystems`. Lifecycle state is global and app-thread oriented.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/init/subsystem.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/init/subsystem.h -->
# File Research: sources/virtualization/spdk/lib/init/subsystem.h

`subsystem.h` is the private header for init subsystem internals. It declares subsystem lookup/iteration helpers, dependency iteration helpers, and `subsystem_config_json()`.

The header allows RPC/config files to inspect registered subsystems without exposing the global TAILQs directly. `subsystem_config_json()` writes one subsystem’s configuration to a JSON writer, falling back to JSON null when no config writer exists.

Research notes: this file is the small internal ABI between `subsystem.c`, `subsystem_rpc.c`, and other init code.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/init/subsystem.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/init/subsystem_rpc.c -->
# File Research: sources/virtualization/spdk/lib/init/subsystem_rpc.c

`subsystem_rpc.c` implements runtime framework RPCs for subsystem and PCI introspection.

`framework_get_subsystems` takes no parameters and returns an array of registered subsystems, each with its name and a `depends_on` array derived from dependency records.

`framework_get_config` decodes a subsystem name and optional `with_batches` flag, looks up the subsystem, and writes its saved configuration through `subsystem_config_json()`. When `with_batches` is false, it adds the JSON writer flag to flatten batches.

`framework_get_pci_devices` takes no parameters and returns all SPDK PCI devices. Each entry includes formatted BDF address, device type, NUMA ID, and PCI config space as a byte array. It reads the first 256 bytes and includes extended config space only when the extended region is not all zeroes.

Research notes: these are control-plane inspection RPCs registered for `SPDK_RPC_RUNTIME`. They depend on generated RPC decode/free helpers for `framework_get_config`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/init/subsystem_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ioat/Makefile -->
# File Research: sources/virtualization/spdk/lib/ioat/Makefile

This Makefile builds the SPDK `ioat` library from `ioat.c`.

It sets `SPDK_ROOT_DIR`, includes common SPDK make rules, declares shared-object version `9.0`, names the library `ioat`, uses `spdk_ioat.map` for symbol exports, and includes `spdk.lib.mk`.

Research notes: this library’s implementation surface in the group is `ioat.c` plus its private internal header.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ioat/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ioat/ioat.c -->
# File Research: sources/virtualization/spdk/lib/ioat/ioat.c

`ioat.c` implements SPDK’s Intel I/OAT DMA engine library. It handles PCI enumeration/attach/detach, BAR mapping, channel reset/start, descriptor ring setup, copy/fill descriptor building, flush/doorbell submission, and completion polling.

Global driver state consists of a mutex and a TAILQ of attached channels. `spdk_ioat_probe()` enumerates PCI I/OAT devices under the lock, skips devices already attached, calls the user probe callback, attaches accepted devices, inserts them into the attached list, and calls the attach callback.

Attach enables PCI bus mastering, maps BAR0 register space, checks I/OAT version, reads DMA capabilities and max transfer size, allocates a DMA completion-update location, allocates a default 32K-entry software descriptor ring and DMA hardware descriptor ring, translates every hardware descriptor address, links descriptors into a ring, resets hardware, programs completion and chain addresses, submits a null descriptor, flushes, and waits for idle state.

Descriptor preparation supports null, copy, and fill descriptors. Build APIs split operations by physical contiguity and `max_xfer_size`, append descriptors to the ring, and attach the user callback only to the final descriptor of the logical operation. If the ring runs out of descriptors, the build path restores the original head so partially prepared descriptors are discarded. Submit APIs call build then `spdk_ioat_flush()`.

`spdk_ioat_flush()` marks the last descriptor for completion update and writes the descriptor count register. Completion polling reads the DMA completion-update memory, detects halted channels, walks completed descriptors from tail until the hardware-completed physical address is reached, invokes descriptor callbacks, advances tail, records `last_seen`, and returns the number of events.

Detach removes the channel from the global attached list under lock, unmaps BAR0, frees software and DMA rings, frees the completion-update buffer, and frees the channel.

Research notes: critical correctness areas are descriptor ring wraparound, physical address translation, head rollback on build failure, and hardware reset/start sequencing. Fill support depends on the device BFILL capability bit.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ioat/ioat.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ioat/ioat_internal.h -->
# File Research: sources/virtualization/spdk/lib/ioat/ioat_internal.h

`ioat_internal.h` defines private structures and helpers for the I/OAT library.

It includes public IOAT/spec headers, queue macros, and MMIO helpers. `IOAT_DEFAULT_ORDER` sets the default descriptor ring size to `1 << 15` entries. `ioat_descriptor` stores the hardware descriptor physical address plus user callback and callback argument.

`spdk_ioat_chan` is the per-device/channel state: PCI device handle, max transfer size, mapped register pointer, DMA completion-update pointer, ring head/tail, ring size order, last completed descriptor address, software descriptor ring, hardware descriptor ring, DMA capability flags, and global attached-list link.

Inline helpers classify channel status values as active, idle, halted, or suspended based on IOAT status bits.

Research notes: this header’s structures are owned by `ioat.c`; changes affect ring management, hardware programming, and completion polling.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ioat/ioat_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/Makefile -->
# File Research: sources/virtualization/spdk/lib/iscsi/Makefile

This Makefile builds the SPDK `iscsi` library. It includes the library directory in `CFLAGS`, compiles connection, initiator group, core iSCSI, parameter, portal group, target node, subsystem, RPC, and task source files, and links against OpenSSL crypto via `LOCAL_SYS_LIBS = -lcrypto`.

It sets shared-object version `10.0`, names the library `iscsi`, uses `spdk_iscsi.map` for symbol exports, and includes the common SPDK library make rules.

Research notes: this group only includes the build file, not the listed iSCSI implementation sources. The Makefile shows that iSCSI depends on crypto and is split across transport/session/config/RPC/task modules.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/Makefile -->