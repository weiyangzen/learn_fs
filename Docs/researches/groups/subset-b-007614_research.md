# Research: subset-b-007614

This grouped report covers the JuiceFS `pkg/object` files assigned to `subset-b-007614`. Each section is source-tree-aligned and wrapped for reconciliation into the corresponding per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/bunny.go -->
# sources/distributed-fs/juicefs/pkg/object/bunny.go

Purpose: implements the optional Bunny.net Storage backend behind the `bunny` build tag and registers it as `bunny`. It adapts `github.com/l0wl3vel/bunny-storage-go-sdk` to JuiceFS `ObjectStorage`.

Important APIs and flow: `bunnyClient` embeds `DefaultObjectStorage`, so unsupported operations use shared defaults. `Get` uses `DownloadPartial` with an inclusive end offset, mapping `limit == -1` to `math.MaxInt64`; `Put` buffers the entire reader and uploads with overwrite enabled; `Delete` ignores Bunny `"Not Found"` errors; `Head` calls `Describe`; `List` only supports delimiter `/`, lists a parent directory, filters by prefix and marker, and returns `generateListResult`.

State and persistence: all data lives in Bunny Storage. This adapter keeps only endpoint and SDK client state. Directory identity is represented by trailing `/` in normalized object names.

Dependencies and integration: depends on Bunny's SDK and JuiceFS helpers `obj`, `generateListResult`, and `notSupported`. `newBunny` normalizes endpoints to `https://...` and uses the password argument as the storage-zone password.

Risks: `Put` and `Get` read whole objects into memory, so large objects are risky. Error handling compares string messages. Context cancellation is not propagated to the Bunny SDK calls. Listing is single-directory oriented and does not use a server continuation token.

Test signals: `object_storage_test.go` contains a Bunny test skeleton, but it is commented out, so this backend has little automated coverage unless built and tested manually with `bunny` tags and credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/bunny.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/ceph.go -->
# sources/distributed-fs/juicefs/pkg/object/ceph.go

Purpose: implements a Ceph RADOS object backend behind the `ceph` build tag and registers it as `ceph`.

Important APIs and flow: `ceph` owns a `rados.Conn` and a bounded pool of `IOContext` objects. `Create` lists pools and creates the target pool if absent. `Get` validates existence through `Head`, then returns `cephReader`, which reads RADOS object ranges incrementally and releases its context on `Close`. `Put` fast-paths non-empty `*bytes.Reader` data below about 85 MiB through `WriteFull`, otherwise streams 1 MiB chunks with increasing offsets. `Delete`, `Head`, and `ListAll` translate RADOS operations into JuiceFS object semantics.

State and persistence: persistent state is the Ceph pool and object namespace. The adapter pools IO contexts and configures `SetPoolFullTry`. It does not persist directory metadata beyond object keys ending in `/`.

Dependencies and integration: uses `github.com/ceph/go-ceph/rados`, shared `obj`, `DefaultObjectStorage`, and `Shutdownable`. `newCeph` reads Ceph config, optional logging/admin-socket environment variables, and opens a connection using cluster and user arguments.

Risks: empty object writes return unsupported or an error, which diverges from most object stores. Most methods ignore caller context. Ordered `ListAll` scans all keys and then stats them concurrently, with comments noting poor performance and possible goroutine leaks on errors. The unordered mode omits sizes and mtimes.

Test signals: `object_storage_test.go` has a commented Ceph test only. Coverage depends on manual build with the `ceph` tag and a live cluster.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/ceph.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/checksum.go -->
# sources/distributed-fs/juicefs/pkg/object/checksum.go

Purpose: provides CRC32C checksum generation and read-time verification used by providers such as Tencent COS.

Important APIs and flow: `checksumAlgr` names `"Crc32c"` and `crc32c` is the Castagnoli table. `generateChecksum` consumes an `io.ReadSeeker`, using reflection to read the backing bytes of `*bytes.Reader` without copying, or streaming through `bufPool` for generic readers. It seeks back to start before returning. `verifyChecksum` and `verifyChecksum0` wrap a `ReadCloser` in `checksumReader` when a checksum string is present. `checksumReader.Read` updates CRC state and returns an error when EOF or the declared content length is reached with a mismatch.

State and persistence: no persistent state. Verification state is per-reader: expected CRC, running checksum, remaining content length, and table.

Dependencies and integration: uses shared `bufPool` from `object_storage.go` and logger for invalid checksum strings. COS stores checksums in metadata and verifies full-object reads.

Risks: reflection into `bytes.Reader` internals is brittle across Go implementation changes. Verification for content length `-1` effectively waits for EOF; partial reads before EOF do not validate. `Read` returns `0, error` on mismatch, which can discard bytes read in that call.

Test signals: `checksum_test.go` covers generation, successful validation, corrupted data, unknown length behavior, and partial-read cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/checksum.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/checksum_test.go -->
# sources/distributed-fs/juicefs/pkg/object/checksum_test.go

Purpose: validates the checksum helpers in `checksum.go`.

Important APIs and flow: `TestChecksum` computes the expected CRC32C of `"hello"` and checks repeated `generateChecksum(bytes.NewReader(...))` calls, including the seek-back behavior. `TestChecksumRead` generates random 10 KiB content, wraps it through `verifyChecksum`, and exercises exact-size reads, oversized buffers, corrupted content, and short reads.

State and persistence: no persistent state; tests use in-memory byte slices and `io.NopCloser`.

Dependencies and integration: uses JuiceFS `utils.RandRead`, Go `hash/crc32`, and standard `testing`. It indirectly verifies the shared `bufPool` path only for non-`bytes.Reader` inputs to the extent reads happen through the wrapper.

Risks and gaps: the tests focus on `bytes.Reader` generation and do not explicitly cover a generic `io.ReadSeeker` implementation. The corruption loop mutates `content[0]` and then reuses the mutated buffer for later short-read checks, which is acceptable for those assertions but can obscure intent. Invalid checksum string logging is not asserted.

Test signal: strong for the expected full-read checksum contract and the special `contentLength == -1` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/checksum_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/cifs.go -->
# sources/distributed-fs/juicefs/pkg/object/cifs.go

Purpose: implements SMB/CIFS storage behind `!nocifs`, registering both `cifs` and `smb`.

