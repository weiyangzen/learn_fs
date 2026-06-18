# sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/displayport.h

## Purpose

`displayport.h` exposes the DisplayPort altmode probe/remove helpers to wrapper drivers such as NVIDIA VirtualLink while providing no-op stubs when DisplayPort altmode support is disabled.

## Important APIs, Types, and Functions

When `CONFIG_TYPEC_DP_ALTMODE` is enabled, it declares `int dp_altmode_probe(struct typec_altmode *alt)` and `void dp_altmode_remove(struct typec_altmode *alt)`. Otherwise it defines inline stubs returning `-ENOTSUPP` and doing nothing.

## Control Flow

There is no independent control flow. `nvidia.c` includes this header and delegates matching VirtualLink altmodes to these helpers. Compile-time configuration decides whether that delegation reaches the real DisplayPort implementation.

## State and Persistence Behavior

The header stores no state. Real state is owned by `displayport.c` when enabled.

## Dependencies and Integration Points

It depends on Type-C altmode declarations being visible to callers and on `CONFIG_TYPEC_DP_ALTMODE`. It integrates the NVIDIA altmode module with the DisplayPort implementation without duplicating code.

## Risks and Edge Cases

The non-static stub definitions in a header are acceptable only because Kconfig prevents consumers that need the real implementation from building without it in normal configurations. Signature drift between header and implementation would break NVIDIA delegation.

## Test Signals

Build NVIDIA altmode with DisplayPort enabled, verify successful linking to exported helpers, and build configurations where DisplayPort is disabled to confirm stubs compile for any guarded users.
