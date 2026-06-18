# sources/control-plane/mayastor/test/python/v1/hdl.py

Purpose: reusable v1 Mayastor gRPC client wrapper for Python tests. `MayastorHandle` hides channel creation, stub construction, default timeouts, and request object boilerplate for bdev, pool, replica, snapshot, host, and nexus services.

Important APIs and control flow: constructor opens an insecure channel to `<ip>:10124`, creates service stubs, reads `config["grpc"]["client_timeout"]`, and runs `_readiness_check`. `install_stub` wraps every public stub method in `functools.partial(..., timeout=self.timeout)`, and `reconnect` rebuilds all stubs. Wrapper methods include `bdev_create/share/unshare/destroy/list`, `pool_create/destroy/list`, `replica_create/destroy/list`, `mayastor_info`, `nexus_create/publish/unpublish/destroy/list/add/remove`, `nexus_create_snapshot`, `pools_as_uris`, and `list_snapshots`.

State, dependencies, and integration: state is the gRPC channel, current timeout, IP address, and installed stubs. It depends on generated protobuf modules, pytest-testconfig, and docker-compose fixtures indirectly through callers.

Risks and test signals: `pool_create` accepts a `type` argument but does not send `pooltype`, so callers needing LVM use raw stubs. `Volume.create` appears to call `nexus_create` with an obsolete signature. Readiness catches only `_InactiveRpcError` and retries once. This file is tested indirectly by nearly every v1 test.
