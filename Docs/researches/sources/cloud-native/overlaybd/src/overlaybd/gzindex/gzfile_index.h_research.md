<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile_index.h -->
# sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile_index.h

## Purpose
Defines the on-disk gzip index format, index entries, constants, and helper declarations shared by index creation, stream indexing, and indexed reads.

## Important APIs, Types, And Functions
Constants include `GZ_CHUNK_SIZE`, `GZ_DICT_COMPERSS_ALGO`, `WINSIZE`, and magic `ddgzidx`. `IndexFileHeader` stores version, dictionary compression, span/window, index sizing, gzip/uncompressed/index file sizes, offsets, and CRC. `IndexEntry` stores decompressed position, compressed position, dictionary position, bit prime count, and dictionary length. Declares `IndexFilterRecorder` helpers, header init, entry creation, and save routines.

## Control Flow
Index builders initialize a header, record entries while inflating gzip blocks, then serialize dictionaries and compressed index entries. Readers validate the header and use entries to restart inflate near a target offset.

## State And Persistence
This header defines the persisted packed ABI for `.gz_idx` files.

## Dependencies And Integration Points
Depends on zlib types, Photon `IFile`, and CRC32C. Shared by `gzfile.cpp`, `gzip_index_create.cpp`, and `gzip/gz.cpp`.

## Risks And Test Signals
Packed structs and `off_t` fields make cross-platform ABI/endian/word-size compatibility important. Misspelled macro `GZ_DICT_COMPERSS_ALGO` is part of the public header. Header CRC excludes only the trailing CRC field. Source size reviewed: 96 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile_index.h -->
