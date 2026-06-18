# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-errno.h

Purpose: defines glusterd-specific operation error numbers for management-layer failures.

Important APIs/types/functions: `enum glusterd_op_errno` assigns values starting at 30800 for internal error, unsupported op, transaction in progress, brick/node down, hard limit, missing volume/snapshot, rebalance running, volume running/stopped/existing, snapshot existing, snap volume, geo-rep running, thin provisioning mismatch, and NFS-Ganesha not enabled.

Control flow: operation code can use these enum values in CLI/RPC responses or error mapping to represent domain-specific failures beyond generic `errno`.

State and persistence behavior: no state. Values are part of the management protocol surface and should be stable.

Dependencies and integration points: standalone header included by glusterd operation modules where needed.

Risks and edge cases: changing numeric values can break clients or logs that interpret these codes. Adding values requires avoiding collisions.

Test signals: CLI/RPC error response tests should verify expected codes for representative management failures.
