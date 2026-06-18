# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/post-receive

## Purpose
Git server post-receive hook that queues CI builds.

## Behavior
- Watches pushes to `refs/heads/master` and tags matching `refs/tags/v*`.
- Writes the target commit hash to `$STATE_DIR/desired`.
- Signals the orchestrator with `SIGUSR1` using `$STATE_DIR/orchestrator.pid` if present.
- Resolves annotated tags to their commit via `git rev-parse "$newrev^{commit}"`.

## Integration
This is the event source for the reconcile-loop CI daemon. There is no queue; the desired file always points to the latest requested commit.
