# subset-b-008016 Research

Grouped source research for Apache Ozone HDDS token verification, X.509 certificate authority/client utilities, server administration helpers, runtime metadata, YAML loading, and event executor contracts. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenVerifier.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenVerifier.java

## Purpose

`ContainerTokenVerifier` adapts the generic short-lived token verifier to Ozone container tokens. It decides when datanode container commands require a token, creates the container-token identifier used for deserialization, and binds the token service check to the container ID in the protobuf command.

## Important APIs, Types, and Functions

The class extends `ShortLivedTokenVerifier<ContainerTokenIdentifier>`. Its constructor accepts `SecurityConfig` and `SecretKeyVerifierClient`. `isTokenRequired(ContainerProtos.Type)` combines `SecurityConfig.isContainerTokenEnabled()` with `HddsUtils.requireContainerToken(cmdType)`. `createTokenIdentifier()` returns a fresh `ContainerTokenIdentifier`. `getService(ContainerCommandRequestProtoOrBuilder)` converts `cmd.getContainerID()` to `ContainerID`.

## Control Flow

All verification flow is inherited. When `verify` is called, the base class asks this class whether the command type is protected, decodes the token identifier, validates the secret-key signature, checks expiration, compares the token service string with the command container ID, and then runs the no-op extension hook.

## State and Persistence Behavior

No mutable state is owned here beyond constructor-injected base-class fields. It depends on the external secret-key verifier client for current/older signing keys and on command contents for the service identity.

## Dependencies and Integration Points

It integrates datanode container RPC command validation with `HddsUtils.requireContainerToken`, `ContainerProtos`, `ContainerID`, `SecurityConfig`, and `SecretKeyVerifierClient`. It is normally installed through `TokenVerifier.create` alongside the block verifier.

## Risks and Edge Cases

The service comparison relies on `ContainerID.toString()` matching the token identifier service string. Misclassification in `HddsUtils.requireContainerToken` weakens enforcement for a command type. A missing or expired signing key causes rejection even if the token itself has not expired.

## Test Signals

Useful tests include enabled/disabled container-token configuration, commands that do and do not require tokens, container ID mismatch, expired token, missing secret key, invalid signature, and a valid token generated with the matching `ContainerTokenIdentifier` service.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/NoopTokenVerifier.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/NoopTokenVerifier.java

## Purpose

`NoopTokenVerifier` is the permissive `TokenVerifier` implementation used when block and container token enforcement are disabled. It preserves the verifier interface without requiring callers to branch around verification.

## Important APIs, Types, and Functions

It implements both `verify(Token<?> token, ContainerCommandRequestProtoOrBuilder cmd)` and `verify(ContainerCommandRequestProtoOrBuilder cmd, String encodedToken)`. Both methods intentionally return without inspecting token, encoded token, or command.

## Control Flow

There is no internal control flow. The explicit encoded-token overload bypasses the default interface method, preventing an empty-token failure in deployments where security settings intentionally disable token checks.

## State and Persistence Behavior

The class is stateless and has no persistence behavior.

## Dependencies and Integration Points

It is selected by `TokenVerifier.create` when both `SecurityConfig.isBlockTokenEnabled()` and `SecurityConfig.isContainerTokenEnabled()` are false. It is used by container RPC paths that always call a verifier even in insecure or token-disabled deployments.

## Risks and Edge Cases

Accidental selection due to incorrect configuration disables token authorization completely. Tests should verify it is only created when both block and container token flags are false.

## Test Signals

Check that null/empty encoded tokens do not fail under this verifier, that normal `TokenVerifier.create` returns it only for fully disabled token settings, and that callers still execute successfully through the shared verifier call path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/NoopTokenVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/OzoneBlockTokenSecretManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/OzoneBlockTokenSecretManager.java

## Purpose

`OzoneBlockTokenSecretManager` issues short-lived Ozone block tokens. It creates `OzoneBlockTokenIdentifier` instances carrying owner, `BlockID`, access modes, expiry time, and maximum allowed length, then signs them with the current managed secret key inherited from `ShortLivedTokenSecretManager`.

## Important APIs, Types, and Functions

The constructor takes token lifetime and `SecretKeySignerClient`. `createIdentifier(String, BlockID, Set<AccessModeProto>, long)` builds the token identifier with `getTokenExpiryTime().toEpochMilli()`. `generateToken(String, BlockID, Set<AccessModeProto>, long)` creates a Hadoop `Token` whose identifier bytes/password/kind/service come from the identifier. `generateToken(BlockID, Set<AccessModeProto>, long)` derives the owner from `UserGroupInformation.getCurrentUser().getShortUserName()`.

## Control Flow

The generation path computes an identifier, logs issuance details when debug is enabled, calls `createPassword` to set the signing key ID and signature, then creates the token with the block service text. The UGI overload only resolves the current user and delegates.

## State and Persistence Behavior

No local token database is maintained. State is embedded in the signed token identifier and depends on the externally managed secret key lifecycle. Token validity persists until the identifier expiry time or signing key expiry.

## Dependencies and Integration Points

It integrates with block access mode protobufs, `BlockID`, Hadoop tokens, UGI, and `SecretKeySignerClient`. Generated tokens are consumed by block token verifiers on container command handling paths.

## Risks and Edge Cases

A null current UGI produces a null owner. Access modes and max length are trusted inputs at creation time and need caller-side correctness. Log guard uses debug check but logs at info level, which can surprise operators if debug is enabled.

## Test Signals

Tests should assert service equals the block ID, secret key ID is populated, password verifies with the signer key, expiry follows configured lifetime, owner selection from UGI works, and max-length/access-mode fields round-trip through token serialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/OzoneBlockTokenSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ShortLivedTokenSecretManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ShortLivedTokenSecretManager.java

## Purpose

`ShortLivedTokenSecretManager` is the generic signing base for short-lived token identifiers. It centralizes token lifetime calculation, signing with the current managed secret key, and construction of Hadoop `Token<T>` objects.

## Important APIs, Types, and Functions

The type parameter is bounded by `ShortLivedTokenIdentifier`. `createPassword(T)` gets `SecretKeySignerClient.getCurrentSecretKey()`, stores that key ID into the token identifier, and returns `ManagedSecretKey.sign(tokenId)`. `getTokenExpiryTime()` returns now plus configured max lifetime. `generateToken(T)` wraps identifier bytes, password, kind, and service in a Hadoop token. `setSecretKeyClient` exists for integration tests.

## Control Flow

Callers construct or receive a populated identifier, then call `generateToken`. The manager signs after setting the secret key ID, so verifiers can later fetch the exact key by ID before checking the signature.

## State and Persistence Behavior

The class stores token lifetime and the signer client reference. It persists no token state. Persistent security state lives in the secret-key subsystem and in serialized token identifiers given to clients.

## Dependencies and Integration Points

It depends on `ManagedSecretKey`, `SecretKeySignerClient`, Hadoop `Token`, and `Text`. Concrete subclasses such as block and container token managers provide domain-specific identifiers and services.

## Risks and Edge Cases

Clock skew affects effective expiry. Replacing the signer client in tests mutates shared manager state, so production code should not call it. If the current secret key rotates immediately after issuance, verifiers must still retain the old key until all tokens expire.

## Test Signals

