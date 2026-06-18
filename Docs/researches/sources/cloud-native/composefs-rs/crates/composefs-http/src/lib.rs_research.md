# sources/cloud-native/composefs-rs/crates/composefs-http/src/lib.rs

Purpose: provides an async downloader that fetches a named splitstream and all referenced splitstreams/objects from an HTTP endpoint into a composefs repository, verifying fs-verity IDs and SHA-256 splitstream body checksums.

Important APIs/types/functions: public API is `DownloadOptions { progress }` and `download(url, name, repo, opts) -> Result<(String, ObjectID)>`. Internal `Downloader` owns a `reqwest::Client`, repository `Arc`, base `Url`, and progress reporter. Key methods are `fetch`, `ensure_object`, `open_splitstream`, and `ensure_stream`. `INITIAL_CONCURRENT_REQUESTS` limits object fetch fan-out to 100.

Control flow: `download` builds a `Downloader` and calls `ensure_stream`. `ensure_stream` fetches `streams/<name>`; if the HTTP `Content-Type` is `text/x-symlink-target`, bytes are treated as an object pathname, otherwise the body is stored directly as an object. It recursively walks splitstream named refs, downloading missing splitstream objects, then collects all non-splitstream object refs. Object downloads run through a bounded `JoinSet` queue. After all objects are present, every splitstream is concatenated through `SplitStreamReader::cat` and verified against its recorded body checksum. Progress events report splitstream fetch messages, object started/progress/done, and verification messages.

State and persistence: downloaded objects are persisted through `Repository::ensure_object_async`; existing objects are reused. No remote state is mutated. The returned tuple is the top-level stream content digest (`sha256:...`) and fs-verity object ID.

Dependencies and integration points: depends on HTTP URL layout conventions: `streams/<name>` and `objects/<object-pathname>`. It uses `SplitStreamReader` to discover nested stream refs and object refs, `DigestWrite<Sha256>` to verify reconstructed stream content, and `composefs::progress` for observability.

Risks: symlink detection depends solely on exact content type; servers with charset parameters or different metadata will be treated as direct object data. Splitstream recursion is sequential except object fetches, and verification is also sequential. `ensure_object` considers any `open_object` error as absence, which can mask permission/corruption errors until later. Concurrent fetch count is fixed rather than configurable. Error messages include expected/measured digest information but all failures collapse to `anyhow::Error`.

Test signals: useful tests would serve synthetic HTTP repositories with nested splitstreams, duplicate refs with conflicting body hashes, object fs-verity mismatches, direct-vs-symlink stream responses, HTTP failures, and progress counts. This subset does not include direct tests for the crate.
