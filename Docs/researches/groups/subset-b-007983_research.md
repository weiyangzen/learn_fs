# subset-b-007983 research

This grouped report covers HDDS common Java sources under `sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds`. Each section is delimited for reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/HddsConfigKeys.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/HddsConfigKeys.java

Purpose: central constant holder for HDDS configuration keys and defaults. It groups heartbeat/report intervals, SCM safe mode thresholds, metadata directory fallback, key/certificate material names, token and CA rotation durations, gRPC TLS knobs, security ACL keys, datanode HTTP/client/Ratis/checksum/disk-balancer settings, DNS and hostname settings, X-Frame options, metrics keys, and Kerberos keytab/principal keys.

Important APIs/types/functions: all exported behavior is public static constants; the private constructor prevents instantiation. Downstream classes import these constants directly, including `HddsUtils`, `OzoneConfiguration`, `RatisHelper`, service configuration beans, datanode services, security modules, and compatibility deprecation mapping.

Control flow: none beyond class loading. State/persistence: no mutable state, but values define persisted config names and default behavior for cluster services. Dependencies: no runtime dependencies beyond Java.

Integration points: Hadoop/Ozone XML configuration, datanode startup, SCM safe mode, certificate/key stores, gRPC TLS, token enforcement, and HTTP security. Risks: renaming or changing defaults has cluster-wide compatibility impact; time strings must match Hadoop duration parsing; defaults like token disabled and bind host `0.0.0.0` are security-sensitive when consumed incorrectly. Test signals: config loading tests, deprecated-key compatibility tests, service startup tests with default configs, and tests asserting generated default XML keys match these constants.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/HddsConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/HddsIdFactory.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/HddsIdFactory.java

Purpose: simple in-process HDDS long ID generator. Important API: `getLongId()` increments a static `AtomicLong` initialized from `System.currentTimeMillis()`.

Control flow: class initialization creates the counter; every call atomically increments and returns the next value. State/persistence: state is process-local and not persisted. The source comment explicitly warns IDs can collide after restart because the initial value is not durably recorded.

Dependencies: Java concurrency only. Integration points: callers needing cheap temporary or best-effort monotonically increasing IDs. It should not be used for IDs that require cluster uniqueness across process restarts or across machines.

Risks: restart collision, clock rollback relative to previously persisted IDs, and multi-process collision because each JVM owns its own counter. Test signals: verify monotonicity and thread safety under concurrent calls; avoid tests assuming persistence or global uniqueness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/HddsIdFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/HddsUtils.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/HddsUtils.java

Purpose: broad stateless utility class for HDDS configuration resolution, datanode/SCM addressing, container command classification, protobuf redaction, exception unwrapping, UUID conversion, JMX registration, path validation, and service helper formatting.

Important APIs: SCM client address resolution handles HA service IDs via `SCMNodeInfo` and non-HA fallbacks through `ozone.scm.client.address` and `ozone.scm.names`; host/port helpers parse config values; `getHostName(ConfigurationSource)` resolves datanode hostnames using explicit config, Hadoop DNS keys, or legacy HDDS DNS keys; `getDatanodeRpcAddress` combines bind host and client port. Container APIs classify read-only commands, token-required commands, open-to-write states, and extract `BlockID` from command-specific protobuf fields. Logging/debug APIs redact write/read payloads and checksums from container request/response protos, redact sensitive config through `ConfigRedactor`, and format stack traces. Other APIs validate child paths, create directories, unwrap RPC/security exceptions, decide no-failover RPC cases, convert Java/protobuf UUIDs, find SCM node IDs, and extract a one-line access-control message.

Control flow: most methods branch on configuration presence or protobuf command type. `getScmServiceId` enforces that multiple SCM service IDs require a default service ID. `processForDebug` rebuilds protobuf messages only for commands carrying binary data, replacing data buffers with `<redacted>` and clearing checksum data where known.

State/persistence: no durable state; only constants and logger. Dependencies: Hadoop `ConfigurationSource`, DNS/NetUtils, SCM HA config, protobufs, Ratis `ByteString`, Hadoop RPC exceptions, metrics MBeans, and Ozone service config.

Integration points: datanode startup, SCM client creation, container protocol auth, log/audit paths, service shutdown, RPC failover logic, and HA SCM discovery. Risks: host parsing strips only numeric `:port` suffixes and can be fragile for IPv6 or malformed values; command classification must stay synchronized with container proto additions; debug redaction is marked possibly incomplete; exception message matching can miss wrapped failures; `validatePath` relies on normalized path prefix and caller-supplied trusted ancestors. Test signals: HA and non-HA SCM address tests, DNS fallback tests, token/read-only classification per command enum, redaction tests for all data-bearing protos, failover exception unwrapping tests, and path traversal tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/HddsUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/JavaUtils.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/JavaUtils.java

Purpose: tiny utility for comparing the running Java specification major version. Important APIs: `isJavaVersionAtLeast(int)` and `isJavaVersionAtMost(int)`.

Control flow: static initialization reads `java.specification.version`, splits at `.`, parses the first component, and clamps to at least 8 so old `"1.8"` reports as 8. State/persistence: immutable static integer only.

Dependencies: Java system properties. Integration points: compatibility gates that need Java-version-specific behavior. Risks: versions with non-numeric prefixes would fail class initialization; the clamp means `isJavaVersionAtLeast(8)` is always true and versions below Java 8 are not distinguishable. Test signals: property-format tests for `"1.8"`, `"9"`, `"10"`, and current JVM; users should not rely on dynamic property changes after class load.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/JavaUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/NodeDetails.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/NodeDetails.java

