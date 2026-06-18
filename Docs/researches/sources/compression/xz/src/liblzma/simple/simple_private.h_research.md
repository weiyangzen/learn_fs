# sources/compression/xz/src/liblzma/simple/simple_private.h

## Purpose
Defines the private wrapper state for simple/BCJ filters and declares the common initializer used by architecture filters.

## Important APIs, Types, And Functions
- `lzma_simple_coder` stores next coder, end flag, direction flag, filter callback, optional filter-specific state, current position, buffer allocation/positions, and flexible buffer.
- `lzma_simple_coder_init()` declaration accepts filter callback, private-state size, maximum unfiltered tail, alignment, and direction.

## Control Flow
No direct control flow; describes the callback signature that architecture filters implement.

## State And Persistence
Defines all persistent state used by `simple_coder.c`, including unflushed filtered bytes and unfiltered tail bytes.

## Dependencies And Integration Points
Includes `simple_coder.h`. Used by all architecture-specific simple filter implementations.

## Risks
Flexible-array allocation size must match `allocated`. Callback contract requires returning the number of bytes safely filtered and leaving incomplete instruction tails unfiltered.

## Test Signals
Wrapper streaming tests for every filter and struct allocation/free tests under sanitizers.
