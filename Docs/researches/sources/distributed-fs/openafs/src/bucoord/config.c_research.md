# sources/distributed-fs/openafs/src/bucoord/config.c

## Purpose
Provides the in-memory backup coordinator configuration root and small helpers for opening files under that root and maintaining tape-host lists. It initializes `bc_globalConfig` and supplies the host add/delete primitives used by tape-host command and persistence code.

## Important APIs, Types, And Functions
Exports `bc_globalConfig`, `bc_open`, `bc_InitConfig`, `bc_AddTapeHost`, and `bc_DeleteTapeHost`. Private helpers `HostAdd` and `HostDelete` operate on `struct bc_hostEntry` singly linked lists, resolving host names to `sockaddr_in` and storing a tape coordinator port offset.

## Control Flow
`bc_InitConfig` allocates a zeroed `struct bc_config`, stores the configuration path, and makes it globally visible. `bc_open` constructs `aconfig->path/aname[aext]` into a fixed local buffer and calls `fopen`. `HostAdd` verifies the host through `gethostbyname`, rejects any existing entry with the same port offset, appends a new host record, and copies the resolved address. `HostDelete` finds an exact host-name and port-offset match, unlinks it, and frees its name and record.

## State And Persistence
`bc_InitConfig` initializes only in-memory state; persistent text configuration is loaded later through BUDB text APIs in other modules. `bc_open` can read or write local files below the configured path, but the current file does not itself save host entries. Host records live in `bc_globalConfig->tapeHosts` until refreshed, saved, or cleared by `tape_hosts.c`.

## Dependencies And Integration Points
Depends on `bc.h` for `struct bc_config` and `struct bc_hostEntry`, libc allocation/string/file APIs, and resolver APIs. The host-list primitives are called by `tape_hosts.c`; `bc_InitConfig` is invoked by `main.c` during `backupInit`.

## Risks And Test Signals
`bc_open` uses unbounded `strcpy`/`strcat` into a 256-byte path buffer. `HostAdd` checks duplicate port offsets only, so two names for the same host with different offsets are allowed while any two hosts sharing one offset are rejected. `gethostbyname` is IPv4-only and legacy. Test signals are initialization with a valid backup directory, add/delete/list host flows, duplicate port offset handling, invalid host handling, and long path/name robustness.
