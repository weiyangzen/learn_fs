# Research Report: subset-b-006159

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_conn.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/hci_conn.c

## Purpose

`hci_conn.c` implements Bluetooth HCI connection lifecycle management for the Linux Bluetooth stack copy in this tree. It creates, links, configures, secures, aborts, tears down, and reports HCI connections for BR/EDR ACL, LE ACL, SCO/eSCO, CIS, BIS, and PA synchronization links. It is the central bridge between upper protocols such as L2CAP, SCO, ISO, SMP, and mgmt, and lower controller command helpers such as `hci_connect_le_sync()`, `hci_abort_conn_sync()`, `hci_le_create_cis_sync()`, and BIG/CIG/periodic advertising setup routines.

The file also owns per-connection delayed work for disconnect, idle/sniff mode, auto-accept, and LE connection timeout handling; connection child/parent relationships; HCI channel allocation; security escalation; PHY changes; transmit timestamp bookkeeping; and ethtool timestamp capability reporting.

## Important APIs, Types, and Functions

Key local helper types are `struct sco_param`, which encodes SCO/eSCO packet type, latency, and retransmission effort presets, `struct conn_handle_t`, which carries a connection plus parent handle into async sync-command work, `struct le_conn_update_data`, which retains a connection across queued LE update work, and `struct iso_list_data`, which is reused for BIG/BIS/CIG/CIS counting and cleanup decisions.

Connection allocation flows through `__hci_conn_add()`, `hci_conn_add_unset()`, and `hci_conn_add()`. `__hci_conn_add()` validates controller MTUs and feature support by link type, resolves LE/ISO identity addresses through IRKs, initializes default connection state, queues, work items, role, mode, auth fields, PHY defaults, ISO/SCO callbacks, and sysfs state, then inserts the connection into `hdev->conn_hash`. Unset outbound handles are allocated from `hdev->unset_handle_ida` above the real controller handle range and later replaced by `hci_conn_set_handle()`.

User-visible connection attempts enter through `hci_connect_acl()`, `hci_connect_le()`, `hci_connect_le_scan()`, `hci_connect_sco()`, `hci_connect_cis()`, `hci_connect_bis()`, `hci_pa_create_sync()`, and `hci_conn_big_create_sync()`. They set pending security, timeouts, role, connection reason, and ISO QoS, then call sync-command helpers to start controller procedures. LE explicit scan cleanup is handled by `hci_connect_le_scan_cleanup()`, which resolves RPAs back to identity addresses, removes or requeues `hci_conn_params`, emits `mgmt_connect_failed()` when appropriate, and updates passive scanning.

Teardown is centered on `hci_disconnect()`, `hci_abort_conn()`, `hci_conn_failed()`, `hci_conn_del()`, `hci_conn_cleanup()`, `hci_conn_hash_flush()`, and link-specific cleanup callbacks `bis_cleanup()` and `cis_cleanup()`. `hci_conn_del()` unlinks children, cancels delayed work, removes the connection from the hash, restores controller packet credits for unacknowledged packets, purges SKB queues, removes debugfs/sysfs, dequeues pending sync callbacks, and drops the owning device reference.

Security APIs include `hci_conn_security()`, `hci_conn_auth()`, `hci_conn_encrypt()`, `hci_conn_check_link_mode()`, and `hci_conn_check_secure()`. LE security delegates to SMP. BR/EDR security escalates authentication and encryption based on requested security level, key type, MITM/FIPS requirements, Secure Connections Only mode, AES-CCM state, and encryption key size availability.

PHY and channel APIs include `hci_chan_create()`, `hci_chan_del()`, `hci_chan_lookup_handle()`, `hci_conn_get_phy()`, `hci_conn_set_phy()`, and helpers mapping mgmt PHY masks to HCI packet type and LE Set PHY masks. Transmit accounting APIs are `hci_setup_tx_timestamp()`, `hci_conn_tx_queue()`, `hci_conn_tx_dequeue()`, and `hci_ethtool_ts_info()`.

## Control Flow

