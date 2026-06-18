# sources/distributed-fs/seaweedfs/weed/s3api/s3api_put_object_helper.go

## Purpose

This helper chooses the correct request body reader for S3 PUT processing.

## Important APIs, Types, and Functions

The sole function is `getRequestDataReader`, using `getRequestAuthType`, IAM enablement, and `iam.newChunkedReader`.

## Control Flow

With IAM enabled, signed and unsigned streaming payloads use the chunked reader. With IAM disabled, signed streaming fails with `ErrAuthNotSetup`, while unsigned streaming still uses the chunked reader to strip AWS chunk framing and checksum trailers. Regular requests pass through unchanged.

## State and Persistence Behavior

No persistent state is changed, but reader choice determines what bytes are eventually stored in the filer.

## Dependencies and Integration Points

The helper depends on IAM auth-type detection and chunked-reader implementation. It integrates with PUT and upload-part handlers before encryption and storage.

## Risks and Edge Cases

The main risk is storing chunk framing as object data when IAM is disabled. Accepting signed streaming without IAM would skip signature validation, so it is rejected.

## Test Signals

Companion tests cover regular, signed, unsigned, checksum-trailer, IAM-enabled, and auth-type detection cases.
