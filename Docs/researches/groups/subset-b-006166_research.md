# subset-b-006166 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/mgmt_config.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/mgmt_config.c

Purpose: implements the Bluetooth management commands that read and set default controller configuration TLVs. It bridges the userspace mgmt API opcodes `MGMT_OP_READ_DEF_SYSTEM_CONFIG`, `MGMT_OP_SET_DEF_SYSTEM_CONFIG`, `MGMT_OP_READ_DEF_RUNTIME_CONFIG`, and runtime set handling to fields stored in `struct hci_dev`.

Important APIs/types/functions: local TLV construction macros `HDEV_PARAM_U32`, `HDEV_PARAM_U16`, `HDEV_PARAM_U8`, `TLV_SET_U*`, and `TLV_SET_U16_JIFFIES_TO_MSECS` define packed response fragments using `struct mgmt_tlv_hdr`. `read_def_system_config` builds one packed response containing page/inquiry scan defaults, BR link supervision/page timeout, sniff intervals, LE advertising/scan/connect intervals, adv monitor scan durations, interleaved-scan enablement, and idle timeout. `set_def_system_config` validates and applies incoming `struct mgmt_tlv` records. `read_def_runtime_config` currently returns an empty success response, while `set_def_runtime_config` rejects parameters.

Control flow: read-system-config creates a stack packed response initialized from `hdev` fields and completes the mgmt command through `mgmt_cmd_complete`. Set-system-config first rejects payloads smaller than one TLV header, then walks the user buffer once to ensure every TLV is fully present and every known type has the expected fixed value length. It accepts unknown parameter types by warning and skipping type-specific validation. A second pass applies recognized types to `hdev` fields, converting little-endian integers and converting autoconnect timeout between milliseconds and jiffies. Successful update returns command-complete with no response payload.

State and persistence behavior: the file mutates per-controller default configuration held in `struct hci_dev`; it does not persist values to disk or controller NVM by itself. Values remain kernel runtime state for the controller object and are consumed later by HCI setup, scanning, connection, advertising, and monitoring paths. The TLV wire format is little-endian and packed, and jiffies/millisecond conversion is part of the ABI boundary for the LE autoconnect timeout field.

Dependencies and integration points: depends on `net/bluetooth/mgmt.h` TLV and opcode definitions, `hci_core.h` for `struct hci_dev` defaults, `mgmt_util.c` for command completion/status helpers, and the broader mgmt command dispatcher. It integrates with BlueZ/userspace default-system-configuration APIs and controller setup policies in HCI core.

Risks: set validation must not overrun malformed TLV buffers; the two-pass approach reduces partial-update risk but still allows unsupported TLVs to be silently ignored after warning. Any mismatch between the read response type list and the set switch cases creates confusing userspace behavior. The numeric case labels use zero-padded hexadecimal constants, which are equivalent in C but easy to mistype. There is no range validation for intervals/timeouts beyond width checks, so nonsensical but correctly sized values can enter `hdev`. Runtime config set currently reports `MGMT_OP_SET_DEF_SYSTEM_CONFIG` in its status path, which is notable if userspace expects the runtime opcode.

Test signals: mgmt socket tests should cover reading the full TLV list, setting each known TLV type, rejecting truncated TLVs, rejecting wrong fixed lengths, skipping unknown types without corrupting following TLVs, and preserving no-partial-update behavior when validation fails. Controller behavior tests should verify changed defaults affect subsequent scan/advertising/connect setup, and endian/jiffies conversion should be checked for the autoconnect timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/mgmt_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/mgmt_config.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/mgmt_config.h

Purpose: declares the default system and runtime configuration mgmt command handlers implemented by `mgmt_config.c`.

Important APIs/types/functions: exposes `read_def_system_config`, `set_def_system_config`, `read_def_runtime_config`, and `set_def_runtime_config`, all with the standard mgmt handler signature using `struct sock *`, `struct hci_dev *`, request data, and request length.

Control flow: this header has no executable flow. The mgmt dispatcher includes it so opcode handling tables can call the configuration handlers.

State and persistence behavior: owns no state. The declared functions operate on `struct hci_dev` runtime configuration and reply over the mgmt socket.

Dependencies and integration points: relies on including contexts to provide declarations for `struct sock`, `struct hci_dev`, and integer types. It is an internal Bluetooth mgmt header, not a stable userspace ABI.

Risks: prototype drift from `mgmt_config.c` or mgmt dispatcher expectations would break builds. Because the header carries no include guard in this snapshot, repeated inclusion would rely on C allowing duplicate compatible function declarations.

Test signals: build coverage of `net/bluetooth` is the primary signal; command dispatch tests indirectly verify each prototype is wired to the correct opcode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/mgmt_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/mgmt_util.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/mgmt_util.c

Purpose: provides shared helpers for Bluetooth management sockets: mgmt skb allocation, event delivery, command status/completion replies, pending command tracking, and mesh transmit tracking.

