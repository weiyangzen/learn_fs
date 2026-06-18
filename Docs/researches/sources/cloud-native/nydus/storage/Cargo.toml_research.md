# sources/cloud-native/nydus/storage/Cargo.toml

## Purpose
This manifest defines the `nydus-storage` Rust crate, version `0.7.2`, the storage subsystem for Nydus Image Service. It acts as a feature-gated backend crate that can read blobs from local filesystems, local disks, OSS/S3-style object storage, container registries, HTTP proxy servers, and Dragonfly proxy integration.

## Important APIs, Types, and Feature Surface
The manifest exposes backend implementations through Cargo features rather than separate crates. Key feature flags are `backend-localdisk`, `backend-localdisk-gpt`, `backend-localfs`, `backend-oss`, `backend-registry`, `backend-s3`, `backend-http-proxy`, `backend-dragonfly-proxy`, and `dedup`. Optional dependencies map directly to those features: OSS pulls in `base64`, `httpdate`, `hmac`, `sha1`, `reqwest`, and `url`; S3 adds `http`, `sha2`, and `time`; HTTP proxy adds `hyper`, `hyperlocal`, `hyper-util`, `http-body-util`, `reqwest`, and `url`; Dragonfly proxy uses `dragonfly-client-util`; dedup uses `rusqlite`, `r2d2`, and `r2d2_sqlite`.

## Control Flow and Build Behavior
The crate is edition 2021 and relies on workspace crates `nydus-api`, `nydus-utils`, `vm-memory`, and `fuse-backend-rs`. Most source modules are conditionally compiled, so runtime behavior depends strongly on feature combinations. The `backend-localdisk-gpt` feature depends on `gpt` plus `backend-localdisk`, making GPT partition discovery an explicit opt-in extension.

## State, Persistence, and Dependencies
The manifest does not persist runtime state itself, but it declares dependencies that drive persistence in backend modules: `rusqlite` for dedup state, `gpt` for local disk partition tables, metrics via `nydus-utils`, and networking through `reqwest`, `hyper`, and `tokio`. Tokio is always included with runtime and synchronization features, while network client crates are optional.

## Integration Points
This crate integrates with `nydus-api` configuration types, `nydus-utils` metrics and singleflight helpers, FUSE memory slices from `fuse-backend-rs`, and optional cloud/proxy protocol clients. Docs.rs is configured to build all features for multiple common targets.

## Risks and Test Signals
The primary risk is feature matrix complexity: conditional modules can compile and behave differently depending on backend combinations. Tests in backend modules exercise many feature-specific paths, but live-network DNS tests and optional feature combinations require targeted CI coverage. Dependency versions are pinned broadly enough to receive semver-compatible updates, so network client behavior can shift without local code changes.
