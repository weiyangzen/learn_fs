# sources/control-plane/longhorn-engine/integration/rpc/__init__.py

## Purpose
This package initializer adjusts Python import search paths so generated gRPC files under `integration/rpc` can resolve their relative-style imports.

## Important APIs, types, and functions
- Imports `os` and `sys`.
- Appends `os.path.abspath(os.path.join(os.path.split(__file__)[0], "."))` to `sys.path`.

## Control flow
At import time, the module computes the absolute path of the `rpc` directory and appends it to `sys.path`.

## State and persistence behavior
The only state change is process-global mutation of `sys.path`. It is not persisted beyond the Python process.

## Dependencies and integration points
Generated protobuf/gRPC modules import packages such as `imrpc`, `bimrpc`, and other generated peers without fully qualified package paths. This initializer supports those imports when tests import the `rpc` package.

## Risks and edge cases
- Repeated imports can append duplicate path entries.
- Process-global `sys.path` mutation can shadow other packages named `imrpc`, `bimrpc`, or `ptypes`.
- The approach depends on local filesystem layout and should be kept in sync with generated code import style.

## Test signals
Successful import of generated modules and RPC client wrappers is the main signal. Failures would appear as `ModuleNotFoundError` during pytest collection or client construction.
