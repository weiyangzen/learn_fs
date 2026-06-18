# sources/cloud-native/moby/daemon/internal/builder-next/worker/worker.go

## Purpose
Implements Docker's local BuildKit worker over Moby layer storage, snapshot/content/cache managers, daemon image source, registry metadata, and Moby exporters.

## APIs, Control Flow, and Integration
`Opt` wires executor, snapshotter, cache/content/lease managers, image source, download manager, v2 metadata service, registry transport, exporter, layer access, platforms, CDI, and proxy provider. `NewWorker` registers image, git, HTTP, and local sources. The worker implements identity/labels/platforms/GC/version/close, source metadata resolution for image/git/http, LLB op resolution, exporters, disk usage/prune, remotes conversion, cache-mount pruning, and remote import.

## State, Dependencies, and Risks
State spans BuildKit cache refs, Moby layers, containerd content, leases, v2 distribution metadata, and source managers. `GetRemotes` can finalize/extract refs and ensure Moby layers; `FromRemote` downloads descriptors into the layer store, deletes content blobs after import, and reconstructs cache refs with creation/description annotations. Risks include source registration only warning on failure, no source-policy support, attestation-chain rejection without containerd image store, mutable platform cache in `Platforms(noCache)`, and metadata Add errors ignored in `layerDescriptor.Registered`. `worker_test.go` covers platform merging only.
