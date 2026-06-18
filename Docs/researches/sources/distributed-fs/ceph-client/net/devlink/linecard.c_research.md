# sources/distributed-fs/ceph-client/net/devlink/linecard.c

## Purpose

`linecard.c` implements devlink linecard objects, including creation, user-visible state reporting, provisioning and unprovisioning, active/inactive transitions, supported type discovery, notifications, and optional nested devlink attachment.

## Important APIs, Types, and Functions

The private `struct devlink_linecard` stores devlink pointer, index, ops, private pointer, state, state lock, current type, supported types, and nested relationship index. Exported APIs include `devlink_linecard_index()`, `devl_linecard_create()`, `devl_linecard_destroy()`, `devlink_linecard_provision_set()`, `devlink_linecard_provision_clear()`, `devlink_linecard_provision_fail()`, `devlink_linecard_activate()`, `devlink_linecard_deactivate()`, and `devlink_linecard_nested_dl_set()`. Netlink handlers are `devlink_nl_linecard_get_doit()`, dumpit, and set.

## Control Flow

Drivers create linecards under the devlink lock, providing ops for provision, unprovision, type count, and type get. Creation snapshots supported types and links the linecard. GET serializes index, state, current type, supported types, and nested devlink handle. SET with a non-empty type validates the linecard is not transitioning, checks type support, moves to PROVISIONING, notifies, drops the state lock while calling driver `provision()`, and rolls back to UNPROVISIONED on synchronous failure. SET with an empty type moves through UNPROVISIONING and calls driver `unprovision()`, with special handling for PROVISIONING_FAILED and already-unprovisioned states. Drivers later call provision/activation helpers for asynchronous completion.

## State and Persistence Behavior

Linecard state persists in `devlink->linecard_list`. `state_lock` protects `state` and `type`; the broader devlink lock protects list membership. Supported type strings and private type pointers are captured at creation. Nested devlink relationships persist by relationship index and are cleaned when the nested object disappears.

## Dependencies and Integration Points

The file uses devlink generic netlink, notification helpers, and relationship support from `core.c`. Driver callbacks implement hardware-specific provisioning. Register/unregister fanout in `dev.c` emits linecard notifications for existing objects.

## Risks

State transitions are asynchronous-friendly but require drivers to call completion helpers consistently. `devlink_linecard_nested_dl_set()` always adds a relationship and does not directly handle `NULL` despite the comment mentioning detach, so caller expectations should be checked against current implementation. Failure paths assume unprovisioned future state. Notifications require registered devlink state and can be missed if listeners attach after transitions.

## Test Signals

Test duplicate linecard indexes, unsupported types, same-provision success, provision/unprovision busy states, synchronous provision failure rollback, asynchronous provision set/fail/clear, activate/deactivate warnings, dump continuation across multiple linecards, and nested devlink handle notification/cleanup.
