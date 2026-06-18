# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_filter.h

## Purpose
`rgw_dedup_filter.h` declares the filter contract used to include or exclude buckets and storage classes from dedup scans.

## Important APIs, Types, And Functions
`filter_mode_t` has `FILTER_NONE`, `FILTER_ALLOW`, and `FILTER_DENY`. `dedup_filter_t` exposes a default all-pass constructor, a file-path constructor, `errcode()`, `is_active()`, `allow_bucket()`, `allow_storage_class()`, and getters for the encoded filter contents.

Friend `encode()` and `decode()` functions serialize private fields for restart notifications.

## Control Flow
The background dedup service can be restarted with an encoded filter. During ingress, code checks `is_active()` or calls the allow methods as it iterates buckets and objects. A failed constructor leaves the object with `d_errcode` set and should prevent issuing a restart with invalid filter input.

## State And Persistence Behavior
The object holds bucket membership in an unordered set and storage-class membership in a vector. There is no direct persistent storage in this header; persistence is by bufferlist encoding in command payloads.

## Dependencies And Integration Points
It depends on Ceph encoding and logging types. It is included by the cluster coordinator and main dedup background service.

## Risks And Edge Cases
Callers must check `errcode()` after using the file-path constructor. The getters expose internal containers by const reference, so lifetime is tied to the filter object. Future encoding changes need versioned compatibility.

## Test Signals
Header-level expectations include inactive default behavior, correct active detection for each dimension, and stable encode/decode API linkage.
