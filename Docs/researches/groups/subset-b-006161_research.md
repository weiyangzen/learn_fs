<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_sync.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/hci_sync.c

## Purpose
Implements the synchronous HCI command execution layer and most higher-level Bluetooth controller state machines that need serialized HCI commands. It covers command request allocation/waiting, deferred command-work queues, controller init/open/close/power transitions, advertising and scan programming, privacy and accept-list maintenance, discovery, suspend/resume, ACL/LE/CIS/BIS/PA connection setup, and several exported convenience commands.

## APIs, Types, and Functions
The low-level API centers on `hci_cmd_sync_alloc()`, `__hci_cmd_sync_sk()`, `__hci_cmd_sync()`, `hci_cmd_sync()`, `__hci_cmd_sync_ev()`, `__hci_cmd_sync_status_sk()`, and `hci_cmd_sync_status()`. These build `HCI_COMMAND_PKT` skbs, optionally attach a socket reference, enqueue through `hdev->cmd_q`, wait on `hdev->req_wait_q`, and return either an skb response or a status/error.

The deferred execution API uses `struct hci_cmd_sync_work_entry` through `hci_cmd_sync_submit()`, `hci_cmd_sync_queue()`, `hci_cmd_sync_queue_once()`, `hci_cmd_sync_run()`, `hci_cmd_sync_run_once()`, lookup/dequeue/cancel helpers, and `hci_cmd_sync_work()`. These serialize callbacks under `hci_req_sync_lock()` and give callers a destroy callback for ownership cleanup.

Major exported state-machine helpers include advertising (`hci_update_adv_data_sync()`, `hci_setup_ext_adv_instance_sync()`, `hci_start_ext_adv_sync()`, `hci_enable_advertising_sync()`, `hci_remove_advertising_sync()`), scan and privacy (`hci_update_random_address_sync()`, `hci_get_random_address()`, `hci_update_passive_scan_sync()`, `hci_update_scan_sync()`), power lifecycle (`hci_dev_open_sync()`, `hci_dev_close_sync()`, `hci_set_powered_sync()`), discovery (`hci_start_discovery_sync()`, `hci_stop_discovery_sync()`), suspend/resume (`hci_suspend_sync()`, `hci_resume_sync()`), and connection operations (`hci_abort_conn_sync()`, `hci_connect_acl_sync()`, `hci_connect_le_sync()`, `hci_le_create_cis_sync()`, `hci_connect_pa_sync()`, `hci_connect_big_sync()`, `hci_past_sync()`, `hci_le_read_remote_features()`, `hci_acl_change_pkt_type()`, `hci_le_set_phy()`).

## Control Flow, State, and Persistence
Single-command synchronous flow is: allocate a command skb, mark `hdev->req_status = HCI_REQ_PEND`, splice a request queue into `hdev->cmd_q`, wake `cmd_work`, then sleep until `hci_cmd_sync_complete()` records `req_result`/`req_rsp` and wakes the waiter. Cancellation records `HCI_REQ_CANCELED`, resets timers/cmd count, and wakes the waiter. Response skbs and attached socket references are explicitly released on completion or error.

Work-item flow is separate from the HCI command queue: callbacks are appended to `hdev->cmd_sync_work_list`, processed by `hdev->cmd_sync_work` on `req_workqueue`, and run under request serialization. `_once` variants search pending entries to avoid duplicate queued work. `hci_cmd_sync_clear()` cancels pending entries and invokes destroy callbacks with `-ECANCELED`.

Persistent state lives mostly in `struct hci_dev`: feature bitmaps, quirks, command support masks, flags, discovery state, LE scan parameters, accept/resolving lists, advertising instances, RPA/static/random addresses, work items, timers, queued commands, connection hashes, local codec lists, SMP registration state, and vendor extension hooks. State is updated only after successful HCI command responses in many paths, but some cached advertising data is copied before a command is sent in legacy paths.

Init/open flow performs optional driver setup, reads version/address/features/commands, programs event masks, BR/EDR and LE defaults, debugfs, local codec and pairing options, host features, and vendor extension open hooks. Power-on then registers SMP, restores SSP/LE/auth/scan/class/name/EIR/advertising state, and notifies mgmt. Close/power-off drains work, stops discovery/scanning/advertising, disconnects connections, unregisters SMP, clears queues and volatile flags, optionally resets on close, and invokes transport close.

