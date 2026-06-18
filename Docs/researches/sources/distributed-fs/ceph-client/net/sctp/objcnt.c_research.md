# sources/distributed-fs/ceph-client/net/sctp/objcnt.c

## Purpose
`objcnt.c` implements debug object counters for SCTP allocations. It exposes counters for key SCTP object classes through procfs so developers can spot leaks, unexpected object growth, or lifetime imbalance during testing.

## Important APIs, Types, And Functions
The file declares counters with `SCTP_DBG_OBJCNT()` for `sock`, `ep`, `transport`, `assoc`, `bind_addr`, `bind_bucket`, `chunk`, `addr`, `datamsg`, and `keys`. It builds `sctp_dbg_objcnt[]` with `SCTP_DBG_OBJCNT_ENTRY()` records and exposes them through seq operations: `sctp_objcnt_seq_start()`, `sctp_objcnt_seq_next()`, `sctp_objcnt_seq_stop()`, and `sctp_objcnt_seq_show()`. The integration entry point is `sctp_dbg_objcnt_init(struct net *net)`.

## Control Flow
During per-net SCTP defaults initialization, `sctp_dbg_objcnt_init()` creates `/proc/net/sctp/sctp_dbg_objcnt` below the namespace's SCTP proc directory. Reads iterate by `loff_t` index over `sctp_dbg_objcnt[]`; each row prints a label and `atomic_read()` of the backing counter. There is no custom open/release logic beyond `proc_create_seq()`.

## State And Persistence
Counter state is global atomic in-memory state, incremented and decremented by macros used in other SCTP files. The proc entry is per net namespace, but the counters themselves are not per-net in this file. Values reset only when the module is unloaded or the kernel restarts.

## Dependencies And Integration Points
This depends on SCTP debug counter macros and procfs support initialized by `proc.c`/`protocol.c`. It is useful only when object allocation/free paths elsewhere consistently call the increment/decrement macros.

## Risks
Because counters are global while proc entries are per-net, readers should not interpret the values as namespace-local. Missing instrumentation in an allocation path creates false confidence. Counter imbalance is a diagnostic signal but not proof of a leak unless object lifetime and delayed RCU frees are also considered.

## Test Signals
Read `/proc/net/sctp/sctp_dbg_objcnt` after module init, after opening/closing SCTP sockets, after creating and tearing down associations, after chunk-heavy sends, and after namespace teardown. Counts should return to baseline after grace periods and no row should disappear or read out of bounds.
