# sources/control-plane/longhorn-engine/app/cmd/stats.go

## Purpose
Defines the `journal` CLI command, which lists controller journal flush operations since the last flush.

## Important APIs, Types, and Functions
- `Journal()` returns a `cli.Command` with `--limit`.
- Action opens controller client and calls `JournalList(limit)`.

## Control Flow
The action creates a controller client, defers close, and invokes `JournalList`. Errors are fatal.

## State and Persistence Behavior
Read-only from this wrapper. It queries controller journal state; exact retention/flush behavior resides in controller implementation.

## Dependencies and Integration Points
Depends on `getControllerClient`, controller client `JournalList`, logrus, and urfave/cli.

## Risks and Edge Cases
No validation on `limit`; controller must interpret zero and negative values. Output formatting is owned by the client call.

## Test Signals
No direct tests in the listed subset. Metrics are covered in `integration/data/test_basic_ops.py`, but journal output is not.
