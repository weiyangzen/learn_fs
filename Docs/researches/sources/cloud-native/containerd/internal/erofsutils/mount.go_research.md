# sources/cloud-native/containerd/internal/erofsutils/mount.go

## Purpose
Provides helpers for recognizing, creating, indexing, and locating EROFS layer blobs used by containerd snapshot/differ paths.

## Important APIs, Types, And Functions
`IsErofsMediaType` checks media-type prefixes. `ConvertTarErofs`, `GenerateTarIndexAndAppendTar`, and `ConvertErofs` invoke `mkfs.erofs`. `AddDefaultMkfsOpts` adds macOS block-size defaults. `MountsToLayer` maps snapshot mounts back to an EROFS layer directory. `SupportGenerateFromTar` probes `mkfs.erofs --help`.

## Control Flow
Conversion functions assemble command arguments, attach stdin/environment, run `mkfs.erofs`, and wrap combined-output failures. Tar-index generation tees input to a temp file, writes an index, then appends original tar data to the output layer. `MountsToLayer` inspects mount type/options and requires `.erofslayer` marker.

## State And Persistence
Creates persistent EROFS layer files and temporary tar files. Uses marker files in layer directories to confirm EROFS snapshot ownership.

## Dependencies And Integration Points
Depends on external `mkfs.erofs`, containerd `mount.Mount`, errdefs, logging, and OS/runtime behavior. It integrates differs, snapshot mounts, and EROFS media-type handling.

## Risks
External command availability/version is critical. Mount option parsing assumes known overlay/bind/mkfs shapes. Temporary file storage can be large for tar-index generation.

## Test Signals
Indirectly covered by fsview EROFS tests that require `mkfs.erofs` tar support and by differ/snapshot integration tests outside this subset.
