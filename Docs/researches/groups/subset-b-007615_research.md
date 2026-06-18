# Research: subset-b-007615

This grouped report covers the requested JuiceFS object storage adapters and VFS support files. Each section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/oss.go -->
# sources/distributed-fs/juicefs/pkg/object/oss.go

Purpose: implements the Alibaba Cloud OSS `ObjectStorage` backend behind the `oss` scheme when `!nooss` is enabled. It adapts the v2 Aliyun OSS SDK to JuiceFS operations: bucket creation, object head/get/put/copy/delete/list, restore, multipart upload, and pending multipart listing.

Important APIs and types: `ossClient` embeds `tierStorage` and exposes `String`, `Limits`, `Create`, `Head`, `Get`, `Put`, `Copy`, `Delete`, `List`, multipart methods, `Restore`, `autoOSSEndpoint`, and `newOSS`. `Limits` advertises OSS multipart and upload-part-copy bounds. `newOSS` parses bucket endpoints, pulls credentials from explicit args or Aliyun environment/default credential chain, determines endpoint and region, chooses signature v1/v4, configures checksums, timeouts, user agent, and shared `httpClient`.

Control flow and state: object calls are thin SDK requests with provider-specific error translation. `Head` maps 404 service errors to `os.ErrNotExist`; `Create` treats existing buckets as success; `Get`, `Put`, and `Delete` write `ResponseAttrs` request IDs and storage class when callers requested them. Full `Get` responses may be wrapped in `verifyChecksum` if checksum metadata exists. Multipart methods marshal JuiceFS `Part`/`MultipartUpload` to OSS SDK types.

Persistence and integration: data persists in one OSS bucket, with optional tier storage class and tags. Registration happens in `init` via `Register("oss", newOSS)`. It depends on shared object helpers (`obj`, `Tier`, checksum helpers, `httpClient`, `UserAgent`) and Aliyun credential providers.

Risks and test signals: region/endpoint inference is complex, especially private link and auto endpoint discovery. `ListUploads` uses `ListParts` keyed by `marker`, which may not enumerate all uploads like a true multipart-upload listing. Request-id propagation is present but not directly tested here; no OSS-specific tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/oss.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/prefix.go -->
# sources/distributed-fs/juicefs/pkg/object/prefix.go

Purpose: provides `WithPrefix`, a transparent `ObjectStorage` decorator that roots all key-based operations under a prefix, plus helpers for deriving parent-directory storage and detecting filesystem-like stores.

Important APIs and types: `withPrefix` wraps an `ObjectStorage`; `WithPrefix` constructs it; `DirStorage` unwraps encryption layers and converts file-like roots to parent directories; `withFile` and `withObj` adapt returned `File`/`Object` instances so `Key()` is relative to the prefix while preserving `Sys()` when available. The wrapper implements normal object methods, multipart, filesystem extension methods (`Chmod`, `Chown`, `Chtimes`), symlink methods, stream upload, restore, and tier support pass-through.

Control flow and state: mutating and lookup methods prepend `p.prefix` before delegating. `Head`, `List`, and `ListAll` call `updateKey` to strip the prefix from returned keys; for known concrete objects it mutates the key, otherwise it wraps the object. `Get` rejects the invalid range combination `off > 0 && limit < 0`. `Copy` delegates without prefixing, while `UploadPartCopy` prefixes both source and destination keys.

Persistence and integration: it changes namespace mapping only; persistence remains in the wrapped backend. It integrates with encryption wrappers, `filestore`, tier, symlink, and filesystem optional interfaces.

Risks and test signals: `Copy` not prefixing differs from most key operations and relies on callers supplying already-correct keys. `ListAll` uses a goroutine and fixed 10240 buffer, so slow consumers retain memory. Tests in `prefix_test.go` cover `DirStorage` directory/file prefix handling and filestore roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/prefix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/prefix_test.go -->
# sources/distributed-fs/juicefs/pkg/object/prefix_test.go

Purpose: validates parent-directory derivation for object storages that may represent either a directory root or a file-like target.

Important APIs and types: `TestDirStorage` creates an in-memory base store with `CreateStorage("mem", ...)`, builds table-driven `ObjectStorage` instances using `WithPrefix` and `filestore`, and checks resulting `String()` values after `DirStorage`.

Control flow and state: each case constructs a fresh storage, calls `DirStorage`, and compares display strings. Covered cases include an already-directory prefix, a nested file prefix, a top-level file prefix, an empty prefix, and filestore directory/file roots.

Persistence and integration: the test does not write objects; it exercises path normalization and wrapper unwrapping behavior at the object layer. It depends on the memory and file store registrations being available in the test package.

Risks and test signals: this test is focused and catches regressions in prefix cleanup such as returning `./`, losing trailing slashes, or failing to unwrap top-level file prefixes. It does not cover encrypted wrappers, copy prefix semantics, list key rewriting, or optional interface passthroughs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/prefix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/qingstor.go -->
# sources/distributed-fs/juicefs/pkg/object/qingstor.go

Purpose: implements the QingStor object backend behind `qingstor` when `!noqingstor` is enabled.

Important APIs and types: `qingstor` wraps a QingStor bucket client plus `tierStorage`. It implements bucket creation, object metadata, range reads, writes with content length and MIME type, delete, copy, list, multipart upload/copy/complete/abort/list, and the unsupported `Restore`. `findLen` normalizes arbitrary readers into a reader plus length for APIs requiring content length.

Control flow and state: `Create` treats `bucket_already_exists` as success. `Head` converts QingStor 404 to `os.ErrNotExist`. `Get` uses shared `getRange` and `checkGetStatus`, populating `ResponseAttrs` request ID and storage class from the output. `Put` may buffer non-sized readers, sets `XQSStorageClass` from the active tier, and expects HTTP 201. List clamps to 1000, optionally includes common prefixes, and sorts mixed object/prefix output.

Persistence and integration: data is stored in a configured QingStor bucket. `newQingStor` parses public or private-cloud endpoint shapes into bucket, zone, host, protocol, and shared HTTP transport.

