# subset-b-008025 Research

This grouped report covers the requested Apache Ozone HDDS framework test sources. Each section is source-tree-aligned and bounded by reconciliation markers so it can be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestDefaultCertificateClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestDefaultCertificateClient.java

Purpose: exercises `DefaultCertificateClient` behavior through the concrete `DNCertificateClient`, covering key persistence, certificate storage/loading, signature generation/verification, certificate renewal, expiry grace calculation, and shutdown of background renewal resources.

Important APIs/types/functions: `DNCertificateClient`, `DefaultCertificateClient`, `CertificateClient.InitResponse`, `KeyStorage`, `HDDSKeyGenerator`, `SecurityConfig`, `CertificateCodec`, `SCMSecurityProtocolClientSideTranslatorPB`, `CertificateSignRequest`, `SCMGetCertResponseProto`, `CAType`, `getPrivateKey`, `getPublicKey`, `storeCertificate`, `getCertificate`, `getAllCaCerts`, `getAllRootCaCerts`, `signData`, `verifySignature`, `renewAndStoreKeyAndCertificate`, and `close`.

Control flow: `setUp` creates a temporary metadata directory, configures retry and metadata settings, mocks SCM security, initializes key storage and the DN certificate client, and generates a test certificate. Tests then mutate files under the configured key/certificate directories, reinstantiate clients to verify reload-on-init, mock SCM certificate-chain responses for renewal, and assert expected client results. The renewal test verifies that old keys/certificates are backed up, temporary new-key/new-cert directories are cleaned, and a second renewal tolerates stale temporary material.

State and persistence behavior: the test suite is strongly filesystem-oriented. It deletes and rewrites private/public key files, writes regular certificates plus root/subordinate CA files, reads certificates by serial number, validates metadata directories and backup directories, and checks that the certificate renewer thread is removed after `close`. Certificate state is cached in the client but must be reconstructible from disk after re-instantiation.

Dependencies and integration points: integrates with Hadoop/Ozone configuration keys, SCM security protocol protobufs, certificate codecs, key storage, generated JCA `KeyPair`/`X509Certificate` objects, Bouncy/JCA signature verification, `GenericTestUtils.LogCapturer`, Mockito, and Apache Commons IO cleanup helpers.

Risks: tests depend on real filesystem cleanup and active thread enumeration, so leaks or slow renewal executor shutdown can be flaky. Generated certificates use test utilities with short validity windows; clock-sensitive expiry assertions require tolerances. The init failure checks depend on log text, which is useful but brittle if diagnostics are reworded.

Test signals: asserts null/missing key behavior, successful persisted key reads, PEM certificate round trips, signature failure without a private key, valid and invalid signature verification, certificate map reloads, CA classification counts, `FAILURE` responses on mismatched key/cert material, expiry grace period clamping, renewal serial-number changes, backup cleanup, and renewer thread shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestDefaultCertificateClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestDnCertificateClientInit.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestDnCertificateClientInit.java

Purpose: parameterized initialization matrix for `DNCertificateClient`, validating how datanode certificate-client startup reacts to combinations of private key, public key, and certificate presence.

Important APIs/types/functions: `DNCertificateClient`, `CertificateClient.InitResponse`, `SUCCESS`, `GETCERT`, `FAILURE`, `KeyStorage.storePrivateKey`, `KeyStorage.storePublicKey`, `CertificateCodec.writeCertificate`, `OzoneSecurityUtil.checkIfFileExist`, and `SecurityConfig` key/certificate path helpers.

Control flow: `parameters()` supplies combinations of present/missing private key, public key, and certificate with expected init responses. `setUp` builds a fresh temp metadata tree, generates one RSA key pair and matching X.509 certificate, and constructs the DN client. Each parameterized test writes or deletes key/certificate files to match the case, invokes `dnCertificateClient.init()`, and validates both response and key-file recovery behavior for `GETCERT`.

State and persistence behavior: all state is persisted under the temporary HDDS metadata directory. Missing public keys may be regenerated from private-key material during `GETCERT` flows, while missing private keys or incompatible certificate states produce failure. The certificate file is intentionally deleted or written through `CertificateCodec`.

Dependencies and integration points: uses `OzoneConfiguration`, `SecurityConfig`, `HDDSKeyGenerator`, Hadoop test key/cert utilities, Apache Commons IO deletion, JUnit parameterization, and Ozone security utilities.

Risks: the test is compact but sensitive to exact init-state semantics. If init later performs additional repair or validation, expected responses in the matrix must change together with file-existence assertions.

Test signals: asserts the correct `InitResponse` for every matrix row and verifies that `GETCERT` paths leave private and public key files on disk.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestDnCertificateClientInit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestRootCaRotationPoller.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestRootCaRotationPoller.java

Purpose: validates client-side polling for root CA rotation, ensuring processors are invoked only when SCM returns previously unknown root CA certificates and that retry behavior works after renewal-related failures.

Important APIs/types/functions: `RootCaRotationPoller`, `SCMSecurityProtocolClientSideTranslatorPB.getAllRootCaCertificates`, `CertificateCodec.getPEMEncodedString`, `SecurityConfig`, `SelfSignedCertificate`, `RootCARotationProcessor`, `pollRootCas`, `addRootCARotationProcessor`, and `setCertificateRenewalError`.

Control flow: setup initializes a mocked SCM security client, a polling interval, and log capture. The first test returns only the already-known root CA and verifies a registered processor is not called. The second test returns a known plus new root CA and checks the processor observes the new set. The retry test has the processor mark renewal error on first processing, then invokes polling again and checks log output for failure followed by success.

State and persistence behavior: poller state is in memory: known certificate set, processor list, and error flags. Certificates are generated as self-signed root CAs and serialized through PEM strings returned by the mocked SCM client. No disk state is created by these tests.

Dependencies and integration points: integrates mocked SCM security RPC, certificate serialization, self-signed root certificate generation, async future/timeout behavior, `AtomicBoolean`, and log capture.

Risks: polling and processor invocation may be asynchronous depending on implementation; timeout assertions can be sensitive to executor timing. Log-message assertions are brittle but capture important retry semantics.

Test signals: verifies no callback for unchanged roots, callback for new roots, processor certificate-set size, caught renewal error logging, and successful subsequent processing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestRootCaRotationPoller.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestCertificateCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestCertificateCodec.java

Purpose: tests certificate encoding/decoding and filesystem round trips in `CertificateCodec`, including PEM strings, certificate paths, prepending certificates, and default component certificate files.

Important APIs/types/functions: `CertificateCodec`, `getPEMEncodedString`, `getX509Certificate`, `getCertPathFromPemEncodedString`, `prependCertToCertPath`, `writeCertificate`, `getTargetCert`, `getCertPath`, `SelfSignedCertificate`, `SecurityConfig`, and Java `CertificateFactory`/`CertPath`.

Control flow: a temp metadata directory is configured for each test. Tests generate self-signed certificates, serialize them to PEM, parse them back, build and decode `CertPath` instances, prepend one cert ahead of another, write PEM and default certificate files, force-rewrite a named certificate, and read multi-cert paths back in order.

State and persistence behavior: files are written under either a supplied base path or the codec's configured component directory. The tests validate content by serial number and object equality, and they check that repeated writes to the same filename are supported.

Dependencies and integration points: uses Ozone `SecurityConfig`, certificate generation utilities, Guava immutable lists for cert paths, JCA certificate factories, and JUnit temp directories.

