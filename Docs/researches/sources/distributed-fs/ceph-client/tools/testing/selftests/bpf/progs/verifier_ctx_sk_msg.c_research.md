# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ctx_sk_msg.c

## Purpose

`verifier_ctx_sk_msg.c` verifies allowed `sk_msg_md` context fields and direct packet access rules for SK_MSG-style programs. It checks valid metadata reads, rejects invalid width and offset accesses, and validates packet data/data_end bounds reasoning.

## Important APIs, Types, and Functions

The file uses `SEC("sk_msg")` and two `SEC("sk_skb")` programs. Test functions cover `family`, IPv4 and IPv6 address fields, remote and local ports, `size`, and packet buffer reads/writes. Metadata macros record success or expected `invalid bpf_context access` failures. The assembly reads context offsets directly rather than using C field names.

## Control Flow

The valid metadata programs read fields at verifier-approved offsets and return. Negative tests attempt a 64-bit read of the 32-bit `size` field, read past the end of the context, or use an invalid offset. Packet tests obtain data and data_end from ctx, check ranges, then read or write packet bytes. The overlapping-check case performs multiple bounds checks that together establish safe direct packet access.

## State and Persistence Behavior

There are no maps. Runtime packet content is transient; verifier state tracks ctx field permissions, packet pointer ids, packet range proofs, and direct-write permission for SK_MSG.

## Dependencies and Integration Points

The file integrates with sk_msg/sk_skb program-type context access callbacks and packet-access verifier logic. It is relevant to sockmap/sk_msg infrastructure because accepted programs can inspect and mutate message data.

## Risks and Test Signals

Risks are accepting context reads at wrong width/offset, rejecting valid SK_MSG metadata fields, or losing range information across overlapping packet checks. Test signals are all valid field accesses loading successfully, the three invalid context reads failing with `invalid bpf_context access`, and packet read/write cases passing only after appropriate data_end checks.
