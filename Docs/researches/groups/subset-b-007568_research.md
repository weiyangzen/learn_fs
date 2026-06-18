# subset-b-007568 Research

Grouped source research for Hadoop HDFS test resources under `hadoop-hdfs/src/test/resources`. The source files were read for their test fixture contracts: edit-log XML persistence coverage, HDFS/security/fault-injection configuration defaults, host include JSON compatibility, and CLI test definitions for ACLs, cache administration, encryption zones, safe deletion, and erasure coding. Each section is marker-delimited for deterministic reconciliation into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/editsStored.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/editsStored.xml

## Purpose

`editsStored.xml` is a stored HDFS edit-log XML fixture. The complete 1604-line XML was read. It captures a canonical serialized edit stream used by NameNode edit-log loader/offline edits tests to ensure that HDFS can parse, replay, and preserve compatibility for many operation encodings across filesystem, cache, ACL, xattr, erasure-coding, delegation-token, and rolling-upgrade features.

## Important APIs, Types, and Functions

The file is data rather than Java code, but it directly exercises edit-log record types consumed by HDFS offline edits processors and NameNode edit replay. Important serialized types include `<RECORD>`, `<OPCODE>`, `<DATA>`, `<TXID>`, `<BLOCK>`, `<PERMISSION_STATUS>`, `<DELEGATION_KEY>`, `<XATTR>`, erasure-coding policy payloads, cache pool/directive records, client identity fields (`RPC_CLIENTID`, `RPC_CALLID`), and lease-recovery records. The operation set includes `OP_START_LOG_SEGMENT`, `OP_UPDATE_MASTER_KEY`, `OP_ADD`, `OP_CLOSE`, `OP_APPEND`, `OP_ALLOCATE_BLOCK_ID`, `OP_SET_GENSTAMP_V2`, `OP_ADD_BLOCK`, `OP_UPDATE_BLOCKS`, `OP_SET_STORAGE_POLICY`, `OP_RENAME_OLD`, `OP_DELETE`, `OP_MKDIR`, snapshot operations, `OP_SET_REPLICATION`, permission/owner/time/quota changes, `OP_RENAME`, `OP_CONCAT_DELETE`, `OP_TRUNCATE`, `OP_SYMLINK`, `OP_REASSIGN_LEASE`, cache operations, ACL/xattr operations, erasure-coding policy operations, `OP_ROLLING_UPGRADE_START`, `OP_ROLLING_UPGRADE_FINALIZE`, and `OP_END_LOG_SEGMENT`.

## Control Flow

The stream begins with transaction 1 starting a log segment, then updates delegation master keys. Transactions 4-18 create, close, append, update block lists, set a storage policy, rename/delete a file, and create a directory. Transactions 19-24 cover allow/disallow snapshot, create, rename, and delete snapshot. Transactions 25-33 mutate a recreated `/file_create` through close, replication, permissions, owner, times, quotas, storage-type quota, and rename. Transactions 34-67 build concat target/source files with explicit block ID/generation-stamp allocation and then concatenate/delete sources. Transactions 68-86 cover truncation, symlink creation, and hard lease recovery with block generation-stamp bump and lease reassignment. Transactions 87-96 cover cache pool/directive and ACL/xattr mutation. Transactions 97-118 add, enable, disable, and remove erasure-coding policies, set an EC xattr on `/ec`, and create both replicated and striped files. Transactions 119-121 cover rolling upgrade start/finalize and log-segment end.

## State and Persistence Behavior

The fixture is entirely about persisted NameNode edit state. It encodes transaction ordering, inode IDs, paths, replication, mtimes/atimes, block IDs, block lengths, generation stamps, permissions, ACL entries, xattrs, quotas, cache pool metadata, cache directive IDs, EC policy lifecycle, striped block IDs, client RPC idempotency metadata, and rolling-upgrade timestamps. It also preserves special values such as empty client IDs, `RPC_CALLID=-2` for internal block updates, and negative striped block IDs.

## Dependencies and Integration Points

The fixture integrates with XML offline edits parsing, binary-to-XML round-trip tests, edit-log replay in FSImage/NameNode startup paths, delegation-token key parsing, cache manager state, snapshot manager state, ACL and xattr feature serialization, erasure-coding policy manager state, and rolling-upgrade metadata. The path names are intentionally broad enough to trigger code paths in namespace, block manager, cache manager, and EC policy logic.

