# sources/distributed-fs/ceph-client/sound/firewire/packets-buffer.h

## Purpose

This header declares the shared ISO packet buffer abstraction for FireWire sound drivers.

## Important APIs, types, and functions

`struct iso_packets_buffer` combines a FireWire `fw_iso_buffer` with an array of per-packet descriptors containing a CPU pointer and byte offset. It declares `iso_packets_buffer_init()` and `iso_packets_buffer_destroy()`.

## Control flow

There is no executable control flow in this header. It defines the lifecycle contract: initialize with a unit, count, maximum packet size, and DMA direction; destroy with the same unit context.

## State and persistence behavior

State persists in the caller-owned struct. Packet descriptors point into pages owned by the embedded `fw_iso_buffer`.

## Dependencies and integration points

It includes DMA mapping and FireWire headers and is implemented by `packets-buffer.c`. It is a lower-level utility beneath protocol-specific stream code.

## Risks and test signals

Risks are ABI/structure changes affecting consumers and misuse after failed initialization. Compile tests across FireWire modules and runtime ISO buffer allocation tests are the best signals.
