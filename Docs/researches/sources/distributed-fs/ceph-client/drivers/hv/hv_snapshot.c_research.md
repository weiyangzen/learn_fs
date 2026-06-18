<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_snapshot.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_snapshot.c

## Purpose

`hv_snapshot.c` implements the Hyper-V Volume Shadow Copy Service integration component. It negotiates VSS protocol with the host, forwards freeze/thaw/hot-backup operations to a userspace daemon, handles daemon registration and timeouts, and returns completion status to the host.

## Important APIs, Types, and Functions

- `vss_transaction` stores the single active host VSS transaction: state, receive buffer length, channel, request ID, and current `hv_vss_msg`.
- `hv_vss_onchannelcallback()` handles host VSS and negotiation messages.
- `vss_on_msg()` handles daemon writes through the utility transport.
- `vss_handle_request()`, `vss_send_op()`, and `vss_respond_to_host()` drive host-to-daemon-to-host request flow.
- `vss_timeout_func()` fails operations when userspace does not respond; freeze gets the longer `VSS_FREEZE_TIMEOUT`.
- `vss_handle_handshake()` supports legacy and reply-required daemon registration.
- `hv_vss_init()`, `hv_vss_init_transport()`, `hv_vss_pre_suspend()`, `hv_vss_pre_resume()`, and `hv_vss_deinit()` are consumed by `hv_util.c`.

## Control Flow

Initialization refuses hosts older than Win8.1, stores the utility receive buffer, sets the channel maximum packet size to two Hyper-V pages, and marks the transaction state waiting for daemon registration. Host callbacks ignore new packets while a transaction is active. Negotiation packets are answered directly with `vmbus_prep_negotiate_resp()`. VSS packets are length-checked, stored in `vss_transaction`, and processed in workqueue context. Freeze, thaw, and hot-backup operations require userspace; they transition to `HVUTIL_HOSTMSG_RECEIVED`, send an operation to the daemon, and arm a timeout. `GET_DM_INFO` is answered in-kernel.

Daemon replies enter `vss_on_msg()`. Registration messages are accepted only outside an active transaction. Operation replies are accepted only after a userspace request was sent; the code updates hot-backup flags when requested, cancels timeout, responds to the host, and polls the channel again. Suspend sends a best-effort fake THAW to userspace after cancelling pending work so filesystems are not left frozen.

## State and Persistence Behavior

Like KVP, VSS relies on one global active transaction. `recv_buffer` is shared with `hv_util.c`, while `hvt` owns the daemon transport. `dm_reg_value` records daemon protocol. Delayed and normal work items persist and are cancelled on reset, suspend, or deinit. State is forced to ready during suspend so later daemon writes fail and force daemon reset instead of completing stale host work.

## Dependencies and Integration Points

This file integrates with `hv_util.c`, `hv_utils_transport.c`, VMBus packet APIs, Hyper-V VSS structures from `<linux/hyperv.h>`, and the userspace `hv_vss_daemon`. It uses the VSS GUID service entry in the utility driver.

## Risks and Edge Cases

The freeze timeout is long because host expectations require it, so hung userspace can delay host-visible completion. Correct thaw-on-suspend behavior is critical to avoid leaving filesystems frozen. Host packets must fit `VSS_MAX_PKT_SIZE`; this is tied to structure comments in Hyper-V headers. Transport reset or daemon restart fails active host transactions.

## Test Signals

Test protocol negotiation, daemon registration modes, freeze/thaw/hot-backup success and timeout, `GET_DM_INFO`, daemon reset mid-transaction, suspend fake thaw, resume tasklet re-enable, unsupported old host versions, and packet length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_snapshot.c -->
