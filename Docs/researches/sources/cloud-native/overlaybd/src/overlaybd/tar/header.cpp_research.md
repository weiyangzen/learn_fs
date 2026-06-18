# sources/cloud-native/overlaybd/src/overlaybd/tar/header.cpp

Purpose: tar header parsing, path normalization, GNU long name/link handling, PAX local/global header parsing, size/path/link overrides, and tar header checksum/mode helpers for `TarCore`.

Important APIs/types/functions: `clean_name` normalizes path strings in place. `remove_last_slash` strips a trailing slash from a `string_view`. `TarCore::get_pathname`, `get_linkname`, and `get_size` apply PAX/GNU overrides before falling back to POSIX header fields. `TarCore::read_header_internal`, `read_sepcial_file`, and `read_header` advance through tar records. `PaxHeader::read_pax` and `parse_pax_records` decode PAX key/value lines. `TarHeader::get_mode`, `get_uid`, `get_gid`, `crc_calc`, and `signed_crc_calc` expose decoded metadata.

Control flow: `read_header` resets prior GNU/PAX state, reads a 512-byte header, treats two zero blocks as EOF unless ignored, validates magic/version/checksum according to option flags, and loops over GNU long name/link and PAX headers until it reaches a real file header. Special header payloads are read in whole 512-byte blocks and optionally copied to a dump file. PAX parsing stores all records and applies supported keys `size`, `path`, and `linkpath`; xattr keys are recognized but left as records for extraction.

State and persistence: `TarCore` owns current `TarHeader`, optional `PaxHeader`, and cached pathname/linkname buffers. When `dump` is supplied, regular file data offsets are temporarily stored in the header's `devmajor` bytes before writing the header to a metadata stream. This metadata stream is later consumed by meta-only extraction paths.

Dependencies/integration: used by `UnTar` extraction, tar metadata dump/replay, `TarFile` adaptor header detection, and EROFS tar ingestion. It depends on Photon `IFile`, path/logging utilities, POSIX tar constants, and option flags from `libtar.h`.

Risks: `read_sepcial_file` returns `int` but stores `size_t` values, and callers compare `size_t sz < 0`, which is ineffective. PAX support ignores many keys except size/path/linkpath and xattr records. PAX `strdup(rec.second.data())` assumes null termination of `std::string::data()`. The metadata dump's reuse of `devmajor` for offsets is non-obvious and corrupts normal device fields in the dumped header stream by design.

Test signals: `tar/test/test.cpp` covers `clean_name` and tar metadata dumping. `erofs_simple.cpp` covers PAX path behavior and EROFS metadata rebuilds.
