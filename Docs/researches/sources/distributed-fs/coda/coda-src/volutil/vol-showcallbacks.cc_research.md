# sources/distributed-fs/coda/coda-src/volutil/vol-showcallbacks.cc

## Purpose

`vol-showcallbacks.cc` implements `S_ShowCallbacks`, a diagnostics RPC that prints callbacks for a specific fid plus global callback state and transfers the report to the client. The complete 82-line file was read.

## Important APIs, Types, and Functions

The exported handler is `S_ShowCallbacks(RPC2_Handle, ViceFid *, SE_Descriptor *)`. It uses `tmpfile()`, `PrintCallBacks()`, `PrintCallBackState()`, and SMARTFTP `FILEBYFD` side effects.

## Control Flow

The handler writes callback information into an unnamed temporary file, rewinds it, initializes a `SERVERTOCLIENT` side-effect transfer by file descriptor, waits for local status, closes the temporary file, and returns the transfer status.

## State and Persistence Behavior

It has no persistent mutations. It reads in-memory callback structures for diagnostics.

## Dependencies and Integration Points

Dependencies include RPC2, `srv.h`, callback printers, and `volutil.h`. The client path is `volclient.cc`'s `showcallbacks()` command.

## Risks and Test Signals

Risks include large callback dumps, failure to preserve caller-provided descriptor fields, and direct return of side-effect errors. Tests should verify fid formatting, empty/no-callback cases, side-effect failures, and inclusion of global callback state.