Risks: certificate path ordering matters; regressions in PEM boundary formatting, newline handling, or overwrite semantics can break interoperability with external tools and other Ozone certificate clients.

Test signals: asserts PEM begin/end markers, X.509 equality after parse, `CertPath` order after encode/decode, prepended certificate ordering, non-null loaded certs, matching serial numbers, and multi-certificate reread order.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestCertificateCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestCertificateSignRequest.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestCertificateSignRequest.java

Purpose: validates `CertificateSignRequest` builder output, CSR subject formatting, public key embedding, extensions, SAN handling, service-ID encoding, invalid argument rejection, and CSR PEM serialization.

Important APIs/types/functions: `CertificateSignRequest.Builder`, `build`, `generateCSR`, `getEncodedString`, `getCertificationRequest`, `getDistinguishedNameFormat`, `getPkcs9Extensions`, `SecurityConfig`, `HDDSKeyGenerator`, Bouncy Castle `PKCS10CertificationRequest`, `Extensions`, `Extension.keyUsage`, `Extension.subjectAlternativeName`, and `JcaContentVerifierProviderBuilder`.

Control flow: tests build CSRs from generated key pairs with subject/SCM/cluster/service identifiers and optional IP/DNS SAN entries. They inspect CSR subject, embedded `SubjectPublicKeyInfo`, extension attributes, criticality, and signature validity. Invalid-parameter tests omit required fields or use invalid dates/subjects, assert exceptions, then complete a valid request. Serialization writes a CSR to PEM and reconstructs it for equality.

State and persistence behavior: no durable store is used beyond transient temp metadata configuration. CSR state is immutable output from the builder and serialized/deserialized through PEM strings.

Dependencies and integration points: integrates Ozone security config, HDDS key generation, Bouncy Castle CSR and ASN.1 extension parsing, and Java key-pair verification.

Risks: distinguished-name ordering and escaping depend on X.500 formatting rules. Extension criticality, SAN representation, and service-ID OID encoding are interoperability-sensitive with SCM certificate signing.

Test signals: asserts subject DN equality, public-key equality, exactly one PKCS#9 extension attribute, critical key-usage/SAN extensions, absent SAN when not configured, valid CSR signatures, expected builder exceptions, service-ID OID/value, and serialized CSR equality.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestCertificateSignRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestRootCertificate.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestRootCertificate.java

Purpose: tests `SelfSignedCertificate` root/non-root certificate generation, distinguished-name content, validity windows, CA basic constraints, fixed root serial behavior, certificate verification, and invalid builder input handling.

Important APIs/types/functions: `SelfSignedCertificate.Builder`, `makeCA`, `build`, `SecurityConfig`, `HDDSKeyGenerator`, `CertificateCodec`, `getPEMEncodedString`, `getTargetCert`, `X509Certificate.verify`, and the basic-constraints extension OID `2.5.29.19`.

Control flow: each test configures security metadata, generates a key pair, builds certificates with subject, SCM ID, cluster ID, validity bounds, and serial ID, then inspects issuer/subject and extensions. CA tests write and reread PEM through `CertificateCodec`. Invalid-param tests clear or invert required fields and expect `IllegalArgumentException`, then checks wrong-key verification fails while a corrected builder still builds.

State and persistence behavior: most state is transient certificate objects; the CA test persists a PEM certificate to a temp path and reloads it. The builder encodes certificate validity and CA flags directly into the generated X.509 object.

Dependencies and integration points: relies on Ozone security config, HDDS key generation, JCA certificate verification, and certificate codec persistence.

Risks: date comparisons can be clock-sensitive. DN formatting follows Java principal canonicalization, so expected strings must track principal behavior. CA basic constraints and root serial number are protocol-significant.

Test signals: asserts issuer equals subject for self-signed certs, dates are within requested bounds, DN content, non-CA basic constraints of `-1`, successful verification with the public key, CA basic constraints and critical extension presence, root serial `BigInteger.ONE`, PEM round trip, invalid builder exceptions, wrong-key verification failure, and valid final build.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestRootCertificate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/package-info.java

Purpose: package-level documentation marker for tests covering certificate helper utilities.

Important APIs/types/functions: declares the `org.apache.hadoop.hdds.security.x509.certificate.utils` test package and documents that this package contains tests for certificate helpers.

Control flow: none; this is a `package-info.java` file with package Javadoc only.

State and persistence behavior: no runtime state, persistence, or side effects.

Dependencies and integration points: integrates with Java package documentation and test source organization for certificate utility tests.

Risks: low functional risk. Its main role is documentation consistency; stale package comments can mislead source navigation but do not alter test behavior.

Test signals: none directly; coverage is provided by sibling test classes in the package.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/package-info.java

Purpose: package-level documentation marker for X.509 certificate and key related tests.

Important APIs/types/functions: declares the `org.apache.hadoop.hdds.security.x509` test package and Javadoc for X.509/key test coverage.

Control flow: none; the file contains only documentation and package declaration.

State and persistence behavior: no runtime state, persistence, or side effects.

Dependencies and integration points: supports Java package documentation and IDE/source navigation for the broader X.509 test namespace.

Risks: no behavioral risk beyond documentation drift.

Test signals: none directly; behavioral coverage is in descendant certificate client and utility test packages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestJsonUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestJsonUtils.java

Purpose: verifies JSON pretty-printing for representative HDDS client objects, specifically `OzoneQuota` instances.

Important APIs/types/functions: `JsonTestUtils.toJsonStringWithDefaultPrettyPrinter`, `OzoneQuota.getOzoneQuota`, `OzoneQuota.getOzoneQuotaNameSpace`, and the local `assertContains` helper.

Control flow: creates a space quota and a namespace quota, serializes each with the default pretty printer, and asserts selected fields are present in the JSON string.

State and persistence behavior: no external state. Objects are constructed in memory and converted to strings.

Dependencies and integration points: integrates client-side quota model classes with the repository JSON utility layer and AssertJ string assertions.

Risks: tests only selected substrings, so formatting and additional fields can change without failure. It is useful for detecting field-name or serialization-regression changes for quota output.

Test signals: asserts `rawSize`, `unit`, and `quotaInNamespace` fields appear with expected values in pretty-printed JSON.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestJsonUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestOzoneAdmins.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestOzoneAdmins.java

Purpose: tests S3/Ozone administrator extraction and authorization matching from `OzoneConfiguration`.

Important APIs/types/functions: `OzoneAdmins`, `getS3AdminsFromConfig`, `getS3AdminsGroupsFromConfig`, `getS3Admins`, `isAdmin`, `isS3Admin`, `OzoneConfigKeys.OZONE_S3_ADMINISTRATORS`, `OZONE_ADMINISTRATORS`, group key variants, and `UserGroupInformation.createUserForTesting`.

Control flow: each parameterized case sets admin or admin-group configuration keys, constructs an `OzoneAdmins` view, then checks direct user and group-based authorization. Tests also cover behavior when configuration contains or omits explicit S3 admins and the static `isS3Admin` helper is given null UGI.

State and persistence behavior: configuration is in-memory per test. No disk or external service state is used.

Dependencies and integration points: integrates Ozone config keys, Hadoop UGI group membership, and the `OzoneAdmins` policy utility.

Risks: authorization behavior depends on fallback rules between S3-specific and Ozone-wide admin keys. Misinterpreting empty/unset admin config can create over-permissive or under-permissive access.