Check generated token fields, key ID mutation before signing, expiry timing, behavior with a fake signer client, and verification compatibility across secret-key rotation windows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ShortLivedTokenSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ShortLivedTokenVerifier.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ShortLivedTokenVerifier.java

## Purpose

`ShortLivedTokenVerifier` is the generic verifier for signed, short-lived Ozone tokens. It handles token decoding, signing-key lookup, signature verification, expiration, service matching, and a subclass hook for additional domain checks.

## Important APIs, Types, and Functions

Subclasses implement `isTokenRequired(ContainerProtos.Type)`, `createTokenIdentifier()`, and `getService(ContainerCommandRequestProtoOrBuilder)`. The public `verify(Token<?> token, ContainerCommandRequestProtoOrBuilder cmd)` performs core validation. Protected `verify(T tokenId, cmd)` is a no-op extension hook. Private `verifyTokenPassword` fetches `ManagedSecretKey` by token secret key ID and validates signature state.

## Control Flow

If the command does not require the token type, verification returns early. Otherwise it reads identifier bytes into a new token identifier, verifies the token password against the referenced secret key, rejects expired token identifiers, compares command service string with token service, and finally invokes subclass-specific validation.

## State and Persistence Behavior

It stores immutable `SecurityConfig` and `SecretKeyVerifierClient` references. No decisions are cached; every call consults token bytes, command data, and secret-key client state.

## Dependencies and Integration Points

It integrates Hadoop tokens with Ozone `ContainerProtos`, `SecurityConfig`, `SecretKeyVerifierClient`, `ManagedSecretKey`, and `SCMSecurityException`/`BlockTokenException`. Concrete block and container verifiers plug into `CompositeTokenVerifier`.

## Risks and Edge Cases

Early return depends entirely on subclass command-type classification. Service comparison is string-based. Missing, expired, or unavailable secret keys reject otherwise well-formed tokens. Decode failures hide the original `IOException` detail in a new exception message.

## Test Signals

Exercise non-required command bypass, malformed identifier bytes, missing secret key, expired signing key, invalid signature, expired token, service mismatch, and subclass hook invocation after all common checks pass.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ShortLivedTokenVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/TokenVerifier.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/TokenVerifier.java

## Purpose

`TokenVerifier` is the common interface for Ozone gRPC/container-token header validation. It provides direct token verification, encoded-token decoding, and a factory that selects no-op or composite block/container verification based on security configuration.

## Important APIs, Types, and Functions

`verify(Token<?> token, ContainerCommandRequestProtoOrBuilder cmd)` is the required method. The default `verify(cmd, encodedToken)` rejects null/empty values, decodes the URL-safe Hadoop token string, and delegates. Static `create(SecurityConfig, SecretKeyVerifierClient)` returns `NoopTokenVerifier` when both token types are disabled, otherwise a `CompositeTokenVerifier` containing `BlockTokenVerifier` and `ContainerTokenVerifier`.

## Control Flow

Callers can pass encoded metadata directly. The default method enforces that a token exists before decoding. The factory chooses verifier topology at service startup or translator construction time.

## State and Persistence Behavior

The interface owns no state. Implementations may hold configuration and secret-key clients; verification state is per request.

## Dependencies and Integration Points

It sits between container command handlers and the Ozone security token subsystem. It depends on Guava `Strings`, Hadoop `Token`, protobuf command builders, `SecurityConfig`, and `SecretKeyVerifierClient`.

## Risks and Edge Cases

Implementations that do not override the encoded-token overload will reject empty tokens. The factory always installs both block and container verifiers when either token type is enabled, relying on each verifier's `isTokenRequired` predicate to bypass irrelevant commands.

## Test Signals

