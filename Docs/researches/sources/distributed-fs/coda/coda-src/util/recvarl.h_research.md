# sources/distributed-fs/coda/coda-src/util/recvarl.h

## Purpose
Declares the recoverable variable-length object wrapper.

## Important APIs, Types, And Functions
`recvarl_length_t`, `class recvarl`, custom `new` overloads, `length`, `vfld`, `size()`, `end()`, and `destroy()` define the API.

## Control Flow
Callers allocate with the sized recoverable `new`, use the inline payload, and free with `destroy()` rather than `delete`.

## State And Persistence
The length and payload are intended to live in RVM and be transactionally initialized.

## Dependencies And Integration Points
Includes `coda_tsa.h`; implementation uses `rvmlib`.

## Risks
The API is nonstandard C++ and easy to misuse with ordinary `new/delete`. There is no bounds helper for payload access.

## Test Signals
Compile allocation syntax in callers and validate payload size/alignment assumptions.