Test signals: asserts extracted admin users/groups, direct user admin checks, group-only admin checks, behavior with admin config enabled/disabled, static S3 admin decisions, and null-user denial.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestOzoneAdmins.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestServerUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestServerUtils.java

Purpose: comprehensive tests for `ServerUtils` filesystem/config helpers: permissions, metadata directory resolution, SCM DB directory fallback, colocated component Ratis directories, backward-compatible old Ratis paths, snapshot paths, and data-directory permission setting.

Important APIs/types/functions: `ServerUtils.getPermissions`, `getDirectoryFromConfig`, `getScmDbDir`, `getOzoneMetaDirPath`, `getRatisDirectory`, `getRatisSnapshotDirectory`, `setDataDirectoryPermissions`, config keys from `HddsConfigKeys`, `ScmConfigKeys`, `ReconConfigKeys`, `OzoneConfigKeys`, and node types `SCM`, `OM`, `DATANODE`.

Control flow: tests build temporary directory trees and `OzoneConfiguration` objects, set config keys, call resolution helpers, and assert returned files, creation side effects, exceptions, and POSIX permissions. Compatibility tests create empty/non-empty legacy `ratis` and `scm-ha` directories to verify migration/fallback precedence. Permission tests convert octal/symbolic strings to expected `PosixFilePermission` sets.

State and persistence behavior: heavily uses temp filesystem state. The helpers create metadata/database/Ratis directories, inspect legacy directory contents, and mutate POSIX permissions. Tests explicitly clean created directories in try/finally blocks where needed.

Dependencies and integration points: integrates Ozone configuration conventions, Java NIO POSIX permissions, Commons IO cleanup, node-type-specific layout rules, and legacy upgrade path compatibility.

Risks: POSIX permission tests may be platform-sensitive if run where POSIX attributes are unsupported. Backward-compatibility path selection is high risk because changing directory precedence can strand existing Ratis data.

Test signals: asserts configured/default permissions, directory creation, null/missing config behavior, rejection of multi-value metadata dirs, SCM DB fallback, mandatory metadata dir errors, distinct colocated component Ratis/snapshot dirs, old non-empty shared Ratis reuse, SCM `scm-ha` precedence, permission mutation for octal/symbolic/default values, no throw for absent directories, and read-only directory skipping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestServerUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/EventHandlerStub.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/EventHandlerStub.java

Purpose: simple test helper that records received events for assertions in event-system tests.

Important APIs/types/functions: implements `EventHandler<PAYLOAD>`, stores `List<PAYLOAD> receivedEvents`, implements `onMessage(PAYLOAD, EventPublisher)`, and exposes `getReceivedEvents`.

Control flow: when the event queue invokes `onMessage`, the payload is appended to an in-memory list. Tests later inspect that list.

State and persistence behavior: state is only the mutable `ArrayList` of received payloads. No synchronization is provided, so callers rely on event queue processing completion before assertions.

Dependencies and integration points: integrates with `org.apache.hadoop.hdds.server.events.EventHandler` and `EventPublisher`; used by watcher/queue tests to avoid repeated mock handlers.

Risks: not thread-safe by itself. If reused in tests with concurrent handler invocation and assertions before queue drain, ordering and visibility could be flaky.

Test signals: helper has no direct tests but provides observable received-event state to sibling tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/EventHandlerStub.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventQueue.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventQueue.java

Purpose: tests core event queue behavior: single event dispatch, multiple subscribers, fixed-thread-pool affinity executor scheduling, queue accounting, and non-power-of-two queue selection.

Important APIs/types/functions: `EventQueue`, `TypedEvent`, `EventHandler`, `EventPublisher`, `EventExecutor`, `FixedThreadPoolWithAffinityExecutor`, `EventQueue.getExecutorName`, `queuedEvents`, `scheduledEvents`, `successfulEvents`, `fireEvent`, and `processAll`.

Control flow: `startEventQueue` creates a fresh queue and `stopEventQueue` closes it. Tests register handlers, fire typed events, call `processAll` with timeouts, and inspect handler side effects or executor counters. The affinity test injects a `LinkedBlockingQueue` and fires multiple values, then checks queue length, scheduled/successful counts, and summed payloads. A `TrackingQueue` subclass records which internal queues receive items.

State and persistence behavior: state is in-memory event queues, handler arrays, atomic counters, executor metrics, and tracking sets. No disk persistence.

Dependencies and integration points: integrates HDDS event abstractions with Java concurrent queues, atomics, concurrent maps, and AssertJ/JUnit assertions.

Risks: async processing and timing can be flaky under slow environments; timeout values need enough headroom. Queue-affinity behavior is implementation-specific and should be updated if scheduling changes intentionally.

Test signals: asserts payload delivery, multiple subscribers receive the same event, queued/scheduled/successful event counts, aggregate event totals, and all queues are selected for non-power-of-two queue counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventQueueChain.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventQueueChain.java

Purpose: demonstrates and tests chained event publication where one handler publishes a follow-up event consumed by another handler.

Important APIs/types/functions: `EventQueue`, `TypedEvent<FailedNode>`, `EventHandler<FailedNode>`, `EventPublisher.fireEvent`, `PipelineManager`, `NodeWatcher`, and `processAll`.

Control flow: registers `PipelineManager` on `DECOMMISSION` and `NodeWatcher` on `DECOMMISSION_START`, fires a `FailedNode`, and drains the queue. `PipelineManager.onMessage` emits the follow-up event; `NodeWatcher.onMessage` is the terminal consumer.

State and persistence behavior: no durable state. The only payload state is `FailedNode.nodeId`, and queue state is transient.

Dependencies and integration points: validates that event handlers can use the supplied `EventPublisher` to enqueue additional work in the same `EventQueue`.

Risks: this test currently has no explicit assertions; it primarily detects exceptions or deadlocks during chained processing. Stronger test signals would record terminal handler receipt.

Test signals: implicit success is no exception and timely `processAll` completion after chained publish.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventQueueChain.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventWatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventWatcher.java

Purpose: tests `EventWatcher` lease-based tracking, completion filtering, timeout emission, in-progress queries, and watcher metrics.

Important APIs/types/functions: `EventWatcher`, `EventWatcherMetrics`, `LeaseManager`, `IdentifiableEventPayload`, `TypedEvent`, `EventQueue`, `EventHandlerStub`, `getTimeoutEvents`, `contains`, `getMetrics`, `onTimeout`, `onFinished`, and `HddsIdFactory`.

Control flow: setup starts a `LeaseManager`, teardown shuts it down. A concrete `CommandWatcherExample` listens for under-replicated start events and completion events. Tests fire watch events, optionally fire completion events, sleep/process until leases expire, then assert timed-out payloads were republished to `UNDER_REPLICATED`. Additional tests query in-progress events by predicate and inspect metrics after one completed and two timed-out events.

State and persistence behavior: state lives in the lease manager, watcher tracking map, metrics counters/gauges, and test helper event lists. No disk state.

Dependencies and integration points: integrates event queue dispatch with lease expiration and metrics. Test payloads implement identity-based equality/hash code to allow correlation between start and completion events.

Risks: sleep/lease-timeout tests are timing-sensitive and may need generous timeouts under load. Metrics assertions depend on exact accounting semantics for tracked/completed/timed-out events.

Test signals: asserts no premature timeout emission, completed events suppress timeout, only unfinished events are republished, in-progress filter results, `contains` transitions, tracked/completed/timed-out metric relationships, and positive timeout counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventWatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/package-info.java

Purpose: package-level documentation marker for event watcher tests.