For outbound LE direct connection, `hci_connect_le()` checks LE enablement, serializes controller connection attempts with `hci_lookup_le_connect()`, handles existing scanning connections, optionally substitutes a cached RPA for an identity address, creates or reuses an unset `LE_LINK`, initializes pending security and timeout fields, then calls `hci_connect_le_sync()`. For scan-based explicit connects, `hci_connect_le_scan()` creates an unset LE connection in `BT_CONNECT`, marks `HCI_CONN_SCANNING`, attaches explicit connection parameters to `hdev->pend_le_conns`, and calls `hci_update_passive_scan()`. Failure later routes through `hci_le_conn_failed()` and `hci_connect_le_scan_cleanup()`.

For BR/EDR ACL, `hci_connect_acl()` rejects disabled BR/EDR and same-address self-connections, creates an ACL connection when absent, holds it for the caller, and starts `hci_connect_acl_sync()` if the connection is open or closed. SCO/eSCO setup first ensures an ACL parent through `hci_connect_acl()`, links the SCO child using `hci_conn_link()`, then either defers until the ACL leaves sniff mode or starts SCO/eSCO setup with `hci_sco_setup()`. Enhanced synchronous setup may be queued through `hci_cmd_sync_queue()` so codec datapath configuration and enhanced setup commands run in command-sync context.

For ISO unicast, `hci_connect_cis()` establishes or scans for the LE parent, normalizes ISO QoS with LE PHY and interval defaults, binds a CIS through `hci_bind_cis()`, links it to the LE parent, marks it `BT_CONNECT`, and queues `hci_le_create_cis_pending()`. CIG/CIS allocation is done by `hci_le_set_cig_params()`, which chooses a reconfigurable CIG and unused CIS then queues `set_cig_params_sync()`. For ISO broadcast, `hci_bind_bis()` allocates BIG/BIS identifiers, validates that all BISes in the same BIG share QoS and BASE data, links BISes together, and `hci_connect_bis()` queues periodic advertising plus `LE Create BIG`.

Abort flow is deliberately serialized. `hci_abort_conn()` records `abort_reason` once, cancels a pending connect command if it is blocking command-sync work, tries `hci_cancel_connect_sync()`, and then executes `abort_conn_sync()` immediately or as a one-shot command-sync callback. This prevents handle replacement after abort and avoids double termination attempts.

## State and Persistence Behavior

Connection state is in-memory and tied to `struct hci_dev`. Persistent-on-disk state is not written here, but connection events update mgmt and upper layers so userspace may persist bonds or policy elsewhere. Important mutable fields include `conn->state`, `role`, `mode`, `flags`, `handle`, `abort_reason`, `sec_level`, `pending_sec_level`, `auth_type`, `key_type`, `conn_timeout`, `sent`, `pkt_type`, PHY fields, ISO QoS, codec data, and parent/child link pointers. `hci_conn_params` lists on the device persist across LE autoconnect attempts until explicitly removed or cleared.

Reference management is central. Connection objects are held by callers with `hci_conn_hold()`, referenced by async callbacks with `hci_conn_get()/hci_conn_put()`, held by channels and parent/child links, and protected by RCU during hash/list traversal. Delayed work items must be canceled before final cleanup. Unset handles are tracked in an IDA and freed when replaced or when the connection is destroyed.

## Dependencies and Integration Points

The file depends on `hci_core.h` for device, connection, flags, command helpers, hash lookup/list walkers, and sync command APIs; on L2CAP/SCO/ISO/SMP for upper-layer confirmation and security; on mgmt for user-visible events; on debugfs/sysfs cleanup; and on controller feature predicates such as `lmp_esco_capable()`, `ext_adv_capable()`, and `enhanced_sync_conn_capable()`. It is called by mgmt, socket protocols, event handlers, and TX scheduling paths.

Important integration points include `mgmt_connect_failed()`, `mgmt_new_conn_param()`, `hci_connect_cfm()`, `hci_disconn_cfm()`, `hci_conn_del_sysfs()`, `hci_cmd_sync_queue()`, `hci_cmd_sync_run_once()`, `hci_update_passive_scan()`, `hci_enable_advertising()`, `hci_start_per_adv_sync()`, `hci_past_sync()`, and upper protocol receive/transmit code that uses `hci_chan`.

