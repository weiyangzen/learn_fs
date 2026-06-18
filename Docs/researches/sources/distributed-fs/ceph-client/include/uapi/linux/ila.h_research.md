
# sources/distributed-fs/ceph-client/include/uapi/linux/ila.h

## Purpose

`ila.h` defines the generic-netlink UAPI for Identifier-Locator Addressing, including family metadata, attributes, commands, direction flags, checksum modes, identifier types, and hook types. The complete 68-line file was read.

## Important APIs, Types, and Functions

Constants include `ILA_GENL_NAME` and `ILA_GENL_VERSION`. Enums define `ILA_ATTR_*`, `ILA_CMD_ADD/DEL/GET/FLUSH`, checksum modes, address/identifier types, and route input/output hook types. Direction flags are `ILA_DIR_IN` and `ILA_DIR_OUT`.

## Control Flow

User space sends generic-netlink commands to add, delete, fetch, or flush ILA mappings. Kernel ILA code applies mappings at route input or output hooks and adjusts or preserves transport checksums according to the selected mode.

## State and Persistence Behavior

ILA locator/identifier mappings and hook configuration are kernel networking state. They persist until deleted or flushed.

## Dependencies and Integration Points

The header has no includes and integrates with generic netlink, IPv6 routing, checksum adjustment code, and user tooling for ILA.

## Risks and Edge Cases

Risks include checksum-neutral mapping errors, direction/hook mismatch, identifier type confusion, ifindex scoping, and generic-netlink attribute validation.

## Test Signals

ILA tests should cover add/get/delete/flush, input/output direction behavior, checksum modes, identifier types, invalid ifindex/attribute combinations, and packet checksum preservation.