Risks and test signals: buffering in `findLen` can be memory-heavy for large non-seekable inputs. Restore is not supported. Endpoint parsing assumes specific host segment patterns. No QingStor-specific tests appear in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/qingstor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/qiniu.go -->
# sources/distributed-fs/juicefs/pkg/object/qiniu.go

Purpose: implements a Qiniu backend that combines Qiniu native APIs with an embedded S3-compatible client for selected operations.

Important APIs and types: `qiniu` embeds `s3client` and holds a Qiniu `BucketManager`, credentials, config, and marker. It implements `String`, disabled tier init, limited `Limits`, native `Head`, `Put`, `Copy`, `Delete`, `List`, and a custom private-domain `download`; normal `Get` can delegate to S3 unless the key begins with `/` and `QINIU_DOMAIN` is set. Multipart upload is explicitly unsupported.

Control flow and state: `newQiniu` parses the bucket from the host and infers region from endpoint naming, builds an AWS S3 client for Qiniu's S3 endpoint, then configures Qiniu zone/upload hosts. Native `Put` calculates length with `findLen` and uses form upload. `List` filters entries and prefixes by `startAfter`, sorts when delimiter is used, and clears continuation if a page yields no visible objects.

Persistence and integration: data persists in one Qiniu bucket. The backend registers as `qiniu` and depends on both `!noqiniu` and `!nos3` build tags.

Risks and test signals: endpoint/region inference is string-based and brittle. Multipart and tier semantics are mostly disabled. Private-domain download requires `QINIU_DOMAIN`, and request attributes are not propagated on native paths. No Qiniu-specific tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/qiniu.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/redis.go -->
# sources/distributed-fs/juicefs/pkg/object/redis.go

Purpose: implements a Redis-backed object store for chunk data using Redis keys as object keys and values as object bytes.

Important APIs and types: `redisStore` embeds `DefaultObjectStorage` and holds a `redis.UniversalClient` plus sanitized URI. It implements `String`, `Get`, `Put`, `Delete`, `Head`, `ListAll`, and `newRedis`.

Control flow and state: `Put` reads the whole input into memory and writes `SET key value` without expiration. `Get` reads the whole value and slices it for range behavior. `Head` reads the value to report size and maps `redis.Nil` to `os.ErrNotExist`. `ListAll` scans either a single client or all cluster masters, filters keys greater than `marker`, sorts them globally, then pipelines `STRLEN` in batches to emit `obj` metadata.

Persistence and integration: persistence is Redis durability and cluster topology dependent. `newRedis` supports standard, cluster, and sentinel/failover URI shapes, explicit username/password overrides, sentinel password via `SENTINEL_PASSWORD_FOR_OBJ`, TLS settings from parsed URL, and disabled retries by default.

Risks and test signals: scanning all keys is explicitly slow for many objects; `Get`/`Head`/`Put` are whole-value operations and memory-bound. Reported mtimes are current time, not object modification time. No Redis-specific tests are included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/redis.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/response_attrs.go -->
# sources/distributed-fs/juicefs/pkg/object/response_attrs.go

Purpose: defines a small opt-in attribute propagation mechanism for object operations, allowing backends to return request IDs, storage class, and request size without changing method signatures.

Important APIs and types: `ResponseAttrs` holds pointer fields for requested attributes. `AttrGetter` is a function that installs pointers into a `ResponseAttrs`. Constructors are `WithRequestID`, `WithStorageClass`, and `WithRequestSize`; `ApplyGetters` applies all getters and returns the mutable carrier. `DefaultStorageClass` is `"STANDARD"`.

Control flow and state: backends call `ApplyGetters(getters...)`, then invoke setters on the returned value. Setters only mutate non-nil pointers, making attributes optional and allocation-free for uninterested callers. `SetStorageClass` ignores empty strings to avoid overwriting a caller's existing/default storage class. `GetRequestSize` returns `-1` when request size was not requested.

Persistence and integration: no persistent state. It is integrated into S3, OSS, TOS, QingStor, UFile-style paths, and delete/get/put operations where providers expose request metadata.

Risks and test signals: pointer ownership remains with callers, so concurrent reuse of the same target variable could race. Empty storage classes are intentionally ignored. Tests in `response_attrs_test.go` cover request ID and non-empty storage class propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/response_attrs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/response_attrs_test.go -->
# sources/distributed-fs/juicefs/pkg/object/response_attrs_test.go

Purpose: verifies the optional response-attribute callback pattern.

Important APIs and types: `apiCall` simulates a backend by applying getters, setting `"STANDARD"` storage class, and setting a fixed request ID. `Test_api_call` uses testify assertions to check caller-visible mutation.

Control flow and state: the test passes pointers for request ID and storage class, then checks they were populated. It then applies only `WithStorageClass`, calls `SetStorageClass("")`, and verifies the previous `"STANDARD"` value remains unchanged because empty storage-class values are ignored.

Persistence and integration: no storage is touched; this is a pure unit test for the generic attribute helper.

Risks and test signals: the test establishes the contract that setters are no-ops unless the attribute was requested and that empty storage class values do not clear existing state. It does not test `WithRequestSize` or concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/response_attrs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/restful.go -->
# sources/distributed-fs/juicefs/pkg/object/restful.go

Purpose: supplies the package-wide HTTP client and a generic signed REST object-storage implementation used by REST-like backends such as UFile.

Important APIs and types: global `resolver` and `httpClient`, `splitIPsByVersion`, `dialParallel`, `dialRandom`, `GetHttpClient`, `cleanup`, `RestfulStorage`, `request`, `parseError`, `getRange`, `checkGetStatus`, and CRUD methods. `RestfulStorage` holds endpoint, credentials, sign name, and signer callback.

Control flow and state: `init` creates an `http.Client` with cached DNS, custom `DialContext`, IPv6 primary dialing with IPv4 fallback after 300 ms, long total timeout, transport buffers, and disabled compression. `RestfulStorage.request` builds a request, sets date and optional headers/content length, invokes signer, then uses the shared client. Object methods map HTTP status codes to object behavior; copy downloads the whole source and reuploads it; listing is unsupported.

Persistence and integration: persistent state is remote HTTP object storage. Shared `httpClient` is also used by many provider SDK configurations. The `ObjectStorage` assertion documents the generic adapter contract.