Test empty/null encoded token rejection, invalid URL token decode, factory selection for all four block/container enablement combinations, and composite behavior where only the relevant verifier enforces a command.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/TokenVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.hdds.security.token` as the HDDS/Ozone token package.

## Important APIs, Types, and Functions

There are no executable APIs in this file. Its package-level documentation covers nearby token identifiers, secret managers, and verifiers.

## Control Flow

No runtime control flow.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It declares the package for JavaDoc and compile structure. The package integrates Hadoop tokens, managed secret keys, and container/block command authorization.

## Risks and Edge Cases

The only risk is documentation drift if package responsibilities change.

## Test Signals

Compile/package JavaDoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/CertInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/CertInfo.java

## Purpose

`CertInfo` wraps an `X509Certificate` with the timestamp at which it was persisted in the database. It provides a DB codec and stable ordering by timestamp for certificate metadata records.

## Important APIs, Types, and Functions

Static `CODEC` is a `DelegatedCodec` over `CertInfoProto`, converting through `fromProtobuf` and `getProtobuf`. `COMPARATOR` orders by `getTimestamp`. Public accessors expose certificate and timestamp. `compareTo`, `equals`, `hashCode`, and `toString` implement value-like semantics. The nested `Builder` sets certificate and timestamp.

## Control Flow

Serialization converts the certificate to PEM with `CertificateCodec.getPEMEncodedString`; deserialization parses PEM with `CertificateCodec.getX509Certificate`. Conversion failures are wrapped in `CodecException`.

## State and Persistence Behavior

The object is immutable after construction. Its persistence behavior is explicitly protobuf-backed via `CertInfoProto`, so it can be stored in Ozone metadata DB tables using `Codec<CertInfo>`.

## Dependencies and Integration Points

It integrates certificate metadata with HDDS DB codecs, `HddsProtos.CertInfoProto`, `CertificateCodec`, and SCM security exceptions.

## Risks and Edge Cases

`Builder.build()` does not validate non-null certificate input. `toString()` calls `x509Certificate.toString()` and can be verbose. Ordering only by timestamp can compare distinct certificates as equal in `compareTo` if persisted at the same millisecond.

## Test Signals

Round-trip codec tests with real PEM certificates, malformed protobuf PEM handling, equality/hash behavior, timestamp ordering, and null-builder field behavior should cover the class.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/CertInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CertificateApprover.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CertificateApprover.java

## Purpose

`CertificateApprover` defines the policy interface used by an Ozone certificate authority to inspect CSRs and sign certificates.

## Important APIs, Types, and Functions

`inspectCSR(PKCS10CertificationRequest)` returns a `CompletableFuture<Void>` that completes normally when the CSR is acceptable. `sign(SecurityConfig, PrivateKey, X509Certificate, Date, Date, PKCS10CertificationRequest, String, String, String)` returns a signed `X509Certificate`. `ApprovalType` enumerates `KERBEROS_TRUSTED`, `MANUAL`, and `TESTING_AUTOMATIC`.

## Control Flow

The interface separates asynchronous or policy-rich CSR inspection from the synchronous signing operation. CA implementations call inspection before signing and select behavior based on approval type.

## State and Persistence Behavior

No state or persistence is defined here. Implementations may hold profiles, configuration, and policy state.

## Dependencies and Integration Points

It is consumed by `DefaultCAServer` and implemented by `DefaultApprover`. It depends on BouncyCastle PKCS#10 requests, Java private keys/certificates, and `SecurityConfig`.

## Risks and Edge Cases

Manual approval is part of the type contract but not implemented by the default CA. The interface permits asynchronous inspection, so callers must handle exceptional completion correctly.

## Test Signals

Mock approver tests should cover normal and exceptional future completion, manual approval rejection in CA code, and sign parameter propagation including validity dates, serial ID, SCM ID, and cluster ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CertificateApprover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CertificateServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CertificateServer.java

## Purpose

`CertificateServer` is the abstraction for an SCM certificate authority. It allows the default in-process CA to be replaced later by external CAs or HSM-backed implementations.

## Important APIs, Types, and Functions

The interface defines `init(SecurityConfig, CAType)`, `getCACertificate()`, `getCaCertPath()`, `getCertificate(String)`, `requestCertificate(PKCS10CertificationRequest, ApprovalType, NodeType, String)`, `listCertificate(NodeType, long, int)`, and `reinitialize(SCMMetadataStore)`.

## Control Flow

Consumers initialize the CA, retrieve CA material, request issued certificates through CSR approval/signing, list stored certificates, and reinitialize the backing store after SCM metadata reload.

## State and Persistence Behavior

Persistence is delegated to implementations and their `CertificateStore`. The interface makes certificate issuance and listing part of the persistent CA contract.

## Dependencies and Integration Points

It bridges HDDS security configuration, SCM metadata store, BouncyCastle CSR objects, protobuf `NodeType`, Java `CertPath`, and `X509Certificate`.

## Risks and Edge Cases

`requestCertificate` returns `Future<CertPath>`, so implementations can be asynchronous and callers must handle delayed exceptional failure. `getCertificate` returns null for absent certificates in the default implementation, so null checks are required.

## Test Signals

Contract tests should cover successful initialization, missing certificate lookup, request failure propagation, certificate path ordering, role-based listing, and store reinitialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CertificateServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CertificateStore.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CertificateStore.java

## Purpose

`CertificateStore` defines the persistent certificate database operations needed by the default CA while avoiding a hard dependency from common HDDS code back into SCM implementation classes.

## Important APIs, Types, and Functions

It extends `SCMHandler` and defaults `getType()` to `SCMRatisProtocol.RequestType.CERT_STORE`. `storeValidCertificate` is annotated with `@Replicate(invocationType = CLIENT)`. Other methods include `storeValidScmCertificate`, `checkValidCertID`, `removeAllExpiredCertificates`, `getCertificateByID`, `listCertificate`, and `reinitialize`.

## Control Flow

The CA checks serial uniqueness, stores issued certificates by role, lists certificates for API calls, removes expired entries, and rebinds to a new `SCMMetadataStore` during SCM state reload.

## State and Persistence Behavior

This is the main persistence boundary for issued certificates. Ratis replication annotations signal operations that must be replicated in SCM HA.

## Dependencies and Integration Points

It integrates Java `X509Certificate`, serial `BigInteger`, protobuf `NodeType`, SCM HA handling, replication metadata, and SCM metadata DB abstractions.

## Risks and Edge Cases

Implementations must keep serial uniqueness atomic with storage. Role-specific listing must define ordering and pagination semantics. HA replication behavior is critical for certificate consistency across SCM nodes.

## Test Signals

Tests should cover duplicate serial rejection, valid certificate storage/listing per role, SCM certificate storage, expired certificate removal, Ratis replication invocation, and reinitialize behavior after metadata checkpoint restore.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CertificateStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/DefaultApprover.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/DefaultApprover.java

## Purpose

`DefaultApprover` implements the default CSR inspection and certificate signing policy for Ozone's in-process CA. It verifies CSR proof-of-possession, checks requested RDNs and extensions against a `PKIProfile`, enforces SCM/cluster identity, validates key size, and emits an X.509 certificate signed by the CA private key.

## Important APIs, Types, and Functions

Constructor arguments are `PKIProfile` and `SecurityConfig`. `sign(...)` builds signature and digest algorithm identifiers, extracts subject OU/O/CN, handles the datanode pre-registration `null` SCM/cluster special case, rebuilds the subject with serial number, validates RSA modulus length against `config.getSize()`, copies supported CSR extensions, and returns a `JcaX509CertificateConverter` result. `inspectCSR` returns a future after `verifyPkcs10Request`, `profile.validateRDN`, and `verfiyExtensions`. Helper methods decode PKCS#9 extension attributes.

## Control Flow

Inspection is staged: validate CSR signature, validate each RDN, validate each requested extension. Signing then performs identity and key checks before constructing `X509v3CertificateBuilder` and signing with `BcRSAContentSignerBuilder`.

## State and Persistence Behavior

The approver owns no persistence; it is a pure policy/signing component over supplied key and certificate material.

## Dependencies and Integration Points

It depends heavily on BouncyCastle ASN.1, PKCS#10, X.509 builder, content signer/verifier APIs, `PKIProfile`, `CertificateSignRequest` helpers, and `SCMSecurityException`. It is created by `DefaultCAServer.init`.

## Risks and Edge Cases

The method assumes OU, O, and CN RDNs are present at index zero; malformed subjects can throw runtime exceptions. `inspectCSR` can call `completeExceptionally` and still continue checking later stages because it does not return immediately after failure. The misspelled `verfiyExtensions` is visible to tests. Only RSA public keys are accepted by the cast to `RSAKeyParameters`.

## Test Signals

Coverage should include valid CSR signing, invalid CSR signature, unsupported extension, unsupported RDN, key size too small, cluster/SCM mismatch, datanode null SCM/cluster substitution, missing RDNs, CA extension handling, and returned certificate subject/issuer/serial/validity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/DefaultApprover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/DefaultCAServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/DefaultCAServer.java

## Purpose

`DefaultCAServer` is the default SCM certificate authority implementation. It bootstraps or validates CA key/certificate files, supports external or self-signed root CA initialization, signs CSRs through `DefaultApprover`, stores issued certificates, and exposes CA certificate lookup/listing APIs.

## Important APIs, Types, and Functions

Constructors set subject, cluster ID, SCM ID, `CertificateStore`, root cert ID, profile, and component name. `init` resolves certificate location, builds `DefaultApprover`, verifies key/cert state, and runs the selected initializer. `requestCertificate` inspects CSR, rejects manual approval, signs/stores automatic requests, and prepends the signed cert to CA cert path. `signAndStoreCertificate` computes validity, locks issuance, checks serial ID, signs, and stores. `processVerificationStatus` maps `SUCCESS`, `MISSING_KEYS`, `MISSING_CERTIFICATE`, and `INITIALIZE` to actions. Root initialization uses `HDDSKeyGenerator`, `KeyStorage`, `SelfSignedCertificate`, and `CertificateCodec`.

## Control Flow

Startup follows a truth table over key and certificate presence. Issuance follows inspect, choose approval mode, sign under lock, persist, build returned cert chain. Root CA initialization either imports an external certificate or generates keys and a self-signed CA certificate.

## State and Persistence Behavior

The server stores configuration, approver, profile, certificate store, component paths, and a lock. Durable state lives in key files, certificate files, and `CertificateStore`. Issued certificate storage is serialized by the lock.

## Dependencies and Integration Points

It integrates SCM metadata DB, `CertificateStore`, `SecurityConfig`, `CertificateCodec`, `KeyStorage`, `HDDSKeyGenerator`, `SelfSignedCertificate`, BouncyCastle CSR handling, and protobuf `NodeType`.

## Risks and Edge Cases

Missing keys with present certs and missing certs with present keys are fatal except external root import. `requestCertificate` checks exceptional CSR futures by calling `get`, but the following signing block is still reachable unless the future handling completes exceptionally first. Null `store` is tolerated for signing but disables persistence. Root CA external import logs errors rather than throwing, leaving success validation to the final status check.

## Test Signals

Tests should cover all verification statuses, external root CA import, self-signed root generation, subordinate initialize failure, manual approval rejection, CSR inspection failure, duplicate serial rejection, role-based duration selection, store reinitialization, and cert chain ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/DefaultCAServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/package-info.java

## Purpose

This package descriptor marks `org.apache.hadoop.hdds.security.x509.certificate.authority` as the certificate authority package.

## Important APIs, Types, and Functions

No executable APIs are defined here. Nearby classes provide CA server, store, approver, and profile integration.

## Control Flow

No runtime control flow.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It supports JavaDoc/package structure for the CA implementation used by SCM.

## Risks and Edge Cases

Documentation drift is the only material risk.

## Test Signals

Compile and JavaDoc/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/DefaultCAProfile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/DefaultCAProfile.java

## Purpose

`DefaultCAProfile` specializes `DefaultProfile` for CA certificate issuance. It permits CA basic constraints and adds certificate-signing usages.

## Important APIs, Types, and Functions

`isCA()` returns true. `getExtensionsMap()` inserts a validator for `Extension.basicConstraints`. `validateBasicExtensions` accepts only extensions whose parsed `BasicConstraints.isCA()` matches the profile CA status. `getKeyUsage()` includes digital signature, encipherment, key agreement, CRL signing, and certificate signing bits.

## Control Flow

The profile is consulted by `DefaultApprover` during CSR extension validation and when deciding which supported extensions to copy into a signed certificate.

## State and Persistence Behavior

No instance persistence is owned. It mutates `DefaultProfile.EXTENSIONS_MAP`, a static shared map, when `getExtensionsMap` is called.

## Dependencies and Integration Points

It depends on BouncyCastle `Extension`, `BasicConstraints`, `KeyUsage`, and the `PKIProfile` contract. It is used by `SCMCertificateClient` when initializing the primary SCM root CA.

## Risks and Edge Cases

The static extension map mutation is JVM-global and can make basic constraints appear supported for later non-CA default profiles. That is a subtle cross-profile coupling risk.

## Test Signals

Tests should validate CA basic constraints acceptance, non-CA constraints rejection, key usage bits, and isolation expectations when `DefaultCAProfile` and `DefaultProfile` are used in the same JVM.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/DefaultCAProfile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/DefaultProfile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/DefaultProfile.java

## Purpose

`DefaultProfile` is the default Ozone PKI profile for non-CA certificates. It defines supported general names, supported X.509 extensions, key-usage constraints, and validation routines used during CSR approval.

## Important APIs, Types, and Functions

Supported general names are DNS, IP address, and otherName. Supported extensions include key usage, SAN, authority key identifier, extended key usage, and logo type. Static validators enforce key usage subset, SAN non-critical status and allowed general names, and non-critical extended key usage limited to serverAuth/clientAuth. Public `PKIProfile` methods expose supported names/extensions, validation, key usage, RDN handling, and `isCA()` status.

## Control Flow

`DefaultApprover` calls `validateRDN` for subject entries and `validateExtension` for each CSR extension. `validateExtension` rejects unsupported OIDs and delegates to the extension-specific predicate in the map.

## State and Persistence Behavior

The profile holds per-instance sets for general name and extended-key-purpose membership. The extension validator map is static and protected, so subclass mutations affect all instances.

## Dependencies and Integration Points

It uses BouncyCastle ASN.1 X.509 classes, Apache Commons `DomainValidator`, hex decoding for IP addresses, and SLF4J logging. It supplies policy to the default CA approver.

## Risks and Edge Cases

IP validation assumes BouncyCastle string values begin with `#` and are hex encoded. DNS validation uses public domain validation, which may reject cluster-local hostnames. RDN validation currently allows everything. The static map design makes extension support mutable across profiles.

