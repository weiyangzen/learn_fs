# sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_fc.c

## Purpose

`scsi_transport_fc.c` implements the Linux SCSI Fibre Channel transport class. It provides the shared transport layer between FC low-level drivers and the SCSI midlayer: host, target, remote-port, and virtual-port class devices; sysfs attributes; FC event netlink notification; FPIN statistics; remote-port loss/recovery state machines; SCSI scan integration; error-handler blocking helpers; and BSG passthrough queues for FC ELS/CT/vendor requests.

This file is infrastructure, not a concrete adapter driver. Low-level drivers attach by passing a `struct fc_function_template` to `fc_attach_transport()`, then use exported service functions such as `fc_remote_port_add()`, `fc_remote_port_delete()`, `fc_remote_port_rolechg()`, `fc_remove_host()`, and `fc_vport_create()` to report topology and NPIV changes.

## Important APIs, Types, and Data

- `struct fc_internal` wraps `struct scsi_transport_template`, the driver-supplied `struct fc_function_template`, and per-object sysfs attribute arrays/containers for SCSI targets, FC hosts, FC remote ports, and FC virtual ports.
- `fc_dev_loss_tmo` is a module parameter and host default for how long a missing remote port remains insulated before target removal or binding preservation.
- The transport classes are `fc_host_class`, `fc_vport_class`, `fc_rport_class`, and `fc_transport_class`; module init registers them and exit unregisters them.
- `fc_attach_transport()` allocates/configures the transport template, conditionally exposes sysfs attributes based on `fc_function_template` callbacks, registers transport containers, and installs `fc_user_scan()` as the user scan hook.
- `fc_release_transport()` unregisters the containers and frees `struct fc_internal`.
- Exported topology APIs include `fc_remote_port_add()`, `fc_remote_port_delete()`, `fc_remote_port_rolechg()`, `fc_find_rport_by_wwpn()`, `fc_vport_create()`, `fc_vport_terminate()`, and `fc_remove_host()`.
- Exported event/error APIs include `fc_get_event_number()`, `fc_host_post_fc_event()`, `fc_host_post_event()`, `fc_host_post_vendor_event()`, `fc_host_fpin_rcv()`, `fc_eh_timed_out()`, `fc_block_rport()`, `fc_block_scsi_eh()`, and `fc_eh_should_retry_cmd()`.
- Internal state is stored in `struct fc_host_attrs`, `struct fc_rport`, `struct fc_vport`, and `struct fc_starget_attrs` via helpers/macros from `scsi_transport_fc.h`.

## Sysfs and Attribute Surface

The file uses macros to define repeated sysfs show/store functions for hosts, SCSI targets, rports, and vports. Driver-backed attributes call optional `fc_function_template` getters/setters before formatting values. Transport-owned attributes expose and modify internal state directly.

Host attributes include WWNs, FC4 lists, supported speeds/classes, model/version strings, port ID/type/state, fabric name, symbolic name, `system_hostname`, target binding type, `dev_loss_tmo`, `issue_lip`, NPIV counts, vport create/delete shortcuts, and statistics. Remote-port attributes include WWNs, port ID, roles, port state, SCSI target ID, `dev_loss_tmo`, `fast_io_fail_tmo`, encryption status, and FPIN statistics. Virtual-port attributes include state, last state, WWNs, roles, type, symbolic name, delete, and disable controls. SCSI target attributes mirror WWNs and port ID, either from the parent rport or old-style driver callbacks.

Important validation rules are embedded in stores: `dev_loss_tmo` parses as an unsigned long and is capped when `fast_io_fail_tmo` is off; `fast_io_fail_tmo` accepts `off` or a positive value less than `dev_loss_tmo`; rport `port_state` sysfs allows only Online/Marginal transitions; vport WWNs must be exactly sixteen hex digits per name in `WWPN:WWNN` form.

## Control Flow and Lifecycle

Module initialization registers transport classes in dependency order. Host setup initializes all FC host attributes to known invalid/default values, initializes rport/vport lists and counters, creates a per-host workqueue, inherits the module `dev_loss_tmo`, and tries to create the host BSG queue. Host removal tears down the BSG queue but the driver is expected to call `fc_remove_host()` before `scsi_remove_host()` to remove transport-owned objects safely.

