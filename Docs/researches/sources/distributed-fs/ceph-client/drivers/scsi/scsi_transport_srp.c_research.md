# sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_srp.c

## Purpose

`scsi_transport_srp.c` implements the SCSI RDMA Protocol transport class. It lets SRP low-level drivers publish remote target ports below a SCSI host, expose SRP-specific sysfs attributes, coordinate reconnect/fail-fast/device-loss policy, and integrate transport failures with SCSI target blocking and error handling.

## Important APIs, Types, and Functions

The private wrapper is `struct srp_internal`, which embeds `struct scsi_transport_template`, points at the low-level `struct srp_function_template`, and owns host/rport attribute containers. `struct srp_host_attrs` stores a per-host `next_port_id` counter in `Scsi_Host.shost_data`.

Exported APIs are `srp_tmo_valid()`, `srp_parse_tmo()`, `srp_start_tl_fail_timers()`, `srp_reconnect_rport()`, `srp_timed_out()`, `srp_rport_get()`, `srp_rport_put()`, `srp_rport_add()`, `srp_rport_del()`, `srp_remove_host()`, `srp_stop_rport_timers()`, `srp_attach_transport()`, and `srp_release_transport()`. Sysfs attributes expose `port_id`, `roles`, `state`, `reconnect_delay`, `failed_reconnects`, `fast_io_fail_tmo`, `dev_loss_tmo`, and optional `delete`.

## Control Flow

Module init registers `srp_host` and `srp_remote_ports` transport classes. `srp_attach_transport()` allocates the transport wrapper, selects attributes according to the function template, registers containers, and returns the embedded transport template. `srp_rport_add()` allocates an `srp_rport`, initializes mutex and delayed work, copies identifiers, sets timeout defaults, names the child device, and publishes it through the transport/device core. `srp_rport_del()` and `srp_remove_host()` remove rport devices.

Failure handling starts with `srp_start_tl_fail_timers()`: reconnect work may be queued, the rport can transition to `BLOCKED`, targets are blocked, and fail-fast/dev-loss delayed work is scheduled. `srp_reconnect_rport()` blocks target command queueing before calling the low-level `reconnect()` callback. On success it cancels timers, returns the port to `RUNNING`, unblocks targets, and restores offline sdevs to running. Fail-fast timeout moves a blocked port to `FAIL_FAST`, unblocks targets as transport-offline, and optionally terminates rport I/O. Dev-loss timeout moves the port to `LOST` and invokes the low-level delete callback.

## State and Persistence Behavior

Runtime state is held in rport devices: state, timeout fields, failed reconnect count, work items, and device references. `rport->mutex` serializes state transitions. Timeout sysfs writes mutate live policy and can queue or cancel reconnect work. `srp_tmo_valid()` prevents unusable combinations such as all recovery mechanisms disabled, zero reconnect delay, fail-fast beyond midlayer bounds, dev-loss jiffies overflow, and fail-fast greater than or equal to dev-loss.

## Dependencies and Integration Points

The file depends on the SCSI midlayer, SCSI transport classes, delayed work, driver-core devices, and `scsi_transport_srp.h`. Low-level SRP drivers integrate through `struct srp_function_template`; SCSI EH and timeout paths integrate through `srp_timed_out()`, `scsi_block_targets()`, and `scsi_target_unblock()`.

## Risks and Edge Cases

Timer teardown and state changes are the main risks. Delayed work cancellation must be sequenced during host teardown, and low-level `reconnect()` implementations must obey the documented synchronization contract because this layer blocks new queueing but does not drain outstanding commands. `store_reconnect_delay()` duplicates `cancel_delayed_work()` without a sync wait, which is harmless but worth noting. The helper `shost_to_rport()` warns if more than one rport child exists, reflecting an assumption about the host/rport topology.

## Test Signals

Test transport attach/release, rport add/delete, sysfs visibility for different function templates, timeout parsing and validation, reconnect success/failure/backoff, fail-fast and dev-loss expiry, `srp_timed_out()` behavior with timers disabled, and removal followed by `srp_stop_rport_timers()` while references are held.
