# sources/control-plane/external-snapshotter/Makefile

## Purpose
Top-level Makefile for building external-snapshotter commands and enforcing vendor checks across both root and client modules.

## Important APIs, Types, and Functions
- Declares phony targets: `all`, `snapshot-controller`, `csi-snapshotter`, `snapshot-conversion-webhook`, `clean`, and `test`.
- Sets `CMDS=snapshot-controller csi-snapshotter snapshot-conversion-webhook`.
- `all: build` delegates build behavior to included release tooling.
- Includes `release-tools/build.make`.
- Adds `test-vendor-client`, and makes `test` depend on it.

## Control Flow
Make includes standard CSI build rules, then augments the test path so `test-vendor-client` runs `../release-tools/verify-vendor.sh` inside `client` and `hack/verify-vendor.sh` at the repository root.

## State and Persistence Behavior
Build targets may create binaries/images through `release-tools/build.make`; this file's explicit custom target only verifies vendored dependencies and does not persist changes.

## Dependencies and Integration Points
Depends on Kubernetes CSI release-tools, `client` as a nested module, and root `hack/verify-vendor.sh`. It is consumed by local developers, Prow, Cloud Build, and Trivy image builds.

## Risks
The root and client module vendor trees can diverge; the custom target mitigates this by checking both. If release-tools target names change, `all: build` or command builds can break.

## Test Signals
`make test-vendor-client` is the focused signal for vendor consistency. `make` and CI image builds exercise the included build rules.
