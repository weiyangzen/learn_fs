<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_res.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_res.h

## Purpose
Defines resource-management constants, data structures, doorbell helpers, hardware queue helpers, chip context, stats context, and resource allocation APIs for `bng_re`.

## Important APIs, Types, And Functions
- Queue/PBL constants define pointer indexing, free-slot calculation, maximum PBL pages per level, doorbell validity/epoch/toggle bits, and maximum TQM allocation requests.
- `struct bng_re_reg_desc` describes an MMIO register mapping.
- `struct bng_re_db_info` stores doorbell pointers, associated hardware queue, XID, flags, and toggle.
- Epoch enums define consumer and producer epoch bits for queue wrap tracking.
- `struct bng_re_chip_ctx` caches chip number, hardware stats size, HWRM interface version, and command timeout.
- `struct bng_re_pbl`, `bng_re_sg_info`, `bng_re_hwq_attr`, and `bng_re_hwq` model paged DMA queue backing and runtime queue indices.
- `struct bng_re_stats` stores DMA stats memory, size, and firmware id.
- `struct bng_re_res` ties PCI device, chip context, and device attributes together.
- `bng_re_get_qe()` returns a queue-entry pointer for an index.
- `BNG_RE_INIT_DBHDR()`, `bng_re_ring_db()`, and `bng_re_ring_nq_db()` build and write 64-bit doorbell records.
- `bng_re_hwq_incr_cons()` advances consumer index and toggles epoch on wrap.
- `_is_max_srq_ext_supported()` tests a firmware capability flag.
- Public prototypes expose hardware queue and stats memory allocation/free.

## Control Flow
Inline helpers are used in the firmware event path and queue allocation path. Consumers call `bng_re_get_qe()` to locate entries, process entries, call `bng_re_hwq_incr_cons()` to advance ring state, then ring an NQ/CQ doorbell with `bng_re_ring_nq_db()` or `bng_re_ring_db()`. Allocation functions declared here are implemented in `bng_res.c`.

## State And Persistence
The structures declared here persist all low-level DMA and MMIO state for queues, doorbells, stats, and chip capabilities. Doorbell info keeps epoch flags that persist across queue wraps. Hardware queues persist producer/consumer indices and PBL address arrays until freed.

## Dependencies And Integration Points
Includes `bng_roce_hsi.h` for hardware bit definitions such as doorbell types and capability flags. The header is consumed by `bng_dev.c`, `bng_fw.c`, `bng_res.c`, and `bng_re.h`. It depends on Linux MMIO `writeq()`, DMA address types, spinlocks, PCI devices, and page-size constants.

## Risks And Edge Cases
`HWQ_FREE_SLOTS()` uses bit masking and therefore assumes `max_elements` is a power of two. `bng_re_get_qe()` does pointer arithmetic on `void *`, relying on compiler extension semantics common in kernel builds. Doorbell writes require correct epoch and toggle handling; stale flags can cause firmware to ignore entries or treat old entries as new. `BNG_RE_INIT_DBHDR()` packs several hardware fields into a 64-bit value, so field masks and shifts must match HSI definitions exactly.

## Test Signals
Compile tests validate HSI constants and structure visibility. Runtime queue tests should verify correct queue-entry addressing, consumer wrap epoch toggling, doorbell writes on CREQ drain, and free-slot behavior at empty, full, and wraparound states. Hardware or emulated firmware tests are needed to validate packed doorbell headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_res.h -->
