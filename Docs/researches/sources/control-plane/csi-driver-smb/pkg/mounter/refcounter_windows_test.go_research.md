# sources/control-plane/csi-driver-smb/pkg/mounter/refcounter_windows_test.go

## Purpose
Windows tests for SMB mapping reference counter behavior.

## Important APIs, Types, and Functions
Tests `lock`, `getRootMappingPath`, increment/decrement/count helpers, and MD5 reference file creation.

## Control Flow
Uses TEMP-derived base paths, creates references for volumes, checks counts, removes references, and cleans temp directories.

## State and Persistence
Creates temporary directories/files under `%TEMP%\TestMappingPathCounter`.

## Dependencies
Uses os, testing, time, and testify/assert.

## Integration Points
Validates cleanup logic used by Windows SMB unmount mapping removal.

## Risks and Edge Cases
Global `basePath` mutation can leak between parallel tests if ever run concurrently. Timing test for lock blocking is sleep-based.

## Test Signals
Passing tests verify expected reference count transitions and path parsing.
