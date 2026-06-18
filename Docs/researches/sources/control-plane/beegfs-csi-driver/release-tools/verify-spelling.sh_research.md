<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-spelling.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/verify-spelling.sh

Purpose: spelling verification for tracked source files, excluding vendor content.
Important APIs/functions: installs `github.com/client9/misspell/cmd/misspell@v0.3.4` into a temporary `GOBIN` when no host `misspell` binary exists, then runs `git ls-files | grep -v vendor | xargs misspell`.
Control flow/state: creates a temp directory, registers an EXIT cleanup handler, writes misspell output to `errors.log`, prefixes emitted diagnostics with `error:`, and exits with status 1 when the log is non-empty. It does not persist repo state unless a host/tool install unexpectedly writes outside the temp directory.
Dependencies/integration: requires git, Go toolchain for on-demand install, network/module cache access when `misspell` is missing, and POSIX tools.
Risks/test signals: `grep -v vendor` is broad and may skip paths containing that token outside dependency trees; `xargs` may be sensitive to odd filenames; the tool version is old. Empty `errors.log` is the pass signal.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-spelling.sh -->
