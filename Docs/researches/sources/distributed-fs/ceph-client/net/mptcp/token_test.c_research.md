# sources/distributed-fs/ceph-client/net/mptcp/token_test.c

## Purpose
This file is the KUnit suite for MPTCP token management. It builds minimal fake request sockets, TCP inet connection sockets, subflow contexts, and MPTCP sockets to validate token registry lifecycle behavior without a real network handshake.

## APIs, Types, and Functions
Helpers are `build_req_sock()`, `build_icsk()`, `build_ctx()`, and `build_msk()`. Test cases are `mptcp_token_test_req_basic()`, `mptcp_token_test_msk_basic()`, `mptcp_token_test_accept()`, and `mptcp_token_test_destroyed()`. The suite is registered as `mptcp-token` with `kunit_test_suite()`.

## Control Flow
The request test initializes a fake `mptcp_subflow_request_sock`, creates a request token, checks that the token is nonzero but not visible as an established socket, then destroys the request. The active socket test attaches a fake subflow context to an `inet_connection_sock`, creates a token for the MPTCP socket, checks lookup and refcount behavior, destroys the token, and verifies lookup failure. The accept test transitions a request token into a full MPTCP socket and verifies request destroy becomes a no-op after the move. The destroyed test simulates a race by setting the socket refcount to zero before lookup and expects no socket to be returned.

## State and Persistence
All objects are KUnit-managed heap allocations, but they interact with the real global token hash initialized by the MPTCP token subsystem. Fake sockets set `sk_refcnt`, net namespace, `sk_prot`, and protocol fields only as far as token helpers require.

## Dependencies and Integration
The file depends on KUnit, `protocol.h`, `init_net`, `tcp_prot`, and token helper exports available under `CONFIG_MPTCP_KUNIT_TEST` when built as a module. It directly tests the code in `token.c`.

## Risks
The suite intentionally avoids full TCP/MPTCP socket initialization, so it does not cover RCU grace periods, real request destruction, concurrent bucket mutation, namespace mismatches, token collision retry loops, or protocol accounting in an integrated stack. Fake objects must stay consistent with what token helpers dereference.

## Test Signals
Strong signals are nonzero token creation, expected lookup visibility before and after accept, refcount increments on successful lookup, no-op request destroy after accept, and refusal to return a zero-ref socket.
