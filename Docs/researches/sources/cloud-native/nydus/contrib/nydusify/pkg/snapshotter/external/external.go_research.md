<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/external.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/external.go

## Purpose

This file is the high-level entry point for generating external snapshotter metadata artifacts. It turns either local walked files or remote modctl-provided attributes into metadata, backend JSON, attribute text, and placeholder files for build context integration.

## Important APIs, Types, and Functions

`Options` carries the local directory, context directory, handler implementations, and output paths. `Handle` runs `backend.NewWalker().Walk`, constructs `Generators`, writes meta bytes, backend JSON, and attributes. `buildAttr` formats file attributes for local external files. `RemoteHandle` obtains backend and file attributes from `RemoteHandler`, writes backend and attributes, then calls `buildEmptyFiles`. `buildEmptyFiles` creates empty placeholder files with recorded modes.

## Control Flow

Local handling is a pipeline: walk source files, convert chunks to on-disk metadata, build attribute lines, and write all outputs. Remote handling bypasses metadata generation, formats richer attribute lines including file size and CRCs, writes backend configuration, and materializes empty files in the context directory.

## State and Persistence Behavior

The file writes `MetaOutput`, `BackendOutput`, `AttributesOutput`, and remote-mode placeholder files. Writes use fixed mode `0644` for outputs and the backend-provided file mode for placeholders. Existing files are overwritten.

## Dependencies and Integration Points

It integrates with `backend.Walker`, `backend.Handler`, `backend.RemoteHanlder`, `NewGenerators`, JSON serialization, and logrus debug logging. The generated attribute format is consumed by external snapshotter/image build flows.

## Risks and Test Signals

Risks include path traversal or absolute paths in remote `RelativePath` values because `buildEmptyFiles` joins with `fmt.Sprintf`, empty attribute files when no chunks are returned, and inconsistent local/remote attribute field sets. Tests cover happy paths and placeholder modes but not malicious relative paths or output write failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/external.go -->
