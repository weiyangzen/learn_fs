# sources/control-plane/csi-lib-utils/release-tools/util.sh

## Purpose

`util.sh` provides shared bash helper functions for release-tools verifier scripts. Its most visible role is trap composition so cleanup handlers can be registered without overwriting existing traps.

## Important Behavior

The file defines Kubernetes-style shell utility helpers. `kube::util::sourced_variable` documents intentionally sourced globals for ShellCheck. `kube::util::sortable_date` emits sortable timestamps. `kube::util::array_contains` checks membership in an argument list. `kube::util::trap_add` prepends a command to existing traps for one or more signals. `kube::util::download_file` retries curl downloads up to five times. `kube::util::wait-for-jobs` waits for all current background jobs and returns a count-based failure status. `kube::util::join` joins arguments with a delimiter. `kube::util::check-file-in-alphabetical-order` diffs a file against `LC_ALL=C sort` and prints a repair command. The file also declares reusable ANSI color constants.

## State, Dependencies, and Integration

The helpers manipulate shell state in the current process: traps, readonly color variables, and function definitions. They have no file persistence except through commands that callers invoke. Integration points are verifier scripts that need cleanup, retrying downloads, background job waits, sorted-file checks, and shared shell UI conventions.

## Risks and Test Signals

Trap manipulation is subtle because quoting and signal lists must preserve existing handlers. `download_file` removes the destination before retrying, so callers should not point it at valuable files without expecting replacement. `wait-for-jobs` waits for all background jobs in the current shell, not just jobs started by one helper. Test signals are indirect through verifier scripts that source `util.sh`, particularly `verify-shellcheck.sh`.