Important APIs and flow: `cifsStore` stores SMB connection parameters and a channel-backed connection pool. `getConnection` reuses live connections until an idle timeout, creates new `smb2` sessions and mounts shares, and honors context cancellation while waiting. `withConn` scopes operations. `Head`, `Get`, `Put`, `Delete`, `List`, `Copy`, `Chtimes`, and `Chmod` map object operations to SMB file operations; `Get` returns a `cifsReadCloser` that releases the connection only after close. `parseEndpoint` accepts `cifs://` or `smb://host[:port]/share`.

State and persistence: persistent state is the remote SMB share. Local state is the connection pool and idle timestamps. Writes use temp paths through `TmpFilePath` unless global `PutInplace` is enabled.

Dependencies and integration: uses `github.com/cloudsoda/go-smb2`, shared `mEntry`, `SectionReaderCloser`, `bufPool`, and `FileSystem`. It reports placeholder owner/group values and marks symlinks where SMB exposes them.

Risks: `Chmod`, `Chown`, and POSIX mode semantics are limited by SMB. Some methods use `context.Background()` for filesystem metadata operations. The pool can create bursts of connections under load, noted by a FIXME. Symlink handling is best-effort. Directory delete trims trailing `/`.

Test signals: covered by environment-gated `TestCifs` and `TestCifs2`, both delegating to broad object and filesystem contract tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/cifs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/context_cancellation_test.go -->
# sources/distributed-fs/juicefs/pkg/object/context_cancellation_test.go

Purpose: asserts that core object interfaces and selected network helpers honor `context.Context` cancellation.

Important APIs and flow: `TestObjectStorageInterfaceMethodsUseContext` reflects over `ObjectStorage` and checks every listed method has `context.Context` as its first input. `TestDialParallel_ContextCanceled` cancels a context before calling `dialParallel` and expects `context.Canceled`. `TestRestfulStorageGet_ContextCanceled` and `TestRestfulStoragePut_ContextCanceled` use a loopback endpoint and pre-canceled context to ensure REST calls report cancellation or deadline errors.

State and persistence: no persistent state. Tests use local contexts, dummy HTTP endpoint configuration, and no real storage writes.

Dependencies and integration: depends on `RestfulStorage`, `dialParallel`, and the public `ObjectStorage` interface. The test acts as a guard for future API changes by requiring context propagation at the interface level.

Risks and gaps: provider implementations may still ignore context internally despite the interface accepting it; this file only directly exercises REST and dial helper behavior. It does not cover cloud SDK, filesystem, or Ceph implementations.

Test signal: important API-contract coverage for cancellation-aware method signatures and selected HTTP/dial paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/context_cancellation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/cos.go -->
# sources/distributed-fs/juicefs/pkg/object/cos.go

Purpose: implements Tencent Cloud COS storage behind `!nocos`, registering `cos`.

Important APIs and flow: `COS` wraps `cos.Client` plus tier configuration. It implements bucket creation, head/get/put/copy/delete/list, restore, and multipart operations. `Get` uses HTTP Range headers and verifies stored CRC32C metadata on full-object reads. `Put` stores CRC metadata for `io.ReadSeeker` inputs, applies storage class and encoded object tag from the active tier, and returns request/storage-class attrs. `List` decodes URL-encoded keys and merges common prefixes for delimiter listing.

State and persistence: objects, metadata, tags, restore state, and multipart uploads live in COS. Local persistent state is limited to the endpoint host and tier map.

Dependencies and integration: depends on Tencent COS SDK, shared checksum helpers, `ResponseAttrs`, `TierKey`, and `DefaultStorageClass`. `newCOS` can discover bucket endpoint from service listing, falls back to `COS_SECRETID` and `COS_SECRETKEY`, and supports disabling SDK CRC with `disable-checksum=true`.

Risks: automatic endpoint discovery needs list-bucket permissions. Some request IDs and storage classes are header-dependent. Checksum verification only applies to full reads with metadata. Copy source formatting depends on endpoint host. `ListAll` is not implemented.

Test signals: environment-gated `TestCOS` in `object_storage_test.go` runs the broad storage contract when COS credentials are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/cos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/dragonfly.go -->
# sources/distributed-fs/juicefs/pkg/object/dragonfly.go

Purpose: implements a Dragonfly object-storage gateway backend behind `!nodragonfly`, registering `dragonfly`.

Important APIs and flow: `dragonfly` talks HTTP to dfdaemon object-storage endpoints. `Create` posts `/buckets/{bucket}` after probing list. `Head`, `Get`, `Put`, `Copy`, `Delete`, and `List` build REST requests under `/buckets/{bucket}`. `Put` and `Copy` use multipart form bodies; write mode can be synchronous `WriteBack` or `AsyncWriteBack`. `List` decodes JSON `ObjectMetadatas`, merges common prefixes, and caps page size at `MaxGetObjectMetadatasLimit`.

State and persistence: object data may be written to Dragonfly cache and backend storage depending on mode. Local state includes endpoint, bucket, selected query filter, write mode, max replicas, and HTTP client.

Dependencies and integration: uses shared `getRange`, `generateListResult`, `obj`, `httpClient`, and `ResponseAttrs`. `newDragonfly` calls `/metadata` to identify the underlying object store and chooses URL-query filters for S3, OSS, or OBS presigned URLs.

Risks: some methods use `http.DefaultClient` rather than `d.client`, reducing consistency. Bucket parsing keeps `uri.Path`, which may include a leading slash in the bucket field. `Delete` treats non-2xx, including not found, as an error. `Put` buffers the complete multipart payload in memory. `getObjectStorageMetadata` returns `nil, nil` on URL parse failure, which can hide errors.

Test signals: environment-gated `TestDragonfly` runs the shared object-storage suite with a configured endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/dragonfly.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/encrypt.go -->
# sources/distributed-fs/juicefs/pkg/object/encrypt.go

Purpose: implements whole-object encryption wrappers and key parsing/encryption primitives for JuiceFS object storage.

