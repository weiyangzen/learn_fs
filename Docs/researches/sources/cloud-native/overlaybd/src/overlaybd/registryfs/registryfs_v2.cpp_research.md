# sources/cloud-native/overlaybd/src/overlaybd/registryfs/registryfs_v2.cpp

## Purpose
Implements the newer Photon HTTP-client based registry filesystem and streaming uploader. It supports read-only ranged registry blob access, bearer/basic auth, redirect and metadata caches, TLS context loading, custom user-agent selection, and chunked blob upload with sha256 digest finalization.

## Important APIs and Types
`RegistryFSImpl_v2`, `RegistryFileImpl_v2`, and `RegistryUploader` are the central classes. Important methods include `get_data`, `get_actual_url`, `get_scope_auth`, `authenticate`, `refresh_token`, `refresh_client`, `RegistryFileImpl_v2::preadv`, `get_length`, `RegistryUploader::write`, `fsync`, `init_upload`, `upload_thread`, `upload_chunk`, `new_tls_context_from_file`, `new_registryfs_v2`, `new_registry_uploader`, and `registry_uploader_fini`.

## Control Flow
Reads resolve authentication and redirect state, issue ranged GETs through `HTTP_OP`, and read response bytes into caller iovecs. Upload starts a background std::thread with its own Photon runtime, initializes an upload URL by POST, uploads staged local-file chunks via PATCH as writes advance, computes sha256 on incoming writes, and completes with a PUT containing the digest.

## State and Persistence
Read-side state includes HTTP client, TLS context, metadata cache, scope-token cache, actual-URL cache, user agent, timeout, and acceleration URL. Upload-side state includes local staging file, write/upload positions, semaphores, upload URL, token, chunk buffer, SHA256 context/sum, and failure/finished flags.

## Dependencies and Integration Points
Uses Photon HTTP client, TLS stream utilities, localfs, Base64 utilities, RapidJSON, OpenSSL SHA256, std::thread, and version metadata. It is the implementation behind `registryfs.h` v2 exports.

## Risks
Ownership of TLS context is shared into uploader-created filesystem instances and needs care to avoid double-free or use-after-free. Upload retry restarts from position zero and must be compatible with local staged data. `read_file` uses a fixed 4096-byte buffer while reading `st.st_size`, risking overflow for larger cert/key files. Authentication challenge parsing was improved for quoted commas but is still custom parsing.

## Test Signals
Tests should cover bearer and basic reads, redirects, custom UA, proxy/acceleration, TLS cert/key loading, token refresh on 401/403, ranged resource-size detection, chunk upload range handling, final digest matching, and upload retry behavior.
