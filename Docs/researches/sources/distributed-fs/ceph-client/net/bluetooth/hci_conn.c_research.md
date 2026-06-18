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