## Risks and Edge Cases

Risks covered include edit-loader drift when new fields are added, incorrect defaulting of legacy fields, transaction order sensitivity, losing RPC idempotency identifiers, mishandling empty block updates, preserving ACL/xattr binary encodings, parsing negative striped block IDs, and compatibility regressions for old rename, truncate, symlink, cache, and rolling-upgrade opcodes. Because this is a golden fixture, small textual changes can invalidate round-trip expectations.

## Test Signals

Useful signals are successful XML parsing, every `TXID` replaying in order from 1 through 121, exact opcode recognition, stable offline-edits XML output, correct namespace reconstruction of files/directories/snapshots/cache entries/EC state, and no unknown-field or compatibility errors during edit-log loader tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/editsStored.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/fi-site.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/fi-site.xml

## Purpose

`fi-site.xml` is the HDFS test fault-injection site configuration. The complete 33-line file was read. It provides a default test-resource override that disables all `fi.*` injected faults unless individual tests explicitly raise a fault probability.

## Important APIs, Types, and Functions

The important configuration key is `fi.*` with value `0.00`. Hadoop `Configuration` and test fault-injection utilities consume this wildcard-style property as the default probability for named injected faults. The file uses the standard Hadoop `<configuration><property><name><value><description>` XML format and references `configuration.xsl` for rendering.

## Control Flow

When test configuration resources are loaded, this file contributes `fi.*=0.00`. Fault-injection-aware tests can then layer more specific `fi.<fault-name>` properties on top. With only this file loaded, injected fault decisions should be false because the configured probability is zero.

## State and Persistence Behavior

The file has no runtime persistence beyond in-memory Hadoop configuration state. Its value affects deterministic test execution by making fault injection opt-in rather than default-on.

## Dependencies and Integration Points

It integrates with HDFS tests that enable fault injection through configuration resources, especially tests that need a known baseline before enabling data-transfer, pipeline, or NameNode/DataNode faults. It depends on Hadoop's XML configuration parser and property overlay semantics.

## Risks and Edge Cases

Risks include tests unexpectedly inheriting nonzero fault probabilities, wildcard matching semantics changing, malformed XML preventing configuration load, or a later resource overriding `fi.*` and introducing nondeterminism. The property describes a floating-point probability bounded from 0 to 1.00.

## Test Signals

Signals are successful resource parsing and fault-injection tests behaving normally unless they explicitly configure a specific fault. A broad failure pattern would be random injected faults in unrelated HDFS tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/fi-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/hadoop-policy.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/hadoop-policy.xml

## Purpose

`hadoop-policy.xml` is the test security authorization policy for HDFS-related protocols. The complete 126-line file was read. It sets permissive ACLs for most service protocols while restricting refresh-policy operations to `${user.name}` so tests can exercise service-level authorization without blocking normal MiniDFSCluster protocol traffic.

## Important APIs, Types, and Functions

The file defines Hadoop service authorization ACL properties: `security.client.protocol.acl`, `security.client.datanode.protocol.acl`, `security.datanode.protocol.acl`, `security.inter.datanode.protocol.acl`, `security.namenode.protocol.acl`, `security.inter.tracker.protocol.acl`, `security.job.submission.protocol.acl`, `security.task.umbilical.protocol.acl`, `security.refresh.policy.protocol.acl`, `security.ha.service.protocol.acl`, and `security.zkfc.protocol.acl`. Values are ACL strings parsed by Hadoop service authorization code, where `*` means all users and `${user.name}` resolves to the active test user.

## Control Flow

During secure or service-authorization-enabled tests, Hadoop loads this XML into `Configuration`, service authorization refresh logic maps protocol interfaces to these ACL properties, and RPC servers allow or deny callers based on the parsed user/group ACL. Most protocol checks short-circuit to allow because the value is `*`; refresh authorization remains user-specific.

## State and Persistence Behavior

The file is static test policy state. It persists no cluster data, but it affects the in-memory authorization tables used by NameNode, DataNode, HA service, ZKFC, and older MapReduce protocol tests if those services load this resource.

## Dependencies and Integration Points

