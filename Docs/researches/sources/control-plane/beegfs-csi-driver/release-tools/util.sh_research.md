# sources/control-plane/beegfs-csi-driver/release-tools/util.sh

Purpose: Shared shell utility library imported by release tooling. It provides small helpers for dates, arrays, traps, downloads, job waits, joins, sorted-file checks, and terminal colors.

Important APIs/types/functions: `kube::util::sourced_variable`, `kube::util::sortable_date`, `kube::util::array_contains`, `kube::util::trap_add`, `kube::util::download_file`, `kube::util::wait-for-jobs`, `kube::util::join`, and `kube::util::check-file-in-alphabetical-order`. Defines color variables when unset.

Control flow: Functions are passive until sourced and called. `trap_add` prepends a new command to existing traps. `download_file` removes destination, retries curl up to five rounds with curl's own retry count, and reports success/failure. `wait-for-jobs` waits on all background jobs and returns number of failures as status. Color initialization declares readonly variables and marks them as intentionally sourced.

State and persistence: `download_file` writes/removes destination files. `trap_add` mutates shell trap state. Color definitions create readonly shell variables in the caller environment.

Dependencies and integration points: Based on Kubernetes release utility conventions. Uses bash features, curl, diff, sort, awk, and process substitution. Intended to be sourced by other release scripts.

Risks: Requires bash despite some release scripts using `/bin/sh`; this file should only be sourced from bash. `wait-for-jobs` returns failure count, which can exceed portable shell status range if many jobs fail. `download_file` has a typo-like redirection `2&> /dev/null` that is unusual and may not behave as intended in all shells.

Test signals: No direct tests in this subset. Behavior is exercised by scripts that source it.
