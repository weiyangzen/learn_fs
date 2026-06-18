# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_wr.h

## Purpose

This header defines the csiostor WR queue data model and public WRM APIs. It provides SGE field constants, queue parameter structures, generic DMA/request structures, IQ footer parsing helpers, queue metadata, SGE cache state, WRM state, accessor macros, and function prototypes.

## Important APIs, Types, And Functions

Important types include `struct csio_iq_params`, `struct csio_eq_params`, `struct csio_dma_buf`, `struct csio_ioreq`, `struct csio_qstatus_page`, `struct csio_iqwr_footer`, `struct csio_wr_pair`, `struct csio_fl_dma_buf`, `struct csio_iq`, `struct csio_eq`, `struct csio_fl`, `struct csio_q`, `struct csio_sge`, and `struct csio_wrm`. The `iq_handler_t` callback type is the WR completion interface. `csio_wr_status()` extracts firmware retval/status from a WR header.

The accessor macros abstract queue arrays and firmware ids (`csio_q_iqid()`, `csio_q_eqid()`, `csio_q_physiqid()`, `csio_q_eq_wrap()`, and others). Prototypes expose queue allocation/creation/destruction, WR reservation/copy/issue, IQ processing, SGE init, and WRM init/exit.

## Control Flow

Higher-level modules allocate queue metadata through `csio_wrm_init()`, allocate specific queues with `csio_wr_alloc_q()`, ask firmware to create contexts, then reserve WR space via `csio_wr_get()`. If a WR spans the circular queue end, callers receive `struct csio_wr_pair` with two segments and can use `csio_wr_copy_to_wrp()` or local split-copy code. Interrupt handlers process IQ entries through `csio_wr_process_iq()` or `_idx()`.

## State And Persistence

This header defines volatile in-memory state mirrored to hardware. `struct csio_ioreq` is cacheline-aligned and reused by SCSI and other protocols. Queue state persists only while the driver owns DMA memory and firmware contexts. Hardware queue ids are invalidated with `CSIO_MAX_QID`; queue memory and SGE cached values are rebuilt on driver/device initialization.

## Dependencies And Integration Points

It includes `csio_defs.h`, generic Chelsio firmware API headers, and storage firmware API definitions. It is consumed by SCSI, hardware, mailbox, interrupt, and possibly lnode/rnode modules. The layout of `struct csio_ioreq` and firmware WR status extraction must match `csio_scsi.c` and firmware ABI structures.

## Risks

The macro `csio_q_iq_to_flid(__hw, __iq_idx)` references `__iq_qidx`, which is not its parameter name; use would fail to compile or expand incorrectly. Many accessor macros evaluate arguments directly and assume valid queue indices. `struct csio_ioreq` embeds generic scratch pointers with protocol-specific meanings, creating aliasing risk. Bitfield layout in parameter structs is host-compiler-sensitive but appears to be an internal mailbox helper contract rather than direct DMA ABI.

## Test Signals

Build coverage should include all macros used by WR/SCSI paths. Runtime signals include valid queue id transitions from `CSIO_MAX_QID` to firmware ids and back, correct two-segment WR behavior, stable `struct csio_ioreq` alignment, and no list/DMA corruption under high I/O and interrupt rates.
