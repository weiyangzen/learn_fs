# sources/distributed-fs/beegfs-go/watch/cmd/test-fileeventlogger/main.go

## Purpose

This test utility connects to the BeeGFS file event Unix packet socket and writes synthetic v1-format metadata event packets. It is intended for manual or performance testing of BeeWatch metadata ingestion without a live metadata service.

## Important APIs, Types, And Functions

Command-line flags configure socket path, output log file, debug logging, event send frequency, path length, and number of random events. `getLogger` builds a zap logger. `generateEvent` assembles a binary event packet from little-endian fields and C-string-like path payloads. `joinSlices` concatenates packet fragments.

## Control Flow

After parsing flags and dialing `net.Dial("unixpacket", socketPath)`, the utility pre-generates either one fixed-size event or several random-sized events. With `frequency == 0`, it writes continuously as fast as possible. Otherwise it installs signal cancellation, starts a ticker, and writes one selected event per tick until interrupted.

## State And Persistence

State is limited to the open Unix packet connection, generated event byte slices, and optional log file. It does not persist sequence counters and uses hard-coded packet contents for dropped/missed sequence fields and event type.

## Dependencies And Integration Points

It depends on the raw v1 event layout expected by `metadata.deserializeEvent` and on BeeWatch listening at the configured Unix packet socket. It integrates with zap only for local logging.

## Risks And Test Signals

The generated packet layout is hand-built and easy to desynchronize from protocol changes. `pathLengths` can generate packets near the 64 KiB reader limit; extreme values should be tested against `metadata` buffer sizing. The random event loop chooses among precomputed events, not newly randomized payloads. The utility exits fatally on write errors, which is appropriate for manual testing but not a resilient load generator.
