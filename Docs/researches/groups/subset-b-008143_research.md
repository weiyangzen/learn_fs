# Research: subset-b-008143

Grouped research for Apache Ozone S3 gateway utility, S3 secret endpoint, deployment descriptors, and S3 gateway unit-test support files. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/S3StorageType.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/S3StorageType.java

Purpose: maps S3 storage class names to Ozone `ReplicationConfig` values. `REDUCED_REDUNDANCY` maps to RATIS/ONE, `STANDARD` to RATIS/THREE, and `STANDARD_IA` to EC 3-2. The reverse helper `fromReplicationConfig` classifies EC as `STANDARD_IA`, standalone or one-node configs as reduced redundancy, and other configs as standard.

Important APIs and control flow: enum constants carry immutable replication config instances exposed by `getReplicationConfig()`. `fromReplicationConfig` depends on `getReplicationType()` and `getRequiredNodes()`, so it treats all EC configs the same regardless of actual EC layout.

State, dependencies, integration: no persistence beyond enum-held config objects. Used by `S3Utils.toReplicationConfig` and likely object PUT/listing code to translate `x-amz-storage-class`. Depends on HDDS replication classes and protobuf replication type/factor enums.

Risks and test signals: unsupported or future S3 storage classes are absent by design. Reverse mapping loses precision for custom EC layouts and any multi-node non-EC config is reported as `STANDARD`. Tests in this subset exercise storage-class headers indirectly in multipart endpoint setup but do not directly assert all enum mappings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/S3StorageType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/S3Utils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/S3Utils.java

Purpose: central stateless utility class for S3 gateway encoding, storage-class replication resolution, exception wrapping, payload-signature classification, chunked-upload validation, ETag formatting, canonical-user ID generation, and Content-MD5 validation.

Important APIs and control flow: `urlDecode`/`urlEncode` use UTF-8 JDK encoders. `resolveS3ClientSideReplicationConfig` prioritizes explicit S3 storage-class headers, then client replication config, then bucket defaults. `toReplicationConfig` parses `S3StorageType.valueOf`; `STANDARD_IA` may use an `ECReplicationConfig` string override. `wrapOS3Exception` converts `OS3Exception` to `WebApplicationException` with XML entity and HTTP status. `hasUnsignedPayload` and `hasMultiChunksPayload` classify `x-amz-content-sha256`. `validateMultiChunksUpload` checks optional `Content-Encoding` for `aws-chunked` and requires `x-amz-decoded-content-length`. `validateSignatureHeader` supplies `UNSIGNED-PAYLOAD` only for unsigned requests; signed requests require the SHA header. `validateContentMD5` decodes base64, enforces 16 bytes, compares to server hex, and distinguishes invalid digest from bad digest.

State, dependencies, integration: no mutable state. Depends on S3 constants and error table, commons-codec/lang, HDDS replication configs, JAX-RS headers/responses, and Java base64/URL codecs. Integrated by endpoint upload paths, signature filters, XML error responses, and listing/response helpers.

Risks and test signals: `S3StorageType.valueOf` is case-sensitive and accepts only enum names. Multi-chunk detection assumes all streaming algorithms share the `STREAMING` prefix. MD5 comparison assumes lower-case server hex. Tests in this subset cover chunk parsing, digest behavior, encoding object names, and endpoint flows that rely on these utilities; direct `S3Utils` unit coverage is not in the listed files.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/S3Utils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/package-info.java

Purpose: package documentation declaring `org.apache.hadoop.ozone.s3.util` as the S3 utility package.

Important APIs and control flow: no executable code. It provides Javadoc package context for utility classes such as `S3Utils` and `S3StorageType`.

State, dependencies, integration: no runtime state or dependencies other than the Java package declaration. It participates only in generated documentation and package-level source organization.

Risks and test signals: no behavioral risk. Test signal is compilation/package discovery only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/Application.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/Application.java

Purpose: Jersey `ResourceConfig` for the S3 secret web application.

Important APIs and control flow: the constructor calls `packages("org.apache.hadoop.ozone.s3secret")`, enabling Jersey to scan the package for resources and providers, including management endpoints and request filters.

State, dependencies, integration: no mutable state after construction. Integrated from `s3g-web/WEB-INF/web.xml` through the `javax.ws.rs.Application` init-param for the `/secret/*` servlet. Depends on GlassFish Jersey.

Risks and test signals: package scanning means new providers/resources in the package are auto-registered, which is convenient but can expose annotated classes unintentionally. There is no direct unit test in the listed files; deployment descriptor correctness is the main signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/Application.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3AdminEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3AdminEndpoint.java

Purpose: JAX-RS name-binding annotation marking endpoints or methods that require S3 administrator access.

Important APIs and control flow: retained at runtime, targeted at types and methods, and annotated with `@NameBinding`. It binds matching resources to `S3SecretAdminFilter`.

State, dependencies, integration: no state. Depends on Java annotation metadata and JAX-RS `NameBinding`. Used by `S3SecretManagementEndpoint` at class level and by the provider annotation on `S3SecretAdminFilter`.