It integrates with Hadoop `ServiceAuthorizationManager`, HDFS client/DataNode/NameNode RPC protocols, HA admin and ZKFC tests, and admin commands that refresh authorization policy. It shares the standard Hadoop policy XML schema used by production `hadoop-policy.xml` files.

## Risks and Edge Cases

The main risks are accidentally making tests too permissive for refresh-policy checks, breaking variable substitution for `${user.name}`, leaving obsolete MapReduce ACL keys that may still be expected by compatibility tests, or changing `*` ACLs in a way that causes unrelated protocol tests to fail under service authorization.

## Test Signals

Signals are MiniDFSCluster startup with service authorization enabled, successful DFSClient/DataNode/NameNode/HA/ZKFC RPCs for arbitrary test users, and targeted refresh-policy tests allowing only the configured current user.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/hadoop-policy.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/hdfs-site.malformed.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/hdfs-site.malformed.xml

## Purpose

`hdfs-site.malformed.xml` is a deliberately unusual HDFS configuration fixture for HDFS-7684. The complete 143-line file was read. Despite the name, the XML is structurally valid; the important malformed aspect is address values with leading and trailing whitespace so tests can verify trimming and URI/address parsing behavior.

## Important APIs, Types, and Functions

The file defines HDFS address keys such as `dfs.namenode.secondary.http-address`, `dfs.namenode.secondary.https-address`, `dfs.datanode.address`, `dfs.datanode.http.address`, `dfs.datanode.ipc.address`, `dfs.datanode.handler.count`, `dfs.namenode.http-address`, `dfs.datanode.https.address`, `dfs.namenode.https-address`, `dfs.namenode.backup.address`, `dfs.namenode.backup.http-address`, `dfs.journalnode.rpc-address`, `dfs.journalnode.http-address`, and `dfs.journalnode.https-address`. Consumers include HDFS address config helpers, NetUtils parsing, NameNode/DataNode/JournalNode HTTP/RPC server binding, and tests that load `hdfs-site.malformed.xml` as a resource.

## Control Flow

The fixture is loaded into a `Configuration`, then code under test reads each address string, trims whitespace where appropriate, parses host/port pairs, and builds socket addresses or HTTP/HTTPS endpoints. It includes values with trailing spaces and one backup HTTP address with leading and trailing spaces.

## State and Persistence Behavior

There is no persisted cluster state. The file influences transient service bind addresses and parsed endpoint values during configuration tests. The handler count of `10` is a normal numeric control value used to ensure non-address properties are still parsed correctly.

## Dependencies and Integration Points

It integrates with Hadoop XML configuration parsing, HDFS address-key constants, `NetUtils.createSocketAddr`, and any tests checking that URL/address strings are sanitized before server startup or URI display.

## Risks and Edge Cases

Risks include trimming regressions causing bind failures, preserving whitespace inside emitted URLs, treating leading whitespace as part of a hostname, and tests confusing this fixture with genuinely invalid XML. Address keys with secure/nonsecure variants make broad parser behavior visible across NameNode, DataNode, BackupNode, SecondaryNameNode, and JournalNode paths.

## Test Signals

Signals are successful parsing and service address resolution to expected host/port values such as `0.0.0.0:9870`, no `UnknownHostException` or number-format failures from whitespace, and tests proving rendered URLs do not include leading/trailing spaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/hdfs-site.malformed.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/hdfs-site.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/hdfs-site.xml

## Purpose

`hdfs-site.xml` is the default HDFS test configuration resource. The complete 34-line file was read. It turns Hadoop security authentication off by default and permits tiny block sizes, matching the needs of many HDFS unit and integration tests.

## Important APIs, Types, and Functions

The file defines `hadoop.security.authentication=simple` and `dfs.namenode.fs-limits.min-block-size=0`. These are consumed by Hadoop `Configuration`, security initialization, NameNode filesystem limits, and MiniDFSCluster setup.

## Control Flow

When HDFS tests load resources from `src/test/resources`, this file contributes simple authentication unless a test overrides it with Kerberos/security-specific resources. It also changes NameNode block-size validation so tests can create very small files and blocks without tripping production minimum block-size checks.

## State and Persistence Behavior

The file contributes in-memory configuration only. Its values affect cluster startup and file-create validation, but it does not create durable filesystem state by itself.

