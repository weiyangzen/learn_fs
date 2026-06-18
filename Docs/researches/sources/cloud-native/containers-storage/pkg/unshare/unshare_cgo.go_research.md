# sources/cloud-native/containers-storage/pkg/unshare/unshare_cgo.go

Purpose: cgo link hook for Linux and FreeBSD unshare C constructors.

Important APIs/types/functions: C constructor `init` calling external `_containers_unshare`.

Control flow: when the package is linked, the C constructor runs before Go initialization and delegates to platform `_containers_unshare`.

State/persistence: may trigger early namespace/session setup through the C implementation based on environment variables.

Dependencies/integration: selected for Linux cgo non-gccgo and FreeBSD cgo builds; paired with `unshare.c` or `unshare_freebsd.c`.

Risks: constructor side effects happen before normal Go code, so environment variables and file descriptors must be correct. Build tags are critical to avoid compiling the wrong C implementation.

Test signals: unshare command tests indirectly verify the constructor runs and synchronizes with Go parent code.
