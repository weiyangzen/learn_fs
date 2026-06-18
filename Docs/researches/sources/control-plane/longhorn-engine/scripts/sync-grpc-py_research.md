## sources/control-plane/longhorn-engine/scripts/sync-grpc-py

### Purpose
`scripts/sync-grpc-py` verifies that Python gRPC generated code used by integration tests is synchronized with the `longhorn/types` repository.

### Important APIs, Types, And Functions
The script clones `https://github.com/longhorn/types.git` into `tmp-longhorn-types`, copies `generated-py/` into `integration/rpc`, removes the temporary clone, then checks `git diff --stat` for `_pb2.py` and `_pb2_grpc.py` changes.

### Control Flow
`set -e` is temporarily relaxed around the diff pipeline so it can inspect grep status. If generated Python files differ, it prints the diff stat and exits with failure.

### State, Persistence, And Dependencies
It writes `integration/rpc`, creates/removes `tmp-longhorn-types`, and depends on git and network access.

### Integration Points
`scripts/ci` runs this before tests, enforcing generated client compatibility for integration RPC code.

### Risks
It tracks the default branch of `longhorn/types`, so CI can fail due to upstream changes unrelated to this repository. A failed clone before cleanup can leave a temporary directory.

### Test Signals
No diff after sync is the success signal. A diff in generated Python files means the repository needs updated generated artifacts.
