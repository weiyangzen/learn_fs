# sources/cloud-native/containerd/cmd/ctr/commands/images/import.go

Purpose: implements `ctr images import`, importing OCI/Docker archive streams into containerd with optional unpacking and reference translation.

Important APIs/functions: `importCommand`; transfer import options; local `containerd.ImportOpt` construction.

Control flow: command creates client/context and chooses transfer-service mode by default or local direct mode with `--local`. Transfer mode rejects `--discard-unpacked-layers`, computes base prefix and digest/named reference options, chooses unpack platform, opens stdin/file, creates an import stream, and calls `client.Transfer()` with progress. Local mode builds archive ref translators, digest/index/compression/platform/all-platform/discard-label options, creates a lease, opens input, calls `client.Import()`, closes input, and unpacks each imported image unless `--no-unpack`.

State and persistence: writes content blobs, image metadata, optional unpacked snapshots, and temporary lease state; reads archive from stdin or file.

Dependencies/integration: containerd import APIs, transfer archive/image APIs, diff apply sync-fs, platform matching, leases, logging.

Risks: transfer and local paths differ: transfer only unpacks one platform even with all-platforms. `--discard-unpacked-layers` requires local and conflicts with `--no-unpack`. Auto-generated import prefixes use the current date and may overwrite named annotations in transfer mode.

Test signals: no local tests in this subset.
