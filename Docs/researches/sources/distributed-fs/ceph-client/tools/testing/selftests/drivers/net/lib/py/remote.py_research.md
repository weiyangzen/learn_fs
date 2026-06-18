
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/remote.py`

## Purpose
Factory for remote endpoint backends used by `NetDrvEpEnv`.

## Important APIs, Types, And Functions
- Module cache `_modules` stores imported backend modules.
- `Remote(kind, args, src_path)` imports `..remote_<kind>` relative to this package, resolves the source directory, and constructs that backend's `Remote` class.

## Control Flow
On first use for a backend kind, the module is imported dynamically with `importlib.import_module()`. Subsequent calls reuse the cached module. The returned object supplies at least `cmd()` and `deploy()` methods.

## State And Persistence
Only the module cache persists. Backend instances own their own remote state.

## Dependencies And Integration Points
Integrated by `NetDrvEpEnv`, which passes `REMOTE_TYPE` and `REMOTE_ARGS` from config or uses `netns` for local netdevsim tests.

## Risks
Backend kind strings directly drive module import, so bad config becomes an import error. There is no validation beyond constructing the class.

## Test Signals
No direct tests; failures surface when environment creation cannot import or instantiate the requested remote backend.