Important APIs/types/functions: `mgmt_alloc_skb`, `mgmt_send_event_skb`, and `mgmt_send_event` build and broadcast mgmt events. `mgmt_cmd_status` and `mgmt_cmd_complete` send synchronous command replies to one management socket and mirror them to the HCI monitor channel. Pending command helpers include `mgmt_pending_find`, `mgmt_pending_foreach`, `mgmt_pending_new`, `mgmt_pending_add`, `mgmt_pending_free`, `mgmt_pending_remove`, `mgmt_pending_listed`, and `mgmt_pending_valid`. Mesh helpers include `mgmt_mesh_foreach`, `mgmt_mesh_next`, `mgmt_mesh_find`, `mgmt_mesh_add`, and `mgmt_mesh_remove`.

Control flow: event helpers allocate an skb with mgmt payload headroom, attach `hdev` and opcode in `bt_cb`, push a `struct mgmt_hdr`, optionally send the payload-only view to the monitor channel, then call `hci_send_to_channel`. Command reply helpers allocate a full mgmt header plus command status/complete event, queue it directly to the originating socket, create a monitor control event with the socket cookie, and free whichever skb is no longer owned. Pending commands are allocated with a held socket reference and copied parameters, then inserted into `hdev->mgmt_pending` under `hdev->mgmt_pending_lock`; removal validates list membership and releases the socket reference. Mesh transmit records are simple list entries under `hdev->mesh_pending` with wrapping nonzero handles.

State and persistence behavior: all state is transient kernel runtime state. Pending commands persist until the command completes, is canceled, or is explicitly removed. Each pending command owns a copied parameter buffer, optional response skb/user data, callback pointer, and socket reference. Mesh transmit state stores copied mesh send parameters, the mgmt socket, controller index, instance, and handle until transmission completion/removal.

Dependencies and integration points: integrates with `hci_sock` channels, monitor events (`HCI_CHANNEL_CONTROL`, `HCI_CHANNEL_MONITOR`, `HCI_MON_CTRL_EVENT`), `struct hci_dev` pending and mesh lists, mgmt ABI records from `mgmt.h`, socket receive queues, sk_buff timestamping, and Bluetooth core socket cookies. It is used broadly by `mgmt.c`, config handlers, mesh mgmt paths, and controller event code.

Risks: lifetime is the main risk: pending commands hold sockets, may be removed while callbacks run, and list membership is protected only by `mgmt_pending_lock`. `mgmt_pending_valid` both checks and unlinks, so callers must free or complete exactly once. Event helpers mutate skb headroom and always free after broadcast, so callers must not reuse skb after `mgmt_send_event_skb`. Mesh helpers do not take an internal lock in this file, so callers must honor the surrounding `hdev` locking convention. Monitor mirroring must preserve timestamps and socket cookies for accurate tracing.

Test signals: mgmt tests should verify command-complete/status replies reach the requesting socket and HCI monitor, broadcast events include the correct controller index including `MGMT_INDEX_NONE`, pending command add/find/remove handles duplicate opcodes and cancellation, socket references are balanced under disconnects, and mesh send handles wrap without becoming zero. KASAN/refcount/lockdep runs are valuable around cancellation and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/mgmt_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/mgmt_util.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/mgmt_util.h

Purpose: defines internal management helper data structures and function prototypes shared by Bluetooth mgmt implementation files.

Important APIs/types/functions: `struct mgmt_pending_cmd` represents a pending asynchronous mgmt command with opcode, controller, copied parameters, socket, optional skb/user data, and completion callback. `struct mgmt_mesh_tx` represents a queued mesh transmission with socket, controller index, handle, instance, and a bounded command parameter buffer. The header declares all event, command reply, pending-command, and mesh-list helpers implemented in `mgmt_util.c`.

Control flow: no executable flow exists here. Callers allocate pending commands through `mgmt_pending_new`/`add`, later search, iterate, validate, remove, and free them through the declared helpers. Mesh callers use add/find/next/foreach/remove to sequence pending mesh sends.

State and persistence behavior: the structs describe transient in-memory state owned by `struct hci_dev` lists. Socket references are held for pending commands and mesh sends until removal. Mesh command storage is sized for `struct mgmt_cp_mesh_send` plus a 31-byte tail.

Dependencies and integration points: depends on list heads, sockets, sk_buffs, HCI devices, and mgmt mesh command definitions from the Bluetooth core include set. It is consumed by mgmt command handlers and HCI event completion paths.

Risks: struct layout is internal but ownership semantics are subtle; callers must respect list locking and avoid freeing pending commands still visible on `hdev->mgmt_pending`. The mesh parameter buffer is fixed-size, so callers must validate lengths before copying into it. Callback signatures imply completion can run with command state still attached unless caller removes carefully.

Test signals: build coverage plus mgmt async command tests, cancellation tests, mesh send queue tests, and lockdep around `mgmt_pending_lock` should exercise this header’s contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/mgmt_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/msft.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/msft.c

