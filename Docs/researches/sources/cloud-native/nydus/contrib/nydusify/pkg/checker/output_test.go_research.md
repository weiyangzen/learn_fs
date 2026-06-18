# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/output_test.go

## Purpose
This file tests checker output generation, JSON dump error behavior, bootstrap unpacking, diff ID validation, and model artifact subject validation.

## Important APIs, Types, and Functions
It defines `buildBootstrapLayer` to create an in-memory gzip-compressed tar and tests `prettyDump` plus `Checker.Output`.

## Control Flow
Tests write OCI parsed artifacts to a temp directory and assert expected files exist. Nydus tests monkeypatch `Parser.PullNydusBootstrap`, first trigger diff ID mismatch, then model manifest missing subject, invalid subject media type, and success with a valid image manifest subject.

## State, Persistence, and Dependencies
Temporary directories are used for most output, but the Nydus validation test writes to literal `source` and removes it afterward. Dependencies include archive/tar, gzip, digest, OCI spec, parser, remote, utils, gomonkey, and testify.

## Integration Points
These tests ensure the checker’s filesystem outputs match downstream rule expectations.

## Risks and Test Signals
The literal `source` directory can collide with a working directory if cleanup fails. Tests do not cover empty diff ID slices or pull/decompression failures beyond the monkeypatched success path.
