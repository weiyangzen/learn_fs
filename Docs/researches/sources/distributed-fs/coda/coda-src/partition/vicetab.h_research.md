# sources/distributed-fs/coda/coda-src/partition/vicetab.h

Purpose: public API and constants for Coda partition table parsing.

Contract: defines default path `/vice/vicetab`, max line/string length, supported partition type strings (`simple`, `ftree`), opaque `Partent`, file operations, constructor/destructor, add/get, option lookup, integer option parsing, and field accessors.

Integration/risks: consumed by partition initialization, tests, and backends. Because `Partent` is opaque, callers cannot accidentally depend on layout, but they do depend on simple whitespace tokenization semantics. Missing `backup` type constant despite backend support is a small documentation/API mismatch.
