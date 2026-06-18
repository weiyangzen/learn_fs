# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_scsi.h

## Purpose

This header defines the public SCSI-module contract for csiostor: host templates, SCSI queue tunables, max SGE sizing, request/stat/state types, freelist helpers, event wrappers, and exported functions implemented by `csio_scsi.c`.

## Important APIs, Types, And Functions

Key constants include `CSIO_SCSI_MAX_SGE`, `CSIO_SCSI_ABRT_TMO_MS`, `CSIO_SCSI_LUNRST_TMO_MS`, `CSIO_SCSI_IQSIZE`, `CSIO_MAX_SNS_LEN`, and `CSIO_SCSI_RSP_LEN`. `struct csio_scsi_stats` records I/O success, readiness failures, DMA failures, SCSI/FW errors, abort/close outcomes, active counts, freelist counts, DDP unalignment, and invalid CPL/opcode counters. `struct csio_scsim` is the module owner for active and free request lists.

`enum csio_scsi_ev` names the request state-machine events, and `enum csio_scsi_lev` plus `struct csio_scsi_level_data` support cleanup or abort at all, lnode, rnode, or LUN scope. Inline APIs manage request and DDP freelists (`csio_get_scsi_ioreq()`, `csio_put_scsi_ioreq()`, `csio_get_scsi_ddp()`), post events (`csio_scsi_completed()`, `csio_scsi_aborted()`, `csio_scsi_closed()`), and start/abort/close requests.

## Control Flow

Consumers include this header to allocate `struct csio_scsim`, register `csio_fcoe_shost_template`, and call `csio_scsim_init()`/`exit()`. Completion paths call the inline wrappers to convert firmware completion classes into state-machine events. Queuecommand and EH paths use `csio_scsi_start_io()`, `csio_scsi_start_tm()`, `csio_scsi_abort()`, and `csio_scsi_close()`; each posts an event and returns `ioreq->drv_status`.

## State And Persistence

All state described here is volatile kernel state. `csio_scsi_cmnd(req)` aliases `req->scratch1`, so the active SCSI command pointer shares generic request scratch storage. Freelist accounting is maintained through stats counters and list membership, protected by the caller's expected locks. There is no persisted configuration beyond module parameters declared elsewhere.

## Dependencies And Integration Points

The header depends on Linux spinlock/completion/SCSI headers, FC FCP definitions, `csio_defs.h`, and `csio_wr.h`. It exposes the SCSI module to the csiostor hardware, interrupt/completion, lnode/rnode, and init paths. The `cmd_size` private area expected by the host template is `struct csio_cmd_priv`.

## Risks

The inline freelist helpers are lockless and rely on callers using `freelist_lock` or `hw->lock` consistently. `csio_scsi_cmnd(req)` is a macro over generic scratch storage, so any other user of `scratch1` would corrupt command association. `csio_put_scsi_ioreq_list()` increments counters by a caller-provided `n`; wrong values desynchronize stats. Event wrappers add list nodes to callback queues based on state side effects, so misuse outside the expected locked completion path can duplicate list entries.

## Test Signals

Build signals catch struct/API drift with `csio_scsi.c`. Runtime signals include balanced `n_free_ioreq` and `n_free_ddp` after stress, correct active/TM counts, SCSI EH completion behavior, and no list-debug warnings under abort, close, LUN reset, and driver cleanup.
