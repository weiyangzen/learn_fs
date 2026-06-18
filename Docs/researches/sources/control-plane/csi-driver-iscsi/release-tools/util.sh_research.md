# sources/control-plane/csi-driver-iscsi/release-tools/util.sh

Purpose: shared shell utility functions and color constants borrowed from Kubernetes-style hack scripts.

Important APIs and types: functions include `kube::util::sourced_variable`, `sortable_date`, `array_contains`, `trap_add`, `download_file`, `wait-for-jobs`, `join`, and `check-file-in-alphabetical-order`. It also declares ANSI color variables when not already set.

Control flow: utility functions are sourced by other scripts and execute only when called. `trap_add` composes new trap commands with existing ones. `download_file` retries curl downloads. `wait-for-jobs` aggregates background job failures.

State and persistence: modifies shell traps and color variables in the caller context. `download_file` writes the requested destination file.

Dependencies and integration: used by `verify-shellcheck.sh`; depends on bash, curl, date, diff, sort, awk, and shell job control.

Risks: `rm "${destination_file}" 2&> /dev/null` appears typo-like and may not redirect as intended. Trap composition evaluates command strings early by design. These utilities assume bash, not POSIX sh.

Test signals: scripts sourcing this file pass shellcheck and runtime validation.
