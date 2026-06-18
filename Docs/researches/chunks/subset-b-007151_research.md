# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 1-5866

## Scope

This chunk is the opening section of the Hadoop Common 2.6.0 JDiff XML API snapshot generated from public and protected Javadoc. It is not executable source code; it records API surface, inheritance, visibility, exceptions, deprecation metadata, and selected documentation. The covered range starts at the XML/API header and includes packages `org.apache.hadoop`, `org.apache.hadoop.conf`, `org.apache.hadoop.crypto`, `org.apache.hadoop.crypto.key`, `org.apache.hadoop.crypto.key.kms`, `org.apache.hadoop.crypto.random`, and the start of `org.apache.hadoop.fs` through part of `CommonConfigurationKeysPublic`.

The chunk stops inside `CommonConfigurationKeysPublic`, ending after `KMS_CLIENT_ENC_KEY_CACHE_LOW_WATERMARK`; later constants and later filesystem APIs are outside this mapped item.

## Purpose

The XML file is a release API baseline for Hadoop Common. JDiff consumes this form to compare public/protected API compatibility across Hadoop releases. For this chunk, the baseline describes the core exception type, the configuration system, runtime reconfiguration hooks, key-provider and KMS extension APIs, and early filesystem abstractions.

This source sits under `dev-support/jdiff`, so its primary function is compatibility governance rather than runtime behavior. It is still important because the XML encodes which classes, methods, constructors, fields, deprecations, and thrown exceptions Hadoop Common 2.6.0 exposed to downstream projects.

## Important APIs, Types, and Functions

### API metadata and base exception

- The root `<api>` names the baseline `hadoop-core 2.6.0`, generated with JDiff 1.0.9 and the `ExcludePrivateAnnotationsJDiffDoclet`.
- `org.apache.hadoop.HadoopIllegalArgumentException` extends `IllegalArgumentException` to distinguish invalid argument failures raised by Hadoop implementation code from those raised by the JDK.

### Configuration model

- `Configurable` defines the minimal `setConf(Configuration)` / `getConf()` contract.
- `Configured` is a concrete base class implementing `Configurable` for objects that carry a Hadoop `Configuration`.
- `Configuration` is the central mutable configuration container. It implements `Iterable` and Hadoop `Writable`, has constructors for default loading, explicit no-default loading, and copy construction, and exposes broad APIs for resource loading, typed access, mutation, serialization, class loading, diagnostics, and deprecation handling.
- Resource APIs include `addDefaultResource`, `addResource` overloads for classpath names, `URL`, `Path`, `InputStream`, named `InputStream`, and another `Configuration`, plus `reloadConfiguration`.
- Lookup and mutation APIs include `get`, `getTrimmed`, `getRaw`, `set`, `unset`, `setIfUnset`, and typed helpers for `int`, `long`, byte-size longs, `float`, `double`, `boolean`, enums, time durations, regex `Pattern`, ranges, string collections, password lookup, socket addresses, class names, instances, local paths, files, and resources.
- Persistence and diagnostics APIs include `writeXml(OutputStream)`, `writeXml(Writer)`, static `dumpConfiguration`, `readFields`, `write`, `iterator`, `size`, `clear`, `getFinalParameters`, `getPropertySources`, `getValByRegex`, `dumpDeprecatedKeys`, and `hasWarnedDeprecation`.
- `Configuration.DeprecationDelta` represents pending global deprecation mappings from an old key to one or more replacement keys plus an optional custom message.
- `Configuration.IntegerRanges` parses positive integer range strings such as `2-3,5,7-` and supports membership tests and iteration.

### Runtime reconfiguration

- `Reconfigurable` extends `Configurable` with `reconfigureProperty`, `isPropertyReconfigurable`, and `getReconfigurableProperties`.
- `ReconfigurableBase` supplies an abstract base for background reconfiguration tasks. Its final `reconfigureProperty` updates the `Configuration` and delegates implementation-specific state updates to `reconfigurePropertyImpl`.
- `ReconfigurationException` records the property, requested new value, and old value for failed runtime changes.
- `ReconfigurationServlet` exposes HTTP GET/POST integration for reviewing and approving node configuration changes. Its public field `CONF_SERVLET_RECONFIGURABLE_PREFIX` is the servlet-context naming prefix for reconfigurable objects.
- `ReconfigurationTaskStatus` exposes task existence, stopped/running state, start/end times, and a status map.
- `ReconfigurationUtil` and `PropertyChange` compare old/new `Configuration` objects and represent changed property triples.

### Key provider and crypto APIs

