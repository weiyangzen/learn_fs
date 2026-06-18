<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/util.sh -->
# sources/control-plane/csi-driver-smb/release-tools/util.sh

Purpose: Shared shell utility functions and color constants for release-tools verification scripts.

Important APIs/functions: `kube::util::sourced_variable` documents externally used variables for shellcheck. `sortable_date` prints sortable timestamps. `array_contains` checks membership. `trap_add` composes multiple commands on a signal. `download_file` retries curl downloads. `wait-for-jobs` waits for all background jobs and returns failure count. `join` joins arguments with a delimiter. `check-file-in-alphabetical-order` diffs a file against `LC_ALL=C sort`. Color constants are declared once and marked as sourced variables.

Control flow: Functions are sourced by other scripts and do not execute substantive work at source time beyond defining colors if unset.

State and persistence behavior: Can set traps and declare readonly color variables in the caller shell. `download_file` removes and writes destination files.

Dependencies and integration points: Used at least by `verify-shellcheck.sh`; useful for broader Kubernetes-style scripts.

Risks: `trap_add` evaluates trap command strings while building traps, requiring careful quoting by callers. `download_file` removes the destination before confirming a replacement can be downloaded.

Test signals: No direct tests; shellcheck coverage via release-tools verifiers.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/util.sh -->