Purpose: abstract base for HA service node metadata: service ID, node ID, RPC host/port, Ratis port, and HTTP/HTTPS endpoints.

Important APIs: constructors accept either an `InetSocketAddress` or host/port pieces; getters expose service/node IDs, RPC address, resolved/host status, Ratis host:port, HTTP/HTTPS addresses, and a thread name prefix derived from `HddsUtils.threadNamePrefix`.

Control flow: `getRpcAddress()` lazily builds and caches an `InetSocketAddress` from host and RPC port when not supplied. `isHostUnresolved`, `getInetAddress`, and `getHostName` delegate to that address.

State/persistence: mutable fields are initialized in constructors, but no setters are present here. `rpcAddress` is lazily cached and not synchronized. Dependencies: Hadoop `NetUtils`, Java networking, `HddsUtils`.

Integration points: HA node descriptors for SCM/OM style services and thread naming. Risks: lazy cache can preserve stale host/port if subclasses mutate inherited fields indirectly; unresolved addresses can propagate to callers; `getHostName()` may perform reverse lookup depending on `InetSocketAddress`. Test signals: constructor equivalence, unresolved host behavior, Ratis host:port formatting, and thread prefix for null/empty node IDs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/NodeDetails.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/StringUtils.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/StringUtils.java

Purpose: HDDS byte/string conversion and simple lexical string boundary helpers.

Important APIs: UTF-8 byte array and `ByteBuffer` decoding, byte-to-hex formatting with optional max byte count and overflow ellipsis, UTF-8 string-to-bytes, one-character lexicographic lower/higher transformations, and `getFirstNChars`.

Control flow: `bytes2Hex(ByteBuffer,int)` duplicates as read-only, enforces positive max, formats uppercase two-digit hex separated by spaces, and appends `...` when truncated. Lexicographic helpers reject null/empty input and prevent underflow/overflow of the last character.

State/persistence: no mutable state. Dependencies: Java NIO charset, Ratis-shaded Netty `Unpooled`, Ratis `Preconditions`.

Integration points: debugging binary buffers, key range calculations, and prefix display. Risks: lexical helpers modify only the last UTF-16 code unit, so they are not Unicode-collation aware; `getFirstNChars` returns the original string when `n` exceeds length but will throw through `substring` for negative `n`; hex formatting via `String.format` is relatively expensive. Test signals: ByteBuffer position preservation, max/truncation behavior, invalid max, min/max character edge cases, null handling, and surrogate-pair inputs if used with non-ASCII keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/StringUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/annotation/InterfaceAudience.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/annotation/InterfaceAudience.java

Purpose: API audience annotations copied into the HDDS namespace to communicate public, limited-private, or private usage intent.

Important APIs/types: nested runtime-retained annotations `Public`, `LimitedPrivate(String[] value)`, and `Private`. The class itself is annotated public/evolving and has a private constructor.

Control flow/state: none at runtime besides Java annotation metadata. Dependencies: Java annotation APIs and `InterfaceStability`.

Integration points: source documentation, generated docs, static analysis, and compatibility review policy. Risks: runtime retention makes annotations visible via reflection; missing annotation on a public class is documented as private by default, which can surprise external users. Test signals: annotation retention and documentation generation rather than functional behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/annotation/InterfaceAudience.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/annotation/InterfaceStability.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/annotation/InterfaceStability.java

Purpose: stability annotations for API compatibility expectations.

Important APIs/types: runtime-retained nested annotations `Stable`, `Evolving`, and `Unstable`. The class documentation defines how public and limited-private APIs should be paired with stability markings.

Control flow/state: no behavior beyond metadata. Dependencies: Java annotation APIs and `InterfaceAudience`.

Integration points: API compatibility policy, generated docs, and code review. Risks: annotations are advisory; incompatible changes are only prevented by process or tests. Runtime retention can affect reflection-based tooling. Test signals: source scanning or doc-lint style checks that public/limited-private classes are annotated.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/annotation/InterfaceStability.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/annotation/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/annotation/package-info.java

Purpose: package documentation for `org.apache.hadoop.hdds.annotation`, describing it as generic Ozone/HDDS annotations.

APIs/control flow/state: no executable code. Dependencies: none beyond package declaration.

Integration points: Javadoc and package-level discoverability. Risks: stale package documentation can mislead API consumers if annotations are added or removed. Test signals: compile/package documentation checks only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/annotation/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/BlockID.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/BlockID.java

Purpose: value object for an Ozone block identity: container ID, local ID, block commit sequence ID, and optional replica index.

Important APIs: constructors from container/local IDs, copy constructor, and `ContainerBlockID`; getters; mutable `setBlockCommitSequenceId`; string append; protobuf conversions for datanode `DatanodeBlockID` and HDDS `BlockID`; equality/hash including commit sequence ID and optional replica index.

Control flow: datanode proto conversion preserves replica index only when present; HDDS proto conversion does not carry replica index and rehydrates it as null. State/persistence: container block ID is final, BCS ID is mutable, replica index is final nullable state.

Dependencies: Jackson `JsonIgnore`, datanode and HDDS protobufs, `ContainerBlockID`. Integration points: container protocol, block allocation, SCM/OM metadata, and client/server serialization. Risks: mutating BCS ID after use in maps/sets breaks hash semantics; null replica index is intentionally distinct from zero; converting through HDDS proto drops replica index. Test signals: round trips through both protobuf forms, equality/hash with null vs zero replica index, and mutation safety expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/BlockID.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ContainerBlockID.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ContainerBlockID.java

