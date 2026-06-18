<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-failpoint-binaries -->
# sources/cloud-native/containerd/script/setup/install-failpoint-binaries

- Purpose: Builds and installs failpoint-enabled binaries used by fault-injection tests.
- Important behavior: Runs make targets for `cni-bridge-fp`, `containerd-shim-runc-fp-v1`, `runc-fp`, and `loopback-v2`, then installs them into CNI or `/usr/local/bin` locations.
- Control flow: Resolve repository root from script path, build each failpoint binary, and `sudo install` it to configurable destination directories.
- State and persistence: Mutates host binary directories such as `/opt/cni/bin` and `/usr/local/bin`.
- Dependencies and integration: Requires make, Go, sudo, and corresponding make targets in the containerd tree. Used by integration tests that activate failpoints.
- Risks: Overwrites binaries in global paths; assumes failpoint make targets are supported on the host OS/arch.
- Test signals: Fault-injection integration tests and executable presence checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-failpoint-binaries -->
