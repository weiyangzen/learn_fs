# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/CloudCostUtils.java

## Purpose
`CloudCostUtils` estimates cloud object-store API cost savings from avoided UFS metadata operations. It maps UFS operation types to hard-coded per-operation prices for S3, ABFS, GCS, and OSS.

## Important APIs and Types
- Static immutable cost maps for `UFSOps.CREATE_FILE`, `GET_FILE_INFO`, `DELETE_FILE`, and `LIST_STATUS`.
- `COSTMAP` maps UFS type strings (`abfs`, `gcs`, `s3`, `oss`) to cost maps.
- `calculateCost(String, Map<String, Long>)` totals operation count times per-operation price, ignoring unknown operation names.

## Control Flow
If the UFS type is unsupported, `calculateCost` returns zero. Otherwise it iterates the per-UFS operation count map, parses each string as `UFSOps`, multiplies by the configured price if present, and ignores invalid enum names.

## State and Persistence
No mutable state or persistence. Pricing constants are embedded in code with comments noting last update dates from 2021.

## Dependencies and Integration Points
Depends on `DefaultFileSystemMaster.Metrics.UFSOps` and Guava `ImmutableMap`. Used by metrics/reporting code that converts saved UFS operations into estimated monetary savings.

## Risks and Edge Cases
- Prices are static and likely stale; output should be treated as an estimate.
- UFS type matching is lowercase and exact.
- Unknown operations and unsupported UFS types silently contribute zero.

## Test Signals
Tests should cover each provider map, unsupported provider returning zero, invalid operation names ignored, and expected arithmetic for mixed operation counts.