Purpose: immutable pair of container ID and local block ID returned by SCM allocation.

Important APIs: constructor, getters, string append/toString, HDDS protobuf conversion, equality and hash. State/persistence: final primitive fields only.

Dependencies: Jackson `JsonIgnore`, HDDS protobufs. Integration points: `BlockID`, SCM block allocation, container datanode commands, persisted metadata.

Control flow: straightforward serialization/deserialization with no validation. Risks: accepts negative or zero IDs if caller passes them; string format is diagnostic not parseable API. Test signals: protobuf round trip and equality/hash contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ContainerBlockID.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/DecommissionUtils.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/DecommissionUtils.java

Purpose: stateless helpers for decommission status filtering and parsing datanode metrics JSON.

Important APIs: `getDecommissioningNodesList` filters streamed node protos by UUID, IP address, or returns all; `getBeansJsonNode` parses metrics JSON and returns the first `beans` element; `getNumDecomNodes` reads `DecommissioningMaintenanceNodesTotal`; `getCountsMap` scans indexed metrics fields for a datanode hostname and populates decommission start time, unclosed pipeline count, under-replicated container count, and unclosed container count.

Control flow: filter preference is UUID first, then IP, then all. Metrics parsing assumes JMX-style `beans[0]` and numbered per-datanode metric keys. State/persistence: no state; caller-supplied map is mutated.

Dependencies: Jackson JSON, Guava `Strings`, `DatanodeDetails`, HDDS protos, Java date formatting. Integration points: CLI/admin decommission status commands and Recon/SCM metrics display. Risks: brittle JSON shape assumptions; hostname matching ignores IP/UUID; default timezone in `SimpleDateFormat` can make output environment-dependent; numeric parsing from `JsonNode.toString()` is fragile compared with `asInt/asLong`. Test signals: metrics JSON with missing fields, zero nodes, hostname mismatch, UUID/IP filter precedence, timezone-sensitive formatting, and malformed JSON.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/DecommissionUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/DefaultReplicationConfig.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/DefaultReplicationConfig.java

Purpose: wrapper for the default replication configuration stored in protocol objects, covering EC and replicated modes.

Important APIs: constructor from any `ReplicationConfig`, `fromProto`, `getType`, `getReplicationConfig`, `toProto`, equality/hash/toString. `toProto` writes an EC submessage for EC configs and legacy type/factor for replicated configs.

Control flow: `fromProto` rejects null, branches on `hasEcReplicationConfig`, otherwise delegates legacy type/factor parsing. State/persistence: immutable references, but wrapped config mutability depends on implementation.

Dependencies: HDDS protobufs and replication config classes. Integration points: bucket/volume/default replication serialization. Risks: non-EC `toProto` derives factor from `getRequiredNodes`, so unsupported node counts throw through `ReplicationFactor.valueOf`; EC field presence controls parsing, so inconsistent proto type and EC payload can surprise consumers. Test signals: EC and RATIS/STANDALONE proto round trips, null proto rejection, equality across wrapped configs, and invalid required node count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/DefaultReplicationConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ECReplicationConfig.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ECReplicationConfig.java

Purpose: immutable erasure-coding replication config implementing `ReplicationConfig`.

Important APIs: constructors from data/parity defaults, explicit codec/chunk size, string format, and proto; enum `EcCodec` with `RS` and `XOR`; getters; `toProto`; `getRequiredNodes` as data plus parity; `getMinimumNodes` as data; string/config formats.

Control flow: string parsing uses regex `<codec>-<data>-<parity>-<chunksize>[k]`, validates known codec and positive data/parity/chunk size, and multiplies chunk size by 1024 if a `k` suffix exists. Proto constructor trusts proto values except enum conversion.

State/persistence: final fields; serializes into `HddsProtos.ECReplicationConfig`. Dependencies: Jackson, regex, HDDS protobufs, JCIP immutable annotation.

Integration points: `ReplicationConfig.parse`, `DefaultReplicationConfig`, OM/SCM replication validation, client API display. Risks: integer overflow when multiplying large chunk sizes by 1024; `chunkKB()` truncates non-KB-aligned proto chunk sizes; proto constructor can create zero/negative configs if upstream data is invalid; default validation pattern restricts allowed EC combinations elsewhere, not here. Test signals: accepted string formats/case, invalid codec and non-positive numbers, proto round trip, chunk suffix behavior, overflow boundaries, and validator integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ECReplicationConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/OzoneQuota.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/OzoneQuota.java

Purpose: represents Ozone namespace and byte quotas and parses user-facing quota strings.

Important APIs: `Units` enum from B through EB with byte multipliers and small-value caches; `parseSpaceQuota`, `parseNameSpaceQuota`, `parseQuota`, `getOzoneQuota`, quota getters, raw size/unit getters, and `toString`.

Control flow: space parsing uppercases and removes whitespace, checks unit suffixes in descending unit order to avoid `B` matching `KB`, parses positive integer sizes, and stores raw unit plus computed bytes. Namespace parsing accepts only positive integer counts and stores byte quota as -1 raw bytes. `RawQuotaInBytes.valueOf` converts a byte count to the largest power-of-1024 unit implied by trailing zero bits and asserts exact reconstruction.

State/persistence: object fields are effectively immutable except `quotaInNamespace` is not final. Dependencies: Ozone byte constants, Guava `Strings`, Ratis `Preconditions`.

