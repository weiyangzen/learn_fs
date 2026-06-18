# subset-b-008141 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/DirectTokenAuth.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/DirectTokenAuth.java

Purpose: `DirectTokenAuth` is the simplest Vault authentication strategy for the remote S3 secret store. It implements the `Auth` contract by taking a `Supplier<String>` token provider and applying that token directly to a BetterCloud `VaultConfig`.

Important APIs and flow: construction stores the token supplier; `auth(VaultConfig)` calls `config.token(tokenProvider.get()).build()` and returns a new `Vault`. There is no retry, caching, token renewal, or validation in this class; errors are surfaced as `VaultException` from the Vault client builder.

State, dependencies, risks, and tests: state is limited to the injected supplier, so persistence lives entirely in Vault and Ozone configuration. The class depends on `com.bettercloud.vault` and integrates with `VaultS3SecretStore` auth injection. The main risks are null/empty tokens and leaking long-lived static tokens through configuration. Test signal is indirect through Vault secret-store tests that install custom `Auth` implementations; a targeted test would assert supplier invocation and token propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/DirectTokenAuth.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/package-info.java

Purpose: this package descriptor documents the Vault authentication subpackage used by the remote S3 secret store. It separates Vault login/token strategies from the storage implementation.

Important APIs and flow: there is no executable code, but the package contains implementations of the `Auth` contract such as direct-token authentication. Runtime flow enters this package when `VaultS3SecretStore` needs an authenticated BetterCloud `Vault` client.

State, dependencies, risks, and tests: no state or persistence exists in the descriptor itself. Its integration point is documentation and package organization for secret-store authentication. Risk is documentation drift if new auth modes are added without updating the package summary. Tests are provided through concrete auth/store tests, not this package-info file directly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/package-info.java

Purpose: this package descriptor identifies the HashiCorp Vault-backed implementation of Ozone's remote S3 secret store. It frames the package as the Vault integration layer for storing generated S3 access secrets outside OM metadata.

Important APIs and flow: no methods are defined here. Runtime flow is through classes in the package, especially `VaultS3SecretStore`, which maps Ozone S3 secret operations to Vault logical read/write/delete calls.

State, dependencies, risks, and tests: the descriptor has no state. Package-level dependencies are BetterCloud Vault client APIs and Ozone S3 secret abstractions. The main risk is stale documentation if the implementation grows beyond Vault. Test coverage comes from `TestVaultS3SecretStore`, which exercises the package behavior against mocked Vault logical operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/test/java/org/apache/hadoop/ozone/s3/remote/vault/TestVaultS3SecretStore.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/test/java/org/apache/hadoop/ozone/s3/remote/vault/TestVaultS3SecretStore.java

Purpose: `TestVaultS3SecretStore` verifies the Vault-backed S3 secret store's basic read/write/delete behavior and its re-authentication behavior after Vault returns unauthorized responses.

Important APIs and flow: setup creates a mocked `Vault`, a custom `Auth` lambda, and a `VaultS3SecretStore` with engine, namespace, secret path, and retry count. `LogicalMock` overrides `read`, `write`, and `delete`, using atomic counters to return either success or HTTP 401-like `LogicalResponseMock` instances. `testReadWrite` stores `S3SecretValue.of("id", "value")` and reads it back. `testReAuth` forces an auth operation before successful store/get/revoke. `testAuthFail` verifies that read and revoke throw `IOException` after authorization is exhausted.