Risks and test signals: protection is opt-in; a secret endpoint not annotated with this binding would bypass the admin filter. No listed test directly exercises this annotation-filter binding.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3AdminEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretAdminFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretAdminFilter.java

Purpose: JAX-RS request filter enforcing admin-only access for `@S3AdminEndpoint` resources.

Important APIs and control flow: injected `OzoneConfiguration` supplies security/admin settings. `filter` returns immediately if Ozone authorization is disabled. When authorization is enabled and a user principal exists, it creates a remote UGI from the principal name and calls `OzoneAdmins.isS3Admin`; non-admin users are aborted with HTTP 403.

State, dependencies, integration: holds injected config. Integrated by name binding and Jersey provider discovery from `Application`. Depends on `OzoneSecurityUtil`, `OzoneAdmins`, Hadoop UGI, and JAX-RS request/response APIs.

Risks and test signals: if authorization is enabled but `SecurityContext` has no principal, the current implementation does not abort, which may be intentional upstream-auth behavior but is security-sensitive. The filter trusts the container principal. No direct tests in this subset cover missing principal/admin failure for this filter.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretAdminFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretConfigKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretConfigKeys.java

Purpose: constants for S3 secret HTTP endpoint configuration.

Important APIs and control flow: exposes `ozone.s3g.secret.http.enabled` with default `false`, the auth config prefix `ozone.s3g.secret.http.auth.`, auth type key, and default auth type `kerberos`. Private constructor prevents instantiation.

State, dependencies, integration: no runtime state. Used by `S3SecretEnabledEndpointRequestFilter` and likely server configuration code outside this subset.

Risks and test signals: endpoint is disabled by default, which is conservative. A config-key typo changes endpoint exposure behavior. No direct listed test validates these constants.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretEnabled.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretEnabled.java

Purpose: JAX-RS name-binding annotation for resources guarded by the S3 secret endpoint enablement flag.

Important APIs and control flow: runtime-retained, applicable to types and methods, and annotated with `@NameBinding`. It binds resources to `S3SecretEnabledEndpointRequestFilter`.

State, dependencies, integration: no state. `S3SecretManagementEndpoint` uses it at class level, so all generate/revoke operations are gated by config.

Risks and test signals: the Javadoc says "disable S3 Secure Endpoint" while the name and filter semantics mean "require endpoint enabled"; documentation wording can confuse maintainers. No direct listed test covers annotation binding.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretEnabled.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretEnabledEndpointRequestFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretEnabledEndpointRequestFilter.java

Purpose: rejects S3 secret endpoint requests unless `ozone.s3g.secret.http.enabled` is true.

Important APIs and control flow: injected `OzoneConfiguration` is queried with default `false`. If disabled, the request is aborted with HTTP 400 and entity `S3 Secret endpoint is disabled.`; otherwise the request proceeds.

State, dependencies, integration: holds injected config and is registered as a Jersey provider through `@Provider` plus the `@S3SecretEnabled` name binding. Integrated with `S3SecretManagementEndpoint`.

Risks and test signals: returns bad request rather than forbidden/not found, making disabled endpoint behavior visible. If injection fails, the filter will NPE. No direct listed unit test covers this filter.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretEnabledEndpointRequestFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretEndpointBase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretEndpointBase.java

Purpose: base class for S3 secret REST endpoints, providing Ozone client initialization and audit-message construction.

Important APIs and control flow: constructor copies `OzoneConfiguration` and disables `S3Auth.S3_AUTH_CHECK` before client creation. `@PostConstruct initialize` creates an `OzoneClient` via `OzoneClientCache.createClient`. `userNameFromRequest` reads the security principal from the container context. Audit helpers build success/failure messages with operation, params, result, exception, and client IP when context is present. Testing setters allow injection of client and context.

State, dependencies, integration: owns an `OzoneClient`, copied config, JAX-RS `ContainerRequestContext`, and static S3G audit logger. Integrated by `S3SecretManagementEndpoint`. Depends on audit framework, `OzoneClientCache`, S3 auth constants, and `AuditUtils`.

Risks and test signals: the class disables S3 auth checks for this internal client, so HTTP/container authorization and admin filters become the critical boundary. `userNameFromRequest` assumes context, security context, and principal are non-null. There is no direct listed test for lifecycle or audit messages on secret endpoints.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretEndpointBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretManagementEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretManagementEndpoint.java

Purpose: REST resource for generating and revoking S3 secrets.

Important APIs and control flow: class is rooted at `/`, guarded by both `@S3SecretEnabled` and `@S3AdminEndpoint`. `PUT /` generates a secret for the request user; `PUT /{username}` generates for a specified user. `generateInternal` calls object store `getS3Secret`, returns XML-serializable `S3SecretResponse`, and audits success. `OMException.S3_SECRET_ALREADY_EXISTS` maps to 400 with reason text; other OM exceptions log and return 500. `DELETE /` and `DELETE /{username}` revoke for current or supplied user; missing secret maps to 404.

State, dependencies, integration: inherits client/context/audit state from `S3SecretEndpointBase`. Uses `S3SecretValue` from OM, JAX-RS `Response`, `S3GAction` audit constants, and SLF4J logging. Deployed under `/secret/*` by `s3g-web/WEB-INF/web.xml`.

