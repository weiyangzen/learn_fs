# sources/cloud-native/containerd/pkg/oci/mounts_freebsd.go

Purpose: FreeBSD-specific OCI mount defaults and OS-dependent image mount hook.

Important APIs/types/functions: `defaultMounts()` returns FreeBSD mount entries for `/dev`, `/dev/fd`, `/dev/fuse`, `/dev/null`, `/dev/random`, `/dev/urandom`, `/dev/zero`, `/proc`, and `/tmp`. `appendOSMounts(s, os)` appends additional defaults when the image OS is `linux` or `freebsd`.

Control flow: default spec population gets FreeBSD defaults. Image config processing can append Linux/FreeBSD compatibility mounts based on image OS.

State/persistence: generated OCI spec mount list only.

Dependencies/integration: build-selected on FreeBSD. Uses runtime-spec mount definitions.

Risks: device and procfs mount behavior is platform-specific and security-sensitive. Appending mounts based on image OS can duplicate or conflict with caller-supplied mounts if not managed carefully.

Test signals: FreeBSD build/integration tests should validate generated spec mounts and image OS handling. General mount tests do not fully cover this platform-specific file.
