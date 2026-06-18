<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-logcheck.sh -->
# sources/control-plane/csi-driver-smb/release-tools/verify-logcheck.sh

Purpose: Runs `sigs.k8s.io/logtools/logcheck` against the repository to verify contextual klog usage.

Important behavior: Accepts optional logcheck version defaulting to `0.10.0`, resolves repo root, installs logcheck into a temporary directory with `go install`, and runs it with `-check-contextual -check-with-helpers` over `<root>/...`.

Control flow: Strict shell options abort on install or check failure. Trap removes the temporary install directory.

State and persistence behavior: Writes a temporary binary directory and uses Go module cache/network. No repo files should change.

Dependencies and integration points: Integrates with Go tooling and logcheck static analysis; useful for repos adopting contextual logging.

Risks: Requires network/module access unless cached. It scans the entire repo module pattern and can be sensitive to generated/vendor code if not excluded by module layout.

Test signals: Static logging API usage signal.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-logcheck.sh -->
