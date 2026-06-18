# sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-pkt-decoder.h

## Purpose
Defines Arm SPE packet types, parser return codes, maximum packet/description sizes, header masks, packet index encodings, payload bitfield helpers, event bit positions, operation subclass predicates, and public packet parser/formatter prototypes.

## Important APIs, Types, and Functions
`enum arm_spe_pkt_type` lists BAD, PAD, END, TIMESTAMP, ADDRESS, COUNTER, CONTEXT, OP_TYPE, EVENTS, and DATA_SOURCE packets.
`struct arm_spe_pkt` carries type, index, and payload.
Constants define short and extended header recognition, address indices (`INS`, `BRANCH`, `DATA_VIRT`, `DATA_PHYS`, `PREV_BRANCH`), counter indices, context index extraction, event bit positions, and operation class/subclass decoding.
Public APIs are `arm_spe_pkt_name()`, `arm_spe_get_packet()`, and `arm_spe_pkt_desc()`.

## Control Flow
The implementation uses these masks to classify headers, derive indices, sanitize address payloads, and interpret operation/event payloads. Higher-level decode uses the same event and operation flags to populate records.

## State and Persistence
The header declares no persistent state. All macros are compile-time constants or payload predicates.

## Dependencies and Integration Points
Includes `linux/bitfield.h` for `FIELD_GET`/GENMASK helpers. Included by both the low-level packet decoder and high-level Arm SPE decoder.

## Risks
Macro correctness is architecture-contract critical. New Arm SPE extensions require adding event bits and operation subclass predicates consistently in both the header and description/high-level decoding code. Some macros use similarly named `PKT`/`PKG` identifiers, so maintenance needs careful review.

## Test Signals
Compile-time and byte-fixture tests should validate header masks, index extraction, address metadata extraction, SVE/SME vector-length calculations, GCS subclass detection, event bit positions, and parser return-code handling for bad and incomplete packets.
