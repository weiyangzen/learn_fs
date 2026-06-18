# sources/control-plane/longhorn/scripts/lhexec

## Purpose
Convenience wrapper to execute Longhorn engine commands for a named volume by locating the running engine instance manager and invoking the engine binary through `kubectl exec`.

## Important APIs and Functions
Uses namespace `longhorn-system`. `print_usage` documents volume and command arguments. `check_volume_exist` verifies `lhv` custom resource existence. `check_engine_state` queries `lhe` resources for the volume's `.status.currentState`. `exec_command` queries `.status.instanceManagerName` and `.status.port`, discovers the Longhorn binary path from process command lines, then runs it with `--url localhost:<port>`.

## Control Flow
The script handles help/empty arguments, defaults missing command args to `help`, validates volume and engine state, and delegates to `exec_command`. JSONPath filters select Longhorn engine CRs by `spec.volumeName`.

## State and Persistence
The script itself persists nothing. Invoked engine subcommands may read or mutate volume engine state, snapshots, replicas, or metadata depending on arguments.

## Dependencies and Integration Points
Requires `kubectl` access to the Longhorn namespace and CRDs `lhv`/`lhe`. Depends on instance-manager pods supporting `bash`, `ps`, `grep`, `awk`, and the Longhorn engine process command shape.

## Risks
Command arguments are interpolated into a remote shell string, so quoting and injection risks exist if untrusted values are passed. `kubectl exec -it` can misbehave in non-TTY automation. If multiple engines match, JSONPath output may concatenate values. Binary discovery by process grep is fragile.

## Test Signals
Use `lhexec <volume> help` on a known running volume. Negative tests should cover missing volume, stopped engine, and command args with spaces. A safer future test would assert generated `kubectl` calls in a mocked environment.
