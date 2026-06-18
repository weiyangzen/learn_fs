# Research: subset-b-005994

This grouped report covers Linux UAPI headers from `sources/distributed-fs/ceph-client/include/uapi/linux`. Each file section is delimited for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tipc_netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tipc_netlink.h

Purpose: Defines the generic netlink ABI for TIPC v2 management. It names the family (`TIPCv2`), version, commands, and nested attribute IDs used by userspace tools and kernel TIPC netlink handlers to inspect and mutate bearers, media, links, sockets, publications, nodes, network identity, monitors, peers, and crypto keys.

Important APIs/types/functions: The main command enum includes legacy dispatch plus bearer enable/disable/get/set/add, socket/publication/link/media/node/net/name-table/monitor queries, peer removal, UDP remote IP lookup, key set/flush, and legacy address get. Top-level `TIPC_NLA_*` attributes wrap nested bearer, socket, publication, link, media, node, net, name-table, monitor, and monitor-peer data. Per-object enums describe typed netlink attributes such as bearer name/domain/UDP opts, socket addr/ref/connection/stat/group, link MTU/state/stats, media properties, node ID/key/rekeying, network ID/address/nodeid, publication range/scope/key, monitor peer maps, socket-group state, connection peer/type/instance, socket stats, link/media/bearer properties, and detailed link statistics.

Control flow: This header has no executable flow beyond enum values. Runtime flow is generic-netlink request/response: userspace sends one `TIPC_NL_*` command with nested `TIPC_NLA_*` payloads; the kernel validates nested attribute policy, reads command-specific attributes, and returns multicast or dump-style nested replies for GET commands or mutates TIPC state for SET/ADD/REMOVE/FLUSH commands.

State and persistence behavior: The ABI exposes live in-kernel TIPC state. Bearer/media/link properties and net/node/key fields can alter kernel networking behavior, but this header itself stores no state. Persistence is external to the caller or service that replays configuration.

Dependencies and integration points: Integrates with Linux generic netlink, the TIPC subsystem, TIPC tooling such as `tipc`, and socket diagnostics. Attribute comments encode expected payload types (`u32`, `u64`, string, flag, nested, TLV, `sockaddr_storage`) and must remain synchronized with kernel netlink policies.

Risks: ABI numbers are stable once released; reordering breaks userspace. Nested attribute parsing must reject malformed lengths and missing mandatory fields. Key-management and bearer commands affect network reachability and security. Stats and state dumps need consistent padding and 64-bit alignment for cross-architecture callers.

Test signals: Validate with `tools/net/tipc` or equivalent netlink tests covering each command, malformed/nested attributes, dump requests, legacy address mode, UDP bearer options, key set/flush, and link-stat reset. Compile-time UAPI tests should verify max constants and userspace inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tipc_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tipc_sockets_diag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tipc_sockets_diag.h

Purpose: Defines the AF_TIPC socket diagnostic request structure used with Linux sock_diag to query open TIPC sockets.

Important APIs/types/functions: `struct tipc_sock_diag_req` contains `sdiag_family` (must be `AF_TIPC`), `sdiag_protocol` (must be zero), zero padding, and `tidiag_states` to filter queried socket states.

Control flow: Userspace submits this request to the sock_diag netlink interface. The kernel filters TIPC sockets by requested states and emits diagnostic socket records through the common sock_diag path.

State and persistence behavior: The structure observes transient kernel socket state only. It does not configure or persist anything.

Dependencies and integration points: Includes `linux/types.h` and `linux/sock_diag.h`; integrates with AF_TIPC, netlink sock_diag, and diagnostic tools such as `ss`.

Risks: The ABI depends on strict zeroing of protocol and padding. Mismatched family or stale state masks should fail or return no results predictably.

Test signals: Exercise sock_diag TIPC dumps for empty and active sockets, all state masks, nonzero padding/protocol rejection, and 32/64-bit userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tipc_sockets_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tls.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tls.h

Purpose: Defines the Linux kernel TLS UAPI for socket options, protocol versions, supported ciphers, crypto parameter structures, and TLS netlink/info attributes.

Important APIs/types/functions: Socket options include `TLS_TX`, `TLS_RX`, TX zerocopy read-only, opportunistic RX no-padding, and max TX payload length. Version helpers encode/decode TLS 1.2 and 1.3. Cipher constants cover AES-GCM-128/256, AES-CCM-128, ChaCha20-Poly1305, SM4-GCM/CCM, and ARIA-GCM-128/256 with per-cipher IV, key, salt, tag, and record-sequence sizes. `struct tls_crypto_info` is the common version/cipher prefix; cipher-specific `tls12_crypto_info_*` structs append keying material. TLS info enum exposes version, cipher, TX/RX config, zerocopy, no-pad, and payload length. Config states include base, software, hardware, and hardware-record modes.

Control flow: Userspace configures a TCP socket with `setsockopt(SOL_TLS, TLS_TX/TLS_RX, struct tls*_crypto_info_*)`; the kernel validates version/cipher and key lengths, then performs software or device-offloaded record processing. Info attributes are used for querying negotiated kernel TLS state.

State and persistence behavior: TLS crypto state lives in the socket and lasts until socket close or reconfiguration permitted by the kernel. Record sequence arrays are caller-provided starting state, so reuse or incorrect endianness can compromise security.

Dependencies and integration points: Includes `linux/types.h`; integrates with kTLS, TCP sockets, crypto API, NIC TLS offload, sendfile zerocopy, and netlink/diagnostic reporting.

Risks: ABI structs carry raw keying material and must be exact size. Ciphers differ in salt/IV layout, notably ChaCha20-Poly1305 salt size zero and 12-byte IV. Record sequence handling, version/cipher mismatches, and hardware-offload fallback are security-sensitive.

Test signals: Compile userspace against all structs, configure TX/RX for each supported cipher, test TLS 1.2/1.3 version rejection paths, verify record sequence progression, query `TLS_INFO_*`, and run kTLS selftests with software and offload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/toshiba.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/toshiba.h

Purpose: Provides the historical userspace ABI for Toshiba laptop SMM/ACPI access through `/proc` and character devices.

Important APIs/types/functions: Path macros identify `TOSH_PROC`, `TOSH_DEVICE`, `TOSHIBA_ACPI_PROC`, and `TOSHIBA_ACPI_DEVICE`. The `SMMRegisters` typedef is a packed/aligned register block carrying CPU register-style fields (`eax`, `ebx`, `ecx`, `edx`, `esi`, `edi`) for firmware calls. Ioctls `TOSH_SMM` and `TOSHIBA_ACPI_SCI` use `_IOWR('t', ...)` with that register block.

Control flow: Userspace opens the Toshiba device node and issues ioctl calls with a populated register block. The driver copies the block, performs a firmware/SMM or ACPI SCI operation, then copies updated register values back.

State and persistence behavior: No state is held in the header. Runtime state is firmware/platform-specific and may change hardware settings immediately; persistence depends on firmware and platform policy.

Dependencies and integration points: Depends on Linux ioctl encoding and the Toshiba laptop driver. The ABI must preserve structure packing because firmware calls map directly to register values.

Risks: Firmware access is privileged and platform-specific; invalid register combinations can fail unpredictably or affect hardware. ABI packing/alignment is critical across compilers and architectures.

Test signals: Build ioctl clients on 32/64-bit, verify `sizeof(SMMRegisters)` and ioctl numbers, run on supported Toshiba hardware or mocked driver paths, and test invalid command handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/toshiba.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tps6594_pfsm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tps6594_pfsm.h

Purpose: Defines userspace ioctls for controlling the TPS6594 PMIC pre-configurable finite state machine.

