<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/constant.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/constant.go

## Purpose

This file centralizes nydusify media types, layer filenames, manifest features, and OCI annotation keys shared across image conversion, parsing, snapshotter, and viewer code.

## Important APIs, Types, and Functions

It defines constants for the Nydus image manifest media type, Nydus OS feature marker, blob media type, bootstrap/backend filenames in layers, cache label, blob/bootstrap/source-chain/artifact annotations, uncompressed digest annotation, commit-blob and prefetch annotations.

## Control Flow

There is no executable control flow. The constants are imported by helpers such as platform matching, filesystem version detection, bootstrap extraction, and manifest construction.

## State and Persistence Behavior

The file itself has no state. Its values become persisted in OCI manifests, descriptors, layer annotations, and archive paths, making them part of the compatibility surface.

## Dependencies and Integration Points

Constants are consumed by `utils.GetNydusFsVersionOrDefault`, `viewer.PullBootstrap`, parser/generator code, and external snapshotter workflows. They align nydusify with containerd snapshot annotations and Nydus runtime expectations.

## Risks and Test Signals

Typos or value changes would break image recognition, bootstrap lookup, or snapshotter behavior across components. Adjacent tests cover some constants indirectly through platform and fs-version helpers, but the constants file has no direct exhaustive test.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/constant.go -->
