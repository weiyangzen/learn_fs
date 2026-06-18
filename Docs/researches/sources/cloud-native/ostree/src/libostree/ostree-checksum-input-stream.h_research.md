<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-checksum-input-stream.h -->
# sources/cloud-native/ostree/src/libostree/ostree-checksum-input-stream.h

## Purpose
Declares the checksum-updating filter input stream type.

## Important APIs and Types
Defines type/cast/check macros, `OstreeChecksumInputStream`, class struct with reserved padding, type getter, and `ostree_checksum_input_stream_new(GInputStream*, GChecksum*)`.

## Control Flow
No implementation flow in the header.

## State and Persistence
Implementation-private state stores a borrowed `GChecksum*`.

## Dependencies and Integration Points
Includes `<gio/gio.h>` and supports stream hashing integrations.

## Risks
The borrowed checksum lifetime is not visible from the type system. Callers need to manage it explicitly.

## Test Signals
Compile/type checks and read-path checksum tests validate the declaration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-checksum-input-stream.h -->