## Risks and Edge Cases

Concurrency risks are high around connection deletion, command-sync callbacks, RCU parent/child links, and delayed work. This file mitigates several of them by validating connections under `hdev->lock` in queued work, using `hci_conn_get()` for async LE update and BIG creation callbacks, synchronizing RCU after link removal, and canceling pending command-sync callbacks during deletion. Any future change that stores raw `struct hci_conn *` in queued work must preserve those lifetime rules.

State-machine risks include double aborts, scan cleanup that removes LE params still needed for autoconnect, CIG/BIG identifier reuse, and controller packet credit restoration on deletion. Security-sensitive paths include same-BDADDR ACL rejection, FIPS/AES-CCM checks, key-size stalling, debug key behavior through flags owned elsewhere, and `HCI_CONN_FLUSH_KEY` removal. ISO cleanup must avoid terminating periodic advertising, BIG sync, CIGs, or PA sync while sibling BIS/CIS connections still use them.

Input validation is scattered through link-type checks, QoS range allocation, PHY masks, handle range validation, and debug/command helper return values. A notable maintenance risk is that many helpers require `hdev->lock` by comment rather than type enforcement.

## Test Signals

Useful test signals include connection lifecycle tests for ACL, LE direct, LE scan/RPA, SCO/eSCO codec fallback, CIS parent-child setup, BIS BIG sharing, PA sync failure, and abort-during-connect. KUnit or fault-injection tests should exercise allocation failures in `__hci_conn_add()`, queued command cancellation, `hci_conn_set_handle()` freeing unset IDs, and `hci_conn_del()` credit restoration. Runtime signals include mgmt `connect-failed`/new-conn-param events, btmon traces of HCI commands, debugfs/sysfs connection directories, packet counters, `link tx timeout` logs, and timestamp delivery for L2CAP/SCO/ISO sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_core.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/hci_core.c

## Purpose

`hci_core.c` is the main HCI device core. It manages global HCI device registration, lookup, lifetime, power transitions, ioctl compatibility operations, inquiry cache, key and OOB stores, advertising instances and monitors, LE connection parameter lists, suspend/resume, RX and TX workqueues, command serialization, packet routing, and driver-facing receive/send entry points. It is the backbone that connects controller drivers, socket/upper protocol code, management operations, debugfs, rfkill, PM notifiers, Microsoft extension support, and HCI event processing.

## Important APIs, Types, and Functions

Global state includes `hci_dev_list` protected by `hci_dev_list_lock`, `hci_cb_list` protected by `hci_cb_list_lock`, and `hci_index_ida` for controller indexes. Device references are acquired by `hci_dev_get()` or the SRCU-aware `hci_dev_get_srcu()` and released by `hci_dev_put()` or `hci_dev_put_srcu()`.

Device lifecycle starts with `hci_alloc_dev_priv()`, which allocates `struct hci_dev`, initializes defaults, locks, queues, work items, delayed timers, lists, IDA/IDR state, sysfs/device state, and command-sync infrastructure. `hci_register_dev()` validates driver callbacks, allocates an HCI index, creates workqueues and debugfs directories, registers the device and rfkill handle, sets setup/auto-off/default BR/EDR flags, adds the device to the global list, announces socket/mgmt events, registers suspend notifier, starts power-on work, initializes adv monitor IDR, and registers MSFT extension support. `hci_unregister_dev()` removes the device from global discovery, disables work, clears command-sync state, closes the device, emits mgmt removal, unregisters rfkill and device state, and leaves final memory cleanup to `hci_release_dev()`.

