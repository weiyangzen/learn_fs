# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt8ListIter.h

## Purpose
Provides typed iteration over `UInt8List`.

## Important APIs and control flow
Wraps `PointerListIter`; `value` converts the pointer slot back to `uint8_t`.

## State, dependencies, integration
Used by UInt8 list deserialization/serialization and consumers of byte-list data.

## Risks and test signals
End iterator value access is invalid. Test ordered byte iteration and max/min values.
