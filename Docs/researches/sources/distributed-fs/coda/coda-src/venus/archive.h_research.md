# sources/distributed-fs/coda/coda-src/venus/archive.h

## Purpose
This header declares the Venus archive writer format constants, selected archive type, and public writer functions.

## Important APIs, Types, and Functions
Constants `TAR_TAR`, `TAR_USTAR`, `CPIO_ODC`, and `CPIO_NEWC` select the output format. `archive_type` is an extern global. `archive_write_entry`, `archive_write_data`, and `archive_write_trailer` form the archive-writing API.

## Control Flow
There is no runtime flow in the header. Callers set `archive_type`, emit entries and data in archive order, and finish with a trailer.

## State and Persistence Behavior
The header exposes mutable process-global archive format state. The implementation writes persistent archive files through `FILE *` streams.

## Dependencies and Integration Points
It depends on `<sys/types.h>` and `<stdio.h>` and is included by Venus CML/repair archive code.

## Risks and Test Signals
Risks are global format races and callers forgetting the trailer. Compile tests should include both C and C++ consumers, and integration tests should validate every format option configured by Venus startup.