Integration points: volume/bucket quota CLI/API, metadata display, quota persistence through byte/count values. Risks: multiplication can overflow for large EB values; no explicit negative byte quota except the namespace-only sentinel path; raw conversion assumes Ozone unit sizes are powers of 1024 and indexes `Units.values()` by trailing-zero groups; error text omits newer units PB/EB. Test signals: all unit suffixes, whitespace/case handling, zero/negative rejection, overflow boundaries, exact unit conversion, namespace-only sentinel, and combined quota parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/OzoneQuota.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/RatisReplicationConfig.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/RatisReplicationConfig.java

Purpose: immutable `ReplicationConfig` for RATIS replication.

Important APIs: static cached `getInstance` for ONE and THREE, `hasFactor`, `getReplicationType`, `getRequiredNodes`, `getReplicationFactor`, `getReplication`, `configFormat`, `getMinimumNodes`, equality/hash/toString.

Control flow: returns shared instances for common factors, creates a new instance for other proto enum values if ever provided. State/persistence: final factor; JSON exposes `replicationType` as enum via `@JsonProperty`.

Dependencies: HDDS protobuf enum types, Jackson, JCIP immutable. Integration points: `ReplicationConfig` parsing, bucket defaults, OM/SCM validation, client JSON. Risks: `getRequiredNodes` calls protobuf `getNumber`, which is not the same API as client `ReplicationFactor.getValue` but works for known proto enum numeric values; unsupported factors can be constructed if proto enum expands. Test signals: singleton behavior for ONE/THREE, JSON property, legacy factor extraction, minimum node behavior, and validation against allowed-config regex.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/RatisReplicationConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicatedReplicationConfig.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicatedReplicationConfig.java

Purpose: marker-style interface for replication schemes that copy data by a factor, such as RATIS and STANDALONE.

Important API: `getReplicationFactor()` returns the HDDS protobuf replication factor. Control flow/state: none. Dependencies: `ReplicationConfig` and HDDS protobufs.

Integration points: `ReplicationConfig.getLegacyFactor`, `DefaultReplicationConfig.toProto`, and code paths that need factor-based behavior only for replicated schemes. Risks: implementors must ensure `getReplicationFactor`, `getRequiredNodes`, and config format remain consistent. Test signals: interface coverage for all replicated implementations and non-EC legacy serialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicatedReplicationConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationConfig.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationConfig.java

Purpose: common interface and factory/parser for HDDS replication configurations.

Important APIs: legacy proto type/factor factories, client type/factor factory, default resolution from config, bucket/default resolution, proto deserialization including EC, legacy factor extraction, factor adjustment for Hadoop FS compatibility, `parse` with fallback from config, `parseWithoutFallback`, and instance methods for type, required/minimum nodes, replication string, and validation format.

Control flow: parsing falls back to `ozone.replication.type` and `ozone.replication` when arguments are null. RATIS/STANDALONE parse numeric or named factors; EC delegates to `ECReplicationConfig`; all parsed configs are validated through `ReplicationConfigValidator` from the active configuration. `adjustReplication` leaves EC unchanged and reparses replicated configs from a short factor.

State/persistence: no state in the interface. Dependencies: Ozone config keys, `ConfigurationSource`, HDDS protobufs, replication implementations and validator.

Integration points: client APIs, bucket defaults, OM/SCM metadata, Hadoop filesystem replication calls, and config validation. Risks: `ReplicationType.valueOf` is case-sensitive; EC is intentionally incompatible with legacy factor APIs; validation pattern can reject otherwise parseable configs; `fromTypeAndFactor` relies on enum name matching between client and proto. Test signals: null fallback behavior, invalid type/factor messages, EC parsing, validator rejection, bucket/default precedence, and adjustReplication for EC and replicated configs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationConfigValidator.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationConfigValidator.java

Purpose: configuration-backed validator restricting allowed replication configs by regex.

Important APIs: `disableValidation`, `setValidationPattern`, `init` as `@PostConstruct`, and `validate`. The default pattern allows STANDALONE/RATIS ONE or THREE and selected EC data/parity/chunk combos.

Control flow: pattern changes trigger recompilation; empty or null pattern disables validation. `validate` compares `replicationConfig.configFormat()` against the compiled pattern and throws `IllegalArgumentException` on mismatch.

State/persistence: holds configured pattern and compiled `Pattern`. Dependencies: HDDS config annotations and Java regex. Integration points: `ReplicationConfig.parseWithoutFallback`, generated config XML, admin controls for allowed replication schemes.

Risks: regex is an operational policy surface; overly restrictive patterns can block writes, overly permissive patterns can admit unsupported layouts. Pattern syntax errors surface during config object initialization or setter use. Test signals: default allowed/disallowed matrix, disabling validation, setter recompilation, invalid regex handling, and exception message containing pattern.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationConfigValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationFactor.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationFactor.java

Purpose: client-facing replication factor enum for ONE and THREE.

Important APIs: `valueOf(int)`, `fromProto`, static and instance `toProto`, and `getValue`.

Control flow: only 1 and 3 are accepted from integers; null proto/client values round trip as null in static conversions; unknown proto values throw. State/persistence: enum constants only. Dependencies: HDDS protobufs.

Integration points: CLI/client parsing, replication config factories, default replication serialization. Risks: adding a new factor requires updates across switch statements and validation patterns; client enum names must remain aligned with protobuf enum names for some factory paths. Test signals: int conversion, null conversion, unsupported proto/int rejection, and proto round trip.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationFactor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationType.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationType.java

Purpose: client-facing replication type enum.

Important APIs: enum values `RATIS`, `STAND_ALONE`, deprecated `CHAINED`, and `EC`; `fromProto` and `toProto` bridge to HDDS protobuf enums.