Important APIs and flow: `ParsePrivateKeyFromPem` handles RSA PKCS#1, PKCS#8, encrypted PEM, and SM2 PKCS#8 keys, returning `ErrKeyNeedPasswd` when encrypted keys lack passphrases. `NewRSAEncryptor` uses RSA-OAEP/SHA256; `NewSM2Encryptor` uses SM2 ASN.1 encryption; `NewKeyEncryptor` dispatches by private key type. `NewDataEncryptor` creates AEAD data encryptors for AES-256-GCM, ChaCha20-Poly1305, or SM4-GCM. `dataEncryptor.Encrypt` generates a random data key and nonce, wraps the key, and stores a compact header; `Decrypt` reverses it. `NewEncrypted` wraps any `ObjectStorage`, encrypting complete objects on `Put` and decrypting complete objects before slicing on `Get`.

State and persistence: encrypted object bytes include wrapped data key, nonce, and AEAD ciphertext. The wrapper keeps the key encryptor in memory and delegates persistent storage to the underlying backend.

Dependencies and integration: integrates with RSA, GM/T SM2/SM4/SM3 libraries, `SupportTier`, and `ObjectStorage`. `Shutdown` unwraps encrypted stores.

Risks: whole-object mode reads entire plaintext/ciphertext into memory and cannot perform efficient range reads. Unsupported private-key types panic in `NewKeyEncryptor`. Typoed error text `"decryt key"` is externally visible. `ExportRsaPrivateKeyToPem` contains an unused error check after ignored return.

Test signals: `encrypt_test.go` covers key parsing, RSA/SM2 operations, AEAD round trips, overhead bounds, benchmarks, and encrypted mem-store behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/encrypt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/encrypt_chunked.go -->
# sources/distributed-fs/juicefs/pkg/object/encrypt_chunked.go

Purpose: provides chunked object encryption that preserves practical range reads and plaintext size reporting.

Important APIs and flow: `NewChunkedEncrypted` wraps an `ObjectStorage` with 1 MiB plaintext chunks. Each stored chunk has a 4-byte big-endian ciphertext-length header followed by encrypted data padded to a fixed encrypted chunk size. `Get` maps plaintext offset/limit to encrypted chunk offset/limit, then returns `chunkDecryptReader`, which decrypts chunk by chunk, skips the initial plaintext offset, and optionally limits output. `Put` streams plaintext through `chunkEncryptReader`, which encrypts each chunk and emits fixed-size records. `Head`, `List`, and `ListAll` wrap returned objects with recalculated plaintext size. Multipart upload encrypts each part stream and disables upload-part-copy.

State and persistence: stored object layout is chunk records; no external metadata is required for size reconstruction. Pools hold plaintext and encrypted chunk buffers per wrapper.

Dependencies and integration: uses `dataEncryptor`, `FileSystem`, `SupportSymlink`, `SupportTier`, and shared `ObjectStorage` methods. It preserves filesystem and symlink interfaces by embedding wrappers when possible.

Risks: `calcPlainSize` is an inference from encrypted size and fixed overhead; malformed/corrupt objects can produce misleading sizes before read-time errors. Each encrypted chunk has fresh key material due to `dataEncryptor.Encrypt`, increasing overhead and CPU cost. `UploadPart` buffers the encrypted part in memory. Small or truncated chunks surface decryption errors during reads.

Test signals: `encrypt_chunked_test.go` stresses concurrent reads and one-byte read patterns to catch buffer aliasing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/encrypt_chunked.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/encrypt_chunked_test.go -->
# sources/distributed-fs/juicefs/pkg/object/encrypt_chunked_test.go

Purpose: regression-tests concurrent reads from chunked encrypted storage.

Important APIs and flow: `TestChunkedEncryptedConcurrentGet` creates a memory store, builds an RSA/AES-GCM `dataEncryptor`, wraps it with `NewChunkedEncrypted`, writes a deterministic 1024-byte object, then launches 30 goroutines. Each goroutine calls `Get` for the whole object and reads one byte at a time before comparing against the original content.

State and persistence: data persists only in the in-memory backend for the test duration. The concurrency pressure targets per-reader buffer state and wrapper-level sync pools.

Dependencies and integration: depends on `rsaKey` from `encrypt_test.go`, `CreateStorage("mem", ...)`, `NewDataEncryptor`, `NewRSAEncryptor`, and testify `require`.

Risks and gaps: the test uses only one small object, one algorithm, and whole-object reads. It does not cover cross-chunk ranges, corrupt chunk headers, multipart upload behavior, or filesystem interface preservation.

Test signal: strong for the specific race/aliasing class where `chunkDecryptReader` retains slices backed by pooled encrypted buffers while many readers are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/encrypt_chunked_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/encrypt_test.go -->
# sources/distributed-fs/juicefs/pkg/object/encrypt_test.go

Purpose: tests and benchmarks the key parsing, key encryption, data encryption, and whole-object encrypted storage code.

Important APIs and flow: `TestParsePrivateKey` covers RSA PKCS#1, encrypted RSA PKCS#8, plain SM2 PKCS#8, and SM2 encrypted with SM4/AES. `TestSM2` and `TestRSA` verify key encryptor round trips and PEM path parsing. `TestDataEncryptor` covers RSA/AES-GCM, RSA/ChaCha20, and SM2/SM4-GCM. `TestEncryptorMaxOverhead` checks `MaxOverhead` bounds for RSA key sizes and SM2. `TestEncryptedStore` wraps `mem` storage and verifies ranged decrypted reads plus corruption handling for an unencrypted empty object.

State and persistence: uses generated private keys, embedded PEM fixtures, temporary files, and in-memory object storage only.

Dependencies and integration: uses `crypto/rsa`, GM/T SM2 libraries, `NewEncrypted`, `CreateStorage`, and testify `require`. Benchmarks measure key encrypt/decrypt and 4 MiB data encrypt/decrypt.

Risks and gaps: tests do not assert cryptographic interoperability with external tools beyond parsing embedded key formats. Randomized encryption makes exact wire format assertions absent. `TestEncryptedStore` covers whole-object mode but not chunked mode.

Test signal: broad for supported key formats, AEAD algorithms, overhead calculations, and wrapper read slicing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/encrypt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/eos.go -->
# sources/distributed-fs/juicefs/pkg/object/eos.go

Purpose: implements an EOS S3-compatible backend behind `!nos3`, registering `eos`.

