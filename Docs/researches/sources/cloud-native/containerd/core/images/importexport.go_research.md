# sources/cloud-native/containerd/core/images/importexport.go

## Purpose

This file declares the abstraction boundaries for image import and export implementations. It does not implement tar parsing or writing; it standardizes the interfaces consumed by higher-level image transfer code.

## Important APIs, Types, and Functions

`Importer` has `Import(ctx, store, reader) (ocispec.Descriptor, error)`, taking a content store and tar stream reader and returning the imported root descriptor. `Exporter` has `Export(ctx, store, desc, writer) error`, taking a content provider, root descriptor, and tar stream writer.

## Control Flow

There is no executable control flow beyond interface method signatures. Implementations define the actual import/export sequence.

## State and Persistence Behavior

Import implementations are expected to write content into a `content.Store`; export implementations read from a `content.Provider` and write to an `io.Writer`. This file owns no state.

## Dependencies and Integration Points

The interfaces depend on `context`, `io`, `core/content`, and OCI descriptors. They connect archive import/export implementations to containerd's content-addressed storage without binding callers to a concrete implementation.

## Risks and Edge Cases

The interfaces do not express image record creation, leases, namespace behavior, platform filtering, or progress reporting. Implementations must define tar format support, duplicate blob handling, descriptor validation, and error semantics.

## Test Signals

Interface-level signals are compile-time conformance for import/export implementations and integration tests that import an archive into a content store and export it back with descriptor and content integrity preserved.
