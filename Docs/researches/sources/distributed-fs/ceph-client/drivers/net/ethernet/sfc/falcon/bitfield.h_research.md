# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/bitfield.h

## Purpose
`bitfield.h` supplies the Falcon driver with endian-safe bitfield construction, extraction, testing, and modification macros for 32-bit dwords, 64-bit qwords, and 128-bit owords used in Solarflare MMIO registers, descriptors, and DMA-visible structures.

## Important APIs, Types, and Functions
The core data types are `ef4_dword_t`, `ef4_qword_t`, and `ef4_oword_t`, all represented with little-endian integer arrays. Field metadata is expected as `FIELD_LBN` and `FIELD_WIDTH`, consumed by `EF4_LOW_BIT()`, `EF4_WIDTH()`, and `EF4_HIGH_BIT()`. Extraction macros include `EF4_DWORD_FIELD`, `EF4_QWORD_FIELD`, and `EF4_OWORD_FIELD`; population macros include `EF4_POPULATE_DWORD_*`, `EF4_POPULATE_QWORD_*`, and `EF4_POPULATE_OWORD_*`; mutation macros include `EF4_SET_*_FIELD`. Formatting helpers expose `EF4_DWORD_FMT`, `EF4_QWORD_FMT`, and `EF4_OWORD_FMT`.

## Control Flow
There is no function control flow; behavior is macro expansion. The macros split bit ranges across native little-endian elements, convert to CPU endianness for extraction, and convert back for insertion. `BITS_PER_LONG` selects 64-bit or 32-bit implementations to fit architecture efficiency. Variadic-like fixed-arity populate wrappers pad missing fields with `EF4_DUMMY_FIELD`.

## State and Persistence
No global state exists. The macros write directly into caller-provided register/descriptor unions. Because these objects often represent MMIO or DMA structures, correctness persists into hardware-visible state.

## Dependencies and Integration Points
The header depends on Linux fixed-width types, endian conversion helpers, `BITS_PER_LONG`, and `dma_addr_t`. It is included by Falcon hardware code that defines register fields and needs portable access to hardware layouts.

## Risks
Macro arguments may be evaluated multiple times, so callers should pass simple lvalues and constants. Field definitions must be correct and non-overlapping; the helpers do not validate register specifications. Width handling is limited by `EF4_MASK32()`/`EF4_MASK64()` assumptions, and invalid widths or shifts can become compile-time or runtime undefined behavior. Endianness annotations are force-cast in all-ones/zero tests, so sparse warnings should be monitored carefully.

## Test Signals
Build coverage across 32-bit and 64-bit architectures is important because different macro variants are selected. Unit-style compile tests can populate and extract known 128-bit patterns, including fields crossing 32-bit and 64-bit boundaries. Runtime signals include correct descriptor programming, register dumps matching datasheet values, and absence of sparse endian warnings.
