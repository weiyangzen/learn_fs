# sources/cloud-native/nydus/contrib/nydusify/pkg/backend/backend_test.go

## Purpose
This test file validates backend descriptor generation and factory selection.

## Important APIs, Types, and Functions
Tests include `TestBlobDesc` and `TestNewBackend`. They exercise `blobDesc`, `NewBackend`, `newOSSBackend`, `newS3Backend`, and `newRegistryBackend` indirectly.

## Control Flow
The tests build sample JSON configs, construct backends for OSS/S3/registry, assert returned type constants, and assert unsupported types return errors. `TestBlobDesc` checks size, digest, media type, and annotations.

## State, Persistence, and Dependencies
Tests do not contact real services. SDK constructors validate some local config shape. Dependencies include `testify/require`, JSON validation, provider remote creation, and utility constants.

## Integration Points
These tests guard the backend creation contract used by CLI and conversion code.

## Risks and Test Signals
They do not test actual upload/read/check behavior or network paths. They rely on SDK validation for OSS/S3 config without mocking remote object storage.
