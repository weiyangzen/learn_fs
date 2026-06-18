<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-logcheck.sh -->
# sources/control-plane/external-snapshotter/release-tools/verify-logcheck.sh

## Purpose
`verify-logcheck.sh` installs and runs Kubernetes `logcheck` to verify contextual klog usage in Go code.

## Important APIs, Types, and Functions
It accepts an optional `LOGCHECK_VERSION` argument, defaults to `0.10.0`, resolves `CSI_LIB_UTIL_ROOT` as the parent of release-tools, creates `CSI_LIB_UTIL_TEMP`, installs `sigs.k8s.io/logtools/logcheck@v${LOGCHECK_VERSION}` with `go install`, and runs `logcheck -check-contextual -check-with-helpers "${CSI_LIB_UTIL_ROOT}/..."`.

## Control Flow, State, and Persistence
The script exits on errors and removes its temporary install directory via trap. It does not persist tool binaries in the repository; all state is temporary except Go module cache downloads.

## Dependencies and Integration Points
It depends on Bash, Go module installation, the `sigs.k8s.io/logtools/logcheck` module, and repository Go packages. It integrates with verification targets that enforce klog contextual logging conventions.

## Risks and Test Signals
Risks include network/module proxy failure, version drift of logcheck rules, and scanning too broad a package tree when vendored or generated Go is present under the parent root. Signals are the install log and a clean logcheck exit.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-logcheck.sh -->
