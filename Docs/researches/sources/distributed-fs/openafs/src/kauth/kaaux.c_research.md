# sources/distributed-fs/openafs/src/kauth/kaaux.c

## Purpose
Implements XDR serializers for kauth counted byte-string structures used by RPC interfaces: `ka_CBS` and `ka_BBS`.

## Important APIs, Types, And Functions
The exported functions are `xdr_ka_CBS` and `xdr_ka_BBS`. They operate on `XDR`, `struct ka_CBS`, and `struct ka_BBS`; both enforce `MAXBS` of 2048 bytes to avoid excessive allocation.

## Control Flow
For `XDR_FREE`, each function frees `SeqBody`. For encode, `ka_CBS` emits `SeqLen` then opaque bytes, while `ka_BBS` emits `MaxSeqLen`, `SeqLen`, and opaque bytes. For decode, each function reads lengths, rejects negative or over-limit values, validates supplied preallocated buffers when `SeqBody` is non-NULL, allocates a new buffer otherwise, updates the length fields, and decodes opaque data.

## State And Persistence
The functions only allocate or free memory referenced by the caller-provided structures. There is no global or durable state.

## Dependencies And Integration Points
They depend on Rx XDR helpers and `afs/kauth.h` generated structures. They are called by rxgen-generated KA RPC marshalling paths for authentication, password-change, ticket, and answer byte buffers.

## Risks And Test Signals
Important risks are allocation failure not being explicitly checked after `malloc`, callers expecting `SeqBody` to be null after `XDR_FREE`, and exact max-size compatibility with generated RPC expectations. Test signals include encode/decode round trips, oversized and negative length rejection, preallocated-buffer decode rejection when too small, `XDR_FREE` cleanup, and zero-length body handling.