Risks and test signals: `Get` leaks response bodies on parse-error paths because `parseError` reads but does not close unless callers clean up. Copy is memory-bound. `dialParallel` behavior is tested in `restful_test.go`, including empty primary/fallback cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/restful.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/restful_test.go -->
# sources/distributed-fs/juicefs/pkg/object/restful_test.go

Purpose: tests the custom TCP dialing helpers used by the shared HTTP transport.

Important APIs and types: `startTCPListener` starts a background accept-and-close listener for test endpoints; `getPort` extracts the bound port. Test cases cover `dialParallel` and `splitIPsByVersion`.

Control flow and state: `TestDialParallel_OnlyPrimaries` confirms direct primary dialing succeeds. `TestDialParallel_OnlyFallbacks` documents and protects the case where primary IPs are empty but fallback IPs are available. `TestDialParallel_PrimaryFailsFast_FallbackSucceeds` verifies fallback starts when the primary path fails. `TestDialParallel_BothFail` expects an error. `TestSplitIPsByVersion` checks IPv4/IPv6 partitioning.

Persistence and integration: no object storage is used. The tests bind local TCP ports and exercise network behavior with short dialer timeouts.

Risks and test signals: tests are timing-sensitive but local. They focus on connection selection and panic prevention, not the full `httpClient` transport, DNS cache, TLS, REST request signing, or response cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/restful_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/s3.go -->
# sources/distributed-fs/juicefs/pkg/object/s3.go

Purpose: implements the main AWS S3 and S3-compatible object storage backend behind `s3`.

Important APIs and types: `s3client` embeds `tierStorage` and owns an AWS v2 S3 client, bucket, region, and checksum toggle. It implements object CRUD, listing, restore, multipart upload/copy/list/complete/abort, endpoint parsing (`parseRegion`, `autoS3Region`, `defaultPathStyle`), and `newS3`.

Control flow and state: `newS3` accepts virtual-host, path-style, Amazon, VPC, Oracle, OVH, and generic compatible endpoint shapes. It infers bucket, endpoint, region, scheme, path-style behavior, anonymous/static/default credentials, disables payload signing, sets retry attempts to one, and optionally disables 100-continue/checksum. Runtime methods map NotFound to `os.ErrNotExist`, ignore missing-key delete errors, propagate request IDs through `ResponseAttrs`, verify checksums on full downloads, and validate listed keys when provider encoding is URL.

Persistence and integration: data persists in a bucket; tier settings control storage class and tags for put/copy. Many provider-specific wrappers embed `s3client`. Registered as `s3`.

Risks and test signals: endpoint parsing is high-risk and provider-specific. Non-seekable `Put` buffers the whole body to compute checksums/S3 body requirements. `ListAll` is unsupported and falls back through generic listing. `s3_test.go` covers display strings for several endpoint forms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/s3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/s3_test.go -->
# sources/distributed-fs/juicefs/pkg/object/s3_test.go

Purpose: checks user-facing string rendering for S3 and S3-compatible endpoints.

Important APIs and types: `Test_s3client_full_string` calls `newS3` for compatible path-style endpoints and an AWS virtual-host endpoint, then asserts `stor.String()`.

Control flow and state: compatible endpoints such as `s3.compatible.site/bucket`, with or without explicit scheme, should retain endpoint plus bucket in the display string. An AWS endpoint like `https://mybucket.s3.us-east-2.amazonaws.com` should display as `s3://mybucket/`.

Persistence and integration: this test constructs clients but does not contact S3 for the compatible path forms; the AWS virtual-host case relies on default AWS config loading without storage operations.

Risks and test signals: it protects endpoint parsing and display behavior but does not validate network calls, region auto-discovery, credentials, checksums, list decoding, or multipart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/s3_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/scw.go -->
# sources/distributed-fs/juicefs/pkg/object/scw.go

Purpose: implements Scaleway Object Storage support as a thin S3-compatible wrapper registered as `scw`.

Important APIs and types: `scw` embeds `s3client`, overrides `String`, and customizes `Limits` to set `MaxPartCount` to 1000 while retaining S3 multipart and upload-part-copy support. `newScw` parses endpoint, bucket, and region, and builds an AWS S3 client with Scaleway endpoint settings.

Control flow and state: endpoint defaults to HTTPS when no scheme is present. The bucket is the first hostname segment; region is read from the third segment; base endpoint is the host without the bucket prefix. Credentials may come from args or `SCW_ACCESS_KEY`/`SCW_SECRET_KEY`. The client uses unsigned payload middleware, shared HTTP client, path-style disabled, and one retry attempt.

Persistence and integration: actual behavior is inherited from `s3client`, so storage class, request attributes, listing, and multipart behavior follow the S3 adapter unless limited by Scaleway.

Risks and test signals: host parsing assumes Scaleway's endpoint layout and may panic or misparse malformed hosts. No SCW-specific tests are present; coverage depends on generic S3 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/scw.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/sftp.go -->
# sources/distributed-fs/juicefs/pkg/object/sftp.go

Purpose: implements an SFTP-backed object store, mapping object keys to remote files/directories under a configured root.

Important APIs and types: `conn` wraps SSH/SFTP clients with close detection. `sftpStore` owns host, port, root, SSH config, and a connection pool. It implements file metadata, range reads, atomic-ish writes, chmod/chown/chtimes, symlink/readlink, delete, delimiter-only list, and authentication setup in `newSftp`.

Control flow and state: operations borrow a pooled connection and return or close it depending on error health. `Put` creates parent directories, writes either in place or to a temp path followed by rename, and treats directory keys as `MkdirAll`. `Head` follows symlinks for metadata but records symlink status. `List` only supports `/` delimiter, lists one remote directory, sorts entries, optionally follows symlinks, filters non-regular files, and emits `file` objects with owner/group/mode.

Persistence and integration: persistence is the remote filesystem. Authentication supports password, private key path, local SSH keys, SSH agent, keyboard interactive, known hosts via `SSH_KNOWN_HOSTS`, or insecure host-key ignore. It implements filesystem and symlink optional interfaces used by prefix wrappers and VFS tooling.