## Dependencies and Integration Points

It integrates with MiniDFSCluster tests, DFSClient file creation, NameNode config validation, and security-sensitive tests that rely on a known simple-auth baseline before enabling Kerberos explicitly.

## Risks and Edge Cases

Risks include accidentally enabling Kerberos for the default test suite, making tiny-block tests fail by restoring a production minimum, or letting this resource mask tests that should explicitly set their own security and block-size assumptions.

## Test Signals

Signals are MiniDFSCluster startup under simple auth and successful creation of files with very small block sizes. Failures would show as authentication setup errors or `min-block-size` validation exceptions in tests that use small blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/hdfs-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/krb5.conf -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/krb5.conf

## Purpose

`krb5.conf` is a Kerberos configuration template for secure HDFS tests. The complete 38-line file was read. It supplies a local realm/domain mapping with placeholders that tests or MiniKdc setup replace at runtime.

## Important APIs, Types, and Functions

Important fields are `[libdefaults] default_realm=EXAMPLE.COM`, `allow_weak_crypto=true`, placeholder keys `_REALM_`, `_UDP_LIMIT_`, `_KDC_TCP_PORT_`, `_KDC_UDP_PORT_`, and `_KDC_PORT_`, a `[realms]` stanza pointing the realm KDC to `localhost`, `[domain_realm]` mappings for `.example.com` and `example.com`, and legacy `[login]` Kerberos 4 conversion flags. Consumers are JVM Kerberos/GSS configuration, Hadoop security login tests, and MiniKdc-based secure HDFS fixtures.

## Control Flow

Secure tests copy or render this template, replace placeholders with the test realm and KDC port settings, point Java Kerberos system properties to the rendered file, and then initialize Hadoop `UserGroupInformation`/Sasl/RPC components. The local KDC endpoint keeps tests self-contained.

## State and Persistence Behavior

The template is static. Rendered copies may be written into test temp directories, but this source resource itself persists no credentials. It controls Kerberos client lookup state through configuration, not through keytabs or tickets.

## Dependencies and Integration Points

It integrates with Hadoop security tests, MiniKdc, HDFS secure RPC and SPNEGO paths, and components that need realm-to-domain resolution. The weak-crypto allowance is a compatibility choice for older test KDC/client combinations.

## Risks and Edge Cases

Risks include placeholder replacement failures, stale default realm mismatching `_REALM_`, Java Kerberos rejecting weak crypto if policies change, UDP/TCP KDC port template comments not being toggled correctly, and tests accidentally using a system krb5.conf instead of the rendered test file.

## Test Signals

Signals are successful Kerberos login, service ticket acquisition against `localhost`, secure HDFS RPC/SPNEGO tests passing, and no fallback to unintended host or realm configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/krb5.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/legacy.dfs.hosts.json -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/legacy.dfs.hosts.json

## Purpose

`legacy.dfs.hosts.json` is a legacy JSON-lines host include/exclude fixture for HDFS DataNode admin-state parsing. The complete 7-line file was read. It preserves compatibility coverage for host records that are not wrapped in a single JSON array.

## Important APIs, Types, and Functions

Each line is an independent JSON object with keys such as `hostName`, `upgradeDomain`, `adminState`, `port`, and `maintenanceExpireTimeInMS`. The fixture exercises host states `DECOMMISSIONED` and `IN_MAINTENANCE`, a numeric `port`, missing optional fields, and a string-valued maintenance expiration. Consumers are HDFS host-file managers, JSON host readers, and DataNode decommission/maintenance tests.

## Control Flow

The host reader scans records line by line, decodes each object, defaults missing fields, and constructs host/property entries. It must accept simple hosts (`host1`), upgrade-domain hosts (`host2`, `host4`), decommissioned hosts (`host3`, `host4`), explicit-port host (`host5`), and maintenance hosts (`host6`, `host7`).

## State and Persistence Behavior

The file is static administrative input. When loaded, it affects in-memory include/exclude host maps and DataNode admin-state decisions, but it does not itself persist NameNode state.

## Dependencies and Integration Points

It integrates with HDFS DataNodeManager host configuration refresh, DFSAdmin refresh commands, decommission tracking, maintenance mode scheduling, and upgrade-domain-aware placement tests.

