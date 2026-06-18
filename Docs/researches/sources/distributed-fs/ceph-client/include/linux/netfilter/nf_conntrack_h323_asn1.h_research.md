# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_h323_asn1.h

## Purpose
This header declares the compact BER/PER decoder interface used by the H.323 conntrack/NAT helper. It decodes only the subset of H.225/H.235/H.245 objects needed for NAT and expectation handling.

## Important APIs, Types, and Functions
It defines `Q931`, whose message type enum includes Q.931 signaling messages and whose `UUIE` member is `H323_UserInformation`. Return codes are `H323_ERROR_NONE`, `H323_ERROR_STOP`, `H323_ERROR_BOUND`, and `H323_ERROR_RANGE`. Decode entry points are `DecodeRasMessage()`, `DecodeQ931()`, and `DecodeMultimediaSystemControlMessage()`.

## Control Flow
The H.323 helper passes packet payload buffers and sizes into the decoder. Successful decode populates static C structures from `nf_conntrack_h323_types.h`; stop/range/bound errors tell the helper whether parsing finished early or failed due to bounds/range checks. The decoder avoids allocation and is designed for packet-path use.

## State and Persistence
No persistent state is declared. Decoded objects are caller-provided stack or per-packet structures. The comments state the decoder uses static object descriptions but remains thread-safe and allocation-free.

## Dependencies and Integration Points
It depends on kernel integer types and generated H.323 type definitions. It integrates with H.323 conntrack parsing and NAT rewrite code.

## Risks
The decoder is deliberately incomplete: at most 30 fast-start entries and IPv4-only address support are documented limitations. Boundary and range errors must be treated as untrusted input handling, not normal success. ASN.1 schema drift can break parsing of newer endpoints.

## Test Signals
Decode valid/invalid RAS, Q.931, and H.245 messages; exercise buffer truncation, range violations, maximum fast-start entries, malformed PER lengths, and concurrent decode calls under packet load.
