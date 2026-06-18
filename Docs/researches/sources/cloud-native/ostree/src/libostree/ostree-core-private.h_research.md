<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-core-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-core-private.h

## Purpose
Defines private constants, on-disk stream format types, and helper prototypes for libostree's core object serialization and validation layer.

## Important APIs and Types
Declares default archive compression level, default file/directory modes, file header variant signatures, object path helpers, static delta path helpers, xattr canonicalization/validation, stat/GFileInfo conversion, bare-user-only mode validation, metadata validation/verification, raw-to-archive stream conversion, timestamp comparison, default sysroot path, and optional detached GPG signature appending.

## Control Flow
No implementation flow. Inline helpers convert checksum variants to strings, derive commitpartial paths, and identify bare repository modes.

## State and Persistence
The header documents persistent OSTree file object stream formats: a big-endian length-prefixed `GVariant` header followed by content, with a zlib variant including uncompressed size. These formats are read by multiple implementation files.

## Dependencies and Integration Points
Includes `ostree-core.h`, `otutil.h`, and `<sys/stat.h>`. It is shared by repo commit, checkout, pull, fsck, static delta, and content conversion code.

## Risks
Changing variant signatures or object path helpers is repository-format breaking. Helpers marked private are still widely coupled inside libostree, so changes require broad integration tests.

## Test Signals
Tests should cover file header round trips, object/static-delta path generation, checksum conversion, xattr canonicalization, metadata schema validation, and downgrade timestamp checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-core-private.h -->
