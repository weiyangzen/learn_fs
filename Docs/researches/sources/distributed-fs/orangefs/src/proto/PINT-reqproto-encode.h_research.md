<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-reqproto-encode.h -->
# sources/distributed-fs/orangefs/src/proto/PINT-reqproto-encode.h

## Purpose
Declares the public OrangeFS request protocol encoding API and the carrier structures used for encoded and decoded messages.

## Important APIs, Types, and Functions
Defines `struct PINT_encoded_msg`, `struct PINT_decoded_msg`, `enum PINT_encode_msg_type`, aliases `PINT_DECODE_REQ` and `PINT_DECODE_RESP`, and prototypes for initialize/finalize, encode/decode, release, and max-size calculation. `PINT_encoded_msg` records destination, encoding type, BMI buffer type, buffer/size lists, total size, and internal single-buffer stub fields. `PINT_decoded_msg` records decoded buffer pointer, encoding type, current pointer, and an inline union for request or response storage.

## Control Flow
Callers initialize the subsystem, call `PINT_encode` before BMI send, release encoded buffers after send, call `PINT_decode` after receive, consume `target_msg->buffer` as request or response, then call `PINT_decode_release`.

## State and Persistence
The structs carry transient ownership and pointer state. Decoded message storage uses an inline request/response union, while nested variable-length decoded fields may point into the receive buffer or heap memory managed by release hooks.

## Dependencies and Integration Points
Includes `pvfs2-req-proto.h` and `bmi.h`. It is consumed by client/server protocol layers and implemented by `PINT-reqproto-encode.c` plus modules such as `PINT-le-bytefield.c`.

## Risks
Callers must respect release pairing and must not free concrete buffers manually. `buffer_list`, `size_list`, and `alloc_size_list` may point to internal stubs for the single-buffer encoder, so copying the struct by value can create aliasing bugs. `PINT_DECODE_REQ` equals `PINT_ENCODE_REQ`, so callers must pass the correct direction despite shared enum values.

## Test Signals
Compile all users against the header, verify ABI expectations of `PINT_encoded_msg`/`PINT_decoded_msg`, test release pairing with both request and response messages, and ensure decode consumers do not outlive input receive buffers for pointer-backed strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-reqproto-encode.h -->