## Test Signals

Cover key-usage subset behavior, SAN critical rejection, DNS/IP/otherName validation, malformed IP hex, unsupported extension rejection, extended-key-usage critical rejection, and profile interaction with `DefaultCAProfile`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/DefaultProfile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/PKIProfile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/PKIProfile.java

## Purpose

`PKIProfile` defines the executable PKI policy contract used by Ozone certificate approval. It abstracts allowed subject names, extensions, key purposes, key usage, RDNs, and CA capability.

## Important APIs, Types, and Functions

The interface exposes `getGeneralNames`, `isSupportedGeneralName`, `validateGeneralName`, `getSupportedExtensions`, `isSupportedExtension`, `validateExtension`, `validateExtendedKeyUsage`, `getKeyUsage`, `getRDNs`, `isValidRDN`, `validateRDN`, `isCA`, and `getExtensionsMap`.

## Control Flow

`DefaultApprover.inspectCSR` and `sign` use this contract to validate CSR contents and decide which requested extensions can be copied into issued certificates.

## State and Persistence Behavior

No state or persistence is prescribed. Implementations can be immutable or dynamic; the default implementation uses in-memory sets/maps.

## Dependencies and Integration Points

It integrates BouncyCastle `GeneralName`, `Extension`, `KeyPurposeId`, `KeyUsage`, and `RDN` policy primitives with Ozone CA code.

## Risks and Edge Cases

Implementations control security policy; overly permissive RDN/general-name/extension validation directly affects issued certificate scope. `getExtensionsMap` exposes the validator map and can allow mutation depending on implementation.

## Test Signals

Profile implementation contract tests should verify all supported/unsupported extension paths, CA versus non-CA behavior, and invalid subject-name rejection under the concrete implementation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/PKIProfile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/package-info.java

## Purpose

This package descriptor documents Ozone certificate authority profile classes and describes PKI profiles as executable certificate policy.

## Important APIs, Types, and Functions

No executable APIs are present. The package contains `PKIProfile`, `DefaultProfile`, and `DefaultCAProfile`.

## Control Flow

No runtime control flow.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

The package integrates BouncyCastle X.509 policy primitives with the SCM CA approver.

## Risks and Edge Cases

The package text can drift from implemented profile behavior.

## Test Signals

Compile and JavaDoc generation are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/CertificateClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/CertificateClient.java

## Purpose

`CertificateClient` defines common certificate operations needed by Ozone components: local key/certificate access, trust-chain access, signature verification, CSR creation, reloadable TLS managers, renewal notifications, root CA rotation listeners, and initialization with recovery.

## Important APIs, Types, and Functions

Core methods expose component name, private/public keys, current certificate, certificate by serial ID, cert path, latest CA/root CA certs, all root/subordinate CA certs, trust chain, and signature verification. `configureCSRBuilder` creates a `CertificateSignRequest.Builder`. TLS methods return `ReloadingX509KeyManager`, `ReloadingX509TrustManager`, and `ClientTrustManager`. `registerNotificationReceiver`, `registerRootCARotationListener`, and `initWithRecovery` control runtime behavior. `InitResponse` has `SUCCESS`, `FAILURE`, and `GETCERT`.

## Control Flow

Implementations initialize local material, recover missing public keys when possible, request certificates when needed, and notify listeners after renewals or CA rotation.

