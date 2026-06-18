# sources/control-plane/mayastor/test/python/tests/rpc/test_rpc.py

Purpose: asynchronous regression test for gRPC timeout handling during a long replica destroy.

Important APIs and control flow: fixtures define `/var/tmp/pool1.img`, create a 3 GiB file, and remove it afterward. `test_rpc_timeout` creates a pool and a 2 GiB replica on `ms1`, lowers the client timeout to 1 second, reconnects the handle to install the timeout, and calls `replica_destroy`. It expects a `grpc.RpcError` with `INVALID_ARGUMENT`, checks logs do not yet contain the timeout warning, retries destroy successfully, then checks logs contain the exact warning pattern for the timed-out call.

State, dependencies, and integration: state spans the large temp file, pool/replica state, client timeout configuration, reconnected gRPC stubs, and container logs. It depends on `common.command.run_cmd`, `common.mayastor`, `grpc`, asyncio pytest, and the log wording in io-engine.

Risks and test signals: a 1-second timeout and 2 GiB destroy are timing-sensitive. Exact log matching is brittle. The core signal is that timeout evidence is deferred until a later call detects the incomplete previous operation.
