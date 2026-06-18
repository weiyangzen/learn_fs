# sources/cloud-native/containerd/core/images/image_test.go

## Purpose

This test file validates media-type consistency checks for image manifests and indexes. It protects callers from accepting content whose descriptor media type disagrees with the JSON document shape or embedded `mediaType` value.

## Important APIs, Types, and Functions

`TestValidateMediaType` is the only test. It builds OCI manifest and index documents, then calls unexported `validateMediaType` with Docker schema 2 manifest, OCI manifest, Docker manifest list, and OCI index media types. It also constructs documents containing only an embedded `mediaType` field and a schema1-style `fsLayers` field.

## Control Flow

The test first loops over descriptor media types and checks that manifest-shaped JSON is accepted only for manifest types and index-shaped JSON only for index types. It then loops over embedded media-type compatibility tables, asserting that manifest descriptors accept manifest embedded types and reject index embedded types, and vice versa. The final subtest checks schema1 detection through `fsLayers`.

## State and Persistence Behavior

The test is fully in-memory. It marshals JSON with `encoding/json` and does not touch content stores, metadata DBs, or global state.

## Dependencies and Integration Points

It depends on `ocispec.Manifest`, `ocispec.Index`, Docker/OCI media-type constants from the package under test, and `testify` assertions. It gives regression coverage for `Children` and `Manifest`, because both call `validateMediaType` before unmarshalling typed image documents.

## Risks and Edge Cases

The test focuses on structural mismatch and embedded media-type mismatch but does not cover invalid JSON, empty documents, documents containing both config/layers and manifests, or future media types. It also does not exercise error wrapping text from callers.

## Test Signals

Passing this test signals that descriptor/document type mismatches are rejected for the core Docker and OCI manifest/index media types and Docker schema1 content remains unsupported.
