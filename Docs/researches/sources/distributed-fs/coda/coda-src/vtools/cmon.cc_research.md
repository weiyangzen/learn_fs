# sources/distributed-fs/coda/coda-src/vtools/cmon.cc

## Purpose

`cmon.cc` is a curses-based Coda server monitor. It periodically binds to one or more Coda file servers, calls `ViceGetStatistics`, and renders per-server CPU, RPC, uptime, binding, workstation, and disk utilization counters.

## Important APIs, Types, and Functions

`struct server` stores per-server LWP id, name, clock tick rate, curses window, bind/probe timestamps, state, and old/new `ViceStatistics`. `struct printvals` contains the computed display values. `main()` initializes curses and RPC2/LWP, creates one `srvlwp()` per server plus `kbdlwp()`, and waits indefinitely. `GetArgs()` parses `-t`, `-a`, `-c`, and `server[:hz]`. `InitRPC()` initializes LWP, SFTP, and RPC2 with IPv6 option support. `srvlwp()` manages `RPC2_NewBinding`, `ViceGetStatistics`, state transitions, and unbinds. `ComputePV()` converts raw counters into absolute or relative display values. `PrintServer()`, `DrawCaptions()`, `when()`, `CmpDisk()`, `ValidServer()`, and `ShortDiskName()` support rendering and validation.

## Control Flow

After setup, each server LWP loops forever. If dead, it attempts an RPC2 binding to the `codasrv` UDP service and `SUBSYS_SRV`; when bound, it snapshots old statistics, fetches new statistics, derives tick rate from `Spare4` if needed, and prints the server column. The keyboard LWP waits on stdin and toggles absolute or relative display with `a` and `r`, then clears/redraws the active window.

## State and Persistence Behavior

State is in memory only: server status, counters, timestamps, and curses windows. There is no durable persistence. In debug builds it writes `/tmp/cmon_dbg`; otherwise RPC2 logs are sent to `/dev/null`. Runtime control is interactive through keypresses.

## Dependencies and Integration Points

It integrates with Coda's RPC2, SFTP, LWP, `ViceGetStatistics`, `ViceStatistics`, `ViceDisk`, `coda_getservbyname`, and `coda_getaddrinfo`, plus curses/ncurses. It assumes server statistics fields and service naming remain compatible.

## Risks

`main()` passes the address of loop variable `i` into each `LWP_CreateProcess`, so LWP startup timing can cause multiple workers to observe the same index. The UI assumes 24-row windows and fixed column widths. Counter differences are unsigned-style arithmetic over fields that may wrap. `ComputePV()` assumes 10 disk slots. Signal cleanup only handles `SIGINT`; other failures can leave terminal modes dirty. Server names are mutated in-place when parsing `server[:hz]`.

## Test Signals

Tests should cover argument parsing, `ValidServer()` failure handling, absolute/relative `ComputePV()` math including zero totals and counter wrap, disk sorting, short-name truncation, and a mocked RPC2/Vice statistics loop. Manual integration tests need live Coda servers and terminal resize/interrupt checks.
