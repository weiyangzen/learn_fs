## sources/control-plane/longhorn-engine/scripts/release

### Purpose
`scripts/release` is a thin release entrypoint that delegates to the full CI script.

### Important APIs, Types, And Functions
It contains only a bash shebang and `exec $(dirname $0)/ci`.

### Control Flow
`exec` replaces the shell with `scripts/ci`, preserving arguments and environment.

### State, Persistence, And Dependencies
It writes no state and depends entirely on `scripts/ci`.

### Integration Points
Release automation can call a semantically named script while reusing the same build/validate/test/package pipeline.

### Risks
There is no separate release-specific validation. Any release behavior must be implemented in `ci` or downstream scripts.

### Test Signals
Running `scripts/release` should behave exactly like `scripts/ci`.
