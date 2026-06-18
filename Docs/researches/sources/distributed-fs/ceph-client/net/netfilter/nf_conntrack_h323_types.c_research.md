# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_h323_types.c

## Purpose
This generated file describes the subset of H.225/H.245 ASN.1 structures that the H.323 helper decodes. It is a schema table collection, not normal procedural code: each `static const struct field_t` array maps PER fields onto C structure offsets, decode/skip/stop behavior, bounds, optionality, extension handling, and nested type tables. The decode engine included elsewhere consumes these tables to populate `Q931`, `RasMessage`, `MultimediaSystemControlMessage`, and related structures used by `nf_conntrack_h323_main.c`.

## Important APIs, Types, And Tables
The key type is `struct field_t` and the macros used inside table entries: `FNAME`, scalar kinds such as `INT`, `OCTSTR`, `BOOL`, `OID`, `SEQ`, `SEQOF`, `CHOICE`, size encodings such as `FIXD`, `BYTE`, `WORD`, `SEMI`, `CONS`, and actions/flags such as `DECODE`, `SKIP`, `STOP`, `OPT`, `EXT`, and `OPEN`. This file does not export symbols directly, but it provides the descriptor tables referenced by generated decoder entry points.

Important decoded tables include `_TransportAddress`, `_H245_TransportAddress`, `_H2250LogicalChannelParameters`, `_OpenLogicalChannel`, `_OpenLogicalChannelAck`, `_H323_UU_PDU`, `_H323_UserInformation`, and `_RasMessage`. These are the tables that expose embedded IPv4/IPv6 addresses, ports, H.245 addresses, media/control channel addresses, Q.931 message bodies, fastStart arrays, and RAS registration/admission/location fields to the runtime helper.

## Control Flow
Control flow is data-driven. A decoder begins at a top-level descriptor such as `_RasMessage`, `_H323_UserInformation`, or `_MultimediaSystemControlMessage`, reads PER bits, selects CHOICE arms, walks SEQUENCE fields in order, and either decodes data into the destination structure or skips/stops parsing for fields that are not relevant to conntrack. For example, `_Setup_UUIE` decodes `h245Address`, `destCallSignalAddress`, `sourceCallSignalAddress`, and `fastStart`; `_RegistrationRequest` decodes `callSignalAddress`, `rasAddress`, and `timeToLive`; `_AdmissionConfirm` decodes `destCallSignalAddress`.

The schema deliberately stops early for many complex or security-related fields after the addresses needed by conntrack are available. This keeps the helper focused on dynamic endpoint discovery rather than fully validating H.323 semantics.

## State And Persistence
All objects in this file are immutable static constants. No per-connection state is stored here. Persistence is only the compiled-in schema layout, which must remain ABI-consistent with the C structs declared in the H.323 header and with the generated decoder logic.

## Dependencies And Integration Points
The file depends on H.323 struct definitions and decoder macros usually included by the translation unit or generated companion. Its primary consumer is `nf_conntrack_h323_main.c`, whose processing functions rely on option bits, choice enums, decoded counts, and offset-filled address fields. Any mismatch between these tables and the struct definitions will corrupt parsed data or make the helper miss expectations.

## Risks
The dominant risk is generated-schema drift: offsets, count limits, extension flags, or decoded/skipped fields must match both the ASN.1 source and C structs. Because packet input is untrusted, malformed PER can exercise every bound and extension path. Many fields are skipped or stopped, so adding helper behavior for a new H.323 field requires changing the descriptor action from `SKIP`/`STOP` to `DECODE` and ensuring the destination structure has storage. Sequence-of bounds such as fastStart and address arrays are also security-relevant because they bound loops in the main helper.

## Test Signals
Decode tests should cover IPv4 and IPv6 `TransportAddress`, H.245 unicast media and media-control addresses, Q.931 setup/connect/alerting/facility/progress with fastStart and tunneled H.245 controls, RAS RRQ/RCF/URQ/ARQ/ACF/LRQ/LCF/IRR messages, extension fields before and after decoded fields, oversized sequence-of inputs, malformed CHOICE indexes, and out-of-bound PER lengths. Runtime tests should verify that the main helper sees decoded option bits and counts exactly as expected.
