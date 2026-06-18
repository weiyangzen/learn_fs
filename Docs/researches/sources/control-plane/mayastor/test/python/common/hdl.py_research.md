# sources/control-plane/mayastor/test/python/common/hdl.py

## Purpose
Provides the central Python `MayastorHandle` wrapper around legacy Mayastor gRPC stubs. It gives tests a concise API for bdev, pool, replica, nexus, NVMe controller stats, and Mayastor info operations.

## Important APIs, Types, And Functions
Important methods include `install_stub`, `_readiness_check`, `reconnect`, `bdev_create/share/unshare/destroy/list`, `pool_create/destroy/list`, `replica_create/create_v2/share/destroy/list/list_v2`, `nexus_create/create_v2/publish/unpublish/destroy/shutdown/list/list_v2/add_replica/remove_replica`, `pools_as_uris`, `stat_nvme_controllers`, and `mayastor_info`.

## Control Flow
Construction opens `grpc.insecure_channel(<ip>:10124)`, installs `BdevRpcStub` and `MayastorStub`, and performs a readiness check by listing bdevs and pools with a one-retry workaround for an inactive-channel error. `install_stub` wraps all stub functions with a default timeout.

## State And Persistence
The handle stores the target IP, gRPC timeout, channel, and stubs. All persistent Mayastor state is remote in io-engine containers.

## Dependencies And Integration Points
Depends on generated legacy `mayastor_pb2`/`mayastor_pb2_grpc`, `grpc`, `pytest_testconfig`, and docker-compose fixture plugins. It is the main integration layer used by nearly all Python tests in this subset.

## Risks
The wrapper mixes old and v2 APIs and has minimal type validation, intentionally allowing invalid URIs through to Mayastor. Channel cleanup is by deletion rather than explicit close, and timeout wrapping only applies to stubs installed through `install_stub`.

## Test Signals
If this handle can create/list/destroy resources, it proves container networking, protobuf generation, gRPC server readiness, and basic Mayastor control plane operations are aligned.
