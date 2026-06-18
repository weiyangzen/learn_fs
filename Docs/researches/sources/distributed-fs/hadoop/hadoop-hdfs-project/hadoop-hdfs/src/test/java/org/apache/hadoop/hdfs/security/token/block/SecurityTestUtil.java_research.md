# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/token/block/SecurityTestUtil.java

Purpose: Test helper exposing block token expiration checks and lifetime mutation for security tests.

Important APIs/types/functions: `SecurityTestUtil`, `isBlockTokenExpired(Token<BlockTokenIdentifier>)`, `setBlockTokenLifetime(BlockTokenSecretManager, long)`, `BlockTokenSecretManager.isTokenExpired`, and `BlockTokenSecretManager.setTokenLifetime`.

Control flow: Both helpers delegate directly to `BlockTokenSecretManager`: one checks if a token is expired, the other sets token lifetime on a supplied manager.

State and persistence behavior: No persistent state. `setBlockTokenLifetime` mutates in-memory secret-manager configuration for tests.

Dependencies and integration points: Used by HDFS block-token tests needing access to expiration behavior without duplicating secret-manager internals.

Risks: Lifetime mutation can leak between tests if managers are reused. This should remain test-scope utility code.

Test signals: No direct assertions; downstream tests use it to force or observe block-token expiration.
