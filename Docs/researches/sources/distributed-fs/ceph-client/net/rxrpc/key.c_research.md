# sources/distributed-fs/ceph-client/net/rxrpc/key.c

## Purpose
`key.c` implements the Linux key type for RxRPC client keys. It parses legacy v1 and AFS/YFS XDR token payloads, stores rxkad/rxgk token lists, exposes key descriptions/readback, requests socket keys by description, and creates server-side data/null keys.

## Important APIs and functions
- `key_type_rxrpc` registers the `rxrpc` key type with preparse, destroy, describe, and read operations.
- `rxrpc_preparse_xdr_rxkad()` parses RxKAD XDR tokens.
- `rxrpc_preparse_xdr_yfs_rxgk()` parses YFS-RxGK XDR tokens.
- `rxrpc_preparse_xdr()` validates the AFS token container and dispatches token parsing.
- `rxrpc_preparse()` handles empty no-security keys, XDR payloads, and legacy v1 rxkad payloads.
- `rxrpc_request_key()` requests a socket key by user-supplied description.
- `rxrpc_get_server_data_key()` builds an internal rxkad server data key from a session key.
- `rxrpc_get_null_key()` creates an instantiated no-security key.
- `rxrpc_read()` serializes AFS keys back to XDR form.

## Control flow
Key instantiation calls `rxrpc_preparse()`. For non-empty payloads larger than the XDR threshold, it first attempts XDR parsing. XDR parsing validates flags, printable cell name, token count, token lengths, padding, and supported security indices, then appends parsed tokens to the preparsed payload list. If not XDR, the v1 path validates version, security index, ticket length, allocates an rxkad token, copies session key/ticket fields, and sets key expiry.

## State and persistence behavior
Key payload data is a linked list of `struct rxrpc_key_token` plus a token count in `payload.data[1]`. Tokens own allocated rxkad or rxgk data, including padded rxgk ticket storage for direct XDR encoding. `prep->expiry` is reduced to token expiry. Destroy and failed preparse paths free token lists carefully.

## Dependencies and integration points
This file depends on Linux keyrings, network-domain key lookup, AFS token format constants, rxkad/rxgk structures from key headers, socket setup, server security/keying paths, and security modules that consume `rxrpc_key_token`.

## Risks
Parsing is exposed to userspace key payloads, so length, padding, printable cell, expiry, supported enctype/security, and overflow checks are important. `rxrpc_read()` intentionally refuses non-`afs@` descriptions and suppresses secret material when `no_leak_key` is set. Error paths must free partially allocated nested token data.

## Test signals
Test empty/null keys, valid legacy rxkad, valid XDR rxkad, valid XDR yfs-rxgk, unsupported token types, malformed lengths/padding, expired rxgk tokens, oversize tickets/keys, `rxrpc_read()` sizing and encoding, no-leak readback, socket key request errors, and server data key creation.