Important APIs/types/functions: declares `org.apache.hadoop.hdds.server.events` and documents the package as tests for event watcher behavior.

Control flow: none; package Javadoc only.

State and persistence behavior: no runtime state or side effects.

Dependencies and integration points: supports Java package documentation and source organization for event system tests.

Risks: no behavioral risk beyond documentation drift.

Test signals: none directly; sibling event tests provide behavioral coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestBaseHttpServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestBaseHttpServer.java

Purpose: tests abstract `BaseHttpServer` address/bind-host resolution and runtime config mutation for HTTP/HTTPS listener addresses.

Important APIs/types/functions: `BaseHttpServer`, `HttpConfig.Policy`, `MutableConfigurationSource`, `BaseHttpServer.getBindAddress`, `start`, `stop`, `getHttpAddress`, `getHttpsAddress`, and subclass hooks for address keys, bind host keys, default ports, auth type, and auth config prefix.

Control flow: `setup` establishes a hostname and temp directory. `getBindAddress` creates an anonymous `BaseHttpServer` subclass with test config keys and asserts default bind host plus explicit bind host behavior. `updatesAddressInConfig` creates a concrete `TestingHttpServer`, starts it for each HTTP policy, and verifies the config is updated with actual bound hostname/port for enabled protocols before stopping.

State and persistence behavior: runtime listener state is owned by the server; configuration is mutated in memory with resolved addresses. Temp directories support server construction but no persistent test data is central.

Dependencies and integration points: integrates Ozone mutable configuration, `HttpConfig.Policy`, port allocation, and BaseHttpServer subclass contracts.

Risks: uses free-port allocation and actual server start/stop, so port races are possible. Tests are sensitive to hostname resolution and policy-specific listener enablement.

Test signals: asserts bind address strings for default and configured hosts, and checks HTTP/HTTPS address keys are updated only when the corresponding policy enables the listener.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestBaseHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHtmlQuoting.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHtmlQuoting.java

Purpose: tests HTML escaping/unescaping helpers and the servlet request wrapper used to quote request parameters.

Important APIs/types/functions: `HtmlQuoting.needsQuoting`, `quoteHtmlChars`, `unquoteHtmlChars`, `HttpServer2.QuotingInputFilter.RequestQuoter`, `HttpServletRequest.getParameter`, and `getParameterValues`.

Control flow: unit tests check which strings require quoting, expected replacements for `<`, `>`, `&`, quotes, and apostrophes, and round-trip quote/unquote for representative inputs. Request-quoting tests mock a servlet request, return single and array parameter values, and assert the wrapper quotes values while preserving nulls.

State and persistence behavior: no external state. All transformations are pure string operations over in-memory servlet mocks.

Dependencies and integration points: integrates HTML quoting utilities with `HttpServer2` input-filter request wrapping and servlet APIs.

Risks: escaping coverage is security-relevant for XSS prevention. The tests cover common characters but not every Unicode or malformed entity edge case.

Test signals: asserts quoting-needed decisions, exact escaped strings, null passthrough, round-trip behavior, quoted single request parameter, quoted parameter array, and null parameter-array passthrough.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHtmlQuoting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2.java

Purpose: verifies `HttpServer2` builder listener idle-timeout configuration.

Important APIs/types/functions: `HttpServer2.Builder`, `setName`, `addEndpoint`, `setIdleTimeout`, `build`, `getListeners`, and Jetty `ServerConnector.getIdleTimeout`.

Control flow: builds an HTTP server bound to localhost port zero with an idle timeout of 60 seconds, then iterates all listeners and asserts Jetty connector idle timeout matches.

State and persistence behavior: no durable state. The server is constructed but not started; listener configuration exists in memory.

Dependencies and integration points: integrates Ozone `HttpServer2` builder with Jetty connector settings.

Risks: narrow coverage; it only verifies configured value propagation, not runtime timeout behavior.

Test signals: asserts every server connector has idle timeout `60000`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2Metrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2Metrics.java

Purpose: tests that `HttpServer2Metrics` exports Jetty thread-pool gauges and server-name tags to Hadoop Metrics2.

Important APIs/types/functions: `HttpServer2Metrics.create`, `getMetrics`, `QueuedThreadPool`, `MetricsCollector`, `MetricsRecordBuilder`, metrics infos `HttpServerThreadCount`, `HttpServerMaxThreadCount`, `HttpServerIdleThreadCount`, `HttpServerThreadQueueWaitingTaskCount`, and `SERVER_NAME`.

Control flow: mocks a `QueuedThreadPool` and Metrics2 collector/record builder, stubs thread counts and queue size, creates the metrics source, invokes `getMetrics`, and verifies record creation, context/tagging, and gauge values.

State and persistence behavior: no persistent state. Metrics values are read from mocks and passed to Metrics2 mocks.

Dependencies and integration points: integrates Jetty threading metrics with Hadoop Metrics2 source/collector contracts and Mockito verification.

Risks: verifies exact metric names and gauges; any intentional metric rename requires test updates. It does not register with a live metrics system.

Test signals: verifies source record name, server-name tag, and all four gauge values are emitted.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2Metrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2SSL.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2SSL.java

Purpose: integration-style tests for `HttpServer2` TLS configuration, including cipher include/exclude lists, protocol restrictions, default TLS connectivity, and propagation of Hadoop `SSLFactory` enabled-protocol settings into Jetty.

Important APIs/types/functions: `HttpServer2.Builder`, `keyPassword`, `keyStore`, `trustStore`, `excludeCiphers`, `includeCiphers`, `start`, `stop`, `getListeners`, `SSLFactory.SSL_ENABLED_PROTOCOLS_KEY`, `SSL_ENABLED_PROTOCOLS_DEFAULT`, `KeyStoreTestUtil`, `HttpsURLConnection`, `SSLSocketFactory`, `SSLSocket`, and a local `ConstrainedSSLSocketFactory`.

Control flow: class-level setup creates test keystore/truststore config and loads server SSL settings. Tests build HTTPS servers with specific cipher/protocol constraints, start them, connect to `/jmx` using a constrained client socket factory, and assert either HTTP 200 or handshake failure. Protocol propagation tests inspect Jetty `SslContextFactory.Server` include/exclude protocol arrays directly.

State and persistence behavior: setup writes temporary keystore/truststore files and SSL config resources, cleaned in `tearDown`. Each test starts/stops an embedded HTTPS server and opens network connections to localhost.

Dependencies and integration points: integrates Ozone `HttpServer2`, Hadoop `SSLFactory` config, Jetty SSL context factories, Java SSL/TLS sockets, trust-manager initialization, and HTTPS URL connections.

Risks: TLS tests are environment-sensitive because supported ciphers/protocols vary by JDK/security policy. Local port allocation and network timing can be flaky. Exact cipher names require JDK support.

Test signals: asserts excluded ciphers reject clients, included ciphers accept matching and reject other ciphers, TLSv1.2-only server accepts TLSv1.2 and rejects TLSv1.1, default config accepts connections, configured/default enabled protocols are included in Jetty, and selected protocol is not excluded.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2SSL.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestProfileServlet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestProfileServlet.java

Purpose: tests profile-output filename generation/validation to prevent unsafe filenames in `ProfileServlet`.

Important APIs/types/functions: `ProfileServlet.generateFileName`, `validateFileName`, `ProfileServlet.Output` values `FLAMEGRAPH`, `SVG`, `COLLAPSED`, and `ProfileServlet.Event.ALLOC`.

