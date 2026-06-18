## sources/control-plane/longhorn-engine/scripts/ci

### Purpose
`scripts/ci` is the top-level local CI orchestrator for longhorn-engine.

### Important APIs, Types, And Functions
It accepts `SKIP_TASKS` as a space-delimited environment variable and defines the ordered task list: `build`, `validate`, `sync-grpc-py`, `test`, `integration-test`, and `package`.

### Control Flow
The script changes to the scripts directory, splits `SKIP_TASKS`, iterates over tasks, skips matching names, and executes each task script. `set -e` stops on the first failed task.

### State, Persistence, And Dependencies
It writes no state itself. Downstream scripts build binaries, run tests, sync generated files, and build images. It depends on bash and sibling executable scripts.

### Integration Points
`scripts/release` delegates directly to this script. CI jobs and developer workflows can set `SKIP_TASKS` to shorten runs.

### Risks
Task names must match exactly. Skipping critical tasks can hide failures. Since the script runs from `scripts`, sibling scripts must remain executable and relative paths must be stable.

### Test Signals
A smoke test can run with `SKIP_TASKS` covering all tasks to verify skip parsing, and CI runs verify downstream task order.