Important APIs and flow: `eos` embeds `s3client`, overriding `String` and `Limits`. `newEos` normalizes endpoints to HTTPS, derives the bucket from the first host label, strips the bucket from the service endpoint, sets region to `us-east-1`, loads `EOS_ACCESS_KEY`, `EOS_SECRET_KEY`, and `EOS_TOKEN` fallbacks, and creates an AWS SDK v2 S3 client with custom endpoint, path-style policy, shared HTTP client, unsigned payload middleware, and one retry attempt.

State and persistence: all object, listing, and multipart persistence is delegated to `s3client` and the remote EOS-compatible service. Local state is the S3 client, bucket, and region.

Dependencies and integration: depends on AWS SDK v2, shared `defaultPathStyle`, `httpClient`, and the package's generic S3 implementation in files outside this subset.

Risks: endpoint parsing assumes bucket-as-first-label host format. Region is hard-coded. All core operation behavior is inherited from `s3client`, so provider-specific quirks must be handled there or through endpoint configuration. Build is disabled by `nos3`.

Test signals: `TestEOS` is environment-gated on `EOS_ENDPOINT` and then runs the shared object-storage contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/eos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/etcd.go -->
# sources/distributed-fs/juicefs/pkg/object/etcd.go

Purpose: implements etcd v3 as an object-storage backend behind `!noetcd`, registering `etcd`.

Important APIs and flow: `etcdClient` stores an etcd client and KV interface. `Get` fetches one key and slices the value by offset/limit. `Put` reads the full reader into memory and stores it as a string value. `Head` reports size from value length and uses current time as mtime. `Delete` deletes the key. `List` supports prefix scans without delimiters, using `genNextKey(prefix)` as the range end and sorted keys with limit. `buildTlsConfig` builds TLS settings from URL query parameters.

State and persistence: each object is one etcd key/value. There is no durable mtime metadata, directory metadata, or chunking.

Dependencies and integration: uses `go.etcd.io/etcd/client/v3`, transport TLS helpers, shared `obj`, and `DefaultObjectStorage`.

Risks: whole-object values are unsuitable for large data and constrained by etcd value size and cluster performance. `Put` converts arbitrary bytes to string, which preserves bytes in Go but may be surprising. `genNextKey` can underflow on empty strings, though `List` avoids it for empty prefixes. Delimiter listing and multipart operations are unsupported. Mtime is synthetic and changes on every `Head`/`List`.

Test signals: `TestEtcd` is environment-gated and runs the broad storage suite when `ETCD_ADDR` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/etcd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/file.go -->
# sources/distributed-fs/juicefs/pkg/object/file.go

Purpose: implements local filesystem storage registered as `file`.

Important APIs and flow: `filestore` maps object keys to paths under `root`. `Head` uses `Lstat`, follows symlinks for target metadata, and returns `file` metadata. `Get` opens files and returns empty readers for directories or out-of-range offsets; ranged reads use `SectionReaderCloser`. `Put` creates directories for slash keys, otherwise writes to a temp file from `TmpFilePath` and renames atomically unless `PutInplace` is set. `Copy` streams through `Get`/`Put`; `Delete` ignores missing paths. `readDirSorted` filters non-regular files, handles symlinks based on `followLink`, and sorts entries. `List` implements delimiter `/` listing and may include the directory itself.

State and persistence: persistent state is the local directory tree. Temporary `.jfs.*.tmp.*` files exist during non-inplace writes. Symlinks are supported through `Symlink` and `Readlink`.

Dependencies and integration: uses platform-specific `getOwnerGroup` and `Chtimes`, shared `file` type, `bufPool`, `TryCFR`, `PutInplace`, `FileSystem`, and `SupportSymlink`.

Risks: path construction differs depending on whether root ends with `/`; callers must understand leading slash behavior. Global `PutInplace` weakens atomic write semantics. `TryCFR` currently uses `io.Copy` rather than explicit copy-file-range here. Permission errors during list are skipped.

Test signals: `TestDisk`, `TestDisk2`, and `TestListAllWithDelimiterDeepStart` exercise object and filesystem behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/file_darwin.go -->
# sources/distributed-fs/juicefs/pkg/object/file_darwin.go

Purpose: provides Darwin-specific timestamp helpers for local filesystem storage.

Important APIs and flow: `getAtime` extracts access time from `syscall.Stat_t.Atimespec` and falls back to `ModTime` if the stat shape is unexpected. `lchtimes` builds two `unix.Timespec` values, uses Darwin's `UTIME_OMIT` equivalent `Sec: -2, Nsec: -2` for atime, and calls `unix.UtimesNanoAt` with `AT_SYMLINK_NOFOLLOW` so only symlink mtime changes.

State and persistence: modifies filesystem timestamps in place, specifically mtime without following symlinks.

Dependencies and integration: used by non-Windows `filestore.Chtimes` from `file_unix.go`. Depends on `golang.org/x/sys/unix` and Darwin syscall stat layout.

Risks: hard-coded `-2` mirrors SDK constants rather than using a named Darwin constant. Behavior depends on filesystem support for no-follow utimes. Atime argument is intentionally ignored.

Test signals: `file_unix_test.go` covers `lchtimes` preserving symlink atime and changing symlink mtime on non-Windows platforms; Darwin-specific execution depends on running tests on macOS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/file_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/file_linux.go -->
# sources/distributed-fs/juicefs/pkg/object/file_linux.go

Purpose: provides Linux-specific timestamp helpers for local filesystem storage.

Important APIs and flow: `getAtime` extracts access time from `syscall.Stat_t.Atim`, falling back to mtime when unavailable. `lchtimes` uses `unix.UtimesNanoAt` with `AT_SYMLINK_NOFOLLOW`, sets atime to `unix.UTIME_OMIT`, and sets mtime from the caller's value.

State and persistence: updates mtime on the filesystem path without following symlinks and leaves atime unchanged.

Dependencies and integration: used by `filestore.Chtimes` in `file_unix.go`. Depends on Linux stat fields and `golang.org/x/sys/unix`.

Risks: filesystem or kernel support for no-follow timestamp updates can vary. Atime input is ignored by design. Error wrapping returns an `os.PathError` with operation `"lchtimes"`.

Test signals: `TestLChtimes` in `file_unix_test.go` validates symlink mtime changes and atime preservation on non-Windows, including Linux.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/file_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/file_unix.go -->
# sources/distributed-fs/juicefs/pkg/object/file_unix.go