Risks and test signals: context parameters do not cancel SFTP calls. Default host-key behavior is insecure unless configured. Connection pool is unbounded. Path/root parsing depends on the last colon and can be tricky for unusual endpoints. No SFTP-specific tests are included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/sftp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/sharding.go -->
# sources/distributed-fs/juicefs/pkg/object/sharding.go

Purpose: composes multiple object stores into a deterministic key-sharded object store and supplies generic full-list helpers.

Important APIs and types: `sharded` holds `stores []ObjectStorage`, hashes keys with FNV-1a in `pick`, and implements object CRUD, tier support, multipart for same-key shards, restore, and merged `ListAll`. Package-level `ListAll` provides generic paginated listing fallback. `nextKey` and `nextObjects` implement a heap for k-way merge.

Control flow and state: writes, reads, heads, deletes, multipart, and restore route to the shard chosen by hashing the key. `Copy` is unsupported because source and destination could hash to different shards. `ListAll` first tries a backend-native method, then falls back to `List`, then to delimiter traversal if simple listing is unsupported. Sharded `ListAll` starts listing each shard, consumes first objects, and heap-merges sorted streams.

Persistence and integration: persistent state is distributed across endpoint instances created by `NewSharded`, which formats the endpoint string with shard index and calls `CreateStorage`.

Risks and test signals: key hash changes would relocate data. Shard list merge assumes each shard stream is sorted and uses nil as failure/end sentinel. Multipart upload-part-copy is disabled in limits. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/sharding.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/space.go -->
# sources/distributed-fs/juicefs/pkg/object/space.go

Purpose: implements DigitalOcean Spaces-style S3-compatible storage as a wrapper registered as `space`.

Important APIs and types: `space` embeds `s3client`, overrides `String`, delegates `Limits`, and overrides `InitTiers` to set empty tiers and return `notSupported` to avoid storage-class panics.

Control flow and state: `newSpace` defaults to HTTPS, parses bucket and region from host segments, removes the bucket from the base endpoint, builds AWS config with static credentials, unsigned payload middleware, path-style disabled, shared HTTP client, and one retry.

Persistence and integration: all storage operations come from embedded `s3client`; persisted data lives in the configured Space. Registration occurs in `init`.

Risks and test signals: endpoint parsing ignores parse errors (`uri, _`) and assumes host has expected segments, so malformed endpoints can panic or misconfigure. Tier support is deliberately disabled. No Spaces-specific tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/space.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/sql.go -->
# sources/distributed-fs/juicefs/pkg/object/sql.go

Purpose: implements an object store backed by SQL rows, shared by MySQL, PostgreSQL, and SQLite registrations.

Important APIs and types: `sqlStore` holds an `xorm.Engine` and display address. `blob` maps to table `jfs_blob` with id, unique binary key, size, modified timestamp, and data blob. Methods implement `String`, `Get`, `Put`, `Head`, `Delete`, `List`, `newSQLStore`, and `removeScheme`.

Control flow and state: `Get` and `Put` read/write whole object bytes. `Put` uses PostgreSQL `ON CONFLICT` upsert when needed, otherwise insert then update. `Head` selects only key, modified, and size. `List` does ordered key pagination for simple prefix listing, but delimiter listing is unsupported. `newSQLStore` handles PostgreSQL schema/search-path restrictions, maps postgres to `pgx`, sets xorm log level from JuiceFS logger, prefixes table names with `jfs_`, and `Sync2`s the schema.

Persistence and integration: data is stored in the SQL database as one row per object. Driver registration files call `newSQLStore`.

Risks and test signals: whole-object reads/writes make this unsuitable for very large objects. Key column size is 255 bytes. SQL quoting uses backticks, which may be driver-sensitive. No SQL-object tests are in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/sql.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/sql_mysql.go -->
# sources/distributed-fs/juicefs/pkg/object/sql_mysql.go

Purpose: registers the MySQL-backed SQL object store when `!nomysql` is enabled.

Important APIs and types: it imports `github.com/go-sql-driver/mysql` for side-effect driver registration and calls `Register("mysql", ...)` in `init`.

Control flow and state: the registration closure strips any URI scheme from `addr` using `removeScheme`, then calls `newSQLStore("mysql", ..., user, pass)`. All object behavior, persistence schema, listing, and risks are inherited from `sql.go`.

Persistence and integration: one MySQL database stores objects in the `jfs_blob` table through xorm. Credentials are supplied through `CreateStorage` arguments and folded into the DSN in `newSQLStore`.

Risks and test signals: this file has no logic beyond registration, so primary risks are build tags and correct side-effect import availability. No MySQL-specific tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/sql_mysql.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/sql_pg.go -->
# sources/distributed-fs/juicefs/pkg/object/sql_pg.go

Purpose: registers the PostgreSQL-backed SQL object store when `!nopg` is enabled.

Important APIs and types: it imports `github.com/jackc/pgx/v5/stdlib` for side-effect driver registration and calls `Register("postgres", ...)`.

Control flow and state: the closure removes any URI scheme and calls `newSQLStore("postgres", ..., user, pass)`. `newSQLStore` then rewrites the driver to `pgx`, builds a postgres URL, optionally honors one `search_path` schema, and creates/synchronizes the shared blob table.

Persistence and integration: persistent data is in PostgreSQL table `jfs_blob`. Runtime behavior is inherited from `sqlStore`.

Risks and test signals: multiple schemas in `search_path` are rejected. No file-local tests exist; coverage would need SQL integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/sql_pg.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/sql_sqlite.go -->
# sources/distributed-fs/juicefs/pkg/object/sql_sqlite.go

Purpose: registers the SQLite-backed SQL object store when `!nosqlite` is enabled.

Important APIs and types: it imports `github.com/mattn/go-sqlite3` for driver registration and registers the scheme `sqlite3`.

Control flow and state: the registration closure calls `newSQLStore("sqlite3", removeScheme(addr), user, pass)`. The shared SQL store handles table creation, whole-object reads and writes, head/delete, and simple listing.

Persistence and integration: object bytes persist in a local or configured SQLite database file using the `jfs_blob` table.