Risks and test signals: path-param username lets admins act on other users, so admin filter correctness is essential. Non-OM `IOException` propagates. `getS3Secret` has create semantics in the client layer, so repeated requests depend on OM duplicate handling. No direct tests in this subset exercise the HTTP secret endpoint.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretManagementEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretResponse.java

Purpose: JAXB response DTO for generated S3 credentials.

Important APIs and control flow: annotated as XML root `S3Secret` with field access. Contains `awsAccessKey` and `awsSecret` elements with standard getters and setters.

State, dependencies, integration: mutable data holder populated by `S3SecretManagementEndpoint.generateInternal` from `S3SecretValue` and serialized by JAX-RS/JAXB. No persistence.

Risks and test signals: it serializes secret material directly, so endpoint filtering and transport security are critical. No direct listed serialization test for this DTO.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/package-info.java

Purpose: package documentation for the S3 secret gateway package.

Important APIs and control flow: no executable code. The Javadoc states the package contains top-level generic classes for the S3 secret gateway.

State, dependencies, integration: no runtime state or dependencies other than declaring `org.apache.hadoop.ozone.s3secret`.

Risks and test signals: no behavioral risk. Compile/package organization is the only signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/META-INF/beans.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/META-INF/beans.xml

Purpose: CDI/Weld bean archive marker for the module-level resources.

Important APIs and control flow: empty `<beans>` document using Java EE beans 1.0 schema. Its presence enables CDI scanning/injection for application classes packaged with this resource.

State, dependencies, integration: no mutable state. Works with Weld listener declared in web descriptors and `@Inject` fields/constructors in S3 gateway resources and filters.

Risks and test signals: empty descriptor relies on container defaults. If omitted or schema handling changes, injection of `OzoneConfiguration` and other beans may fail. No direct listed test exercises deployment-time CDI boot.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/META-INF/beans.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/webapps/s3g-web/WEB-INF/web.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/webapps/s3g-web/WEB-INF/web.xml

Purpose: deployment descriptor for the S3 secret web application.

Important APIs and control flow: declares Jersey `ServletContainer` named `secret`, configured with `org.apache.hadoop.ozone.s3secret.Application`, loaded on startup, and mapped to `/secret/*`. Registers Weld servlet listener for CDI.

State, dependencies, integration: no application state. Integrates servlet container, Jersey application scanning, and CDI injection for the `org.apache.hadoop.ozone.s3secret` package.

Risks and test signals: any mismatch in application class name or servlet mapping would make secret endpoints unavailable. The descriptor exposes only `/secret/*`, relying on filters and config for security. No direct web-container test is present in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/webapps/s3g-web/WEB-INF/web.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/webapps/s3gateway/WEB-INF/beans.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/webapps/s3gateway/WEB-INF/beans.xml

Purpose: CDI/Weld bean archive marker for the main S3 gateway web application.

Important APIs and control flow: empty beans 1.0 descriptor. It enables CDI discovery/injection in the WAR when paired with the Weld listener.

State, dependencies, integration: no state. Supports injection for Jersey resources/filters configured in the main gateway `web.xml`.

Risks and test signals: deployment depends on the servlet container honoring this legacy schema. Unit tests build endpoints manually through `EndpointBuilder`, so they do not catch CDI descriptor regressions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/webapps/s3gateway/WEB-INF/beans.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/webapps/s3gateway/WEB-INF/web.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/webapps/s3gateway/WEB-INF/web.xml

Purpose: deployment descriptor for the main S3 gateway web application.

Important APIs and control flow: maps Jersey `ServletContainer` named `jaxrs` to `/*`, configured with `org.apache.hadoop.ozone.s3.GatewayApplication`, and loads it on startup. Registers `EmptyContentTypeFilter` for all requests and the Weld listener.

State, dependencies, integration: no persistent state. Integrates servlet filtering, Jersey resource routing, and CDI bootstrapping. The `optional-content-type` filter removes empty `Content-Type` header values before JAX-RS processing.

Risks and test signals: because the servlet maps `/*`, filters and resource path handling must be correct for all S3 operations. XML formatting includes a line break inside `filter-class` text, which the container must trim/parse as expected. `TestEmptyContentTypeFilter` covers the filter wrapper behavior but not descriptor loading.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/webapps/s3gateway/WEB-INF/web.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/ClientProtocolStub.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/ClientProtocolStub.java

Purpose: in-memory `ClientProtocol` implementation for S3 gateway unit tests, bridging `OzoneClientStub` and `ObjectStoreStub` to endpoint code that expects a full client protocol.

Important APIs and control flow: delegates active key paths to bucket stubs: create/rewrite key, create-if-absent, conditional rewrite, read/get/head key, delete key, multipart initiate/upload/complete/abort/list parts, directory creation, and object tagging. S3 object helpers use the default S3 volume. `getS3Secret` returns fixed stub credentials. Large portions of the interface return `null`, `false`, `0`, or no-op for unsupported volume, tenant, token, filesystem, ACL, snapshot, and transport operations.

