# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/commiter.go

Purpose: implements committing a running container's changes into a new Nydus image.

Important APIs and flow: `Opt` carries workdir, containerd address/namespace, container ID, image refs, max commit count, fs/compressor options, and selected include/exclude paths. `NewCommitter` prepares a temp workdir and container manager. `Commit` resolves short container IDs, inspects containerd state, pulls the base Nydus bootstrap, enforces maximum committed layers, discovers fs version/compressor via `nydus-image check`, pushes lower blobs, syncs filesystems, pauses the container, commits upperdir diff and requested mount paths as Nydus blobs, commits appended mount paths discovered during diff, merges bootstraps, and pushes config/bootstrap/manifest. Helper functions cover bootstrap pulling, upper diff packing, blob pushing from local files or remote source layers, pausing/unpausing, namespace sync, descriptor generation, mount copying with `nsenter tar`, bootstrap merging, retry, target ref validation, bootstrap info extraction, and short ID resolution.

State and persistence: creates temp workdir files for base bootstrap, upper/mount blobs, merged bootstrap tar/gz, and output JSON. It pauses/resumes containers, runs host and namespace `sync`, reads remote images, and pushes blobs/manifests. It mutates the target image manifest/config diff IDs and Nydus commit annotations.

Dependencies and integration: ties together containerd manager, parser/provider remotes, snapshotter-converter pack/merge, overlay diff package, nsenter, local content readers, OCI descriptors, distribution source labels, and Nydus annotation constants.

Risks and test signals: high operational risk due to container pause windows, mount namespace access, overlay diff correctness, remote push retry with reused readers, and external command dependence. Lower blob detection by `blob-mount-` name overlaps explicit mount blob names, so call context matters. Close errors in `pushBlob` are captured in a deferred variable but checked before deferred close runs, making close failures effectively lost.
