# sources/cloud-native/containerd/cmd/ctr/commands/images/push.go

Purpose: implements `ctr images push`, uploading local image content to a remote registry.

Important APIs/types/functions: `pushCommand`, `pushjobs`, `newPushJobs()`, `pushjobs.add()`, and `pushjobs.status()`.

Control flow: validates remote ref, creates client/context, then defaults to transfer-service mode unless `--local`. Transfer mode rejects local-only flags, creates credentials/registry destination, resolves local ref defaulting to remote ref, configures optional platform filters, and calls `client.Transfer()` with progress. Local mode resolves manifest descriptor either from `--manifest` or local image metadata, optionally narrows to one platform manifest, enables HTTP trace, builds resolver, starts an errgroup for `client.Push()` plus progress rendering, skips non-distributable blobs unless allowed, applies max concurrent upload option, and waits.

State and persistence: reads local content/image metadata and writes remote registry blobs/manifests. Progress status uses Docker status tracker state.

Dependencies/integration: transfer registry/image APIs, remotes/docker status tracker, content progress display, errgroup, platform/image child traversal, resolver helpers.

Risks: default transfer path rejects many registry flags that local path supports. In local platform narrowing, if no matching manifest is found the descriptor may remain the index. Non-distributable blobs are skipped by both handler and wrapper when not allowed.

Test signals: no local tests in this subset.