Command and ioctl APIs include `hci_dev_open()`, `hci_dev_close()`, `hci_dev_reset()`, `hci_dev_reset_stat()`, `hci_dev_cmd()`, `hci_inquiry()`, `hci_get_dev_list()`, and `hci_get_dev_info()`. Modern command serialization is handled by `hci_send_cmd()`, `__hci_cmd_send()`, `hci_cmd_work()`, `hci_send_cmd_sync()`, `hci_cmd_timeout()`, `hci_ncmd_timeout()`, `hci_req_cmd_complete()`, and helpers for sent command/event data.

State-store APIs include inquiry cache helpers, `hci_add_link_key()`, `hci_find_link_key()`, `hci_remove_link_key()`, `hci_add_ltk()`, `hci_find_ltk()`, `hci_add_irk()`, `hci_find_irk_by_rpa()`, `hci_find_irk_by_addr()`, blocked-key handling, remote OOB add/remove/clear, advertising instance add/remove/update helpers, advertising monitor add/remove helpers, generic BDADDR list helpers, and LE connection parameter helpers.

Packet interfaces are `hci_recv_frame()`, `hci_recv_diag()`, `hci_send_acl()`, `hci_send_sco()`, `hci_send_iso()`, `hci_register_cb()`, `hci_unregister_cb()`, and the internal RX/TX workers. Driver-specific pseudo packets are intercepted in `hci_send_frame()` and delegated to `hci_drv_process_cmd()`.

## Control Flow

Open and close operations are serialized with `hci_req_sync_lock()`. `hci_dev_open()` rejects unconfigured non-user-channel opens, cancels auto-off, flushes setup work, enables legacy bondable mode for non-mgmt users, and runs `hci_dev_open_sync()`. `hci_dev_close()` rejects user-channel close, cancels power-on/auto-off work, and runs `hci_dev_close_sync()`. Reset purges RX and command queues, drains work safely, flushes inquiry cache and connections, resets packet counters, and calls `hci_reset_sync()`.

Power management flows through work items and rfkill callbacks. `hci_power_on()` either converts an auto-off powered controller into a mgmt power-on completion or opens the device, checks rfkill/unconfigured/address validity, schedules auto-off, and emits mgmt index-added transitions from setup/config states. `hci_rfkill_set_block()` sets `HCI_RFKILLED` and powers down or closes if needed. `hci_suspend_dev()` cancels blocking sync commands, calls `hci_suspend_sync()`, clears wake reason, reports mgmt suspend, and emits socket suspend events; `hci_resume_dev()` calls `hci_resume_sync()` and reports wake reason.

Receive flow starts when a driver calls `hci_recv_frame()`. The function verifies the device is up or initializing, optionally lets the driver classify packet type, converts ACL packets carrying ISO handles into ISO packets, timestamps the skb, queues it on `hdev->rx_q`, and schedules `hci_rx_work()`. RX work mirrors packets to monitors and promiscuous sockets, drops data packets in inappropriate user-channel/init states, then dispatches HCI events to `hci_event_packet()`, ACL data to L2CAP, SCO data to SCO, and ISO data to ISO.

Transmit flow from upper protocols queues formatted ACL/SCO/ISO skbs onto connection or channel queues and schedules `hci_tx_work()`. TX work first schedules SCO/eSCO, ISO, ACL, and LE data unless the device is user-channel, then drains raw queued packets. The schedulers choose connections/channels with pending data and low sent counts, apply controller packet credits (`acl_cnt`, `le_cnt`, `sco_cnt`, `iso_cnt`), update last-TX timestamps, and call `hci_send_conn_frame()`. ACL and LE scheduling also recalculates priority and opportunistically schedules SCO after data packets.

Command flow uses `hdev->cmd_q` and `cmd_cnt`. `hci_send_cmd()` allocates a command skb, marks it as a request start, queues it, and schedules command work. `hci_cmd_work()` sends one command when the controller has command credits and arms `cmd_timer`. `hci_send_cmd_sync()` clones the last command into `hdev->sent_cmd`, sends it through the driver, decrements command count, and snapshots request skb state for pending sync requests. Event handling later calls `hci_req_cmd_complete()` to match command completion/status against the last command, clear pending flags, run request callbacks, and drop queued commands belonging to failed requests.

## State and Persistence Behavior