Control flow: null conversions return null; known values switch explicitly; unsupported proto/type values throw. State/persistence: enum constants only. Dependencies: HDDS protobufs.

Integration points: parsing, serialization, client API, replication validation. Risks: deprecated `CHAINED` remains serializable; enum name alignment with protobuf is relied on elsewhere; new proto values require code changes. Test signals: all enum conversions, null handling, deprecated CHAINED compatibility, and invalid-value behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/StandaloneReplicationConfig.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/StandaloneReplicationConfig.java

Purpose: immutable replication config for legacy STANDALONE replication.

Important APIs: cached `getInstance` for ONE/THREE, factor/type/required-node getters, JSON `replicationType()` returning `"STANDALONE"` while `getReplicationType()` returns proto `STAND_ALONE`, string/config format, equality/hash, and minimum nodes equal to factor.

Control flow/state: final factor with singleton common instances. Dependencies: Jackson, HDDS protobufs, JCIP immutable.

Integration points: legacy replication paths, `ReplicationConfig` factories, JSON output that expects `STANDALONE` spelling, default replication proto. Risks: dual spelling (`STAND_ALONE` vs `STANDALONE`) is compatibility-sensitive; `getMinimumNodes` differs from RATIS by requiring all replicas. Test signals: JSON spelling, singleton behavior, config format matching validator, equality/hash, and proto legacy round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/StandaloneReplicationConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/package-info.java

Purpose: package documentation for HDDS client base property types for containers and replication.

APIs/control flow/state: no executable code. Integration points: Javadoc and package-level organization. Risks: stale description if package grows beyond base properties. Test signals: compile/package-doc generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/DelegatingProperties.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/DelegatingProperties.java

Purpose: `Properties` wrapper used by `OzoneConfiguration` to enforce crypto compliance restrictions while delegating storage and mutation to an underlying `Properties`.

Important APIs: constructor with base properties, compliance mode, and crypto-tagged properties; `checkCompliance`; overridden `getProperty`, mutation and collection methods; `iterator()` returning checked string key/value entries.

Control flow: compliance checking is enabled unless mode is `unrestricted`. For crypto-tagged configs except the compliance mode key itself, the value must appear in `<config>.<mode>.whitelist` if that whitelist is present; otherwise a `ConfigurationException` is thrown. Most `Properties` operations delegate directly and do not apply checks except `getProperty` and custom `iterator`.

State/persistence: wrapper holds references to mutable backing properties and crypto properties. Dependencies: Ozone config keys, Hadoop `StringUtils`, HDDS `ConfigurationException`.

Integration points: `OzoneConfiguration.getProps`, config object binding, iteration over configuration entries, crypto compliance mode. Risks: `get(Object)` bypasses compliance while `getProperty(String)` enforces it; null values may be checked against whitelist and rejected; concurrent behavior depends on backing properties; whitelist omission means any value is accepted. Test signals: restricted and unrestricted modes, whitelist allow/deny, bypass via `get`, iterator enforcement, and compliance mode key exemption.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/DelegatingProperties.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/HddsPrometheusConfig.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/HddsPrometheusConfig.java

Purpose: configuration bean for the HDDS Prometheus servlet endpoint.

Important APIs: annotated field `hdds.prometheus.endpoint.token`, getter and setter. The description states a configured token allows token authorization and disables SPNEGO-based authentication for the endpoint.

Control flow/state: mutable bean field populated by config injection. Dependencies: HDDS config annotations. Integration points: generated config XML and Prometheus servlet authentication setup.

Risks: token presence changes authentication mode; empty default means no token. Token storage and logging must be handled carefully by consumers. Test signals: config binding, default empty token, and endpoint authentication mode selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/HddsPrometheusConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/OzoneConfiguration.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/OzoneConfiguration.java

Purpose: Ozone/HDDS-specific Hadoop `Configuration` subclass and `MutableConfigurationSource` implementation.

Important APIs: static `of` adapters, `newInstanceOf`, constructors, XML property unmarshalling classes, `getConfigurationResourceFiles`, `activate`, `getAllPropertiesByTag`, `getOzoneProperties`, config key iteration, prefix-trimming lookup, tag recognition, deprecated-key registration, fallback `getInt`, `reloadConfiguration`, guarded `getProps`, `getOrFixDuration`, and iterator.

Control flow: static initialization registers deprecations and activates default resources. Resource activation includes Hadoop defaults/sites, generated module defaults, `ozone-default.xml`, and `ozone-site.xml`. `getProps` lazily wraps Hadoop properties in `DelegatingProperties`, reading crypto compliance mode without compliance checks and crypto-tagged properties through Hadoop tag APIs. Reload resets the cached wrapper. `getAllPropertiesByTag` reloads props first and overlays current values because the superclass can miss overridden untagged values.

State/persistence: mutable Hadoop config plus cached delegating properties. Dependencies: Hadoop `Configuration`, JAXB, config tags, Ozone/SCM/HDDS keys, Ratis keys, and `DelegatingProperties`.

Integration points: nearly every service config read, generated config beans, deprecated Hadoop/Ozone keys, Ratis property propagation, crypto compliance policy, and XML config tooling. Risks: static default resource registration affects global Hadoop configuration; `of(ConfigurationSource)` casts non-legacy sources to `OzoneConfiguration`; cached `delegatingProps` must be invalidated on reload; fallback `getInt` logs even when fallback is null; Hadoop 2 tag API absence disables crypto compliance tag lookup. Test signals: default resource ordering, deprecated key mappings, compliance wrapper behavior, reload invalidation, prefix trimming, invalid duration auto-fix, XML unmarshalling, and adapter casts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/OzoneConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/RatisConfUtils.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/RatisConfUtils.java

