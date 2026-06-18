# sources/distributed-fs/ceph-client/net/ceph/auth_x.h

## Purpose
Declares private CephX backend data structures and the `ceph_x_init()` initializer.

## Important APIs, Types, and Functions
`struct ceph_x_ticket_handler` stores one service ticket in an rbtree node, including service id, session key, `have_key`, secret id, ticket blob, renewal time, and expiration time. `struct ceph_x_authorizer` wraps the generic authorizer, a cloned session key, encoded buffer, service id, nonce, secret id, and aligned 128-byte encryption scratch buffer. `struct ceph_x_info` stores the client secret, starting state, server challenge, key bitmask, ticket-handler tree, and reusable AUTH authorizer. `CEPHX_AU_ENC_BUF_LEN` sizes small encrypted blobs.

## Control Flow
No executable flow. These structs are allocated and mutated by `auth_x.c` under the generic auth mutex.

## State and Persistence
All declared state is per-auth-client or per-authorizer memory. Ticket blobs are refcounted Ceph buffers; crypto keys require explicit destruction.

## Dependencies and Integration Points
Includes generic Ceph auth types, crypto private declarations, rbtree support, and CephX wire protocol structures. The layout is internal to libceph.

## Risks
The fixed 128-byte authorizer encryption scratch buffer must remain large enough for all encrypted challenge/signature blocks. Adding key usages beyond three requires updating `struct ceph_crypto_key` transform capacity in `crypto.h`. State lifetime requires matching cleanup in `ceph_x_destroy_authorizer()` and `ceph_x_destroy()`.

## Test Signals
Compile with CephX enabled, KASAN/KMEMLEAK tests for ticket and authorizer lifetime, encrypted blob size tests against `CEPHX_AU_ENC_BUF_LEN`, and reset/destroy tests with multiple service tickets in the rbtree.
