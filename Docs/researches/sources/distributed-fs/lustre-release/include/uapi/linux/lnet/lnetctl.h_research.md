# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnetctl.h

## Purpose
This UAPI header defines `/dev/lnet` fault-simulation ioctl payloads for LNet message drop and delay rules. It also exposes the device ID and path used by user tools.

## Important APIs, Types, And Functions
The command enum identifies add/delete/reset/list operations for drop and delay simulation. Message-type bits cover ACK, PUT, GET, and REPLY. Health-status bits encode local interrupt, local drop, local abort, no-route, local error, local timeout, remote error/drop/timeout, network timeout, and random health selection. `struct lnet_fault_attr` describes rule match fields and either drop or delay attributes. `struct lnet_fault_stat` reports matched, per-message-type, dropped, and delayed counts.

## Control Flow
User space fills `lnet_fault_attr` and sends it through the LNet control path. Source, destination, local NID, portal mask, and message mask gate whether a message is eligible. The union then selects drop behavior by rate or interval and health error mask, or delay behavior by rate or interval plus latency. Kernel fault-injection code updates `lnet_fault_stat` counters as matching messages are processed.

## State, Persistence, And Dependencies
The header itself stores no state. The kernel keeps rule state and counters after ioctls are applied. It depends on `lnet-types.h` for `lnet_nid_t` and on Linux fixed-width integer types. The union includes spare space to preserve ABI room.

## Integration Points
LNet test tools and administrative utilities include this file to configure message loss/latency fault injection through `LNET_DEV_PATH`. The masks line up with LNet message kinds and health counters exposed elsewhere in LNet.

## Risks
Because this is UAPI, command values and struct layout are compatibility-sensitive. Portal masks are 64-bit, so callers must ensure portal indexes fit the mask. Rate and interval fields are mutually exclusive by comment but require kernel validation. A broad wildcard rule can disrupt live traffic if accidentally installed.

## Test Signals
Tests should add, list, reset, and delete drop and delay rules; verify wildcard and portal/message masks; check that mutually exclusive rate/interval inputs are rejected or handled predictably; and confirm health counters reflect injected errors.
