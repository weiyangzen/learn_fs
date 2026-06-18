## sources/control-plane/csi-driver-iscsi/.github/workflows/shellcheck.yaml

Purpose: runs ShellCheck for repository scripts on version-tag/master/release pushes and matching pull requests.

Control flow checks out code and invokes `ludeeus/action-shellcheck` with warning severity, together mode, GCC format, and `SHELLCHECK_OPTS=-e SC2034`. It ignores vendor, release-tools, and hack paths.

State is workflow output only. Dependencies are pinned shellcheck action. Risks include ignoring the `hack` directory where many repo scripts live, so this workflow misses most listed shell scripts; separate `hack/verify-all.sh` covers some of that on Linux. Test signal is shellcheck annotations for non-ignored scripts.
