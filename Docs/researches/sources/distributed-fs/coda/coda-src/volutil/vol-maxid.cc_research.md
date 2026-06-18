# sources/distributed-fs/coda/coda-src/volutil/vol-maxid.cc

## Purpose

`vol-maxid.cc` exposes administrative RPCs to read and safely advance the server's maximum allocated volume id. The complete 88-line file was read. It protects the server-id byte embedded in volume ids and prevents lowering the allocator watermark.

## Important APIs, Types, and Functions

`S_VolGetMaxVolId()` returns `VGetMaxVolumeId()`. `S_VolSetMaxVolId()` validates the requested id against `SRV_RVM(MaxVolId)`, then calls `VSetMaxVolumeId()` inside an RVM transaction.

## Control Flow

The get path is direct and side-effect free. The set path rejects any id with a different high server-id byte and rejects ids less than the current maximum. Only then does it begin a `restore` transaction, update `MaxVolId`, and flush the transaction.

## State and Persistence Behavior

The only persistent mutation is `SRV_RVM(MaxVolId)`, through the volume-layer setter. Transaction boundaries make the update recoverable in RVM. There is no explicit `VInitVolUtil()` call here; it relies on the volutil worker context already being initialized.

## Dependencies and Integration Points

Dependencies include `recov.h`, `camprivate.h`, `coda_globals.h`, `volume.h`, `rvmlib`, and `volutil.h`. The client commands are `volutil getmaxvol` and `volutil setmaxvol` in `volclient.cc`.

## Risks and Test Signals

Risks are mostly administrative: setting an unexpectedly high id can create large gaps, while validation only checks high-byte server identity and monotonicity. Tests should cover get, successful monotonic set, server-id mismatch rejection, lower-id rejection, transaction failure propagation, and persistence across restart.
