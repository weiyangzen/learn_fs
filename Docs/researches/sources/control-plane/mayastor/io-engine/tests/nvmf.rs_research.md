# sources/control-plane/mayastor/io-engine/tests/nvmf.rs

Purpose: validates NVMf subsystem creation/claiming, target interface selection, and ignored RDMA target publish/connectivity behavior.

Important APIs/types/functions: `bdev_create`, `NvmfSubsystem`, `SubType`, `UntypedBdev`, `MayastorEnvironment`, `BdevShareRequest`, `BdevUri`, v1 pool/replica/nexus/publish requests, `ShareProtocolNexus`, `NetworkMode`, `Regex`, `nvme_connect`, and `nvme_disconnect_nqn`.

Control flow: `nvmf_target` creates an aio bdev, starts an NVMf subsystem, verifies duplicate creation fails, counts subsystems, checks bdev claim ownership, stops and unsafely shuts down the subsystem, and verifies claim release. `nvmf_set_target_interface` starts containers with `-T` selectors, shares a malloc bdev, parses the URI, and checks advertised IP. Ignored `test_rdma_target` sets up rxe, starts privileged host-network io-engine with RDMA enabled, publishes a nexus, checks `nvmf+rdma+tcp`, connects via NVMe RDMA, and cleans up.

State and persistence behavior: no persistent store. State is subsystem registry, bdev claimed/unclaimed state, target address selection, and published URI scheme.

Dependencies and integration points: SPDK NVMf, Docker networking, host RDMA/rxe, NVMe CLI, regex parsing, and v0/v1 gRPC.

Risks: RDMA test requires host privileges and is ignored; interface tests assume Docker network behavior.

Test signals: duplicate subsystem error, subsystem count, claim owner, URI IP match, RDMA scheme, and NVMe RDMA connection success.
