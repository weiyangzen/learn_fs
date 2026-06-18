# sources/control-plane/csi-driver-iscsi/release-tools/verify-logcheck.sh

Purpose: verifies contextual logging usage with `sigs.k8s.io/logtools/logcheck`.

Important APIs and types: optional first argument is `LOGCHECK_VERSION`, default `0.10.0`. It computes `CSI_LIB_UTIL_ROOT` as the parent of release-tools and installs `logcheck` into a temp `GOBIN`.

Control flow: strict shell mode, create temp dir with cleanup trap, `go install` the requested logcheck version, then run `logcheck -check-contextual -check-with-helpers <root>/...`.

State and persistence: temporary binary directory only, deleted on exit. Does not change repo files.

Dependencies and integration: depends on Go module install, network access, and logcheck support for the target codebase.

Risks: variable names mention `CSI_LIB_UTIL` even though this is release-tools. Installing at runtime makes the verifier dependent on external module availability.

Test signals: nonzero exit from logcheck indicates logging violations.
