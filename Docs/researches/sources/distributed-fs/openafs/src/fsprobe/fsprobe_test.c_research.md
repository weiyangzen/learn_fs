# sources/distributed-fs/openafs/src/fsprobe/fsprobe_test.c

## Purpose
Provides an interactive/manual test driver for the fsprobe library.

## Important APIs, Types, And Functions
Defines `FS_Handler`, which prints current `fsprobe_Results`, and `main`, which resolves three hard-coded server names, initializes fsprobe, sleeps, then cleans up.

## Control Flow
`main` builds three `sockaddr_in` entries for `servername1`, `servername2`, and `servername3` on port 7000, calls `fsprobe_Init` with a 30-second interval and debugging enabled, waits ten minutes using `fsprobe_Wait`, then calls `fsprobe_Cleanup` and `rx_Finalize`. The handler iterates over three result entries and prints probe status, many counters, and disk partition summaries.

## State And Persistence
The program relies on fsprobe globals for all result state. It writes only console output.

## Dependencies And Integration Points
Links against `libfsprobe`, Rx, fsint, volser, util, and roken. It uses `hostutil_GetHostByName` to resolve test servers.

## Risks And Test Signals
The test is not self-contained: server names are placeholders and the handler hard-codes three servers regardless of `fsprobe_numServers`. It also prints only 26 disk slots even though `VOLMAXPARTS` can differ. Useful signals are mainly manual: successful connection to real FileServers, periodic handler output, partition data, forced cleanup, and failure behavior when names cannot resolve.
