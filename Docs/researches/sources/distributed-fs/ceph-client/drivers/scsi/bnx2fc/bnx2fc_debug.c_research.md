# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_debug.c

## Purpose

`bnx2fc_debug.c` implements formatted debug logging helpers for I/O, target/session, and HBA contexts. Logging is gated by the global `bnx2fc_debug_level` module parameter and uses `shost_printk()` when a SCSI host is available.

## Important APIs, Types, and Functions

`BNX2FC_IO_DBG()` logs command-scoped messages when `LOG_IO` is enabled and prefixes the XID. `BNX2FC_TGT_DBG()` logs target/session messages when `LOG_TGT` is enabled and prefixes remote port ID. `BNX2FC_HBA_DBG()` logs host/lport messages when `LOG_HBA` is enabled. All use `struct va_format` and varargs.

## Control Flow

Each helper checks its debug bit with a likely-disabled fast path, formats varargs, and emits through `shost_printk(KERN_INFO, ...)` if nested context pointers reach a valid `Scsi_Host`; otherwise it falls back to `pr_info("NULL ...")`.

## State and Persistence Behavior

Only `bnx2fc_debug_level` is read. Output persists only in the kernel log.

## Dependencies and Integration Points

The file includes `bnx2fc.h` for structures, log bits, `PFX`, and printk APIs. It is linked into the composite module and called by ELS, lifecycle, hardware, I/O, and target paths.

## Risks and Edge Cases

Debug calls can occur in atomic or lock-held contexts, so helpers must remain lightweight. Pointer checks prevent obvious NULL dereferences, but object lifetime still depends on caller locking/refcounts. `LOG_IO` can flood logs under heavy I/O.

## Test Signals

Enable each debug bit, confirm XID/port/host prefixes, call with NULL/partial contexts, verify no output when disabled, and run with lockdep to catch logging from unsuitable contexts.
