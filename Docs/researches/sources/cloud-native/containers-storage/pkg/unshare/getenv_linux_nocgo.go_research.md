# sources/cloud-native/containers-storage/pkg/unshare/getenv_linux_nocgo.go

Purpose: non-cgo Linux implementation of unshare package environment lookup.

Important APIs/types/functions: `getenv(name string) string` delegates to `os.Getenv`.

Control flow: direct return of the Go runtime environment value.

State/persistence: reads process environment.

Dependencies/integration: keeps rootless/unshare logic available in `CGO_ENABLED=0` builds.

Risks: must remain semantically aligned with the cgo C `getenv` variant.

Test signals: non-cgo builds should exercise rootless environment parsing and namespace reexec decisions.
