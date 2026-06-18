# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_qdio.h`

## Purpose

`zfcp_qdio.h` declares the zfcp QDIO queue state, per-request SBAL cursor state, and inline helpers for constructing QDIO request queue buffers. It is used by FSF command code to lay out request ids, QTCBs, CT/ELS payloads, SCSI data SGs, chaining flags, data-router division counts, and multi-buffer scount values before submission.

## Important APIs, Types, And Data

- `ZFCP_QDIO_SBALE_LEN` defines one SBALE data capacity as `PAGE_SIZE`.
- `ZFCP_QDIO_MAX_SBALS_PER_REQ` caps one request at 36 SBALs for chaining.
- `struct zfcp_qdio` stores response/request queue buffer arrays, request queue index/free count, accounting and request locks, utilization counters, full counter, wait queue, tasklets, request timer, adapter pointer, and per-SBAL/per-request element limits.
- `struct zfcp_qdio_req` stores the in-progress request's SBAL type, number, first/last/limit indices, current SBALE index, and outbound queue usage snapshot.
- `zfcp_qdio_sbale_req()` returns element zero for the current request SBAL, used for request id/control metadata.
- `zfcp_qdio_sbale_curr()` returns the current SBALE cursor.
- `zfcp_qdio_req_init()` initializes a request in the current free SBAL, writes request id into element zero, sets command/type flags, computes SBAL limit from free count, and optionally writes the first data block.
- `zfcp_qdio_fill_next()` adds another data block within a single SBAL and BUGs on overflow.
- `zfcp_qdio_set_sbale_last()` marks the current entry as the last entry.
- `zfcp_qdio_sg_one_sbale()` returns true when a scatterlist fits in one SBALE.
- `zfcp_qdio_skip_to_last_sbale()` moves the cursor to the last element of the current SBAL.
- `zfcp_qdio_sbal_limit()` restricts how many SBALs the request may use.
- `zfcp_qdio_set_data_div()` writes the data division count into the first SBALE length field.
- `zfcp_qdio_real_bytes()` totals scatterlist bytes.
- `zfcp_qdio_set_scount()` writes multi-buffer SBAL count into the first SBALE.

## Control Flow And Integration

FSF command setup starts with `zfcp_qdio_req_init()` under `qdio->req_q_lock`, then appends command-specific buffers using inline helpers and/or `zfcp_qdio_sbals_from_sg()` from `zfcp_qdio.c`. The first SBALE carries request id and command flags. Later helpers mark the last entry, limit chaining for ELS, set data division counts for separated protection/data SGs, and set scount for multi-buffer requests. Finally `zfcp_qdio_send()` submits the prepared request.

## State And Persistence

`struct zfcp_qdio` persists per adapter after setup. `struct zfcp_qdio_req` is embedded in each `struct zfcp_fsf_req` and persists for the FSF request lifetime. Inline functions mutate queue buffer memory directly, so the queue buffer contents are transient but hardware-visible until QDIO completion.

## Dependencies

The header depends on Linux interrupt/tasklet definitions, s390 QDIO buffer structures and constants, and scatterlist helpers. It assumes the including code has the full `struct zfcp_adapter` definition available when dereferencing adapter-related fields indirectly.

## Risks And Edge Cases

- `zfcp_qdio_req_init()` computes `sbal_limit` from current free count; callers must hold `req_q_lock` through final send to keep the free-count view valid.
- `zfcp_qdio_fill_next()` is only for single-SBAL requests and BUGs if it would cross the SBAL boundary.
- `zfcp_qdio_set_data_div()` and `zfcp_qdio_set_scount()` overload fields in the first SBALE according to hardware conventions; misuse can corrupt command interpretation.
- `zfcp_qdio_real_bytes()` walks until `sg_next()` returns NULL; malformed SG chains can overrun expectations.
- Request ids are converted with `u64_to_dma64()` and recovered from DMA addresses on completion; this encoding is central to FSF request lookup.

## Test Signals

Validation should cover:

- Initial request layout: first SBALE request id, command/type flags, optional QTCB pointer/length, and correct cursor values.
- Last-entry and chaining flags appear at expected entries for single and multi-SBAL requests.
- SBAL limits prevent ELS/CT layouts from exceeding hardware-supported chains.
- Data division and scount values match SG counts and SBAL count for data-router/multi-buffer cases.
- Free count and request queue index remain stable when building under lock until `zfcp_qdio_send()`.
