
# sources/distributed-fs/ceph-client/include/uapi/linux/if_ltalk.h

## Purpose

`if_ltalk.h` defines LocalTalk link-layer constants for Linux UAPI consumers. The complete 10-line file contains only header guards and MTU/header/address length constants.

## Important APIs, Types, and Functions

Constants are `LTALK_HLEN`, `LTALK_MTU`, and `LTALK_ALEN`. There are no structs, enums, functions, or ioctls.

## Control Flow

No runtime flow is present. Drivers or tools include the constants when sizing LocalTalk headers, device addresses, or MTU constraints.

## State and Persistence Behavior

No state is stored by the header. The constants describe protocol sizing assumptions used by external code.

## Dependencies and Integration Points

The header has no includes and integrates with legacy LocalTalk networking code and generic network-device validation.

## Risks and Edge Cases

The values are legacy ABI assumptions. Changing them can mis-size buffers or break tools that assume one-byte LocalTalk addresses and a 600-byte MTU.

## Test Signals

Compile coverage for LocalTalk users and simple checks that interface setup paths still apply the expected header length, MTU, and address length.
