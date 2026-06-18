# sources/distributed-fs/ceph-client/include/net/tipc.h

## Purpose

`tipc.h` defines a small TIPC header helper for receive packet steering. It extracts an RPS key from a basic TIPC header, using source node identity for normal traffic and randomization for keepalive probe traffic.

## Important APIs, types, and functions

The file defines `KEEPALIVE_MSG_MASK`, `struct tipc_basic_hdr` containing four big-endian words, and `tipc_hdr_rps_key()`. The helper inspects word 0 and returns word 3 unless the message looks like a keepalive.

## Control flow

Receive-side steering code calls `tipc_hdr_rps_key()` with a parsed TIPC basic header. For normal messages the source node field gives stable flow affinity. For link keepalive/probe messages the helper generates random bytes so probes and replies are spread across CPUs instead of concentrating on a single source key.

## State and persistence behavior

The header owns no persistent state. Random keepalive keys are generated per call and do not persist.

## Dependencies and integration points

It depends on `linux/random.h`, endian conversion, and TIPC message layout. It integrates with network receive hashing/RPS and TIPC link protocol message handling.

## Risks and test signals

Risks include incorrect mask constants causing normal traffic to be randomized or keepalives to be pinned, wrong endian handling, and assuming the four-word header is present before calling. Tests should cover normal message keys, keepalive probe/probe-reply recognition, CPU distribution for keepalives, and short-packet validation in callers.