Important APIs/types/functions: `struct pmic_state_opt` carries state options as `gpio_retention` and `ddr_retention` booleans/bytes. Ioctls under base `'P'` include standby, low-power standby, update PGM, set active state, set MCU-only state, and set retention state.

Control flow: Userspace opens the PMIC PFSM device and issues an ioctl. Some commands are pure transitions; MCU-only and retention transitions pass `pmic_state_opt` via `_IOW` so the kernel programs retention policy before state change.

State and persistence behavior: Commands alter PMIC power state and retention behavior. Effects may outlive the calling process and can influence system suspend/resume or power domains.

Dependencies and integration points: Includes `linux/const.h`, `linux/ioctl.h`, and `linux/types.h`; integrates with the TPS6594 PMIC driver and platform power-management stack.

Risks: Incorrect transition requests may power down domains unexpectedly. ABI leaves reserved expansion minimal, so future flags need compatibility care.

Test signals: Validate ioctl numbers, userspace structure size, permission checks, transition success/failure on supported boards, and retention options across suspend/resume cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tps6594_pfsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/trace_mmap.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/trace_mmap.h

Purpose: Defines metadata shared with userspace for mmap-backed tracing buffers.

Important APIs/types/functions: `struct trace_buffer_meta` exposes buffer metadata including event sub-buffer size/count, reader identity, flags, entries, overrun count, read counters, and reserved fields for future expansion. `TRACE_MMAP_IOCTL_GET_READER` retrieves reader state.

Control flow: A tracing consumer maps a trace buffer and reads metadata to coordinate sub-buffer consumption. The ioctl provides an explicit reader pointer/index update path for consumers that cannot infer it from mapped metadata alone.

State and persistence behavior: Metadata is live shared state maintained by tracing infrastructure. It is volatile and tied to the tracing instance and mapping lifetime.

Dependencies and integration points: Depends on `linux/types.h`, tracing ring-buffer internals, and ioctl plumbing. Consumers include tracing tools that avoid copy-heavy reads.

Risks: Shared-memory ABI must handle producer/consumer races, alignment, and reserved-field zeroing. Readers need memory-ordering discipline around counters and buffer indices.

Test signals: mmap tracing buffers, verify metadata updates under high event rates, ioctl reader retrieval, overrun accounting, sub-buffer wraparound, and 32/64-bit layout stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/trace_mmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tty.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tty.h

Purpose: Defines public TTY line discipline numbers and the total line-discipline count.

Important APIs/types/functions: Constants map discipline IDs such as `N_TTY`, SLIP, PPP, AX.25, X.25, HDLC, Bluetooth HCI UART, SLCAN, PPS, GSM0710, NFC NCI, Speakup, MCTP, development/testing, and CAN327. `NR_LDISCS` is 31.

Control flow: Userspace passes these IDs to TTY ioctls such as `TIOCSETD`/`TIOCGETD`; the kernel switches or reports the line discipline for the TTY.

State and persistence behavior: Line discipline selection is per-TTY runtime state. It disappears when the TTY closes or is reset.

Dependencies and integration points: Integrates with TTY core, protocol line disciplines, serial drivers, and userspace tools configuring serial protocol stacks.

Risks: Numeric IDs are ABI. Removing or reusing values breaks userspace. Some disciplines are protocol parsers exposed to untrusted serial data, so selecting them has security and stability implications.

Test signals: Compile UAPI users, set/get representative disciplines on pseudo-terminals or serial test devices, and verify out-of-range IDs fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tty.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tty_flags.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/tty_flags.h

Purpose: Defines serial/TTY async flag bit positions and masks shared with userspace.

Important APIs/types/functions: User-visible bit positions include hangup notification, fourport, SAK, speed aliases, skip test, auto IRQ, hard PPS, low latency, buggy UART, autoprobe, and magic multiplier. Kernel/internal positions include initialized, suspended, normal active, boot autoconfig, closing, CTS flow, carrier detect, shared IRQ, and console flow. Masks include `ASYNC_FLAGS`, `ASYNC_DEPRECATED`, `ASYNC_USR_MASK`, speed masks, and `ASYNC_INTERNAL_FLAGS`.

Control flow: Userspace observes or sets allowed flags through serial ioctls; the kernel masks user inputs, preserves internal bits, and applies behavior such as baud aliasing or low-latency handling.

State and persistence behavior: Flags are per-serial-port runtime/configuration state, often initialized from driver defaults or boot probing. Persistence depends on userspace reconfiguration and driver behavior.

Dependencies and integration points: Integrates with serial core, TTY ioctls, setserial-style tools, and driver-specific port configuration.

Risks: User and kernel bit ranges overlap only by explicit masks; incorrect masking can leak internal state or let userspace corrupt driver state. Several user flags are deprecated but retained for ABI.

Test signals: Verify mask behavior, deprecated flag preservation, user/kernel flag separation, speed alias interactions, and 32-bit unsigned shift correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/tty_flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/typelimits.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/typelimits.h

Purpose: Provides kernel UAPI integer limit macros without relying on libc headers.

Important APIs/types/functions: `__KERNEL_INT_MAX` computes signed int max from `~0U >> 1`; `__KERNEL_INT_MIN` derives the minimum as negative max minus one.

Control flow: None; compile-time constants only.

State and persistence behavior: No runtime state.

Dependencies and integration points: Used by UAPI headers that need portable integer bounds in userspace-visible definitions.

Risks: Assumes two's-complement-like signed integer range used by supported Linux ABIs. Macro names are internal-style UAPI and should not conflict with libc `INT_MAX`.

