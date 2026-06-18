# sources/cloud-native/nydus/contrib/nydusify/pkg/backend/oss.go

## Purpose
This file implements the Alibaba Cloud OSS backend for Nydus blobs. It uploads blobs as multipart OSS objects, optionally skips existing objects, verifies CRC64 integrity, and exposes object readers/range readers.

## Important APIs, Types, and Functions
`OSSBackend` stores object prefix, OSS bucket, pending multipart statuses, and mutex. `multipartStatus` tracks initiated upload, parts, object key, and CRC channels. Functions include `newOSSBackend`, `calcCrc64ECMA`, `Upload`, `Finalize`, `Check`, `RangeReader`, `Reader`, `Size`, and `remoteID`.

## Control Flow
`newOSSBackend` parses JSON config, validates endpoint and bucket, creates SDK client and bucket handle. `Upload` builds a blob descriptor and URL, skips existing objects unless forced, starts CRC calculation in a goroutine, splits the file into 200 MB chunks, uploads parts concurrently with `errgroup`, appends multipart status, and returns before completion. `Finalize(false)` completes each multipart upload and compares server CRC64 against local CRC when available; `Finalize(true)` aborts pending uploads.

## State, Persistence, and Dependencies
Persistent state is OSS objects. In-memory state is the pending multipart list guarded by `msMutex`. Dependencies include aliyun OSS SDK, crc64, errgroup, logrus, HTTP headers, and OCI descriptors.

## Integration Points
Converter code can upload blobs into OSS while cache manifests record blob descriptors/remote IDs. Checker/cache can use `Check`, `Reader`, `RangeReader`, and `Size` for validation.

## Risks and Test Signals
Multipart upload is two-phase: callers must call `Finalize`, or uploaded parts may remain pending. CRC goroutine channels are consumed only in finalize. Object key is simple prefix concatenation, so missing slashes in prefix change paths. `calcCrc64ECMA` error text says md5sum, a misleading message. Tests cover config parsing, remote ID, type, and CRC calculation, but not real multipart upload/finalize.
