# sources/distributed-fs/coda/coda-src/librepair/repcmds.h

## Purpose
Public interface and shared data structures for Coda client repair commands.

## APIs, Types, and Functions
Defines constants `MAXVOLNAME`, `MAXHOSTS`, `HOSTNAMLEN`, `DEF_BUF`, and conflict-kind values `LOCAL_GLOBAL`, `SERVER_SERVER`, and `MIXED_CONFLICT`. Defines `struct conflict` with conflict FID/VV, replica list, repair directory, realm, and conflict-type flags; and `struct replica` with RW replica FID/VV, realm/server/component names, and next pointer. Declares repair operations `BeginRepair()`, `ClearInc()`, `CompareDirs()`, `DoRepair()`, `EndRepair()`, `RemoveInc()`, helpers `dorep()`, `makedff()`, rvol helpers, and path helpers. Macros `freeif()` and `strerr()` centralize cleanup and formatted error writing.

## Control Flow, State, and Persistence
No implementation. The structs model repair-session state that persists from `BeginRepair()` until `EndRepair()` frees it; functions declared here mutate Venus repair state and server replica metadata.

## Dependencies and Integration
Includes broad Coda, RPC2, parser, auth, Venus ioctl, copyfile, inconsistency, repio, and resolver headers. It is the main header for repair CLIs or libraries using non-interactive repair.

## Risks and Test Signals
Risks include broad header coupling, fixed host/path sizes, variadic `strerr` macro portability, mutable linked-list ownership rules, and flags stored as `char`. Test signals are compile/link of repair clients and end-to-end repair-session lifecycle tests.
