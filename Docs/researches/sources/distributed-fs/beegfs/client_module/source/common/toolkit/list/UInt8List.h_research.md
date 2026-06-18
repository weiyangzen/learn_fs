# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt8List.h

## Purpose
Defines a `uint8_t` value list backed by pointer-slot casts.

## Important APIs and control flow
`UInt8List_append` stores the byte value in a pointer slot through `size_t`. Lifecycle, clear, and length delegate to `PointerList`.

## State, dependencies, integration
Used by serialization for compact byte lists. The list owns nodes only and does not allocate separate byte payloads.

## Risks and test signals
Tests should cover zero, 255, clear behavior, and deserialization appending exact byte counts.
