# sources/control-plane/longhorn/scripts/migrate-for-pre-070-volumes.sh

## Purpose
Wrapper for the Longhorn manager's `migrate-for-pre-070-volumes` command, used to migrate old pre-0.7.0 Longhorn volumes by volume name or `--all`.

## Important APIs and Functions
Namespace constant `NS=longhorn-system`; `print_usage`; `exec_command` finds a `longhorn-manager` pod via `kubectl get po -l app=longhorn-manager`, then runs `longhorn-manager migrate-for-pre-070-volumes` inside it.

## Control Flow
Help or empty argument prints usage. Otherwise the script warns if more than one argument is passed, then forwards all args to the manager command.

## State and Persistence
The wrapper persists nothing locally, but the manager command mutates Longhorn volume metadata/state for old volumes.

## Dependencies and Integration Points
Requires `kubectl`, Longhorn manager pods, and manager binary support for the migration command. Integrates with Longhorn CR/state migration workflows.

## Risks
It selects the second line of tabular `kubectl get po` output instead of using JSONPath, so output changes can break selection. It does not exit after detecting too many arguments. `kubectl exec -it` may fail in noninteractive contexts.

## Test Signals
Test `--help`, a dry/non-mutating manager invocation if available, and `--all` in a controlled cluster. Confirm old volumes become compatible and no unrelated volumes are modified.