## State and Persistence Behavior

The interface defines local filesystem-backed key/cert behavior but leaves storage details to implementations. `assertValidKeysAndCertificate` validates that all three core materials are present.

## Dependencies and Integration Points

It integrates Ozone security exceptions, reloadable SSL managers, SCM client trust manager, `CertificateSignRequest`, and Java crypto/certificate APIs.

## Risks and Edge Cases

Callers must tolerate null returns for missing local material. Listener registration assumes implementation lifecycle has created pollers/managers as needed. `assertValidKeysAndCertificate` wraps many failure modes into one Ozone security result code.

## Test Signals

Interface-level tests should exercise init response handling through concrete classes, missing material assertions, trust-chain construction, listener callbacks, and signature verification behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/CertificateClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/CertificateNotification.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/CertificateNotification.java

## Purpose

`CertificateNotification` is a callback interface for consumers that need to react when a `CertificateClient` renews its certificate.

## Important APIs, Types, and Functions

`notifyCertificateRenewed(CertificateClient certClient, String oldCertId, String newCertId)` is the single method.

## Control Flow

`DefaultCertificateClient` invokes registered receivers after resetting/reloading local certificate state during renewal.

## State and Persistence Behavior

No state or persistence is defined by this interface. Implementations such as reloadable key/trust managers update their own in-memory state.

## Dependencies and Integration Points

It integrates certificate-client renewal events with TLS manager reloads and any service-specific consumers.

## Risks and Edge Cases

Callbacks run synchronously inside notification iteration in the default client. Slow or throwing receivers can affect renewal follow-up unless callers guard their implementations.

## Test Signals

Register fake receivers and assert they receive old/new IDs during `reloadKeyAndCertificate`; test multiple receivers and receiver failure behavior in the concrete notifier.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/CertificateNotification.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/DNCertificateClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/DNCertificateClient.java

## Purpose

`DNCertificateClient` is the datanode-specific certificate client. It supplies datanode identity in CSRs and calls the SCM security protocol endpoint for datanode certificate chains.

## Important APIs, Types, and Functions

The constructor passes component `dn`, datanode thread prefix, cert ID save callback, and shutdown callback to `DefaultCertificateClient`. `configureCSRBuilder` sets `CA=false`, key pair from local keys, current security config, and subject as current short user plus local canonical host. `sign` calls `SCMSecurityProtocolClientSideTranslatorPB.getDataNodeCertificateChain(dnProto, csrPem)`.

## Control Flow

Initialization and renewal are inherited. When a cert is needed, the subclass builds a DN CSR and delegates signing to SCM using the datanode protobuf identity.

## State and Persistence Behavior

It adds immutable datanode details. Key/cert persistence, renewal directory swaps, and cert ID persistence callbacks are inherited.

## Dependencies and Integration Points

It integrates `DatanodeDetails`, UGI, local hostname resolution, `CertificateSignRequest`, SCM security protocol, and default certificate-client storage.

## Risks and Edge Cases

Hostname or current-user lookup failures abort CSR creation. The subject uses local runtime hostname, which must match expectations for certificate consumers. `new KeyPair(getPublicKey(), getPrivateKey())` assumes both keys are already available.

## Test Signals

Tests should cover CSR subject construction, CA flag false, key pair propagation, SCM RPC invocation with datanode details, hostname/UGI failure wrapping, and inherited init/renewal behavior for DN component paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/DNCertificateClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/DefaultCertificateClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/DefaultCertificateClient.java

## Purpose

`DefaultCertificateClient` is the base implementation for Ozone component certificate clients. It manages local key and certificate loading, certificate maps, CA/root CA sets, initialization recovery, CSR signing/storage, signature helpers, reloadable TLS managers, scheduled renewal, root CA rotation-triggered renewal, and atomic key/cert directory replacement.

## Important APIs, Types, and Functions

Important state includes `KeyStorage`, cached private/public keys, current `CertPath`, `certificateMap`, root/subordinate CA sets, current cert/CA/root IDs, SCM security client, notification receivers, renewal executor, and `RootCaRotationPoller`. Public APIs implement `CertificateClient`. `init` computes an `InitCase` bitmask over private key, public key, and certificate. `handleCase` maps eight material states to success, failure, or get-cert with recovery. `recoverStateIfNeeded` requests and stores a certificate when needed. `storeCertificate` writes PEM and optionally updates caches. `renewAndStoreKeyAndCertificate` creates new directories, generates new keys, signs a new cert, atomically swaps directories, and rolls back on failure. `CertificateRenewerService` performs scheduled or forced renewal.

## Control Flow

Certificate loading scans the component certificate directory and classifies files by CA filename prefix. Initialization reads local material, recovers public key from certificate or RSA private key when possible, validates key pairs by signing a challenge, and obtains a certificate from SCM when required. Renewal waits until the grace period or forced root-CA rotation, performs disk swaps, persists the new serial ID through callback, reloads caches, notifies receivers, and deletes backup dirs.

## State and Persistence Behavior

State is split between synchronized in-memory caches and filesystem persistence under configured key/certificate locations. Renewal uses `_new` and `_backup` directories plus `ATOMIC_MOVE` to limit partial-update exposure. The caller-supplied cert ID save callback persists the active serial ID outside this class, typically in a VERSION file.

## Dependencies and Integration Points

It integrates `SecurityConfig`, `KeyStorage`, `HDDSKeyGenerator`, `CertificateCodec`, SCM security protocol RPCs, reloadable key/trust managers, `ClientTrustManager`, root CA poller, Apache Commons `FileUtils` and `RandomStringUtils`, Java crypto signatures, and Ozone security utilities.

## Risks and Edge Cases

Several methods are synchronized, but renewal synchronizes on `DefaultCertificateClient.class`, serializing all clients in the JVM. `registerRootCARotationListener` assumes the poller exists when auto rotation is enabled; calling it before `startRootCaRotationPoller` can null-deref. `getRootCACertificate` assumes the ID exists in `certificateMap`. Directory swaps can still require manual recovery if rollback fails. `loadAllCertificates` can start background services during cache refresh, so getters may have side effects.

## Test Signals

High-value tests cover all eight init cases, public key recovery from cert/private key, invalid key-pair detection, cert fetch/store, trust-chain fallback, renewal success and every rollback branch, cert ID callback failures, root CA forced renewal, notification receiver updates, close behavior, and cache reload after filesystem changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/DefaultCertificateClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/RootCaRotationPoller.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/RootCaRotationPoller.java

## Purpose

`RootCaRotationPoller` periodically asks SCM for all root CA certificates and triggers registered processors when SCM knows root CAs that the client does not.

## Important APIs, Types, and Functions

The constructor captures polling interval, initial known root cert set, SCM security client, thread name prefix, processor list, scheduled executor, and an atomic renewal-error flag. `pollRootCas` fetches PEM roots, converts to X.509, computes unknown certs, logs IDs, runs all processors with `CompletableFuture.allOf`, and updates `knownRootCerts` only if processors complete successfully and no renewal error was signaled. `addRootCARotationProcessor`, `run`, `close`, and `setCertificateRenewalError` control lifecycle.

## Control Flow

`run` schedules `pollRootCas` at fixed rate with zero initial delay. Each poll is a fetch/compare/notify/update cycle. Processors receive the full SCM root list, not just the new certificates.

