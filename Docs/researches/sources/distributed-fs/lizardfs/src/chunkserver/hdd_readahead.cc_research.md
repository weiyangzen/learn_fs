# sources/distributed-fs/lizardfs/src/chunkserver/hdd_readahead.cc

## Purpose
`hdd_readahead.cc` defines the global `HDDReadAhead` configuration object used by chunkserver HDD read operations.

## Important APIs, Types, And Functions
- `HDDReadAhead gHDDReadAhead;`

## Control Flow
The object is default-constructed at process startup and accessed through the extern declaration in the header.

## State And Persistence
Runtime read-behind/read-ahead settings live in atomic fields inside `gHDDReadAhead`. There is no direct persistence; configuration reload code elsewhere likely sets values.

## Dependencies And Integration Points
`bgjobs.cc` passes readahead/readbehind values into `hdd_read`; other code can read or update `gHDDReadAhead`.

## Risks
Default atomic values are not explicitly initialized in `HDDReadAhead`, so unless default construction value-initializes them elsewhere or configuration sets them before use, startup defaults may be unclear.

## Test Signals
`hdd_readahead_unittest.cc` tests conversion behavior using local `HDDReadAhead` instances, not the global object.
