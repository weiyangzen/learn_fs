# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/stargz_adaptor.go

This file adds estargz compatibility paths to `Filesystem`. `UpperPath` maps snapshot IDs to the upper filesystem directory. `StargzEnabled` checks resolver configuration. `IsStargzDataLayer` parses registry labels, builds auth, fetches a stargz blob, and detects TOC offset to decide whether the layer is estargz.

`PrepareStargzMetaLayer` downloads the stargz TOC, writes it to storage, chooses a blob-meta path based on fscache mode, and runs the configured nydusd binary as `nydus-image create --source-type stargz_index` to generate a Nydus bootstrap and `.blob.meta`. `MergeStargzMetaLayer` locates per-parent bootstraps, copies non-base blob-meta files into the first parent, and either reflinks a single bootstrap or invokes `nydus-image merge` to build `image.boot`. `StargzLayer` checks the stargz label marker.

State is file-heavy: TOC files, converted bootstraps, blob-meta files, temp files, chmodded outputs, and copied metadata. Dependencies include auth, registry label parsing, stargz resolver, reflink, nydusd/nydus-image CLI behavior, digest validation, and global fs-driver config. Risks include external command failures, assumptions about parent order, temp cleanup, file-name digest detection, and no direct tests in this subset.
