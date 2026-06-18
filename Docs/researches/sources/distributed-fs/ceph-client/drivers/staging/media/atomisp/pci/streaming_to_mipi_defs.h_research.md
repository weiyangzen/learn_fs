# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/streaming_to_mipi_defs.h

## Purpose
Defines bit positions for a streaming-to-MIPI word layout.

## Important APIs, Types, and Functions
Macros define valid bits for channels A/B, start/end of line, start/end of frame, channel-id LSB, and data-A LSB.

## Control Flow
No execution. Constants are used by code that packs or decodes synthetic MIPI stream words.

## State and Persistence Behavior
No mutable state; these constants model the persistent bit-level hardware/test protocol.

## Dependencies and Integration Points
No includes. Integrates with AtomISP input-system simulation, test pattern, or stream-to-MIPI conversion code.

## Risks
The definitions are bit-position contracts. Any shift change can mislabel frame boundaries or data bits.

## Test Signals
Bit-packing tests should verify SOL/EOL/SOF/EOF and channel id extraction for generated streaming-to-MIPI words.
