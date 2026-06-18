# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-misc.h

## Purpose
Collects shared changelog format constants, socket path builders, header parsing macro, HTIME/CSNAP path macros, event type enums, mode enum, and encoder enum.

## APIs, Types, and Functions
Defines file and xattr names (`CHANGELOG`, `HTIME`, `CHANGELOG.SNAP`, `trusted.glusterfs.htime`, `trusted.glusterfs.current_htime`), format version 1.2, Unix socket templates, `CHANGELOG_HEADER`, `CHANGELOG_MAKE_SOCKET_PATH()`, `CHANGELOG_MAKE_TMP_SOCKET_PATH()`, `CHANGELOG_GET_HEADER_INFO()`, `CHANGELOG_FILL_HTIME_DIR()`, `CHANGELOG_FILL_CSNAP_DIR()`, `changelog_log_type`, `changelog_mode_t`, `changelog_encoder_t`, and predicates for valid encoding and internal record types.

## Control Flow, State, and Persistence
The header establishes persistent on-disk format details: header text, major/minor version, encoding values, changelog type values, and HTIME xattr names. Socket macros hash brick paths with xxh64 to create stable per-brick Unix socket paths and process-specific temporary reverse socket paths.

## Dependencies and Integration
Requires Gluster defaults and xxhash wrapper visibility through including translation units. Used by both xlator and library decoders, so it is the compatibility hinge between writer and reader.

## Risks and Test Signals
Risks include format-string coupling in `CHANGELOG_GET_HEADER_INFO()`, path truncation from hashed socket templates, and ABI impact if enum values change. Test signals include header parse round-trips, socket path stability for brick paths, and decoder rejection of invalid encodings.
