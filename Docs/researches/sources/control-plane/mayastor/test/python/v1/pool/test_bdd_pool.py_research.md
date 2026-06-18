# sources/control-plane/mayastor/test/python/v1/pool/test_bdd_pool.py

Purpose: v1 pytest-bdd pool management coverage, including UUID validation, import/export, name-filtered listing, duplicate handling, invalid disks, aio pools, and destroy errors.

Important APIs and control flow: fixtures create `/tmp/ms0-disk0.img`, wrap `pool_rpc.CreatePool`, list by name, track pools for cleanup, and destroy any remaining tracked pools with name and UUID. Steps expect `INVALID_ARGUMENT` for invalid block size, invalid UUID, and multiple disks; create valid UUID pools; create/export/import aio pools; reject import with invalid UUID; list all/name-filtered pools; and capture duplicate or missing destroy errors. Then steps assert `ALREADY_EXISTS`, `NOT_FOUND`, empty/non-empty find results, filtered list sizes, and UUID preservation.

State, dependencies, and integration: state includes an aio image, pool records, optional UUID fields, exported/imported on-disk metadata, and live gRPC responses. It depends on `pool_pb2`, pytest-bdd, `grpc`, `run_cmd`, and `v1.mayastor`.

Risks and test signals: some create calls pass a string instead of list for disks in error paths, intentionally exercising validation but also coupling to protobuf coercion behavior. The test has strong signals for API status codes and persistent UUID import semantics.
