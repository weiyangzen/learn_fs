# sources/distributed-fs/openafs/src/libadmin/test/kas.h

## Purpose

`kas.h` is the local header for the KAS portion of the `afscp` libadmin test client. It gathers the OpenAFS headers needed by `kas.c` and exposes the single setup entry point used by the main test program.

## Important APIs, Types, and Functions

The header includes standard C headers, pthreads, RX/RX stats, `afs_Admin.h`, `afs_kasAdmin.h`, `afs_utilAdmin.h`, `afs_clientAdmin.h`, cell configuration, command parsing, and `common.h`. It declares `SetupKasAdminCmd(void)` and imports `existing_tokens`, which is set by `afscp.c` when the client obtains pre-existing tokens.

## Control Flow

There is no executable control flow in the header. Its main integration role is making `SetupKasAdminCmd` visible and sharing the `existing_tokens` guard state with the KAS command handlers.

## State and Persistence Behavior

The header declares external process state but stores none itself. The `existing_tokens` flag affects whether KAS commands are allowed to reach remote KAS database state.

## Dependencies and Integration Points

This file is tightly coupled to the libadmin test harness. `common.h` is expected to provide `cellHandle`, error macros, and common command argument helpers used by `kas.c`.

## Risks and Test Signals

The comment notes that existing tokens are "incompatable" with KAS operations; callers need tests ensuring that `SetupKasAdminCmd` commands consistently reject that mode. Because the header includes many heavy dependencies, build tests should cover both Unix and any supported pthread/RX configuration.
