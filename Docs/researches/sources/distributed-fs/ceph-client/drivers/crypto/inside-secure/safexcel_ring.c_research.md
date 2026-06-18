# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel_ring.c Research

## Purpose
`safexcel_ring.c` provides descriptor ring allocation and pointer management for the Safexcel EIP197/EIP97 crypto driver. It owns the low-level command descriptor ring (CDR), command shadow token ring, and result descriptor ring (RDR) helpers used by cipher, hash, and other Safexcel algorithm files.

## Important APIs, Types, and Functions
`safexcel_init_ring_descriptors()` allocates coherent DMA memory for CDR, CDR shadow token storage, and RDR using offsets from `priv->config`. It initializes read/write pointers and pre-populates each command descriptor's `atok_lo`/`atok_hi` fields with the DMA address of its shadow token area.

`safexcel_select_ring()` round-robins requests over the configured hardware rings using `atomic_inc_return(&priv->ring_used)`.

Internal helpers `safexcel_ring_next_cwptr()` and `safexcel_ring_next_rwptr()` reserve the next command or result slot, detect ring-full conditions, update write pointers with wraparound, and return `ERR_PTR(-ENOMEM)` when no descriptor is available. `safexcel_ring_next_rptr()` consumes the next result descriptor and returns `ERR_PTR(-ENOENT)` when the ring is empty. `safexcel_ring_curr_rptr()`, `safexcel_ring_first_rdr_index()`, and `safexcel_ring_rdr_rdesc_index()` expose read pointer/index information to the core request tracking code.

`safexcel_ring_rollback_wptr()` backs up a write pointer after partially constructed requests fail. `safexcel_add_cdesc()` fills a command descriptor with segment flags, data DMA address, packet length, context pointer, and first-descriptor control options. `safexcel_add_rdesc()` fills a result descriptor with destination DMA address, segment flags, result token size, and pessimistic error defaults that hardware clears on success.

## Control Flow
Probe/setup calls `safexcel_init_ring_descriptors()` for each ring. Algorithm send paths reserve one command descriptor per input segment through `safexcel_add_cdesc()` and one result descriptor per output segment through `safexcel_add_rdesc()`. If any reservation fails, the caller rolls back already reserved descriptors with `safexcel_ring_rollback_wptr()`. Completion paths consume descriptors with `safexcel_ring_next_rptr()`.

## State and Persistence
All state is in DMA-coherent ring memory and in-memory read/write pointers inside `struct safexcel_desc_ring`. The ring keeps separate command shadow write pointers because token memory is parallel to command descriptors. State persists only while the driver/device instance is alive.

## Dependencies and Integration Points
The file depends on descriptor layouts and constants from `safexcel.h`, DMA allocation APIs, and bit helpers for 64-bit DMA addresses. It is a shared integration point for Safexcel cipher/hash request builders and core completion code.

## Risks and Edge Cases
Ring-full checks rely on pointer arithmetic over byte-addressed descriptor regions. Offsets must match hardware descriptor sizes supplied by `priv->config`, or pointer wrap and index calculations become wrong. `safexcel_add_cdesc()` deliberately forces first packet length to at least one byte because EIP97 can hang on zero-length input; callers must still use dummy-safe buffers. Rollback must be called the exact number of successful reservations.

## Test Signals
Stress tests should exercise ring wraparound, full-ring backpressure, multi-segment requests, descriptor rollback after induced result-ring exhaustion, empty result-ring reads, zero-length request paths, and mixed cipher/hash traffic over multiple rings.
