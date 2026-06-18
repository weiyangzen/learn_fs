# sources/cloud-native/containerd/cmd/ctr/commands/images/tag.go

Purpose: implements `ctr images tag`, creating one or more new image references for an existing image.

Important APIs/functions: `tagCommand`.

Control flow: validates source and at least one target, creates client/context, then defaults to transfer-service mode unless `--local`. Transfer mode validates target references unless skipped and transfers from source store to each target store. Local mode creates a lease, fetches source image metadata, validates each target, attempts create, and if `--force` with already-exists, deletes and recreates.

State and persistence: creates image metadata references; local mode may delete existing target refs under force.

Dependencies/integration: transfer image store, image service, leases, Docker/distribution reference parser, errdefs.

Risks: force delete/create is not atomic. Transfer mode ignores `--force`; existing target behavior depends on transfer service.

Test signals: no local tests.
