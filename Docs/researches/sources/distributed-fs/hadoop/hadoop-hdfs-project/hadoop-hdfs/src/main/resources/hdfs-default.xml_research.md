<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/resources/hdfs-default.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/resources/hdfs-default.xml

## Purpose
`hdfs-default.xml` is the canonical default configuration catalog for the HDFS module. It documents and supplies defaults for NameNode, DataNode, JournalNode, Secondary NameNode, WebHDFS, balancer, mover, storage policy satisfier, security, HA/federation, caching, snapshots, erasure coding, provided storage, disk balancer, and client behavior. The file explicitly warns operators not to edit it directly; site overrides belong in `hdfs-site.xml`.

## Important APIs, Types, And Functions
- The public surface is a large set of `<property>` entries under a Hadoop `<configuration>` root. Each entry defines a `<name>`, `<value>`, and usually a `<description>`.
- Address and binding keys configure service endpoints: `dfs.namenode.rpc-address`, `dfs.namenode.servicerpc-address`, `dfs.namenode.lifeline.rpc-address`, `dfs.namenode.http-address`, `dfs.datanode.address`, `dfs.datanode.http.address`, `dfs.datanode.ipc.address`, `dfs.journalnode.rpc-address`, and matching `*-bind-host` / HTTPS keys.
- Storage and persistence keys include `dfs.namenode.name.dir`, `dfs.namenode.edits.dir`, `dfs.namenode.shared.edits.dir`, `dfs.datanode.data.dir`, `dfs.journalnode.edits.dir`, checkpoint directories, fsimage compression/parallel-load settings, edit-log retention, and storage directory permissions.
- Block-management keys define replication, block size, safemode thresholds, block reports, invalidation, decommission, stale/slow DataNode avoidance, placement-policy classes, upgrade domains, and EC placement/reconstruction.
- Client and data-transfer keys cover write retries, pipeline replacement policy, socket caches/timeouts, short-circuit reads, mmap cache, hedged reads, dead-node detection, refresh of located blocks, fsck timeouts, congestion backoff, and failover retry policy.
- Security keys configure HDFS permissions, ACLs, xattrs, block access tokens, delegation tokens, Kerberos principals/keytabs for daemons and SPNEGO, data transfer encryption/SASL QOP, WebHDFS OAuth2/CSRF, X-Frame-Options, and admin ACLs.
- HA and federation keys include `dfs.nameservices`, `dfs.nameservice.id`, `dfs.internal.nameservices`, `dfs.ha.namenodes.*`, `dfs.ha.namenode.id`, automatic failover, edit-log tailing/rolling, observer reads, standby checkpointing, stale reads, and failover proxy/resolver settings.
- Operational subsystem keys configure balancer, mover, storage policy satisfier, disk balancer, provided storage alias maps, cache reports, metrics percentiles, audit logging, lock tracing, and GC/lock monitoring.

## Control Flow
The file has no executable control flow; it is loaded by Hadoop's configuration machinery as an XML resource. Runtime behavior emerges when HDFS classes query these keys through Hadoop `Configuration`, typically after combining `hdfs-default.xml`, `hdfs-site.xml`, command-line overrides, and programmatic overrides. Empty defaults often mean "disabled", "auto-detect", or "derive from another property"; several descriptions state fallback chains such as service RPC falling back to NameNode RPC, checkpoint edits dir falling back to checkpoint dir, and internal nameservices falling back to `dfs.nameservices`.

Feature toggles gate major code paths. Examples include HA automatic failover, lifeline RPC, WebHDFS CSRF, HTTP/HTTPS policy, centralized caching, observer nodes, storage policy satisfier mode, disk balancer, provided storage alias map service, data transfer encryption, erasure coding validation, retry cache, and dead-node detection. Numeric throttles and thread counts bound periodic loops such as heartbeats, block reports, directory scans, cache reports, image transfers, edit-log tailing, decommission scans, balancer iterations, and reconstruction work.

## State And Persistence
This file itself is static source data. Its values control persistent HDFS state locations and compatibility-sensitive formats: NameNode namespace images and edit logs, DataNode block directories, JournalNode edit storage, checkpoint images, alias map stores, cache metadata, and storage policy behavior. Several settings affect what state is retained (`dfs.namenode.num.checkpoints.retained`, extra edits retained, edit segment caps) or whether existing state can be read efficiently (`dfs.image.parallel.load`, compression codec, provided storage alias maps). Runtime-only state is also shaped through retry caches, cache reports, mmap/socket caches, dead-node detection state, balancer moved-window tracking, and delegation token/key lifetimes.

## Dependencies And Integration Points
`hdfs-default.xml` is consumed across the HDFS Java codebase through configuration constants and by daemon launchers that include this resource on the classpath. It integrates with Hadoop common configuration merging, the NameNode and DataNode RPC/HTTP servers, Kerberos/SPNEGO login, KMS/key providers for encryption zones, JournalNode/quorum journal managers, WebHDFS/HttpFS clients, native libraries for short-circuit reads and cache hints, operating-system limits such as `RLIMIT_MEMLOCK`, topology resolvers, block placement policy classes, alias map implementations, and web UI/JMX endpoints. Documentation and tests also depend on this file remaining synchronized with code defaults.

## Risks And Edge Cases
- Defaults here are production-impacting even without site overrides; a bad default can change security posture, persistence paths, availability, or cluster performance.
- Empty values are overloaded and must be interpreted consistently by each consumer. Misinterpreting an empty endpoint, principal, resolver, or class name can start unwanted services, disable required services, or silently fall back.
- Many properties are class names. Renaming Java implementations without updating these values breaks startup or feature activation.
- Some descriptions encode constraints not enforced by XML, such as valid percentages, positive intervals, max values, and ratios. Validation must live in code and tests.
- Security toggles have sharp edges: HTTP-only defaults, disabled transfer encryption, optional block tokens, anonymous/simple web settings, and CSRF disabled by default are appropriate only in expected deployment contexts.
- Persistence and compatibility settings such as fsimage parallel loading, compression, format permission, storage policies, and provided storage can affect rollback, rolling upgrades, and data recoverability.
- Large thread counts and throttles for balancer, mover, block reports, cache operations, EC reconstruction, and DataNode transfer can overload NameNode/DataNode resources if changed without capacity testing.

## Test Signals
Useful signals include XML well-formedness validation, Hadoop configuration-load tests, tests that compare `DFSConfigKeys`/`HdfsClientConfigKeys` defaults with `hdfs-default.xml`, daemon startup tests with default configuration, HA/federation mini-cluster tests, secure MiniKDC/SPNEGO tests, WebHDFS HTTP policy/CSRF tests, balancer/mover/storage policy satisfier integration tests, fsimage/edit-log compatibility tests, and docs generation checks that consume the default configuration catalog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/resources/hdfs-default.xml -->