Remote-port creation flows through `fc_remote_port_add()`. It first flushes host work, searches blocked/not-present active rports for a binding match, then searches the preserved binding list when binding is enabled. A reused rport has identifiers refreshed, driver private data cleared, devloss timers cancelled as appropriate, SCSI targets unblocked and rescanned when it is still a target, and BSG queues restarted. If no binding exists, `fc_remote_port_create()` allocates the rport, initializes timers/work items, assigns a transport number and possibly a SCSI target ID, adds the class device, adds BSG support, and queues a target scan for FCP target roles.

Remote-port deletion is deliberately delayed. `fc_remote_port_delete()` moves online/marginal ports to `FC_PORTSTATE_BLOCKED`, blocks SCSI targets, schedules optional fast-I/O-fail work, and schedules devloss work. `fc_timeout_fail_rport_io()` marks fast failure and unblocks/fails queued I/O. `fc_timeout_deleted_rport()` either no-ops if the port returned, removes non-target or unbound ports, or moves target rports to `rport_bindings`, marks them `NOTPRESENT`, clears non-binding identifiers, queues SCSI target deletion, and invokes the driver `dev_loss_tmo_callbk()` once. `fc_rport_final_delete()` handles complete teardown: terminates I/O, flushes pending scans/timers, deletes SCSI descendants, invokes devloss callback if needed, removes BSG, destroys devloss workqueue, removes transport devices, and drops references.

Role changes via `fc_remote_port_rolechg()` may allocate a SCSI target ID when a port becomes an FCP target, cancel devloss timers, unblock the target, and schedule a rescan. Scans are performed by `fc_scsi_scan_rport()` only for online/marginal FCP target rports unless the driver disables target scanning.

Virtual-port creation flows through `fc_vport_setup()`. It validates driver support and NPIV capacity, allocates the vport plus optional driver private data, adds it to the host vport list, creates a class device under the chosen parent, invokes the driver `vport_create()` callback, optionally creates a symlink from the physical shost, then clears the `CREATING` flag. Deletion through sysfs or API marks `DELETING`, calls the driver `vport_delete()`, removes the object from lists and sysfs/transport, decrements NPIV usage, and drops references.

## State and Persistence Behavior

The most important persistent-in-memory behavior is target ID binding. While a SCSI host remains attached, rports that represented FCP targets can preserve their `scsi_target_id` across fabric disappearance and return. Binding can be by WWPN, WWNN, FC address, or disabled. When a remote port exceeds `dev_loss_tmo`, target objects are removed but the rport may remain on `fc_host->rport_bindings` with only the binding identifier retained. Changing `tgtid_bind_type` purges unused consistent bindings by moving them to deleted state and queuing final deletion.

State is protected mainly by `shost->host_lock` around rport/vport lists, flags, target ID counters, and port state transitions. Device lifetime uses class-device self references, parent references, `scsi_host_get()/put()`, and release callbacks that free rport/vport memory. Workqueues carry asynchronous deletion, scan, and timeout paths. There is no on-disk persistence; all binding and transport state is scoped to the lifetime of the SCSI host.

## Events, FPIN, and Statistics

`fc_get_event_number()` uses an atomic sequence for FC netlink events. `fc_host_post_fc_event()` builds an `fc_nl_event` skb and multicasts to `SCSI_NL_GRP_FC_EVENTS`; convenience wrappers handle basic and vendor events. If netlink allocation or socket state fails, it logs a dropped event warning.

`fc_host_fpin_rcv()` parses Fabric Performance Impact Notification TLVs, updates host or matching rport `struct fc_fpin_stats` counters for link integrity, delivery, peer congestion, and congestion descriptors, then posts the FPIN payload as a netlink event. The parsing loop bounds itself by both provided payload length and FPIN descriptor length, using TLV header/length helpers.

Host statistics are exposed through a `statistics` sysfs group when the driver supplies `get_fc_host_stats()`. The file also exposes transport-maintained FPIN counters for hosts and rports and supports a driver-backed reset hook.

