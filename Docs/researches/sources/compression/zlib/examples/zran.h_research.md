# sources/compression/zlib/examples/zran.h

## Purpose
`zran.h` exposes the data structures and API for the random-access deflate index example implemented in `zran.c`.

## Important APIs, Types, and Functions
It defines `point_t`, which stores uncompressed offset, compressed file offset, bit offset, dictionary length, and dictionary bytes. It also defines `struct deflate_index`, containing point count, stream mode, uncompressed length, point list, and reusable `z_stream`. The API surface is `deflate_index_build()`, `deflate_index_extract()`, and `deflate_index_free()`.

## Control Flow, State, and Persistence
The header performs no runtime work. Its comments define the ownership contract: successful builds return an allocated index through `*built`, failed builds return `NULL`, extraction returns byte counts or negative zlib errors, and the caller must eventually free the index.

## Dependencies and Integration Points
It includes `<stdio.h>` and `zlib.h`, so users get `FILE`, `off_t`, `ptrdiff_t`, `size_t`, and `z_stream` through the expected zlib platform layer. It intentionally exposes access-point internals to permit persistence outside this example.

## Risks and Test Signals
Risks are ABI sensitivity and ownership misuse, especially failing to free per-point `window` allocations. Compile and integration tests should verify that applications can build, inspect, extract with, and free a `struct deflate_index` without depending on hidden implementation state.
