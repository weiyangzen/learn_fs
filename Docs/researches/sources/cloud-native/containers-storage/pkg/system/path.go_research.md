# sources/cloud-native/containers-storage/pkg/system/path.go

Purpose: exposes the default executable search path used by containers/storage callers when constructing container environments.

Important APIs/types/functions: `defaultUnixPathEnv` constant and `DefaultPathEnv(platform string) string`.

Control flow: non-Windows hosts always return the Unix default. On Windows, Linux containers on Windows can receive the Unix default when `platform` differs from `runtime.GOOS` and `LCOWSupported()` is true; Windows containers return an empty default so the container supplies its own path.

State/persistence: no persistence; result depends on the host runtime and LCOW capability.

Dependencies/integration: integrates with container environment setup code and platform selection. Depends on `runtime` and the package's Windows LCOW helper.

Risks: empty Windows default is intentional but can surprise callers that assume a non-empty PATH. LCOW support detection controls whether Linux-style paths are injected on Windows.

Test signals: platform tests should cover Linux/Unix defaults, Windows-container empty defaults, and LCOW Linux-platform behavior.
