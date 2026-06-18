# sources/control-plane/rook/pkg/util/log/log.go

## Purpose
`log.go` wraps capnslog calls with namespace or namespaced-name prefixes.

## Important APIs, Types, and Functions
`NamedInfo()`, `NamedWarning()`, `NamedError()`, `NamedDebug()`, and `NamedTrace()` prefix with `types.NamespacedName.String()`. `NamespacedInfo()`, `NamespacedWarning()`, `NamespacedError()`, `NamespacedDebug()`, and `NamespacedTrace()` prefix messages with `[namespace]` and format the message.

## Control Flow, State, and Persistence
The functions are thin logging wrappers. They do not return errors or persist data beyond log output.

## Dependencies and Integration Points
It depends on capnslog and Kubernetes `types.NamespacedName`. Reconciler code can use it to make logs easier to correlate with namespaces/resources.

## Risks
Formatting is performed before passing to capnslog, so format-string mistakes happen inside `fmt.Sprintf`. Sensitive args are logged as provided. The `namespace` parameter can be a full namespaced name when using `Named*`.

## Test Signals
No direct mapped tests. Useful coverage would need a log capture mechanism to assert prefixes and formatting.
