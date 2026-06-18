# sources/cloud-native/moby/integration/container/export_test.go

Purpose: Validates container rootfs export and import, including export after daemon restart.

Important APIs and flow: `TestExportContainerAndImportImage` runs a container, waits for stop, calls `ContainerExport`, feeds the stream into `ImageImport`, decodes a `jsonstream.Message`, and compares its status to an `ImageList` result filtered by reference. `TestExportContainerAfterDaemonRestart` uses a child daemon, creates a container, restarts dockerd, and ensures `ContainerExport` still returns a stream.

State and dependencies: Creates a new image reference through import and exercises daemon metadata persistence across restart. Skips Windows and remote daemon for restart control.

Risks and signals: It detects broken export streams, image import output mismatch, and failure to export containers created before the current daemon process. It is a storage metadata and tar stream integration signal.