Advertising flow branches between legacy and extended advertising. It chooses connectable/scannable/event properties from mgmt flags, checks controller LE state compatibility, chooses public/static/RPA/NRPA address modes, sets parameters and data, schedules legacy software rotation with `adv_instance_expire`, and handles periodic advertising/Broadcast Announcement data. Scan flow disables active scanning before reconfiguration, updates random addresses and accept/resolving lists, handles interleaved adv-monitor scans, chooses duplicate filtering, and adjusts duty cycle for suspend, connection, discovery, mesh, and monitor use cases.

Connection flow queues create/cancel commands as cmd-sync work. ACL setup may cancel inquiry and use inquiry-cache page-scan data. LE setup may use directed advertising for peripheral role, extended create connection when available, stop scanning, choose connection params, wait for the correct enhanced/legacy complete event, and clean up on timeout. ISO helpers serialize CIS creation per CIG, PA sync creation/transfer, BIG sync creation/termination, and PAST sender commands.

## Dependencies and Integration
Depends on Bluetooth core headers, mgmt, SMP, EIR builders, codec/debugfs helpers, vendor extension modules (`msft`, `aosp`), LED integration, kernel workqueues/timers/wait queues/skbs/sockets, firmware node properties, RCU lists, IDR-based adv monitors, and HCI command-complete/status event handlers elsewhere in the stack. It integrates with transport driver callbacks (`open`, `close`, `setup`, `post_init`, `set_bdaddr`, `set_diag`, `shutdown`, `flush`, `wakeup`), mgmt notifications, debugfs, SMP channel registration, connection hash lifecycle, and controller quirk policy.

## Risks and Test Signals
Risks include races between command completion/cancel/timeout, incorrect request-lock use by callers of `__hci_cmd_sync*()`, stale cached advertising/scan data when HCI commands fail, work-entry duplicate matching by optional fields, controller-specific command-disallowed behavior while scanning/advertising/resolving lists are active, privacy/address changes deferred while advertising or initiating, suspend wake filter regressions, and cleanup ordering across `rx_work`, `cmd_work`, timers, skbs, and transport close. Notable code-review signals include an apparently uninitialized `err` return path in `hci_le_set_host_features_sync()` when neither CIS nor Channel Sounding host feature is programmed, and unreachable fallback code after the first return in `hci_le_read_all_remote_features_sync()`.

Strong test signals are HCI emulator tests for command complete/status/timeout/cancel paths, mgmt tests for power on/off and unconfigured-to-configured transitions, advertising instance rotation/removal and extended advertising command sequences, RPA/NRPA/static-address selection, accept/resolving-list overflow and rollback, discovery stop/start/interleaving, suspend/resume wake filters, LE create connection timeout cancellation, CIS/PA/BIG single-pending-command behavior, and fault injection for allocation failures and transport callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_sysfs.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/hci_sysfs.c

## Purpose
Provides driver-model/sysfs support for Bluetooth HCI host devices and connection child devices. It registers the global `bluetooth` class, initializes host and link `struct device` objects, exposes a write-only host `reset` attribute, and handles object release.

## APIs, Types, and Functions
`bt_class` is the shared class. `bt_link_release()` frees an `hci_conn`, and `bt_link` names connection devices as type `link`. `hci_conn_init_sysfs()`, `hci_conn_add_sysfs()`, and `hci_conn_del_sysfs()` initialize, register, and unregister per-connection devices. `bt_host_release()` frees or releases an `hci_dev` and drops the module reference taken during initialization. `reset_store()` invokes `hdev->reset` when available. `hci_init_sysfs()`, `bt_sysfs_init()`, and `bt_sysfs_cleanup()` initialize host device objects and register/unregister the class.

## Control Flow, State, and Persistence
Host devices get type `bt_host`, class `bluetooth`, and a module reference before `device_initialize()`. Their lifetime ends through `bt_host_release()`, which chooses `hci_release_dev()` for unregistering devices and `kfree()` otherwise. Connection devices are initialized under their parent HCI device, named as `<hdev-name>:<handle>`, and added only once. Deletion handles both paths: if `device_add()` never succeeded it only calls `put_device()`, otherwise it moves children off the connection device before `device_unregister()`.

The only sysfs attribute is `reset`; writing it does not parse the buffer and simply calls the transport reset callback if present. No persistent data is stored in this file beyond device model references, names, class/type metadata, and module references.

## Dependencies and Integration
Depends on the Linux device model, module reference counting, Bluetooth core `hci_dev`/`hci_conn` conversion helpers, and transport callbacks embedded in `struct hci_dev`. It integrates with the HCI connection lifecycle and the global Bluetooth subsystem init/exit sequence through `bt_sysfs_init()` and `bt_sysfs_cleanup()`.

