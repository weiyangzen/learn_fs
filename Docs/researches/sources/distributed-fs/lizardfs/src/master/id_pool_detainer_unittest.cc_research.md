# sources/distributed-fs/lizardfs/src/master/id_pool_detainer_unittest.cc

Purpose: verifies basic `IdPoolDetainer` allocation, release, null-id behavior, mark-as-acquired, detention, iteration, and expiry.

Important APIs/types/functions: `TestGet` drains the pool; `TestPut` repeatedly acquire/releases; `TestIdIsNull` and `TestPutNull` check null id handling; `TestIfAllDifferent` checks uniqueness and immediate reuse when release count is zero/base behavior; `TestMarkAsAcquired` reserves specific ids; `TestIfDetained` releases a set into detention, verifies later acquires avoid them, iterates detained ids, then releases expired detention.

Control flow: tests instantiate `IdPoolDetainer<uint32_t,uint32_t>` with small pool sizes and deterministic timestamps, then assert pool counts and returned ids.

State and persistence behavior: no disk persistence tested; in-memory detention only.

Dependencies/integration: depends on GoogleTest and the detainer template.

Risks and test signals: tests do not cover detention cap overflow, Judy backend, bucket boundary exactness, duplicate release into detention, or `detain()` API. They provide good coverage for common inode-pool behavior.