Purpose: supplies Unix-only owner/group extraction and mtime changes for `filestore`.

Important APIs and flow: `getOwnerGroup` inspects `info.Sys()` as either `*syscall.Stat_t` or `*sftp.FileStat`, converting UID/GID to names through `utils.UserName` and `utils.GroupName`. `(*filestore).Chtimes` maps an object key to a path and calls platform-specific `lchtimes` to change mtime without following symlinks.

State and persistence: no standalone persistent state, but `Chtimes` changes local filesystem metadata.

Dependencies and integration: compiled for `!windows`; bridges local filesystem and SFTP stat representations to the common `File` metadata interface. Requires `file_linux.go` or `file_darwin.go` to provide `lchtimes` and `getAtime` on supported Unix targets.

Risks: owner/group lookup depends on host user/group databases and may return empty names. SFTP metadata support depends on the remote server and SFTP library stat values. The actual atime behavior is delegated to OS-specific files.

Test signals: `file_unix_test.go` tests the timestamp path. Broader owner/group behavior is indirectly covered in filesystem contract tests where metadata is compared after chmod/chown on capable backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/file_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/file_unix_test.go -->
# sources/distributed-fs/juicefs/pkg/object/file_unix_test.go

Purpose: validates Unix symlink timestamp handling used by local filesystem storage.

Important APIs and flow: `TestLChtimes` creates a temporary regular file and symlink, captures the symlink's old stat and access time through `getAtime`, calls `lchtimes` with an mtime one hour earlier, then `Lstat`s the symlink again. It asserts the symlink mtime changed to the requested value and atime stayed unchanged.

State and persistence: uses temporary filesystem entries only.

Dependencies and integration: compiled only on `!windows`. It directly exercises OS-specific `lchtimes` implementations and their shared `getAtime` helpers.

Risks and gaps: exact timestamp equality can be sensitive to filesystem timestamp precision. The test covers symlink metadata, not regular-file `Chtimes` through `filestore`. It does not cover error paths such as unsupported filesystems.

Test signal: focused regression coverage for preserving atime and avoiding symlink-following timestamp changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/file_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/file_windows.go -->
# sources/distributed-fs/juicefs/pkg/object/file_windows.go

Purpose: supplies Windows-specific filesystem metadata helpers for `filestore`.

Important APIs and flow: `getOwnerGroup` returns empty owner and group strings. `lookupUser` and `lookupGroup` are stubs returning 0. `(*filestore).Chtimes` maps the object key to a local path and calls `os.Chtimes` with zero atime and requested mtime.

State and persistence: changes local Windows filesystem timestamps through `os.Chtimes`; no owner/group state is tracked.

Dependencies and integration: compiled on Windows in place of Unix helpers. It lets `filestore` satisfy `FileSystem` with reduced ownership semantics.

Risks: ownership information is unavailable and chown behavior in `file.go` relies on `utils.LookupUser`/`LookupGroup`, not these stubs, so Windows permission semantics remain limited. `os.Chtimes` follows normal Windows behavior and does not provide the Unix no-follow symlink semantics used elsewhere.

Test signals: no Windows-specific test in this subset. Cross-platform filesystem tests can cover basic storage behavior when run on Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/file_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/filesystem_test.go -->
# sources/distributed-fs/juicefs/pkg/object/filesystem_test.go

Purpose: defines a reusable contract test for filesystem-like object backends.

Important APIs and flow: `testFileSystem` creates a small directory tree, verifies directory `Head`, lists with prefixes, exercises chmod effects on listings, tests symlink creation/readlink/head/list behavior for stores implementing `SupportSymlink`, and writes a 255-character filename. It is invoked by `TestDisk2`, `TestSftp2`, `TestCifs2`, `TestHDFS2`, `TestNFS2`, and Gluster tests. `testKeysEqual` provides strict ordered key comparisons.

State and persistence: tests mutate temporary disk storage or configured external filesystems, then delete created keys in reverse order to handle directory emptiness.

Dependencies and integration: validates the `ObjectStorage`, `FileSystem`, and `SupportSymlink` contracts for local and network filesystem adapters. It expects delimiter listing and recursive `listAll` behavior from package helpers.

Risks and gaps: many backends are environment-gated and skipped without credentials or services. Permission behavior has backend-specific exceptions for NFS, CIFS, and Gluster. Cleanup failures can fail tests after earlier assertions.

Test signal: high-value shared behavioral coverage for path ordering, directory markers, permissions, symlink following, and long names across filesystem-style implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/filesystem_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/gluster.go -->
# sources/distributed-fs/juicefs/pkg/object/gluster.go

Purpose: implements GlusterFS object storage behind the `gluster` build tag, registering `gluster`.

Important APIs and flow: `gluster` holds one or more `gfapi.Volume` clients and selects them round-robin through an atomic counter. `Head`, `Get`, `Put`, `Delete`, `List`, `Chmod`, and metadata conversion map JuiceFS object operations to gfapi calls. `Put` creates directories as needed, writes through a 1 MiB buffer, calls `Sync`, and removes partial files on errors. `readDirSorted` filters `.`/`..`, handles symlinks when requested, filters non-regular files, and sorts entries.

State and persistence: persistent state lives in the Gluster volume. Local state is the mounted gfapi clients and selected log configuration.

Dependencies and integration: depends on `github.com/juicedata/gogfapi/gfapi`, shared `mEntry`, `file`, `bufPool`, and Unix owner/group helpers. `newGluster` parses `gluster://host[,host]/volume`, supports `JFS_NUM_GLUSTER_CLIENTS`, log level, and log path.

Risks: build requires Gluster support. `Chtimes` and `Chown` are not supported. Writes are not temp-renamed like `filestore`, so partial files can be visible until error cleanup. Host ports are noted as unsupported. Listing uses filepath joins and slash normalization carefully but remains path-sensitive.

Test signals: `gluster_test.go` runs shared storage and filesystem tests only when built with `gluster` and `GLUSTER_VOLUME` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/gluster.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/gluster_test.go -->
# sources/distributed-fs/juicefs/pkg/object/gluster_test.go

Purpose: wires GlusterFS into JuiceFS shared object and filesystem contract tests.

Important APIs and flow: `TestGluster` checks `GLUSTER_VOLUME`, creates a Gluster backend with `newGluster`, and calls `testStorage`. `TestGluster2` does the same but calls `testFileSystem`.

