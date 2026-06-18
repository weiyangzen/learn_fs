# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fw_update.h

## Purpose
Declares the public firmware-update entry points used by the rest of the `ice` driver.

## Important APIs, types, and functions
- `ice_devlink_flash_update()` exposes the devlink flash-update implementation.
- `ice_get_pending_updates()` exposes pending NVM/Option ROM/netlist activation checks.
- `ice_write_one_nvm_block()` exposes the low-level NVM block write plus completion wait helper.

## Control flow
This header has no executable control flow. It defines the compile-time contract between devlink integration, update support code, and any callers that need direct block-write or pending-update behavior.

## State and persistence behavior
No state is stored here. The declarations operate on `struct ice_pf`, `struct devlink`, NVM modules, and netlink extack objects owned elsewhere.

## Dependencies and integration points
The prototypes require driver-visible definitions for `struct ice_pf`, devlink flash parameters, `netlink_ext_ack`, and fixed-width integer types. It is included by the implementation and by driver code that wires devlink operations.

## Risks
Signature changes here affect devlink registration and low-level NVM callers. Because `ice_write_one_nvm_block()` assumes NVM resource ownership, any new caller must follow the locking contract documented in the `.c` file.

## Test signals
Build coverage should catch signature drift. Runtime signals come from devlink flash update and pending-update query paths.
