# sources/distributed-fs/ceph-client/tools/include/tools/be_byteshift.h

## Purpose
Provides unaligned big-endian load/store helpers for 16-, 32-, and 64-bit integers in user-space tools that cannot rely on direct unaligned typed memory access.

## Important APIs, Types, and Functions
Defines internal byte-pointer helpers `__get_unaligned_be16/32/64()` and `__put_unaligned_be16/32/64()`, plus public `void *` wrappers `get_unaligned_be16/32/64()` and `put_unaligned_be16/32/64()`.

## Control Flow, State, and Persistence
All helpers are `static inline` and deterministic. Reads assemble values with shifts from `uint8_t` bytes in network/big-endian order; writes decompose high-order bytes first. No state is stored.

## Dependencies and Integration
Depends only on `<stdint.h>`. It integrates with binary parsers, perf data readers, BPF tooling, and protocol/file-format code that needs endian-stable unaligned access.

## Risks and Test Signals
Risks include passing too-short buffers, relying on integer promotion without preserving unsigned byte semantics, and confusing these helpers with host-endian conversion. Useful tests round-trip known byte arrays such as `01 02 03 04`, exercise unaligned offsets, and compare against `htobe*`/`be*toh` expectations.