Control flow: valid tests generate filenames for several output types/events and pass them to validation. Negative tests prepend newline-containing or path-traversal strings and assert validation rejects them.

State and persistence behavior: no file I/O occurs in the test. It validates string safety before filenames could be used for profiler artifacts.

Dependencies and integration points: integrates profiler servlet naming with JUnit exception assertions.

Risks: filename validation is security-sensitive because profiler output may be served or written to disk. Tests cover newline and slash traversal, but additional platform-specific forbidden characters may need separate coverage.

Test signals: accepts generated filenames and rejects newline/path traversal inputs with `IllegalArgumentException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestProfileServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestPrometheusMetricsIntegration.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestPrometheusMetricsIntegration.java

Purpose: integration tests for `PrometheusMetricsSink` with Hadoop Metrics2 publication, covering metric formatting, duplicate metric names with labels, HELP/TYPE uniqueness, and stale metric removal across flushes.

Important APIs/types/functions: `DefaultMetricsSystem.instance`, `MetricsSystem.register`, `unregisterSource`, `publishMetricsNow`, `PrometheusMetricsSink.writeMetrics`, `MetricsSource`, `MetricsCollector`, `MetricsTag`, `MutableCounterLong`, `@Metrics`, `@Metric`, and `GenericTestUtils.waitFor`.

Control flow: setup registers a Prometheus sink with the default metrics system; teardown stops it. Tests register annotated or lambda metrics sources, mutate counters, wait until expected metric names appear in sink output, and assert Prometheus text contains expected samples and metadata. Stale-metric testing unregisters one source, registers another, republishes, and verifies old samples disappear.

State and persistence behavior: metrics system state is global in-process and reset by teardown. Sink output is written to an in-memory writer. Stale samples are held inside the sink until flush/publish cycles.

Dependencies and integration points: integrates Metrics2 with Prometheus exposition formatting, Apache Commons string counting, and Ozone sink naming/tag utilities.

Risks: default metrics system global state can leak between tests if teardown fails. Asynchronous metrics publication requires polling. Formatting assertions are sensitive to name-normalization changes.

Test signals: asserts exported counter samples with labels, duplicate metric names disambiguated by labels, single TYPE line for same metric with different labels, stale metric removal after source replacement, and expected HELP/TYPE/sample content.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestPrometheusMetricsIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestPrometheusServletAuthorization.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestPrometheusServletAuthorization.java

Purpose: verifies bearer-token authorization behavior of `PrometheusServlet`.

Important APIs/types/functions: `PrometheusServlet`, `PrometheusServlet.SECURITY_TOKEN`, `BaseHttpServer.PROMETHEUS_SINK`, `PrometheusMetricsSink.writeMetrics`, servlet `init`, `doGet`, request `Authorization` header, and HTTP 403 response status.

Control flow: setup mocks servlet context/config to provide a security token and sink, then initializes the servlet. A helper invokes `doGet` with a mocked request/response and writer. The valid-token test passes `Bearer mytoken` and verifies metrics are written. Parameterized invalid headers include missing, empty, wrong scheme, wrong token, malformed spacing, and verify 403 plus no sink write.

State and persistence behavior: state is servlet instance fields initialized from mocked context attributes. No persistent state.

Dependencies and integration points: integrates servlet context initialization, HTTP authorization header parsing, and Prometheus metrics sink access control.

Risks: token comparison and header parsing are security-sensitive. Tests enforce exact bearer scheme behavior but do not cover case-insensitive schemes unless included in invalid values.

Test signals: verifies valid bearer token allows one sink write and no forbidden status; invalid headers set 403 and never call `writeMetrics`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestPrometheusServletAuthorization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestRatisDropwizardExports.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestRatisDropwizardExports.java

Purpose: tests Prometheus export of Ratis Dropwizard metrics through `RatisDropwizardExports`.

Important APIs/types/functions: `SegmentedRaftLogMetrics`, `RatisMetricsUtils.getDropWizardMetricRegistry`, Dropwizard `MetricRegistry`, `Timer`, `RatisDropwizardExports.collectAndExportAsText`, and Ratis raft log metric `RAFT_LOG_SYNC_TIME`.

Control flow: creates a Ratis segmented raft log metrics instance, locates a timer in its Dropwizard registry, records timing events, constructs the exporter, writes Prometheus text to a writer, and asserts expected normalized metric output appears.

State and persistence behavior: metrics state is in-memory in a Dropwizard registry. No disk persistence.

Dependencies and integration points: integrates Apache Ratis metrics with Ozone's Prometheus export path and Dropwizard timer types.

Risks: metric names and registry internals are tied to Ratis versions. Export text assertions may require updates when normalization or Prometheus type mapping changes.

Test signals: confirms a Ratis timer can be discovered and exported with expected Prometheus text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestRatisDropwizardExports.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestRatisNameRewrite.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestRatisNameRewrite.java

Purpose: parameterized tests for Ratis metric-name normalization and label extraction.

Important APIs/types/functions: `RatisNameRewriteSampleBuilder.normalizeRatisMetric`, parameterized `Arguments`, mutable tag name/value lists, and expected normalized metric names.

Control flow: `parameters()` supplies original Ratis metric names plus expected Prometheus names and tag arrays. The test calls the normalizer, then compares the normalized name and populated tag lists to expectations.

State and persistence behavior: no persistent state. The method mutates supplied `List<String>` instances to append tag names and values.

Dependencies and integration points: integrates Ozone Prometheus naming conventions with Ratis metric naming schemes for groups, peers, instances, and subcomponents.

Risks: normalization logic is compatibility-sensitive for dashboards and alerting. Parameter expectations must track both Ratis name changes and Prometheus label rules.

Test signals: asserts exact normalized names and exact ordered tag names/values for each representative Ratis metric pattern.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestRatisNameRewrite.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/package-info.java

Purpose: package-level documentation marker for HTTP server tests.

Important APIs/types/functions: declares the `org.apache.hadoop.hdds.server.http` test package.

Control flow: none; package declaration/documentation only.

State and persistence behavior: no runtime state or persistence.

Dependencies and integration points: supports Java package documentation and source organization for HTTP, servlet, SSL, and metrics tests.

Risks: no behavioral risk beyond documentation drift.

Test signals: none directly; sibling HTTP test classes provide coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/upgrade/TestHDDSLayoutVersionManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/upgrade/TestHDDSLayoutVersionManager.java

Purpose: tests HDDS layout feature upgrade-action registration and monotonic layout-version numbering.

Important APIs/types/functions: `HDDSLayoutVersionManager`, `HDDSLayoutFeature`, `INITIAL_VERSION`, `DATANODE_SCHEMA_V2`, `maxLayoutVersion`, `registerUpgradeActions`, feature `scmAction`/`datanodeAction`, `HDDSUpgradeAction.execute`, and test `MockComponent` actions.

Control flow: first verifies finalized manager state does not register actions. Then a mocked unfinalized manager calls the real `registerUpgradeActions` with a test package, after which the test retrieves SCM and datanode actions from layout features, executes them against a mocked component, and verifies the correct method is invoked. The version test iterates all HDDS layout features and expects each layout version to increment by one.

State and persistence behavior: state is in-memory layout version manager metadata layout version and static feature/action registration. No disk state.

Dependencies and integration points: integrates the upgrade action annotation scan/registration mechanism with feature enum metadata and Ozone upgrade action components.

Risks: action registration depends on package scanning; missing package names or finalized-state logic can silently skip actions. Static action attachment can leak if tests are not isolated.

Test signals: asserts no actions when finalized, actions present when unfinalized, correct action classes for SCM/DN, correct execution target method calls, absent actions for non-applicable components, and strictly increasing feature versions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/upgrade/TestHDDSLayoutVersionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/upgrade/test/MockComponent.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/upgrade/test/MockComponent.java

Purpose: fixture component and annotated upgrade actions used to test HDDS upgrade action discovery/registration.

Important APIs/types/functions: `MockComponent`, no-op `mockMethodScm`, no-op `mockMethodDn`, nested `MockScmUpgradeAction`, nested `MockDnUpgradeAction`, `HDDSUpgradeAction<MockComponent>`, and `@UpgradeActionHdds` annotations bound to `INITIAL_VERSION`/`SCM` and `DATANODE_SCHEMA_V2`/`DATANODE`.

Control flow: executing each nested action calls the corresponding method on a supplied `MockComponent`. Tests use Mockito mocks of `MockComponent` to verify the call.

State and persistence behavior: no internal state or persistence. The class is purely a registration/execution fixture.

Dependencies and integration points: integrates annotation metadata with `HDDSLayoutVersionManager.registerUpgradeActions` scanning in the test package.

Risks: annotation values must stay aligned with feature/component expectations in the registration test. Since component methods are no-op, correctness depends on external verification.

Test signals: consumed by `TestHDDSLayoutVersionManager`, which validates discovery and method invocation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/upgrade/test/MockComponent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/MapBackedTableIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/MapBackedTableIterator.java

Purpose: reusable unit-test implementation of `Table.KeyValueIterator<String,V>` over a `NavigableMap`, with optional prefix filtering.

Important APIs/types/functions: constructor `MapBackedTableIterator(NavigableMap<String,V>, String)`, `seekToFirst`, `seekToLast`, `seek`, `hasNext`, `next`, `removeFromDB`, `close`, and `Table.newKeyValue`.

Control flow: construction stores the map/prefix and calls `seekToFirst`. `seekToFirst` streams all entries, filters by prefix, maps entries to `Table.KeyValue` with value-size metadata, and installs an iterator. `seekToLast` delegates to `seek(values.lastKey())`. `seek` filters by prefix and key >= target, installs a new iterator, and returns the map ceiling entry for the target.

State and persistence behavior: iterator state is the current Java iterator over a snapshot stream pipeline. The backing map remains external and in-memory. `removeFromDB` and `close` are no-ops.

Dependencies and integration points: integrates test maps with the HDDS `Table` iterator contract and is used by `StringInMemoryTestTable`.

Risks: `seek` returns `values.ceilingEntry(s)` without applying the prefix filter to the returned value, while the installed iterator does filter; this can differ when a target key ceiling does not match the prefix. `seekToLast` on an empty map will throw due to `lastKey`.

Test signals: no direct tests in this file; behavioral validation is indirect through consumers of in-memory test tables.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/MapBackedTableIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestArchiver.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestArchiver.java

Purpose: tests archive buffer-size selection and hard-link-based inclusion of files into tar archives.

Important APIs/types/functions: `Archiver.getBufferSize`, `Archiver.linkAndIncludeFile`, `TarArchiveOutputStream`, `TarArchiveEntry`, `Files.createLink`, Mockito static mocking, and argument capture.

Control flow: parameterized tests check minimum, proportional, and maximum buffer-size behavior for file sizes. The successful hard-link test creates a temp file, invokes `linkAndIncludeFile`, verifies tar archive entry interactions and copied byte count, and ensures temporary link cleanup. The failure test statically mocks `Files.createLink` to throw, then expects the method to surface the IOException and avoid archive inclusion.

State and persistence behavior: uses temporary directories/files and hard links. Successful flow creates and removes a link file under the temp dir; failure flow verifies no hard link remains.

Dependencies and integration points: integrates Ozone archiver helper with Apache Commons Compress tar output, Java NIO hard links, and Mockito `MockedStatic`.

Risks: hard-link behavior can be filesystem/platform-sensitive. Static mocking of `Files` must be tightly scoped to avoid impacting other tests. Archive entry metadata must match actual file size.

Test signals: asserts buffer-size bounds, bytes-copied equals source size, archive entry name/size, put/close archive calls, link cleanup, propagated IOException message, and no hard link creation on failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestArchiver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestCollectionUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestCollectionUtils.java

Purpose: tests collection helper utilities for concatenating iterables and selecting top-N filtered values.

Important APIs/types/functions: `CollectionUtils.newIterator`, `CollectionUtils.topN`, comparators (`naturalOrder`, `reverseOrder`), predicates, and helper assertions `assertIteration`, `testTopN`, `assertTopN`.

Control flow: iterator tests pass lists of lists with single, multiple, empty, and mixed collections, consume the returned iterator into a list, and compare expected concatenation. Top-N tests build sorted expected lists after filtering and compare `CollectionUtils.topN` results for all N values plus `Integer.MAX_VALUE`, over strings and integers with natural/reverse comparators.

State and persistence behavior: pure in-memory collection processing; no external state.

Dependencies and integration points: validates utility behavior used by HDDS/Ozone code that composes iterators or needs bounded sorted selections.

Risks: top-N behavior must match comparator ordering and predicate filtering exactly; off-by-one and empty input cases are explicitly covered.

Test signals: asserts concatenation output for all list-shape cases and top-N output for each N, comparator, predicate, and input ordering combination.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestCollectionUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestDecayRpcSchedulerUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestDecayRpcSchedulerUtil.java

Purpose: tests helpers for parsing DecayRpcScheduler metrics and creating username metric tags.

Important APIs/types/functions: `DecayRpcSchedulerUtil.splitMetricNameIfNeeded`, `checkMetricNameForUsername`, `createUsernameTag`, and Hadoop `MetricsTag`.

Control flow: tests split a DecayRpcScheduler metric name containing username and metric type, verify unrelated metrics remain unchanged, extract username from scheduler metric names, return null for unrelated metrics, and create optional username tags only when username is non-null.

State and persistence behavior: pure string/tag processing with no external state.

Dependencies and integration points: supports metrics formatting and tagging for scheduler/user-level Prometheus or Metrics2 output.

Risks: metric-name parsing depends on exact record and metric naming conventions; changes upstream in scheduler metric names can break extraction.

Test signals: asserts split metric type, unchanged random metrics, username extraction, null extraction for unrelated metrics, absent tag for null username, and tag name/value/description for non-null username.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestDecayRpcSchedulerUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestHttpServletUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestHttpServletUtils.java

Purpose: tests servlet response-format negotiation and error-response rendering in `HttpServletUtils`.

Important APIs/types/functions: `HttpServletUtils.getResponseFormat`, `writeErrorResponse`, `HttpHeaders.ACCEPT`, servlet request/response mocks, `PrintWriter`, and response formats JSON/XML.

Control flow: parameterized cases stub the Accept header and assert selected response format. Separate tests mock response writers, call error writer for JSON and XML, and compare exact serialized error bodies.

State and persistence behavior: uses in-memory `StringWriter` output and mocked servlet objects. No durable state.

Dependencies and integration points: integrates servlet HTTP content negotiation with Ozone utility error serialization.

Risks: exact XML/JSON strings can be brittle if serializer formatting changes, but they pin the public error body contract. Accept-header parsing may need more cases for quality values or multiple content types.

Test signals: asserts format selection for provided Accept values and exact JSON/XML error output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestHttpServletUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestPrometheusMetricsSinkUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestPrometheusMetricsSinkUtil.java

Purpose: tests Prometheus metrics sink utility behavior for adding username/servername tags and normalizing metric names.

Important APIs/types/functions: `PrometheusMetricsSinkUtil.addTags`, `prometheusName`, `getMetricName`, `getUsername`, `MetricsTag`, username/servername tag constants, and representative metric record/name strings.

Control flow: tag tests call `addTags` with null, empty, and non-empty username plus UGI/non-UGI metric keys, then inspect returned tag lists for added or omitted tags. Naming tests feed camel-case, RocksDB, pipeline, and space-containing metric names into `prometheusName`, and helper tests check raw metric-name/username extraction when no embedded username exists.

State and persistence behavior: pure in-memory list/string transformations. Input tag lists are unmodifiable to ensure utility returns a usable copy rather than mutating immutable inputs.

Dependencies and integration points: feeds Prometheus exposition naming and labels used by `PrometheusMetricsSink` and HTTP metrics endpoints.

Risks: metric naming is dashboard/alert compatibility-sensitive. Tag-addition rules must avoid adding blank usernames and add servername only for UGI metrics.

Test signals: asserts absent username tag for null/empty username, present username tag for non-empty username, servername tag only for UGI metrics, both tags together, exact normalized names for camel-case/RocksDB/pipeline/space cases, unchanged metric name extraction, and null username extraction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestPrometheusMetricsSinkUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestRDBSnapshotProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestRDBSnapshotProvider.java

Purpose: tests `RDBSnapshotProvider` candidate snapshot download, incremental SST handling, DB content equivalence, cleanup on init, and leader-change consistency.

Important APIs/types/functions: `RDBSnapshotProvider`, `downloadDBSnapshotFromLeader`, `downloadSnapshot`, `getCandidateDir`, `init`, `checkLeaderConsistency`, `getInitCount`, `RDBStore`, `DBCheckpoint`, `Table`, `HAUtils.getExistingFiles`, `HddsServerUtil.writeDBCheckpointToStream`, and RocksDB managed options/statistics.

Control flow: setup creates a multi-column-family `RDBStore`, then subclasses `RDBSnapshotProvider` so `downloadSnapshot` inserts random data, takes a checkpoint, records it, and writes checkpoint files to the target stream while considering existing SST files. The download test obtains three snapshots, checks candidate directory growth, compares latest checkpoint DB contents with downloaded candidate DBs, and verifies `init` cleans the candidate directory. The leader test writes a dummy SST, changes leader IDs, and asserts reinitialization only when leader changes.

State and persistence behavior: heavy temp filesystem and RocksDB state. Candidate directories retain SSTs between downloads until init/leader-change cleanup. DB content is persisted in checkpoint directories and reopened for byte-for-byte table comparison.

Dependencies and integration points: integrates RocksDB stores/checkpoints, HA utility file detection, checkpoint streaming, file cleanup, managed RocksDB options/statistics, and codec leak detection.

Risks: RocksDB native resources and `CodecBuffer` leak detection require reliable cleanup. Random data and multiple checkpoints can be IO-heavy. Candidate directory reuse logic is high risk for HA snapshot correctness.

Test signals: asserts candidate dir existence, initial emptiness, first/second/third snapshot file-count growth, DB table equality across used column families, cleanup after `init`, leader-change init counts, dummy file deletion on new leader, no reinit for same leader, and reinit for different leader.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestRDBSnapshotProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestUgiMetricsUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestUgiMetricsUtil.java

Purpose: tests `UgiMetricsUtil.createServernameTag`, which adds a servername metrics tag only for compatible UGI metrics keys.

Important APIs/types/functions: `UgiMetricsUtil.createServernameTag`, `Optional<MetricsTag>`, Hadoop `MetricsTag`, compatible key `ugi_metrics`, and non-compatible key handling.

Control flow: one test passes a non-UGI key and asserts no tag is returned. The other passes `ugi_metrics` plus a server name and asserts a present tag with expected value, name, and description.

State and persistence behavior: pure in-memory key/tag creation; no external state or persistence.

Dependencies and integration points: supports Prometheus/Metrics2 labeling by adding server identity to UGI metrics before export.

Risks: compatibility depends on matching the UGI metrics key convention exactly. If the metrics key changes, servername labeling can silently disappear.

Test signals: asserts absent tag for non-compatible keys and present tag with value/name `servername` and description `name of the server` for `ugi_metrics`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestUgiMetricsUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/InMemoryTestTable.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/InMemoryTestTable.java

Purpose: generic in-memory `Table<KEY,VALUE>` implementation for tests that need simple table semantics without RocksDB.

Important APIs/types/functions: constructors from name/map, `put`, `isEmpty`, `isExist`, `get`, `getIfExist`, `delete`, `deleteRange`, `getName`, `getEstimatedKeyCount`, `getMap`, and unsupported `Table` operations such as batch writes, iterators, range queries, prefix deletes, dump/load.

Control flow: constructors copy supplied values into a `ConcurrentSkipListMap`. Basic CRUD methods delegate directly to the map. `deleteRange` clears a sub-map. Unsupported methods throw `UnsupportedOperationException`.

State and persistence behavior: state is a concurrent sorted in-memory map. There is no durable persistence, batching, or file dump/load behavior.

Dependencies and integration points: implements the HDDS `Table` interface and is extended by `StringInMemoryTestTable` to provide string-key iteration.

Risks: only a subset of `Table` behavior is implemented; tests using unsupported methods will fail fast. `ConcurrentSkipListMap` requires comparable keys or compatible ordering.

Test signals: no direct tests in this file; correctness is observed through tests that use the in-memory table as a fixture.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/InMemoryTestTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/StringInMemoryTestTable.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/StringInMemoryTestTable.java

Purpose: string-key specialization of `InMemoryTestTable` that adds iterator support via `MapBackedTableIterator`.

Important APIs/types/functions: constructors mirroring the parent table and override `iterator(String prefix, IteratorType type)`.

Control flow: construction delegates to the parent. Calling `iterator` returns a new `MapBackedTableIterator` over the parent `getMap()` and requested prefix; the `IteratorType` argument is accepted but not used.

State and persistence behavior: state is inherited in-memory `ConcurrentSkipListMap` content. Iterators read from that map and provide prefix-filtered traversal.

Dependencies and integration points: integrates test `Table` consumers needing string-key iteration with `MapBackedTableIterator`.

Risks: iterator type is ignored, so tests depending on different iterator modes are not modeled. Prefix filtering behavior inherits the iterator caveats around `seek`.

Test signals: no direct tests in this file; it is a fixture for DB/table tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/StringInMemoryTestTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodec.java

Purpose: broad test coverage for HDDS `Codec` implementations and `CodecBuffer` serialization paths.

Important APIs/types/functions: `Codec`, `ShortCodec`, `IntegerCodec`, `LongCodec`, `StringCodec`, `FixedLengthStringCodec`, `ByteStringCodec`, `UuidCodec`, `CodecBuffer`, `CodecTestUtil.runTest`, `RDBBatchOperation.Bytes`, Guava primitive byte conversions, protobuf `ByteString`, and RocksDB native library loading.

Control flow: static setup enables leak detection and loads RocksDB. Numeric codec tests cover edge values and random values, comparing persisted bytes to Guava conversions. String tests cover ASCII, multilingual UTF-8, malformed UTF-8 fallback/no-fallback behavior, and serialized-size expectations. Fixed-length string tests require ASCII and reject multibyte characters. ByteString and UUID tests round-trip empty, random, multilingual, and edge values. Shared `runTest` validates byte-array and heap/direct `CodecBuffer` forms.

State and persistence behavior: no external persistence; serialization produces byte arrays and buffers. Direct buffers are closed in try-with-resources and leak detection is exercised through `gc`.

Dependencies and integration points: integrates codec implementations with RocksDB batch byte wrappers, direct/heap buffer allocators, Guava/protobuf byte formats, and codec test utilities.

Risks: direct buffer lifecycle is important; leaks can destabilize native memory. UTF-8 malformed behavior differs between fallback and no-fallback codecs and is compatibility-sensitive. Fixed-length codec rejects multibyte strings by design.

Test signals: asserts round-trip equality, serialized sizes, byte compatibility with Guava primitives, malformed UTF-8 exception/fallback behavior, fixed-length status, multibyte rejection for fixed-length strings, direct empty buffer behavior, UUID size, and equality/hash consistency for array-vs-buffer `Bytes`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodecBufferCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodecBufferCodec.java

Purpose: tests `CodecBufferCodec` conversion behavior for direct and heap-backed `CodecBuffer` values.

Important APIs/types/functions: `CodecBufferCodec.get(boolean direct)`, `fromCodecBuffer`, `fromPersistedFormat`, `CodecBuffer.allocateDirect`, `CodecBuffer.asReadOnlyByteBuffer`, `getArray`, and `StringCodec`.

Control flow: parameterized tests run for direct/non-direct modes. `fromCodecBuffer` verifies the codec returns the same buffer instance. Persisted-format tests decode string bytes into a buffer and then use `StringCodec` to recover the string. Byte-array allocation tests check resulting length, directness rules, and byte-array equality.

State and persistence behavior: state is transient buffer memory. Buffers are closed with try-with-resources to avoid leaks.

Dependencies and integration points: validates codec behavior used when DB layers persist or retrieve raw `CodecBuffer` values.

Risks: ownership semantics are important because `fromCodecBuffer` returns the same object rather than copying. Directness behavior for zero-length buffers is explicit and must remain stable.

Test signals: asserts same-object return, string round trip, buffer remaining length, direct vs heap allocation expectations, and exact array contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodecBufferCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodecRegistry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodecRegistry.java

Purpose: verifies `CodecRegistry` resolves codecs by object instance and by Java class.

Important APIs/types/functions: `CodecRegistry.newBuilder`, `addCodec`, `getCodec`, `getCodecFromClass`, `IntegerCodec`, `LongCodec`, `StringCodec`, `ByteArrayCodec`, `ByteStringCodec`, `Codec.EMPTY_BYTE_ARRAY`, and protobuf `ByteString.EMPTY`.

Control flow: a registry is built with a ByteString codec in addition to defaults. Helper methods retrieve a codec for an object or class and assert the exact codec class. Tests cover integer, long, string, byte array, and ByteString values/classes.

State and persistence behavior: registry state is in-memory codec mappings. No persistence.

Dependencies and integration points: validates DB serialization infrastructure that dynamically selects codecs for table key/value types.

Risks: exact-class assertions mean subclass/proxy behavior is not covered. Missing mappings would fail table initialization or runtime serialization.

Test signals: asserts resolved codec is an instance of and exactly the expected codec class for each supported type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodecRegistry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestDBConfigFromFile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestDBConfigFromFile.java

Purpose: tests loading RocksDB DB and column-family options from `.ini` option files via `DBConfigFromFile`.

Important APIs/types/functions: `DBConfigFromFile.CONFIG_DIR`, `getOptionsFileNameFromDB`, `readDBOptionsFromFile`, `readCFOptionsFromFile`, RocksDB `DBOptions`, `ManagedColumnFamilyOptions`, `CompactionStyle`, and test resource `test.db.ini`.

Control flow: setup points the config-dir system property at a temp directory and copies the test `.ini` resource there; teardown clears the property. Tests read DB options from an existing file and assert option values, return null for missing/empty paths, throw for an empty option file, and read named column-family options with expected RocksDB settings.

State and persistence behavior: uses temp filesystem config files and a process-wide system property. RocksDB option objects hold native resources through managed wrappers.

Dependencies and integration points: integrates DB option-file naming, RocksDB option parsing, managed column-family options, and resource copying.

Risks: system property cleanup is important for test isolation. RocksDB option-file syntax and expected option values are version-sensitive.

Test signals: asserts DB options `maxManifestFileSize`, `keepLogFileNum`, `writableFileMaxBufferSize`; null for non-existent/empty paths; RocksDB exception text for empty file; and CF options including write buffer size, levels, blob file size, memtable factory, compaction style, and arena block size.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestDBConfigFromFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestDBStoreBuilder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestDBStoreBuilder.java

Purpose: tests `DBStoreBuilder` validation and RocksDB store construction with tables, writes, DB profiles, column-family options, and auto-compaction settings.

Important APIs/types/functions: `DBStoreBuilder.newBuilder`, `setName`, `setPath`, `addTable`, `setProfile`, `build`, `DBStore`, `RDBStore`, `Table`, `DBProfile.DISK`, `DBColumnFamilyDefinition`, `DBDefinition.WithMap`, `ManagedColumnFamilyOptions`, `RocksDatabase.ColumnFamily`, and `disableAutoCompactions`.

Control flow: early tests assert missing name/path combinations throw `IOException`. Open/close and write tests build stores in temp directories, add tables, put/get random byte-array keys/values, and verify empty second tables. Column-family option tests define a custom DB definition with per-table options, build an `RDBStore`, inspect column-family descriptors, and assert non-default settings were applied. Parameterized compaction tests build with config controlling auto-compaction and assert each column family reflects it.

State and persistence behavior: creates real RocksDB stores under temp paths, writes table data, inspects column-family metadata, and closes stores to release native resources. Uses a system property for DB config directory in setup.

Dependencies and integration points: integrates Ozone configuration, RocksDB-backed `RDBStore`, table definitions/codecs, managed CF options, random test data, and DB profiles.

Risks: native RocksDB resources require reliable close. Random keys are fine for uniqueness but make failures less reproducible. Builder validation and column-family options are high risk because misconfiguration affects DB layout/performance.

Test signals: asserts builder exceptions, successful open/close, duplicate table handling, byte-array persistence, empty secondary table, disk profile writes, column-family count, custom CF option effect, and configured auto-compaction flag per column family.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestDBStoreBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestFixedLengthStringCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestFixedLengthStringCodec.java

Purpose: tests that `FixedLengthStringCodec` can encode bytes into a string form and decode back to the original bytes for numeric container IDs.

Important APIs/types/functions: `FixedLengthStringCodec.bytes2String`, `FixedLengthStringCodec.string2Bytes`, `LongCodec.toByteArray`, and `LongCodec.fromByteArray`.

Control flow: iterates a range of long container IDs, converts each long to bytes, turns bytes into a fixed-length string, converts the string back to bytes, decodes the long, and asserts equality.

State and persistence behavior: pure in-memory byte/string conversion with no external state.

Dependencies and integration points: validates fixed-length string encoding used when binary keys need string-safe representation while preserving byte length/order assumptions.

Risks: coverage is focused on long byte arrays; multibyte string rejection and broader codec behavior are covered in `TestCodec`.

Test signals: asserts decoded container ID equals original for each generated ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestFixedLengthStringCodec.java -->
