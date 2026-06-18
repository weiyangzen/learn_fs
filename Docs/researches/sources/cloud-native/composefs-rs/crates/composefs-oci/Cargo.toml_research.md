## sources/cloud-native/composefs-rs/crates/composefs-oci/Cargo.toml

Purpose: this manifest defines `composefs-oci`, the crate that imports OCI/container images into composefs repositories, manages OCI metadata, supports containers-storage and optional boot image generation, and exposes test/varlink-adjacent feature surfaces.

Important configuration: default features include `containers-storage`. `test` enables tar generation, rand, and `composefs/test`. `boot` enables `composefs-boot`. `containers-storage` enables optional `composefs-storage` (`cstorage`), `base64`, and the cstorage user namespace helper. `varlink` enables `zlink-core` and `composefs/varlink`. Core dependencies include `composefs`, `containers-image-proxy`, `ocidir`, `cap-std-ext`, async/tokio utilities, compression libraries, serde/serde_json, sha2/hex, rustix, tar parsing crates, progress/tracing support, and optional storage/boot helpers.

Control flow and integration: feature selection determines which import paths are available. The modules in this work item use these dependencies for OCI layout imports, skopeo/proxy pulls, containers-storage direct/proxied imports, tar splitting, delta reconstruction, filesystem construction, and boot-image metadata rewriting.

State and persistence behavior: the manifest does not persist runtime state, but dependencies reveal that runtime code writes composefs splitstreams/objects, OCI config and manifest streams, image refs, referrers, and optional boot EROFS objects into repositories.

Test signals: dev-dependencies include `cap-tempfile`, `similar-asserts`, `composefs` test features, `composefs-boot`, `once_cell`, `proptest`, `tempfile`, and `tar`, indicating broad unit and integration coverage for tar round trips, filesystem semantics, generated images, boot handling, and property-style tests.

Risks: the default `containers-storage` feature pulls in platform- and environment-sensitive local storage behavior. Optional features must stay aligned with cfg usage in source files. Compression and OCI parsing libraries are security-sensitive because many code paths process untrusted image content.
