# sources/control-plane/longhorn-engine/integration/rpc/imrpc/common_pb2_grpc.py

## Purpose
This generated gRPC companion for `imrpc/common.proto` contains only the generated header/import because the common proto defines shared enums but no services.

## Important APIs, types, and functions
No stubs, servicers, registration helpers, or methods are defined. It imports `grpc`.

## Control flow
Import-time behavior is limited to importing `grpc`.

## State and persistence behavior
No state is initialized except the normal imported module reference.

## Dependencies and integration points
It exists for generator consistency and may satisfy code that expects every proto to have a `_pb2_grpc.py` module. Shared message/enum definitions live in `common_pb2.py`.

## Risks and edge cases
There is no runtime RPC surface here. Risk is limited to import compatibility if generated file presence is assumed.

## Test signals
Successful import is the only direct signal.
