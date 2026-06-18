# sources/distributed-fs/coda/coda-src/util/recvarl.cc

## Purpose
Implements `recvarl`, a recoverable variable-length allocation object with an inline length header and flexible payload area.

## Important APIs, Types, And Functions
Custom `operator new(size_t,int)` allocates `payload_size + sizeof(recvarl_length_t)` with `rvmlib_rec_malloc`. The normal `operator new(size_t)` and destructor assert. Constructor records and zeroes payload. `size()`, `end()`, and `destroy()` report total size, pointer past end, and free the recoverable object.

## Control Flow
Callers allocate with `new (payload_len) recvarl(payload_len)`. Construction logs the full allocation range, stores `length`, and zero-fills `vfld`. Destruction is not via `delete`; callers use `destroy()`.

## State And Persistence
State is recoverable allocation containing `length` and variable payload bytes. It must be created and destroyed under RVM transaction discipline.

## Dependencies And Integration Points
Depends on `rvmlib`, `util.h`, and transaction annotations. Used for persistent variable-length fields in Coda metadata.

## Risks
The dummy normal `new`, destructor, and `operator delete` all assert, so ordinary C++ lifetime management is invalid. Payload alignment is based on `unsigned long vfld[1]` but allocation size is byte-oriented. `destroy()` has a comment questioning correctness.

## Test Signals
Allocate several payload sizes in transactions, verify zeroed bytes, `size()` and `end()`, committed recovery, abort rollback, and `destroy()` freeing through RVM.
