
# sources/distributed-fs/ceph-client/include/uapi/linux/ioam6_genl.h

## Purpose

`ioam6_genl.h` defines the IPv6 IOAM generic-netlink UAPI for namespaces, schemas, schema binding, and trace events. The complete 72-line file was read.

## Important APIs, Types, and Functions

Constants include `IOAM6_GENL_NAME`, `IOAM6_GENL_VERSION`, `IOAM6_MAX_SCHEMA_DATA_LEN`, and event multicast group `IOAM6_GENL_EV_GRP_NAME`. Enums define namespace/schema attributes, commands `ADD/DEL/DUMP_NAMESPACE`, `ADD/DEL/DUMP_SCHEMA`, `NS_SET_SCHEMA`, event types, and trace event attributes.

## Control Flow

User space manages IOAM namespaces and schemas through generic-netlink commands. Kernel IOAM code emits trace events with namespace, nodelen, trace type, and binary trace data through the event group.

## State and Persistence Behavior

Namespaces, schema data, and namespace-to-schema bindings are kernel IOAM state. They persist until deleted or reconfigured.

## Dependencies and Integration Points

The header has no includes and integrates with generic netlink, `ioam6.h` trace formats, IPv6 IOAM packet processing, and observability tooling.

## Risks and Edge Cases

Schema binary data length is bounded by `255 * 4`. Risks include namespace ID collisions, schema deletion while referenced, event payload sizing, and generic-netlink attribute validation.

## Test Signals

Generic-netlink tests should add/delete/dump namespaces and schemas, bind schemas to namespaces, reject oversized schema data, and verify trace event attributes.