Test signals: Compile under supported architectures and C modes; static assertions should match libc `INT_MAX`/`INT_MIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/typelimits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/types.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/types.h

Purpose: Provides common Linux UAPI scalar, endian-tagged, aligned, and bitwise types for userspace headers.

Important APIs/types/functions: Includes architecture scalar types from `asm/types.h` and POSIX-like kernel types from `linux/posix_types.h`. Defines optional 128-bit signed/unsigned types for non-32-bit userspace. Sparse-aware `__bitwise` tagging annotates endian and checksum types: `__le16`, `__be16`, `__le32`, `__be32`, `__le64`, `__be64`, `__sum16`, `__wsum`, and `__poll_t`. Alignment macros `__aligned_u64`, `__aligned_s64`, `__aligned_be64`, and `__aligned_le64` force 8-byte alignment in UAPI structs.

Control flow: No executable flow; this is a foundational type header.

State and persistence behavior: No state. Its ABI impact is structural layout and compile-time type checking.

Dependencies and integration points: Used by almost every Linux UAPI header, including this work item. Integrates with sparse (`__CHECKER__`) and architecture-specific type definitions.

Risks: Any change affects broad UAPI layout. 64-bit alignment macros are critical for compat ioctls. Endian tags are compile-time only unless checked by sparse.

Test signals: Build UAPI headers standalone for multiple architectures, verify struct layout involving `__aligned_u64`, run sparse checks for endian misuse, and validate 32-bit compat ioctl layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ublk_cmd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ublk_cmd.h

Purpose: Defines the complete userspace ABI for `ublk`, a user-space block device framework built on control commands and `io_uring` command delivery.

Important APIs/types/functions: Control commands cover device add/delete/start/stop, parameter set/get, queue affinity, feature discovery, user recovery, async delete, size update, quiesce, safe stop, and shared-memory buffer registration. IO commands include fetch, commit-and-fetch, need-get-data, buffer register/unregister, and batch prep/commit/fetch. Feature flags describe zero copy, task completion, recovery semantics, unprivileged devices, ioctl encoding, user copy, zoned support, size update, auto buffer registration, quiesce, per-IO daemons, off-daemon buffer registration, batch IO, integrity metadata, safe stop, no auto partition scan, and shared-memory zero-copy. Core structs include `ublksrv_ctrl_cmd`, `ublksrv_ctrl_dev_info`, `ublksrv_io_desc`, `ublk_auto_buf_reg`, `ublksrv_io_cmd`, `ublk_batch_io`, and `ublk_params` with basic/discard/devt/zoned/DMA/segment/integrity sub-parameters. Inline helpers decode op/flags, pack/unpack auto-buffer registration in `sqe->addr`, and encode/decode shared-memory zero-copy addresses.

Control flow: A userspace server creates/configures a device through control ioctls or uring commands, starts queues, then repeatedly fetches block requests, processes them against a backing store, and commits results. Optional modes change the flow: `NEED_GET_DATA` separates write buffer acquisition, user-copy uses `pread`/`pwrite`, auto-buffer registration attaches buffers during fetch, batch IO delivers multiple tags per command, recovery allows server restart, quiesce coordinates upgrade, and shared-memory zero-copy encodes buffer index/offset in request addresses.

State and persistence behavior: Device state constants are dead/live/quiesced/fail-IO. Control info stores queue geometry, owner UID/GID, flags, and server PID. Kernel state persists while the ublk device exists and may survive userspace server restart under recovery flags, but backing data persistence is entirely server-defined.

Dependencies and integration points: Includes `linux/types.h`; references Linux block op semantics, `io_uring` uring_cmd, zoned block definitions from `linux/blkzoned.h`, integrity constants from `linux/fs.h`, udev ownership, and block-device partition scanning.

Risks: This is a complex ABI with many feature interactions. Incorrect flag negotiation can leak uninitialized data (`UBLK_F_USER_COPY` restrictions), hang IO on failed auto-buffer registration, corrupt zoned semantics, mishandle recovery/quiesce, or break 32/64-bit layouts. Address bitfields for queue/tag/buffer and shared-memory zero-copy must stay within documented masks.

Test signals: Run ublk selftests for add/start/stop/delete, feature discovery, read/write/flush/discard/write-zeroes, recovery modes, unprivileged setup, user copy, zoned report/append/reset, resize, quiesce timeout, batch IO, integrity metadata, shared-memory zero-copy, and compat-layout checks for all structs and ioctl encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ublk_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/udf_fs_i.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/udf_fs_i.h

Purpose: Exposes UDF filesystem-specific ioctl numbers for extended attributes, volume identification, and block relocation.

Important APIs/types/functions: `UDF_GETEASIZE` returns extended attribute size, `UDF_GETEABLOCK` reads EA block data, `UDF_GETVOLIDENT` reads the volume identifier, and `UDF_RELOCATE_BLOCKS` performs block relocation via `_IOWR('l', 0x43, long)`.

Control flow: Userspace issues ioctls against a UDF file or filesystem handle; the filesystem driver copies requested metadata or updates the relocation argument.

State and persistence behavior: Query ioctls are read-only. Relocation may alter on-disk block placement and is persistent if supported.

Dependencies and integration points: Integrates with the UDF filesystem driver and Linux ioctl numbering for filesystem-private range `'l', 0x40-0x7f`.

Risks: Pointer-typed ioctls must validate user buffers. Relocation is sensitive to filesystem consistency and media behavior.

Test signals: Mount UDF images, verify EA size/block and volume ID retrieval, fuzz invalid pointers/lengths, and test relocation on disposable images with fsck verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/udf_fs_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/udmabuf.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/udmabuf.h

Purpose: Defines the userspace DMA-BUF creation ABI for exporting memfd-backed memory as dma-buf objects.

Important APIs/types/functions: `UDMABUF_FLAGS_CLOEXEC` controls close-on-exec. `struct udmabuf_create` describes a single memfd, flags, offset, and size. `struct udmabuf_create_item` describes one segment for list creation. `struct udmabuf_create_list` carries common flags, count, and a flexible array of items. Ioctls `UDMABUF_CREATE` and `UDMABUF_CREATE_LIST` use `_IOW('u', ...)`.

Control flow: Userspace creates/seals or prepares memfd storage, opens udmabuf, and issues create ioctl. The kernel validates offsets/sizes, pins or references pages as required, and returns a dma-buf file descriptor.

State and persistence behavior: The exported dma-buf object persists while file descriptors/references exist. Underlying memfd lifetime and mutability influence sharing semantics.

Dependencies and integration points: Includes `linux/types.h` and `linux/ioctl.h`; integrates with dma-buf, memfd, GPU/display/media drivers, and cross-device buffer sharing.

Risks: Offset/size overflow, memfd seal expectations, cache coherency, lifetime management, and list-count validation are important. CLOEXEC defaults affect descriptor leakage across exec.

Test signals: Create single and multi-item buffers, test invalid offsets/sizes/counts, CLOEXEC behavior, dma-buf import by another subsystem, and 32/64-bit struct layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/udmabuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/udp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/udp.h

Purpose: Defines the UDP packet header and Linux UDP socket option/encapsulation constants.

Important APIs/types/functions: `struct udphdr` contains big-endian source port, destination port, length, and checksum. Socket options include `UDP_CORK`, `UDP_ENCAP`, IPv6 checksum disable/accept controls, `UDP_SEGMENT` for GSO size, and `UDP_GRO`. Encapsulation types include ESP-in-UDP, L2TP, GTP0/GTP1U, RXRPC, ESP-in-TCP, and OpenVPN-in-UDP.

Control flow: Packet parsing reads `udphdr`; socket options alter send/receive paths, segmentation aggregation, checksum behavior, or encapsulation demultiplexing.

State and persistence behavior: Socket options are per-socket runtime state. Packet headers are wire-format transient data.

Dependencies and integration points: Includes `linux/types.h`; integrates with IPv4/IPv6 UDP stacks, tunnel drivers, xfrm, GTP, L2TP, RXRPC, OpenVPN, GRO/GSO offload, and packet capture tools.

Risks: Checksum disabling is protocol-sensitive. Encapsulation values overlap with other subsystems and must remain stable. `UDP_SEGMENT` requires correct MTU/offload validation.

Test signals: Validate UDP header layout, setsockopt/getsockopt behavior, UDP GSO/GRO, each encapsulation demux path, IPv6 checksum controls, and packet captures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/udp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/uhid.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/uhid.h

Purpose: Defines the userspace HID device ABI for `/dev/uhid`, allowing a userspace process to create and drive HID devices.

Important APIs/types/functions: Event types cover create/destroy, start/stop, open/close, output, input, get/set report and replies, with legacy aliases retained. `uhid_create2_req` embeds device identity and report descriptor. `uhid_start_req` returns numbered-report flags. Report/input/output structures carry up to `UHID_DATA_MAX` bytes. `struct uhid_event` is a packed tagged union of all request/reply payloads.

Control flow: Userspace writes `UHID_CREATE2`, then handles kernel-generated lifecycle/report/output events read from the device and writes `UHID_INPUT2`, report replies, or destroy events. The kernel extends short events with zeroes and userspace must do the same for short reads.

State and persistence behavior: The virtual HID device exists while the uhid file/session remains active or until destroy. Open/close and start/stop events reflect kernel HID consumer state.

Dependencies and integration points: Includes `linux/input.h`, `linux/types.h`, and `linux/hid.h`; integrates with HID core, input subsystem, Bluetooth/USB emulation layers, and userspace device emulators.

Risks: Packed ABI contains obsolete pointer-based legacy create fields; new code should use `UHID_CREATE2`. Report sizes and IDs must match descriptors. Blocking report requests need timely replies to avoid stalled clients.

Test signals: Create virtual HID devices with numbered/un-numbered reports, send input, handle output and get/set report, verify legacy compatibility, short write/read zero extension, and 32/64-bit packing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/uhid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/uinput.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/uinput.h

Purpose: Defines the userspace input device creation ABI for `/dev/uinput`.

Important APIs/types/functions: `UINPUT_VERSION` is 5 and names are limited by `UINPUT_MAX_NAME_SIZE`. `uinput_setup` configures input ID, name, and force-feedback capacity. `uinput_abs_setup` configures one absolute axis. Ioctls create/destroy devices, set event/key/relative/absolute/misc/LED/sound/FF/switch/property bits, set physical path, get sysfs name, and get version. Force-feedback upload/erase structs coordinate callback requests. Legacy `uinput_user_dev` supports write-based setup.

Control flow: Userspace opens uinput, sets supported bits, configures setup and axes, calls `UI_DEV_CREATE`, writes input events, handles optional FF upload/erase event/ioctl handshake, then destroys or closes the device.

State and persistence behavior: Virtual input device state is kernel runtime state tied to the file descriptor and created device lifetime. Events affect input subsystem state until released.

Dependencies and integration points: Includes `linux/types.h` and `linux/input.h`; integrates with evdev, input core, force-feedback, sysfs, and compositor/desktop input stacks.

Risks: Partial setup may be applied before an ioctl fails. Incorrect capability bits create misleading devices. FF callbacks block until userspace completes the paired end ioctl.

Test signals: Create devices through modern and legacy flows, configure absolute axes, emit events, read from evdev, verify sysfs name/version, and exercise FF upload/erase handshakes and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/uinput.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/uio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/uio.h

Purpose: Defines scatter/gather vector structures and UIO limits for userspace/kernel transfer APIs.

Important APIs/types/functions: `struct iovec` carries `void __user *iov_base` and `__kernel_size_t iov_len`. The file also exposes devmem/dmabuf fragment/token structures (`dmabuf_cmsg`, `dmabuf_token`) for passing dma-buf-backed memory metadata, plus `UIO_FASTIOV` and `UIO_MAXIOV` constants.

Control flow: System calls such as `readv`, `writev`, `sendmsg`, and `recvmsg` iterate iovec arrays to copy or map data. DMABUF token metadata is consumed by networking/device-memory paths that return fragment ownership information.

State and persistence behavior: Iovecs and tokens are transient call arguments or ancillary data. No state is stored by the header.

Dependencies and integration points: Includes `linux/compiler.h` for `__user` and `linux/types.h`; integrates with VFS, sockets, networking, and dma-buf/development memory APIs.

Risks: Overflow when summing lengths, pointer validation, maximum vector counts, and compat pointer sizing are central. New token structs must preserve alignment and reserved fields.

Test signals: Vectored I/O boundary tests, `UIO_MAXIOV` enforcement, zero-length vectors, compat syscalls, ancillary DMABUF metadata round trips, and overflow/fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/uio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/uleds.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/uleds.h

Purpose: Defines the userspace LED device creation ABI.

Important APIs/types/functions: `LED_MAX_NAME_SIZE` is 64. `struct uleds_user_dev` contains a LED class device name and maximum brightness.

Control flow: Userspace writes the structure to the uleds device to create a virtual LED; subsequent brightness control flows through LED class sysfs or related kernel APIs.

State and persistence behavior: The virtual LED exists while the userspace file/session is active. Brightness is runtime state managed by LED core.

Dependencies and integration points: Integrates with the LED subsystem, sysfs LED class, and userspace LED emulators/tests.

Risks: Name truncation/collision and invalid brightness ranges should be handled by the driver. The ABI is small, so future expansion would require a new structure or versioning.

Test signals: Create virtual LEDs, verify sysfs registration/name length, set brightness through LED class, close creator and confirm cleanup, and validate invalid max brightness handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/uleds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ultrasound.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ultrasound.h

Purpose: Provides legacy OSS sequencer macros for programming Gravis Ultrasound synthesizer private events.

Important APIs/types/functions: `_GUS_*` command constants identify voice count, voice on/off/fade/mode/balance/frequency/volume, ramp configuration, volume scale, and voice position operations. `_GUS_CMD` writes an 8-byte `SEQ_PRIVATE` event into the OSS sequencer buffer using `_SEQ_NEEDBUF`, `_seqbuf`, `_seqbufptr`, and `_SEQ_ADVBUF`. Public macros such as `GUS_VOICEON`, `GUS_VOICEFREQ`, and `GUS_RAMPRANGE` pack parameters.

Control flow: Userspace sequencer code invokes a macro, which appends a private event to the sequencer buffer. The OSS sequencer/GUS driver interprets bytes as channel, command, voice, and two 16-bit parameters.

State and persistence behavior: Commands alter synthesizer voice state and hardware playback/ramp settings. State is device runtime state, not persisted by the header.

Dependencies and integration points: Requires OSS sequencer macros and buffer globals from other sound headers. Integrates with legacy GUS hardware support.

Risks: Macros perform unaligned `unsigned short *` writes into byte buffers and assume little host behavior matching legacy ABI. Parameters must be zeroed when unused as documented.

Test signals: Compile legacy OSS clients, verify emitted 8-byte event encoding, run with OSS/GUS emulation if available, and test buffer-advance behavior under near-full sequencer buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ultrasound.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/um_timetravel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/um_timetravel.h

Purpose: Defines the User-Mode Linux time-travel protocol for coordinating simulated time with an external calendar/controller.

Important APIs/types/functions: `struct um_timetravel_msg` carries operation, sequence, and nanosecond time. Operations include ACK, START, REQUEST, WAIT, GET, UPDATE, RUN, FREE_UNTIL, GET_TOD, and BROADCAST. Shared-memory support defines max fd count, fd indices, start ACK ID mask, version 2, capability/flag enums, `union um_timetravel_schedshm_client`, and `struct um_timetravel_schedshm` containing version, length, free-until, current time, running client ID, max clients, and per-client request records.

Control flow: A UML instance sends START, negotiates optional shared-memory fds, requests a run time, waits, and resumes when the controller sends RUN or permits FREE_UNTIL. Shared-memory-capable clients publish requests and current time in shared memory to avoid messages for common operations.

State and persistence behavior: Protocol state is live simulation state: sequence numbers, requested run times, current time, free-until horizon, running client, and per-client capabilities. It is not persistent beyond the controller/UML session.

Dependencies and integration points: Includes `linux/types.h`; integrates with UML, simulation controllers, Unix sockets with fd passing, shared memory mappings, and coordinated virtual time tests.

Risks: Shared memory has explicit writer ownership rules; violating them can corrupt scheduling. Sequence mismatches, stale `free_until`, incorrect controller time-domain conversion, and missing ACK expectations can deadlock simulations.

Test signals: Simulate START/REQUEST/WAIT/RUN cycles, sequence mismatch handling, shared-memory version fallback, multi-client request ordering, FREE_UNTIL behavior, broadcast delivery, fd passing, and log-fd flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/um_timetravel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/un.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/un.h

Purpose: Defines the AF_UNIX socket address structure and a UNIX-specific ioctl.

Important APIs/types/functions: `UNIX_PATH_MAX` is 108. `struct sockaddr_un` contains `sun_family` and `sun_path`. `SIOCUNIXFILE` is a protocol-private ioctl to open a socket file with `O_PATH`.

Control flow: Userspace passes `sockaddr_un` to bind/connect/sendto or receives it from getsockname/getpeername. The ioctl is issued on AF_UNIX sockets for file access semantics provided by the kernel.

State and persistence behavior: Socket address binding is runtime socket/VFS state; pathname sockets may create filesystem entries outside the header's control.

Dependencies and integration points: Includes `linux/socket.h`; integrates with AF_UNIX sockets, VFS pathname sockets, abstract namespace sockets, and socket ioctls.

Risks: `sun_path` may not be NUL-terminated when length-bound, and abstract names begin with NUL. Callers must calculate sockaddr lengths carefully.

Test signals: Bind/connect pathname and abstract sockets, check length handling at 108 bytes, ioctl behavior, and compat with libc `sockaddr_un`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/un.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/unistd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/unistd.h

Purpose: Provides the generic include wrapper for architecture-specific syscall numbers.

Important APIs/types/functions: Includes `asm/unistd.h`, which defines `__NR_*` syscall numbers and related architecture declarations.

Control flow: No runtime flow; userspace compilation resolves syscall constants through the architecture header.

State and persistence behavior: No state.

Dependencies and integration points: Integrates with libc, syscall wrappers, seccomp filters, tracers, and architecture-specific UAPI.

Risks: Architecture-specific syscall numbering must be used; generic code must not assume identical `__NR_*` values across architectures.

Test signals: Compile syscall-using userspace for multiple target architectures and verify expected `__NR_*` presence for seccomp/tracing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/unix_diag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/unix_diag.h

Purpose: Defines AF_UNIX socket diagnostic request, response, and attributes for sock_diag netlink.

Important APIs/types/functions: `struct unix_diag_req` filters by family, protocol, states, inode, show mask, and cookie. Show flags request name, VFS info, peer, pending connections, queue lengths, memory info, and UID. `struct unix_diag_msg` reports family/type/state/inode/cookie. Attribute enum includes name, VFS, peer, icons, receive queue length, meminfo, shutdown, and UID. `unix_diag_vfs` and `unix_diag_rqlen` carry inode/device and queue counters.

Control flow: Userspace sends a diagnostic request through netlink; the kernel filters AF_UNIX sockets and emits messages with requested optional attributes.

State and persistence behavior: Observes transient socket state only. Cookies help correlate sockets across dumps but are not persistent storage.

Dependencies and integration points: Includes `linux/types.h`; integrates with sock_diag, AF_UNIX, netlink diagnostics, and tools like `ss`.

Risks: Optional show flags can expose path, UID, peer, queue, or memory data and must respect permissions. Attribute numbering is ABI-stable.

Test signals: Dump active UNIX sockets with each show flag, verify cookie/inode filters, queue length reporting, pending connection icons, UID exposure, and malformed request handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/unix_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/audio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/audio.h

Purpose: Defines USB Audio Class UAPI constants, class-specific descriptor structures, and helper accessors for UAC1/UAC2/UAC3-style layouts used by host and gadget code.

Important APIs/types/functions: Constants cover UAC versions, audio subclasses, AC/AS/MS descriptor subtypes, request codes, feature-unit controls, processing-unit controls, terminal types, MIDI streaming subtypes, audio format types, endpoint attributes, and status bits. Descriptor structs include audio-control headers, input/output terminals, feature/mixer/selector/processing/extension units, audio-streaming headers, format type I/II/III descriptors, MIDI/audio endpoint descriptors, and status words. Inline helpers compute offsets into variable-length descriptors for channel counts, channel config, names, controls, mixer strings, processing strings, and UAC3 cluster descriptor IDs.

Control flow: USB host/gadget parsers walk class-specific descriptors, using fixed fields and helper offset calculations to interpret topology and supported controls. Control requests use UAC set/get current/min/max/res/mem/stat codes to query or change device state.

State and persistence behavior: Descriptors advertise device capabilities. Actual state is device runtime state for mixer controls, sample rates, feature units, processing units, and endpoint behavior.

Dependencies and integration points: Includes `linux/types.h`; integrates with USB core, ALSA USB audio, gadget functions, MIDI streaming, and descriptor-generation code.

Risks: Variable-length descriptor helpers are offset-sensitive and need length validation before access. Packed USB little-endian fields must not be treated as host-endian. UAC1/UAC2/UAC3 layout differences make parser assumptions risky.

Test signals: Parse real and generated descriptors for terminals, feature units, mixers, processing/extension units, continuous/discrete sample rates, MIDI jacks, endpoint status, malformed length fuzzing, and gadget descriptor round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/cdc-wdm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/cdc-wdm.h

Purpose: Defines the cdc-wdm userspace ioctl for querying maximum command size.

Important APIs/types/functions: `IOCTL_WDM_MAX_COMMAND` uses `_IOR('H', 0xA0, __u16)` to return the device/driver maximum command length.

Control flow: Userspace opens a cdc-wdm device and issues the ioctl before sending management commands, sizing buffers according to the returned maximum.

State and persistence behavior: Read-only query of driver/device capability; no persistent state.

Dependencies and integration points: Includes `linux/types.h`; integrates with USB CDC WDM devices such as modems and MBIM/QMI management channels.

Risks: Callers must still handle short reads/writes and device-specific framing. A stale max value after device reset should be re-queried.

Test signals: Query on supported cdc-wdm devices, verify ioctl return size/value, handle disconnect/reset, and test invalid user pointer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/cdc-wdm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/cdc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/cdc.h

Purpose: Defines USB Communications Device Class constants, functional descriptors, requests, notifications, and NCM/MBIM data structures.

Important APIs/types/functions: Constants cover CDC subclasses/protocols, functional descriptor types, ACM/call-management capabilities, class-specific requests, line coding, control-line bits, Ethernet packet filters, notifications, serial state bits, NCM NTB parameters, NTH/NDP signatures, datagram pointer entries, MBIM signatures, NCM capabilities, NTB formats, and CRC modes. Structs model header, call management, ACM, union, country, network terminal, Ethernet, DMM, MDLM/detail, OBEX, NCM, MBIM and extended MBIM descriptors, line coding, notifications, speed-change notifications, NCM parameter blocks, NTH16/NTH32, NDP16/NDP32, DPE16/DPE32, and NCM input-size negotiation.

Control flow: During enumeration, host drivers parse descriptors to bind ACM, Ethernet, NCM, MBIM, or other CDC functions. Runtime control requests configure line coding, control line state, Ethernet filters, NTB format/input size, datagram size, CRC mode, and encapsulated commands. Interrupt notifications report network, serial, response, or speed changes.

State and persistence behavior: Descriptors are static capability data. Runtime state includes line coding, DTR/RTS, packet filters, NTB format and input size, CRC mode, network connection, and NCM/MBIM transfer aggregation parameters.

Dependencies and integration points: Includes `linux/types.h`; integrates with USB core, CDC ACM, cdc_ether, cdc_ncm, cdc_mbim, modem-management stacks, and gadget implementations.

Risks: NCM/MBIM structures are wire-format and alignment-sensitive. NTB length/index validation is security-critical. Descriptor capability bits and request availability must match device behavior.

Test signals: Enumerate descriptor variants, negotiate line coding/control lines, exercise Ethernet packet filters, NCM NTB16/NTB32 aggregation, MBIM IPS/DSS sessions, notification parsing, and malformed descriptor/NTB fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/cdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/ch11.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/ch11.h

Purpose: Defines USB hub and port constants/structures from USB chapter 11 for hub control, status, descriptors, transaction translators, and SuperSpeed ports.

Important APIs/types/functions: Constants include max child/port counts, hub/port request types, hub class requests, hub and port feature selectors, link power management selectors, remote wake masks, port status/change bits, SuperSpeed link states/speed masks, extended port lane helpers, hub characteristic masks, TT think-time modes, and descriptor sizes. Structs include `usb_port_status`, hub descriptors, hub status, SuperSpeed hub descriptors, and related packed status records.

Control flow: Hub drivers issue class requests to get/clear/set hub and port features, read port status, reset ports, manage TT state, set hub depth, and retrieve error counts. Status/change bits drive enumeration, power, reset, suspend/resume, and link-state transitions.

State and persistence behavior: Hub and port state is live hardware state: connection, enable, power, overcurrent, reset, link state, speed, wake masks, and change latches. The header has no persistence.

Dependencies and integration points: Includes `linux/types.h` and depends on request/type macros from USB chapter 9. Integrates with USB hub core, xHCI/EHCI/OHCI/UHCI host controllers, and hub diagnostics.

Risks: Bit definitions differ between USB2 and SuperSpeed contexts. Change bits are write-one-to-clear hardware latches; mishandling can miss events. Port power/reset sequencing is timing-sensitive.

Test signals: Hub enumeration tests, port connect/disconnect/reset, overcurrent/change clearing, SuperSpeed link-state decoding, lane count helper validation, TT buffer requests, and descriptor size checks against real hubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/ch11.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/ch9.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/ch9.h

Purpose: Provides the central USB device-model UAPI: control request constants, standard descriptor structures, class codes, endpoint helpers, capability descriptors, speeds, states, and link-power definitions from USB chapter 9 and related ECNs/specs.

Important APIs/types/functions: Defines directions, request types/recipients, standard and wireless/PD requests, feature selectors, status bits, `struct usb_ctrlrequest`, descriptor type constants, packed descriptor structs for device/config/string/interface/endpoint/qualifier/OTG/debug/IAD/security/BOS/capabilities/PD/PTM/wireless/authentication, endpoint transfer/sync/usage masks, inline endpoint classification helpers, SuperSpeed companion helpers, speed/state/link-state enums, and LPM selector structures.

Control flow: USB host/gadget code uses `usb_ctrlrequest` for setup packets, parses descriptors returned by GET_DESCRIPTOR, sets configuration/interface/feature state, and classifies endpoints through inline helpers. Device state progresses through attached, powered, default, address, configured, suspended, and related wireless/auth states.

State and persistence behavior: The header defines wire-format descriptors and runtime state labels. Actual state lives in USB devices, host controller drivers, and gadget functions; descriptors may be static firmware/gadget data.

Dependencies and integration points: Includes `linux/types.h` and `asm/byteorder.h`; used by usbfs, kernel USB host APIs, gadget APIs, FunctionFS, raw gadget, class drivers, and userspace descriptor tooling.

Risks: All descriptors are packed and many fields are little-endian on the wire. Device/config descriptors read from `/dev/bus/usb` are an exception where the kernel may convert selected fields. Endpoint helper correctness depends on masks and endian conversion. ABI constants are broadly consumed and must not change.

Test signals: Descriptor layout static assertions, endpoint helper unit tests, enumeration against USB2/USB3 devices, BOS/capability parsing, LPM timeout validation, usbfs/gadget descriptor round trips, and malformed descriptor fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/ch9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/charger.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/charger.h

Purpose: Defines USB charger type and state enums shared with userspace or platform code.

Important APIs/types/functions: Charger type values identify unknown, SDP, DCP, CDP, ACA, and Apple-style charger classes. Charger state values represent removed, present, online, and unknown states.

Control flow: USB charger detection code classifies a port/charger and reports state to power-supply or platform consumers.

State and persistence behavior: Charger state is live physical/power state. It changes with cable attachment, negotiation, and removal.

Dependencies and integration points: Integrates with USB PHY/charger detection, power_supply, Type-C/BC1.2 policy, and platform battery charging logic.

Risks: Misclassification can overdraw current or undercharge. Vendor-specific Apple currents require platform policy beyond enum values.

Test signals: Simulate or attach each charger type, verify state transitions on plug/unplug, power-supply reporting, and unknown/fallback handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/charger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/functionfs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/functionfs.h

Purpose: Defines the FunctionFS userspace gadget ABI for supplying descriptors/strings, receiving control events, endpoint ioctls, and DMABUF-backed transfers.

Important APIs/types/functions: Magic values identify descriptor and string blocks, with v2 descriptor flags for FS/HS/SS descriptors, MS OS descriptors, virtual addresses, eventfd, all-control-recipient handling, and config0 setup. Structs include endpoint descriptor without audio fields, DFU functional descriptor, v2 and legacy descriptor headers, MS OS descriptor headers, extended compatibility/property descriptors, `usb_functionfs_strings_head`, `usb_functionfs_event`, and `usb_ffs_dmabuf_transfer_req`. Ioctls expose FIFO status/flush, clear halt, interface/endpoint reverse mapping, endpoint descriptor retrieval, and DMABUF attach/detach/transfer.

Control flow: Userspace mounts FunctionFS, writes descriptor and string blobs to ep0, reads bind/enable/setup/suspend/resume events from ep0, handles setup data phases, and performs I/O on endpoint files. Optional DMABUF flow attaches a dma-buf fd to an endpoint and enqueues it for transfer.

State and persistence behavior: Function state is tied to the FunctionFS instance, descriptor upload, gadget binding, endpoint enablement, and open endpoint file descriptors. Attached DMABUFs are automatically detached when endpoint descriptors close.

Dependencies and integration points: Includes USB chapter 9 definitions and Linux ioctl/types. Integrates with configfs gadget composition, USB gadget controller drivers, DFU, Microsoft OS descriptors, eventfd, and dma-buf.

Risks: Descriptor blobs are variable-layout and endian-specific; unrecognized v2 flags are rejected. Setup direction controls data phase ordering. DMABUF lifetime and endpoint shutdown races must be handled carefully.

Test signals: Mount FunctionFS and enumerate FS/HS/SS gadgets, validate v2/legacy descriptor parsing, string language tables, setup/event sequencing, endpoint reverse mapping, halt/fifo ioctls, DMABUF attach/transfer/detach, and malformed descriptor fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/functionfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/g_hid.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/g_hid.h

Purpose: Defines platform/configuration data for the USB HID gadget function.

Important APIs/types/functions: `struct hidg_func_descriptor` carries subclass, protocol, report length, report descriptor length, and pointer to report descriptor data.

Control flow: Gadget setup code supplies this descriptor to instantiate a HID function. The gadget exposes HID descriptors and endpoints according to the report descriptor and report length.

State and persistence behavior: Descriptor data defines static gadget capabilities for the lifetime of the configured function. HID runtime state depends on host traffic and gadget implementation.

Dependencies and integration points: Integrates with USB gadget HID function, configfs/platform gadget setup, HID class drivers, and host input stacks.

Risks: Pointer field is unsuitable as a stable cross-process wire ABI and is mainly for in-kernel/platform setup. Report length must match descriptor semantics to avoid truncated or stalled reports.

Test signals: Instantiate HID gadget with keyboard/mouse/custom descriptors, enumerate on a host, validate report descriptor and report I/O lengths, and test invalid descriptor sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/g_hid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/g_printer.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/g_printer.h

Purpose: Defines ioctl ABI for the USB printer gadget function.

Important APIs/types/functions: Printer gadget ioctls return device ID, get/set bidirectional mode, and soft-reset printer state. They use printer gadget-specific ioctl numbers and character-device interaction.

Control flow: Userspace opens the printer gadget device, queries identity, toggles bidirectional behavior, exchanges print data through reads/writes, and can request a soft reset.

State and persistence behavior: Bidirectional mode and soft-reset effects are runtime gadget state. Device ID is configured gadget identity.

Dependencies and integration points: Integrates with the USB gadget printer function, host USB printer class drivers, and userspace print emulators.

Risks: Host class drivers expect IEEE-1284-compatible IDs and reset behavior. Mode changes during active transfers need synchronization.

Test signals: Enumerate as printer gadget, query device ID, toggle bidirectional mode, exchange bulk data with host printer class driver, and test soft reset during idle and active transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/g_printer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/g_uvc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/g_uvc.h

Purpose: Defines UVC gadget-specific event and request codes used by userspace video gadget functions.

Important APIs/types/functions: The header exposes UVC gadget event constants for connect/disconnect, setup, data, stream on/off, and request handling, plus payload structures for UVC control exchanges where present.

Control flow: Userspace UVC gadget code receives events from the gadget/video device, responds to class-specific control setup/data phases, and starts/stops streaming in response to host negotiation.

State and persistence behavior: Streaming state, negotiated probe/commit controls, and control values are runtime gadget state maintained by userspace and kernel gadget glue.

Dependencies and integration points: Integrates with USB gadget UVC, V4L2, UVC class descriptors from `usb/video.h`, and host webcam drivers.

Risks: Probe/commit negotiation must match descriptors and frame intervals. Incorrect event handling can stall enumeration or streaming.

Test signals: Enumerate UVC gadget on a host, handle probe/commit controls, stream video frames, test stream on/off events, and fuzz malformed class control requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/g_uvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/gadgetfs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/gadgetfs.h

Purpose: Defines the legacy GadgetFS userspace gadget ABI for events and endpoint ioctls.

Important APIs/types/functions: Event types include connect, disconnect, setup, suspend, and nop. `struct usb_gadgetfs_event` carries event type and setup packet for control requests. Endpoint ioctls mirror gadget endpoint controls: FIFO status, FIFO flush, and clear halt.

Control flow: Userspace writes descriptors to ep0, reads gadget events, handles setup requests and data phases, and performs endpoint I/O. Endpoint ioctls inspect or modify endpoint FIFO/halt state.

State and persistence behavior: Gadget state is runtime and tied to open GadgetFS files, descriptor upload, host connection, and endpoint enablement.

Dependencies and integration points: Includes USB chapter 9 definitions; integrates with USB gadget UDC drivers and legacy userspace gadget implementations.

Risks: GadgetFS is older and less structured than FunctionFS. Correct setup direction/data phase handling and descriptor validity are critical.

Test signals: Enumerate a GadgetFS sample gadget, handle setup/suspend/disconnect events, use endpoint FIFO/halt ioctls, and verify behavior across host reset/reconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/gadgetfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/midi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/midi.h

Purpose: Defines USB MIDI 2.0 group terminal block descriptor constants and structures.

Important APIs/types/functions: Constants describe MIDI streaming descriptor subtypes and group terminal block types/protocols. Structures model group terminal block descriptors and block headers with fields for block ID, group terminal count, group counts, protocol, maximum input/output bandwidth, and string indices.

Control flow: USB MIDI host/gadget code parses descriptors during enumeration to discover MIDI 2.0 group terminal blocks and supported protocols/bandwidth.

State and persistence behavior: Descriptor data is static capability advertisement. Runtime MIDI stream state lives in class drivers and endpoints.

Dependencies and integration points: Includes USB audio/MIDI class context and Linux types; integrates with ALSA rawmidi/UMP support and USB gadget MIDI functions.

Risks: Descriptor lengths and protocol values must match USB MIDI spec revisions. Misreported bandwidth/group counts can break host routing.

Test signals: Parse MIDI 1.0 and MIDI 2.0 descriptors, enumerate gadget MIDI devices, verify group terminal counts/protocols, and fuzz descriptor length/count mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/midi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/raw_gadget.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/raw_gadget.h

Purpose: Defines the USB Raw Gadget ioctl ABI for userspace to emulate a USB device directly on a UDC.

Important APIs/types/functions: `usb_raw_init` selects UDC driver/device name and speed. Event types report connect, control, suspend, resume, reset, and disconnect. `usb_raw_event` returns event data, with control events carrying `usb_ctrlrequest`. `usb_raw_ep_io` performs EP0 and endpoint reads/writes with flags such as zero packet. Endpoint info structs expose endpoint capabilities, limits, names, and addresses. Ioctls initialize, run, fetch events, EP0 read/write/stall, enable/disable endpoints, endpoint read/write, configure, set VBUS draw, query endpoint info, and set/clear halt or wedge.

Control flow: Userspace initializes a raw gadget, runs it, fetches events, responds to EP0 setup packets, enables endpoints using descriptors, configures the device, and services endpoint I/O synchronously through ioctls.

State and persistence behavior: Raw gadget state is tied to the open instance and selected UDC. Endpoint handles are valid while enabled and reset/disconnect events can invalidate assumptions.

Dependencies and integration points: Includes `asm/ioctl.h`, `linux/types.h`, and USB chapter 9. Integrates with UDC drivers, dummy_hcd/dummy_udc, fuzzing frameworks, and custom USB device emulators.

Risks: This ABI exposes low-level USB device behavior and is often used for fuzzing. EP0 direction must match the last setup packet. Endpoint descriptor/capability mismatches and reset/disconnect races are common failure points.

Test signals: Use dummy UDC to initialize/run, fetch connect/control/reset events, handle standard enumeration requests, enable bulk/interrupt endpoints, transfer data, query endpoint caps, and test halt/wedge/stall behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/raw_gadget.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/tmc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/tmc.h

Purpose: Defines the USB Test and Measurement Class userspace ioctl ABI, including USBTMC-USB488 operations.

Important APIs/types/functions: Structs include terminal-character configuration, generic control requests, and message-based read/write requests. Ioctls cover indicator pulse, clear, abort bulk in/out, clear halt, vendor/control request, get/set timeout, EOM enable, termchar config, read/write and write-result retrieval, API version, USB488 capabilities, status byte reads, REN/local/lockout/trigger/SRQ controls, message-in attributes, auto-abort, cancel and cleanup I/O. Capability bits describe trigger, simple, REN, go-to-local, local lockout, 488.2, DT1, RL1, SR1, and full SCPI support.

Control flow: Userspace controls lab instruments by configuring timeouts/termchar/EOM, sending USBTMC messages, reading responses/status bytes, and using USB488 control operations for bus-management semantics.

State and persistence behavior: Timeout, EOM, termchar, auto-abort, and pending I/O are runtime per-device/file state. Instrument command state is external device state.

Dependencies and integration points: Integrates with USBTMC kernel driver, USB control/bulk transfers, VISA/SCPI stacks, and lab automation tooling.

Risks: Long-running I/O and abort/clear races must be handled. Timeouts and termchar config affect protocol framing. Capability bits overlap historically and require careful interpretation.

Test signals: Query API/caps, perform SCPI write/read, test timeouts, termchar and EOM handling, abort/clear paths, cancel/cleanup during blocking I/O, and USB488 status/trigger controls with real or emulated instruments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/tmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/video.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usb/video.h

Purpose: Defines USB Video Class constants and descriptor structures for UVC controls, streaming formats, frames, endpoints, color metadata, and payload headers.

Important APIs/types/functions: Constants cover UVC subclasses/protocols, VC/VS/endpoint descriptor subtypes, request codes, terminal/selector/camera/processing/video-stream controls, terminal types, payload flags, and control capabilities. Enums define color primaries, transfer characteristics, and matrix coefficients. Structs model descriptor headers, VC headers, input/output/camera terminals, selector/processing/extension units, control endpoints, input/output streaming headers, color matching, streaming control, uncompressed/MJPEG/frame-based formats and frames, and size macros for variable-length descriptors.

Control flow: Host/gadget code parses descriptors during enumeration, negotiates stream parameters via probe/commit controls, then uses payload header flags (`FID`, `EOF`, `PTS`, `SCR`, etc.) to frame video data over isochronous or bulk endpoints.

State and persistence behavior: Descriptors advertise static capabilities. Runtime state includes selected format/frame interval, camera and processing controls, stream on/off, frame IDs, timestamps, and error flags.

Dependencies and integration points: Includes `linux/types.h`; integrates with UVC kernel driver, V4L2, USB gadget UVC, webcam firmware, and userspace media stacks.

Risks: Variable-length descriptor macros require length validation. Probe/commit values must align with descriptor-supported frames and bandwidth. Payload flags affect frame boundary detection and timestamp sync.

Test signals: Enumerate UVC cameras/gadgets, parse descriptor trees, negotiate multiple formats/frame intervals, stream frames with payload header validation, exercise camera/processing controls, and fuzz malformed descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usb/video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usbdevice_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usbdevice_fs.h

Purpose: Defines the usbfs `/dev/bus/usb` userspace ABI for direct USB device access.

Important APIs/types/functions: Structs describe control/bulk transfers, interface setting, disconnect signals, driver query, connection info, extended connection info, URBs with iso packet descriptors, driver-private ioctls, hub port info, disconnect claim, and stream allocation. Flags define URB behavior, URB types, capabilities, and disconnect-claim modes. Ioctls support control/bulk transfer, reset/clear halt, set interface/configuration, get driver, submit/discard/reap URBs, disconnect signal, claim/release interface or port, connect/disconnect/reset, query capabilities/speed/connection info, allocate/free streams, drop privileges, and suspend control. 32-bit compat ioctl aliases are provided for pointer-sized structs.

Control flow: Userspace opens a usbfs device node, claims interfaces, performs synchronous control/bulk ioctls or asynchronous URB submit/reap cycles, optionally disconnects kernel drivers, allocates streams, and releases/reset devices as needed.

State and persistence behavior: Claimed interfaces, dropped privileges, submitted URBs, stream allocations, suspend forbids, and disconnect claims are runtime state tied to the file/device. Device configuration changes affect hardware until changed again or reset.

Dependencies and integration points: Includes `linux/types.h` and `linux/magic.h`; integrates with USB core, libusb, device firmware tools, scanners, programmers, and test harnesses.

Risks: Direct device access is security-sensitive. Pointer fields and compat ioctls require careful translation. URB lifetime, disconnect races, mmap capability, privilege dropping, and kernel-driver detachment are key hazards.

Test signals: libusb-style claim/transfer tests, sync control/bulk, async interrupt/iso/bulk URBs, disconnect during pending URBs, reset/clear halt, stream allocation, capability queries, drop privileges, suspend forbid/allow/wait, and 32-bit compat coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usbdevice_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usbip.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/usbip.h

Purpose: Defines USB/IP userspace-visible device status and URB transfer flag constants.

Important APIs/types/functions: `enum usbip_device_status` identifies available, used, shared, and error/unknown statuses. URB flags include short-not-ok, isochronous ASAP, DMA mapping modes, zero packet, no interrupt, free buffer, direction mask, setup mapping, combined SG, aligned temporary buffer, and local mapping flags.

Control flow: USB/IP tooling and kernel code use status values to report exported/imported device state and transfer flags to serialize or reconstruct URB behavior across the network.

State and persistence behavior: Status is runtime export/import state. URB flags are per-transfer metadata.

Dependencies and integration points: Integrates with usbip host/vhci drivers, USB core URB semantics, and usbip userspace utilities.

Risks: Direction and DMA/local mapping flags must be translated safely across machines where DMA addresses are not meaningful. Status races occur when devices are attached/detached remotely.

Test signals: Export/import devices with usbip, verify status transitions, transfer bulk/control/iso URBs, disconnect during transfer, and compare flag preservation across host/vhci boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/usbip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/user_events.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/user_events.h

Purpose: Defines the user_events tracing ABI for registering, unregistering, and writing user-defined trace events.

Important APIs/types/functions: System names are `user_events` and `user_events_multi`, with prefix `u:`. `DYN_LOC(offset, size)` encodes dynamic field locations. Registration flags include persistence, multi-format, and other user-event behavior flags. `struct user_reg` carries size, enable bit location, flags, event name/format, write index, and enable address/bit metadata. `struct user_unreg` carries size and disable metadata. Ioctls `DIAG_IOCSREG`, `DIAG_IOCSDEL`, and `DIAG_IOCSUNREG` register, delete, and unregister events through the tracing diagnostics interface.

Control flow: Userspace registers an event format, receives an enable bit/index, checks whether tracing is enabled, then writes event payloads to the user_events data path. Unregister/delete ioctls remove per-process or named event registrations.

State and persistence behavior: Registration creates tracing metadata in kernel tracefs/user_events state. Enable bits are shared with userspace so tracing can be skipped cheaply. Persistent events may outlive the registering process depending on flags and kernel policy.

Dependencies and integration points: Includes `linux/types.h` and `linux/ioctl.h`; integrates with ftrace/tracefs, perf/BPF consumers, dynamic event format parsing, and observability agents.

Risks: User-provided format strings and dynamic locations require strict validation. Enable address handling crosses user/kernel memory boundaries. Event deletion must not race active writers/readers.

Test signals: Register simple and dynamic events, verify enable bit toggling through tracefs, write payloads and read trace output, unregister/delete, test duplicate formats, invalid flags/addresses, and multi-process persistence behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/user_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/userfaultfd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/userfaultfd.h

Purpose: Defines the userfaultfd UAPI for userspace page-fault handling, memory migration, write protection, minor-fault resolution, poisoning, and related virtual-memory events.

Important APIs/types/functions: `USERFAULTFD_IOC_NEW` creates fds via `/dev/userfaultfd`; `UFFD_API` identifies the negotiated API. Feature masks advertise pagefault write-protect flag, fork/remap/remove/unmap events, hugetlbfs/shmem missing and minor faults, SIGBUS mode, thread ID, exact address, WP on hugetlbfs/shmem/unpopulated, poison, async WP, and move. Ioctls include API negotiation, register/unregister, wake, copy, zeropage, move, writeprotect, continue, and poison. `struct uffd_msg` is read from the fd for pagefault/fork/remap/remove/unmap events. Request structs include `uffdio_api`, `uffdio_range`, `uffdio_register`, `uffdio_copy`, `uffdio_zeropage`, `uffdio_writeprotect`, `uffdio_continue`, `uffdio_poison`, and `uffdio_move`. `UFFD_USER_MODE_ONLY` restricts faults to user-mode.

Control flow: Userspace creates a userfaultfd, negotiates features with `UFFDIO_API`, registers address ranges and modes, polls/reads events, resolves missing faults with copy/zeropage, resolves minor faults with continue, manages write-protection, wakes waiters, poisons ranges, or moves page contents. Event flags distinguish write, write-protect, and minor faults.

State and persistence behavior: Registered ranges and feature negotiation live on the userfaultfd and target mm lifetime. Page contents, write-protection state, poison markers, and moved pages persist in the process address space until changed.

Dependencies and integration points: Includes `linux/types.h`; integrates with `userfaultfd(2)`, `/dev/userfaultfd`, memory management, shmem, hugetlbfs, live migration, post-copy VM migration, garbage collectors, checkpoint/restore, and sandboxing.

Risks: Deadlocks are possible if the fault handler faults on registered memory or fails to wake waiters. Feature negotiation must be honored before using ioctls. DONTWAKE, WP async, move, poison, and exact-address semantics are subtle. Return fields at the end of structs are kernel-written and intentionally not read by `copy_from_user`.

Test signals: Run kernel userfaultfd selftests for missing, WP, minor, shmem, hugetlbfs, fork/remap/remove/unmap, SIGBUS, thread ID, exact address, async WP, poison, move, unregister/wake, and `/dev/userfaultfd` creation with `UFFD_USER_MODE_ONLY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/userfaultfd.h -->
