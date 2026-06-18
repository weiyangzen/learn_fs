# sources/control-plane/longhorn-engine/integration/rpc/imrpc/__init__.py

## Purpose
This package initializer is empty. It marks generated instance-manager RPC modules as an importable `imrpc` package.

## Important APIs, types, and functions
No APIs, imports, functions, or side effects are defined.

## Control flow
There is no runtime control flow.

## State and persistence behavior
No state is initialized or persisted.

## Dependencies and integration points
It supports imports such as `from imrpc import disk_pb2` and generated peer imports in gRPC modules.

## Risks and edge cases
Package recognition depends on this file in environments that do not use implicit namespace packages.

## Test signals
Successful import of generated `imrpc` protobuf and gRPC modules is the indirect signal.
