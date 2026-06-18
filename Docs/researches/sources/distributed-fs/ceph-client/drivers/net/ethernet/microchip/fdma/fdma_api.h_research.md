# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/fdma_api.h

## Purpose
This header defines the common data structures, bit encoders, inline helpers, callbacks, and function prototypes for Microchip Frame DMA descriptors.

## Important APIs, Types, and Functions
`struct fdma_db` stores one data pointer and status word. `struct fdma_dcb` stores a next pointer, info word, and up to `FDMA_DB_MAX` DBs. `struct fdma_ops` supplies the dataptr and nextptr callbacks. `struct fdma` contains caller private data, DCB memory, DMA base, allocation size, active DCB/DB indices, descriptor dimensions, channel ID, and callbacks.

Inline helpers advance and reset indices (`fdma_dcb_advance`, `fdma_db_advance`, `fdma_db_reset`), test descriptor state (`fdma_dcb_is_reusable`, `fdma_db_is_done`, `fdma_has_frames`, `fdma_is_last`), access current or indexed DCB/DB objects, decode DB length, set DCB length, compute default next pointers, and compute contiguous data buffer DMA/virtual addresses with `XDP_PACKET_HEADROOM`.

## Control Flow and State
The header supports ring-style consumption by keeping `dcb_index` and `db_index` in `struct fdma`. Callers inspect `fdma_has_frames`, process the current DB/DCB, advance indices, and use `fdma_dcb_is_reusable` when a DCB contains multiple DBs. The default pointer helpers assume a contiguous descriptor-and-buffer layout.

## Dependencies and Integration Points
It includes Linux bit, Ethernet, and type definitions, and uses DMA address types, `GENMASK`, `BIT`, `XDP_PACKET_HEADROOM`, and `PAGE_SIZE`-aligned allocation assumptions from the implementation. Switch drivers include this header, often with an include path from their Makefiles.

## Risks
Most helpers do no bounds checks, so bad indices corrupt adjacent descriptor memory. `fdma_dcb_len_set` overwrites `info` rather than masking in the length, which is safe only if callers intend to replace all info bits. Contiguous pointer helpers are valid only when DCBs and data buffers are allocated in the combined layout described by `fdma_get_size_contiguous`.

## Test Signals
Compile users should cover all inline helpers. Runtime tests should exercise multi-DB advancement, descriptor done detection, contiguous pointer arithmetic, XDP headroom alignment, and `FDMA_DCB_STATUS_*`/`FDMA_DCB_INFO_*` bit encoders.
