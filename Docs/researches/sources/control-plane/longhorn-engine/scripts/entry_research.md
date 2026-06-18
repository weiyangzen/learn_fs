## sources/control-plane/longhorn-engine/scripts/entry

### Purpose
`scripts/entry` is a container/developer entrypoint wrapper that forces vendored Go module mode and dispatches to repository scripts when the first argument names one.

### Important APIs, Types, And Functions
The script exports `GOFLAGS=-mod=vendor`, creates `bin`, then checks `./scripts/$1`. If present, it executes the script with all arguments; otherwise it executes the requested command directly.

### Control Flow
`set -e` fails fast. Dispatch is positional: `entry build` runs `./scripts/build`, while `entry bash` runs `bash`.

### State, Persistence, And Dependencies
It creates `bin/` and sets process environment. It depends on bash and the repository layout.

### Integration Points
This wrapper is suitable for Docker entrypoints and CI shells that need consistent vendored Go builds.

### Risks
If `$1` is empty, `[ -e ./scripts/$1 ]` tests the scripts directory and may attempt to run it with an empty command. Callers should pass a command.

### Test Signals
Smoke tests should verify script dispatch, direct command dispatch, and `GOFLAGS` propagation.