Most state is in-memory per `struct hci_dev`: flags, quirks, capabilities, feature pages, MTUs, packet credits, discovery cache, keys, IRKs, LTKs, remote OOB data, adv instances, monitors, connection params, command queues, workqueues, timers, rfkill, debugfs, sysfs device, and PM notifier. The file does not directly persist to disk, but it decides which keys are persistent via `hci_persistent_key()` and exposes/updates state consumed by mgmt and userspace policy.

RCU is used for key lists and some connection/parameter traversals. SRCU protects device lookup during reset against unregister. Workqueue disable/drain order is important in unregister and reset so delayed command timers and worker callbacks do not run after lists or queues have been destroyed. Packet credit counters are volatile controller flow-control state and are restored/updated by events and connection teardown.

## Dependencies and Integration Points

The file depends on Linux kernel subsystems including workqueues, rfkill, debugfs, crypto, kcov, PM notifiers, IDA/IDR, SRCU/RCU, skb queues, wait bits, and user-copy helpers. Bluetooth dependencies include `hci_core.h`, L2CAP, SCO, ISO, SMP, mgmt, debugfs, LED helpers, MSFT/AOSP extensions, codec handling, monitor/socket forwarding, and HCI event parsing.

Controller drivers integrate by allocating `hci_dev`, filling `open`, `close`, `send`, optional `flush`, `reset`, `wakeup`, `set_diag`, `classify_pkt_type`, and driver-specific command handlers, then calling `hci_register_dev()`. Upper layers integrate by registering `hci_cb`, sending ACL/SCO/ISO data, consuming RX callbacks, and using mgmt/ioctl APIs.

## Risks and Edge Cases

The highest-risk areas are lifecycle races among unregister, workqueue callbacks, command timers, rfkill poweroff, suspend/resume, and packet RX. The file uses device references, SRCU, ordered workqueues, explicit work disable, and `HCI_CMD_DRAIN_WORKQUEUE` to reduce those races. Future changes must preserve the reset/unregister ordering around command timers and workqueue draining.

Security-sensitive areas include blocked-key filtering, persistent-key policy, public/static identity address selection, OOB data exposure, same-controller power state gating, debugfs secrets created elsewhere, and command validation for legacy ioctls. Data path risks include packet type misclassification, ISO-over-ACL correction, unknown-handle packet logging, fragmented skb header construction, flow-control counter underflow, and stalled link timeout disconnects.

Memory and bounds risks are mitigated by `kzalloc_flex()`, max response checks for ioctls, IDR/IDA bounds, list safe iteration, RCU frees, and command length checks. Several helpers rely on callers holding `hdev->lock` or `hci_req_sync_lock()`, so misuse may appear as list corruption or inconsistent mgmt notifications rather than local compile errors.

## Test Signals

Test coverage should include register/unregister under active RX/TX, rfkill during setup, open/close/reset through ioctl and mgmt paths, command timeout and ncmd timeout injection, suspend/resume while command-sync work is pending, inquiry cache refresh and user-copy bounds, key add/remove/blocked-key lookup, advertising instance rotation/removal, adv monitor MSFT fallback, and LE connection parameter list cleanup. Runtime signals include btmon command/event traces, debugfs state files, mgmt index/settings events, HCI socket device events, rfkill state, workqueue warnings, packet counters in `hdev->stat`, and controller credit behavior under ACL/LE/ISO/SCO traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_debugfs.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/hci_debugfs.c

## Purpose

`hci_debugfs.c` creates debugfs files for inspecting and, for selected test-only parameters, modifying HCI device state. It is split by controller capability: common files, BR/EDR files, LE files, per-connection directories, and basic test/diagnostic files. The file is not part of normal Bluetooth protocol control, but it exposes important internal state for diagnostics and provides controlled debug knobs for timing, key-size policy, test mode, vendor diagnostics, static address selection, MITM forcing, and selected controller quirks.

## Important APIs, Types, and Functions

