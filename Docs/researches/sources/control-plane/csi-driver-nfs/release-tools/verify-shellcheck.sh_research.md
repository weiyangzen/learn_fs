## sources/control-plane/csi-driver-nfs/release-tools/verify-shellcheck.sh

Purpose: verifies every tracked shell script in the NFS CSI repository with ShellCheck. It resolves `release-tools/util.sh`, accepts an optional root directory, gathers `*.sh` files while excluding generated/private, `.git`, and `vendor` paths, and also filters git-ignored files.

Important APIs and flow: `join_by` builds the comma-separated disabled rule list, `create_container` starts a long-lived `koalaman/shellcheck-alpine:v0.6.0` container, and `remove_container` cleans it through a release-tools trap. The script prefers a host `shellcheck` only when its reported version exactly matches `0.6.0`; otherwise it runs `docker exec` for each script.

State is limited to the fixed Docker container name `k8s-shellcheck` and the in-memory `errors` array. Dependencies include Docker, git, ShellCheck, Bash process substitution, and Kubernetes release-tool trap helpers. Risks are stale pinned ShellCheck version/image, collision with another container named `k8s-shellcheck`, and unchecked behavior when Docker is unavailable. Test signal is CI/static presubmit failure with collected ShellCheck output.