State, dependencies, risks, and tests: test persistence is an in-memory `STORE` map keyed by Vault path; auth and success limits are mutable atomic counters reset before each test. Dependencies include BetterCloud Vault logical APIs, Mockito, JUnit 5, and Ozone `S3SecretValue`. Risks include mocked response behavior being narrower than real Vault namespaces, KV versions, and response payloads. Passing tests signal that the store maps secrets to Vault data, retries auth on 401, and surfaces repeated auth failure as `IOException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/test/java/org/apache/hadoop/ozone/s3/remote/vault/TestVaultS3SecretStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/dev-support/findbugsExcludeFile.xml

Purpose: this SpotBugs/FindBugs filter file is the module-local exclusion list for the S3 Gateway Maven build.

Important APIs and flow: the XML contains an empty `<FindBugsFilter>` root. Maven's `spotbugs-maven-plugin` references this file from `s3gateway/pom.xml`, so static analysis runs with no module-specific suppressions.

State, dependencies, risks, and tests: there is no runtime state or persistence. The dependency is the SpotBugs plugin's filter schema. The key risk is that future suppressions could hide real S3G defects, but the current empty file is a positive signal. Build/test signal is SpotBugs configuration loading successfully and not excluding any findings for this module.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/pom.xml

Purpose: this Maven POM builds the `ozone-s3gateway` jar, defining the server, REST/JAX-RS, XML binding, Ozone client, security, tracing, and runtime container dependencies required for the S3-compatible gateway.

Important APIs and flow: it inherits from the root `org.apache.ozone:ozone` parent at version `2.3.0-SNAPSHOT`, disables annotation processing for compilation, and declares runtime Jersey, HK2, Weld, JAXB, Jetty, Netty, and reload4j dependencies. It also depends on Ozone client/common/interface modules, HDDS framework modules, Hadoop auth/common, Jackson XML/JAXB support, servlet/CDI/inject APIs, OpenTelemetry API, Ratis, picocli, commons libraries, and an `ozone-client` test jar.

State, dependencies, risks, and tests: the build persists compiled classes and unpacks static web assets/docs during `prepare-package` from `hdds-server-framework` and `hdds-docs`. SpotBugs uses `dev-support/findbugsExcludeFile.xml`. Risks include mixed `jakarta.*` and `javax.*` API dependencies, runtime-only CDI/Jersey binding mismatches, and security-sensitive dependency drift. Test signals are Maven compile/test, classpath generation, SpotBugs loading, and packaging verifying the static web assets and servlet runtime are assembled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/audit/S3GAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/audit/S3GAction.java

Purpose: `S3GAction` enumerates audit action names for the S3 Gateway and implements the shared `AuditAction` interface.

Important APIs and flow: enum constants cover bucket APIs, root listing, object operations, multipart upload operations, secret generation/revocation, tagging, and object ACL. `getAction()` returns the enum name string used by `AuditMessage` and `AuditLogger`.

State, dependencies, risks, and tests: there is no mutable state or persistence. The enum integrates with `EndpointBase`, `S3RequestContext`, auditing handlers, and S3G audit log consumers. Risks are missing constants for newly added REST APIs or renaming values in ways that break log queries. Tests are indirect through endpoint tests and audit assertions that expect action names to be stable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/audit/S3GAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/audit/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/audit/package-info.java

Purpose: this package descriptor documents the S3 Gateway audit package and identifies `S3GAction` as the gateway's `AuditAction` implementation.

Important APIs and flow: there is no executable code. The documented package is consumed by endpoint and handler classes that write S3G audit records.

State, dependencies, risks, and tests: no state is held. The dependency is documentation alignment with the audit framework. Risk is stale package documentation if more audit types are introduced. Test signal is indirect through S3G audit logging paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/audit/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/AuthorizationFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/AuthorizationFilter.java

Purpose: `AuthorizationFilter` is the pre-matching JAX-RS request filter that parses the incoming AWS authorization material and builds the SigV4 string-to-sign before later filters mutate the request.

Important APIs and flow: the filter injects `SignatureProcessor` and request-scoped `SignatureInfo`. `filter` calls `parseSignature`, initializes `SignatureInfo`, accepts only `SignatureInfo.Version.V4`, computes the signature base through `StringToSignProducer.createSignatureBase`, and rejects missing AWS access IDs. `OS3Exception` is wrapped as a JAX-RS exception; unexpected failures become S3 internal errors.

State, dependencies, risks, and tests: state is request-scoped `SignatureInfo`; persistence is none. It integrates with signature parsers, endpoint initialization, `S3Auth`, and OM thread-local auth. Risks include unsupported SigV2/query forms being rejected here, signature canonicalization depending on unmodified request state, and generic exceptions masking malformed input as internal errors. Tests should exercise valid V4, missing access ID, unsupported version, and parser failure; endpoint integration tests indirectly require this filter to populate auth.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/AuthorizationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/ClientIpFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/ClientIpFilter.java

Purpose: `ClientIpFilter` records the client IP address into request headers for later audit and request-context use.

Important APIs and flow: it is a pre-matching request filter with priority after header preprocessing. It reads `x-real-ip`; if absent, it uses the first `x-forwarded-for` address; if still absent, it uses `HttpServletRequest.getRemoteAddr()`. The selected value is written as `client_ip`.

State, dependencies, risks, and tests: no persistent state is held; the only state mutation is adding a request header. It depends on servlet request injection and Jersey request filtering. Risks include trusting unvalidated forwarded headers and not trimming whitespace from multi-hop `x-forwarded-for`. Tests should cover header precedence, forwarded header parsing, and remote-address fallback; audit tests indirectly depend on this header.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/ClientIpFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/CommonHeadersContainerResponseFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/CommonHeadersContainerResponseFilter.java

Purpose: this response filter adds S3-compatible common response headers to every gateway response.

Important APIs and flow: it injects request-scoped `RequestIdentifier` and appends `Server: Ozone`, `x-amz-id-2`, and `x-amz-request-id` to `ContainerResponseContext` headers. It does not inspect status or entity type, so success and error responses receive the same common identifiers.

State, dependencies, risks, and tests: state comes from `RequestIdentifier`, which is generated per request; there is no persistence. The filter integrates with all Jersey resources and exception mappers. Risks are duplicate headers if another layer adds the same names and missing identifiers if CDI injection fails. Test signals include response-header assertions in S3 endpoint and error-mapper tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/CommonHeadersContainerResponseFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/EmptyContentTypeFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/EmptyContentTypeFilter.java

Purpose: `EmptyContentTypeFilter` normalizes requests whose `Content-Type` is the empty string, a compatibility path for clients such as older Ruby SDK behavior.

Important APIs and flow: as a servlet `Filter`, `doFilter` checks `HttpServletRequest.getContentType()`. If it equals `""`, the request is wrapped so `getContentType`, `getHeader("Content-Type")`, and `getHeaders("Content-Type")` return null, and `getHeaderNames()` skips `Content-Type` through `EnumerationWrapper`. Otherwise the original request passes through unchanged.

State, dependencies, risks, and tests: no persistent state exists. It integrates before Jersey routing and message body reader selection. Risks include `getHeaders("Content-Type")` returning null instead of an empty enumeration, and `EnumerationWrapper.step()` only skipping one adjacent content-type entry per step. Tests should cover empty content type removal, non-empty pass-through, enumeration behavior, and Jersey method routing for SDK requests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/EmptyContentTypeFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/Gateway.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/Gateway.java

Purpose: `Gateway` is the picocli/HDDS CLI entry point for the Ozone S3-compatible REST service.

Important APIs and flow: `main` disables JVM network address caching if configured and runs the command. `call()` loads the `OzoneConfiguration`, stores it in `OzoneConfigurationHolder`, initializes tracing and UGI, performs Kerberos login when security is enabled, sets HTTP base dir, constructs the S3 API server and web-admin/content server, creates S3G and Netty metrics, starts services, and registers a shutdown hook. `start()` emits startup metadata, initializes metrics, starts the JVM pause monitor and both servers. `stop()` closes servers, stops pause monitoring, and unregisters metrics.

State, dependencies, risks, and tests: runtime state is server handles, metrics handles, and a pause monitor. Persistence is limited to logs/metrics and served static files. It depends on HDDS server framework, security utilities, tracing, Ozone configuration, and shutdown hooks. Risks include unsupported non-Kerberos security methods, partial startup cleanup, static configuration reuse in tests, and content-server failures affecting the S3 API process. Tests generally verify address accessors, startup under mini-cluster configs, and security login behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/Gateway.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/GatewayApplication.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/GatewayApplication.java

Purpose: `GatewayApplication` is the Jersey `ResourceConfig` that exposes the S3 Gateway REST resources and filters.

Important APIs and flow: the constructor calls `packages("org.apache.hadoop.ozone.s3")`, causing Jersey to scan endpoint resources, filters, exception mappers, producers, and providers under the S3 package tree.

State, dependencies, risks, and tests: the class has no mutable state or persistence. It depends on Jersey server package scanning and module classpath completeness. Risks are package scanning being too broad or missing resources moved outside the package. Test signal is application startup and endpoint discovery in Jersey/container tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/GatewayApplication.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/HeaderPreprocessor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/HeaderPreprocessor.java

Purpose: `HeaderPreprocessor` rewrites request `Content-Type` values after signature processing so Jersey routes AWS-compatible requests to the intended resource methods.

Important APIs and flow: it records any original `Content-Type` under `X-Ozone-Original-Content-Type`. For `?delete` and requests with `uploadId`, it forces `application/xml`. For `?uploads` without `uploadId`, it uses the special `ozone/mpu` marker so multipart-upload initiation with an empty body does not get parsed as a complete-upload XML request.

State, dependencies, risks, and tests: state is only modified request headers. The filter runs after `VirtualHostStyleFilter` and after authorization so signed headers remain canonical. Risks include query-parameter precedence when both `uploads` and `uploadId` exist, and signature mismatches if the priority ordering changes. Tests should verify routing for multi-delete, complete MPU, initiate MPU, and preservation of original content type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/HeaderPreprocessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/MultiDigestInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/MultiDigestInputStream.java

Purpose: `MultiDigestInputStream` wraps an input stream and updates multiple `MessageDigest` instances in a single pass, allowing S3 uploads to compute ETag MD5 and optional payload SHA-256 without rereading the body.

Important APIs and flow: constructors register provided digest instances by algorithm. `read()` and `read(byte[], int, int)` delegate to the wrapped stream and update all digests when enabled. `on(boolean)` toggles digest updates, `getMessageDigest`, `getAllDigests`, `resetDigests`, `setMessageDigest`, `addMessageDigest`, and `removeMessageDigest` expose digest management.

State, dependencies, risks, and tests: mutable state is the digest map and the `on` flag; no persistence exists. It integrates with `EndpointBase.getS3ChunkInputStreamInfo` and object upload verification. Risks include digest algorithm name collisions, callers mutating returned digest instances, no synchronization for concurrent reads, and single-byte `read()` casting signed bytes while `MessageDigest.update(byte)` accepts raw byte value. Tests should cover byte and buffer reads, toggling, resets, multiple algorithms, and empty stream behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/MultiDigestInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/OzoneClientCache.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/OzoneClientCache.java

Purpose: `OzoneClientCache` owns the singleton Ozone client used by request-scoped S3 endpoint producers.

Important APIs and flow: `initialize()` sets S3 auth checking and minimum OM version configuration, disables OM group rights for the gateway client, and creates an RPC client. `createClient` chooses HA or non-HA RPC creation based on OM service ID. If gRPC TLS is enabled, `setCertificate` temporarily creates a Hadoop-RPC client with S3 auth disabled to retrieve OM service certificates and installs CA certs into `GrpcOmTransport`. `cleanup()` closes the cached client.

State, dependencies, risks, and tests: state is the cached `OzoneClient` and mutable shared `OzoneConfiguration`. It integrates with `OzoneClientProducer`, OM client protocol, TLS certificate setup, and S3 thread-local auth. Risks include mutating shared config, certificate bootstrap failure, static gRPC CA state, and using a single client across requests while relying on thread-local auth cleanup. Tests should cover initialization config, HA/non-HA selection, TLS cert bootstrap, and cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/OzoneClientCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/OzoneClientProducer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/OzoneClientProducer.java

Purpose: `OzoneClientProducer` provides an `OzoneClient` to CDI/JAX-RS endpoint instances for each request while reusing the singleton cached client.

Important APIs and flow: `createClient()` pulls the shared client from `OzoneClientCache` and exposes it with `@Produces`. On request destruction, `destroy()` clears thread-local S3 auth from the client's proxy.

State, dependencies, risks, and tests: state is the request-scoped `client` reference, not an owned connection. It depends on CDI request scope and `OzoneClientCache`. The main risk is leaking per-request S3 auth if `@PreDestroy` does not run or if `client` is null after producer failure. Test signal is endpoint operations using different credentials without cross-request auth contamination.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/OzoneClientProducer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/OzoneConfigurationHolder.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/OzoneConfigurationHolder.java

Purpose: `OzoneConfigurationHolder` bridges CLI-created `OzoneConfiguration` into CDI injection for Jersey resources and filters.

Important APIs and flow: `configuration()` is a static `@Produces` method returning the stored configuration. `setConfiguration` sets the static value only when it is null, supporting mini-cluster/test setup that preloads configuration. `resetConfiguration` clears it for tests.

State, dependencies, risks, and tests: state is a process-static configuration reference. There is no persistence. It integrates with `Gateway`, tracing, filters, and clients needing injected config. Risks include stale configuration across tests or multiple gateway instances in one JVM, and null configuration if startup order is wrong. Tests should reset between cases and assert one-time set semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/OzoneConfigurationHolder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/RequestIdentifier.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/RequestIdentifier.java

Purpose: `RequestIdentifier` creates AWS-style request identifiers for response headers and audit parameters.

Important APIs and flow: construction generates an 8-to-15 character alphanumeric `amzId` using `SecureRandom` through `RandomStringUtils`, and an Ozone request ID via `OzoneUtils.getRequestID()`. Getters expose both values.

State, dependencies, risks, and tests: state is immutable per request due to `@RequestScoped`; no persistence exists. It integrates with `CommonHeadersContainerResponseFilter` and `EndpointBase.auditMessageFor`. Risks are identifier collision probability, expensive secure randomness under heavy load, and CDI scope mistakes producing reused identifiers. Tests should assert per-instance non-null IDs and response header propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/RequestIdentifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/S3GatewayConfigKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/S3GatewayConfigKeys.java

Purpose: `S3GatewayConfigKeys` centralizes public, unstable configuration keys and defaults for S3 Gateway HTTP servers, auth, domain routing, buffering, FSO directory behavior, listing behavior, and metrics.

Important APIs and flow: constants define S3 API and web-admin HTTP/HTTPS addresses, bind hosts, default ports, auth config prefixes, Kerberos keytab/principal keys, client buffer size default, virtual-host domain name, FSO directory creation flag, shallow list-keys flag, metrics percentile intervals, and max list keys limit. The class is final and non-instantiable.

State, dependencies, risks, and tests: there is no runtime state or persistence. It integrates with `Gateway`, `S3GatewayHttpServer`, `S3GatewayWebAdminServer`, `VirtualHostStyleFilter`, `EndpointBase`, and bucket listing. Risks are changing key strings/default ports incompatibly and adding behavior without config docs. Test signals come from config-based server startup, routing, and list behavior tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/S3GatewayConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/S3GatewayHttpServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/S3GatewayHttpServer.java

Purpose: `S3GatewayHttpServer` adapts the HDDS `BaseHttpServer` to serve the S3-compatible API port.

Important APIs and flow: it disables default web apps, sets a common filter-priority spacing constant, and maps BaseHttpServer key lookups to S3G-specific address, bind host, HTTPS, keytab, SPNEGO principal, enablement, and HTTP auth config keys.

State, dependencies, risks, and tests: server state is owned by `BaseHttpServer`; this subclass only supplies configuration names. It integrates with `Gateway`, servlet/Jersey deployment, and security config. Risks are wrong key mapping causing bind failures or SPNEGO misconfiguration, and disabling default apps requiring the web-admin server to expose static/admin content. Tests are server startup/address assertions under configured and default ports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/S3GatewayHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/S3GatewayWebAdminServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/S3GatewayWebAdminServer.java

Purpose: `S3GatewayWebAdminServer` serves static/admin content and protects the `/secret/*` endpoint when the S3 secret HTTP feature is enabled.

Important APIs and flow: construction calls the base server, adds a favicon redirect servlet, and invokes `addSecretAuthentication`. If secret HTTP is enabled, the method requires Hadoop security and Kerberos auth type, builds Kerberos principal/keytab params, creates an `AuthenticationFilter`, and maps it to `/secret/*`; otherwise it throws an `IllegalStateException`. The server maps web-admin address, auth, bind-host, keytab, and SPNEGO config keys to S3G constants.

State, dependencies, risks, and tests: server state is Jetty/BaseHttpServer state plus optional filter mappings. It depends on Hadoop auth, UGI security state, servlet handlers, and S3 secret config keys. Risks include exposing secrets if auth is disabled incorrectly, hard failure on non-Kerberos secret auth, and principal hostname substitution using the configured bind host. Tests should cover disabled secret endpoint, secured Kerberos filter installation, and favicon redirect.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/S3GatewayWebAdminServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/SignedChunksInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/SignedChunksInputStream.java

Purpose: `SignedChunksInputStream` unwraps AWS SigV4 streaming signed chunked upload bodies so downstream object-write code reads only object payload bytes.

Important APIs and flow: `read()` and `read(byte[], int, int)` maintain `remainingData` for the current chunk and `isFinalChunkEncountered` for EOF. When a new chunk is needed, `readContentLengthFromHeader` reads until CRLF, matches `([0-9A-Fa-f]+);chunk-signature=.*`, parses the hex chunk length, and returns zero for the final chunk. After each data chunk it consumes the trailing CRLF.

State, dependencies, risks, and tests: state is per-stream chunk parser state; there is no persistence. It integrates with `EndpointBase.getS3ChunkInputStreamInfo` for multi-chunk signed payloads. The class explicitly does not verify chunk signatures or trailers, so security depends on higher-level request authentication and optional digest behavior. Risks include malformed chunk handling, integer length limits, ignored trailer checksum/signature, and recursive single-byte read. Tests should cover multiple chunks, final zero chunk, trailers, invalid signature line, buffer boundaries, and premature EOF.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/SignedChunksInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/TracingFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/TracingFilter.java

Purpose: `TracingFilter` creates and closes OpenTelemetry/HDDS tracing spans around JAX-RS resource execution, with special handling for streaming object downloads.

Important APIs and flow: the request filter ends any active span, names a new span from resource class and method, creates it from W3C HTTP headers, and stores the closeable in the request context. The response filter closes the span immediately except for `GET ObjectEndpoint.get`, where it wraps the entity output stream and closes the span only after streaming output is closed.

State, dependencies, risks, and tests: state is the request property holding `TraceCloseable`. It depends on `ResourceInfo`, `TracingUtil`, `OzoneConfigurationHolder`, and `WrappedOutputStream`. Risks include ending an unrelated active span, missing closure on streaming write failures before stream close, and class/method-name based detection breaking after refactors. Tests should cover normal endpoint span closure, streaming GET delayed closure, and null entity stream fallback.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/TracingFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/UnsignedChunksInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/UnsignedChunksInputStream.java

Purpose: `UnsignedChunksInputStream` unwraps AWS streaming unsigned chunked payloads, including trailer-style bodies, and exposes only object payload bytes.

Important APIs and flow: it mirrors `SignedChunksInputStream` without a `chunk-signature` parser. `readContentLengthFromHeader` reads a CRLF-terminated hex length line; zero marks the final chunk and later trailer bytes are ignored. Both single-byte and buffer reads consume trailing CRLF after each payload chunk.

State, dependencies, risks, and tests: state is `remainingData` and final-chunk flag. It integrates with `EndpointBase.getS3ChunkInputStreamInfo` for `STREAMING-UNSIGNED-PAYLOAD-TRAILER`. The explicit risk is that trailer checksum verification is not implemented, so bad trailer checksums are ignored. Additional risks include malformed hex lines, integer overflow, premature EOF, and CRLF assumptions. Tests should cover trailers, multi-buffer chunk boundaries, empty chunks, invalid lengths, and consistency between read overloads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/UnsignedChunksInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/VirtualHostStyleFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/VirtualHostStyleFilter.java

Purpose: `VirtualHostStyleFilter` converts configured S3 virtual-host-style requests into path-style URIs before resource matching.

Important APIs and flow: on each request it reads `ozone.s3g.domain.name`. If no domains are configured, it returns. It strips a port from the `Host` header, picks the longest configured suffix matching the host, and throws `InvalidRequestException` if none matches. If the host has a bucket prefix before the domain, it validates the prefix ends with `.`, removes the dot, rebuilds the request URI as `/{bucket}/{currentPath}`, and preserves query parameters.

State, dependencies, risks, and tests: state is the injected configuration and a per-request domains array. It integrates after signature processing and before header preprocessing/resource matching. Risks include simplistic port stripping for IPv6 host literals, host-header trust, longest-suffix domain ambiguity, and invalid request exceptions not using S3 XML errors unless mapped. Tests should cover path style, virtual-host rewrite, multiple domains, query preservation, bad hosts, and ports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/VirtualHostStyleFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/BucketMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/BucketMetadata.java

Purpose: `BucketMetadata` is the JAXB model for one bucket entry in `ListAllMyBucketsResult`.

Important APIs and flow: it has `Name` and `CreationDate` XML fields, with `Instant` marshalled through `IsoDateAdapter`. Getters and setters are simple bean accessors used by root listing responses.

State, dependencies, risks, and tests: state is transient response data only; no persistence exists. It integrates with `ListBucketResponse` and root endpoint bucket iteration. Risks are null dates/names and formatting compatibility with AWS clients. Tests should marshal list-buckets XML and assert name/date elements.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/BucketMetadata.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/CommonPrefix.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/CommonPrefix.java

Purpose: `CommonPrefix` models a `CommonPrefixes/Prefix` entry for delimited object listing responses.

Important APIs and flow: the `Prefix` field is an `EncodingTypeObject` marshalled by `ObjectKeyNameAdapter`, allowing URL encoding when `encoding-type=url` is requested. It provides a default JAXB constructor, a convenience constructor, and accessors.

State, dependencies, risks, and tests: state is response-only. It integrates with `ListObjectResponse.addPrefix` and `BucketEndpoint` delimiter logic. Risks are incorrect URL encoding of delimiters/prefixes and null prefix handling. Tests should cover common-prefix XML with and without URL encoding.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/CommonPrefix.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/DirectoryBucketMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/DirectoryBucketMetadata.java

Purpose: `DirectoryBucketMetadata` represents one bucket row in the `ListDirectoryBuckets` response.

Important APIs and flow: JAXB fields include `Name`, `CreationDate`, `BucketRegion`, and `BucketArn`, with the date marshalled by `IsoDateAdapter`. It is a simple mutable bean populated by the directory-bucket listing endpoint.

State, dependencies, risks, and tests: state is transient response data. It integrates with `ListDirectoryBucketsResponse`. Risks include region/ARN semantics diverging from AWS directory bucket expectations and null field marshalling. Tests should assert XML shape and date formatting for directory bucket listings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/DirectoryBucketMetadata.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/EncodingTypeObject.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/EncodingTypeObject.java

Purpose: `EncodingTypeObject` pairs a raw object/bucket listing string with an optional encoding type so JAXB adapters can decide whether to URL-encode it.

Important APIs and flow: it is an immutable value object with `getEncodingType`, `getName`, and `createNullable`, which returns null instead of wrapping a null name. `ObjectKeyNameAdapter` consumes it during XML marshalling.

State, dependencies, risks, and tests: state is immutable response data. It integrates with list-object fields such as prefix, delimiter, key, and start-after. Risks are callers passing unsupported encoding strings and null handling causing missing XML elements. Tests should cover null factory behavior and URL/non-URL adapter output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/EncodingTypeObject.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/IsoDateAdapter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/IsoDateAdapter.java

Purpose: `IsoDateAdapter` marshals Java `Instant` values into S3 XML timestamp strings.

Important APIs and flow: construction builds a UTC `DateTimeFormatter` with pattern `yyyy-MM-dd'T'HH:mm:ss.SSSX`. `marshal` formats the `Instant`; `unmarshal` is unsupported because these DTOs are response-only for date fields.

State, dependencies, risks, and tests: state is the formatter instance. It integrates with bucket/key/multipart response DTOs. Risks include null `Instant` causing formatter failure, AWS compatibility around millisecond precision, and unsupported unmarshal if reused for request parsing. Tests should marshal known instants and assert UTC output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/IsoDateAdapter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/KeyMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/KeyMetadata.java

Purpose: `KeyMetadata` is the JAXB model for one `Contents` object in a list-objects response.

Important APIs and flow: fields include URL-encodable `Key`, `Owner`, `LastModified`, `ETag`, `Size`, and `StorageClass`. `BucketEndpoint.addKey` populates it from `OzoneKey` metadata, replication config, owner, size, and modification time.

State, dependencies, risks, and tests: state is transient response data. It depends on `ObjectKeyNameAdapter`, `IsoDateAdapter`, `S3Owner`, and Ozone constants. Risks include missing/incorrect ETag quoting, null owner, incorrect storage-class mapping, and URL encoding mismatches. Tests should assert list response XML for normal keys, special characters, owners, and storage classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/KeyMetadata.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/ObjectKeyNameAdapter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/ObjectKeyNameAdapter.java

Purpose: `ObjectKeyNameAdapter` marshals `EncodingTypeObject` values into S3-compliant object key text for XML responses.

Important APIs and flow: `marshal` checks whether encoding type is `"url"`. If so, it calls `S3Utils.urlEncode` and then restores encoded slash `%2F` to `/`, matching S3 list response conventions. Without URL encoding, it returns the raw name. `unmarshal` is unsupported.

State, dependencies, risks, and tests: no mutable state exists. It integrates with `CommonPrefix`, `KeyMetadata`, and list response prefix/delimiter fields. Risks include unsupported unmarshal reuse, special-character encoding differences, and preserving `/` when callers expected full percent encoding. Tests should cover spaces, unicode/control-safe characters, slashes, and non-url encoding.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/ObjectKeyNameAdapter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/RequestParameters.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/RequestParameters.java

Purpose: `RequestParameters` wraps JAX-RS query parameters with typed lookup helpers used throughout S3 endpoints and handlers.

Important APIs and flow: `of` creates a `MultivaluedMapImpl`. `get` returns the first value, `get(key, defaultValue)` supplies a default, and `getInt` parses integers or throws S3 `InvalidArgument`. The nested `Mutable` interface and implementation support endpoint tests by setting/unsetting query keys.

State, dependencies, risks, and tests: state is a reference to the underlying mutable `MultivaluedMap`; there is no persistence. It integrates with `EndpointBase.initialization`, bucket listing, multipart handlers, and object subresource handlers. Risks include first-value-only semantics, unhandled long/boolean parsing, and unchecked null `params`. Tests should cover integer parsing failure, defaults, and mutation via `queryParamsForTest`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/RequestParameters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/package-info.java

Purpose: this package descriptor declares the default S3 XML namespace for common S3 response/request types and documents the package as common S3 REST API classes.

Important APIs and flow: the `@XmlSchema` annotation sets `S3Consts.S3_XML_NAMESPACE`, qualified elements, and the default namespace prefix for JAXB marshalling. DTOs under this package inherit the namespace unless overridden.

State, dependencies, risks, and tests: no runtime state exists. It integrates with JAXB XML output for list responses, common prefixes, keys, buckets, and adapters. Risks are namespace drift or missing imports if `S3Consts` changes. Test signal is XML marshalling matching S3 namespace expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/AuditingBucketOperationHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/AuditingBucketOperationHandler.java

Purpose: `AuditingBucketOperationHandler` decorates bucket-operation handlers with consistent audit success/failure logging.

Important APIs and flow: each overridden `handleDeleteRequest`, `handleGetRequest`, and `handlePutRequest` delegates to the wrapped handler, logs write/read success with `S3RequestContext` action and performance data, and logs write/read failure when exceptions are thrown. The constructor copies dependencies between endpoint and decorator/delegate.

State, dependencies, risks, and tests: state is the delegate reference. It depends on `EndpointBase` audit helpers and action mutation by downstream handlers. Risks include logging a null or stale action if no handler claims a request, duplicate auditing for special paths like multi-delete that audit manually, and missed performance data if handlers do not populate context. Tests should verify success/failure audit calls and action selection through the bucket handler chain.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/AuditingBucketOperationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/AuditingObjectOperationHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/AuditingObjectOperationHandler.java

Purpose: `AuditingObjectOperationHandler` wraps object-operation handlers with bucket-owner verification and audit logging.

Important APIs and flow: before each delegate call it verifies `x-amz-expected-bucket-owner` style conditions when present. It then delegates DELETE/GET/HEAD/PUT handling and logs read/write success or failure using the action stored in `ObjectRequestContext`; GET/PUT include performance data.

State, dependencies, risks, and tests: state is only the delegate reference. It integrates with `S3Owner`, object handler chains, `EndpointBase` audit helpers, and metrics/performance context. Risks include bucket-owner verification happening for subresources that may not need bucket fetch, null actions for ignored handlers, and failure logging with partially initialized context. Tests should cover expected-owner mismatch, delegated success, delegated failure, and audit action correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/AuditingObjectOperationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketAclHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketAclHandler.java

Purpose: `BucketAclHandler` handles bucket `?acl` GET and PUT subresource requests, translating between S3 ACL XML/header grants and Ozone native ACLs.

Important APIs and flow: `shouldHandle` checks the `acl` query parameter. GET loads the bucket, verifies expected owner, converts each Ozone ACL to S3 grants, deduplicates grants across ACCESS/DEFAULT scopes, and returns `S3BucketAcl`. PUT reads grant headers or unmarshals an XML body, converts grants to bucket and volume ACL lists, resets bucket ACLs, removes old volume ACLs for affected identities, and adds new volume ACLs.

State, dependencies, risks, and tests: state is only a memoized XML unmarshaller. It integrates with Ozone volume/bucket ACL APIs, `S3Acl`, `S3BucketAcl`, metrics, and owner verification. Risks include full ACL replacement semantics, fragile comma/equal header parsing, only supported user identities, duplicated ACCESS/DEFAULT behavior, and partial failure between bucket and volume ACL updates. Tests should cover body grants, header grants, unsupported grantees, dedupe, owner condition, metrics on failure, and volume ACL synchronization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketAclHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketCrudHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketCrudHandler.java

Purpose: `BucketCrudHandler` handles plain bucket create and delete requests when no bucket subresource query parameter is present.

Important APIs and flow: `shouldHandle` excludes `?acl`, `?uploads`, and `?delete`. PUT sets the action to `CREATE_BUCKET`, calls `ObjectStore.createS3Bucket`, updates metrics, and returns HTTP 200 with `Location: /bucket`. DELETE optionally verifies expected bucket owner, calls `OzoneVolume.deleteBucket`, updates metrics, and returns 204.

State, dependencies, risks, and tests: no persistent state exists. It integrates with the bucket handler chain, Ozone object store/volume APIs, metrics, and owner verification. Risks include subresource detection gaps for future query parameters, create returning 200 instead of some AWS variants, and failure metrics not auditing directly except through the wrapper. Tests should cover normal create/delete, expected-owner condition, non-empty/missing bucket errors via OM mapping, and ignored subresource paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketCrudHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketEndpoint.java

Purpose: `BucketEndpoint` exposes bucket-level S3 REST APIs, including list objects, bucket create/delete/head, and multi-object delete, while delegating subresources to a handler chain.

Important APIs and flow: JAX-RS methods route GET/PUT/DELETE through `handler`, while HEAD directly checks bucket existence and owner. `handleGetRequest` implements ListObjects/ListObjectsV2 compatibility: reads continuation token, delimiter, marker/start-after, prefix, max-keys, and encoding-type; validates max keys and encoding; obtains an Ozone key iterator; optionally uses shallow listing for `/` delimiter; groups common prefixes; builds `ListObjectResponse`; calculates truncation and next continuation token. `multiDelete` collects delete keys, verifies owner, calls `bucket.deleteKeys`, treats key-not-found as successful deletion, honors quiet mode, records errors, metrics, and audit.

State, dependencies, risks, and tests: state includes configured shallow-listing flag, max-keys limit, and initialized handler chain. It integrates with Ozone buckets, `ContinueToken`, list response DTOs, metrics, S3 owner checks, and audit. Risks include delimiter grouping edge cases, continuation token correctness with `prevDir`, duplicate delete key handling, mutation of `deleteKeys` while auditing failures, and mapping `FILE_NOT_FOUND` prefix errors to empty listings. Tests should cover list v1/v2 parameters, encoding, delimiter/common prefixes, truncation tokens, max-key validation, head owner checks, and multi-delete mixed success/error behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketGetLocationHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketGetLocationHandler.java

Purpose: `BucketGetLocationHandler` explicitly handles `GET Bucket ?location` by returning `NotImplemented` instead of falling through to list-objects.

Important APIs and flow: `handleGetRequest` checks the `location` query parameter. If absent, it returns null for the chain. If present, it sets `S3GAction.GET_BUCKET_LOCATION` and throws `NOT_IMPLEMENTED` for `GetBucketLocation`.

State, dependencies, risks, and tests: no state or persistence exists. It integrates with the bucket handler chain and audit wrapper. Risk is that AWS-compatible clients expecting location responses fail, but explicit not-implemented behavior is clearer than an incorrect XML body. Tests should verify `?location` claims the request and plain GET bucket still lists objects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketGetLocationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketOperationHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketOperationHandler.java

Purpose: `BucketOperationHandler` is the abstract base for bucket subresource handlers in a chain-of-responsibility design.

Important APIs and flow: default `handlePutRequest`, `handleGetRequest`, and `handleDeleteRequest` return null, signaling "not responsible". `copyDependenciesFrom` copies endpoint dependencies from an `EndpointBase`, enabling handlers created manually in `BucketEndpoint.init()` to use CDI-provided config/client/context fields.

State, dependencies, risks, and tests: state is inherited endpoint dependency state. It integrates with `BucketOperationHandlerChain`, concrete ACL/CRUD/location/multipart handlers, and auditing wrappers. Risks include handlers forgetting to return null for unclaimed requests or failing to set action before returning/throwing. Tests should verify dependency copying and chain fall-through semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketOperationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketOperationHandlerChain.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketOperationHandlerChain.java

Purpose: `BucketOperationHandlerChain` dispatches bucket requests to the first handler that claims them.

Important APIs and flow: for DELETE, GET, and PUT it loops through handlers in insertion order, returning the first non-null `Response`. The builder copies dependencies from the owning `BucketEndpoint` into each added handler and into the final chain.

State, dependencies, risks, and tests: state is an ordered list of handlers. It integrates with `BucketEndpoint.init`, where location, ACL, multipart listing, CRUD, and fallback endpoint handlers are ordered deliberately. Risks include ordering changes causing broad handlers to preempt specific subresources, null response after all handlers, and dependency copy timing. Tests should cover ordering and fallback for each subresource.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketOperationHandlerChain.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CompleteMultipartUploadRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CompleteMultipartUploadRequest.java

Purpose: `CompleteMultipartUploadRequest` is the JAXB request model for S3 Complete Multipart Upload XML.

Important APIs and flow: the root element is `CompleteMultipartUpload` in the S3 namespace. It contains a list of `Part` elements, each with `PartNumber` and `ETag`. The object endpoint consumes this model after XML unmarshalling to complete an MPU in Ozone.

State, dependencies, risks, and tests: state is request body data only. It integrates with `CompleteMultipartUploadRequestUnmarshaller` and object MPU completion. Risks include accepting unordered, duplicate, missing, or empty part lists unless later validation catches them. Tests should unmarshal namespace and non-namespace XML and validate downstream error handling for bad parts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CompleteMultipartUploadRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CompleteMultipartUploadRequestUnmarshaller.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CompleteMultipartUploadRequestUnmarshaller.java

Purpose: this JAX-RS provider unmarshals complete-MPU XML while rejecting an empty request body early.

Important APIs and flow: it extends `MessageUnmarshaller<CompleteMultipartUploadRequest>`. `readFrom` checks `inputStream.available() == 0`, throws S3 `InvalidRequest` with "You must specify at least one part", otherwise delegates to the secure namespace-filtering unmarshaller. IO failures are wrapped as S3 invalid request errors.

State, dependencies, risks, and tests: no mutable state beyond inherited JAXB context. It integrates with Jersey body readers and object endpoint complete-MPU. Risks include `InputStream.available()` not being a reliable body-length check for all stream types and parse errors exposing parser messages. Tests should cover empty body, malformed XML, namespace/no-namespace XML, and at least-one-part validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CompleteMultipartUploadRequestUnmarshaller.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CompleteMultipartUploadResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CompleteMultipartUploadResponse.java

Purpose: `CompleteMultipartUploadResponse` is the JAXB XML result model for a successful complete-MPU request.

Important APIs and flow: fields are `Location`, `Bucket`, `Key`, and `ETag` under `CompleteMultipartUploadResult`. Object endpoint code populates these after Ozone completes multipart assembly.

State, dependencies, risks, and tests: state is transient response data. It integrates with JAXB and Ozone MPU completion metadata. Risks are incorrect ETag quoting/location format and null fields for edge cases. Tests should assert XML shape and ETag/location content after complete MPU.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CompleteMultipartUploadResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CopyObjectResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CopyObjectResponse.java

Purpose: `CopyObjectResponse` is the JAXB result for successful S3 CopyObject.

Important APIs and flow: it contains `LastModified` marshalled through `IsoDateAdapter` and `ETag`. Object copy handling fills the values from the created/copied Ozone key metadata.

State, dependencies, risks, and tests: state is response-only. It depends on JAXB, `IsoDateAdapter`, and Ozone ETag metadata. Risks include ETag quote compatibility and timestamp precision/timezone. Tests should assert copy-object response XML and metadata propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CopyObjectResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CopyPartResult.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CopyPartResult.java

Purpose: `CopyPartResult` is the JAXB response for successful multipart `UploadPartCopy`.

Important APIs and flow: it exposes `LastModified` and `ETag`; the convenience constructor sets the ETag and `Instant.now()`. Object MPU copy-part handling returns this model after creating the copied part.

State, dependencies, risks, and tests: state is transient response data. It depends on `IsoDateAdapter` and S3 XML namespace constants. Risks include using gateway wall-clock time rather than storage commit time when the convenience constructor is used, and ETag quote handling. Tests should check XML output and timestamp/ETag expectations for copy part.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CopyPartResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/EndpointBase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/EndpointBase.java

Purpose: `EndpointBase` is the shared foundation for S3 Gateway resources and handlers, centralizing injected dependencies, query parameter capture, S3 auth propagation, metadata/tag parsing, audit helpers, replication resolution, copy-source parsing, chunked upload input selection, digest creation, and common validation utilities.

Important APIs and flow: `initialization()` builds `RequestParameters`, creates `S3Auth` from `SignatureInfo`, installs it into the OM client proxy thread-local, loads buffer/chunk/datastream config, and calls `init()`. Bucket helpers list the S3 volume and map OM errors to S3 errors. Metadata helpers extract custom `x-amz-meta-*` headers, enforce metadata size, and remap custom `ETag` to `etag-custom`. Tag helpers parse `x-amz-tagging`, validate S3 tag count/length/pattern/uniqueness, and differentiate missing XML values from header empty values. Audit helpers add request IDs and client IP. Upload helpers parse copy-source, part-number markers, select `SignedChunksInputStream` or `UnsignedChunksInputStream`, wrap with `MultiDigestInputStream`, and validate content length.

State, dependencies, risks, and tests: state includes injected config/client/signature/request IDs/context/headers plus per-endpoint S3 auth, query params, buffer sizes, and datastream flags. It depends on Ozone client APIs, OM `S3Auth`, S3 utility classes, metrics, audit framework, JAX-RS context, and digest algorithms. Risks include thread-local auth leaks if producer cleanup fails, metadata/tag validation drift from AWS, no per-chunk signature/trailer verification, mutable query params in tests, and digest thread-local reuse requiring callers to reset/digest correctly. Tests should cover initialization, metadata remapping/limits, tag validation, copy-source decoding, chunk stream selection, content-length validation, audit parameters, and replication config resolution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/EndpointBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListBucketResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListBucketResponse.java

Purpose: `ListBucketResponse` is the JAXB result model for root ListBuckets (`ListAllMyBucketsResult`).

Important APIs and flow: it wraps a `Buckets` list of `BucketMetadata` elements and an `Owner`. Root endpoint code appends bucket metadata and sets the owner before returning XML.

State, dependencies, risks, and tests: state is response-only. It integrates with root bucket listing and `BucketMetadata`. Risks are missing owner, incorrect wrapper element names, and bucket ordering/count mismatches. Tests should assert XML shape and `getBucketsNum` for list-buckets behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListBucketResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListDirectoryBucketsResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListDirectoryBucketsResponse.java

Purpose: `ListDirectoryBucketsResponse` is the JAXB model for S3 directory bucket listing responses.

Important APIs and flow: it wraps a `Buckets` list of `DirectoryBucketMetadata` and exposes an optional `ContinuationToken`. The root endpoint populates bucket rows and continuation state.

State, dependencies, risks, and tests: state is response-only. It integrates with directory-bucket list APIs and directory bucket metadata. Risks include incomplete AWS compatibility around continuation, region, and ARN fields. Tests should assert XML wrapping and continuation token behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListDirectoryBucketsResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListMultipartUploadsHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListMultipartUploadsHandler.java

Purpose: `ListMultipartUploadsHandler` handles bucket `?uploads` requests that list in-progress multipart uploads.

Important APIs and flow: it claims requests with the `uploads` query parameter, sets `LIST_MULTIPART_UPLOAD`, reads key marker, upload ID marker, prefix, and max uploads, caps max uploads at 1000, rejects values less than one, verifies bucket owner, calls `OzoneBucket.listMultipartUploads`, and maps Ozone upload entries into `ListMultipartUploadsResult.Upload` with storage class.

State, dependencies, risks, and tests: no persistent state exists. It integrates with Ozone multipart listing, bucket handler chain, metrics, owner verification, and response DTOs. Risks include not supporting delimiter semantics here, max-upload parsing/capping behavior, and exception mapping through outer endpoint code. Tests should cover markers, prefix, max upload validation/capping, owner mismatch, truncation markers, and storage-class mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListMultipartUploadsHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListMultipartUploadsResult.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListMultipartUploadsResult.java

Purpose: `ListMultipartUploadsResult` is the JAXB XML response for listing active multipart uploads in a bucket.

Important APIs and flow: top-level fields capture bucket, key/upload markers, next markers, prefix, max uploads, truncation flag, and a list of `Upload` entries. Each upload includes key, upload ID, owner, initiator, storage class, and initiation time marshalled through `IsoDateAdapter`.

State, dependencies, risks, and tests: state is transient response data. It integrates with `ListMultipartUploadsHandler`, `S3Owner`, and `S3StorageType`. Risks include default owner/initiator values hiding real identity, null markers, and storage-class string compatibility. Tests should assert truncated and non-truncated XML, upload rows, and date formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListMultipartUploadsResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListObjectResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListObjectResponse.java

Purpose: `ListObjectResponse` is the JAXB model for `ListBucketResult`, shared by S3 list objects compatibility paths.

Important APIs and flow: fields include name, prefix, marker, max keys, key count, delimiter, encoding type, truncation flag, next continuation token, next marker, current continuation token, contents, common prefixes, and start-after. URL-sensitive fields use `ObjectKeyNameAdapter`. `BucketEndpoint` populates it while iterating Ozone keys.

State, dependencies, risks, and tests: state is response-only. It integrates with `KeyMetadata`, `CommonPrefix`, `EncodingTypeObject`, and bucket listing flow. Risks include the lowercase XML element name `continueToken`, v1/v2 compatibility fields appearing together, and key count recalculation. Tests should marshal normal, delimited, encoded, truncated, and empty listings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListObjectResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListPartsResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListPartsResponse.java

Purpose: `ListPartsResponse` is the JAXB response for S3 list-parts on an active multipart upload.

Important APIs and flow: top-level fields hold bucket, key, upload ID, storage class, part marker, next part marker, max parts, truncation flag, and `Part` entries. Each part includes part number, last modified, ETag, and size. `MultipartKeyHandler` populates it from `OzoneMultipartUploadPartListParts`.

State, dependencies, risks, and tests: state is transient response data. It integrates with multipart object handlers, `IsoDateAdapter`, and Ozone part metadata. Risks include ETag fallback to part name when ETag is empty, max-parts validation occurring outside the DTO, and marker defaults. Tests should assert XML for truncated/non-truncated part lists, ETag fallback, storage class, and date formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListPartsResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MessageUnmarshaller.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MessageUnmarshaller.java

Purpose: `MessageUnmarshaller<T>` is a generic secure XML body reader for S3 request models, tolerant of XML with or without the S3 namespace.

Important APIs and flow: construction creates a JAXB context for the target class and a secure SAX parser factory via `XMLUtils`. `isReadable` matches the exact target type. `readFrom` creates an XML reader, a JAXB unmarshaller handler, wraps it in `XmlNamespaceFilter` for the S3 namespace, parses the input, and casts the result. Parse failures are converted to S3 `InvalidRequest`. A convenience `readFrom(InputStream)` supports programmatic use.

State, dependencies, risks, and tests: state is the JAXB context, parser factory, and target class. It integrates with multi-delete, ACL, and complete-MPU unmarshallers. Risks include exact type matching missing subclass/generic cases, parser error messages leaking details, and no schema validation beyond JAXB. Tests should cover namespaced and non-namespaced XML, XXE-safe parser behavior, malformed XML, and programmatic reads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MessageUnmarshaller.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultiDeleteRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultiDeleteRequest.java

Purpose: `MultiDeleteRequest` is the JAXB request model for S3 multi-object delete.

Important APIs and flow: root `Delete` contains optional `Quiet` and a list of `Object` elements. Each `DeleteObject` has `Key` and optional `VersionId`. `BucketEndpoint.multiDelete` consumes the object list and quiet flag.

State, dependencies, risks, and tests: state is request body data. Version IDs are parsed but current delete flow ignores versioning. Risks include null object list/key entries, duplicate keys, quiet Boolean nullability versus primitive setter, and unsupported version semantics. Tests should cover quiet true/false, namespace/no-namespace XML, empty objects, null keys, and version ID handling expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultiDeleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultiDeleteRequestUnmarshaller.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultiDeleteRequestUnmarshaller.java

Purpose: `MultiDeleteRequestUnmarshaller` registers the generic XML unmarshaller for `MultiDeleteRequest` bodies.

Important APIs and flow: it is a singleton JAX-RS provider producing `application/xml`, and its constructor binds `MessageUnmarshaller` to `MultiDeleteRequest.class`. All read behavior is inherited.

State, dependencies, risks, and tests: inherited state is JAXB context and parser factory. It integrates with `BucketEndpoint.multiDelete` body binding. Risks are inherited from `MessageUnmarshaller`, especially malformed XML and namespace tolerance. Tests should assert Jersey selects this reader and parses delete XML with and without namespace.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultiDeleteRequestUnmarshaller.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultiDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultiDeleteResponse.java

Purpose: `MultiDeleteResponse` is the JAXB XML result for S3 multi-object delete.

Important APIs and flow: it stores `Deleted` entries and `Error` entries. `DeletedObject` includes key and version ID; `Error` includes key, code, and message. `BucketEndpoint.multiDelete` appends deleted rows unless quiet mode is true and appends errors for failed keys or all-key internal failures.

State, dependencies, risks, and tests: state is response-only. It integrates with multi-delete endpoint logic and S3 error code mapping. Risks include version ID not being XML-annotated in `DeletedObject`, quiet mode suppressing success rows but not errors, and all-key errors using key `ALL`. Tests should assert mixed success/error XML, quiet behavior, and version field serialization expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultiDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultipartKeyHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultipartKeyHandler.java

Purpose: `MultipartKeyHandler` handles object-key multipart operations that are not POST: list parts and abort multipart upload.

Important APIs and flow: GET claims requests with `uploadId`, sets `LIST_PARTS`, parses `max-parts` and `part-number-marker`, and calls `listParts`. DELETE claims non-empty `uploadId`, sets `ABORT_MULTIPART_UPLOAD`, and calls `ClientProtocol.abortMultipartUpload`. `listParts` calls `OzoneBucket.listParts`, fills `ListPartsResponse`, maps storage class and truncated next marker, converts part metadata to response parts, and maps missing upload/access errors to S3 errors.

State, dependencies, risks, and tests: no persistent state exists. It integrates with object handler chains, Ozone multipart APIs, metrics, `ListPartsResponse`, and S3 error table. Risks include no explicit max-parts lower/upper validation here, integer parsing exceptions, ETag fallback to part name, and access-denied mapping depending on OM result codes. Tests should cover list parts, abort, missing upload, access denied, part marker parsing, truncation, and metric updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultipartKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultipartUploadInitiateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultipartUploadInitiateResponse.java

Purpose: `MultipartUploadInitiateResponse` is the JAXB XML result for initiating a multipart upload.

Important APIs and flow: fields are `Bucket`, `Key`, and `UploadId`. The object endpoint fills them after Ozone creates a multipart upload record.

State, dependencies, risks, and tests: state is response-only. It integrates with object PUT `?uploads` handling. Risks include missing URL encoding for keys and null upload IDs if Ozone initiation fails before response creation. Tests should assert XML shape and correct bucket/key/upload ID values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultipartUploadInitiateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectAclHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectAclHandler.java

Purpose: `ObjectAclHandler` reserves object ACL handling for the object handler chain but currently reports it as not implemented.

Important APIs and flow: `getAction` checks for the `acl` query parameter and returns `PUT_OBJECT_ACL` only for HTTP PUT. `handlePutRequest` ignores the request if no action is selected; otherwise it throws S3 `NOT_IMPLEMENTED` for the key and updates put-object-ACL failure metrics.

State, dependencies, risks, and tests: there is no persistent state. It integrates with object operation chain action selection, query params, request method, metrics, and audit wrapper. Risks include GET object ACL falling through to another handler if not separately handled, and clients expecting ACL support receiving not implemented. Tests should verify PUT `?acl` returns not implemented, failure metrics increment, and non-ACL PUT falls through.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectAclHandler.java -->
