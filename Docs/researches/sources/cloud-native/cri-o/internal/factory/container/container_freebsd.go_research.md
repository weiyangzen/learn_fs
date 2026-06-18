# sources/cloud-native/cri-o/internal/factory/container/container_freebsd.go

Purpose: provides FreeBSD-specific SELinux label behavior for containers.

Important APIs/types/functions: `(*container).SelinuxLabel(sboxLabel string) ([]string, error)`.

Control flow: always returns an empty string slice and nil error.

State and persistence behavior: none.

Dependencies/integration points: FreeBSD platform variant of the container factory interface.

Risks: SELinux label handling is disabled on FreeBSD, as expected.

Test signals: no direct FreeBSD tests.
