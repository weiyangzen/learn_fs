# sources/control-plane/longhorn-engine/integration/rpc/controller/__init__.py

## Purpose
This package initializer adjusts Python import paths for generated controller gRPC modules under `integration/rpc/controller`.

## Important APIs, types, and functions
- Imports `os` and `sys`.
- Appends the absolute controller package directory to `sys.path`.

## Control flow
The path append happens at import time using `os.path.split(__file__)[0]`.

## State and persistence behavior
The only state mutation is process-global `sys.path`; no persistent state is written.

## Dependencies and integration points
It supports generated controller modules that use relative-style imports and the `controller_client.py` wrapper that imports `ptypes.controller_pb2` and `ptypes.controller_pb2_grpc`.

## Risks and edge cases
Duplicate path entries can accumulate, and path mutation can shadow unrelated modules if names collide. Import correctness depends on generated file layout.

## Test signals
Successful import of `rpc.controller.controller_client.ControllerClient` and generated controller protobuf modules is the practical signal.
