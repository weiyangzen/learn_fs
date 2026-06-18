<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/check-env.sh -->
## sources/control-plane/ceph-csi/scripts/check-env.sh

Purpose: checks local build prerequisites for Ceph-CSI development.

Control flow: detects rpm/dpkg for package advice, creates a temporary cgo program including `rados/librados.h` and `rbd/librbd.h`, runs `go run -mod=vendor`, reports missing Ceph development packages, checks Go version >= 1.13, verifies `GO111MODULE` is on/auto/empty, and requires `CGO_ENABLED=1`. Accumulates errors and exits with count.

State and persistence: creates/removes temporary Go file.

Dependencies: Go toolchain, CGO, Ceph headers/libraries, package manager detection.

Integration points: developer preflight and CI environment diagnostics.

Risks: temp file cleanup occurs only when Go exists and compile path is reached; failures before removal may leave temp files. Go version parsing assumes classic `go version` format.

Test signals: no direct tests; output is intended for humans.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/check-env.sh -->
