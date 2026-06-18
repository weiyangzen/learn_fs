# sources/distributed-fs/coda/coda-src/volutil/vol-showvnode.cc

## Purpose

`vol-showvnode.cc` implements `S_VolShowVnode`, a diagnostics RPC that dumps one vnode's metadata, optional directory contents, and optional resolution log to a SMARTFTP result file. The complete 199-line file was read.

## Important APIs, Types, and Functions

The entry point is `S_VolShowVnode(RPC2_Handle, RPC2_Unsigned, RPC2_Unsigned, RPC2_Unsigned, SE_Descriptor *)`. It uses `XlateVid()`, `VGetVolume()`, `VGetVnode()`, `FPrintVV()`, directory cache helpers `DC_Get()`/`DH_Print()`/`DC_Put()`, `PrintLog()`, and SMARTFTP `FILEBYNAME`.

## Control Flow

The handler translates replicated ids, starts a transaction, attaches the volume, reads the vnode with barren access allowed, writes metadata to `/tmp/vshowvnode.tmp`, prints directory and resolution-log details when applicable, releases the volume, ends the transaction, closes the file, and transfers it back to the client.

## State and Persistence Behavior

The operation is intended as read-only diagnostics. It still opens a transaction and uses a fixed temporary path. It puts the vnode at exit after the transfer setup.

## Dependencies and Integration Points

Dependencies include `srv.h`, `volume.h`, `partition.h`, `viceinode.h`, `vutil.h`, `vrdb.h`, `codadir.h`, and resolution-log headers. The client path is `volclient.cc`'s `showvnode()`.

## Risks and Test Signals

Risks include fixed `/tmp` filename races, returning after `VPutVolume()` but before `VPutVnode()`, side-effect path exposure, and assert-prone directory/log printing on corrupt vnodes. Tests should cover files, directories, symlinks, barren vnodes, missing vnode/volume, replicated id translation, output file transfer, and concurrent requests.
