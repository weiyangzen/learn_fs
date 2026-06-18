# sources/distributed-fs/ceph-client/net/devlink/dpipe.c

## Purpose

`dpipe.c` implements devlink's data-path pipeline introspection support. It lets drivers register hardware pipeline headers and tables, expose table matches/actions/entries over netlink, control table counters, and associate tables with devlink resources.

## Important APIs, Types, and Functions

The file exports global header descriptors `devlink_dpipe_header_ethernet`, `devlink_dpipe_header_ipv4`, and `devlink_dpipe_header_ipv6`. Exported helpers include `devlink_dpipe_match_put()`, `devlink_dpipe_action_put()`, `devlink_dpipe_entry_ctx_prepare()`, `devlink_dpipe_entry_ctx_append()`, `devlink_dpipe_entry_ctx_close()`, `devlink_dpipe_entry_clear()`, `devl_dpipe_headers_register()`, `devl_dpipe_headers_unregister()`, `devlink_dpipe_table_counter_enabled()`, `devl_dpipe_table_register()`, `devl_dpipe_table_unregister()`, and `devl_dpipe_table_resource_set()`. Netlink handlers include table get, entries get, headers get, and table counters set.

## Control Flow

Drivers register headers and tables under the devlink lock. Table GET walks the table list, asks each table op for size, matches, and actions, and sends multipart replies when the skb fills. Entries GET finds a named table and delegates entry generation to driver `entries_dump()`, using a dump context that drivers prepare, append entries into, and close. Header GET serializes registered header fields. Counter SET finds a table, rejects externally controlled counters, toggles `counters_enabled`, and calls `counters_set_update()` if supplied.

## State and Persistence Behavior

Persistent state is stored on `struct devlink`: `dpipe_headers` and the RCU-protected `dpipe_table_list`. Each `struct devlink_dpipe_table` stores name, ops, private driver pointer, counter state, optional resource ID/units, and whether counters are externally controlled. Entry values allocated by drivers are cleaned by `devlink_dpipe_entry_clear()`.

## Dependencies and Integration Points

The implementation uses generic netlink attribute construction, devlink handles from `devl_internal.h`, RCU list traversal, and driver-supplied `devlink_dpipe_table_ops`. Resource linkage lets devlink resource accounting describe table capacity.

## Risks

Multipart reply code must handle `-EMSGSIZE` without duplicating or skipping tables/headers. Table lookup mixes lockdep-protected and RCU traversal, so unregister requires RCU free. Driver `entries_dump()` must use the context protocol correctly or replies can be malformed. Counter toggles affect future driver table entries and must not race with hardware updates outside the devlink lock.

## Test Signals

Test header and table registration/unregistration, duplicate table names, table and entry dumps with small skb forcing multipart output, counter enable/disable with and without external control, resource association, entry clear freeing values and masks, and drivers with absent optional ops.