## State and Persistence Behavior

State is in-memory only: known root certs and renewal-error flag. Persistence of new root certificates is delegated to processors such as `DefaultCertificateClient` renewal handlers.

## Dependencies and Integration Points

It integrates `SCMSecurityProtocolClientSideTranslatorPB.getAllRootCaCertificates`, `OzoneSecurityUtil.convertToX509`, scheduled executors, and certificate-client rotation processors.

## Risks and Edge Cases

The processor list is an unsynchronized `ArrayList`; adding processors while polling can race. `pollingInterval.getSeconds()` truncates sub-second durations. Exceptions inside asynchronous processors are handled by `whenComplete`, but update happens asynchronously after `pollRootCas` returns.

## Test Signals

Test no-op when cert sets match, processor invocation for new roots, known-set update only after successful processors, renewal-error suppression, SCM fetch IOException handling, close shutdown, and concurrent listener registration behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/RootCaRotationPoller.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/SCMCertificateClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/SCMCertificateClient.java

## Purpose

`SCMCertificateClient` is the SCM-specific certificate client used to bootstrap and maintain SCM subordinate CA material. It builds CA CSRs, obtains sub-CA certificates either from a leader/root CA or local primary root CA, refreshes CA certificates, and initializes a root CA server for primary SCM bootstrapping.

## Important APIs, Types, and Functions

`COMPONENT_NAME` points to the SCM sub-CA storage path. Constructors accept SCM ID, cluster ID, cert ID, hostname, primary-SCM flag, and save callback. `configureCSRBuilder` sets subject from `SCM_SUB_CA_PREFIX + scmHostname`, SCM/cluster IDs, `CA=true`, and local key pair. `sign` is unsupported because SCM uses custom paths. Overridden `signAndStoreCertificate` calls `getSCMCertChain(..., true)` and stores subordinate/root material. `refreshCACertificates` runs `RefreshCACertificates`, which fetches leader root CAs and stores unknown certs. `recoverStateIfNeeded` chooses primary self-signed or root-signed certificate acquisition. `initializeRootCertificateServer` creates `DefaultCAServer`.

## Control Flow

On `GETCERT`, non-primary SCM requests a chain from SCM security RPC; primary SCM creates/initializes a root CA server, signs its own sub-CA CSR through that server, stores root and sub-CA material, persists the serial ID, and leaves renewer service disabled.

## State and Persistence Behavior

It inherits filesystem key/cert caches and adds SCM ID, cluster ID, hostname, primary flag, refresh executor, and save callback. It persists sub-CA certificates both via `storeCertificate` and a direct write to the component certificate filename expected by sub-CA server code.

## Dependencies and Integration Points

It integrates SCM security RPC, `DefaultCAServer`, `DefaultCAProfile`, `CertificateStore`, `CertificateCodec`, Ozone constants, `HddsUtils.threadNamePrefix`, and SCM node protobufs.

## Risks and Edge Cases

`signAndStoreCertificate` catches `Throwable` and rethrows runtime errors. `getPrimarySCMSelfSignedCert` catches `InterruptedException` with other exceptions and always interrupts the thread, even for non-interrupt failures. CA storage uses `CAType.SUBORDINATE` for root PEMs in some SCM flows because SCM treats root CA as CA cert, which can confuse naming expectations.

## Test Signals

Cover primary and non-primary bootstrap, CSR fields with CA=true, unsupported `sign`, root CA server initialization, cert ID callback, refresh of newly discovered leader roots, no-op refresh when unchanged, executor close, and storage filenames for sub-CA/root material.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/SCMCertificateClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/package-info.java

## Purpose

This package descriptor identifies the certificate client package for creating and using certificates.

## Important APIs, Types, and Functions

No executable APIs are present. The package contains certificate-client interfaces, default implementation, DN/SCM clients, notification hooks, and root CA rotation polling.

## Control Flow

No runtime control flow.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

The package integrates component key/cert filesystem state with SCM certificate services and reloadable TLS managers.

## Risks and Edge Cases

Documentation can drift from package responsibilities.

## Test Signals

Compile and JavaDoc/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/package-info.java

## Purpose

This package descriptor documents common routines used for maintaining X.509 certificates.

## Important APIs, Types, and Functions

No executable APIs are present. The package includes certificate metadata, authority, client, and utility subpackages.

## Control Flow

No runtime control flow.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It anchors the package namespace used by Ozone certificate infrastructure.

## Risks and Edge Cases

Documentation drift only.

## Test Signals

Compile and JavaDoc/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/CertificateSignRequest.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/CertificateSignRequest.java

## Purpose

`CertificateSignRequest` builds, encodes, and decodes PKCS#10 CSRs for Ozone components. Its builder assembles subject identity, key usage, basic constraints, and subject alternative names before signing the CSR with the component private key.

## Important APIs, Types, and Functions

Static DN helpers expose `CN=%s,OU=%s,O=%s` and serial-number variants. `getPkcs9ExtRequest` and `getPkcs9Extensions` extract CSR extension requests. `toEncodedFormat` writes PEM `CERTIFICATE REQUEST`. `generateCSR` builds a `JcaPKCS10CertificationRequestBuilder` and signs with configured algorithm/provider. `getCertificationRequest` parses PEM input. Builder methods set config, key, subject, cluster/SCM IDs, digital usage flags, CA flag, DNS/IP/service SANs, and host inet addresses.

## Control Flow

Callers configure the builder, `build` validates required key and subject, creates extensions, and returns an immutable request object. Encoding calls `generateCSR`, which adds extension attributes only when present and signs with the private key.

## State and Persistence Behavior

The object holds key pair, config, extensions, subject, cluster ID, and SCM ID in memory. It does not persist files; PEM output is passed over RPC or written by callers.

## Dependencies and Integration Points

It depends on BouncyCastle CSR/ASN.1 APIs, Apache Commons validators, `SecurityConfig`, Ozone certificate exceptions, and `HddsServerUtil.getValidInetsForCurrentHost`. It is used by DN/SCM/default certificate clients and `DefaultApprover`.

## Risks and Edge Cases

Only key and subject are required in `build`; config, SCM ID, and cluster ID can be null until later failures. `getPkcs9Extensions` assumes the extension set exists and has a first element. Domain validation may reject local hostnames. OtherName uses a fixed Microsoft OID.

## Test Signals

Test CSR PEM round-trip, subject/DN formats, key usage flags for signature/encryption/CA, SAN DNS/IP/otherName encoding, missing extension request handling, malformed PEM, missing required builder fields, and generated CSR signature verification.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/CertificateSignRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/SelfSignedCertificate.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/SelfSignedCertificate.java

## Purpose

`SelfSignedCertificate` builds a self-signed X.509 certificate, primarily for bootstrapping an Ozone root CA when no external CA certificate is configured.

## Important APIs, Types, and Functions

`newBuilder` returns the nested builder. `generateCertificate` converts the public key to `SubjectPublicKeyInfo`, creates a `ContentSigner`, chooses the serial ID from CA serial or monotonic time, builds a subject/issuer name with serial number, creates `X509v3CertificateBuilder`, and adds CA basic constraints, key usage, and SAN extensions when `makeCA` was used. Builder methods set subject, SCM ID, cluster ID, validity dates, key pair, config, CA serial, and SANs from DNS/IP/current host.

