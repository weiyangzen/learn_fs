# sources/distributed-fs/ceph-client/net/nfc/netlink.c

## Purpose

This file is the NFC generic-netlink control and event plane. It exposes device, target, LLCP, firmware, secure element, DEP link, polling, and vendor command operations to user space, and emits multicast events when NFC device state changes.

## Important APIs, Types, and Functions

The core object is `nfc_genl_family`, configured with `nfc_genl_policy`, one multicast event group, and `nfc_genl_ops[]`. Command handlers include `nfc_genl_get_device()`, `nfc_genl_dev_up()`, `nfc_genl_dev_down()`, `nfc_genl_start_poll()`, `nfc_genl_stop_poll()`, target activation/deactivation, DEP link up/down, LLCP parameter get/set and SDP request, firmware download, secure element enable/disable/get/IO, and vendor command dispatch.

Event helpers include `nfc_genl_targets_found()`, `nfc_genl_target_lost()`, `nfc_genl_device_added()`, `nfc_genl_device_removed()`, `nfc_genl_dep_link_up_event()`, `nfc_genl_dep_link_down_event()`, target-mode activated/deactivated events, LLCP service discovery responses, secure element add/remove/transaction/connectivity events, and firmware-download completion.

Vendor support is built around `nfc_genl_vendor_cmd()`, `__nfc_alloc_vendor_cmd_reply_skb()`, and `nfc_vendor_cmd_reply()`, using `dev->cur_cmd_info` to route replies to the triggering request.

## Control Flow

Request handlers parse required attributes, obtain `struct nfc_dev` with `nfc_get_device()`, call the NFC core operation, then put the device. Operations that mutate polling ownership use `dev->genl_data.genl_data_mutex`; target and LLCP operations often take `device_lock(&dev->dev)`. Dump operations retain iteration state in `netlink_callback->args`, use device generation counters for consistency, and release references in `.done` callbacks.

Multicast event helpers allocate a netlink skb, emit command-specific attributes, end the generic-netlink message, then multicast on the NFC family event group. Secure element IO is asynchronous: the request allocates `se_io_ctx`, validates device/up/SE state in `nfc_se_io()`, passes a callback to the driver, and `se_io_cb()` later multicasts APDU output and frees the context.

The netlink notifier listens for `NETLINK_URELEASE`. If the process that started polling disappears, scheduled work iterates NFC devices and stops polling for matching `poll_req_portid`.

## State and Persistence

Persistent kernel state lives mostly in `struct nfc_dev`: device index, target arrays/generation, polling state, DEP state, secure element list, vendor command table, and `genl_data.poll_req_portid`. This file initializes and destroys only the per-device generic-netlink mutex and tracks no durable storage.

## Dependencies and Integration Points

The file depends on generic netlink, public NFC uapi definitions, the local NFC core header, and LLCP internals. It is the user-space ABI endpoint for NFC daemons and tools. It also bridges vendor driver callbacks and NFC core functions such as `nfc_start_poll()`, `nfc_activate_target()`, `nfc_fw_download()`, and `nfc_enable_se()`.

## Risks and Edge Cases

Many operations intentionally use relaxed legacy validation flags, so per-command attribute checks are the main protection. Poll ownership is tied to netlink portid; incorrect cleanup could leave polling active. LLCP SDP request building must free partial TLV lists on all errors. Vendor replies depend on `dev->cur_cmd_info` being set only during command execution. Event allocation failures generally drop events with `-ENOMEM` or `-EMSGSIZE`, so userspace must tolerate missed notifications.

## Test Signals

Exercise each command with missing, malformed, and valid attributes; verify admin-only flags for mutating commands; test dumps across multiple devices/targets/secure elements; test poll start then netlink socket release; validate LLCP parameter bounds and SDP nested parsing; test SE IO callback success and error paths; verify vendor command dispatch/reply and unsupported vendor returns.
