# Group Research: group_1653_qemu_sources_virtualization_qemu_hw_virtio_virtio_c_sources_virtual_a74aa192f493

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/virtualization/qemu`, which is included in subset A. Each listed file was read completely, including the empty `tools/meson.build`.

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio.c

## Purpose
Core QEMU virtio implementation. This file implements common virtio device and virtqueue behavior shared by virtio transports and devices, including split rings, packed rings, queue notification, DMA mapping, reset/lifecycle handling, migration state, ioeventfd integration, and QMP inspection helpers.

## Main Data Structures
- `VRingDesc`, `VRingAvail`, `VRingUsedElem`, `VRingUsed`: split virtqueue layout.
- `VRingPackedDesc`, `VRingPackedDescEvent`: packed virtqueue layout and event suppression structures.
- `VRingMemoryRegionCaches`: cached guest memory mappings for descriptor, available, and used rings, freed through RCU.
- `VRing`: queue size, alignment, guest physical ring addresses, and region caches.
- `VirtQueue`: per-queue runtime state: vring, used element staging, avail/used indexes and wrap counters, notification state, vector, event notifiers, queue handler, and owning `VirtIODevice`.

## Major Responsibilities
- Maintains `virtio_device_names[]` and maps virtio IDs to stable device names.
- Initializes and refreshes ring memory caches with `virtio_init_region_cache()`, invalidating old mappings through RCU.
- Computes split-ring addresses from descriptor base and alignment in `virtio_queue_update_rings()`.
- Reads/writes split and packed descriptors with endian-aware helpers.
- Implements queue notification enable/disable for split and packed queues, including event index handling and memory barriers.
- Detects queue emptiness and polls for new descriptors.
- Maps guest DMA descriptors into host iovecs, with descriptor validation and cleanup paths.
- Pops, fills, flushes, pushes, rewinds, detaches, and drops virtqueue elements for split, packed, and in-order modes.
- Implements interrupt signaling through ISR bits, guest notifiers, irqfd/deferred notifier paths, and config-change notifications.
- Handles virtio status negotiation, feature validation, reset, queue setup, queue vector lists, and lifecycle hooks.
- Saves and loads legacy and modern virtio migration state, including optional subsections for endian, 64/128-bit features, ringsize, broken/started/disabled flags, packed queues, and transport extra state.
- Registers QOM type `TYPE_VIRTIO_DEVICE` and default class methods.
- Provides QMP experimental inspection APIs for queue status and split-ring queue elements.
- Supplies guarded bottom-half helpers tied to the transport reentrancy guard.

## Key Control Flow
- Device setup: `virtio_init()` allocates queues/config, initializes vectors and default state, and registers VM state change handling.
- Queue creation: `virtio_add_queue()` finds a free queue slot, sets default size/alignment, stores output handler, and allocates `used_elems`.
- Guest queue setup: transport calls address/size setters, which update ring addresses and region caches.
- Descriptor processing: `virtqueue_pop()` dispatches to split or packed pop logic, validates descriptor chains, maps DMA buffers, and advances avail state.
- Completion: device calls `virtqueue_fill()` plus `virtqueue_flush()` or `virtqueue_push()`; the file writes used entries/descriptors, updates indexes, unmaps DMA, and decrements `inuse`.
- Notification: `virtio_notify()` checks event suppression rules and signals the transport vector or notifier.
- Migration: `virtio_save()` and `virtio_load()` preserve queue state, feature state, config, and device-specific data.

## Error Handling and Safety
- Guest mistakes call `virtio_error()`, which marks virtio 1.x devices as needing reset, notifies config, and marks the device broken.
- Descriptor loops, invalid indirect tables, zero-sized buffers, out-of-range heads, bad queue indexes, and failed mappings are detected.
- Memory ordering is explicit around descriptor visibility, event flags, and avail/used indexes.
- Cached guest memory is invalidated after writes and replaced under RCU to avoid use-after-free across readers.
- Migration load validates queue counts, queue indexes, feature compatibility, ring consistency, and in-use arithmetic.

## Filesystem/Storage Relevance
This is the common virtio substrate used by storage-facing devices such as virtio-blk, virtio-scsi, virtio-fs, virtio-pmem, and related vhost/virtio devices. Correct descriptor mapping, completion ordering, notification suppression, and migration restoration are foundational for virtual block and filesystem I/O correctness.

## Notable Details
- Supports both legacy split rings and modern packed rings.
- Supports `VIRTIO_F_IN_ORDER`, `VIRTIO_RING_F_EVENT_IDX`, `VIRTIO_F_NOTIFICATION_DATA` compatibility checks, IOMMU-platform feature validation, and variable legacy vring alignment.
- For packed queues, `last_avail_idx` and `used_idx` include wrap-counter state in packed migration/helper encodings.
- QMP element inspection explicitly rejects packed rings.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/ebpf/rss.bpf.c -->
# File Research: sources/virtualization/qemu/tools/ebpf/rss.bpf.c

## Purpose
eBPF socket filter program for virtio-net RSS steering. It parses packet headers, computes a Toeplitz RSS hash using QEMU-provided BPF maps, and returns a selected queue.

## Main Data Structures
- `rss_config_t`: runtime RSS configuration: redirect flag, hash population flag, hash types, indirection length, and default queue.
- `toeplitz_key_data_t`: preprocessed Toeplitz key state.
- `packet_hash_info_t`: parsed packet metadata for IPv4/IPv6, TCP/UDP, ports, fragmentation, and IPv6 extension source/destination addresses.
- BPF maps:
  - `tap_rss_map_configurations`
  - `tap_rss_map_toeplitz_key`
  - `tap_rss_map_indirection_table`

## Behavior
- `parse_eth_type()` handles Ethernet type parsing with single/double VLAN tags.
- `parse_packet()` extracts IPv4 or IPv6 addressing, detects fragmentation, and extracts TCP/UDP ports when safe.
- `parse_ipv6_ext()` walks bounded IPv6 extension headers, including routing header type 2 and home address destination option handling.
- `calculate_rss_hash()` builds an RSS input buffer based on negotiated virtio-net hash type bits and computes the Toeplitz hash.
- `tun_rss_steering_prog()` looks up config/key maps, computes hash if redirect is enabled, indexes the indirection table, and returns either selected queue or default queue.

## Safety/Verifier Constraints
- IPv6 extension and option parsing loops are bounded by `IP6_EXTENSIONS_COUNT` and `IP6_OPTIONS_COUNT`.
- Packet reads use `bpf_skb_load_bytes_relative()`.
- Hash input buffer is fixed-size and zero-initialized.
- Missing BPF map entries fall back to queue `0` or configured default queue.

## Filesystem/Storage Relevance
Indirect. This is virtualization networking support, not filesystem code, but it belongs to the QEMU virtualization source tree in subset A. It supports virtio-net multiqueue packet steering.

## Notable Detail
`net_toeplitz_add()` accepts a `len` argument but loops over `HASH_CALCULATION_BUFFER_SIZE`; the caller zero-fills the full buffer, so unused bytes contribute zero input.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/ebpf/rss.bpf.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/i386/qemu-vmsr-helper.c -->
# File Research: sources/virtualization/qemu/tools/i386/qemu-vmsr-helper.c

## Purpose
Privileged helper process that lets QEMU read a narrow allowlist of Intel RAPL MSRs through a Unix socket. It is intended to expose virtual RAPL MSR values while isolating raw MSR access in a helper with `CAP_SYS_RAWIO`.

## Main Behavior
- Computes default socket and pidfile paths under QEMU local state.
- Verifies the host CPU vendor is Intel via CPUID.
- Verifies Intel RAPL is enabled through `/sys/class/powercap/intel-rapl/enabled`.
- Listens on a Unix socket or systemd socket activation fd.
- Accepts clients, obtains peer PID, and serves requests in coroutines.
- Each request is three `uint32_t` values: MSR register, CPU ID, and TID.
- Only allows RAPL MSRs listed in `rapl-msr-index.h`.
- Reads `/dev/cpu/<cpu>/msr` with `pread()`.
- Verifies requested TID belongs to the peer process by checking `/proc/<pid>/task/<tid>`.
- Replies with a `uint64_t` MSR value or zero on failed/unauthorized reads.

## CLI and Runtime
Options include help/version, daemon mode, pidfile, socket path, trace settings, verbose errors, and optional user/group flags when libcap-ng is enabled. The main loop handles SIGTERM/SIGINT/SIGHUP and closes the server socket on termination.

## Security Model
- Restricts MSR reads to four package/RAPL registers.
- Checks peer task ownership for the supplied TID.
- Can integrate with libcap-ng to retain only `CAP_SYS_RAWIO`.
- Rejects relative socket paths.
- Supports socket activation but only one inherited fd.

## Filesystem/Storage Relevance
Indirect. This is virtualization host-helper infrastructure, not filesystem logic. It does interact with Linux device files and `/proc`/`/sys` paths to safely proxy privileged CPU telemetry into QEMU.

## Notable Limitations
- RAPL and CPU checks happen before option parsing.
- `uid`/`gid` parsed under libcap-ng are stored but this file’s `drop_privileges()` only clears/adds capabilities and does not itself switch user/group.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/i386/qemu-vmsr-helper.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/i386/rapl-msr-index.h -->
# File Research: sources/virtualization/qemu/tools/i386/rapl-msr-index.h

## Purpose
Small header defining the RAPL MSR allowlist used by `qemu-vmsr-helper.c`.

## Contents
Defines:
- `MSR_RAPL_POWER_UNIT` as `0x00000606`
- `MSR_PKG_POWER_LIMIT` as `0x00000610`
- `MSR_PKG_ENERGY_STATUS` as `0x00000611`
- `MSR_PKG_POWER_INFO` as `0x00000614`

## Integration
`qemu-vmsr-helper.c` includes this header and accepts only these register IDs in `is_msr_allowed()`.

## Filesystem/Storage Relevance
None directly. It supports the virtualization helper’s controlled access to host MSR device files.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/i386/rapl-msr-index.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/meson.build -->
# File Research: sources/virtualization/qemu/tools/meson.build

## Purpose
Empty Meson build file.

## Contents
The file has zero lines and no declarations.

## Integration
No build targets, dependencies, or subdir rules are defined here. Tool-specific build logic for this group appears in subdirectories such as `tools/qemu-vnc/meson.build`.

## Filesystem/Storage Relevance
None directly.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/audio.c -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/audio.c

## Purpose
Audio support for standalone `qemu-vnc`, connecting to QEMU’s D-Bus display audio interface and exposing received audio to QEMU’s VNC audio capture path.

## Main Structures
- `CaptureVoiceOut`: registered capture consumer with audio settings and callbacks.
- `AudioOut`: currently tracked D-Bus output stream ID and audio settings.

## Behavior
- Handles D-Bus `AudioOutListener` methods: `Init`, `Fini`, `SetEnabled`, `SetVolume`, and `Write`.
- Converts D-Bus audio format metadata into QEMU `audsettings`.
- Tracks one active output stream in `audio_out`.
- On enable/disable, notifies all registered capture callbacks.
- On write, forwards raw bytes only to captures with matching format/settings.
- Provides a dummy `AudioBackend` so VNC audio capture registration has a non-NULL backend.
- Sets up a peer-to-peer D-Bus connection via socketpair and registers an audio listener with QEMU.

## Filesystem/Storage Relevance
None directly. It is part of virtualization UI/audio tooling around QEMU.

## Notable Limitations
No resampling, mixing, or format conversion is implemented; mismatched capture settings are ignored.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/audio.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/chardev.c -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/chardev.c

## Purpose
Discovers QEMU D-Bus chardev objects and exposes selected character devices as VNC text consoles.

## Behavior
- Defaults to chardev names:
  - `org.qemu.console.serial.0`
  - `org.qemu.monitor.hmp.0`
- Allows caller-provided chardev name list.
- For matching `org.qemu.Display1.Chardev` objects, creates a Unix socketpair.
- Passes one fd to QEMU through `Register`.
- Creates a local `QemuTextConsole` for the other fd after registration succeeds.
- Reads optional `org.qemu.Display1.Chardev.VCEncoding` to set text encoding.

## Error Handling
- Failed registration closes the local fd.
- Failed text console creation also closes the local fd.
- Unknown or unmatched chardevs are ignored.

## Filesystem/Storage Relevance
Indirect. This exposes monitor/serial channels over VNC, which may be used for VM management but is not filesystem-specific.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/chardev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/clipboard.c -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/clipboard.c

## Purpose
Bridges QEMU’s internal clipboard peer API with QEMU’s D-Bus display clipboard interface for standalone `qemu-vnc`.

## Behavior
- Supports UTF-8 text clipboard only: `text/plain;charset=utf-8`.
- Maintains D-Bus clipboard proxy/skeleton and one pending request per selection.
- On local clipboard update, advertises/grabs text MIME availability over D-Bus.
- On remote grab, creates a `QemuClipboardInfo` and updates QEMU clipboard state if serial is valid.
- On remote release, releases the corresponding clipboard peer selection.
- On request, returns existing clipboard data or triggers an async local request with a five-second timeout.
- On unregister, cancels pending requests.
- Registers as a `QemuClipboardPeer` named `dbus`.

## Error Handling
Rejects invalid selections, concurrent pending requests, empty clipboard, and unsupported MIME requests with D-Bus errors.

## Filesystem/Storage Relevance
None directly. It is desktop/console integration for the virtualization UI path.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/clipboard.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/console.c -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/console.c

## Purpose
Implements a minimal standalone `QemuTextConsole` for `qemu-vnc`, backed directly by a raw fd and QEMU’s VT100 emulator.

## Main Structure
`QemuTextConsole` embeds `QemuConsole`, owns a `QemuVT100`, chardev fd, GLib IO watch id, and name.

## Behavior
- Defines QOM type `QEMU_TEXT_CONSOLE`.
- Creates an 80x24 text surface using configured text cell dimensions.
- Initializes VT100 rendering over a pixman display surface.
- Reads from the fd through a GLib IO watch and feeds bytes to `vt100_input()`.
- Flushes VT100 output FIFO back to the fd.
- Updates VNC display regions on VT100 image changes.
- Handles keysyms through `vt100_keysym()`.
- Resizes text console according to VT100 dimensions.

## Filesystem/Storage Relevance
None directly. It supports serial/HMP console exposure through VNC.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/console.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/dbus.c -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/dbus.c

## Purpose
Implements the standalone `qemu-vnc` management D-Bus API under `org.qemu.Vnc1`, and forwards QEMU VNC client events into D-Bus objects/signals.

## Main Structures
- `VncDbusClient`: one D-Bus object per connected VNC client, with host/service/path/auth metadata.
- Global server skeleton and object manager for `/org/qemu/Vnc1`.

## Server API Behavior
- Exports `/org/qemu/Vnc1/Server`.
- Sets server properties: name, auth, vencrypt subauth, clients, and listeners.
- Implements methods:
  - `SetPassword`
  - `ExpirePassword`
  - `ReloadCertificates`
  - `AddClient`
- Builds listener property data from `qmp_query_vnc_servers()`.

## Client Tracking
- On connect, creates `/org/qemu/Vnc1/Client_<id>`, sets host/service/family/websocket, updates server `Clients`, and emits `ClientConnected`.
- On initialized, fills X.509 DN and SASL username where available and emits `ClientInitialized`.
- On disconnect, emits `ClientDisconnected`, unexports the object, removes it from the list, and updates `Clients`.

## Event Forwarding
Overrides local `qapi_event_emit()` for VNC connected/initialized/disconnected events and maps the QDict event payload into D-Bus client updates.

## VNC Actions
`vnc_action_shutdown()` and `vnc_action_reset()` locate the D-Bus client for a `VncState` and emit corresponding client signals.

## Filesystem/Storage Relevance
None directly. It is management/control-plane infrastructure for the standalone virtualization UI tool.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/dbus.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/display.c -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/display.c

## Purpose
D-Bus display listener for standalone `qemu-vnc`, handling graphic console scanout, incremental updates, shared-memory scanout, cursor updates, UI info, and input proxy discovery.

## Main Structure
`ConsoleData` stores D-Bus console/keyboard/mouse proxies, the local graphic console, listener connection, and whether the current surface is read-only.

## Behavior
- Creates proxies for `org.qemu.Display1.Console`, `Keyboard`, and `Mouse`.
- Creates a local QEMU graphic console.
- Registers a D-Bus display listener through a peer-to-peer socket connection.
- Implements listener methods:
  - `Scanout`: creates writable pixman surface from D-Bus byte array.
  - `Update`: composites update pixels into active writable surface.
  - `ScanoutMap`: mmaps passed fd read-only with `MAP_PRIVATE` and creates surface.
  - `UpdateMap`: marks rectangle dirty for mapped scanout.
  - `CursorDefine`: creates and installs QEMU cursor.
- Sends UI size information back through `SetUIInfo`.
- Calls `input_setup()` with keyboard and mouse proxies.

## Safety/Ownership
- Byte-array scanout keeps the `GVariant` alive until pixman image destroy.
- Mapped scanout unmaps memory through pixman destroy callback.
- Plain updates are rejected when the active surface is read-only.

## Filesystem/Storage Relevance
None directly. It is display plumbing for virtualization UI.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/display.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/input.c -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/input.c

## Purpose
Forwards QEMU/VNC input events to QEMU’s D-Bus display keyboard and mouse interfaces.

## Behavior
- Maintains LED event handlers and mouse mode notifiers expected by QEMU UI code.
- Converts Linux keycodes to QEMU key numbers and sends D-Bus `Press`/`Release`.
- Queues absolute and relative mouse motion until `qemu_input_event_sync()`.
- Sends absolute position or relative motion D-Bus calls on sync.
- Reports absolute mouse capability from D-Bus mouse property.
- Sends mouse button press/release calls for changed button bits.
- Reacts to keyboard modifier and mouse absolute-mode property changes.

## Filesystem/Storage Relevance
None directly. It is virtualization UI input integration.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/input.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/meson.build -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/meson.build

## Purpose
Meson build definition for the standalone `qemu-vnc` executable and generated D-Bus bindings.

## Behavior
- Applies VNC source set `vnc_ss`.
- Generates `qemu-vnc1.h` and `qemu-vnc1.c` from `qemu-vnc1.xml` using `gdbus-codegen`.
- Builds executable `qemu-vnc` from:
  - main/source bridge files
  - VNC source set output
  - generated D-Bus display and VNC1 bindings
- Links dependencies: VNC dependencies, `io`, `crypto`, `qemuutil`, `gio`, and `ui`.
- Creates a development symlink from build subdir to `../../qemu-bundle` so relocated path lookup works.

## Filesystem/Storage Relevance
None directly. It controls build integration for the standalone virtualization UI tool.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/qemu-vnc.c -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/qemu-vnc.c

## Purpose
Main program for standalone `qemu-vnc`, a VNC server that connects to a running QEMU instance through the `org.qemu.Display1` D-Bus display interface.

## Main State
`QemuVncState` tracks D-Bus connection/name, selected chardev names, shutdown reason, VT enabling, owner tracking, and termination flags.

## Startup Flow
- Initializes QEMU exec/data dirs, trace, QOM, options, and main loop.
- Parses GLib options for D-Bus address or p2p fd, bus name, wait mode, VNC listen address, websocket, sharing, TLS, SASL, objects, chardev exposure, keyboard layout, password, lossy mode, and adaptive encoding.
- Creates optional user-creatable objects.
- Creates TLS credentials and optional systemd credential-backed VNC password secret.
- Converts CLI settings into a QEMU `vnc` option with id `default`.
- Connects to session bus, custom bus address, or p2p fd.
- Watches the QEMU bus name or starts setup immediately for p2p/direct connection.

## Display Setup
- Optionally reads VM name from `/org/qemu/Display1/VM`.
- Creates a D-Bus object manager for display objects.
- Discovers console object paths and sorts them for deterministic console numbering.
- Calls `console_setup()` for each console.
- Creates the VNC display after consoles exist.
- Initializes VNC management D-Bus API, clipboard, audio, and optional chardev text consoles.

## Shutdown
Terminates when the D-Bus owner vanishes, connection closes, or setup fails; emits a VNC D-Bus `Leaving` signal, cleans up VNC D-Bus state and VNC display state, and exits.

## Filesystem/Storage Relevance
None directly. This is standalone virtualization UI entrypoint code.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/qemu-vnc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/qemu-vnc.h -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/qemu-vnc.h

## Purpose
Shared internal header for the standalone `qemu-vnc` tool.

## Contents
- Includes QEMU/GIO/D-Bus/display headers needed across qemu-vnc modules.
- Defines text console geometry constants:
  - `TEXT_COLS 80`
  - `TEXT_ROWS 24`
  - `TEXT_FONT_WIDTH 8`
  - `TEXT_FONT_HEIGHT 16`
- Declares cross-module functions for:
  - text console creation
  - input setup
  - console setup and proxy lookup
  - audio/clipboard/chardev setup
  - peer-to-peer D-Bus thread creation
  - VNC management D-Bus setup, cleanup, leaving signal, and client events

## Filesystem/Storage Relevance
None directly. It is module glue for virtualization UI code.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/qemu-vnc.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/qemu-vnc1.xml -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/qemu-vnc1.xml

## Purpose
D-Bus introspection XML for generated `org.qemu.Vnc1` bindings used by standalone `qemu-vnc`.

## Interfaces
### `org.qemu.Vnc1.Server`
Implemented at `/org/qemu/Vnc1/Server`.

Properties:
- `Name`
- `Auth`
- `VencryptSubAuth`
- `Clients`
- `Listeners`

Methods:
- `SetPassword`
- `ExpirePassword`
- `ReloadCertificates`
- `AddClient`

Signals:
- `ClientConnected`
- `ClientInitialized`
- `ClientDisconnected`
- `Leaving`

### `org.qemu.Vnc1.Client`
Implemented at `/org/qemu/Vnc1/Client_$id`.

Properties:
- `Host`
- `Service`
- `Family`
- `WebSocket`
- `X509Dname`
- `SaslUsername`

Signals:
- `ShutdownRequest`
- `ResetRequest`

## Integration
`tools/qemu-vnc/meson.build` runs `gdbus-codegen` on this XML to generate C bindings.

## Filesystem/Storage Relevance
None directly. It defines the management API for the virtualization VNC service.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/qemu-vnc1.xml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/stubs.c -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/stubs.c

## Purpose
Provides link-time/runtime stubs needed by the standalone `qemu-vnc` binary so it can reuse QEMU UI/VNC code without pulling in full system-emulator subsystems.

## Stubbed Symbols
- `runstate_is_running()` always returns true.
- `phase_check()` always returns true.
- `qdev_find_recursive()` returns NULL.
- Monitor stubs return NULL/false/error, avoiding the generic monitor stub object that would conflict with `qapi_event_emit()`.
- Defines empty `VMStateInfo` objects for migration-related symbols referenced by linked VNC code.

## Filesystem/Storage Relevance
None directly. It supports standalone linking of virtualization UI code.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/stubs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/trace.h -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/trace.h

## Purpose
Small local trace include shim for `qemu-vnc`.

## Contents
Includes generated trace declarations from `trace/trace-tools_qemu_vnc.h`.

## Integration
Used by qemu-vnc source files for tracepoints without duplicating generated trace include paths.

## Filesystem/Storage Relevance
None directly.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/utils.c -->
# File Research: sources/virtualization/qemu/tools/qemu-vnc/utils.c

## Purpose
Utility code for establishing peer-to-peer D-Bus connections over already-created file descriptors.

## Behavior
- `dbus_p2p_from_fd()` wraps an fd in `GSocket`, creates a `GSocketConnection`, and creates a `GDBusConnection` with client authentication and delayed message processing.
- Reports errors for socket wrapping, socket connection creation, and D-Bus connection creation.
- `p2p_server_setup_thread()` is the GLib thread entry point.
- `p2p_dbus_thread_new()` starts a thread named `p2p-server-setup` and passes the fd through.

## Integration
Used by display and audio listener registration code to accept the local end of socketpairs while QEMU connects over the other end.

## Filesystem/Storage Relevance
None directly. It is IPC helper code for virtualization UI.
<!-- END FILE RESEARCH: sources/virtualization/qemu/tools/qemu-vnc/utils.c -->