State, dependencies, integration: stores only an `ObjectStoreStub` reference; actual state lives in volumes/buckets/keys. Integrated by `OzoneClientStub` constructor as the client proxy. Depends on a broad OM/client protocol API surface to satisfy compilation.

Risks and test signals: unsupported methods silently returning defaults can hide missing stub behavior in new tests. `getS3Secret` ignores the requested Kerberos ID and always returns constant credentials. Several methods intentionally do not mutate state, so endpoint tests using new code paths must extend the stub. Existing endpoint tests in this subset exercise key, multipart, tagging, and head/get paths through this class.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/ClientProtocolStub.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/ObjectStoreStub.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/ObjectStoreStub.java

Purpose: in-memory `ObjectStore` implementation for tests.

Important APIs and control flow: maintains a map of volume name to `OzoneVolumeStub`. `createVolume` constructs stub volumes from `VolumeArgs`. `getVolume` throws `VOLUME_NOT_FOUND` when absent. Volume listing filters by prefix and optional previous-volume marker, with one by-user method filtering owner. `getS3Volume` returns the configured default S3 volume. `createS3Bucket` lazily creates the S3 volume before creating a bucket; `deleteS3Bucket` delegates bucket deletion.

State, dependencies, integration: persistent test state is the in-memory `HashMap`. Default S3 volume name comes from `HddsClientUtils.getDefaultS3VolumeName(conf)`. Used by `OzoneClientStub`, `ClientProtocolStub`, and endpoint tests.

Risks and test signals: state is not thread-safe. Listing by user uses `< 0` for `prevVolume`, unlike normal forward pagination; if relied on, this may diverge from production. It does not support multitenant S3 volume behavior. Bucket endpoint tests rely heavily on create/get/delete S3 bucket behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/ObjectStoreStub.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneBucketStub.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneBucketStub.java

Purpose: in-memory `OzoneBucket` for endpoint tests, modeling keys, key bytes, multipart uploads, ACLs, replication config, directories, and object tags.

Important APIs and control flow: key creation returns output streams whose `close` commits bytes and `OzoneKeyDetails` into maps. Conditional create/rewrite methods throw OM exceptions for existing/missing/ETag mismatch. Stream key creation writes through a byte buffer. Reads/list/head use sorted key maps and support shallow listing by delimiter-like path truncation. Multipart initiation stores upload metadata; part upload records numbered parts and ETags; completion checks part order and ETags, concatenates bytes, writes final key details, and returns completion info. Abort removes upload state. Tagging methods mutate tags stored on key details. Directory creation inserts non-file zero-length key details.

State, dependencies, integration: in-memory maps hold `keyDetails`, `keyContents`, `keyToMultipartUpload`, and `partList`; ACLs are an array list; replication config is mutable. Integrated by `OzoneVolumeStub`, `ClientProtocolStub`, and endpoint tests for object/bucket listing, ACL, multipart, and tagging scenarios.

Risks and test signals: no synchronization and many production features are simplified. `deleteKey` removes metadata but leaves `keyContents`, so stale bytes may remain if read by direct map path. Shallow listing uses simple string splitting and may diverge from OM listing edge cases. Multipart completion does not clear upload/part state after success. Endpoint tests in this subset validate listing, owners, multipart abort, ACL handling, and bucket-not-empty behavior through this stub.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneBucketStub.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneClientStub.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneClientStub.java

Purpose: test `OzoneClient` backed by in-memory object store and protocol stubs.

Important APIs and control flow: default constructor creates an `ObjectStoreStub`; main constructor passes object store and `ClientProtocolStub` to the superclass and initializes S3 gateway metrics. `close` is a no-op.

State, dependencies, integration: state is owned by the supplied `ObjectStoreStub`. Used throughout endpoint tests via `EndpointBuilder`.

Risks and test signals: metrics creation is global/static and can leak between tests if not handled by the metrics implementation. No-op close means resource lifecycle is not tested. Nearly every endpoint test in this subset uses this client.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneClientStub.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneDataStreamOutputStub.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneDataStreamOutputStub.java

Purpose: test `OzoneDataStreamOutput` wrapper that delegates to an in-memory `ByteBufferStreamOutput`.

Important APIs and control flow: `write(ByteBuffer, off, len)`, `flush`, and `close` forward to the underlying stream; close is idempotent. `getCommitUploadPartInfo` returns `null` until closed, then returns part name and ETag metadata. `getKeyDataStreamOutput` exposes the underlying stream when it implements `KeyDataStreamOutput`.

State, dependencies, integration: tracks `partName` and `closed` flag. Used by `OzoneBucketStub` for streaming key and streaming multipart paths.

Risks and test signals: assumes metadata is available through the superclass/underlying output. Behavior is simpler than real data stream commit semantics, so tests using it validate endpoint logic, not datanode streaming. Multipart tests indirectly exercise commit-part info.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneDataStreamOutputStub.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneOutputStreamStub.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneOutputStreamStub.java

Purpose: test `OzoneOutputStream` wrapper for in-memory output streams, especially multipart part commits.