The exported creation functions are `hci_debugfs_create_common()`, `hci_debugfs_create_bredr()`, `hci_debugfs_create_le()`, `hci_debugfs_create_conn()`, and `hci_debugfs_create_basic()`. These are declared in `hci_debugfs.h` and called by HCI setup paths when debugfs support is enabled.

Two macros generate repeated file operations. `DEFINE_QUIRK_ATTRIBUTE()` creates read/write boolean attributes for quirks that may only be changed while the controller is down. `DEFINE_INFO_ATTRIBUTE()` creates seq-file show handlers for string fields such as hardware and firmware information.

Common read-only views include `features`, `manufacturer`, `hci_version`, `hci_revision`, `hardware_error`, `device_id`, `device_list`, `blacklist`, `blocked_keys`, `uuids`, `remote_oob`, `use_debug_keys`, `sc_only_mode`, `hardware_info`, and `firmware_info`. Common writable numeric attributes include `conn_info_min_age` and `conn_info_max_age`, with cross-field validation.

BR/EDR views include inquiry cache, link keys, device class, voice setting, SSP debug mode, minimum encryption key size, auto-accept delay, idle timeout, sniff interval bounds, and optional `force_bredr_smp` on controllers without BR/EDR Secure Connections. LE views include identity address/IRK/RPA, RPA timeout, random/static addresses, force-static-address, allow/resolving lists, IRKs, LTKs, connection interval/latency/supervision defaults, advertising channel and interval defaults, key-size bounds, auth payload timeout, `force_no_mitm`, and quirk toggles.

Basic files include `dut_mode` and optional `vendor_diag`. `hci_debugfs_create_conn()` creates a per-connection debugfs directory named by HCI handle.

## Control Flow

Show handlers generally acquire `hci_dev_lock()` when traversing mutable device lists or reading multi-field state. Key lists and blocked keys use `rcu_read_lock()` because the underlying lists are RCU-managed by `hci_core.c`. Data is formatted with seq-file helpers for multi-line files and `simple_read_from_buffer()` for boolean files.

Write handlers parse booleans with `kstrtobool_from_user()` or bounded `copy_from_user()` plus `kstrtobool()`, parse numeric values through `DEFINE_DEBUGFS_ATTRIBUTE()`, validate ranges and cross-field relationships, then update `struct hci_dev` fields under `hci_dev_lock()` or through HCI flag helpers. Some writes are gated by controller state: quirk toggles reject changes while `HCI_UP`, `force_static_address` rejects powered devices, and `dut_mode` requires an up device.

`dut_mode_write()` uses `hci_req_sync_lock()` and synchronous HCI commands to enable DUT mode or reset the controller when disabling, then toggles `HCI_DUT_MODE`. `vendor_diag_write()` either stores the desired flag for non-persistent diagnostic quirks while inactive/user-channel, or calls the driver `set_diag` callback under request sync lock before updating `HCI_VENDOR_DIAG`.

## State and Persistence Behavior

Debugfs files expose live in-memory `struct hci_dev` state and, in some cases, mutate defaults used by future HCI procedures. Values such as connection intervals, advertising intervals, sniff intervals, key-size bounds, RPA timeout, auth payload timeout, force flags, and diagnostic flags live only for the current device lifetime unless userspace applies them again. Secret material such as link keys, LTKs, IRKs, and OOB data is exposed through root-readable debugfs files, not persisted by this file.

The file creates debugfs entries under `hdev->debugfs`; recursive removal is handled by device/connection cleanup in other files. Per-connection directories are named from `conn->handle`, so unset or changed handles can affect debugfs naming decisions through creation timing.

## Dependencies and Integration Points

The file depends on debugfs, seq_file helpers generated by `DEFINE_SHOW_ATTRIBUTE`, `kstrtox`, `hci_core.h`, SMP helpers, and HCI flag/quirk helpers. It reads state maintained by `hci_core.c` and `hci_conn.c`, including discovery cache, key lists, OOB data, LE connection parameters, adv list sizes, identity address selection, and connection handles. It integrates with controller command paths through `__hci_cmd_sync()` for DUT mode and driver callbacks for vendor diagnostics.

