# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hldio.c

## Purpose
This file implements optional NVMe direct I/O from storage into HabanaLabs PCI P2P memory, under strict assumptions: P2PDMA-capable kernel/topology, `O_DIRECT`, page-aligned reads, non-sparse files, compatible block devices, and synchronous read support.

## Important APIs, Types, And Functions
`hl_dio_ssd2hl()` is the public synchronous SSD-to-device path. `hl_p2p_region_init()` and `hl_p2p_region_fini_all()` manage published P2P regions. `hl_dio_start()`/`hl_dio_stop()` manage inflight counters and enablement. Internal helpers validate file descriptors, count inflight I/O, translate device VA to P2P pages via `hl_mmu_va_to_pa()`, and build `bio_vec` iterators for `read_iter()`.

## Control Flow
An I/O request allocates a descriptor, registers and validates the fd, checks page alignment, acquires the I/O path and context reference, allocates `bio_vec` entries, translates each device page into a P2P page, calls file `read_iter()`, then releases vector memory, context reference, and fd. Stop disables new I/O and polls until per-CPU inflight counters drain.

## State And Persistence
State lives in `hdev->hldio`: P2P regions, region count, per-CPU inflight counters, and `io_enabled`. Each I/O temporarily holds file and context references. P2P region memory persists until device teardown.

## Dependencies And Integration Points
It depends on block files, PCI P2PDMA, HabanaLabs MMU translation, context refcounting, and `hldio.h`. It integrates with device setup/teardown and memory mappings that place device VAs inside configured P2P regions.

## Risks
The `iov_iter_bvec()` call uses one segment while allocating one `bio_vec` per page, which is a likely multi-page transfer risk. `vzalloc()` in the I/O path is expensive. `io_enabled` is not atomic. Sparse/topology support is intentionally limited.

## Test Signals
Test aligned/unaligned requests, non-`O_DIRECT` and sparse files, unsupported P2PDMA, failed VA translation, multi-page reads, stop during inflight reads, and partial P2P init cleanup.
