# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileSystemIterator.hh

## Purpose
This header declares `FileSystemIterator`, an iterator abstraction for fsview keys in QuarkDB. It lets callers enumerate known filesystem views without exposing qclient scanner parsing details.

## Important APIs, Types, and Functions
The constructor takes a `qclient::QClient&`. Public methods return the parsed filesystem id, whether the current key is an unlinked view, the raw Redis key, validity, and advance operation. Private parsing methods split and validate scanner keys.

## Control Flow
The class follows a simple valid/current/next iterator model. Construction positions the iterator at the first valid fsview key, and `next()` moves to the next valid key.

## State and Persistence Behavior
It stores only scanner state and the parsed current key. It has no persistence behavior and no ownership of the qclient.

## Dependencies and Integration Points
It includes EOS namespace macros, `IFileMD` for location type, and `QScanner`. It is a utility for fsview consistency checks and any code that needs raw fsview set keys.

## Risks and Test Signals
The API exposes parsed values only when `valid()` is true; callers should not read them after invalidation. Tests should verify constructor skip behavior and that `getRedisKey()` remains aligned with the parsed id/unlinked state.
