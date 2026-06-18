# sources/distributed-fs/coda/coda-src/volutil/vol-timing.cc

## Purpose

`vol-timing.cc` implements `S_VolTiming`, which toggles server timing/probing and transfers processed timing traces when disabled. The complete 115-line file was read.

## Important APIs, Types, and Functions

The service entry point is `S_VolTiming(RPC2_Handle, RPC2_Integer, SE_Descriptor *)`. It uses global `probingon`, `tpinfo`, `FileresTPinfo`, `timing_path::postprocess()`, and SMARTFTP `FILEBYNAME` transfer from `/tmp/timing.tmp`.

## Control Flow

When `OnFlag` is true, the handler initializes volutil mode and sets `probingon`. When `OnFlag` is false and probing is active, it disables probing, writes processed timing-path reports to the temp file, deletes timing buffers, transfers the file to the client, and disconnects.

## State and Persistence Behavior

It mutates in-memory timing globals only. The temporary report path is fixed and not persistent configuration.

## Dependencies and Integration Points

Dependencies include LWP timers, RPC2 side effects, `timing.h`, `volume.h`, `vice.h`, and `util.h`. The client path is `volclient.cc`'s `timing on|off [file]` command.

## Risks and Test Signals

Risks include fixed temp-file races, no transfer when `off` is requested while probing is already off, deletion of global timing buffers, and side-effect error returns as `-1`. Tests should cover on/off transitions, double-off behavior, postprocess output for both timing buffers, side-effect failures, and cleanup of globals.
