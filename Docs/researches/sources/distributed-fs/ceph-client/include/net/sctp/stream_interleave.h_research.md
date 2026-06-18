# sources/distributed-fs/ceph-client/include/net/sctp/stream_interleave.h

## Purpose
This header defines the pluggable SCTP stream-interleaving operations used to support classic DATA/SSN and interleaved I-DATA/MID/FSN formats.

## Important APIs, Types, And Functions
`struct sctp_stream_interleave` contains chunk/header lengths and callbacks for data chunk creation, assignment, validation, event creation, TSN/FSN handling, FWD-TSN generation/skip, and stream sequence skipping. `sctp_stream_interleave_init()` selects/initializes the stream interleave mode on an `sctp_stream`.

## Control Flow
Send paths use the active interleave ops to build DATA or I-DATA chunks and assign stream sequence metadata. Receive and ULP queue paths use validation, event creation, and reassembly helpers appropriate to the negotiated interleaving capability.

## State And Persistence
The persistent selector is `sctp_stream::si`; stream in/out entries hold either SSN or MID/MID_UO/FSN state depending on mode.

## Dependencies And Integration Points
It integrates with `structs.h` stream definitions, ULP queue reassembly, PR-SCTP FWD-TSN handling, and association capability negotiation (`intl_capable`).

## Risks And Test Signals
Risks include mixing SSN and MID state, wrong chunk length calculations, reassembly ordering bugs, and FWD-TSN skip errors. Test signals include interleaving negotiation, fragmented unordered/ordered messages, classic non-interleaved fallback, and stream reset with I-DATA traffic.
