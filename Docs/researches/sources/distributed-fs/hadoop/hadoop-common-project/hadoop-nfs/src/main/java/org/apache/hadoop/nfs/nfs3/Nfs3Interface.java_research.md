# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Interface.java

## Purpose
`Nfs3Interface.java` defines the Java handler contract for all NFSv3 RPC procedures from RFC 1813.

## Important APIs, Types, and Functions
- `nullProcedure()` returns an NFS null response.
- Methods for all standard NFSv3 operations accept request `XDR` and `RpcInfo` and return `NFS3Response`: `getattr`, `setattr`, `lookup`, `access`, `readlink`, `read`, `write`, `create`, `mkdir`, `symlink`, `mknod`, `remove`, `rmdir`, `rename`, `link`, `readdir`, `readdirplus`, `fsstat`, `fsinfo`, `pathconf`, and `commit`.

## Control Flow and State
The interface has no state. Implementations decode request XDR, use `RpcInfo` for request context/credentials, perform filesystem work, and return typed NFS response objects.

## Dependencies and Integration Points
It integrates `NFS3Response`, ONCRPC `RpcInfo`, and `XDR`. NFSv3 RPC programs dispatch from `Nfs3Constant.NFSPROC3` values to implementations of this interface.

## Risks and Edge Cases
The interface exposes every NFSv3 operation, so implementation consistency is critical for auth, idempotence, write stability, and response status mapping. The API does not declare checked exceptions, implying implementations encode errors into `NFS3Response`.

## Test Signals
Coverage should exist at implementation level for each procedure's XDR decode, authorization, filesystem side effects, and response serialization.
