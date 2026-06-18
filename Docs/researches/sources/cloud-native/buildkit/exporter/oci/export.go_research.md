# sources/cloud-native/buildkit/exporter/oci/export.go

Purpose: implements OCI and Docker image archive exporters. It commits image metadata and layers via `containerimage.ImageWriter`, builds an archive content provider, then either streams a tarball to the caller or copies content into a caller content store.

Important APIs and types: `ExporterVariant` distinguishes `client.ExporterOCI` and `client.ExporterDocker`; `Opt` carries session, image writer, variant, and lease manager; `Resolve` parses image commit opts and `tar`; `imageExporterInstance.Export` performs commit and transfer; `normalizedNames` parses and tag-normalizes comma-separated names.

Control flow: Docker variant rejects manifest lists. Metadata is cloned and augmented, annotations are parsed, OCI type defaults are set, and commit opts are validated. A temporary lease protects committed content until a `DescriptorReference` owns cleanup. Export response includes image digest, optional config digest, descriptor JSON as base64, and normalized image names. Refs are un-lazied concurrently, descriptors are added to a multiprovider, and archive export streams through `filesync.CopyFileWriter` when `tar=true`; otherwise a session content store receives the descriptor chain.

State and persistence: content is retained through leases and descriptor references. The caller receives either an archive stream or content-store blobs. Descriptor annotations may be mutated to expose response fields.

Dependencies and integration: integrates containerd archive exporter, BuildKit image writer, cache remotes, compression config, session/filesync/content, progress reporting, and gRPC error handling for `AlreadyExists`.

Risks and test signals: risks include Docker manifest-list incompatibility, lease cleanup on error, name parsing failures, lazy remote materialization failures, and incomplete stream close handling. Existing image exporter integration tests and normalized name behavior cover this surface.
