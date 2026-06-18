# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/convert.go

Purpose: Defines `ctr-remote images convert`, a containerd image conversion command for eStargz, external TOC eStargz, zstd:chunked, uncompressed layers, and OCI media conversion.

Important APIs: `ConvertCommand`, `getESGZConvertOpts`, `getZstdchunkedConvertOpts`, and `readPathsFromRecordFile`. Flags control conversion type, compression/chunking, record-in prioritization, external TOC, keep-diff-id mode, gzip helper, and platform selection.

Control flow: The action validates source/target refs, selects platform matcher, builds a layer convert function based on mutually exclusive flags, optionally enables Docker-to-OCI conversion, opens a containerd client and lease, handles interrupts by cancelling context, runs `converter.Convert`, performs external TOC finalization if needed, and prints resulting digest and extra image name.

State and persistence: Writes converted image content and image records into containerd's content/image stores. Reads optional record JSON from the filesystem.

Dependencies and integration: Uses containerd converter APIs, native converter packages, eStargz options, zstd, recorder entries, and gzip helper utilities.

Risks: Some invalid flag combinations are caught explicitly. `readPathsFromRecordFile` streams JSON entries with `dec.More()` at top level, relying on recorder output format. External TOC creates an additional image and deletes any existing image by that name.

Test signals: No direct tests in this subset; conversion behavior is likely covered in converter package tests elsewhere.
