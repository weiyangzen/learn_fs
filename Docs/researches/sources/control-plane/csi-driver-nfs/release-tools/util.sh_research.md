# sources/control-plane/csi-driver-nfs/release-tools/util.sh

Purpose: shared shell utility functions and color constants for Kubernetes release-tools scripts.

Important APIs and functions: `kube::util::sourced_variable`, `kube::util::sortable_date`, `kube::util::array_contains`, `kube::util::trap_add`, `kube::util::download_file`, `kube::util::wait-for-jobs`, `kube::util::join`, `kube::util::check-file-in-alphabetical-order`, and color variables.

Control flow: utilities provide reusable operations: membership checks, trap composition, curl downloads with retries, waiting for background jobs with aggregate failures, delimiter joins, and sorted-file verification with helpful remediation output.

State and persistence behavior: `download_file` removes and rewrites destination files. `trap_add` mutates shell trap state. Color variables are declared read-only if not already set.

Dependencies and integration points: intended to be sourced by shell verification/release scripts. Depends on standard Unix tools such as date, curl, sleep, jobs, wait, diff, and sort.

Risks: `download_file` contains `2&> /dev/null`, which appears intended as `2>/dev/null` and may not redirect as expected. `trap_add` parses `trap -p` output with awk and can be fragile for complex quoted trap commands.

Test signals: no direct tests in this subset; behavior is exercised by scripts that source it.