Risks and test signals: SQLite write concurrency and database-file durability become object-store concerns. This file has no dedicated tests; behavior depends on `sql.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/sql_sqlite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/storj.go -->
# sources/distributed-fs/juicefs/pkg/object/storj.go

Purpose: implements a Storj DCS/uplink object storage backend behind `storj`.

Important APIs and types: `storjClient` holds an `uplink.Project` and bucket. It implements `Shutdown`, CRUD, list, multipart begin/upload/commit/abort/list, and `storjBackoff` for rate-limit retries.

Control flow and state: `storjBackoff` retries `uplink.ErrTooManyRequests` with exponential delays and respects context cancellation. `Put` retries only when the input is seekable, rewinding to the captured start position. `List` compensates for uplink ordering and prefix semantics by broadening the prefix, filtering client-side, deduplicating prefix entries, sorting, and truncating to `limit`. Multipart upload commits parts by upload ID rather than passing a part list.

Persistence and integration: persistent state is in a Storj bucket opened from an access grant. `newStorj` requires the access grant via access-key argument and bucket name in endpoint, sets `UserAgent`, opens the project, and registers in `init`.

Risks and test signals: list pagination ignores `token` and uses start-after style filtering; returning `hasMore` depends on `generateListResult` after client truncation. Non-seekable puts cannot be retried safely. No Storj-specific tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/storj.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/swift.go -->
# sources/distributed-fs/juicefs/pkg/object/swift.go

Purpose: implements an OpenStack Swift object backend behind `swift`.

Important APIs and types: `swiftOSS` holds a Swift connection, region, storage URL, and container. It implements `Create`, `Get`, `Put`, `Delete`, `List`, `Head`, and `newSwiftOSS`.

Control flow and state: `newSwiftOSS` parses `container.host`, builds a v1 auth URL at `/auth/v1.0`, uses username/API key/token, and authenticates with the shared HTTP transport. `Get` uses Range headers for partial reads. `Put` guesses MIME type. `Delete` treats `swift.ObjectNotFound` as success. `List` validates a single-rune delimiter, maps Swift pseudo directories to directory objects, and uses `generateListResult`. `Head` maps object-not-found to `os.ErrNotExist`.

Persistence and integration: objects persist in the configured Swift container. This backend embeds `DefaultObjectStorage`, so unsupported operations fall back to default behavior.

Risks and test signals: only v1 auth is supported. Delimiter must be one rune. The transport type assertion assumes the shared HTTP client uses `*http.Transport`. No Swift-specific tests are included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/swift.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/tikv.go -->
# sources/distributed-fs/juicefs/pkg/object/tikv.go

Purpose: implements a TiKV RawKV object store behind `tikv`.

Important APIs and types: `tikv` embeds `DefaultObjectStorage` and owns a `rawkv.Client` plus address string. It implements whole-value `Get`, `Put`, `Head`, `Delete`, simple `List`, and `newTiKV`.

Control flow and state: reads and writes map object keys directly to RawKV keys. `Get` and `Head` convert missing or empty values to `os.ErrNotExist` in slightly different ways. Range reads are implemented by slicing the returned byte slice. `List` rejects delimiters, defaults marker to prefix, caps to `rawkv.MaxRawKVScanLimit`, scans from marker, and emits objects with current-time mtimes.

Persistence and integration: data persists in TiKV RawKV. `newTiKV` reduces PingCAP logging based on JuiceFS log level, parses PD endpoints, fills default port 2379, and configures TLS/security from URL query (`ca`, `cert`, `key`, `verify-cn`).

Risks and test signals: object metadata has no real mtime; values are whole-object loaded into memory. `List` does not explicitly filter by prefix before `generateListResult`, so correctness depends on downstream behavior. No TiKV-specific tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/tikv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/tos.go -->
# sources/distributed-fs/juicefs/pkg/object/tos.go

Purpose: implements Volcengine TOS object storage behind `tos`.

Important APIs and types: `tosClient` stores bucket, TOS V2 client, and `tierStorage`. It implements object CRUD, listing, restore, multipart upload/copy/list/abort/complete, and `newTOS`.

Control flow and state: `Create` treats bucket-exists errors as success. `Get` applies shared range/status checking, propagates request ID/storage class, and verifies checksum metadata on full reads. `Put` adds checksum metadata when the reader is seekable, applies tier storage class and tags, and records response attributes. `Head` maps 404 to `os.ErrNotExist` and formats restore status. `List` validates returned keys against prefix/start, includes common prefixes, and sorts mixed output. Multipart methods map JuiceFS parts to TOS part structures.

Persistence and integration: data persists in a TOS bucket. `newTOS` parses bucket and region from host segments, creates static credentials with optional token, configures SSL verification and CRC behavior from shared transport/query, and registers as `tos`.

Risks and test signals: multipart `CreateMultipartUpload` advertises 5 MiB minimum while `Limits` says 4 MiB. Endpoint parsing assumes three host segments. No TOS-specific tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/tos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/ufile.go -->
# sources/distributed-fs/juicefs/pkg/object/ufile.go

Purpose: implements UCloud UFile storage by extending `RestfulStorage` with UFile signing, bucket creation, copy acceleration, listing, and multipart support.

Important APIs and types: `ufile` embeds `RestfulStorage`. `ufileSigner` builds the UCloud authorization header. Additional types model list and multipart JSON responses. Methods include `Create`, `parseResp`, `Copy`, `List`, multipart create/upload/abort/complete/list, `Limits`, and `newUFile`.

Control flow and state: `Create` calls UCloud's API service with query-string signature and treats duplicate bucket/create success responses as nil. `Copy` tries UFile `uploadhit` using source ETag and content length, falling back to read-and-write copy. `List` rejects delimiters despite having dead common-prefix handling, caps max keys, parses JSON, and uses the last returned key as marker because UFile's `NextMarker` is unreliable. Multipart upload adjusts part numbers to UFile's zero-based convention.

Persistence and integration: data persists in UFile and generic CRUD comes from signed REST calls. Registered as `ufile`.

Risks and test signals: copy/list/multipart rely on provider quirks and fallback behavior. `AbortUpload` ignores response cleanup. Delimiter listing is unsupported. No UFile-specific tests are included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/ufile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/wasabi.go -->
# sources/distributed-fs/juicefs/pkg/object/wasabi.go

Purpose: implements Wasabi object storage as an S3-compatible wrapper registered as `wasabi`.

Important APIs and types: `wasabi` embeds `s3client`, overrides `String`, and disables tier storage by setting empty tiers in `InitTiers` and returning `notSupported`.

Control flow and state: `newWasabi` defaults to HTTPS, parses bucket and region from host segments, strips the bucket from the base endpoint, builds a static-credential AWS S3 client with unsigned payload middleware, virtual-host addressing, shared HTTP client, and one retry attempt.

Persistence and integration: object behavior is inherited from `s3client`; persistent data lives in a Wasabi bucket.

Risks and test signals: endpoint parsing assumes Wasabi host layout and can misparse nonstandard endpoints. Tier support is deliberately disabled to avoid unsupported storage-class behavior. No Wasabi-specific tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/wasabi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/webdav.go -->
# sources/distributed-fs/juicefs/pkg/object/webdav.go

Purpose: implements WebDAV-backed object storage, mapping object keys to remote WebDAV paths.

Important APIs and types: `webdav` embeds `DefaultObjectStorage` and holds endpoint URL plus a `gowebdav.Client`. It implements `String`, no-op `Create`, `Head`, `Get`, `Put`, `Delete`, `Copy`, delimiter-only `List`, and `newWebDAV`. `webDAVFile` appends directory suffixes in sorted listing.

Control flow and state: `Head` maps WebDAV not-found to `os.ErrNotExist`. `Get` uses full or ranged stream reads. `Put` creates directories for suffix `/` keys or streams file content. `Delete` refuses non-empty directories and ignores missing paths. `List` supports only `/` delimiter, reads one directory, normalizes directory names with trailing slash, sorts, filters by prefix/marker, and uses `generateListResult`.

Persistence and integration: data persists on the WebDAV server. The shared HTTP transport is installed on the client; credentials come from user/password args.

Risks and test signals: no context cancellation is passed to WebDAV calls. `Put` does not create parent directories for files. Delete of non-empty directories returns an error. No WebDAV-specific tests are included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/webdav.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/accesslog.go -->
# sources/distributed-fs/juicefs/pkg/vfs/accesslog.go

Purpose: implements VFS access logging and related Prometheus operation metrics exposed through the internal `.accesslog` file.

Important APIs and types: global histograms/counters track operation durations, totals, and IO errors. `logReader` holds a buffered channel and partial `last` bytes. Functions are `logit`, `openAccessLog`, `closeAccessLog`, and `readAccessLog`.

Control flow and state: `logit` observes metrics for every operation, skips log line construction when there are no readers and the operation is not slow, quotes string arguments when needed, logs slow operations to the normal logger, and non-blockingly fan-outs formatted lines to all active readers. Reader state is held in the package map guarded by `readerLock`. `readAccessLog` first drains partial leftovers, then waits up to one second for log lines, returning `#\n` as a heartbeat on timeout.

