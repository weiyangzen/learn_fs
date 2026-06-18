<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzip/gz.h -->
# sources/cloud-native/overlaybd/src/overlaybd/gzip/gz.h

## Purpose
Declares gzip adapter APIs and the `IGzFile` interface for stream readers that can save generated indexes and report compressed-stream checksum.

## Important APIs, Types, And Functions
`IGzFile` extends Photon `VirtualReadOnlyFile` with `save_index` and `sha256_checksum`. Exports `open_gzfile_adaptor` and `open_gzstream_file`.

## Control Flow
Callers wrap either a filesystem gzip path or a Photon stream. Stream users read decompressed bytes and call `save_index` when complete.

## State And Persistence
The interface itself owns no state; implementations may create temporary files and persisted index outputs.

## Dependencies And Integration Points
Includes Photon filesystem/virtual-file and network socket stream types. Used by gzindex tests and stream conversion components.

## Risks And Test Signals
`open_gzstream_file` defaults `save_index=true` and workdir to current directory. Lifetime and stream ownership are implementation-defined. Source size reviewed: 33 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzip/gz.h -->
