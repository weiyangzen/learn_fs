# sources/distributed-fs/openafs/src/ptserver/ptclient.h

## Purpose
Provides a small public include shim for protection client code.

## Important APIs, Types, And Functions
Includes `afs/afs_lock.h`, `ubik.h`, `ptint.h`, and `ptserver.h`, then defines `pr_ErrorMsg` as `afs_error_message`.

## Control Flow
There is no runtime flow. Including this header pulls in the core protection RPC/database types and gives callers the legacy `pr_ErrorMsg` name for error formatting.

## State And Persistence
No state is declared or modified.

## Dependencies And Integration Points
Used by `ptclient.c` and installed as both `prclient.h` and `ptclient.h` aliases through the makefile. It bridges callers to Ubik and generated protection interfaces.

## Risks And Test Signals
Risks are broad transitive includes and macro alias drift if error-message APIs change. Test signals are successful compilation of protection clients and correct error string formatting.
