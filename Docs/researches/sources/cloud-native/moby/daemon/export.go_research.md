# sources/cloud-native/moby/daemon/export.go

Purpose: implements container filesystem export to a tar stream.

Important APIs and control flow: `ContainerExport` resolves the container, rejects Windows container export from unsupported daemons, rejects dead or removal-in-progress containers with conflict errors, delegates to `containerExport`, wraps errors with the requested name, and logs an export event on success. `containerExport` validates `RWLayer`, checks context cancellation, mounts the RW layer with the container mount label, defers unmount with warning-only logging, creates an uncompressed chroot tar with daemon ID mapping, closes the archive when context is cancelled, copies the archive to the output writer, maps cancellation during copy to `errdefs.Cancelled`, and logs `ActionExport`.

State, dependencies, and risks: state is the mounted RW layer and streamed tar reader. Dependencies include `chrootarchive.Tar`, archive compression options, ID mappings, container RWLayer, and daemon events. Export is a volatile snapshot: writes during copy can appear inconsistently. Risks include unmount failures, cancellation races while streaming, and unsupported Windows-container path. No direct tests appear here; behavior is covered through API/integration tests elsewhere.
