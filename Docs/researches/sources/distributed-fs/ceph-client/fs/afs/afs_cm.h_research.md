# sources/distributed-fs/ceph-client/fs/afs/afs_cm.h

## Purpose
`afs_cm.h` defines AFS cache-manager service constants and operation IDs for server-to-client callback RPCs.

## Important APIs, types, and functions
It defines `AFS_CM_PORT`, `CM_SERVICE`, `enum AFS_CM_Operations`, and `AFS_CAP_ERROR_TRANSLATION`. Operation IDs include `CBCallBack`, `CBInitCallBackState`, `CBProbe`, `CBInitCallBackState3`, `CBProbeUuid`, and `CBTellMeAboutYourself`.

## Control flow
`cmservice.c` dispatches incoming RxRPC calls by these operation IDs and selects the corresponding call type/deliver/work handlers.

## State and persistence
There is no runtime state in the header. Constants define wire protocol behavior.

## Dependencies and integration points
It is consumed by cache-manager service and security code and must align with AFS/YFS protocol expectations.

## Risks and test signals
Risks include wrong operation IDs or service IDs causing callback dispatch failures. Test signals include incoming callback RPC decoding, probe/probeuuid behavior, capability replies, and unsupported-operation rejection.
