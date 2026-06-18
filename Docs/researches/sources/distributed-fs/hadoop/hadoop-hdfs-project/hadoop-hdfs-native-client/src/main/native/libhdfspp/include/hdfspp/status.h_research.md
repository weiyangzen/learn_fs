# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/status.h

## Purpose
`Status` is libhdfs++'s value-type error carrier for synchronous returns and asynchronous callbacks.

## Important APIs, Control Flow, and State
An OK status has code 0. Factory methods create invalid argument, resource unavailable, unimplemented, server exception, generic error, authentication/authorization failure, canceled, path not found, invalid offset, not-a-directory, and mutex errors. `ok`, `is_invalid_offset`, `pathNotFound`, `code`, `ToString`, `notWorthRetry`, and server exception accessors expose classification. Codes map common cases to `std::errc` values and reserve non-errc codes from 256 for Hadoop/server-specific errors.

## Dependencies and Integration Points
Every libhdfs++ public API uses `Status`. Event responses, config validation, RPC retry/failover logic, C errno translation, and examples all depend on consistent code mapping.

## Risks and Test Signals
Changing codes can break retry decisions and C binding errno mapping. Tests should cover every factory, `ToString`, `notWorthRetry`, server exception class/detail preservation, equality-by-code assumptions if any, and mapping from NameNode Java exceptions such as StandbyException and AccessControlException.