State and persistence: tests mutate the configured external Gluster volume, so they are skipped unless explicitly configured.

Dependencies and integration: compiled only with the `gluster` build tag. Depends on `newGluster`, `testStorage`, and `testFileSystem`.

Risks and gaps: no unit-level mocking; failures require a live Gluster environment to reproduce. The constructor error is ignored in both tests, so a nil backend could cause less clear downstream failures. Coverage is broad when enabled but absent in default builds.

Test signal: environment-gated integration coverage for both object-store semantics and filesystem-specific semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/gluster_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/gs.go -->
# sources/distributed-fs/juicefs/pkg/object/gs.go

Purpose: implements Google Cloud Storage behind `!nogs`, registering `gs`.

Important APIs and flow: `gs` maintains multiple `storage.Client` instances and selects them round-robin. `Create` probes list, discovers project ID from env, metadata, or default credentials, guesses region from metadata zone, and creates the bucket. `Head`, `Get`, `Put`, `Copy`, `Delete`, and `List` use the GCS client. `Put` sets storage class from active tier and a 5 MiB writer chunk size. `List` uses `iterator.Pager`, supports delimiter common prefixes, and returns page tokens.

State and persistence: persistent state is GCS bucket/object data. Local state includes clients, bucket, region, tier config, and atomic index.

Dependencies and integration: depends on `cloud.google.com/go/storage`, Google auth/metadata packages, shared `Tier`, `ResponseAttrs`, and `DefaultStorageClass`.

Risks: `newGS` returns a `gs` with zero-value tier map unless `InitTiers` is called; methods like `Create` and `Put` assume tier access. Credential discovery and bucket creation require environment or metadata availability. Restore is unsupported because GCS does not expose the same temporary restore operation. `ListAll` is inherited/default unsupported unless generic helpers use `List`.

Test signals: `TestGS` is environment-gated on `GOOGLE_APPLICATION_CREDENTIALS` and runs `testStorage`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/gs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/hdfs.go -->
# sources/distributed-fs/juicefs/pkg/object/hdfs.go

Purpose: implements HDFS storage behind `!nohdfs`, registering `hdfs`.

Important APIs and flow: `hdfsclient` wraps `colinmarc/hdfs` with address, base path, replication, umask, and close retry timings. `path` joins base path and key. `Head` maps HDFS `FileInfo` to JuiceFS `file`, normalizing HDFS superuser/group to root and sticky bit representation. `Get` returns empty for directories/out-of-range offsets or a section reader for ranges. `Put` creates temp files unless `PutInplace`, creates parents, handles existing temp paths, writes with `bufPool`, retries `Close` while HDFS reports replication in progress, then renames. `List` implements delimiter `/` sorted by path. `Chtimes`, `Chmod`, and `Chown` map to HDFS operations.

State and persistence: persistent state is HDFS files and directories under `basePath`. Temporary `.jfs.*` files may exist during writes.

Dependencies and integration: uses Hadoop configuration loading, optional Kerberos client, shared `FileSystem`, `SectionReaderCloser`, and `TmpFilePath`. `parseHDFSAddr` supports namenode HA nameservices from Hadoop config.

Risks: context parameters are not passed to the HDFS client. `Chtimes` updates atime too, noted by a FIXME. Close retry may delay writes for up to configured timeouts. User/group mapping is environment-sensitive.

Test signals: `TestHDFS` validates address parsing unconditionally, then runs storage tests only with `HDFS_ADDR`; `TestHDFS2` runs filesystem tests when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/hdfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/hdfs_kerberos.go -->
# sources/distributed-fs/juicefs/pkg/object/hdfs_kerberos.go

Purpose: supplies Kerberos authentication support for HDFS builds.

Important APIs and flow: `getKerberosClient` loads krb5 config from `KRB5_CONFIG` or `/etc/krb5.conf`. It first tries keytab authentication from `KRB5KEYTAB_BASE64` or `KRB5KEYTAB` plus `KRB5PRINCIPAL`, splitting principal into username and realm. If no keytab is available, it loads a credential cache from `KRB5CCNAME`, stripping `FILE:` prefixes, or defaults to `/tmp/krb5cc_{uid}`. It returns a gokrb5 client from keytab or ccache.

State and persistence: reads host Kerberos config, keytab material, and ccache files. It does not write credentials.

Dependencies and integration: used by `newHDFS` when Hadoop client options already indicate Kerberos. Depends on `github.com/jcmturner/gokrb5/v8`.

Risks: `KRB5PRINCIPAL` must include `@realm` for keytab mode. Unsupported ccache schemes error. Base64 keytab data in environment is sensitive. Logging includes username and realm. Runtime behavior depends heavily on host Kerberos configuration.

Test signals: no direct tests in this subset; HDFS integration tests cover this only in a configured Kerberized environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/hdfs_kerberos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/ibmcos.go -->
# sources/distributed-fs/juicefs/pkg/object/ibmcos.go

Purpose: implements IBM Cloud Object Storage behind `!noibmcos`, registering `ibmcos`.

Important APIs and flow: `ibmcos` directly uses IBM's S3-compatible SDK. It supports create, limits, get, restore, put, copy, head, delete, list, multipart upload, upload part, abort, complete, and list uploads. `Put` ensures an `io.ReadSeeker`, guesses content type, applies storage class and encoded tags, and captures request ID. `List` decodes URL-encoded keys and common prefixes. Multipart copy is explicitly unsupported.

State and persistence: bucket objects, storage class, restore status, tags, and multipart uploads persist in IBM COS. Local state is bucket, S3 client, and tier config.

Dependencies and integration: uses `github.com/IBM/ibm-cos-sdk-go`, IAM static credentials, shared `Tier`, `decodeKey`, and `DefaultStorageClass`. `newIBMCOS` parses bucket and region from host labels and creates IAM credentials from API key and service instance ID arguments.

Risks: endpoint parsing assumes a specific IBM COS hostname layout. `newIBMCOS` ignores the URL parse error. Context is not used for `Create`/`Restore`. Non-seekable puts buffer the full object. List upload time parsing has a FIXME. Upload-part-copy is not supported even though other S3-like stores may support it.