Persistence and integration: access log state is in memory but can be captured into handle dumps in `handle.go`. Metrics integrate with Prometheus collection in `internal.go`.

Risks and test signals: reader buffers drop log lines when full. `readAccessLog` serializes reads per handle with a mutex. Tests in `accesslog_test.go` verify formatting, partial reads, invalid handles, and heartbeat behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/accesslog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/accesslog_test.go -->
# sources/distributed-fs/juicefs/pkg/vfs/accesslog_test.go

Purpose: verifies `.accesslog` reader lifecycle and log formatting.

Important APIs and types: `TestAccessLog` uses `openAccessLog`, `closeAccessLog`, `NewLogContext`, `logit`, and `readAccessLog`.

Control flow and state: the test opens handle 1, writes one synthetic operation, confirms reading an invalid handle returns zero, then does a partial read to ensure stored leftovers are returned without blocking. It reads the rest of the line, parses the timestamp, validates uid/gid/pid/method/error/duration formatting, and finally confirms an empty blocking read returns `#\n`.

Persistence and integration: no persistent state; it exercises in-memory access-log channels and the meta context wrapper.

Risks and test signals: the test depends on timing thresholds and exact byte counts. It covers core read semantics but not multi-reader fan-out, dropped lines under buffer pressure, slow-operation logger output, or Prometheus metric values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/accesslog_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/backup.go -->
# sources/distributed-fs/juicefs/pkg/vfs/backup.go

Purpose: periodically dumps JuiceFS metadata to object storage and rotates old backups.

Important APIs and types: Prometheus gauges `LastBackupTimeG` and `LastBackupDurationG`; functions `Backup`, `backup`, `cleanupBackups`, and `rotate`.

Control flow and state: `Backup` loops forever with jitter, reads the root xattr `lastBackup`, skips until the interval elapses, optionally refuses frequent backups on very large inode counts, writes a new timestamp xattr, dumps metadata, starts cleanup after success, and updates gauges. `backup` writes a gzip JSON dump under the local temp `meta/` directory, chooses more dump threads for TiKV metadata, then copies it to `blob` as `meta/dump-YYYY-MM-DD-HHMMSS.json.gz`. `cleanupBackups` lists `meta/` and deletes objects selected by `rotate`.

Persistence and integration: state persists in metadata xattr `lastBackup`, temporary local dump files, and object storage backup files. It integrates with `meta.Meta`, `object.ObjectStorage`, and `pkg/sync.CopyData`.

Risks and test signals: failed backups still leave `lastBackup` advanced because the xattr is set before dumping. Rotation parses names by fixed length. `backup_test.go` covers rotation policy and that a backup object appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/backup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/backup_test.go -->
# sources/distributed-fs/juicefs/pkg/vfs/backup_test.go

Purpose: tests metadata backup retention and basic periodic backup execution.

Important APIs and types: `TestRotate` exercises `rotate`; `TestBackup` uses `createTestVFS`, `Backup`, `object.WithPrefix`, and `object.ListAll`.

Control flow and state: `TestRotate` simulates twice-daily backups across 200 half-day increments, applying rotation each time, then compares the retained set against expected monthly/weekly/daily/recent samples. `TestBackup` starts `Backup` with a 100 ms interval against a memory-backed VFS/blob, waits briefly, lists the `meta/` prefix, and expects at least one dump file.

