<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile.h -->
# sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile.h

## Purpose
Declares the public gzip-index API for creating random-access gzip file adapters and building index files.

## Important APIs, Types, And Functions
Exports `new_gzfile`, `create_gz_index`, and `is_gzfile`. Documents default chunk size and dictionary compression options.

## Control Flow
Consumers first create an index with `create_gz_index`, open gzip and index files, then wrap them with `new_gzfile` for `pread` support.

## State And Persistence
`create_gz_index` writes an index file; `new_gzfile` optionally owns the supplied file handles.

## Dependencies And Integration Points
Includes Photon filesystem and `gzfile_index.h`. Used by `gzip/gz.cpp` stream index save and `gzindex/test`.

## Risks And Test Signals
Ownership defaults to false, so caller lifetime management matters. Source size reviewed: 41 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile.h -->
