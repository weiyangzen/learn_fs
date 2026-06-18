# sources/control-plane/csi-lib-utils/release-tools/verify-logcheck.sh

## Purpose

This verifier runs `sigs.k8s.io/logtools/logcheck` to check contextual klog usage in the CSI lib utils source tree.

## Important Behavior

It accepts an optional logcheck version, defaulting to `0.10.0`. It canonicalizes the repository root as the parent of release-tools, creates a temporary `GOBIN`, installs `logcheck` with `go install`, and runs it with `-check-contextual -check-with-helpers` over the repository.

## State, Dependencies, and Integration

It creates a temporary directory removed by trap. Dependencies are bash, Go, network/module access, and the logcheck module. It integrates with CI or local verification for klog contextual logging standards.

## Risks and Test Signals

Installing a tool on every run can be slow and sensitive to module proxy/network issues. The fixed default version stabilizes checks. Test signal is the logcheck exit code and diagnostics.
