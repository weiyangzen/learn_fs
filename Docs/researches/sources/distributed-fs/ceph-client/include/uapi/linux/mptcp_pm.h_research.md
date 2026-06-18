# sources/distributed-fs/ceph-client/include/uapi/linux/mptcp_pm.h

## Purpose
Defines the auto-generated generic netlink ABI for the MPTCP path manager: family metadata, event types, address/subflow/endpoint attributes, command attributes, event attributes, and command IDs.

## Important APIs, Types, And Functions
Exports `MPTCP_PM_NAME`, `MPTCP_PM_VER`, `mptcp_event_type`, `MPTCP_PM_ADDR_ATTR_*`, `MPTCP_SUBFLOW_ATTR_*`, `MPTCP_PM_ENDPOINT_ADDR`, `MPTCP_PM_ATTR_*`, `mptcp_event_attr`, and `MPTCP_PM_CMD_*`.

## Control Flow
Userspace sends generic netlink commands to add/delete/get/flush endpoints, set/get limits, set flags, announce/remove addresses, and create/destroy subflows. Kernel sends events for connection creation, establishment, close, address announcement/removal, subflow establishment/close/priority, and listener lifecycle.

## State, Persistence, And Dependencies
State persists in MPTCP path-manager endpoint tables, per-connection tokens, limits, and active subflows. The header is generated from a netlink YAML spec.

## Integration Points
Used by `ip mptcp`, MPTCP daemons, tests, and monitoring agents subscribing to command and event multicast groups defined in `mptcp.h`.

## Risks
Auto-generated numeric IDs are ABI; changing them breaks netlink clients. Events have optional attributes and gaps in numbering, so parsers must tolerate missing fields and sparse event values.

## Test Signals
Check YNL spec conformance, command round trips, event multicast delivery, endpoint address nesting, subflow token reporting, limits update, and unknown attribute tolerance.