Purpose: helper namespace for Ratis configuration adjustments.

Important API: `RatisConfUtils.Grpc.setMessageSizeMax(RaftProperties,int)` validates a desired maximum and sets Ratis gRPC max message size to that value plus 1 MB, preserving a required gap for RATIS-2135.

Control flow: asserts max is positive and at least the current Ratis log appender buffer byte limit, then writes `GrpcConfigKeys.setMessageSizeMax`. State/persistence: mutates caller-provided `RaftProperties`; no class state.

Dependencies: Ratis config keys, `RaftProperties`, `Preconditions`, `SizeInBytes`. Integration points: datanode/server Ratis property setup. Risks: assertion failures at startup if max is under buffer limit; the extra 1 MB is protocol/config compatibility-sensitive. Test signals: below/above buffer-limit cases, exact gap setting, and positive validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/RatisConfUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/package-info.java

Purpose: package documentation for Ozone configuration classes.

APIs/control flow/state: no executable code. Integration points: Javadoc and package-level organization. Risks: documentation drift only. Test signals: compile/package-doc generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsageSource.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsageSource.java

Purpose: interface for components that report directory or volume capacity, available space, and used space.

Important APIs: `getUsedSpace`, `getCapacity`, `getAvailable`, default `snapshot`, static `UNKNOWN`, and immutable nested `Fixed` implementation.

Control flow: default `snapshot` calls the three measurement methods and stores them in a `Fixed`. `Fixed` clamps available space to `0..capacity-used` and returns itself for snapshot. State/persistence: implementations may be live; `Fixed` is immutable point-in-time state.

Dependencies: HDDS audience/stability annotations and Java `UncheckedIOException`. Integration points: datanode volume accounting, tests, and disk usage caching. Risks: `Fixed` does not clamp negative used or capacity, so invalid inputs can produce odd values; live implementations may throw unchecked I/O. Test signals: snapshot consistency, clamping behavior, `UNKNOWN`, immutable snapshot, and propagation of unchecked I/O from implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsageSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/fs/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/fs/package-info.java

Purpose: package documentation for filesystem-related HDDS utilities.

APIs/control flow/state: no executable code. Integration points: Javadoc. Risks: documentation drift only. Test signals: compile/package-doc generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/fs/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/package-info.java

Purpose: package documentation for generic HDDS configurator and helper classes.

APIs/control flow/state: no executable code. Integration points: Javadoc/package documentation. Risks: stale description as the package includes both configuration constants and utility/value support. Test signals: compile/package-doc generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/protocol/DatanodeDetails.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/protocol/DatanodeDetails.java

Purpose: central datanode identity and endpoint descriptor, extending SCM network topology `NodeImpl` and providing protobuf/DB codec support.

Important APIs: `getCodec`, ID/UUID accessors, IP/host setters/getters, `validateDatanodeIpAddress`, synchronized port setters/getters, operational state helpers for decommission/maintenance, proto builders/parsers, extended proto conversion, version/setup/revision fields, compare/equality, builder, and nested `Port` value type with port name sets.

Control flow: builder parsing supports current `id` plus older `uuid128`/string UUID fields. Proto serialization writes current and deprecated UUID fields, byte-string host/IP fields, network topology, persisted operational state, expiry, and ports. Port serialization filters by requested port set and by client version: old clients receive only V0 ports, while newer clients can handle unknown ports. `getPort` falls back from RATIS_ADMIN, RATIS_SERVER, and RATIS_DATASTREAM to the legacy RATIS port for compatibility; `hasPort(Name)` checks explicit presence without fallback. `validateDatanodeIpAddress` resolves hostname and updates changed IPs.

State/persistence: mutable datanode metadata, volatile persisted op-state fields, synchronized port list access, DB codec via delegated proto codec. Equality and hash are based only on immutable `DatanodeID`.

Dependencies: HDDS protobufs, layout-feature annotations, client version gates, `DatanodeID`, `StringWithByteString`, network topology classes, DB codecs, DNS resolution, and logging.

Integration points: SCM node manager, datanode registration/heartbeat, pipelines, Ratis peer construction, network topology, persisted metadata, upgrade compatibility, and client-facing protobuf APIs. Risks: mutable fields on an equality-by-ID object can obscure stale endpoint data; port fallback can hide missing split Ratis ports; client-version filtering must track new port names; ignored unknown port names in proto parsing can lose endpoints; IP validation performs DNS lookups and logs but does not fail hard. Test signals: proto compatibility across client versions, unknown/filtered ports, legacy UUID fields, operational state defaults/expiry, builder defaults for network location, copy constructor, DB codec round trip, and explicit-vs-fallback port behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/protocol/DatanodeDetails.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/protocol/DatanodeID.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/protocol/DatanodeID.java

Purpose: immutable primary datanode identifier backed by a UUID and cached string/bytes representation.

Important APIs: comparison/equality/hash/toString, JSON-facing `getUuid`, deprecated byte-string accessor, `toPipelineID`, proto conversion, factories from proto/string/UUID, cached `of(UUID)`, and uncached `randomID`.

Control flow: `of(UUID)` uses a concurrent cache to canonicalize identifiers; `randomID()` deliberately avoids adding random IDs to the cache. State/persistence: static concurrent cache grows with distinct UUIDs; instances are immutable.