Purpose: implements support for Microsoft vendor-specific Bluetooth HCI extensions, especially LE advertisement monitor offload, address-filter-assisted monitor tracking, filter enablement, supported-feature discovery, and suspend/resume re-registration.

Important APIs/types/functions: vendor subcommands include `MSFT_OP_READ_SUPPORTED_FEATURES`, `MSFT_OP_LE_MONITOR_ADVERTISEMENT`, `MSFT_OP_LE_CANCEL_MONITOR_ADVERTISEMENT`, and `MSFT_OP_LE_SET_ADVERTISEMENT_FILTER_ENABLE`. Key private types are `struct msft_data`, `struct msft_monitor_advertisement_handle_data`, `struct msft_monitor_addr_filter_data`, and the packed command/response/event records. Public functions include `msft_register`, `msft_release`, `msft_do_open`, `msft_do_close`, `msft_vendor_evt`, `msft_get_features`, `msft_monitor_supported`, `msft_add_monitor_pattern`, `msft_remove_monitor`, `msft_set_filter_enable`, `msft_suspend_sync`, `msft_resume_sync`, and `msft_curve_validity`.

Control flow: registration allocates `hdev->msft_data` and initializes handle/address-filter lists. Open reads supported features using the controller-specific vendor opcode, stores feature bits and optional event prefix, sets curve-validity state, enables advertisement filtering when supported, and re-registers existing adv monitors. Adding a monitor validates RSSI constraints, serializes monitor patterns into a vendor command, sends it synchronously, maps the mgmt monitor handle to the returned MSFT handle, and marks the monitor offloaded. Removing a monitor sends cancel, drops handle mapping, optionally frees the mgmt monitor, clears tracked devices, and removes any dependent address filters. Suspend removes all offloaded monitors while preserving mgmt monitors for resume; resume clears tracked devices and re-adds monitors.

Control flow continued: vendor events are filtered by optional prefix, then dispatched by event code under `hdev` lock. `MSFT_EV_LE_MONITOR_DEVICE` maps controller handles back to mgmt monitor handles. Without the address-filter quirk, pattern monitor events are reported directly as found/lost devices. With `HCI_QUIRK_USE_MSFT_EXT_ADDRESS_FILTER`, pattern hits create per-device address filters asynchronously via `hci_cmd_sync_queue`, and only address-filter events are reported to mgmt; lost events cancel the address filter and remove the monitored device. Filter enable commands treat controller status `0x0c` as success because some devices may already be in the requested state.

State and persistence behavior: all MSFT state is per-controller runtime memory. `features`, `evt_prefix`, handle maps, address filters, suspend/resume flags, and `filter_enabled` live in `struct msft_data`. Offloaded monitor state is mirrored in `struct adv_monitor` entries in the HCI device IDR. Tracked devices live in `hdev->monitored_devices` and drive mgmt found/lost notifications. Controllers silently drop monitors on power-off, so close clears local mappings and open/resume rebuilds offload state.

Dependencies and integration points: depends on HCI synchronous command APIs, `hci_cmd_sync_queue`, HCI device locking, adv monitor core (`struct adv_monitor`, pattern lists, monitor IDR and states), mgmt advertisement monitor notifications, Bluetooth address conversion, controller quirks, and vendor-event routing from HCI core. It also feeds `hdev->msft_curve_validity` for pairing/security behavior.

Risks: state synchronization is delicate because address filters are manipulated by vendor events, queued command callbacks, monitor removal, close, suspend, and resume. `filter_lock` and `hdev` lock ordering must remain consistent. A stale MSFT handle mapping can cause wrong mgmt monitor notifications or leaks. Power-off removes controller state without command responses, so local cleanup must reset monitor state exactly once. Malformed vendor events must not overread sk_buffs. Address-filter quirk behavior intentionally suppresses pattern events, so a failed address-filter add can hide device-found signals.

Test signals: test controllers or mocks should cover feature read, event prefix matching, pattern monitor add/remove success and failure, RSSI validation, suspend/resume rebuilding, close/open monitor state reset, filter enable status `0x0c`, malformed vendor events, and address-filter quirk flows with rapid found/lost events. Runtime signals include correct `ADV_MONITOR_STATE_OFFLOADED` transitions, mgmt device-found/lost notifications, empty handle/address-filter lists after close/release, and lockdep cleanliness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/msft.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/msft.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/msft.h

Purpose: declares the internal interface for Microsoft Bluetooth extension support and provides no-op fallbacks when `CONFIG_BT_MSFTEXT` is disabled.

Important APIs/types/functions: defines feature masks for BR/EDR RSSI monitor, LE connection RSSI monitor, LE advertising RSSI monitor, LE advertising monitor, curve-validity, and concurrent advertisement monitor support. When enabled, it declares MSFT lifecycle, open/close, vendor-event, feature, monitor, filter-enable, suspend/resume, and curve-validity helpers. When disabled, inline stubs return false, zero, or `-EOPNOTSUPP` as appropriate.

