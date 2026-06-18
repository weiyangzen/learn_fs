# Group Research: group_1324_nvme_cli_sources_virtualization_nvme_cli_libnvme_src_nvme_ioctl_win_871bb0991bd5

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/nvme-cli`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl-win.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl-win.c

Windows implementation of libnvme ioctl-style passthrough APIs. Unlike Linux, Windows does not expose one generic NVMe ioctl interface for all commands, so this file translates selected NVMe admin and I/O opcodes into Windows storage APIs.

Key behavior:
- Converts Windows `GetLastError()` and `STORAGE_PROTOCOL_STATUS_*` values into errno-style negative returns.
- Implements unsupported reset operations as `-ENOTSUP`; namespace rescan/block-size update use `IOCTL_DISK_UPDATE_PROPERTIES`.
- Derives namespace ID from `IOCTL_SCSI_GET_ADDRESS` by mapping SCSI LUN to `nsid = Lun + 1`.
- Provides generic `IOCTL_STORAGE_PROTOCOL_COMMAND` submission for vendor-specific commands and some WinPE-only cases.
- Maps NVMe flush/read/write to SCSI pass-through commands:
  - Flush -> `SCSIOP_SYNCHRONIZE_CACHE`
  - Read -> `SCSIOP_READ16`
  - Write -> `SCSIOP_WRITE16`
- Translates selected admin commands to Windows-specific mechanisms:
  - Get Log Page and Identify -> `IOCTL_STORAGE_QUERY_PROPERTY`
  - Set/Get Features -> storage protocol property set/query
  - Firmware Commit/Download -> `IOCTL_STORAGE_FIRMWARE_ACTIVATE` / `IOCTL_STORAGE_FIRMWARE_DOWNLOAD`
  - Format NVM -> WinPE passthrough or Windows sanitize/reinitialize IOCTL mapping
  - Security Send/Receive -> SCSI Security Protocol In/Out
- Dispatches public `libnvme_submit_io_passthru()` and `libnvme_submit_admin_passthru()` by opcode.

Important dependencies:
- Windows headers: `windows.h`, `winioctl.h`, `ntddscsi.h`.
- libnvme command opcode and bitfield helpers from `libnvme.h`, `types.h`, and `ioctl.h`.
- Transport hooks from `struct libnvme_transport_handle`: `submit_entry`, `submit_exit`, `decide_retry`, and global `dry_run`.

Research notes:
- The file preserves libnvme’s hook/retry semantics around every supported Windows submission path.
- Windows support is intentionally partial and command-specific; unsupported commands return `-ENOTSUP`.
- WinPE is detected through `HKLM\SYSTEM\CurrentControlSet\Control\MiniNT` and enables a few paths that normal Windows blocks.
- Result handling is often reduced to CQE DW0 or zero because Windows APIs do not expose full Linux-style NVMe completion details for every translated command.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl-win.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl.c

Tiny fallback/default implementation for passthrough submission hooks.

Contents:
- `__libnvme_submit_entry()` returns `NULL`.
- `__libnvme_submit_exit()` is a no-op.
- `__libnvme_decide_retry()` returns `false`.

Research notes:
- These are default hook implementations used when callers do not install custom tracing/retry callbacks on a transport handle.
- The retry default is conservative: no retries unless a caller or transport installs a policy.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl.h

Public declarations for libnvme direct ioctl/passthrough operations.

Key definitions:
- `NVME_DEFAULT_IOCTL_TIMEOUT` is `0`, meaning kernel/default timeout.
- `NVME_LOG_PAGE_PDU_SIZE` is `4096`, used as a safe log transfer chunk size.
- Declares synchronous submit/exec APIs for admin and I/O passthrough.
- Declares async passthrough queue/reap/wait APIs and `struct libnvme_passthru_completion`.
- Declares controller/namespace management helpers:
  - subsystem reset
  - controller reset
  - namespace rescan
  - namespace ID retrieval
  - block size update

Research notes:
- The header is Linux-described, but its public API is also implemented by platform-specific files such as `ioctl-win.c`.
- Async comments note io_uring sharing for Linux, so direct async use and synchronous execution should not be mixed on one handle when io_uring is active.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/json.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/json.c

JSON configuration and topology serialization for libnvme hosts, subsystems, controllers, namespaces, and fabrics options.

Key behavior:
- Parses a strict JSON array config into existing/created libnvme host/subsystem/controller objects.
- Reads host fields such as `hostnqn`, `hostid`, `dhchap_key`, `hostsymname`, and persistent discovery controller state.
- Reads subsystem fields including `nqn`, `application`, and `ports`.
- Updates fabrics controller config fields such as queue counts, timeouts, digest flags, TLS settings, keyring, TLS key identity, and persistent/discovery flags.
- Writes persistent config back as a JSON array, skipping PCIe controllers and discovery subsystems where appropriate.
- Dumps runtime tree state as a JSON object containing hosts, subsystems, namespaces, paths, ANA state, NUMA nodes, queue depth, and controller details.

Important dependencies:
- json-c APIs: `json_object_*`, `json_tokener_*`, `json_object_to_fd`.
- libnvme tree accessors and mutators from `libnvme.h`.
- Internal logging through `libnvme_msg()`.

Research notes:
- Parsing updates only unset/default-ish controller config fields for many options, preserving values already set elsewhere.
- Config update and tree dump are separate views: config output targets reconnect/fabrics persistence, while tree dump targets discovered runtime topology.
- Strict JSON parsing is enforced through `JSON_TOKENER_STRICT`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/json.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/lib-types.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/lib-types.h

Core public type definitions shared by libnvme transport, ioctl, and MI code.

Key definitions:
- Forward declares:
  - `struct libnvme_global_ctx`
  - `struct libnvme_transport_handle`
  - `struct libnvme_mi_ep`
- Defines `struct libnvme_passthru_cmd`, a platform-neutral NVMe passthrough command layout with opcode, namespace, command dwords, data/metadata pointers, lengths, timeout, and result.
- Defines `struct libnvme_uring_cmd`, the io_uring-oriented variant without result.
- Defines `libnvme_fd_t` differently by platform:
  - Windows: `HANDLE`, invalid value `INVALID_HANDLE_VALUE`
  - non-Windows: `int`, invalid value `-1`

Research notes:
- The passthrough command layout is the central ABI object used by Linux ioctl paths, Windows translations, and MI admin passthrough.
- `addr` and `metadata` are stored as `__u64`, so implementations cast through `uintptr_t` when accessing user buffers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/lib-types.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/lib.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/lib.c

Core libnvme context and transport-handle lifecycle implementation.

Key behavior:
- Creates and frees `struct libnvme_global_ctx`.
- Initializes logging file descriptor/level and list heads for hosts and MI endpoints.
- Enables ioctl probing by default.
- Derives default MI probing behavior from `LIBNVME_MI_PROBE_ENABLED`; unset means enabled, `0`, `false`, or `disable*` disable it.
- Frees fabrics state, hosts, MI endpoints, config path, application string, and context.
- Provides setters for dry-run mode, ioctl probing, passthrough submit-entry/submit-exit hooks, retry-decision hook, and default timeout.
- Opens direct Linux handles by validating `/dev/nvme*` or `/dev/ng*` names and file type:
  - controllers must be character devices
  - namespaces must be block devices
- Attempts io_uring setup for controller character devices.
- Supports special test handles named `NVME_TEST_FD` and `NVME_TEST_FD64`.
- Dispatches `mctp:` device names to MI transport setup.

Research notes:
- `libnvme_open()` creates one transport handle and chooses direct versus MI by name prefix.
- `libnvme_close()` dispatches cleanup by handle type.
- Transport type predicates are simple wrappers over handle type or `stat` mode.
- Direct handle ownership includes closing io_uring state, closing fd, and freeing the handle.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/lib.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/lib.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/lib.h

Public libnvme core API declarations.

Key API areas:
- Global context lifecycle:
  - `libnvme_create_global_ctx()`
  - `libnvme_free_global_ctx()`
- Logging:
  - log levels
  - default log level
  - set/get logging level, PID flag, timestamp flag
- Transport handles:
  - open/close
  - get fd/name/MI endpoint
  - test whether handle is controller, namespace, direct, or MI
- Passthrough hooks:
  - submit-entry callback
  - submit-exit callback
  - retry-decision callback
  - default timeout setter
- Global behavior toggles:
  - MI endpoint probing
  - dry run
  - ioctl probing

Research notes:
- The header describes Linux naming semantics for `libnvme_open()`, while implementation also supports `mctp:` and test-handle names.
- Hook callbacks are part of the public API, enabling tracing, custom retry logic, and per-command state management without modifying submission code.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/lib.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/linux.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/linux.c

Linux sysfs attribute utility implementation.

Key behavior:
- Writes sysfs-like attributes by opening `<dir>/<attr>` for write and writing the provided string.
- Reads attributes by opening `<dir>/<attr>`, reading up to 4095 bytes, trimming one trailing newline and trailing spaces, and returning a duplicated string.
- Exposes helpers for subsystem, controller, namespace, and path objects by using their sysfs directory accessors.

Important dependencies:
- Linux file APIs: `open`, `read`, `write`, `close`.
- `asprintf()` for path construction.
- cleanup helpers for fd/free management.
- libnvme tree sysfs directory accessors.

Research notes:
- `libnvme_set_attr()` returns the raw `write()` result on success, not normalized zero.
- `libnvme_get_attr()` returns `NULL` for open/read failure or empty trimmed value; it resets `errno` to zero after successful reads.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/linux.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/linux.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/linux.h

Public Linux-specific libnvme utility declarations, mostly around authentication/key handling and host identity.

Key API areas:
- DH-HMAC-CHAP:
  - HMAC algorithm enum
  - DHCHAP key generation
  - raw secret creation
- Linux keyring operations:
  - lookup keyring
  - describe key serial
  - lookup key
  - link keyring into session keyring
  - read/update key payload
- TLS PSK handling:
  - scan TLS keys
  - insert retained TLS keys
  - versioned/compat insertion
  - generate TLS key identity
  - revoke TLS keys
  - export/import PSK interchange format
- Host identity:
  - generate host NQN
  - generate host NQN from host ID
  - generate host ID
  - read host NQN/host ID from default config locations

Research notes:
- This header is declaration-only in the researched group; implementations are elsewhere in libnvme.
- The APIs bridge NVMe/TCP security material with Linux kernel keyrings and libnvme configuration flows.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/linux.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/log.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/log.c

Basic libnvme logging implementation.

Key behavior:
- `write_all()` writes a full buffer to a file descriptor, retrying on `EINTR` and `EAGAIN`.
- `__libnvme_msg()` filters by log level, builds optional timestamp/PID/function-name prefixes, formats the message, and writes it to the context log fd.
- Timestamp uses `CLOCK_MONOTONIC` unless `LOG_CLOCK` is overridden.
- Public setters/getters manage log level, PID inclusion, and timestamp inclusion.

Research notes:
- Logging assumes a valid `struct libnvme_global_ctx`; there is no NULL-context fallback here.
- If final write fails, it reports through `perror()`, not libnvme logging, avoiding recursion.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/log.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mem-linux.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mem-linux.c

Linux memory allocation helpers for libnvme.

Key behavior:
- `libnvme_alloc()` page-aligns allocation size to 4 KiB, uses `posix_memalign()` with system page size alignment, and zeroes the buffer.
- `libnvme_realloc()` allocates a fresh aligned buffer, copies up to `min(old_len, len)` using `malloc_usable_size()`, and frees the old pointer on success.
- `libnvme_free()` wraps `free()`.
- `libnvme_alloc_huge()`:
  - Uses normal aligned allocation for buffers smaller than `HUGE_MIN` (`0x80000`).
  - Tries `mmap(... MAP_HUGETLB ...)` for larger allocations.
  - Falls back to 2 MiB-aligned `posix_memalign()` plus `madvise(... MADV_HUGEPAGE ...)`.
- `libnvme_free_huge()` frees either heap-backed allocation or `munmap()`s huge-page mapping based on descriptor metadata.

Research notes:
- The huge allocation descriptor records whether cleanup should use `free()` or `munmap()`.
- `libnvme_realloc()` preserves the original buffer on allocation failure.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mem-linux.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mem-win.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mem-win.c

Windows memory allocation helpers matching the public `mem.h` API.

Key behavior:
- Defines a local `getpagesize()` using `GetSystemInfo()`.
- `libnvme_alloc()` rounds to 4 KiB, allocates with `_aligned_malloc()` using system page-size alignment, and zeroes memory.
- `libnvme_realloc()` handles NULL as allocation, determines old size with `_aligned_msize()`, allocates a new aligned buffer, copies preserved data, and frees old memory on success.
- `libnvme_free()` wraps `_aligned_free()`.
- `libnvme_alloc_huge()`:
  - Uses regular aligned allocation below the large-page threshold.
  - Tries `VirtualAlloc(... MEM_LARGE_PAGES ...)` when large pages are available.
  - Falls back to regular `VirtualAlloc()`.
  - Finally falls back to `_aligned_malloc()` with large-page or page-size alignment.
- `libnvme_free_huge()` uses `_aligned_free()` or `VirtualFree()` based on descriptor metadata.

Research notes:
- Large-page allocation requires Windows privilege (`SeLockMemoryPrivilege`), so the fallback chain is important.
- The implementation mirrors Linux metadata semantics: descriptor tells the free path whether the memory is libnvme heap-backed or OS virtual allocation-backed.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mem-win.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mem.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mem.h

Public memory allocation API for libnvme.

Key declarations:
- `libnvme_alloc(size_t len)` for zero-initialized libnvme-compatible allocation.
- `libnvme_realloc(void *p, size_t len)` preserving old contents and zero-initializing newly allocated portions.
- `libnvme_free(void *p)`.
- `struct libnvme_mem_huge`, containing:
  - allocation length
  - whether allocation came from libnvme heap allocator
  - pointer
- `libnvme_alloc_huge()` and `libnvme_free_huge()`.

Research notes:
- The header abstracts platform differences between POSIX aligned allocation/mmap and Windows aligned heap/VirtualAlloc.
- Callers must retain the huge allocation descriptor for correct cleanup.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mi-mctp-compat.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mi-mctp-compat.h

Compatibility definitions for systems whose installed headers lack Linux MCTP socket definitions.

Contents:
- Defines `mctp_eid_t`.
- Defines `struct mctp_addr`.
- Defines `struct sockaddr_mctp`.
- Defines MCTP constants:
  - `MCTP_NET_ANY`
  - `MCTP_ADDR_NULL`
  - `MCTP_ADDR_ANY`
  - `MCTP_TAG_MASK`
  - `MCTP_TAG_OWNER`

Research notes:
- This is only used when `NVME_HAVE_LINUX_MCTP_H` is false.
- It keeps MCTP support buildable on systems where `linux/mctp.h` has not propagated into standard include paths.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mi-mctp-compat.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mi-mctp.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mi-mctp.c

MCTP transport implementation for NVMe-MI endpoints.

Key behavior:
- Uses Linux `AF_MCTP` datagram sockets for NVMe-MI messages.
- Provides compatibility definitions for older MCTP tag allocation ioctls.
- Keeps transport state in `struct libnvme_mi_transport_mctp`: network ID, endpoint ID, command socket, AEM socket, and reusable response buffers.
- Abstracts socket operations through `struct __mi_mctp_socket_ops`, allowing tests to override socket/send/recv/poll/ioctl behavior.
- Allocates and drops MCTP tags where supported; falls back to owner-tag behavior if explicit allocation is unavailable.
- Sends MI requests as iovec fragments:
  - header excluding MCTP type byte
  - optional payload
  - MIC
- Receives responses into a linear buffer, restores the MCTP type byte, splits header/data/MIC back into libnvme response structures, and preserves MIC for upper-layer validation.
- Handles “More Processing Required” responses in the transport layer so the MCTP tag remains allocated while waiting for the final response.
- Provides AEM support:
  - opens a nonblocking AEM socket
  - returns pollable fd
  - purges pending AEM datagrams
  - reads async event messages
- Provides endpoint descriptions like `mctp: net <id> eid <id>`.
- With `CONFIG_DBUS`, scans `mctpd` over D-Bus for endpoints supporting NVMe-MI message type and adds them to a new global context.
- Without `CONFIG_DBUS`, `libnvme_mi_scan_mctp()` returns `NULL`.

Research notes:
- Transport `mic_enabled = true`, so upper layers calculate and verify CRC/MIC for MCTP.
- Default opened endpoint timeout is set to 5000 ms, based on conservative MCTP-over-I2C timing.
- Response buffer allocation grows dynamically when requested response size exceeds the cached buffer.
- The D-Bus scan path de-duplicates by `(network, eid)`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mi-mctp.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mi-types.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mi-types.h

NVMe-MI wire protocol type definitions.

Key definitions:
- `NVME_MI_MSGTYPE_NVME` (`0x84`), the MCTP NVMe message type with MIC bit set.
- MI message type enum:
  - control primitive
  - MI command
  - Admin command
  - PCIe command
  - asynchronous event
- Request/response direction enum.
- MI response status enum with standard NVMe-MI status codes.
- Packed wire structs:
  - generic MI message header
  - generic response
  - MI request/response headers
  - Admin request/response headers
  - Control request/response structs
- MI command opcode enum for Read MI Data, Health Status Poll, Configuration Set/Get.
- Data Structure Type enum for subsystem, port, controller list, controller info, optional command support, and MEB support.
- Configuration IDs and SMBus frequency values.
- Asynchronous Event Message structures:
  - supported list header/item
  - enable list header/item
  - occurrence data
  - occurrence list header
  - full AEM message header
- Declares bitfield helper functions for AEM supported/enabled/event occurrence fields.

Research notes:
- The file is protocol/wire-layout focused, separate from higher-level NVMe-MI payload structures in `nvme-types-mi.h`.
- Packed attributes and explicit endian types are essential because these structures map directly to MI/MCTP payloads.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mi-types.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mi.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mi.c

Core NVMe-MI implementation: endpoint lifecycle, MI/Admin message submission, controller scanning, quirk handling, status parsing, and AEM state machine.

Key behavior:
- Parses `mctp:<net>,<eid>` and `mctp:<net>,<eid>:<ctrl-id>` device names.
- Initializes MI transport handles and closes MI controller handles.
- Probes endpoints once for model-specific quirks unless disabled in the global context.
- Uses an Identify Controller command via MI to detect a Samsung model requiring a minimum inter-command delay.
- Implements endpoint initialization with default timeout, endpoint/controller lists, and submit hooks.
- Creates controller transport handles under an MI endpoint.
- Scans endpoints by issuing Read MI Data Controller List and creating handles for returned controller IDs.
- Calculates and verifies MI MIC using CRC32C-like update logic.
- Central `libnvme_mi_submit()`:
  - validates header alignment and sizes
  - invokes submit-entry hook
  - performs quirk probing
  - calculates MIC
  - inserts quirk delay when needed
  - calls transport submit
  - validates MIC, message type, response direction, and command slot
  - invokes submit-exit hook
- Provides raw admin transfer and passthrough support over MI, including NVMe-MI DLEN/DOFF limits and no bidirectional transfer support.
- Provides Control Primitive execution.
- Provides MI command helpers:
  - raw MI transfer
  - Read MI Data subsystem/port/controller-list/controller-info
  - Subsystem Health Status Poll
  - Configuration Get/Set
  - Asynchronous Event configuration Get/Set
- Closes endpoints by closing child transport handles, invoking transport close, unlinking from global context, and freeing.
- Implements MI status string mapping.
- Implements AEM bitfield helpers and validation helpers.
- Implements AEM enable/disable/process flow:
  - opens AEM transport path
  - disables preexisting enabled events
  - enables requested event IDs
  - validates occurrence lists
  - stores callback context
  - exposes pollable fd
  - lets callbacks iterate events with `libnvme_mi_aem_get_next_event()`
  - ACKs events when callback requests `NVME_MI_AEM_HNA_ACK`

Research notes:
- MI returns use mixed conventions: negative errno-style errors for local/transport/protocol problems and NVMe/MI status values for device responses.
- Admin passthrough enforces 4096-byte data length and rejects bidirectional transfers.
- AEM processing uses an internal context whose event payload pointers are valid only during callback processing.
- Duplicate AEM generation numbers are treated as no new events.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mi.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mi.h

Public NVMe Management Interface API for libnvme-mi.

Key API areas:
- Documents MI topology:
  - endpoint represents the remote MI-capable management endpoint
  - controller transport handles represent NVMe controllers behind an endpoint
- Defines `libnvme_mi_ep_t`.
- Endpoint operations:
  - set CSI bit
  - iterate endpoints in a global context
  - set/get timeout
  - set MPRT maximum wait
  - open MCTP endpoint
  - close endpoint
  - scan MCTP via D-Bus
  - scan endpoint for controllers
  - create controller transport handle
  - get controller ID
  - describe endpoint
- MI tracing hooks:
  - endpoint submit-entry callback
  - endpoint submit-exit callback
  - weak global submit-entry/exit hooks
- MI command API:
  - raw MI transfer
  - Read MI Data subsystem, port, controller list, controller info
  - Subsystem Health Status Poll
  - Configuration Get/Set
  - inline helpers for SMBus frequency, MCTP MTU, and health status change clearing
  - async event configuration get/set and ACK helper
- Admin channel:
  - raw Admin transfer over MI.
- Control primitive:
  - `libnvme_mi_control()`.
- AEM API:
  - handler next-action enum
  - event structure
  - enabled-map structure
  - AEM config structure
  - get pollable fd
  - enable/get-enabled/disable/process
  - iterate event payloads during callback

Research notes:
- The header explicitly separates endpoint-level MI commands from controller-targeted Admin commands.
- It documents expected return conventions: zero success, negative communication/protocol errors, and positive MI status errors.
- It notes that Admin `_args` fd/timeout fields are ignored for MI, though implementation supports passthrough command timeout override on the endpoint.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/mi.h -->