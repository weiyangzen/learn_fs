# sources/cloud-native/containerd/cmd/ctr/commands/images/export.go

Purpose: implements `ctr images export`, exporting image references as an OCI archive stream/file.

Important APIs/functions: `exportCommand`; local archive options and transfer archive options.

Control flow: validates output path and at least one image, opens stdout or creates output file, then chooses transfer-service mode by default or direct local mode with `--local`. Transfer mode builds `tarchive` platform/compatibility/non-distributable options, adds extra image references to an image store source, and calls `client.Transfer()` to an export stream with progress. Local mode builds `archive.ExportOpt` values and calls `client.Export()`.

State and persistence: writes an archive to stdout or a file; reads image/content metadata.

Dependencies/integration: transfer API, archive exporter, image store transfer source, platform parser, progress handler.

Risks: output file is created before export and may remain partial on failure. Transfer and local modes have separate option implementations with possible semantic drift. Platform flags require content availability.

Test signals: no local tests in this subset.