## Risks and Test Signals
Risks include device lifetime mismatches around failed `device_add()`, use-after-free if connection children are not detached before unregister, reset callback side effects from any sysfs write content, and module reference leaks if `hci_init_sysfs()` is not paired with release. Test signals are sysfs class creation/removal, host device registration and release, failed connection `device_add()` cleanup, child-device reparenting on connection deletion, and reset attribute invocation under a fake transport callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hidp/Kconfig -->
# sources/distributed-fs/ceph-client/net/bluetooth/hidp/Kconfig

## Purpose
Defines the kernel configuration entry for Bluetooth HIDP support, which carries HID reports over Bluetooth for the Human Interface Device Profile.

## APIs, Types, and Functions
The single symbol is `CONFIG_BT_HIDP`, a tristate named `BT_HIDP` with prompt `HIDP protocol support`. It depends on `BT_BREDR` and `HID`, and the help text documents built-in (`Y`) and module (`M`, module name `hidp`) builds.

## Control Flow, State, and Persistence
There is no runtime control flow. The symbol controls whether the HIDP sources are compiled and whether the module init/exit paths in `core.c` and socket registration in `sock.c` are present. The dependency on BR/EDR excludes HIDP from LE-only Bluetooth builds.

## Dependencies and Integration
Integrates with the Bluetooth Kconfig tree, the HID subsystem, and the HIDP Makefile via `obj-$(CONFIG_BT_HIDP)`. It ensures the module is built only when classic Bluetooth and HID core support are available.

## Risks and Test Signals
Risks are configuration-level: missing `BT_BREDR` or `HID` silently hides HIDP, and build coverage can be lost if only LE Bluetooth configurations are tested. Test signals are `allmodconfig`/`allyesconfig` builds, `CONFIG_BT_HIDP=m` module build and load, `CONFIG_BT_HIDP=y` built-in link, and disabled dependency configurations confirming the symbol is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hidp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hidp/Makefile -->
# sources/distributed-fs/ceph-client/net/bluetooth/hidp/Makefile

## Purpose
Builds the Bluetooth HIDP module or built-in object from the HIDP core and socket implementation.

## APIs, Types, and Functions
`obj-$(CONFIG_BT_HIDP) += hidp.o` selects the composite object when the Kconfig symbol is enabled. `hidp-objs := core.o sock.o` links session/device logic from `core.o` with PF_BLUETOOTH socket/ioctl registration from `sock.o`.

## Control Flow, State, and Persistence
There is no runtime behavior in the Makefile. Build-time control flow follows the value of `CONFIG_BT_HIDP`; the resulting `hidp.o` contains both module lifecycle code and the socket family operations.

## Dependencies and Integration
Depends on the surrounding kernel kbuild system and the `BT_HIDP` Kconfig symbol. It integrates the two implementation files into one loadable module named `hidp` when built as `m`.

## Risks and Test Signals
Risks include missing either object from `hidp-objs`, which would break module init or ioctl/session symbols at link time. Test signals are successful built-in and module builds, `modinfo hidp` metadata from `core.c`, and link errors if either object dependency is accidentally removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hidp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hidp/core.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/hidp/core.c

## Purpose
Implements the Bluetooth HIDP runtime: session creation/deletion, L2CAP control and interrupt channel I/O, HID/input device registration, boot-protocol keyboard/mouse fallback, HID raw report transactions, idle timeout handling, and module init/exit.

## APIs, Types, and Functions
Public entry points used by `sock.c` are `hidp_connection_add()`, `hidp_connection_del()`, `hidp_get_connlist()`, and `hidp_get_conninfo()`. Module lifecycle is `hidp_init()`/`hidp_exit()`, which delegate socket setup/cleanup to `hidp_init_sockets()` and `hidp_cleanup_sockets()`.

Session management uses global `hidp_session_list`, `hidp_session_sem`, and `hidp_session_wq`; `struct hidp_session` is defined in `hidp.h` and refcounted with `kref`. Key helpers include `hidp_session_new()`, `hidp_session_start_sync()`, `hidp_session_probe()`, `hidp_session_remove()`, `hidp_session_run()`, `hidp_session_thread()`, `hidp_session_unregister_conn()`, `hidp_session_get()`, and `hidp_session_put()`.

I/O helpers include `hidp_send_message()`, `hidp_send_ctrl_message()`, `hidp_send_intr_message()`, `hidp_recv_ctrl_frame()`, `hidp_recv_intr_frame()`, `hidp_process_handshake()`, `hidp_process_hid_control()`, `hidp_process_data()`, `hidp_process_transmit()`, and `hidp_send_frame()`. HID/input integration uses `hidp_setup_hid()`, `hidp_setup_input()`, `hidp_session_dev_init()`, `hidp_session_dev_add()`, `hidp_session_dev_del()`, `hidp_session_dev_work()`, and HID low-level driver callbacks `hidp_parse()`, `hidp_raw_request()`, `hidp_output_report()`, `hidp_get_raw_report()`, and `hidp_set_raw_report()`.

