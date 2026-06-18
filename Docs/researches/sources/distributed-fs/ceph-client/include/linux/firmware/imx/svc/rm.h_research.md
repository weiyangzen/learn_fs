# sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/rm.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/rm.h` defines i.MX SCU Resource Management service function IDs and resource-owner helper APIs. The source was read as a complete 74-line file for this report.

## Important APIs, Types, and Functions

`enum imx_sc_rm_func` covers partition allocation/free/static/lock, DID queries, parent/assign/move operations, master/peripheral permissions, resource ownership, memory-region allocation/fragment/split/assign/permissions, pad assignment, and dumps. APIs are `imx_sc_rm_is_resource_owned` and `imx_sc_rm_get_resource_owner`; disabled builds return `true` for ownership and `-EOPNOTSUPP` for owner query.

## Control Flow

SCU RM clients use these IDs in RPC messages and call ownership helpers before touching resources. Disabled builds optimistically treat resources as owned to avoid blocking non-SCU platforms.

## State and Persistence Behavior

No state is owned here. Resource partitioning and ownership are maintained by SCFW.

## Dependencies and Integration Points

It includes `sci.h` and integrates with i.MX SCFW RM service, partitioning, device ownership, memory-region permissions, pad control, and platform drivers.

## Risks and Edge Cases

Ownership stubs returning `true` are convenient but can hide missing SCU checks if used on wrong platforms. RM operations are security/isolation-sensitive. Resource IDs and partition IDs are firmware ABI.

## Test Signals

SCU RM ownership tests, partition/resource assignment tests, disabled-config behavior tests, and firmware rejection/error-path tests.