## Control Flow

Builder validation requires key, nonblank subject/cluster/SCM IDs, begin date before end date, and duration no longer than configured max. `build` creates the certificate object and delegates to BouncyCastle signing/conversion.

## State and Persistence Behavior

No files are written here. The generated `X509Certificate` is returned to callers such as `DefaultCAServer`, which writes it through `CertificateCodec`.

## Dependencies and Integration Points

It integrates `SecurityConfig`, BouncyCastle X.509 builders, `CertificateSignRequest` DN format, Ozone certificate exceptions, domain/inet utilities, and Hadoop `Time.monotonicNow`.

## Risks and Edge Cases

When no CA serial ID is supplied, the serial comes from monotonic time and is not globally durable. SANs are only added in the CA-serial path. `beginDate`/`endDate` are dereferenced without explicit null checks, so missing dates produce null-pointer failures.

## Test Signals

Cover successful CA certificate creation, max-duration rejection, invalid date order, missing fields, SAN encoding, fixed serial ID, self-signed issuer/subject equality, basic constraints/key usage presence, and generated certificate verification with its public key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/SelfSignedCertificate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/package-info.java

## Purpose

This package descriptor identifies helper classes for certificate utilities.

## Important APIs, Types, and Functions

No executable APIs are present. The package includes CSR, self-signed certificate, and certificate codec helpers.

## Control Flow

No runtime control flow.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

The package supports certificate authority and certificate client flows.

## Risks and Edge Cases

Documentation drift only.

## Test Signals

Compile and JavaDoc/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/OzoneAdmins.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/OzoneAdmins.java

## Purpose

`OzoneAdmins` models configured Ozone administrator users and groups and provides authorization helpers for superuser, read-only admin, and S3 admin checks.

## Important APIs, Types, and Functions

Constructors create immutable username/group sets. Static factories read standard Ozone config keys for admins, read-only admins, and S3 admins. `isAdmin(UserGroupInformation)` checks wildcard, short username membership, and group intersection. `checkAdminUserPrivilege` throws `AccessControlException` when a non-admin attempts an admin operation. S3 helpers provide fallback from S3-specific config to general admin config and include the current service user.

## Control Flow

Callers build an instance from configuration and call `isAdmin` or `checkAdminUserPrivilege` during authorization. Setter `setAdminUsernames` can refresh the volatile username set while groups remain constructor-defined.

## State and Persistence Behavior

State is in-memory only: volatile admin usernames and immutable admin groups. Persistent source is `OzoneConfiguration`.

## Dependencies and Integration Points

It integrates Ozone config keys, Hadoop UGI, Hadoop `StringUtils`, Guava `Sets.intersection`, and access-control exception handling in server-side authorization.

## Risks and Edge Cases

The starter/current user is automatically added in several paths, which is intentional but security-sensitive. Group updates require a new object because only usernames have a setter in common usage. `getS3Admins` suppresses IOException by returning an empty user set before group evaluation.

## Test Signals

Test wildcard admin, short-name matching, group matching, starter user insertion, read-only config parsing, S3 fallback behavior, IOException fallback, setter refresh, and access exception messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/OzoneAdmins.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/OzoneBlacklist.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/OzoneBlacklist.java

## Purpose

`OzoneBlacklist` models configured blacklisted Ozone users and groups and provides denial checks for normal and read-only blacklist settings.

## Important APIs, Types, and Functions

Constructors create unmodifiable username/group sets. Static factories read `OZONE_BLACKLIST_USERS`, `OZONE_BLACKLIST_GROUPS`, `OZONE_READ_BLACKLIST_USERS`, and `OZONE_READ_BLACKLIST_GROUPS`. `isBlacklisted(UserGroupInformation)` checks short username and group intersection. `checkBlacklist` throws `AccessControlException` for blacklisted users. Setters allow replacing volatile user and group sets.

## Control Flow

Authorization code constructs a blacklist from configuration and calls `checkBlacklist` before allowing access. Collection parsing helpers support both full configuration and raw config-value strings.

## State and Persistence Behavior

State is in-memory only, with volatile user/group sets refreshed by setters. Persistent source is Ozone configuration.

## Dependencies and Integration Points

It mirrors `OzoneAdmins` behavior and integrates with Hadoop UGI, Guava set intersection, Ozone config keys, and server authorization code.

## Risks and Edge Cases

There is no wildcard handling; only explicit usernames/groups deny access. Group membership comparisons depend on UGI group freshness. Empty/null config yields empty immutable sets and no denial.

## Test Signals

Test user denial, group denial, nonblacklisted pass-through, null UGI pass-through, read blacklist config parsing, raw-value parsing, runtime setter replacement, and access exception text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/OzoneBlacklist.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/OzoneProtocolMessageDispatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/OzoneProtocolMessageDispatcher.java

## Purpose

`OzoneProtocolMessageDispatcher` is a generic server-side RPC helper that wraps request handling with trace span import/creation, request/response logging, and protocol message metrics.

## Important APIs, Types, and Functions

The class is generic over request, response, and enum request type. Constructors accept service name, `ProtocolMessageMetrics`, logger, and optional request/response preprocessors. `processRequest` takes a request, checked method call, type, and trace ID. `escapeNewLines` is the default log preprocessor.

## Control Flow

`processRequest` imports a trace span, enters scope, logs the request at trace or debug level, measures the method call with `protocolMessageMetrics.measure(type)`, logs the response at trace level, returns the response, and always ends the span in `finally`.

## State and Persistence Behavior

It holds immutable logging/metrics/preprocessor dependencies. No persistence.

## Dependencies and Integration Points

It integrates server-side translators with OpenTelemetry `Span`/`Scope`, `TracingUtil`, `ProtocolMessageMetrics`, Ratis `CheckedFunction`, and protobuf `ServiceException`.

## Risks and Edge Cases

Default preprocessing calls `toString()` and regex replacement, which can be expensive or leak sensitive data at trace level. If a preprocessor throws, request handling fails before the method call. Metrics measurement depends on `measure(type)` returning a closeable even for exceptions.

## Test Signals

Test successful request flow, method exception propagation, span end on exception, metrics close on exception, trace/debug logging branches with custom preprocessors, and newline escaping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/OzoneProtocolMessageDispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/ServerUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/ServerUtils.java

## Purpose

`ServerUtils` provides shared HDDS/Ozone server helpers for configuration sanitization, RPC listen address updates, metadata/DB directory resolution and permissions, remote user lookup, and default Ratis directory selection with upgrade compatibility.

## Important APIs, Types, and Functions

`sanitizeUserArgs` clamps a value to min/max factors of a base value. `updateRPCListenAddress` and `updateListenAddress` update `OzoneConfiguration` after binding. `getScmDbDir`, `getDBPath`, and `getOzoneMetaDirPath` resolve metadata directories. `getDirectoryFromConfig` enforces single directory, creates it, and sets POSIX permissions. `getPermissions`, `getSymbolicPermission`, and `setDataDirectoryPermissions` handle configured modes. `getRemoteUserName` wraps Hadoop IPC server state. `getDefaultRatisDirectory` and `getDefaultRatisSnapshotDirectory` derive component-specific paths, checking legacy SCM/shared Ratis locations through `findExistingRatisDirectory`.