## Control Flow, State, and Persistence
`hidp_connection_add()` verifies that both sockets are connected L2CAP sockets with matching source/destination addresses, validates flags, gets the underlying `l2cap_conn`, allocates a session, initializes HID or boot input devices, takes socket file references, and registers an `l2cap_user`. The L2CAP probe callback prevents duplicate sessions for the same remote address, starts the kthread, registers boot input synchronously or schedules HID registration asynchronously, then links the session into the global list with its own reference.

The session thread attaches wait entries to both socket wait queues, boosts priority, starts the idle timer, signals startup, and loops while not terminated and both sockets are `BT_CONNECTED`. Each loop drains interrupt receive skbs, sends queued interrupt frames, drains control receive skbs, sends queued control frames, then sleeps on the global HIDP wait queue. Runtime errors, socket disconnect, virtual cable unplug, idle timeout, or explicit deletion set `terminate`, wake the thread, unregister the L2CAP user, wake report waiters, delete timers, and drop references.

Incoming interrupt data with `HIDP_TRANS_DATA | HIDP_DATA_RTYPE_INPUT` resets the idle timer and feeds either boot input decoding or the HID core. Control frames handle handshakes, HID_CONTROL commands, and DATA reports. Raw GET_REPORT and SET_REPORT are serialized by `report_mutex`, set wait bits in `session->flags`, transmit control requests, and wait up to 5 or 10 seconds for matching DATA/handshake completion on `report_queue`.

State persists in `struct hidp_session`: address, L2CAP user/connection, control and interrupt sockets, transmit queues, MTUs, idle timeout, HID/input devices, report descriptor data, keyboard state, LED state, report transaction fields, timer, kthread state, termination flag, and refcount. Global state persists as the session list and module/socket registrations.

## Dependencies and Integration
Depends on Bluetooth core, L2CAP socket internals, HID core and hidraw, input core, skbs, kthreads, timers, wait queues, kernel socket send APIs, file references, and module reference counting. It integrates with userspace through the HIDP ioctl ABI in `sock.c`, with L2CAP through `l2cap_register_user()`, with the HID subsystem through `hid_ll_driver`, and with the input subsystem for boot-protocol devices when no usable HID report descriptor is supplied or the HID device is ignored.

## Risks and Test Signals
Risks include concurrent teardown between userspace deletion, L2CAP removal, idle timeout, and self-unregistering thread exit; report waiters hanging or receiving the wrong report if flags/numbered reports are mishandled; skb ownership transfer in `hidp_process_data()`; unbounded trust in userspace report descriptors subject to HID parser behavior; boot keyboard/mouse decoding limits; socket wakeup and memory-barrier assumptions; and cleanup ordering for asynchronous HID registration work versus session removal.

Strong test signals are ioctl-driven add/delete/list/info flows with duplicate-session checks, mismatched or disconnected socket rejection, HID descriptor device registration and fallback boot input registration, virtual cable unplug behavior, idle timeout disconnect, GET_REPORT/SET_REPORT success/handshake/timeout/signal paths, interrupt input delivery to HID and input devices, transmit retry on `-EAGAIN`, L2CAP removal during device probe, and module unload after active sessions terminate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hidp/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hidp/hidp.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/hidp/hidp.h

## Purpose
Defines the internal and userspace ABI surface for the Bluetooth HIDP implementation: protocol constants, ioctl numbers, request/response structures, session state, `struct hidp_session`, and cross-file function prototypes.

## APIs, Types, and Functions
Protocol definitions include HIDP header masks, transaction types (`HIDP_TRANS_*`), handshake result codes, HID control operation codes, data report type bits, and boot/report protocol constants. Ioctl numbers are `HIDPCONNADD`, `HIDPCONNDEL`, `HIDPGETCONNLIST`, and `HIDPGETCONNINFO`.

Userspace ABI structs are `struct hidp_connadd_req`, `struct hidp_conndel_req`, `struct hidp_conninfo`, and `struct hidp_connlist_req`. Internal state uses `enum hidp_session_state` and `struct hidp_session`, which stores list/refcounting, thread and termination state, L2CAP user/connection, sockets, transmit queues, MTUs, device pointers, report descriptor, keyboard/LED state, raw-report wait state, and a temporary input buffer. Prototypes expose connection management to `sock.c` and socket init/cleanup to `core.c`.

