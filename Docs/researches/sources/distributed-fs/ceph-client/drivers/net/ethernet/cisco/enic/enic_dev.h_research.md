<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_dev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_dev.h

## Purpose

`enic_dev.h` declares ENIC devcmd wrapper functions and provides a proxy macro for commands that may target a PF or a VF by index.

## Important APIs, Types, and Definitions

`ENIC_DEVCMD_PROXY_BY_INDEX` locks `devcmd_lock`, checks `enic_is_valid_vf`, optionally starts VF proxy mode, invokes a provided `vnicdevcmdfn`, ends proxy mode, and unlocks. The header declares all wrapper functions from `enic_dev.c`, VLAN callbacks, coalescing timer info, and status conversion.

## Control Flow

The macro implements inline control flow used by port-profile operations: valid VF indexes are proxied, otherwise the command is issued to the owning vNIC. Regular function prototypes defer control flow to `enic_dev.c`.

## State and Persistence Behavior

The header stores no state. The macro mutates transient firmware proxy mode and may cause persistent firmware changes through the invoked command.

## Dependencies and Integration Points

It includes `vnic_dev.h` and `vnic_vic.h` and is used by main, ethtool, port-profile, and resource paths.

## Risks and Edge Cases

The macro's fallback behavior means invalid/non-SR-IOV VF inputs can become PF/self commands unless callers validate separately. Lock ordering must match other devcmd users. Macro arguments must be side-effect safe enough for single evaluation in the chosen command expression.

## Test Signals

Compile all macro call sites, test PF and VF port-profile commands, invalid VF handling, and concurrent devcmd operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_dev.h -->
