# sources/control-plane/mayastor/test/python/setup.sh

## Purpose
Bootstraps the Python test environment and generated gRPC modules.

## Important APIs, Types, And Functions
Runs `grpc_tools.protoc` for legacy `mayastor.proto` and v1 protobufs, then creates `test/python/venv` and installs `requirements.txt`.

## Control Flow
The script uses `set -euxo pipefail`, requires `SRCDIR`, changes to it, generates Python protobuf code into `test/python`, creates a virtualenv without setuptools, and installs dependencies.

## State And Persistence
Writes generated protobuf Python files and a virtualenv under the source tree.

## Dependencies And Integration Points
Depends on Python, `grpc_tools`, `virtualenv`, requirements, `SRCDIR`, and the protobuf submodule path under `utils/dependencies/apis/io-engine/protobuf`.

## Risks
Generated files can become stale if protos change and setup is not rerun. The script assumes `IO_ENGINE_DIR` indirectly through tests but not here.

## Test Signals
Successful setup means Python tests can import generated legacy and v1 gRPC modules.
