# sources/control-plane/external-snapshotter/client/hack/run-cel-tests.sh

## Purpose
Runs server-side admission/CEL validation fixtures under `client/hack/cel-tests`.

Source size: 112 lines, 2772 bytes.

## Important APIs, Types, and Functions
- Shell functions: `exec_case`, `exec_tx_case`.
- External commands/helpers: `find`, `grep`, `kubectl`.

## Control Flow
- Parses optional `-v/--verbose` and rejects unknown arguments.
- `exec_case` dry-runs each YAML with `kubectl apply --dry-run=server` and compares success/failure to adjacent `.err` files.
- `exec_tx_case` applies each `.pre.yaml`, applies the matching `.post.yaml`, checks `.tx_err` expectations, deletes the post resource, and counts successes/failures.
- Exits non-zero if any fixture outcome differs from expectation.

## State and Persistence
- Writes temporary `.out` files beside fixtures.
- Transaction tests create real API objects for the pre-state and clean up using the post manifest.
- Counters are process-local.

## Dependencies and Integration Points
- kubectl connected to a cluster with snapshot CRDs installed.
- Fixture `.err` and `.tx_err` files containing expected validation substrings.
- Bash, find, grep, and server-side Kubernetes dry-run support.

## Risks and Edge Cases
- Exact error text matching can be brittle across Kubernetes versions.
- Transaction cleanup uses the post manifest and may leave pre-state if apply/delete paths fail unexpectedly.
- The first loop includes `.pre.yaml` and `.post.yaml` as standalone YAMLs before transaction tests, which is intentional but can surprise maintainers.

## Test Signals
- The script is the executable test harness for all CEL fixtures in this subset.
