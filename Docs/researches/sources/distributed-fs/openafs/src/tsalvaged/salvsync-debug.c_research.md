# sources/distributed-fs/openafs/src/tsalvaged/salvsync-debug.c

## Purpose
Implements `salvsync-debug`, a command-line utility for interacting with the demand-attach salvageserver SALVSYNC protocol. It can request stats/nop, schedule salvage, cancel one salvage, cancel all, raise priority, and query salvage status.

## Important APIs, Types, And Functions
The code is gated by `AFS_DEMAND_ATTACH_FS`; without it, `main` reports unsupported. Important types are `struct salv_state`, `struct fssync_state`, `SYNC_response`, and `SALVSYNC_response_hdr`. Main helpers include `common_prolog`, `common_salv_prolog`, `do_salvop`, response/command/reason/state string mappers, and operation callbacks `OpStats`, `OpSalvage`, `OpCancel`, `OpCancelAll`, `OpRaisePrio`, and `OpQuery`.

## Control Flow
Demand-attach `main` initializes server paths, creates `cmd` syntaxes and aliases, wires common parameters by fixed offsets, and dispatches. `common_prolog` initializes winsock when needed, initializes the volume package and directory package, parses optional reason and program type, and connects to SALVSYNC. `common_salv_prolog` allocates salvage request state and parses volume id, partition, and priority. `do_salvop` calls `SALVSYNC_SalvageVolume`, reports transport/protocol response details, prints queue/priority/state fields if valid, and disconnects.

## State And Persistence
The utility creates transient process state and sends requests to the salvageserver, which may persist or mutate salvage queue state for volumes. It initializes volume package state locally but mostly for client protocol setup. `struct salv_state` allocations are not freed before process exit.

## Dependencies And Integration Points
It depends on OpenAFS command parsing, directory/volume/partition packages, daemon communication, SALVSYNC/FSSYNC protocol headers, Windows event logging/winsock conditionals, and demand-attach fileserver definitions. It is built by `tsalvaged/Makefile.in`.

## Risks And Test Signals
Risks include fixed parameter offsets that must match syntax construction, `atoi` parsing with little validation, always calling `common_salv_prolog` for stats despite the syntax not requiring a volume, and command string typos such as `SALVSYNC_CANCELLALL`. Tests should cover unsupported non-DAFS builds, each subcommand, optional reason/programtype names and numeric values, missing/invalid volume id, queue response formatting, and behavior when no salvageserver is reachable.
