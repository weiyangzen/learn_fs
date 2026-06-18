# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_filter.cc

## Purpose
`rgw_dedup_filter.cc` implements bucket and storage-class filtering for dedup scans. It lets admin restart commands restrict scans by allowlist or denylist files and serializes the selected filter for watcher delivery.

## Important APIs, Types, And Functions
`dedup_filter_t::allow_bucket()` and `allow_storage_class()` apply `FILTER_NONE`, `FILTER_ALLOW`, or `FILTER_DENY` to bucket names and storage class names. `read_filter_file()` reads one name per line, strips `#` comments, trims whitespace, validates names, and populates a set.

The file-level validators currently return success unconditionally, intentionally allowing all strings rather than enforcing S3 bucket-name or storage-class validation. The constructor enforces mutual exclusion between allow and deny files per dimension, reads the configured files, sets modes, and records negative errno in `d_errcode` on failure.

`encode()` and `decode()` persist the two modes plus bucket set and storage-class vector in Ceph encoding version 1.

## Control Flow
The constructor validates arguments first. It then reads either the bucket allow file or bucket deny file, then either the storage-class allow file or storage-class deny file. Storage classes are read into a temporary set for deduplication and then moved to a vector for cheap iteration.

At scan time, bucket ingress calls filter methods to decide whether to scan a bucket and whether to skip an object based on its storage class. On restart, `rgw_dedup_cluster.cc` encodes an optional filter into the restart notify payload.

## State And Persistence Behavior
The runtime state is the bucket mode and set, storage-class mode and vector, and construction error code. The filter is not stored independently in RADOS; it is encoded into the restart notification payload and then held in the background service's `d_filter`.

## Dependencies And Integration Points
The file depends on Ceph bufferlist encoding, `DoutPrefixProvider` logging, errno values, and the S3 REST header context for potential validation. It integrates directly with dedup restart and object ingress.

## Risks And Edge Cases
Empty filter files return `-ENODATA`. Opening a missing file returns `-ENOENT`. Since validation accepts all strings, typos in names are not rejected and become silent allow or deny entries. Storage-class order is nondeterministic because it is copied from an unordered set; current logic only performs membership checks, so order is not semantic.

## Test Signals
Tests should cover comment stripping, whitespace trimming, empty files, duplicate names, mutually exclusive arguments, allow and deny behavior for buckets and storage classes, and encode/decode round trips with active and inactive filters.