Important APIs and control flow: delegates `write`, `flush`, and idempotent `close` to the wrapped output stream. After close, `getCommitUploadPartInfo` returns part name plus ETag from `KeyMetadataAware` metadata; before close it returns `null`.

State, dependencies, integration: tracks part name and close state. Used by `OzoneBucketStub.createMultipartKey` and normal key paths that need a concrete `OzoneOutputStream`.

Risks and test signals: casts the wrapped stream to `KeyMetadataAware`, so callers must supply compatible streams. It does not model asynchronous commit or failure after close. Multipart endpoint utilities use returned ETags for completion requests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneOutputStreamStub.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneVolumeStub.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneVolumeStub.java

Purpose: in-memory `OzoneVolume` for tests, owning buckets and volume ACLs.

Important APIs and control flow: builder preserves fluent `OzoneVolume.Builder` methods. `createBucket` throws `BUCKET_ALREADY_EXISTS` on duplicate and creates `OzoneBucketStub` with default RATIS/THREE replication, bucket layout, storage type, versioning, and creation time. `getBucket` throws `BUCKET_NOT_FOUND` when absent. Bucket listing filters by prefix/previous marker and sorts by bucket name. `deleteBucket` removes only empty bucket stubs, otherwise throws `BUCKET_NOT_EMPTY`. ACL methods clone or mutate an in-memory list.

State, dependencies, integration: holds maps of bucket name to bucket and an ACL list. Used by `ObjectStoreStub` and bucket/ACL/list/delete tests.

Risks and test signals: state is not thread-safe. ACL cloning is shallow. Default replication and bucket args are simplified but enough for S3 endpoint behavior. `TestBucketDelete`, `TestBucketAcl`, and `TestBucketList` depend on this implementation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneVolumeStub.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/package-info.java

Purpose: test package documentation for in-memory Ozone client stubs.

Important APIs and control flow: no executable code. Declares the `org.apache.hadoop.ozone.client` test package.

State, dependencies, integration: no runtime state. Provides source organization for stub classes used by S3 gateway tests.

Risks and test signals: no behavioral risk beyond package compilation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/protocolPB/TestGrpcOmTransport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/protocolPB/TestGrpcOmTransport.java

Purpose: unit tests for OM transport factory selection and gRPC transport lifecycle.

Important APIs and control flow: `setUp` configures Hadoop RPC protocol engine for `OzoneManagerProtocolPB`. `testGrpcOmTransportFactory` sets `OZONE_OM_TRANSPORT_CLASS` to `GrpcOmTransportFactory`, creates transport via `OmTransportFactory.create`, closes it, and asserts class simple name is `GrpcOmTransport`. `testHrpcOmTransportFactory` sets the Hadoop RPC factory and asserts the result is not gRPC. `testStartStop` instantiates `GrpcOmTransport`, starts it, and shuts it down in `finally`.

State, dependencies, integration: uses static `OzoneConfiguration` mutated across tests. Integrates OM protocol transport factories, Hadoop RPC engine, and current UGI.

Risks and test signals: shared mutable config means test order could matter if future tests add properties. It verifies factory wiring and start/stop smoke behavior, not real OM request traffic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/protocolPB/TestGrpcOmTransport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestAuthorizationFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestAuthorizationFilter.java

Purpose: tests AWS authorization filter parsing and string-to-sign generation.

Important APIs and control flow: parameterized failure cases build mocked `ContainerRequestContext` with malformed/stale/empty/unsupported auth headers and verify HTTP 400 or 403 plus expected error messages. Success cases cover path-style and virtual-host style request URIs, configuring `AWSSignatureProcessor` and `SignatureInfo`, invoking `AuthorizationFilter.filter`, then computing the expected canonical request and AWS4 string-to-sign for assertion. `setupContext` mocks headers, query params, path params, method, and URI.

State, dependencies, integration: uses current date/time in AWS date format, mocked JAX-RS context, signature parser/processor classes, and S3 constants. No persistent state.

Risks and test signals: tests use dynamic current date/time, so expected strings track the test run date. They do not verify cryptographic signature validation, only parsing/canonicalization state. They explicitly reject AWS V2 signatures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestAuthorizationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestEmptyContentTypeFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestEmptyContentTypeFilter.java

Purpose: tests `EmptyContentTypeFilter.EnumerationWrapper`, the helper used by the servlet filter that removes empty `Content-Type` header entries.

Important APIs and control flow: first test feeds an enumeration containing `Content-Type`, `1`, `2`, `Content-Type` and asserts only `1` and `2` are returned. Second test feeds only `Content-Type` and asserts the wrapper is empty.

State, dependencies, integration: uses `Vector` enumerations and the nested wrapper class. Integration point is the `optional-content-type` filter configured in main `web.xml`.

Risks and test signals: covers enumeration behavior only, not full servlet request wrapping. It assumes exact string matching for `Content-Type`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestEmptyContentTypeFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestMultiDigestInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestMultiDigestInputStream.java

Purpose: tests `MultiDigestInputStream`, which reads data while updating one or more `MessageDigest` instances.

