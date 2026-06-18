# sources/cloud-native/buildkit/exporter/tar/export.go

Purpose: implements the `tar` exporter, reusing local export filesystem construction and sending the resulting filesystem as a tar stream to the client.

Important APIs and functions: `Opt` carries `session.Manager`; `New` and `Resolve` create `localExporterInstance`; `Export` orchestrates `local.CreateFS`, platform subdirectory assembly, session lookup, writer creation, and `writeTar`.

Control flow: options are parsed with `local.CreateFSOpts.Load`. Export resolves epoch from source metadata when needed, validates multi-ref platform mapping, builds per-platform `fsutil.Dir` entries, wraps multi-platform map exports with `fsutil.SubDirFS`, then obtains a filesync writer and streams a tar archive. Cleanup functions are stored and invoked in reverse order.

State and persistence: no server-side durable state; mounted refs and temp dirs are released by deferred cleanup. Output persists only as the client-received tar stream.

Dependencies and integration: depends on `exporter/local` for filesystem and attestation preparation, `exptypes` for platform mapping, session/filesync for transport, and platform-specific `writeTar` implementations.

Risks and test signals: risks include missing platform mappings, cleanup order, `CopyFileWriter`/tar close errors, and platform-split differences from local exporter delete/copy modes. It shares most behavior with local exporter tests and platform-specific tar tests.
