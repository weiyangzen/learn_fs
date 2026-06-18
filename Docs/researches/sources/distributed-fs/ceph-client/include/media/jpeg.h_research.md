# sources/distributed-fs/ceph-client/include/media/jpeg.h

## Purpose
Declares shared JPEG marker constants for media drivers.

## Important APIs, Types, and Functions
The header defines marker byte constants for TEM, SOF0, DHT, RST, SOI, EOI, SOS, DQT, DRI, DHP, APP0, and COM.

## Control Flow
Codec or capture drivers compare JPEG marker bytes against these constants while parsing or generating JPEG headers.

## State and Persistence Behavior
No persistent state is owned.

## Dependencies and Integration Points
Integrates V4L2 codec drivers and JPEG-capable capture devices with common marker definitions.

## Risks
Marker constants must match the JPEG bitstream spec; downstream parsers must still handle truncated or malformed buffers safely.

## Test Signals
Compile coverage and codec/capture parser tests for valid headers, truncated buffers, unknown marker skipping, and marker generation.