## Risks and Edge Cases

Risks include parsers assuming a JSON array instead of JSON lines, rejecting unknown/missing optional fields, mishandling string versus numeric maintenance expiration, failing to default absent ports or admin states, and losing backward compatibility for legacy host files.

## Test Signals

Signals are successful parsing of seven host entries, expected admin states for `host3`, `host4`, `host6`, and `host7`, correct `host5:8090` handling, and no parse failure from the line-oriented format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/legacy.dfs.hosts.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testAclCLI.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testAclCLI.xml

## Purpose

`testAclCLI.xml` is an HDFS CLI test definition for ACL commands. The complete 1075-line file was read. It defines 25 `test` cases in `test` mode that drive `hdfs dfs` operations against a test NameNode and compare command output for `getfacl`, `setfacl`, recursive ACL handling, default ACL inheritance, effective permissions, `ls` ACL markers, and copy-from-local inheritance.

## Important APIs, Types, and Functions

The fixture uses the Hadoop CLI test XML schema: `<mode>`, `<tests>`, `<test>`, `<description>`, `<test-commands>`, `<cleanup-commands>`, `<comparators>`, `<comparator>`, `<type>`, and `<expected-output>`. It invokes DFS shell commands such as `-touchz`, `-mkdir`, `-setfacl`, `-getfacl`, `-getfacl -R`, `-setfacl -R`, `-setfacl --set`, `-setfacl -x`, `-setfacl -k`, `-setfacl -b`, `-ls`, `-copyFromLocal`, `-rm`, and `-rm -R`. Comparator types include `SubstringComparator`, `ExactComparator`, `ExactLineComparator`, `RegexpComparator`, and `RegexpAcrossOutputComparator`.

## Control Flow

Each test creates a file or directory tree, applies ACL changes, reads ACL output, and then removes the tree. Early tests verify base file and directory ACL output. Middle tests add and remove named user/group ACLs, default ACLs, minimal default ACLs, invalid default ACLs on files, clearing defaults with `-k`, and removing extended entries with `-b`. Later tests check inherited default ACLs on files and directories, recursive display/modification/removal/set operations over mixed file and directory trees, complete `--set` replacement, removal of `mask::`, effective permission annotations, extended ACL marker `+` in `ls`, and default ACL inheritance for `copyFromLocal`.

## State and Persistence Behavior

The test mutates NameNode inode permission state and ACL feature state for paths such as `/file1`, `/dir1`, `/dir1/dir2`, and copied data files. Cleanup commands remove created paths so tests remain isolated. Expected output embeds `USERNAME` and `supergroup` placeholders and relies on stable ACL ordering and mask calculation.

## Dependencies and Integration Points

It integrates the DFS shell, NameNode ACL storage, permission status formatting, recursive filesystem traversal, local test data under `CLITEST_DATA`, output comparator framework, and `FsShell` command parsing. It also verifies that CLI text output stays compatible with POSIX ACL expectations.

## Risks and Edge Cases

Important risks are mask recomputation errors, default ACLs leaking into files where they should not, recursive operations applying directory-only defaults to files, output-order drift breaking exact comparisons, false-negative regexes for absence checks, platform/user placeholder expansion issues, and cleanup failures leaving ACL state behind for later cases.

## Test Signals

Signals include exact or substring matches for ACL headers, owner/group lines, base and named entries, `mask::` entries, absence of removed entries/defaults, invalid default-ACL error text, recursive exact output blocks, effective permission comments, `drwxr-xr-x+` listing markers, and copied-file ACL inheritance without default entries in file output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testAclCLI.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testAclCLIWithPosixAclInheritance.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testAclCLIWithPosixAclInheritance.xml

## Purpose

`testAclCLIWithPosixAclInheritance.xml` is a variant of the HDFS ACL CLI test suite with POSIX ACL inheritance semantics enabled. The complete 1152-line file was read. It mirrors the core ACL CLI coverage and adds inheritance checks for `mkdir -p` ancestor directories and different inherited mask/effective-permission behavior.

## Important APIs, Types, and Functions