Important APIs and control flow: parameterized `testRead` validates empty and non-empty streams with MD5, SHA-1, and SHA-256. `testOnOffFunctionality` disables digest updates and expects the empty digest. `testOnOffWithPartialRead` verifies only bytes read while enabled affect the digest. `testResetDigests` clears digest state after partial reads. `testDigestManagement` validates `getAllDigests`, adding, replacing, removing, missing lookup, and post-read digest correctness.

State, dependencies, integration: state is held by the stream under test in digest maps and enabled flag. Uses `ByteArrayInputStream`, Apache IOUtils, and Java security digests. Relevant to upload checksum/Content-MD5 handling.

Risks and test signals: tests digest state after calling `digest()`, which finalizes each `MessageDigest`; repeated checks need fresh digest state. The suite covers normal read and byte-array read paths but not mark/reset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestMultiDigestInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestOzoneClientCache.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestOzoneClientCache.java

Purpose: tests failure behavior of `OzoneClientCache.initialize`.

Important APIs and control flow: one test enables security and clears OM address, expecting `IOException`. Another configures multiple OM service IDs without an internal service ID and asserts the error mentions multiple service IDs. The third sets internal service ID with multiple service IDs and asserts initialization still fails for incomplete config but not for the multiple-service-ID validation.

State, dependencies, integration: each test creates a new `OzoneConfiguration` and `OzoneClientCache`. Integration point is endpoint/client initialization code that builds Ozone clients from config.

Risks and test signals: failure-only tests do not verify successful client caching or close behavior. They protect user-facing diagnostics for ambiguous HA service ID config.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestOzoneClientCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestS3GatewayAuditLog.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestS3GatewayAuditLog.java

Purpose: tests S3 gateway audit log output for selected endpoint operations.

Important APIs and control flow: setup creates an `OzoneClientStub`, S3 bucket, shared `RequestIdentifier`, and endpoint instances via `EndpointBuilder`, overriding `getAuditParameters` for bucket/object endpoints. Tests call head bucket, root list buckets, and head object, then verify the first line in `audit.log` exactly matches expected user/ip/op/params/request-id/result formatting. `verifyLog` retries briefly for async logging and truncates the log after each assertion. `tearDown` deletes `audit.log`.

State, dependencies, integration: mutates process system property `log4j.configurationFile`, local `audit.log`, in-memory bucket content, and request identifiers. Integrates endpoint audit code and log4j config.

Risks and test signals: exact string assertions are brittle to log formatting/order changes. It checks success paths only and uses `user=null`, `ip=null` because mocked context lacks identity/IP.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestS3GatewayAuditLog.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestSignedChunksInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestSignedChunksInputStream.java

Purpose: tests decoding of AWS signed chunked upload bodies by `SignedChunksInputStream`.

Important APIs and control flow: covers empty body, empty body with trailer, empty body without final CRLF, single chunk, single chunk with trailer, single chunk without final terminator, multiple chunks, and multiple chunks with trailer. Each scenario wraps encoded bytes and asserts decoded content through full `IOUtils.toString`, full byte-array reads, and partial reads.

State, dependencies, integration: no persistent state; uses `ByteArrayInputStream` and UTF-8 assertions. Integrated with S3 streaming upload handling and `x-amz-content-sha256` streaming signatures.

Risks and test signals: tests verify chunk framing removal but not cryptographic signature validation. It includes trailer formats and missing-end tolerance, which are important compatibility signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestSignedChunksInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestUnsignedChunkInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestUnsignedChunkInputStream.java

Purpose: tests decoding of unsigned AWS chunked upload bodies by `UnsignedChunkInputStream`.

Important APIs and control flow: mirrors signed chunk tests for empty, trailer, missing terminator, single chunk, and multiple chunk cases. Assertions use full string read, full buffer read, and partial buffer read to ensure read APIs all return only decoded payload bytes.

State, dependencies, integration: no persistent state; uses byte-array input and UTF-8. Relevant to `STREAMING-UNSIGNED-PAYLOAD-TRAILER` and unsigned streaming upload paths.

Risks and test signals: covers framing and trailer tolerance, not checksum validation. Compatibility behavior around incomplete final CRLF is explicitly accepted by the tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestUnsignedChunkInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestVirtualHostStyleFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestVirtualHostStyleFilter.java

Purpose: tests conversion of virtual-host-style S3 requests to path-style URIs.

Important APIs and control flow: setup configures HTTP address `localhost:9878` and S3 domain `localhost`. `createContainerRequest` builds Jersey `ContainerRequest` objects with base URI, request URI, method, host header, and mocked security/properties. Tests verify `mybucket.localhost:9878` plus optional path/query becomes `/mybucket[/key]?query`, while path-style host remains unchanged. Parameterized invalid host tests assert `InvalidRequestException` for domain mismatch or invalid host format.

State, dependencies, integration: uses `OzoneConfiguration`, Jersey container request classes, and mocked security context. Integrated with the gateway request filter chain before endpoint matching.

Risks and test signals: configured domain parsing strips port from the HTTP address. Tests validate URI rewriting and query preservation but not HTTPS, IPv6, or multi-label domain edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestVirtualHostStyleFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/commontypes/TestObjectKeyNameAdapter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/commontypes/TestObjectKeyNameAdapter.java

