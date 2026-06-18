# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_dump.h

## Purpose
Defines the etnaviv devcoredump file section format and declares the core dump entry point.

## Important APIs, Types, and Functions
Defines magic `ETDUMP_MAGIC`, section type enum values (`REG`, `MMU`, `RING`, `CMD`, `BOMAP`, `BO`, `END`), `struct etnaviv_dump_object_header`, `struct etnaviv_dump_registers`, and `etnaviv_core_dump()`.

## Control Flow
No executable flow. `etnaviv_dump.c` writes arrays of these headers and data sections for userspace tools to decode.

## State and Persistence
The structures define persistent dump binary layout exposed through devcoredump.

## Dependencies and Integration Points
Included by dump implementation and scheduler hang handling. Consumers outside the kernel can parse these records.

## Risks
Changing header layout or enum values can break existing dump parsers. Endianness fields are explicitly little-endian and must be populated correctly.

## Test Signals
Compile-time layout usage, devcoredump parser compatibility, and generated dump inspection validate this contract.