- `CachingKeyProvider` wraps a `KeyProvider` and caches key versions and metadata for short-lived bursts, invalidating relevant cache entries on delete and key roll.
- `JavaKeyStoreProvider.Factory`, `UserProvider.Factory`, and `KMSClientProvider.Factory` are `KeyProviderFactory` implementations discovered through `ServiceLoader`.
- `JavaKeyStoreProvider.KeyMetadata` adapts Hadoop key metadata to `java.security.Key`/`Serializable` so it can be stored in a Java KeyStore.
- `KeyProvider` is the abstract provider of secret key material. It defines provider configuration access, option creation, transient-provider detection, key listing, metadata lookup, version lookup, key creation, key deletion, key rolling, flush/close, generated key material, version-name helpers, provider lookup, and default cipher/bit-length constants. The Javadoc states implementations must be thread-safe.
- `KeyProvider.KeyVersion` carries a key name, version name, and material bytes.
- `KeyProvider.Metadata` carries cipher, bit length, description, attributes, creation date, and version count, with protected byte serialization/deserialization helpers.
- `KeyProvider.Options` is the fluent key-creation options holder for cipher, bit length, description, and attributes.
- `KeyProviderExtension<E>` is an abstract delegating wrapper that forwards normal `KeyProvider` operations to an underlying provider while exposing an extension object.
- `KeyProviderExtension.Extension` is a marker for extension interfaces.
- `KeyProviderCryptoExtension.CryptoExtension` adds encrypted-key generation, encrypted-key decryption, warm-up, and queue drain behavior.
- `KeyProviderCryptoExtension.EncryptedKeyVersion` carries the encryption key name, encryption key version name, encrypted-key IV, and encrypted encryption key version. Its `createForDecryption` factory permits partially populated objects for decrypt paths, and `deriveIV` avoids direct IV reuse.
- `KeyProviderDelegationTokenExtension` and nested `DelegationTokenExtension` add delegation-token acquisition into Hadoop `Credentials`.
- `KeyProviderFactory` creates providers from configured URI paths via service loading, with public `KEY_PROVIDER_PATH`.
- `KeyShell` is the CLI `Tool` for key-provider operations and exposes public `out` and `err` streams for test capture.
- KMS-specific public nested types in this chunk include `KMSClientProvider.KMSEncryptedKeyVersion`, `KMSKeyVersion`, and `KMSMetadata`, plus `ValueQueue.QueueRefiller` and `ValueQueue.SyncGenerationPolicy`.

### Filesystem APIs

- `AbstractFileSystem` is the public implementor-facing filesystem abstraction used through `FileContext`. It validates URI scheme/authority/path membership, creates filesystem instances from `fs.AbstractFileSystem.<scheme>.impl`, tracks per-filesystem statistics, qualifies paths, exposes home and initial working directories, and defines abstract or overridable filesystem operations.
- Covered `AbstractFileSystem` operations include create/open/delete/rename/mkdir, symlink support and link target lookup, permissions and ownership updates, timestamp updates, checksums, file status and link status, block locations, filesystem status, listing, corrupt block iteration, checksum verification, canonical service name, delegation tokens, ACL operations, xattr operations, and equality/hash behavior.
- `AvroFSInput` adapts `FSDataInputStream` and `FileContext`/`Path` to Avro `SeekableInput`.
- `BatchedRemoteIterator` implements batched remote pagination with `makeRequest(prevKey)`, `elementToPrevKey(element)`, and `RemoteIterator` methods. `BatchedEntries` abstracts a returned page; `BatchedListEntries` backs it with a `List`.
- `BlockLocation` models replica hostnames, cached hosts, transfer names, topology paths, file offset, length, and corrupt state.
- `ByteBufferReadable` defines stream reads directly into `ByteBuffer` and documents caller-visible position/limit semantics and possible `UnsupportedOperationException`.
- `CanSetDropBehind` and `CanSetReadahead` define optional stream tuning knobs.
- `ChecksumException` extends `IOException` and records the file position of a checksum error.
- `ChecksumFileSystem` is an abstract `FilterFileSystem` that creates and verifies client-side checksum files alongside raw files. It provides checksum file naming/length helpers, verification/write toggles, open/append/create/delete/rename/list/copy/local-output behavior, and checksum failure reporting.
- The visible portion of `CommonConfigurationKeysPublic` declares public constants for native library availability, network topology scripts and mappings, default filesystem name, disk usage/status intervals, symlink resolution, trash intervals, local block size default, automatic filesystem close, file and FTP filesystem implementation settings, MapFile/TFile/SequenceFile I/O settings, IPC client/server retry and socket settings, socket factories, hash type, group mapping caches, authentication and authorization, SSL/HTTP policy, RPC protection, SASL props, crypto codec/cipher/provider/buffer settings, impersonation provider, and KMS encrypted-key cache settings.

## Control Flow

The XML itself has no runtime control flow. Its structure is deterministic: package elements contain class/interface declarations, each declaration lists constructors, methods, fields, implemented interfaces, exceptions, and Javadoc text.

