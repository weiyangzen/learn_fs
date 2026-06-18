# sources/distributed-fs/openafs/src/WINNT/afsd/cunlog.c

## Purpose

`cunlog.c` implements the Windows `unlog` utility for discarding AFS/Kerberos tokens from the cache manager. It can forget tokens for selected cells or forget all cached tokens.

## Important APIs, Types, and Functions

`CommandProc()` is the command handler registered through the OpenAFS `cmd` package. It builds an `afs` service principal per `-cell` item and calls `ktc_ForgetToken()`, or calls `ktc_ForgetAllTokens()` when no cells are supplied. `main()` initializes Winsock, defines the syntax with optional `-cell` list, dispatches the command, and returns the dispatch status.

## Control Flow

If `-cell` is present, the handler iterates each cell item, clears the service instance, sets service name `afs`, and forgets just that service token. Failures are printed and the final nonzero code is retained. Without `-cell`, it requests a global token purge and reports a single failure if present.

## State and Persistence Behavior

This utility mutates cache-manager token state but does not maintain its own files or registry values. The only persistent effect is that future authenticated AFS requests from the current token set lose the discarded credentials.

## Dependencies and Integration Points

It depends on the OpenAFS auth/ktc library, command parser, AFS integer/protocol headers, and Winsock startup. It integrates with user login/logout workflows and any scripts that need to clear cell-specific credentials.

## Risks and Edge Cases

Cell names are copied directly into `server.cell` without a visible bounds check, so safety depends on command parser limits and `ktc_principal` sizing. Multi-cell mode returns only the last error, which can hide earlier failures from callers. The utility does not distinguish missing tokens from cache-manager communication failures in its output beyond the returned code.

## Test Signals

Tests should cover no-argument full token purge, one-cell purge, multiple cells with mixed success/failure, long cell names, cache-manager-not-running errors, and command parser behavior for malformed `-cell` lists.
