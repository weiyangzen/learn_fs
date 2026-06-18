<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_unsupported.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_unsupported.go

Purpose: build-tagged fallback for platforms other than Linux, Windows, and FreeBSD where OSL sandboxes are not implemented.

Important APIs/types/functions: exposes `ErrNotImplemented`, `NewSandbox(key string, osCreate, isRestore bool) (*Namespace, error)`, and `GenerateKey(containerID string) string`. `NewSandbox` always returns `nil, ErrNotImplemented`; `GenerateKey` returns an empty string.

Control flow: there is no runtime state transition. The file exists so higher-level packages compile on unsupported targets while any attempt to create a namespace fails explicitly.

State and persistence: no namespace state, filesystem path, or persisted key is created. The empty `GenerateKey` value is a signal that unsupported platforms cannot derive usable namespace keys.

Dependencies and integration points: imports only `errors`. It satisfies references from libnetwork sandbox restore/create code at compile time for unsupported GOOS values.

Risks and test signals: callers must not assume sandbox operations are available merely because symbols compile. A risk is accidental use of empty `GenerateKey` if higher-level code fails to gate unsupported platforms. The implementation is intentionally tiny; coverage is mostly by build matrix compilation rather than behavior tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_unsupported.go -->
