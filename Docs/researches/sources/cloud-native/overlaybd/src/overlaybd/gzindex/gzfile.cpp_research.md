<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile.cpp

## Purpose
Implements a read-only random-access view of a gzip file using a separately generated index of deflate restart points and dictionaries.

## Important APIs, Types, And Functions
Defines internal `GzFile` with `pread`, `fstat`, `init`, `parse_index`, `seek_index`, `extract`, and `get_dict_by_index`. Exports `new_gzfile` and `is_gzfile`.

## Control Flow
First read or stat lazily initializes by reading and validating `IndexFileHeader`, checking CRC/magic/version/index size/gzip size, and parsing compressed or uncompressed `IndexEntry` array. `pread` finds the nearest index entry at or before requested decompressed offset, initializes raw deflate inflate state, primes partial bits if needed, loads the saved 32 KiB dictionary, skips bytes up to the requested offset, then fills the caller buffer.

## State And Persistence
State includes underlying gzip/index file pointers, parsed header, heap-owned vector of `IndexEntry*`, init mutex, and optional file ownership. Index file is read-only during normal use.

## Dependencies And Integration Points
Depends on zlib, Photon `VirtualReadOnlyFile`, Photon filesystem/stat APIs, CRC32C, and index format from `gzfile_index.h`. Used directly in gzindex tests and by gzip-cache integration.

## Risks And Test Signals
`pread` does not clamp count against uncompressed size itself; zlib stream end returns short reads. Index parsing allocates one entry per index point and destructor does not visibly free `index_` entries, implying a leak. `is_gzfile` changes file position and requires seekable input. Tests cover fixed, OOB, random, cached, and fstat reads. Source size reviewed: 381 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile.cpp -->