## Risks and Edge Cases

The main security risk is exposure of pairing and identity material through debugfs. Permissions are mostly restrictive for secrets (`0400`), but debugfs is not intended for production policy boundaries. Write risks include changing live timing/security defaults while other operations are active; several handlers lock the device but do not issue controller reconfiguration themselves, so changes may apply only to subsequent operations. Cross-field validation prevents invalid min/max ordering for connection, advertising, sniff, and key-size bounds.

Concurrency risks are lower than protocol code but still present because debugfs reads race with device removal and list mutation. The code uses device locks or RCU for list traversal, and debugfs removal in release paths should prevent long-lived new opens after teardown. Handlers that call synchronous HCI commands must avoid deadlocks with existing request-sync work.

## Test Signals

Tests should verify debugfs creation by capability, permission modes for secret files, range validation for every writable numeric attribute, down/up gating for quirk and static-address writes, DUT mode command success and failure paths, vendor diagnostic callback behavior for persistent and non-persistent quirks, RCU-safe key/list output under concurrent updates, and absence of debugfs entries when `CONFIG_BT_DEBUGFS` is disabled. Runtime signals include file contents under `/sys/kernel/debug/bluetooth/hciX`, HCI command traces for DUT mode, driver `set_diag` callbacks, and error returns such as `-EINVAL`, `-EBUSY`, `-ENETDOWN`, and `-EALREADY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_debugfs.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/hci_debugfs.h

## Purpose

`hci_debugfs.h` is the debugfs integration boundary for the HCI core. It declares the debugfs creation functions used by core/setup code when Bluetooth debugfs support is enabled and provides no-op inline stubs when `CONFIG_BT_DEBUGFS` is disabled. This lets callers unconditionally invoke debugfs setup without scattering preprocessor checks through protocol code.

## Important APIs, Types, and Functions

When `IS_ENABLED(CONFIG_BT_DEBUGFS)` is true, the header declares:

- `hci_debugfs_create_common(struct hci_dev *hdev)`
- `hci_debugfs_create_bredr(struct hci_dev *hdev)`
- `hci_debugfs_create_le(struct hci_dev *hdev)`
- `hci_debugfs_create_conn(struct hci_conn *conn)`
- `hci_debugfs_create_basic(struct hci_dev *hdev)`

When debugfs is disabled, each function is defined as an empty `static inline` with the same signature. The header relies on prior visibility of `struct hci_dev` and `struct hci_conn`, normally supplied by `hci_core.h` or nearby Bluetooth headers in the including C file.

## Control Flow

There is no runtime control flow beyond compile-time selection. Enabled builds link to the implementations in `hci_debugfs.c`. Disabled builds compile calls away as empty inline functions. This pattern preserves call-site readability while eliminating runtime branches and object dependencies in non-debugfs configurations.

## State and Persistence Behavior

The header owns no state. Its compile-time branch determines whether debugfs entries are created at all. In disabled builds, no debugfs files, directories, or mutable debug knobs from `hci_debugfs.c` exist, and all related side effects are absent.

## Dependencies and Integration Points

The header depends on `CONFIG_BT_DEBUGFS` and Linux `IS_ENABLED()` semantics. It is included by `hci_core.c` and any setup path that wants to create debugfs files without direct preprocessor guards. It forms the ABI-like internal contract between HCI core code and the debugfs implementation.

## Risks and Edge Cases

The main risk is signature drift: implementations in `hci_debugfs.c`, enabled declarations, and disabled stubs must stay identical. If a call site depends on side effects from debugfs creation, that logic would silently disappear in non-debugfs builds, so debugfs functions must remain observational or diagnostic rather than required for protocol correctness.

## Test Signals

Build testing should cover both `CONFIG_BT_DEBUGFS=y/m` and disabled configurations. Enabled builds should link `hci_debugfs.c` and expose files; disabled builds should compile callers with no unresolved symbols and no debugfs behavior. Static analysis should flag any new debugfs creation function added to `hci_debugfs.c` but not represented in both header branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_drv.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/hci_drv.c

## Purpose

`hci_drv.c` implements a small driver-specific HCI pseudo-packet command layer. It lets code send `HCI_DRV_PKT` commands through the regular HCI send path and dispatch them to driver-provided common or driver-specific handlers, then lets handlers report command status or command completion back into the normal receive path as `HCI_DRV_PKT` events. This provides an internal command/event mechanism parallel to controller HCI commands without sending those packets to the physical controller.

## Important APIs, Types, and Functions

`hci_drv_cmd_status()` allocates an skb containing `struct hci_drv_ev_hdr` plus `struct hci_drv_ev_cmd_status`, fills the event opcode `HCI_DRV_EV_CMD_STATUS`, embeds the original command opcode and status byte, marks the skb as `HCI_DRV_PKT`, and injects it with `hci_recv_frame()`.

`hci_drv_cmd_complete()` similarly allocates an event skb for `HCI_DRV_EV_CMD_COMPLETE`, includes the original opcode, status, and optional return parameters, marks the packet type, and injects it through `hci_recv_frame()`.

`hci_drv_process_cmd()` is the dispatcher called by `hci_core.c` from `hci_send_frame()` when an outgoing skb has packet type `HCI_DRV_PKT`. It parses `struct hci_drv_cmd_hdr`, validates that the embedded length equals the remaining skb length, decodes OGF/OCF, selects a handler table from `hdev->hci_drv`, verifies handler existence and exact payload length, and invokes `handler->func(hdev, skb->data, len)`.

## Control Flow

Outgoing driver packets are intercepted before `hdev->send()` so they never reach the transport. `hci_drv_process_cmd()` first rejects malformed short headers or mismatched lengths with `-EILSEQ`. If the device has no `hci_drv` table, if the opcode does not map to an installed handler, or if the handler function is missing, it injects an unknown-command status event. If the payload length differs from `handler->data_len`, it injects an invalid-parameters status event. Only validated commands call the handler.

Handlers are responsible for their own semantics and may use `hci_drv_cmd_status()` or `hci_drv_cmd_complete()` to emit responses. Those responses enter the normal RX queue through `hci_recv_frame()`, preserving monitor/socket visibility and ordering semantics of other received packets.

## State and Persistence Behavior

This file stores no persistent state. It reads `hdev->hci_drv`, handler counts, and handler arrays from the device. Allocated response skbs are transient and owned by the receive path after successful injection. Command payload bytes are consumed directly from the outgoing skb after the header is pulled; the skb is freed by the caller in `hci_send_frame()` after dispatch returns.

## Dependencies and Integration Points

The file depends on `hci_drv.h` for packet header, event, status, and handler definitions; on `hci_core.h` for `struct hci_dev` and `hci_recv_frame()`; on Bluetooth skb helpers for packet typing; and on HCI opcode helpers for OGF/OCF decoding. Its primary integration point is `hci_core.c:hci_send_frame()`, which detects `HCI_DRV_PKT`, calls `hci_drv_process_cmd()`, frees the outgoing skb, and returns the handler result.

## Risks and Edge Cases

The dispatcher deliberately requires exact payload length, which protects handlers from short or overlong payloads but means handler metadata must stay synchronized with command definitions. Handler table indexing is split between common opcodes and `HCI_DRV_OGF_DRIVER_SPECIFIC` OCFs; incorrect OGF/OCF assignment will produce unknown-command events. Response allocation failures return `-ENOMEM` and no event is injected, so callers waiting for a response need timeout behavior. Because responses re-enter `hci_recv_frame()`, they require the device to be up or initializing just like other received frames.

## Test Signals

Tests should cover malformed command headers, length mismatch, missing `hci_drv`, unknown common opcode, unknown driver-specific OCF, invalid handler payload length, successful handler dispatch, command status response injection, command complete response with return parameters, and behavior when the HCI device is not up. Runtime signals include `HCI_DRV_PKT` monitor traces, handler return codes, injected command-status/complete events, and command timeout behavior if a handler fails to respond.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/hci_drv.c -->
