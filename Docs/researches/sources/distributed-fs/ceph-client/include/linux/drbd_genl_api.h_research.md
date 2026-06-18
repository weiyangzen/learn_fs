# sources/distributed-fs/ceph-client/include/linux/drbd_genl_api.h

## Purpose
This header defines the DRBD-specific generic-netlink family header and wires the DRBD schema into the generic netlink macro generator.

## Important APIs, types, and functions
`struct drbd_genlmsghdr` carries `minor` plus a union of request `flags` and reply `ret_code`. `DRBD_GENL_F_SET_DEFAULTS` is the current request flag. `enum drbd_state_info_bcast_reason` defines status reply, state change, helper pre/post, and sync-progress reasons. Generator configuration macros define the family version, family name, header size, and include file before including `linux/genl_magic_struct.h`.

## Control flow, state, and persistence
The header has no runtime logic, but it defines the fixed family header prepended to DRBD generic-netlink messages. The `minor` field selects a device unless the request is resource/connection scoped, in which case the context attribute is used.

## Dependencies and integration points
It includes `linux/drbd.h`, undefines the preprocessor symbol `linux` to avoid include path conflicts, then includes generator support. It is consumed by generated netlink struct and function code.

## Risks and test signals
Changing the header layout or family header size is ABI-sensitive. Tests should encode/decode messages for minor-scoped and resource-scoped commands, verify reply return code handling, and confirm generator output includes the expected DRBD schema.
