# sources/cloud-native/composefs-rs/crates/composefs-oci/src/tar.rs

## Purpose
This module converts tar layer byte streams into composefs splitstreams and reads those splitstreams back into structured tar entries. It preserves tar bytes closely enough for OCI diff ID verification while moving large regular file content into external fs-verity objects.

## Important APIs, Types, and Functions
`split_async()` is the async tar-to-splitstream writer. `get_entry()` reads one logical tar entry from a `SplitStreamReader`. `TarItem<ObjectID>` models directory, leaf content, and hardlink entries. `TarEntry<ObjectID>` combines absolute path, `Stat`, and `TarItem`, and implements `Display` using dumpfile writers. Helpers include `pax_mtime_nsec()` for subsecond PAX mtime parsing, `receive_and_finalize_object()` for blocking tmpfile finalization, `stream_large_file()` for background external object streaming, and `make_absolute_path()` for tar path normalization.

## Control Flow
`split_async()` uses `tar_core::Parser` as a sans-IO tar parser and a `BytesMut` buffer. It reads enough bytes for the parser, handles global extensions inline, rejects sparse entries, and handles end-of-archive by preserving extra GNU record padding through EOF. For normal entries it writes headers and extension bytes inline, computes storage size rounded to 512 bytes, and chooses a content strategy. Regular files larger than `INLINE_CONTENT_MAX_V0` are streamed through an mpsc channel into a blocking task that writes a repository tmpfile and finalizes it as an external object; the splitstream builder records the external handle and then stores tar padding inline. Smaller files and non-file entries keep content and padding inline. `get_entry()` accumulates header blocks until `tar_core` emits a parsed entry, reads the stored payload from the splitstream as inline or external, maps tar entry types to composefs leaf content, extracts xattrs and PAX nanoseconds, and returns absolute paths.

## State and Persistence
The module persists splitstreams and external content objects in the composefs repository. Large file object writes use tmpfiles, fs-verity finalization, and object store methods surfaced through `ImportStats`. The splitstream stores tar metadata, small payloads, padding, and external object references, preserving byte-exact archive reconstruction through `SplitStreamReader::cat()`.

## Dependencies and Integration Points
It depends on `tar-core` parsing, `bytes`, `tokio` async IO and mpsc, `rustix::fs::makedev`, composefs splitstream/repository/tree/dumpfile types, and OCI import stats. It is called by layer import paths such as `skopeo.rs` for tar media types.

## Risks
The parser rejects sparse entries, so images using sparse tar extensions are unsupported. Large file streaming must consume exactly the file content before parsing continues; channel failure handling explicitly awaits the writer task because continuing would corrupt parser alignment. `actual_size as usize` can be risky on platforms where huge tar entries exceed addressable memory. `get_entry()` assumes external chunks only represent regular/continuous files and enforces inline/external threshold invariants. Path normalization strips leading and trailing slashes and maps bare root to an empty path, which is a deliberate composefs convention.

## Test Signals
The file has extensive tests: PAX mtime parsing, absolute path normalization, empty tar, GNU record padding preservation, small/large threshold behavior, byte-exact round trips, special filenames, GNU long names and long links, USTAR prefix handling, multiple large external files, long path and hardlink table tests, property tests across path lengths, hardlink targets, file sizes, and tar byte round trips. An ignored benchmark exercises large tar split throughput.
