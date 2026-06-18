# sources/distributed-fs/orangefs/src/io/description/dist-basic.c

## Purpose
Implements the basic OrangeFS distribution where all data resides on a single data file/server.

## Important APIs, Types, And Functions
Defines static distribution methods for logical/physical offset identity mapping, next mapped offset, fixed contiguous length, logical file size, one-data-file selection, block size, empty parameter encode/decode, registration/unregistration, and params string. Exports `PINT_dist basic_dist`.

## Control Flow
All offset conversions return the input offset. `logical_file_size` returns `psizes[0]` and errors on NULL. `get_num_dfiles` always returns one. Method table `basic_methods` is attached to `basic_dist` for registry lookup and encoding/decoding.

## State And Persistence
Uses a static zero-sized parameter struct and static method table. No runtime persistence exists beyond distribution registration.

## Dependencies And Integration Points
Depends on `pint-distribution.h`, `pint-dist-utils.h`, PVFS types, and `pvfs2-dist-basic.h`. Registered by `PINT_dist_initialize`.

## Risks And Test Signals
Risks are minimal, but `contiguous_length` returns arbitrary 64 KiB chunks rather than unlimited contiguity and parameter encoding is intentionally empty. Tests should verify one-data-file selection, identity mappings, logical size from first physical size, and encode/decode of zero-parameter distribution.
