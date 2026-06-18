## sources/control-plane/csi-driver-smb/.github/workflows/shellcheck.yaml

Purpose: runs ShellCheck over repository shell scripts on master/release pushes, version tags, and pull requests to master/release branches.

Important behavior: it uses the pinned `ludeeus/action-shellcheck` action with warning severity, checks scripts together, emits GCC format, disables SC2034, and ignores `vendor`, `release-tools`, and `hack`.

State is read-only CI analysis. Dependencies are checkout and the action's bundled ShellCheck. Risks include warning-level severity possibly allowing risky scripts, ignored `hack` and `release-tools` scripts escaping coverage, and global SC2034 suppression. Test signal is static shell lint output in GitHub Actions.
