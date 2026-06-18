# sources/distributed-fs/coda/coda-src/volutil/vol-setlogparms.cc

## Purpose

`vol-setlogparms.cc` implements `S_VolSetLogParms`, the administrative RPC for enabling/disabling RVM resolution logging on a volume and increasing the log admin limit. The complete 145-line file was read.

## Important APIs, Types, and Functions

The entry point is `S_VolSetLogParms(RPC2_Handle, VolumeId, RPC2_Integer, RPC2_Integer)`. It uses `VInitVolUtil()`, `XlateVid()`, `VGetVolume()`, `V_RVMResOn()`, `V_VolLog()`, `recov_vol_log::Increase_Admin_Limit()`, `VUpdateVolume()`, RVM transactions, and `VPutVolume()`.

## Control Flow

After initializing and translating the id, the handler attaches the volume and validates `OnFlag`. It updates `ResOn` for `RVMRES` or `0`, begins a transaction, optionally validates that the requested log size is a multiple of 32, increases the admin limit if resolution/log storage are active, updates the volume header, flushes or aborts the transaction, releases the volume, and disconnects.

## State and Persistence Behavior

It persistently mutates the volume header's `ResOn` flag and possibly the recoverable volume log admin limit. Header update and log limit change are wrapped in one RVM transaction.

## Dependencies and Integration Points

Dependencies include `rvmlib`, `vrdb.h`, `srv.h`, `vutil.h`, `volume.h`, and `recov_vollog.h`. The client command is `volutil setlogparms <volid> reson <flag> logsize <nentries>`.

## Risks and Test Signals

Risks include changing `ResOn` before `rvmlib_begin_transaction()`, allowing unsupported flags only by runtime validation, and only supporting log-size increases in practice. Tests should cover enable, disable, invalid flag, invalid size multiple, replicated id translation, inactive resolution with log-size request, and persistence across detach/reattach.