The file uses the same CLI test XML schema and DFS shell commands as `testAclCLI.xml`: `-touchz`, `-mkdir`, `-mkdir -p`, `-setfacl`, `-getfacl`, recursive `getfacl`/`setfacl`, `--set`, `-x`, `-k`, `-b`, `-ls`, `-copyFromLocal`, and cleanup `-rm`/`-rm -R`. It relies on comparator types including substring, exact, exact-line, regex, token-like output matching through regex, and across-output negative checks.

## Control Flow

The first portion repeats base permissions, named ACL addition/removal, default ACL addition/removal, and invalid default ACL-on-file behavior. It then checks default ACL inheritance to created files and directories, including an extra case where `mkdir -p /dir1/dir2/dir3` must apply inherited default ACLs to ancestor `/dir1/dir2`. Recursive `getfacl` and recursive `setfacl` cases then validate mixed directory/file behavior. Final cases cover full ACL replacement, mask removal, only-default ACL display, effective permission comments under POSIX inheritance, extended ACL marker in `ls`, recursive modify/remove/set over mixed trees, and `copyFromLocal` into a default-ACL directory.

## State and Persistence Behavior

The fixture mutates ACL state on transient test paths. Compared with the non-POSIX variant, inherited file entries can retain broader effective permissions, such as copied files showing `user:charlie:rwx #effective:rw-` and `mask::rw-`. Directory inheritance includes both access and default entries on newly created directories and on intermediate ancestors created by `mkdir -p`.

## Dependencies and Integration Points

It integrates with the same DFS shell and NameNode ACL systems, plus the HDFS configuration switch or test mode that enables POSIX ACL inheritance semantics. It is especially tied to directory creation code paths and recursive shell traversal.

## Risks and Edge Cases

Risks include divergence between POSIX and legacy inheritance expectations, intermediate directories from `mkdir -p` not inheriting defaults, incorrect mask derivation for inherited files, exact-output brittleness from ACL ordering, and cleanup masking failures if inherited default ACLs affect removal behavior.

## Test Signals

Signals are the 26 test cases matching expected ACL lines, inherited `default:*` entries on directories, no default entries on files, expected effective permission annotations, successful ancestor inheritance for `/dir1/dir2`, recursive exact outputs for mixed trees, `ls` ACL marker output, and copied-file inherited ACL entries under POSIX-style mask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testAclCLIWithPosixAclInheritance.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testCacheAdminConf.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testCacheAdminConf.xml

## Purpose

`testCacheAdminConf.xml` is the HDFS cacheadmin CLI test definition. The complete 580-line file was read. It defines 22 test cases for `hdfs cacheadmin` usage, cache pool lifecycle, directive lifecycle, filtering, statistics, TTL/limit formatting, and replication override behavior.

## Important APIs, Types, and Functions

The XML uses `<cache-admin-command>` entries inside the CLI test schema. Commands include bare usage, `-listPools`, `-addPool`, `-modifyPool`, `-removePool`, `-addDirective`, `-modifyDirective`, `-removeDirective`, `-removeDirectives`, `-listDirectives`, `-help addPool`, `-stats`, `-id`, `-pool`, `-path`, `-ttl`, `-limit`, `-maxTtl`, `-owner`, `-group`, `-mode`, and `-defaultReplication`. Comparators are mostly `SubstringComparator`, checking stable text tables and result counts.

## Control Flow

The tests start with usage and empty pool listing. Pool cases add, modify, delete, list all, and list one pool. Directive cases create directives in pools, remove pools to delete directives, filter by pool/path/path+pool, remove one directive by ID, remove every directive for a path using a relative path, modify directive path and pool, and list a single directive by ID. Later cases verify help text, pool and directive statistics columns, max TTL formatting (`never`, `000:04:00:00.000`), unlimited limits, and default/overridden replication after pool and directive modification.

## State and Persistence Behavior

The fixture mutates NameNode cache-manager state: cache pools, owners, groups, modes, byte limits, max TTLs, default replication, cache directives, directive IDs, paths, directive replication, and directive TTLs. Cleanup removes created pools, which also removes their directives.

## Dependencies and Integration Points

It integrates with the `CacheAdmin` CLI, NameNode cache manager RPCs, table formatting, directive ID allocation, path normalization, permission-style mode rendering, stats counters, and CLI comparator framework.

## Risks and Edge Cases

