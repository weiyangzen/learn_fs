# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/RangeNotSatisfiableEOFException.java

Purpose: EOFException subclass representing HTTP 416 Range Not Satisfiable.

Important APIs/types: constructor accepts operation and cause, uses operation as message, and initializes cause.

Control flow: exception translation maps range failures to this type so readers expecting EOF semantics continue to work.

State and persistence behavior: standard exception message/cause only.

Dependencies and integration points: used by S3A input stream/range read logic and retry/error handling.

Risks: callers must distinguish legitimate EOF from stale metadata or file-change cases where remote object length changed.

Test signals: range-read tests should assert 416 responses are catchable as `EOFException` and preserve the underlying cause.