Purpose: tests `ObjectKeyNameAdapter` URL-encoding behavior for list response key/prefix names.

Important APIs and control flow: with `encodingType=url`, plain names stay readable, spaces become `+`, plus signs become `%2B`, and empty/null names return empty strings. Without encoding type, values are returned unchanged except null becomes empty.

State, dependencies, integration: no persistent state. Integrated with `ListObjectResponse` and bucket listing output when query parameter `encoding-type=url` is used.

Risks and test signals: URL encoding uses Java form-style encoding where spaces become `+`, matching the expected S3 response behavior in these tests. The tests focus on small representative strings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/commontypes/TestObjectKeyNameAdapter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/EndpointBuilder.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/EndpointBuilder.java

Purpose: reusable builder for constructing S3 endpoint instances in unit tests without a full Jersey/CDI container.

Important APIs and control flow: stores optional base endpoint, client, config, headers, request context, request ID, and signature info. Constructor prepares default `OzoneConfiguration`, `RequestIdentifier`, mocked `SignatureInfo` with signed payload, and mocked request/URI query/path maps. `build` creates or reuses the endpoint, injects client/config/context/headers/request ID/signature info, calls `initialization`, and returns the ready endpoint. Static factories create builders for root, bucket, bucket ACL handler, and object endpoints.

State, dependencies, integration: per-builder mutable test setup state. Integrates endpoint tests with `OzoneClientStub`, mocked JAX-RS APIs, and endpoint lifecycle methods.

Risks and test signals: because it bypasses Jersey/CDI, tests using it do not validate production injection, filters, or servlet mappings. Defaults such as signed payload may hide unsigned-request paths unless tests override them.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/EndpointBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/EndpointTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/EndpointTestUtils.java

Purpose: helper methods for endpoint unit tests, especially object GET/PUT/DELETE, tagging, multipart upload, and error/status assertions.

Important APIs and control flow: methods set query params and mocked HTTP methods/headers before invoking `ObjectEndpoint` methods. Multipart helpers initiate upload, upload parts, build completion requests, and assert response entities/ETags. `assertStatus`, `assertSucceeds`, and `assertErrorResponse` centralize response/error assertions. `FailingInputStream` simulates upload interruption after a configured byte count.

State, dependencies, integration: no global state; it mutates endpoint query params and Mockito stubs supplied by callers. Integrated by multipart/object endpoint tests. Depends on S3 constants, JAX-RS responses, Apache HTTP status, and Ratis checked functional interfaces.

Risks and test signals: helpers can leave query parameters set on reused endpoint instances, so tests must manage endpoint state. Error assertion overload closing a response assumes lazy exception behavior from some endpoint methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/EndpointTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestAbortMultipartUpload.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestAbortMultipartUpload.java

Purpose: tests aborting multipart uploads through `ObjectEndpoint`.

Important APIs and control flow: creates stub client and S3 bucket, sets `x-amz-storage-class` to `STANDARD`, builds object endpoint, initiates multipart upload, aborts it and expects HTTP 204, then aborts with a random upload ID and expects S3 `NO_SUCH_UPLOAD`.

State, dependencies, integration: uses in-memory multipart state in `OzoneBucketStub` through `EndpointTestUtils`. Integration covers object endpoint query-param dispatch to multipart abort.

Risks and test signals: only aborts before any parts are uploaded and does not verify cleanup of part maps. It protects the HTTP status and missing-upload error mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestAbortMultipartUpload.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketAcl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketAcl.java

Purpose: tests bucket ACL GET and PUT behavior through `BucketEndpoint`.

Important APIs and control flow: setup creates an S3 bucket, mocked servlet/header state, and endpoint with `?acl`. Tests cover reading ACLs, setting grant headers for READ/WRITE/READ_ACP/WRITE_ACP/FULL_CONTROL, multiple grants, replacing old ACLs, body XML parsing for user grants, rejecting group grants, bucket-not-found mapping, invalid XML wrapping as invalid request, invalid/whitespace grant headers as invalid argument, empty grant header as no-op success, and header precedence over XML body when both are present.

State, dependencies, integration: mutates in-memory bucket/volume ACL lists in stubs. Reads XML resources from test classpath. Integrates `BucketEndpoint`, `BucketAclHandler`/ACL conversion classes, JAX-RS responses, and `OzoneAcl`.

Risks and test signals: assertions around volume ACLs in `testPutClearOldAcls` show nuanced mapping from S3 grants to Ozone ACLs and may be easy to regress. Header-over-body precedence is explicitly protected. Tests use mocked `parameterMap`, while the built endpoint also has query-params-for-test set, so there are two query mechanisms in play.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketAcl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketAclHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketAclHandler.java

Purpose: focused tests for `BucketAclHandler` dispatch and ACL handling.