## Control Flow

Most methods validate config, create directories when missing, set permissions, and return concrete paths. Ratis directory fallback first checks old non-empty directories to preserve upgrade behavior, otherwise returns a new component-specific path under `ozone.metadata.dirs`.

## State and Persistence Behavior

No class state. It creates directories and changes POSIX permissions on disk, and mutates `OzoneConfiguration` for listen addresses and metadata path setters.

## Dependencies and Integration Points

It depends on HDDS/Ozone/SCM/Recon config keys, Hadoop IPC `Server`, Hadoop filesystem permissions, Java NIO file APIs, protobuf `NodeType`, and logging.

## Risks and Edge Cases

`getDirectoryFromConfig` rejects multiple metadata dirs for components that do not support them. POSIX permission APIs can fail on non-POSIX filesystems. `setDataDirectoryPermissions` logs warnings instead of failing startup. `getComponentName` throws for new enum values until updated.

## Test Signals

Test clamp boundaries, listen-address mutation, missing/multiple directory config, octal and symbolic permission conversion, non-writable permission skip, fallback to metadata dirs, legacy Ratis path detection, snapshot path naming, and remote user null handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/ServerUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/ServiceRuntimeInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/ServiceRuntimeInfo.java

## Purpose

`ServiceRuntimeInfo` defines common runtime metadata exposed by Ozone service components without using an MXBean/MBean suffix that can confuse JMX property discovery.

## Important APIs, Types, and Functions

Methods are `getNamespace()` with default empty string, `getVersion()`, `getSoftwareVersion()`, and `getStartedTimeInMillis()`.

## Control Flow

There is no implementation flow beyond the default namespace. Service-specific MXBean interfaces extend this interface and implementations provide version/start-time values.

## State and Persistence Behavior

No state or persistence is defined.

## Dependencies and Integration Points

It integrates service implementations with JMX/runtime reporting and is implemented by `ServiceRuntimeInfoImpl`.

## Risks and Edge Cases

Implementations must call their start-time setter or return a meaningful value. Naming convention is part of the JMX behavior contract.

## Test Signals

Test concrete MXBean exposure, default namespace behavior, and start-time/version values from implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/ServiceRuntimeInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/ServiceRuntimeInfoImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/ServiceRuntimeInfoImpl.java

## Purpose

`ServiceRuntimeInfoImpl` is a base implementation of `ServiceRuntimeInfo` that reports Hadoop/Ozone version strings and service start time.

## Important APIs, Types, and Functions

The constructor accepts `VersionInfo`. `getVersion()` returns version plus revision, `getSoftwareVersion()` returns version only, `getStartedTimeInMillis()` returns the stored start time, and `setStartTime()` sets it to `System.currentTimeMillis()`.

## Control Flow

Services instantiate with version info and call `setStartTime` during startup. JMX/runtime queries read the stored values.

## State and Persistence Behavior

It stores in-memory start time and immutable version info. No persistence.

## Dependencies and Integration Points

It depends on `org.apache.hadoop.hdds.utils.VersionInfo` and is intended as a superclass for service runtime/JMX implementations.

## Risks and Edge Cases

If `setStartTime` is never called, start time remains zero. The constructor is protected, so only subclasses can instantiate it.

## Test Signals

Test formatted version string, software version string, start time initially zero, and start time update within expected wall-clock range.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/ServiceRuntimeInfoImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/YamlUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/YamlUtils.java

## Purpose

`YamlUtils` centralizes safe-ish YAML loading and atomic YAML dumping for HDDS/Ozone server code.

## Important APIs, Types, and Functions

Static `LOADER` is created by `getYamlForLoad`, which configures SnakeYAML `LoaderOptions` with a `TagInspector` that allows tags whose class names start with `org.apache.hadoop.hdds.` or `org.apache.hadoop.ozone.`. `loadAs(InputStream, Class<? super T>)` delegates to the shared loader. `dump(Yaml, Object, File, Logger)` writes UTF-8 YAML through `AtomicFileOutputStream` and logs/rethrows IO failures.

## Control Flow

Load callers use the preconfigured loader. Dump callers pass their chosen `Yaml` instance and data; the method writes atomically and closes streams with try-with-resources.

## State and Persistence Behavior

The shared loader is static. Dumping persists YAML to a target file atomically to avoid partial writes.

## Dependencies and Integration Points

It integrates SnakeYAML, Ratis atomic file output streams, UTF-8 encoding, and server loggers. It is used by code that reads/writes Ozone YAML state or configuration-like files.

## Risks and Edge Cases

Allowed tag prefixes are broad within Ozone/HDDS packages; unsafe classes under those packages would be loadable. `loadAs` does not close the input stream. Dump safety depends on caller-provided `Yaml` configuration.

## Test Signals

Test allowed and rejected YAML tags, typed load behavior, atomic dump content, exception logging/rethrow on IO failure, and UTF-8 output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/YamlUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/Event.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/Event.java

## Purpose

`Event<PAYLOAD>` identifies an asynchronous event type in the HDDS server event framework.

## Important APIs, Types, and Functions

`getPayloadType()` returns the Java class of the event payload. `getName()` returns a human-readable name for thread names and monitoring.

## Control Flow

The event queue uses event identity and payload type metadata to route payloads to compatible handlers and executors.

## State and Persistence Behavior

The interface defines no state or persistence. Implementations are usually enum-like constants or small descriptor objects.

## Dependencies and Integration Points

It integrates with `EventQueue`, `EventHandler`, `EventPublisher`, and `EventExecutor` in the same server event package.

## Risks and Edge Cases

Incorrect payload type declarations can cause handler cast errors or missed validation. Non-unique names can make metrics/thread diagnostics ambiguous.

## Test Signals

Test event registration with matching/mismatched payload types and monitoring names in queue/executor diagnostics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/Event.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventExecutor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventExecutor.java

## Purpose

`EventExecutor<PAYLOAD>` defines how an event handler is invoked and monitored by the HDDS event queue. Executors provide thread separation while guaranteeing that a single handler is not executed concurrently by multiple threads.

## Important APIs, Types, and Functions

`onMessage(EventHandler<PAYLOAD>, PAYLOAD, EventPublisher)` schedules or invokes handler processing. Metrics methods expose failed, successful, queued, scheduled, dropped, long-wait, and long-execution event counts. `getName()` returns a human-readable executor name. It extends `AutoCloseable`.

## Control Flow

`EventQueue` delegates event delivery to an executor, which decides synchronous/asynchronous scheduling, failure accounting, and downstream publishing through the supplied publisher.

## State and Persistence Behavior

The interface defines metric state but not storage. Implementations keep counters and queues in memory; no persistence is implied.

## Dependencies and Integration Points

It integrates event handlers and publishers with monitoring and lifecycle cleanup in the server event framework.

## Risks and Edge Cases

The non-concurrent-per-handler guarantee is documented here and must be enforced by implementations. Default dropped/long-wait/long-execution methods return zero, so older implementations may hide those metrics.

## Test Signals

Executor implementation tests should cover serialization per handler, success/failure counters, queued/scheduled counters, close behavior, dropped-event accounting, long wait/execution thresholds, and publisher use by handlers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventExecutor.java -->
