<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/util.sh -->
# sources/control-plane/external-snapshotter/release-tools/util.sh

## Purpose
`util.sh` provides small Bash utility functions shared by release-tools verification scripts, mostly copied from Kubernetes helper conventions. It also centralizes ANSI color constants while marking them as intentionally sourced variables for shellcheck.

## Important APIs, Types, and Functions
Functions are `kube::util::sourced_variable`, `kube::util::sortable_date`, `kube::util::array_contains`, `kube::util::trap_add`, `kube::util::download_file`, `kube::util::wait-for-jobs`, `kube::util::join`, and `kube::util::check-file-in-alphabetical-order`. Constants are `color_start`, `color_red`, `color_yellow`, `color_green`, `color_blue`, `color_cyan`, and `color_norm`.

## Control Flow, State, and Persistence
The file is intended to be sourced. It mutates shell process state by defining functions, declaring readonly color variables once, and allowing callers to append trap handlers via `kube::util::trap_add`. `download_file` removes and rewrites a destination path, retrying curl up to five times. `wait-for-jobs` waits on all current background jobs and returns a failure count.

## Dependencies and Integration Points
Dependencies include Bash, `date`, `trap`, `awk`, `curl`, `seq`, `sleep`, `jobs`, `wait`, `diff`, and `sort`. `verify-shellcheck.sh` sources this file for trap composition and utilities.

## Risks and Test Signals
Risks include trap-command quoting complexity, Bash-only constructs, `download_file` deleting the destination before a successful replacement, and `wait-for-jobs` waiting for all shell jobs rather than a scoped list. Test signals are shellcheck coverage and successful use by scripts that source it, especially cleanup traps and alphabetized-file checks.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/util.sh -->
