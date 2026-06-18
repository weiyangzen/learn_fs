
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_status.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_status.go

## Purpose

This file implements CRI `ImageStatus` and conversion of internal CRI image metadata into CRI `runtime.Image` and optional verbose info.

## Important APIs, Types, and Functions

Key functions are `(*CRIImageService).ImageStatus`, `toCRIImage`, package-local `getUserFromImage`, `verboseImageInfo`, and `(*CRIImageService).toCRIImageInfo`.

## Control Flow

`ImageStatus` resolves the requested image locally. `NotFound` returns an empty response with no error. Other resolution errors are wrapped. For found images, it converts the image to CRI fields, optionally builds verbose info, and returns both. `toCRIImage` splits references into repo tags and repo digests, copies ID, size, pinned flag, and converts image config user into either `Uid` or `Username`. Verbose info JSON includes chain ID and the OCI image spec under the `"info"` map key.

## State and Persistence Behavior

The file is read-only. It does not verify snapshot/content readiness at status time and does not refresh image-store metadata.

## Dependencies and Integration Points

Dependencies include JSON encoding, CRI runtime API, image-spec, CRI image store, CRI util reference parsing, errdefs, and logging. The conversion helper is also used by `ListImages`.

## Risks and Edge Cases

Returning empty success for missing images matches CRI semantics but can hide stale references. Verbose JSON marshal errors are logged and returned as the info string rather than failing the status call. `getUserFromImage` ignores group fields and treats only the substring before `:`. Snapshot readiness is a TODO.

## Test Signals

Existing tests cover missing image response, found image conversion, and user parsing for numeric, username, empty, and multi-separator forms. Additional tests should cover verbose info, pinned images, marshal failure behavior, and stale snapshot/content conditions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_status.go -->