Risks include directive ID sequence assumptions, table spacing drift, TTL formatting changes, pool removal failing to purge directives, path normalization bugs for relative `../../foo`, incorrect inheritance/override of default replication, and stale cache-manager state between tests.

## Test Signals

Signals are expected success messages, result counts (`Found 0/1/2/3`), exact table substrings for owners/groups/modes/limits/TTLs/replication, zero-valued stats columns, successful help text, and final directive listings after remove/modify operations showing only intended entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testCacheAdminConf.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testCryptoConf.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testCryptoConf.xml

## Purpose

`testCryptoConf.xml` is the HDFS crypto CLI test definition. The complete 738-line file was read. It defines 35 tests for encryption-zone command usage, encryption-zone creation errors and successes, rename restrictions across encryption zones, trash provisioning, file encryption info lookup, encryption-zone listing with Trash and snapshots, and re-encryption commands.

## Important APIs, Types, and Functions

The fixture uses `<crypto-admin-command>` entries and normal DFS shell commands. Crypto commands include usage/help, `-createZone -keyName ... -path ...`, `-provisionTrash -path ...`, `-getFileEncryptionInfo -path ...`, `-listZones`, `-reencryptZone -start`, `-reencryptZone -cancel`, and `-listReencryptionStatus`. DFS shell setup/cleanup commands include `-mkdir`, `-touchz`, `-ls`, `-mv`, `-rm`, `-rm -r`, `-rm -r -skipTrash`, `-rmdir`, `-allowSnapshot`, `-createSnapshot`, and `-deleteSnapshot`. Comparators include substring, regex-across-output, and token comparison.

## Control Flow

Early tests validate usage/help argument handling and create-zone errors for missing paths, duplicate zones, non-empty directories, missing keys, missing path, and missing key name. Creation success is checked for subdirectories and nested paths. Rename tests validate disallowed moves across zones, into zones, and from zones, while allowing encryption-zone root rename and intra-zone rename. Trash provisioning tests cover non-zone paths, pre-existing `.Trash`, successful provisioning, and incorrect subdirectory roots. File encryption info tests check EZ files, non-EZ files, nonexistent files, EZ directories, and subdirectories. Zone listing tests verify deleted zones remain listed under Trash, permanently deleted zones disappear, snapshots preserve deleted zones, and nested snapshot/trash scenarios behave correctly. Re-encryption tests cover successful submission, non-EZ rejection, cancel rejection for zones not being re-encrypted, and list status tokens.

## State and Persistence Behavior

The tests mutate encryption-zone xattrs/metadata, create `.Trash` under zones, move or delete paths into user Trash, create snapshots that preserve zone roots, and submit re-encryption state. Cleanup uses `-skipTrash` or explicit Trash cleanup where necessary so zone listing expectations are isolated.

## Dependencies and Integration Points

It integrates with the `CryptoAdmin` CLI, key provider setup for `myKey` and `zone2`, NameNode encryption-zone manager, DFS rename restrictions, Trash semantics, snapshot manager, file encryption info lookup, and re-encryption status tracking.

## Risks and Edge Cases

Risks include accidentally permitting cross-zone renames, failing to provision zone-local Trash, stale deleted zones in listings after permanent cleanup, snapshot references hiding deleted-zone metadata, key-existence errors changing text, and asynchronous re-encryption status output being too timing-sensitive for token comparison.

## Test Signals

Signals are expected usage/help/error strings, `Added encryption zone` success messages, rename denial messages naming source/destination zones, Trash provisioning messages, `keyName: myKey, ezKeyVersionName: myKey@0`, no-info and file-not-found errors, regex listing of live/Trash/snapshot zones, and `/src,Completed,false,myKey,zone2` token output for re-encryption status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testCryptoConf.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testDeleteConf.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testDeleteConf.xml

## Purpose

`testDeleteConf.xml` is an HDFS CLI test definition for recursive delete behavior with and without `-safely`. The complete 83-line file was read. It defines two tests that build small directory trees and verify expected delete output.

## Important APIs, Types, and Functions

The fixture uses DFS shell commands `-mkdir`, `-copyFromLocal`, `-ls`, and `-rm -r` with and without `-safely`. It depends on `CLITEST_DATA/data15bytes`, `data30bytes`, `data60bytes`, and `data120bytes`. It uses `RegexpComparator` to match `Deleted /dir0`.

