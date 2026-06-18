<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/bdev.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/bdev.rs

Purpose: Thin async helper wrappers around v1 bdev gRPC APIs for tests.

Important APIs: `create_bdev(rpc, uri)` locks a shared RPC handle and sends `CreateBdevRequest`; `list_bdevs(rpc)` sends `ListBdevOptions { name: None }`; `find_bdev_by_name(rpc, name)` lists and filters by name, returning `None` on list errors.

Control flow: all functions use `SharedRpcHandle::lock().await`, call the generated gRPC client, and unwrap response envelopes into `Bdev` vectors or values.

State and dependencies: depends on `compose::rpc::v1` generated API types and the shared handle lock. It mutates remote io-engine state only through create calls.

Integration points: used by higher-level tests that need simple bdev lifecycle or lookup without manually constructing protobuf requests.

Risks and test signals: `find_bdev_by_name` hides RPC errors as not found, which is convenient but can mask transport failures. Tests should assert create/list separately when diagnosing infrastructure issues.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/bdev.rs -->
