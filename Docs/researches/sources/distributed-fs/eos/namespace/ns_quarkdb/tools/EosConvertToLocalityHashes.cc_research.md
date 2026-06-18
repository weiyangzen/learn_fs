# sources/distributed-fs/eos/namespace/ns_quarkdb/tools/EosConvertToLocalityHashes.cc

## Purpose
This standalone migration tool converts older QuarkDB namespace metadata stored in hash buckets into the newer locality-hash layout. It is explicitly described as a temporary compatibility tool for EOS instances created before the automatic new layout cutoff.

## Important APIs, Types, and Functions
`processFileBucket(qclient::QClient&, uint64_t)` scans one old file metadata bucket, deserializes each `FileMdProto`, computes a locality hint from the parent container ID and file name, and invokes `CONVERT-HASH-FIELD-TO-LHASH`. `processContainerBucket(qclient::QClient&, uint64_t)` does the same for `ContainerMdProto`, using parent ID and container name. `main()` parses a single comma-separated QuarkDB member list, configures `qclient::QClient` with transparent redirects and timeout retries, then iterates all configured file and container bucket IDs.

## Control Flow
Each bucket processor runs `HLEN` against the old bucket, aborts on unexpected response types, prints progress, then iterates a `qclient::QHash`. On every item it deserializes the protobuf payload via `Serialization::deserialize()`, aborts on parse errors, builds the locality hint with `LocalityHint::build()`, and sends the conversion command. Progress is printed every 1024 entries. `main()` processes `1024 * 1024` file buckets and `128 * 1024` container buckets, calling each bucket processor twice, presumably to tolerate conversion side effects while iterating the bucket.

## State and Persistence Behavior
The tool mutates QuarkDB namespace metadata layout in place. It reads old hash bucket keys such as `<bucket> + sFileKeySuffix` or `<bucket> + sContKeySuffix` and writes locality-hash entries under `constants::sFileKey` or `constants::sContainerKey`. Failures call `std::abort()`, so partial conversion is possible and operational recovery depends on command idempotency.

## Dependencies and Integration Points
It depends on QuarkDB client APIs, `qclient::Members`, `qclient::QHash`, EOS namespace constants, metadata serialization, request/persistency headers, and `LocalityHint`. It integrates at the storage-layout level rather than through the higher-level metadata services.

## Risks and Edge Cases
This is a dangerous live-data migration utility. It lacks dry-run mode, authentication handling, checkpointing, resumable progress state, or detailed error recovery. The double-processing loop makes idempotency of `CONVERT-HASH-FIELD-TO-LHASH` critical. Because it aborts on a single malformed protobuf, one corrupt metadata entry can stop the whole conversion. Performance is dominated by scanning more than one million file buckets even if most are empty.

## Test Signals
There are no tests in this file. Useful validation would run against a controlled QuarkDB dataset with known old buckets, verify locality-hash entries and locality hints, rerun to prove idempotency, and inject malformed bucket values to confirm failure behavior.