Control flow: callers can invoke MSFT helpers unconditionally; compile-time stubs collapse behavior when the extension is not built. Enabled builds dispatch into `msft.c`.

State and persistence behavior: the header owns no state. Enabled implementations store per-controller state in `hdev->msft_data` and `hdev->msft_curve_validity`; disabled stubs leave controllers without MSFT runtime state.

Dependencies and integration points: integrates with HCI device setup/teardown, adv monitor offload, suspend/resume, and vendor-event dispatch. It depends on Bluetooth core types being visible from include context.

Risks: fallback return values must match caller expectations; for example monitor operations fail with `-EOPNOTSUPP`, while lifecycle functions silently do nothing. New MSFT features require updating both declarations and disabled stubs to keep build configurations consistent.

Test signals: build with and without `CONFIG_BT_MSFTEXT`; disabled builds should compile callers without unresolved symbols and report no MSFT monitor support, while enabled builds should execute the real feature and monitor paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/msft.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/Kconfig -->
# sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/Kconfig

Purpose: defines kernel configuration options for the Bluetooth RFCOMM protocol layer and optional RFCOMM TTY emulation.

Important APIs/types/functions: `config BT_RFCOMM` is a tristate depending on `BT_BREDR`; it builds RFCOMM stream transport for Dialup Networking, OBEX, and similar Bluetooth applications. `config BT_RFCOMM_TTY` is a bool depending on `BT_RFCOMM` and `TTY`; it enables `/dev/rfcomm*` TTY emulation over RFCOMM channels.

Control flow: Kconfig selection determines whether the RFCOMM object is built into the kernel, as a module, or omitted, and whether `tty.o` is included in the RFCOMM module.

State and persistence behavior: no runtime state. Configuration persists in the kernel `.config` and determines compiled code and module availability.

Dependencies and integration points: `BT_RFCOMM` integrates with BR/EDR Bluetooth and `BTPROTO_RFCOMM`; `BT_RFCOMM_TTY` integrates with the Linux TTY subsystem and the RFCOMM device ioctl layer.

Risks: enabling TTY support expands the RFCOMM attack surface to ioctls, device lifetime, sysfs attributes, and line-discipline interactions. Disabling RFCOMM removes user-visible protocol support expected by legacy Bluetooth applications.