Dependencies: protobuf `ByteString`, HDDS protobufs, `PipelineID`, `StringWithByteString`. Integration points: `DatanodeDetails`, Ratis peer IDs, pipeline identity conversion, JSON/protobuf serialization. Risks: cache is unbounded; deprecated byte string remains for old proto compatibility; random IDs are not canonicalized. Test signals: cache identity behavior, proto/string round trips, compare ordering, pipeline conversion, and randomID non-cache behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/protocol/DatanodeID.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/protocol/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/protocol/package-info.java

Purpose: package documentation for HDDS protocol-related classes.

APIs/control flow/state: no executable code. Integration points: Javadoc and package organization. Risks: documentation drift only. Test signals: compile/package-doc generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/protocol/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/ContainerCommandRequestMessage.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/ContainerCommandRequestMessage.java

Purpose: Ratis `Message` implementation wrapping a `ContainerCommandRequestProto` while separating large write payload bytes from the serialized header.

Important APIs: `toMessage(request, traceId)`, `toProto(bytes, groupId)`, `getContent`, and debug `toString`. Content format is a 4-byte header size, serialized header, then raw data bytes.

Control flow: `toMessage` copies the request, adds trace ID, sets current client version when missing, extracts `WriteChunk.data` or `PutSmallFile.data` into a separate `ByteString`, and clears data from the header. `toProto` reads header length, parses the header, verifies or fills pipeline ID from the Raft group ID, and reattaches data for write/small-file commands. Content is memoized.

State/persistence: immutable header/data fields with memoized serialized content. Dependencies: container protos, Ratis `Message`/`RaftGroupId`, Ozone `ClientVersion`, checksum int encoding, and `HddsUtils` debug redaction.

Integration points: datanode container command replication through Ratis. Risks: malformed byte strings shorter than four bytes or invalid lengths can throw; pipeline/group mismatch is a correctness guard; only WriteChunk and PutSmallFile payloads are split, so new data-bearing commands need updates. Test signals: round trip for write, put small file, and non-data commands; trace/version injection; group ID mismatch; content memoization; malformed length handling; debug redaction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/ContainerCommandRequestMessage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/RatisHelper.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/RatisHelper.java

Purpose: utility class for bridging HDDS datanodes/pipelines/configuration to Apache Ratis clients, peers, groups, TLS, retry policies, routing tables, debug logging, and leadership transfer.

Important APIs: Ratis peer ID/address conversion, Raft peer/group construction, Ozone client Raft client factories, TLS parameter setup, `newRaftProperties`, client/server property propagation from `hdds.ratis.*`, TLS client config creation, retry policy reflection, min replicated index, routing table generation, byte buffer debug dump, `transferRatisLeadership`, retry-until condition helper, attempt calculation, and first-election-timeout setting.

Control flow: peer address uses a static `OzoneConfiguration` to decide host vs IP and reads RATIS_SERVER, RATIS_ADMIN, RATIS, and RATIS_DATASTREAM ports from `DatanodeDetails`. Client construction creates properties, enables Netty data stream, copies only client/grpc/netty/data-stream config prefixes, attaches TLS params for GRPC, and sets retry policy. Server property propagation excludes client configs except stream-related keys. Leadership transfer validates target membership and follower role, queries remote group info, checks group equality, raises target priority, calls Ratis transferLeadership, and resets priorities in finally when configuration was changed.

State/persistence: static logger, static default `OzoneConfiguration`, dummy empty group ID/group, no durable state; methods mutate caller-provided `RaftProperties` and perform networked Ratis admin operations.

Dependencies: HDDS config/security/pipeline/datanode types, Ratis client/server/config/protocol APIs, TLS config, Java duration/time utilities, Netty buffers. Integration points: container pipeline clients, OM/SCM HA leadership transfer, datanode Ratis server/client setup, secure gRPC, and data stream configuration.

Risks: static `CONF` for hostname preference may not reflect caller configuration; missing split Ratis ports rely on `DatanodeDetails` fallback; reflection-based retry policy creation wraps all failures in runtime exceptions; routing table returns null on closest-node lookup failure; debug dumps can be large; leadership transfer has distributed failure modes and priority reset can fail, leaving operational impact. Test signals: peer address host/IP modes, client/server property filtering, TLS GRPC-only behavior, retry policy class loading, leadership transfer success/failure/reset, routing table order, attempt calculation bounds, and first election timeout setting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/RatisHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/ServerNotLeaderException.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/ServerNotLeaderException.java

Purpose: HDDS IOException wrapper for Ratis `NotLeaderException` with optional suggested leader host:port extraction.

Important APIs: constructors for no suggested leader, explicit suggested leader, string message parsing for remote exception unwrap, `getSuggestedLeader`, and static `convertToNotLeaderException`.

Control flow: message constructor uses regexes to recognize "is not the leader" and extract `Suggested leader is Server:<host>:<port>`. Conversion from Ratis exception extracts hostname from suggested leader address using `HddsUtils.getHostName(...).get()`, appends the provided port, and builds an HDDS exception.

State/persistence: immutable `leader` string set at construction. Dependencies: Ratis peer and NotLeader exception, `HddsUtils`, regex. Integration points: datanode/container RPC error mapping and client retry/redirect behavior.

Risks: regex parsing is message-format fragile; `Optional.get()` can throw if suggested leader address has no host; conversion drops the suggested leader's original port and uses caller-provided port; null suggested leader is expected. Test signals: message parsing variants, no-leader cases, hostname extraction, malformed address, and remote exception unwrap compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/ServerNotLeaderException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/conf/RatisClientConfig.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/conf/RatisClientConfig.java

Purpose: annotated configuration bean for HDDS Ratis client behavior.