Test signals: `TestIBMCOS` is environment-gated on `IBMCOS_ENDPOINT` and then runs shared storage tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/ibmcos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/interface.go -->
# sources/distributed-fs/juicefs/pkg/object/interface.go

Purpose: defines the central object-storage interfaces and shared object metadata structs.

Important APIs and flow: `Object` exposes key, size, mtime, directory/symlink flags, storage class, and status. `obj` is the default implementation. `MultipartUpload`, `Part`, `PendingPart`, and `Limits` standardize multipart capabilities. `ObjectStorage` defines idempotent storage operations, all context-first, including create, get, put, copy, delete, head, list, list-all, multipart lifecycle, and restore. `Shutdownable` plus `Shutdown` unwraps encrypted, chunked encrypted, prefix, and sharded wrappers to close underlying stores.

State and persistence: no persistent state itself; it specifies the contract all backends implement.

Dependencies and integration: imports only `context`, `io`, and `time`, but names wrapper types implemented elsewhere (`encrypted`, `chunkedEncrypted`, `withPrefix`, `sharded`) in `Shutdown`.

Risks: changing method signatures affects all providers; `context_cancellation_test.go` guards this. The interface combines simple stores with advanced multipart/restore features, so many implementations rely on `DefaultObjectStorage` unsupported defaults.

Test signals: reflection tests enforce context-first signatures; broad storage tests exercise behavior through this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/ks3.go -->
# sources/distributed-fs/juicefs/pkg/object/ks3.go

Purpose: implements Kingsoft KS3 storage behind `!nos3 && !noks3`, registering `ks3`.

Important APIs and flow: `ks3` wraps the KS3 SDK. It implements create, limits, head, get, put, copy, delete, list, restore, multipart create/upload/copy/abort/complete/list. Helper dereference functions handle nullable time and bool pointers. `Head` maps 404 to `os.ErrNotExist` and defaults storage class to `STANDARD` when metadata is absent. `Put` buffers non-seekable readers, guesses MIME type, applies tier storage class and tag. `newKS3` parses bucket and region from endpoint host, maps KS3 regions, optionally uses AWS_REGION for non-KS3 endpoints, and unescapes credentials.

State and persistence: object data, metadata, tags, restore status, and multipart uploads persist in KS3. Local state is bucket, SDK client, and tiers.

Dependencies and integration: uses `github.com/ks3sdklib/aws-sdk-go`, shared `decodeKey`, `DefaultStorageClass`, `ResponseAttrs`, and package `httpClient`.

Risks: endpoint parsing assumes bucket.region host patterns and slices `hostParts[1][3:]`. For native KS3 domains, path-style is disabled. Non-seekable puts are fully buffered. List upload timestamp parsing has a FIXME. Request/storage-class attrs depend on KS3 metadata keys.

Test signals: `TestKS3` is environment-gated on `KS3_ACCESS_KEY` and runs the shared object-storage contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/ks3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/mem.go -->
# sources/distributed-fs/juicefs/pkg/object/mem.go

Purpose: implements an in-memory object storage registered as `mem`, primarily for tests and local transient use.

Important APIs and flow: `memStore` protects a map of key to `mobj` with a mutex. `Head`, `Get`, `Put`, `Copy`, `Delete`, and `List` implement the common object contract. Empty keys are rejected. `Get` slices byte data by offset/limit. `Put` reads the entire input and stores mtime as `time.Now()`. `List` scans all keys, handles delimiter common prefixes, sorts by key, applies limit, and calls `generateListResult`.

State and persistence: all state is process-local memory in `objects`; it is lost on process exit. `mobj` can hold mode, owner, and group fields, but `Put` currently stores only data and mtime.

Dependencies and integration: embeds `DefaultObjectStorage` and returns `file` metadata objects so tests can use common file/object assertions. Used heavily by encryption and object-storage tests.

Risks: no persistence, no efficient large-object handling, and no context cancellation. The delimiter code derives common-prefix metadata from the first matching object, which may carry mostly empty owner/mode values. Copy does not close the reader returned by `Get`.

Test signals: `TestMem`, encryption tests, chunked encryption tests, sharding tests, and many helper paths rely on this backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/mem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/minio.go -->
# sources/distributed-fs/juicefs/pkg/object/minio.go

Purpose: implements MinIO/S3-compatible storage behind `!nos3`, registering `minio`.

Important APIs and flow: `minio` embeds the generic `s3client`, overriding `String` and multipart `Limits`. `newMinio` normalizes endpoints to HTTP, parses SSL and optional `region` query, falls back to `MINIO_REGION`, `MINIO_ACCESS_KEY`, and `MINIO_SECRET_KEY`, loads AWS SDK v2 config, builds an S3 client with custom base endpoint, path-style setting, shared HTTP client, unsigned payload middleware, and a single retry attempt. It extracts the bucket from the endpoint path, including a compatibility case for paths starting with `minio/`.

State and persistence: all persistent behavior is delegated to the remote MinIO bucket through `s3client`.

Dependencies and integration: uses AWS SDK v2 and package helpers `defaultPathStyle`, `httpClient`, and generic S3 code outside this subset.

Risks: missing bucket path is an error. Endpoint path parsing only uses the first path segment after optional `minio/`. All provider behavior beyond construction depends on `s3client`. Path-style defaults can be critical for MinIO deployments.

Test signals: `TestMinIO` is environment-gated on `MINIO_TEST_BUCKET`; when configured it runs `testStorage`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/minio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/nfs.go -->
# sources/distributed-fs/juicefs/pkg/object/nfs.go

Purpose: implements NFSv3-backed object storage behind `!nonfs`, registering `nfs`.

Important APIs and flow: `nfsStore` wraps a mounted `nfs.Target`, user identity, root, and default file/directory modes. `Head` follows symlinks by reading the link target and recursively heading it, marking the result symlink. `Get`, `Put`, `Delete`, `List`, `Chtimes`, `Chmod`, `Chown`, `Symlink`, and `Readlink` map object operations to NFS calls. `mkdirAll` recursively creates directories. `List` uses `ReadDirPlus`, symlink following rules, sorting, and delimiter-only listing.

State and persistence: persistent data is in the mounted NFS export. Writes use temp object names unless `PutInplace`, then rename. Owner/group and mode changes call NFS setattr.

