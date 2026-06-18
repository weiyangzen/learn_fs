<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/utils.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/utils.go

## Purpose

This file provides general nydusify utility functions for platform detection, retry policy, descriptor marshaling, archive extraction, path checks, and Blake3 file hashing.

## Important APIs, Types, and Functions

It defines supported OS/architecture constants, `FsVersion` (`V5`, `V6`), `GetNydusFsVersionOrDefault`, `WithRetry`, `RetryWithAttempts`, `RetryWithHTTP`, `MarshalToDesc`, `IsNydusPlatform`, `IsSupportedArch`, `MatchNydusPlatform`, `UnpackFile`, `UnpackFromTar`, `unpackTarPath`, `IsEmptyString`, `IsPathExists`, and `HashFile`.

## Control Flow

Retry helpers loop until success, non-retryable error, cancellation, or exhausted attempts. Platform helpers inspect OCI platform fields and `OSFeatures`. Archive helpers decompress streams, iterate tar entries, copy matching content, and sanitize tar paths before writing. `HashFile` streams 64 KiB chunks into a Blake3 hasher.

## State and Persistence Behavior

`UnpackFile` and `UnpackFromTar` write target files/directories. Other helpers are stateless except for sleeping in retries and reading files/environmental behavior through dependencies.

## Dependencies and Integration Points

The file integrates with containerd compression, Harbor acceleration retry classification, OCI image specs, OpenContainers digest, logrus, syscall errors, and Blake3. It is used by parser, viewer, image conversion, and tests.

## Risks and Test Signals

`UnpackFile` creates the target without parent directory creation and ignores non-EOF tar errors in the loop until the next iteration. `WithRetry` sleeps before retrying after the first failure and retries 401 as an HTTP retryable condition. `UnpackFromTar` has explicit traversal protection. Tests cover platform helpers, retries, descriptor digest, file extraction, hashing, and traversal rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/utils.go -->
