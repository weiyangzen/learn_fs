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
