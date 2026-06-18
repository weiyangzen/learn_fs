<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/error_macros.h -->
# sources/distributed-fs/openafs/src/budb/error_macros.h

## Purpose
Defines local error-handling macros used throughout budb server code.

## Important APIs, Types, And Functions
`ERROR(evalue)` assigns `code` and jumps to `error_exit`. `ABORT(evalue)` assigns `code` and jumps to `abort_exit`. `BUDB_EXIT(evalue)` audits a server exit event and calls `exit`.

## Control Flow
The macros standardize the common transaction pattern: validate, perform work, jump to cleanup on errors, and either end or abort the Ubik transaction in labeled cleanup blocks.

## State And Persistence
No direct state is stored. Indirectly, correct use determines whether partial persistent database mutations are committed or aborted.

## Dependencies And Integration Points
Used across database, allocation, hash, text, dump, verify, and RPC modules. `BUDB_EXIT` depends on audit infrastructure.

## Risks And Test Signals
The macros assume a local variable named `code` and matching labels. Misuse can jump past required cleanup or abort the wrong transaction. Compile warnings, static analysis for labels, and transaction error-path tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/error_macros.h -->
