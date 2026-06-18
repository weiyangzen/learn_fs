<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/replace.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/replace.go

Purpose: creates a container while cleaning up stale containerd state if the requested ID already exists.

Important APIs and types: `ReplaceContainer(ctx, client, id, spec, shim, runtimeOptions, opts...)`.

Control flow: first tries `client.NewContainer`. On non-conflict success/failure it returns immediately. On conflict, it loads the stale container, loads its task if present, force-deletes the task, deletes the container, then retries creation. Not-found during cleanup is treated as a race that can proceed.

State and persistence: mutates containerd state by deleting stale task/container objects and creating a replacement. It does not persist state itself.

Dependencies and integration: used by the plugin containerd executor and likely other daemon container creation paths. It depends on the abstract `libcontainerd/types.Client` and `errdefs` classification.

Risks: if task loading fails with an unknown error, the function refuses to delete the container because deletion would likely hit the same task error. Force-deleting a stale task is destructive by design. Errors are wrapped, so callers need errdefs-aware unwrapping.

Test signals: no direct tests in this subset; correctness depends on integration with containerd error mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/replace.go -->
