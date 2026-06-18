# sources/distributed-fs/ceph-client/net/nfc/core.c

## Purpose

`core.c` is the NFC subsystem device and lifecycle manager. It allocates/registers NFC devices, controls device up/down and polling, manages targets and secure elements, coordinates DEP links and target-mode activation, integrates rfkill, emits generic netlink notifications, owns presence checking timers, and initializes the NFC core module.

## Important APIs, Types, and Functions

Device lifecycle APIs include `nfc_allocate_device()`, `nfc_register_device()`, `nfc_unregister_rfkill()`, `nfc_remove_device()`, `nfc_unregister_device()`, and the release path `nfc_release()`. Operational APIs include `nfc_fw_download()`, `nfc_dev_up()`, `nfc_dev_down()`, `nfc_start_poll()`, `nfc_stop_poll()`, `nfc_activate_target()`, `nfc_deactivate_target()`, `nfc_data_exchange()`, `nfc_dep_link_up()`, `nfc_dep_link_down()`, and `nfc_dep_link_is_up()`.

Target and SE APIs include `nfc_targets_found()`, `nfc_target_lost()`, `nfc_add_se()`, `nfc_remove_se()`, `nfc_enable_se()`, `nfc_disable_se()`, `nfc_se_transaction()`, and `nfc_se_connectivity()`. Target mode and LLCP hooks include `nfc_tm_activated()`, `nfc_tm_deactivated()`, `nfc_tm_data_received()`, `nfc_set_remote_general_bytes()`, and `nfc_get_local_general_bytes()`.

## Control Flow

`nfc_init()` registers the NFC class, generic netlink interface, raw sockets, LLCP, and PF_NFC socket family in that order. Device allocation validates required driver operations, allocates an ID from `nfc_index_ida`, initializes a class device, stores driver ops/protocols/headroom, initializes generic netlink per-device data, secure-element list, target generation, and optional presence timer/work.

Most operations take `device_lock(&dev->dev)`, reject `shutting_down`, and enforce state transitions. `nfc_dev_up()` checks rfkill and firmware download state before calling driver `dev_up` and optionally discovering secure elements. Polling starts only when the device is up and not already polling, calls driver `start_poll`, and records polling state. Target discovery from drivers assigns target IDs, replaces the target array, bumps generation, clears polling, and sends generic netlink notifications.

Initiator data exchange verifies the active target, pauses presence checking around driver `im_transceive`, and restores the timer. Target mode sends through `tm_send`. DEP link-up obtains LLCP general bytes, calls driver `dep_link_up`, and later `nfc_dep_link_is_up()` marks state and notifies LLCP/genl. Unregister first marks rfkill/shutdown and notifies userspace, then cancels timers/work, unregisters LLCP, removes the device, and release frees targets, secure elements, genl data, IDA ID, and the device.

## State and Persistence Behavior

Persistent device state includes `dev_up`, `polling`, `active_target`, `dep_link_up`, `rf_mode`, target array and generation, secure-element list and state, rfkill pointer, firmware-download flag, `shutting_down`, and optional presence timer/work. Global state includes `nfc_devlist_generation`, `nfc_devlist_mutex`, `nfc_index_ida`, and the exported `nfc_class`.

Targets are replaced as a batch on discovery and compacted on loss. Secure elements are list entries owned by the device. Presence checking periodically calls driver `check_presence` and emits target-lost notifications on failure.

## Dependencies and Integration Points

The core depends on rfkill, the device model, generic netlink NFC notifications, LLCP, raw sockets, PF_NFC sockets, skbuff allocation helpers, IDA, timers, and driver-provided `struct nfc_ops`. Digital, NCI, HCI, and hardware drivers call into these exported APIs.

## Risks and Edge Cases

State transitions rely on `device_lock`; driver callbacks must not call back in ways that deadlock. Presence timers must be deleted around transceive/deactivate/unregister. Firmware download, rfkill, polling, and active target state are mutually constrained. `nfc_targets_found()` must not be called from atomic context but uses `GFP_ATOMIC` for target duplication. Shutdown ordering must prevent userspace notifications or LLCP callbacks after device removal.

## Test Signals

Use NFC generic netlink commands for device add/remove, up/down, polling, target discovery/loss, DEP link up/down, secure element add/remove/enable/disable, rfkill block/unblock, and firmware download completion. Driver fault injection should cover `check_presence`, polling errors, and unregister during active work.