Persistence and integration: tests use memory-backed JuiceFS components and object storage, avoiding external services.

Risks and test signals: `TestBackup` starts a goroutine that runs indefinitely for the process lifetime. Timing is short and may be sensitive under heavy load. It verifies existence, not dump content or cleanup after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/backup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/compact.go -->
# sources/distributed-fs/juicefs/pkg/vfs/compact.go

Purpose: compacts multiple metadata slices into a new contiguous chunk object.

Important APIs and types: `compactSizeHistogram`, helper `readSlice`, and exported `Compact(conf, store, slices, id, tierID)`.

Control flow and state: `Compact` waits while allocated memory minus store-used memory exceeds roughly 1.5 buffer sizes, sums slice lengths, records histogram data, opens a new chunk writer with writeback disabled, and copies each input slice into sequential positions. Zero-ID slices are written as zero-filled holes. Nonzero slices are read in block-sized pages with `readSlice`; each page is written to the new writer. When enough data accumulates, it flushes to the current position. Any read/write/finish failure aborts the writer.

Persistence and integration: compaction writes a new chunk to the configured `chunk.ChunkStore`, but metadata replacement is handled elsewhere by `meta.Compact`. It depends on chunk pages, writers, and meta slice layout.

Risks and test signals: `writer.FlushTo` errors panic instead of returning, which can crash compaction callers. Memory wait has no context cancellation. `compact_test.go` validates successful byte preservation and read-failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/compact.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/compact_test.go -->
# sources/distributed-fs/juicefs/pkg/vfs/compact_test.go

Purpose: verifies compacted chunks contain the concatenated bytes of source slices and that missing source data fails compaction.

Important APIs and types: `TestCompact` constructs `chunk.Config`, a memory object store, `chunk.NewCachedStore`, source `meta.Slice` values, and calls `Compact`.

Control flow and state: the test writes 100 chunks with deterministic byte patterns and increasing sizes, compacts all slices into chunk id 1000, reads back each segment, and checks byte-for-byte correctness. It then removes one source object and expects a subsequent compaction attempt to fail.

Persistence and integration: uses in-memory object storage through the cached chunk store, testing the VFS compaction logic against real chunk store APIs without external services.

Risks and test signals: the test does not inject write or flush failures, matching the TODO in source. It also does not cover zero-fill slices, tier IDs, memory-throttle behavior, or panic path on `FlushTo` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/compact_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/context_cancellation_test.go -->
# sources/distributed-fs/juicefs/pkg/vfs/context_cancellation_test.go

Purpose: protects cancellation behavior for readers and internal control commands.

Important APIs and types: `blockingChunkReader`, `blockingChunkStore`, `createCancellationTestReader`, `decodeControlOutput`, `runInternalControlWithCancel`, `buildTestTreeForControlCancel`, and four tests for reader close/invalidate and control Info/Summary cancellation.

Control flow and state: the blocking reader exposes channels to detect read start, cancellation, and release. Tests verify `FileReader.Close` and `DataReader.Invalidate` do not immediately cancel an in-flight BUSY read; the read completes after release. Control tests build a small tree, run `handleInternalMsg` with a context canceled immediately, decode progress/data frames, and require failed/EINTR-style responses for InfoV2 and OpSummary.

Persistence and integration: uses memory metadata, UUID-backed format names, mock chunk store, VFS creation helpers, and internal control binary framing.

Risks and test signals: the tests document a deliberate behavior: close/invalidate mark state but do not cancel BUSY reads immediately. They are timing-sensitive but give strong regression signals for cancellation semantics and internal response framing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/context_cancellation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/fill.go -->
# sources/distributed-fs/juicefs/pkg/vfs/fill.go

Purpose: implements cache warmup, eviction, and cache-status checking over VFS paths or inode IDs.

Important APIs and types: `_file`, `CacheAction` (`WarmupCache`, `EvictCache`, `CheckCache`), `CacheFiller`, `NewCacheFiller`, `cacheFile`, `Cache`, path `resolve`, `walkDir`, `sliceIterator`, and `newSliceIterator`.

Control flow and state: `Cache` resolves each requested path, recursively walks directories, queues files, and processes them with bounded concurrency. `cacheFile` selects a slice handler: fill cache, evict cache, or check cache and aggregate `CacheResponse` locations/misses. Warmup may briefly open files when metadata open-cache is enabled. `sliceIterator` reads file slices chunk by chunk from metadata, counts slices/bytes, and invokes handlers either directly or in goroutines using the shared token channel.

Persistence and integration: it mutates chunk cache state through `chunk.ChunkStore` methods and reads namespace/slice metadata through `meta.Meta`. It integrates with internal control command `FillCache`.

Risks and test signals: `sliceIterator.err` is written by concurrent goroutines without synchronization. Symbolic link resolution rejects absolute or external targets. `fill_test.go` covers normal paths, directories, symlinks, internal nodes, missing paths, and missing chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/fill.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/fill_test.go -->
# sources/distributed-fs/juicefs/pkg/vfs/fill_test.go

Purpose: smoke-tests cache filling over normal and problematic path inputs.

Important APIs and types: `TestFill` uses `createTestVFS`, VFS mkdir/create/write/flush/release/symlink methods, and `v.cacheFiller.Cache`.

Control flow and state: the test creates `/test/file`, writes data, creates relative and absolute symlinks, warms cache for a direct file, directory, symlink, and root path, then removes backing chunk objects and invokes warmup on paths expected to hit bad cases (`/test/file`, absolute symlink, relative missing symlink, internal `.stats`, and nonexistent path).

Persistence and integration: uses memory VFS/object components and real cache filler paths. It exercises metadata resolution, recursive walking, symlink handling, and chunk-store errors.

Risks and test signals: the test mainly ensures no panic and broad path coverage; it does not assert `CacheResponse` counters, cache locations, or error logs. It does not cover evict/check modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/fill_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/handle.go -->
# sources/distributed-fs/juicefs/pkg/vfs/handle.go

Purpose: manages VFS file, directory, access-log, and control handles, including locking, operation cancellation, and handle-state persistence for restart recovery.

