# sources/cloud-native/containers-storage/pkg/unshare/getenv_linux_cgo.go

Purpose: cgo-backed environment lookup for Linux builds using cgo.

Important APIs/types/functions: `getenv(name string) string`, calling C `getenv`.

Control flow: converts the Go string to a C string, defers `free`, calls `C.getenv`, and converts the returned pointer to a Go string.

State/persistence: reads process environment; no mutation.

Dependencies/integration: used by Linux rootless/unshare helpers to read environment variables that may be set before Go runtime initialization or by C constructor code.

Risks: `C.GoString(nil)` returns an empty string, matching expected missing variable behavior. cgo availability changes which file supplies `getenv`, so behavior should remain aligned with the non-cgo implementation.

Test signals: rootless environment tests should cover `_CONTAINERS_ROOTLESS_UID/GID` and `_CONTAINERS_USERNS_CONFIGURED` under cgo builds.