The runtime flows described by the API docs are:

- `Configuration` loads default resources (`core-default.xml`, then `core-site.xml`) unless disabled, then overlays later resources in insertion order while respecting final parameters. Getters trigger variable expansion and deprecation alias resolution. Setters update deprecated/replacement aliases as documented. Reload clears resource-derived values and final flags so resources are reread lazily on the next access while explicitly set values remain overlaid.
- Global configuration deprecations are updated by creating a new deprecation context from the old one and atomically swapping it in, retrying on races.
- Reconfiguration compares a freshly loaded configuration with the old one, presents or starts changes through the servlet/background task API, then applies accepted properties by calling the final `ReconfigurableBase.reconfigureProperty`, which updates `Configuration` and delegates internal state mutation to subclass `reconfigurePropertyImpl`.
- Key-provider flows center on `KeyProviderFactory.getProviders(conf)` and `get(uri, conf)` creating providers from configured URI schemes, then `KeyProvider` methods listing, creating, rolling, deleting, flushing, and retrieving key material. Extension wrappers delegate all base operations to the underlying provider while adding crypto or delegation-token behavior.
- Encrypted-key generation uses the current key version for a named encryption key, creates transient encrypted key material that is not stored by the provider, and later decrypts `EncryptedKeyVersion` objects using key name, key version, and IV.
- `AbstractFileSystem` factory flow maps a URI scheme to an implementation class in `Configuration`, constructs an implementation with the URI and config, and requires later path operations to pass paths that match the filesystem scheme/authority or are slash-relative. Many methods defer exact semantics to matching `FileContext` operations.
- `BatchedRemoteIterator` flow fetches a page keyed by the previous element key, yields elements from the page, and uses `hasMore` to decide whether another remote request is required.
- `ChecksumFileSystem` flow wraps raw filesystem operations, maps data paths to checksum paths, writes or verifies checksum side files depending on configuration, and can report checksum failures for retry decisions.

## State and Persistence Behavior

The JDiff XML is a persisted compatibility artifact. Changes to this file are meaningful because downstream compatibility tooling can interpret removed methods, changed signatures, changed exceptions, changed deprecation flags, or changed visibility as API drift.

The APIs represented here describe several stateful systems:

- `Configuration` owns mutable key/value state, loaded resources, final-parameter state, property source tracking, deprecation-warning state, class loader state, quiet-mode state, and serialized `Writable`/XML representations. It also participates in JVM-wide default-resource and deprecation maps.
- Configuration resources persist as XML files or streams. `writeXml` persists non-default properties, while `dumpConfiguration` emits a JSON-like diagnostic representation of all parameters and metadata except input-stream-loaded parameters.
- Password lookup intentionally prefers credential providers before cleartext configuration fallback, so secret state may live outside XML configuration in provider-backed storage.
- Reconfiguration state includes active or completed background task timestamps and per-property status results.
- Key provider implementations persist key material and metadata according to provider type. The abstract contract requires `flush()` to write changes to persistent storage; transient providers explicitly are not long-term storage. Metadata has protected byte serialization helpers for provider storage.
- `CachingKeyProvider` introduces in-memory cached copies of key versions and metadata with timeout behavior controlled by constructor arguments. Mutating operations must invalidate or refresh cache state.
- KMS client value queues cache encrypted keys and refill through `QueueRefiller`; the sync generation policy controls behavior when a queue is empty.
- `AbstractFileSystem` maintains statistics per filesystem URI scheme/authority and per-instance `statistics`. Filesystem operations mutate external persistent filesystem namespace state: files, directories, permissions, ACLs, xattrs, symlinks, replication, timestamps, and checksums.
- `ChecksumFileSystem` persists checksum side files for raw files and may copy or omit CRC files during local copy operations.
- `BlockLocation` is mutable metadata state for block placement/caching/corruption observations, not persistent storage by itself.

## Dependencies and Integration Points

- The JDiff generation command references the Hadoop annotations doclet, compiled Hadoop Common classes, Hadoop Auth, Guava, Commons CLI/Math/HTTP/IO/Net/Configuration/Logging/Lang/Collections/Compress, servlet API, Jetty, Jersey/Jackson/Jettison/JAXB, Log4j/SLF4J, Jets3t, HttpComponents, Avro, Snappy, Ant, Protobuf, Gson, Apache Directory Kerberos, Curator/ZooKeeper, JSch, FindBugs annotations, HTrace, Netty, and XZ.
- `Configuration` integrates with `Path`, local filesystem access, credential providers, `Writable`, class loading, Java regex/time/concurrency APIs, `InetSocketAddress`, `System` properties, and Hadoop default resources.
- Reconfiguration integrates with servlet APIs (`HttpServlet`, request/response, `ServletException`) and service/node classes that implement `Reconfigurable`.
- Key-provider APIs integrate with Java crypto (`Key`, `NoSuchAlgorithmException`, `GeneralSecurityException`), Java `URI`, Hadoop `Credentials`, Hadoop `Token`, service-loaded provider factories, Java KeyStore storage, user credential storage, and KMS HTTP-backed providers.
- Filesystem APIs integrate with `FileContext`, `FileSystem`, `Path`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `BlockLocation`, permissions/ACLs/xattrs, delegation tokens, Avro `SeekableInput`, and Hadoop security access-control exceptions.
- `CommonConfigurationKeysPublic` is the constant bridge to `core-default.xml` and therefore to user/admin configuration files.

