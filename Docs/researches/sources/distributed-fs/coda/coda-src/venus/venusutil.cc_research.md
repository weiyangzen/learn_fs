# sources/distributed-fs/coda/coda-src/venus/venusutil.cc

## Purpose
This file implements general Venus utility behavior: debug logging, fatal error handling, state dumps, operation/error stringification, statistics initialization/printing, RPC packet-stat snapshots, malloc/RDS tracing hooks, log swapping, lock-level names, current time, and fid comparison.

## Important APIs, Types, and Functions
Globals include `logFile`, `LogLevel`, `MallocTrace`, `NullFid`, `NullVV`, `VFSStats`, and `RPCOpStats`. `dprint()` writes stamped debug logs. `choke()` prints a fatal message, dumps state, flushes/terminates recovery, unmounts, and asserts. `VenusPrint()` dispatches module-specific printers. `VenusOpStr()`, `IoctlOpStr()`, and `VenusRetStr()` map operation numbers and returns to strings. `VVPrint()`, `binaryfloor()`, `LogInit()`, `DebugOn()`, `DebugOff()`, `Terminate()`, `DumpState()`, `RusagePrint()`, `VFSPrint()`, `RPCPrint()`, `GetCSS()`, `SubCSSs()`, `MallocPrint()`, `StatsInit()`, `ToggleMallocTrace()`, `rds_printer()`, `SwapLog()`, `lvlstr()`, `Vtime()`, and `FAV_Compare()` round out utility support.

## Control Flow
Logging is inert until `LogInit()` sets `LogInited`. `dprint()` prefixes messages with the current vproc stamp and inserts blank lines when vproc/sequence changes. `VenusPrint()` parses requested module names and invokes the relevant printers. `StatsInit()` zeroes VFS/RPC stats and copies static operation names. `RPCPrint()` snapshots RPC2/SFTP counters and prints unicast/multicast stats. Fatal paths funnel through `choke()`, which performs best-effort persistent flush and unmount before invoking Coda assertion handling.

## State and Persistence Behavior
Most state is transient logging/statistics. `choke()` and `Terminate()` can force recovery flushing and clean termination side effects. `SwapLog()` reopens log and console files. `ToggleMallocTrace()` changes RDS heap tracing state.

## Dependencies and Integration Points
It depends on nearly all Venus subsystems for printing and cleanup: recovery, FSDB, VDB, HDB, users, connections, servers, VSG/mgrp, callbacks, workers, mariner, RPC2/SFTP counters, RDS tracing, and ioctl constants. `venus.private.h` declares many of its functions for broad use.

## Risks and Test Signals
Risks include fixed-size buffers in logging/string conversion, varargs declarations in old style, divide-by-zero possibilities in stat means if counters and times disagree, stale operation tables, and fatal cleanup reentrancy. Tests should cover log initialization, control-triggered stats dump, ioctl/op string mappings, RPC stat subtraction, malloc tracing toggles, and `FAV_Compare()` ordering.