Important APIs and control flow: setup builds the handler with stub client/headers and default `?acl`. PUT tests verify handler returns null without `?acl`, succeeds for all supported grant headers and multiple headers, rejects unsupported grantee URI/email types, throws for nonexistent buckets, accepts valid XML body, rejects invalid header format, supports multiple grantees in one header, and replaces existing ACLs. GET tests verify null without `?acl`, success with `?acl`, bucket-not-found exception, and returned ACL structure after setting a grant. `mockContext` supplies an `S3RequestContext` backed by a mocked bucket endpoint/volume.

State, dependencies, integration: uses in-memory bucket state and mocked context wrappers. Integrates handler-level logic independently from `BucketEndpoint`.

Risks and test signals: some bucket-not-found tests expect raw `OMException`, while endpoint-level tests expect S3-mapped exceptions; this distinction matters for layering. Tests validate dispatch contract where returning `null` means another handler should process the request.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketAclHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketDelete.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketDelete.java

Purpose: tests bucket delete behavior through `BucketEndpoint`.

Important APIs and control flow: setup creates stub client/object store and S3 bucket. `testBucketEndpoint` deletes the bucket and expects HTTP 204. `testDeleteWithNoSuchBucket` asserts S3 `NO_SUCH_BUCKET` code/message for missing bucket. `testDeleteWithBucketNotEmpty` creates a directory marker and asserts S3 `BUCKET_NOT_EMPTY`.

State, dependencies, integration: depends on `OzoneVolumeStub.deleteBucket` emptiness checks and `BucketEndpoint` OM-to-S3 error mapping.

Risks and test signals: tests use manual try/catch/fail rather than `assertThrows`, but they clearly protect error codes/messages. Bucket emptiness depends on stub `OzoneBucketStub.isEmpty`, which checks key metadata only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketGetLocation.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketGetLocation.java

Purpose: tests `GET /{bucket}?location` behavior.

Important APIs and control flow: setup creates a stub bucket and sets query parameter `location`. The test asserts `bucketEndpoint.get(BUCKET_NAME)` returns S3 `NOT_IMPLEMENTED`.

State, dependencies, integration: minimal in-memory client state. Integrates bucket endpoint query dispatch for unsupported GetBucketLocation.

Risks and test signals: documents that bucket location is intentionally not implemented, so future support should update this test. Bucket name contains a space, which also lightly exercises name propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketGetLocation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketHead.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketHead.java

Purpose: tests HEAD bucket behavior through `BucketEndpoint`.

Important APIs and control flow: setup creates an S3 bucket and endpoint. Success test calls `head(bucketName)` and expects HTTP 200. Missing-bucket test catches `OS3Exception` and asserts S3 `NO_SUCH_BUCKET` code and message.

State, dependencies, integration: relies on `ObjectStoreStub`/`OzoneVolumeStub` bucket lookup and endpoint error mapping.

Risks and test signals: covers only existence status, not headers. Manual try/catch style means reaching the end without exception fails explicitly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketHead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketList.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketList.java

Purpose: broad tests for S3 ListObjects behavior in `BucketEndpoint`.

Important APIs and control flow: helper creates stub bucket `b1` with requested keys. Tests cover root listing with delimiter, directory/prefix listing, avoiding prefix false positives, owner propagation from current UGI, empty results, prefix+delimiter common prefixes, empty-string delimiter as no delimiter, continuation-token pagination over contents and common prefixes, invalid continuation token mapping to invalid argument, `start-after`, `encoding-type=url`, unsupported encoding type, non-integer/negative/zero `max-keys`, zero max-keys in non-empty bucket, and configured `OZONE_S3G_LIST_MAX_KEYS_LIMIT` capping results.

State, dependencies, integration: mutates in-memory key maps and current login user in one owner test. Integrates endpoint query parsing, `OzoneBucketStub.listKeys`, list response DTOs, object key encoding, continuation token handling, and configuration.

Risks and test signals: changing list ordering, common-prefix accounting, continuation-token encoding, or max-key validation will break these tests. Shared UGI mutation can leak if not reset by the broader test harness. Stub shallow-list behavior is simpler than production OM but still exercises endpoint response logic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketPut.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketPut.java

Purpose: tests S3 bucket creation through `BucketEndpoint.put`.

Important APIs and control flow: setup builds endpoint on a stub client. Test creates a bucket, expects HTTP 200 and non-null `Location`, then tries to create the same bucket again and expects S3 `BUCKET_ALREADY_EXISTS`.

State, dependencies, integration: uses `ObjectStoreStub.createS3Bucket` and `OzoneVolumeStub.createBucket` duplicate detection. Endpoint maps duplicate OM exception to S3 error.

Risks and test signals: covers duplicate behavior but not invalid bucket names, ACLs on create, or location constraints. Protects response location presence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketPut.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketResponse.java

Purpose: tests JAXB serialization of bucket listing response types.

Important APIs and control flow: builds a `ListBucketResponse`, adds one bucket entry, marshals it with JAXB, and prints the serialized output.

State, dependencies, integration: no persistent state. Integrates response DTO annotations with JAXB.

Risks and test signals: the test appears to be a smoke test without strong XML assertions, so it may not catch structural regressions beyond marshalling failures. It is still useful for JAXB annotation validity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketResponse.java -->
