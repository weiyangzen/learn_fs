# sources/control-plane/mayastor/io-engine/tests/nexus_with_local.rs

Purpose: validates nexus behavior when one child is a local `bdev:///` replica and another is a remote NVMf replica, with emphasis on local alias lifecycle.

Important APIs/types/functions: v1 `CreatePoolRequest`, `CreateReplicaRequest`, `CreateNexusRequest`, `AddChildNexusRequest`, `RemoveChildNexusRequest`, `DestroyBdevRequest`, `ListBdevOptions`, `RpcHandle`, `NVME_NQN_PREFIX`, `create_replicas`, `check_aliases`, and `create_nexus`.

Control flow: the test starts two io-engine containers, creates and shares a replica on each, then creates a nexus on node 1 with local `bdev:///repl0` and remote NVMf children. It checks a `bdev:///` alias is present, removes the local child and expects alias absence, re-adds the child, verifies duplicate add fails, checks alias presence, and destroys the local bdev.

State and persistence behavior: no persistent store. State is local bdev alias registration/removal, duplicate child detection, and bdev destroy behavior.

Dependencies and integration points: v1 pool, replica, nexus, and bdev gRPC services; NVMf URI construction; local child URI handling.

Risks: alias detection is broad and could false-positive if unrelated `bdev:///` aliases exist.

Test signals: alias present/absent at expected points, duplicate add errors, and destroy succeeds.
