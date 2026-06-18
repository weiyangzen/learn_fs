<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-shellcheck.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/verify-shellcheck.sh

Purpose: repository lint gate for shell scripts. It discovers tracked `*.sh` files under the selected root, filters ignored paths with `git check-ignore`, excludes `_`, `.git`, and vendor trees, and runs shellcheck 0.6.0 either from the host or from the pinned `koalaman/shellcheck-alpine` image.
Important APIs/functions: sources `release-tools/util.sh` for `kube::util::trap_add`, defines `join_by`, `create_container`, and `remove_container`, and passes a comma-separated disabled lint list for SC1090 and SC2230.
Control flow/state: changes to the root directory, builds `all_shell_scripts`, checks host shellcheck version, starts a long-lived Docker container when needed, execs shellcheck for each file, accumulates non-empty diagnostics, and fails at the end if any diagnostics were collected. Persistent state is limited to the temporary Docker container named `k8s-shellcheck`, removed on EXIT.
Dependencies/integration: depends on git, shellcheck or Docker, the pinned image digest, and the repo's ignore rules. It is meant for release/Prow style verification.
Risks/test signals: fixed container name can collide with a concurrent run; the required shellcheck version is old; docker-only fallback fails in rootless/containerless CI. Success signal is the congratulatory message; failure prints all shellcheck diagnostics.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-shellcheck.sh -->
