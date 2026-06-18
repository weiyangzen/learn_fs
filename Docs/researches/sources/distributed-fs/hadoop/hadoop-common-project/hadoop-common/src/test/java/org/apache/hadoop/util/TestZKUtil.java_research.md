# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestZKUtil.java

Purpose: Unit tests for ZooKeeper utility parsing in `ZKUtil`. The file covers ACL string parsing, auth string parsing, permission removal, and configuration indirection through `@file` references.

Important APIs/types/functions: Tests call `ZKUtil.parseACLs()`, `parseAuth()`, `removeSpecificPerms()`, and `resolveConfIndirection()`. `badAcl()` verifies `BadAclFormatException` message text. `ZKAuthInfo` and ZooKeeper `ACL`/`Perms` are the primary returned types.

Control flow: Empty and null ACL/auth strings must produce empty lists. Invalid ACL forms are passed to `badAcl()` to assert exact diagnostics. Valid ACLs parse comma-separated SASL identities with permission characters into `ACL` objects. Valid auth strings split only the first scheme/data separator so `scheme2:user:pass` preserves `user:pass`. Conf indirection reads a UTF-8 test file when the value starts with `@`, while plain strings and null are returned unchanged.

State and persistence behavior: `TEST_FILE` is under `GenericTestUtils.getTempPath("TestZKUtil")`; the test creates parent directories and writes content through Guava `Files.asCharSink`. No ZooKeeper server state is used. Permission state is represented only by integer bitmasks.

Dependencies and integration points: Depends on Hadoop `ZKUtil`, ZooKeeper ACL classes, Hadoop common configuration defaults, Guava-shaded file helpers, and JUnit. The parsing behavior feeds ZooKeeper-backed Hadoop coordination services and security configuration.

Risks: Exact exception-message assertions make diagnostics part of the test contract. `resolveConfIndirection()` reads local files from config values, so path handling and file-not-found messages matter. The ACL parser tests only SASL-style examples and a small invalid set, not digest/world/ip schemes.

Test signals: Empty-list returns, exact ACL permissions and identity fields, auth byte data preservation, removed `CREATE` bit, resolved file content, and `FileNotFoundException` prefix for missing indirection files are core signals.
