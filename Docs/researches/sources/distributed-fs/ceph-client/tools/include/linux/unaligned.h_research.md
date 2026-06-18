# sources/distributed-fs/ceph-client/tools/include/linux/unaligned.h

## Purpose
Implements endian-aware unaligned load/store helpers for tool code that parses binary kernel, filesystem, network, or tracing data without assuming pointer alignment.

## APIs, Types, and Functions
The public macros are `get_unaligned()` and `put_unaligned()`. Inline helpers cover little-endian and big-endian 16/32/64-bit access, 24-bit access in both byte orders, big-endian 48-bit put/get, and private byte assembly helpers such as `__get_unaligned_be24()` and `__put_unaligned_le24()`.

## Control Flow, State, and Persistence
Control flow is straight-line byte loading, shifting, endian conversion, and byte storing. The helpers mutate only the caller-provided memory for put operations and retain no state. Reads are deterministic for the bytes at the supplied address and do not perform bounds checks.

## Dependencies and Integration
Depends on `linux/types.h`, `asm/byteorder.h`, and `linux/unaligned/packed_struct.h` for CPU-endian unaligned access primitives. It integrates with tools that decode packed structures where direct typed dereference may fault or violate strict alignment.

## Risks and Test Signals
Risks are caller-provided buffer underruns/overruns, wrong endian helper selection, and assuming 24/48-bit helpers sign-extend. Test signals are byte-pattern round trips for all widths and endian modes, unaligned addresses at every alignment offset, UBSan/ASan runs for parser callers, and cross-endian build coverage.