## Control Flow, State, and Persistence
The header itself has no runtime control flow, but it defines the persistent per-session shape used by `core.c`. `HIDP_SESSION_IDLING`, `HIDP_SESSION_PREPARING`, and `HIDP_SESSION_RUNNING` gate startup and asynchronous device registration. Flag bits record user-visible options (`HIDP_VIRTUAL_CABLE_UNPLUG`, `HIDP_BOOT_PROTOCOL_MODE`, `HIDP_BLUETOOTH_VENDOR_ID`) and internal report waits (`HIDP_WAITING_FOR_RETURN`, `HIDP_WAITING_FOR_SEND_ACK`).

## Dependencies and Integration
Depends on kernel type definitions, HID core, kref, Bluetooth core, and L2CAP. It is included by both `core.c` and `sock.c`, and its ioctl structs form the compatibility contract with legacy HIDP userspace tools.

## Risks and Test Signals
Risks include ABI layout stability, pointer-size differences handled separately by compat ioctl code, fixed 128-byte names, user pointer lifetime for report descriptors during add, and the misspelled `HIDP_DATA_RTYPE_OUPUT` constant being part of the source API spelling used throughout the implementation. Test signals include 32-bit compat ioctl coverage, structure size/layout checks for userspace tools, flag validation, and raw report paths for numbered and unnumbered reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hidp/hidp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hidp/sock.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/hidp/sock.c

## Purpose
Provides the HIDP PF_BLUETOOTH raw socket endpoint and ioctl bridge used by userspace to add, remove, list, and inspect HIDP sessions. It also registers the HIDP Bluetooth protocol family entry, procfs listing, and protocol object.

## APIs, Types, and Functions
Socket operations are `hidp_sock_create()`, `hidp_sock_release()`, `hidp_sock_ioctl()`, and optional `hidp_sock_compat_ioctl()`, wired through `hidp_sock_ops`. The ioctl dispatcher `do_hidp_sock_ioctl()` handles `HIDPCONNADD`, `HIDPCONNDEL`, `HIDPGETCONNLIST`, and `HIDPGETCONNINFO`. `hidp_init_sockets()` registers `hidp_proto`, `BTPROTO_HIDP`, and `/proc` support; `hidp_cleanup_sockets()` tears them down. `hidp_sk_list` tracks open HIDP sockets.

## Control Flow, State, and Persistence
Creating a socket requires `SOCK_RAW`, allocates a `struct bt_sock`, assigns HIDP proto ops, marks it unconnected, and links it into `hidp_sk_list`. Release unlinks, orphans, and drops the socket reference.

For `HIDPCONNADD`, ioctl handling requires `CAP_NET_ADMIN`, copies `struct hidp_connadd_req` from userspace, looks up the supplied control and interrupt socket file descriptors, NUL-terminates the name, calls `hidp_connection_add()`, optionally copies the request back, and drops both socket fd references. `HIDPCONNDEL` also requires `CAP_NET_ADMIN` and calls `hidp_connection_del()`. Listing and info ioctls copy request structs in, delegate to `core.c`, and copy updated results out. Compat handling remaps 32-bit pointers for `HIDPGETCONNLIST` and `HIDPCONNADD`.

Persistent state is limited to registered protocol metadata and the global Bluetooth socket list. Actual HIDP session state is owned by `core.c`.

## Dependencies and Integration
Depends on Bluetooth socket helpers (`bt_sock_alloc`, `bt_sock_link`, `bt_sock_register`, procfs helpers), Linux file descriptor lookup, usercopy helpers, capability checks, compat pointer conversion, and the HIDP core connection APIs. It integrates with module init/exit in `core.c` and exposes the legacy userspace control plane for creating HIDP sessions over already-connected L2CAP sockets.

## Risks and Test Signals
Risks include ioctl ABI compatibility, usercopy failures after sessions are created, fd lifetime/reference mistakes around `sockfd_lookup()`/`sockfd_put()`, insufficient privilege checks on future mutating commands, 32-bit compat structure drift, and raw socket creation outside the initial network namespace assumptions implied by procfs init on `init_net`.

Strong test signals are raw socket create/release, unsupported socket type rejection, capability checks for add/delete, bad user pointer handling, invalid `cnum` rejection, fd lookup cleanup when one socket lookup fails, compat add/list from a 32-bit process, registration rollback if `bt_sock_register()` or procfs init fails, and cleanup removing procfs/protocol registrations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hidp/sock.c -->
