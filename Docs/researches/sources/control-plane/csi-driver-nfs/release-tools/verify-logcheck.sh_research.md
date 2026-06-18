# sources/control-plane/csi-driver-nfs/release-tools/verify-logcheck.sh

Purpose: verifies contextual klog usage with the `sigs.k8s.io/logtools/logcheck` tool.

Important variables and commands: strict shell options, `LOGCHECK_VERSION` positional default `0.10.0`, `CSI_LIB_UTIL_ROOT`, a temporary install directory, `go install sigs.k8s.io/logtools/logcheck@v<version>`, and `logcheck -check-contextual -check-with-helpers <root>/...`.

Control flow: resolves the repository root as the parent of release-tools, creates a temp directory, installs the requested logcheck version into it, runs logcheck against all packages, and removes the temp directory on exit.

State and persistence behavior: writes only the temporary binary directory and Go module cache side effects from `go install`.

Dependencies and integration points: used by CI verification for repositories that have migrated to contextual logging conventions. Depends on Go tooling and network/module access unless cached.

Risks: always installs at runtime, which can be slow or fail due to network/module proxy issues. The variable name `CSI_LIB_UTIL_ROOT` is generic from another repo and may be confusing but resolves correctly.

Test signals: nonzero logcheck exit fails the verification job and points to logging call sites.
