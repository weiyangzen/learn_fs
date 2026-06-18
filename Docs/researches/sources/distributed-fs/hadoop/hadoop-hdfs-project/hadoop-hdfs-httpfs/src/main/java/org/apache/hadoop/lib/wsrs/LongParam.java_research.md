# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/LongParam.java

## Purpose
`LongParam` parses long integer query parameters for HttpFS REST operations.

## Important APIs, Types, and Functions
It extends `Param<Long>`, parses with `Long.parseLong(str)`, and describes its domain as `"a long"`.

## Control Flow
Blank and absent values keep defaults through the base parser. Nonblank values must be valid Java decimal long values.

## State and Persistence
Only per-instance parsed value is kept; no persistence occurs.

## Dependencies and Integration Points
Concrete HttpFS parameters use long values for offsets, lengths, block sizes, timestamps, and new truncate lengths. These values are then passed to Hadoop `FileSystem` or HDFS APIs.

## Risks
No range, unit, or sentinel validation is done in this base class. Negative values may be valid for some APIs and invalid for others, so endpoint logic must enforce semantics.

## Test Signals
`BaseTestHttpFSWith` exercises long-valued paths such as create block size, setTimes timestamps, truncate length, block-location offsets/lengths, and snapshot diff listing.
