# sources/distributed-fs/lizardfs/src/tools/recursive_remove.cc

Purpose: Implements `lizardfs rremove`, a long-running recursive delete command with task-id based cancellation support.

Important APIs/types/functions: `recursive_remove_run`; static `recursive_remove`; `cltoma::requestTaskId`; `matocl::requestTaskId`; `cltoma::recursiveRemove`; `matocl::recursiveRemove`; shared `signalHandler`.

Control flow: Resolves the target path, opens a master connection on its parent, requests a task id, starts a signal-handling thread bound to that job id, sends the recursive remove request, waits for the first non-NOP response with configurable timeout, deserializes status, joins the signal thread via `LambdaGuard`, and prints success or error.

State and persistence: Mutates namespace state through the master by deleting subtrees. Maintains temporary process signal mask/thread state and a master-side task id.

Dependencies and integration: Uses `ServerConnection`, `cltoma`/`matocl` task packets, `lambda_guard`, and common master connection helpers. Integrates with master async task infrastructure.

Risks and test signals: High operational risk due to deletion. Cancellation relies on signals and a secondary master connection in `signalHandler`. Timeout defaults to 60 seconds unless `-l` simulates long wait. No direct tests in this subset.
