# sources/distributed-fs/ceph-client/drivers/greybus/svc.c

## Purpose

`svc.c` implements the Greybus SVC protocol device, the management channel responsible for initial protocol negotiation, HELLO, module hotplug events, interface power/route/connection operations, UniPro DME access, pwrmon diagnostics, watchdog sysfs controls, and deferred hotplug processing.

## Important APIs, Types, and Functions

- `gb_svc_create()`, `gb_svc_add()`, `gb_svc_del()`, and `gb_svc_put()` manage SVC device and static connection lifetime.
- Management operations include `gb_svc_intf_device_id()`, `gb_svc_intf_eject()`, VSYS/REFCLK/UniPro setters, `gb_svc_intf_activate()`, `gb_svc_intf_resume()`, DME get/set, connection create/destroy, route create/destroy, power mode setters, and `gb_svc_ping()`.
- Pwrmon functions query rail count/names and rail/interface samples, feeding debugfs and interface sysfs measurements.
- `gb_svc_request_handler()` enforces RESET -> PROTOCOL_VERSION -> SVC_HELLO ordering and dispatches incoming SVC requests.
- `gb_svc_queue_deferred_request()` moves mutating hotplug work to an ordered SVC workqueue.
- Deferred processors handle HELLO power-mode workaround, module inserted/removed, interface oops, and mailbox events.

## Control Flow

Host-device creation creates a static SVC connection on `GB_SVC_CPORT_ID`; `gb_svc_add()` enables that connection. The remote SVC first sends protocol version, then HELLO. HELLO records `endo_id` and AP interface ID, registers the SVC device, creates/enables watchdog, queues deferred link power reconfiguration, and initializes debugfs. Later module and interface events are validated in the request handler and deferred so the operation response can complete while the ordered workqueue mutates module/interface state.

Management helper functions build protocol request/response structures, call `gb_operation_sync()` or timeout variants, convert little-endian fields, and map SVC status/result codes to Linux errnos. SVC deletion disables RX, removes debugfs/watchdog/device if registered, flushes deferred work, removes modules, and disables the SVC connection.

## State and Persistence Behavior

`struct gb_svc` stores host pointer, static connection, protocol state, endo/AP IDs, device-ID allocator, ordered workqueue, watchdog pointer, watchdog action, debugfs state, and pwrmon rail metadata. Incoming SVC state progression is serialized by the connection request path. Deferred requests hold operation references until their work item completes.

## Dependencies and Integration Points

This file integrates with Greybus operations, static connections, module/interface lifecycle, SVC watchdog, debugfs root, pwrmon sysfs/debugfs readers, Linux IDA, ordered workqueues, and SVC protocol structures from `greybus_protocols.h`.

## Risks and Edge Cases

- The request handler depends on serialized incoming requests for `svc->state`; changes to connection workqueue ordering would affect this.
- HELLO registers the device from a request handler, so teardown must handle partially registered SVC devices.
- Module hotplug list operations are not guarded by an explicit host module-list lock here; ordering relies on the SVC workqueue and broader lifecycle serialization.
- Several destroy operations log but ignore remote errors, which is appropriate for teardown but can hide hardware state drift.
- `gb_svc_intf_set_power_mode()` reads `response.result_code` without endian conversion, while related helpers use little-endian conversion; this should be reviewed against the protocol field type.
- Debugfs rail names are copied into fixed buffers from firmware-provided data and should be treated as untrusted diagnostics.

## Test Signals

Test protocol-order enforcement, version negotiation, HELLO registration failures, watchdog create failure, SVC deletion before HELLO, module insertion/removal ordering, duplicate/unexpected module events, interface oops and mailbox handling, each management operation's status/error mapping, pwrmon rail-count/names/sample paths, debugfs cleanup, deferred work flush, and SVC ping failures.