## Control Flow

The first test creates `/dir0` with four files and two child directories, lists it, then deletes recursively without `-safely`; even though the tree meets warning criteria, the expected output is deletion. The second test creates a slightly smaller tree that does not meet warning criteria and deletes with `-safely`; it also expects deletion. Cleanup tries to remove `/dir0` in both cases in case the main delete fails.

## State and Persistence Behavior

The tests create transient HDFS files and directories under `/dir0`. They exercise namespace deletion and Trash/safe-delete prompting behavior through the CLI, then remove all state during cleanup.

## Dependencies and Integration Points

It integrates with `FsShell` delete command parsing, HDFS namespace mutation, CLI safe-delete threshold configuration, local CLI test data resources, and regex output comparison.

## Risks and Edge Cases

Risks include safe-delete warning thresholds changing, interactive prompt behavior entering automated tests, cleanup hiding partial delete failures, and output wording drift from `Deleted /dir0`.

## Test Signals

Signals are command completion and output matching `Deleted /dir0` in both safe and non-safe recursive delete scenarios, with no leftover `/dir0` for later CLI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testDeleteConf.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testErasureCodingConf.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testErasureCodingConf.xml

## Purpose

`testErasureCodingConf.xml` is the HDFS erasure-coding CLI test definition. The complete 1086-line file was read. It defines 58 tests for `hdfs ec` usage/help, policy set/unset/get/list/add/enable/disable/remove command behavior, invalid parameter handling, codec listing, and `count -e`/`ls -e` display of erasure-coding policy.

## Important APIs, Types, and Functions

The fixture uses `<ec-admin-command>` and DFS shell commands. EC commands include usage/help for subcommands, `-setPolicy`, `-unsetPolicy`, `-getPolicy`, `-listPolicies`, `-addPolicies`, `-removePolicy`, `-enablePolicy`, `-disablePolicy`, and `-listCodecs`. DFS shell commands include `-mkdir`, `-touchz`, `-rm`, `-rmdir`, `-count -e -v`, and `-ls -e`. It references built-in policies such as `RS-6-3-1024k`, `RS-3-2-1024k`, `REPLICATION`, and user-added policies from a policy file including `XOR-2-1-128k`, `RS-12-4-128k`, and `RS-LEGACY-12-4-128k`.

## Control Flow

The first ten tests validate usage and help text for the top-level command and subcommands. Policy behavior tests set policies on directories, repeat setting, set replication policy, unset and get policy, change policy, warn on non-empty directories, handle inherited policies, reject unsetting where no explicit policy exists, and query files/directories with and without EC policy. Policy management tests list built-ins, add user policies, list disabled user policies, enable/disable policies idempotently, and validate illegal/missing/extra parameters for set/get/list/add/enable/disable/listCodecs. Final tests verify codec listing and show EC policy in `count -e -v` and `ls -e`, including directories, files, disabled policy display, and replication policy display.

## State and Persistence Behavior

The fixture mutates NameNode EC policy xattrs on directories, creates files inheriting EC policy, adds user-defined policies to the EC policy manager, toggles policy enabled/disabled state, and relies on cleanup of `/ecdir`, `/dir1`, and `/file1`. Some operations intentionally leave global EC policy manager state changed for later list/enable/disable assertions within the same CLI suite.

## Dependencies and Integration Points

It integrates with `ECAdmin`, NameNode erasure-coding policy manager, filesystem xattr storage for policy assignments, DFS shell `count` and `ls` formatting, policy-file parsing, codec registry, and CLI comparator framework.

## Risks and Edge Cases

Risks include policy-name matching drift, warning text changes for non-empty directories, inherited versus explicit policy confusion, allowing `-replicate` with `-policy`, disabled policy display regressions, global policy state leaking across tests, codec registry differences by runtime, and exact regex assumptions for formatted `ls -e`/`count -e` columns.

## Test Signals

Signals include expected help text, policy set/unset/get messages, non-empty directory warnings, `NoECPolicySetException`, policy-list entries and `State=DISABLED`, add-policy success/failure messages, idempotent enable/disable strings, invalid-argument diagnostics, codec listing header, and regex matches showing EC policy columns in `count` and `ls`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testErasureCodingConf.xml -->
