# sources/cloud-native/nydus/contrib/nydus-backend-proxy/src/main.rs

## Purpose
This Rust binary implements a simple Rocket HTTP server that behaves like enough of a registry blob backend for Nydus clients. It serves files from a blob directory under registry-style `/namespace/repo/blobs/sha256:<digest>` routes, with whole-file and range-read support.

## Important APIs, Types, and Functions
`BlobBackend` stores the root directory and a digest-to-open-file map. `BLOB_BACKEND` is a global async mutex. Routes are `check` for `HEAD` and `fetch` for `GET`. `FileStream` and `RangeStream` implement Rocket responders. `HeaderData` extracts `Host` and `Range` headers. `init_blob_backend` and `populate_blobs_map` initialize and refresh blob state.

## Control Flow
`main` parses required `--blobsdir`, initializes the backend map, mounts routes plus a static file server, and launches Rocket. `fetch` validates the `sha256:` prefix, serves the full file through `NamedFile` when no `Range` header is present, or looks up/repopulates the open-file map and streams bytes using `pread` for range requests. `check` validates the digest and returns a responder if the file exists.

## State, Persistence, and Dependencies
The server state is global in-memory mapping of blob file names to `Arc<fs::File>`. Persistent data is the supplied blob directory. Dependencies include Rocket, `http_range`, `nix::sys::uio`, `clap`, `lazy_static`, and standard filesystem APIs.

## Integration Points
It integrates with Nydus daemon storage flows that expect registry-like blob checks and reads. Docker headers such as `Docker-Content-Digest` and `Content-Range` are emitted for compatibility.

## Risks and Test Signals
Range handling uses only the first parsed range and reports `Content-Range` total as range length rather than full object size, which may be semantically incorrect. The global mutex guards map access but readdir refresh is coarse. `populate_blobs_map` panics if the root directory cannot be read. Digest names are accepted after prefix trimming without validating SHA-256 hex. No tests are visible for this binary.