## Risks and Edge Cases

- Because this is generated XML, manual edits risk corrupting compatibility baselines. The correct source of truth is the Java API and JDiff generation process.
- The chunk is a partial file range. Any per-file report must merge later chunks before concluding the full Hadoop Common 2.6.0 API surface.
- The root generation command embeds local absolute paths from the build machine. These are historical metadata, not portable build instructions.
- `Configuration` deprecation APIs have deprecated overloads that accept multiple replacement keys; docs say attempts to add deprecations after loading resources once can throw `UnsupportedOperationException`.
- `Configuration.addResource(InputStream)` caches stream contents and closes the stream after read, with explicit memory-use warning.
- Final configuration parameters block later resource overrides, which can surprise callers that expect last-writer-wins semantics.
- Variable expansion falls back to system properties, so values may depend on JVM environment at read time.
- Typed getters throw `NumberFormatException` for invalid numeric/time/range values except booleans and patterns, which document fallback behavior.
- `getPassword` may fall back to cleartext configuration if credential providers do not resolve the alias, preserving compatibility but weakening secret hygiene.
- Reconfiguration requires subclasses to update every internal structure derived from a property and recursively reconfigure owned `Reconfigurable` objects; partial implementations can leave live services inconsistent with their `Configuration`.
- `KeyProvider` implementations must be thread-safe and must respect `flush()` persistence semantics. Providers that cache metadata or key versions need careful invalidation on roll/delete.
- Encrypted-key APIs state generated encrypted keys are not stored by the provider; callers must persist returned encrypted key material where needed.
- `EncryptedKeyVersion.createForDecryption` returns partially populated objects, so code must avoid using them for operations other than decrypt paths.
- `AbstractFileSystem` distinguishes fully qualified paths from slash-relative paths and can throw `InvalidPathException`, `UnresolvedLinkException`, `UnsupportedFileSystemException`, `AccessControlException`, or `IOException` depending on operation and implementation.
- Several filesystem feature methods, including ACL/xattr/symlink-related operations, may be unsupported or implementation-specific despite being present in the abstract API.
- `ByteBufferReadable` explicitly allows implementations to throw `UnsupportedOperationException` and leaves buffer position/limit undefined after exceptions.
- `ChecksumFileSystem` side-file behavior means rename, delete, copy, and local-output paths must keep data files and checksum files consistent.
- `CommonConfigurationKeysPublic` includes deprecated MapReduce sort constants moved to MapReduce defaults and contains typoed documentation text such as "Defalt"; compatibility consumers should treat names and deprecation metadata as authoritative, not prose quality.

## Test Signals

- JDiff comparison tests should flag removed classes, changed method/constructor signatures, changed field visibility/static/final attributes, changed thrown exception sets, and changed deprecation metadata relative to this baseline.
- Configuration tests should cover default resource order, final parameters, resource overlays, reload behavior, variable expansion, deprecated-key aliases, source tracking, typed getter parse failures, password credential-provider fallback, XML/Writable round trips, and class loading.
- Reconfiguration tests should cover changed-property detection, successful property updates, rejected non-reconfigurable properties, exception detail fields, background task status transitions, and servlet GET/POST integration.
- Key-provider tests should cover service-loader factory selection by URI, create/delete/roll/current-version flows, metadata serialization, flush persistence, transient-provider behavior, delegation token pass-through, crypto extension encrypted-key generation/decryption, IV derivation, and cache invalidation in `CachingKeyProvider`.
- Filesystem tests should cover URI scheme/authority validation, path qualification, statistics registration/clearing, create/open/delete/rename/mkdir semantics, symlink resolution, permission/owner/time changes, status/listing/block-location APIs, delegation token retrieval, ACL and xattr operations, and unsupported-feature failures.
- Checksum filesystem tests should cover checksum file naming and length, write/verify toggles, open/create/append behavior, rename/delete consistency for checksum files, local copy CRC options, and checksum failure reporting.
- Constant compatibility tests should assert public names in `CommonConfigurationKeysPublic` remain stable, especially deprecated constants that downstream code may still compile against.
