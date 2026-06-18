## sources/control-plane/juicefs-csi-driver/pkg/util/log.go

### Purpose
`log.go` provides context-aware logger propagation and secret redaction for map-based configuration data. It lets call chains use a logger stored in context and provides a utility to strip sensitive values before logging.

### Important APIs, Types, And Functions
`LogKey` and `LoggerType` define the context key. `WithLog(parentCtx, log)` stores a `klog.Logger`. `GenLog(ctx, log, name)` returns the context logger if present, otherwise a named child logger when `name` is non-empty. `stripKeys` lists sensitive keys. `StripSecret(secret)` copies a string map, replaces sensitive keys with `"***"`, and recursively redacts JSON `initconfig`.

### Control Flow
Logger generation is first context lookup, then optional `WithName`. Secret stripping copies the input map to avoid mutation, checks known key names exactly, parses `initconfig` as JSON object if present, recursively strips it, and marshals it back.

### State, Persistence, And Dependencies
There is no persistent state. Dependencies are `context`, `encoding/json`, and `klog/v2`.

### Integration Points
Mount and resource code call `util.GenLog` to preserve operation-scoped loggers. Configuration and secret logging paths can call `StripSecret` before emitting user-provided settings.

### Risks
The context value is type-asserted without checking, so a wrong value under the same key panics. Redaction is exact-key and lowercase oriented; variants outside `stripKeys` are not masked. Invalid `initconfig` JSON becomes `"null"` or an empty marshaled structure after ignored errors, which can alter observability output.

### Test Signals
No tests are listed. Useful tests would assert non-mutation, nested `initconfig` redaction, missing/uppercase key behavior, and logger context override semantics.