Important APIs and types: `handle` stores inode/fh, directory handler, file reader/writer, lock owners, active operation contexts, RW lock counters/condition, internal-file buffers, and tier ID. VFS methods include `newHandle`, `findAllHandles`, `findHandle`, `releaseHandle`, `newFileHandle`, `releaseFileHandle`, `invalidateDirHandle`, `dumpAllHandles`, and `loadAllHandles`. `state` and `saveHandle` encode JSON recovery data.

Control flow and state: file handles are allocated with odd/even low bits for read-only/read-write distinction and skip recovered descriptors. `Rlock`/`Wlock` wait with timeout and abort if the operation context is canceled. Active contexts are tracked for cancellation by pid. Release waits for readers/writers before closing reader/writer objects. Dump serializes handles, flushes writers, captures access-log pending data, and writes JSON. Load reconstructs handles, access-log readers, readers, and writers from JSON.

Persistence and integration: handle recovery state is persisted to a JSON file path chosen by callers. It integrates with `reader`, `writer`, `meta.DirHandler`, accesslog globals, and VFS handle maps.

Risks and test signals: the field `hanleM` spelling is inherited but easy to misuse. Recovered read-only handles can be synthesized by `findHandle`. Dump writes directly with `os.Create`, not atomic rename. No dedicated handle tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/handle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/helpers.go -->
# sources/distributed-fs/juicefs/pkg/vfs/helpers.go

Purpose: contains small VFS formatting and context helpers used by logging, tests, and diagnostics.

Important APIs and types: mode permission constants, `strerr`, `typestr`, `smode.String`, `Entry.String`, `LogContext`, `logContext`, and `NewLogContext`.

Control flow and state: `strerr` maps errno 0 to `"OK"` and otherwise uses the errno error string. `smode.String` builds Unix file-mode text including file type, rwx bits, and suid/sgid/sticky uppercase/lowercase semantics. `Entry.String` lazily formats meta entry inode plus selected attributes. `NewLogContext` wraps a `meta.Context` with a start timestamp so `Duration` reports elapsed operation time.

Persistence and integration: no persistence. Used by access logging, tests, and VFS log output.

Risks and test signals: formatting is exact-string-sensitive and must match Unix mode conventions. `helpers_test.go` covers mode strings, entry formatting, and errno string conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/helpers_test.go -->
# sources/distributed-fs/juicefs/pkg/vfs/helpers_test.go

Purpose: unit-tests VFS helper formatting.

Important APIs and types: `smodeCase`, global `cases`, `TestSmode`, `TestEntryString`, and `TestError`.

Control flow and state: `TestSmode` checks directory, regular, symlink, and socket modes with special bits. `TestEntryString` verifies nil entries, entries without attrs, and file entries with mode/nlink/uid/gid/timestamps/length. `TestError` checks errno formatting for success and `EACCES`.

Persistence and integration: no storage or metadata service is required beyond constructing a `meta.Attr`.

Risks and test signals: these tests are high-signal for diagnostic output compatibility. They do not test `NewLogContext.Duration` timing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/internal.go -->
# sources/distributed-fs/juicefs/pkg/vfs/internal.go

Purpose: defines special internal VFS nodes and implements binary control-message handlers for management operations such as remove, clone, info, summary, compact, and cache fill.

Important APIs and types: special inode constants, `internalNode`, `IsSpecialNode`, `IsSpecialName`, `GetInternalNodeByName`, `CollectMetrics`, `writeProgress`, `CalcObjects`, response structs (`InfoResponse`, `SummaryReponse`, `CacheResponse`), and `VFS.handleInternalMsg`.

Control flow and state: init stamps internal node attributes with current uid/gid/time. Control handles are per-pid in `controlHandlers`. `CollectMetrics` flattens Prometheus metrics into text. `writeProgress` emits `meta.CPROGRESS` frames every 300 ms until a background operation completes. `CalcObjects` maps a slice ID/range to object keys based on format hash-prefix and block size. `handleInternalMsg` decodes command payloads, runs metadata operations in goroutines for long tasks, streams progress, and writes either errno bytes or `meta.CDATA` JSON/text frames.

Persistence and integration: internal nodes expose `.control`, `.accesslog`, `.stats`, `.config`, and trash. Commands integrate with `meta.Meta`, object storage head for restore status, cache filler, compaction, and invalidation callbacks.

Risks and test signals: binary protocol parsing assumes valid buffer layout. Some operations continue in background. Object restore status lookup uses `context.Background`, not the control context. Cancellation tests cover InfoV2 and OpSummary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/reader.go -->
# sources/distributed-fs/juicefs/pkg/vfs/reader.go

Purpose: implements VFS file reading, chunk-slice reads, readahead, read-buffer accounting, invalidation, truncation, retry, and cleanup.

Important APIs and types: states `NEW`, `BUSY`, `REFRESH`, `BREAK`, `READY`, `INVALID`; interfaces `FileReader` and `DataReader`; `frange`; `sliceReader`; `session`; `fileReader`; `dataReader`; constructors and methods `NewDataReader`, `Open`, `Read`, `Truncate`, `Invalidate`, `Close`, and slice read helpers.

Control flow and state: each open file has a linked list of `sliceReader` requests guarded by the file mutex. `fileReader.Read` throttles if buffer use is high, computes the requested range, removes stale readahead requests, splits around existing slices, prepares missing requests, updates sequential session readahead, and waits for slice IO. `sliceReader.run` reads metadata slices, uses `dataReader.Read` to fill a page, retries transient metadata/read mismatches, and transitions state. `dataReader` tracks all open readers per inode, periodically releases idle buffers, invalidates overlapping slices, and reads multiple metadata slices concurrently.

Persistence and integration: state is in memory; data comes from `meta.Meta` slice maps and `chunk.ChunkStore`. Handles in `handle.go` own reader lifetimes.

Risks and test signals: concurrency is delicate: state transitions call `runtime.Goexit`, global `readBufferUsed` spans all readers, and BUSY invalidation deliberately does not cancel immediately. `context_cancellation_test.go` documents close/invalidate behavior. No direct tests cover readahead tuning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/reader.go -->
