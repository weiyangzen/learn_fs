<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-shellcheck.sh -->
# sources/control-plane/csi-driver-smb/release-tools/verify-shellcheck.sh

Purpose: Runs shellcheck over repository shell scripts, using either a matching host shellcheck binary or a pinned Docker image.

Important behavior: Sources `util.sh`, discovers `.sh` files excluding hidden/build/vendor/git-ignored paths, checks for host shellcheck version `0.6.0`, otherwise creates a long-lived Docker container and executes shellcheck inside it. It disables lint IDs 1090 and 2230 and aggregates all failures before exiting.

Control flow: Strict shell options plus explicit temporary disabling around shellcheck invocation to collect failures. `trap_add` cleans up the Docker container.

State and persistence behavior: May create/remove a Docker container named `k8s-shellcheck`; otherwise read-only.

Dependencies and integration points: Invoked by `.prow.sh`; depends on Docker if host shellcheck version is absent.

Risks: Pinning an old shellcheck version gives stable results but misses newer diagnostics. Docker dependency can fail in restricted CI. Discovery only covers `*.sh`, not extensionless shell entrypoints.

Test signals: Static shell lint signal for release-tools scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-shellcheck.sh -->