## BSG Integration

When a driver supplies `bsg_request`, `fc_bsg_hostadd()` creates a host BSG queue named `fc_hostN`; `fc_bsg_rportadd()` creates per-rport queues named after the rport device. Queue limits are initialized from SCSI host limits and capped by `max_bsg_segments`; private BSG data size comes from `dd_bsg_size`.

Dispatch validates request length, message code, payload direction requirements, and host vendor IDs before calling the driver. Host commands include add/delete rport, ELS without login, CT, and vendor requests. Rport commands include ELS and CT. Rport dispatch has an extra prep stage that returns resource pressure while a port is blocked but not fast-failed, I/O error for unavailable states, and success for online/marginal rports. Timeout handling resets the timer for blocked rports, invokes optional driver abort handling, and ends timed-out requests with I/O error when needed.

## Dependencies and Integration Points

This file depends on the SCSI midlayer (`scsi_host`, `scsi_device`, `scsi_target`, scan/remove/block helpers), the generic transport class framework, Linux device model/sysfs, workqueues and delayed work, blk-mq/BSG library, SCSI netlink, FC UAPI ELS/FPIN structures, and low-level FC driver callbacks in `struct fc_function_template`.

Integration with drivers is callback-heavy. Drivers choose which sysfs attributes exist by setting `show_*`, `get_*`, `set_*`, vport, stats, BSG, timeout, devloss, and scan-control callbacks. Drivers also own transport-specific private areas sized by `dd_fcrport_size`, `dd_fcvport_size`, and `dd_bsg_size`.

Integration with SCSI error handling is explicit: `fc_eh_timed_out()` asks the midlayer to reset command timers while an rport is blocked; `fc_block_rport()` and `fc_block_scsi_eh()` make driver EH callbacks wait for unblock or fast fail; `fc_eh_should_retry_cmd()` maps marginal transport state to `DID_TRANSPORT_MARGINAL` for failfast requests.

## Risks and Edge Cases

- Lifecycle ordering is fragile: the file itself warns that drivers must call `fc_remove_host()` before `scsi_remove_host()` or stale `/sys/class/fc_remote_ports` objects can crash the system.
- Several sysfs string store helpers inspect `buf[count - 1]` without an explicit zero-count check; sysfs writes normally provide nonzero count, but malformed internal use would be risky.
- `fc_user_scan()` initializes target bounds once; with wildcard channels, the inner target loop is not reset per channel, so only the first channel iterates the full target range unless surrounding assumptions prevent multi-channel use.
- FPIN stats updates locate rports by WWPN under lock but then update counters without taking a dedicated rport lock; this matches the file's lightweight stats style but can race with concurrent reads/updates.
- Workqueue/timer cancellation relies on port state rechecks after flushes. Correctness depends on every async path honoring `port_state` and `FC_RPORT_*` flags.
- Target ID binding preserves driver hostdata when saving bindings, intentionally pushing responsibility for private state validity to the low-level driver.
- BSG validation checks minimum command sizes and payload presence but delegates semantic validation and transport completion discipline to the driver callback.
- `fc_bsg_remove()` simply passes the queue to `bsg_remove_queue()`; callers set queues to `NULL` before successful setup but do not always clear after removal, so repeated teardown assumptions depend on BSG helper tolerance and caller lifecycle.

## Test Signals

Useful validation signals include successful registration/unregistration of all four transport classes; host attach/release with the expected sysfs attributes for different `fc_function_template` capability combinations; rport add/delete/re-add tests for each target binding mode; devloss and fast-I/O-fail timeout behavior; SCSI target scans and removals under online, marginal, blocked, not-present, and deleted rport states; `fc_eh_timed_out()` timer reset behavior for blocked ports; `fc_block_scsi_eh()` returning `FAST_IO_FAIL` after fast timeout; vport create/delete/disable sysfs paths including NPIV capacity checks; BSG command validation and timeout behavior; netlink FC event delivery and dropped-event logging; FPIN TLV parsing with host/rport statistic increments; and cleanup behavior from `fc_remove_host()` with pending scans, timers, vports, active rports, and preserved bindings.