Important APIs/configs: watch replication level, write/watch request timeouts, multilinear random retry policy string, exponential backoff base/max sleep and max retries, fixed retry-limited interval/count, retry policy class name, plus nested `RaftConfig` for Ratis `raft.client.*` max outstanding requests and RPC/watch timeouts.

Control flow/state: mutable fields populated by config injection with getters/setters. Defaults are encoded both in annotations and field initializers for durations/ints where present. The bean is later consumed by retry policy creators and `RatisHelper.createRetryPolicy`; nested `RaftConfig` maps properties copied into `RaftProperties`.

Dependencies: HDDS config annotations, `RatisHelper` prefix, Ratis `RaftClientConfigKeys`, Java `Duration`. Integration points: generated default config XML, Ratis client creation, retry policy behavior, write/watch latency and reliability tuning.

Risks: `retrylimitedRetryInterval` and `retrylimitedMaxRetries` lack explicit field initializers and rely on config object injection to apply annotation defaults; malformed retry policy class names fail at client creation; timeout settings must align with Ratis server timeouts; watch type is raw string. Test signals: config binding defaults, setter overrides, retry policy construction, malformed policy string/class, and nested `RaftConfig` propagation into `RaftProperties`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/conf/RatisClientConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/conf/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/conf/package-info.java

Purpose: package documentation for Ratis-related configuration classes.

APIs/control flow/state: no executable code. Integration points: Javadoc. Risks: documentation drift only. Test signals: compile/package-doc generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/conf/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/package-info.java

Purpose: package documentation for Apache Ratis integration classes.

APIs/control flow/state: no executable code. Integration points: Javadoc and package organization. Risks: documentation drift only. Test signals: compile/package-doc generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/RequestTypeDependentRetryPolicyCreator.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/RequestTypeDependentRetryPolicyCreator.java

Purpose: builds a Ratis retry policy that varies by request type and exception class.

Important APIs: implements `RetryPolicyCreator.create(ConfigurationSource)`, plus helpers for exponential backoff, exception-dependent policy, and duration conversion.

Control flow: reads `RatisClientConfig`, constructs exponential backoff and multiple-linear-random policies, then builds a `RequestTypeDependentRetryPolicy`. WRITE requests use no retry for not-replicated/group-mismatch/state-machine exceptions, exponential retry for resource unavailable and timeout, and multilinear random default. WATCH requests use the same no-retry and resource-unavailable behavior, but timeout uses no retry. Write/watch request timeouts are also configured.

State/persistence: stateless. Dependencies: HDDS config source and Ratis client config, Ratis retry APIs, Ratis exception classes, protobuf request type cases. Integration points: `RatisHelper.createRetryPolicy` default policy for Raft clients.

Risks: raw `Class[]` and raw loop lose generic type safety; malformed multilinear policy strings fail during client creation; retry semantics affect consistency/latency under slow datanodes; timeouts of zero/negative durations are not validated here. Test signals: exception mapping matrix, write vs watch timeout behavior, malformed multilinear config, and exponential config boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/RequestTypeDependentRetryPolicyCreator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/RetryLimitedPolicyCreator.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/RetryLimitedPolicyCreator.java

Purpose: alternate retry policy creator that uses a fixed sleep and maximum retry count.

Important API: `create(ConfigurationSource)` reads `RatisClientConfig.getRetrylimitedMaxRetries` and `getRetrylimitedRetryInterval`, converts interval milliseconds to `TimeDuration`, and returns `RetryPolicies.retryUpToMaximumCountWithFixedSleep`.

Control flow/state: stateless, single config-driven policy construction. Dependencies: HDDS config source, Ratis client config, Ratis retry APIs.

Integration points: selectable through `hdds.ratis.client.retry.policy`. Risks: defaults rely on config injection; zero/negative retry interval or count validation is delegated to Ratis or may produce unexpected behavior. Test signals: config binding, fixed sleep/count behavior, invalid interval/count, and selection via `RatisHelper.createRetryPolicy`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/RetryLimitedPolicyCreator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/RetryPolicyCreator.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/RetryPolicyCreator.java

Purpose: small extension point for constructing Ratis `RetryPolicy` instances from HDDS configuration.

Important API: single `create(ConfigurationSource)` method. State/control flow: none in the interface. Dependencies: HDDS config source and Ratis retry policy.

Integration points: `RatisHelper.createRetryPolicy` loads implementations by configured class name. Risks: implementations need public no-arg constructors for current reflection path and should validate config values. Test signals: custom implementation loading, type checking, and exception wrapping in `RatisHelper`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/RetryPolicyCreator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/package-info.java

Purpose: package documentation for Ratis retry policy helpers.

APIs/control flow/state: no executable code. Integration points: Javadoc and package organization. Risks: documentation drift only. Test signals: compile/package-doc generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/recon/ReconConfig.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/recon/ReconConfig.java

Purpose: annotated configuration bean for Recon service security settings.

Important APIs/configs: Kerberos principal, Kerberos keytab file, datanode container protocol ACL, getters/setters, and nested `ConfigStrings` constants for the same config keys.

Control flow/state: mutable bean fields populated by config injection. Defaults are empty principal/keytab and wildcard ACL. Dependencies: HDDS config annotations and tags.

Integration points: Recon daemon login, generated default configs, service ACL setup, and consumers using string constants. Risks: wildcard ACL default is permissive; empty Kerberos settings require consumers to handle insecure or disabled auth modes; duplicated key strings in annotations and `ConfigStrings` can drift. Test signals: config binding defaults, getter/setter behavior, generated XML keys, and ACL/Kerberos integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/recon/ReconConfig.java -->
