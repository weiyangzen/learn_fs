# sources/distributed-fs/ceph-client/net/rxrpc/insecure.c

## Purpose
`insecure.c` implements the `rxrpc_no_security` security module for anonymous/no-security RxRPC calls. It provides no-op connection/call crypto while still fitting the common `struct rxrpc_security` interface.

## Important APIs and functions
- `rxrpc_no_security` is the exported security module descriptor for `RXRPC_SECURITY_NONE`.
- `none_alloc_txbuf()` allocates plain DATA tx buffers sized up to one jumbo payload.
- `none_secure_packet()` sets plaintext packet length and marks full-size packets as jumbo-capable.
- `none_verify_packet()` marks received packets verified.
- `none_validate_challenge()` and `none_verify_response()` abort if challenge/response packets appear on a no-security connection.

## Control flow
When a call or connection chooses no security, output uses `alloc_txbuf()` and `secure_packet()` without adding crypto headers or checksums, input marks DATA verified immediately, and challenge/response paths reject protocol-inconsistent security handshakes.

## State and persistence behavior
The module stores no per-connection or per-call crypto state. Init, exit, free-call-crypto, and clear hooks are no-ops. Verification sets only `RXRPC_RX_VERIFIED` in skb private flags.

## Dependencies and integration points
It depends on common txbuf allocation, connection abort handling, skb private metadata, and the security lookup/selection code elsewhere. It is the default security pointer for newly allocated connections.

## Risks
The main risk is accidentally accepting secured-control packets on a no-security connection; this implementation aborts such packets as protocol errors. Plaintext packets depend on higher layers to enforce any minimum security policy.

## Test signals
Test anonymous calls, full-size plaintext jumbo eligibility, DATA verification flagging, CHALLENGE rejection, RESPONSE rejection, and no-op cleanup during call/connection teardown.