Dependencies and integration: uses `github.com/vmware/go-nfs-client/nfs`, RPC auth from current UID/GID, shared `FileSystem`, `SupportSymlink`, `mEntry`-like behavior, and `utils` user/group lookups.

Risks: `ListAll` is explicitly unsupported, so generic list-all must use delimiter traversal. Context arguments are mostly not used by NFS calls. Symlink resolution uses path joins and may behave differently from POSIX for edge cases. `newNFSStore` requires `host:path` format and sets large read-dir counts. Empty root delete is a no-op.

Test signals: `TestNFS` and `TestNFS2` are environment-gated and run shared object/filesystem contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/nfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/object_storage.go -->
# sources/distributed-fs/juicefs/pkg/object/object_storage.go

Purpose: provides shared object-storage infrastructure: registration, default unsupported methods, file metadata helpers, list traversal, temp naming, and tier management.

Important APIs and flow: `Register`, `IsSupported`, and `CreateStorage` manage backend constructors. `DefaultObjectStorage` supplies nil/no-op/`notSupported` implementations so providers can override only supported features. `MarshalObject` and `UnmarshalObject` serialize object/file metadata. `ListAllWithDelimiter` recursively walks delimiter-based listings with prefetch worker goroutines and ordered output. `generateListResult`, `decodeKey`, and `TmpFilePath` are small shared helpers. `tierStorage` implements `SupportTier`, validates tags, encodes tags for HTTP headers, and returns a tier from `context` via `TierKey`.

State and persistence: global state includes `ctx`, logger, `UserAgent`, registry map, and pooled copy buffers. Tier state is per storage instance.

Dependencies and integration: used by nearly every backend. `Shutdown` is defined in `interface.go`; wrappers and providers rely on `DefaultObjectStorage` and tier helpers.

Risks: `storages` map is global and unguarded, safe for init-time registration but not concurrent mutation. `ListAllWithDelimiter` has complex coordination and sends `nil` as an error sentinel. `UnmarshalObject` assumes JSON-decoded numeric fields are `float64` and can panic on malformed maps. `TmpFilePath` uses `math/rand` global randomness, not collision-proof.

Test signals: broad indirect coverage through all storage tests; `TestMarsharl`, `TestNameString`, and `TestListAllWithDelimiterDeepStart` cover selected helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/object_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/object_storage_test.go -->
# sources/distributed-fs/juicefs/pkg/object/object_storage_test.go

Purpose: defines the broad shared test suite for `ObjectStorage` implementations.

Important APIs and flow: `testStorage` exercises create idempotence, prefix wrapping, cleanup, Unicode/control-character keys, missing gets, ranged gets, list/list-all ordering, storage-class attrs, overwrite, directory-like keys, multipart upload and optional upload-part-copy, copy, delete idempotence, empty objects, and slash-suffixed keys. Helper `listAll` routes through package `ListAll`; `setStorageClass` configures tiers for stores supporting `SupportTier`. Individual `Test*` functions instantiate many backends, usually guarded by environment variables.

State and persistence: tests mutate either `mem`, temp disk paths, or external object stores. Cleanup is best effort through deletes and deferred calls. `TestMain` can load environment variables from a file.

Dependencies and integration: integrates almost every backend in the package, plus wrappers such as encrypted and sharded stores. Also validates HDFS address parsing, endpoint regexes, marshal/unmarshal, prefix naming, and delimiter traversal.

Risks and gaps: many cloud/provider tests are skipped by default. Shared assertions include provider-specific relaxations, so edge behavior can be tolerated. Some constructor errors are ignored in environment tests. Tests are mutating and require isolated buckets or prefixes.

Test signal: very high as a behavioral contract for object semantics across providers when relevant environments are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/object_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/obs.go -->
# sources/distributed-fs/juicefs/pkg/object/obs.go

Purpose: implements Huawei Cloud OBS behind `!noobs`, registering `obs`.

Important APIs and flow: `obsClient` wraps the OBS SDK and tier config. It supports create, limits, head, get, put, copy, restore, delete, list, multipart create/upload/copy/abort/complete/list. `Put` computes MD5 and content length for all inputs, sets content MD5, MIME type, storage class, and optional tags, then optionally validates ETag when bucket encryption is absent. `Copy` can replace tags by adding placeholder metadata. `newOBS` normalizes endpoint, discovers bucket region when needed, configures proxy from environment, disables SDK retry due to seek issues, and detects whether ETag checking is safe.

State and persistence: object data, storage class, tags, restore status, and multipart uploads persist in OBS. Local state includes bucket, region, ETag-check flag, SDK client, and tiers.

Dependencies and integration: uses Huawei OBS SDK, shared `Tier`, `ResponseAttrs`, `getRange`, `checkGetStatus`, and `httpClient` transport.

Risks: non-seekable puts buffer entire data. Region parsing assumes known OBS hostname format. ETag validation is disabled for encrypted buckets but detection can warn and continue. SDK retry is disabled, affecting transient-failure resilience. `ListAll` unsupported.

Test signals: `TestOBS` is environment-gated and runs the shared storage suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/obs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/oos.go -->
# sources/distributed-fs/juicefs/pkg/object/oos.go

Purpose: implements CTYun OOS/S3-compatible storage behind `!nos3`, registering `oos`.

Important APIs and flow: `oos` embeds `s3client`, overriding `String`, `Limits`, `Create`, and `List`. `Create` does not create buckets; it probes list and asks the user to create the bucket manually on failure. `List` caps limit at 1000, delegates to `s3client.List`, and removes the first object when it equals the `start` marker to handle provider-inclusive listing. `newOOS` parses bucket and region from endpoint host, derives service endpoint, chooses path-style except for `xstore.ctyun.cn`, and builds an AWS SDK v2 S3 client with static credentials and unsigned payload middleware.

State and persistence: persistent data is delegated to the remote OOS bucket via `s3client`.

Dependencies and integration: uses AWS SDK v2, shared S3 implementation, `httpClient`, and `defaultPathStyle`-style behavior.

Risks: endpoint parsing assumes host label shape where the second label starts with a region prefix sliced by `[4:]`. Bucket creation is unsupported operationally. Inclusive-marker adjustment is provider-specific and can affect pagination if the delegate behavior changes.

Test signals: `TestOOS` is environment-gated on `OOS_ACCESS_KEY` and runs the shared storage suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/oos.go -->
