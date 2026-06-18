# sources/distributed-fs/coda/coda-src/volutil/vol-printstats.cc

## Purpose

`vol-printstats.cc` implements `S_PrintStats`, an administrative RPC that captures server counters and callback state and transfers them back to the volutil client over SMARTFTP. The complete 81-line file was read.

## Important APIs, Types, and Functions

The only exported service handler is `S_PrintStats(RPC2_Handle, SE_Descriptor *)`. It uses `tmpfile()`, `PrintCounters()`, `PrintCallBackState()`, `RPC2_InitSideEffect()`, and `RPC2_CheckSideEffect()`.

## Control Flow

The handler writes stats to an unnamed temporary file, seeks back to offset zero, constructs a `SERVERTOCLIENT` SMARTFTP descriptor using `FILEBYFD`, initializes the side effect, waits for local status, closes the file, and returns the RPC/side-effect status.

## State and Persistence Behavior

It has no persistent state. It reads current in-memory counters and callback state, and the temporary file is closed after transfer.

## Dependencies and Integration Points

The file depends on RPC2 side effects, `srv.h` stats/callback printers, and `volutil.h`. It is called by `volclient.cc`'s `printstats()` command.

## Risks and Test Signals

Risks include transferring large callback dumps through a temporary file, losing the original client-supplied side-effect descriptor, and returning side-effect error codes directly. Tests should mock SMARTFTP failure paths, verify file rewind before transfer, and confirm both counter and callback sections are present.