Test signals: allmodconfig/build tests should cover built-in and module modes, and runtime tests should confirm RFCOMM sockets are unavailable when disabled, available when `BT_RFCOMM` is enabled, and `/dev/rfcomm*` support appears only with `BT_RFCOMM_TTY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/Makefile -->
# sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/Makefile

Purpose: builds the Bluetooth RFCOMM protocol module from its core, socket, and optional TTY sources.

Important APIs/types/functions: `obj-$(CONFIG_BT_RFCOMM) += rfcomm.o` creates the RFCOMM built-in/module target. `rfcomm-y := core.o sock.o` always includes protocol/session and socket support. `rfcomm-$(CONFIG_BT_RFCOMM_TTY) += tty.o` conditionally adds TTY emulation.

Control flow: kbuild expands the object list according to Kconfig. If `CONFIG_BT_RFCOMM=m`, the combined `rfcomm.ko` includes the selected objects; if built-in, objects link into the kernel image.

State and persistence behavior: no runtime state; it controls build composition only.

Dependencies and integration points: aligns with `rfcomm/Kconfig`, module init/exit in `core.c`, socket init/cleanup in `sock.c`, and optional TTY init/cleanup in `tty.c`.

Risks: object ordering matters because `core.o` module init calls socket and TTY init functions; missing `tty.o` when `CONFIG_BT_RFCOMM_TTY` is enabled would break symbols, and including it when disabled would expose unwanted TTY code.

Test signals: build matrix for `CONFIG_BT_RFCOMM` disabled/built-in/module and `CONFIG_BT_RFCOMM_TTY` on/off catches composition errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/core.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/core.c

Purpose: implements the core RFCOMM protocol engine over L2CAP, including RFCOMM sessions, data link connections, frame encoding/decoding, credit-based flow control, modem status signaling, security callbacks, listener management, the `krfcommd` worker thread, module lifecycle, and debugfs state reporting.

Important APIs/types/functions: public core APIs include `rfcomm_dlc_alloc`, `rfcomm_dlc_free`, `rfcomm_dlc_open`, `rfcomm_dlc_close`, `rfcomm_dlc_exists`, `rfcomm_dlc_send`, `rfcomm_dlc_send_noerror`, `__rfcomm_dlc_throttle`, `__rfcomm_dlc_unthrottle`, `rfcomm_dlc_set_modem_status`, `rfcomm_dlc_get_modem_status`, `rfcomm_session_getaddr`, `rfcomm_send_rpn`, and `rfcomm_dlc_accept`. Key private units are `struct rfcomm_session`, `struct rfcomm_dlc`, `session_list`, `rfcomm_mutex`, `rfcomm_wq`, frame helpers for SABM/UA/DM/DISC/UIH/MCC commands, and `rfcomm_cb.security_cfm`.

Control flow: outgoing socket or TTY users allocate a DLC and call `rfcomm_dlc_open`. The core finds or creates an L2CAP-backed session, links the DLC, sets `BT_CONFIG`, performs security, negotiates PN, sends SABM, waits for UA, transitions to `BT_CONNECTED`, sends modem status, and then transmits queued UIH frames. Incoming L2CAP connections are accepted by a listening RFCOMM session, peer SABM/PN frames call `rfcomm_connect_ind` in the socket layer, and accepted DLCs proceed through security/deferred setup to UA and connected state. Close sends DISC immediately or queues it behind pending data, then unlinks the DLC and eventually closes the control session when no DLCs remain.

Control flow continued: `krfcommd` wakes on L2CAP callbacks, timers, and queued data. Each pass processes listener accepts, L2CAP connection completion, receive queues, DLC authentication flags, session/DLC timeouts, modem-status exchanges, credit replenishment, and queued TX frames. RX parsing validates FCS, decodes one- or two-byte lengths, dispatches SABM/DISC/UA/DM/UIH, handles MCC types PN/RPN/RLS/MSC/FCOFF/FCON/TEST/NSC, and delivers user data to the DLC owner callback. HCI security confirmation maps encryption/auth results to RFCOMM accept/reject/drop flags that the worker later consumes.

State and persistence behavior: state is in-memory only. `session_list` tracks L2CAP sessions with timers, direction, MTU, CFC mode, flags, and linked DLCs. Each DLC tracks dlci, address byte, state, timers, security level, role switch, MTU, priority, CFC credits, V.24 modem signals, pending flags, owner callbacks, and TX queue. Module parameters `disable_cfc`, `channel_mtu`, and `l2cap_ertm` alter runtime negotiation. Sessions hold module references except listeners; timers hold DLC references while armed.

Dependencies and integration points: depends on L2CAP kernel sockets, HCI connection security, Bluetooth socket and address helpers, RFCOMM public definitions in `net/bluetooth/rfcomm.h`, `rfcomm/sock.c` for incoming connect indications, optional `rfcomm/tty.c` callbacks, kthreads/wait queues/timers, sk_buffs, debugfs, and HCI callback registration. It registers module alias `bt-proto-3`.

Risks: protocol state transitions are highly concurrent: L2CAP callbacks, timers, security confirmations, socket close, TTY release, and the worker all touch DLC/session state under `rfcomm_mutex` plus per-DLC locks. Incorrect timer reference handling can leak or free DLCs prematurely. Credit-based flow control must avoid deadlock when credits hit zero or RX throttling suppresses replenishment. Frame parsing must reject malformed lengths/FCS without skb overreads. Deferred setup and security failure paths must not leave accepted sockets or DLCs orphaned. Module init ordering must unwind thread, sockets, TTY, HCI callbacks, and debugfs correctly.

Test signals: BlueZ RFCOMM socket tests, OBEX/DUN interoperability, incoming/outgoing simultaneous channel setup, deferred setup, security failures, encryption drop, CFC enabled/disabled peers, MTU override, DISC queued behind data, L2CAP close/reset, and high-throughput TX/RX should be covered. Runtime debugfs `rfcomm_dlc`, KASAN/KCSAN/lockdep, packet traces of SABM/PN/MSC/UIH, and forced timer expiry are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/sock.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/sock.c

Purpose: implements the RFCOMM `PF_BLUETOOTH` socket interface, mapping stream/raw socket operations to RFCOMM DLC operations and exposing listen/accept/connect/send/receive/options/ioctl/debugfs behavior.

Important APIs/types/functions: key operations are `rfcomm_sock_create`, `rfcomm_sock_bind`, `rfcomm_sock_connect`, `rfcomm_sock_listen`, `rfcomm_sock_accept`, `rfcomm_sock_getname`, `rfcomm_sock_sendmsg`, `rfcomm_sock_recvmsg`, `rfcomm_sock_setsockopt`, `rfcomm_sock_getsockopt`, `rfcomm_sock_ioctl`, `rfcomm_sock_shutdown`, and `rfcomm_sock_release`. `rfcomm_connect_ind` is the core-layer callback for incoming DLCs. Registration functions are `rfcomm_init_sockets` and `rfcomm_cleanup_sockets`. Socket state lives in `struct rfcomm_pinfo` from the public RFCOMM header plus a per-socket `struct rfcomm_dlc`.

Control flow: socket creation allocates a Bluetooth sock and a DLC, installs DLC callbacks, links the sock in `rfcomm_sk_list`, and sets default buffers. Bind stores source address/channel and prevents duplicate bound/listening channel/address pairs. Connect stores destination/channel, copies security and role-switch settings into the DLC, drops the socket lock to avoid RFCOMM lock deadlock, opens the DLC, then waits for `BT_CONNECTED` unless nonblocking. Listen allocates an automatic channel if needed and marks the socket `BT_LISTEN`. Incoming connect indications locate a listening parent, allocate a child socket/DLC, enqueue it on the accept queue, and return the DLC to core.

Control flow continued: DLC callbacks enqueue received skbs to the socket receive queue, throttle the DLC when receive memory exceeds the buffer, and mirror DLC state changes into socket state and accept queues. Sendmsg waits until the socket is ready, packages stream data into MTU-sized skbs with RFCOMM head/tail reserve, and passes them to `rfcomm_dlc_send`. Recvmsg handles deferred setup by accepting the DLC on the first receive, then drains stream data and unthrottles when receive memory falls below a threshold. Options support legacy `SOL_RFCOMM` link mode/conninfo and `SOL_BLUETOOTH` security/defer setup.

State and persistence behavior: all socket state is runtime-only. `rfcomm_sk_list` tracks live sockets under an rwlock. A socket owns one DLC until destruction; listening parents own accept queues of children. Socket receive/write queues buffer user data, while the DLC TX queue buffers framed outgoing data. Security level, role switch, source/destination address, and channel persist for the socket lifetime. `SOCK_ZAPPED` marks closed sockets awaiting orphan cleanup.

Dependencies and integration points: integrates with RFCOMM core DLC APIs, Bluetooth socket helpers (`bt_sock_alloc`, accept queues, wait helpers, procfs/debugfs), L2CAP/HCI conninfo, security cloning, optional RFCOMM TTY device ioctls, compat ioctl handling, and standard proto/proto_ops registration as `BTPROTO_RFCOMM`.

Risks: lock ordering between socket locks, `rfcomm_sk_list.lock`, DLC locks, and `rfcomm_mutex` is critical; connect deliberately drops the socket lock before opening the DLC. Receive memory accounting must stay balanced when data is moved or consumed, or throttling can become permanent. Incoming accept cleanup can race with DLC state callbacks and orphan kill. Deferred setup changes recv semantics and must not allow sends before accept. `rfcomm_dev_ioctl` expands behavior only when TTY support is compiled, so ioctls must fail predictably otherwise.

Test signals: tests should cover bind/listen conflicts, automatic channel allocation, blocking/nonblocking connect and accept, close during connect, deferred setup receive acceptance, security option mapping, receive-buffer throttling/unthrottling, send fragmentation by MTU, legacy RFCOMM options, TTY ioctl availability, procfs/debugfs rows, and orphan cleanup under socket close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/tty.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/tty.c

Purpose: implements RFCOMM TTY emulation, exposing RFCOMM DLCs as dynamic serial-like `/dev/rfcommN` devices with tty operations, device ioctls, sysfs attributes, modem-status mapping, and optional DLC reuse from connected sockets.

Important APIs/types/functions: `struct rfcomm_dev` holds tty port, ID/name, flags/status, source/destination/channel, modem status, owned DLC, sysfs device, write accounting, and pending receive queue. Device ioctl entry point is `rfcomm_dev_ioctl` handling `RFCOMMCREATEDEV`, `RFCOMMRELEASEDEV`, `RFCOMMGETDEVLIST`, and `RFCOMMGETDEVINFO`. TTY lifecycle uses `rfcomm_tty_install`, `rfcomm_tty_cleanup`, `rfcomm_tty_open`, `rfcomm_tty_close`, `rfcomm_tty_write`, `rfcomm_tty_set_termios`, throttle/unthrottle, modem `tiocmget/tiocmset`, and driver registration through `rfcomm_init_ttys`/`rfcomm_cleanup_ttys`.

Control flow: creating a device validates privileges and flags, either reuses the caller's connected DLC or allocates a fresh DLC after checking no duplicate channel exists, creates an ordered device ID, installs DLC callbacks, registers a dynamic tty device, reparents it under the HCI connection sysfs device when possible, and adds `address`/`channel` sysfs attributes. Opening the tty activates the port by opening the DLC and blocks until carrier is raised (`BT_CONNECTED`). Incoming DLC data is inserted into the tty flip buffer or queued as pending until the tty is ready. Writes allocate skbs up to DLC MTU, attach write-accounting destructors, and queue them through `rfcomm_dlc_send_noerror`.

Control flow continued: release ioctls mark a device released once, optionally close the DLC immediately, synchronously vhangup the tty, and drop tty-port references according to ownership flags. Termios changes are translated into RFCOMM RPN commands for baud, parity, stop bits, data bits, and XON/XOFF characters. TTY throttle/unthrottle maps to RFCOMM DLC flow control, and modem ioctls map Linux `TIOCM_*` bits to RFCOMM V.24 signals. Cleanup detaches the TTY, purges the DLC TX queue to avoid reference cycles, unregisters the device, removes it from the list, and drops the module reference.

State and persistence behavior: device state is transient kernel memory but user-visible as dynamic tty devices and sysfs attributes. `rfcomm_dev_list` is protected by `rfcomm_dev_lock`; ioctl create/release is serialized by `rfcomm_ioctl_mutex`. Write memory accounting is per-device via `wmem_alloc`, and `rfcomm_room` caps outstanding packets at forty. `RFCOMM_RELEASE_ONHUP`, `RFCOMM_REUSE_DLC`, `RFCOMM_TTY_ATTACHED`, `RFCOMM_TTY_OWNED`, and `RFCOMM_DEV_RELEASED` drive lifetime behavior.

Dependencies and integration points: depends on RFCOMM core DLC APIs, Bluetooth HCI routing/connection lookup for sysfs reparenting, Linux TTY core and tty_port helpers, sk_buffs, user copy for RFCOMM ioctls, capabilities (`CAP_NET_ADMIN`), sysfs device attributes, and RFCOMM public ioctl structs.

Risks: lifetime and reference ownership are complex, especially with `RFCOMM_REUSE_DLC`, release-on-hangup, tty port references, skb destructors, and socket-to-TTY ownership transfer. Device release must avoid double free while allowing synchronous hangup. Pending receive migration from reused sockets must maintain receive memory accounting. Termios translation sends RPN but local TTY settings may not be fully supported by the peer. `dev->tty_dev` assumptions during shutdown require the device to have registered successfully.

Test signals: exercise create/release/list/info ioctls with and without privileges, fixed and automatic device IDs, DLC reuse from connected sockets, open blocking until connection, release-on-hangup, write-room accounting, pending receive delivery, modem status changes, termios-to-RPN packets, sysfs attributes, close/hangup races, and cleanup under module unload. KASAN/refcount/lockdep are important for tty/DLC lifetime paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/tty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/sco.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/sco.c

Purpose: implements Bluetooth SCO/eSCO socket support for synchronous audio links. It registers `BTPROTO_SCO`, manages socket-to-HCI SCO connection binding, exposes send/receive/options APIs, handles incoming connection indication/confirmation callbacks, and reports state through procfs/debugfs.

Important APIs/types/functions: private `struct sco_conn` wraps an HCI connection, socket pointer, lock, MTU, delayed timeout work, and kref. `struct sco_pinfo` stores Bluetooth socket state, source/destination, flags, voice setting, codec, and `sco_conn`. Major functions include `sco_connect`, `sco_send_frame`, `sco_recv_frame`, socket operations `sco_sock_*`, option handlers for `BT_DEFER_SETUP`, `BT_VOICE`, `BT_PKT_STATUS`, `BT_CODEC`, `BT_PHY`, `BT_SNDMTU`, `BT_RCVMTU`, lower-layer callbacks `sco_connect_ind`, `sco_connect_cfm`, `sco_disconn_cfm`, packet entry `sco_recv_scodata`, and lifecycle `sco_init`/`sco_exit`.

Control flow: socket create allocates a seqpacket Bluetooth socket with default CVSD voice/codec settings. Bind stores the local address; connect routes to an HCI device, chooses SCO or eSCO based on controller capability and `disable_esco`, validates transparent air mode, calls `hci_connect_sco`, creates/gets `sco_conn`, attaches the socket, copies the source address, sets `BT_CONNECT` or `BT_CONNECTED`, and waits for connection unless nonblocking. Incoming HCI connection indications search listening sockets and optionally request deferred setup. Connection confirmation creates or finds `sco_conn` and either completes an outgoing socket or creates/enqueues an accepted child socket.

Control flow continued: sendmsg builds one skb from user data, validates connection state and MTU, attaches TX timestamp metadata, and calls `hci_send_sco`. Received SCO data looks up the HCI handle under device lock, holds `sco_conn`, and queues non-empty skbs to the connected socket. Deferred accept is triggered by recvmsg in `BT_CONNECT2`, sending either classic accept or synchronous accept HCI commands with voice settings. Shutdown/release clear timers, close channels, drop connection references, and kill orphaned sockets.

State and persistence behavior: all state is transient. `sco_sk_list` tracks live sockets. `sco_conn` lifetime is kref-managed and also tied to `hcon->sco_data`; delayed timeout work reports `ETIMEDOUT` to sockets still connecting/configuring. Each socket stores selected voice setting and codec, and connection MTU comes from HCI or defaults to 60. Socket queues hold inbound, outbound, and error-queue data. Module parameter `disable_esco` forces classic SCO connection creation.

Dependencies and integration points: depends on HCI core connection creation/drop, HCI callback registration, codec offload support and local codec lists, Bluetooth socket helpers, `net/bluetooth/sco.h` ABI structs/options, procfs/debugfs, delayed work, sk_buffs, control message parsing for TX timestamps, and mgmt/HCI packet-status error queues.

Risks: `sco_conn` lifetime is sensitive because HCI callbacks, socket close, delayed work, receive path, and accept path all reference the same connection. The code uses krefs, `kref_get_unless_zero`, socket holds, and conn locks to avoid UAF; regressions here are high risk. Option handling for codecs copies variable-sized user data and enumerates controller codec capability buffers. Deferred setup must not accept with unsupported voice settings. MTU enforcement is simple and will reject larger audio frames. `sco_conn_del` has unusual double-put behavior on the no-socket path, worth watching in refcount tests.

Test signals: validate outgoing SCO/eSCO connect, classic fallback with `disable_esco`, transparent air mode capability rejection, incoming listen/accept including deferred setup, send MTU enforcement, receive delivery and empty packet drop, voice/codec option set/get including offload codec enumeration, packet status/error queue behavior, shutdown with linger, HCI disconnect/error mapping, procfs/debugfs output, and KASAN/refcount/lockdep under close/connect races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/sco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/selftest.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/selftest.c

Purpose: runs optional Bluetooth subsystem selftests at initialization time, including ECDH P-256 test vectors and SMP selftests, with a debugfs result file for the ECDH test when enabled.

Important APIs/types/functions: under `CONFIG_BT_SELFTEST_ECDH`, static test vectors define private keys, public keys, and expected DH keys for three ECDH cases. `test_ecdh_sample` sets a private key and computes both sides of a shared secret. `test_ecdh` allocates the `ecdh-nist-p256` KPP transform, runs samples, records duration, and creates debugfs file `selftest_ecdh`. `run_selftest` calls `test_ecdh` and `bt_selftest_smp`. `bt_selftest` or `bt_selftest_init` dispatches the run depending on whether Bluetooth is modular or built-in.

Control flow: when selftesting is compiled in, initialization logs start, runs ECDH if configured, aborts on ECDH failure, then runs SMP selftests, logs finish, and returns the first error. Built-in Bluetooth schedules selftests via `late_initcall` so Bluetooth and crypto init ordering does not clash. Modular Bluetooth exposes `bt_selftest` for module init. ECDH debugfs reads return a cached `PASS (<usecs>)` or `FAIL` string.

State and persistence behavior: test vectors are `__initconst`; ECDH helper functions are `__init`. The only persistent runtime artifact is `test_ecdh_buffer` and the debugfs file, both representing the latest boot/module-load selftest result. The tests do not persist secrets or alter controller state.

Dependencies and integration points: depends on Linux crypto KPP `ecdh-nist-p256`, Bluetooth ECDH helpers, SMP selftest implementation in `smp.c`, `bt_debugfs`, debugfs file operations, kernel time accounting, and Bluetooth init/module mode.

Risks: failures in crypto allocation or ECDH vector comparison can fail Bluetooth selftest initialization. The ECDH transform is freed on the success path but not explicitly freed on early failure after allocation in this snapshot, which is a leak risk during failing init. Debugfs creation assumes `bt_debugfs` is usable. Test coverage is compile-time gated, so many builds may not run these checks.

Test signals: enable `CONFIG_BT_SELFTEST` and `CONFIG_BT_SELFTEST_ECDH`, boot or load the module, check kernel logs for pass/fail and `/sys/kernel/debug/bluetooth/selftest_ecdh` for result text. Negative testing can force bad vectors or missing crypto algorithm to verify failure propagation. SMP selftest logs/results provide the second major signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/selftest.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/selftest.h

Purpose: declares or stubs the Bluetooth selftest entry point according to `CONFIG_BT_SELFTEST` and whether the Bluetooth core is built as a module.

Important APIs/types/functions: when `CONFIG_BT_SELFTEST` is enabled and `CONFIG_BT` is a module, it declares `int bt_selftest(void);`. Otherwise it provides a static inline `bt_selftest` that returns success and has no side effects.

Control flow: modular Bluetooth builds call the real `bt_selftest` during module initialization. Built-in Bluetooth runs selftests from `selftest.c` through a late initcall instead, so users of this header get a no-op inline. Builds without selftests also compile to the no-op inline.

State and persistence behavior: owns no state. It only controls whether a caller sees a real module-load selftest entry or a no-op.

Dependencies and integration points: depends on Kconfig symbols `CONFIG_BT_SELFTEST` and `CONFIG_BT`. It is included by Bluetooth core initialization code to keep module and built-in selftest paths distinct.

Risks: configuration logic must match `selftest.c`; otherwise module builds could miss real selftests or built-in builds could attempt to call an unavailable symbol. The no-op success return can hide lack of selftest coverage unless build configuration is inspected.

Test signals: compile Bluetooth as module and built-in with `CONFIG_BT_SELFTEST` enabled and disabled; verify module builds call the real function, built-in builds run the late initcall, and disabled builds have no selftest side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/selftest.h -->
