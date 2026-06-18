# sources/cloud-native/cri-o/internal/config/node/node_freebsd.go

Purpose: implements FreeBSD node configuration validation as a no-op placeholder.

Important APIs/types/functions: `ValidateConfig() error` returns nil.

Control flow: callers can invoke `ValidateConfig` uniformly across platforms; FreeBSD performs no singleton probing in this file.

State and persistence behavior: no state and no persistence.

Dependencies/integration points: platform variant for the shared `node` package.

Risks: missing FreeBSD-specific validation means configuration errors may surface later at runtime as platform support grows.

Test signals: no direct tests.
