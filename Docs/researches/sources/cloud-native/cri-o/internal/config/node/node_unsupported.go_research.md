# sources/cloud-native/cri-o/internal/config/node/node_unsupported.go

Purpose: provides a generic unsupported-platform `ValidateConfig` stub.

Important APIs/types/functions: `ValidateConfig() error` returns nil under `!linux && !freebsd`.

Control flow: no validation work.

State and persistence behavior: none.

Dependencies/integration points: platform compilation shim for shared callers.

Risks: unsupported builds do not receive early validation and may fail later where platform features are needed.

Test signals: no tests.
